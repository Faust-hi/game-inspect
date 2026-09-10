"""Сквозной пользовательский сценарий (офлайн, уровень API).

Цепочка: профиль → рекомендации → корзина → нагрузка → железо → план.
Дефект: потеря или искажение данных между шагами (пустые рекомендации
без причин, потеря неизвестных кодов, расхождение корзины и железа,
необъяснённые исключения, неустойчивость повторного расчёта).

Используется временная файловая SQLite из conftest; внешняя сеть
не нужна, рабочая БД не затрагивается.
"""
from __future__ import annotations


def test_recommend_ranked_with_reasons(client, profile):
    """Рекомендации отсортированы внутри функции, с причинами и критериями."""
    data = client.post(
        "/api/recommend", json={"profile": profile, "basket": []}
    ).json()
    assert data["recommendations"]
    for function in {item["function_code"] for item in data["recommendations"]}:
        group = [item for item in data["recommendations"] if item["function_code"] == function]
        assert [item["score"] for item in group] == sorted(
            [item["score"] for item in group], reverse=True
        )
        assert [item["rank"] for item in group] == list(range(1, len(group) + 1))
    first = data["recommendations"][0]
    assert first["reasons"] and first["criteria"]
    assert first["engine_support"] is not None
    assert data["meta"]["algorithm_version"] and data["meta"]["dataset_version"]


def test_unknown_codes_become_risks(client):
    """Неизвестные коды не теряются молча, а становятся рисками."""
    response = client.post("/api/recommend", json={
        "profile": {
            "format": "3D", "world_type": "linear", "scale": "medium",
            "stage": "prototype", "engine": "custom", "platforms": ["pc_windows"],
            "functions": ["function_missing_from_catalog"],
            "target_resolution": "1080p", "target_quality": "high", "target_fps": 60,
        },
        "basket": ["method_missing_from_catalog"],
    })
    assert response.status_code == 200
    codes = {item["code"] for item in response.json()["risks"]}
    assert {"unknown_function", "unknown_method"} <= codes


def test_excluded_explain_reason(client):
    """Исключённое решение остаётся видимым с причиной (не исчезает)."""
    data = client.post("/api/recommend", json={
        "profile": {
            "format": "3D", "world_type": "open_world", "scale": "large",
            "stage": "prototype", "engine": "unreal", "platforms": ["pc_windows"],
            "functions": ["open_world_streaming"], "complexity_tolerance": 1,
        },
        "basket": [],
    }).json()
    assert data["excluded"]
    assert all(item["excluded_reasons"] for item in data["excluded"])


def test_basket_flows_into_load_and_hardware(client, profile):
    """Корзина из рекомендаций пересчитывается в нагрузку и железо без потерь."""
    data = client.post(
        "/api/recommend", json={"profile": profile, "basket": []}
    ).json()
    basket = [item["method_code"] for item in data["recommendations"][:3]]
    assert basket

    loaded = client.post(
        "/api/load-profile", json={"profile": profile, "basket": basket}
    )
    assert loaded.status_code == 200
    body = loaded.json()
    assert set(body["per_resource"]) == {"cpu", "gpu", "ram", "vram", "disk", "network"}
    assert all(0.0 <= body[key] <= 100.0 for key in ("cpu", "gpu", "ram", "vram"))

    estimate = client.post(
        "/api/hardware-estimate", json={"profile": profile, "basket": basket}
    ).json()
    assert estimate["reference_gpu"] and estimate["reference_cpu"]
    assert estimate["caveats"]
    assert 0.0 < estimate["confidence"] < 1.0


def test_same_profile_reproduces_same_result(client, profile):
    """Повторный расчёт того же профиля даёт тот же порядок и баллы."""
    first = client.post(
        "/api/recommend", json={"profile": profile, "basket": []}
    ).json()
    second = client.post(
        "/api/recommend", json={"profile": profile, "basket": []}
    ).json()
    assert [item["method_code"] for item in first["recommendations"]] == [
        item["method_code"] for item in second["recommendations"]
    ]
    assert [item["score"] for item in first["recommendations"]] == [
        item["score"] for item in second["recommendations"]
    ]


def test_baseline_keeps_hardware_and_marks_unknown(client):
    """Зафиксированная корзина не меняет физику расчёта; чужая видна как риск."""
    profile = {
        "engine": "unreal", "stage": "prototype", "format": "3D",
        "functions": ["baked_lighting", "dynamic_global_illumination", "physics_simulation"],
        "world_type": "hub", "scale": "large",
    }
    basket = ["lightmap_atlas_baking"]
    baseline = {"profile": profile, "basket": basket}
    later = client.post("/api/recommend", json={
        "profile": dict(profile, stage="release"),
        "basket": basket, "baseline": baseline,
    })
    assert later.status_code == 200, later.text
    body = later.json()
    transition = next(
        item for item in body["transitions"] if item["method_code"] == basket[0]
    )
    assert transition["status"] == "retained"
    without = client.post("/api/recommend", json={
        "profile": dict(profile, stage="release"), "basket": basket,
    }).json()
    for field in ("required_cpu_index", "required_gpu_index",
                  "estimated_ram_gb", "estimated_vram_gb"):
        assert body["hardware"][field] == without["hardware"][field]

    unknown = client.post("/api/recommend", json={
        "profile": profile, "basket": [],
        "baseline": {"profile": profile, "basket": ["missing"]},
    }).json()
    assert any(risk["code"] == "unknown_baseline" for risk in unknown["risks"])
