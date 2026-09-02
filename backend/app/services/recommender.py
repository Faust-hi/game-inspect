"""Алгоритм формирования рекомендаций (раздел 4 плана).

Последовательность работы:
1. анализ характеристик проекта;
2. выявление потенциальных рисков;
3. поиск подходящих вариантов реализации выбранных функций;
4. исключение решений, нарушающих обязательные ограничения;
5. учёт стадии разработки и стоимости позднего внедрения;
6. ранжирование допустимых решений методом TOPSIS;
7. формирование объяснения каждой рекомендации;
8. показ общих методов и их аналогов в выбранном движке;
9. предупреждение о конфликтах и возможном изменении концепции.
"""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models.entities import (
    Conflict, Engine, EngineTool, GameExample, GameFunction, Method, MethodEngineLink,
)
from ..models.enums import (
    CalcMode, ConflictType, DevStage, LateCost, Level3, RelationType, SolutionLevel,
)
from ..schemas.catalog import (
    BasketConflictOut, CriterionScore, LoadProfileOut, MethodEngineLinkOut,
    RecommendationOut, RecommendationResult, RiskOut, SimilarGameOut,
)
from . import gower, hardware, rules, serializers
from .topsis import Criterion, criterion_matrix_rows, topsis

# Веса критериев в зависимости от приоритета пользователя.
WEIGHT_PROFILES: dict[str, dict[str, float]] = {
    "balanced": {
        "performance_gain": 1.0, "quality_preservation": 1.0, "concept_fidelity": 1.0,
        "implementation_cost": 1.0, "late_penalty": 1.0, "risk": 0.8,
        "resource_fit": 1.0, "confidence": 0.6,
    },
    "performance": {
        "performance_gain": 1.7, "quality_preservation": 0.7, "concept_fidelity": 0.8,
        "implementation_cost": 0.8, "late_penalty": 0.8, "risk": 0.8,
        "resource_fit": 1.3, "confidence": 0.6,
    },
    "quality": {
        "performance_gain": 0.7, "quality_preservation": 1.9, "concept_fidelity": 1.5,
        "implementation_cost": 0.9, "late_penalty": 1.0, "risk": 0.8,
        "resource_fit": 0.8, "confidence": 0.6,
    },
    "cost": {
        "performance_gain": 0.8, "quality_preservation": 0.6, "concept_fidelity": 0.9,
        "implementation_cost": 1.9, "late_penalty": 1.5, "risk": 1.0,
        "resource_fit": 0.9, "confidence": 0.6,
    },
}

FLAG_LABELS = {
    "recommended": "рекомендуется",
    "conditional": "применимо при условиях",
    "implement_now": "желательно внедрить сейчас",
    "late_difficult": "позднее внедрение затруднено",
    "needs_prototyping": "требует прототипирования",
    "may_reduce_quality": "может снизить качество",
    "may_change_concept": "может изменить концепцию",
    "not_recommended": "не рекомендуется",
}

RELATION_PRIORITY = ["direct", "automation", "partial", "alternative", "complement", "diagnostic", "limited", "missing"]


# ---------------------------------------------------------------------------
# Вспомогательные преобразования
# ---------------------------------------------------------------------------
def link_out(db: Session, link: MethodEngineLink) -> MethodEngineLinkOut:
    tool: EngineTool | None = db.get(EngineTool, link.tool_id)
    engine: Engine | None = db.get(Engine, tool.engine_id) if tool else None
    try:
        label = RelationType(link.relation_type).label
    except ValueError:
        label = link.relation_type
    return MethodEngineLinkOut(
        engine_code=engine.code if engine else "",
        engine_name=engine.name if engine else "",
        tool_code=tool.code if tool else "",
        tool_name=tool.name if tool else "",
        relation_type=link.relation_type,
        relation_label=label,
        note=link.note,
        docs_url=tool.docs_url if tool else "",
    )


def _label(enum_cls, value: str, default: str = "") -> str:
    try:
        return enum_cls(value).label
    except ValueError:
        return default


