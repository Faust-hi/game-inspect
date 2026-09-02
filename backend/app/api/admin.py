"""Административный раздел: наполнение, проверка и публикация базы знаний."""
from __future__ import annotations

import csv
import io
import uuid
from typing import Any

from fastapi import APIRouter, Depends, File, Header, HTTPException, Request, UploadFile
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..config import settings
from ..database import get_db
from ..models.entities import (
    Conflict, Engine, EngineTool, GameExample, GameFunction, HardwareCPU, HardwareGPU,
    Method, MethodEngineLink, Project, ValidationIssue,
)
from ..schemas.catalog import BasketRequest
from ..seed import seeder
from ..services.security import enforce_rate_limit, token_matches
from .catalog import method_to_out

router = APIRouter(prefix="/admin", tags=["Администрирование"])


def require_admin(
    request: Request,
    x_admin_token: str | None = Header(default=None),
) -> None:
    """Проверяет токен администратора и частоту обращений к разделу."""
    enforce_rate_limit(request, settings.RATE_LIMIT_ADMIN_PER_MINUTE, "admin")
    if not token_matches(x_admin_token):
        raise HTTPException(
            status_code=401,
            detail="Требуется токен администратора",
            headers={"WWW-Authenticate": "Bearer"},
        )


# ---------------------------------------------------------------------------
# Обзор и целостность
# ---------------------------------------------------------------------------
@router.get("/overview", summary="Сводка по наполнению базы")
def overview(db: Session = Depends(get_db), _: None = Depends(require_admin)):
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
def validate(db: Session = Depends(get_db), _: None = Depends(require_admin)):
    issues = seeder.validate_knowledge_base(db)
    db.commit()
    return {"issues": issues, "total": len(issues)}


@router.post("/seed", summary="Заполнить базу демонстрационными данными")
def run_seed(db: Session = Depends(get_db), _: None = Depends(require_admin)):
    return seeder.seed_all(db, validate=True)


# ---------------------------------------------------------------------------
# Работа с методами
# ---------------------------------------------------------------------------
class MethodIn(BaseModel):
    code: str
    name: str
    kind: str = "optimization"
    function_code: str | None = None
    summary: str = ""
    description: str = ""
    problem: str = ""
    level: str = "algorithm"
    recommended_stage: str = "prototype"
    late_cost: str = "medium"
    calc_mode: str = "realtime"
    impact_cpu: int = 0
    impact_gpu: int = 0
    impact_ram: int = 0
    impact_vram: int = 0
    impact_disk: int = 0
    impact_network: int = 0
    quality_impact: int = 0
    concept_impact: int = 0
    performance_gain: float = 0.5
    implementation_cost: int = 3
    complexity: int = 3
    confidence: float = 0.7
    requires_prototype: bool = False
    applicable_formats: list[str] = Field(default_factory=list)
    applicable_world_types: list[str] = Field(default_factory=list)
    applicable_engines: list[str] = Field(default_factory=list)
    applicable_platforms: list[str] = Field(default_factory=list)
    requires_features: list[str] = Field(default_factory=list)
    requires_hw_features: list[str] = Field(default_factory=list)
    requires_conditions: list[str] = Field(default_factory=list)
    min_scale: str | None = None
    pros: list[str] = Field(default_factory=list)
    cons: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)
    verification_method: str = ""
    verification_tools: list[str] = Field(default_factory=list)
    source_title: str = ""
    source_url: str = ""
    source_date: str = ""


class StatusIn(BaseModel):
    status: str


@router.get("/methods", summary="Список методов со всеми статусами")
def admin_methods(db: Session = Depends(get_db), _: None = Depends(require_admin)):
    rows = db.scalars(select(Method).order_by(Method.code)).all()
    return [method_to_out(db, m) for m in rows]


