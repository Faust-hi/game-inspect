"""Pydantic-схемы каталогов и профиля проекта.

Значения анкеты заданы перечислениями, а не произвольными строками, и имеют
границы. Причина не в строгости ради строгости: значения профиля подставляются
в формулы оценки оборудования и в матрицу TOPSIS. Отрицательное число объектов
или допустимая сложность 999 дают результат, который выглядит как расчёт, но
им не является.
"""
from __future__ import annotations

import hashlib
import json
import math
from typing import Annotated, Any, Literal

from pydantic import BaseModel, Field, field_validator, model_validator

from ..models.enums import (
    DevStage, GameFormat, MemoryModel, NetworkTopology, Platform,
    Priority, RenderAPI, Resolution, Quality, Scale, StorageType,
    UpscalingMethod, WorldType,
)


def _values(enum_cls) -> list[str]:
    return [item.value for item in enum_cls]


#: Псевдоним для качественного уровня. `unknown` означает, что источник
#: характеристики не сообщает; это не отдельный уровень нагрузки.
LevelValue = Literal["unknown", "low", "medium", "high"]


def level_unspecified(value: str | None) -> bool:
    """Уровень не задан: поле отсутствует либо явно помечено как «не указано».

    `unknown` — разрешённое значение анкеты. Его нельзя отождествлять ни с
    `None`, ни с реальным уровнем нагрузки: отсутствие значения не должно
    превращаться в измеренную величину.
    """
    return value is None or value == "unknown"


# ---------------------------------------------------------------------------
# Профиль проекта (анкета, раздел 3 плана)
# ---------------------------------------------------------------------------
class ProjectProfile(BaseModel):
    """Описание разрабатываемой игры, заполняемое пользователем."""

    name: Annotated[str, Field(min_length=1, max_length=200)] = "Проект без названия"

    # Формат и структура мира
    format: Literal[tuple(_values(GameFormat))] = "3D"
    world_type: Literal[tuple(_values(WorldType))] = "open_world"
    scale: Literal[tuple(_values(Scale))] = "large"

    # Стадия и технологии
    stage: Literal[tuple(_values(DevStage))] = "prototype"
    # Код движка не зашит перечислением: движок добавляется через каталог, и
    # новый код должен приниматься без правки схемы. Допустимость проверяется
    # по фактическому наполнению каталога — см. `services/engines.py`.
    engine: Annotated[str, Field(min_length=1, max_length=64, pattern=r"^[A-Za-z0-9_.-]+$")] = "unreal"
    engine_version: Annotated[str | None, Field(max_length=40)] = None
    platforms: Annotated[
        list[Literal[tuple(_values(Platform))]], Field(min_length=1, max_length=11)
    ] = ["pc_windows"]

    # Масштаб сцены
    object_count_level: LevelValue = "medium"
    object_count: Annotated[int | None, Field(ge=0, le=100_000_000)] = None
    npc_count_level: LevelValue = "medium"
    npc_count: Annotated[int | None, Field(ge=0, le=10_000_000)] = None
    player_count: Annotated[int, Field(ge=1, le=10000)] = 1
    multiplayer: bool = False
    # Число локальных вьюпортов (split-screen). Это не сетевые игроки:
    # кооп на одном экране умножает рендер-нагрузку, но не сетевой трафик.
    # None — не задано; при выбранной функции split-screen используется
    # сценарное предположение «2 вьюпорта», отражаемое в modeling_gaps.
    local_view_count: Annotated[int | None, Field(ge=1, le=8)] = None

    # Функции
    # Простые значения по умолчанию нужны также для FastAPI `Depends()` в
    # GET /report-data: FastAPI передаёт default_factory как служебный объект
    # вместо вызова фабрики при разборе модели-зависимости. Pydantic копирует
    # изменяемые значения по умолчанию для каждого экземпляра модели.
    functions: Annotated[list[str], Field(max_length=40)] = []

    # Целевые показатели
    target_resolution: Literal[tuple(_values(Resolution))] = "1080p"
    target_quality: Literal[tuple(_values(Quality))] = "high"
    target_fps: Annotated[int, Field(ge=15, le=480)] = 60

    # Технические параметры, которые влияют на оценку, но раньше терялись.
    # Значения auto/None означают «не задано», а не идеальную конфигурацию:
    # аппаратный сервис явно отражает эту неопределённость в результате.
    render_api: Literal[tuple(_values(RenderAPI))] = "auto"
    storage_type: Literal[tuple(_values(StorageType))] = "auto"
    memory_model: Literal[tuple(_values(MemoryModel))] = "auto"
    upscaling_method: Literal[tuple(_values(UpscalingMethod))] = "auto"
    network_topology: Literal[tuple(_values(NetworkTopology))] = "auto"
    frame_generation: bool = False
    base_render_fps: Annotated[int | None, Field(ge=15, le=480)] = None
    streaming_pool_gb: Annotated[float | None, Field(gt=0, le=512)] = None
    draw_call_budget: Annotated[int | None, Field(ge=100, le=1_000_000)] = None
    simulation_radius_m: Annotated[int | None, Field(ge=0, le=100_000)] = None
    physics_tick_hz: Annotated[float | None, Field(ge=15, le=480, allow_inf_nan=False)] = None
    audio_complexity: LevelValue | None = None

    # Необязательные проверяемые цели. Отсутствие значения означает
    # `unknown`, а не нулевую нагрузку и не автоматически выполненную цель.
    target_1_percent_low_fps: Annotated[int | None, Field(ge=1, le=480)] = None
    max_startup_seconds: Annotated[float | None, Field(gt=0, le=600)] = None
    max_streaming_latency_ms: Annotated[int | None, Field(gt=0, le=60000)] = None
    max_save_seconds: Annotated[float | None, Field(gt=0, le=600)] = None
    target_network_latency_ms: Annotated[int | None, Field(gt=0, le=2000)] = None
    target_server_tick_hz: Annotated[float | None, Field(gt=0, le=1000)] = None
    max_network_kbps: Annotated[float | None, Field(gt=0, le=1000000)] = None

    # Обязательные ограничения
    ram_limit_gb: Annotated[float | None, Field(gt=0, le=512)] = None
    vram_limit_gb: Annotated[float | None, Field(gt=0, le=256)] = None
    size_limit_gb: Annotated[float | None, Field(gt=0, le=4096)] = None
    deadline_weeks: Annotated[int | None, Field(ge=0, le=1040)] = None
    complexity_tolerance: Annotated[int | None, Field(ge=1, le=5)] = None

    # Приоритет при ранжировании
    priority: Literal[tuple(_values(Priority))] = "balanced"

    # Проектные бюджеты (качественные уровни)
    cpu_budget: LevelValue | None = None
    gpu_budget: LevelValue | None = None
    ram_budget: LevelValue | None = None
    vram_budget: LevelValue | None = None

    @field_validator("name")
    @classmethod
    def _name_not_blank(cls, v: str) -> str:
        value = (v or "").strip()
        if not value:
            raise ValueError("название проекта не может быть пустым")
        return value

    @field_validator("functions", mode="before")
    @classmethod
    def _clean_functions(cls, v):
        """Убирает пустые значения и повторы, сохраняя порядок."""
        if not v:
            return []
        if not isinstance(v, list):
            raise ValueError("список функций должен быть массивом")
        seen, out = set(), []
        for item in v:
            # Раньше любой объект приводился к строке: словарь превращался в
            # код "{'a': 5}" и молча попадал в расчёт как неизвестное решение.
            if not isinstance(item, str):
                raise ValueError("код должен быть строкой")
            code = item.strip()
            if not code or code in seen:
                continue
            seen.add(code)
            out.append(code)
        return out

    @model_validator(mode="after")
    def _consistent_counts(self):
        """Точное число и качественный уровень не должны противоречить друг другу.

        Если пользователь указал 5 000 000 объектов и уровень «низкий», расчёт
        получает два взаимоисключающих входа. Уточняем уровень по числу.
        """
        if self.frame_generation and self.base_render_fps is not None and self.base_render_fps > self.target_fps:
            raise ValueError("базовый FPS не может превышать целевой отображаемый FPS при генерации кадров")
        for field, level_field in (("object_count", "object_count_level"),
                                   ("npc_count", "npc_count_level")):
            value = getattr(self, field)
            if value is None:
                continue
            derived = _level_from_count(value, field)
            if derived is not None:
                setattr(self, level_field, derived)
        return self

    @property
    def object_count_effective(self) -> float:
        """Численная оценка числа объектов: точное значение или уровень."""
        return _effective_count(self.object_count, self.object_count_level, "object_count")

    @property
    def npc_count_effective(self) -> float:
        return _effective_count(self.npc_count, self.npc_count_level, "npc_count")


