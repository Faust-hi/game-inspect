"""Точечные исправления известных исходных записей с сохранением ручных правок."""
import re

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models.entities import (
    Conflict, DependencyEdge, Engine, EngineTool, EvidenceClaim,
    EvidenceSource, GameFunction, HardwareCPU, HardwareGPU, Method,
    MethodEngineLink, TechnologyNode,
)
from . import methods_data, sources

#: Дата публикации, записанная как «1 января»: точность таких источников —
#: только год, а день добавлен нормализацией. Реестр хранит их как `YYYY`,
#: пакеты исследований — так же.
_YEAR_ONLY_DATE = re.compile(r"^\d{4}-01-01$")

#: Литералы-заглушки для источников без объявленной даты публикации
#: (постоянно обновляемая документация, страницы SDK).
_PLACEHOLDER_DATES = frozenset({"2025-01-01", "2026-09-09"})

#: Недоступные адреса источников: прежний URL → проверенная замена.
#: Проба HTTP выполнена 2026-09-11 (`tools/verify_sources.py`): каждый новый
#: адрес ответил 2xx, принадлежит тому же вендору и раскрывает ту же тему.
#: Здесь только переезд адреса; источники без проверенной замены сюда не
#: попадают — недоступный источник объявляется, а не подменяется похожим.
SOURCE_URL_REPLACEMENTS: dict[str, str] = {
    # Unity перенесла справочник 6000.x под /Documentation/Manual/.
    "https://docs.unity3d.com/Manual/ShaderLoadTimeOptimization.html":
        "https://docs.unity3d.com/6000.0/Documentation/Manual/shader-loading.html",
    "https://docs.unity3d.com/6000.0/Manual/job-system-overview.html":
        "https://docs.unity3d.com/6000.0/Documentation/Manual/job-system-overview.html",
}


def repair_dead_source_urls(db: Session) -> int:
    """Перевести уже записанные недоступные адреса на проверенные замены.

    Реестр источников меняется, но `evidence_catalog.sync_sources` намеренно не
    перезаписывает непустые поля (правка администратора важнее), поэтому
    исправление реестра само по себе до существующей базы не доезжает: 404
    продолжали жить в `evidence_sources`, `methods`, `conflicts`,
    `method_engine_links` и `hardware_*`. Функция идемпотентна и срабатывает
    только на точное совпадение прежнего адреса — собственная ссылка
    администратора не заменяется.
    """
    updated = 0
    for model, column in (
        (EvidenceSource, "url"),
        (Method, "source_url"),
        (Conflict, "source_url"),
        (MethodEngineLink, "source_url"),
        (HardwareCPU, "source_url"),
        (HardwareGPU, "source_url"),
        # Узел технологии ссылается на ту же страницу вендора, но через
        # `docs_url`. Без этой пары переезд справочника Unity не доезжал до
        # `technology_nodes`: в списке выше были только методы и железо.
        (TechnologyNode, "docs_url"),
    ):
        for old_url, new_url in SOURCE_URL_REPLACEMENTS.items():
            for row in db.scalars(select(model).where(getattr(model, column) == old_url)):
                setattr(row, column, new_url)
                updated += 1
    if updated:
        db.flush()
    return updated


def correct_shadow_relation(db: Session) -> int:
    """Заменить только точную устаревшую запись штатного каталога."""
    # Старый формат: conflict_type="conflict" → новый: hard_conflict
    # Правильный тип для синергии теней: complement (было synergy)
    old_hard_conflict = {
        "a_code": "cascaded_shadow_maps",
        "b_code": "distance_field_shadows",
        "conflict_type": "hard_conflict",
        "severity": 1,
        "description": "Два механизма теней для направленного света дублируют стоимость и дают непредсказуемое наложение результатов.",
        "resolution": "Выбрать одну систему теней как основную.",
        "source_url": "https://en.wikipedia.org/wiki/Shadow_mapping",
        "status": "published",
    }
    # Также проверяем старый тип "conflict" для совместимости с устаревшими базами
    old_conflict = {**old_hard_conflict, "conflict_type": "conflict"}
    
    row = db.scalar(select(Conflict).where(*[
        getattr(Conflict, key) == value for key, value in old_hard_conflict.items()
    ]))
    if row is None:
        # Проверяем старый формат
        row = db.scalar(select(Conflict).where(*[
            getattr(Conflict, key) == value for key, value in old_conflict.items()
        ]))
    if row is None:
        return 0
    # Если уже правильно задано complement (было synergy) — не трогаем
    existing = db.scalar(select(Conflict).where(
        Conflict.a_code == old_hard_conflict["a_code"], Conflict.b_code == old_hard_conflict["b_code"],
        Conflict.conflict_type == "complement",
    ))
    if existing is not None:
        return 0
    _, relations = methods_data.with_sources()
    # В methods_data теперь должен быть complement вместо synergy
    replacement = next(item for item in relations if item["a_code"] == old_hard_conflict["a_code"]
                       and item["b_code"] == old_hard_conflict["b_code"] and item["conflict_type"] == "complement")
    for key, value in replacement.items():
        if hasattr(Conflict, key):
            setattr(row, key, value)
    db.flush()
    return 1


