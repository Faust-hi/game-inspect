"""Заполнение базы знаний демонстрационными данными MVP.

Операция идемпотентна: существующие записи обновляются, новые добавляются.
Каталог методов, функций и движков хранится в Python-модулях seed, а
характеристики оборудования — в `seed/data/hardware.json`.

Статус записей задаётся явно. По модели новый материал по умолчанию получает
«черновик», поэтому заполнение обязано указывать «опубликовано» — иначе база
окажется наполненной, но пустой для публичных каталогов.
"""
from __future__ import annotations

import json
import pathlib
from dataclasses import dataclass, field

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..config import DATA_DIR
from ..models.entities import (
    Conflict, DependencyEdge, Engine, EngineTool, EvidenceClaim,
    EvidenceSource, GameFunction, HardwareCPU, HardwareGPU, Method,
    MethodEngineLink, TechnologyNode, ValidationIssue,
)
from ..models.enums import DevStage, Status
from . import engines_data, functions_data, methods_data
from .corrections import (
    correct_contradictory_relations, correct_effect_scopes, correct_engine_tool_independence,
    correct_legacy_conflict_types,
    correct_method_sources, correct_placeholder_source_dates, correct_relation_types,
    correct_reversed_physics_dependencies,
    correct_shadow_relation, correct_source_publication, correct_source_records,
    correct_splitscreen_dependency,
    declare_evidence_gaps,
)

PUBLISHED = Status.PUBLISHED.value

#: Коды стадий разработки, допустимые в полях `recommended_stage`.
_DEV_STAGES = {stage.value for stage in DevStage}

#: Ключ, по которому сущность узнаётся в отчёте о заполнении.
_ENTITY_LABELS = {
    "game_functions": "функция",
    "methods": "метод",
    "engines": "движок",
    "engine_tools": "инструмент движка",
    "method_engine_links": "связь метода с инструментом",
    "conflicts": "связь методов",
    "hardware_cpu": "процессор",
    "hardware_gpu": "видеокарта",
}


@dataclass
class SeedOutcome:
    """Итог заполнения: что добавлено, что пропущено и что сохранено.

    Раньше отчёт содержал только счётчики, поэтому два класса потерь были
    невидимы: непрочитанный файл или строка без обязательного поля пропадали
    молча, и формальный успех не означал полного импорта (N02); а повторное
    заполнение перезаписывало ручные правки без предупреждения (D43.6).
    """

    #: Заменять ли существующие записи демонстрационными данными. По умолчанию
    #: — нет: восстановление демоданных выполняется явно.
    overwrite: bool = False
    added: dict[str, int] = field(default_factory=dict)
    skipped: list[dict] = field(default_factory=list)
    preserved: list[dict] = field(default_factory=list)

    def add(self, entity: str, count: int = 1) -> None:
        self.added[entity] = self.added.get(entity, 0) + count

    def skip(self, entity: str, key: str, reason: str) -> None:
        """Запись не попала в базу: причина обязана быть названа."""
        self.skipped.append({
            "entity": entity,
            "entity_label": _ENTITY_LABELS.get(entity, entity),
            "key": str(key),
            "reason": reason,
        })

    def preserve(self, entity: str, key: str, fields: list[str]) -> None:
        """Существующая запись сохранена: правки не затираются молча."""
        self.preserved.append({
            "entity": entity,
            "entity_label": _ENTITY_LABELS.get(entity, entity),
            "key": str(key),
            "fields": fields,
        })

    def as_report(self) -> dict:
        return {
            "added": dict(sorted(self.added.items())),
            "skipped": self.skipped,
            "skipped_count": len(self.skipped),
            "preserved": self.preserved,
            "preserved_count": len(self.preserved),
        }


def _load_json(name: str) -> list[dict]:
    path: pathlib.Path = DATA_DIR / name
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8"))


def _differing_fields(obj, values: dict) -> list[str]:
    """Поля, которыми существующая запись отличается от демонстрационных данных."""
    return [
        name for name, value in values.items()
        if getattr(obj, name, None) != value
    ]


