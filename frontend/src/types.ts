/** Типы данных, отражающие контракты backend-приложения. */
export interface ImplementationBaseline { profile: ProjectProfile; basket: string[] }
export interface ImplementationTransition {
  method_code: string;
  status: string;
  scope: string;
  cost_min: number;
  cost_max: number;
  complexity_min: number;
  complexity_max: number;
  replaces: string[];
  affected_methods: string[];
  reasons: string[];
  evidence: string;
}

export interface EnumOption {
  value: string;
  label: string;
}

export interface Enums {
  formats: EnumOption[];
  world_types: EnumOption[];
  scales: EnumOption[];
  stages: EnumOption[];
  platforms: EnumOption[];
  levels: EnumOption[];
  render_apis: EnumOption[];
  storage_types: EnumOption[];
  memory_models: EnumOption[];
  upscalers: EnumOption[];
  network_topologies: EnumOption[];
  priorities: EnumOption[];
  solution_levels: EnumOption[];
  late_costs: EnumOption[];
  calc_modes: EnumOption[];
  relation_types: EnumOption[];
  conflict_types: EnumOption[];
  statuses: EnumOption[];
  method_kinds: EnumOption[];
}

/** Анкета проекта (раздел 3 плана). */
export interface ProjectProfile {
  name: string;
  format: string;
  world_type: string;
  scale: string;
  stage: string;
  engine: string;
  engine_version?: string | null;
  platforms: string[];
  object_count_level: string;
  object_count?: number | null;
  npc_count_level: string;
  npc_count?: number | null;
  player_count: number;
  local_view_count?: number | null;
  multiplayer: boolean;
  functions: string[];
  target_resolution: string;
  target_quality: string;
  target_fps: number;
  render_api: string;
  storage_type: string;
  memory_model: string;
  upscaling_method: string;
  network_topology: string;
  frame_generation: boolean;
  base_render_fps?: number | null;
  streaming_pool_gb?: number | null;
  draw_call_budget?: number | null;
  simulation_radius_m?: number | null;
  physics_tick_hz?: number | null;
  audio_complexity?: string | null;
  ram_limit_gb?: number | null;
  vram_limit_gb?: number | null;
  size_limit_gb?: number | null;
  deadline_weeks?: number | null;
  complexity_tolerance?: number | null;
  priority: string;
  cpu_budget?: string | null;
  gpu_budget?: string | null;
  ram_budget?: string | null;
  vram_budget?: string | null;
}

export interface GameFunction {
  code: string;
  name: string;
  description: string;
  category: string;
  formats: string[];
  typical_world_types: string[];
  sort_order: number;
  source_title: string;
  source_url: string;
}

export interface EngineTool {
  code: string;
  name: string;
  subsystem: string;
  description: string;
  tool_type: string;
  docs_url: string;
}

export interface Engine {
  code: string;
  name: string;
  vendor: string;
  versions: string[];
  supported_formats: string[];
  notes: string;
  docs_url: string;
  tools: EngineTool[];
}

export interface MethodEngineLink {
  engine_code: string;
  engine_name: string;
  tool_code: string;
  tool_name: string;
  relation_type: string;
  relation_label: string;
  note: string;
  docs_url: string;
}

export interface Method {
  application_steps?: string[];
  used_in_projects?: string[];
  code: string;
  name: string;
  kind: string;
  function_code: string | null;
  summary: string;
  description: string;
  problem: string;
  pros: string[];
  cons: string[];
  limitations: string[];
  level: string;
  level_label: string;
  recommended_stage: string;
  recommended_stage_label: string;
  late_cost: string;
  late_cost_label: string;
  calc_mode: string;
  calc_mode_label: string;
  /** Где проявляется эффект: только `client` меняет требования к компьютеру игрока. */
  effect_scope: string;
  effect_scope_label: string;
  impact_cpu: number;
  impact_gpu: number;
  impact_ram: number;
  impact_vram: number;
  impact_disk: number;
  impact_network: number;
  quality_impact: number;
  concept_impact: number;
  performance_gain: number;
  implementation_cost: number;
  complexity: number;
  confidence: number;
  requires_prototype: boolean;
  applicable_formats: string[];
  applicable_world_types: string[];
  applicable_engines: string[];
  applicable_platforms: string[];
  requires_features: string[];
  requires_hw_features: string[];
  requires_conditions: string[];
  verification_method: string;
  verification_tools: string[];
  status: string;
  source_title: string;
  source_url: string;
  engine_links: MethodEngineLink[];
}

export interface Conflict {
  a_code: string;
  b_code: string;
  conflict_type: string;
  conflict_label: string;
  severity: number;
  description: string;
  resolution: string;
  source_url: string;
}

