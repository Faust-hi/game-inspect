"""Устойчивость ранга: вилка при дрожании весов, честный None без сравнения."""
from __future__ import annotations

from app.services.sensitivity import analyze
from app.services.topsis import Criterion


def _criteria():
    return [Criterion("gain", "Эффект", "benefit", 1.0),
            Criterion("cost", "Цена", "cost", 1.0)]


def test_clear_winner_is_stable():
    result = analyze([[0.9, 1.0], [0.2, 5.0]], _criteria(), ["a", "b"])
    assert result is not None
    assert result["a"].stable is True
    assert (result["a"].rank_min, result["a"].rank_max) == (1, 1)


def test_near_tie_is_unstable():
    """Почти равные альтернативы обязаны показать вилку, а не ложную точность.

    Ничья должна быть в пространстве оценок (d+ ≈ d-), а не в сырых числах:
    преимущество 0.01 по gain против 0.1 по cost — это разгром, а не ничья.
    """
    result = analyze([[1.0, 1.01], [0.99, 1.0]], _criteria(), ["a", "b"])
    assert result is not None
    assert result["a"].stable is False
    assert (result["a"].rank_min, result["a"].rank_max) == (1, 2)


def test_single_alternative_has_no_stability():
    assert analyze([[0.5, 0.5]], _criteria(), ["a"]) is None


def test_identical_alternatives_have_no_stability():
    assert analyze([[0.5, 0.5], [0.5, 0.5]], _criteria(), ["a", "b"]) is None


def test_api_returns_stability(client):
    response = client.post("/api/recommend", json={
        "profile": {"name": "T", "functions": ["open_world_streaming"]}, "basket": [],
    })
    recommendations = response.json()["recommendations"]
    assert recommendations
    assert all("stability" in item for item in recommendations)
    assert any(item["stability"] is not None for item in recommendations)
