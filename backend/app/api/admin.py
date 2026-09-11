"""Административный раздел: наполнение, проверка и публикация базы знаний."""
from __future__ import annotations

import csv
import io
import json
import logging
from typing import Any

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..config import settings
from ..database import get_db
from ..errors import ApiError, ErrorCode
from ..models.entities import (
    Conflict, Engine, EngineTool, GameFunction, HardwareCPU, HardwareGPU,
    Method, MethodEngineLink, PublicationLog, ValidationIssue,
)
from ..models.enums import Status
from ..schemas.import_rows import (
    CONFLICT_KEY_FIELDS, as_str_list, list_columns, normalize_row, row_key,
)
from .. import repositories
from ..seed import seeder
from ..services import publication
from .catalog import method_to_out

logger = logging.getLogger("gamedev_dss.admin")

# Локальное приложение: административный раздел открыт без токена.
router = APIRouter(prefix="/admin", tags=["Администрирование"])


# ---------------------------------------------------------------------------
# Обзор и целостность
# ---------------------------------------------------------------------------
@router.get("/overview", summary="Сводка по наполнению базы")
def overview(db: Session = Depends(get_db)):
    counts = {
        "game_functions": db.scalar(select(func.count(GameFunction.id))),
        "methods": db.scalar(select(func.count(Method.id))),
        "methods_published": db.scalar(select(func.count(Method.id)).where(Method.status == "published")),
        "engines": db.scalar(select(func.count(Engine.id))),
        "engine_tools": db.scalar(select(func.count(EngineTool.id))),
        "method_engine_links": db.scalar(select(func.count(MethodEngineLink.id))),
        "conflicts": db.scalar(select(func.count(Conflict.id))),
        "hardware_cpu": db.scalar(select(func.count(HardwareCPU.id))),
        "hardware_gpu": db.scalar(select(func.count(HardwareGPU.id))),
    }
    issues = db.scalars(select(ValidationIssue).order_by(ValidationIssue.severity)).all()
    return {
        "counts": counts,
        # Снимок опубликованных записей — отдельным полем, а не внутри counts:
        # фронт рендерит каждое значение counts как число, вложенный словарь
        # ронял вкладку администрирования («Objects are not valid as a React child»).
        "published": repositories.published_snapshot_counts(db),
        "issues": [
            {"entity": i.entity, "entity_code": i.entity_code, "severity": i.severity, "message": i.message}
            for i in issues
        ],
        "issues_by_severity": {
            "error": sum(1 for i in issues if i.severity == "error"),
            "warning": sum(1 for i in issues if i.severity == "warning"),
        },
    }


@router.post("/validate", summary="Проверить целостность базы знаний")
def validate(db: Session = Depends(get_db)):
    issues = seeder.validate_knowledge_base(db)
    db.commit()
    return {"issues": issues, "total": len(issues)}


class SeedIn(BaseModel):
    """Запрос на заполнение демонстрационными данными.

    `restore_demo` — явное согласие заменить существующие записи. Без него
    повторное заполнение сохраняет административные правки и сообщает о
    расхождениях: иначе исправления каталога исчезают без предупреждения.
    """

    restore_demo: bool = False
    #: Имя отлично от `validate`: это имя занято методом BaseModel.
    run_validation: bool = True


@router.post("/seed", summary="Заполнить базу демонстрационными данными")
def run_seed(payload: SeedIn = SeedIn(), db: Session = Depends(get_db)):
    return seeder.seed_all(
        db, validate=payload.run_validation, overwrite=payload.restore_demo
    )


