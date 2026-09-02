"""Механизмы защиты: проверка токена и ограничение частоты запросов.

Ограничение частоты реализовано в памяти процесса. Этого достаточно для одного
экземпляра сервиса; при развёртывании нескольких копий за балансировщиком
ограничение нужно выносить в общее хранилище (Redis) или на уровень прокси.
"""
from __future__ import annotations

import hmac
import logging
import threading
import time
from collections import defaultdict, deque

from fastapi import HTTPException, Request

from ..config import settings

logger = logging.getLogger("gamedev_dss.security")


def token_matches(provided: str | None) -> bool:
    """Сравнивает переданный токен с настроенным за одинаковое время.

    Обычное сравнение строк завершается на первом несовпавшем символе и по времени
    выполнения выдаёт длину совпавшего префикса. hmac.compare_digest такого не делает.
    """
    expected = settings.ADMIN_TOKEN or ""
    if not provided:
        # Сравниваем всё равно, чтобы время ответа не зависело от наличия заголовка.
        return hmac.compare_digest("", expected) and False
    return hmac.compare_digest(provided, expected)


class SlidingWindowLimiter:
    """Счётчик запросов по скользящему окну для каждого ключа."""

    def __init__(self) -> None:
        self._events: dict[str, deque[float]] = defaultdict(deque)
        self._lock = threading.Lock()
        self._max_keys = 10_000

    def _purge(self, key: str, now: float, window: float) -> None:
        events = self._events.get(key)
        if events is None:
            return
        while events and now - events[0] > window:
            events.popleft()
        if not events:
            self._events.pop(key, None)

    def check(self, key: str, limit: int, window: float = 60.0) -> tuple[bool, int]:
        """Возвращает (допустимо ли, сколько запросов осталось)."""
        if limit <= 0:
            return True, limit
        now = time.monotonic()
        with self._lock:
            if len(self._events) >= self._max_keys:
                # Защита от неограниченного роста памяти при большом числе адресов.
                for stale in [k for k, v in self._events.items() if not v]:
                    self._events.pop(stale, None)
                if len(self._events) >= self._max_keys:
                    self._events.clear()
            self._purge(key, now, window)
            events = self._events[key]
            if len(events) >= limit:
                return False, 0
            events.append(now)
            return True, limit - len(events)

    def reset(self) -> None:
        with self._lock:
            self._events.clear()


limiter = SlidingWindowLimiter()


def client_key(request: Request) -> str:
    """Ключ ограничения: адрес клиента с учётом стандартного заголовка прокси."""
    forwarded = request.headers.get("x-forwarded-for", "")
    if forwarded:
        # Берём первый адрес — исходный клиент; остальные добавляют прокси.
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def enforce_rate_limit(request: Request, limit: int, scope: str) -> None:
    """Вызывает 429, если клиент превысил лимит запросов в минуту."""
    if not settings.RATE_LIMIT_ENABLED or limit <= 0:
        return
    allowed, remaining = limiter.check(f"{scope}:{client_key(request)}", limit)
    if allowed:
        return
    logger.warning("Превышен лимит запросов: scope=%s client=%s", scope, client_key(request))
    raise HTTPException(
        status_code=429,
        detail="Слишком много запросов. Повторите попытку позже.",
        headers={"Retry-After": "60"},
    )
