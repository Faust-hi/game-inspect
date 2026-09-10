"""Математика решений и ранжирование (офлайн).

Каждый тест — один дефект, опасный неверной рекомендацией:
перевёрнутый порядок, игнорирование весов, ложная точность при
отсутствии сравнения, нестабильный порядок, нечисловой результат.
Ожидаемое следует из независимого расчёта на малой матрице,
а не из копирования формулы реализации.
"""
from __future__ import annotations

import math

from app.services.sensitivity import analyze
from app.services.topsis import NEUTRAL_SCORE, Criterion, topsis


def _criteria():
    return [
        Criterion("gain", "Эффект", "benefit", 1.0),
        Criterion("cost", "Стоимость", "cost", 1.0),
    ]


def test_dominant_alternative_ranks_first():
    """Доминирующая по всем критериям альтернатива — первая.

    Дефект: инверсия направления критерия (benefit/cost перепутаны).
    Опасность: пользователю советуют худшее решение как лучшее.
    """
    matrix = [[0.9, 2.0], [0.3, 5.0], [0.6, 3.0]]
    scores = topsis(matrix, _criteria()).scores
    assert scores[0] > scores[2] > scores[1]


def test_weights_flip_order():
    """Вес меняет порядок, а не только значения баллов.

    Дефект: приоритет пользователя не влияет на ранжирование.
    Опасность: выбор «производительность vs качество» — декорация.
    """
    matrix = [[0.4, 1.0], [0.8, 4.0]]
    effect_first = topsis(matrix, [
        Criterion("gain", "Эффект", "benefit", 3.0),
        Criterion("cost", "Стоимость", "cost", 1.0),
    ]).scores
    assert effect_first[1] > effect_first[0]
    cost_first = topsis(matrix, [
        Criterion("gain", "Эффект", "benefit", 1.0),
        Criterion("cost", "Стоимость", "cost", 3.0),
    ]).scores
    assert cost_first[0] > cost_first[1]


def test_single_alternative_is_neutral_not_worst():
    """Единственная альтернатива — нейтральна, а не «не рекомендуется».

    Дефект: классический TOPSIS при n=1 даёт 0.0 (идеалы совпадают).
    Опасность: хорошее единственное решение помечается худшим.
    """
    result = topsis([[0.9, 1.0]], _criteria())
    assert result.scores == [NEUTRAL_SCORE]
    assert result.comparable is False


def test_identical_alternatives_are_incomparable():
    """Одинаковые альтернативы несравнимы, но не нулевые."""
    result = topsis([[0.5], [0.5], [0.5]], _criteria()[:1])
    assert len(set(result.scores)) == 1
    assert result.scores[0] == NEUTRAL_SCORE
    assert result.comparable is False


def test_same_input_gives_same_order():
    """Одинаковый расчёт воспроизводится (детерминизм)."""
    matrix = [[0.5, 3.0], [0.8, 4.0], [0.2, 1.0]]
    assert topsis(matrix, _criteria()).scores == topsis(matrix, _criteria()).scores


def test_scores_are_finite_and_bounded():
    """Результат — число в [0, 1], а не NaN/inf (нечисловой результат)."""
    matrix = [[0.4, 1.0], [0.8, 4.0], [0.6, 3.0]]
    for score in topsis(matrix, _criteria()).scores:
        assert math.isfinite(score)
        assert 0.0 <= score <= 1.0


def test_clear_winner_is_stable_and_tie_shows_fork():
    """Явный победитель стабилен; почти-ничья показывает вилку.

    Дефект: ложная точность — ничья выглядит уверенной победой.
    Опасность: пользователь внедряет решение, думая, что выбор надёжен.
    """
    stable = analyze([[0.9, 1.0], [0.2, 5.0]], _criteria(), ["a", "b"])
    assert stable is not None and stable["a"].stable is True
    assert (stable["a"].rank_min, stable["a"].rank_max) == (1, 1)
    tie = analyze([[1.0, 1.01], [0.99, 1.0]], _criteria(), ["a", "b"])
    assert tie is not None and tie["a"].stable is False
    assert (tie["a"].rank_min, tie["a"].rank_max) == (1, 2)


def test_single_option_has_no_stability_fork():
    """Без сравнения вилка не строится (честный прочерк вместо псевдоточности)."""
    assert analyze([[0.5, 0.5]], _criteria(), ["a"]) is None


def test_priority_changes_api_ranking_not_just_weights(client, profile):
    """Приоритет переставляет рекомендации через API.

    Дефект: веса попадают в ответ, но порядок не меняется.
    Опасность: персонализация под приоритет — иллюзия.
    """
    base = dict(profile, functions=[
        "open_world_streaming", "dynamic_global_illumination", "crowd_simulation",
    ])
    orders = {}
    for priority in ("performance", "quality"):
        data = client.post(
            "/api/recommend",
            json={"profile": dict(base, priority=priority), "basket": []},
        ).json()
        assert len(data["recommendations"]) > 1
        orders[priority] = [item["method_code"] for item in data["recommendations"]]
    assert orders["performance"] != orders["quality"]