# ---------------------------------------------------------------------------
# Работа с методами
# ---------------------------------------------------------------------------
class MethodIn(BaseModel):
    """Поля метода, доступные администратору.

    Ограничения заданы не для удобства, а потому что значения попадают прямо в
    матрицу TOPSIS: влияние 999 или достоверность вне 0..1 делают несравнимыми
    все остальные записи.
    """

    code: str = Field(min_length=1, max_length=64, pattern=r"^[A-Za-z0-9_.-]+$")
    name: str = Field(min_length=1, max_length=200)
    kind: str = "optimization"
    function_code: str | None = None
    summary: str = Field(default="", max_length=1000)
    description: str = ""
    problem: str = ""
    level: str = "algorithm"
    recommended_stage: str = "prototype"
    late_cost: str = "medium"
    calc_mode: str = "realtime"
    effect_scope: str = "client"
    impact_cpu: int = Field(default=0, ge=-3, le=3)
    impact_gpu: int = Field(default=0, ge=-3, le=3)
    impact_ram: int = Field(default=0, ge=-3, le=3)
    impact_vram: int = Field(default=0, ge=-3, le=3)
    impact_disk: int = Field(default=0, ge=-3, le=3)
    impact_network: int = Field(default=0, ge=-3, le=3)
    quality_impact: int = Field(default=0, ge=-2, le=2)
    concept_impact: int = Field(default=0, ge=-2, le=0)
    performance_gain: float = Field(default=0.5, ge=0.0, le=1.0)
    implementation_cost: int = Field(default=3, ge=1, le=5)
    complexity: int = Field(default=3, ge=1, le=5)
    confidence: float = Field(default=0.7, ge=0.0, le=1.0)
    requires_prototype: bool = False
    applicable_formats: list[str] = Field(default_factory=list, max_length=8)
    applicable_world_types: list[str] = Field(default_factory=list, max_length=12)
    applicable_engines: list[str] = Field(default_factory=list, max_length=12)
    applicable_platforms: list[str] = Field(default_factory=list, max_length=16)
    requires_features: list[str] = Field(default_factory=list, max_length=24)
    requires_hw_features: list[str] = Field(default_factory=list, max_length=16)
    requires_conditions: list[str] = Field(default_factory=list, max_length=24)
    min_scale: str | None = None
    pros: list[str] = Field(default_factory=list, max_length=24)
    cons: list[str] = Field(default_factory=list, max_length=24)
    limitations: list[str] = Field(default_factory=list, max_length=24)
    verification_method: str = ""
    verification_tools: list[str] = Field(default_factory=list, max_length=24)
    application_steps: list[str] = Field(default_factory=list, max_length=24)
    source_title: str = Field(default="", max_length=300)
    source_url: str = Field(default="", max_length=600)
    source_date: str = Field(default="", max_length=20)

    @field_validator("source_url")
    @classmethod
    def _url_scheme(cls, v: str) -> str:
        if v and not publication.is_valid_url(v):
            raise ValueError("ссылка на источник должна начинаться с http:// или https://")
        return v


class StatusIn(BaseModel):
    status: str
    comment: str = ""


@router.get("/methods", summary="Список методов со всеми статусами")
def admin_methods(db: Session = Depends(get_db)):
    rows = db.scalars(select(Method).order_by(Method.code)).all()

    return [method_to_out(db, m) for m in rows]


