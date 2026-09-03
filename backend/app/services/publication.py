"""Политика публикации базы знаний.

Здесь собраны правила, которыми раньше управлял каждый маршрут по-своему:
какие переходы статуса допустимы, что обязана содержать публикуемая запись и
в каких диапазонах должны лежать числовые оценки.

Правила вынесены в отдельный модуль, потому что проверять их нужно в трёх
местах сразу: при создании записи, при импорте и при смене статуса. Когда
проверка живёт в обработчике, она неизбежно в одном из мест отсутствует.
"""
from __future__ import annotations

import re
from typing import Any, Iterable

from ..models.enums import (
    CalcMode, ConflictType, DevStage, GameFormat, LateCost, Level3, MethodKind,
    Platform, Scale, SolutionLevel, Status, WorldType,
)

# Разрешённые переходы жизненного цикла. Обратный переход с «опубликовано»
# означает снятие с публикации, а не возврат в черновик.
ALLOWED_TRANSITIONS: dict[str, set[str]] = {
    Status.DRAFT.value: {Status.REVIEWED.value},
    Status.REVIEWED.value: {Status.PUBLISHED.value, Status.DRAFT.value},
    Status.PUBLISHED.value: {Status.REVIEWED.value},
}

#: Диапазоны числовых полей. За их пределами оценка перестаёт быть сравнимой
#: с остальными записями и искажает ранжирование TOPSIS.
NUMERIC_RANGES: dict[str, tuple[float, float]] = {
    "performance_gain": (0.0, 1.0),
    "confidence": (0.0, 1.0),
    "implementation_cost": (1, 5),
    "complexity": (1, 5),
    "severity": (1, 3),
    "single_thread_score": (0.0, 1.0),
    "multi_thread_score": (0.0, 1.0),
    "raster_score": (0.0, 1.0),
    "rt_score": (0.0, 1.0),
    "perf_class": (1, 5),
    "quality_impact": (-2, 2),
    "concept_impact": (-2, 0),
    **{f"impact_{key}": (-3, 3)
       for key in ("cpu", "gpu", "ram", "vram", "disk", "network")},
}

#: Справочные поля и перечисления, которым значение должно соответствовать.
ENUM_FIELDS: dict[str, tuple] = {
    "status": Status,
    "level": SolutionLevel,
    "recommended_stage": DevStage,
    "late_cost": LateCost,
    "calc_mode": CalcMode,
    "kind": MethodKind,
    "conflict_type": ConflictType,
    "min_scale": Scale,
    "format": GameFormat,
    "world_type": WorldType,
    "scale": Scale,
    "object_count_level": Level3,
    "npc_count_level": Level3,
}

_URL_RE = re.compile(r"^https?://", re.IGNORECASE)


def is_valid_url(value: str) -> bool:
    """Допустимы только http и https: остальные схемы не являются источником."""
    return bool(value) and bool(_URL_RE.match(value.strip()))


def allowed_targets(current: str | None) -> set[str]:
    return set(ALLOWED_TRANSITIONS.get(current or Status.DRAFT.value, set()))


def can_transition(current: str | None, target: str) -> bool:
    return target in allowed_targets(current)


def transition_error(current: str | None, target: str) -> str | None:
    """Текст отказа на недопустимый переход либо None, если переход разрешён."""
    current = current or Status.DRAFT.value
    if target not in {s.value for s in Status}:
        return f"Недопустимый статус: {target}"
    if target == current:
        return f"Запись уже находится в статусе «{_status_label(target)}»"
    if not can_transition(current, target):
        allowed = ", ".join(sorted(_status_label(s) for s in allowed_targets(current)))
        return (
            f"Переход «{_status_label(current)}» → «{_status_label(target)}» запрещён. "
            f"Из статуса «{_status_label(current)}» допустимо: {allowed}."
        )
    return None


def _status_label(value: str) -> str:
    try:
        return Status(value).label
    except ValueError:
        return value


