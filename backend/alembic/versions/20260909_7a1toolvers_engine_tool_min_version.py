"""add engine tool min version

Revision ID: 7a1toolvers
Revises: e103004d1fae
Create Date: 2026-09-09

Добавляет `engine_tools.min_version` — минимальную версию движка, в которой
встроенный инструмент существует. Без неё наличие инструмента определялось
только по названию, и встроенный Nanite показывался доступным для UE 4.27,
где его нет: решение превращалось в «настроить встроенную подсистему» вместо
собственной реализации с другой стоимостью внедрения.

Пустое значение означает не «доступен всегда», а «граница не подтверждена»:
миграция не заполняет колонку, чтобы отсутствие данных не выдавалось за
подтверждённую доступность.
"""

from __future__ import annotations

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

# Идентификатор ревизии; используется Alembic.
revision: str = '7a1toolvers'
down_revision: str | None = 'e103004d1fae'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("engine_tools", sa.Column("min_version", sa.String(40), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table("engine_tools") as batch_op:
        batch_op.drop_column("min_version")