@router.post("/methods", summary="Добавить или обновить метод")
def upsert_method(payload: MethodIn, db: Session = Depends(get_db)):
    """Новая запись всегда создаётся черновиком.

    Раньше запись получала статус по умолчанию из модели — «опубликовано», —
    то есть непроверенный материал сразу попадал в публичные рекомендации.
    """
    data = payload.model_dump()
    function_code = data.pop("function_code", None)
    if function_code:
        fn = db.scalar(select(GameFunction).where(GameFunction.code == function_code))
        if fn:
            data["function_id"] = fn.id

    problems = publication.record_problems(Method, data)
    if problems:
        raise ApiError(
            "Запись отклонена",
            code=ErrorCode.PUBLICATION_REJECTED,
            status=422,
            details=publication.deduplicate(problems),
        )

    obj = db.scalar(select(Method).where(Method.code == payload.code))
    if obj is None:
        data["status"] = Status.DRAFT.value
        obj = Method(**data)
        db.add(obj)
        created = True
    else:
        data.pop("status", None)
        was_published = obj.status == Status.PUBLISHED.value
        changed = _has_substantive_change(obj, data)
        for key, value in data.items():
            setattr(obj, key, value)
        created = False
        if was_published:
            # Правка опубликованной записи обязана сохранять требования
            # публикации. Иначе штатным API можно убрать источник и оставить
            # запись опубликованной: главный контракт каталога нарушается.
            has_links = db.scalar(
                select(func.count(MethodEngineLink.id)).where(
                    MethodEngineLink.method_id == obj.id,
                    MethodEngineLink.status == Status.PUBLISHED.value,
                )
            ) or 0
            problems = publication.publication_problems(obj, has_links=has_links > 0)
            if problems:
                db.rollback()
                raise ApiError(
                    "Правка нарушает требования к публикации",
                    code=ErrorCode.PUBLICATION_REJECTED,
                    status=409,
                    details=publication.deduplicate(problems),
                )
            if changed:
                # Содержательная правка снимает прежнее подтверждение: запись
                # уходит на повторную проверку, а не остаётся подтверждённой.
                obj.status = Status.REVIEWED.value
                db.add(PublicationLog(
                    entity=Method.__tablename__, entity_code=obj.code,
                    from_status=Status.PUBLISHED.value, to_status=Status.REVIEWED.value,
                    actor="admin", comment="Содержательная правка опубликованной записи",
                ))
    try:
        db.commit()
    except Exception:  # noqa: BLE001 — нарушение ограничения БД
        db.rollback()
        logger.exception("Не удалось сохранить метод %s", payload.code)
        raise HTTPException(409, "Запись не сохранена: нарушено ограничение базы данных")
    return {"created": created, "code": obj.code, "status": obj.status}


@router.patch("/methods/{code}/status", summary="Изменить статус записи (черновик → проверено → опубликовано)")
def set_method_status(code: str, payload: StatusIn, db: Session = Depends(get_db)):
    """Изменение статуса с соблюдением жизненного цикла.

    Публикация — не просто запись значения: проверяется допустимость перехода,
    наличие источника, диапазоны оценок и связи с инструментами движков.
    """
    obj = db.scalar(select(Method).where(Method.code == code))
    if not obj:
        raise HTTPException(404, "Метод не найден")

    rejection = publication.transition_error(obj.status, payload.status)
    if rejection:
        raise HTTPException(409, rejection)

    # Повторная установка текущего статуса: ничего не меняем и не пишем в журнал.
    if obj.status == payload.status:
        return {"code": obj.code, "status": obj.status, "previous_status": obj.status}

    if payload.status == Status.PUBLISHED.value:
        problems = publication.publication_problems(
            obj, has_links=_has_published_links(db, obj)
        )
        if problems:
            raise ApiError(
                "Публикация невозможна",
                code=ErrorCode.PUBLICATION_REJECTED,
                status=422,
                details=publication.deduplicate(problems),
            )

    previous = obj.status
    obj.status = payload.status
    db.add(PublicationLog(
        entity=Method.__tablename__, entity_code=obj.code,
        from_status=previous, to_status=payload.status,
        actor="admin", comment=payload.comment,
    ))
    db.commit()
    return {"code": obj.code, "status": obj.status, "previous_status": previous}


# ---------------------------------------------------------------------------
# Жизненный цикл всех сущностей каталога
# ---------------------------------------------------------------------------
# Раньше смена статуса работала только для методов: движок, инструмент, пример
# или процессор, добавленные через каталог, оставались черновиками навсегда,
# и расширение базы «без кода» не выполнялось. Обращение по идентификатору, а
# не по естественному ключу, потому что у конфликта и у связи метода с
# инструментом естественный ключ составной или вовсе отсутствует.
@router.get("/entities", summary="Сущности каталога, участвующие в публикации")
def list_entities():
    return [
        {"entity": code, "label": policy.label, "key_fields": list(policy.key_fields)}
        for code, policy in publication.ENTITY_POLICIES.items()
    ]


