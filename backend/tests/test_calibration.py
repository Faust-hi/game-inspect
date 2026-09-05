"""Калибровка соответствия: эталонные проекты обязаны давать правдивые классы.

В отличие от test_profile_influence (там проверяется направление влияния —
«больше разрешение → больше индекс»), здесь фиксируются абсолютные значения:
если данные каталога или формулы тихо уплывут, классы изменятся и тест упадёт,
а не начнёт молча завышать/занижать требования к железу пользователей.
"""
from __future__ import annotations


def _estimate(client, basket=(), **overrides):
    profile = {
        "name": "Калибровочный",
        "format": "3D",
        "world_type": "open_world",
        "scale": "large",
        "stage": "prototype",
        "engine": "unreal",
        "platforms": ["pc_windows"],
        "functions": [],
        "target_resolution": "1080p",
        "target_quality": "high",
        "target_fps": 60,
    }
    profile.update(overrides)
    return client.post(
        "/api/hardware-estimate", json={"profile": profile, "basket": list(basket)}
    ).json()


def test_2d_small_is_entry_class(client):
    """Крошечная 2D-игра не должна требовать больше начального класса."""
    est = _estimate(
        client, format="2D", world_type="linear", scale="small",
        target_resolution="1080p", target_quality="low", target_fps=60,
    )
    assert 0.05 <= est["required_gpu_index"] <= 0.20
    assert est["gpu_class"] <= 2
    assert est["cpu_class"] <= 2
    assert est["exceeds_catalog"] is False


def test_linear_medium_is_mid_class(client):
    """Линейная 3D на baked-свете честно тянется GTX 1660 Super (класс 2).

    Класс 3 здесь был бы завышением требований: индекс ~0.24 не дотягивает
    до карт класса 3, и это правильно — тяжёлых функций в профиле нет.
    """
    est = _estimate(
        client, world_type="linear", scale="medium",
        target_resolution="1080p", target_quality="high", target_fps=60,
        functions=["baked_lighting"],
    )
    assert 0.15 <= est["required_gpu_index"] <= 0.35
    assert est["gpu_class"] == 2
    assert est["exceeds_catalog"] is False


def test_open_world_heavy_is_high_class(client):
    est = _estimate(
        client, world_type="open_world", scale="large",
        target_resolution="1440p", target_quality="high", target_fps=60,
        functions=["open_world_streaming", "dynamic_global_illumination", "crowd_simulation"],
    )
    assert 0.55 <= est["required_gpu_index"] <= 0.90
    assert est["gpu_class"] in (4, 5)
    assert est["exceeds_catalog"] is False


def test_4k_ultra_exceeds_catalog(client):
    """Запредельный профиль обязан честно признавать превышение каталога."""
    est = _estimate(
        client, world_type="open_world", scale="very_large",
        target_resolution="4k", target_quality="ultra", target_fps=60,
        functions=["open_world_streaming", "dynamic_global_illumination",
                   "crowd_simulation", "volumetric_effects"],
    )
    assert est["required_gpu_index"] > 1.0
    assert est["exceeds_catalog"] is True
    assert est["confidence"] < 0.75
    assert est["caveats"]


def test_vram_ram_are_plausible(client):
    """Память для среднего профиля — единицы ГБ, не нули и не сотни."""
    est = _estimate(
        client, world_type="linear", scale="medium",
        target_resolution="1080p", target_quality="high", target_fps=60,
        functions=["baked_lighting"],
    )
    assert 2.0 <= est["estimated_vram_gb"] <= 12.0
    assert 4.0 <= est["estimated_ram_gb"] <= 32.0


