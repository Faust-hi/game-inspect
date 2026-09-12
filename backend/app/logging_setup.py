"""Настройка журналирования для локального запуска (текстовый формат)."""
from __future__ import annotations

import logging
import sys

from .config import settings


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
    handler.setFormatter(TextFormatter())
    root.addHandler(handler)
    root.setLevel(settings.LOG_LEVEL.upper())

    # Шумные библиотеки: оставляем только предупреждения и выше.
    for name in ("uvicorn.access", "sqlalchemy.engine", "watchfiles"):
        logging.getLogger(name).setLevel(logging.WARNING)