#: Пороговые значения, по которым точное число переводится в качественный уровень.
_COUNT_BOUNDS: dict[str, tuple[int, int]] = {
    "object_count": (5_000, 100_000),       # ниже — немного, выше — много
    "npc_count": (50, 1_000),
}

#: Численная оценка уровня, когда точное значение не указано.
_LEVEL_FALLBACK: dict[str, float] = {"unknown": 0.55, "low": 0.25, "medium": 0.55, "high": 0.9}

#: Оценка, которой соответствует нижняя граница логарифмической шкалы.
#: Величина не является измеренной: она задаёт долю шкалы, отводимую диапазону
#: ниже нижней границы, чтобы обе ветви нормализации сходились в одной точке.
#: Раньше под-шкала заканчивалась на этом значении, а логарифмическая ветвь
#: начиналась с нуля: 499 объектов давали оценку 0.04, а 500 — 0.0, и нагрузка
#: падала при увеличении числа. Шкала обязана быть неубывающей.
_SUB_SCALE_MAX = 0.04


def _level_from_count(value: int | None, field: str) -> str | None:
    if value is None:
        return None
    low, high = _COUNT_BOUNDS[field]
    if value < low:
        return "low"
    if value > high:
        return "high"
    return "medium"


def count_scale_bounds(field: str) -> tuple[float, float]:
    """Границы логарифмической шкалы счётчика: (нижняя, верхняя).

    За верхней границей модель перестаёт различать значения: 10 000 и
    10 000 000 NPC дают один индекс. Это ограничение модели, и оно должно
    сообщаться явно, а не выдаваться за одинаковую реальную нагрузку.
    """
    low, high = _COUNT_BOUNDS[field]
    return max(1.0, low / 10.0), high * 10.0


