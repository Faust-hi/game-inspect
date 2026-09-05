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

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..config import DATA_DIR
from ..models.entities import (
    Conflict, Engine, EngineTool, GameExample, GameFunction, HardwareCPU, HardwareGPU,
    Method, MethodEngineLink, ValidationIssue,
)
from ..models.enums import Status
from . import engines_data, functions_data, methods_data

PUBLISHED = Status.PUBLISHED.value


def _load_json(name: str) -> list[dict]:
    path: pathlib.Path = DATA_DIR / name
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8"))


def _example_files() -> list[tuple[pathlib.Path, str]]:
    """Файлы примеров игр со статусом по умолчанию.

    Базовый файл и Трек 1 (по движкам) — опубликованный срез каталога.
    Трек 2 (игры-фуроры для аргументации отчёта) — черновики: они живут в базе
    для административного раздела, но не попадают в публичные рекомендации
    (репозиторий отдаёт только опубликованное). Новый файл добавляется без
    изменения кода (OCP), порядок детерминирован.
    """
    files: list[tuple[pathlib.Path, str]] = []
    base = DATA_DIR / "game_examples.json"
    if base.exists():
        files.append((base, PUBLISHED))
    track_dir = DATA_DIR / "track1"
    if track_dir.is_dir():
        files.extend((path, PUBLISHED) for path in sorted(track_dir.glob("*.json")))
    track2_dir = DATA_DIR / "track2"
    if track2_dir.is_dir():
        files.extend((path, Status.DRAFT.value) for path in sorted(track2_dir.glob("*.json")))
    return files


def _upsert(db: Session, model, key: str, values: dict):
    obj = db.scalar(select(model).where(getattr(model, key) == values[key]))
    if obj is None:
        obj = model(**values)
        db.add(obj)
        return obj, True
    for field, value in values.items():
        setattr(obj, field, value)
    return obj, False


def seed_functions(db: Session) -> dict[str, GameFunction]:
    out: dict[str, GameFunction] = {}
    for data in functions_data.with_sources():
        payload = {k: v for k, v in data.items() if hasattr(GameFunction, k)}
        payload.setdefault("status", PUBLISHED)
        obj, _ = _upsert(db, GameFunction, "code", payload)
        out[obj.code] = obj
    db.flush()
    return out


def seed_methods(db: Session, functions: dict[str, GameFunction]) -> dict[str, Method]:
    methods, _conflicts = methods_data.with_sources()
    out: dict[str, Method] = {}
    for data in methods:
        function_code = data.pop("function_code", None)
        payload = {k: v for k, v in data.items() if hasattr(Method, k) and k != "links"}
        payload.setdefault("status", PUBLISHED)
        if function_code and function_code in functions:
            payload["function_id"] = functions[function_code].id
        obj, _ = _upsert(db, Method, "code", payload)
        out[obj.code] = obj
    db.flush()
    return out


def seed_engines(db: Session) -> dict[str, Engine]:
    out: dict[str, Engine] = {}
    for data in engines_data.ENGINES:
        obj, _ = _upsert(db, Engine, "code", {**data, "status": PUBLISHED})
        out[obj.code] = obj
    db.flush()
    return out


def seed_engine_tools(db: Session, engines: dict[str, Engine]) -> dict[str, EngineTool]:
    out: dict[str, EngineTool] = {}
    for data in engines_data.ENGINE_TOOLS:
        engine_code = data.pop("engine_code", None)
        payload = {k: v for k, v in data.items() if hasattr(EngineTool, k)}
        payload.setdefault("status", PUBLISHED)
        if engine_code in engines:
            payload["engine_id"] = engines[engine_code].id
        obj, _ = _upsert(db, EngineTool, "code", payload)
        out[obj.code] = obj
    db.flush()
    return out


def seed_method_links(db: Session, methods: dict[str, Method], tools: dict[str, EngineTool]) -> int:
    count = 0
    for method_code, per_engine in methods_data.all_links().items():
        method = methods.get(method_code)
        if method is None:
            continue
        for engine_code, (tool_code, relation, note) in per_engine.items():
            tool = tools.get(tool_code)
            if tool is None:
                continue
            exists = db.scalar(
                select(MethodEngineLink).where(
                    MethodEngineLink.method_id == method.id,
                    MethodEngineLink.tool_id == tool.id,
                )
            )
            if exists:
                exists.relation_type = relation
                exists.note = note
                exists.source_url = tool.docs_url
                exists.status = PUBLISHED
            else:
                db.add(MethodEngineLink(
                    method_id=method.id, tool_id=tool.id,
                    relation_type=relation, note=note, source_url=tool.docs_url,
                    status=PUBLISHED,
                ))
                count += 1
    db.flush()
    return count


def seed_conflicts(db: Session) -> int:
    # Ключ апсерта — вся тройка (a_code, b_code, conflict_type), как в UNIQUE
    # uq_conflict_pair. Раньше ключом был один a_code: при повторном сиде вторая
    # запись с тем же a_code перезаписывала первую и падала с IntegrityError.
    _, conflicts = methods_data.with_sources()
    count = 0
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
        else:
            for field, value in payload.items():
                setattr(obj, field, value)
    db.flush()
    return count


def seed_examples(db: Session) -> int:
    count = 0
    for path, default_status in _example_files():
        try:
            rows = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if not isinstance(rows, list):
            continue
        for data in rows:
            if not isinstance(data, dict) or not data.get("source_url"):
                continue
            payload = {k: v for k, v in data.items() if hasattr(GameExample, k)}
            # Явный статус в файле важнее умолчания каталога: так Трек 2
            # остаётся черновиком, даже если запись уже была опубликована.
            if "status" not in payload:
                payload["status"] = default_status
            _, created = _upsert(db, GameExample, "title", payload)
            if created:
                count += 1
        # Сброс после каждого файла: _upsert ищет через SELECT, а незафлашенные
        # вставки того же title из прошлого файла он не увидит — будет дубль.
        # Порядок файлов детерминирован, поэтому track1/* побеждает legacy.
        db.flush()
    return count


def seed_hardware(db: Session) -> int:
    #: Внимание: переменная цикла не должна называться `payload` — она затеняет
    #: загруженный JSON, и второй цикл начинает перебирать поля последнего
    #: процессора вместо списка видеокарт. Из-за этого каталог GPU оставался
    #: пустым, хотя наполнение выполнялось без ошибок.
    data = _load_json("hardware.json")
    if not isinstance(data, dict):
        return 0
    count = 0
    for model_cls, section in ((HardwareCPU, "cpu"), (HardwareGPU, "gpu")):
        for row in data.get(section, []):
            if not row.get("model"):
                continue
            fields = {k: v for k, v in row.items() if hasattr(model_cls, k)}
            fields.setdefault("status", PUBLISHED)
            _, created = _upsert(db, model_cls, "model", fields)
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

    for ex in db.scalars(select(GameExample)):
        if ex.status == "published" and not ex.source_url:
            add("game_example", ex.title, "error", "Опубликованный пример игры не имеет источника.")

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


def seed_all(db: Session, validate: bool = True) -> dict:
    functions = seed_functions(db)
    methods = seed_methods(db, functions)
    engines = seed_engines(db)
    tools = seed_engine_tools(db, engines)
    links = seed_method_links(db, methods, tools)
    conflicts = seed_conflicts(db)
    examples = seed_examples(db)
    hardware = seed_hardware(db)
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
        "game_examples": examples,
        "hardware_records": hardware,
        "validation_issues": len(issues),
    }


def is_empty(db: Session) -> bool:
    return db.scalar(select(Method.id).limit(1)) is None
