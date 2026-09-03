"""Ограничения целостности для баз, созданных до появления миграций.

Первичная ревизия создаёт схему целиком и подходит для новой базы. Базы,
созданные `create_all` на более ранней версии моделей, уже содержат таблицы,
но не содержат проверочных ограничений: `create_all` не изменяет существующие
таблицы. Без этих ограничений инварианты каталога существуют только в коде —
запрос в обход приложения может записать статус вне перечня или оценку влияния
вне диапазона.

Миграция проверяет, каких ограничений не хватает, и добавляет только их. На
свежей базе, где ограничения уже созданы первой ревизией, она ничего не делает:
это позволяет применять её и к новым, и к существующим базам.

Revision ID: 0c7ee9887f46
Revises: cdf89f70b108
Create Date: 2026-09-03 17:20:17.573656

"""
from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# Идентификатор ревизии; используется Alembic.
revision: str = '0c7ee9887f46'
down_revision: str | None = 'cdf89f70b108'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

#: Перечень допустимых статусов. Повторяет перечисление приложения.
STATUS_CHECK = "status in ('draft', 'reviewed', 'published')"

#: Ограничения, которые обязаны присутствовать в схеме: таблица → список пар
#: «имя ограничения — условие». Состав соответствует моделям приложения.
CONSTRAINTS: dict[str, list[tuple[str, str]]] = {
    "game_functions": [("ck_status_values", STATUS_CHECK)],
    "methods": [
        ("ck_status_values", STATUS_CHECK),
        ("ck_methods_gain", "performance_gain between 0.0 and 1.0"),
        ("ck_methods_confidence", "confidence between 0.0 and 1.0"),
        ("ck_methods_cost", "implementation_cost between 1 and 5"),
        ("ck_methods_complexity", "complexity between 1 and 5"),
        ("ck_methods_quality", "quality_impact between -2 and 2"),
        ("ck_methods_concept", "concept_impact between -2 and 0"),
        ("ck_methods_impact_cpu", "impact_cpu between -3 and 3"),
        ("ck_methods_impact_gpu", "impact_gpu between -3 and 3"),
        ("ck_methods_impact_ram", "impact_ram between -3 and 3"),
        ("ck_methods_impact_vram", "impact_vram between -3 and 3"),
        ("ck_methods_impact_disk", "impact_disk between -3 and 3"),
        ("ck_methods_impact_network", "impact_network between -3 and 3"),
    ],
    "engines": [("ck_status_values", STATUS_CHECK)],
    "engine_tools": [("ck_status_values", STATUS_CHECK)],
    "method_engine_links": [("ck_status_values", STATUS_CHECK)],
    "conflicts": [
        ("ck_status_values", STATUS_CHECK),
        ("ck_conflicts_distinct", "a_code <> b_code"),
        ("ck_conflicts_severity", "severity between 1 and 3"),
    ],
    "game_examples": [("ck_status_values", STATUS_CHECK)],
    "hardware_cpu": [
        ("ck_status_values", STATUS_CHECK),
        ("ck_cpu_class", "perf_class between 1 and 5"),
        ("ck_cpu_single", "single_thread_score between 0.0 and 1.0"),
        ("ck_cpu_multi", "multi_thread_score between 0.0 and 1.0"),
    ],
    "hardware_gpu": [
        ("ck_status_values", STATUS_CHECK),
        ("ck_gpu_class", "perf_class between 1 and 5"),
        ("ck_gpu_raster", "raster_score between 0.0 and 1.0"),
        ("ck_gpu_rt", "rt_score between 0.0 and 1.0"),
    ],
}


def _existing_constraints(table: str) -> set[str]:
    """Имена проверочных ограничений, уже присутствующих в таблице."""
    inspector = sa.inspect(op.get_bind())
    if table not in inspector.get_table_names():
        return set()
    try:
        return {item["name"] for item in inspector.get_check_constraints(table)}
    except NotImplementedError:
        # Диалект не сообщает ограничения: считаем, что их нет, и добавляем.
        return set()


def upgrade() -> None:
    for table, items in CONSTRAINTS.items():
        present = _existing_constraints(table)
        missing = [(name, condition) for name, condition in items if name not in present]
        if not missing:
            continue
        # SQLite не добавляет ограничение к существующей таблице: в пакетном
        # режиме Alembic пересоздаёт таблицу и переносит данные самостоятельно.
        with op.batch_alter_table(table) as batch:
            for name, condition in missing:
                batch.create_check_constraint(name, condition)


def downgrade() -> None:
    for table, items in CONSTRAINTS.items():
        present = _existing_constraints(table)
        existing = [name for name, _ in items if name in present]
        if not existing:
            continue
        with op.batch_alter_table(table) as batch:
            for name in existing:
                batch.drop_constraint(name, type_="check")
