"""Точечные исправления известных исходных записей с сохранением ручных правок."""
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models.entities import Conflict, Method
from . import methods_data, sources


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
            row.source_url = new["url"]
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
