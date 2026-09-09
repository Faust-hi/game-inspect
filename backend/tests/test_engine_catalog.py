"""Движок проекта выбирается из каталога, а не из перечисления в схеме.

Раньше допустимые коды были зашиты в схему анкеты, поэтому движок, добавленный
через каталог, отклонялся до обращения к базе: расширение базы знаний «без
изменения кода» не работало. Проверка перенесена в слой, где видно фактическое
наполнение каталога.
"""
from __future__ import annotations

import pytest

from app.models.entities import Engine, EngineTool
from app.services import engines as engine_catalog

LEGACY_CODES = ["unreal", "unity", "godot", "cryengine", "source", "heroengine", "custom"]

CALCULATION_ENDPOINTS = [
    "/api/recommend",
    "/api/load-profile",
    "/api/hardware-estimate",
]


@pytest.fixture
def new_engine(db) -> Engine:
    """Движок, добавленный через каталог: его нет в прежнем перечислении."""
    engine = Engine(
        code="defold", name="Defold", docs_url="https://defold.com/", status="published",
    )
    db.add(engine)
    db.flush()
    return engine


def _post(client, path: str, basket: list[str] | None = None, **profile_overrides):
    profile = {
        "name": "Проект", "format": "3D", "world_type": "open_world", "scale": "large",
        "stage": "prototype", "engine": "unreal", "platforms": ["pc_windows"],
        "functions": [], "target_resolution": "1080p", "target_quality": "high",
        "target_fps": 60,
    }
    profile.update(profile_overrides)
    return client.post(path, json={"profile": profile, "basket": basket or []})


@pytest.mark.parametrize("path", CALCULATION_ENDPOINTS)
def test_engine_added_through_catalog_is_accepted(client, new_engine, path):
    """Новый движок принимается всеми расчётами без изменения кода."""
    response = _post(client, path, engine=new_engine.code)

    assert response.status_code == 200, response.text


def test_legacy_engine_codes_remain_valid(client, db):
    """Прежние коды сохранены: совместимость со старыми проектами не нарушена."""
    codes = engine_catalog.known_codes(db)

    for code in LEGACY_CODES:
        assert code in codes, f"Код движка «{code}» пропал из каталога"


@pytest.mark.parametrize("path", CALCULATION_ENDPOINTS)
def test_unknown_engine_is_rejected(client, path):
    """Неизвестный движок не проходит молча: расчёт без инструментов пуст."""
    response = _post(client, path, engine="no_such_engine")

    assert response.status_code == 422, response.text
    body = response.json()
    assert body["code"] == "validation_error"
    assert "no_such_engine" in body["error"]
    # Сообщение обязано помогать: называть допустимые коды, а не только отказ.
    assert any("unreal" in item for item in body["details"]), body["details"]
    assert body["request_id"]


def test_draft_engine_is_not_offered(client, db):
    """Черновой движок не доступен для выбора, пока не опубликован."""
    db.add(Engine(code="draft_engine", name="Черновик", docs_url="https://e.org", status="draft"))
    db.flush()

    assert "draft_engine" not in engine_catalog.known_codes(db)
    assert _post(client, "/api/recommend", engine="draft_engine").status_code == 422


def test_empty_catalog_falls_back_to_legacy_codes(db):
    """Пустой каталог не делает приложение непригодным до заполнения."""
    for engine in engine_catalog.published_engines(db):
        engine.status = "draft"
    db.flush()

    assert engine_catalog.known_codes(db) == LEGACY_CODES


@pytest.mark.parametrize("code", ["", "un real", "../etc", "движок"])
def test_engine_code_shape_is_checked(client, code):
    """Код движка — идентификатор, а не произвольный текст."""
    assert _post(client, "/api/recommend", engine=code).status_code == 422


# --- Версия движка и наличие встроенного инструмента ------------------------

@pytest.mark.parametrize("actual,required,expected", [
    ("5.0", "5.0", True),
    ("5.5", "5.0", True),
    ("4.27", "5.0", False),
    ("2022 LTS", "2021 LTS", True),
    ("Source 2", "5.0", None),          # номер не извлекается
    (None, "5.0", None),                # версия не указана
    ("4.27", None, None),               # граница не задана
])
def test_version_at_least_distinguishes_unknown_from_available(actual, required, expected):
    """Неопределённость не приравнивается к доступности инструмента."""
    assert engine_catalog.version_at_least(actual, required) is expected


def test_nanite_is_unavailable_for_ue_4_27(db):
    """Встроенного Nanite в 4.27 нет: граница версии задана в каталоге."""
    from sqlalchemy import select

    tool = db.scalar(select(EngineTool).where(EngineTool.code == "ue_nanite"))
    assert tool is not None and tool.min_version == "5.0"

    unavailable = engine_catalog.unavailable_tools(db, "unreal", "4.27")
    assert "ue_nanite" in unavailable, unavailable
    assert engine_catalog.unavailable_tools(db, "unreal", "5.5") == {}


def test_recommendation_marks_builtin_tool_missing_in_engine_version(client, db):
    """Карточка не выдаёт отсутствующий в версии инструмент за готовый аналог."""
    response = _post(
        client, "/api/recommend", engine="unreal", engine_version="4.27",
        functions=["large_scale_terrain"],
    )
    assert response.status_code == 200
    payload = response.json()
    cards = [
        row for row in payload["recommendations"]
        if row["method_code"] == "virtual_geometry_clusters"
    ]
    assert cards, [row["method_code"] for row in payload["recommendations"]]
    support = cards[0]["engine_support"]
    assert support is not None and support["tool_code"] == "ue_nanite"
    assert support["available"] is False
    assert "4.27" in (support["availability_note"] or "")


def test_missing_builtin_tool_becomes_visible_risk(client, db):
    """Встроенный инструмент без версии — риск плана, а не молчаливая подмена."""
    response = _post(
        client, "/api/recommend", basket=["virtual_geometry_clusters"],
        engine="unreal", engine_version="4.27", functions=["large_scale_terrain"],
    )
    assert response.status_code == 200
    codes = {risk["code"] for risk in response.json()["risks"]}
    assert "engine_tool_version" in codes, codes
