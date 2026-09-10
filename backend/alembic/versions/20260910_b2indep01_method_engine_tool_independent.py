"""add method engine tool independence

Revision ID: b2indep01
Revises: 7a1toolvers
Create Date: 2026-09-10

Добавляет `methods.engine_tool_independent` — признак, что решение реализуется
своими средствами и не опирается на встроенный инструмент движка.

Без него отсутствие связей с инструментами (`method_engine_links`) означало
два разных состояния, которые выдача не различала: «методу не нужен
встроенный инструмент» (сетевой код и античит пишутся поверх движка,
DirectStorage — платформенный API) и «данных нет». В карточке оба выглядели
как пустая привязка к версии движка.

По умолчанию False, то есть отсутствие связей по-прежнему считается пробелом
в данных: признак проставляется только там, где независимость обоснована.
Миграция не заполняет колонку для существующих записей — это сделает синхронизация
каталога при запуске, а не догадка в миграции.
"""

from __future__ import annotations

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

# Идентификатор ревизии; используется Alembic.
revision: str = 'b2indep01'
down_revision: str | None = '7a1toolvers'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Значение по умолчанию задаётся на стороне СУБД, потому что колонка
    # добавляется в уже заполненную таблицу: без него EXISTS-строки получили бы
    # NULL при ограничении NOT NULL. Снимать его после заполнения нельзя —
    # SQLite не поддерживает `ALTER COLUMN ... DROP DEFAULT`, из-за чего
    # миграция падала на этой базе. Значение задаёт и модель (`default=False`),
    # поэтому расхождение на поведение не влияет.
    op.add_column(
        "methods",
        sa.Column("engine_tool_independent", sa.Boolean(), nullable=False, server_default=sa.false()),
    )


def downgrade() -> None:
    with op.batch_alter_table("methods") as batch_op:
        batch_op.drop_column("engine_tool_independent")