def _upsert(db: Session, model, key: str, values: dict, *, outcome: SeedOutcome, entity: str):
    """Добавить запись либо обновить существующую.

    Без явного разрешения `outcome.overwrite` существующая запись не меняется:
    иначе повторное заполнение стирает административные правки, и пользователь
    узнаёт об этом только по исчезнувшим исправлениям. Различия попадают в
    отчёт, чтобы восстановление демоданных оставалось осознанным выбором.
    """
    obj = db.scalar(select(model).where(getattr(model, key) == values[key]))
    if obj is None:
        obj = model(**values)
        db.add(obj)
        outcome.add(entity)
        return obj, True
    if outcome.overwrite:
        for name, value in values.items():
            setattr(obj, name, value)
        return obj, False
    differing = _differing_fields(obj, values)
    if differing:
        outcome.preserve(entity, values[key], differing)
    return obj, False


def seed_functions(db: Session, outcome: SeedOutcome) -> dict[str, GameFunction]:
    out: dict[str, GameFunction] = {}
    for data in functions_data.with_sources():
        payload = {k: v for k, v in data.items() if hasattr(GameFunction, k)}
        payload.setdefault("status", PUBLISHED)
        obj, _ = _upsert(db, GameFunction, "code", payload, outcome=outcome, entity="game_functions")
        out[obj.code] = obj
    db.flush()
    return out


def seed_methods(db: Session, functions: dict[str, GameFunction], outcome: SeedOutcome) -> dict[str, Method]:
    methods, _conflicts = methods_data.with_sources()
    out: dict[str, Method] = {}
    for data in methods:
        # Чтение без `pop`: словари методов — общие с другими вызовами, и
        # удаление ключа меняло бы исходные данные каталога.
        function_code = data.get("function_code")
        payload = {k: v for k, v in data.items() if hasattr(Method, k) and k != "links"}
        payload.setdefault("status", PUBLISHED)
        if function_code and function_code in functions:
            payload["function_id"] = functions[function_code].id
        obj, _ = _upsert(db, Method, "code", payload, outcome=outcome, entity="methods")
        out[obj.code] = obj
    db.flush()
    return out


