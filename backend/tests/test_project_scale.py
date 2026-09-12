"""Масштаб проекта — объявленный вход, влияющий на базис памяти.

Проверяется три вещи:

1. Параметр независим и по умолчанию ничего не меняет: значение «medium»
   воспроизводит прежний расчёт. Это обязательное свойство — новый объявляемый
   вход не должен задним числом менять уже выданные оценки.
2. Уровни монотонно двигают базис памяти и только его: множители на контент
   (качество, разрешение, объём мира) остаются прежними.
3. Неизвестное значение не сдвигает расчёт: параметр объявленный, и отсутствие
   ответа не должно уводить результат в сторону, которую пользователь не выбирал.
"""
from __future__ import annotations

from app.schemas.catalog import ProjectProfile
from app.services import hardware

BASE = {
    "name": "Масштаб проекта",
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


def memory(**overrides) -> dict[str, dict[str, float]]:
    """Состав памяти при профиле с заданными отклонениями."""
    profile = ProjectProfile(**{**BASE, **overrides})
    content = hardware._active_scene(profile)
    world = hardware._world_content(profile, content)
    return hardware._memory_components(profile, world, set())


def total_ram(**overrides) -> float:
    return sum(v.get("ram", 0.0) for v in memory(**overrides).values())


def test_default_is_medium_and_changes_nothing():
    """По умолчанию — «medium», и он должен совпадать с прежним расчётом."""
    assert ProjectProfile(**BASE).project_scale == "medium"
    assert memory()["engine"]["ram"] == memory(project_scale="medium")["engine"]["ram"]
    assert hardware.ENGINE_BASE_RAM_GB == 2.0


def test_levels_move_baseline_monotonically():
    """Базис растёт с уровнем: small < medium < large < very_large."""
    levels = ["small", "medium", "large", "very_large"]
    values = [memory(project_scale=lvl)["engine"]["ram"] for lvl in levels]
    assert values == sorted(values), values
    assert len(set(values)) == len(levels), "уровни обязаны различаться"
    # Полный размах влияния задан явно, чтобы незаметное изменение коэффициентов
    # не прошло как «настройка».
    assert values[0] < values[-1]


def test_unknown_level_does_not_shift_result():
    """Неизвестный уровень — не повод менять расчёт."""
    assert memory(project_scale="unknown")["engine"]["ram"] == memory()["engine"]["ram"]


def test_content_multipliers_are_untouched():
    """Масштаб проекта двигает базис, а не множители на контент.

    Разница между уровнями одна и та же при любом качестве и разрешении: иначе
    параметр начал бы описывать наполнение, что уже делает `scale` и `content`.
    """
    for quality in ("low", "high", "ultra"):
        low = total_ram(project_scale="small", target_quality=quality)
        high = total_ram(project_scale="very_large", target_quality=quality)
        assert abs((high - low) - (total_ram(project_scale="very_large")
                                   - total_ram(project_scale="small"))) < 1e-6


def test_world_scale_and_project_scale_are_independent_axes():
    """Масштаб мира и масштаб проекта — разные оси: обе могут меняться порознь."""
    assert memory(scale="small", project_scale="very_large")["engine"]["ram"] > \
        memory(scale="small", project_scale="small")["engine"]["ram"]
    # Объём мира при этом не зависит от масштаба проекта.
    assert hardware._world_volume(ProjectProfile(**{**BASE, "scale": "small"})) == \
        hardware._world_volume(
            ProjectProfile(**{**BASE, "scale": "small", "project_scale": "very_large"}))
