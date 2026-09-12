"""Публикация доказательств: источник есть — утверждение видно.

Дефект этого класса: загрузчик пакетов не задавал статус вовсе, поэтому все
утверждения из пакетов навсегда оставались черновиками. Целые семейства
доказательств (инструменты движков, движки, технологические узлы, стадии,
профили нагрузки, сетевые режимы, риски, целевые метрики, платформы) были
недостижимы через API и отчёт, хотя источник у каждого утверждения был.

Спека формулирует правило однозначно: «запись без обязательного источника не
публикуется». Обратное тоже верно и здесь проверяется: запись с источником
обязана попадать в публичную выдачу.
"""
from __future__ import annotations

import pytest

from app.seed.pack_loader import DRAFT, PUBLISHED

pytestmark = pytest.mark.extended


#: Семейства доказательств, которые обязаны быть публичными, потому что
#: их источник — конкретный документ, а не экспертное допущение без ссылки.
REQUIRED_PUBLIC_FAMILIES = (
    "game_function",
    "engine",
    "engine_tool",
    "technology_node",
    "target_metric",
    "stage_budget",
    "load_profile",
    "network_mode",
    "target_platform",
    "risk_factor",
    "research",
)


def test_every_family_with_sources_is_visible(client):
    """У каждого семейства с источником есть хотя бы одно публичное утверждение.

    Проверка ловит возврат к прежнему поведению, когда статус не задавался и
    семейство целиком выпадало из выдачи.
    """
    response = client.get("/api/catalog/evidence")
    assert response.status_code == 200, response.text
    public = response.json()
    assert public, "публичная выдача доказательств не должна быть пустой"

    families = {claim["entity"] for claim in public}
    missing = [name for name in REQUIRED_PUBLIC_FAMILIES if name not in families]
    assert not missing, f"семейства без публичных утверждений: {missing}"


def test_category_two_claims_carry_sources_and_calculations(client):
    """Доказательства проектирования опираются на источник или на расчёт.

    Спека допускает два равноправных способа обоснования: внешний источник с
    локатором либо воспроизводимый расчёт (формула и входные параметры). Ни
    одно из утверждений параметров проектирования не должно оставаться без
    обоих: тогда проверить его нечем.

    Поле ответа называется `source`: API отдаёт источник целиком, а не его id.
    """
    response = client.get("/api/catalog/evidence")
    assert response.status_code == 200, response.text
    claims = [c for c in response.json() if c["entity"] in REQUIRED_PUBLIC_FAMILIES]
    assert claims, "нет публичных доказательств по параметрам проектирования"

    for claim in claims:
        has_source = claim["source"] is not None
        has_calculation = bool(claim.get("formula")) and bool(claim.get("input_parameters"))
        assert has_source or has_calculation, (
            f"утверждение без источника и без расчёта: {claim['code']}"
        )
        if claim["basis"] == "derived":
            # Производное значение обязано быть воспроизводимым: без формулы и
            # входных параметров его нельзя пересчитать, и оно не отличается от
            # необоснованного числа.
            assert has_calculation, f"derived без формулы или входных параметров: {claim['code']}"
