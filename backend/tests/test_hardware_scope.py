"""Область применимости аппаратной оценки: платформы, память, частоты.

Регрессии аудита 2026-09-08 (D06, G04/N04, G05):

* количественный прогноз — только Windows/Linux ПК; чисто не-PC цель
  получает явный отказ вместо PC-карты в поле подходящей рекомендации;
* сгенерированные кадры не масштабируют симуляцию: при фиксированном базовом
  рендере изменение отображаемого FPS не меняет CPU-индекс;
* единая память не получает универсальную скидку VRAM — ограничение
  фиксируется явно.
"""
from __future__ import annotations

from app.schemas.catalog import ProjectProfile
from app.services.hardware import _load_indices


def _estimate(client, basket=(), **overrides):
    profile = {
        "name": "Область-оценки",
        "format": "3D",
        "world_type": "linear",
        "scale": "medium",
        "stage": "prototype",
        "engine": "custom",
        "platforms": ["pc_windows"],
        "functions": [],
        "target_resolution": "1080p",
        "target_quality": "high",
        "target_fps": 60,
        "object_count_level": "medium",
        "npc_count_level": "low",
    }
    profile.update(overrides)
    response = client.post(
        "/api/hardware-estimate", json={"profile": profile, "basket": list(basket)}
    )
    assert response.status_code == 200, response.text
    return response.json()


def test_macos_only_has_no_pc_reference(client):
    """Аудит-проба D06: platforms=[macos] не возвращает GeForce RTX 2060."""
    est = _estimate(client, platforms=["macos"])
    assert est["reference_gpu"] is None, est["reference_gpu"]
    assert est["reference_cpu"] is None, est["reference_cpu"]
    assert est["alternative_gpus"] == []
    assert est["alternative_cpus"] == []
    assert est["exceeds_catalog"] is True
    scope = " ".join([*est["unmet_limits"], *est["applicability_limits"], *est["caveats"]])
    assert "только для Windows/Linux ПК" in scope, scope


def test_mixed_platforms_keep_pc_reference_with_warning(client):
    """Смешанная цель сохраняет PC-ориентир, но честно предупреждает."""
    est = _estimate(client, platforms=["pc_windows", "macos"])
    assert est["reference_gpu"] is not None
    scope = " ".join([*est["applicability_limits"], *est["caveats"]])
    assert "только для Windows/Linux ПК" in scope, scope
    assert "только к PC-цели" in scope, scope


def test_pc_only_is_unchanged(client):
    est = _estimate(client, platforms=["pc_windows"])
    assert est["reference_gpu"] is not None
    assert est["reference_cpu"] is not None


def test_unified_memory_has_no_vram_discount():
    """G05: unified не дешевле dedicated при прочих равных + явный gap."""
    base = {"target_resolution": "1080p", "target_quality": "high"}
    dedicated = _load_indices(ProjectProfile(memory_model="dedicated", **base), [])
    unified = _load_indices(ProjectProfile(memory_model="unified", **base), [])
    assert unified["vram_gb"] == dedicated["vram_gb"]
    assert any("unified" in gap for gap in unified["modeling_gaps"]), unified["modeling_gaps"]


def test_displayed_fps_does_not_scale_cpu_with_fixed_base():
    """Аудит-проба G04/N04: FG + base 60, target 60→120 не меняет CPU."""
    kwargs = {
        "frame_generation": True,
        "base_render_fps": 60,
        "physics_tick_hz": 60,
        "functions": ["physics_simulation"],
    }
    low = _load_indices(ProjectProfile(target_fps=60, **kwargs), [])
    high = _load_indices(ProjectProfile(target_fps=120, **kwargs), [])
    assert high["cpu_index"] == low["cpu_index"]
    assert high["gpu_index"] == low["gpu_index"]


def test_target_fps_still_scales_cpu_without_generation():
    """Без генерации целевой FPS по-прежнему влияет на CPU (render thread)."""
    low = _load_indices(ProjectProfile(target_fps=60), [])
    high = _load_indices(ProjectProfile(target_fps=120), [])
    assert high["cpu_index"] > low["cpu_index"]
