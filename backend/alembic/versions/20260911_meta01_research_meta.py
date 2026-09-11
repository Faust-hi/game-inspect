"""Метаданные исследовательского слоя: варианты реализации и основания связей.

Закрывает три поля, которые требовала спецификация, но которым не было места
в схеме:

* `methods.implementation_variants` — «варианты реализации» карточки метода
  (в исследованиях их 564, но переносить их было некуда);
* `methods.required_data_and_tools` — «требуемые данные и инструменты»;
* `conflicts.basis` и `dependency_edges.basis` — основание рекомендации
  «решение / workaround». Без него выведенное решение неотличимо от
  документированного, что и было нарушением принципа «источник или явное
  экспертное допущение».

Колонки добавляются с `server_default`: таблицы уже заполнены, а SQLite не
умеет снимать DEFAULT после добавления. Значения задаёт и модель, поэтому
расхождение на поведение не влияет. Каждая операция защищена проверкой
текущего состояния, поэтому на базе, собранной из метаданных приложения,
ревизия не выполняет ни одного DDL.
"""
from __future__ import annotations

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "meta01_research_meta"
down_revision: str | None = "sync01_model_indexes"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

#: (таблица, колонка, тип, server_default)
_COLUMNS: tuple[tuple[str, str, sa.types.TypeEngine, str], ...] = (
    ("methods", "implementation_variants", sa.JSON(), "'[]'"),
    ("methods", "required_data_and_tools", sa.Text(), "''"),
    ("conflicts", "basis", sa.String(length=30), "''"),
    ("dependency_edges", "basis", sa.String(length=30), "''"),
)


def _has_column(inspector, table: str, column: str) -> bool:
    return any(item["name"] == column for item in inspector.get_columns(table))


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    tables = set(inspector.get_table_names())

    for table, column, type_, default in _COLUMNS:
        if table not in tables or _has_column(inspector, table, column):
            continue
        op.add_column(
            table,
            sa.Column(column, type_, nullable=False, server_default=sa.text(default)),
        )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    tables = set(inspector.get_table_names())

    for table, column, _type, _default in _COLUMNS:
        if table not in tables or not _has_column(inspector, table, column):
            continue
        with op.batch_alter_table(table) as batch:
            batch.drop_column(column)
