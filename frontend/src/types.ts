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

export interface ProjectImport {
  profile: ProjectProfile;
  /**
   * Только реально извлечённые из файлов поля.
   *
   * `profile` — это предпросмотр полной анкеты: незаполненные поля в нём
   * содержат значения по умолчанию. Применение `profile` целиком сбросило бы
   * ответы пользователя, поэтому применяется только `patch`.
   */
  patch: Partial<ProjectProfile>;
  filled: string[];
  suggested: SuggestedMethod[];
  detected: string[];
  warnings: string[];
}

export interface PresetFile {
  name: string;
  language: string;
  content: string;
}

export interface FeedbackVote {
  public_id: string;
  method_code: string;
  up: number;
  down: number;
}

export interface FeedbackSummary {
  projects_with_feedback: number;
  methods: { method_code: string; up: number; down: number; total: number; helpful_rate: number }[];
  suggestions: { method_code: string; current_confidence: number; suggested_confidence: number; reason: string }[];
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
  recommended_storage: string;
  estimated_draw_calls: number;
  modeling_gaps: string[];
}

export interface SimilarGame {
  example: GameExample;
  similarity: number;
  matching_optimizations: string[];
}

export interface RecommendationResult {
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
  similar_games: SimilarGame[];
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
  game_examples: number;
  hardware_records: number;
  validation_issues: number;
  added: Record<string, number>;
  skipped: SeedSkip[];
  skipped_count: number;
  preserved: SeedPreserved[];
  preserved_count: number;
}