def _effective_count(value: int | None, level: str, field: str) -> float:
    """Приводит «число или уровень» к одной числовой шкале 0..1.

    Точное число переводится логарифмически: разница между 1 000 и 10 000
    объектов заметна, а между 1 000 000 и 1 010 000 — нет. Шкала совпадает с
    численной оценкой уровня, поэтому уровень и число взаимозаменяемы, а
    указанное число действительно влияет на результат.

    Ноль и отсутствие значения — разные состояния. Раньше `value <= 0`
    обрабатывался как «не указано» и подставлял качественный уровень, из-за
    чего профиль с нулём NPC получал нагрузку больше, чем профиль с одним NPC.
    """
    if value is None:
        return _LEVEL_FALLBACK.get(level, 0.55)
    if value <= 0:
        return 0.0

    span_low, span_high = count_scale_bounds(field)
    if value < span_low:
        # Линейно внутри диапазона ниже нижней границы: 0 → 0, граница → _SUB_SCALE_MAX.
        return round(_SUB_SCALE_MAX * value / span_low, 6)
    ratio = (math.log10(float(value)) - math.log10(span_low)) / (
        math.log10(span_high) - math.log10(span_low)
    )
    # Логарифмическая ветвь начинается там, где закончилась под-шкала, и идёт
    # до единицы: иначе на границе диапазонов оценка падала бы скачком.
    ratio = max(0.0, min(1.0, ratio))
    return round(_SUB_SCALE_MAX + (1.0 - _SUB_SCALE_MAX) * ratio, 6)


class BasketRequest(BaseModel):
    """Профиль проекта и выбранные решения («корзина проекта»)."""

    profile: ProjectProfile
    basket: Annotated[list[str], Field(max_length=200)] = Field(default_factory=list)

    @field_validator("basket", mode="before")
    @classmethod
    def _clean_basket(cls, v):
        if not v:
            return []
        if not isinstance(v, list):
            raise ValueError("корзина должна быть массивом кодов")
        seen, out = set(), []
        for item in v:
            # Раньше любой объект приводился к строке: словарь превращался в
            # код "{'a': 5}" и молча попадал в расчёт как неизвестное решение.
            if not isinstance(item, str):
                raise ValueError("код должен быть строкой")
            code = item.strip()
            if not code or code in seen:
                continue
            seen.add(code)
            out.append(code)
        return out


class ImplementationBaseline(BasketRequest):
    """Реализованная основа, явно зафиксированная пользователем."""


class RecommendationRequest(BasketRequest):
    baseline: ImplementationBaseline | None = None
    #: Профиль команды и учёт зависимостей для календаря в снимке отчёта.
    #: Раньше снимок всегда считался по малой команде с включёнными
    #: зависимостями, поэтому экспортированный календарь не совпадал с тем,
    #: который пользователь выбрал на экране расписания.
    team: Annotated[str, Field(min_length=1, max_length=40)] = "small_2_5"
    include_dependencies: bool = True


class ScheduleRequest(BaseModel):
    """Вход для сценарного календарного плана."""

    profile: ProjectProfile
    basket: Annotated[list[str], Field(max_length=200)] = Field(default_factory=list)
    team: Annotated[str, Field(min_length=1, max_length=40)] = "small_2_5"
    include_dependencies: bool = True


class TransitionOut(BaseModel):
    method_code: str
    status: str
    scope: str
    cost_min: float
    cost_max: float
    complexity_min: float = 0
    complexity_max: float = 5
    replaces: list[str] = Field(default_factory=list)
    affected_methods: list[str] = Field(default_factory=list)
    reasons: list[str] = Field(default_factory=list)
    evidence: str = "expert_scenario"


# ---------------------------------------------------------------------------
# Каталоги
# ---------------------------------------------------------------------------
class EngineToolOut(BaseModel):
    code: str
    name: str
    subsystem: str
    description: str
    tool_type: str
    docs_url: str
    #: Минимальная версия движка, в которой встроенный инструмент существует.
    #: None — граница не задана, а не «доступен в любой версии».
    min_version: str | None = None


class EngineOut(BaseModel):
    code: str
    name: str
    vendor: str
    versions: list[str]
    supported_formats: list[str]
    notes: str
    docs_url: str
    tools: list[EngineToolOut] = Field(default_factory=list)


class GameFunctionOut(BaseModel):
    code: str
    name: str
    description: str
    category: str
    formats: list[str]
    typical_world_types: list[str]
    sort_order: int
    source_title: str
    source_url: str


class MethodEngineLinkOut(BaseModel):
    engine_code: str
    engine_name: str
    tool_code: str
    tool_name: str
    relation_type: str
    relation_label: str
    note: str
    docs_url: str
    #: Минимальная версия движка, в которой существует встроенный инструмент.
    tool_min_version: str | None = None
    #: Доступность инструмента в версии движка проекта: True — доступен,
    #: False — в этой версии его нет, None — проверить нельзя (версия не
    #: указана или граница не задана). None не означает «доступен».
    available: bool | None = None
    availability_note: str | None = None
    source_locator: str = ""
    #: Собственный URL связи. Пустая строка означает, что публичного
    #: источника не существует (например, инструмент пользовательского
    #: движка) — это не то же самое, что «источник не проверен».
    source_url: str = ""
    evidence_basis: str = "unknown"
    evidence_status: str = "unknown"