#: Устаревшие значения `conflict_type`, которые встречаются в базах, созданных
#: до разделения связей на типы. Код обрабатывает только значения перечисления
#: `ConflictType`, поэтому старые записи не исключали методы и не давали
#: предупреждений — связь существовала в базе, но ни на что не влияла.
LEGACY_CONFLICT_TYPES = {
    "conflict": "hard_conflict",   # был единственный тип запрета
    "synergy": "complement",       # синергия, в новом формате — complement
}


def correct_legacy_conflict_types(db: Session) -> int:
    """Привести устаревшие типы связей к значениям перечисления.

    Исправление общее, а не точечное: в отличие от `correct_shadow_relation`
    оно не может сослаться на одну известную запись, потому что устаревшие
    значения мог получить любой конфликт. Меняются только те строки, у которых
    тип заведомо не входит в перечисление, — осознанная правка администратора
    с корректным типом не трогается.
    """
    updated = 0
    for legacy, actual in LEGACY_CONFLICT_TYPES.items():
        rows = list(db.scalars(select(Conflict).where(Conflict.conflict_type == legacy)))
        for row in rows:
            row.conflict_type = actual
            updated += 1
    if updated:
        db.flush()
    return updated


def correct_splitscreen_dependency(db: Session) -> int:
    """Убрать ложную зависимость split-screen от сетевого кода (D42).

    Split-screen — локальная функция: два вьюпорта на одной машине, сетевой
    код для неё не нужен. Прежняя запись требовала `multiplayer_netcode` и
    исключала решение из одиночных кооп-проектов. Заменяется только точное
    унаследованное значение: осознанная правка администратора не трогается.
    """
    row = db.scalar(select(Method).where(Method.code == "splitscreen_render_budget"))
    if row is None or list(row.requires_features or []) != ["multiplayer_netcode"]:
        return 0
    row.requires_features = ["split_screen_rendering"]
    db.flush()
    return 1


#: Связи, чей тип исправлен по фактическому смыслу пары, а не по названию.
#: Ключ — пара кодов, значение — прежний тип, который нужно заменить на тип
#: из актуального каталога. Осознанная правка администратора с другим типом
#: не трогается: заменяется только известное унаследованное значение.
#:
#: Причина правки — исследование каталога: универсальные `hard_conflict`
#: запрещали пары, которые в смешанной сцене сосуществуют, а `dependency`
#: объявляла обязательным условие, без которого решение работает.
RELATION_TYPE_FIXES: dict[tuple[str, str], str] = {
    ("lightmap_atlas_baking", "hardware_raytraced_gi"): "hard_conflict",
    ("gpu_procedural_placement", "lightmap_atlas_baking"): "hard_conflict",
    ("motion_matching", "animation_compression"): "hard_conflict",
    ("static_shadow_caching", "hardware_raytraced_gi"): "hard_conflict",
    ("agent_update_budget", "crowd_instancing_impostors"): "complement",
    ("skeletal_2d_deform", "sprite_atlas_batching"): "dependency",
    ("skeletal_2d_deform", "sprite_sheet_compression"): "hard_conflict",
    ("crowd_2d_instancing", "agent_update_budget"): "complement",
    ("deterministic_lockstep", "multithreaded_physics_jobs"): "hard_conflict",
    ("ml_frame_generation", "client_prediction_reconciliation"): "hard_conflict",
    ("planar_reflection_budget", "screen_space_gi"): "hard_conflict",
    ("tiled_clustered_light_culling", "depth_prepass_early_z"): "complement",
}


