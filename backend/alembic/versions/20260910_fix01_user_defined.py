"""Явная пометка пользовательских технологий.

Custom-движок и его инструменты — это внутренние сущности каталога, а не
внешне подтверждённые технологии. Без явного флага они выглядели в выдаче
как равноправные проверенные движки, что противоречит правилу «отсутствие
источника не трактуется как подтверждение».
"""
from __future__ import annotations

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "fix01_userdef"
down_revision: str | None = "dss_evidence01"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    for table in ("engines", "engine_tools"):
        with op.batch_alter_table(table) as batch:
            batch.add_column(
                sa.Column("is_user_defined", sa.Boolean(), nullable=False, server_default=sa.false())
            )
    # Собственный движок и его инструменты помечаются сразу: это свойство
    # каталога, а не решение администратора конкретной установки.
    op.execute(
        "UPDATE engines SET is_user_defined = 1 WHERE code = 'custom'"
    )
    op.execute(
        "UPDATE engine_tools SET is_user_defined = 1 "
        "WHERE engine_id IN (SELECT id FROM engines WHERE code = 'custom')"
    )


def downgrade() -> None:
    for table in ("engine_tools", "engines"):
        with op.batch_alter_table(table) as batch:
            batch.drop_column("is_user_defined")
