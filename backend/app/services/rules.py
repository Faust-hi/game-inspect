"""Экспертные правила применимости решений.

Правила разделяются на два класса:
  * жёсткие (исключающие) — решение нарушает обязательное ограничение проекта;
  * мягкие (порождающие условия и пометки) — решение применимо с оговорками.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from collections.abc import Mapping, Sequence

from ..models.entities import Conflict, Method
from ..models.enums import DevStage, EffectScope, LateCost, Scale
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


def stage_pressure(profile_stage: str, method_stage: str) -> float:
    """Насколько текущая стадия проекта позже рекомендованной для метода (0..1).

    Делитель 4 — экспертное допущение: шкала стадий содержит восемь позиций
    (concept..post_release), и смещение на четыре шага и более считается
    предельным давлением позднего внедрения. Независимая калибровка не
    выполнялась; значение заявлено как допущение, а не как измерение.
    """
    current = STAGE_ORDER.get(profile_stage, 2)
    recommended = STAGE_ORDER.get(method_stage, 2)
    return max(0.0, min(1.0, (current - recommended) / 4.0))


def resource_severity(profile: ProjectProfile) -> dict[str, float]:
    """Насколько критичен дефицит каждого ресурса (0 — не критичен, 1 — критичен).

    Веса бюджета и значения по умолчанию — экспертные допущения: измерений
    чувствительности модели к дефициту ресурса не выполнялось. Неизвестный
    уровень даёт 0,4 — между «высоким» (0,2) и «средним» (0,5), чтобы
    отсутствие ответа не читалось как ни тугая, ни свободная смета.
    """
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

    # Requirements of the reviewed mechanisms, also used when accounting a
    # selected basket. Text-only conditions must not admit an offline server.
    if method.code in {'subtick_networking', 'lag_compensation_rewind'}:
        if not profile.multiplayer:
            result.excluded_reasons.append('Серверная обработка сетевых команд требует мультиплеера.')
        if profile.network_topology == 'lockstep':
            result.excluded_reasons.append('Выбран чистый lockstep; для этого метода нужен авторитетный обработчик команд с отдельной историей времени.')
        if profile.network_topology in {'auto', 'p2p'}:
            result.conditions.append('Уточнить авторитетного владельца симуляции и проверку времени команд; распределённые узлы сами по себе этого не обеспечивают.')
    if method.code == 'async_compute_overlap':
        if profile.render_api not in {'auto', 'dx12', 'vulkan'}:
            result.excluded_reasons.append('Вариант с явными асинхронными очередями требует DX12 или Vulkan; выбран другой API.')
        if profile.render_api == 'auto':
            result.conditions.append('Уточнить API и поддержку нескольких очередей движком и GPU.')
    if method.code == 'directstorage_io' and profile.render_api not in {'auto', 'dx12'}:
        result.conditions.append('Для выбранного RHI не предполагается прямой GPU-путь DirectStorage: проверить CPU/системную память или отдельный D3D12 interop без обещания ускорения.')

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
            "Текущая стадия проекта позже рекомендованной: проверить, затронет ли внедрение уже готовые материалы."
        )

    if method.quality_impact <= -1:
        result.conditions.append("Возможны потери визуального качества: проверить их приемлемость на целевой сцене.")

    if method.concept_impact <= -1:
        result.conditions.append("Решение может изменить исходную концепцию: требуется согласование с геймдизайном.")

    if method.requires_prototype or method.confidence < 0.7:
        result.conditions.append("Оценка эффекта требует прототипирования до принятия решения.")

    return result


def mandatory_dependency_closure(
    methods: Sequence[Method],
    catalog: Mapping[str, Method],
    relations: Sequence[Conflict],
) -> tuple[list[Method], list[str]]:
    """Достроить обязательные зависимости выбранных решений (транзитивно).

    Обязательная зависимость означает «без B эффект A не реализуется». Раньше
    отсутствие B в корзине просто выбрасывало A, и корзина схлопывалась: без
    `async_loading_pipeline` исчезал `world_partition_streaming`, а без
    `gpu_compute_culling` — `gpu_instancing_vegetation`. Пользователь выбирал
    технику и получал нейтральную нагрузку 50/50, не зная, что расчёт пуст:
    у Horizon Zero Dawn так пропадали все 6 решений из 6.

    Здесь зависимости достраиваются до неподвижной точки. Добавленные решения
    возвращаются отдельным списком пояснений, чтобы их появление в расчёте было
    видно пользователю, а не выглядело самовольным расширением корзины.

    Каскадное исключение в `assess_selected_methods` при этом сохраняется: если
    достроенная зависимость окажется неприменимой к профилю, зависящее от неё
    решение по-прежнему не будет учитываться — но уже с названной причиной.
    """
    ordered: list[Method] = list(methods)
    seen = {method.code for method in ordered}
    required_by: dict[str, str] = {}

    changed = True
    while changed:
        changed = False
        for relation in relations:
            if relation.conflict_type != "dependency":
                continue
            if relation.a_code not in seen or relation.b_code in seen:
                continue
            target = catalog.get(relation.b_code)
            if target is None:
                continue
            ordered.append(target)
            seen.add(target.code)
            required_by[target.code] = relation.a_code
            changed = True

    notes = [
        f"«{catalog[code].name}» добавлено в расчёт как обязательная зависимость "
        f"для «{catalog[required_by[code]].name}»."
        for code in required_by
        if code in catalog and required_by[code] in catalog
    ]
    return ordered, notes


def assess_selected_methods(
    methods: list[Method], profile: ProjectProfile, relations: Sequence[Conflict] = (),
) -> tuple[list[Method], list[str]]:
    """Одинаковая проверка корзины для сводной нагрузки и аппаратной оценки."""
    applicable: list[Method] = []
    notes: list[str] = []
    for method in methods:
        # A planning preference cannot remove the runtime work of a selected
        # implementation. Physical compatibility and dependencies still apply.
        result = evaluate(method, profile.model_copy(update={"complexity_tolerance": None}))
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
            # Дополнение допускает совместное применение, но не доказывает выигрыш.
            warnings.append(
                f"{relation.a_code} + {relation.b_code}: дополнение. "
                "Разные механизмы могут применяться совместно; общий выигрыш требует измерения. " + (relation.description or "")
            )
        elif ctype == "overlap":
            # Перекрывающиеся эффекты: частичная дублировка
            warnings.append(
                f"{relation.a_code} / {relation.b_code}: перекрытие эффектов. "
                "Области действия могут пересекаться; величину перекрытия нужно проверить. " + (relation.description or "")
            )
        elif ctype == "unknown":
            # Непроверенная комбинация: отсутствие запрета ≠ доказанная совместимость
            warnings.append(
                f"{relation.a_code} / {relation.b_code}: не проверено. "
                "Совместимость не подтверждена отдельно. " + (relation.description or "")
            )
        elif ctype == "dependency":
            # Обязательная зависимость — не конфликт и не риск: её обрабатывает
            # отдельный каскадный проход ниже (метод без доступной зависимости
            # исключается). Раньше тип не имел ветки и проваливался в `else`,
            # поэтому на каждой штатной зависимости пользователь видел
            # «тип связи «dependency» не распознан» — хотя связь учитывалась.
            continue
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


def resource_fit(method: Method, profile: ProjectProfile, workload: dict[str, float] | None = None) -> float:
    """Насколько профиль нагрузки метода соответствует дефицитным ресурсам проекта (0..1)."""
    severity = resource_severity(profile)
    if workload:
        severity = {key: (value + workload.get(key, value)) / 2 for key, value in severity.items()}
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
