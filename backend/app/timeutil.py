"""Единые правила работы с метками времени.

Колонки объявлены как `DateTime` без сведений о часовом поясе, поэтому SQLite
(и PostgreSQL в режиме `timestamp without time zone`) при чтении отдаёт
«наивное» значение: попытка вычесть его из `datetime.now(timezone.utc)`
приводит к `TypeError: can't subtract offset-naive and offset-aware datetimes`.

Чтобы не гадать в каждом месте, какие значения сравниваются, здесь определены
три функции:

* :func:`utcnow` — текущий момент в UTC без сведений о поясе. Используется как
  значение по умолчанию колонок и в арифметике над сохранёнными метками.
* :func:`as_utc` — приводит метку к «осознанному» UTC. Нужна при сравнении со
  значением из внешнего источника и при формировании ответа API.
* :func:`utcnow_iso` — текущий момент в формате ISO 8601 с явным указанием UTC.
"""
from __future__ import annotations

import datetime as dt

UTC = dt.timezone.utc


def utcnow() -> dt.datetime:
    """Текущий момент в UTC, «наивный»: в таком виде значения лежат в базе."""
    return dt.datetime.now(UTC).replace(tzinfo=None)


def as_utc(value: dt.datetime | None) -> dt.datetime | None:
    """Привести метку к «осознанному» UTC, не меняя момент времени.

    Наивное значение считается уже находящимся в UTC: именно так оно было
    записано функцией :func:`utcnow`.
    """
    if value is None:
        return None
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)


def utcnow_iso() -> str:
    """Текущий момент в ISO 8601 с явным суффиксом UTC — для ответов API."""
    return dt.datetime.now(UTC).isoformat()


def age_days(value: dt.datetime | None) -> float | None:
    """Возраст метки в сутках. None, если метка не задана."""
    if value is None:
        return None
    return (utcnow() - value).total_seconds() / 86400.0