# ---------------------------------------------------------------------------
# 1-2. Анализ проекта и выявление рисков
# ---------------------------------------------------------------------------
def detect_risks(profile, basket_codes: list[str], methods_by_code: dict[str, Method]) -> list[RiskOut]:
    risks: list[RiskOut] = []
    stage_order = DevStage(profile.stage).order if profile.stage in {s.value for s in DevStage} else 2

    def add(code: str, title: str, severity: str, description: str, advice: str) -> None:
        risks.append(RiskOut(code=code, title=title, severity=severity, description=description, advice=advice))

    # Поздняя стадия без архитектурных решений.
    if stage_order >= DevStage.ALPHA.order and profile.world_type in ("open_world", "procedural"):
        if "world_partition_streaming" not in basket_codes:
            add(
                "late_streaming", "Отсутствует решение по стримингу открытого мира",
                "high",
                "Проект с открытым миром находится на поздней стадии, но потоковая загрузка мира "
                "не заложена. Внедрение на этой стадии требует переработки уровней и ассетов.",
                "Оценить возможность частичного внедрения плиточной загрузки или зафиксировать "
                "ограничение размера мира.",
            )

    # Поздняя стадия и архитектурные изменения.
    if stage_order >= DevStage.ALPHA.order:
        arch_missing = [
            m.code for m in methods_by_code.values()
            if m.code not in basket_codes and m.level == "architecture" and m.late_cost == "critical"
        ]
        if arch_missing:
            add(
                "architecture_locked", "Архитектурные решения уже заблокированы стадией",
                "high",
                f"На текущей стадии внедрение {len(arch_missing)} архитектурных решений имеет "
                "критическую стоимость. Часть из них уже недоступна без переработки проекта.",
                "Сосредоточиться на решениях уровня настроек, алгоритмов и производственного процесса.",
            )

    # Большое число NPC без решений по толпе.
    if profile.npc_count_level == "high" and "crowd_simulation" in profile.functions:
        if not any(c in basket_codes for c in ("ecs_data_oriented_crowd", "agent_update_budget", "crowd_instancing_impostors")):
            add(
                "crowd_budget", "Не определён подход к симуляции толпы",
                "high",
                "Заявлено большое число NPC, но не выбрано ни одного решения по их симуляции и отрисовке.",
                "Выбрать подход до начала массового наполнения уровней.",
            )

    # Мультиплеер без сетевых решений.
    if profile.multiplayer and profile.player_count >= 16:
        if not any(c in basket_codes for c in ("network_relevancy_priority", "delta_compression_state", "headless_dedicated_server")):
            add(
                "network_scale", "Не определена схема сетевой нагрузки",
                "high",
                f"Заявлено до {profile.player_count} игроков в сессии, но сетевая репликация "
                "не ограничена правилами релевантности.",
                "Заложить релевантность и приоритизацию репликации до проектирования игрового режима.",
            )

    # Сочетание высокого разрешения и качества с открытым миром.
    if profile.target_resolution.lower() in ("2160p", "4k") and profile.target_quality in ("high", "ultra"):
        add(
            "gpu_budget_high", "Высокие требования к GPU",
            "medium",
            "Сочетание 4K и высокой детализации с выбранным масштабом мира создаёт высокую "
            "нагрузку на GPU даже при использовании масштабирования.",
            "Предусмотреть временное масштабирование и динамическое разрешение как обязательные решения.",
        )

    # Ограничение памяти при большом мире.
    if profile.ram_limit_gb and profile.ram_limit_gb < 8 and profile.scale in ("large", "very_large"):
        add(
            "memory_budget", "Ограничение оперативной памяти",
            "medium",
            f"Задан предел {profile.ram_limit_gb} ГБ при большом масштабе мира: стандартные подходы "
            "к загрузке могут не уложиться в бюджет.",
            "Предусмотреть потоковую загрузку и сжатие данных как обязательные решения.",
        )

    # Мобильные платформы при высоких требованиях.
    if any(p in ("android", "ios", "switch") for p in profile.platforms) and profile.target_fps >= 60:
        add(
            "mobile_target", "Целевое оборудование существенно слабее десктопного",
            "medium",
            "Для мобильных платформ бюджет GPU и памяти на порядок ниже, чем у персональных компьютеров.",
            "Проверить применимость каждого решения на минимальной мобильной конфигурации.",
        )

    # Ранняя стадия без прототипа при дорогих решениях.
    if profile.stage in ("concept", "preproduction"):
        prototype_required = [
            c for c in basket_codes if methods_by_code.get(c) and methods_by_code[c].requires_prototype
        ]
        if prototype_required:
            add(
                "prototype_needed", "Выбранные решения требуют проверки на прототипе",
                "medium",
                f"{len(prototype_required)} выбранных решений имеют оценку эффекта, требующую "
                "экспериментальной проверки.",
                "Запланировать прототип до принятия окончательного решения.",
            )

    # Конфликты внутри корзины.
    conflicting = [
        c for c in basket_codes
        if any(code in basket_codes for code in _conflict_partners(c))
    ]
    if conflicting:
        add(
            "basket_conflict", "В корзине присутствуют конфликтующие решения",
            "high",
            "Часть выбранных решений взаимно исключает друг друга или дублирует стоимость.",
            "Проверить раздел совместимости набора и выбрать одну из альтернатив.",
        )

    return risks


