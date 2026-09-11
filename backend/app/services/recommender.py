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

from collections.abc import Sequence

from sqlalchemy.orm import Session

from .. import repositories, timeutil
from ..models.entities import Method
from ..models.enums import (
    CalcMode, ConflictType, DevStage, EffectScope, LateCost, SolutionLevel,
)
from ..schemas.catalog import (
    BasketConflictOut, CriterionScore, HardwareEstimateOut, LoadProfileOut,
    RecommendationOut, RecommendationResult, RiskOut, StageGuidanceOut,
    input_fingerprint,
)
from ..seed.methods_data import FUNCTION_ASSIGNMENTS
from . import engines as engine_service
from . import evidence as evidence_service
from . import hardware, rules, sensitivity, serializers, stage_guidance, transitions
from .serializers import label_of as _label
from .serializers import link_out
from .topsis import Criterion, criterion_matrix_rows, equivalence_group, topsis, EQUIVALENCE_TOLERANCE

#: Версия алгоритма. Меняется при любом изменении формул, весов или правил
#: отбора: по ней можно понять, какой версией получен сохранённый результат.
#: 2.3.0 — область прогноза только Windows/Linux ПК, CPU следует за базовым
#: рендером при генерации кадров, unified-память без универсальной скидки.
ALGORITHM_VERSION = "2.5.1"

#: Версия набора данных. Меняется при обновлении базы знаний, влияющем на
#: ранжирование (пересчёт индексов оборудования, пересмотр оценок эффекта).
DATASET_VERSION = "mvp-1.8"

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
    "tied_leader": "равнозначно с лидером",
    "implement_now": "желательно внедрить сейчас",
    "late_difficult": "позднее внедрение затруднено",
    "needs_rework": "проверить объём переработки",
    "needs_prototyping": "требует прототипирования",
    "may_reduce_quality": "может снизить качество",
    "may_change_concept": "может изменить концепцию",
    "not_recommended": "не рекомендуется",
}

RELATION_PRIORITY = ["direct", "automation", "partial", "alternative", "complement", "diagnostic", "limited", "missing"]
# Эти оптимизации имеют родительскую подсистему для классификации и расчёта,
# но остаются сквозными кандидатами: пользователю не нужно выбирать отдельную
# функцию «PSO» или «патчи», чтобы увидеть соответствующий метод.
CROSS_CUTTING_METHODS = frozenset(FUNCTION_ASSIGNMENTS)


# ---------------------------------------------------------------------------
# Вспомогательные преобразования
# ---------------------------------------------------------------------------
def _function_name(functions: dict, method: Method) -> str | None:
    """Название игровой функции метода. Один помощник вместо двух копий."""
    if method.function and method.function.code in functions:
        return functions.get(method.function.code).name
    return None


def _recommendation_function(method: Method) -> tuple[str | None, str | None]:
    """Вернуть область показа метода, сохраняя общий список оптимизаций."""
    if method.function is None:
        return method.code, method.name
    return method.function.code, method.function.name


