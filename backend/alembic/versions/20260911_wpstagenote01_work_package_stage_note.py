"""Примечание к рекомендованной стадии пакета работ.

Пакеты используют одно имя поля `recommended_stage` для двух разных смыслов:
кода перечисления `DevStage` и развёрнутой текстовой рекомендации. Загрузчик
пакетов нормализует значение к коду, а исходный текст обязан сохраняться как
примечание — это прямо записано в контракте `pack_loader.normalize_stage`, —
но сохранять его было некуда, и текст молча терялся (512 записей в двух
пакетах). Ревизия добавляет колонку `stage_note`.

DDL защищён проверкой состояния: на базе, где колонка уже есть (например,
созданной из метаданных приложения), ревизия не выполняет ничего.
"""
from __future__ import annotations

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "wpstagenote01"
down_revision: str | None = "meta01_research_meta"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_TABLE = "work_packages"
_COLUMN = "stage_note"


def _has_column(inspector, table: str, column: str) -> bool:
    return any(item["name"] == column for item in inspector.get_columns(table))


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if _TABLE not in set(inspector.get_table_names()):
        return
    if _has_column(inspector, _TABLE, _COLUMN):
        return
    # NOT NULL с серверным значением по умолчанию: заполненная база получает
    # пустую строку, а модель — то же значение по умолчанию, что и в Python.
    op.add_column(
        _TABLE,
        sa.Column(_COLUMN, sa.Text(), nullable=False, server_default=""),
    )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if _TABLE not in set(inspector.get_table_names()):
        return
    if not _has_column(inspector, _TABLE, _COLUMN):
        return
    with op.batch_alter_table(_TABLE) as batch:
        batch.drop_column(_COLUMN)