def correct_relation_types(db: Session) -> int:
    """Привести типы связей к актуальному смыслу каталога.

    Тип связи меняет расчёт целиком: `hard_conflict` исключает оба решения из
    корзины, `dependency` исключает первое без второго. Ошибка в типе поэтому
    не косметическая — она убирала из расчёта работающие решения или, наоборот,
    оставляла пару, требующую внимания, без предупреждения.

    Исправление точечное: заменяется только известное прежнее значение типа.
    Если администратор задал свой тип — строка не трогается.
    """
    _methods, relations = methods_data.with_sources()
    actual = {
        (item["a_code"], item["b_code"]): item
        for item in relations
    }
    updated = 0
    for pair, legacy_type in RELATION_TYPE_FIXES.items():
        replacement = actual.get(pair)
        if replacement is None:
            continue
        row = db.scalar(select(Conflict).where(
            Conflict.a_code == pair[0],
            Conflict.b_code == pair[1],
            Conflict.conflict_type == legacy_type,
        ))
        if row is None:
            continue
        # Ключ уникальности включает тип, поэтому сид создаёт связь с новым
        # типом рядом с прежней строкой. Прежнюю строку нужно убрать: иначе
        # пара существует дважды — с устаревшим типом и с актуальным.
        duplicate = db.scalar(select(Conflict).where(
            Conflict.a_code == pair[0],
            Conflict.b_code == pair[1],
            Conflict.conflict_type == replacement["conflict_type"],
            Conflict.id != row.id,
        ))
        if duplicate is not None:
            db.delete(row)
        else:
            for key, value in replacement.items():
                if hasattr(Conflict, key):
                    setattr(row, key, value)
        updated += 1
    if updated:
        db.flush()
    return updated


#: Связи, снятые как противоречащие другой связи той же пары (N6).
#:
#: Метод не может быть объявлен обязательным условием того, с чем он
#: несовместим: движок применял обе связи, и корзина получала сразу два
#: взаимоисключающих сообщения — «исключить оба метода» от `hard_conflict`
#: и «сначала внедрить зависимость» от `dependency`. То же у `risk`: его
#: решение предлагает оставить оба метода, тогда как `hard_conflict` той же
#: пары требует оставить один.
#:
#: Удаляется только точная унаследованная запись — по паре, типу и тексту
#: описания. Осознанная правка администратора с другим текстом не трогается.
#: В каталоге и пакетах эти записи уже сняты; этот проход нужен потому, что
#: сид не перетирает существующие строки, и по существующей базе правка
#: каталога остаётся невидимой.
CONTRADICTORY_RELATIONS: list[dict[str, str]] = [
    {
        "a_code": "motion_matching",
        "b_code": "animation_lod_budget",
        "conflict_type": "dependency",
        "description": "Метод «motion_matching» требует предварительного метода «animation_lod_budget».",
    },
    {
        "a_code": "sdf_global_illumination",
        "b_code": "hardware_raytraced_gi",
        "conflict_type": "dependency",
        "description": "Метод «sdf_global_illumination» требует предварительного метода «hardware_raytraced_gi».",
    },
    {
        "a_code": "full_path_tracing_pipeline",
        "b_code": "selective_ray_traced_effects",
        "conflict_type": "dependency",
        "description": "Метод «full_path_tracing_pipeline» требует предварительного метода «selective_ray_traced_effects».",
    },
    {
        "a_code": "animation_lod_budget",
        "b_code": "motion_matching",
        "conflict_type": "risk",
        "description": "Motion matching searches the database on tick; throttling the tick rate "
                       "throttles responsiveness, and root-motion locomotion blocks the "
                       "parallel-update path entirely, which removes one of the two ways to pay "
                       "for motion matching in a crowd.",
    },
]


def correct_contradictory_relations(db: Session) -> int:
    """Снять связи, противоречащие другой связи той же пары (N6).

    Вместе со строкой `conflicts` снимается и ребро графа: `sync_dependency_graph`
    только добавляет рёбра, поэтому без явного удаления ребро пережило бы
    строку-основание и продолжало бы управлять порядком внедрения.
    """
    removed = 0
    nodes = {n.code: n for n in db.scalars(select(TechnologyNode))}
    for spec in CONTRADICTORY_RELATIONS:
        row = db.scalar(select(Conflict).where(*[
            getattr(Conflict, key) == value for key, value in spec.items()
        ]))
        if row is None:
            continue
        src = nodes.get(f"method:{spec['a_code']}")
        dst = nodes.get(f"method:{spec['b_code']}")
        if src is not None and dst is not None:
            for edge in db.scalars(select(DependencyEdge).where(
                    DependencyEdge.source_node_id == src.id,
                    DependencyEdge.target_node_id == dst.id,
                    DependencyEdge.dependency_type == spec["conflict_type"])):
                db.delete(edge)
        db.delete(row)
        removed += 1
    if removed:
        db.flush()
    return removed


#: Источники карты, подобранные по названию, а не по механизму: ссылка
#: описывала другую технологию и не обосновывала утверждение карточки
#: (временное сглаживание вместо переменной частоты затенения, обратная
#: кинематика вместо подбора движений, DLSS вместо нейронного сжатия текстур,
#: виртуальные теневые карты вместо теней по полям расстояний).
#: Ключ — код решения, значение — прежний и актуальный ключи источника.
METHOD_SOURCE_FIXES: dict[str, tuple[str, str]] = {
    "variable_rate_shading": ("WIKI_TAA", "MS_VRS"),
    "motion_matching": ("WIKI_IK", "UE_MOTION_MATCHING"),
    "neural_texture_compression": ("WIKI_DLSS", "NVIDIA_NTC"),
    "distance_field_shadows": ("UE_VSM", "UE_DISTANCE_SHADOWS"),
    "ability_visual_effect_budget": ("GPP_STATE", "UE_NIAGARA"),
}


