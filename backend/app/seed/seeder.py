"""Заполнение базы знаний демонстрационными данными MVP.

Операция идемпотентна: существующие записи обновляются, новые добавляются.
Данные по оборудованию и примерам игр читаются из JSON-файлов (каталог seed/data),
что позволяет обновлять их без изменения кода.

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
    Conflict, Engine, EngineTool, GameFunction, HardwareCPU, HardwareGPU,
    Method, MethodEngineLink, ValidationIssue,
)
from ..models.enums import Status
from . import engines_data, functions_data, methods_data
from .corrections import (
    correct_effect_scopes, correct_legacy_conflict_types, correct_shadow_relation,
    correct_splitscreen_dependency,
)

PUBLISHED = Status.PUBLISHED.value

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
        function_code = data.pop("function_code", None)
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
    return {
        "functions_created": created_functions,
        "methods_linked": linked_methods,
        "method_metadata_updated": metadata_updated,
        "relations_corrected": correct_shadow_relation(db),
        "legacy_conflict_types_corrected": correct_legacy_conflict_types(db),
        "effect_scopes_corrected": correct_effect_scopes(db),
        "splitscreen_dependency_corrected": correct_splitscreen_dependency(db),
    }


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
        engine_code = data.pop("engine_code", None)
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
    linked = {db.get(Method, link.method_id).code for link in db.scalars(select(MethodEngineLink))}
    for m in methods:
        if m.code not in linked:
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

    # 6. Минимальное наполнение MVP.
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
    # Записи, сохранённые до появления области эффекта, получают явные значения
    # каталога: иначе исправление расчёта действует только на новые базы.
    scopes_corrected = correct_effect_scopes(db)
    splitscreen_corrected = correct_splitscreen_dependency(db)
    legacy_conflicts = correct_legacy_conflict_types(db)
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
        **outcome.as_report(),
    }


def is_empty(db: Session) -> bool:
    return db.scalar(select(Method.id).limit(1)) is None
