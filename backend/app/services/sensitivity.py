"""Устойчивость ранжирования к дрожанию весов.

Коэффициент TOPSIS относителен: сдвиг веса на пару процентов может поменять
места у близких альтернатив. Честный инструмент показывает это заранее:
карточка помечается устойчивой, только если ранг не двигается при изменении
каждого веса на ±10% по одному. Иначе показывается вилка рангов.

Функция чистая и детерминированная: те же входы — тот же ответ.
"""
from __future__ import annotations

from dataclasses import dataclass

from .topsis import Criterion, topsis

#: Относительное дрожание веса в каждую сторону.
DELTA = 0.10


@dataclass(frozen=True)
class Stability:
    rank_min: int
    rank_max: int
    stable: bool


def _order(scores: list[float], codes: list[str]) -> list[int]:
    """Порядок индексов: тот же тай-брейк, что и в рекомендателе."""
    return sorted(range(len(scores)), key=lambda i: (-scores[i], codes[i]))


def analyze(
    matrix: list[list[float]],
    criteria: list[Criterion],
    codes: list[str],
    delta: float = DELTA,
) -> dict[str, Stability] | None:
    """Вилка рангов каждого метода при дрожании весов.

    Возвращает None, когда сравнивать нечего (меньше двух различимых строк):
    там и TOPSIS некомпарабелен, и говорить об устойчивости нечего.
    """
    if len(matrix) < 2 or len(criteria) == 0:
        return None
    base = topsis(matrix, criteria)
    if not base.comparable:
        return None
    base_ranks = {idx: rank for rank, idx in enumerate(_order(base.scores, codes), start=1)}
    extremes: dict[int, list[int]] = {i: [base_ranks[i]] for i in range(len(matrix))}
    for pos, criterion in enumerate(criteria):
        for factor in (1.0 - delta, 1.0 + delta):
            tweaked = [
                Criterion(criterion.key, criterion.label, criterion.kind,
                          criterion.weight * factor) if i == pos else criterion
                for i, criterion in enumerate(criteria)
            ]
            perturbed = topsis(matrix, tweaked)
            if not perturbed.comparable:
                continue
            for rank, idx in enumerate(_order(perturbed.scores, codes), start=1):
                extremes[idx].append(rank)
    out: dict[str, Stability] = {}
    for idx, code in enumerate(codes):
        ranks = extremes[idx]
        out[code] = Stability(rank_min=min(ranks), rank_max=max(ranks),
                              stable=min(ranks) == max(ranks))
    return out
