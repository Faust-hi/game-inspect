"""Контекст игры и этап разработки (офлайн).

Дефекты: игнорирование значимого профиля проекта, неподходящий
совет для текущего этапа, отсутствие предупреждения о переработке.
"""
from __future__ import annotations


BASE = {
    "name": "Контекст",
    "format": "3D",
    "world_type": "open_world",
    "scale": "large",
    "stage": "prototype",
    "engine": "unreal",
    "platforms": ["pc_windows"],
    "functions": ["open_world_streaming", "crowd_simulation"],
    "target_resolution": "1440p",
    "target_quality": "high",
    "target_fps": 60,
    "npc_count_level": "high",
}


def recommend(client, basket=(), **overrides):
    profile = dict(BASE, **overrides)
    response = client.post(
        "/api/recommend", json={"profile": profile, "basket": list(basket)}
    )
    assert response.status_code == 200, response.text
    return response.json()


def test_object_count_moves_result(client):
    """Поле анкеты меняет ответ, а не лежит декорацией."""
    small = client.post("/api/hardware-estimate", json={
        "profile": dict(BASE, object_count=100), "basket": [],
    }).json()
    large = client.post("/api/hardware-estimate", json={
        "profile": dict(BASE, object_count=1_000_000), "basket": [],
    }).json()
    assert large["required_gpu_index"] > small["required_gpu_index"]
    assert large["estimated_ram_gb"] > small["estimated_ram_gb"]


def test_stage_keeps_architecture_with_rework_mark(client):
    """Стадия — цена внедрения, а не удаление: архитектура остаётся с пометкой.

    Дефект: на релизе архитектурное решение исчезало из рекомендаций,
    продолжая учитываться в корзине и железе (противоречивый расчёт).
    """
    early = recommend(client, stage="concept")
    late = recommend(client, stage="release")
    assert late["stage_guidance"]["rework_levels"] == ["architecture"]
    assert early["stage_guidance"]["rework_levels"] == []

    methods = client.get("/api/catalog/methods").json()
    architecture = {
        item["code"] for item in methods if item.get("level") == "architecture"
    } & {item["method_code"] for item in early["recommendations"]}
    assert architecture, "в выдаче концепта нет архитектурных решений"
    assert architecture <= {item["method_code"] for item in late["recommendations"]}
    flagged = {
        item["method_code"] for item in late["recommendations"]
        if "needs_rework" in item.get("flags", [])
    }
    assert flagged & architecture


def test_stage_guidance_differs_and_unknown_falls_back(client):
    """У ранней и поздней стадий своё содержание; неизвестная — прототип без 500."""
    concept = client.get(
        "/api/catalog/stage-guidance", params={"stage": "concept"}
    ).json()
    release = client.get(
        "/api/catalog/stage-guidance", params={"stage": "release"}
    ).json()
    for guide in (concept, release):
        assert guide["summary"] and guide["warnings"] and guide["suggestions"]
    assert concept["summary"] != release["summary"]
    assert concept["rework_levels"] == []
    assert "architecture" in release["rework_levels"]

    unknown = client.get(
        "/api/catalog/stage-guidance", params={"stage": "нет_такой_стадии"}
    )
    assert unknown.status_code == 200
    assert unknown.json()["stage"] == "prototype"


def test_concept_change_is_flagged(client):
    """Решение, меняющее замысел, помечено, а не подано как нейтральное."""
    data = recommend(client)
    item = next(
        (row for row in data["recommendations"]
         if row["method_code"] == "art_direction_stylization"),
        None,
    )
    assert item is not None
    assert "may_change_concept" in item["flags"]


def test_gated_network_method_needs_its_function(client):
    """Сетевой метод виден только с сетевой функцией, иначе — в исключённых с причиной."""
    without = recommend(client, functions=["open_world_streaming"])
    assert "tickrate_budgeting" not in {
        item["method_code"] for item in without["recommendations"]
    }
    excluded = {item["method_code"]: item for item in without["excluded"]}
    assert "tickrate_budgeting" in excluded
    assert excluded["tickrate_budgeting"]["excluded_reasons"]

    online = recommend(
        client,
        functions=["open_world_streaming", "multiplayer_netcode"],
        multiplayer=True,
        player_count=32,
    )
    assert "tickrate_budgeting" in {
        item["method_code"] for item in online["recommendations"]
    }