# ---------------------------------------------------------------------------
# 1-2. Анализ проекта и выявление рисков
# ---------------------------------------------------------------------------
def conflict_map(db: Session) -> dict[str, list[str]]:
    """Карта конфликтующих пар, построенная для конкретного запроса.

    Раньше карта хранилась в глобальной переменной и перезаполнялась на каждый
    запрос. При параллельной обработке два запроса видели чужую карту: результат
    зависел от порядка выполнения. Карта строится локально и передаётся явно.
    Учитываются только HARD_CONFLICT и RISK — остальные типы не исключают методы.
    """
    mapping: dict[str, list[str]] = {}
    for row in repositories.conflicts(db):
        if row.conflict_type not in {ConflictType.HARD_CONFLICT.value, ConflictType.RISK.value}:
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
    known_function_codes: set[str] | None = None,
    version_notes: list[str] | None = None,
) -> list[RiskOut]:
    risks: list[RiskOut] = []
    conflicts = conflicts or {}
    engines = engines or []
    stage_order = DevStage(profile.stage).order if profile.stage in {s.value for s in DevStage} else 2

    def add(code: str, title: str, severity: str, description: str, advice: str) -> None:
        risks.append(RiskOut(code=code, title=title, severity=severity, description=description, advice=advice))

    unknown_methods = sorted(set(basket_codes) - set(methods_by_code))
    if unknown_methods:
        add(
            "unknown_method", "Метод отсутствует в опубликованном каталоге", "high",
            "Следующие коды из корзины не сопоставлены с опубликованными методами и не "
            "учтены в рекомендациях и аппаратной оценке: " + ", ".join(unknown_methods) + ".",
            "Зафиксировать метод в каталоге знаний или удалить его из входных данных до повторного расчёта.",
        )

    if known_function_codes is not None:
        unknown_functions = sorted(set(profile.functions) - known_function_codes)
        if unknown_functions:
            add(
                "unknown_function", "Функция отсутствует в опубликованном каталоге", "high",
                "Следующие функции профиля не сопоставлены с каталогом и получили только общий "
                "нейтральный вклад в аппаратной оценке: " + ", ".join(unknown_functions) + ".",
                "Добавить функцию и её методы реализации в каталог либо выбрать существующую функцию.",
            )

    # Поздняя стадия без архитектурных решений.
    if stage_order >= DevStage.ALPHA.order and profile.world_type in ("open_world", "procedural"):
        if not any(methods_by_code[c].function and methods_by_code[c].function.code == "open_world_streaming"
                   for c in basket_codes if c in methods_by_code):
            add(
                "late_streaming", "Отсутствует решение по стримингу открытого мира",
                "high",
                "Проект с открытым миром находится на поздней стадии, но потоковая загрузка мира "
                "не указана в корзине. Это не доказывает её отсутствие в проекте; проверить существующую реализацию и возможный объём переделок.",
                "Оценить возможность частичного внедрения плиточной загрузки или зафиксировать "
                "ограничение размера мира.",
            )

    # Поздняя стадия и архитектурные изменения.
    if stage_order >= DevStage.ALPHA.order:
        arch_missing = [
            m.code for m in methods_by_code.values()
            if m.code not in basket_codes and m.level == "architecture" and m.late_cost == "critical"
            and m.function and m.function.code in profile.functions and rules.evaluate(m, profile).applicable
        ]
        if arch_missing:
            add(
                "architecture_locked", "Проверить стоимость архитектурных изменений",
                "high",
                f"На текущей стадии внедрение {len(arch_missing)} архитектурных решений имеет "
                "высокий экспертный риск позднего внедрения. Стадия не доказывает необходимость полной переработки.",
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

    # Сетевая функция без флага мультиплеера: либо флаг забыт, либо функция лишняя.
    if not profile.multiplayer and "multiplayer_netcode" in (profile.functions or []):
        add(
            "network_without_flag", "Сетевая функция при выключенном мультиплеере",
            "medium",
            "Выбрана функция сетевого кода, но мультиплеер в анкете выключен: либо флаг "
            "пропущен, либо функция не нужна проекту.",
            "Включить мультиплеер и указать число игроков либо убрать функцию из анкеты.",
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

    # Встроенный инструмент движка отсутствует в выбранной версии.
    #
    # Название инструмента не подтверждает его наличие в конкретной версии:
    # Nanite нет в UE 4.27. Решение остаётся в расчёте — меняется способ
    # получения эффекта и стоимость внедрения, а не физическая нагрузка.
    if version_notes:
        add(
            "engine_tool_version", "Встроенный инструмент отсутствует в версии движка",
            "medium",
            " ".join(version_notes)
            + " Готовый аналог в этой версии недоступен: эффект достигается собственной "
            "реализацией, а не настройкой встроенной подсистемы.",
            "Проверить версию движка либо заложить собственную реализацию и её стоимость.",
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
def build_recommendations(db: Session, profile, basket_codes: list[str], baseline=None) -> RecommendationResult:
    # Freeze the catalogue cards used by every view, including printed reports.
    from .catalog_revision import published_revision

    basket_codes = sorted(set(basket_codes))
    profile = profile.model_copy(update={
        "functions": sorted(set(profile.functions)),
        "platforms": sorted(set(profile.platforms)),
    })
    result = _build_recommendations(db, profile, basket_codes, baseline)
    selected = repositories.methods_by_codes(db, basket_codes)
    accounted, _ = rules.assess_selected_methods(selected, profile, repositories.conflicts(db))
    result.selected_methods = [
        serializers.method_to_out_public(db, method, profile=profile) for method in selected
    ]
    result.accounted_method_codes = sorted(method.code for method in accounted)
    result.catalog_revision = published_revision(db)
    result.meta["dataset_version"] = result.catalog_revision
    result.baseline = baseline
    relations = repositories.conflicts(db)
    methods = {m.code: m for m in repositories.methods(db)}
    result.transitions = [transitions.assess(m, profile, baseline, methods, relations, basket_codes) for m in selected]
    result.transitions.extend(transitions.removed(baseline, basket_codes, relations))
    if baseline:
        unknown = sorted(set(baseline.basket) - set(methods))
        if unknown:
            result.risks.append(RiskOut(code="unknown_baseline", title="Неполная реализованная основа", severity="high",
                                       description="В каталоге отсутствуют: " + ", ".join(unknown),
                                       advice="Уточнить исходную реализацию; стоимость перехода неполна."))
    result.input_key = input_fingerprint(profile, basket_codes, ALGORITHM_VERSION, result.catalog_revision, baseline)
    return result


def _build_recommendations(db: Session, profile, basket_codes: list[str], baseline=None) -> RecommendationResult:
    conflicts = conflict_map(db)
    engines = repositories.engines(db)

    # Публичный снимок: функции, методы, примеры и оборудование — только
    # опубликованные записи. Корзина тоже фильтруется: неопубликованный метод
    # не должен попадать в расчёт даже по прямому коду.
    functions = {f.code: f for f in repositories.functions(db)}
    all_methods = repositories.methods(db)
    methods_by_code = {m.code: m for m in all_methods}
    basket_methods = repositories.methods_by_codes(db, basket_codes)
    relations = repositories.conflicts(db)
    transition_map = {m.code: transitions.assess(m, profile, baseline, methods_by_code, relations, basket_codes) for m in all_methods}

    calculated_at = timeutil.utcnow_iso()

    # 3. Кандидаты: методы для выбранных функций плюс общие методы без функции.
    # Общие методы (kind=optimization, function=None) проходят тот же фильтр
    # правил: нерелевантные отсекаются через requires_features и applicability,
    # а не молчаливым отсутствием в выдаче.
    selected = set(profile.functions)
    candidates = [m for m in all_methods if (
        m.function is None
        or m.function.code in selected
        or m.code in CROSS_CUTTING_METHODS
    )]

    # 4-5. Исключение и оценка применимости.
    evaluated: list[tuple[Method, rules.Applicability]] = []
    excluded: list[RecommendationOut] = []
    for method in candidates:
        retained = transition_map[method.code].status == "retained"
        applicability = rules.evaluate(method, profile.model_copy(update={"complexity_tolerance": None}) if retained else profile)
        if retained:
            applicability.late_penalty = 0
            applicability.stage_pressure = 0
            applicability.conditions = [c for c in applicability.conditions if not c.startswith("Текущая стадия")]
        if not applicability.applicable:
            excluded.append(_build_excluded(method, functions, applicability))
            continue
        if not rules.min_scale_satisfied(method, profile):
            excluded.append(_build_excluded(
                method, functions, applicability,
                extra=f"Метод оправдан при масштабе мира не ниже «{method.min_scale}».",
            ))
            continue
        # Стадия не исключает решение: она определяет стоимость внедрения.
        # Архитектурное решение на релизе не исчезает из физической модели —
        # выбранная работающая реализация продолжает учитываться и в корзине,
        # и в аппаратной оценке. Календарный запрет удалял решение из выдачи,
        # оставляя его в расчёте, из-за чего список и корзина расходились.
        # Вместо запрета решение помечается как требующее переработки.
        if not retained and stage_guidance.needs_rework(method, profile.stage):
            applicability.conditions.append(stage_guidance.rework_note(method, profile.stage))
        evaluated.append((method, applicability))

    if not evaluated:
        # Ни одно решение не прошло фильтр обязательных ограничений. Профиль
        # нагрузки и аппаратная оценка всё равно возвращаются: пользователю
        # важно видеть причины исключения и ориентир по железу.
        tail = _tail(
            db, profile, basket_methods, basket_codes, methods_by_code,
            conflicts, engines, set(functions),
        )
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
            practice_check=tail["practice_check"],
            evidence_summary=tail["evidence_summary"],
            contributions=tail["contributions"],
            basket_codes=basket_codes,
            input_key=tail["input_key"],
            stage_guidance=_stage_guidance_out(profile.stage),
            meta=_meta(profile, weights={}, candidates=len(candidates), applicable=0,
                       excluded=len(excluded), calculated_at=calculated_at,
                       note="Ни одно решение не прошло проверку обязательных ограничений проекта."),
        )

    # 6. Матрица решений и TOPSIS.
    weights = WEIGHT_PROFILES.get(profile.priority, WEIGHT_PROFILES["balanced"])
    criteria = [
        Criterion("performance_gain", "Экспертная оценка эффекта", "benefit", weights["performance_gain"]),
        Criterion("quality_preservation", "Сохранение качества", "benefit", weights["quality_preservation"]),
        Criterion("concept_fidelity", "Соответствие исходной концепции", "benefit", weights["concept_fidelity"]),
        Criterion("implementation_cost", "Стоимость внедрения", "cost", weights["implementation_cost"]),
        Criterion("late_penalty", "Штраф за позднее внедрение", "cost", weights["late_penalty"]),
        Criterion("risk", "Риск реализации", "cost", weights["risk"]),
        Criterion("resource_fit", "Соответствие ресурсным ограничениям", "benefit", weights["resource_fit"]),
        Criterion("confidence", "Достоверность оценки", "benefit", weights["confidence"]),
    ]

    matrix: list[list[float]] = []
    # Technical demand contributes to resource fit, independently within each
    # function. An unrelated function must not reshuffle this comparison.
    function_workloads = {}
    for method, applicability in evaluated:
        key, _ = _recommendation_function(method)
        if key not in function_workloads:
            scoped_profile = profile.model_copy(update={"functions": [key] if method.function else []})
            model = hardware.build_model(scoped_profile, [], None)
            cpu_work, gpu_work = sum(model.cpu.values()), sum(model.gpu.values())
            function_workloads[key] = {
                "cpu": cpu_work / (cpu_work + model.budget_ms),
                "gpu": gpu_work / (gpu_work + model.budget_ms),
            }
        workload = function_workloads[key] if rules.effect_scope_of(method) == EffectScope.CLIENT else None
        resource = rules.resource_fit(method, profile, workload)
        transition = transition_map[method.code]
        risk_value = (transition.complexity_min + transition.complexity_max) / 10 if baseline else (method.complexity - 1) / 4.0
        late_penalty = applicability.late_penalty
        if transition.status != "retained" and stage_guidance.needs_rework(method, profile.stage):
            # Переработка удорожает внедрение, но не запрещает его: решение
            # остаётся в списке и просто уступает в порядке внедрения.
            late_penalty *= stage_guidance.REWORK_PENALTY_MULTIPLIER
        matrix.append([
            float(method.performance_gain),
            (method.quality_impact + 2) / 4.0,
            1.0 + method.concept_impact / 2.0,
            (transition.cost_min + transition.cost_max) / 2,
            late_penalty,
            risk_value,
            resource,
            float(method.confidence),
        ])

    # Compare alternatives only within the function whose implementation they solve.
    groups: dict[str | None, list[int]] = {}
    for index, (method, _) in enumerate(evaluated):
        key, _ = _recommendation_function(method)
        groups.setdefault(key, []).append(index)
    recommendations: list[RecommendationOut] = []
    comparison_notes: list[str] = []
    all_comparable = True
    for function_code, indices in sorted(groups.items(), key=lambda item: item[0] or ""):
        group_matrix = [matrix[index] for index in indices]
        group_methods = [evaluated[index] for index in indices]
        ranking = topsis(group_matrix, criteria)
        rows = criterion_matrix_rows(group_matrix, criteria)
        stability = sensitivity.analyze(group_matrix, criteria, [method.code for method, _ in group_methods])
        order = sorted(range(len(indices)), key=lambda index: (-ranking.scores[index], group_methods[index][0].code))
        if not ranking.comparable:
            all_comparable = False
            comparison_notes.append(f"{function_code or 'general'}: {ranking.reason}")
        # Группа равнозначных: разница с лидером меньше порога различимости
        # TOPSIS, поэтому строгий топ-1 в этой группе — артефакт округления
        # экспертных баллов, а не результат сравнения.
        tied = equivalence_group(ranking.scores) if ranking.comparable else [False] * len(indices)
        leader_score = max(ranking.scores) if ranking.scores else 0.0
        tied_count = sum(tied)
        for rank, index in enumerate(order, start=1):
            method, applicability = group_methods[index]
            recommendations.append(_build_recommendation(
                db, method, functions, applicability, ranking.scores[index], rank,
                len(indices), rows[index], profile, comparable=ranking.comparable,
                compare_reason=ranking.reason,
                stability=stability.get(method.code) if stability else None,
                tied_with_leader=tied[index],
                score_gap=leader_score - ranking.scores[index],
                tied_count=tied_count,
                transition=transition_map[method.code],
            ))

    tail = _tail(
        db, profile, basket_methods, basket_codes, methods_by_code,
        conflicts, engines, set(functions),
    )

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
        practice_check=tail["practice_check"],
        evidence_summary=tail["evidence_summary"],
        contributions=tail["contributions"],
        basket_codes=basket_codes,
        input_key=tail["input_key"],
        stage_guidance=_stage_guidance_out(profile.stage),
        meta=_meta(
            profile, weights=weights, candidates=len(candidates), applicable=len(evaluated),
            excluded=len(excluded), calculated_at=calculated_at,
            comparable=all_comparable,
            compare_reason="; ".join(comparison_notes) or None,
            note=(
                "Сравнение решений ограничено: " + "; ".join(comparison_notes)
                if not all_comparable else None
            ),
        ),
    )


def _stage_guidance_out(stage: str) -> StageGuidanceOut:
    """Блок «что означает текущая стадия» в публичном ответе."""
    return stage_guidance.guidance_out(stage)


def _tail(
    db: Session, profile, basket_methods, basket_codes, methods_by_code, conflicts,
    engines, known_function_codes: set[str],
) -> dict:
    """Общая хвостовая часть результата: одинакова для пустого и полного расчёта.

    Раньше обе ветки `build_recommendations` собирали совместимость корзины,
    нагрузку и железо каждая по-своему — правка одной забывала вторую.
    Теперь сборка в одном месте.
    """
    relations = repositories.conflicts(db)
    estimate = hardware.estimate_hardware(db, profile, basket_methods)
    case_codes = [method.code for method in basket_methods]
    cases = evidence_service.cases_for_methods(db, case_codes)
    basket_conflicts, basket_dependencies, basket_synergies = basket_compatibility(
        db, basket_codes, methods_by_code
    )
    return {
        "basket_conflicts": basket_conflicts,
        "basket_dependencies": basket_dependencies,
        "basket_synergies": basket_synergies,
        "load_profile": aggregate_load(basket_methods, profile, relations=relations, estimate=estimate),
        "hardware": estimate,
        "practice_check": evidence_service.practice_check(cases),
        "evidence_summary": evidence_service.summary(db),
        "contributions": hardware.build_contributions(
            profile, basket_methods, estimate, relations=relations,
        ),
        "risks": detect_risks(
            profile, basket_codes, methods_by_code, conflicts, engines, known_function_codes,
            version_notes=engine_service.method_version_notes(db, profile, basket_methods),
        ),
        "input_key": input_fingerprint(
            profile, [m.code for m in basket_methods],
            algorithm_version=ALGORITHM_VERSION, dataset_version=DATASET_VERSION,
        ),
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
    *, comparable: bool, stage_order: int, method_stage: int, needs_rework: bool,
    tied_with_leader: bool = False,
) -> list[str]:
    """Пометки решения: абсолютные признаки + относительное место в списке.

    Переработка не является запретом, поэтому она не заменяет пометку места
    в ранге: решение остаётся сопоставимым с остальными и дополнительно
    помечается стоимостью внедрения.
    """
    flags: list[str] = []
    rank_flags: list[str] = []
    if comparable:
        share = rank / max(1, total)
        if rank == 1 or share <= 1 / 3:
            rank_flags.append("recommended")
        elif share <= 2 / 3:
            rank_flags.append("conditional")
        else:
            rank_flags.append("lower_priority")
    else:
        # Единственный или неразличимый набор: относительного порядка нет,
        # и утверждать «не рекомендуется» было бы неправдой.
        rank_flags.append("single_option" if total == 1 else "comparison_limited")
    flags.extend(rank_flags)
    if needs_rework:
        flags.append("needs_rework")
    if tied_with_leader and rank > 1:
        flags.append("tied_leader")
    if stage_order <= method_stage:
        flags.append("implement_now")
    if method.late_cost in ("high", "critical") and applicability.stage_pressure > 0 and not needs_rework:
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
    tied_with_leader: bool = False,
    score_gap: float = 0.0,
    tied_count: int = 1,
) -> list[str]:
    """Человекочитаемое объяснение рекомендации."""
    reasons: list[str] = [
        f"Экспертный балл эффекта: {method.performance_gain:.2f} из 1. Это не измеренный процент ускорения."
    ]
    if comparable:
        if tied_with_leader and rank > 1:
            reasons.append(
                f"Разница с лидером группы ({score_gap:.3f}) меньше порога различимости "
                f"({EQUIVALENCE_TOLERANCE}): по критериям решения равнозначны, выбирайте по соответствию задаче."
            )
        elif rank == 1 and tied_count > 1:
            reasons.append(
                f"В группе {tied_count} равнозначных решений: различия коэффициента близости "
                f"в пределах порога {EQUIVALENCE_TOLERANCE} — строгий лидер не определяется."
            )
        else:
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
        reasons.append("Текущая стадия проекта не позднее рекомендованной: календарная надбавка не начислена; фактические трудозатраты зависят от реализации.")
    else:
        reasons.append(
            f"Текущая стадия проекта позже рекомендованной: экспертная оценка риска позднего внедрения — "
            f"{_label(LateCost, method.late_cost)}."
        )
    reasons.append(f"Способ расчёта: {_label(CalcMode, method.calc_mode)}.")
    scope = EffectScope.of(getattr(method, "effect_scope", None))
    if scope is not None and not scope.affects_client:
        reasons.append(
            f"Область эффекта — {scope.label}: {scope.hardware_note}; требования к компьютеру "
            "игрока решение не меняет."
        )
    # Нагрузка снижается не обязательно там, где её измеряет оценка
    # оборудования: серверная сборка облегчает машину сервера.
    where = "" if (scope is None or scope.affects_client) else f" ({scope.label})"
    positives = _impact_text(method)
    if positives:
        reasons.append("Ожидаемое направление эффекта при выполнении условий — снижение нагрузки на" + where + ": " + ", ".join(positives) + ". Величина требует измерения.")
    negatives = _impact_text(method, positive=False)
    if negatives:
        reasons.append("Возможные дополнительные расходы" + where + ": " + ", ".join(negatives) + ".")
    if method.quality_impact:
        reasons.append(
            f"Влияние на качество: {method.quality_impact:+d} ({'улучшает' if method.quality_impact > 0 else 'снижает'})."
        )
    if method.concept_impact:
        reasons.append("Внимание: решение затрагивает исходную концепцию игры.")
    for condition in applicability.conditions:
        reasons.append("Условие: " + condition)
    return reasons