def correct_method_sources(db: Session) -> int:
    """Заменить источники, не соответствующие механизму решения.

    Ссылка — часть обоснования карточки: если она описывает другую
    технологию, пользователь не может проверить утверждение. Исправление
    касается и уже существующих баз, иначе новая ссылка появилась бы только
    при пересоздании каталога.

    Заменяется только прежний URL из каталога: если администратор указал
    собственный источник, строка не трогается.
    """
    updated = 0
    for code, (old_key, new_key) in METHOD_SOURCE_FIXES.items():
        old = sources.SOURCES.get(old_key) or {}
        new = sources.SOURCES.get(new_key) or {}
        if not old.get("url") or not new.get("url"):
            continue
        row = db.scalar(select(Method).where(Method.code == code))
        if row is not None and row.source_url == old["url"]:
            # The URL and its human-readable title form one provenance pair.
            # Updating only the URL leaves an apparently plausible but false
            # citation in the public catalogue (for example VSM titled as
            # Distance Field Shadows).  Replace the legacy title/date only
            # when the URL still has its seeded value; administrator-owned
            # sources remain untouched.
            row.source_url = new["url"]
            row.source_title = new.get("title", row.source_title)
            row.source_date = new.get("date", row.source_date)
            updated += 1
    if updated:
        db.flush()
    return updated


def correct_source_publication(db: Session) -> int:
    """Опубликовать источники, оставшиеся черновиками при переносе из пакетов.

    Тип источника по умолчанию — черновик, поэтому записи, созданные без
    явного статуса, не отдавались в выдаче: `source_to_out` возвращает None для
    неопубликованного источника, и публичное утверждение выглядело как
    утверждение без источника. Исправление нужно и уже существующим базам —
    иначе публикация доказательной базы появится только при пересоздании.

    Публикуется только источник, на который ссылается хотя бы одно публичное
    утверждение: остальной черновик — рабочая заготовка, и повышать его без
    причины нельзя.
    """
    referenced: set[int] = set()
    for claim in db.scalars(select(EvidenceClaim).where(EvidenceClaim.status == "published")):
        if claim.source_id:
            referenced.add(claim.source_id)
    updated = 0
    if referenced:
        for source in db.scalars(
            select(EvidenceSource).where(
                EvidenceSource.id.in_(referenced),
                EvidenceSource.status != "published",
            )
        ):
            source.status = "published"
            updated += 1
    if updated:
        db.flush()
    return updated


def correct_effect_scopes(db: Session) -> int:
    """Проставить область эффекта записям, созданным до появления поля.

    Область задавалась неявно: все решения считались влияющими на компьютер
    игрока, из-за чего серверная экономия уменьшала требования к клиенту.
    Явные значения каталога нужно донести и до уже существующих баз, иначе
    исправление расчёта подействует только на новые установки.

    Значение, отличное от прежнего неявного `client`, не трогается: это
    осознанная правка администратора, а не унаследованное умолчание.
    """
    methods, _relations = methods_data.with_sources()
    declared = {
        item["code"]: item["effect_scope"]
        for item in methods
        if item.get("effect_scope") not in (None, "client")
    }
    updated = 0
    for code, scope in declared.items():
        row = db.scalar(select(Method).where(Method.code == code))
        if row is not None and row.effect_scope == "client":
            row.effect_scope = scope
            updated += 1
    if updated:
        db.flush()
    return updated


def correct_engine_tool_independence(db: Session) -> int:
    """Отметить решения, не опирающиеся на встроенный инструмент движка.

    Признак нужен, чтобы отличать «методу не нужен встроенный инструмент»
    от «данных нет»: без него пустая привязка к версии движка читалась
    как пробел в каталоге. Значение доносится и до существующих баз, иначе
    различие действует только на новые установки.

    Снимается только в одну сторону: значение True у записи, которой нет
    в списке каталога, могло быть поставлено администратором осознанно.
    """
    declared = methods_data.ENGINE_TOOL_INDEPENDENT
    updated = 0
    for code in sorted(declared):
        row = db.scalar(select(Method).where(Method.code == code))
        if row is not None and not row.engine_tool_independent:
            row.engine_tool_independent = True
            updated += 1
    if updated:
        db.flush()
    return updated


