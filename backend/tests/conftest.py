"""Общая среда для тестов: временная база, заполненная демонстрационными данными."""
from __future__ import annotations

import os
import pathlib
import sys

import pytest

BACKEND_DIR = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))

TMP_DB = BACKEND_DIR / "test_gamedev_dss.db"
os.environ["DATABASE_URL"] = f"sqlite:///{TMP_DB.as_posix()}"
os.environ["AUTO_SEED"] = "false"
# Тесты не должны зависеть от счётчиков ограничения частоты запросов.
os.environ["ENVIRONMENT"] = "test"
os.environ["RATE_LIMIT_ENABLED"] = "false"


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
    finally:
        session.close()


@pytest.fixture(scope="session")
def client(seeded_database):
    from fastapi.testclient import TestClient

    from app.main import app

    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="session")
def db(seeded_database):
    from app.database import SessionLocal

    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


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
