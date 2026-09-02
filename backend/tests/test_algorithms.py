"""Модульные тесты математических методов: TOPSIS, расстояние Гауэра, правила."""
from __future__ import annotations

import pytest

from app.schemas.catalog import ProjectProfile
from app.services import gower, rules
from app.services.topsis import Criterion, topsis


# ---------------------------------------------------------------------------
# TOPSIS
# ---------------------------------------------------------------------------
def test_topsis_prefers_better_alternative():
    """Альтернатива, доминирующая по всем критериям, получает высший коэффициент."""
    criteria = [
        Criterion("gain", "Эффект", "benefit", 1.0),
        Criterion("cost", "Стоимость", "cost", 1.0),
    ]
    #    gain  cost
    matrix = [
        [0.9, 2.0],   # доминирующая альтернатива
        [0.3, 5.0],   # худшая
        [0.6, 3.0],   # промежуточная
    ]
    scores = topsis(matrix, criteria)
    assert scores[0] > scores[2] > scores[1]
    assert 0.0 <= min(scores) and max(scores) <= 1.0


def test_topsis_is_deterministic():
    """При одинаковых входных данных результат воспроизводится."""
    criteria = [Criterion("a", "A", "benefit", 1.0), Criterion("b", "B", "cost", 2.0)]
    matrix = [[0.5, 3.0], [0.8, 4.0], [0.2, 1.0]]
    first = topsis(matrix, criteria)
    second = topsis(matrix, criteria)
    assert first == second


def test_topsis_handles_identical_alternatives():
    """Одинаковые альтернативы получают одинаковый коэффициент."""
    criteria = [Criterion("a", "A", "benefit", 1.0)]
    scores = topsis([[0.5], [0.5], [0.5]], criteria)
    assert len(scores) == 3
    assert len(set(scores)) == 1


def test_topsis_empty_matrix():
    assert topsis([], [Criterion("a", "A", "benefit")]) == []


# ---------------------------------------------------------------------------
# Расстояние Гауэра
# ---------------------------------------------------------------------------
def test_gower_identical_vectors_have_zero_distance():
    profile = ProjectProfile(format="3D", world_type="open_world", scale="large")
    a = gower.project_vector(profile)
    result = gower.gower_distance(a, a)
    assert result.distance == pytest.approx(0.0)
    assert result.similarity == pytest.approx(1.0)


def test_gower_different_formats_increase_distance():
    base = ProjectProfile(format="3D", world_type="open_world", scale="large")
    other = ProjectProfile(format="2D", world_type="open_world", scale="large")
    d = gower.gower_distance(gower.project_vector(base), gower.project_vector(other))
    assert d.distance > 0.0


def test_gower_missing_values_are_excluded():
    """Отсутствующий признак не должен искажать расстояние."""
    a = {"format": "3D", "scale": 0.8, "target_resolution": None}
    b = {"format": "3D", "scale": 0.8, "target_resolution": 2.0}
    with_resolution = gower.gower_distance(a, b)
    assert with_resolution.comparable_weight > 0.0
    # Разрешение исключено из сравнения, поэтому расстояние определяется
    # только совпадающими признаками и равно нулю.
    assert with_resolution.distance == pytest.approx(0.0)


def test_gower_find_similar_returns_ranked_list(db):
    from app.models.entities import GameExample
    from sqlalchemy import select

    examples = list(db.scalars(select(GameExample).where(GameExample.status == "published")))
    profile = ProjectProfile(format="3D", world_type="open_world", scale="large",
                             functions=["crowd_simulation"])
    result = gower.find_similar(profile, examples, top_n=5)
    assert len(result) == 5
    similarities = [item[1] for item in result]
    assert similarities == sorted(similarities, reverse=True)


# ---------------------------------------------------------------------------
# Экспертные правила
# ---------------------------------------------------------------------------
def test_rule_excludes_incompatible_format(db):
    from sqlalchemy import select

    from app.models.entities import Method

    method = db.scalar(select(Method).where(Method.applicable_formats.contains('"2D"')))
    profile = ProjectProfile(format="3D", world_type="linear")
    result = rules.evaluate(method, profile)
    # Метод, применимый и к 2D, и к 3D, не должен исключаться по формату.
    if "3D" in (method.applicable_formats or []):
        assert result.applicable
    else:
        assert not result.applicable


def test_rule_excludes_by_complexity_tolerance(db):
    from sqlalchemy import select

    from app.models.entities import Method

    method = db.scalar(select(Method).where(Method.complexity == 5))
    profile = ProjectProfile(complexity_tolerance=1)
    result = rules.evaluate(method, profile)
    assert not result.applicable
    assert any("Сложность внедрения" in reason for reason in result.excluded_reasons)


def test_rule_reports_late_stage_pressure(db):
    from sqlalchemy import select

    from app.models.entities import Method

    method = db.scalar(select(Method).where(Method.recommended_stage == "preproduction"))
    early = ProjectProfile(stage="preproduction")
    late = ProjectProfile(stage="release")
    assert rules.evaluate(method, early).stage_pressure == 0.0
    assert rules.evaluate(method, late).stage_pressure > 0.0


def test_rule_requires_missing_feature(db):
    from sqlalchemy import select

    from app.models.entities import Method

    method = db.scalar(select(Method).where(Method.requires_features != []))
    profile = ProjectProfile(functions=[])
    result = rules.evaluate(method, profile)
    assert not result.applicable


def test_min_scale_check(db):
    from sqlalchemy import select

    from app.models.entities import Method

    method = db.scalar(select(Method).where(Method.min_scale == "large"))
    assert rules.min_scale_satisfied(method, ProjectProfile(scale="very_large"))
    assert not rules.min_scale_satisfied(method, ProjectProfile(scale="small"))


def test_resource_fit_within_bounds(db):
    from sqlalchemy import select

    from app.models.entities import Method

    for method in db.scalars(select(Method)).all()[:20]:
        value = rules.resource_fit(method, ProjectProfile())
        assert 0.0 <= value <= 1.0
