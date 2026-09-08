"""Жизненный цикл публикации для всех сущностей каталога (D26).

Раньше смена статуса работала только для методов: движок, инструмент, пример
игры или процессор, добавленные через каталог, оставались черновиками навсегда,
и обещание «расширять базу без изменения кода» не выполнялось.

Проверки строятся так, чтобы была видна не только механика перехода, но и
предметное требование: каждая сущность публикуется лишь при наличии источника,
причём поля источника у сущностей называются по-разному.
"""
from __future__ import annotations

import pytest
from sqlalchemy import select

from app.models.entities import (
    Conflict, Engine, EngineTool, GameFunction, HardwareCPU, HardwareGPU,
    Method, MethodEngineLink, PublicationLog,
)
from app.models.enums import Status
from app.services import publication

SOURCE_URL = "https://example.org/source"
SOURCE_TITLE = "Источник"


# ---------------------------------------------------------------------------
# Помощники: создать запись, удовлетворяющую политике своей сущности
# ---------------------------------------------------------------------------
def _add(db, model, values: dict, overrides: dict):
    """Добавить черновую запись: переопределения накладываются на значения."""
    obj = model(**{**values, **overrides, "status": overrides.get("status", Status.DRAFT.value)})
    db.add(obj)
    db.flush()
    return obj


def _method(db, code: str, **overrides) -> Method:
    return _add(db, Method, {
        "code": code, "name": f"Метод {code}",
        "source_url": SOURCE_URL, "source_title": SOURCE_TITLE,
    }, overrides)


def _function(db, code: str, **overrides) -> GameFunction:
    return _add(db, GameFunction, {
        "code": code, "name": f"Функция {code}",
        "source_url": SOURCE_URL, "source_title": SOURCE_TITLE,
    }, overrides)


def _engine(db, code: str, **overrides) -> Engine:
    return _add(db, Engine, {
        "code": code, "name": f"Движок {code}", "docs_url": SOURCE_URL,
    }, overrides)


def _tool(db, code: str, engine: Engine, **overrides) -> EngineTool:
    return _add(db, EngineTool, {
        "code": code, "name": f"Инструмент {code}",
        "engine_id": engine.id, "docs_url": SOURCE_URL,
    }, overrides)


def _cpu(db, model: str, **overrides) -> HardwareCPU:
    return _add(db, HardwareCPU, {
        "model": model, "vendor": "TestVendor",
        "source_url": SOURCE_URL, "source_title": SOURCE_TITLE,
    }, overrides)


def _gpu(db, model: str, **overrides) -> HardwareGPU:
    return _add(db, HardwareGPU, {
        "model": model, "vendor": "TestVendor",
        "source_url": SOURCE_URL, "source_title": SOURCE_TITLE,
    }, overrides)


def _conflict(db, a_code: str, b_code: str, **overrides) -> Conflict:
    return _add(db, Conflict, {
        "a_code": a_code, "b_code": b_code, "conflict_type": "hard_conflict",
        "severity": 2, "source_url": SOURCE_URL,
    }, overrides)


@pytest.fixture
def catalog_rows(db):
    """По одной черновой записи каждой сущности, готовой к публикации."""
    engine = _engine(db, "tmp_engine")
    tool = _tool(db, "tmp_tool", engine)
    rows = {
        "methods": _method(db, "tmp_method"),
        "game_functions": _function(db, "tmp_function"),
        "engines": engine,
        "engine_tools": tool,
        "method_engine_links": None,  # заполняется ниже: нужны метод и инструмент
        "conflicts": _conflict(db, "tmp_a", "tmp_b"),
        "hardware_cpu": _cpu(db, "Test CPU tmp"),
        "hardware_gpu": _gpu(db, "Test GPU tmp"),
    }
    # Связь метода с инструментом создаётся через API: у неё нет отдельного
    # маршрута с черновиком, и она публикуется вместе с методом.
    rows["method_engine_links"] = None
    return rows


# ---------------------------------------------------------------------------
# Реестр политик
# ---------------------------------------------------------------------------
def test_every_catalog_entity_has_a_policy():
    """Сущность без политики не может пройти жизненный цикл."""
    assert publication.ENTITY_POLICIES, "Реестр политик публикации пуст"

    for code, policy in publication.ENTITY_POLICIES.items():
        assert hasattr(policy.model, "status"), f"У {code} нет статуса"
        assert policy.key_fields, f"У {code} не задан ключ записи"
        assert policy.label, f"У {code} нет названия"


def test_fallback_policy_is_the_strictest():
    """Неописанная сущность не получает послаблений по умолчанию."""
    fallback = publication.policy_of(type("Незнакомая", (), {"__tablename__": "unknown"})())

    assert fallback.requires_source_title is True
    assert fallback.requires_links is False


def test_composite_key_is_readable():
    policy = publication.policy_for("conflicts")
    conflict = Conflict(a_code="a", b_code="b", conflict_type="conflict")

    assert publication.entity_key(conflict, policy) == "a / b / conflict"


