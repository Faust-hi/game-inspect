"""Общая среда для тестов: временная база, заполненная демонстрационными данными.

Изоляция устроена так, чтобы прогон тестов не изменял рабочий проект:

* база создаётся в отдельном временном каталоге и удаляется вместе с ним,
  поэтому тесты не пишут в `backend/gamedev_dss.db` и не оставляют после себя
  записей, из-за которых следующий прогон начинает падать на чужих данных;
* каждый тест выполняется внутри транзакции, которая откатывается по завершении,
  поэтому тесты не влияют друг на друга и порядок их выполнения не важен.
"""
from __future__ import annotations

import os
import pathlib
import sys
import tempfile

import pytest

BACKEND_DIR = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))

# Каталог со временной базой: уникален для каждого прогона, удаляется pytest
# вместе с остальными временными каталогами.
if not os.environ.get("DATABASE_URL"):
    _TMP_DB_DIR = pathlib.Path(tempfile.mkdtemp(prefix="gamedev_dss_tests_"))
    os.environ["DATABASE_URL"] = f"sqlite:///{(_TMP_DB_DIR / 'test.db').as_posix()}"

os.environ["AUTO_SEED"] = "false"
# Тесты не должны зависеть от счётчиков ограничения частоты запросов.
os.environ.setdefault("ENVIRONMENT", "test")
os.environ.setdefault("RATE_LIMIT_ENABLED", "false")


@pytest.fixture(scope="session")
def seeded_database():
    """Однократно создаёт схему и заполняет базу демонстрационными данными."""
    from app.database import Base, SessionLocal, engine
    from app.seed import seeder

    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    try:
        if seeder.is_empty(session):
            seeder.seed_all(session, validate=True)
        session.commit()
    finally:
        session.close()


@pytest.fixture
def db_session(seeded_database):
    """Сессия в транзакции, которая откатывается после каждого теста.

    Та же сессия подменяет зависимость `get_db`, поэтому изменения, сделанные
    обработчиками запросов, тоже откатываются: тест, создавший метод, не ломает
    следующий тест, ожидающий пустой каталог.
    """
    from sqlalchemy.orm import Session

    from app.database import engine
    from app.main import app
    from app.database import get_db

    connection = engine.connect()
    transaction = connection.begin()
    session = Session(
        bind=connection,
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
        join_transaction_mode="create_savepoint",
    )

    app.dependency_overrides[get_db] = lambda: session
    try:
        yield session
    finally:
        app.dependency_overrides.pop(get_db, None)
        session.close()
        transaction.rollback()
        connection.close()


@pytest.fixture
def client(db_session):
    """HTTP-клиент, работающий с изолированной от других тестов базой."""
    from fastapi.testclient import TestClient

    from app.main import app

    with TestClient(app) as c:
        yield c


@pytest.fixture
def db(db_session):
    """Псевдоним для тестов, работающих с ORM напрямую."""
    return db_session


@pytest.fixture
def profile() -> dict:
    """Базовый профиль проекта: трёхмерный открытый мир на ранней стадии."""
    return {
        "name": "Тестовый проект",
        "format": "3D",
        "world_type": "open_world",
        "scale": "large",
        "stage": "prototype",
        "engine": "unreal",
        "platforms": ["pc_windows"],
        "functions": ["open_world_streaming", "crowd_simulation"],
        "target_resolution": "1440p",
        "target_quality": "high",
        "target_fps": 60,
        "npc_count_level": "high",
    }
