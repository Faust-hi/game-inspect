"""Точечные исправления известных исходных записей с сохранением ручных правок."""
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models.entities import Conflict
from . import methods_data


def correct_shadow_relation(db: Session) -> int:
    """Заменить только точную устаревшую запись штатного каталога."""
    old = {
        "a_code": "cascaded_shadow_maps",
        "b_code": "distance_field_shadows",
        "conflict_type": "conflict",
        "severity": 1,
        "description": "Два механизма теней для направленного света дублируют стоимость и дают непредсказуемое наложение результатов.",
        "resolution": "Выбрать одну систему теней как основную.",
        "source_url": "https://en.wikipedia.org/wiki/Shadow_mapping",
        "status": "published",
    }
    row = db.scalar(select(Conflict).where(*[
        getattr(Conflict, key) == value for key, value in old.items()
    ]))
    if row is None:
        return 0
    existing = db.scalar(select(Conflict).where(
        Conflict.a_code == old["a_code"], Conflict.b_code == old["b_code"],
        Conflict.conflict_type == "synergy",
    ))
    if existing is not None:
        # Два варианта требуют ручного решения; ничего не удаляем и не затираем.
        return 0
    _, relations = methods_data.with_sources()
    replacement = next(item for item in relations if item["a_code"] == old["a_code"]
                       and item["b_code"] == old["b_code"] and item["conflict_type"] == "synergy")
    for key, value in replacement.items():
        if hasattr(Conflict, key):
            setattr(row, key, value)
    db.flush()
    return 1