def _conflict_partners(code: str) -> list[str]:
    return _CONFLICT_MAP.get(code, [])


_CONFLICT_MAP: dict[str, list[str]] = {}


def _build_conflict_map(db: Session) -> None:
    _CONFLICT_MAP.clear()
    for row in db.scalars(select(Conflict)):
        if row.conflict_type != "conflict":
            continue
        _CONFLICT_MAP.setdefault(row.a_code, []).append(row.b_code)
        _CONFLICT_MAP.setdefault(row.b_code, []).append(row.a_code)


# ---------------------------------------------------------------------------
# 3-8. Подбор, фильтрация и ранжирование
# ---------------------------------------------------------------------------
def build_recommendations(db: Session, profile, basket_codes: list[str]) -> RecommendationResult:
    _build_conflict_map(db)

    functions = {f.code: f for f in db.scalars(select(GameFunction))}
    all_methods = list(db.scalars(select(Method).where(Method.status == "published")))
    methods_by_code = {m.code: m for m in all_methods}

    # 3. Кандидаты: методы для выбранных функций.
    selected = set(profile.functions)
    candidates = [m for m in all_methods if (m.function and m.function.code in selected)]

    # 4-5. Исключение и оценка применимости.
    evaluated: list[tuple[Method, rules.Applicability]] = []
    excluded: list[RecommendationOut] = []
    for method in candidates:
        applicability = rules.evaluate(method, profile)
        if not applicability.applicable:
            excluded.append(_build_excluded(method, functions, applicability))
            continue
        if not rules.min_scale_satisfied(method, profile):
            excluded.append(_build_excluded(
                method, functions, applicability,
                extra=f"Метод оправдан при масштабе мира не ниже «{method.min_scale}».",
            ))
            continue
        evaluated.append((method, applicability))

    if not evaluated:
        # Ни одно решение не прошло фильтр обязательных ограничений. Профиль
        # нагрузки, похожие игры и аппаратная оценка всё равно возвращаются:
        # пользователю важно видеть причины исключения и ориентир по железу.
        basket_methods = [methods_by_code[c] for c in basket_codes if c in methods_by_code]
        examples = list(db.scalars(select(GameExample).where(GameExample.status == "published")))
        similar = [
            SimilarGameOut(
                example=serializers.example_out(ex),
                similarity=sim,
                matching_optimizations=match,
            )
            for ex, sim, match in gower.find_similar(profile, examples, top_n=5)
        ]
        return RecommendationResult(
            profile=profile,
            risks=detect_risks(profile, basket_codes, methods_by_code),
            recommendations=[],
            excluded=excluded,
            load_profile=aggregate_load(basket_methods, profile),
            basket_conflicts=basket_compatibility(db, basket_codes, methods_by_code)[0],
            basket_synergies=basket_compatibility(db, basket_codes, methods_by_code)[1],
            hardware=hardware.estimate_hardware(db, profile, basket_methods, similar_examples=len(similar)),
            similar_games=similar,
            meta={
                "candidates": len(candidates),
                "applicable": 0,
                "excluded": len(excluded),
                "note": "Ни одно решение не прошло проверку обязательных ограничений проекта.",
            },
        )

    # 6. Матрица решений и TOPSIS.
    weights = WEIGHT_PROFILES.get(profile.priority, WEIGHT_PROFILES["balanced"])
    criteria = [
        Criterion("performance_gain", "Ожидаемый прирост производительности", "benefit", weights["performance_gain"]),
        Criterion("quality_preservation", "Сохранение качества", "benefit", weights["quality_preservation"]),
        Criterion("concept_fidelity", "Соответствие исходной концепции", "benefit", weights["concept_fidelity"]),
        Criterion("implementation_cost", "Стоимость внедрения", "cost", weights["implementation_cost"]),
        Criterion("late_penalty", "Штраф за позднее внедрение", "cost", weights["late_penalty"]),
        Criterion("risk", "Риск реализации", "cost", weights["risk"]),
        Criterion("resource_fit", "Соответствие ресурсным ограничениям", "benefit", weights["resource_fit"]),
        Criterion("confidence", "Достоверность оценки", "benefit", weights["confidence"]),
    ]

    matrix: list[list[float]] = []
    for method, applicability in evaluated:
        resource = rules.resource_fit(method, profile)
        risk_value = (method.complexity - 1) / 4.0 * 0.6 + (1 - method.confidence) * 0.4
        matrix.append([
            float(method.performance_gain),
            (method.quality_impact + 2) / 4.0,
            1.0 + method.concept_impact / 2.0,
            float(method.implementation_cost),
            applicability.late_penalty,
            risk_value,
            resource,
            float(method.confidence),
        ])

    scores = topsis(matrix, criteria)
    rows = criterion_matrix_rows(matrix, criteria)

    # Сортировка: по убыванию коэффициента близости, при равенстве — по коду (воспроизводимость).
    order = sorted(range(len(evaluated)), key=lambda i: (-scores[i], evaluated[i][0].code))

    recommendations: list[RecommendationOut] = []
    for rank, idx in enumerate(order, start=1):
        method, applicability = evaluated[idx]
        score = scores[idx]
        recommendations.append(_build_recommendation(
            db, method, functions, applicability, score, rank, rows[idx], profile, basket_codes
        ))

    # 9. Профиль нагрузки и совместимость корзины.
    basket_methods = [methods_by_code[c] for c in basket_codes if c in methods_by_code]
    load_profile = aggregate_load(basket_methods, profile)
    basket_conflicts, basket_synergies = basket_compatibility(db, basket_codes, methods_by_code)

    # Похожие игры и аппаратная оценка.
    examples = list(db.scalars(select(GameExample).where(GameExample.status == "published")))
    similar = [
        SimilarGameOut(
            example=serializers.example_out(ex),
            similarity=sim,
            matching_optimizations=match,
        )
        for ex, sim, match in gower.find_similar(profile, examples, top_n=5)
    ]
    hw = hardware.estimate_hardware(db, profile, basket_methods, similar_examples=len(similar))

    return RecommendationResult(
        profile=profile,
        risks=detect_risks(profile, basket_codes, methods_by_code),
        recommendations=recommendations,
        excluded=excluded,
        load_profile=load_profile,
        basket_conflicts=basket_conflicts,
        basket_synergies=basket_synergies,
        hardware=hw,
        similar_games=similar,
        meta={
            "candidates": len(candidates),
            "applicable": len(evaluated),
            "excluded": len(excluded),
            "algorithm": "TOPSIS (векторная нормализация, евклидово расстояние)",
            "weights": weights,
            "priority": profile.priority,
        },
    )