def sync_function_taxonomy(db: Session) -> dict[str, int]:
    """Добавить новые подсистемы и синхронизировать классификацию методов.

    Полный сидер не запускается на каждом старте, чтобы не перетирать
    административные правки. Эта узкая синхронизация добавляет новые функции,
    декларативные связи методов и заполняет только пустые планы внедрения.
    """
    from .verified_corrections import correct_existing
    functions: dict[str, GameFunction] = {}
    created_functions = 0
    for data in functions_data.with_sources():
        payload = {k: v for k, v in data.items() if hasattr(GameFunction, k)}
        payload.setdefault("status", PUBLISHED)
        obj = db.scalar(select(GameFunction).where(GameFunction.code == payload["code"]))
        if obj is None:
            obj = GameFunction(**payload)
            db.add(obj)
            created_functions += 1
        functions[obj.code] = obj
    db.flush()

    linked_methods = 0
    metadata_updated = 0
    metadata_codes = set(methods_data.FUNCTION_ASSIGNMENTS) | set(methods_data.APPLICATION_STEPS)
    for method_code in metadata_codes:
        method = db.scalar(select(Method).where(Method.code == method_code))
        if method is None:
            continue
        function_code = methods_data.FUNCTION_ASSIGNMENTS.get(method_code)
        function = functions.get(function_code) if function_code else None
        if function is not None and method.function_id is None:
            method.function_id = function.id
            linked_methods += 1
        steps = methods_data.APPLICATION_STEPS.get(method_code)
        if steps and not method.application_steps:
            method.application_steps = list(steps)
            metadata_updated += 1
    db.flush()
    from .evidence_catalog import sync_all as sync_evidence_catalog
    from .fixes_v2 import apply_all as apply_fixes_v2
    from .pack_loader import sync_packs
    extension_stats = sync_technical_extensions(db, functions)
    fix_stats = apply_fixes_v2(db)
    # Порядок проходов — как в полном сидере: коррекции связей идут до загрузки
    # пакетов. Обратный порядок удалял связь, которую объявляет пакет: коррекция
    # типа срабатывала уже после загрузки, и вернуть связь было нечем. Из-за
    # этого старт приложения терял, например, исследованное дополнение
    # `agent_update_budget` ↔ `crowd_instancing_impostors`.
    corrections = {
        "relations_corrected": correct_shadow_relation(db),
        "legacy_conflict_types_corrected": correct_legacy_conflict_types(db),
        "effect_scopes_corrected": correct_effect_scopes(db),
        "splitscreen_dependency_corrected": correct_splitscreen_dependency(db),
        "relation_types_corrected": correct_relation_types(db),
        "contradictory_relations_removed": correct_contradictory_relations(db),
        "method_sources_corrected": correct_method_sources(db),
        "source_dates_corrected": correct_placeholder_source_dates(db),
        "source_records_corrected": correct_source_records(db),
        "verified_fields_corrected": correct_existing(db),
    }
    pack_stats = sync_packs(db)
    # Канонизация связей — та же, что в полном сидере. Без неё старт приложения
    # возвращал связи, которые разрыв циклов уже убрал: пакет объявляет
    # `dependency`, понижение превращает её в `complement`, и следующий проход
    # загрузчика считал `dependency` отсутствующей и вставлял её заново — без
    # решения и без ребра, а обязательный цикл возвращался. Здесь эти проходы
    # выполняются после загрузки, поэтому база сходится к тому же состоянию,
    # что и собранная с нуля.
    from .dependency_graph import (
        break_dependency_cycles, dedupe_symmetric_relations, sync_dependency_graph,
    )
    from .relation_resolutions import apply_relation_resolutions
    # Граф строится после загрузки пакетов — тем же порядком, что и в полном
    # сидере. Только `sync_dependency_graph` превращает строки `conflicts` в
    # рёбра `dependency_edges`; без него новый проход загрузчика создавал связь,
    # но ребра у неё не было, и `graph_checks` её не видел, тогда как сборка с
    # нуля ребро получала. Два входа в одну базу обязаны давать одно состояние.
    graph_stats = sync_dependency_graph(db)
    # Перевёрнутые обязательные связи снимаются **до** разрыва циклов: пока они
    # на месте, разрыв понижает верное ребро, а не перевёрнутое.
    graph_stats["reversed_physics_dependencies_corrected"] = (
        correct_reversed_physics_dependencies(db)
    )
    graph_stats.update(break_dependency_cycles(db))
    graph_stats.update(dedupe_symmetric_relations(db))
    # Декларации пробелов — до решений: основание решения зависит от маркера
    # источника (`user_defined:`), который ставит именно этот проход.
    gap_stats = declare_evidence_gaps(db)
    canonical = {
        **graph_stats,
        **gap_stats,
        **apply_relation_resolutions(db),
    }
    return {
        "functions_created": created_functions,
        **extension_stats,
        "methods_linked": linked_methods,
        "method_metadata_updated": metadata_updated,
        **corrections,
        **fix_stats,
        **pack_stats,
        **canonical,
        **sync_evidence_catalog(db),
    }


def sync_technical_extensions(db: Session, functions: dict[str, GameFunction]) -> dict[str, int]:
    """Add the reviewed technical extension to existing databases, preserving edits."""
    from .technical_extensions import EFFECTS, CONFLICTS
    from .reviewed_methods import EFFECTS as reviewed_effects, CONFLICTS as reviewed_conflicts
    extension_codes = set(EFFECTS) | set(reviewed_effects)
    method_rows, relation_rows = methods_data.with_sources()
    created_methods = created_relations = 0
    for data in method_rows:
        if data['code'] not in extension_codes or db.scalar(select(Method.id).where(Method.code == data['code'])):
            continue
        payload = {k: v for k, v in data.items() if hasattr(Method, k)}
        payload.update(status=PUBLISHED, function_id=functions[data['function_code']].id)
        db.add(Method(**payload))
        created_methods += 1
    db.flush()
    keys = {(r['a_code'], r['b_code'], r['conflict_type']) for r in [*CONFLICTS, *reviewed_conflicts]}
    for data in relation_rows:
        if (data['a_code'], data['b_code'], data['conflict_type']) not in keys:
            continue
        # Preserve even a manually changed type for an existing pair.
        existing = db.scalar(select(Conflict.id).where(
            ((Conflict.a_code == data['a_code']) & (Conflict.b_code == data['b_code'])) |
            ((Conflict.a_code == data['b_code']) & (Conflict.b_code == data['a_code']))))
        if existing is None:
            payload = {k: v for k, v in data.items() if hasattr(Conflict, k)}
            db.add(Conflict(**{**payload, 'status': PUBLISHED}))
            created_relations += 1
    db.flush()
    return {'technical_methods_created': created_methods, 'technical_relations_created': created_relations}


