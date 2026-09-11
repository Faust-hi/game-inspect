"""Сценарная оценка трудоёмкости и календарный critical path.

Единица оценки - человеко-день. P50/P80 являются экспертными сценарными
диапазонами, пока проект не импортирует собственные измерения. Размер команды
влияет на календарную ёмкость и критический путь, но не уменьшает общий объём
работ.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from sqlalchemy.orm import Session

from .. import repositories
from ..models.entities import Method, WorkPackage
from ..schemas.catalog import (
    EffortEstimateOut, EstimateBand, ScheduleOut, ScheduleTaskOut,
    TeamScenarioOut, WorkPackageOut,
)

PACKAGE_ORDER = {
    "design": 0, "feasibility": 1, "prototype": 1, "integration": 2,
    "content": 3, "asset_preparation": 3, "optimization": 4,
    "qa": 5, "regression": 5, "release": 6, "documentation": 7,
    "maintenance": 8,
}

DEFAULT_TEAMS = {
    "solo": {
        "name": "Solo",
        "description": "Один специалист; узкие роли выполняются последовательно.",
        "team_size": 1, "role_capacity": {"design": 1, "engineering": 1, "technical_art": 1, "qa": 1, "production": 1},
        "parallel_tracks": 1, "communication_pct": 0.05, "unplanned_pct": 0.25,
    },
    "small_2_5": {
        "name": "Малая команда (2-5)",
        "description": "Небольшая команда с двумя параллельными потоками и общей QA/production ёмкостью.",
        "team_size": 4, "role_capacity": {"design": 1, "engineering": 2, "technical_art": 1, "qa": 1, "production": 1},
        "parallel_tracks": 2, "communication_pct": 0.12, "unplanned_pct": 0.18,
    },
    "mid_6_15": {
        "name": "Средняя команда (6-15)",
        "description": "Специализированные роли и несколько независимых потоков, но ограниченный production/QA gate.",
        "team_size": 10, "role_capacity": {"design": 2, "engineering": 5, "technical_art": 2, "qa": 2, "production": 1},
        "parallel_tracks": 5, "communication_pct": 0.18, "unplanned_pct": 0.15,
    },
    "large_16_plus": {
        "name": "Большая команда (16+)",
        "description": "Много специализированных ролей; сроки ограничиваются зависимостями, интеграцией и проверками.",
        "team_size": 24, "role_capacity": {"design": 3, "engineering": 10, "technical_art": 5, "qa": 4, "production": 2},
        "parallel_tracks": 12, "communication_pct": 0.25, "unplanned_pct": 0.12,
    },
    "custom": {
        "name": "Собственный состав",
        "description": (
            "Промежуточная ёмкость под нетиповую команду. Численность и роли — "
            "экспертное допущение и переопределяются пользователем; это шаблон, "
            "а не измеренная пропускная способность конкретной студии."
        ),
        "team_size": 6, "role_capacity": {"design": 1, "engineering": 3, "technical_art": 1, "qa": 1, "production": 1},
        "parallel_tracks": 3, "communication_pct": 0.15, "unplanned_pct": 0.16,
    },
}


@dataclass
class Task:
    code: str
    name: str
    method_code: str
    package_type: str
    role: str
    minimum: float
    p50: float
    p80: float
    parallelizable: bool
    late_factor: float
    dependencies: list[str] = field(default_factory=list)
    # Рекомендуемая стадия и основание оценки нужны в выдаче: без них пакет
    # работ нельзя ни поставить в план по стадии, ни отличить измерение от
    # экспертного допущения.
    recommended_stage: str = "prototype"
    basis: str = "expert_estimate"


def _team_out(row) -> TeamScenarioOut:
    return TeamScenarioOut(
        code=row.code, name=row.name, description=row.description,
        team_size=row.team_size, role_capacity=row.role_capacity or {},
        parallel_tracks=row.parallel_tracks,
        communication_pct=row.communication_pct, unplanned_pct=row.unplanned_pct,
        specialist_capacity=row.specialist_capacity or {},
    )


def team_for(db: Session, code: str) -> TeamScenarioOut:
    row = repositories.team_scenario(db, code)
    if row is not None:
        return _team_out(row)
    # Неизвестный профиль команды не подменяется похожим: иначе пользователь
    # получит чужой календарь и не узнает об этом. Сценарий возвращается под
    # своим кодом, а его описание прямо сообщает о подстановке.
    data = dict(DEFAULT_TEAMS.get(code, DEFAULT_TEAMS["small_2_5"]))
    if code not in DEFAULT_TEAMS:
        data["description"] = (
            f"Профиль «{code}» не найден в каталоге; ниже показана нейтральная "
            "ёмкость малой команды как явная подстановка, а не измерение."
        )
    return TeamScenarioOut(code=code, **data, specialist_capacity={})


def _late_factor(method: Method) -> float:
    return {"low": 1.08, "medium": 1.2, "high": 1.45, "critical": 1.8}.get(method.late_cost, 1.2)


def _fallback_packages(method: Method) -> list[Task]:
    """Прозрачная fallback-оценка для старых баз без work_packages."""
    cost = max(1.0, float(method.implementation_cost or 3))
    complexity = max(1.0, float(method.complexity or 3))
    prototype = 0.6 + complexity * 0.35 if (method.requires_prototype or complexity >= 4) else 0.0
    base = [
        ("design", "Проектирование и контракт", "design", 0.45 + cost * 0.22),
        ("feasibility", "Проверка реализуемости", "engineering", prototype),
        ("integration", "Интеграция в проект", "engineering", 0.9 + cost * 0.55),
        ("content", "Подготовка контента и ассетов", "technical_art", 0.35 + complexity * 0.3),
        ("optimization", "Оптимизация и измерительный стенд", "engineering", 0.4 + complexity * 0.25),
        ("qa", "QA и регрессия", "qa", 0.45 + complexity * 0.22),
        ("release", "Стабилизация и документация", "production", 0.25 + cost * 0.12),
    ]
    out: list[Task] = []
    previous = None
    for kind, name, role, p50 in base:
        if p50 <= 0:
            continue
        code = f"{method.code}.{kind}"
        out.append(Task(
            code=code, name=f"{method.name}: {name}", method_code=method.code,
            package_type=kind, role=role, minimum=round(p50 * 0.65, 2),
            p50=round(p50, 2), p80=round(p50 * 1.5, 2), parallelizable=kind not in {"integration", "qa", "release"},
            late_factor=_late_factor(method), dependencies=[previous] if previous else [],
            recommended_stage=method.recommended_stage or "prototype",
            basis="expert_estimate",
        ))
        previous = code
    return out


def _db_packages(rows: list[WorkPackage]) -> list[Task]:
    out: list[Task] = []
    for row in rows:
        out.append(Task(
            code=row.code, name=row.name, method_code=row.method_code,
            package_type=row.package_type, role=row.role,
            minimum=float(row.min_days), p50=float(row.p50_days), p80=float(row.p80_days),
            parallelizable=bool(row.parallelizable), late_factor=float(row.late_factor),
            dependencies=[],
            recommended_stage=row.recommended_stage or "prototype",
            basis=row.basis or "expert_estimate",
        ))
    by_method: dict[str, list[Task]] = {}
    for item in out:
        by_method.setdefault(item.method_code, []).append(item)
    for items in by_method.values():
        items.sort(key=lambda item: (PACKAGE_ORDER.get(item.package_type, 50), item.code))
        for previous, current in zip(items, items[1:]):
            current.dependencies.append(previous.code)
    lookup = {row.code: row for row in rows}
    for item in out:
        row = lookup[item.code]
        # dependency_codes are method codes, not arbitrary task names. The
        # first package of a method waits for the integration package of each
        # prerequisite when that prerequisite exists in the selected set.
        if PACKAGE_ORDER.get(item.package_type, 50) == 0:
            for dependency in row.dependency_codes or []:
                item.dependencies.append(f"{dependency}.integration")
    return out


def _methods_with_dependencies(db: Session, codes: list[str], include: bool) -> tuple[list[str], list[str]]:
    selected = set(codes)
    unresolved: list[str] = []
    if not include:
        return sorted(selected), unresolved
    nodes = {node.code: node for node in repositories.technology_nodes(db)}
    edges = repositories.dependency_edges(db)
    changed = True
    while changed:
        changed = False
        for edge in edges:
            source = nodes.get(edge.source_node_id) if isinstance(edge.source_node_id, str) else None
            target = nodes.get(edge.target_node_id) if isinstance(edge.target_node_id, str) else None
            # ORM ids are integers; build the mapping once without assuming
            # relationship attributes were eagerly loaded.
        # Prefix-based nodes are resolved through a small id map below.
        by_id = {node.id: node for node in nodes.values()}
        for edge in edges:
            source = by_id.get(edge.source_node_id)
            target = by_id.get(edge.target_node_id)
            if source is None or target is None or source.node_type != "method" or not edge.mandatory:
                continue
            if source.code.removeprefix("method:") not in selected:
                continue
            target_code = target.code.removeprefix("method:") if target.node_type == "method" else ""
            if target_code and target_code not in selected:
                if any(m.code == target_code for m in repositories.methods(db)):
                    selected.add(target_code)
                    changed = True
                else:
                    unresolved.append(f"{source.code} требует отсутствующий метод {target.code}")
            elif not target_code and target is None:
                unresolved.append(f"{source.code} требует неизвестный узел")
    # Validate mandatory non-method dependencies against the selected profile.
    by_id = {node.id: node for node in nodes.values()}
    for edge in edges:
        source = by_id.get(edge.source_node_id)
        target = by_id.get(edge.target_node_id)
        if source is None or target is None:
            unresolved.append(f"edge:{edge.id}: неизвестный узел")
            continue
        source_method = source.code.removeprefix("method:") if source.node_type == "method" else ""
        if edge.mandatory and source_method in selected and target.node_type in {"plugin", "sdk", "api", "library", "tool"}:
            if not target.version and edge.min_version:
                unresolved.append(f"{source.code} -> {target.code}: версия {edge.min_version} не подтверждена")
    return sorted(selected), sorted(set(unresolved))


def _ordered_tasks(tasks: list[Task]) -> tuple[list[Task], list[str]]:
    by_code = {task.code: task for task in tasks}
    indegree = {task.code: sum(1 for dep in task.dependencies if dep in by_code) for task in tasks}
    dependents: dict[str, list[str]] = {task.code: [] for task in tasks}
    for task in tasks:
        for dep in task.dependencies:
            if dep in by_code:
                dependents[dep].append(task.code)
    queue = sorted([code for code, degree in indegree.items() if degree == 0])
    ordered: list[Task] = []
    while queue:
        code = queue.pop(0)
        ordered.append(by_code[code])
        for child in sorted(dependents[code]):
            indegree[child] -= 1
            if indegree[child] == 0:
                queue.append(child)
                queue.sort()
    return ordered, sorted(set(by_code) - {task.code for task in ordered})


def _schedule_tasks(tasks: list[Task], team: TeamScenarioOut) -> tuple[list[ScheduleTaskOut], float, float, list[str]]:
    ordered, cycles = _ordered_tasks(tasks)
    finish50: dict[str, float] = {}
    finish80: dict[str, float] = {}
    task_out: dict[str, ScheduleTaskOut] = {}
    role_available: dict[str, float] = {}
    factor = 1.0 + team.communication_pct + team.unplanned_pct
    for task in ordered:
        capacity = float((team.role_capacity or {}).get(task.role, 1) or 1)
        capacity = max(1.0, min(capacity, float(max(1, team.parallel_tracks))))
        duration50 = task.p50 * factor / capacity
        duration80 = task.p80 * factor / capacity
        dep50 = max((finish50.get(dep, 0.0) for dep in task.dependencies), default=0.0)
        dep80 = max((finish80.get(dep, 0.0) for dep in task.dependencies), default=0.0)
        start50 = max(dep50, role_available.get(task.role, 0.0))
        start80 = max(dep80, role_available.get(task.role, 0.0))
        end50 = start50 + duration50
        end80 = start80 + duration80
        finish50[task.code] = end50
        finish80[task.code] = end80
        role_available[task.role] = end50
        task_out[task.code] = ScheduleTaskOut(
            code=task.code, name=task.name, method_code=task.method_code,
            package_type=task.package_type, role=task.role,
            dependencies=[dep for dep in task.dependencies if dep in finish50],
            minimum_days=task.minimum,
            p50_days=task.p50, p80_days=task.p80,
            parallelizable=task.parallelizable,
            recommended_stage=task.recommended_stage,
            late_factor=task.late_factor,
            basis=task.basis,
            start_p50=round(start50, 2), finish_p50=round(end50, 2),
            start_p80=round(start80, 2), finish_p80=round(end80, 2),
        )
    max_finish = max(finish50.values(), default=0.0)
    max_finish80 = max(finish80.values(), default=0.0)
    critical: list[str] = []
    current = max(finish50, key=finish50.get, default=None)
    while current:
        critical.append(current)
        item = task_out[current]
        candidates = [dep for dep in item.dependencies if dep in task_out]
        current = max(candidates, key=lambda dep: finish50.get(dep, 0), default=None)
    for code in critical:
        item = task_out[code]
        task_out[code] = item.model_copy(update={"critical": True})
    return [task_out[task.code] for task in ordered], round(max_finish, 2), round(max_finish80, 2), cycles


def schedule(db: Session, profile, basket_codes: list[str], team_code: str = "small_2_5", include_dependencies: bool = True) -> ScheduleOut:
    selected_codes, unresolved = _methods_with_dependencies(db, sorted(set(basket_codes)), include_dependencies)
    methods = {method.code: method for method in repositories.methods_by_codes(db, selected_codes)}
    rows = repositories.work_packages(db, list(methods))
    by_method: dict[str, list[WorkPackage]] = {}
    for row in rows:
        by_method.setdefault(row.method_code, []).append(row)
    tasks: list[Task] = []
    for code in selected_codes:
        method = methods.get(code)
        if method is None:
            unresolved.append(f"Неизвестный метод {code}")
            continue
        tasks.extend(_db_packages(by_method[code]) if by_method.get(code) else _fallback_packages(method))
    team = team_for(db, team_code)
    task_out, calendar50, calendar80, cycles = _schedule_tasks(tasks, team)
    unresolved.extend(f"Цикл обязательных зависимостей: {code}" for code in cycles)
    p50 = sum(item.p50 for item in tasks)
    p80 = sum(item.p80 for item in tasks)
    minimum = sum(item.minimum for item in tasks)
    late = []
    if profile.stage in {"alpha", "beta", "release", "post_release"}:
        late.append("Поздняя стадия увеличивает риск переработки; пакетная оценка не является обещанием срока.")
    return ScheduleOut(
        team=team, methods=selected_codes,
        effort=EstimateBand(minimum=round(minimum, 2), p50=round(p50, 2), p80=round(p80, 2), unit="человеко-дни", basis="expert_estimate"),
        calendar=EstimateBand(minimum=None, p50=calendar50, p80=calendar80, unit="рабочие дни", basis="dependency_dag_plus_team_capacity"),
        critical_path=[item.code for item in task_out if item.critical],
        tasks=task_out, unresolved_dependencies=sorted(set(unresolved)),
        stage_notes=late, evidence_basis="expert_estimate",
    )


def effort_for_methods(db: Session, method_codes: list[str]) -> list[EffortEstimateOut]:
    methods = {method.code: method for method in repositories.methods_by_codes(db, method_codes)}
    rows = repositories.work_packages(db, method_codes)
    by_method: dict[str, list[WorkPackage]] = {}
    for row in rows:
        by_method.setdefault(row.method_code, []).append(row)
    result: list[EffortEstimateOut] = []
    for code in sorted(set(method_codes)):
        method = methods.get(code)
        if method is None:
            continue
        if by_method.get(code):
            packages = [WorkPackageOut(
                code=row.code, method_code=row.method_code, name=row.name,
                package_type=row.package_type, role=row.role, min_days=row.min_days,
                p50_days=row.p50_days, p80_days=row.p80_days,
                parallelizable=row.parallelizable, recommended_stage=row.recommended_stage,
                late_factor=row.late_factor, dependency_codes=row.dependency_codes or [], basis=row.basis,
            ) for row in sorted(by_method[code], key=lambda item: (PACKAGE_ORDER.get(item.package_type, 50), item.code))]
        else:
            tasks = _fallback_packages(method)
            packages = [WorkPackageOut(
                code=item.code, method_code=item.method_code, name=item.name,
                package_type=item.package_type, role=item.role, min_days=item.minimum,
                p50_days=item.p50, p80_days=item.p80, parallelizable=item.parallelizable,
                recommended_stage=method.recommended_stage, late_factor=item.late_factor,
                dependency_codes=item.dependencies, basis="expert_estimate_fallback",
            ) for item in tasks]
        result.append(EffortEstimateOut(
            method_code=code, method_name=method.name, packages=packages,
            total=EstimateBand(
                minimum=round(sum(p.min_days for p in packages), 2),
                p50=round(sum(p.p50_days for p in packages), 2),
                p80=round(sum(p.p80_days for p in packages), 2),
                unit="человеко-дни", basis="expert_estimate",
                confidence=method.confidence,
            ),
            risk_factors=[
                "требуется прототип" if method.requires_prototype else "",
                f"поздний фактор { _late_factor(method):.2f }" if method.late_cost in {"high", "critical"} else "",
            ],
        ))
    for item in result:
        item.risk_factors = [risk for risk in item.risk_factors if risk]
    return result
