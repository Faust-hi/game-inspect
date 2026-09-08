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
    ] = Field(default_factory=lambda: ["pc_windows"])

    # Масштаб сцены
    object_count_level: LevelValue = "medium"
    object_count: Annotated[int | None, Field(ge=0, le=100_000_000)] = None
    npc_count_level: LevelValue = "medium"
    npc_count: Annotated[int | None, Field(ge=0, le=10_000_000)] = None
    player_count: Annotated[int, Field(ge=1, le=10000)] = 1
    multiplayer: bool = False

    # Функции
    functions: Annotated[list[str], Field(max_length=40)] = Field(default_factory=list)

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

#: Максимальная оценка для количества ниже нижней границы логарифмической
#: шкалы. Величина не является измеренной: она только сохраняет монотонность
#: (один объект не может стоить дороже двух), не изобретая точности.
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
        return round(_SUB_SCALE_MAX * value / span_low, 6)
    ratio = (math.log10(float(value)) - math.log10(span_low)) / (
        math.log10(span_high) - math.log10(span_low)
    )
    return max(0.0, min(1.0, ratio))


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
    used_in_projects: list[str] = Field(default_factory=list)
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
    source_url: str


class GameExampleOut(BaseModel):
    title: str
    year: int
    developer: str
    engine: str
    format: str
    world_type: str
    scale: str
    platforms: list[str]
    target_resolution: str
    target_fps: int
    object_count_level: str
    npc_count_level: str
    multiplayer: bool
    player_count: int
    features: list[str]
    optimizations_used: list[str]
    summary: str
    performance_outcome: str
    source_title: str
    source_url: str
    verified_by: str


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
    summary: str
    performance_gain: float
    implementation_cost: int
    complexity: int
    late_cost: str
    recommended_stage: str
    quality_impact: int
    concept_impact: int
    source_url: str


class RiskOut(BaseModel):
    code: str
    title: str
    severity: str
    description: str
    advice: str


class LoadProfileOut(BaseModel):
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


class SimilarGameOut(BaseModel):
    example: GameExampleOut
    similarity: float
    matching_optimizations: list[str]


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
    similar_games: list[SimilarGameOut] = Field(default_factory=list)
    meta: dict[str, Any] = Field(default_factory=dict)
    basket_codes: list[str] = Field(default_factory=list)
    input_key: str = ""

    @model_validator(mode="after")
    def _fill_input_key(self):
        # Ключ всегда задаётся сервисом расчёта. Здесь он заполняется только для
        # результатов, собранных вручную, — и тогда берётся корзина из ответа,
        # иначе отпечаток молча относился бы к пустому набору.
        if not self.input_key:
            object.__setattr__(
                self, "input_key", input_fingerprint(self.profile, self.basket_codes)
            )
        return self


class SuggestedMethod(BaseModel):
    """Кандидат в корзину, найденный в файлах проекта (эвристика, не факт)."""

    method_code: str
    reason: str


class ProjectImportOut(BaseModel):
    """Частичная анкета из файлов движка + прозрачность извлечения.

    `profile` — предпросмотр полной анкеты для показа пользователю. Применять
    его целиком нельзя: незаполненные поля в нём содержат значения по
    умолчанию, а не ответы пользователя. Для применения служит `patch` — только
    действительно извлечённые из файлов поля.
    """

    profile: ProjectProfile
    #: Только извлечённые поля в нормализованном виде. Именно этот набор
    #: накладывается на существующую анкету; пустой patch не должен ничего
    #: сбрасывать.
    patch: dict[str, Any] = Field(default_factory=dict)
    filled: list[str] = Field(default_factory=list)
    suggested: list[SuggestedMethod] = Field(default_factory=list)
    detected: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class PresetFile(BaseModel):
    name: str
    language: str
    content: str


class ProjectPresetsOut(BaseModel):
    files: list[PresetFile] = Field(default_factory=list)


class FeedbackIn(BaseModel):
    method_code: str = Field(min_length=1, max_length=64)
    useful: bool


class FeedbackOut(BaseModel):
    public_id: str
    method_code: str
    up: int
    down: int


class MethodFeedbackOut(BaseModel):
    method_code: str
    up: int
    down: int
    total: int
    helpful_rate: float


class ConfidenceSuggestionOut(BaseModel):
    method_code: str
    current_confidence: float
    suggested_confidence: float
    reason: str


class FeedbackSummaryOut(BaseModel):
    projects_with_feedback: int
    methods: list[MethodFeedbackOut] = Field(default_factory=list)
    suggestions: list[ConfidenceSuggestionOut] = Field(default_factory=list)


def input_fingerprint(
    profile: ProjectProfile,
    basket: list[str],
    algorithm_version: str = "",
    dataset_version: str = "",
) -> str:
    """Устойчивый отпечаток входа: одинаковым данным — одинаковый ключ.

    Версии алгоритма и набора данных входят в ключ только когда заданы явно:
    без них сохраняется прежний формат (для результатов, собранных вручную),
    с ними — ключ различает расчёты разных версий для одного профиля и корзины.
    Пустые строки не добавляются, чтобы старые вызовы давали прежний хеш.
    """
    payload_dict: dict[str, object] = {
        "profile": profile.model_dump(mode="json"),
        "basket": sorted(basket or []),
    }
    if algorithm_version:
        payload_dict["algorithm_version"] = algorithm_version
    if dataset_version:
        payload_dict["dataset_version"] = dataset_version
    payload = json.dumps(
        payload_dict,
        sort_keys=True,
        ensure_ascii=False,
        separators=(",", ":"),
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:32]
