"""drop_cases_and_planning

Удаляет подсистемы, вырезанные из бэкенда 2026-09-12:
  * игровые кейсы — `game_cases`, `case_evidence`;
  * планирование трудоёмкости — `work_packages`, `team_scenarios`.

Порядок удаления — от дочерних к родительским: `case_evidence` ссылается на
`game_cases` и `evidence_sources`, поэтому падает первым. Доказательный слой
(`evidence_sources`, `evidence_claims`, `technology_nodes`, `dependency_edges`)
не затрагивается.

Revision ID: wcut01
Revises: pubdate80
Create Date: 2026-09-12
"""
from __future__ import annotations

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

# Идентификатор ревизии; используется Alembic.
revision: str = "wcut01"
down_revision: str | None = "pubdate80"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


#: (таблица, индексы) в порядке удаления: дочерние первыми.
_DROP_ORDER: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("case_evidence", ("ix_case_evidence_status", "ix_case_evidence_code")),
    ("work_packages", (
        "ix_work_packages_method_code", "ix_work_packages_code", "ix_work_packages_status",
    )),
    ("team_scenarios", ("ix_team_scenarios_status", "ix_team_scenarios_code")),
    ("game_cases", ("ix_game_cases_status", "ix_game_cases_code")),
)


def upgrade() -> None:
    """Удалить таблицы кейсов и планирования трудоёмкости.

    Таблицы могут отсутствовать в базах, созданных после удаления
    соответствующих ORM-моделей из metadata, поэтому существование
    проверяется перед каждым удалением.
    """
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    tables = set(inspector.get_table_names())

    for table, table_indexes in _DROP_ORDER:
        if table not in tables:
            continue
        present = {ix["name"] for ix in inspector.get_indexes(table)}
        for index in table_indexes:
            if index in present:
                op.drop_index(index, table_name=table)
        op.drop_table(table)


