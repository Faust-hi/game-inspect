"""Административный раздел: наполнение, проверка и публикация базы знаний."""
from __future__ import annotations

import csv
import io
import json
import logging
import uuid
from typing import Any

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..config import settings
from ..database import get_db
from ..models.entities import (
    Conflict, Engine, EngineTool, GameExample, GameFunction, HardwareCPU, HardwareGPU,
    Method, MethodEngineLink, Project, PublicationLog, ValidationIssue,
)
from ..models.enums import Status
from ..schemas.catalog import BasketRequest
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
        "game_examples": db.scalar(select(func.count(GameExample.id))),
        "hardware_cpu": db.scalar(select(func.count(HardwareCPU.id))),
        "hardware_gpu": db.scalar(select(func.count(HardwareGPU.id))),
        "projects": db.scalar(select(func.count(Project.id))),
    }
    issues = db.scalars(select(ValidationIssue).order_by(ValidationIssue.severity)).all()
    counts["published"] = repositories.published_snapshot_counts(db)
    return {
        "counts": counts,
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


@router.post("/seed", summary="Заполнить базу демонстрационными данными")
def run_seed(db: Session = Depends(get_db)):
    return seeder.seed_all(db, validate=True)


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
        raise HTTPException(422, {"error": "Запись отклонена", "details": publication.deduplicate(problems)})

    obj = db.scalar(select(Method).where(Method.code == payload.code))
    if obj is None:
        data["status"] = Status.DRAFT.value
        obj = Method(**data)
        db.add(obj)
        created = True
    else:
        # Редактирование не меняет статус: запись остаётся там, где была.
        data.pop("status", None)
        for key, value in data.items():
            setattr(obj, key, value)
        created = False
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
        # Считаются только опубликованные связи: черновая связь не делает метод
        # пригодным к публикации, потому что пользователь её не увидит.
        has_links = db.scalar(
            select(func.count(MethodEngineLink.id)).where(
                MethodEngineLink.method_id == obj.id,
                MethodEngineLink.status == Status.PUBLISHED.value,
            )
        ) or 0
        problems = publication.publication_problems(obj, has_links=has_links > 0)
        if problems:
            raise HTTPException(
                422,
                {"error": "Публикация невозможна", "details": publication.deduplicate(problems)},
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
    "game_examples": GameExample,
    "hardware_cpu": HardwareCPU,
    "hardware_gpu": HardwareGPU,
    "conflicts": Conflict,
}


def _coerce(model, row: dict[str, Any]) -> dict[str, Any]:
    result = {}
    for column in model.__table__.columns:
        if column.name not in row:
            continue
        value = row[column.name]
        if hasattr(column.type, "python_type") and column.type.python_type is list:
            if isinstance(value, str):
                value = [p.strip() for p in value.split(";") if p.strip()] if value else []
        if column.type.python_type is int and isinstance(value, str):
            value = int(value) if value.strip().lstrip("-").isdigit() else 0
        if column.type.python_type is float and isinstance(value, str):
            try:
                value = float(value)
            except ValueError:
                value = 0.0
        if column.type.python_type is bool and isinstance(value, str):
            value = value.strip().lower() in ("1", "true", "yes", "да")
        result[column.name] = value
    return result


def _read_rows(raw: bytes, filename: str | None, entity: str) -> list[dict[str, Any]]:
    """Разобрать импортируемый файл. Ошибка формата отклоняет весь импорт."""
    if filename and filename.lower().endswith(".json"):
        payload = json_loads(raw)
        rows = payload.get(entity, []) if isinstance(payload, dict) else payload
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


def _validate_rows(model, rows: list[dict[str, Any]], key_field: str) -> list[str]:
    """Проверить все строки до первой записи в базу.

    Возвращает список найденных нарушений. Проверка выполняется заранее, чтобы
    частично некорректный файл не оставлял в базе половину изменений.
    """
    problems: list[str] = []
    seen: set[str] = set()
    for index, row in enumerate(rows, start=1):
        key = str(row.get(key_field) or "").strip()
        if not key:
            problems.append(f"Строка {index}: не указан ключ «{key_field}».")
            continue
        if key in seen:
            problems.append(f"Строка {index}: ключ «{key}» повторяется внутри файла.")
        seen.add(key)
        try:
            data = _coerce(model, row)
        except (TypeError, ValueError) as exc:
            problems.append(f"Строка {index} ({key}): значение не распознано — {exc}.")
            continue
        problems.extend(
            f"Строка {index} ({key}): {message}"
            for message in publication.record_problems(model, data)
        )
    return problems


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

    key_field = "code" if hasattr(model, "code") else ("model" if hasattr(model, "model") else "title")
    problems = _validate_rows(model, rows, key_field)
    if problems:
        # Ни одна запись не записана: файл отклонён целиком.
        raise HTTPException(
            422,
            {"error": "Импорт отклонён: файл содержит некорректные данные", "details": problems[:50]},
        )

    created = updated = 0
    try:
        for row in rows:
            data = _coerce(model, row)
            if "status" not in data:
                data["status"] = Status.DRAFT.value
            obj = db.scalar(select(model).where(getattr(model, key_field) == data[key_field]))
            if obj is None:
                db.add(model(**data))
                created += 1
            else:
                # Публикация через импорт запрещена: статус меняется только
                # через явный переход в административном разделе.
                data.pop("status", None)
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


# ---------------------------------------------------------------------------
# Сохранение проектов (локальное, без срока хранения)
# ---------------------------------------------------------------------------
projects_router = APIRouter(prefix="/projects", tags=["Проекты"])


@projects_router.post("", summary="Сохранить проект")
def save_project(payload: BasketRequest, db: Session = Depends(get_db)):
    public_id = uuid.uuid4().hex[:16]
    project = Project(
        public_id=public_id,
        name=payload.profile.name[:200],
        profile=payload.profile.model_dump(),
        basket=(payload.basket or [])[:200],
    )
    db.add(project)
    db.commit()
    return {"public_id": public_id}


@projects_router.get("/{public_id}", summary="Загрузить сохранённый проект")
def get_project(public_id: str, db: Session = Depends(get_db)):
    if len(public_id) > 36 or not public_id.isalnum():
        raise HTTPException(404, "Проект не найден")
    project = db.scalar(select(Project).where(Project.public_id == public_id))
    if not project:
        raise HTTPException(404, "Проект не найден")

    return {
        "public_id": project.public_id,
        "name": project.name,
        "profile": project.profile,
        "basket": project.basket,
    }