def correct_placeholder_source_dates(db: Session) -> int:
    """Заменить подставные даты публикации на честные значения из реестра.

    Дата источника живёт в **трёх** местах: сама запись реестра
    (`evidence_sources.published_date`) и две её производные копии —
    `methods.source_date` и `game_functions.source_date` (обе подставляются из
    того же реестра: `methods_data.with_sources` → `data["source_date"] =
    s["date"]`). Проход долго правил только первую: копии заполнялись один раз
    при первичной сборке и после этого не обновлялись никогда, поэтому 96
    методов и 33 функции продолжали показывать `2025-01-01` как дату
    публикации, хотя каталог объявил для этих источников `n/a`.

    Записи каталога источников наполняются с оговоркой «существующее значение
    не перезаписывается» (см. `evidence_catalog.sync_sources`), поэтому правка
    реестра сама по себе не доезжала до уже существующих баз: 93 источника
    продолжали показывать `2025-01-01` как дату публикации, хотя у постоянно
    обновляемой документации даты нет, а 11 источников выдавали «1 января» за
    настоящий день выхода.

    Заменяются только значения, которые заведомо подставные: заглушка «1 января»,
    литерал из `_PLACEHOLDER_DATES`, пустое поле и — отдельный случай — любая
    конкретная дата у источника, для которого реестр **прямо объявил** `n/a`.
    Последнее не оговорка, а суть правила: у постоянно обновляемой документации
    даты публикации не существует, поэтому конкретное число здесь — либо
    заглушка, либо дата проверки ссылки, выданная за публикацию. Настоящая дата
    у источника с объявленной датой не трогается: сравнивается с реестром.

    Производные копии опознаются по `source_url`: ключа источника (`source_key`)
    в строке нет — `with_sources` его вынимает. Один адрес реестра из 160 делят
    две записи с разными датами (`counter-strike.net/cs2`); такой адрес не
    разрешается вовсе — выбрать одну из двух дат значило бы выдумать.
    """
    # Оба реестра: `sources.SOURCES` (базовый) и `EXTRA_SOURCES` из каталога
    # доказательств. Источники второго реестра не попадали бы в сводку только
    # по `sources.SOURCES`, и восемь записей сохранили бы подставные даты.
    from .evidence_catalog import EXTRA_SOURCES
    registry = {**sources.SOURCES, **EXTRA_SOURCES}

    # Адрес → объявленная дата. Неоднозначные адреса собираются отдельно: по
    # ним замена не делается, но факт неоднозначности не растворяется молча.
    by_url: dict[str, str] = {}
    ambiguous_urls: set[str] = set()
    for record in registry.values():
        url = (record.get("url") or "").strip()
        date = (record.get("date") or "").strip()
        if not url or not date:
            continue
        if url in by_url and by_url[url] != date:
            ambiguous_urls.add(url)
            continue
        by_url[url] = date

    def _is_placeholder(current: str, expected: str) -> bool:
        """Хранимое значение заведомо не настоящая дата публикации."""
        if not current or expected == current:
            return False
        # Реестр прямо объявляет отсутствие даты публикации (`n/a`). Значит любая
        # конкретная дата в базе недостоверна: у обновляемой документации даты
        # публикации не существует, и конкретное число здесь — либо заглушка,
        # либо дата проверки ссылки, выданная за публикацию. Правило закрывает
        # именно этот класс: две страницы dev.epicgames.com показывали
        # `2026-09-01`/`2026-09-07`, тогда как соседние страницы того же вендора
        # помечены `n/a`.
        return (
            bool(_YEAR_ONLY_DATE.match(current))
            or current in _PLACEHOLDER_DATES
            or expected == "n/a"
        )

    updated = 0

    # 1. Записи реестра. Пустое поле здесь не заполняется: его закрывает
    # `sync_sources` по тому же реестру (правило «заполняется только пустое»),
    # и второй проход по тому же значению был бы лишним.
    for row in db.scalars(select(EvidenceSource)):
        current = (row.published_date or "").strip()
        if not current:
            continue
        expected = ((registry.get(row.code) or {}).get("date") or "").strip()
        if _is_placeholder(current, expected):
            row.published_date = expected
            updated += 1

    # 2. Производные копии. У них прохода «заполнить пустое» нет вовсе, поэтому
    # пустое поле здесь закрывается: реестр значение объявляет, а пустое поле
    # проект относит к другой категории (`missing_published_date`) — то есть
    # «дата неизвестна», тогда как у этих источников она объявлена как
    # отсутствующая. Четыре метода так и держали пустое при объявленном `n/a`.
    for model in (Method, GameFunction):
        for row in db.scalars(select(model)):
            url = (row.source_url or "").strip()
            if not url or url in ambiguous_urls:
                continue
            expected = by_url.get(url, "")
            current = (row.source_date or "").strip()
            if not expected:
                continue
            if current == expected:
                continue
            if not current or _is_placeholder(current, expected):
                row.source_date = expected
                updated += 1

    if updated:
        db.flush()
    return updated


