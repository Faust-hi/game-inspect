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
  effect_scopes: EnumOption[];
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
  /** Масштаб проекта (производства), а не мира. Объявляется пользователем. */
  project_scale: string;
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
  /** Минимальная версия движка, где инструмент существует; null — граница не задана. */
  min_version?: string | null;
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
  tool_min_version?: string | null;
  available?: boolean | null;
  availability_note?: string | null;
  source_locator?: string;
  /** Собственный URL связи; пусто — публичного источника не существует. */
  source_url?: string;
  evidence_basis?: string;
  evidence_status?: string;
}

export interface MethodVariant {
  /** Как именно метод может быть построен (например, «Global distance field»). */
  name: string;
  description: string;
  /** Основание варианта: documented / measured / expert_estimate / unknown. */
  basis: string;
  /** Коды источников, подтверждающих вариант. */
  evidence: string[];
}

export interface Method {
  application_steps?: string[];
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
  /** Решение реализуется своими средствами: пустые связи с инструментами движков — не пробел данных. */
  engine_tool_independent: boolean;
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
  /** Варианты реализации: пустой список — данных в исследовании нет, а не пробел переноса. */
  implementation_variants: MethodVariant[];
  /** Что нужно иметь до внедрения (данные, API, инструменты). */
  required_data_and_tools: string;
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
  /** Основание рекомендации: derived / expert_estimate / unknown / documented. */
  basis: string;
  source_url: string;
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
  benchmark_name?: string;
  benchmark_context?: string;
  benchmark_raw_value?: number | null;
  normalization_note?: string;
  evidence_basis?: string;
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
  benchmark_name?: string;
  benchmark_context?: string;
  benchmark_raw_value?: number | null;
  normalization_note?: string;
  evidence_basis?: string;
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
  /** Решение реализуется своими средствами: пустая поддержка движка — не пробел данных. */
  engine_tool_independent: boolean;
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
  /** Основание рекомендации «что делать» (см. `Conflict.basis`). */
  basis: string;
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
  frame_budget_ms?: number | null;
  target_assessments?: TargetAssessment[];
}

export interface EstimateBand {
  minimum: number | null;
  p50: number | null;
  p80: number | null;
  unit: string;
  basis: string;
  confidence?: number | null;
}

export interface TargetAssessment {
  metric: string;
  label: string;
  target: number | null;
  unit: string;
  status: string;
  estimated: number | null;
  basis: string;
  note: string;
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
  cpu_requirement?: EstimateBand | null;
  gpu_requirement?: EstimateBand | null;
  ram_requirement?: EstimateBand | null;
  vram_requirement?: EstimateBand | null;
  evidence_basis?: string;
  hardware_evidence?: string[];
  target_assessments?: TargetAssessment[];
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
  /** Единица измерения `delta`: «доля» (относительное изменение), «мс» или «×». */
  unit: string;
  detail: string;
}

export interface Contributions {
  parameters: ContributionItem[];
  methods: ContributionItem[];
  assumptions: string[];
  exclusions: string[];
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
  contributions: Contributions;
  stage_guidance?: StageGuidance | null;
  meta: Record<string, unknown>;
  /** Отпечаток входа, для которого выполнен расчёт (присваивается backend). */
  input_key: string;
  evidence_summary?: EvidenceSummary;
}

export interface EvidenceSource {
  code: string;
  title: string;
  authors: string;
  publisher: string;
  source_type: string;
  published_date: string;
  checked_at: string;
  url: string;
  version: string;
  platform: string;
  locator: string;
  availability: string;
  applicability: string;
  notes: string;
}

export interface EvidenceClaim {
  code: string;
  entity: string;
  entity_code: string;
  field: string;
  claim: string;
  unit: string;
  value_text: string;
  value_num?: number | null;
  range_min?: number | null;
  range_max?: number | null;
  source?: EvidenceSource | null;
  locator: string;
  basis: string;
  verification_status: string;
  evidence_level: string;
  formula: string;
  input_parameters: Record<string, unknown>;
  context: string;
}

export interface Dependency {
  code: string;
  source_code: string;
  source_name: string;
  source_type: string;
  target_code: string;
  target_name: string;
  target_type: string;
  dependency_type: string;
  mandatory: boolean;
  min_version: string;
  max_version: string;
  platform: string;
  scope: string;
  severity: number;
  source?: EvidenceSource | null;
  description: string;
  workaround: string;
  /** Основание обходного пути: derived / expert_estimate / unknown / documented. */
  basis: string;
  status: string;
}

export interface GraphIssue {
  check: string;
  severity: string;
  message: string;
  details: Record<string, unknown>;
}

export interface GraphChecks {
  issues: GraphIssue[];
  counts: Record<string, number>;
  engine?: string | null;
  engine_version?: string | null;
  render_api?: string | null;
  basket: string[];
}

export interface EvidenceSummary {
  source_count: number;
  claim_count: number;
  claims_with_sources: number;
  numeric_claims_published: number;
  numeric_claims_unknown: number;
  coverage_label: string;
  unconfirmed_numeric_factors: string[];
  calibration_status: string;
}

export interface ReportData {
  recommendation: RecommendationResult;
  evidence_summary: EvidenceSummary;
  sources: EvidenceSource[];
  dependencies: Dependency[];
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
