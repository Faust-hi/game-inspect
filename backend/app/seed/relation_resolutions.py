"""Решение / workaround для связей каталога.

Спецификация (стр. 142) требует у каждой связи технологического графа
«решение или workaround». Паки описывают связь только полем `note`: почему она
существует, но не что с ней делать. Из-за этого блок «Что делать» в карточке
конфликта оставался пустым у 88 % связей.

Решение выводится детерминированно из семантики типа связи и имён методов: это
действие, однозначно следующее из самого отношения — жёсткий конфликт нельзя
совместить, дополнение не даёт численного бонуса без отдельного измерения,
непроверенная связь требует собственного замера. Ничего не выдумывается:
причина связи остаётся в `description` рядом с решением, а основание пишется в
`basis`, чтобы выведенное решение нельзя было принять за документированное.

Модуль идемпотентен и не затирает уже заполненные решения (курируемые значения
каталога и текст понижения цикла сохраняются).
"""
from __future__ import annotations

import logging

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models.entities import (
    Conflict, DependencyEdge, EngineTool, Method, TechnologyNode,
)
from ..models.enums import ConflictType

logger = logging.getLogger("gamedev_dss.seed.resolutions")

#: Действие по типу связи. «{a}» и «{b}» — имена методов.
_ACTIONS: dict[str, str] = {
    ConflictType.HARD_CONFLICT.value: (
        "Оставить один механизм — «{a}» или «{b}» — как основной и исключить "
        "второй из рабочей корзины: совместное применение несовместимо."
    ),
    ConflictType.RISK.value: (
        "Снять риск совместного применения «{a}» и «{b}»: проверить условие из "
        "описания связи и подтвердить результат замером до интеграции."
    ),
    ConflictType.ALTERNATIVE.value: (
        "Выбрать «{a}» или «{b}» по условиям проекта; одновременно оба не "
        "включать — это взаимозаменяемые решения одной задачи."
    ),
    ConflictType.DEPENDENCY.value: (
        "Сохранять оба: «{a}» требует «{b}». Сначала внедряется зависимость, "
        "иначе эффект «{a}» не учитывается в расчёте."
    ),
    ConflictType.COMPLEMENT.value: (
        "Применять «{a}» и «{b}» совместно и измерить совместный эффект "
        "отдельно: дополнение не даёт автоматического численного бонуса."
    ),
    ConflictType.OVERLAP.value: (
        "Учитывать вклад «{a}» и «{b}» один раз: эффекты перекрываются, "
        "суммирование завысит оценку выигрыша."
    ),
    ConflictType.UNKNOWN.value: (
        "Связь «{a}» ↔ «{b}» источником не подтверждена. Отсутствие запрета не "
        "означает совместимости: до совместного применения провести собственный замер."
    ),
}

#: Основание для типов, у которых решение выводится из отношения.
_DERIVED = "derived"
_UNKNOWN = "unknown"
_EXPERT = "expert_estimate"

#: Обходной путь для прямой привязки «метод — инструмент».
DIRECT_TOOL_WORKAROUND = (
    "Инструмент применяется штатно. Если он недоступен в выбранной версии "
    "движка — реализовать метод собственными средствами или выбрать "
    "альтернативный инструмент."
)

#: Обходной путь для связи «инструмент — движок».
TOOL_ENGINE_WORKAROUND = (
    "Инструмент существует только внутри этого движка. Для другого движка — "
    "искать аналог в его наборе инструментов или реализовать вручную."
)

#: Обходной путь «инструмент — движок», когда инструмент — собственная
#: разработка команды: искать аналог негде, поддержки вендора нет.
TOOL_ENGINE_CUSTOM_WORKAROUND = (
    "Реализуется командой самостоятельно; внешней поддержки нет."
)

#: Оба текста — шаблоны, выводимые из признака инструмента, а не курируемый
#: текст. Только их и разрешено пересчитывать: правка администратора не трогается.
TOOL_ENGINE_TEMPLATES = frozenset(
    {TOOL_ENGINE_WORKAROUND, TOOL_ENGINE_CUSTOM_WORKAROUND}
)

#: Типы рёбер, которые берут решение из одноимённой связи «метод-метод».
_METHOD_EDGE_TYPES = frozenset(action for action in _ACTIONS)


def _basis_for(conflict: Conflict) -> str:
    """Основание решения: источник есть — выведено; иначе — экспертное допущение."""
    if conflict.conflict_type == ConflictType.UNKNOWN.value:
        return _UNKNOWN
    if (conflict.source_url or "").startswith("user_defined:"):
        return _EXPERT
    return _DERIVED


def _text_for(conflict: Conflict, names: dict[str, str]) -> str:
    template = _ACTIONS.get(conflict.conflict_type)
    if template is None:
        return ""
    return template.format(
        a=names.get(conflict.a_code, conflict.a_code),
        b=names.get(conflict.b_code, conflict.b_code),
    )


