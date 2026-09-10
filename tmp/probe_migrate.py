"""Ручная сверка доката старой базы до новой ревизии (без pytest)."""
from __future__ import annotations

import os
import tempfile
from pathlib import Path

tmpdir = Path(tempfile.mkdtemp(prefix="migprobe"))
db_path = tmpdir / "legacy.db"
url = f"sqlite:///{db_path.as_posix()}"
os.environ["DATABASE_URL"] = url

from sqlalchemy import create_engine, inspect, text  # noqa: E402

from app.config import reload_settings  # noqa: E402
from app.db_migrate import ensure_schema  # noqa: E402
from app.models import Base  # noqa: E402

reload_settings()

# 1. Свежая база: миграции поднимают схему с нуля.
report_new = ensure_schema()
engine = create_engine(url, future=True)
with engine.connect() as conn:
    names = set(inspect(conn).get_table_names())
    cols = {c["name"] for c in inspect(conn).get_columns("methods")}
print("НОВАЯ:", report_new["stamped"], report_new["migrated"], "methods" in names,
      "engine_tool_independent" in cols)
engine.dispose()

# 2. Имитация базы предыдущей ревизии: структуры без новой колонки
#    и без таблицы версий (как было у баз от create_all).
db_path.unlink()
engine = create_engine(url, future=True)
Base.metadata.create_all(engine)
with engine.begin() as conn:
    conn.execute(text("ALTER TABLE methods DROP COLUMN engine_tool_independent"))
engine.dispose()

report_legacy = ensure_schema()
engine = create_engine(url, future=True)
with engine.connect() as conn:
    cols = {c["name"] for c in inspect(conn).get_columns("methods")}
    version = conn.execute(text("SELECT version_num FROM alembic_version")).scalar()
engine.dispose()
print("СТАРАЯ:", report_legacy["stamped"], report_legacy["migrated"],
      "engine_tool_independent" in cols, "версия:", version)
print("ОШИБКА:", report_legacy["error"])