def seed_engines(db: Session, outcome: SeedOutcome) -> dict[str, Engine]:
    out: dict[str, Engine] = {}
    for data in engines_data.ENGINES:
        obj, _ = _upsert(
            db, Engine, "code", {**data, "status": PUBLISHED},
            outcome=outcome, entity="engines",
        )
        out[obj.code] = obj
    db.flush()
    return out


def seed_engine_tools(db: Session, engines: dict[str, Engine], outcome: SeedOutcome) -> dict[str, EngineTool]:
    out: dict[str, EngineTool] = {}
    for data in engines_data.ENGINE_TOOLS:
        # Раньше код движка извлекался через `pop`, что изменяло исходный
        # словарь каталога: при повторном заполнении в том же процессе ключ
        # исчезал, и инструмент создавался без движка.
        engine_code = data.get("engine_code")
        payload = {k: v for k, v in data.items() if hasattr(EngineTool, k)}
        payload.setdefault("status", PUBLISHED)
        if engine_code in engines:
            payload["engine_id"] = engines[engine_code].id
        obj, _ = _upsert(db, EngineTool, "code", payload, outcome=outcome, entity="engine_tools")
        out[obj.code] = obj
    db.flush()
    return out


def seed_method_links(
    db: Session, methods: dict[str, Method], tools: dict[str, EngineTool], outcome: SeedOutcome,
) -> int:
    count = 0
    entity = "method_engine_links"
    for method_code, per_engine in methods_data.all_links().items():
        method = methods.get(method_code)
        if method is None:
            outcome.skip(entity, method_code, "метод не найден в каталоге")
            continue
        for engine_code, (tool_code, relation, note) in per_engine.items():
            tool = tools.get(tool_code)
            if tool is None:
                outcome.skip(entity, f"{method_code} → {tool_code}", "инструмент движка не найден")
                continue
            exists = db.scalar(
                select(MethodEngineLink).where(
                    MethodEngineLink.method_id == method.id,
                    MethodEngineLink.tool_id == tool.id,
                )
            )
            if exists:
                if outcome.overwrite:
                    exists.relation_type = relation
                    exists.note = note
                    exists.source_url = tool.docs_url
                    exists.status = PUBLISHED
                continue
            else:
                db.add(MethodEngineLink(
                    method_id=method.id, tool_id=tool.id,
                    relation_type=relation, note=note, source_url=tool.docs_url,
                    status=PUBLISHED,
                ))
                count += 1
                outcome.add(entity)
    db.flush()
    return count


def seed_conflicts(db: Session, outcome: SeedOutcome) -> int:
    # Ключ апсерта — вся тройка (a_code, b_code, conflict_type), как в UNIQUE
    # uq_conflict_pair. Раньше ключом был один a_code: при повторном сиде вторая
    # запись с тем же a_code перезаписывала первую и падала с IntegrityError.
    _, conflicts = methods_data.with_sources()
    count = 0
    entity = "conflicts"
    for data in conflicts:
        payload = {k: v for k, v in data.items() if hasattr(Conflict, k)}
        payload.setdefault("status", PUBLISHED)
        obj = db.scalar(
            select(Conflict).where(
                Conflict.a_code == payload["a_code"],
                Conflict.b_code == payload["b_code"],
                Conflict.conflict_type == payload["conflict_type"],
            )
        )
        if obj is None:
            db.add(Conflict(**payload))
            count += 1
            outcome.add(entity)
        elif outcome.overwrite:
            for name, value in payload.items():
                setattr(obj, name, value)
        else:
            differing = _differing_fields(obj, payload)
            if differing:
                outcome.preserve(entity, _conflict_key(payload), differing)
    db.flush()
    return count


def _conflict_key(payload: dict) -> str:
    return " / ".join(str(payload.get(part, "")) for part in ("a_code", "b_code", "conflict_type"))


