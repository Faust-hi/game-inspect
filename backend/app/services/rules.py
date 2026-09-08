"""Экспертные правила применимости решений.

Правила разделяются на два класса:
  * жёсткие (исключающие) — решение нарушает обязательное ограничение проекта;
  * мягкие (порождающие условия и пометки) — решение применимо с оговорками.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from collections.abc import Sequence

from ..models.entities import Conflict, Method
from ..models.enums import DevStage, EffectScope, LateCost, Level3, Scale
from ..schemas.catalog import ProjectProfile

# Порядок стадий для сравнения «раньше / позже».
STAGE_ORDER: dict[str, int] = {s.value: s.order for s in DevStage}

# Платформы, на которых возможности современных графических API недоступны.
LEGACY_PLATFORMS = {"ps4", "xbox_one", "web", "android", "ios", "switch"}


def effect_scope_of(method: Method) -> EffectScope | None:
    """Область, в которой проявляется эффект решения.

    None означает, что значение не распознано. Оно не приравнивается к
    клиентской области: неизвестное происхождение эффекта нельзя превращать в
    экономию на компьютере игрока, поэтому вызывающая сторона обязана
    обработать такой случай явно.
    """
    return EffectScope.of(getattr(method, "effect_scope", None))


def split_by_effect_scope(methods) -> tuple[list[Method], list[Method]]:
    """Разделить решения по области эффекта.

    Возвращает `(клиентские, остальные)`. Оценка оборудования отвечает на
    вопрос о компьютере игрока, поэтому в неё входят только клиентские эффекты:
    выделенный сервер без графики не облегчает рендер на клиенте, а быстрый
    пересчёт освещения на машине художника не ускоряет кадр у игрока. Раньше
    такие эффекты складывались в общую нагрузку, и выбранный набор решений
    выглядел дешевле, чем он есть на самом деле.
    """
    client: list[Method] = []
    others: list[Method] = []
    for method in methods:
        scope = effect_scope_of(method)
        (client if scope is not None and scope.affects_client else others).append(method)
    return client, others


def non_client_reason(method: Method) -> str:
    """Почему эффект решения не меняет требования к компьютеру игрока."""
    scope = effect_scope_of(method)
    if scope is None:
        return "область эффекта не распознана, решение не учтено в оценке оборудования"
    return f"{scope.hardware_note}, поэтому требования к компьютеру игрока не меняет"


@dataclass
class Applicability:
    applicable: bool = True
    excluded_reasons: list[str] = field(default_factory=list)
    conditions: list[str] = field(default_factory=list)
    stage_pressure: float = 0.0
    late_penalty: float = 0.0


def _level_value(level: str | None, default: float = 0.55) -> float:
    if not level:
        return default
    try:
        return Level3(level).numeric
    except ValueError:
        return default


def stage_pressure(profile_stage: str, method_stage: str) -> float:
    """Насколько текущая стадия проекта позже рекомендованной для метода (0..1)."""
    current = STAGE_ORDER.get(profile_stage, 2)
    recommended = STAGE_ORDER.get(method_stage, 2)
    return max(0.0, min(1.0, (current - recommended) / 4.0))


def resource_severity(profile: ProjectProfile) -> dict[str, float]:
    """Насколько критичен дефицит каждого ресурса (0 — не критичен, 1 — критичен)."""
    mapping = {"low": 1.0, "medium": 0.5, "high": 0.2}

    def get(value: str | None) -> float:
        return mapping.get(value or "", 0.4)

    return {
        "cpu": get(profile.cpu_budget),
        "gpu": get(profile.gpu_budget),
        "ram": get(profile.ram_budget),
        "vram": get(profile.vram_budget),
        "disk": 0.4 if profile.size_limit_gb else 0.25,
        "network": 0.8 if profile.multiplayer else 0.1,
    }


def evaluate(method: Method, profile: ProjectProfile) -> Applicability:
    """Проверить применимость метода к проекту."""
    result = Applicability()

    # --- Жёсткие правила -------------------------------------------------
    if method.applicable_formats and profile.format not in method.applicable_formats:
        result.excluded_reasons.append(
            f"Метод применим только к формату {', '.join(method.applicable_formats)}, "
            f"в проекте указан формат {profile.format}."
        )

    if method.applicable_world_types and profile.world_type not in method.applicable_world_types:
        result.excluded_reasons.append(
            f"Тип мира «{profile.world_type}» не входит в область применимости метода "
            f"(поддерживается: {', '.join(method.applicable_world_types)})."
        )

    if method.applicable_engines and profile.engine not in method.applicable_engines:
        result.excluded_reasons.append(
            f"Метод реализуется только на движках: {', '.join(method.applicable_engines)}."
        )

    if method.applicable_platforms:
        missing = [p for p in profile.platforms if p not in method.applicable_platforms]
        if missing:
            result.excluded_reasons.append(
                "Метод не поддерживается на целевых платформах: "
                + ", ".join(missing)
                + "."
            )

    for feature in method.requires_features:
        if feature not in profile.functions:
            result.excluded_reasons.append(
                f"Метод требует наличия функции «{feature}», которая не выбрана в профиле."
            )

    # Оборудование: требуемые аппаратные возможности против целевых платформ.
    modern_platforms = [p for p in profile.platforms if p not in LEGACY_PLATFORMS]
    for feature in method.requires_hw_features:
        if not modern_platforms:
            result.excluded_reasons.append(
                f"Метод требует поддержки «{feature}», недоступной на выбранных платформах."
            )
        elif len(modern_platforms) < len(profile.platforms):
            result.conditions.append(
                f"Проверить поддержку «{feature}» на всех целевых платформах проекта."
            )

    # Ограничение по сложности реализации.
    if profile.complexity_tolerance and method.complexity > profile.complexity_tolerance:
        result.excluded_reasons.append(
            f"Сложность внедрения {method.complexity} превышает допустимую {profile.complexity_tolerance}."
        )

    # Ограничение по объёму сборки: метод критично увеличивает размер.
    if profile.size_limit_gb is not None and profile.size_limit_gb < 2 and method.impact_disk >= 2:
        result.excluded_reasons.append(
            "Метод существенно увеличивает размер сборки, что нарушает заданный предел."
        )

    result.applicable = not result.excluded_reasons

    # --- Мягкие правила --------------------------------------------------
    result.stage_pressure = stage_pressure(profile.stage, method.recommended_stage)
    try:
        late_weight = LateCost(method.late_cost).weight
    except ValueError:
        late_weight = 0.35
    result.late_penalty = late_weight * (0.4 + 0.6 * result.stage_pressure)

    for condition in method.requires_conditions or []:
        result.conditions.append(condition)

    if result.stage_pressure > 0 and method.late_cost in ("high", "critical"):
        result.conditions.append(
            "Текущая стадия проекта позже рекомендованной: внедрение потребует переработки уже готовых материалов."
        )

    if method.quality_impact <= -1:
        result.conditions.append("Решение снижает визуальное качество: требуется оценка приемлемости потерь.")

    if method.concept_impact <= -1:
        result.conditions.append("Решение может изменить исходную концепцию: требуется согласование с геймдизайном.")

    if method.requires_prototype or method.confidence < 0.7:
        result.conditions.append("Оценка эффекта требует прототипирования до принятия решения.")

    return result


def assess_selected_methods(
    methods: list[Method], profile: ProjectProfile, relations: Sequence[Conflict] = (),
) -> tuple[list[Method], list[str]]:
    """Одинаковая проверка корзины для сводной нагрузки и аппаратной оценки."""
    applicable: list[Method] = []
    notes: list[str] = []
    for method in methods:
        result = evaluate(method, profile)
        if not result.applicable:
            notes.append(f"{method.name}: эффект не учтён. " + " ".join(result.excluded_reasons))
            continue
        if not min_scale_satisfied(method, profile):
            notes.append(
                f"{method.name}: эффект не учтён. Метод оправдан при масштабе мира "
                f"не ниже «{method.min_scale}»."
            )
            continue
        applicable.append(method)
        for condition in result.conditions:
            notes.append(f"{method.name}: {condition}")
    available = {method.code for method in applicable}
    rejected: set[str] = set()
    warnings: list[str] = []
    for relation in relations:
        ctype = relation.conflict_type
        both_present = {relation.a_code, relation.b_code} <= available
        if not both_present:
            continue
        if ctype == "hard_conflict":
            # Жёсткая несовместимость: оба исключаются, но с явной причиной
            rejected.update((relation.a_code, relation.b_code))
            notes.append(
                f"{relation.a_code} / {relation.b_code}: жёсткая несовместимость. "
                "Оба решения исключены из расчёта. " + (relation.description or "")
            )
        elif ctype == "risk":
            # Условный риск: оба остаются, предупреждение видно
            warnings.append(
                f"{relation.a_code} / {relation.b_code}: риск. "
                "Решения совместимы, но требуют внимания: " + (relation.description or "")
            )
        elif ctype == "alternative":
            # Альтернативы: не исключаем, но отмечаем выбор
            warnings.append(
                f"{relation.a_code} / {relation.b_code}: альтернативы. "
                "Рекомендуется выбрать одно, оба не исключены. " + (relation.description or "")
            )
        elif ctype == "complement":
            # Синергия/дополнение: вместе выгоднее, но работают по отдельности
            warnings.append(
                f"{relation.a_code} + {relation.b_code}: синергия. "
                "Вместе дают больший эффект, по отдельности работают. " + (relation.description or "")
            )
        elif ctype == "overlap":
            # Перекрывающиеся эффекты: частичная дублировка
            warnings.append(
                f"{relation.a_code} / {relation.b_code}: перекрытие эффектов. "
                "Часть выигрыша дублируется, не суммируется полностью. " + (relation.description or "")
            )
        elif ctype == "unknown":
            # Непроверенная комбинация: отсутствие запрета ≠ доказанная совместимость
            warnings.append(
                f"{relation.a_code} / {relation.b_code}: не проверено. "
                "Совместимость не подтверждена отдельно. " + (relation.description or "")
            )
        else:
            # Неизвестный тип связи. Раньше такая запись не попадала ни в одну
            # ветку и связь молча исчезала из расчёта: в базе она была, но не
            # исключала и не предупреждала. Неопределённость обязана быть видна.
            warnings.append(
                f"{relation.a_code} / {relation.b_code}: тип связи «{ctype}» не распознан. "
                "Связь не учтена в расчёте. " + (relation.description or "")
            )
    available -= rejected
    notes.extend(warnings)
    # Удаление обязательной зависимости может сделать неприменимой всю цепочку.
    changed = True
    while changed:
        changed = False
        for relation in relations:
            if relation.conflict_type == "dependency" and relation.a_code in available and relation.b_code not in available:
                available.remove(relation.a_code)
                notes.append(
                    f"{relation.a_code}: эффект не учтён — обязательная зависимость "
                    f"{relation.b_code} отсутствует или неприменима."
                )
                changed = True
    return [method for method in applicable if method.code in available], notes


def resource_fit(method: Method, profile: ProjectProfile) -> float:
    """Насколько профиль нагрузки метода соответствует дефицитным ресурсам проекта (0..1)."""
    severity = resource_severity(profile)
    balance = (
        -method.impact_cpu * severity["cpu"]
        - method.impact_gpu * severity["gpu"]
        - method.impact_ram * severity["ram"]
        - method.impact_vram * severity["vram"]
        - method.impact_disk * severity["disk"]
        - method.impact_network * severity["network"]
    )
    return max(0.0, min(1.0, 0.5 + balance / 8.0))


def min_scale_satisfied(method: Method, profile: ProjectProfile) -> bool:
    """Проверка минимального масштаба мира, при котором метод оправдан."""
    if not method.min_scale:
        return True
    # Неизвестный масштаб не доказывает ни применимость, ни неприменимость.
    # Не исключаем метод молча: неопределённость должна остаться видимой в
    # аппаратной оценке и быть уточнена пользователем.
    if profile.scale == "unknown":
        return True
    order = {"small": 0, "medium": 1, "large": 2, "very_large": 3}
    try:
        required = order[Scale(method.min_scale).value]
        actual = order[Scale(profile.scale).value]
    except ValueError:
        return True
    return actual >= required