export interface GameExample {
  title: string;
  year: number;
  developer: string;
  engine: string;
  format: string;
  world_type: string;
  scale: string;
  platforms: string[];
  target_resolution: string;
  target_fps: number;
  object_count_level: string;
  npc_count_level: string;
  multiplayer: boolean;
  player_count: number;
  features: string[];
  optimizations_used: string[];
  summary: string;
  performance_outcome: string;
  source_title: string;
  source_url: string;
  verified_by: string;
}

export interface HardwareCPU {
  model: string;
  vendor: string;
  generation: string;
  architecture: string;
  release_year: number;
  cores: number;
  threads: number;
  single_thread_score: number;
  multi_thread_score: number;
  perf_class: number;
  memory_support: string;
  tdp_w: number;
  notes: string;
  source_title: string;
  source_url: string;
}

export interface HardwareGPU {
  model: string;
  vendor: string;
  generation: string;
  architecture: string;
  release_year: number;
  vram_gb: number;
  vram_type: string;
  memory_bandwidth_gbs: number;
  api_support: string[];
  hw_features: string[];
  raster_score: number;
  rt_score: number;
  perf_class: number;
  tdp_w: number;
  notes: string;
  source_title: string;
  source_url: string;
}

export interface CriterionScore {
  key: string;
  label: string;
  raw: number;
  normalized: number;
  weight: number;
  weighted: number;
  kind: string;
}

export interface RankStability {
  rank_min: number;
  rank_max: number;
  stable: boolean;
}

export interface SuggestedMethod {
  method_code: string;
  reason: string;
}

export interface Recommendation {
  transition?: ImplementationTransition | null;
  method_code: string;
  method_name: string;
  function_code: string | null;
  function_name: string | null;
  kind: string;
  score: number;
  rank: number;
  flags: string[];
  flag_labels: string[];
  reasons: string[];
  stability?: RankStability | null;
  excluded_reasons: string[];
  criteria: CriterionScore[];
  engine_support: MethodEngineLink | null;
  engine_alternatives: MethodEngineLink[];
  summary: string;
  performance_gain: number;
  implementation_cost: number;
  complexity: number;
  late_cost: string;
  recommended_stage: string;
  quality_impact: number;
  concept_impact: number;
  source_url: string;
  effect_scope: string;
  effect_scope_label: string;
  equivalent_to_leader?: boolean;
  score_gap?: number;
}

export interface Risk {
  code: string;
  title: string;
  severity: string;
  description: string;
  advice: string;
}

/** Разбор сводки по одному ресурсу. */
export interface LoadResourceDetail {
  /** Для количественных ресурсов — относительное изменение стоимости кадра. */
  raw: number;
  normalized: number;
  label: string;
  direction: string;
  /**
   * false — ресурс без числовой модели (накопитель, сеть).
   * Его normalized всегда равен нейтральным 50, а смысл несёт level.
   */
  quantitative: boolean;
  /** Качественный уровень влияния для ресурсов без числовой модели. */
  level?: string;
  /** Пояснение: что именно утверждается и чего в оценке нет. */
  explanation?: string;
}

export interface LoadProfile {
  notes?: string[];
  cpu: number;
  gpu: number;
  ram: number;
  vram: number;
  /** Накопитель: без числовой модели, значение всегда нейтральное 50. */
  disk: number;
  /** Сеть: без числовой модели, значение всегда нейтральное 50. */
  network: number;
  per_resource: Record<string, LoadResourceDetail>;
}

export interface BasketConflict {
  a_code: string;
  a_name: string;
  b_code: string;
  b_name: string;
  conflict_type: string;
  conflict_label: string;
  severity: number;
  description: string;
  resolution: string;
}

export interface SubsystemBreakdown {
  label: string;
  share: number;
}

export interface MemoryComposition {
  label: string;
  ram_gb: number;
  vram_gb: number;
}

/** Одна цель сборки: ОС и разрешённый для неё графический API. */
export interface PlatformTarget {
  platform: string;
  label: string;
  render_api: string;
  api_label: string;
  /** explicit — задан пользователем, auto — выбран по ОС. */
  api_source: string;
  compatible: boolean;
  /** confirmed, mismatch или unknown — сверка API с движком. */
  engine_check: string;
  notes: string[];
  cpu_index: number | null;
  gpu_index: number | null;
  ram_gb: number | null;
  vram_gb: number | null;
  /** Цель с наибольшей потребностью: она объясняет общий ориентир. */
  binding: boolean;
}