def _build_recommendation(
    db: Session, method: Method, functions: dict, applicability: rules.Applicability,
    score: float, rank: int, criteria_rows: list[dict], profile, basket_codes: list[str],
) -> RecommendationOut:
    flags: list[str] = []

    if score >= 0.55:
        flags.append("recommended")
    elif score >= 0.42:
        flags.append("conditional")
    else:
        flags.append("not_recommended")

    stage_order = DevStage(profile.stage).order if profile.stage in {s.value for s in DevStage} else 2
    method_stage = DevStage(method.recommended_stage).order if method.recommended_stage in {s.value for s in DevStage} else 2
    if stage_order <= method_stage:
        flags.append("implement_now")
    if method.late_cost in ("high", "critical") and applicability.stage_pressure > 0:
        flags.append("late_difficult")
    if method.requires_prototype or method.confidence < 0.7:
        flags.append("needs_prototyping")
    if method.quality_impact <= -1:
        flags.append("may_reduce_quality")
    if method.concept_impact <= -1:
        flags.append("may_change_concept")

    reasons: list[str] = []
    reasons.append(
        f"Ожидаемый эффект: {method.performance_gain:.0%} — {_gain_text(method.performance_gain)}."
    )
    reasons.append(
        f"Уровень решения: {_label(SolutionLevel, method.level)}; рекомендуемая стадия — "
        f"{_label(DevStage, method.recommended_stage)}."
    )
    if applicability.stage_pressure == 0:
        reasons.append("Текущая стадия проекта не позднее рекомендованной: стоимость внедрения минимальна.")
    else:
        reasons.append(
            f"Текущая стадия проекта позже рекомендованной: стоимость позднего внедрения — "
            f"{_label(LateCost, method.late_cost)}."
        )
    reasons.append(
        f"Способ расчёта: {_label(CalcMode, method.calc_mode)}."
    )
    positives = _impact_text(method)
    if positives:
        reasons.append("Снижает нагрузку на: " + ", ".join(positives) + ".")
    negatives = _impact_text(method, positive=False)
    if negatives:
        reasons.append("Увеличивает нагрузку на: " + ", ".join(negatives) + ".")
    if method.quality_impact:
        reasons.append(
            f"Влияние на качество: {method.quality_impact:+d} ({'улучшает' if method.quality_impact > 0 else 'снижает'})."
        )
    if method.concept_impact:
        reasons.append("Внимание: решение затрагивает исходную концепцию игры.")
    for condition in applicability.conditions:
        reasons.append("Условие: " + condition)

    # 8. Аналоги в выбранном движке.
    links = [link_out(db, l) for l in method.engine_links]
    links.sort(key=lambda l: (
        0 if l.engine_code == profile.engine else 1,
        RELATION_PRIORITY.index(l.relation_type) if l.relation_type in RELATION_PRIORITY else 99,
    ))
    support = next((l for l in links if l.engine_code == profile.engine), None)
    alternatives = [l for l in links if l.engine_code != profile.engine][:4]

    return RecommendationOut(
        method_code=method.code,
        method_name=method.name,
        function_code=method.function.code if method.function else None,
        function_name=(functions.get(method.function.code).name if method.function and method.function.code in functions else None),
        kind=method.kind,
        score=round(score, 4),
        rank=rank,
        flags=flags,
        flag_labels=[FLAG_LABELS[f] for f in flags],
        reasons=reasons,
        criteria=[CriterionScore(**row) for row in criteria_rows],
        engine_support=support,
        engine_alternatives=alternatives,
        summary=method.summary,
        performance_gain=method.performance_gain,
        implementation_cost=method.implementation_cost,
        complexity=method.complexity,
        late_cost=method.late_cost,
        recommended_stage=method.recommended_stage,
        quality_impact=method.quality_impact,
        concept_impact=method.concept_impact,
        source_url=method.source_url,
    )