@router.get("/entities/{entity}", summary="Записи сущности с их статусами")
def list_entity_records(entity: str, db: Session = Depends(get_db)):
    policy = publication.policy_for(entity)
    if policy is None:
        raise HTTPException(404, f"Сущность каталога не поддерживает публикацию: {entity}")
    rows = db.scalars(select(policy.model).order_by(policy.model.id)).all()
    return [
        {
            "id": row.id,
            "key": publication.entity_key(row, policy),
            "status": row.status,
            "allowed_transitions": sorted(publication.allowed_targets(row.status)),
        }
        for row in rows
    ]


@router.patch(
    "/entities/{entity}/{entity_id}/status",
    summary="Изменить статус любой записи каталога",
)
def set_entity_status(
    entity: str, entity_id: int, payload: StatusIn, db: Session = Depends(get_db),
):
    policy = publication.policy_for(entity)
    if policy is None:
        raise HTTPException(404, f"Сущность каталога не поддерживает публикацию: {entity}")

    obj = db.get(policy.model, entity_id)
    if obj is None:
        raise HTTPException(404, f"{policy.label} с идентификатором {entity_id} не найден")

    rejection = publication.transition_error(obj.status, payload.status)
    if rejection:
        raise HTTPException(409, rejection)

    # Повторная установка текущего статуса: ничего не меняем и не пишем в журнал.
    if obj.status == payload.status:
        return {"entity": entity, "id": entity_id, "status": obj.status, "changed": False}

    if payload.status == Status.PUBLISHED.value:
        has_links = _has_published_links(db, obj) if policy.requires_links else True
        problems = publication.publication_problems(obj, has_links=has_links)
        if problems:
            raise ApiError(
                "Публикация невозможна",
                code=ErrorCode.PUBLICATION_REJECTED,
                status=422,
                details=publication.deduplicate(problems),
            )

    previous = obj.status
    obj.status = payload.status
    db.add(PublicationLog(
        entity=entity, entity_code=publication.entity_key(obj, policy),
        from_status=previous, to_status=payload.status,
        actor="admin", comment=payload.comment,
    ))
    try:
        db.commit()
    except Exception:  # noqa: BLE001 — нарушение ограничения БД
        db.rollback()
        logger.exception("Не удалось изменить статус %s #%s", entity, entity_id)
        raise HTTPException(409, "Статус не изменён: нарушено ограничение базы данных")
    return {
        "entity": entity, "id": entity_id, "status": obj.status,
        "previous_status": previous, "changed": True,
    }


def _has_published_links(db: Session, obj) -> bool:
    """Есть ли у метода хотя бы одна опубликованная связь с инструментом.

    Черновая связь не делает метод пригодным к публикации: пользователь её
    не увидит, а карточка метода окажется без способа реализации.
    """
    count = db.scalar(
        select(func.count(MethodEngineLink.id)).where(
            MethodEngineLink.method_id == obj.id,
            MethodEngineLink.status == Status.PUBLISHED.value,
        )
    )
    return bool(count)


@router.get("/publication-log", summary="Журнал изменений статусов")
def publication_log(
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db),
):
    rows = db.scalars(
        select(PublicationLog).order_by(PublicationLog.created_at.desc()).limit(limit)
    ).all()
    return [
        {
            "entity": row.entity,
            "entity_code": row.entity_code,
            "from_status": row.from_status,
            "to_status": row.to_status,
            "actor": row.actor,
            "comment": row.comment,
            "created_at": row.created_at.isoformat(),
        }
        for row in rows
    ]


@router.delete("/methods/{code}", summary="Удалить метод")
def delete_method(code: str, db: Session = Depends(get_db)):
    obj = db.scalar(select(Method).where(Method.code == code))
    if not obj:
        raise HTTPException(404, "Метод не найден")
    db.delete(obj)
    db.commit()
    return {"deleted": code}


# ---------------------------------------------------------------------------
# Связи методов с инструментами движков
# ---------------------------------------------------------------------------
class LinkIn(BaseModel):
    method_code: str
    tool_code: str
    relation_type: str = "direct"
    note: str = ""