def _engine_support(db: Session, method: Method, engine_code: str, profile=None):
    """Аналог метода в выбранном движке + альтернативы из других движков.

    Доступность встроенного инструмента проверяется по версии движка: Nanite
    не существует в UE 4.27, и показывать его готовым аналогом нельзя.
    """
    links = [link_out(db, link, profile) for link in repositories.method_links(db, method.id)]
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
    tied_with_leader: bool = False,
    score_gap: float = 0.0,
    tied_count: int = 1,
    transition=None,
) -> RecommendationOut:
    # Метод сюда попадает применимым, а стадия влияет на стоимость внедрения,
    # поэтому «не рекомендуется» здесь не выводится из календаря: позднее
    # внедрение означает переработку, а не физическую невозможность реализации.
    stage_order = _stage_order(profile.stage)
    method_stage = _stage_order(method.recommended_stage)
    needs_rework = stage_guidance.needs_rework(method, profile.stage) or (
        method.late_cost == "critical"
        and applicability.stage_pressure >= 1.0
        and stage_order > method_stage
    )
    if transition and transition.status == "retained":
        needs_rework = False
    flags = _recommendation_flags(
        method, applicability, rank, total, comparable=comparable,
        stage_order=stage_order, method_stage=method_stage, needs_rework=needs_rework,
        tied_with_leader=tied_with_leader,
    )
    reasons = _recommendation_reasons(
        method, applicability, score, rank, total,
        comparable=comparable, compare_reason=compare_reason,
        tied_with_leader=tied_with_leader,
        score_gap=score_gap,
        tied_count=tied_count,
    )
    support, alternatives = _engine_support(db, method, profile.engine, profile)
    if transition:
        reasons.extend(transition.reasons)
        if transition.status == "retained":
            reasons = [r for r in reasons if not r.startswith("Текущая стадия проекта")]
            flags = [f for f in flags if f not in {"implement_now", "late_difficult", "needs_rework"}]
    function_code, function_name = _recommendation_function(method)

    return RecommendationOut(
        method_code=method.code,
        method_name=method.name,
        function_code=function_code,
        function_name=function_name,
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
        engine_tool_independent=bool(method.engine_tool_independent),
        summary=method.summary,
        performance_gain=method.performance_gain,
        implementation_cost=method.implementation_cost,
        complexity=method.complexity,
        late_cost=method.late_cost,
        recommended_stage=method.recommended_stage,
        quality_impact=method.quality_impact,
        concept_impact=method.concept_impact,
        source_url=method.source_url,
        effect_scope=method.effect_scope,
        effect_scope_label=_label(EffectScope, method.effect_scope) or "не распознана",
        equivalent_to_leader=tied_with_leader,
        score_gap=round(score_gap, 4),
        transition=transition,
    )


