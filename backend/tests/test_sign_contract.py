"""Единый знаковый контракт двух каналов влияния решений (R4) и порог сборки (R16).

Знаковый контракт. Каналов три, и соглашения у них разные:
* `METHOD_SUBSYSTEM_EFFECTS` cpu/gpu (`hardware.py`): плюс = **снижает** нагрузку;
* `METHOD_SUBSYSTEM_EFFECTS` mem: плюс = **увеличивает** объём;
* `methods.impact_*` (`models/entities.py:114`): плюс = **увеличивает** нагрузку.

Тест приводит оба канала к одной оси («нагрузка») и требует совпадения знака.
Известные расхождения перечислены явно: список — это долг, а не разрешение.
Новое расхождение уронит тест; исправление старого — тоже, и это заставит
осознанно сократить список, а не потерять запись молча.
"""
from __future__ import annotations

import pytest

from app.services.hardware import METHOD_SUBSYSTEM_EFFECTS
from app.services.rules import TIGHT_BUILD_LIMIT_GB, disk_severity

pytestmark = pytest.mark.critical

#: Расхождения знака между курируемой таблицей и карточкой метода на 2026-09-12.
KNOWN_SIGN_CONFLICTS: set[tuple[str, str]] = {
    ("async_incremental_saves", "impact_cpu"),
    ("async_loading_pipeline", "impact_cpu"),
    ("chunked_procedural_terrain", "impact_cpu"),
    ("chunked_procedural_terrain", "impact_ram"),
    ("delta_compression_state", "impact_cpu"),
    ("deterministic_lockstep", "impact_cpu"),
    ("dynamic_resolution_scaling", "impact_gpu"),
    ("full_path_tracing_pipeline", "impact_gpu"),
    ("gpu_compute_culling", "impact_gpu"),
    ("gpu_procedural_placement", "impact_vram"),
    ("hardware_raytraced_gi", "impact_gpu"),
    ("lightmap_atlas_baking", "impact_vram"),
    ("meshlet_pipeline_adoption", "impact_gpu"),
    ("particle_pooling", "impact_ram"),
    ("raycast_vehicle_physics", "impact_cpu"),
    ("rt_effect_resolution_budget", "impact_vram"),
    ("selective_ray_traced_effects", "impact_gpu"),
    ("splitscreen_render_budget", "impact_ram"),
    ("splitscreen_render_budget", "impact_vram"),
    ("tilemap_chunk_streaming", "impact_cpu"),
    ("virtual_texturing", "impact_ram"),
    ("world_partition_streaming", "impact_cpu"),
}

PAIRS = (("cpu", "impact_cpu"), ("gpu", "impact_gpu"),
         ("mem", "impact_ram"), ("mem", "impact_vram"))


def _load_sign(code: str, subsys: str) -> int:
    """Знак ПРИВЕДЁННОЙ нагрузки по курируемой таблице: +1 растёт, −1 падает."""
    total = sum(((METHOD_SUBSYSTEM_EFFECTS.get(code) or {}).get(subsys) or {}).values())
    if total == 0:
        return 0
    if subsys in ("cpu", "gpu"):
        return -1 if total > 0 else 1
    return 1 if total > 0 else -1


def _sgn(value) -> int:
    return 0 if not value else (1 if value > 0 else -1)


def test_sign_contract_between_curated_effects_and_method_cards(db):
    """Курируемая таблица и карточка метода обязаны говорить одно и то же."""
    from app.models import Method

    methods = {m.code: m for m in db.query(Method).all()}
    conflicts: set[tuple[str, str]] = set()
    for code, method in methods.items():
        if code not in METHOD_SUBSYSTEM_EFFECTS:
            continue
        for subsys, attr in PAIRS:
            curated = _load_sign(code, subsys)
            card = _sgn(getattr(method, attr))
            if curated and card and curated != card:
                conflicts.add((code, attr))

    new = conflicts - KNOWN_SIGN_CONFLICTS
    fixed = KNOWN_SIGN_CONFLICTS - conflicts
    assert not new, (
        "Новые расхождения знака между METHOD_SUBSYSTEM_EFFECTS и impact_*: "
        f"{sorted(new)}. Карточка метода и профиль нагрузки противоречат друг другу."
    )
    assert not fixed, (
        "Расхождения исправлены — сократите KNOWN_SIGN_CONFLICTS: "
        f"{sorted(fixed)}"
    )


def test_curated_cpu_positive_means_saving():
    """Соглашение cpu/gpu закреплено: плюс в таблице — это экономия."""
    assert _load_sign("hierarchical_lod", "cpu") == -1
    assert _load_sign("hierarchical_lod", "gpu") == -1


def test_curated_mem_positive_means_growth():
    """Соглашение памяти противоположно: плюс — это прирост объёма."""
    assert _load_sign("virtual_texturing", "mem") == -1  # textures: -0.45
    assert _load_sign("lightmap_atlas_baking", "mem") == 1  # textures: +0.20


def test_disk_severity_falls_as_limit_grows():
    """R16: критичность диска падает по мере ослабления предела сборки.

    Прежде было `0.4 if size_limit_gb else 0.25` — ступенька на факте НАЛИЧИЯ
    поля: предел «4096 ГБ» поднимал критичность так же, как «2 ГБ».
    """
    assert disk_severity(None) == 0.25
    assert disk_severity(TIGHT_BUILD_LIMIT_GB) == 0.4
    assert disk_severity(4096) == 0.25
    assert disk_severity(TIGHT_BUILD_LIMIT_GB) > disk_severity(64) > disk_severity(256)
