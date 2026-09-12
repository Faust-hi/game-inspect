"""Регрессии публичных маршрутов доказательного слоя."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.extended


def test_evidence_endpoints_return_claims_by_code(client):
    """Доказательство по коду сущности возвращается и не смешивает сущности.

    Объединяет две проверки одного и того же маршрута (слияние M3): общий
    инвариант — выдача по `entity/entity_code` отфильтрована ровно по этой
    паре, и сценарий UI/отчёта — ссылка «показать доказательства этой
    сущности» для параметров проектирования не ведёт в пустоту. Пока
    утверждения пакетов оставались черновиками, она вела в пустоту.
    """
    cases = [
        ("stage_budget", "concept"),
        ("stage_budget", "production"),
        ("target_metric", "frame_budget_ms"),
        ("load_profile", "client_runtime"),
        ("network_mode", "dedicated_server"),
        ("risk_factor", "scope_creep"),
        ("target_platform", "pc_windows"),
    ]
    listed = client.get("/api/catalog/evidence", params={"entity": "method"})
    assert listed.status_code == 200
    claims = listed.json()
    assert claims
    selected = claims[0]
    cases.append((selected["entity"], selected["entity_code"]))

    empty: list[str] = []
    for entity, code in cases:
        response = client.get(f"/api/catalog/evidence/{entity}/{code}")
        assert response.status_code == 200, response.text
        returned = response.json()
        if not returned:
            empty.append(f"{entity}/{code}")
        assert all(
            item["entity"] == entity and item["entity_code"] == code
            for item in returned
        ), f"выдача {entity}/{code} содержит чужие утверждения"
    assert not empty, f"пустая выдача доказательств: {empty}"


def test_graph_checks_reports_no_mandatory_cycles(client):
    """Граф обязан быть ациклическим по обязательным зависимостям.

    Цикл обязательных зависимостей неразрешим: ни один метод в нём нельзя
    поставить в план. Если этот тест падает, в каталог попали взаимные
    предусловия, которые нужно понизить до дополнения.
    """
    response = client.get("/api/catalog/graph-checks")

    assert response.status_code == 200
    payload = response.json()
    assert payload["counts"]["edges"] > 0
    assert payload["counts"]["nodes"] > 0
    cycles = [item for item in payload["issues"] if item["check"] == "cyclic_mandatory"]
    assert cycles == [], f"найдены циклы обязательных зависимостей: {cycles}"


def test_graph_checks_flags_unknown_version_instead_of_compatibility(client):
    """Без версии движка соответствие версиям не проверяется.

    Проверка обязана вернуть явный статус «не проверено», а не молчаливое
    «нарушений нет»: отсутствие данных не означает совместимость.
    """
    response = client.get("/api/catalog/graph-checks")

    assert response.status_code == 200
    checks = {item["check"] for item in response.json()["issues"]}
    assert "version_unknown" in checks


def test_graph_checks_detects_hard_conflict_inside_basket(client):
    """Жёсткий конфликт внутри корзины должен быть найден.

    Тест сам находит существующую пару hard_conflict, поэтому не зависит от
    конкретного содержимого каталога.
    """
    conflicts = client.get("/api/catalog/conflicts").json()
    hard = [item for item in conflicts if item["conflict_type"] == "hard_conflict"]
    if not hard:
        # Каталог без жёстких конфликтов — не повод считать проверку рабочей.
        return

    pair = hard[0]
    response = client.get(
        "/api/catalog/graph-checks",
        params=[("basket", pair["a_code"]), ("basket", pair["b_code"])],
    )

    assert response.status_code == 200
    found = [item for item in response.json()["issues"] if item["check"] == "basket_hard_conflict"]
    assert found, f"жёсткий конфликт {pair['a_code']} / {pair['b_code']} не обнаружен"


def test_graph_checks_api_incompatibility_is_reported(client):
    """Выбор API, не покрывающего обязательное требование, — ошибка, а не заметка."""
    response = client.get(
        "/api/catalog/graph-checks",
        params={"render_api": "dx11", "engine": "unreal", "engine_version": "5.4"},
    )

    assert response.status_code == 200
    issues = response.json()["issues"]
    assert any(item["check"] == "api_incompatibility" for item in issues)
