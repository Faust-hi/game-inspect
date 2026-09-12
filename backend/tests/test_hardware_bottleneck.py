"""Подбор железа и узкие места (офлайн).

Дефекты: игнорирование ограничивающего CPU/GPU или памяти,
смешение клиентской и серверной нагрузки, противоречие целевым
условиям (разрешение/FPS/лимиты), ложная точность при нехватке данных.
"""
from __future__ import annotations

import pytest


BASE = {
    "name": "Железо",
    "format": "3D",
    "world_type": "open_world",
    "scale": "large",
    "stage": "prototype",
    "engine": "unreal",
    "platforms": ["pc_windows"],
    "functions": ["open_world_streaming", "crowd_simulation"],
    "target_resolution": "1080p",
    "target_quality": "high",
    "target_fps": 60,
}


def estimate(client, basket=(), **overrides):
    profile = dict(BASE, **overrides)
    response = client.post(
        "/api/hardware-estimate", json={"profile": profile, "basket": list(basket)}
    )
    assert response.status_code == 200, response.text
    return response.json()


@pytest.mark.critical
def test_higher_resolution_needs_stronger_gpu(client):
    """2160p требует больше GPU, чем 720p (цель не противоречит результату)."""
    low = estimate(client, target_resolution="720p")
    high = estimate(client, target_resolution="2160p")
    assert high["required_gpu_index"] > low["required_gpu_index"]


@pytest.mark.critical
def test_higher_fps_needs_more_compute(client):
    """144 FPS дороже 30 FPS по CPU и GPU (ограничение не игнорируется)."""
    low = estimate(client, target_fps=30)
    high = estimate(client, target_fps=144)
    assert high["required_gpu_index"] > low["required_gpu_index"]
    assert high["required_cpu_index"] > low["required_cpu_index"]


@pytest.mark.critical
def test_violated_vram_limit_blocks_and_names_bottleneck(client):
    """Нехватка памяти: предел фиксируется, узкое место — память.

    Дефект: память игнорируется, система советует железо,
    на котором проект не помещается.
    """
    data = estimate(
        client,
        world_type="open_world",
        scale="very_large",
        target_resolution="1440p",
        functions=["open_world_streaming", "dynamic_global_illumination"],
        vram_limit_gb=2.0,
    )
    assert data["unmet_limits"]
    assert data["bottleneck"] == "memory"


@pytest.mark.critical
def test_no_memory_bottleneck_without_deficit(client):
    """Без дефицита память не объявляется узким местом.

    Дефект: величина в ГБ всегда побеждала доли бюджета кадра,
    и память была «узким местом» почти у всех проектов.
    """
    data = estimate(
        client,
        world_type="linear",
        scale="medium",
        functions=["character_animation", "ai_pathfinding"],
        vram_limit_gb=16,
        ram_limit_gb=32,
    )
    assert data["bottleneck"] != "memory"


@pytest.mark.critical
def test_alternatives_cover_estimate(client):
    """Альтернативы не слабее оценки (не советуем заведомо слабое железо)."""
    data = estimate(client)
    for gpu in data["alternative_gpus"]:
        assert gpu["raster_score"] >= data["required_gpu_index"]
        assert gpu["vram_gb"] >= data["estimated_vram_gb"]


@pytest.mark.critical
def test_unknown_inputs_lower_confidence_instead_of_promise(client):
    """Неизвестность — явная неопределённость, а не обещание.

    Дефект: auto/None подменялись измерением, FPS «гарантировался».
    """
    data = estimate(
        client,
        scale="unknown",
        object_count_level="unknown",
        npc_count_level="unknown",
    )
    gaps = " ".join(data["modeling_gaps"])
    assert "масштаб" in gaps or "объект" in gaps or "NPC" in gaps
    assert 0.0 < data["confidence"] < 1.0
    assert data["caveats"]
    assert "guaranteed_fps" not in data and "fps" not in data


@pytest.mark.critical
def test_zero_means_empty_not_missing(client):
    """Явный ноль дешевле неизвестности; шкала монотонна с нуля.

    Дефект: «NPC нет» приравнивалось к «неизвестно». Тогда пустой проект
    получал ту же нагрузку, что и неописанный, а отсутствие данных выглядело
    как измеренная величина.
    """
    zero = estimate(client, npc_count=0)
    unknown = estimate(client, npc_count=None, npc_count_level="unknown")
    one = estimate(client, npc_count=1)
    assert zero["required_cpu_index"] < unknown["required_cpu_index"]
    assert zero["required_cpu_index"] < one["required_cpu_index"]