def downgrade() -> None:
    """Воссоздать таблицы кейсов и планирования (обратная операция)."""
    op.create_table(
        "game_cases",
        sa.Column("id", sa.INTEGER(), nullable=False),
        sa.Column("code", sa.VARCHAR(length=120), nullable=False),
        sa.Column("title", sa.VARCHAR(length=200), nullable=False),
        sa.Column("studio", sa.VARCHAR(length=200), nullable=False),
        sa.Column("release_year", sa.INTEGER(), nullable=True),
        sa.Column("technology", sa.VARCHAR(length=200), nullable=False),
        sa.Column("engine_code", sa.VARCHAR(length=64), nullable=False),
        sa.Column("world_type", sa.VARCHAR(length=80), nullable=False),
        sa.Column("network_mode", sa.VARCHAR(length=120), nullable=False),
        sa.Column("summary", sa.TEXT(), nullable=False),
        sa.Column("relevance", sa.TEXT(), nullable=False),
        sa.Column("transfer_limits", sa.TEXT(), nullable=False),
        sa.Column("status", sa.VARCHAR(length=20), nullable=False),
        sa.Column("updated_at", sa.DATETIME(), nullable=False),
        sa.CheckConstraint(
            "status in ('draft', 'reviewed', 'published')", name="ck_status_values",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code", name="uq_game_cases_code"),
    )
    with op.batch_alter_table("game_cases", schema=None) as batch_op:
        batch_op.create_index("ix_game_cases_status", ["status"], unique=False)
        batch_op.create_index("ix_game_cases_code", ["code"], unique=False)

    op.create_table(
        "team_scenarios",
        sa.Column("id", sa.INTEGER(), nullable=False),
        sa.Column("code", sa.VARCHAR(length=40), nullable=False),
        sa.Column("name", sa.VARCHAR(length=120), nullable=False),
        sa.Column("description", sa.TEXT(), nullable=False),
        sa.Column("team_size", sa.INTEGER(), nullable=False),
        sa.Column("role_capacity", sqlite.JSON(), nullable=False),
        sa.Column("parallel_tracks", sa.INTEGER(), nullable=False),
        sa.Column("communication_pct", sa.FLOAT(), nullable=False),
        sa.Column("unplanned_pct", sa.FLOAT(), nullable=False),
        sa.Column("specialist_capacity", sqlite.JSON(), nullable=False),
        sa.Column("status", sa.VARCHAR(length=20), nullable=False),
        sa.Column("updated_at", sa.DATETIME(), nullable=False),
        sa.CheckConstraint(
            "status in ('draft', 'reviewed', 'published')", name="ck_status_values",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code", name="uq_team_scenarios_code"),
    )
    with op.batch_alter_table("team_scenarios", schema=None) as batch_op:
        batch_op.create_index("ix_team_scenarios_status", ["status"], unique=False)
        batch_op.create_index("ix_team_scenarios_code", ["code"], unique=False)

    op.create_table(
        "work_packages",
        sa.Column("id", sa.INTEGER(), nullable=False),
        sa.Column("code", sa.VARCHAR(length=180), nullable=False),
        sa.Column("method_code", sa.VARCHAR(length=64), nullable=False),
        sa.Column("name", sa.VARCHAR(length=220), nullable=False),
        sa.Column("package_type", sa.VARCHAR(length=40), nullable=False),
        sa.Column("role", sa.VARCHAR(length=60), nullable=False),
        sa.Column("min_days", sa.FLOAT(), nullable=False),
        sa.Column("p50_days", sa.FLOAT(), nullable=False),
        sa.Column("p80_days", sa.FLOAT(), nullable=False),
        sa.Column("parallelizable", sa.BOOLEAN(), nullable=False),
        sa.Column("recommended_stage", sa.VARCHAR(length=20), nullable=False),
        sa.Column("late_factor", sa.FLOAT(), nullable=False),
        sa.Column("dependency_codes", sqlite.JSON(), nullable=False),
        sa.Column("basis", sa.VARCHAR(length=40), nullable=False),
        sa.Column("source_id", sa.INTEGER(), nullable=True),
        sa.Column("status", sa.VARCHAR(length=20), nullable=False),
        sa.Column("updated_at", sa.DATETIME(), nullable=False),
        sa.Column("stage_note", sa.TEXT(), server_default="", nullable=False),
        sa.CheckConstraint(
            "status in ('draft', 'reviewed', 'published')", name="ck_status_values",
        ),
        sa.CheckConstraint(
            "p50_days >= 0 and p80_days >= p50_days", name="ck_work_package_bands",
        ),
        sa.ForeignKeyConstraint(["source_id"], ["evidence_sources.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code", name="uq_work_packages_code"),
    )
    with op.batch_alter_table("work_packages", schema=None) as batch_op:
        batch_op.create_index("ix_work_packages_method_code", ["method_code"], unique=False)
        batch_op.create_index("ix_work_packages_code", ["code"], unique=False)
        batch_op.create_index("ix_work_packages_status", ["status"], unique=False)

    op.create_table(
        "case_evidence",
        sa.Column("id", sa.INTEGER(), nullable=False),
        sa.Column("code", sa.VARCHAR(length=160), nullable=False),
        sa.Column("case_id", sa.INTEGER(), nullable=False),
        sa.Column("function_code", sa.VARCHAR(length=64), nullable=False),
        sa.Column("method_code", sa.VARCHAR(length=64), nullable=False),
        sa.Column("fact", sa.TEXT(), nullable=False),
        sa.Column("match_level", sa.VARCHAR(length=30), nullable=False),
        sa.Column("locator", sa.VARCHAR(length=300), nullable=False),
        sa.Column("source_id", sa.INTEGER(), nullable=True),
        sa.Column("basis", sa.VARCHAR(length=30), nullable=False),
        sa.Column("transfer_limits", sa.TEXT(), nullable=False),
        sa.Column("status", sa.VARCHAR(length=20), nullable=False),
        sa.Column("updated_at", sa.DATETIME(), nullable=False),
        sa.CheckConstraint(
            "status in ('draft', 'reviewed', 'published')", name="ck_status_values",
        ),
        sa.ForeignKeyConstraint(["case_id"], ["game_cases.id"]),
        sa.ForeignKeyConstraint(["source_id"], ["evidence_sources.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code", name="uq_case_evidence_code"),
    )
    with op.batch_alter_table("case_evidence", schema=None) as batch_op:
        batch_op.create_index("ix_case_evidence_status", ["status"], unique=False)
        batch_op.create_index("ix_case_evidence_code", ["code"], unique=False)
