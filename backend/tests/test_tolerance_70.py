"""Допуск калибровки: верифицированные кейсы обязаны лежать в пределах ±1 класса.

Критерий точности проекта (см. CALIBRATION_WILD66.md): инструмент не видит код
игры и точное устройство модифицированного движка — он собирает максимально
похожую конфигурацию из функций и решений. Поэтому требуется совпадение
с погрешностью не менее 70% схожести: на практике — не менее 70% эталонных
сверок должны попадать в ±1 класс (фактически на 66 играх: 46/51 = 90.2%).

Ниже — точечные регрессионные проверки на кейсах, где официальные требования
имеют проверенные цели 1080p/60 и точные якоря в каталоге. Каждый профиль —
эталонная нагрузка (источник требований — в комментарии): если данные каталога
или формулы тихо уплывут больше чем на класс, тест упадёт.
"""
from __future__ import annotations


def _estimate(client, basket=(), **overrides):
    profile = {
        "name": "Допуск-70",
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
    return client.post(
        "/api/hardware-estimate", json={"profile": profile, "basket": list(basket)}
    ).json()


def _within_one(est_class: int, official_class: int) -> bool:
    return abs(est_class - official_class) <= 1


def test_deathloop_matches_official_specs(client):
    """Deathloop: официалы 2060/9700K под 1080p/60/high (Steam + PC Gamer)."""
    est = _estimate(
        client, world_type="hub",
        functions=["character_animation", "ai_pathfinding", "physics_simulation",
                   "dynamic_shadows", "post_processing"],
    )
    assert _within_one(est["gpu_class"], 2)  # RTX 2060 — класс 2 каталога
    assert _within_one(est["cpu_class"], 3)  # i7-9700K — класс 3 каталога


def test_wolong_gpu_matches_official_specs(client):
    """Wo Long: официалы 2060 под 1080p/60/Standard (Team Ninja)."""
    est = _estimate(
        client,
        functions=["character_animation", "ai_pathfinding", "physics_simulation",
                   "dynamic_shadows", "post_processing", "particle_systems"],
    )
    assert _within_one(est["gpu_class"], 2)  # RTX 2060 — класс 2 каталога


def test_like_a_dragon_matches_official_specs(client):
    """Like a Dragon: IW — официалы 2060/Ryzen 5 1600 под 1080p/60 без FSR."""
    est = _estimate(
        client, world_type="hub", npc_count_level="medium",
        functions=["character_animation", "ai_pathfinding", "physics_simulation",
                   "dynamic_shadows", "post_processing"],
    )
    assert _within_one(est["gpu_class"], 2)  # RTX 2060 — класс 2 каталога
    assert _within_one(est["cpu_class"], 2)  # Ryzen 5 1600 — класс 2 каталога


def test_granblue_cpu_matches_official_specs(client):
    """Granblue Relink: официалы i7-8700 под 1080p/60/Ultra (Cygames)."""
    est = _estimate(
        client, world_type="hub", npc_count_level="medium",
        functions=["character_animation", "ai_pathfinding", "physics_simulation",
                   "dynamic_shadows", "post_processing", "particle_systems"],
        multiplayer=True, player_count=4,
    )
    assert _within_one(est["cpu_class"], 3)  # i7-8700 — класс 3 каталога


def test_mirage_cpu_matches_official_specs(client):
    """AC Mirage: официалы i7-8700K под 1080p/60/High (Ubisoft)."""
    est = _estimate(
        client, world_type="open_world", scale="medium", npc_count_level="medium",
        functions=["open_world_streaming", "character_animation", "ai_pathfinding",
                   "physics_simulation", "dynamic_shadows", "post_processing"],
    )
    assert _within_one(est["cpu_class"], 3)  # i7-8700K — класс 3 каталога


def test_back4blood_cpu_within_tolerance(client):
    """Back 4 Blood: официалы i5-8400 под 1080p/60/High (Turtle Rock)."""
    est = _estimate(
        client,
        functions=["particle_systems", "physics_simulation", "character_animation",
                   "dynamic_shadows", "post_processing"],
        multiplayer=True, player_count=4,
    )
    assert _within_one(est["cpu_class"], 2)  # i5-8400 — класс 2 каталога


def test_tekken_cpu_within_tolerance(client):
    """Tekken 8: официалы Ryzen 5 2600; DSOG: dual-core держит 60fps Ultra."""
    est = _estimate(
        client, world_type="arena", scale="small",
        object_count_level="low", npc_count_level="low",
        functions=["character_animation", "post_processing"],
        multiplayer=True, player_count=2,
    )
    assert _within_one(est["cpu_class"], 2)  # Ryzen 5 2600 — класс 2 каталога


def test_persona3_gpu_within_tolerance(client):
    """Persona 3 Reload: официалы GTX 1650 под 1080p/60/high (Atlus)."""
    est = _estimate(
        client, world_type="hub",
        functions=["character_animation", "ai_pathfinding", "dynamic_shadows",
                   "post_processing"],
    )
    assert _within_one(est["gpu_class"], 1)  # GTX 1650 — класс 1 каталога