class MethodVariantOut(BaseModel):
    """Вариант реализации метода: как именно он может быть построен."""

    name: str
    description: str
    basis: str
    evidence: list[str] = Field(default_factory=list)


class MethodOut(BaseModel):
    code: str
    name: str
    kind: str
    function_code: str | None = None
    summary: str
    description: str
    problem: str
    pros: list[str]
    cons: list[str]
    limitations: list[str]
    level: str
    level_label: str
    recommended_stage: str
    recommended_stage_label: str
    late_cost: str
    late_cost_label: str
    calc_mode: str
    calc_mode_label: str
    # Где проявляется эффект: только `client` меняет требования к компьютеру
    # игрока. Поле читается интерфейсом, чтобы серверная экономия и ускорение
    # разработки не выглядели ускорением игры.
    effect_scope: str = "client"
    effect_scope_label: str = "клиент"
    # Решение реализуется своими средствами и не опирается на встроенный
    # инструмент движка. Различает «привязка к версии не нужна» и «данных
    # нет»: без признака пустой список связей читается как пробел каталога.
    engine_tool_independent: bool = False
    impact_cpu: int
    impact_gpu: int
    impact_ram: int
    impact_vram: int
    impact_disk: int
    impact_network: int
    quality_impact: int
    concept_impact: int
    performance_gain: float
    implementation_cost: int
    complexity: int
    confidence: float
    requires_prototype: bool
    applicable_formats: list[str]
    applicable_world_types: list[str]
    applicable_engines: list[str]
    applicable_platforms: list[str]
    requires_features: list[str]
    requires_hw_features: list[str]
    requires_conditions: list[str]
    verification_method: str
    verification_tools: list[str]
    application_steps: list[str] = Field(default_factory=list)
    # «Варианты реализации» карточки метода: как именно он может быть построен.
    # Пустой список означает, что вариантов нет в исследовании, а не что поле
    # забыли перенести: перенос идёт из паков, покрытие проверяется тестом.
    implementation_variants: list[MethodVariantOut] = Field(default_factory=list)
    # Что нужно иметь до внедрения. Отдельно от `verification_tools`: те служат
    # для проверки результата, а не для работы.
    required_data_and_tools: str = ""
    status: str
    source_title: str
    source_url: str
    engine_links: list[MethodEngineLinkOut] = Field(default_factory=list)


class ConflictOut(BaseModel):
    a_code: str
    b_code: str
    conflict_type: str
    conflict_label: str
    severity: int
    description: str
    resolution: str
    #: Основание рекомендации: documented / derived / expert_estimate / unknown.
    #: Без него выведенное решение неотличимо от документированного.
    basis: str = ""
    source_url: str


class HardwareCPUOut(BaseModel):
    model: str
    vendor: str
    generation: str
    architecture: str
    release_year: int
    cores: int
    threads: int
    single_thread_score: float
    multi_thread_score: float
    perf_class: int
    memory_support: str
    tdp_w: int
    notes: str
    source_title: str
    source_url: str
    benchmark_name: str = ""
    benchmark_context: str = ""
    benchmark_raw_value: float | None = None
    normalization_note: str = ""
    evidence_basis: str = "derived"


class HardwareGPUOut(BaseModel):
    model: str
    vendor: str
    generation: str
    architecture: str
    release_year: int
    vram_gb: float
    vram_type: str
    memory_bandwidth_gbs: float
    api_support: list[str]
    hw_features: list[str]
    raster_score: float
    rt_score: float
    perf_class: int
    tdp_w: int
    notes: str
    source_title: str
    source_url: str
    benchmark_name: str = ""
    benchmark_context: str = ""
    benchmark_raw_value: float | None = None
    normalization_note: str = ""
    evidence_basis: str = "derived"


# ---------------------------------------------------------------------------
# Результаты расчёта
# ---------------------------------------------------------------------------
class CriterionScore(BaseModel):
    key: str
    label: str
    raw: float
    normalized: float
    weight: float
    weighted: float
    kind: str


class StabilityOut(BaseModel):
    """Устойчивость ранга при дрожании весов TOPSIS на ±10%.

    None означает «сравнивать было нечего» (одна альтернатива или неразличимые
    строки) — там и сам TOPSIS некомпарабелен.
    """

    rank_min: int
    rank_max: int
    stable: bool


class RecommendationOut(BaseModel):
    method_code: str
    method_name: str
    function_code: str | None
    function_name: str | None
    kind: str
    score: float
    rank: int
    flags: list[str]
    flag_labels: list[str]
    reasons: list[str]                      # почему рекомендуется
    excluded_reasons: list[str] = Field(default_factory=list)
    criteria: list[CriterionScore] = Field(default_factory=list)
    stability: StabilityOut | None = None
    engine_support: MethodEngineLinkOut | None = None
    engine_alternatives: list[MethodEngineLinkOut] = Field(default_factory=list)
    # Решение реализуется своими средствами: пустая привязка к версии движка
    # тогда обоснована, а не означает пробел в данных. Без признака эти два
    # состояния в карточке неразличимы.
    engine_tool_independent: bool = False
    summary: str
    performance_gain: float
    implementation_cost: int
    complexity: int
    late_cost: str
    recommended_stage: str
    quality_impact: int
    concept_impact: int
    source_url: str
    # Область эффекта: интерфейс не должен показывать серверную экономию и
    # ускорение разработки как ускорение игры.
    effect_scope: str
    effect_scope_label: str
    # Группа равнозначных: разница с лидером меньше порога различимости TOPSIS.
    equivalent_to_leader: bool = False
    score_gap: float = 0.0
    transition: TransitionOut | None = None


