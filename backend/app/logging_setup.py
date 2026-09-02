"""Настройка журналирования.

Поддерживаются два формата:
  * текстовый — для локальной разработки;
  * JSON — для сбора логов внешними системами (LOG_JSON=true).
"""
from __future__ import annotations

import json
import logging
import sys
from datetime import datetime, timezone

from .config import settings


class JsonFormatter(logging.Formatter):
    """Однострочный JSON: каждая запись — отдельная строка, пригодная для парсинга."""

    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        extra = getattr(record, "extra_fields", None)
        if isinstance(extra, dict):
            payload.update(extra)
        return json.dumps(payload, ensure_ascii=False)


class TextFormatter(logging.Formatter):
    def __init__(self) -> None:
        super().__init__("%(asctime)s %(levelname)-8s %(name)-24s %(message)s", datefmt="%Y-%m-%d %H:%M:%S")


def configure_logging(force: bool = False) -> None:
    """Настраивает корневой логгер приложения. Повторный вызов безопасен."""
    root = logging.getLogger()
    if root.handlers and not force:
        return

    if force:
        for handler in list(root.handlers):
            root.removeHandler(handler)

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter() if settings.LOG_JSON else TextFormatter())
    root.addHandler(handler)
    root.setLevel(settings.LOG_LEVEL.upper())

    # Шумные библиотеки: оставляем только предупреждения и выше.
    for name in ("uvicorn.access", "sqlalchemy.engine", "watchfiles"):
        logging.getLogger(name).setLevel(logging.WARNING)


def log_event(logger: logging.Logger, level: int, message: str, **fields) -> None:
    """Пишет запись с дополнительными полями (попадают в JSON-вывод)."""
    logger.log(level, message, extra={"extra_fields": fields or None})