@router.post("/links", summary="Связать метод с инструментом движка")
def upsert_link(payload: LinkIn, db: Session = Depends(get_db)):
    method = db.scalar(select(Method).where(Method.code == payload.method_code))
    tool = db.scalar(select(EngineTool).where(EngineTool.code == payload.tool_code))
    if not method or not tool:
        raise HTTPException(404, "Метод или инструмент не найден")
    link = db.scalar(
        select(MethodEngineLink).where(
            MethodEngineLink.method_id == method.id, MethodEngineLink.tool_id == tool.id
        )
    )
    if link is None:
        # Связь — вспомогательная запись без собственного цикла проверки: она
        # существует только в контексте метода и публикуется вместе с ним.
        # Черновиком связь становится только при импорте, как и любой материал.
        db.add(MethodEngineLink(
            method_id=method.id, tool_id=tool.id,
            relation_type=payload.relation_type, note=payload.note, source_url=tool.docs_url,
            status=Status.PUBLISHED.value,
        ))
    else:
        link.relation_type = payload.relation_type
        link.note = payload.note
    db.commit()
    return {"method": payload.method_code, "tool": payload.tool_code, "relation": payload.relation_type}


# ---------------------------------------------------------------------------
# Импорт данных CSV / JSON
# ---------------------------------------------------------------------------
SUPPORTED_IMPORT = {
    "methods": Method,
    "game_functions": GameFunction,
    "engine_tools": EngineTool,
    "hardware_cpu": HardwareCPU,
    "hardware_gpu": HardwareGPU,
    "conflicts": Conflict,
}


def _coerce(model, row: dict[str, Any], list_fields: frozenset[str] = frozenset()) -> dict[str, Any]:
    """Привести значения строки к типам колонок модели.

    `list_fields` передаётся снаружи, потому что тип JSON-колонки в SQLAlchemy
    определить нельзя: `python_type` у неё равен `dict` для любого содержимого.
    """
    result = {}
    for column in model.__table__.columns:
        if column.name not in row:
            continue
        value = row[column.name]
        if column.name in list_fields:
            value = as_str_list(value)
        if column.type.python_type is int and isinstance(value, str):
            text = value.strip()
            if text == "":
                # Пустая ячейка CSV — поле не задано: пусть действует default
                # модели, а не изобретённый 0 (для cost/gain 0 вне диапазона
                # и ранее отклонялся бы, а для impact маскировался бы под "без
                # влияния"). Пропуск честнее выдумки.
                continue
            if not text.lstrip("-").isdigit():
                raise ValueError(f"поле «{column.name}» должно быть целым числом, получено {value!r}")
            value = int(text)
        if column.type.python_type is float and isinstance(value, str):
            text = value.strip()
            if text == "":
                continue
            try:
                value = float(text)
            except ValueError:
                raise ValueError(f"поле «{column.name}» должно быть числом, получено {value!r}")
        if column.type.python_type is bool and isinstance(value, str):
            token = value.strip().lower()
            if token == "":
                # Пустая ячейка — «не указано», а не «нет»: значение не
                # подставляется, остаётся прежнее (или модельное по умолчанию).
                continue
            if token in ("1", "true", "yes", "да"):
                value = True
            elif token in ("0", "false", "no", "нет"):
                value = False
            else:
                # Раньше любое нераспознанное слово молча становилось False
                # (включая опечатку «ture»): импорт принимал ошибку за ответ.
                raise ValueError(
                    f"поле «{column.name}» должно быть логическим (true/false), получено {value!r}"
                )
        result[column.name] = value
    return result


