"""Content revision of the published catalogue, independent of timestamps."""
import hashlib
import json

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models.entities import (
    Conflict, Engine, EngineTool, GameExample, GameFunction, HardwareCPU,
    HardwareGPU, Method, MethodEngineLink,
)


def published_revision(db: Session) -> str:
    db.flush()
    content = {}
    for model in (GameFunction, Method, Engine, EngineTool, MethodEngineLink,
                  Conflict, GameExample, HardwareCPU, HardwareGPU):
        fields = [column.name for column in model.__table__.columns
                  if column.name not in {"created_at", "updated_at"}]
        rows = [json.dumps({name: getattr(row, name) for name in fields},
                           sort_keys=True, ensure_ascii=False, allow_nan=False)
                for row in db.scalars(select(model).where(model.status == "published"))]
        content[model.__tablename__] = sorted(rows)
    return hashlib.sha256(json.dumps(content, sort_keys=True).encode()).hexdigest()