@pytest.mark.critical
def test_beyond_model_range_is_reported(client):
    """Выход за границу модели виден в ответе, а не выдаётся за измерение."""
    data = estimate(client, npc_count=10_000_000, target_fps=240)
    assert data["applicability_limits"]


@pytest.mark.critical
def test_scene_scale_changes_load_not_frame_cost(client):
    """Масштаб сцены обязан менять расчёт нагрузки, но не стоимость кадра.

    Обязательная проверка спеки: «изменение масштаба сцены меняет расчёт
    нагрузки». Размер мира задаёт стриминг, резидентную память и объём
    контента — то есть RAM/VRAM, draw-call ориентир и класс накопителя.
    Работу на кадр задаёт активная сцена (объекты и NPC), а не площадь мира,
    поэтому CPU/GPU-индексы остаются прежними при том же числе сущностей.
    Раньше один множитель `content` включал и мир, и активную сцену: тогда
    рост масштаба молча удорожал кадр без изменения сцены.
    """
    small = estimate(client, scale="small")
    very_large = estimate(client, scale="very_large")

    # Нагрузка и память монотонно растут вместе с масштабом.
    assert very_large["ram_requirement"]["p50"] > small["ram_requirement"]["p50"]
    assert very_large["vram_requirement"]["p50"] > small["vram_requirement"]["p50"]
    assert very_large["estimated_draw_calls"] > small["estimated_draw_calls"]

    # Класс накопителя отражает рост объёма контента.
    assert very_large["recommended_storage"] != "hdd"
    assert small["recommended_storage"] in {"hdd", "sata_ssd"}

    # Стоимость кадра при неизменной активной сцене не меняется от площади мира.
    assert very_large["required_cpu_index"] == small["required_cpu_index"]
    assert very_large["required_gpu_index"] == small["required_gpu_index"]


@pytest.mark.extended
def test_baseline_api_feature_does_not_empty_gpu_pool(client):
    """«Compute Shaders» — базовая возможность API, а не расширение вендора.

    Каталог не перечисляет её в `hw_features` (как и документация карт), поэтому
    требование не мог подтвердить ни один GPU: пул отсеивался целиком, ориентир
    пропадал, и оценка оборудования обнулялась из-за одного метода в корзине.
    """
    data = estimate(client, basket=["gpu_particle_simulation"])
    assert data["reference_gpu"] is not None
    assert not any("Compute Shaders" in item for item in data["unmet_limits"])


@pytest.mark.extended
def test_feature_support_distinguishes_unknown_from_absent():
    """Возможность подтверждается по API, но неизвестность не становится отказом."""
    from app.services import hardware as hardware_service

    class ModernGPU:
        api_support = ["DirectX 12", "Vulkan 1.2"]
        hw_features: list[str] = []

    class LegacyGPU:
        api_support = ["DirectX 9", "OpenGL 3.3"]
        hw_features: list[str] = []

    # Базовая возможность API подтверждается поддержкой самого API.
    assert hardware_service._gpu_feature_support(ModernGPU(), "Compute Shaders") is True
    # Карта без нужного API заведомо без возможности — это отказ, а не неизвестность.
    assert hardware_service._gpu_feature_support(LegacyGPU(), "Compute Shaders") is False
    # Неизвестная возможность остаётся неизвестной и не превращается в отказ.
    assert hardware_service._gpu_feature_support(ModernGPU(), "Неведомая возможность") is None


@pytest.mark.critical
def test_cpu_ceiling_is_named_when_requirement_exceeds_catalog(client):
    """Требование выше потолка каталога объясняется, а не отдаёт пустой ориентир."""
    data = estimate(
        client,
        basket=["tickrate_budgeting", "network_relevancy_priority"],
        world_type="arena",
        engine="source",
        functions=["multiplayer_netcode"],
        target_quality="low",
        target_fps=240,
        multiplayer=True,
        player_count=10,
    )
    assert data["reference_cpu"] is None
    assert any("Core i9-14900K" in item for item in data["caveats"])