def seed_hardware(db: Session, outcome: SeedOutcome) -> int:
    #: Внимание: переменная цикла не должна называться `payload` — она затеняет
    #: загруженный JSON, и второй цикл начинает перебирать поля последнего
    #: процессора вместо списка видеокарт. Из-за этого каталог GPU оставался
    #: пустым, хотя наполнение выполнялось без ошибок.
    entity_by_model = {HardwareCPU: "hardware_cpu", HardwareGPU: "hardware_gpu"}
    data = _load_json("hardware.json")
    if not isinstance(data, dict):
        outcome.skip("hardware_cpu", "hardware.json", "файл не содержит разделов cpu/gpu")
        return 0
    count = 0
    for model_cls, section in ((HardwareCPU, "cpu"), (HardwareGPU, "gpu")):
        entity = entity_by_model[model_cls]
        for row in data.get(section, []):
            if not row.get("model"):
                outcome.skip(entity, section, "строка без названия модели")
                continue
            # Внешний источник может честно оставить характеристику неизвестной
            # (например, bandwidth у мобильной или встроенной графики). Не
            # записываем NULL в существующую NOT NULL-колонку: для новой записи
            # сработает нейтральный default модели, для существующей сохраняется
            # последнее валидное значение.
            fields = {
                k: v for k, v in row.items()
                if hasattr(model_cls, k) and v is not None
            }
            fields.setdefault("status", PUBLISHED)
            _, created = _upsert(db, model_cls, "model", fields, outcome=outcome, entity=entity)
            count += int(created)
    db.flush()
    return count


