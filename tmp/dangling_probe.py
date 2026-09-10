"""Мутация: в каталоге появляется связь с несуществующим методом.

Проверяет, что исправленная проверка целостности её обнаруживает, а прежняя
(вакуумная) формулировка — нет.
"""
import os
import pathlib
import sys
import tempfile

BACKEND = pathlib.Path(r"C:\Users\user\Desktop\game-inspect\backend")
sys.path.insert(0, str(BACKEND))

tmp = tempfile.mkdtemp(prefix="dangling_")
os.environ["DATABASE_URL"] = f"sqlite:///{tmp.replace(chr(92), '/')}/probe.db"
os.environ["AUTO_SEED"] = "false"

from app.database import Base, SessionLocal, engine  # noqa: E402
from app.models.entities import Conflict  # noqa: E402
from app.seed import seeder  # noqa: E402

Base.metadata.create_all(bind=engine)
session = SessionLocal()
if seeder.is_empty(session):
    seeder.seed_all(session, validate=True)
session.add(Conflict(
    a_code="метод_которого_нет", b_code="тоже_нет",
    conflict_type="hard_conflict", severity=3,
    description="Оборванная связь для проверки.",
    status="published",
))
session.commit()

from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402

client = TestClient(app)
methods = client.get("/api/catalog/methods").json()
codes = {item["code"] for item in methods}
links = client.get("/api/catalog/conflicts").json()
dangling = [link for link in links
            if link["a_code"] not in codes or link["b_code"] not in codes]
print("всего связей:", len(links), "оборванных:", len(dangling))

# Прежняя формулировка: всегда истинна при непустом коде.
old_ok = all((link["a_code"] in codes or link["a_code"])
             and (link["b_code"] in codes or link["b_code"]) for link in links)
# Исправленная: строгое вхождение.
try:
    for link in links:
        assert link["a_code"] in codes, link
        assert link["b_code"] in codes, link
    new_ok = True
except AssertionError as exc:
    new_ok = False
    print("исправленная проверка упала на:", str(exc)[:80])

print("прежняя формулировка проходит:", old_ok)
print("исправленная формулировка проходит:", new_ok)
