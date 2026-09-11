"""Синхронизация схемы доказательного слоя с моделями.

Ревизия `dss_evidence01` создала восемь таблиц доказательного слоя с
`updated_at`, допускающим NULL, и без индексов, объявленных в моделях
(`index=True` на `code`, `status`, `entity`, `entity_code`, `method_code`).
Из-за этого база, собранная миграциями с нуля, не совпадала с моделями, и
проверка `alembic check` (gate в CI) падала: «миграции создают схему,
соответствующую моделям» перестало быть правдой.

Здесь недостающие индексы создаются, а `updated_at` приводится к NOT NULL.
Каждая операция защищена проверкой текущего состояния: на базе, которая уже
соответствует моделям (например, созданной из метаданных приложения),
ревизия не выполняет ни одного DDL и потому безопасна.
"""
from __future__ import annotations

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "sync01_model_indexes"
down_revision: str | None = "fix01_userdef"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

#: Индексы, объявленные в моделях, но не созданные ревизией dss_evidence01.
_INDEXES: tuple[tuple[str, str, tuple[str, ...]], ...] = (
    ("case_evidence", "ix_case_evidence_code", ("code",)),
    ("case_evidence", "ix_case_evidence_status", ("status",)),
    ("dependency_edges", "ix_dependency_edges_status", ("status",)),
    ("evidence_claims", "ix_evidence_claims_code", ("code",)),
    ("evidence_claims", "ix_evidence_claims_entity", ("entity",)),
    ("evidence_claims", "ix_evidence_claims_entity_code", ("entity_code",)),
    ("evidence_claims", "ix_evidence_claims_status", ("status",)),
    ("evidence_sources", "ix_evidence_sources_code", ("code",)),
    ("evidence_sources", "ix_evidence_sources_status", ("status",)),
    ("game_cases", "ix_game_cases_code", ("code",)),
    ("game_cases", "ix_game_cases_status", ("status",)),
    ("team_scenarios", "ix_team_scenarios_code", ("code",)),
    ("team_scenarios", "ix_team_scenarios_status", ("status",)),
    ("technology_nodes", "ix_technology_nodes_code", ("code",)),
    ("technology_nodes", "ix_technology_nodes_status", ("status",)),
    ("work_packages", "ix_work_packages_code", ("code",)),
    ("work_packages", "ix_work_packages_method_code", ("method_code",)),
    ("work_packages", "ix_work_packages_status", ("status",)),
)

#: Таблицы, у которых `updated_at` объявлен NOT NULL в моделях.
_NOT_NULL_UPDATED_AT: tuple[str, ...] = (
    "case_evidence", "dependency_edges", "evidence_claims", "evidence_sources",
    "game_cases", "team_scenarios", "technology_nodes", "work_packages",
)

_DATETIME = sa.DateTime(timezone=True)


def _index_names(inspector, table: str) -> set[str]:
    return {item["name"] for item in inspector.get_indexes(table)}


def _is_nullable(inspector, table: str, column: str) -> bool:
    for item in inspector.get_columns(table):
        if item["name"] == column:
            return bool(item["nullable"])
    return False


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    tables = set(inspector.get_table_names())

    # Сначала nullability: batch-режим SQLite пересоздаёт таблицу, поэтому
    # индексы создаются после, чтобы пересоздание их не затронуло.
    for table in _NOT_NULL_UPDATED_AT:
        if table not in tables:
            continue
        if not _is_nullable(inspector, table, "updated_at"):
            continue
        with op.batch_alter_table(table) as batch:
            batch.alter_column("updated_at", existing_type=_DATETIME, nullable=False)

    for table, name, columns in _INDEXES:
        if table not in tables:
            continue
        if name in _index_names(inspector, table):
            continue
        op.create_index(name, table, list(columns))


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    tables = set(inspector.get_table_names())

    for table, name, _columns in _INDEXES:
        if table in tables and name in _index_names(inspector, table):
            op.drop_index(name, table_name=table)

    for table in _NOT_NULL_UPDATED_AT:
        if table not in tables:
            continue
        if _is_nullable(inspector, table, "updated_at"):
            continue
        with op.batch_alter_table(table) as batch:
            batch.alter_column("updated_at", existing_type=_DATETIME, nullable=True)