class RiskOut(BaseModel):
    code: str
    title: str
    severity: str
    description: str
    advice: str


class LoadProfileOut(BaseModel):
    """Сводный профиль нагрузки набора решений.

    cpu, gpu, ram и vram — числовая шкала 0..100 с нейтральной серединой 50:
    измеряется изменение стоимости кадра относительно того же проекта без
    выбранных решений.

    disk и network — качественные ресурсы. У них нет подсистемной модели
    стоимости кадра, поэтому в числовых полях стоит нейтральное значение 50,
    а смысл содержится в per_resource: направление, уровень влияния и
    пояснение. Показывать эти два поля как «проценты нагрузки» нельзя.
    """

    notes: list[str] = Field(default_factory=list)
    cpu: float
    gpu: float
    ram: float
    vram: float
    disk: float
    network: float
    per_resource: dict[str, dict[str, Any]] = Field(default_factory=dict)


class BasketConflictOut(BaseModel):
    a_code: str
    a_name: str
    b_code: str
    b_name: str
    conflict_type: str
    conflict_label: str
    severity: int
    description: str
    resolution: str
    #: Основание рекомендации «что делать» (см. `ConflictOut.basis`).
    basis: str = ""


class NonClientMethodOut(BaseModel):
    """Решение, чей эффект не относится к компьютеру игрока.

    Выделенный сервер и ускорение производственных итераций — полезные решения,
    но они не удешевляют кадр на машине игрока. Пока такие эффекты складывались
    в общую нагрузку, набор решений выглядел дешевле, чем он есть на самом деле.
    """

    code: str
    name: str
    effect_scope: str
    effect_scope_label: str
    reason: str


class SubsystemBreakdown(BaseModel):
    """Разбор стоимости по подсистемам.

    Значения — нормированные доли работы подсистемы внутри своего процессора
    (сумма по всем подсистемам равна 1.0). Это позволяет видеть, какая именно
    часть кадра определяет требование, а не только итоговое число.
    """

    label: str
    share: float


class MemoryComposition(BaseModel):
    """Состав памяти: из чего сложилась оценка RAM и VRAM."""

    label: str
    ram_gb: float = 0.0
    vram_gb: float = 0.0


class PlatformTargetOut(BaseModel):
    """Одна цель сборки в результатах оценки.

    Цели выводятся раздельно: нативный графический путь Windows и Linux
    различается, поэтому общий ориентир не заменяет результат каждой цели.
    """

    platform: str = Field(description="Код платформы: pc_windows или pc_linux")
    label: str = Field(default="", description="Название цели")
    render_api: str = Field(default="auto", description="Разрешённый графический API")
    api_label: str = Field(default="", description="Название API")
    api_source: str = Field(default="auto", description="explicit — задан, auto — выбран по ОС")
    compatible: bool = Field(default=True, description="Есть ли нативный путь для цели")
    engine_check: str = Field(
        default="unknown", description="confirmed, mismatch или unknown"
    )
    notes: list[str] = Field(default_factory=list)
    # Собственные результаты цели. Отсутствуют, если нативного пути нет.
    cpu_index: float | None = None
    gpu_index: float | None = None
    ram_gb: float | None = None
    vram_gb: float | None = None
    # Цель с наибольшей потребностью: она объясняет общий ориентир.
    binding: bool = False
    frame_budget_ms: float | None = None
    target_assessments: list["TargetAssessmentOut"] = Field(default_factory=list)


class EstimateBand(BaseModel):
    """Оценочный диапазон; P50/P80 не являются runtime-измерением."""

    minimum: float | None = None
    p50: float | None = None
    p80: float | None = None
    unit: str = ""
    basis: str = "expert_estimate"
    confidence: float | None = None


class TargetAssessmentOut(BaseModel):
    metric: str
    label: str
    target: float | None = None
    unit: str = ""
    status: str = "unknown"  # meets | at_risk | unknown | not_modeled
    estimated: float | None = None
    basis: str = "unknown"
    note: str = ""


PlatformTargetOut.model_rebuild()