def apply_relation_resolutions(db: Session) -> dict[str, int]:
    """Заполнить решения связей и основание, затем перенести их в рёбра графа.

    Заполняются только пустые значения: курируемое решение каталога и текст
    понижения цикла не перезаписываются.
    """
    names = {m.code: m.name for m in db.scalars(select(Method))}
    conflicts = list(db.scalars(select(Conflict)))

    resolved = 0
    for conflict in conflicts:
        if (conflict.resolution or "").strip():
            continue
        text = _text_for(conflict, names)
        if not text:
            continue
        conflict.resolution = text
        conflict.basis = _basis_for(conflict)
        resolved += 1

    # Основание проставляется и там, где решение уже было (курируемые связи).
    basis_filled = 0
    for conflict in conflicts:
        if (conflict.resolution or "").strip() and not (conflict.basis or "").strip():
            conflict.basis = _basis_for(conflict)
            basis_filled += 1

    # Согласование основания с источником: `derived` означает «выведено из
    # связи с источником», поэтому связь с пользовательским или отсутствующим
    # источником такого основания иметь не может. Проход приводит к правилу
    # базы, собранные прежней версией, где маркер `user_defined:` ставился уже
    # после записи основания, и потому оно не пересчитывалось. На базе,
    # собранной текущей версией, проход не находит ничего.
    basis_repaired = 0
    for conflict in conflicts:
        if conflict.basis == _DERIVED and _basis_for(conflict) != _DERIVED:
            conflict.basis = _basis_for(conflict)
            basis_repaired += 1

    db.flush()

    node_ids = {
        code: node_id
        for node_id, code in db.execute(
            select(TechnologyNode.id, TechnologyNode.code).where(
                TechnologyNode.node_type == "method"
            )
        ).all()
    }
    edges = list(db.scalars(select(DependencyEdge)))

    by_key = {(e.source_node_id, e.target_node_id, e.dependency_type): e for e in edges}
    propagated = 0
    for conflict in conflicts:
        resolution = (conflict.resolution or "").strip()
        if not resolution:
            continue
        source_id = node_ids.get(f"method:{conflict.a_code}")
        target_id = node_ids.get(f"method:{conflict.b_code}")
        if source_id is None or target_id is None:
            continue
        edge = by_key.get((source_id, target_id, conflict.conflict_type))
        if edge is None:
            continue
        if (edge.workaround or "").strip() != resolution:
            edge.workaround = resolution[:2000]
            edge.basis = conflict.basis or _DERIVED
            propagated += 1

    # Прямые привязки «метод — инструмент» и «инструмент — движок»: у них
    # обходного пути нет по существу, но пустое поле неотличимо от пробела.
    filled_direct = 0
    for edge in edges:
        if (edge.workaround or "").strip():
            continue
        if edge.dependency_type == "engine_tool":
            edge.workaround = DIRECT_TOOL_WORKAROUND
        elif edge.dependency_type == "engine":
            edge.workaround = TOOL_ENGINE_WORKAROUND
        else:
            continue
        # Основание здесь не проставляется: его назначает общий проход ниже по
        # наличию источника. Раньше здесь жёстко писалось `derived`, и одно и то
        # же ребро получало разное основание в зависимости от того, был ли
        # обходной путь уже заполнен: шаблонный текст помечался `derived` даже у
        # связи без источника, тогда как точно такое же ребро, дошедшее до
        # общего прохода, помечалось `expert_estimate`.
        filled_direct += 1

    # Текст обхода «инструмент — движок» выводится из признака собственного
    # инструмента. Если граф построен раньше, чем инструмент помечен
    # пользовательским, ребро остаётся с шаблоном «искать аналог в наборе
    # движка», хотя правильный текст — «реализуется командой». Шаблон
    # пересчитывается; курируемый текст не трогается.
    node_code = {
        node_id: code
        for node_id, code in db.execute(
            select(TechnologyNode.id, TechnologyNode.code).where(
                TechnologyNode.code.like("tool:%")
            )
        ).all()
    }
    tool_flags = {
        code: is_user_defined
        for code, is_user_defined in db.execute(
            select(EngineTool.code, EngineTool.is_user_defined)
        ).all()
    }
    workaround_reconciled = 0
    for edge in edges:
        if edge.dependency_type != "engine":
            continue
        current = (edge.workaround or "").strip()
        if current not in TOOL_ENGINE_TEMPLATES:
            continue
        code = node_code.get(edge.source_node_id, "")
        if not code.startswith("tool:"):
            continue
        flag = tool_flags.get(code[len("tool:"):])
        if flag is None:
            continue
        expected = TOOL_ENGINE_CUSTOM_WORKAROUND if flag else TOOL_ENGINE_WORKAROUND
        if current != expected:
            edge.workaround = expected
            workaround_reconciled += 1

    # Основание у остальных рёбер: подтверждено источником либо допущение.
    edge_basis = 0
    for edge in edges:
        if (edge.basis or "").strip():
            continue
        edge.basis = _DERIVED if edge.source_id else _EXPERT
        edge_basis += 1

    # То же согласование для рёбер: ребро без источника не может быть
    # «выведенным». Чинит базы, где шаблонный обходной путь помечался `derived`
    # независимо от источника; на базе текущей версии не находит ничего.
    edge_basis_repaired = 0
    for edge in edges:
        if edge.basis == _DERIVED and not edge.source_id:
            edge.basis = _EXPERT
            edge_basis_repaired += 1

    db.flush()
    stats = {
        "resolutions_created": resolved,
        "resolution_basis_filled": basis_filled,
        "resolution_basis_repaired": basis_repaired,
        "edge_workarounds_propagated": propagated,
        "edge_workarounds_direct": filled_direct,
        "edge_workarounds_reconciled": workaround_reconciled,
        "edge_basis_filled": edge_basis,
        "edge_basis_repaired": edge_basis_repaired,
    }
    logger.info("Решения связей: %s", stats)
    return stats
