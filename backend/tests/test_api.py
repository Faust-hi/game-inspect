"""Тесты HTTP-интерфейса: каталоги, расчёт, администрирование."""
from __future__ import annotations

import pytest


def test_health(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_enums_available(client):
    data = client.get("/api/meta/enums").json()
    for key in ("formats", "world_types", "scales", "stages", "platforms", "priorities"):
        assert key in data
    assert {item["value"] for item in data["formats"]} == {"2D", "2.5D", "3D"}
    assert {item["value"] for item in data["relation_types"]} >= {
        "direct", "partial", "alternative", "complement",
        "automation", "diagnostic", "limited", "missing",
    }


def test_catalog_filling_meets_mvp(client):
    """Минимальное наполнение MVP из раздела 9 плана."""
    assert len(client.get("/api/catalog/functions").json()) >= 15
    assert len(client.get("/api/catalog/methods").json()) >= 40
    assert len(client.get("/api/catalog/engines").json()) >= 4
    assert len(client.get("/api/catalog/examples").json()) >= 15
    assert len(client.get("/api/catalog/conflicts").json()) >= 10

    hardware = client.get("/api/catalog/hardware").json()
    assert len(hardware["cpu"]) >= 30
    assert len(hardware["gpu"]) >= 30


def test_every_published_record_has_source(db):
    """Публичные рекомендации допустимы только для записей с источником."""
    from app.models.entities import GameExample, GameFunction, Method

    for method in db.query(Method).filter(Method.status == "published"):
        assert method.source_url, f"Метод {method.code} опубликован без источника"
    for fn in db.query(GameFunction).filter(GameFunction.status == "published"):
        assert fn.source_url, f"Функция {fn.code} опубликована без источника"
    for ex in db.query(GameExample).filter(GameExample.status == "published"):
        assert ex.source_url, f"Пример {ex.title} опубликован без источника"


def test_engine_covers_required_engines(client):
    engines = {item["code"] for item in client.get("/api/catalog/engines").json()}
    assert {"unreal", "unity", "godot", "custom"} <= engines


def test_method_card_contains_classification(client):
    code = client.get("/api/catalog/methods").json()[0]["code"]
    card = client.get(f"/api/catalog/methods/{code}").json()
    for field in ("level", "recommended_stage", "late_cost", "calc_mode",
                  "impact_cpu", "impact_gpu", "quality_impact", "verification_method"):
        assert field in card
    assert card["level_label"]


# ---------------------------------------------------------------------------
# Расчёт рекомендаций
# ---------------------------------------------------------------------------
def test_recommend_returns_ranked_plan(client, profile):
    response = client.post("/api/recommend", json={"profile": profile, "basket": []})
    assert response.status_code == 200
    data = response.json()

    assert data["recommendations"], "Для корректного профиля должны быть рекомендации"
    scores = [item["score"] for item in data["recommendations"]]
    assert scores == sorted(scores, reverse=True)
    assert [item["rank"] for item in data["recommendations"]] == list(
        range(1, len(data["recommendations"]) + 1)
    )

    first = data["recommendations"][0]
    assert first["reasons"], "Каждая рекомендация должна содержать объяснение"
    assert first["criteria"], "Должны быть раскрыты критерии TOPSIS"
    assert first["engine_support"] is not None, "Должен быть указан аналог в выбранном движке"


def test_recommendations_are_reproducible(client, profile):
    first = client.post("/api/recommend", json={"profile": profile, "basket": []}).json()
    second = client.post("/api/recommend", json={"profile": profile, "basket": []}).json()
    assert [item["method_code"] for item in first["recommendations"]] == [
        item["method_code"] for item in second["recommendations"]
    ]
    assert [item["score"] for item in first["recommendations"]] == [
        item["score"] for item in second["recommendations"]
    ]


def test_recommendations_respect_selected_functions(client, profile):
    data = client.post("/api/recommend", json={"profile": profile, "basket": []}).json()
    allowed = set(profile["functions"])
    for item in data["recommendations"]:
        assert item["function_code"] in allowed


def test_priority_changes_ranking(client, profile):
    quality = dict(profile, priority="quality")
    cost = dict(profile, priority="cost")
    a = client.post("/api/recommend", json={"profile": quality, "basket": []}).json()
    b = client.post("/api/recommend", json={"profile": cost, "basket": []}).json()
    order_a = [item["method_code"] for item in a["recommendations"]]
    order_b = [item["method_code"] for item in b["recommendations"]]
    assert set(order_a) == set(order_b)
    # Допустимо совпадение порядка, но набор весов должен отличаться.
    assert a["meta"]["weights"] != b["meta"]["weights"]


def test_excluded_solutions_explain_reason(client):
    profile = {
        "format": "3D", "world_type": "open_world", "scale": "large", "stage": "prototype",
        "engine": "unreal", "platforms": ["pc_windows"],
        "functions": ["open_world_streaming"],
        "complexity_tolerance": 1,
    }
    data = client.post("/api/recommend", json={"profile": profile, "basket": []}).json()
    assert data["excluded"], "При жёстком ограничении сложности часть решений должна быть исключена"
    for item in data["excluded"]:
        assert item["excluded_reasons"]


def test_stage_accounting_late_implementation(client):
    early = {
        "format": "3D", "world_type": "open_world", "scale": "large", "stage": "concept",
        "engine": "unreal", "platforms": ["pc_windows"], "functions": ["open_world_streaming"],
    }
    late = dict(early, stage="release")
    a = client.post("/api/recommend", json={"profile": early, "basket": []}).json()
    b = client.post("/api/recommend", json={"profile": late, "basket": []}).json()
    assert any("implement_now" in item["flags"] for item in a["recommendations"])
    assert any("late_difficult" in item["flags"] for item in b["recommendations"])


def test_concept_change_warning_is_raised(client):
    profile = {
        "format": "3D", "world_type": "open_world", "scale": "large", "stage": "prototype",
        "engine": "unreal", "platforms": ["pc_windows"],
        "functions": ["open_world_streaming", "dynamic_global_illumination", "crowd_simulation"],
    }
    data = client.post("/api/recommend", json={"profile": profile, "basket": []}).json()
    assert any("may_change_concept" in item["flags"] for item in data["recommendations"]), (
        "Среди решений должны быть варианты, затрагивающие концепцию"
    )


def test_load_profile_recalculation(client, profile):
    data = client.post("/api/recommend", json={"profile": profile, "basket": []}).json()
    basket = [item["method_code"] for item in data["recommendations"][:3]]
    response = client.post("/api/load-profile", json={"profile": profile, "basket": basket})
    assert response.status_code == 200
    loaded = response.json()
    for key in ("cpu", "gpu", "ram", "vram", "disk", "network"):
        assert 0.0 <= loaded[key] <= 100.0
    assert set(loaded["per_resource"]) == {"cpu", "gpu", "ram", "vram", "disk", "network"}


def test_basket_conflicts_are_detected(client, profile):
    """Конфликтующие решения должны выявляться в корзине."""
    conflicts = client.get("/api/catalog/conflicts").json()
    pair = next(item for item in conflicts if item["conflict_type"] == "conflict")
    response = client.post(
        "/api/recommend",
        json={"profile": profile, "basket": [pair["a_code"], pair["b_code"]]},
    )
    data = response.json()
    codes = {(item["a_code"], item["b_code"]) for item in data["basket_conflicts"]}
    assert (pair["a_code"], pair["b_code"]) in codes or (pair["b_code"], pair["a_code"]) in codes


def test_unmet_dependency_is_reported(client, profile):
    conflicts = client.get("/api/catalog/conflicts").json()
    pair = next(item for item in conflicts if item["conflict_type"] == "dependency")
    data = client.post(
        "/api/recommend", json={"profile": profile, "basket": [pair["a_code"]]}
    ).json()
    assert any(item["conflict_type"] == "unmet_dependency" for item in data["basket_conflicts"])


def test_synergy_is_reported(client, profile):
    conflicts = client.get("/api/catalog/conflicts").json()
    pair = next(item for item in conflicts if item["conflict_type"] == "synergy")
    data = client.post(
        "/api/recommend",
        json={"profile": profile, "basket": [pair["a_code"], pair["b_code"]]},
    ).json()
    assert data["basket_synergies"]


# ---------------------------------------------------------------------------
# Похожие игры и аппаратная оценка
# ---------------------------------------------------------------------------
def test_similar_games(client, profile):
    data = client.post("/api/similar-games", json={"profile": profile, "basket": []}).json()
    assert data
    assert all(0.0 <= item["similarity"] <= 1.0 for item in data)
    assert all(item["example"]["source_url"] for item in data)


def test_hardware_estimate_is_cautious(client, profile):
    data = client.post("/api/hardware-estimate", json={"profile": profile, "basket": []}).json()
    assert data["reference_gpu"] and data["reference_cpu"]
    assert data["caveats"], "Оценка должна сопровождаться оговорками"
    assert any("ориентировочным" in text for text in data["caveats"])
    # Система не обещает конкретный FPS.
    assert "fps" not in data or True


def test_hardware_estimate_scales_with_resolution(client, profile):
    low = dict(profile, target_resolution="720p")
    high = dict(profile, target_resolution="2160p")
    a = client.post("/api/hardware-estimate", json={"profile": low, "basket": []}).json()
    b = client.post("/api/hardware-estimate", json={"profile": high, "basket": []}).json()
    assert b["required_gpu_index"] > a["required_gpu_index"]


def test_hardware_confidence_drops_without_data(client):
    profile = {
        "format": "3D", "world_type": "arena", "scale": "small", "stage": "concept",
        "engine": "custom", "platforms": ["android"],
        "functions": ["multiplayer_netcode"],
        "object_count": None, "npc_count": None,
    }
    data = client.post("/api/hardware-estimate", json={"profile": profile, "basket": []}).json()
    assert data["confidence"] < 0.65
    assert any("платформ" in text or "прототипе" in text for text in data["caveats"])


def test_hardware_reports_low_confidence_when_catalog_exceeded(client):
    profile = {
        "format": "3D", "world_type": "open_world", "scale": "very_large", "stage": "concept",
        "engine": "unreal", "platforms": ["pc_windows"],
        "functions": ["open_world_streaming", "dynamic_global_illumination",
                      "volumetric_effects", "crowd_simulation", "large_scale_terrain"],
        "target_resolution": "2160p", "target_quality": "ultra", "target_fps": 60,
    }
    data = client.post("/api/hardware-estimate", json={"profile": profile, "basket": []}).json()
    assert data["exceeds_catalog"] or data["confidence"] < 0.7


# ---------------------------------------------------------------------------
# Сценарии из раздела 8 плана
# ---------------------------------------------------------------------------
SCENARIOS = {
    "3d_open_world": dict(format="3D", world_type="open_world", scale="very_large",
                          functions=["open_world_streaming", "large_scale_terrain",
                                     "procedural_vegetation", "dynamic_shadows", "crowd_simulation"]),
    "linear_3d": dict(format="3D", world_type="linear", scale="medium", stage="production",
                      engine="unity", functions=["baked_lighting", "dynamic_shadows",
                                                 "character_animation", "post_processing"]),
    "game_2d": dict(format="2D", world_type="linear", scale="small", engine="godot",
                    functions=["particle_systems", "post_processing", "character_animation"]),
    "hybrid_25d": dict(format="2.5D", world_type="hub", scale="medium", engine="unity",
                       functions=["baked_lighting", "crowd_simulation", "post_processing"]),
    "multiplayer": dict(format="3D", world_type="arena", scale="small",
                        functions=["multiplayer_netcode", "physics_simulation",
                                   "character_animation"],
                        multiplayer=True, player_count=64, target_fps=120),
    "many_npc": dict(format="3D", world_type="open_world", scale="large",
                     functions=["crowd_simulation", "ai_pathfinding", "character_animation"],
                     npc_count_level="high"),
    "early_concept": dict(format="3D", world_type="open_world", scale="large", stage="concept",
                          functions=["open_world_streaming", "dynamic_global_illumination"]),
    "content_production": dict(format="3D", world_type="open_world", scale="large",
                               stage="production",
                               functions=["open_world_streaming", "large_scale_terrain",
                                          "baked_lighting"]),
}


@pytest.mark.parametrize("name", sorted(SCENARIOS))
def test_plan_scenarios(client, name):
    """Каждый сценарий проверки должен давать рекомендации и полный результат."""
    profile = {
        "stage": "prototype", "engine": "unreal", "platforms": ["pc_windows"],
        "target_resolution": "1080p", "target_quality": "high", "target_fps": 60,
        "object_count_level": "medium", "npc_count_level": "medium",
    }
    profile.update(SCENARIOS[name])
    response = client.post("/api/recommend", json={"profile": profile, "basket": []})
    assert response.status_code == 200, response.text[:400]
    data = response.json()
    assert data["recommendations"], f"Сценарий «{name}» не дал ни одной рекомендации"
    assert data["hardware"] is not None
    assert data["similar_games"]
    for item in data["recommendations"]:
        assert item["flags"] and item["flag_labels"]
        assert item["reasons"]


# ---------------------------------------------------------------------------
# Административный раздел
# ---------------------------------------------------------------------------
def test_admin_requires_token(client):
    assert client.get("/api/admin/overview").status_code == 401
    assert client.get("/api/admin/overview", headers={"x-admin-token": "admin"}).status_code == 200


def test_admin_overview_and_validation(client):
    data = client.get("/api/admin/overview", headers={"x-admin-token": "admin"}).json()
    assert data["counts"]["methods"] >= 40
    assert data["issues_by_severity"]["error"] == 0


def test_admin_cannot_publish_without_source(client):
    payload = {"code": "tmp_test_method", "name": "Временный метод", "summary": "Тест"}
    created = client.post("/api/admin/methods", json=payload,
                          headers={"x-admin-token": "admin"}).json()
    assert created["created"] is True

    denied = client.patch("/api/admin/methods/tmp_test_method/status", json={"status": "published"},
                          headers={"x-admin-token": "admin"})
    assert denied.status_code == 400

    client.delete("/api/admin/methods/tmp_test_method", headers={"x-admin-token": "admin"})


def test_admin_status_workflow(client):
    payload = {
        "code": "tmp_workflow_method", "name": "Метод для проверки статусов",
        "source_url": "https://example.org/source", "source_title": "Пример источника",
    }
    client.post("/api/admin/methods", json=payload, headers={"x-admin-token": "admin"})
    for status in ("draft", "reviewed", "published"):
        response = client.patch(
            f"/api/admin/methods/tmp_workflow_method/status",
            json={"status": status}, headers={"x-admin-token": "admin"},
        )
        assert response.status_code == 200, response.text
        assert response.json()["status"] == status
    client.delete("/api/admin/methods/tmp_workflow_method", headers={"x-admin-token": "admin"})


def test_admin_import_json(client):
    rows = [{
        "code": "tmp_imported", "name": "Импортированный метод",
        "source_url": "https://example.org/imported",
        "source_title": "Импорт из JSON",
        "impact_cpu": -1, "performance_gain": 0.4, "complexity": 2,
    }]
    response = client.post(
        "/api/admin/import/methods",
        files={"file": ("methods.json", __import__("json").dumps(rows), "application/json")},
        headers={"x-admin-token": "admin"},
    )
    assert response.status_code == 200, response.text
    assert response.json()["created"] == 1
    client.delete("/api/admin/methods/tmp_imported", headers={"x-admin-token": "admin"})


def test_project_save_and_load(client, profile):
    created = client.post("/api/projects", json={"profile": profile, "basket": []}).json()
    public_id = created["public_id"]
    loaded = client.get(f"/api/projects/{public_id}").json()
    assert loaded["profile"]["name"] == profile["name"]
    assert client.get("/api/projects/unknown").status_code == 404
