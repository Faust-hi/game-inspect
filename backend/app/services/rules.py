"""Экспертные правила применимости решений.

Правила разделяются на два класса:
  * жёсткие (исключающие) — решение нарушает обязательное ограничение проекта;
  * мягкие (порождающие условия и пометки) — решение применимо с оговорками.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from ..models.entities import Method
from ..models.enums import DevStage, Level3, Scale
from ..schemas.catalog import ProjectProfile

# Порядок стадий для сравнения «раньше / позже».
STAGE_ORDER: dict[str, int] = {s.value: s.order for s in DevStage}

# Платформы, на которых возможности современных графических API недоступны.
LEGACY_PLATFORMS = {"ps4", "xbox_one", "web", "android", "ios", "switch"}


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
    get = lambda value: mapping.get(value or "", 0.4)  # noqa: E731
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
    late_weight = {"low": 0.0, "medium": 0.35, "high": 0.7, "critical": 1.0}.get(method.late_cost, 0.35)
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
    order = {"small": 0, "medium": 1, "large": 2, "very_large": 3}
    try:
        required = order[Scale(method.min_scale).value]
        actual = order[Scale(profile.scale).value]
    except ValueError:
        return True
    return actual >= required