class HardwareEstimateOut(BaseModel):
    required_gpu_index: float
    required_cpu_index: float
    estimated_vram_gb: float
    estimated_ram_gb: float
    gpu_class: int
    cpu_class: int
    reference_gpu: HardwareGPUOut | None = None
    reference_cpu: HardwareCPUOut | None = None
    alternative_gpus: list[HardwareGPUOut] = Field(default_factory=list)
    alternative_cpus: list[HardwareCPUOut] = Field(default_factory=list)
    confidence: float
    confidence_label: str
    caveats: list[str]
    required_hw_features: list[str]
    exceeds_catalog: bool
    recommended_storage: str = "sata_ssd"
    estimated_draw_calls: int = 0
    modeling_gaps: list[str] = Field(default_factory=list)
    # Явный список невыполненных обязательных ограничений: пределы памяти и
    # обязательные аппаратные возможности. Раньше они растворялись в caveats,
    # и интерфейс показывал конфигурацию как подходящую.
    unmet_limits: list[str] = Field(default_factory=list)
    # Выход входов за область применимости численной модели. Внутри этой
    # области результат перестаёт различать значения, поэтому насыщение шкалы
    # нельзя выдавать за одинаковую реальную нагрузку.
    applicability_limits: list[str] = Field(default_factory=list)
    # Решения, не вошедшие в расчёт потому, что их эффект проявляется не на
    # компьютере игрока. Перечислены явно: иначе пользователь не отличит
    # «не повлияло» от «забыто при расчёте».
    non_client_methods: list[NonClientMethodOut] = Field(default_factory=list)
    # Цели сборки считаются и показываются раздельно: общий ориентир
    # удовлетворяет каждой из них, а не усредняет их.
    targets: list[PlatformTargetOut] = Field(default_factory=list)

    # --- Подсистемный разбор (исправление расчётной модели) -----------------
    # Раздельная стоимость последовательной (главный поток) и параллельной
    # работы CPU: подбор процессора учитывает обе характеристики, а не одну.
    cpu_main_thread_cost: float = 0.0
    cpu_parallel_cost: float = 0.0
    cpu_subsystems: list[SubsystemBreakdown] = Field(default_factory=list)
    # GPU: обычный рендеринг, трассировка лучей и требуемая память считаются
    # раздельно и не складываются в общую «скидку».
    gpu_raster_cost: float = 0.0
    gpu_rt_cost: float = 0.0
    gpu_subsystems: list[SubsystemBreakdown] = Field(default_factory=list)
    # Наиболее медленный участок обработки кадра — он и ограничивает результат.
    bottleneck: str = ""
    bottleneck_label: str = ""
    # Состав памяти: буферы и ресурсы складываются, а не перемножаются.
    memory_composition: list[MemoryComposition] = Field(default_factory=list)
    # Последствия выбора для качества, сети и внедрения.
    consequences: list[str] = Field(default_factory=list)
    # Требование к накопителю отдельной строкой: это самостоятельный результат,
    # а не только оговорка.
    storage_requirement: str = ""
    # Диапазоны показывают неопределённость каталога и сценарных оценок;
    # конкретный FPS без runtime-профиля не выводится.
    cpu_requirement: EstimateBand | None = None
    gpu_requirement: EstimateBand | None = None
    ram_requirement: EstimateBand | None = None
    vram_requirement: EstimateBand | None = None
    evidence_basis: str = "derived_plus_expert_estimate"
    hardware_evidence: list[str] = Field(default_factory=list)
    target_assessments: list[TargetAssessmentOut] = Field(default_factory=list)


class PracticeCheckOut(BaseModel):
    """Блок «Сверка с практикой».

    Кейсы подтверждают факт применения подхода, но не переносят FPS и не
    превращают одну игру в эталон другой.
    """

    status: str = "case_evidence"
    title: str = "Сверка с практикой"
    message: str = (
        "Публичные кейсы подтверждают применение механизмов и инженерные "
        "компромиссы. Точность FPS и межигровая переносимость не вычисляются "
        "без runtime-профилей и реальной валидационной выборки."
    )
    details: list[str] = Field(default_factory=list)
    case_count: int = 0
    case_codes: list[str] = Field(default_factory=list)
    accuracy_status: str = "not_calibrated"
    transferability: str = "not_claimed"


# ---------------------------------------------------------------------------
# Доказательства, кейсы, зависимости и планирование
# ---------------------------------------------------------------------------
class EvidenceSourceOut(BaseModel):
    code: str
    title: str
    authors: str
    publisher: str
    source_type: str
    published_date: str
    checked_at: str
    url: str
    version: str
    platform: str
    locator: str
    availability: str
    applicability: str
    notes: str


class EvidenceClaimOut(BaseModel):
    code: str
    entity: str
    entity_code: str
    field: str
    claim: str
    unit: str
    value_text: str
    value_num: float | None = None
    range_min: float | None = None
    range_max: float | None = None
    source: EvidenceSourceOut | None = None
    locator: str
    basis: str
    verification_status: str
    evidence_level: str
    formula: str
    input_parameters: dict[str, Any] = Field(default_factory=dict)
    context: str


class CaseEvidenceOut(BaseModel):
    code: str
    function_code: str
    method_code: str
    fact: str
    match_level: str
    locator: str
    source: EvidenceSourceOut | None = None
    basis: str
    transfer_limits: str


class GameCaseOut(BaseModel):
    code: str
    title: str
    studio: str
    release_year: int | None
    technology: str
    engine_code: str
    world_type: str
    network_mode: str
    summary: str
    relevance: str
    transfer_limits: str
    evidence: list[CaseEvidenceOut] = Field(default_factory=list)


class DependencyOut(BaseModel):
    code: str
    source_code: str
    source_name: str
    source_type: str
    target_code: str
    target_name: str
    target_type: str
    dependency_type: str
    mandatory: bool
    min_version: str
    max_version: str
    platform: str
    scope: str
    severity: int
    source: EvidenceSourceOut | None = None
    description: str
    workaround: str
    #: Основание обходного пути (см. `ConflictOut.basis`).
    basis: str = ""
    status: str


