"""Область применимости аппаратной оценки: платформы, память, частоты.

Регрессии аудита 2026-09-08 (D06, G04/N04, G05):

* количественный прогноз — только Windows/Linux ПК; чисто не-PC цель
  получает явный отказ вместо PC-карты в поле подходящей рекомендации;
* сгенерированные кадры не масштабируют симуляцию: при фиксированном базовом
  рендере изменение отображаемого FPS не меняет CPU-индекс;
* единая память не получает универсальную скидку VRAM: общие физические
  страницы учитываются один раз, а потребность в системной памяти включает
  GPU-резидентные ресурсы — ограничение фиксируется явно.
"""
from __future__ import annotations

import pytest

from app.schemas.catalog import ProjectProfile
from app.services import hardware
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


def test_nonpc_only_has_no_pc_reference(client):
    """Аудит-проба D06: platforms=[ps5] не возвращает GeForce RTX 2060."""
    est = _estimate(client, platforms=["ps5"])
    assert est["reference_gpu"] is None, est["reference_gpu"]
    assert est["reference_cpu"] is None, est["reference_cpu"]
    assert est["alternative_gpus"] == []
    assert est["alternative_cpus"] == []
    assert est["exceeds_catalog"] is True
    scope = " ".join([*est["unmet_limits"], *est["applicability_limits"], *est["caveats"]])
    assert "только для Windows/Linux ПК" in scope, scope


def test_mixed_platforms_keep_pc_reference_with_warning(client):
    """Смешанная цель сохраняет PC-ориентир, но честно предупреждает."""
    est = _estimate(client, platforms=["pc_windows", "ps5"])
    assert est["reference_gpu"] is not None
    scope = " ".join([*est["applicability_limits"], *est["caveats"]])
    assert "только для Windows/Linux ПК" in scope, scope
    assert "только к PC-цели" in scope, scope


def test_pc_only_is_unchanged(client):
    est = _estimate(client, platforms=["pc_windows"])
    assert est["reference_gpu"] is not None
    assert est["reference_cpu"] is not None


def test_unified_memory_merges_shared_pages_without_discount():
    """G05: единая память не даёт скидки и не считает общие страницы дважды.

    Общий пул физически один: системная память держит и данные CPU, и
    GPU-резидентные ресурсы, поэтому потребность в ней не может быть меньше
    раздельного варианта. Повторный счёт устранён в компонентах — отдельного
    резерва видеопамяти и второго зеркала ресурсов нет.
    """
    base = {"target_resolution": "1080p", "target_quality": "high"}
    dedicated = _load_indices(ProjectProfile(memory_model="dedicated", **base), [])
    unified = _load_indices(ProjectProfile(memory_model="unified", **base), [])
    assert unified["ram_gb"] > dedicated["ram_gb"]
    # Резерв видеопамяти рабочего стола перенесён в общий пул, а не списан.
    assert unified["vram_gb"] == pytest.approx(
        dedicated["vram_gb"] - hardware.OS_VRAM_RESERVE_GB, abs=0.05,
    )
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
    # CPU-нагрузка не меняется: такт физики и рендер привязаны к базовому FPS.
    assert high["cpu_index"] == low["cpu_index"]
    # Стоимость отрисованных кадров не меняется, но генерация добавляет
    # отдельную подсистему.
    for key in ("geometry", "shading", "lighting_shadows", "transparency", "raster"):
        assert high["gpu_subsystem_load"][key] == pytest.approx(
            low["gpu_subsystem_load"][key]
        )
    assert high["gpu_subsystem_load"]["frame_generation"] > 0


def test_target_fps_still_scales_cpu_without_generation():
    """Без генерации целевой FPS по-прежнему влияет на CPU (render thread)."""
    low = _load_indices(ProjectProfile(target_fps=60), [])
    high = _load_indices(ProjectProfile(target_fps=120), [])
    assert high["cpu_index"] > low["cpu_index"]