# ---------------------------------------------------------------------------
# Общий маршрут смены статуса
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("entity", sorted(publication.ENTITY_POLICIES))
def test_entity_reaches_published_through_the_lifecycle(client, db, catalog_rows, entity):
    """Любая сущность каталога проходит черновик → проверено → опубликовано."""
    if entity == "method_engine_links":
        row_id = _link_id(client, db, catalog_rows["methods"])
    elif entity == "methods":
        # Метод публикуется только со связью: без неё пользователь не узнает,
        # чем реализовать решение в своём движке.
        _link_id(client, db, catalog_rows["methods"], tool_code="tmp_tool")
        row_id = catalog_rows["methods"].id
    else:
        row_id = catalog_rows[entity].id

    listed = client.get(f"/api/admin/entities/{entity}").json()
    assert any(item["id"] == row_id for item in listed), f"{entity} не виден в списке"

    reviewed = client.patch(
        f"/api/admin/entities/{entity}/{row_id}/status", json={"status": "reviewed"}
    )
    assert reviewed.status_code == 200, reviewed.text
    assert reviewed.json()["status"] == "reviewed"

    published = client.patch(
        f"/api/admin/entities/{entity}/{row_id}/status", json={"status": "published"}
    )
    assert published.status_code == 200, published.text
    assert published.json()["status"] == "published"

    log = db.scalar(
        select(PublicationLog).where(
            PublicationLog.entity == entity,
            PublicationLog.to_status == "published",
        )
    )
    assert log is not None, f"Переход {entity} в «опубликовано» не записан в журнал"
    assert log.entity_code


def _link_id(client, db, method: Method, tool_code: str = "tmp_tool") -> int:
    """Связать метод с инструментом движка и вернуть идентификатор связи."""
    tool = db.scalar(select(EngineTool).where(EngineTool.code == tool_code))
    response = client.post("/api/admin/links", json={
        "method_code": method.code, "tool_code": tool.code, "relation_type": "direct",
    })
    assert response.status_code in (200, 201), response.text

    return db.scalar(
        select(MethodEngineLink.id).where(
            MethodEngineLink.method_id == method.id, MethodEngineLink.tool_id == tool.id
        )
    )


def test_direct_publish_from_draft_is_rejected(client, db, catalog_rows):
    """Публикация минует проверку: из черновика можно только в «проверено»."""
    response = client.patch(
        f"/api/admin/entities/engines/{catalog_rows['engines'].id}/status",
        json={"status": "published"},
    )

    assert response.status_code == 409, response.text
    body = response.json()
    assert body["code"] == "conflict"
    assert "запрещён" in body["error"]


def test_unknown_entity_is_rejected(client):
    assert client.get("/api/admin/entities/unknown_table").status_code == 404
    response = client.patch(
        "/api/admin/entities/unknown_table/1/status", json={"status": "reviewed"}
    )
    assert response.status_code == 404


def test_missing_record_is_reported(client):
    response = client.patch(
        "/api/admin/entities/engines/999999/status", json={"status": "reviewed"}
    )
    assert response.status_code == 404


def test_repeated_status_change_is_a_no_op(client, db, catalog_rows):
    row_id = catalog_rows["engines"].id
    first = client.patch(
        f"/api/admin/entities/engines/{row_id}/status", json={"status": "reviewed"}
    )
    assert first.json()["changed"] is True

    second = client.patch(
        f"/api/admin/entities/engines/{row_id}/status", json={"status": "reviewed"}
    )
    assert second.status_code == 200
    assert second.json()["changed"] is False


# ---------------------------------------------------------------------------
# Предметные требования к публикации
# ---------------------------------------------------------------------------
def test_engine_is_published_by_docs_url(client, db):
    """Источником движка служит ссылка на документацию, а не `source_url`."""
    engine = _engine(db, "tmp_engine_no_docs", docs_url="")
    client.patch(f"/api/admin/entities/engines/{engine.id}/status", json={"status": "reviewed"})

    response = client.patch(
        f"/api/admin/entities/engines/{engine.id}/status", json={"status": "published"}
    )

    assert response.status_code == 422, response.text
    details = " ".join(response.json()["details"])
    assert "источник" in details.lower()


def test_method_without_engine_link_is_not_published(client, db):
    """Метод без способа реализации в движке не публикуется."""
    method = _method(db, "tmp_method_unlinked")
    client.patch(f"/api/admin/entities/methods/{method.id}/status", json={"status": "reviewed"})

    response = client.patch(
        f"/api/admin/entities/methods/{method.id}/status", json={"status": "published"}
    )

    assert response.status_code == 422, response.text
    assert any("связ" in item.lower() for item in response.json()["details"]), response.text


def test_hardware_requires_source(client, db):
    cpu = _cpu(db, "Test CPU no source", source_url="", source_title="")
    client.patch(f"/api/admin/entities/hardware_cpu/{cpu.id}/status", json={"status": "reviewed"})

    response = client.patch(
        f"/api/admin/entities/hardware_cpu/{cpu.id}/status", json={"status": "published"}
    )

    assert response.status_code == 422, response.text
    assert len(response.json()["details"]) >= 2  # ссылка и название источника


def test_publication_failure_leaves_status_unchanged(client, db):
    """Неудачная публикация не должна оставлять запись опубликованной."""
    engine = _engine(db, "tmp_engine_bad_url", docs_url="ftp://example.org/docs")
    client.patch(f"/api/admin/entities/engines/{engine.id}/status", json={"status": "reviewed"})
    response = client.patch(
        f"/api/admin/entities/engines/{engine.id}/status", json={"status": "published"}
    )
    assert response.status_code == 422, response.text

    db.refresh(engine)
    assert engine.status == Status.REVIEWED.value


# ---------------------------------------------------------------------------
# Совместимость прежнего маршрута методов
# ---------------------------------------------------------------------------
def test_legacy_method_status_endpoint_still_works(client, db):
    """Прежний маршрут по коду метода сохранён: он используется интерфейсом."""
    method = _method(db, "tmp_legacy_method")
    response = client.patch(
        f"/api/admin/methods/{method.code}/status", json={"status": "reviewed"}
    )

    assert response.status_code == 200, response.text
    assert response.json()["code"] == "tmp_legacy_method"
    assert response.json()["status"] == "reviewed"
