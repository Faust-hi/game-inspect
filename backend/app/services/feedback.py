"""Петля обратной связи: оценки применимости и предложения по достоверности.

Инструмент-консультант не переписывает оценки сам: предложение вычисляется
чистой функцией с явными порогами, а применяет его человек через
административный раздел. Так калибровка остаётся проверяемой, а не чёрным
ящиком: видно, сколько голосов стоит за каждым предложением.
"""
from __future__ import annotations

from dataclasses import dataclass

#: Минимум голосов, после которого предложение считается значимым.
MIN_VOTES = 5
#: Доля «бесполезно», при которой достоверность предлагается снизить.
DOWN_RATE = 0.6
#: Шаг изменения достоверности.
STEP_DOWN = 0.10
STEP_UP = 0.05


@dataclass(frozen=True)
class MethodFeedback:
    method_code: str
    up: int
    down: int

    @property
    def total(self) -> int:
        return self.up + self.down

    @property
    def helpful_rate(self) -> float:
        return self.up / self.total if self.total else 0.0


@dataclass(frozen=True)
class ConfidenceSuggestion:
    method_code: str
    current_confidence: float
    suggested_confidence: float
    reason: str


def summarize(feedback: dict[str, dict[str, int]]) -> list[MethodFeedback]:
    """Свернуть голоса {код: {up, down}} в список по убыванию числа голосов."""
    rows = [
        MethodFeedback(method_code=code,
                       up=int(votes.get("up", 0)), down=int(votes.get("down", 0)))
        for code, votes in feedback.items()
    ]
    rows.sort(key=lambda row: (-row.total, row.method_code))
    return rows


def suggest_confidence_adjustments(
    summary: list[MethodFeedback],
    current: dict[str, float],
) -> list[ConfidenceSuggestion]:
    """Предложения по достоверности. Пусто — тоже ответ: данных мало."""
    out: list[ConfidenceSuggestion] = []
    for row in summary:
        if row.total < MIN_VOTES or row.method_code not in current:
            continue
        confidence = current[row.method_code]
        down_rate = row.down / row.total
        if down_rate >= DOWN_RATE:
            suggested = round(max(0.1, confidence - STEP_DOWN), 2)
            if suggested != confidence:
                out.append(ConfidenceSuggestion(
                    method_code=row.method_code,
                    current_confidence=confidence,
                    suggested_confidence=suggested,
                    reason=f"{row.down} из {row.total} отметили бесполезным — достоверность завышена.",
                ))
        elif row.helpful_rate >= 0.8:
            suggested = round(min(0.95, confidence + STEP_UP), 2)
            if suggested != confidence:
                out.append(ConfidenceSuggestion(
                    method_code=row.method_code,
                    current_confidence=confidence,
                    suggested_confidence=suggested,
                    reason=f"{row.up} из {row.total} отметили полезным — достоверность можно поднять.",
                ))
    return out
