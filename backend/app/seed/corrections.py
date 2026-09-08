"""Точечные исправления известных исходных записей с сохранением ручных правок."""
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models.entities import Conflict, Method
from . import methods_data


def correct_shadow_relation(db: Session) -> int:
    """Заменить только точную устаревшую запись штатного каталога."""
    # Старый формат: conflict_type="conflict" → новый: hard_conflict
    # Правильный тип для синергии теней: complement (было synergy)
    old_hard_conflict = {
        "a_code": "cascaded_shadow_maps",
        "b_code": "distance_field_shadows",
        "conflict_type": "hard_conflict",
        "severity": 1,
        "description": "Два механизма теней для направленного света дублируют стоимость и дают непредсказуемое наложение результатов.",
        "resolution": "Выбрать одну систему теней как основную.",
        "source_url": "https://en.wikipedia.org/wiki/Shadow_mapping",
        "status": "published",
    }
    # Также проверяем старый тип "conflict" для совместимости с устаревшими базами
    old_conflict = {**old_hard_conflict, "conflict_type": "conflict"}
    
    row = db.scalar(select(Conflict).where(*[
        getattr(Conflict, key) == value for key, value in old_hard_conflict.items()
    ]))
    if row is None:
        # Проверяем старый формат
        row = db.scalar(select(Conflict).where(*[
            getattr(Conflict, key) == value for key, value in old_conflict.items()
        ]))
    if row is None:
        return 0
    # Если уже правильно задано complement (было synergy) — не трогаем
    existing = db.scalar(select(Conflict).where(
        Conflict.a_code == old_hard_conflict["a_code"], Conflict.b_code == old_hard_conflict["b_code"],
        Conflict.conflict_type == "complement",
    ))
    if existing is not None:
        return 0
    _, relations = methods_data.with_sources()
    # В methods_data теперь должен быть complement вместо synergy
    replacement = next(item for item in relations if item["a_code"] == old_hard_conflict["a_code"]
                       and item["b_code"] == old_hard_conflict["b_code"] and item["conflict_type"] == "complement")
    for key, value in replacement.items():
        if hasattr(Conflict, key):
            setattr(row, key, value)
    db.flush()
    return 1


#: Устаревшие значения `conflict_type`, которые встречаются в базах, созданных
#: до разделения связей на типы. Код обрабатывает только значения перечисления
#: `ConflictType`, поэтому старые записи не исключали методы и не давали
#: предупреждений — связь существовала в базе, но ни на что не влияла.
LEGACY_CONFLICT_TYPES = {
    "conflict": "hard_conflict",   # был единственный тип запрета
    "synergy": "complement",       # синергия, в новом формате — complement
}


def correct_legacy_conflict_types(db: Session) -> int:
    """Привести устаревшие типы связей к значениям перечисления.

    Исправление общее, а не точечное: в отличие от `correct_shadow_relation`
    оно не может сослаться на одну известную запись, потому что устаревшие
    значения мог получить любой конфликт. Меняются только те строки, у которых
    тип заведомо не входит в перечисление, — осознанная правка администратора
    с корректным типом не трогается.
    """
    updated = 0
    for legacy, actual in LEGACY_CONFLICT_TYPES.items():
        rows = list(db.scalars(select(Conflict).where(Conflict.conflict_type == legacy)))
        for row in rows:
            row.conflict_type = actual
            updated += 1
    if updated:
        db.flush()
    return updated


def correct_splitscreen_dependency(db: Session) -> int:
    """Убрать ложную зависимость split-screen от сетевого кода (D42).

    Split-screen — локальная функция: два вьюпорта на одной машине, сетевой
    код для неё не нужен. Прежняя запись требовала `multiplayer_netcode` и
    исключала решение из одиночных кооп-проектов. Заменяется только точное
    унаследованное значение: осознанная правка администратора не трогается.
    """
    row = db.scalar(select(Method).where(Method.code == "splitscreen_render_budget"))
    if row is None or list(row.requires_features or []) != ["multiplayer_netcode"]:
        return 0
    row.requires_features = ["split_screen_rendering"]
    db.flush()
    return 1


def correct_effect_scopes(db: Session) -> int:
    """Проставить область эффекта записям, созданным до появления поля.

    Область задавалась неявно: все решения считались влияющими на компьютер
    игрока, из-за чего серверная экономия уменьшала требования к клиенту.
    Явные значения каталога нужно донести и до уже существующих баз, иначе
    исправление расчёта подействует только на новые установки.

    Значение, отличное от прежнего неявного `client`, не трогается: это
    осознанная правка администратора, а не унаследованное умолчание.
    """
    methods, _relations = methods_data.with_sources()
    declared = {
        item["code"]: item["effect_scope"]
        for item in methods
        if item.get("effect_scope") not in (None, "client")
    }
    updated = 0
    for code, scope in declared.items():
        row = db.scalar(select(Method).where(Method.code == code))
        if row is not None and row.effect_scope == "client":
            row.effect_scope = scope
            updated += 1
    if updated:
        db.flush()
    return updated