def _read_rows(raw: bytes, filename: str | None, entity: str) -> list[dict[str, Any]]:
    """Разобрать импортируемый файл. Ошибка формата отклоняет весь импорт."""
    if filename and filename.lower().endswith(".json"):
        payload = json_loads(raw)
        if isinstance(payload, dict):
            # Объект без раздела нужной сущности — это ошибка формата, а не
            # пустой импорт: раньше он давал `created=0` и код 200, хотя
            # документация обещает отклонить некорректный файл целиком.
            if entity not in payload:
                raise HTTPException(
                    400,
                    f"В JSON нет раздела «{entity}». Ожидался объект с ключом «{entity}» "
                    "или массив записей.",
                )
            rows = payload[entity]
        else:
            rows = payload
    else:
        rows = list(csv.DictReader(io.StringIO(raw.decode("utf-8-sig"))))
    if not isinstance(rows, list):
        raise HTTPException(400, "Ожидался список записей")
    if len(rows) > settings.IMPORT_MAX_ROWS:
        raise HTTPException(
            413,
            f"Слишком много записей: {len(rows)}. Предел — {settings.IMPORT_MAX_ROWS}.",
        )
    for row in rows:
        if not isinstance(row, dict):
            raise HTTPException(400, "Каждая запись должна быть объектом")
    return rows


def _validate_rows(
    model, rows: list[dict[str, Any]], entity: str, key_label: str, db: Session,
) -> list[str]:
    """Проверить все строки до первой записи в базу.

    Возвращает список найденных нарушений. Проверка выполняется заранее, чтобы
    частично некорректный файл не оставлял в базе половину изменений.
    Ссылки связей проверяются против текущего каталога: связь на несуществующий
    метод отклоняется, а не сохраняется висячей строкой.
    """
    from pydantic import ValidationError

    list_fields = list_columns(entity)
    problems: list[str] = []
    seen: set[str] = set()
    method_codes: set[str] | None = None
    if entity == "conflicts":
        # Один запрос на весь файл: состав файла не меняет каталог методов,
        # импорт сущностей выполняется отдельными файлами.
        method_codes = set(db.scalars(select(Method.code)).all())
    for index, row in enumerate(rows, start=1):
        key = row_key(entity, row)
        if not key:
            problems.append(f"Строка {index}: не указан ключ «{key_label}».")
            continue
        if key in seen:
            problems.append(f"Строка {index}: ключ «{key}» повторяется внутри файла.")
        seen.add(key)
        try:
            row = {**row, **normalize_row(entity, row)}
        except ValidationError as exc:
            for item in exc.errors()[:5]:
                field = ".".join(str(part) for part in item.get("loc", ()))
                problems.append(f"Строка {index} ({key}): поле «{field}» — {item.get('msg', '')}.")
            continue
        try:
            data = _coerce(model, row, list_fields)
        except (TypeError, ValueError) as exc:
            problems.append(f"Строка {index} ({key}): значение не распознано — {exc}.")
            continue
        if entity == "conflicts" and method_codes is not None:
            problems.extend(
                _conflict_reference_problems(data, method_codes, index, key)
            )
        problems.extend(
            f"Строка {index} ({key}): {message}"
            for message in publication.record_problems(model, data)
        )
    return problems


def _conflict_reference_problems(
    data: dict[str, Any], method_codes: set[str], index: int, key: str,
) -> list[str]:
    """Ссылки концов связи на каталог методов.

    Связь без обоих концов не имеет смысла для правил применимости: раньше она
    сохранялась с HTTP 200 и позже давала ложные срабатывания либо молча
    игнорировалась. Проверка идёт до записи, файл отклоняется целиком.
    """
    problems: list[str] = []
    a_code = str(data.get("a_code") or "").strip()
    b_code = str(data.get("b_code") or "").strip()
    if a_code and a_code not in method_codes:
        problems.append(
            f"Строка {index} ({key}): метод «{a_code}» не найден в каталоге."
        )
    if b_code and b_code not in method_codes:
        problems.append(
            f"Строка {index} ({key}): метод «{b_code}» не найден в каталоге."
        )
    if a_code and b_code and a_code == b_code:
        problems.append(
            f"Строка {index} ({key}): связь метода с самим собой запрещена."
        )
    return problems


