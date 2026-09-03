"""Метод TOPSIS для ранжирования допустимых решений.

Классическая схема метода:
1. построение матрицы «альтернатива × критерий»;
2. векторная нормализация столбцов;
3. умножение на веса критериев;
4. определение положительного и отрицательного идеальных решений;
5. вычисление евклидовых расстояний до них;
6. вычисление коэффициента близости  C = d⁻ / (d⁺ + d⁻).

Метод детерминирован: при одинаковых входных данных результат воспроизводится.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import sqrt


@dataclass(frozen=True)
class Criterion:
    key: str
    label: str
    kind: str          # "benefit" — больше лучше; "cost" — меньше лучше
    weight: float = 1.0


@dataclass(frozen=True)
class TopsisResult:
    """Результат TOPSIS вместе с признаком вырожденности.

    `comparable=False` означает, что относительное сравнение невозможно: метода
    хватает на одну альтернативу или все альтернативы одинаковы. В этом случае
    `scores` содержит нейтральное значение и его нельзя выдавать за оценку
    качества — иначе единственный применимый вариант получает 0.0 и попадает
    в разряд «не рекомендуется» только из-за того, что сравнивать его не с чем.
    """

    scores: list[float]
    comparable: bool
    reason: str = ""

    def __iter__(self):
        return iter(self.scores)


#: Значение, которое получает альтернатива при невозможности сравнения.
NEUTRAL_SCORE = 0.5


def topsis(matrix: list[list[float]], criteria: list[Criterion]) -> TopsisResult:
    """Вернуть коэффициент близости для каждой альтернативы (0..1, больше — лучше)."""
    n = len(matrix)
    if n == 0:
        return TopsisResult(scores=[], comparable=False, reason="нет альтернатив")
    m = len(criteria)
    if m == 0:
        return TopsisResult(scores=[NEUTRAL_SCORE] * n, comparable=False, reason="нет критериев")
    if n == 1:
        return TopsisResult(
            scores=[NEUTRAL_SCORE],
            comparable=False,
            reason="одна альтернатива: сравнивать не с чем",
        )
    if _all_rows_equal(matrix):
        return TopsisResult(
            scores=[NEUTRAL_SCORE] * n,
            comparable=False,
            reason="альтернативы не различаются по критериям",
        )

    # 1-2. Векторная нормализация.
    norms: list[float] = []
    for j in range(m):
        col_sum = sum(matrix[i][j] ** 2 for i in range(n))
        norms.append(sqrt(col_sum) if col_sum > 0 else 0.0)

    normalized = [[0.0] * m for _ in range(n)]
    for i in range(n):
        for j in range(m):
            normalized[i][j] = matrix[i][j] / norms[j] if norms[j] > 0 else 0.0

    # 3. Взвешивание.
    weighted = [[normalized[i][j] * criteria[j].weight for j in range(m)] for i in range(n)]

    # 4. Идеальные решения.
    best: list[float] = []
    worst: list[float] = []
    for j in range(m):
        column = [weighted[i][j] for i in range(n)]
        if criteria[j].kind == "benefit":
            best.append(max(column))
            worst.append(min(column))
        else:
            best.append(min(column))
            worst.append(max(column))

    # 5-6. Расстояния и коэффициент близости.
    scores: list[float] = []
    for i in range(n):
        d_plus = sqrt(sum((weighted[i][j] - best[j]) ** 2 for j in range(m)))
        d_minus = sqrt(sum((weighted[i][j] - worst[j]) ** 2 for j in range(m)))
        total = d_plus + d_minus
        scores.append(NEUTRAL_SCORE if total == 0 else d_minus / total)
    return TopsisResult(scores=scores, comparable=True)


def _all_rows_equal(matrix: list[list[float]]) -> bool:
    first = matrix[0]
    return all(row == first for row in matrix[1:])


def criterion_matrix_rows(matrix: list[list[float]], criteria: list[Criterion]) -> list[list[dict]]:
    """Вспомогательная функция: нормализованные и взвешенные значения для объяснения решения."""
    n = len(matrix)
    if n == 0:
        return []
    m = len(criteria)
    # При одной альтернативе векторная нормализация даёт ±1 для любого ненулевого
    # значения: сравнивать не с чем, поэтому показывается исходное значение.
    single = n == 1
    norms = [
        sqrt(sum(matrix[i][j] ** 2 for i in range(n))) if sum(matrix[i][j] ** 2 for i in range(n)) > 0 else 0.0
        for j in range(m)
    ]
    rows: list[list[dict]] = []
    for i in range(n):
        row = []
        for j in range(m):
            normalized = matrix[i][j] if single else (matrix[i][j] / norms[j] if norms[j] > 0 else 0.0)
            row.append({
                "key": criteria[j].key,
                "label": criteria[j].label,
                "raw": round(matrix[i][j], 4),
                "normalized": round(normalized, 4),
                "weight": round(criteria[j].weight, 4),
                "weighted": round(normalized * criteria[j].weight, 4),
                "kind": criteria[j].kind,
            })
        rows.append(row)
    return rows
