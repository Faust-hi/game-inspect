"""Фактическое наполнение демонстрационной базы (для сверки с README)."""
import os
import pathlib
import sys
import tempfile

BACKEND = pathlib.Path(r"C:\Users\user\Desktop\game-inspect\backend")
sys.path.insert(0, str(BACKEND))

tmp = tempfile.mkdtemp(prefix="counts_")
os.environ["DATABASE_URL"] = f"sqlite:///{tmp.replace(chr(92), '/')}/probe.db"
os.environ["AUTO_SEED"] = "false"

from app.database import Base, SessionLocal, engine  # noqa: E402
from app.seed import seeder  # noqa: E402

Base.metadata.create_all(bind=engine)
session = SessionLocal()
if seeder.is_empty(session):
    seeder.seed_all(session, validate=True)
session.commit()
session.close()

from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402

client = TestClient(app)
methods = client.get("/api/catalog/methods").json()
print("методов в публичном каталоге:", len(methods))
print("функций:", len(client.get("/api/catalog/functions").json()))
print("движков:", len(client.get("/api/catalog/engines").json()))
print("конфликтов:", len(client.get("/api/catalog/conflicts").json()))
hardware = client.get("/api/catalog/hardware").json()
print("CPU:", len(hardware["cpu"]), "GPU:", len(hardware["gpu"]))
print("health.catalog:", client.get("/api/health").json()["catalog"])
print("из них без source_url:", sum(1 for m in methods if not m.get("source_url")))
