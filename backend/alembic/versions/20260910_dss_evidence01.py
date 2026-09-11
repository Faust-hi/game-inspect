"""Доказательная база, кейсы, граф зависимостей и планирование.

Legacy-поля источника и стоимости намеренно не удаляются. Новая ревизия
добавляет нормализованный слой, чтобы один источник можно было переиспользовать
в claims, кейсах, hardware anchors и технологических зависимостях, а диапазон
трудоёмкости не подменялся одним баллом 1..5.
"""
from __future__ import annotations

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "dss_evidence01"
down_revision: str | None = "b2indep01"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _common_columns() -> list:
    return [
        sa.Column("status", sa.String(length=20), nullable=False, server_default="draft"),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    ]


def upgrade() -> None:
    # First create the source table because the optional provenance columns on
    # hardware and links reference it.
    op.create_table(
        "evidence_sources",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("code", sa.String(length=120), nullable=False),
        sa.Column("title", sa.String(length=300), nullable=False),
        sa.Column("authors", sa.String(length=300), nullable=False, server_default=""),
        sa.Column("publisher", sa.String(length=200), nullable=False, server_default=""),
        sa.Column("source_type", sa.String(length=40), nullable=False, server_default="secondary"),
        sa.Column("published_date", sa.String(length=20), nullable=False, server_default=""),
        sa.Column("checked_at", sa.String(length=30), nullable=False, server_default=""),
        sa.Column("url", sa.String(length=800), nullable=False, server_default=""),
        sa.Column("version", sa.String(length=80), nullable=False, server_default=""),
        sa.Column("platform", sa.String(length=120), nullable=False, server_default=""),
        sa.Column("locator", sa.String(length=300), nullable=False, server_default="overview"),
        sa.Column("availability", sa.String(length=30), nullable=False, server_default="available"),
        sa.Column("applicability", sa.Text(), nullable=False, server_default=""),
        sa.Column("notes", sa.Text(), nullable=False, server_default=""),
        *_common_columns(),
        sa.UniqueConstraint("code", name="uq_evidence_sources_code"),
        sa.CheckConstraint("status in ('draft', 'reviewed', 'published')", name="ck_evidence_sources_status"),
    )

    op.create_table(
        "evidence_claims",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("code", sa.String(length=160), nullable=False),
        sa.Column("entity", sa.String(length=60), nullable=False),
        sa.Column("entity_code", sa.String(length=120), nullable=False),
        sa.Column("field", sa.String(length=120), nullable=False),
        sa.Column("claim", sa.Text(), nullable=False),
        sa.Column("unit", sa.String(length=40), nullable=False, server_default=""),
        sa.Column("value_text", sa.Text(), nullable=False, server_default=""),
        sa.Column("value_num", sa.Float(), nullable=True),
        sa.Column("range_min", sa.Float(), nullable=True),
        sa.Column("range_max", sa.Float(), nullable=True),
        sa.Column("source_id", sa.Integer(), sa.ForeignKey("evidence_sources.id"), nullable=True),
        sa.Column("locator", sa.String(length=300), nullable=False, server_default=""),
        sa.Column("basis", sa.String(length=30), nullable=False, server_default="unknown"),
        sa.Column("verification_status", sa.String(length=30), nullable=False, server_default="unverified"),
        sa.Column("evidence_level", sa.String(length=20), nullable=False, server_default="low"),
        sa.Column("formula", sa.Text(), nullable=False, server_default=""),
        sa.Column("input_parameters", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column("context", sa.Text(), nullable=False, server_default=""),
        *_common_columns(),
        sa.UniqueConstraint("code", name="uq_evidence_claims_code"),
        sa.CheckConstraint("status in ('draft', 'reviewed', 'published')", name="ck_evidence_claims_status"),
    )

    op.create_table(
        "game_cases",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("code", sa.String(length=120), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("studio", sa.String(length=200), nullable=False, server_default=""),
        sa.Column("release_year", sa.Integer(), nullable=True),
        sa.Column("technology", sa.String(length=200), nullable=False, server_default=""),
        sa.Column("engine_code", sa.String(length=64), nullable=False, server_default=""),
        sa.Column("world_type", sa.String(length=80), nullable=False, server_default=""),
        sa.Column("network_mode", sa.String(length=120), nullable=False, server_default=""),
        sa.Column("summary", sa.Text(), nullable=False, server_default=""),
        sa.Column("relevance", sa.Text(), nullable=False, server_default=""),
        sa.Column("transfer_limits", sa.Text(), nullable=False, server_default=""),
        *_common_columns(),
        sa.UniqueConstraint("code", name="uq_game_cases_code"),
        sa.CheckConstraint("status in ('draft', 'reviewed', 'published')", name="ck_game_cases_status"),
    )

    op.create_table(
        "case_evidence",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("code", sa.String(length=160), nullable=False),
        sa.Column("case_id", sa.Integer(), sa.ForeignKey("game_cases.id"), nullable=False),
        sa.Column("function_code", sa.String(length=64), nullable=False, server_default=""),
        sa.Column("method_code", sa.String(length=64), nullable=False, server_default=""),
        sa.Column("fact", sa.Text(), nullable=False),
        sa.Column("match_level", sa.String(length=30), nullable=False, server_default="direct"),
        sa.Column("locator", sa.String(length=300), nullable=False, server_default=""),
        sa.Column("source_id", sa.Integer(), sa.ForeignKey("evidence_sources.id"), nullable=True),
        sa.Column("basis", sa.String(length=30), nullable=False, server_default="case_evidence"),
        sa.Column("transfer_limits", sa.Text(), nullable=False, server_default=""),
        *_common_columns(),
        sa.UniqueConstraint("code", name="uq_case_evidence_code"),
        sa.CheckConstraint("status in ('draft', 'reviewed', 'published')", name="ck_case_evidence_status"),
    )

    op.create_table(
        "technology_nodes",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("code", sa.String(length=160), nullable=False),
        sa.Column("node_type", sa.String(length=30), nullable=False),
        sa.Column("name", sa.String(length=220), nullable=False),
        sa.Column("version", sa.String(length=80), nullable=False, server_default=""),
        sa.Column("platform", sa.String(length=120), nullable=False, server_default=""),
        sa.Column("scope", sa.String(length=30), nullable=False, server_default="runtime"),
        sa.Column("docs_url", sa.String(length=800), nullable=False, server_default=""),
        sa.Column("source_id", sa.Integer(), sa.ForeignKey("evidence_sources.id"), nullable=True),
        *_common_columns(),
        sa.UniqueConstraint("code", name="uq_technology_nodes_code"),
        sa.CheckConstraint("status in ('draft', 'reviewed', 'published')", name="ck_technology_nodes_status"),
    )

    op.create_table(
        "dependency_edges",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("source_node_id", sa.Integer(), sa.ForeignKey("technology_nodes.id"), nullable=False),
        sa.Column("target_node_id", sa.Integer(), sa.ForeignKey("technology_nodes.id"), nullable=False),
        sa.Column("dependency_type", sa.String(length=30), nullable=False, server_default="requires"),
        sa.Column("mandatory", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("min_version", sa.String(length=80), nullable=False, server_default=""),
        sa.Column("max_version", sa.String(length=80), nullable=False, server_default=""),
        sa.Column("platform", sa.String(length=120), nullable=False, server_default=""),
        sa.Column("scope", sa.String(length=30), nullable=False, server_default="runtime"),
        sa.Column("severity", sa.Integer(), nullable=False, server_default="2"),
        sa.Column("source_id", sa.Integer(), sa.ForeignKey("evidence_sources.id"), nullable=True),
        sa.Column("description", sa.Text(), nullable=False, server_default=""),
        sa.Column("workaround", sa.Text(), nullable=False, server_default=""),
        *_common_columns(),
        sa.UniqueConstraint("source_node_id", "target_node_id", "dependency_type", name="uq_dependency_edge"),
        sa.CheckConstraint("status in ('draft', 'reviewed', 'published')", name="ck_dependency_edges_status"),
        sa.CheckConstraint("severity between 1 and 3", name="ck_dependency_edges_severity"),
    )

    op.create_table(
        "work_packages",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("code", sa.String(length=180), nullable=False),
        sa.Column("method_code", sa.String(length=64), nullable=False, server_default=""),
        sa.Column("name", sa.String(length=220), nullable=False),
        sa.Column("package_type", sa.String(length=40), nullable=False, server_default="integration"),
        sa.Column("role", sa.String(length=60), nullable=False, server_default="engineering"),
        sa.Column("min_days", sa.Float(), nullable=False, server_default="0"),
        sa.Column("p50_days", sa.Float(), nullable=False, server_default="1"),
        sa.Column("p80_days", sa.Float(), nullable=False, server_default="1.5"),
        sa.Column("parallelizable", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("recommended_stage", sa.String(length=20), nullable=False, server_default="prototype"),
        sa.Column("late_factor", sa.Float(), nullable=False, server_default="1"),
        sa.Column("dependency_codes", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("basis", sa.String(length=40), nullable=False, server_default="expert_estimate"),
        sa.Column("source_id", sa.Integer(), sa.ForeignKey("evidence_sources.id"), nullable=True),
        *_common_columns(),
        sa.UniqueConstraint("code", name="uq_work_packages_code"),
        sa.CheckConstraint("status in ('draft', 'reviewed', 'published')", name="ck_work_packages_status"),
        sa.CheckConstraint("p50_days >= 0 and p80_days >= p50_days", name="ck_work_package_bands"),
    )

    op.create_table(
        "team_scenarios",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("code", sa.String(length=40), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("description", sa.Text(), nullable=False, server_default=""),
        sa.Column("team_size", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("role_capacity", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column("parallel_tracks", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("communication_pct", sa.Float(), nullable=False, server_default="0.1"),
        sa.Column("unplanned_pct", sa.Float(), nullable=False, server_default="0.15"),
        sa.Column("specialist_capacity", sa.JSON(), nullable=False, server_default="{}"),
        *_common_columns(),
        sa.UniqueConstraint("code", name="uq_team_scenarios_code"),
        sa.CheckConstraint("status in ('draft', 'reviewed', 'published')", name="ck_team_scenarios_status"),
    )

    for table in ("method_engine_links",):
        with op.batch_alter_table(table) as batch:
            batch.add_column(sa.Column("source_locator", sa.String(length=300), nullable=False, server_default=""))
            batch.add_column(sa.Column("evidence_basis", sa.String(length=30), nullable=False, server_default="unknown"))
            batch.add_column(sa.Column("evidence_status", sa.String(length=30), nullable=False, server_default="unknown"))
    for table in ("hardware_cpu", "hardware_gpu"):
        with op.batch_alter_table(table) as batch:
            batch.add_column(sa.Column("benchmark_name", sa.String(length=180), nullable=False, server_default=""))
            batch.add_column(sa.Column("benchmark_context", sa.Text(), nullable=False, server_default=""))
            batch.add_column(sa.Column("benchmark_raw_value", sa.Float(), nullable=True))
            batch.add_column(sa.Column("normalization_note", sa.Text(), nullable=False, server_default=""))
            batch.add_column(sa.Column("evidence_basis", sa.String(length=30), nullable=False, server_default="derived"))
            batch.add_column(sa.Column(
                "evidence_source_id", sa.Integer(),
                sa.ForeignKey("evidence_sources.id", name=f"fk_{table}_evidence_source"),
                nullable=True,
            ))


def downgrade() -> None:
    for table in ("hardware_cpu", "hardware_gpu"):
        with op.batch_alter_table(table) as batch:
            batch.drop_column("evidence_source_id")
            batch.drop_column("evidence_basis")
            batch.drop_column("normalization_note")
            batch.drop_column("benchmark_raw_value")
            batch.drop_column("benchmark_context")
            batch.drop_column("benchmark_name")
    with op.batch_alter_table("method_engine_links") as batch:
        batch.drop_column("evidence_status")
        batch.drop_column("evidence_basis")
        batch.drop_column("source_locator")
    for table in ("team_scenarios", "work_packages", "dependency_edges", "technology_nodes", "case_evidence", "game_cases", "evidence_claims", "evidence_sources"):
        op.drop_table(table)
