"""Модульные тесты математических методов: TOPSIS, расстояние Гауэра, правила."""
from __future__ import annotations

import pytest

from app.schemas.catalog import ProjectProfile
from app.services import rules
from app.services.topsis import NEUTRAL_SCORE, Criterion, topsis


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
    result = topsis(matrix, criteria)
    assert result.comparable is True
    scores = result.scores
    assert scores[0] > scores[2] > scores[1]
    assert 0.0 <= min(scores) and max(scores) <= 1.0


def test_topsis_is_deterministic():
    """При одинаковых входных данных результат воспроизводится."""
    criteria = [Criterion("a", "A", "benefit", 1.0), Criterion("b", "B", "cost", 2.0)]
    matrix = [[0.5, 3.0], [0.8, 4.0], [0.2, 1.0]]
    first = topsis(matrix, criteria)
    second = topsis(matrix, criteria)
    assert first.scores == second.scores
    assert first.comparable == second.comparable


def test_topsis_handles_identical_alternatives():
    """Одинаковые альтернативы не сравнить: коэффициент нейтральный, признак вырожденности поднят."""
    criteria = [Criterion("a", "A", "benefit", 1.0)]
    result = topsis([[0.5], [0.5], [0.5]], criteria)
    assert len(result.scores) == 3
    assert len(set(result.scores)) == 1
    # Ключевой момент: раньше совпадение идеалов давало 0.0, и равные
    # варианты попадали в разряд «не рекомендуется».
    assert result.scores[0] == NEUTRAL_SCORE
    assert result.comparable is False
    assert result.reason


def test_topsis_single_alternative_is_not_penalized():
    """Единственная альтернатива не должна получать 0.0 из-за отсутствия сравнения.

    Классический TOPSIS при n=1 совмещает положительный и отрицательный идеалы,
    из-за чего коэффициент близости равен нулю, и хорошее решение получает
    текстовую пометку «не рекомендуется». Здесь это предотвращено.
    """
    criteria = [
        Criterion("gain", "Эффект", "benefit", 1.0),
        Criterion("cost", "Стоимость", "cost", 1.0),
    ]
    result = topsis([[0.9, 1.0]], criteria)
    assert result.scores == [NEUTRAL_SCORE]
    assert result.comparable is False
    assert "одна альтернатива" in result.reason


def test_topsis_single_alternative_score_is_independent_of_values():
    """При n=1 значение коэффициента не зависит от величин критериев."""
    criteria = [Criterion("a", "A", "benefit", 1.0)]
    good = topsis([[1.0]], criteria)
    bad = topsis([[0.01]], criteria)
    assert good.scores == bad.scores == [NEUTRAL_SCORE]
    assert good.comparable is False


def test_topsis_empty_matrix():
    result = topsis([], [Criterion("a", "A", "benefit")])
    assert result.scores == []
    assert result.comparable is False


def test_topsis_without_criteria():
    result = topsis([[1.0], [2.0]], [])
    assert result.scores == [NEUTRAL_SCORE, NEUTRAL_SCORE]
    assert result.comparable is False


def test_topsis_weights_change_ranking():
    """Вес критерия влияет на порядок, а не только на разницу значений."""
    criteria = [
        Criterion("gain", "Эффект", "benefit", 3.0),
        Criterion("cost", "Стоимость", "cost", 1.0),
    ]
    #    gain  cost
    matrix = [
        [0.4, 1.0],   # дешёвый, но слабый эффект
        [0.8, 4.0],   # сильный эффект, но дорогой
    ]
    with_effect_weight = topsis(matrix, criteria)
    assert with_effect_weight.scores[1] > with_effect_weight.scores[0]

    cheap_first = [
        Criterion("gain", "Эффект", "benefit", 1.0),
        Criterion("cost", "Стоимость", "cost", 3.0),
    ]
    with_cost_weight = topsis(matrix, cheap_first)
    assert with_cost_weight.scores[0] > with_cost_weight.scores[1]


def test_topsis_identical_columns_do_not_produce_zero():
    """Если альтернативы различаются, но столбец константен, метод остаётся рабочим."""
    criteria = [
        Criterion("same", "Одинаковый", "benefit", 1.0),
        Criterion("diff", "Различающийся", "benefit", 1.0),
    ]
    result = topsis([[0.5, 0.2], [0.5, 0.9]], criteria)
    assert result.comparable is True
    assert result.scores[1] > result.scores[0]


# ---------------------------------------------------------------------------
# Расстояние Гауэра
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