def _build_excluded(method: Method, functions: dict, applicability: rules.Applicability, extra: str | None = None) -> RecommendationOut:
    reasons = list(applicability.excluded_reasons)
    if extra:
        reasons.append(extra)
    return RecommendationOut(
        method_code=method.code,
        method_name=method.name,
        function_code=method.function.code if method.function else None,
        function_name=(functions.get(method.function.code).name if method.function and method.function.code in functions else None),
        kind=method.kind,
        score=0.0,
        rank=0,
        flags=["not_recommended"],
        flag_labels=[FLAG_LABELS["not_recommended"]],
        reasons=reasons,
        excluded_reasons=reasons,
        summary=method.summary,
        performance_gain=method.performance_gain,
        implementation_cost=method.implementation_cost,
        complexity=method.complexity,
        late_cost=method.late_cost,
        recommended_stage=method.recommended_stage,
        quality_impact=method.quality_impact,
        concept_impact=method.concept_impact,
        source_url=method.source_url,
    )


def _gain_text(value: float) -> str:
    if value >= 0.7:
        return "высокий"
    if value >= 0.5:
        return "заметный"
    if value >= 0.3:
        return "умеренный"
    if value > 0:
        return "небольшой"
    return "отсутствует (решение повышает качество)"


RESOURCE_LABELS = {
    "cpu": "CPU", "gpu": "GPU", "ram": "RAM", "vram": "VRAM",
    "disk": "накопитель", "network": "сеть",
}


