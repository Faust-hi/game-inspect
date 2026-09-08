"""Штатные миграции: бэкап, upgrade head, отказ на неизвестной структуре.

Этап 6 (D37/D38/D43.4): схема обновляется только Alembic; перед изменением
существующего файла делается проверяемая копия; база без ревизии, но с
известной структурой штампуется на начальную ревизию (не на head); чужая
структура и не-SQLite URL получают явный отказ вместо догадок.
"""
from __future__ import annotations

import os
from pathlib import Path

import pytest
from sqlalchemy import create_engine, text


@pytest.fixture
def isolated_database_url(monkeypatch, tmp_path):
    """Временно переключает настройки на базу в tmp_path с возвратом назад."""
    from app.config import reload_settings

    original = os.environ.get("DATABASE_URL")
    target = tmp_path / "migrate_test.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{target.as_posix()}")
    reload_settings()
    try:
        yield target
    finally:
        if original is None:
            monkeypatch.delenv("DATABASE_URL", raising=False)
        else:
            monkeypatch.setenv("DATABASE_URL", original)
        reload_settings()


@pytest.fixture(autouse=True)
def _preserve_migrate_state():
    """Глобальное состояние миграций не протекает между тестами."""
    from app import db_migrate

    saved = dict(db_migrate.state)
    try:
        yield
    finally:
        db_migrate.state.clear()
        db_migrate.state.update(saved)


def test_sqlite_path_of_memory_is_none():
    from app.db_migrate import sqlite_path_of

    assert sqlite_path_of("sqlite:///:memory:") is None
    assert sqlite_path_of("postgresql://u:p@localhost/db") is None


def test_unsupported_database_error_is_explicit():
    from app.db_migrate import UnsupportedDatabaseError, assert_supported_database

    assert_supported_database("sqlite:///./local.db")
    with pytest.raises(UnsupportedDatabaseError, match="только SQLite"):
        assert_supported_database("postgresql+psycopg2://u:p@localhost/db")


def test_backup_sqlite_is_verifiable(tmp_path):
    from app.db_migrate import backup_sqlite

    source = tmp_path / "game.db"
    source.write_bytes(b"sqlite-bytes")
    copy = backup_sqlite(source)
    assert copy.exists() and copy.stat().st_size > 0
    assert copy.parent == source.parent
    assert copy.name.startswith("game.bak-")


def test_wait_gate_markers():
    import wait_for_services

    assert wait_for_services.backend_ready(b'{"version":"1","database":"ready"}')
    assert not wait_for_services.backend_ready(b"<html>foreign</html>")
    assert wait_for_services.frontend_ready(b'<div id="root"></div>')
    assert not wait_for_services.frontend_ready(b'{"version":"1"}')


def test_ensure_schema_creates_fresh_db(isolated_database_url):
    from app import db_migrate

    target: Path = isolated_database_url
    assert not target.exists()
    report = db_migrate.ensure_schema()
    assert report["migrated"] is True, report
    assert report["backup"] is None
    assert db_migrate._current_revisions(f"sqlite:///{target.as_posix()}")
    assert "methods" in db_migrate._table_names(f"sqlite:///{target.as_posix()}")


def test_ensure_schema_backs_up_before_upgrading(isolated_database_url):
    from app import db_migrate

    target: Path = isolated_database_url
    first = db_migrate.ensure_schema()
    assert first["migrated"] is True
    second = db_migrate.ensure_schema()
    assert second["migrated"] is True, second
    assert second["backup"] is not None
    assert Path(str(second["backup"])).exists()


def test_ensure_schema_upgrades_legacy_db_without_version(isolated_database_url):
    """Наследие до effect_scope: штамп точки application_steps + upgrade."""
    from app import db_migrate
    from app.database import Base
    from app.models import entities as _entities  # noqa: F401 — регистрация таблиц в metadata

    target: Path = isolated_database_url
    url = f"sqlite:///{target.as_posix()}"
    engine = create_engine(url, future=True)
    try:
        Base.metadata.create_all(bind=engine)
        with engine.begin() as connection:
            connection.execute(text("ALTER TABLE methods DROP COLUMN effect_scope"))
    finally:
        engine.dispose()
    assert db_migrate._current_revisions(url) is None

    report = db_migrate.ensure_schema()
    assert report["migrated"] is True, report
    assert report["stamped"] == db_migrate.APPLICATION_STEPS_REVISION
    engine = create_engine(url, future=True)
    try:
        with engine.connect() as connection:
            columns = {row[1] for row in connection.execute(text("PRAGMA table_info(methods)")).all()}
    finally:
        engine.dispose()
    assert "effect_scope" in columns


def test_ensure_schema_upgrades_ancient_db_without_either_column(isolated_database_url):
    """Наследие до application_steps: штамп начальной ревизии + полный upgrade."""
    from app import db_migrate
    from app.database import Base
    from app.models import entities as _entities  # noqa: F401 — регистрация таблиц в metadata

    target: Path = isolated_database_url
    url = f"sqlite:///{target.as_posix()}"
    engine = create_engine(url, future=True)
    try:
        Base.metadata.create_all(bind=engine)
        with engine.begin() as connection:
            connection.execute(text("ALTER TABLE methods DROP COLUMN effect_scope"))
            connection.execute(text("ALTER TABLE methods DROP COLUMN application_steps"))
    finally:
        engine.dispose()

    report = db_migrate.ensure_schema()
    assert report["migrated"] is True, report
    assert report["stamped"] == db_migrate.INITIAL_REVISION


def test_ensure_schema_refuses_unknown_structure(isolated_database_url):
    from app import db_migrate

    target: Path = isolated_database_url
    url = f"sqlite:///{target.as_posix()}"
    engine = create_engine(url, future=True)
    try:
        with engine.begin() as connection:
            connection.execute(text("CREATE TABLE foreign_data (id INTEGER PRIMARY KEY)"))
    finally:
        engine.dispose()

    report = db_migrate.ensure_schema()
    assert report["migrated"] is False, report
    assert "неизвестной структурой" in str(report["error"])
    assert report["backup"] is not None


def test_ensure_schema_rejects_postgres_url(monkeypatch):
    import os

    from app import db_migrate
    from app.config import reload_settings

    original = os.environ.get("DATABASE_URL")
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg2://u:p@localhost/db")
    reload_settings()
    try:
        report = db_migrate.ensure_schema()
    finally:
        if original is None:
            monkeypatch.delenv("DATABASE_URL", raising=False)
        else:
            monkeypatch.setenv("DATABASE_URL", original)
        reload_settings()
    assert report["migrated"] is False, report
    assert "только SQLite" in str(report["error"])


def test_health_reports_readiness(client):
    body = client.get("/api/health").json()
    assert body["version"]
    assert body["ready"] is True
    assert body["schema_error"] is None
    assert body["catalog"]["methods"] > 0


def test_health_unavailable_on_schema_error(client, monkeypatch):
    from app import db_migrate

    monkeypatch.setitem(db_migrate.state, "schema_ok", False)
    monkeypatch.setitem(db_migrate.state, "schema_error", "boom")
    response = client.get("/api/health")
    assert response.status_code == 503
    body = response.json()
    assert body["status"] == "unavailable"
    assert body["ready"] is False
    assert body["schema_error"] == "boom"