def validate_knowledge_base(db: Session) -> list[dict]:
    """Проверка целостности базы знаний. Результат сохраняется для админ-раздела."""
    issues: list[dict] = []

    db.query(ValidationIssue).delete()

    methods = list(db.scalars(select(Method)))
    method_codes = {m.code for m in methods}
    tools = list(db.scalars(select(EngineTool)))
    tool_codes = {t.code for t in tools}
    cpus = list(db.scalars(select(HardwareCPU)))
    gpus = list(db.scalars(select(HardwareGPU)))

    def add(entity: str, code: str, severity: str, message: str) -> None:
        issues.append({"entity": entity, "entity_code": code, "severity": severity, "message": message})
        db.add(ValidationIssue(entity=entity, entity_code=code, severity=severity, message=message))

    # 1. У опубликованной записи должен быть источник.
    for m in methods:
        if m.status == "published" and not m.source_url:
            add("method", m.code, "error", "Опубликованный метод не имеет источника.")

    for fn in db.scalars(select(GameFunction)):
        if fn.status == "published" and not fn.source_url:
            add("game_function", fn.code, "error", "Опубликованная функция не имеет источника.")

    # 2. Связи должны ссылаться на существующие методы и инструменты.
    for link in db.scalars(select(MethodEngineLink)):
        method = db.get(Method, link.method_id)
        tool = db.get(EngineTool, link.tool_id)
        if method is None or tool is None:
            add("method_engine_link", str(link.id), "error", "Связь ссылается на несуществующую запись.")
        elif method.code not in method_codes or tool.code not in tool_codes:
            add("method_engine_link", str(link.id), "warning", "Связь ссылается на запись вне каталога.")

    # 3. Конфликты должны ссылаться на существующие методы.
    for c in db.scalars(select(Conflict)):
        if c.a_code not in method_codes:
            add("conflict", c.a_code, "error", f"Метод {c.a_code} в конфликте не найден.")
        if c.b_code not in method_codes:
            add("conflict", c.b_code, "error", f"Метод {c.b_code} в конфликте не найден.")

    # 4. У каждого метода должна быть связь хотя бы с одним движком.
    # Исключение — решения, не опирающиеся на встроенный инструмент: для них
    # отсутствие связи обосновано. Без этого различия предупреждение было бы
    # ложным для каждого такого метода, а настоящий пробел в данных тонул
    # в их числе. Обратное противоречие (признак есть и связи есть) — ошибка.
    # `db.get` возвращает None, если связь ссылается на удалённую запись;
    # прежнее прямое `.code` на результате роняло всю валидацию на одной
    # висячей строке вместо того, чтобы сообщить о ней (сообщение о висячей
    # связи уже выдаётся выше, в блоке проверки связей).
    linked = {
        method.code
        for link in db.scalars(select(MethodEngineLink))
        if (method := db.get(Method, link.method_id)) is not None
    }
    for m in methods:
        if m.code in linked:
            if m.engine_tool_independent:
                add("method", m.code, "error",
                    "Метод помечен не зависящим от инструментов движка, но связи есть.")
        elif not m.engine_tool_independent:
            add("method", m.code, "warning", "У метода нет связей с инструментами движков.")

    # 5. Оборудование: контроль нормализованных индексов.
    for cpu in cpus:
        if not (0.0 <= cpu.single_thread_score <= 1.0 and 0.0 <= cpu.multi_thread_score <= 1.0):
            add("hardware_cpu", cpu.model, "error", "Нормализованный индекс вне диапазона 0..1.")
        if not cpu.source_url:
            add("hardware_cpu", cpu.model, "error", "Отсутствует источник данных.")
    for gpu in gpus:
        if not (0.0 <= gpu.raster_score <= 1.0 and 0.0 <= gpu.rt_score <= 1.0):
            add("hardware_gpu", gpu.model, "error", "Нормализованный индекс вне диапазона 0..1.")
        if not gpu.source_url:
            add("hardware_gpu", gpu.model, "error", "Отсутствует источник данных.")

    # 6. Доказательства: источник и локатор различаются, а числовой claim
    # с экспертным основанием не считается измеренным только из-за URL.
    sources = list(db.scalars(select(EvidenceSource)))
    source_by_id = {source.id: source for source in sources}
    for source in sources:
        if source.status == PUBLISHED and not source.url:
            add("evidence_source", source.code, "error", "Опубликованный источник не имеет URL.")
    for claim in db.scalars(select(EvidenceClaim)):
        if claim.status != PUBLISHED:
            continue
        source = source_by_id.get(claim.source_id) if claim.source_id else None
        if claim.source_id and source is None:
            add("evidence_claim", claim.code, "error", "Claim ссылается на несуществующий источник.")
        # Источник, оставшийся черновиком, при выдаче обнуляется: `source_to_out`
        # возвращает None для неопубликованного источника. Публичное утверждение
        # тогда выглядит как утверждение без источника, хотя ссылка в базе есть,
        # — то есть ровно как нарушение «запись без обязательного источника не
        # публикуется». Пробел относится к источнику, а не к утверждению, поэтому
        # сообщение указывает на источник.
        if source is not None and source.status != PUBLISHED:
            add(
                "evidence_source", source.code, "warning",
                "Публичное утверждение опирается на источник в статусе черновика: "
                "при выдаче ссылка обнуляется.",
            )
        # A documented/measured/case claim needs an external source and a
        # locator. A derived claim can be self-provenanced by its explicit
        # formula and input parameters: the calculation is reproducible even
        # when no publication asserts the resulting number.
        externally_supported = claim.basis in {"documented", "measured", "case_evidence"}
        self_contained_derived = (
            claim.basis == "derived" and bool(claim.formula)
            and bool(claim.input_parameters) and bool(claim.locator)
        )
        if externally_supported and (source is None or not claim.locator):
            add("evidence_claim", claim.code, "warning", "У claim нет одновременно источника и проверяемого локатора.")
        elif claim.basis == "derived" and not self_contained_derived and (source is None or not claim.locator):
            add("evidence_claim", claim.code, "warning", "У derived claim нет источника либо воспроизводимой формулы и входных параметров.")

    nodes = list(db.scalars(select(TechnologyNode)))
    node_ids = {node.id for node in nodes}
    for edge in db.scalars(select(DependencyEdge)):
        if edge.status == PUBLISHED and (edge.source_node_id not in node_ids or edge.target_node_id not in node_ids):
            add("dependency_edge", str(edge.id), "error", "Зависимость ссылается на несуществующий узел.")

    for method in methods:
        if method.status == PUBLISHED and method.recommended_stage not in _DEV_STAGES:
            add(
                "method", method.code, "error",
                f"Рекомендованная стадия «{method.recommended_stage}» не является "
                f"кодом этапа. Допустимо: {', '.join(sorted(_DEV_STAGES))}.",
            )

    # 7. Минимальное наполнение MVP.
    if len(methods) < 40:
        add("knowledge_base", "methods", "warning", f"Методов меньше рекомендуемых 40: {len(methods)}.")
    if len(cpus) < 30:
        add("knowledge_base", "hardware_cpu", "warning", f"CPU меньше рекомендуемых 30: {len(cpus)}.")
    if len(gpus) < 30:
        add("knowledge_base", "hardware_gpu", "warning", f"GPU меньше рекомендуемых 30: {len(gpus)}.")

    db.flush()
    return issues


