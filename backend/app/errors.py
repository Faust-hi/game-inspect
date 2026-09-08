"""Единый контракт ошибок API.

Раньше формат ошибки зависел от ветки: проверка схемы возвращала строку в
`error` и список в `details`, административные маршруты передавали словарь
вместо строки, а идентификатор запроса в теле оставался `null`, хотя заголовок
его содержал. Клиент разбирал только строковый `error`, поэтому причина
импорта или публикации заменялась безликим «Ошибка 422».

Здесь задаётся один формат для всех ветвей:

    {
        "error": "<понятное сообщение>",   # строка, а не объект
        "code": "<машинный код>",          # для обработки в коде
        "details": [...],                  # подробности по полям/записям
        "request_id": "<непустой>"         # совпадает с заголовком и журналом
    }
"""
from __future__ import annotations

from enum import Enum


class ErrorCode(str, Enum):
    """Машинные коды ошибок: по ним клиент различает причины, а не по тексту."""

    VALIDATION = "validation_error"
    NOT_FOUND = "not_found"
    CONFLICT = "conflict"
    PUBLICATION_REJECTED = "publication_rejected"
    UNSUPPORTED = "unsupported"
    INTERNAL = "internal_error"


#: Код по умолчанию для каждой группы ответов: сообщения не всегда известны
#: заранее, а клиенту всё равно нужен различимый код.
_CODE_BY_STATUS: dict[int, ErrorCode] = {
    400: ErrorCode.VALIDATION,
    404: ErrorCode.NOT_FOUND,
    409: ErrorCode.CONFLICT,
    422: ErrorCode.VALIDATION,
    500: ErrorCode.INTERNAL,
}


def code_for_status(status: int) -> ErrorCode:
    """Код ошибки по HTTP-статусу для исключений без явного кода."""
    return _CODE_BY_STATUS.get(status, ErrorCode.INTERNAL)


class ApiError(Exception):
    """Ошибка с машинным кодом, сообщением и подробностями.

    Используется там, где недостаточно одного текстового `detail`: например
    при отклонении записи каталога, когда клиенту нужен и смысл, и список
    конкретных нарушенных полей.
    """

    def __init__(
        self,
        message: str,
        *,
        code: ErrorCode,
        status: int = 400,
        details: list | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.code = code
        self.status = status
        self.details = details or []


def error_payload(
    message: str,
    *,
    code: ErrorCode | str,
    request_id: str,
    details: list | None = None,
) -> dict:
    """Тело ответа об ошибке в едином формате."""
    return {
        "error": message,
        "code": code.value if isinstance(code, Enum) else code,
        "details": details or [],
        "request_id": request_id,
    }