def _impact_text(method: Method, positive: bool = True) -> list[str]:
    impacts = {
        "cpu": method.impact_cpu, "gpu": method.impact_gpu, "ram": method.impact_ram,
        "vram": method.impact_vram, "disk": method.impact_disk, "network": method.impact_network,
    }
    out = []
    for key, value in impacts.items():
        if positive and value < 0:
            out.append(RESOURCE_LABELS[key])
        if not positive and value > 0:
            out.append(RESOURCE_LABELS[key])
    return out


# ---------------------------------------------------------------------------
# Агрегированный профиль нагрузки корзины
# ---------------------------------------------------------------------------
def aggregate_load(methods: list[Method], profile) -> LoadProfileOut:
    """Суммарное влияние выбранных решений на подсистемы (шкала 0..100)."""
    keys = ["cpu", "gpu", "ram", "vram", "disk", "network"]
    totals = {k: 0 for k in keys}
    for m in methods:
        totals["cpu"] += m.impact_cpu
        totals["gpu"] += m.impact_gpu
        totals["ram"] += m.impact_ram
        totals["vram"] += m.impact_vram
        totals["disk"] += m.impact_disk
        totals["network"] += m.impact_network

    per_resource: dict[str, dict] = {}
    for key in keys:
        raw = totals[key]
        # Нормализация: -6..+6 отображается в 0..100, нейтральное значение 50.
        normalized = max(0.0, min(100.0, 50.0 + raw * (50.0 / 6.0)))
        per_resource[key] = {
            "raw": raw,
            "normalized": round(normalized, 1),
            "label": RESOURCE_LABELS[key],
            "direction": "снижает" if raw < 0 else ("повышает" if raw > 0 else "не влияет"),
        }

    return LoadProfileOut(
        cpu=per_resource["cpu"]["normalized"],
        gpu=per_resource["gpu"]["normalized"],
        ram=per_resource["ram"]["normalized"],
        vram=per_resource["vram"]["normalized"],
        disk=per_resource["disk"]["normalized"],
        network=per_resource["network"]["normalized"],
        per_resource=per_resource,
    )


def basket_compatibility(db: Session, basket_codes: list[str], methods_by_code: dict[str, Method]) -> tuple[list, list]:
    """Проверить корзину на конфликты, зависимости и усиления."""
    conflicts: list[BasketConflictOut] = []
    synergies: list[BasketConflictOut] = []
    basket = set(basket_codes)
    for row in db.scalars(select(Conflict)):
        if row.a_code in basket and row.b_code in basket:
            a = methods_by_code.get(row.a_code)
            b = methods_by_code.get(row.b_code)
            item = BasketConflictOut(
                a_code=row.a_code, a_name=a.name if a else row.a_code,
                b_code=row.b_code, b_name=b.name if b else row.b_code,
                conflict_type=row.conflict_type,
                conflict_label=_label(ConflictType, row.conflict_type),
                severity=row.severity,
                description=row.description,
                resolution=row.resolution,
            )
            if row.conflict_type == "conflict":
                conflicts.append(item)
            else:
                synergies.append(item)

        # Зависимость, не закрытая корзиной.
        elif row.conflict_type == "dependency" and row.a_code in basket and row.b_code not in basket:
            a = methods_by_code.get(row.a_code)
            b = methods_by_code.get(row.b_code)
            if b is not None:
                conflicts.append(BasketConflictOut(
                    a_code=row.a_code, a_name=a.name if a else row.a_code,
                    b_code=row.b_code, b_name=b.name if b else row.b_code,
                    conflict_type="unmet_dependency",
                    conflict_label="незакрытая зависимость",
                    severity=row.severity,
                    description=f"Решение «{a.name if a else row.a_code}» требует «{b.name}»: {row.description}",
                    resolution=f"Добавить «{b.name}» в корзину или отказаться от «{a.name if a else row.a_code}».",
                ))

    conflicts.sort(key=lambda c: -c.severity)
    synergies.sort(key=lambda c: -c.severity)
    return conflicts, synergies
