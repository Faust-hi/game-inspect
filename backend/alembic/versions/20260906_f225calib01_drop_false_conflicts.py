"""drop false conflict rows (FULL225 calibration)

Revision ID: f225calib01
Revises: b140134d9bc2
Create Date: 2026-09-06

Удаляет 7 связей, признанных ложными калибровкой FULL225 (доказательства —
контрпримеры shipped-игр, см. CALIBRATION_FULL225.md и комментарий в
app/seed/methods_data.py). Сидер делает только upsert, поэтому без миграции
старые БД сохранили бы удалённые строки.
"""

from __future__ import annotations

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

# Идентификатор ревизии; используется Alembic.
revision: str = 'f225calib01'
down_revision: str | None = 'b140134d9bc2'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

REMOVED: list[tuple[str, str, str]] = [
    ("baked_occlusion_culling", "world_partition_streaming", "conflict"),
    ("dynamic_resolution_scaling", "temporal_upscaling", "conflict"),
    ("fixed_timestep_physics", "multithreaded_physics_jobs", "dependency"),
    ("client_prediction_reconciliation", "fixed_timestep_physics", "dependency"),
    ("ecs_data_oriented_crowd", "gpu_skinning_compute", "dependency"),
    ("headless_dedicated_server", "client_prediction_reconciliation", "dependency"),
    ("destruction_geometry_cache", "async_loading_pipeline", "dependency"),
]


def upgrade() -> None:
    conn = op.get_bind()
    for a_code, b_code, conflict_type in REMOVED:
        conn.execute(
            sa.text(
                "DELETE FROM conflicts WHERE a_code = :a AND b_code = :b "
                "AND conflict_type = :t"
            ),
            {"a": a_code, "b": b_code, "t": conflict_type},
        )


def downgrade() -> None:
    # Откат возвращает строки как черновики без исходных текстов: полные тексты
    # живут в methods_data.py соответствующей ревизии и подтянутся сидером.
    conn = op.get_bind()
    for a_code, b_code, conflict_type in REMOVED:
        conn.execute(
            sa.text(
                "INSERT INTO conflicts (a_code, b_code, conflict_type, severity, description, "
                "resolution, status, source_url) SELECT :a, :b, :t, 2, '', '', 'draft', '' "
                "WHERE NOT EXISTS (SELECT 1 FROM conflicts WHERE a_code = :a AND b_code = :b "
                "AND conflict_type = :t)"
            ),
            {"a": a_code, "b": b_code, "t": conflict_type},
        )
