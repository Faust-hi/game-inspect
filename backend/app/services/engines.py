"""Движок проекта как выбор из каталога, а не из перечисления в схеме.

Раньше допустимые коды движков были зашиты в схему анкеты перечислением. Из-за
этого движок, добавленный администратором через каталог, отклонялся ещё до
обращения к базе, и обещание «расширять базу знаний без изменения кода»
не выполнялось: новому движку требовалась правка исходников.

Проверка перенесена в слой, где видно фактическое наполнение базы. Прежний
набор кодов остаётся допустимым: все они есть в демонстрационном наполнении,
а при пустом каталоге служат резервным перечнем — иначе приложение нельзя
использовать до первого заполнения.
"""
from __future__ import annotations

import re

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..errors import ApiError, ErrorCode
from ..models.entities import EngineTool
from ..models.enums import EngineCode
from ..repositories import engines as published_engines

#: Число в начале строки версии: «5.0», «4.27», «2022 LTS» → (5, 0), (4, 27),
#: (2022,). Номер ищется только в начале: у «Source 2» или «V (5.x)» цифра не
#: является номером версии, и извлекать её из середины строки было бы
#: случайным совпадением, а не сравнением версий.
_NUMBER_PREFIX = re.compile(r"^\s*(?:v|ver\.?)?\s*(\d+(?:\.\d+)*)", re.IGNORECASE)


def version_key(version: str | None) -> tuple[int, ...] | None:
    """Числовой ключ версии для сравнения.

    Версии движков — строки одной и той же схемы внутри движка («4.27», «5.0»),
    поэтому сравнивается числовой префикс. Если номер извлечь не удалось
    («Source 2», «любая»), возвращается None: сравнение невозможно, и это не
    основание ни объявлять инструмент доступным, ни объявлять его отсутствующим.
    """
    if not version:
        return None
    match = _NUMBER_PREFIX.match(str(version))
    if not match:
        return None
    try:
        return tuple(int(part) for part in match.group(1).split("."))
    except ValueError:
        return None


def version_at_least(actual: str | None, required: str | None) -> bool | None:
    """Доступна ли версия `actual`, если инструмент требует `required`.

    True — версия не ниже требуемой, False — ниже, None — сравнить нельзя.
    """
    left, right = version_key(actual), version_key(required)
    if left is None or right is None:
        return None
    return left >= right


def tool_available_in(tool: EngineTool, engine_code: str | None, engine_version: str | None) -> bool | None:
    """Проверить, существует ли встроенный инструмент в указанной версии движка.

    None означает, что ответить нельзя: версия не задана, инструмент относится
    к другому движку или граница версии не заполнена. Неопределённость не
    приравнивается к доступности — вызывающая сторона обязана показать её.
    """
    engine = getattr(tool, "engine", None)
    if engine is not None and engine_code and engine.code != engine_code:
        return None
    required = getattr(tool, "min_version", None)
    if not required:
        return None
    if not engine_version:
        return None
    return version_at_least(engine_version, required)


def unavailable_tools(db: Session, engine_code: str | None, engine_version: str | None) -> dict[str, str]:
    """Инструменты выбранного движка, недоступные в указанной версии.

    Возвращает `код инструмента → пояснение`. Инструменты без заданной границы
    версии и без указанной версии движка в расчёт не попадают: отсутствие
    данных не означает подтверждённую доступность, но и не даёт основания
    исключать инструмент.
    """
    if not engine_code or not engine_version:
        return {}
    result: dict[str, str] = {}
    for tool in db.scalars(select(EngineTool).where(EngineTool.status == "published")):
        if tool_available_in(tool, engine_code, engine_version) is False:
            result[tool.code] = (
                f"Встроенный инструмент «{tool.name}» доступен с версии "
                f"{tool.min_version}, а в проекте указана {engine_version}."
            )
    return result


def method_version_notes(db: Session, profile, methods) -> list[str]:
    """Выбранные решения, чей встроенный аналог отсутствует в версии движка.

    Показывать Nanite доступным для UE 4.27 нельзя: в этой версии встроенной
    подсистемы нет, и решение превращается в собственную реализацию с другой
    стоимостью внедрения. Физическая модель метода при этом не меняется —
    меняется цена и способ получения эффекта, поэтому решение не удаляется из
    расчёта, а сопровождается явным пояснением.
    """
    engine_code = getattr(profile, "engine", None)
    engine_version = getattr(profile, "engine_version", None)
    unavailable = unavailable_tools(db, engine_code, engine_version)
    if not unavailable:
        return []
    from ..repositories import method_links

    notes: set[str] = set()
    for method in methods:
        for link in method_links(db, method.id):
            tool = getattr(link, "tool", None)
            note = unavailable.get(tool.code) if tool is not None else None
            if note:
                notes.add(f"«{method.name}»: {note}")
    return sorted(notes)


def known_codes(db: Session) -> list[str]:
    """Коды движков, доступные для выбора в анкете."""
    codes = [engine.code for engine in published_engines(db)]
    if codes:
        return codes
    return [item.value for item in EngineCode]


def require_known(db: Session, code: str) -> None:
    """Отклонить движок, которого нет в каталоге.

    Неизвестный код — не повод молча продолжать расчёт: у такого движка нет
    ни инструментов, ни проверенных связей, и объяснения решений оказались бы
    пустыми, а отсутствие запрета выглядело бы как подтверждённая поддержка.
    """
    codes = known_codes(db)
    if code in codes:
        return
    raise ApiError(
        f"Движок «{code}» отсутствует в каталоге",
        code=ErrorCode.VALIDATION,
        status=422,
        details=[
            f"Допустимые коды движков: {', '.join(codes)}.",
            "Новый движок добавляется через административный раздел каталога.",
        ],
    )