def refresh_tool_engine_notes(db: Session) -> int:
    """Дописать оговорку о пользовательской технологии уже созданным рёбрам.

    Ребро «инструмент → движок» создаётся один раз, и его описание с тех пор не
    пересобирается: каталог добавил к фразе оговорку «и помечен как
    пользовательская технология», но семь рёбер, созданных раньше, её не
    получили — оговорка объясняет, почему у ребра нет публичного источника.

    Описание пересобирается тем же шаблоном (`dependency_graph.
    tool_engine_description`), а замена делается только когда хранимый текст
    содержит **прежний** вид фразы: запись, поправленную человеком, проход не
    трогает.
    """
    from .dependency_graph import tool_engine_description

    nodes = {node.id: node.code for node in db.scalars(select(TechnologyNode))}
    tools = {tool.code: tool for tool in db.scalars(select(EngineTool))}
    engines = {engine.code: engine for engine in db.scalars(select(Engine))}

    updated = 0
    for edge in db.scalars(
        select(DependencyEdge).where(DependencyEdge.dependency_type == "engine")
    ):
        src = nodes.get(edge.source_node_id, "")
        dst = nodes.get(edge.target_node_id, "")
        if not src.startswith("tool:") or not dst.startswith("engine:"):
            continue
        tool = tools.get(src[len("tool:"):])
        engine = engines.get(dst[len("engine:"):])
        if tool is None or engine is None or not tool.is_user_defined:
            continue
        old_text = tool_engine_description(tool.name, engine.name, is_user_defined=False)
        new_text = tool_engine_description(tool.name, engine.name, is_user_defined=True)
        stored = edge.description or ""
        if old_text in stored and new_text not in stored:
            edge.description = stored.replace(old_text, new_text)
            updated += 1
    if updated:
        db.flush()
    return updated


#: Записи источников, которые каталог привёл к согласованному виду, а база
#: сохранила в прежнем, самопротиворечивом. Ключ — код записи, значение —
#: **прежний** набор полей: проход срабатывает, только если хранится ровно он.
#: Иначе запись не трогается — её мог поправить человек.
#:
#: `SRC-RND-048` — якорь метода `splitscreen_render_budget` для поля
#: `impact.gpu`. Разбор Digital Foundry по It Takes Two отдал 404 (2026-09-11),
#: адрес заменили на страницу Wikipedia, а сам метод перенаправили на два
#: проверенных источника. Запись осталась прежней и противоречит себе: заголовок
#: Digital Foundry стоит на URL Wikipedia, локатор сообщает о 404, а дата —
#: обрубок прежнего среза до 20 знаков. Ссылается на неё одно утверждение с
#: `basis='unknown'` — объявленный пробел «опубликованных цифр не нашлось»,
#: поэтому запись не удаляется, а приводится в согласованный вид.
SOURCE_RECORD_LEGACY: dict[str, dict[str, str]] = {
    "SRC-RND-048": {
        "title": "It Takes Two tech analysis (Digital Foundry)",
        "locator": "n/a - server returned '404 Not Found'",
        "published_date": "2021 (URL in catalog",
    },
}


def correct_source_records(db: Session) -> int:
    """Перенести в существующую базу записи источников, починенные каталогом.

    `pack_loader._upsert_source` при существующей строке возвращает её как есть,
    не трогая ни одного поля: правка администратора важнее каталога. Обратная
    сторона — **ни один** ремонт записи источника до уже собранной базы не
    доезжает, и она расходится со свежей установкой. Проход закрывает этот
    случай, сохраняя защиту: замена идёт только при точном совпадении прежнего
    набора полей (`SOURCE_RECORD_LEGACY`), а новые значения берутся из пакета
    тем же разбором, что и при первичной загрузке.

    `notes` и `status` не трогаются: это поля администратора.
    """
    from .pack_loader import _load_packs, _sequence, source_record_values

    wanted = set(SOURCE_RECORD_LEGACY)
    if not wanted:
        return 0

    packs, _failures = _load_packs()
    records: dict[str, dict] = {}
    for pack in packs:
        for payload in _sequence(pack, "sources"):
            if isinstance(payload, dict) and payload.get("code") in wanted:
                records[payload["code"]] = payload

    updated = 0
    for code, legacy in SOURCE_RECORD_LEGACY.items():
        row = db.scalar(select(EvidenceSource).where(EvidenceSource.code == code))
        payload = records.get(code)
        if row is None or payload is None:
            continue
        if any((getattr(row, field) or "") != value for field, value in legacy.items()):
            # Запись уже отличается от прежней: её правил человек либо она уже
            # приведена — в обоих случаях вмешиваться нельзя.
            continue
        for field, value in source_record_values(payload).items():
            setattr(row, field, value)
        updated += 1
    if updated:
        db.flush()
    return updated


