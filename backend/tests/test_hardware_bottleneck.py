"""Подбор железа и узкие места (офлайн).

Дефекты: игнорирование ограничивающего CPU/GPU или памяти,
смешение клиентской и серверной нагрузки, противоречие целевым
условиям (разрешение/FPS/лимиты), ложная точность при нехватке данных.
"""
from __future__ import annotations


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


def test_higher_resolution_needs_stronger_gpu(client):
    """2160p требует больше GPU, чем 720p (цель не противоречит результату)."""
    low = estimate(client, target_resolution="720p")
    high = estimate(client, target_resolution="2160p")
    assert high["required_gpu_index"] > low["required_gpu_index"]


def test_higher_fps_needs_more_compute(client):
    """144 FPS дороже 30 FPS по CPU и GPU (ограничение не игнорируется)."""
    low = estimate(client, target_fps=30)
    high = estimate(client, target_fps=144)
    assert high["required_gpu_index"] > low["required_gpu_index"]
    assert high["required_cpu_index"] > low["required_cpu_index"]


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


def test_alternatives_cover_estimate(client):
    """Альтернативы не слабее оценки (не советуем заведомо слабое железо)."""
    data = estimate(client)
    for gpu in data["alternative_gpus"]:
        assert gpu["raster_score"] >= data["required_gpu_index"]
        assert gpu["vram_gb"] >= data["estimated_vram_gb"]


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


def test_zero_means_empty_not_missing(client):
    """Явный ноль дешевле неизвестности; шкала монотонна с нуля."""
    from app.schemas.catalog import ProjectProfile
    from app.services.hardware import _load_indices

    zero = _load_indices(ProjectProfile(npc_count=0), [])["cpu_index"]
    unknown = _load_indices(
        ProjectProfile(npc_count=None, npc_count_level="unknown"), []
    )["cpu_index"]
    assert zero < unknown
    one = _load_indices(ProjectProfile(npc_count=1), [])["cpu_index"]
    assert zero < one


def test_beyond_model_range_is_reported(client):
    """Выход за границу модели виден в ответе, а не выдаётся за измерение."""
    data = estimate(client, npc_count=10_000_000, target_fps=240)
    assert data["applicability_limits"]
