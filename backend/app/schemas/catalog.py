"""Pydantic-схемы каталогов и профиля проекта."""
from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field, field_validator


# ---------------------------------------------------------------------------
# Профиль проекта (анкета, раздел 3 плана)
# ---------------------------------------------------------------------------
class ProjectProfile(BaseModel):
    """Описание разрабатываемой игры, заполняемое пользователем."""

    name: str = "Проект без названия"

    # Формат и структура мира
    format: str = "3D"                     # 2D | 2.5D | 3D
    world_type: str = "open_world"         # linear | hub | arena | open_world | procedural | sandbox
    scale: str = "large"                   # small | medium | large | very_large

    # Стадия и технологии
    stage: str = "prototype"               # concept..post_release
    engine: str = "unreal"                 # unreal | unity | godot | custom
    engine_version: str | None = None
    platforms: list[str] = Field(default_factory=lambda: ["pc_windows"])

    # Масштаб сцены
    object_count_level: str = "medium"     # low | medium | high
    object_count: int | None = None
    npc_count_level: str = "medium"
    npc_count: int | None = None
    player_count: int = 1
    multiplayer: bool = False

    # Функции
    functions: list[str] = Field(default_factory=list)

    # Целевые показатели
    target_resolution: str = "1080p"
    target_quality: str = "high"           # low | medium | high | ultra
    target_fps: int = 60

    # Обязательные ограничения
    ram_limit_gb: float | None = None
    vram_limit_gb: float | None = None
    size_limit_gb: float | None = None
    deadline_weeks: int | None = None
    complexity_tolerance: int | None = None   # 1..5

    # Приоритет при ранжировании
    priority: str = "balanced"             # quality | performance | cost | balanced

    # Проектные бюджеты (качественные уровни)
    cpu_budget: str | None = None          # low | medium | high
    gpu_budget: str | None = None
    ram_budget: str | None = None
    vram_budget: str | None = None
    geometry_detail: str | None = None
    texture_quality: str | None = None
    view_distance: str | None = None
    lighting_complexity: str | None = None
    physics_complexity: str | None = None
    simulation_complexity: str | None = None
    npc_update_rate: str | None = None
    network_update_rate: str | None = None

    @field_validator("target_fps")
    @classmethod
    def _fps(cls, v: int) -> int:
        return max(15, min(480, int(v)))

    @field_validator("functions", mode="before")
    @classmethod
    def _uniq(cls, v):
        if not v:
            return []
        seen, out = set(), []
        for item in v:
            if item not in seen:
                seen.add(item)
                out.append(item)
        return out


class BasketRequest(BaseModel):
    """Профиль проекта и выбранные решения («корзина проекта»)."""

    profile: ProjectProfile
    basket: list[str] = Field(default_factory=list)


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


class SimilarGameOut(BaseModel):
    example: GameExampleOut
    similarity: float
    matching_optimizations: list[str]


class RecommendationResult(BaseModel):
    profile: ProjectProfile
    risks: list[RiskOut]
    recommendations: list[RecommendationOut]
    excluded: list[RecommendationOut]
    load_profile: LoadProfileOut
    basket_conflicts: list[BasketConflictOut]
    basket_synergies: list[BasketConflictOut]
    hardware: HardwareEstimateOut | None = None
    similar_games: list[SimilarGameOut] = Field(default_factory=list)
    meta: dict[str, Any] = Field(default_factory=dict)
