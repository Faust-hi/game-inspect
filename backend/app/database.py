"""Подключение к локальной SQLite-базе (единственная поддерживаемая СУБД)."""
from __future__ import annotations

from urllib.parse import urlparse

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from .config import settings


def _connect_args(database_url: str) -> dict:
    # `check_same_thread` — параметр SQLite-драйвера; для других схем его
    # передавать нельзя. Неподдерживаемые схемы не падают здесь: явный отказ
    # с объяснением выдаёт `db_migrate.ensure_schema` и /api/health (D38).
    if urlparse(database_url).scheme == "sqlite":
        return {"check_same_thread": False}
    return {}


engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DB_ECHO,
    future=True,
    connect_args=_connect_args(settings.DATABASE_URL),
)


@event.listens_for(Engine, "connect")
def _set_sqlite_pragma(dbapi_connection, _connection_record):
    """Включает внешние ключи и WAL.

    SQLite по умолчанию не проверяет внешние ключи: описанные в модели
    связи существуют только «на бумаге», и удаление родительской записи
    оставляет осиротевшие строки. Без этого PRAGMA каскадное удаление,
    описанное в моделях, не работает.
    """
    cursor = dbapi_connection.cursor()
    try:
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.execute("PRAGMA synchronous=NORMAL")
        try:
            # WAL недоступен для баз на сетевых дисках: это не повод не запускаться.
            cursor.execute("PRAGMA journal_mode=WAL")
        except Exception:  # noqa: BLE001 — второстепенная настройка
            pass
    finally:
        cursor.close()

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False, future=True)


class Base(DeclarativeBase):
    """Базовый класс для всех ORM-моделей."""

    def to_dict(self) -> dict:
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


def get_db():
    """Зависимость FastAPI: сессия БД на время запроса."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
