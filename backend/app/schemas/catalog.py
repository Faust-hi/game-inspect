"""Pydantic-схемы каталогов и профиля проекта.

Значения анкеты заданы перечислениями, а не произвольными строками, и имеют
границы. Причина не в строгости ради строгости: значения профиля подставляются
в формулы оценки оборудования и в матрицу TOPSIS. Отрицательное число объектов
или допустимая сложность 999 дают результат, который выглядит как расчёт, но
им не является.
"""
from __future__ import annotations

from typing import Annotated, Any, Literal

from pydantic import BaseModel, Field, field_validator, model_validator

from ..models.enums import (
    DevStage, EngineCode, GameFormat, Level3, Platform, Priority, Resolution,
    Quality, Scale, WorldType,
)


def _values(enum_cls) -> list[str]:
    return [item.value for item in enum_cls]


#: Псевдоним для качественного уровня: везде low | medium | high.
LevelValue = Literal["low", "medium", "high"]


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
    engine: Literal[tuple(_values(EngineCode))] = "unreal"
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
    geometry_detail: LevelValue | None = None
    texture_quality: LevelValue | None = None
    view_distance: LevelValue | None = None
    lighting_complexity: LevelValue | None = None
    physics_complexity: LevelValue | None = None
    simulation_complexity: LevelValue | None = None
    npc_update_rate: LevelValue | None = None
    network_update_rate: LevelValue | None = None

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
            code = str(item).strip()
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
_LEVEL_FALLBACK: dict[str, float] = {"low": 0.25, "medium": 0.55, "high": 0.9}


def _level_from_count(value: int | None, field: str) -> str | None:
    if value is None:
        return None
    low, high = _COUNT_BOUNDS[field]
    if value < low:
        return "low"
    if value > high:
        return "high"
    return "medium"


def _effective_count(value: int | None, level: str, field: str) -> float:
    """Приводит «число или уровень» к одной числовой шкале 0..1.

    Точное число переводится логарифмически: разница между 1 000 и 10 000
    объектов заметна, а между 1 000 000 и 1 010 000 — нет. Шкала совпадает с
    численной оценкой уровня, поэтому уровень и число взаимозаменяемы, а
    указанное число действительно влияет на результат.
    """
    if value is None or value <= 0:
        return _LEVEL_FALLBACK.get(level, 0.55)
    import math

    low, high = _COUNT_BOUNDS[field]
    # «Низкий» и «высокий» уровни — за пределами этой логарифмической шкалы.
    span_low, span_high = max(1.0, low / 10.0), high * 10.0
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
            code = str(item).strip()
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
    # Явный список невыполненных обязательных ограничений: пределы памяти и
    # обязательные аппаратные возможности. Раньше они растворялись в caveats,
    # и интерфейс показывал конфигурацию как подходящую.
    unmet_limits: list[str] = Field(default_factory=list)


class SimilarGameOut(BaseModel):
    example: GameExampleOut
    similarity: float
    matching_optimizations: list[str]


class RecommendationResult(BaseModel):
    """Результат расчёта.

    Поле `input_key` — отпечаток профиля и корзины. Клиент сравнивает его со
    своим текущим состоянием и понимает, что результат получен именно для тех
    данных, которые сейчас на экране, а не для предыдущих.
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
    input_key: str = ""

    @model_validator(mode="after")
    def _fill_input_key(self):
        if not self.input_key:
            object.__setattr__(self, "input_key", input_fingerprint(self.profile, []))
        return self


def input_fingerprint(profile: ProjectProfile, basket: list[str]) -> str:
    """Устойчивый отпечаток входа: одинаковым данным — одинаковый ключ."""
    import hashlib
    import json

    payload = json.dumps(
        {"profile": profile.model_dump(mode="json"), "basket": sorted(basket or [])},
        sort_keys=True,
        ensure_ascii=False,
        separators=(",", ":"),
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:32]
