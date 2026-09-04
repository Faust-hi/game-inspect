"""Поиск похожих игр по расстоянию Гауэра.

Метод позволяет сравнивать проекты, описываемые одновременно числовыми
и категориальными признаками: для каждого признака вычисляется частное
расстояние от 0 до 1, затем они усредняются с весами.

Категориальный признак: 0 при совпадении, 1 при различии.
Числовой признак: |xi − xj| / Rk, где Rk — размах признака в каталоге.
Отсутствующие значения исключаются из сравнения.
"""
from __future__ import annotations

from dataclasses import dataclass

from ..models.entities import GameExample
from ..schemas.catalog import ProjectProfile

LEVEL_TO_NUMBER = {"low": 0.25, "medium": 0.55, "high": 0.9, "small": 0.25, "large": 0.9, "very_large": 1.0}
SCALE_TO_NUMBER = {"small": 0.25, "medium": 0.55, "large": 0.8, "very_large": 1.0}


def canonical_engine(value: str | None) -> str | None:
    """Приводит название движка к семейству.

    Проект хранит движок как «unreal», а пример игры — как «Unreal Engine 5.1».
    Для расстояния Гауэра это разные категории, и совпадение не засчитывается,
    хотя технически игры сравнимы. Канонизация сводит оба значения к «unreal».

    Собственные движки сводятся к «custom»: сравнивать конкретные названия
    бессмысленно, а общий признак «свой движок» сопоставим.
    """
    if not value:
        return None
    text = value.strip().lower()
    if not text:
        return None
    if "unreal" in text:
        return "unreal"
    if "unity" in text:
        return "unity"
    if "godot" in text:
        return "godot"
    # Движки Трека 1 — отдельные семейства, чтобы похожесть различала их,
    # а не схлопывала в «custom». Остальные (id tech, anvil, decima и т.д.) —
    # это Трек 2, они по-прежнему сводятся к «custom».
    if "cryengine" in text or "cry engine" in text:
        return "cryengine"
    if "heroengine" in text or "hero engine" in text:
        return "heroengine"
    if "source" in text:
        return "source"
    for marker in ("id tech", "anvil", "decima", "fox", "havok"):
        if marker in text:
            return "custom"
    return "custom"

# Признак: (тип, вес, размах)
FEATURES: dict[str, tuple[str, float, float]] = {
    "format": ("categorical", 1.0, 1.0),
    "world_type": ("categorical", 1.5, 1.0),
    "scale": ("numeric", 1.2, 0.75),
    "object_count": ("numeric", 1.0, 0.65),
    "npc_count": ("numeric", 1.0, 0.65),
    "target_fps": ("numeric", 0.6, 90.0),
    "target_resolution": ("numeric", 0.8, 3.0),
    "multiplayer": ("categorical", 1.2, 1.0),
    "player_count": ("numeric", 0.8, 64.0),
    "engine": ("categorical", 0.6, 1.0),
    "features": ("set", 1.6, 1.0),
}

RESOLUTION_TO_NUMBER = {
    "720p": 1.0, "1080p": 2.0, "1440p": 2.5, "2k": 2.7, "4k": 4.0, "2160p": 4.0,
}


def _resolution_number(value: str) -> float | None:
    if not value:
        return None
    return RESOLUTION_TO_NUMBER.get(value.strip().lower())


def _level_number(value: str | None) -> float | None:
    if not value:
        return None
    return LEVEL_TO_NUMBER.get(value)


def project_vector(profile: ProjectProfile) -> dict[str, object]:
    """Привести профиль проекта к вектору признаков."""
    return {
        "format": profile.format,
        "world_type": profile.world_type,
        "scale": SCALE_TO_NUMBER.get(profile.scale, 0.55),
        "object_count": _level_number(profile.object_count_level) or 0.55,
        "npc_count": _level_number(profile.npc_count_level) or 0.55,
        "target_fps": float(profile.target_fps),
        "target_resolution": _resolution_number(profile.target_resolution),
        "multiplayer": profile.multiplayer,
        "player_count": float(max(1, profile.player_count)),
        "engine": canonical_engine(profile.engine),
        "features": set(profile.functions),
    }


def example_vector(example: GameExample) -> dict[str, object]:
    """Привести пример игры к вектору признаков."""
    return {
        "format": example.format,
        "world_type": example.world_type,
        "scale": SCALE_TO_NUMBER.get(example.scale, 0.55),
        "object_count": _level_number(example.object_count_level) or 0.55,
        "npc_count": _level_number(example.npc_count_level) or 0.55,
        "target_fps": float(example.target_fps),
        "target_resolution": _resolution_number(example.target_resolution),
        "multiplayer": bool(example.multiplayer),
        "player_count": float(max(1, example.player_count)),
        "engine": canonical_engine(example.engine),
        "features": set(example.features or []),
    }


@dataclass
class GowerResult:
    distance: float
    similarity: float
    comparable_weight: float


def gower_distance(a: dict[str, object], b: dict[str, object]) -> GowerResult:
    """Частное расстояние Гауэра между двумя векторами признаков."""
    total = 0.0
    weight_sum = 0.0
    for key, (kind, weight, span) in FEATURES.items():
        va, vb = a.get(key), b.get(key)
        if va is None or vb is None:
            continue
        if kind == "categorical":
            delta = 0.0 if va == vb else 1.0
        elif kind == "numeric":
            delta = min(1.0, abs(float(va) - float(vb)) / span) if span else 0.0
        elif kind == "set":
            sa, sb = set(va), set(vb)  # type: ignore[arg-type]
            union = sa | sb
            delta = 0.0 if not union else 1.0 - len(sa & sb) / len(union)
        else:
            continue
        total += weight * delta
        weight_sum += weight
    if weight_sum == 0:
        return GowerResult(distance=1.0, similarity=0.0, comparable_weight=0.0)
    distance = total / weight_sum
    return GowerResult(distance=distance, similarity=1.0 - distance, comparable_weight=weight_sum)


def find_similar(
    profile: ProjectProfile,
    examples: list[GameExample],
    top_n: int = 5,
    basket: list[str] | None = None,
) -> list[tuple[GameExample, float, list[str]]]:
    """Вернуть наиболее похожие игры и совпавшие с выбранными решениями техники.

    Раньше совпадения искались как пересечение `optimizations_used` примера с
    `profile.functions` — кодами игровых функций. Это разные множества: в
    `optimizations_used` лежат коды методов оптимизации, в функциях — коды
    игровых возможностей. Пересечение было случайным и совпадало у двух игр из
    пятнадцати. Сравнивать нужно с корзиной выбранных решений.
    """
    pv = project_vector(profile)
    basket_codes = set(basket or [])
    scored: list[tuple[GameExample, float, list[str]]] = []
    for example in examples:
        ev = example_vector(example)
        result = gower_distance(pv, ev)
        matching = sorted(set(example.optimizations_used or []) & basket_codes)
        scored.append((example, round(result.similarity, 4), matching))
    scored.sort(key=lambda item: (-item[1], item[0].title))
    return scored[:top_n]
