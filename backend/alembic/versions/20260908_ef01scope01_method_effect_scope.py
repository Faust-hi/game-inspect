"""add method effect scope

Revision ID: ef01scope01
Revises: f225calib01
Create Date: 2026-09-08

Добавляет `methods.effect_scope` — область, в которой проявляется эффект
метода. Без неё оценка оборудования складывала в нагрузку клиента и серверную
экономию, и ускорение разработки: выделенный сервер без графики уменьшал
требования к GPU игрока, а быстрый пересчёт лайтмапов — требования к его
процессу.

Существующие записи получают `client`: это прежнее поведение модели, поэтому
миграция не меняет результаты, а лишь делает область эффекта задаваемой.
"""

from __future__ import annotations

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

# Идентификатор ревизии; используется Alembic.
revision: str = 'ef01scope01'
down_revision: str | None = 'f225calib01'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Значение не задаётся умолчанием схемы: дальше им управляет приложение,
    # а расхождение схемы с моделями ловит `alembic check`. Заполнение идёт
    # отдельным оператором, а не `server_default`: SQLite не умеет снимать
    # умолчание на месте, для этого таблица пересоздаётся, а копия строк при
    # пересоздании не получает значений из временного умолчания.
    op.add_column("methods", sa.Column("effect_scope", sa.String(20), nullable=True))
    op.execute("UPDATE methods SET effect_scope = 'client' WHERE effect_scope IS NULL")
    with op.batch_alter_table("methods") as batch_op:
        batch_op.alter_column("effect_scope", existing_type=sa.String(20), nullable=False)


def downgrade() -> None:
    with op.batch_alter_table("methods") as batch_op:
        batch_op.drop_column("effect_scope")