class GraphIssueOut(BaseModel):
    """Одна находка проверки графа зависимостей."""

    check: str
    severity: str
    message: str
    details: dict[str, Any] = Field(default_factory=dict)


class GraphChecksOut(BaseModel):
    """Результат проверок графа.

    Список находок содержит не только ошибки: непроверенные сочетания
    перечисляются отдельно, потому что «не проверено» и «совместимо» — это
    разные утверждения.
    """

    issues: list[GraphIssueOut] = Field(default_factory=list)
    counts: dict[str, int] = Field(default_factory=dict)
    engine: str | None = None
    engine_version: str | None = None
    render_api: str | None = None
    basket: list[str] = Field(default_factory=list)


class WorkPackageOut(BaseModel):
    code: str
    method_code: str
    name: str
    package_type: str
    role: str
    min_days: float
    p50_days: float
    p80_days: float
    parallelizable: bool
    recommended_stage: str
    stage_note: str = ""
    late_factor: float
    dependency_codes: list[str] = Field(default_factory=list)
    basis: str


class EffortEstimateOut(BaseModel):
    method_code: str
    method_name: str
    packages: list[WorkPackageOut] = Field(default_factory=list)
    total: EstimateBand
    risk_factors: list[str] = Field(default_factory=list)


class TeamScenarioOut(BaseModel):
    code: str
    name: str
    description: str
    team_size: int
    role_capacity: dict[str, Any] = Field(default_factory=dict)
    parallel_tracks: int
    communication_pct: float
    unplanned_pct: float
    specialist_capacity: dict[str, Any] = Field(default_factory=dict)


class ScheduleTaskOut(BaseModel):
    code: str
    name: str
    method_code: str
    package_type: str
    role: str
    dependencies: list[str] = Field(default_factory=list)
    #: Минимальная оценка нужна, чтобы показать разброс, а не только P50/P80.
    minimum_days: float = 0.0
    p50_days: float
    p80_days: float
    parallelizable: bool = True
    recommended_stage: str = "prototype"
    #: Исходный свободный текст стадии из пакета, если поле было не кодом:
    #: нормализованный код без него неотличим от кода, заданного явно.
    stage_note: str = ""
    late_factor: float = 1.0
    #: Основание оценки: экспертное допущение или выведенное значение.
    basis: str = "expert_estimate"
    start_p50: float
    finish_p50: float
    start_p80: float
    finish_p80: float
    critical: bool = False


class ScheduleOut(BaseModel):
    team: TeamScenarioOut
    methods: list[str] = Field(default_factory=list)
    effort: EstimateBand
    calendar: EstimateBand
    critical_path: list[str] = Field(default_factory=list)
    tasks: list[ScheduleTaskOut] = Field(default_factory=list)
    unresolved_dependencies: list[str] = Field(default_factory=list)
    stage_notes: list[str] = Field(default_factory=list)
    evidence_basis: str = "expert_estimate"


class EvidenceSummaryOut(BaseModel):
    source_count: int = 0
    claim_count: int = 0
    case_count: int = 0
    claims_with_sources: int = 0
    numeric_claims_published: int = 0
    numeric_claims_unknown: int = 0
    coverage_label: str = "не оценено"
    unconfirmed_numeric_factors: list[str] = Field(default_factory=list)
    calibration_status: str = "not_calibrated"


class ContributionItem(BaseModel):
    """Вклад одного фактора в результат.

    `delta` — величина вклада, а `unit` — в чём она измерена. По умолчанию
    (`unit='доля'`) это относительное изменение стоимости: доля, не процент.
    Нулевой вклад означает «фактор учтён, но не изменил стоимость» и не равен
    «фактор потерян при расчёте».

    Единица указывается явно там, где вклад не является относительным
    изменением: проход трассировки и бюджет кадра измеряются в миллисекундах,
    такт физики — множителем. Раньше поле `delta` было безразмерным, и число
    без единицы читалось как доля: «+16.667» в интерфейсе не отличить от
    «+16.667 %», а множитель 1.0 — от «+100 %».
    """

    label: str
    delta: float
    #: Единица измерения `delta`: «доля», «мс» или «×».
    unit: str = "доля"
    detail: str = ""


class ContributionsOut(BaseModel):
    """Вклад параметров анкеты и выбранных решений в результат."""

    parameters: list[ContributionItem] = Field(default_factory=list)
    methods: list[ContributionItem] = Field(default_factory=list)
    # Явные допущения: значения, которых нет в анкете и которые подставлены
    # расчётом. Без их перечисления «не указано» читается как «не влияет».
    assumptions: list[str] = Field(default_factory=list)
    # Причины, по которым эффект решения не вошёл в расчёт, с указанием решения.
    exclusions: list[str] = Field(default_factory=list)


class StageNoteOut(BaseModel):
    """Предупреждение или предложение, привязанное к стадии проекта."""

    code: str
    title: str
    text: str


