"""Совместное действие методов (офлайн).

Дефекты: двойной учёт одного эффекта, наивное сложение улучшений,
применение эффекта вне его области (сервер/разработка удешевляют ПК
игрока, не-клиентская скидка, out-of-frame молча).
"""
from __future__ import annotations

import pytest

BASE = {
    "name": "Совместный учёт",
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


def recommend(client, basket=(), **overrides):
    profile = dict(BASE, **overrides)
    response = client.post(
        "/api/recommend", json={"profile": profile, "basket": list(basket)}
    )
    assert response.status_code == 200, response.text
    return response.json()


def test_streaming_pool_counts_only_transient_part(client):
    """Пул 8 ГБ не даёт +8 RAM / +4 VRAM поверх текстур (двойной учёт объёма)."""
    base = estimate(client)
    with_pool = estimate(client, streaming_pool_gb=8)
    delta_ram = with_pool["estimated_ram_gb"] - base["estimated_ram_gb"]
    delta_vram = with_pool["estimated_vram_gb"] - base["estimated_vram_gb"]
    assert 0.3 <= delta_ram <= 0.8
    assert 0.0 < delta_vram <= 0.3


def test_upscaling_field_and_card_act_once(client):
    """Поле и карточка апскейлинга — одно действие, а не две скидки."""
    field_only = estimate(client, upscaling_method="fsr")
    both = estimate(client, upscaling_method="fsr", basket=["temporal_upscaling"])
    assert both["gpu_raster_cost"] == pytest.approx(field_only["gpu_raster_cost"])
    assert both["estimated_vram_gb"] > field_only["estimated_vram_gb"]


def test_frame_generation_field_and_card_act_once(client):
    """Поле и карточка генерации кадров — одна стоимость синтеза."""
    overrides = {"frame_generation": True, "base_render_fps": 60, "target_fps": 120}
    field_only = estimate(client, **overrides)
    both = estimate(client, basket=["ml_frame_generation"], **overrides)
    assert both["gpu_raster_cost"] == pytest.approx(field_only["gpu_raster_cost"])
    assert both["estimated_vram_gb"] > field_only["estimated_vram_gb"]


def test_rt_cost_scales_with_resolution(client):
    """RT-проход дорожает с разрешением (1080p → 4K более чем вдвое)."""
    basket = ["hardware_raytraced_gi"]
    low = estimate(client, basket=basket, target_resolution="1080p")
    high = estimate(client, basket=basket, target_resolution="2160p")
    assert low["gpu_rt_cost"] > 0
    assert high["gpu_rt_cost"] > low["gpu_rt_cost"] * 2.0


def test_rt_budget_reduces_introduced_pass(client):
    """Бюджет трассировки сокращает введённый проход, а не теряется."""
    functions = BASE["functions"] + ["ray_traced_effects"]
    plain = estimate(client, basket=["hardware_raytraced_gi"], functions=functions)
    budgeted = estimate(
        client,
        basket=["hardware_raytraced_gi", "rt_effect_resolution_budget"],
        functions=functions,
    )
    assert plain["gpu_rt_cost"] > 0
    assert budgeted["gpu_rt_cost"] < plain["gpu_rt_cost"]


def test_raster_and_rt_share_one_frame_budget(client):
    """Требование к GPU — сумма проходов, а не более тяжёлая часть."""
    functions = BASE["functions"] + ["ray_traced_effects"]
    result = estimate(client, basket=["hardware_raytraced_gi"], functions=functions)
    budget_ms = 1000.0 / BASE["target_fps"]
    assert result["required_gpu_index"] == pytest.approx(
        (result["gpu_raster_cost"] + result["gpu_rt_cost"]) / budget_ms, abs=0.02
    )


def test_two_increments_sum_but_two_savings_count_once(client):
    """Два расхода складываются; две экономии одного объёма — по максимуму."""
    vsm = estimate(client, basket=["virtual_shadow_maps"])
    caching = estimate(client, basket=["static_shadow_caching"])
    both_up = estimate(
        client, basket=["virtual_shadow_maps", "static_shadow_caching"]
    )
    assert both_up["estimated_vram_gb"] > vsm["estimated_vram_gb"]
    assert both_up["estimated_vram_gb"] > caching["estimated_vram_gb"]

    functions = BASE["functions"] + ["large_scale_terrain"]
    base = estimate(client, functions=functions)["estimated_vram_gb"]
    first = estimate(client, basket=["heightmap_compression"], functions=functions)
    second = estimate(client, basket=["neural_texture_compression"], functions=functions)
    both_down = estimate(
        client,
        basket=["heightmap_compression", "neural_texture_compression"],
        functions=functions,
    )
    saving = lambda result: base - result["estimated_vram_gb"]
    assert saving(first) > 0 and saving(second) > 0
    assert saving(both_down) == pytest.approx(
        max(saving(first), saving(second)), abs=0.2
    )
    assert saving(both_down) < saving(first) + saving(second)


def test_server_effect_does_not_discount_player_pc(client):
    """Сервер без графики не облегчает рендер у игрока (область эффекта)."""
    base = estimate(
        client, functions=["multiplayer_netcode"], multiplayer=True,
    )
    selected = estimate(
        client,
        basket=["headless_dedicated_server"],
        functions=["multiplayer_netcode"],
        multiplayer=True,
    )
    assert selected["required_gpu_index"] == base["required_gpu_index"]
    assert selected["required_cpu_index"] == base["required_cpu_index"]


def test_out_of_frame_effect_is_named_not_silent(client):
    """Эффект вне стоимости кадра назван в exclusions, а не пропущен молча."""
    notes = recommend(client, basket=["pso_precaching_warmup"])["contributions"][
        "exclusions"
    ]
    assert any("кадра" in note for note in notes)
