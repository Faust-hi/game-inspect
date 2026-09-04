"""Единые правила работы с метками времени.

Колонки объявлены как `DateTime` без сведений о часовом поясе, поэтому SQLite
при чтении отдаёт «наивное» значение: попытка вычесть его из
`datetime.now(timezone.utc)` приводит к
`TypeError: can't subtract offset-naive and offset-aware datetimes`.

Здесь две функции: `utcnow` — значение для записи в базу, `utcnow_iso` —
метка времени расчёта для ответа API.
"""
from __future__ import annotations

import datetime as dt

UTC = dt.timezone.utc


def utcnow() -> dt.datetime:
    """Текущий момент в UTC, «наивный»: в таком виде значения лежат в базе."""
    return dt.datetime.now(UTC).replace(tzinfo=None)


def utcnow_iso() -> str:
    """Текущий момент в ISO 8601 с явным суффиксом UTC — для ответов API."""
    return dt.datetime.now(UTC).isoformat()