def _build_excluded(method: Method, functions: dict, applicability: rules.Applicability, extra: str | None = None) -> RecommendationOut:
    reasons = list(applicability.excluded_reasons)
    if extra:
        reasons.append(extra)
    function_code, function_name = _recommendation_function(method)
    return RecommendationOut(
        method_code=method.code,
        method_name=method.name,
        function_code=function_code,
        function_name=function_name,
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
        effect_scope=method.effect_scope,
        effect_scope_label=_label(EffectScope, method.effect_scope) or "не распознана",
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

#: Ресурсы, у которых нет подсистемной модели стоимости кадра.
#:
#: Для CPU, GPU, RAM и VRAM сводка считает стоимость кадра и может показать
#: изменение в процентах. Для накопителя и сети такой модели нет: трафик и
#: объём зависят от форматов, сжатия и сценария игры, а не только от выбранных
#: решений. Раньше суммарный экспертный балл умножался на коэффициент и
#: превращался в «проценты нагрузки» — число выглядело измерением, но им не
#: было и расходилось с аппаратным объяснением. Теперь по этим ресурсам
#: выдаётся качественная оценка направления и величины.
QUALITATIVE_RESOURCES = ("disk", "network")

#: Пороги суммарного экспертного балла для качественного уровня (по модулю).
QUALITATIVE_LEVELS = ((6.0, "существенное"), (3.0, "умеренное"), (0.0, "небольшое"))

#: Нейтральное значение шкалы: множитель стоимости 1.0.
NEUTRAL_SCORE = 50.0


def _qualitative_level(score: float) -> str:
    """Уровень влияния по суммарному экспертному баллу (без единиц измерения)."""
    magnitude = abs(score)
    if magnitude < 1e-6:
        return "без значимого влияния"
    for threshold, label in QUALITATIVE_LEVELS:
        if magnitude >= threshold:
            return label
    return "без значимого влияния"


def _qualitative_explanation(key: str, score: float, level: str) -> str:
    """Пояснение к качественной оценке: что именно сказано и чего в ней нет."""
    label = RESOURCE_LABELS[key]
    if abs(score) < 1e-6:
        return (
            f"Выбранные решения не меняют требования к {label}: "
            "значимых эффектов в каталоге для них не указано."
        )
    sign = "снижает" if score < 0 else "повышает"
    return (
        f"Набор {sign} требования к {label}: суммарный экспертный балл "
        f"{score:+g} — уровень влияния {level}. Это качественная оценка "
        "направления и относительной величины: модель не оценивает ни объём "
        "данных, ни скорость, ни трафик, поэтому числового требования здесь нет."
    )


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
def aggregate_load(
    methods: list[Method], profile, *, relations=(), estimate: HardwareEstimateOut | None = None,
) -> LoadProfileOut:
    """Суммарное влияние выбранных решений на компьютер игрока (шкала 0..100).

    Сводка строится **той же моделью стоимости кадра**, что и аппаратная
    оценка: полосы и подбор оборудования не могут разойтись, потому что читают
    один разбор подсистем. Значение показывает стоимость ресурса относительно
    того же проекта без выбранных решений: 50 — изменений нет, ниже 50 —
    нагрузка снижена, выше 50 — повышена.

    В сводку входят только клиентские эффекты: серверная экономия и ускорение
    разработки не меняют требования к компьютеру игрока. Невошедшие решения
    перечислены в пояснениях, чтобы их отсутствие не выглядело потерей данных.

    Накопитель и сеть показаны качественно (направление и уровень влияния),
    а не числом: для них нет подсистемной модели стоимости кадра, и процент
    был бы выдуманной величиной.
    """
    selected, notes = rules.assess_selected_methods(methods, profile, relations)
    counted, outside_client = rules.split_by_effect_scope(selected)
    if outside_client:
        notes = list(notes) + [
            f"«{method.name}»: {rules.non_client_reason(method)}."
            for method in outside_client
        ]

    current = hardware.build_model(profile, counted, relations)
    baseline = hardware.build_model(profile, [], relations)
    ram_now, vram_now, _ = hardware._memory_totals(current)
    ram_base, vram_base, _ = hardware._memory_totals(baseline)

    def cpu_cost(model) -> float:
        return model.cpu_sequential_ms + model.cpu_parallel_ms / hardware.PARALLEL_SPEEDUP

    def gpu_cost(model) -> float:
        return model.gpu_raster_ms + model.gpu_rt_ms

    relative = {
        "cpu": _ratio(cpu_cost(current), cpu_cost(baseline)),
        "gpu": _ratio(gpu_cost(current), gpu_cost(baseline)),
        "ram": _ratio(ram_now, ram_base),
        "vram": _ratio(vram_now, vram_base),
    }

    per_resource: dict[str, dict] = {}
    for key in ("cpu", "gpu", "ram", "vram"):
        raw = relative[key]
        # Нейтральное значение 50: множитель стоимости 1.0.
        normalized = max(0.0, min(100.0, NEUTRAL_SCORE * (1.0 + raw)))
        per_resource[key] = {
            "raw": round(raw, 4),
            "normalized": round(normalized, 1),
            "label": RESOURCE_LABELS[key],
            "direction": "снижает" if raw < -1e-6 else ("повышает" if raw > 1e-6 else "не влияет"),
            "quantitative": True,
            "unit": "относительное изменение стоимости кадра",
        }

    # Накопитель и сеть не имеют подсистем стоимости кадра: для них остаётся
    # суммарная экспертная оценка выбранных решений, показанная качественно.
    totals = {"disk": 0, "network": 0}
    for m in counted:
        totals["disk"] += m.impact_disk
        totals["network"] += m.impact_network

    for key in QUALITATIVE_RESOURCES:
        score = float(totals[key])
        level = _qualitative_level(score)
        per_resource[key] = {
            "raw": round(score, 4),
            # Нейтральное значение: числовой шкалы у ресурса нет, столбец не строится.
            "normalized": NEUTRAL_SCORE,
            "label": RESOURCE_LABELS[key],
            "direction": "снижает" if score < -1e-6 else ("повышает" if score > 1e-6 else "не влияет"),
            "quantitative": False,
            "level": level,
            "explanation": _qualitative_explanation(key, score, level),
        }

    if any(per_resource[key]["direction"] != "не влияет" for key in QUALITATIVE_RESOURCES):
        notes.append(
            "Накопитель и сеть оценены качественно: модель считает стоимость кадра "
            "для CPU, GPU, RAM и VRAM, но не объём данных и не трафик, поэтому по "
            "этим двум ресурсам указаны направление и уровень влияния, а не число."
        )

    if estimate is not None and estimate.bottleneck_label:
        notes.append(
            f"Расчёт ограничивает {estimate.bottleneck_label}: именно этот участок "
            "обработки кадра определяет достижимый результат."
        )

    return LoadProfileOut(
        notes=notes,
        cpu=per_resource["cpu"]["normalized"],
        gpu=per_resource["gpu"]["normalized"],
        ram=per_resource["ram"]["normalized"],
        vram=per_resource["vram"]["normalized"],
        disk=per_resource["disk"]["normalized"],
        network=per_resource["network"]["normalized"],
        per_resource=per_resource,
    )


def _ratio(value: float, base: float) -> float:
    """Относительное изменение стоимости: 0 — без изменений, −0.3 — минус 30%."""
    if base <= 0:
        return 0.0
    return (value - base) / base


def basket_compatibility(
    db: Session, basket_codes: list[str], methods_by_code: dict[str, Method]
) -> tuple[list[BasketConflictOut], list[BasketConflictOut], list[BasketConflictOut]]:
    """Проверить корзину и вернуть три самостоятельные категории связей.

    Раньше всё, что не является конфликтом, попадало в «усиления». Из-за этого
    закрытая зависимость, при которой одно решение просто не работает без
    другого, показывалась как «усиливающее сочетание» — то есть как достоинство
    набора. Категории разделены: конфликты, зависимости, усиления.
    Теперь используются новые типы: HARD_CONFLICT, RISK, ALTERNATIVE,
    DEPENDENCY, COMPLEMENT, OVERLAP, UNKNOWN.
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
            basis=getattr(row, "basis", "") or "",
        )

    for row in repositories.conflicts(db):
        pair_in_basket = row.a_code in basket and row.b_code in basket
        ctype = row.conflict_type
        if ctype == ConflictType.HARD_CONFLICT.value:
            if pair_in_basket:
                conflicts.append(item(
                    row, ctype, _label(ConflictType, ctype),
                    row.description, row.resolution,
                ))
        elif ctype == ConflictType.RISK.value:
            if pair_in_basket:
                # Риск показываем в конфликтах с пометкой
                conflicts.append(item(
                    row, ctype, _label(ConflictType, ctype),
                    row.description, row.resolution,
                ))
        elif ctype == ConflictType.ALTERNATIVE.value:
            if pair_in_basket:
                # Альтернативы — в конфликтах (выбор одного)
                conflicts.append(item(
                    row, ctype, _label(ConflictType, ctype),
                    row.description, row.resolution,
                ))
        elif ctype == ConflictType.DEPENDENCY.value:
            if pair_in_basket:
                dependencies.append(item(
                    row, ctype, _label(ConflictType, ctype),
                    row.description or "Одно решение опирается на другое.",
                    row.resolution or "Сохранять оба решения в плане.",
                ))
            elif row.a_code in basket and row.b_code not in basket:
                # Зависимость не закрыта: решение в корзине не сработает в одиночку.
                b = methods_by_code.get(row.b_code)
                required_name = b.name if b is not None else row.b_code
                conflicts.append(item(
                    row, "unmet_dependency", "незакрытая зависимость",
                    f"Решение «{row.a_code}» требует «{required_name}»: {row.description}",
                    (f"Добавить «{required_name}» в корзину или отказаться от решения «{row.a_code}»."
                     if b is not None else "Обязательная зависимость отсутствует в опубликованном каталоге."),
                ))
        elif ctype in {ConflictType.COMPLEMENT.value}:
            if pair_in_basket:
                synergies.append(item(
                    row, ctype, _label(ConflictType, ctype),
                    row.description, row.resolution,
                ))
        elif ctype == ConflictType.OVERLAP.value:
            if pair_in_basket:
                # Перекрытие — показываем в синергиях с пометкой
                synergies.append(item(
                    row, ctype, _label(ConflictType, ctype),
                    row.description, row.resolution,
                ))
        elif ctype == ConflictType.UNKNOWN.value:
            if pair_in_basket:
                # Непроверенное сочетание — в конфликтах с пометкой
                conflicts.append(item(
                    row, ctype, _label(ConflictType, ctype),
                    row.description, row.resolution,
                ))

    conflicts.sort(key=lambda c: -c.severity)
    dependencies.sort(key=lambda c: -c.severity)
    synergies.sort(key=lambda c: -c.severity)
    return conflicts, dependencies, synergies
