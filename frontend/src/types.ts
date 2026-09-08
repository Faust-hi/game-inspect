/** Типы данных, отражающие контракты backend-приложения. */

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

export interface LoadProfile {
  notes?: string[];
  cpu: number;
  gpu: number;
  ram: number;
  vram: number;
  disk: number;
  network: number;
  per_resource: Record<
    string,
    { raw: number; normalized: number; label: string; direction: string }
  >;
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
  blocked_levels: string[];
  blocked_level_labels: string[];
  /** Уровни, у которых закрыта только часть решений. */
  restricted_levels: string[];
  restricted_level_labels: string[];
  warnings: StageNote[];
  suggestions: StageNote[];
}

export interface RecommendationResult {
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

/** Сводка расчёта, сохранённая вместе с версией набора. */
export interface VersionSummary {
  algorithm_version?: string | null;
  catalog_revision?: string | null;
  /** Ограниченный список лидеров: полный результат сохранять незачем. */
  recommendations: { code: string; name: string; score: number }[];
  basket_size: number;
  hardware: {
    reference_cpu: string | null;
    reference_gpu: string | null;
    estimated_ram_gb: number | null;
    estimated_vram_gb: number | null;
    bottleneck_label: string | null;
    confidence_label: string | null;
  } | null;
  conflict_count: number;
}

/**
 * Сохранённая версия набора решений.
 *
 * Патч или обновление игры меняет набор решений, и прежний набор должен
 * остаться доступным: без него нельзя сказать, что именно изменил патч.
 * Версия хранит не только коды, но и сводку расчёта — иначе сравнение версий
 * свелось бы к списку кодов и не показывало изменение аппаратной оценки.
 */
export interface ProjectVersion {
  id: string;
  /** Порядковый номер, начиная с 1: «версия 3» понятнее идентификатора. */
  number: number;
  label: string;
  note: string;
  created_at: string;
  profile: ProjectProfile;
  basket: string[];
  /** Отпечаток входа: совпадение с текущим ключом означает «изменений нет». */
  input_key: string;
  summary: VersionSummary | null;
}

/** Разница между сохранённой версией и текущим набором. */
export interface VersionDiff {
  added: string[];
  removed: string[];
  kept: string[];
  /** Изменившиеся поля профиля с человекочитаемыми названиями. */
  profile_changes: { field: string; label: string; from: string; to: string }[];
  hardware: {
    ram_delta_gb: number | null;
    vram_delta_gb: number | null;
    cpu_changed: boolean;
    gpu_changed: boolean;
    bottleneck_changed: boolean;
  } | null;
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
