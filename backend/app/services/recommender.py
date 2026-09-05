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

Важное разделение: **применимость** решения определяется экспертными правилами
(жёсткие ограничения проекта), а **порядок** — методом TOPSIS. Коэффициент
близости относителен по своей природе: при одной альтернативе он не несёт
информации о качестве, поэтому текстовая пометка «рекомендуется» из него
напрямую не выводится.
"""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import repositories, timeutil
from ..models.entities import Method
from ..models.enums import (
    CalcMode, ConflictType, DevStage, LateCost, SolutionLevel,
)
from ..schemas.catalog import (
    BasketConflictOut, CriterionScore, LoadProfileOut,
    RecommendationOut, RecommendationResult, RiskOut, SimilarGameOut, input_fingerprint,
)
from . import gower, hardware, rules, sensitivity, serializers
from .serializers import label_of as _label
from .serializers import link_out
from .topsis import Criterion, criterion_matrix_rows, topsis

#: Версия алгоритма. Меняется при любом изменении формул, весов или правил
#: отбора: по ней можно понять, какой версией получен сохранённый результат.
ALGORITHM_VERSION = "2.0.1"

#: Версия набора данных. Меняется при обновлении базы знаний, влияющем на
#: ранжирование (пересчёт индексов оборудования, пересмотр оценок эффекта).
DATASET_VERSION = "mvp-1.1"

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
    "lower_priority": "уступает другим вариантам",
    "single_option": "единственный применимый вариант",
    "comparison_limited": "сравнение ограничено",
    "implement_now": "желательно внедрить сейчас",
    "late_difficult": "позднее внедрение затруднено",
    "late_blocked": "внедрение на этой стадии практически закрыто",
    "needs_prototyping": "требует прототипирования",
    "may_reduce_quality": "может снизить качество",
    "may_change_concept": "может изменить концепцию",
    "not_recommended": "не рекомендуется",
}

RELATION_PRIORITY = ["direct", "automation", "partial", "alternative", "complement", "diagnostic", "limited", "missing"]


# ---------------------------------------------------------------------------
# Вспомогательные преобразования
# ---------------------------------------------------------------------------
def _function_name(functions: dict, method: Method) -> str | None:
    """Название игровой функции метода. Один помощник вместо двух копий."""
    if method.function and method.function.code in functions:
        return functions.get(method.function.code).name
    return None


# ---------------------------------------------------------------------------
# 1-2. Анализ проекта и выявление рисков
# ---------------------------------------------------------------------------
def conflict_map(db: Session) -> dict[str, list[str]]:
    """Карта конфликтующих пар, построенная для конкретного запроса.

    Раньше карта хранилась в глобальной переменной и перезаполнялась на каждый
    запрос. При параллельной обработке два запроса видели чужую карту: результат
    зависел от порядка выполнения. Карта строится локально и передаётся явно.
    """
    mapping: dict[str, list[str]] = {}
    for row in repositories.conflicts(db):
        if row.conflict_type != ConflictType.CONFLICT.value:
            continue
        mapping.setdefault(row.a_code, []).append(row.b_code)
        mapping.setdefault(row.b_code, []).append(row.a_code)
    return mapping


def detect_risks(
    profile,
    basket_codes: list[str],
    methods_by_code: dict[str, Method],
    conflicts: dict[str, list[str]] | None = None,
    engines: list | None = None,
) -> list[RiskOut]:
    risks: list[RiskOut] = []
    conflicts = conflicts or {}
    engines = engines or []
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

    # Версия движка вне перечня проверенных.
    #
    # Поле собиралось анкетой, но ни на что не влияло. Ничего не изобретаем:
    # версия не меняет ранжирование, но если её нет в списке известных для
    # движка, применимость инструментов требует проверки — об этом и сообщаем.
    version = (getattr(profile, "engine_version", "") or "").strip()
    if version:
        engine = next((e for e in engines if e.code == profile.engine), None)
        known = [str(v).lower() for v in (getattr(engine, "versions", None) or [])]
        if engine is not None and known and version.lower() not in known:
            add(
                "unknown_engine_version", "Версия движка не входит в перечень проверенных",
                "medium",
                f"Указана версия «{version}», тогда как в базе для {engine.name} известны: "
                f"{', '.join(str(v) for v in engine.versions)}. Применимость инструментов "
                "проверялась на других версиях.",
                "Проверить применимость выбранных решений на указанной версии "
                "или выбрать версию из перечня.",
            )

    # Конфликты внутри корзины.
    conflicting = [
        c for c in basket_codes
        if any(code in basket_codes for code in conflicts.get(c, []))
    ]
    if conflicting:
        add(
            "basket_conflict", "В корзине присутствуют конфликтующие решения",
            "high",
            "Часть выбранных решений взаимно исключает друг друга или дублирует стоимость.",
            "Проверить раздел совместимости набора и выбрать одну из альтернатив.",
        )

    # Срок разработки против стоимости выбранных решений.
    if profile.deadline_weeks:
        heavy = [
            code for code in basket_codes
            if methods_by_code.get(code) and methods_by_code[code].implementation_cost >= 4
        ]
        if heavy and profile.deadline_weeks < 4 * len(heavy):
            add(
                "deadline_pressure", "Срок разработки не покрывает выбранные решения",
                "high",
                f"До релиза {profile.deadline_weeks} недель, при этом {len(heavy)} выбранных "
                "решений относятся к трудоёмким. Внедрение всего набора за этот срок маловероятно.",
                "Оставить в плане только решения, которые можно внедрить в срок, "
                "остальные перенести в этап поддержки.",
            )
        elif heavy:
            add(
                "deadline_pressure", "Часть решений трудоёмка относительно срока",
                "medium",
                f"До релиза {profile.deadline_weeks} недель, {len(heavy)} выбранных решений "
                "требуют существенных затрат на внедрение.",
                "Проверить, что трудоёмкие решения запланированы на ранние этапы.",
            )

    return risks


# ---------------------------------------------------------------------------
# 3-8. Подбор, фильтрация и ранжирование
# ---------------------------------------------------------------------------
def build_recommendations(db: Session, profile, basket_codes: list[str]) -> RecommendationResult:
    conflicts = conflict_map(db)
    engines = repositories.engines(db)

    # Публичный снимок: функции, методы, примеры и оборудование — только
    # опубликованные записи. Корзина тоже фильтруется: неопубликованный метод
    # не должен попадать в расчёт даже по прямому коду.
    functions = {f.code: f for f in repositories.functions(db)}
    all_methods = repositories.methods(db)
    methods_by_code = {m.code: m for m in all_methods}
    examples = repositories.examples(db)
    basket_methods = repositories.methods_by_codes(db, basket_codes)

    calculated_at = timeutil.utcnow_iso()

    # 3. Кандидаты: методы для выбранных функций плюс общие методы без функции.
    # Общие методы (kind=optimization, function=None) проходят тот же фильтр
    # правил: нерелевантные отсекаются через requires_features и applicability,
    # а не молчаливым отсутствием в выдаче.
    selected = set(profile.functions)
    candidates = [m for m in all_methods
                  if (m.function is None or m.function.code in selected)]

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
        tail = _tail(db, profile, basket_methods, basket_codes, methods_by_code, conflicts, engines, examples)
        return RecommendationResult(
            profile=profile,
            risks=tail["risks"],
            recommendations=[],
            excluded=excluded,
            load_profile=tail["load_profile"],
            basket_conflicts=tail["basket_conflicts"],
            basket_dependencies=tail["basket_dependencies"],
            basket_synergies=tail["basket_synergies"],
            hardware=tail["hardware"],
            similar_games=tail["similar"],
            basket_codes=basket_codes,
            input_key=tail["input_key"],
            meta=_meta(profile, weights={}, candidates=len(candidates), applicable=0,
                       excluded=len(excluded), calculated_at=calculated_at,
                       note="Ни одно решение не прошло проверку обязательных ограничений проекта."),
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

    result = topsis(matrix, criteria)
    scores = result.scores
    rows = criterion_matrix_rows(matrix, criteria)

    # Сортировка: по убыванию коэффициента близости, при равенстве — по коду (воспроизводимость).
    order = sorted(range(len(evaluated)), key=lambda i: (-scores[i], evaluated[i][0].code))
    total = len(evaluated)

    # Устойчивость рангов: тот же тай-брейк, что и выше, иначе вилка врёт.
    stability = sensitivity.analyze(
        matrix, criteria, [method.code for method, _ in evaluated],
    )

    recommendations: list[RecommendationOut] = []
    for rank, idx in enumerate(order, start=1):
        method, applicability = evaluated[idx]
        recommendations.append(_build_recommendation(
            db, method, functions, applicability, scores[idx], rank, total, rows[idx],
            profile, comparable=result.comparable, compare_reason=result.reason,
            stability=stability.get(method.code) if stability else None,
        ))

    tail = _tail(db, profile, basket_methods, basket_codes, methods_by_code, conflicts, engines, examples)

    return RecommendationResult(
        profile=profile,
        risks=tail["risks"],
        recommendations=recommendations,
        excluded=excluded,
        load_profile=tail["load_profile"],
        basket_conflicts=tail["basket_conflicts"],
        basket_dependencies=tail["basket_dependencies"],
        basket_synergies=tail["basket_synergies"],
        hardware=tail["hardware"],
        similar_games=tail["similar"],
        basket_codes=basket_codes,
        input_key=tail["input_key"],
        meta=_meta(
            profile, weights=weights, candidates=len(candidates), applicable=len(evaluated),
            excluded=len(excluded), calculated_at=calculated_at,
            comparable=result.comparable,
            compare_reason=result.reason or None,
            note=(
                "Сравнение решений ограничено: " + result.reason
                if not result.comparable else None
            ),
        ),
    )


def _tail(db: Session, profile, basket_methods, basket_codes, methods_by_code, conflicts, engines, examples) -> dict:
    """Общая хвостовая часть результата: одинакова для пустого и полного расчёта.

    Раньше обе ветки `build_recommendations` собирали похожие игры,
    совместимость корзины, нагрузку и железо каждая по-своему — правка одной
    забывала вторую. Теперь сборка в одном месте.
    """
    similar = [
        SimilarGameOut(
            example=serializers.example_out(ex),
            similarity=sim,
            matching_optimizations=match,
        )
        for ex, sim, match in gower.find_similar(
            profile, examples, top_n=5, basket=[m.code for m in basket_methods]
        )
    ]
    basket_conflicts, basket_dependencies, basket_synergies = basket_compatibility(
        db, basket_codes, methods_by_code
    )
    return {
        "similar": similar,
        "basket_conflicts": basket_conflicts,
        "basket_dependencies": basket_dependencies,
        "basket_synergies": basket_synergies,
        "load_profile": aggregate_load(basket_methods, profile),
        "hardware": hardware.estimate_hardware(db, profile, basket_methods, similar_examples=len(similar)),
        "risks": detect_risks(profile, basket_codes, methods_by_code, conflicts, engines),
        "input_key": input_fingerprint(profile, [m.code for m in basket_methods]),
    }


def _meta(
    profile,
    *,
    weights: dict[str, float],
    candidates: int,
    applicable: int,
    excluded: int,
    calculated_at: str,
    comparable: bool = True,
    compare_reason: str | None = None,
    note: str | None = None,
) -> dict:
    """Служебные сведения о расчёте.

    Версия алгоритма, версия набора данных, веса и время расчёта сохраняются
    вместе с результатом: без них нельзя объяснить, почему два сохранённых
    расчёта для одного профиля различаются.
    """
    meta: dict = {
        "candidates": candidates,
        "applicable": applicable,
        "excluded": excluded,
        "algorithm": "TOPSIS (векторная нормализация, евклидово расстояние)",
        "algorithm_version": ALGORITHM_VERSION,
        "dataset_version": DATASET_VERSION,
        "weights": weights,
        "priority": profile.priority,
        "calculated_at": calculated_at,
        "comparable": comparable,
    }
    if compare_reason:
        meta["compare_reason"] = compare_reason
    if note:
        meta["note"] = note
    return meta


def _stage_order(value: str) -> int:
    """Порядковый номер стадии; неизвестное значение — середина шкалы."""
    return DevStage(value).order if value in {s.value for s in DevStage} else 2


def _recommendation_flags(
    method: Method, applicability: rules.Applicability, rank: int, total: int,
    *, comparable: bool, stage_order: int, method_stage: int, late_blocked: bool,
) -> list[str]:
    """Пометки решения: абсолютные признаки + относительное место в списке."""
    flags: list[str] = []
    if late_blocked:
        flags.append("not_recommended")
        flags.append("late_blocked")
    if comparable:
        share = rank / max(1, total)
        if share <= 1 / 3:
            flags.append("recommended")
        elif share <= 2 / 3:
            flags.append("conditional")
        else:
            flags.append("lower_priority")
    else:
        # Единственный или неразличимый набор: относительного порядка нет,
        # и утверждать «не рекомендуется» было бы неправдой.
        flags.append("single_option" if total == 1 else "comparison_limited")
    if stage_order <= method_stage:
        flags.append("implement_now")
    if method.late_cost in ("high", "critical") and applicability.stage_pressure > 0 and not late_blocked:
        flags.append("late_difficult")
    if method.requires_prototype or method.confidence < 0.7:
        flags.append("needs_prototyping")
    if method.quality_impact <= -1:
        flags.append("may_reduce_quality")
    if method.concept_impact <= -1:
        flags.append("may_change_concept")
    return flags


def _recommendation_reasons(
    method: Method, applicability: rules.Applicability, score: float,
    rank: int, total: int, *, comparable: bool, compare_reason: str = "",
) -> list[str]:
    """Человекочитаемое объяснение рекомендации."""
    reasons: list[str] = [
        f"Ожидаемый эффект: {method.performance_gain:.0%} — {_gain_text(method.performance_gain)}."
    ]
    if comparable:
        reasons.append(
            f"Место {rank} из {total} допустимых решений; коэффициент близости {score:.2f}."
        )
    else:
        reasons.append(
            "Относительное сравнение невозможно: "
            f"{compare_reason or 'альтернативы не различаются'}. "
            "Решение применимо к проекту, но оценено без сопоставления с другими."
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
    reasons.append(f"Способ расчёта: {_label(CalcMode, method.calc_mode)}.")
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
    return reasons


def _engine_support(db: Session, method: Method, engine_code: str):
    """Аналог метода в выбранном движке + альтернативы из других движков."""
    links = [link_out(db, link) for link in repositories.method_links(db, method.id)]
    links.sort(key=lambda link: (
        0 if link.engine_code == engine_code else 1,
        RELATION_PRIORITY.index(link.relation_type) if link.relation_type in RELATION_PRIORITY else 99,
    ))
    support = next((link for link in links if link.engine_code == engine_code), None)
    alternatives = [link for link in links if link.engine_code != engine_code][:4]
    return support, alternatives


def _build_recommendation(
    db: Session, method: Method, functions: dict, applicability: rules.Applicability,
    score: float, rank: int, total: int, criteria_rows: list[dict], profile,
    *, comparable: bool = True, compare_reason: str = "",
    stability: sensitivity.Stability | None = None,
) -> RecommendationOut:
    # Метод сюда попадает только применимым, поэтому «не рекомендуется» здесь
    # возможно лишь по абсолютному признаку — окно внедрения закрыто стадией.
    stage_order = _stage_order(profile.stage)
    method_stage = _stage_order(method.recommended_stage)
    late_blocked = (
        method.late_cost == "critical"
        and applicability.stage_pressure >= 1.0
        and stage_order > method_stage
    )
    flags = _recommendation_flags(
        method, applicability, rank, total, comparable=comparable,
        stage_order=stage_order, method_stage=method_stage, late_blocked=late_blocked,
    )
    reasons = _recommendation_reasons(
        method, applicability, score, rank, total,
        comparable=comparable, compare_reason=compare_reason,
    )
    support, alternatives = _engine_support(db, method, profile.engine)

    return RecommendationOut(
        method_code=method.code,
        method_name=method.name,
        function_code=method.function.code if method.function else None,
        function_name=_function_name(functions, method),
        kind=method.kind,
        score=round(score, 4),
        rank=rank,
        flags=flags,
        flag_labels=[FLAG_LABELS[f] for f in flags],
        reasons=reasons,
        criteria=[CriterionScore(**row) for row in criteria_rows],
        stability=(
            {"rank_min": stability.rank_min, "rank_max": stability.rank_max,
             "stable": stability.stable}
            if stability is not None else None
        ),
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
        function_name=_function_name(functions, method),
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


def basket_compatibility(
    db: Session, basket_codes: list[str], methods_by_code: dict[str, Method]
) -> tuple[list[BasketConflictOut], list[BasketConflictOut], list[BasketConflictOut]]:
    """Проверить корзину и вернуть три самостоятельные категории связей.

    Раньше всё, что не является конфликтом, попадало в «усиления». Из-за этого
    закрытая зависимость, при которой одно решение просто не работает без
    другого, показывалась как «усиливающее сочетание» — то есть как достоинство
    набора. Категории разделены: конфликты, зависимости, усиления.
    """
    conflicts: list[BasketConflictOut] = []
    dependencies: list[BasketConflictOut] = []
    synergies: list[BasketConflictOut] = []
    basket = set(basket_codes)

    def item(row, conflict_type: str, label: str, description: str, resolution: str) -> BasketConflictOut:
        a = methods_by_code.get(row.a_code)
        b = methods_by_code.get(row.b_code)
        return BasketConflictOut(
            a_code=row.a_code, a_name=a.name if a else row.a_code,
            b_code=row.b_code, b_name=b.name if b else row.b_code,
            conflict_type=conflict_type, conflict_label=label,
            severity=row.severity, description=description, resolution=resolution,
        )

    for row in repositories.conflicts(db):
        pair_in_basket = row.a_code in basket and row.b_code in basket
        if row.conflict_type == ConflictType.CONFLICT.value:
            if pair_in_basket:
                conflicts.append(item(
                    row, row.conflict_type, _label(ConflictType, row.conflict_type),
                    row.description, row.resolution,
                ))
        elif row.conflict_type == ConflictType.DEPENDENCY.value:
            if pair_in_basket:
                dependencies.append(item(
                    row, "dependency", _label(ConflictType, row.conflict_type),
                    row.description or "Одно решение опирается на другое.",
                    row.resolution or "Сохранять оба решения в плане.",
                ))
            elif row.a_code in basket and row.b_code not in basket:
                # Зависимость не закрыта: решение в корзине не сработает в одиночку.
                b = methods_by_code.get(row.b_code)
                if b is not None:
                    conflicts.append(item(
                        row, "unmet_dependency", "незакрытая зависимость",
                        f"Решение «{methods_by_code.get(row.a_code).name if methods_by_code.get(row.a_code) else row.a_code}» "
                        f"требует «{b.name}»: {row.description}",
                        f"Добавить «{b.name}» в корзину или отказаться от решения «{row.a_code}».",
                    ))
        elif row.conflict_type == ConflictType.SYNERGY.value:
            if pair_in_basket:
                synergies.append(item(
                    row, row.conflict_type, _label(ConflictType, row.conflict_type),
                    row.description, row.resolution,
                ))

    conflicts.sort(key=lambda c: -c.severity)
    dependencies.sort(key=lambda c: -c.severity)
    synergies.sort(key=lambda c: -c.severity)
    return conflicts, dependencies, synergies
