"""Научная корректность (офлайн).

Дефекты: ошибка метрики, улучшение результата за счёт пропущенных
предсказаний, пересечение обучающих и проверочных данных, выдача
условной оценки за доказанную точность.

Арифметика внешней сверки живёт в validation/test_evaluate.py
(не импортируется рантаймом); здесь — честность продукта:
условное не выдаётся за доказанное, пустое покрытие — результат,
а не успех, черновики не смешиваются с опубликованным срезом.
"""
from __future__ import annotations


def test_practice_check_is_development_not_proof(client, profile):
    """Сверка с практикой — «в разработке», а не заявленная точность."""
    data = client.post(
        "/api/recommend", json={"profile": profile, "basket": []}
    ).json()
    assert data["practice_check"]["status"] == "in_development"
    assert data["practice_check"]["title"] and data["practice_check"]["message"]


def test_estimate_marks_uncertainty_and_gaps(client, profile):
    """Оборудование: уверенность ниже единицы, оговорки и пробелы названы."""
    data = client.post(
        "/api/hardware-estimate", json={"profile": profile, "basket": []}
    ).json()
    assert 0.0 < data["confidence"] < 1.0
    assert data["caveats"]
    assert data["confidence_label"] in {"низкая", "средняя", "повышенная"}


def test_beyond_catalog_is_flagged_not_hidden(client):
    """Запредельный профиль признаёт превышение каталога или низкую уверенность."""
    data = client.post("/api/hardware-estimate", json={
        "profile": {
            "format": "3D", "world_type": "open_world", "scale": "very_large",
            "stage": "concept", "engine": "unreal", "platforms": ["pc_windows"],
            "functions": ["open_world_streaming", "dynamic_global_illumination",
                          "volumetric_effects", "crowd_simulation",
                          "large_scale_terrain"],
            "target_resolution": "2160p", "target_quality": "ultra",
            "target_fps": 60,
        },
        "basket": [],
    }).json()
    assert data["exceeds_catalog"] or data["confidence"] < 0.7


def test_missing_prediction_does_not_become_success(client):
    """Пропуск не улучшает результат: неизвестное — риск, а не покрытие."""
    response = client.post("/api/recommend", json={
        "profile": {
            "format": "3D", "world_type": "linear", "scale": "medium",
            "stage": "prototype", "engine": "custom", "platforms": ["pc_windows"],
            "functions": ["function_missing_from_catalog"],
            "target_resolution": "1080p", "target_quality": "high",
            "target_fps": 60,
        },
        "basket": [],
    })
    assert response.status_code == 200
    assert "unknown_function" in {
        item["code"] for item in response.json()["risks"]
    }


def test_catalog_ratio_matches_external_anchor(db):
    """Относительная мощность карт сверена с внешним якорем (не только с собой).

    technical.city: RTX 3090 быстрее GTX 1660 Super примерно в 2.1 раза.
    Допуск 25%: ручная «правка» скоров ловится разрывом с реальностью.
    """
    from sqlalchemy import select

    from app.models.entities import HardwareGPU

    scores = {
        model: db.scalar(
            select(HardwareGPU.raster_score).where(HardwareGPU.model == model)
        )
        for model in (
            "GeForce GTX 1660 Super",
            "GeForce RTX 3090",
        )
    }
    assert all(scores.values())
    ratio = scores["GeForce RTX 3090"] / scores["GeForce GTX 1660 Super"]
    assert 1.7 <= ratio <= 2.7, ratio


def test_chosen_basket_moves_hardware_class(client):
    """Разумная корзина опускает класс (цикл «корзина → пересчёт» не декорация)."""
    profile = {
        "name": "Калибровочный",
        "format": "3D",
        "world_type": "open_world",
        "scale": "large",
        "stage": "prototype",
        "engine": "custom",
        "platforms": ["pc_windows"],
        "functions": ["open_world_streaming", "large_scale_terrain",
                      "crowd_simulation", "ai_pathfinding",
                      "physics_simulation", "character_animation",
                      "particle_systems", "dynamic_shadows",
                      "water_simulation", "post_processing"],
        "target_resolution": "1080p",
        "target_quality": "high",
        "target_fps": 60,
        "object_count_level": "high",
        "npc_count_level": "high",
    }
    basket = ["world_partition_streaming", "hierarchical_lod",
              "gpu_instancing_vegetation", "crowd_instancing_impostors",
              "animation_lod_budget", "physics_lod_sleeping",
              "time_sliced_pathfinding", "temporal_upscaling"]
    data = client.post(
        "/api/hardware-estimate", json={"profile": profile, "basket": basket}
    ).json()
    assert data["required_gpu_index"] < 0.45, data["required_gpu_index"]
    assert data["gpu_class"] == 3, data["gpu_class"]