export interface HardwareEstimate {
  required_gpu_index: number;
  required_cpu_index: number;
  estimated_vram_gb: number;
  estimated_ram_gb: number;
  gpu_class: number;
  cpu_class: number;
  reference_gpu: HardwareGPU | null;
  reference_cpu: HardwareCPU | null;
  alternative_gpus: HardwareGPU[];
  alternative_cpus: HardwareCPU[];
  confidence: number;
  confidence_label: string;
  caveats: string[];
  required_hw_features: string[];
  exceeds_catalog: boolean;
  /** Явный список невыполненных обязательных ограничений (пределы памяти, RT). */
  unmet_limits: string[];
  /** Выход входов за область применимости модели (насыщение шкал, платформы). */
  applicability_limits?: string[];
  recommended_storage: string;
  estimated_draw_calls: number;
  modeling_gaps: string[];
  /** Решения, не вошедшие в расчёт: их эффект не относится к компьютеру игрока. */
  non_client_methods: NonClientMethod[];
  /** Подсистемный разбор (исправление расчётной модели). */
  cpu_main_thread_cost: number;
  cpu_parallel_cost: number;
  cpu_subsystems: SubsystemBreakdown[];
  gpu_raster_cost: number;
  gpu_rt_cost: number;
  gpu_subsystems: SubsystemBreakdown[];
  bottleneck: string;
  bottleneck_label: string;
  memory_composition: MemoryComposition[];
  consequences: string[];
  storage_requirement: string;
  /** Цели сборки считаются и показываются раздельно. */
  targets?: PlatformTarget[];
}

/** Решение из корзины, исключённое из аппаратной оценки с указанием причины. */
export interface NonClientMethod {
  code: string;
  name: string;
  effect_scope: string;
  effect_scope_label: string;
  reason: string;
}

export interface ContributionItem {
  label: string;
  delta: number;
  detail: string;
}

export interface Contributions {
  parameters: ContributionItem[];
  methods: ContributionItem[];
  assumptions: string[];
  exclusions: string[];
}

export interface PracticeCheck {
  status: string;
  title: string;
  message: string;
  details: string[];
}

/** Предупреждение или предложение, привязанное к стадии проекта. */
export interface StageNote {
  code: string;
  title: string;
  text: string;
}

/** Что означает текущая стадия для выбора решений. */
export interface StageGuidance {
  stage: string;
  stage_label: string;
  summary: string;
  available_levels: string[];
  available_level_labels: string[];
  /** Уровни, внедрение которых целиком требует переработки. */
  rework_levels: string[];
  rework_level_labels: string[];
  /** Уровни, у которых переработку требует только часть решений. */
  restricted_levels: string[];
  restricted_level_labels: string[];
  warnings: StageNote[];
  suggestions: StageNote[];
}

export interface RecommendationResult {
  baseline?: ImplementationBaseline | null;
  transitions?: ImplementationTransition[];
  snapshot_id?: string | null;
  catalog_revision?: string | null;
  selected_methods?: Method[];
  accounted_method_codes?: string[];
  basket_codes?: string[];
  profile: ProjectProfile;
  risks: Risk[];
  recommendations: Recommendation[];
  excluded: Recommendation[];
  load_profile: LoadProfile;
  basket_conflicts: BasketConflict[];
  /** Закрытые зависимости: решения, осмысленные только в паре. */
  basket_dependencies: BasketConflict[];
  basket_synergies: BasketConflict[];
  hardware: HardwareEstimate | null;
  practice_check: PracticeCheck;
  contributions: Contributions;
  stage_guidance?: StageGuidance | null;
  meta: Record<string, unknown>;
  /** Отпечаток входа, для которого выполнен расчёт (присваивается backend). */
  input_key: string;
}

export interface ValidationIssue {
  entity: string;
  entity_code: string;
  severity: string;
  message: string;
}

export interface AdminOverview {
  counts: Record<string, number>;
  /** Снимок опубликованных записей по сущностям — вне counts, т.к. там только числа. */
  published?: Record<string, number>;
  issues: ValidationIssue[];
  issues_by_severity: { error: number; warning: number };
}

/** Запись, не попавшая в базу при заполнении: причина обязательна. */
export interface SeedSkip {
  entity: string;
  entity_label: string;
  key: string;
  reason: string;
}

/** Существующая запись, сохранённая при заполнении: правки не затираются. */
export interface SeedPreserved {
  entity: string;
  entity_label: string;
  key: string;
  fields: string[];
}

export interface SeedReport {
  functions: number;
  methods: number;
  engines: number;
  engine_tools: number;
  method_engine_links: number;
  conflicts: number;
  hardware_records: number;
  validation_issues: number;
  added: Record<string, number>;
  skipped: SeedSkip[];
  skipped_count: number;
  preserved: SeedPreserved[];
  preserved_count: number;
}