def test_catalog_ratios_match_external_benchmarks(db):
    """Относительная мощность карт в каталоге соответствует technical.city.

    Внешний якорь (technical.city, сводный рейтинг и средний FPS):
    RTX 3090 быстрее GTX 1660 Super примерно в 2.1 раза (63.57 против 30.39;
    1440p в среднем 120 против 55 FPS). Каталог даёт 0.70/0.30 = 2.33 —
    в допуске 25%. Если кто-то «поправит» скоры вручную, тест поймает разрыв
    с реальностью, а не только внутреннюю согласованность.
    """
    from sqlalchemy import select

    from app.models.entities import HardwareGPU

    scores = {
        m: db.scalar(
            select(HardwareGPU.raster_score).where(HardwareGPU.model == m)
        )
        for m in ("GeForce GTX 1050 Ti", "GeForce GTX 1660 Super", "GeForce RTX 3090")
    }
    assert all(scores.values())
    ratio_high = scores["GeForce RTX 3090"] / scores["GeForce GTX 1660 Super"]
    assert 1.7 <= ratio_high <= 2.7, ratio_high
    ratio_mid = scores["GeForce GTX 1660 Super"] / scores["GeForce GTX 1050 Ti"]
    assert 1.5 <= ratio_mid <= 3.0, ratio_mid


def test_catalog_vram_matches_specs(db):
    """Объём видеопамяти эталонных карт — по спецификациям (6 и 24 ГБ)."""
    from sqlalchemy import select

    from app.models.entities import HardwareGPU

    for model, expected in (("GeForce GTX 1660 Super", 6.0), ("GeForce RTX 3090", 24.0)):
        vram = db.scalar(select(HardwareGPU.vram_gb).where(HardwareGPU.model == model))
        assert vram == expected, (model, vram)


def test_chosen_basket_converges_to_official_specs(client):
    """С корзиной оценка сходится к официальным требованиям, а не к верхней границе.

    Якоря с technical.city: GTA V Enhanced — RTX 3060 (1080p/high/60),
    Cyberpunk 2077 — RTX 2060 Super (1080p/high/60). Разумная корзина обязана
    опустить класс до 3 или ниже: иначе выбор решений не влияет на железо
    и весь цикл «профиль → корзина → пересчёт» — декорация.
    """
    gta_basket = ["world_partition_streaming", "hierarchical_lod",
                  "gpu_instancing_vegetation", "crowd_instancing_impostors",
                  "animation_lod_budget", "physics_lod_sleeping",
                  "time_sliced_pathfinding", "temporal_upscaling"]
    est = _estimate(
        client, gta_basket, engine="custom",
        object_count_level="high", npc_count_level="high",
        functions=["open_world_streaming", "large_scale_terrain", "crowd_simulation",
                   "ai_pathfinding", "physics_simulation", "character_animation",
                   "particle_systems", "dynamic_shadows", "water_simulation",
                   "post_processing"],
    )
    assert est["required_gpu_index"] < 0.45, est["required_gpu_index"]
    assert est["gpu_class"] <= 3, est["gpu_class"]

    cp_basket = ["world_partition_streaming", "hierarchical_lod",
                 "crowd_instancing_impostors", "animation_lod_budget",
                 "physics_lod_sleeping", "time_sliced_pathfinding",
                 "temporal_upscaling", "particle_pooling"]
    est = _estimate(
        client, cp_basket, engine="custom",
        object_count_level="high", npc_count_level="high",
        functions=["open_world_streaming", "crowd_simulation", "ai_pathfinding",
                   "character_animation", "particle_systems", "dynamic_shadows",
                   "post_processing", "physics_simulation"],
    )
    assert est["required_gpu_index"] < 0.45, est["required_gpu_index"]
    assert est["gpu_class"] <= 3, est["gpu_class"]


def test_memory_limits_are_binding(client):
    """Заданный предел памяти обязан порождать unmet, а не молча игнорироваться."""
    est = _estimate(
        client, world_type="open_world", scale="large",
        target_resolution="1440p", target_quality="high", target_fps=60,
        functions=["open_world_streaming", "dynamic_global_illumination"],
        vram_limit_gb=2.0,
    )
    assert est["unmet_limits"]
