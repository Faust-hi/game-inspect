"""Exact legacy-field corrections; user-authored values are preserved."""

FIELD_CHANGES = {
    'flow_field_pathing': {
        'description': ('Вместо индивидуального пути для каждого агента строится векторное поле, общее для всей группы; стоимость не зависит от числа агентов.',
                        'Группа агентов использует общее поле направлений. Построение поля переиспользуется, но чтение поля, движение, локальное избегание и обновления по-прежнему требуют работы.'),
        'pros': (['Стоимость не зависит от числа агентов', 'Естественное поведение толпы'],
                 ['Переиспользование навигационного поля для общей цели', 'Не требуется отдельный глобальный поиск для каждого агента']),
    },
    'world_origin_shifting': {
        'pros': (['Устраняет артефакты точности', 'Обязательно для миров больше ~5 км'],
                 ['Может уменьшить ошибки координат вдали от начала', 'Применимость определяется единицами мира и требуемой точностью']),
    },
    'art_direction_stylization': {
        'summary': ('Художественный стиль снижает требования к fidelity: low-poly, плоское освещение и читаемые силуэты дают 60 FPS там, где реализм требует трассировки и 4K-текстур.',
                    'Технические ограничения геометрии, материалов и освещения согласуются с художественным стилем; стоимость определяется конкретным набором проходов и ассетов.'),
        'description': ('Архитектурное решение уровня концепции: вместо гонки за реализмом игра выбирает стилизацию (как Limbo, Torna Way и clean low-poly), и тогда не нужны ни тяжёлое освещение, ни плотная геометрия. Цена — сама концепция: решение определяет весь арт-пайплайн и не откатывается без пересоздания ассетов.',
                        'В расчёт входят выбранные технические бюджеты геометрии, текстур, материалов и освещения. Стилизация сама по себе не гарантирует дешёвый рендер; стоимость изменения зависит от переиспользуемых ассетов и проходов.'),
        'problem': ('Фотореализм требует железа, которого нет у целевой аудитории.',
                    'Нужно согласовать бюджеты контента и рендера с целевым оборудованием.'),
        'pros': (['Дешёвый рендер при выразительной картинке', 'Стабильный FPS на слабом железе'],
                 ['Позволяет заранее ограничить сложность контента', 'Можно сравнить варианты материалов и освещения прототипом']),
        'cons': (['Определяет всю игру', 'Поздняя смена — пересоздание ассетов'],
                 ['Ограничивает подготовку визуального контента', 'Смена ограничений может потребовать переработки части ассетов']),
    },
}

SOURCE_CHANGES = {
    'flow_field_pathing': ('WIKI_NAVMESH', 'GAME_AI_FLOW_FIELDS'),
    'art_direction_stylization': ('WIKI_IMPOSTOR', 'UNITY_GPU_BUDGETS'),
    'voxel_cone_tracing': ('WIKI_SVO', 'NVIDIA_VOXEL_CONES'),
}


def correct_record(record):
    for field, (old, new) in FIELD_CHANGES.get(record['code'], {}).items():
        if record.get(field) == old:
            record[field] = new.copy() if isinstance(new, list) else new
    change = SOURCE_CHANGES.get(record['code'])
    if change and record.get('source_key') == change[0]:
        record['source_key'] = change[1]


def correct_existing(db):
    from sqlalchemy import select
    from ..models.entities import Method
    from .sources import src

    changed = 0
    for code in sorted(set(FIELD_CHANGES) | set(SOURCE_CHANGES)):
        row = db.scalar(select(Method).where(Method.code == code))
        if row is None:
            continue
        for field, (old, new) in FIELD_CHANGES.get(code, {}).items():
            if getattr(row, field) == old:
                setattr(row, field, new.copy() if isinstance(new, list) else new)
                changed += 1
        if code in SOURCE_CHANGES:
            old, new = (src(key) for key in SOURCE_CHANGES[code])
            if (row.source_url, row.source_title, row.source_date) == (old['url'], old['title'], old['date']):
                row.source_url, row.source_title, row.source_date = new['url'], new['title'], new['date']
                changed += 1
    db.flush()
    return changed
