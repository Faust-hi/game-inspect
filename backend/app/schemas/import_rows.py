"""Типизированные схемы строк импорта каталога.

Файл приходит извне, поэтому каждая запись проверяется до записи в базу.
Раньше тип колонки определялся как `column.type.python_type`, но у JSON-колонок
SQLAlchemy это `dict`, а не `list`: проверка `python_type is list` не
срабатывала, и значение `"быстро;дёшево"` сохранялось строкой вместо списка.
Такой каталог ломает сериализацию публичных карточек и правила применимости.

Здесь тип каждой сущности описан явно. Схема не дублирует модель целиком: она
описывает то, что нужно проверить и преобразовать, а остальные колонки
пропускаются.
"""
from __future__ import annotations

from typing import ClassVar

from pydantic import BaseModel, ConfigDict, field_validator

#: Разделитель элементов списка в CSV. Точка с запятой выбрана потому, что
#: запятая уже занята как разделитель полей.
LIST_SEPARATOR = ";"


def as_str_list(value: object) -> object:
    """Приводит ячейку к списку строк: массив строк, строка с «;» или пусто.

    Элементы массива обязаны быть строками. Раньше произвольные значения
    молча превращались в строку через ``str()``: словарь
    ``{"bad": "structure"}`` сохранялся как ``"{'bad': 'structure'}"`` и
    выглядел корректной записью каталога. Такое преобразование скрывает
    ошибку источника, поэтому нестроковый элемент отклоняет всю строку.
    """
    if value is None:
        return None
    if isinstance(value, list):
        result: list[str] = []
        for item in value:
            if not isinstance(item, str):
                raise ValueError(
                    f"элемент списка должен быть строкой, получено {type(item).__name__}: {item!r}"
                )
            text = item.strip()
            if text:
                result.append(text)
        return result
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return []
        return [part.strip() for part in text.split(LIST_SEPARATOR) if part.strip()]
    raise ValueError("ожидался список либо строка с разделителем «;»")


class ImportRow(BaseModel):
    """База строки импорта: списки приводятся к типу до проверки."""

    model_config = ConfigDict(extra="ignore")

    #: Поля, которые в базе хранятся как JSON-массивы.
    LIST_FIELDS: ClassVar[tuple[str, ...]] = ()

    @field_validator("*", mode="before")
    @classmethod
    def _split_list_fields(cls, value: object, info) -> object:
        if info.field_name in cls.LIST_FIELDS:
            return as_str_list(value)
        return value

    @classmethod
    def key_of(cls, row: dict) -> str | None:
        """Ключ записи в файле. Пустой ключ — повод отклонить строку."""
        raise NotImplementedError


class MethodRow(ImportRow):
    LIST_FIELDS = (
        "pros", "cons", "limitations", "applicable_formats", "applicable_world_types",
        "applicable_engines", "applicable_platforms", "requires_features",
        "requires_hw_features", "requires_conditions", "verification_tools",
        "application_steps",
    )

    code: str | None = None
    pros: list[str] | None = None
    cons: list[str] | None = None
    limitations: list[str] | None = None
    applicable_formats: list[str] | None = None
    applicable_world_types: list[str] | None = None
    applicable_engines: list[str] | None = None
    applicable_platforms: list[str] | None = None
    requires_features: list[str] | None = None
    requires_hw_features: list[str] | None = None
    requires_conditions: list[str] | None = None
    verification_tools: list[str] | None = None
    application_steps: list[str] | None = None

    @classmethod
    def key_of(cls, row: dict) -> str | None:
        return str(row.get("code") or "").strip() or None


class GameFunctionRow(ImportRow):
    LIST_FIELDS = ("formats", "typical_world_types")

    code: str | None = None
    formats: list[str] | None = None
    typical_world_types: list[str] | None = None

    @classmethod
    def key_of(cls, row: dict) -> str | None:
        return str(row.get("code") or "").strip() or None


class EngineToolRow(ImportRow):
    code: str | None = None

    @classmethod
    def key_of(cls, row: dict) -> str | None:
        return str(row.get("code") or "").strip() or None


class HardwareCPURow(ImportRow):
    model: str | None = None
    single_thread_score: float | None = None
    multi_thread_score: float | None = None
    perf_class: int | None = None

    @classmethod
    def key_of(cls, row: dict) -> str | None:
        return str(row.get("model") or "").strip() or None


class HardwareGPURow(ImportRow):
    LIST_FIELDS = ("api_support", "hw_features")

    model: str | None = None
    api_support: list[str] | None = None
    hw_features: list[str] | None = None
    raster_score: float | None = None
    rt_score: float | None = None
    perf_class: int | None = None

    @classmethod
    def key_of(cls, row: dict) -> str | None:
        return str(row.get("model") or "").strip() or None


class ConflictRow(ImportRow):
    """Связь задаётся тройкой, а не одним кодом.

    У связи нет ни `code`, ни `model`, ни `title`: раньше ключ выбирался из
    этого списка и скатывался в `title`, которого у записи тоже нет. Строка
    отклонялась требованием несуществующего поля, а при его добавлении импорт
    падал с ошибкой 500.
    """

    a_code: str | None = None
    b_code: str | None = None
    conflict_type: str | None = None

    @classmethod
    def key_of(cls, row: dict) -> str | None:
        parts = (
            str(row.get("a_code") or "").strip(),
            str(row.get("b_code") or "").strip(),
            str(row.get("conflict_type") or "").strip(),
        )
        return " / ".join(parts) if all(parts) else None


ROW_SCHEMAS: dict[str, type[ImportRow]] = {
    "methods": MethodRow,
    "game_functions": GameFunctionRow,
    "engine_tools": EngineToolRow,
    "hardware_cpu": HardwareCPURow,
    "hardware_gpu": HardwareGPURow,
    "conflicts": ConflictRow,
}

#: Поля составного ключа связи — по ним ищется существующая запись.
CONFLICT_KEY_FIELDS = ("a_code", "b_code", "conflict_type")


def row_key(entity: str, row: dict) -> str | None:
    """Ключ строки файла: для связей составной, для остальных — одиночный."""
    schema = ROW_SCHEMAS.get(entity)
    if schema is None:
        return None
    return schema.key_of(row)


def list_columns(entity: str) -> frozenset[str]:
    """Имена колонок, которые в базе хранятся как JSON-массивы."""
    schema = ROW_SCHEMAS.get(entity)
    return frozenset(schema.LIST_FIELDS) if schema else frozenset()


def normalize_row(entity: str, row: dict) -> dict:
    """Проверить строку по схеме и вернуть нормализованные значения.

    Возвращает только реально переданные поля: пустая ячейка CSV означает
    «не задано», а не пустой список или ноль.
    """
    schema = ROW_SCHEMAS.get(entity)
    if schema is None:
        return {}
    validated = schema.model_validate(row)
    return {
        name: value for name, value in validated.model_dump().items()
        if name in row and value is not None
    }
