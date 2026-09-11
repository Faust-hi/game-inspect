"""Проверки графа технологических зависимостей.

Граф не должен молча выдавать «совместимо» там, где связь неизвестна.
Каждая проверка возвращает находки с явным статусом, а не только ошибки:
список непроверенного здесь так же важен, как список нарушений.
"""
from __future__ import annotations

import re
from typing import Any, Iterable

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models.entities import (
    DependencyEdge, Engine, EngineTool, TechnologyNode,
)

#: Типы рёбер, которые задают обязательность для расчёта корзины.
_MANDATORY_TYPES = {"dependency", "engine", "runtime_api", "package", "sdk", "library"}


def parse_version(text: str | None) -> tuple[int, ...] | None:
    """Разобрать версию в сравнимый кортеж. None — версию сравнить нельзя."""
    if not text:
        return None
    numbers = re.findall(r"\d+", str(text))
    if not numbers:
        return None
    return tuple(int(n) for n in numbers[:4])


def _version_lt(a: str | None, b: str | None) -> bool | None:
    """True, если a < b. None — сравнить невозможно (не выдумываем результат)."""
    pa, pb = parse_version(a), parse_version(b)
    if pa is None or pb is None:
        return None
    return pa < pb


def graph_checks(
    db: Session,
    *,
    basket: Iterable[str] | None = None,
    engine: str | None = None,
    engine_version: str | None = None,
    render_api: str | None = None,
) -> dict[str, Any]:
    """Выполнить проверки графа и вернуть находки и счётчики."""
    basket_set = {c for c in (basket or []) if c}
    nodes = {n.id: n for n in db.scalars(select(TechnologyNode))}
    edges = list(db.scalars(select(DependencyEdge)))

    issues: list[dict[str, Any]] = []

    def issue(check: str, severity: str, message: str, **extra: Any) -> None:
        issues.append(
            {"check": check, "severity": severity, "message": message, "details": extra}
        )

    # 1. Отсутствующий узел — ребро в никуда делает проверки недостоверными.
    dangling = 0
    for edge in edges:
        if edge.source_node_id not in nodes or edge.target_node_id not in nodes:
            dangling += 1
    if dangling:
        issue(
            "missing_node", "error",
            f"Рёбер с отсутствующим узлом: {dangling}. Транзитивные проверки по ним недостоверны.",
        )

    # 2. Циклическая обязательная зависимость.
    adjacency: dict[int, list[int]] = {}
    for edge in edges:
        if edge.mandatory and edge.dependency_type in _MANDATORY_TYPES:
            adjacency.setdefault(edge.source_node_id, []).append(edge.target_node_id)

    WHITE, GREY, BLACK = 0, 1, 2
    color = {nid: WHITE for nid in nodes}
    cycles: list[list[str]] = []

    def walk(start: int) -> None:
        stack: list[tuple[int, int]] = [(start, 0)]
        path: list[int] = []
        while stack:
            node_id, idx = stack.pop()
            if idx == 0:
                color[node_id] = GREY
                path.append(node_id)
            neighbours = adjacency.get(node_id, [])
            if idx < len(neighbours):
                stack.append((node_id, idx + 1))
                nxt = neighbours[idx]
                if color.get(nxt, WHITE) == GREY:
                    cut = path.index(nxt) if nxt in path else 0
                    cycles.append([nodes[i].code for i in path[cut:] + [nxt] if i in nodes])
                elif color.get(nxt, WHITE) == WHITE:
                    stack.append((nxt, 0))
            else:
                color[node_id] = BLACK
                if path:
                    path.pop()

    for nid in nodes:
        if color[nid] == WHITE:
            walk(nid)
    if cycles:
        issue(
            "cyclic_mandatory", "error",
            f"Найдено циклических обязательных зависимостей: {len(cycles)}. "
            "Обязательное ребро в цикле неразрешимо.",
            cycles=cycles[:10],
        )

    # 3. Зависимость от неподдерживаемой версии.
    tools = {t.id: t for t in db.scalars(select(EngineTool))}
    engines = {e.id: e for e in db.scalars(select(Engine))}
    unsupported = 0
    for edge in edges:
        if not edge.min_version:
            continue
        target = nodes.get(edge.target_node_id)
        if target is None or target.node_type != "tool":
            continue
        tool = next((t for t in tools.values() if f"tool:{t.code}" == target.code), None)
        if tool is None:
            continue
        tool_engine = engines.get(tool.engine_id)
        if tool_engine is None:
            continue
        if engine and tool_engine.code == engine and engine_version:
            if _version_lt(engine_version, tool.min_version) is True:
                unsupported += 1
                issue(
                    "unsupported_version", "error",
                    f"Инструмент «{tool.name}» появляется только с версии {tool.min_version}, "
                    f"а выбрана {engine_version}.",
                    engine=engine, tool=tool.code, required=tool.min_version,
                )
    if not engine_version:
        # Без версии движка проверить нельзя — это не «подходит».
        issue(
            "version_unknown", "info",
            "Версия движка не указана: соответствие версиям инструментов не проверено "
            "(отсутствие нарушения здесь не означает совместимость).",
        )

    # 4. Несовместимость с выбранным графическим API.
    if render_api:
        for edge in edges:
            if edge.dependency_type != "runtime_api" or not edge.mandatory:
                continue
            api = nodes.get(edge.target_node_id)
            if api is None:
                continue
            wanted = api.code.split(":", 1)[-1]
            if wanted and wanted != render_api:
                issue(
                    "api_incompatibility", "error",
                    f"Обязательное требование к API «{api.name}», а выбран «{render_api}».",
                    required_api=wanted, selected_api=render_api,
                    source_node=nodes.get(edge.source_node_id).code if edge.source_node_id in nodes else "",
                    workaround=edge.workaround,
                )

    # 5–7. Проверки по корзине решений.
    if basket_set:
        for edge in edges:
            src = nodes.get(edge.source_node_id)
            dst = nodes.get(edge.target_node_id)
            if src is None or dst is None:
                continue
            src_method = src.code.split(":", 1)[-1] if src.node_type == "method" else None
            dst_method = dst.code.split(":", 1)[-1] if dst.node_type == "method" else None

            # 5. Жёсткий конфликт внутри корзины.
            if edge.dependency_type == "hard_conflict" and src_method in basket_set and dst_method in basket_set:
                issue(
                    "basket_hard_conflict", "error",
                    f"Жёсткий конфликт: «{src_method}» и «{dst_method}» не могут быть в одной корзине.",
                    a=src_method, b=dst_method, workaround=edge.workaround,
                )

            # 6. Незакрытая обязательная транзитивная зависимость.
            if (
                edge.dependency_type == "dependency"
                and edge.mandatory
                and src_method in basket_set
                and dst_method
                and dst_method not in basket_set
            ):
                issue(
                    "unresolved_dependency", "warning",
                    f"«{src_method}» требует «{dst_method}», которого нет в корзине.",
                    required=dst_method, dependent=src_method,
                )

            # 7. Неизвестная связь — это не подтверждённая совместимость.
            if edge.dependency_type == "unknown" and (
                src_method in basket_set or dst_method in basket_set
            ):
                issue(
                    "unknown_relation", "warning",
                    f"Связь «{src.code}» ↔ «{dst.code}» не проверена: "
                    "отсутствие запрета не означает совместимость.",
                    a=src.code, b=dst.code,
                )

        # Метод, зависящий от инструмента недоступной версии, неприменим.
        for edge in edges:
            if edge.dependency_type != "engine_tool":
                continue
            src = nodes.get(edge.source_node_id)
            dst = nodes.get(edge.target_node_id)
            if src is None or dst is None or dst.node_type != "tool":
                continue
            src_method = src.code.split(":", 1)[-1]
            if src_method not in basket_set:
                continue
            tool = next((t for t in tools.values() if f"tool:{t.code}" == dst.code), None)
            if tool is None or not tool.is_user_defined:
                continue
            issue(
                "user_defined_tool", "info",
                f"Метод «{src_method}» опирается на пользовательский инструмент «{tool.name}»: "
                "внешнего подтверждения совместимости не существует.",
                method=src_method, tool=tool.code,
            )

    by_severity: dict[str, int] = {}
    for item in issues:
        by_severity[item["severity"]] = by_severity.get(item["severity"], 0) + 1

    return {
        "issues": issues,
        "counts": {
            "edges": len(edges),
            "nodes": len(nodes),
            "mandatory_edges": sum(1 for e in edges if e.mandatory),
            "issues": len(issues),
            **{f"severity_{k}": v for k, v in by_severity.items()},
        },
        "engine": engine,
        "engine_version": engine_version,
        "render_api": render_api,
        "basket": sorted(basket_set),
    }
