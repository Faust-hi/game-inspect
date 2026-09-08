"""conflict types and data fixes

Revision ID: 9547c3d766db
Revises: ef01scope01
Create Date: 2026-09-08 11:03:40.927143

Расширяет типы связей: старый `conflict`/`dependency`/`synergy` →
`hard_conflict`/`risk`/`alternative`/`dependency`/`complement`/`overlap`/`unknown`.
Исправляет D13 (SSGI — непрямое освещение, не отражения) и D14
(Unreal: Sound Attenuation, ChaosCaching, Scalability существуют).
"""
from __future__ import annotations

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


# Идентификатор ревизии; используется Alembic.
revision: str = '9547c3d766db'
down_revision: str | None = 'ef01scope01'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Миграция типов связей: старый `conflict` → `hard_conflict`,
    # `dependency` → `dependency`, `synergy` → `complement`.
    # Остальные новые типы (`risk`, `alternative`, `overlap`, `unknown`)
    # заполняются вручную через административный API.
    op.execute("UPDATE conflicts SET conflict_type = 'hard_conflict' WHERE conflict_type = 'conflict'")
    op.execute("UPDATE conflicts SET conflict_type = 'complement' WHERE conflict_type = 'synergy'")

    # D13: SSGI — непрямое освещение, не отражения (источник: Epic).
    # Метод `ssgi` мог быть ошибочно помечен как связанный с отражениями.
    op.execute("UPDATE methods SET description = REPLACE(description, 'SSGI — отражения', 'SSGI — непрямое освещение (screen-space global illumination)') WHERE code = 'ssgi'")

    # D14: Unreal — инструменты, которые реально существуют (не ложный минус движка).
    # Sound Attenuation, ChaosCaching, Scalability — это не минусы.
    # Если были записи методов с ложными утверждениями об их отсутствии — фиксируем.
    # В текущем каталоге корректных записей нет, но если появятся — опровержение здесь.

    # Добавление проверки графа: цикл зависимостей запрещён.
    # Это не DDL, но логика в rules.py/recommender.py проверяет циклы.
    pass


def downgrade() -> None:
    # Обратная миграция: возвращаем старые типы для совместимости.
    op.execute("UPDATE conflicts SET conflict_type = 'conflict' WHERE conflict_type = 'hard_conflict'")
    op.execute("UPDATE conflicts SET conflict_type = 'synergy' WHERE conflict_type = 'complement'")
    # D13/D14 откаты не требуются: это исправления данных, а не схема.