def seed_all(db: Session, validate: bool = True, overwrite: bool = False) -> dict:
    """Заполнить базу демонстрационными данными.

    `overwrite=True` — явное восстановление демоданных: существующие записи
    заменяются. Без него правки администратора сохраняются, а все расхождения
    попадают в отчёт, чтобы потеря исправлений не осталась незамеченной.
    """
    outcome = SeedOutcome(overwrite=overwrite)
    functions = seed_functions(db, outcome)
    methods = seed_methods(db, functions, outcome)
    engines = seed_engines(db, outcome)
    tools = seed_engine_tools(db, engines, outcome)
    links = seed_method_links(db, methods, tools, outcome)
    conflicts = seed_conflicts(db, outcome)
    hardware = seed_hardware(db, outcome)
    # Пачка исправлений v2 — тот же проход, что выполняет стартовая синхронизация
    # (`sync_function_taxonomy`). Без него свежая база отличалась от базы,
    # прошедшей хотя бы один старт приложения: у 13 методов не поднимался
    # `confidence` и оставался на значении по умолчанию 0.5 при наличии
    # опубликованного источника, не исправлялась пара «название — URL» (1 запись)
    # и не проставлялись сырые значения бенчмарков железа. Функция идемпотентна:
    # повторный вызов ничего не меняет.
    from .fixes_v2 import apply_all as apply_fixes_v2
    fixes_v2 = apply_fixes_v2(db)
    # Записи, сохранённые до появления области эффекта, получают явные значения
    # каталога: иначе исправление расчёта действует только на новые базы.
    scopes_corrected = correct_effect_scopes(db)
    splitscreen_corrected = correct_splitscreen_dependency(db)
    legacy_conflicts = correct_legacy_conflict_types(db)
    # Типы связей меняют расчёт целиком, поэтому приводятся к актуальному
    # смыслу каталога и в уже существующих базах.
    relations_corrected = correct_relation_types(db)
    # Связи, противоречащие другой связи той же пары, снимаются и в уже
    # существующих базах: иначе база, собранная с нуля, и база, обновлённая
    # сидом, расходятся по составу корзины.
    contradictory_relations_removed = correct_contradictory_relations(db)
    # Источники, подобранные по названию, а не по механизму, заменяются и в
    # уже существующих базах: ссылка — часть обоснования карточки.
    sources_corrected = correct_method_sources(db)
    # Подставные даты публикации заменяются на объявленные значения из реестра:
    # `sync_sources` не перезаписывает уже заполненное поле, поэтому без явного
    # прохода унаследованная база сохраняла прежние заглушки.
    source_dates_corrected = correct_placeholder_source_dates(db)
    # Записи источников, починенные каталогом: `_upsert_source` существующую
    # строку не обновляет, поэтому без этого прохода свежая установка и уже
    # собранная база расходились бы по содержанию записи.
    source_records_corrected = correct_source_records(db)
    independence_corrected = correct_engine_tool_independence(db)
    from .verified_corrections import correct_existing
    verified_fields_corrected = correct_existing(db)
    from .evidence_catalog import sync_all as sync_evidence_catalog
    evidence = sync_evidence_catalog(db)
    # Источники, перенесённые из пакетов, по умолчанию оставались черновиками и
    # обнулялись при выдаче: публичное утверждение выглядело как утверждение без
    # источника. Публикуется только тот источник, на который уже ссылается
    # публичное утверждение или факт кейса.
    sources_published = correct_source_publication(db)
    db.flush()
    db.commit()
    # Повторная загрузка пакетов: разделы доказательств (инструменты движков,
    # узлы технологий, стадии, профили нагрузки, сетевые режимы, риски,
    # целевые метрики и платформы) ссылаются на сущности, которые создаются
    # позже первого вызова sync_packs. Без этого прохода такие утверждения
    # записывались только при повторном заполнении базы, то есть в свежей
    # установке их не было вовсе. Функция идемпотентна: уже существующие
    # записи возвращаются как есть, дубликатов не создаётся.
    from .pack_loader import sync_packs
    pack_stats = sync_packs(db)
    for key, value in pack_stats.items():
        evidence[key] = evidence.get(key, 0) + value
    db.flush()
    db.commit()
    # Граф зависимостей строится последним: ему нужны и узлы технологий, и
    # связи «метод-метод» из загруженных пакетов.
    from .dependency_graph import (
        break_dependency_cycles, dedupe_symmetric_relations, sync_dependency_graph,
    )
    graph_stats = sync_dependency_graph(db)
    # Перевёрнутые обязательные связи снимаются до разрыва циклов: пока они на
    # месте, разрыв понижает верное ребро, а не перевёрнутое.
    graph_stats["reversed_physics_dependencies_corrected"] = (
        correct_reversed_physics_dependencies(db)
    )
    graph_stats.update(break_dependency_cycles(db))
    # Повторная загрузка пакетов добавляет связи «метод-метод», часть которых
    # образует взаимные предусловия. Обязательное ребро в цикле неразрешимо —
    # ни один метод в нём нельзя поставить в план, — поэтому циклы разрываются
    # ещё раз, уже после построения графа. Без этого шага свежая база
    # получала граф с циклами, который проходил проверки только потому, что
    # первая загрузка пакетов не успевала создать спорные рёбра.
    for key, value in break_dependency_cycles(db).items():
        graph_stats[key] = graph_stats.get(key, 0) + value
    # Симметричная связь, записанная в обе стороны, — дубль, а не два факта.
    # Проход убирает встречные записи, оставшиеся от прежних сборок; на базе,
    # собранной с нуля, он не находит ничего.
    graph_stats.update(dedupe_symmetric_relations(db))
    db.flush()
    db.commit()
    # Декларации пробелов — ДО заполнения решений. Проход ставит конфликтам без
    # источника маркер `user_defined:catalog_dependency`, а решение о базисе
    # принимается по этому полю (`derived` — связь с источником,
    # `expert_estimate` — пользовательская). Обратный порядок приводил к тому,
    # что 30 зависимостей каталога помечались как выведенные из документа,
    # хотя публичного источника у них нет: маркер ставился уже после того, как
    # основание было записано. Проход идемпотентен и заполняет только пустое.
    declarations = declare_evidence_gaps(db)
    db.flush()
    db.commit()
    # Решения связей — после разрыва циклов: пониженная связь уже получила
    # собственный текст, и он не должен быть перезаписан. Модуль заполняет
    # только пустые решения и переносит их в рёбра графа.
    from .relation_resolutions import apply_relation_resolutions
    resolutions = apply_relation_resolutions(db)
    db.flush()
    db.commit()
    issues = validate_knowledge_base(db) if validate else []
    db.commit()
    return {
        "functions": len(functions),
        "methods": len(methods),
        "engines": len(engines),
        "engine_tools": len(tools),
        "method_engine_links": links,
        "conflicts": conflicts,
        "hardware_records": hardware,
        "validation_issues": len(issues),
        "effect_scopes_corrected": scopes_corrected,
        "splitscreen_dependency_corrected": splitscreen_corrected,
        "legacy_conflict_types_corrected": legacy_conflicts,
        "relation_types_corrected": relations_corrected,
        "contradictory_relations_removed": contradictory_relations_removed,
        "method_sources_corrected": sources_corrected,
        "sources_published": sources_published,
        "source_dates_corrected": source_dates_corrected,
        "source_records_corrected": source_records_corrected,
        "engine_tool_independence_corrected": independence_corrected,
        "verified_fields_corrected": verified_fields_corrected,
        **fixes_v2,
        **evidence,
        **graph_stats,
        **resolutions,
        **declarations,
        **outcome.as_report(),
    }


def is_empty(db: Session) -> bool:
    return db.scalar(select(Method.id).limit(1)) is None