def declare_evidence_gaps(db: Session) -> dict[str, int]:
    """Довести машинно-читаемые декларации пробелов до согласованного вида.

    Три класса записей законно не имеют внешнего источника, но декларация об
    этом не была проставлена в машиночитаемое поле, и аудит считал их
    «незадекларированными дырами»:

    * связка «метод-инструмент» с инструментом собственной реализации
      (`is_user_defined`) — публичного источника не существует; честное
      состояние — `evidence_status='user_defined'`, а не пустой URL;
    * конфликт, выведенный из структуры каталога («A требует B»), — URL не
      существует: это не факт из документа, а следствие связей каталога;
      помечается `source_url='user_defined:catalog_dependency'`;
    * ребро графа без источника — плановая зависимость пакетов работ;
      помечается префиксом `[expert_estimate:no_external_source]` в описании;
    * ребро «инструмент → движок» с инструментом собственной реализации —
      описание дополняется оговоркой о пользовательской технологии: она и
      объясняет отсутствие публичного источника;
    * игровой кейс, оставшийся черновиком при переносе из пакетов, —
      публикуется, если подтверждён опубликованным фактом с источником.

    Функция идемпотентна и нужна уже существующим базам. Раньше эти проходы
    выполнялись внутри `seed_methods` — до того, как создавались сами
    инструменты, связи и железо, — поэтому на свежей базе не срабатывали:
    декларации появлялись только при повторном заполнении.
    """
    from .fixes_v2 import apply_hardware_raw_values, mark_user_defined_tech, normalize_link_evidence

    # Инструменты собственной реализации и их связи.
    links_marked = mark_user_defined_tech(db)
    links_normalized = normalize_link_evidence(db)

    # Конфликты без источника: выведены из структуры каталога, а не из документа.
    conflicts_declared = 0
    for row in db.scalars(select(Conflict)):
        if not (row.source_url or "").strip():
            row.source_url = "user_defined:catalog_dependency"
            conflicts_declared += 1

    # Рёбра графа без источника: плановая зависимость пакетов работ.
    marker = "[expert_estimate:no_external_source]"
    edges_declared = 0
    for row in db.scalars(select(DependencyEdge)):
        if not row.source_id and marker not in (row.description or ""):
            row.description = f"{marker} {row.description or ''}".strip()
            edges_declared += 1

    # Оговорка о пользовательской технологии в описании ребра «инструмент →
    # движок»: она объявляет, почему публичного источника нет. Каталог добавил
    # её позже самих рёбер, и семь записей остались без объяснения.
    tool_notes_refreshed = refresh_tool_engine_notes(db)

    # Сырые значения бенчмарков: нормализованные индексы были записаны без
    # исходной величины, из-за чего нормализация непроверяема.
    hardware_raw = apply_hardware_raw_values(db)

    # Переехавшие адреса источников: 404 в уже собранной базе.
    urls_repaired = repair_dead_source_urls(db)

    if conflicts_declared or edges_declared:
        db.flush()
    return {
        "links_user_defined_marked": links_marked,
        "links_evidence_normalized": links_normalized,
        "conflicts_declared": conflicts_declared,
        "dependency_edges_declared": edges_declared,
        "tool_engine_notes_refreshed": tool_notes_refreshed,
        "hardware_raw_values": hardware_raw,
        "source_urls_repaired": urls_repaired,
    }


#: Перевёрнутые обязательные связи карточки `fixed_timestep_physics`.
#: Карточка объявляла `cloth_constraint_simulation` и `raycast_vehicle_physics`
#: своими зависимостями, тогда как по смыслу — и по их собственным карточкам —
#: это они зависят от фиксированного шага. Из-за перевёрнутого ребра возникал
#: цикл `fixed_timestep_physics ↔ raycast_vehicle_physics`, и автоматический
#: разрыв цикла понижал **верное** ребро `raycast_vehicle_physics →
#: fixed_timestep_physics` (жертва выбиралась по алфавиту кодов). Итог: достройка
#: корзины тянула неприменимый метод, каскад снимал выбранный метод
#: пользователя, и корзина обнулялась — 22 из 108 применимых методов не влияли
#: ни на профиль нагрузки, ни на подбор железа.
_REVERSED_PHYSICS_DEPENDENCIES: tuple[tuple[str, str], ...] = (
    ("fixed_timestep_physics", "cloth_constraint_simulation"),
    ("fixed_timestep_physics", "raycast_vehicle_physics"),
)

#: Встречная (верная) связь, понижённая автоматическим разрывом цикла.
_DEMOTED_PHYSICS_DEPENDENCY = ("raycast_vehicle_physics", "fixed_timestep_physics")