#: Поля, изменение которых не требует повторной проверки: служебная дата и
#: порядок не меняют смысл утверждения.
_NON_SUBSTANTIVE_FIELDS = frozenset({"updated_at", "id"})


def _has_substantive_change(obj, data: dict) -> bool:
    """Изменилось ли содержание записи, а не только служебные поля."""
    for key, value in data.items():
        if key in _NON_SUBSTANTIVE_FIELDS:
            continue
        if getattr(obj, key, None) != value:
            return True
    return False


def _find_existing(db: Session, model, entity: str, data: dict):
    """Найти существующую запись по ключу сущности.

    Связь идентифицируется тройкой `(a_code, b_code, conflict_type)`: у неё нет
    ни одного общего с остальными сущностями поля-ключа, и поиск по «code»
    либо «title» для неё бессмыслен.
    """
    if entity == "conflicts":
        conditions = [getattr(model, field) == data.get(field) for field in CONFLICT_KEY_FIELDS]
        return db.scalar(select(model).where(*conditions))
    if entity in ("hardware_cpu", "hardware_gpu"):
        key_field = "model"
    else:
        key_field = "code"
    value = data.get(key_field)
    if not value:
        return None
    return db.scalar(select(model).where(getattr(model, key_field) == value))


@router.post("/import/{entity}", summary="Импорт записей из CSV или JSON")
async def import_entity(
    entity: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    model = SUPPORTED_IMPORT.get(entity)
    if model is None:
        raise HTTPException(400, f"Неподдерживаемая сущность: {entity}")

    raw = await _read_upload(file)
    rows = _read_rows(raw, file.filename, entity)

    key_label = (
        " / ".join(CONFLICT_KEY_FIELDS) if entity == "conflicts"
        else ("model" if entity in ("hardware_cpu", "hardware_gpu") else "code")
    )
    problems = _validate_rows(model, rows, entity, key_label, db)
    if problems:
        # Ни одна запись не записана: файл отклонён целиком.
        raise ApiError(
            "Импорт отклонён: файл содержит некорректные данные",
            code=ErrorCode.PUBLICATION_REJECTED,
            status=422,
            details=problems[:50],
        )

    list_fields = list_columns(entity)
    created = updated = 0
    try:
        for row in rows:
            data = _coerce(model, {**row, **normalize_row(entity, row)}, list_fields)
            # Статус из файла не принимается: импорт не является каналом
            # публикации. Раньше колонка `status` в файле проходила насквозь, и
            # новая запись могла сразу создаться опубликованной, хотя докумен-
            # тация и комментарий ниже обещают обратное. Обновление статуса —
            # только явным переходом в административном разделе.
            data.pop("status", None)
            obj = _find_existing(db, model, entity, data)
            if obj is None:
                data["status"] = Status.DRAFT.value
                db.add(model(**data))
                created += 1
            else:
                for key, value in data.items():
                    setattr(obj, key, value)
                updated += 1
        db.commit()
    except Exception:  # noqa: BLE001 — импорт либо применяется целиком, либо нет
        db.rollback()
        logger.exception("Импорт %s отменён, транзакция откачена", entity)
        raise HTTPException(500, "Импорт не выполнен: изменения отменены")

    seeder.validate_knowledge_base(db)
    db.commit()
    return {"entity": entity, "created": created, "updated": updated, "skipped": 0}


async def _read_upload(file: UploadFile) -> bytes:
    """Прочитать файл с ограничением размера, не загружая его целиком в память."""
    limit = settings.IMPORT_MAX_BYTES
    chunks: list[bytes] = []
    total = 0
    while True:
        chunk = await file.read(64 * 1024)
        if not chunk:
            break
        total += len(chunk)
        if total > limit:
            raise HTTPException(
                413,
                f"Файл больше допустимого размера {limit // (1024 * 1024)} МБ.",
            )
        chunks.append(chunk)
    return b"".join(chunks)


def json_loads(raw: bytes):
    return json.loads(raw.decode("utf-8-sig"))