def enum_problems(data: dict[str, Any]) -> list[str]:
    """Проверка справочных полей и числовых диапазонов словаря полей."""
    problems: list[str] = []

    for field, (low, high) in NUMERIC_RANGES.items():
        if field not in data or data[field] is None:
            continue
        value = data[field]
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            problems.append(f"Поле «{field}» должно быть числом, получено {value!r}.")
            continue
        if not (low <= float(value) <= high):
            problems.append(f"Поле «{field}» вне диапазона {low}..{high}: {value}.")

    for field, enum_cls in ENUM_FIELDS.items():
        if field not in data or data[field] in (None, ""):
            continue
        allowed = {item.value for item in enum_cls}
        if data[field] not in allowed:
            problems.append(
                f"Поле «{field}» имеет недопустимое значение «{data[field]}». "
                f"Допустимо: {', '.join(sorted(allowed))}."
            )

    for field in ("platforms", "applicable_platforms"):
        if field in data and data[field]:
            allowed = {item.value for item in Platform}
            unknown = [p for p in data[field] if p not in allowed]
            if unknown:
                problems.append(f"Поле «{field}» содержит неизвестные платформы: {', '.join(map(str, unknown))}.")

    for field in ("source_url", "docs_url"):
        if field in data and data[field]:
            if not is_valid_url(str(data[field])):
                problems.append(f"Поле «{field}» должно быть ссылкой http(s): {data[field]}")

    return problems


def record_problems(model, data: dict[str, Any]) -> list[str]:
    """Проверка словаря полей, поступающего из импорта или административного API.

    Функция не обращается к базе: она проверяет только саму запись. Проверки
    целостности ссылок выполняет :func:`publication_problems`.
    """
    problems = enum_problems(data)

    # Импорт не должен задавать статус публикации напрямую: это нарушает
    # жизненный цикл и немедленно открывает запись в публичных каталогах.
    if data.get("status") == Status.PUBLISHED.value:
        problems.append(
            "Импорт не может создавать опубликованные записи: "
            "публикация выполняется отдельным переходом после проверки."
        )
    return problems


def publication_problems(obj: Any, *, has_links: bool = True) -> list[str]:
    """Проверки, обязательные для перевода записи в статус «опубликовано»."""
    problems: list[str] = []

    if not (getattr(obj, "source_url", "") or "").strip():
        problems.append("Отсутствует ссылка на источник: без неё запись нельзя публиковать.")
    elif not is_valid_url(obj.source_url):
        problems.append("Ссылка на источник должна начинаться с http:// или https://.")

    if not (getattr(obj, "source_title", "") or "").strip():
        problems.append("Отсутствует название источника.")

    if not (getattr(obj, "name", "") or getattr(obj, "title", "") or "").strip():
        problems.append("Не заполнено название записи.")

    problems.extend(enum_problems(_columns_of(obj)))

    # Метод без привязки к движку бесполезен: пользователь не узнает, чем его
    # реализовать в своём проекте.
    if getattr(obj, "__tablename__", "") == "methods" and not has_links:
        problems.append("У метода нет ни одной связи с инструментом движка.")

    return problems


def _columns_of(obj: Any) -> dict[str, Any]:
    return {c.name: getattr(obj, c.name) for c in obj.__table__.columns}


def describe_transition(obj: Any, target: str, *, actor: str = "admin") -> dict[str, Any]:
    """Описание перехода для журнала публикаций."""
    return {
        "entity": getattr(obj, "__tablename__", type(obj).__name__),
        "entity_code": _entity_code(obj),
        "from_status": getattr(obj, "status", Status.DRAFT.value),
        "to_status": target,
        "actor": actor,
    }


def _entity_code(obj: Any) -> str:
    for field in ("code", "model", "title"):
        value = getattr(obj, field, None)
        if value:
            return str(value)
    return str(getattr(obj, "id", ""))


def deduplicate(problems: Iterable[str]) -> list[str]:
    """Убирает повторы, сохраняя порядок: одна и та же ошибка не дублируется."""
    seen: set[str] = set()
    result: list[str] = []
    for problem in problems:
        if problem not in seen:
            seen.add(problem)
            result.append(problem)
    return result