@router.post("/methods", summary="Добавить или обновить метод")
def upsert_method(payload: MethodIn, db: Session = Depends(get_db), _: None = Depends(require_admin)):
    data = payload.model_dump()
    function_code = data.pop("function_code", None)
    if function_code:
        fn = db.scalar(select(GameFunction).where(GameFunction.code == function_code))
        if fn:
            data["function_id"] = fn.id
    obj = db.scalar(select(Method).where(Method.code == payload.code))
    if obj is None:
        obj = Method(**data)
        db.add(obj)
        created = True
    else:
        for key, value in data.items():
            setattr(obj, key, value)
        created = False
    db.commit()
    return {"created": created, "code": obj.code, "status": obj.status}


@router.patch("/methods/{code}/status", summary="Изменить статус записи (черновик → проверено → опубликовано)")
def set_method_status(code: str, payload: StatusIn, db: Session = Depends(get_db), _: None = Depends(require_admin)):
    if payload.status not in ("draft", "reviewed", "published"):
        raise HTTPException(400, "Недопустимый статус")
    obj = db.scalar(select(Method).where(Method.code == code))
    if not obj:
        raise HTTPException(404, "Метод не найден")
    if payload.status == "published" and not obj.source_url:
        raise HTTPException(400, "Публикация невозможна: у записи отсутствует источник")
    obj.status = payload.status
    db.commit()
    return {"code": obj.code, "status": obj.status}


@router.delete("/methods/{code}", summary="Удалить метод")
def delete_method(code: str, db: Session = Depends(get_db), _: None = Depends(require_admin)):
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
def upsert_link(payload: LinkIn, db: Session = Depends(get_db), _: None = Depends(require_admin)):
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
        db.add(MethodEngineLink(
            method_id=method.id, tool_id=tool.id,
            relation_type=payload.relation_type, note=payload.note, source_url=tool.docs_url,
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


@router.post("/import/{entity}", summary="Импорт записей из CSV или JSON")
async def import_entity(
    entity: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    _: None = Depends(require_admin),
):
    model = SUPPORTED_IMPORT.get(entity)
    if model is None:
        raise HTTPException(400, f"Неподдерживаемая сущность: {entity}")
    raw = await file.read()
    rows: list[dict[str, Any]] = []
    if file.filename and file.filename.lower().endswith(".json"):
        payload = json_loads(raw)
        if isinstance(payload, dict):
            rows = payload.get(entity, [])
        else:
            rows = payload
    else:
        text = raw.decode("utf-8-sig")
        rows = list(csv.DictReader(io.StringIO(text)))

    key_field = "code" if hasattr(model, "code") else ("model" if hasattr(model, "model") else "title")
    created = updated = skipped = 0
    for row in rows:
        if not row.get(key_field):
            skipped += 1
            continue
        data = _coerce(model, row)
        obj = db.scalar(select(model).where(getattr(model, key_field) == data[key_field]))
        if obj is None:
            db.add(model(**data))
            created += 1
        else:
            for key, value in data.items():
                setattr(obj, key, value)
            updated += 1
    db.commit()
    seeder.validate_knowledge_base(db)
    db.commit()
    return {"entity": entity, "created": created, "updated": updated, "skipped": skipped}


def json_loads(raw: bytes):
    import json
    return json.loads(raw.decode("utf-8-sig"))


# ---------------------------------------------------------------------------
# Сохранение проектов (публичный доступ по идентификатору)
# ---------------------------------------------------------------------------
projects_router = APIRouter(prefix="/projects", tags=["Проекты"])


@projects_router.post("", summary="Сохранить проект и результат расчёта")
def save_project(payload: BasketRequest, db: Session = Depends(get_db)):
    public_id = uuid.uuid4().hex[:12]
    project = Project(
        public_id=public_id,
        name=payload.profile.name,
        profile=payload.profile.model_dump(),
        basket=payload.basket or [],
    )
    db.add(project)
    db.commit()
    return {"public_id": public_id}


@projects_router.get("/{public_id}", summary="Загрузить сохранённый проект")
def get_project(public_id: str, db: Session = Depends(get_db)):
    project = db.scalar(select(Project).where(Project.public_id == public_id))
    if not project:
        raise HTTPException(404, "Проект не найден")
    return {
        "public_id": project.public_id,
        "name": project.name,
        "profile": project.profile,
        "basket": project.basket,
        "updated_at": project.updated_at.isoformat(),
    }
