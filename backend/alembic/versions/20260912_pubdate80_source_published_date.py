"""Дата публикации источника хранится целиком.

Пакеты несут дату вместе с оговоркой куратора («2019-09-17 (последний акт
обновления)»), а колонка имела ширину 20 и загрузчик дополнительно срезал
значение тем же лимитом. В результате 227 источников хранили обрубок на
середине слова, причём вместе с датой терялась оговорка — то есть часть
провенанса записи. Ревизия расширяет колонку; значения восстанавливает
загрузчик пакетов, срабатывая только на прежнем (обрезанном) значении.

DDL защищён проверкой состояния: на базе, где ширина уже достаточна, ревизия
не выполняет ничего.
"""
from __future__ import annotations

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "pubdate80"
down_revision: str | None = "wpstagenote01"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_TABLE = "evidence_sources"
_COLUMN = "published_date"
_WIDTH = 80


def _current_width(inspector) -> int | None:
    for item in inspector.get_columns(_TABLE):
        if item["name"] == _COLUMN:
            return getattr(item["type"], "length", None)
    return None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if _TABLE not in set(inspector.get_table_names()):
        return
    width = _current_width(inspector)
    if width is None or width >= _WIDTH:
        return
    # SQLite не умеет ALTER COLUMN: расширение идёт пересборкой таблицы.
    with op.batch_alter_table(_TABLE) as batch:
        batch.alter_column(
            _COLUMN,
            existing_type=sa.String(width),
            type_=sa.String(_WIDTH),
            existing_nullable=False,
        )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if _TABLE not in set(inspector.get_table_names()):
        return
    width = _current_width(inspector)
    if width is None or width <= 20:
        return
    with op.batch_alter_table(_TABLE) as batch:
        batch.alter_column(
            _COLUMN,
            existing_type=sa.String(width),
            type_=sa.String(20),
            existing_nullable=False,
        )