class StageGuidanceOut(BaseModel):
    """Что означает текущая стадия для выбора решений.

    Стадия — это стоимость внедрения, а не физическое свойство реализации:
    она меняет порядок внедрения, риски и предупреждения, но не удаляет
    решение из расчёта. Архитектурное решение на релизе остаётся в списке с
    пометкой о переработке: иначе оно пропадало бы из рекомендаций, продолжая
    учитываться в корзине, и два экрана расходились.
    """

    stage: str
    stage_label: str
    summary: str
    # Уровни, внедряемые на этой стадии без переработки.
    available_levels: list[str] = Field(default_factory=list)
    available_level_labels: list[str] = Field(default_factory=list)
    # Уровни, внедрение которых целиком требует переработки готовых материалов.
    rework_levels: list[str] = Field(default_factory=list)
    rework_level_labels: list[str] = Field(default_factory=list)
    # Уровни, у которых переработку требует только часть решений: говорить
    # «уровень требует переработки» про них нельзя — половина решений
    # внедряется напрямую.
    restricted_levels: list[str] = Field(default_factory=list)
    restricted_level_labels: list[str] = Field(default_factory=list)
    warnings: list[StageNoteOut] = Field(default_factory=list)
    suggestions: list[StageNoteOut] = Field(default_factory=list)


class RecommendationResult(BaseModel):
    """Результат расчёта.

    Поле `input_key` — отпечаток профиля, корзины и версий расчёта
    (см. `input_fingerprint`). Клиент сравнивает его со своим текущим
    состоянием и понимает, что результат получен именно для тех данных,
    которые сейчас на экране, а не для предыдущих.

    Корзина включена в ответ, чтобы отпечаток был проверяемым: без неё клиент
    не может убедиться, что результат посчитан для того же набора решений.
    Версии в ключе нужны, чтобы одинаковый профиль на разных версиях алгоритма
    не выглядел актуальным.
    """

    profile: ProjectProfile
    risks: list[RiskOut]
    recommendations: list[RecommendationOut]
    excluded: list[RecommendationOut]
    load_profile: LoadProfileOut
    basket_conflicts: list[BasketConflictOut] = Field(default_factory=list)
    basket_dependencies: list[BasketConflictOut] = Field(default_factory=list)
    basket_synergies: list[BasketConflictOut] = Field(default_factory=list)
    hardware: HardwareEstimateOut | None = None
    practice_check: "PracticeCheckOut" = Field(default_factory=lambda: PracticeCheckOut())
    evidence_summary: "EvidenceSummaryOut" = Field(default_factory=lambda: EvidenceSummaryOut())
    contributions: "ContributionsOut" = Field(default_factory=lambda: ContributionsOut())
    stage_guidance: "StageGuidanceOut" = Field(default_factory=lambda: StageGuidanceOut(
        stage="", stage_label="", summary="",
    ))
    meta: dict[str, Any] = Field(default_factory=dict)
    basket_codes: list[str] = Field(default_factory=list)
    input_key: str = ""
    catalog_revision: str | None = None
    selected_methods: list[MethodOut] = Field(default_factory=list)
    accounted_method_codes: list[str] = Field(default_factory=list)
    baseline: ImplementationBaseline | None = None
    transitions: list[TransitionOut] = Field(default_factory=list)

    @model_validator(mode="after")
    def _fill_input_key(self):
        # Ключ всегда задаётся сервисом расчёта. Здесь он заполняется только для
        # результатов, собранных вручную, — и тогда берётся корзина из ответа,
        # иначе отпечаток молча относился бы к пустому набору.
        if not self.input_key:
            object.__setattr__(
                self, "input_key", input_fingerprint(self.profile, self.basket_codes, baseline=self.baseline)
            )
        return self


def input_fingerprint(
    profile: ProjectProfile,
    basket: list[str],
    algorithm_version: str = "",
    dataset_version: str = "",
    baseline: ImplementationBaseline | None = None,
) -> str:
    """Устойчивый отпечаток входа: одинаковым данным — одинаковый ключ.

    Версии алгоритма и набора данных входят в ключ только когда заданы явно:
    без них сохраняется прежний формат (для результатов, собранных вручную),
    с ними — ключ различает расчёты разных версий для одного профиля и корзины.
    Пустые строки не добавляются, чтобы старые вызовы давали прежний хеш.
    """
    normalized = profile.model_dump(mode="json")
    for key in ("functions", "platforms"):
        normalized[key] = sorted(set(normalized[key]))
    if normalized["target_resolution"] == "4k":
        normalized["target_resolution"] = "2160p"
    payload_dict: dict[str, object] = {
        "profile": normalized,
        "basket": sorted(set(basket or [])),
    }
    if algorithm_version:
        payload_dict["algorithm_version"] = algorithm_version
    if dataset_version:
        payload_dict["dataset_version"] = dataset_version
    if baseline is not None:
        payload_dict["baseline"] = input_fingerprint(baseline.profile, baseline.basket)
    payload = json.dumps(
        payload_dict,
        sort_keys=True,
        ensure_ascii=False,
        separators=(",", ":"),
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:32]


class ReportDataOut(BaseModel):
    """Снимок, достаточный для печатного отчёта и исследовательского аудита."""

    recommendation: RecommendationResult
    evidence_summary: EvidenceSummaryOut
    sources: list[EvidenceSourceOut] = Field(default_factory=list)
    cases: list[GameCaseOut] = Field(default_factory=list)
    dependencies: list[DependencyOut] = Field(default_factory=list)
    schedule: ScheduleOut
