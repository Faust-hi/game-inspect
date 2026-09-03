"""Окружение Alembic: подключение к базе и метаданные моделей приложения.

Адрес базы читается из тех же настроек, что использует приложение
(`DATABASE_URL`), поэтому миграции и приложение работают с одной базой.

Для SQLite миграции выполняются в пакетном режиме (`render_as_batch`): SQLite не
поддерживает изменение и удаление колонок на месте, и Alembic пересоздаёт
таблицу. В пакетном режиме внешние ключи сохраняются только если они включены
для соединения — поэтому PRAGMA задаётся здесь, а не только в приложении.
"""
from __future__ import annotations

import sys
from logging.config import fileConfig
from pathlib import Path

from alembic import context
from sqlalchemy import engine_from_config, pool

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.config import settings  # noqa: E402 — путь добавлен выше
from app.database import Base  # noqa: E402
from app.models import entities  # noqa: E402,F401 — модели регистрируют таблицы в метаданных

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

config.set_main_option("sqlalchemy.url", settings.DATABASE_URL.replace("%", "%%"))

target_metadata = Base.metadata


def _sqlite_url() -> bool:
    return settings.DATABASE_URL.startswith("sqlite")


def run_migrations_offline() -> None:
    """Генерация SQL-скрипта без подключения к базе."""
    context.configure(
        url=settings.DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        render_as_batch=_sqlite_url(),
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Подключение к базе и выполнение миграций.

    Для SQLite миграции выполняются без общей транзакции и с отключённой
    проверкой внешних ключей. Причина в пакетном режиме: SQLite не умеет
    добавлять ограничение к существующей таблице, и Alembic пересоздаёт её —
    создаёт новую под временным именем, переносит данные и удаляет исходную.
    Удаление исходной таблицы невозможно при включённых внешних ключах, а
    `PRAGMA foreign_keys` игнорируется внутри транзакции. Поэтому соединение
    переводится в автокоммит, ключи отключаются на время миграций и включаются
    снова по завершении.
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            render_as_batch=_sqlite_url(),
            compare_type=True,
        )
        if not _sqlite_url():
            with context.begin_transaction():
                context.run_migrations()
            return

        connection = connection.execution_options(isolation_level="AUTOCOMMIT")
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            render_as_batch=True,
            compare_type=True,
        )
        connection.exec_driver_sql("PRAGMA foreign_keys=OFF")
        try:
            context.run_migrations()
        finally:
            connection.exec_driver_sql("PRAGMA foreign_keys=ON")


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
