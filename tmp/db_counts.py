"""Полное наполнение базы по моделям (для сверки с таблицей README)."""
import os
import pathlib
import sys
import tempfile

BACKEND = pathlib.Path(r"C:\Users\user\Desktop\game-inspect\backend")
sys.path.insert(0, str(BACKEND))

tmp = tempfile.mkdtemp(prefix="dbcounts_")
os.environ["DATABASE_URL"] = f"sqlite:///{tmp.replace(chr(92), '/')}/probe.db"
os.environ["AUTO_SEED"] = "false"

from sqlalchemy import func, select  # noqa: E402

from app.database import Base, SessionLocal, engine  # noqa: E402
from app.models.entities import (  # noqa: E402
    Conflict,
    Engine,
    EngineTool,
    GameFunction,
    HardwareCPU,
    HardwareGPU,
    Method,
    MethodEngineLink,
    PublicationLog,
    ValidationIssue,
)
from app.seed import seeder  # noqa: E402

Base.metadata.create_all(bind=engine)
session = SessionLocal()
if seeder.is_empty(session):
    seeder.seed_all(session, validate=True)
session.commit()

for model in (GameFunction, Method, Engine, EngineTool, MethodEngineLink,
              Conflict, HardwareCPU, HardwareGPU, PublicationLog, ValidationIssue):
    total = session.scalar(select(func.count()).select_from(model))
    extra = ""
    if model is Method:
        published = session.scalar(
            select(func.count()).select_from(Method).where(Method.status == "published")
        )
        extra = f" (опубликовано {published}, черновиков {total - published})"
    print(f"{model.__name__}: {total}{extra}")

print("\n--- Замечания целостности после заполнения ---")
for issue in session.scalars(select(ValidationIssue)).all():
    print(f"[{issue.severity}] {issue.entity}: {issue.message}")
session.close()