#: Начало текста, которым разрыв цикла помечает понижённую связь.
_DEMOTION_MARKER = "Связь понижена из обязательной зависимости"

#: Описание верной связи — то же, что объявляет карточка метода.
_DEMOTED_PHYSICS_NOTE = (
    "Suspension feel and stability are timestep-dependent; without a fixed step, "
    "handling changes with framerate."
)


def _method_node_id(db: Session, code: str) -> int | None:
    return db.scalar(select(TechnologyNode.id).where(TechnologyNode.code == f"method:{code}"))


def _drop_mandatory_edge(db: Session, a_code: str, b_code: str) -> bool:
    src, dst = _method_node_id(db, a_code), _method_node_id(db, b_code)
    if src is None or dst is None:
        return False
    edge = db.scalar(select(DependencyEdge).where(
        DependencyEdge.source_node_id == src,
        DependencyEdge.target_node_id == dst,
        DependencyEdge.dependency_type == "dependency",
    ))
    if edge is None:
        return False
    db.delete(edge)
    return True


def _restore_mandatory_edge(db: Session, a_code: str, b_code: str) -> bool:
    """Вернуть обязательное ребро `a → b` и снять устаревшее «дополнение».

    Ребро могло быть удалено автоматическим разрывом цикла, а могло быть уже
    пересоздано построением графа из исправленных связей — тогда достаточно
    снять с него признак понижения. Уникальность задана тройкой
    (источник, цель, тип), поэтому перевести «дополнение» в «зависимость» без
    проверки нельзя: верная зависимость может уже существовать.
    """
    src, dst = _method_node_id(db, a_code), _method_node_id(db, b_code)
    if src is None or dst is None:
        return False
    changed = False
    edge = db.scalar(select(DependencyEdge).where(
        DependencyEdge.source_node_id == src,
        DependencyEdge.target_node_id == dst,
        DependencyEdge.dependency_type == "dependency",
    ))
    if edge is None:
        db.add(DependencyEdge(
            source_node_id=src, target_node_id=dst,
            dependency_type="dependency", mandatory=1, severity=3,
            description=_DEMOTED_PHYSICS_NOTE, basis="derived", status="published",
        ))
        changed = True
    elif not edge.mandatory:
        edge.mandatory = 1
        edge.severity = 3
        changed = True
    # Устаревшая запись «дополнение» от автоматического понижения больше не нужна:
    # пара уже описана верной обязательной связью.
    stale = db.scalar(select(DependencyEdge).where(
        DependencyEdge.source_node_id == src,
        DependencyEdge.target_node_id == dst,
        DependencyEdge.dependency_type == "complement",
    ))
    if stale is not None:
        db.delete(stale)
        changed = True
    return changed


def correct_reversed_physics_dependencies(db: Session) -> int:
    """Снять перевёрнутые обязательные связи и вернуть понижённую встречную.

    Проход срабатывает **только на точное прежнее значение**: известная пара
    концов у перевёрнутой обязательной связи и текст автоматического понижения у
    встречной. Ничего другого не трогает и идемпотентен — повторный прогон даёт
    ноль. Данные пака исправлены там же (`research/packs/pack_ai_sim.json`),
    чтобы сборка с нуля не воспроизводила дефект.
    """
    corrected = 0
    for a_code, b_code in _REVERSED_PHYSICS_DEPENDENCIES:
        row = db.scalar(select(Conflict).where(
            Conflict.a_code == a_code, Conflict.b_code == b_code,
            Conflict.conflict_type == "dependency",
        ))
        if row is not None:
            db.delete(row)
            corrected += 1
        if _drop_mandatory_edge(db, a_code, b_code):
            corrected += 1

    a_code, b_code = _DEMOTED_PHYSICS_DEPENDENCY
    demoted = db.scalar(select(Conflict).where(
        Conflict.a_code == a_code, Conflict.b_code == b_code,
        Conflict.conflict_type == "complement",
    ))
    if demoted is not None and (demoted.resolution or "").startswith(_DEMOTION_MARKER):
        already = db.scalar(select(Conflict.id).where(
            Conflict.a_code == a_code, Conflict.b_code == b_code,
            Conflict.conflict_type == "dependency",
        ))
        if already is None:
            # Верной связи ещё нет — вернуть понижённую запись.
            demoted.conflict_type = "dependency"
            demoted.severity = 3
            demoted.resolution = ""
        else:
            # Верная связь уже объявлена (её вернул загрузчик пакетов, который
            # только добавляет): остаётся снять устаревшую запись понижения,
            # иначе та же пара показана и как зависимость, и как дополнение.
            db.delete(demoted)
        corrected += 1
        if _restore_mandatory_edge(db, a_code, b_code):
            corrected += 1
    if corrected:
        db.flush()
    return corrected
