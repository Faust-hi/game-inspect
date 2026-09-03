"""Конфигурация приложения.

По умолчанию используется локальный SQLite-файл, чтобы система запускалась без
установки СУБД. Для PostgreSQL достаточно задать переменную окружения
DATABASE_URL, например:
    DATABASE_URL=postgresql+psycopg2://user:password@localhost:5432/gamedev_dss

Значения читаются из окружения и из файла backend/.env. В эксплуатационном
режиме (ENVIRONMENT=production) конфигурация проверяется жёстче: запрещены
стандартный токен администратора и разрешающие всем правила CORS.
"""
from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parents[1]
PROJECT_DIR = BACKEND_DIR.parent
DATA_DIR = BACKEND_DIR / "app" / "seed" / "data"
FRONTEND_DIST = PROJECT_DIR / "frontend" / "dist"

#: Токен, который нельзя использовать в эксплуатации.
DEFAULT_ADMIN_TOKEN = "admin"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BACKEND_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    APP_TITLE: str = "ИС поддержки принятия решений по оптимизации разработки игр"
    APP_VERSION: str = "1.0.0"
    API_PREFIX: str = "/api"

    # Режим работы: development | production | test
    ENVIRONMENT: str = "development"

    DATABASE_URL: str = f"sqlite:///{(BACKEND_DIR / 'gamedev_dss.db').as_posix()}"
    DB_ECHO: bool = False

    ADMIN_TOKEN: str = DEFAULT_ADMIN_TOKEN
    CORS_ORIGINS: str = "*"

    # Если True, при старте пустая база заполняется демонстрационными данными
    # (MVP-наполнение). Заполнение выполняется только для пустой базы.
    AUTO_SEED: bool = True

    # Ограничение частоты запросов (защита от перебора и случайной нагрузки).
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_ADMIN_PER_MINUTE: int = 60     # административный раздел
    RATE_LIMIT_CALC_PER_MINUTE: int = 120     # расчётные эндпоинты

    # Логирование.
    LOG_LEVEL: str = "INFO"
    LOG_JSON: bool = False                    # True — однострочный JSON для сбора логов

    # Заголовок HSTS. Включать только при работе по HTTPS.
    SECURITY_HSTS_ENABLED: bool = False

    # Адреса прокси, которым можно доверять заголовок X-Forwarded-For.
    # Пустой список — заголовок игнорируется: иначе любой клиент может
    # подменить свой адрес и обойти ограничение частоты запросов.
    TRUSTED_PROXIES: str = ""

    # Предельный размер импортируемого файла (байт). Ограничение защищает
    # от исчерпания памяти и диска одним запросом администратора.
    IMPORT_MAX_BYTES: int = 5 * 1024 * 1024
    IMPORT_MAX_ROWS: int = 5000

    # Срок хранения публично сохранённых проектов (дни).
    PROJECT_TTL_DAYS: int = 90
    PROJECTS_PER_MINUTE: int = 20

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT.strip().lower() == "production"

    @property
    def is_testing(self) -> bool:
        return self.ENVIRONMENT.strip().lower() == "test"

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]

    @property
    def trusted_proxies_list(self) -> list[str]:
        return [p.strip() for p in self.TRUSTED_PROXIES.split(",") if p.strip()]

    @property
    def uses_default_admin_token(self) -> bool:
        return not self.ADMIN_TOKEN or self.ADMIN_TOKEN == DEFAULT_ADMIN_TOKEN

    def production_problems(self) -> list[str]:
        """Возвращает список проблем конфигурации, недопустимых в эксплуатации."""
        problems: list[str] = []
        if self.uses_default_admin_token:
            problems.append(
                "ADMIN_TOKEN имеет стандартное значение «admin». "
                "Задайте надёжный токен переменной окружения ADMIN_TOKEN."
            )
        if "*" in self.cors_origins_list:
            problems.append(
                "CORS_ORIGINS разрешает любые источники. "
                "Перечислите конкретные адреса frontend через запятую."
            )
        if self.is_production and self.DATABASE_URL.startswith("sqlite"):
            problems.append(
                "В эксплуатации используется SQLite. "
                "Для совместной работы задайте PostgreSQL в DATABASE_URL."
            )
        if self.is_production and self.AUTO_SEED:
            problems.append(
                "AUTO_SEED включён: в пустую базу будет записан демонстрационный набор. "
                "Отключите AUTO_SEED после первичного развёртывания."
            )
        if self.is_production and self.DB_ECHO:
            problems.append("DB_ECHO включён: SQL-запросы будут записаны в журнал.")
        return problems


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


def env_flag(name: str, default: bool = False) -> bool:
    """Читает логический флаг из окружения (1/true/yes/on)."""
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}
