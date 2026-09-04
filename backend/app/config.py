"""Конфигурация локального приложения.

Система работает только локально на SQLite-файле, установка СУБД не требуется.
Значения читаются из окружения и из файла backend/.env.
"""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parents[1]
PROJECT_DIR = BACKEND_DIR.parent
DATA_DIR = BACKEND_DIR / "app" / "seed" / "data"
FRONTEND_DIST = PROJECT_DIR / "frontend" / "dist"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BACKEND_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    APP_TITLE: str = "ИС поддержки принятия решений по оптимизации разработки игр"
    APP_VERSION: str = "1.0.0"
    API_PREFIX: str = "/api"

    DATABASE_URL: str = f"sqlite:///{(BACKEND_DIR / 'gamedev_dss.db').as_posix()}"
    DB_ECHO: bool = False

    # Если True, при старте пустая база заполняется демонстрационными данными
    # (MVP-наполнение). Заполнение выполняется только для пустой базы.
    AUTO_SEED: bool = True

    # Логирование.
    LOG_LEVEL: str = "INFO"

    # Предельный размер импортируемого файла (байт).
    IMPORT_MAX_BYTES: int = 5 * 1024 * 1024
    IMPORT_MAX_ROWS: int = 5000


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()


def reload_settings() -> Settings:
    """Сбрасывает кэш настроек. Используется в тестах и после изменения .env."""
    get_settings.cache_clear()
    global settings  # noqa: PLW0603 — модульный синглтон настроек
    settings = get_settings()
    return settings
