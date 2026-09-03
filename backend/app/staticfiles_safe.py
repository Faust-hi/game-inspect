"""Безопасная раздача файлов собранного frontend.

Проблема, которую решает модуль: путь из URL нельзя передавать в конструктор
``Path`` и проверять только ``is_file()``. На Windows операция
``root / "C:\\secret"`` отбрасывает корень и возвращает абсолютный путь, а
``root / "../backend/gamedev_dss.db"`` выходит за пределы каталога сборки.
Кроме того, сегмент ``..`` может прийти в URL-encoded (``%2e%2e%2f``) и
double-encoded (``%252e%252e%252f``) виде.

Правило простое: сначала путь отвергается по признакам, несовместимым с именем
файла внутри каталога сборки, затем он склеивается с корнем, приводится к
каноническому виду и проверяется на вложенность в корень. Любое сомнение
трактуется как «файла нет».
"""
from __future__ import annotations

import os
import pathlib
import posixpath
import unicodedata
from urllib.parse import unquote

#: Расширения, которые допустимо отдавать как статические файлы.
ALLOWED_SUFFIXES = frozenset({
    ".html", ".htm", ".js", ".mjs", ".css", ".map", ".json", ".txt", ".webmanifest",
    ".ico", ".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".avif", ".woff",
    ".woff2", ".ttf", ".otf", ".eot", ".mp3", ".wav", ".ogg", ".mp4", ".webm",
})

#: Подкаталоги каталога сборки, из которых файлы отдаются без ограничения по расширению.
ALLOWED_DIRS = frozenset({"assets"})


def _reject_reason(raw_path: str) -> str | None:
    """Возвращает причину отказа, если путь заведомо непригоден."""
    if raw_path is None:
        return "пустой путь"
    if len(raw_path) > 512:
        return "слишком длинный путь"
    # Управляющие символы и нулевой байт не могут быть частью имени файла.
    if any(ord(ch) < 32 or ord(ch) == 127 for ch in raw_path):
        return "управляющие символы в пути"
    # Обратная косая черта — разделитель Windows и одновременно допустимый
    # символ имени в POSIX: единого толкования нет, поэтому путь отвергается.
    if "\\" in raw_path:
        return "обратная косая черта в пути"
    # Абсолютный путь (POSIX- или Windows-формы) отбрасывает корень сборки.
    if raw_path.startswith("/") or (len(raw_path) >= 2 and raw_path[1] == ":"):
        return "абсолютный путь"
    # Оставшиеся после однократного декодирования процентные последовательности
    # означают двойное кодирование: скрытый сегмент может появиться позже.
    if "%" in raw_path:
        return "процентное кодирование в пути"
    return None


def safe_static_path(root: pathlib.Path, raw_path: str) -> pathlib.Path | None:
    """Преобразует путь из URL в путь к файлу внутри каталога сборки.

    Возвращает ``None``, если путь выходит за пределы ``root``, указывает на
    каталог, содержит запрещённые элементы или расширение файла не разрешено.
    Вызывающая сторона при ``None`` должна отдать ``index.html``.
    """
    if not raw_path:
        return None

    reason = _reject_reason(raw_path)
    if reason is not None:
        return None

    # Путь мог прийти уже декодированным сервером или закодированным вручную.
    decoded = unquote(raw_path)
    reason = _reject_reason(decoded)
    if reason is not None:
        return None

    if unicodedata.normalize("NFC", decoded) != decoded:
        # Ненормализованные последовательности могут скрывать разделители.
        decoded = unicodedata.normalize("NFC", decoded)

    # Приводим к POSIX-виду и убираем '.' и пустые сегменты.
    normalized = posixpath.normpath(decoded).lstrip("/")
    if not normalized or normalized == ".":
        return None

    parts = [part for part in normalized.split("/") if part not in ("", ".")]
    if not parts:
        return None
    if any(part == ".." for part in parts):
        return None

    candidate = (root / pathlib.PurePosixPath(*parts)).resolve()
    root_resolved = root.resolve()
    if candidate == root_resolved or not _is_within(candidate, root_resolved):
        return None
    if not candidate.is_file():
        return None

    # Для файлов вне служебных каталогов проверяем расширение: это исключает
    # выдачу случайно попавших в сборку .env, .db и .py.
    relative = candidate.relative_to(root_resolved)
    if relative.parts[0] not in ALLOWED_DIRS and candidate.suffix.lower() not in ALLOWED_SUFFIXES:
        return None
    return candidate


def _is_within(candidate: pathlib.Path, root: pathlib.Path) -> bool:
    """Проверяет вложенность с учётом регистра файловой системы Windows."""
    try:
        candidate.relative_to(root)
        return True
    except ValueError:
        pass
    if os.name == "nt":
        # Windows не различает регистр: сравниваем приведённые строки.
        candidate_str = str(candidate).lower()
        root_str = str(root).rstrip("\\/").lower() + os.sep
        return candidate_str.startswith(root_str)
    return False
