/**
 * Версии набора решений (патчи и обновления проекта).
 *
 * Патч или обновление игры меняет набор выбранных решений, и прежний набор
 * должен остаться доступным: без него нельзя сказать, что именно изменил патч
 * и как изменилась аппаратная оценка. Поэтому версия хранит не только коды
 * решений, но и сводку расчёта на момент сохранения.
 */
import type {
  ProjectProfile,
  ProjectVersion,
  RecommendationResult,
  VersionDiff,
  VersionSummary,
} from './types';

const STORAGE_KEY = 'gamedev_dss_versions_v1';

/** Сколько лидеров рейтинга сохраняется в версии: полный список не нужен. */
const TOP_RECOMMENDATIONS = 8;

/** Русские подписи полей профиля: в сравнении версий коды полей не читаются. */
const PROFILE_LABELS: Record<string, string> = {
  name: 'Название',
  format: 'Формат',
  world_type: 'Тип мира',
  scale: 'Масштаб',
  stage: 'Стадия',
  engine: 'Движок',
  engine_version: 'Версия движка',
  platforms: 'Платформы',
  functions: 'Функции',
  object_count_level: 'Число объектов',
  object_count: 'Число объектов (точно)',
  npc_count_level: 'Число NPC',
  npc_count: 'Число NPC (точно)',
  player_count: 'Игроков',
  local_view_count: 'Поле зрения',
  multiplayer: 'Мультиплеер',
  target_resolution: 'Разрешение',
  target_quality: 'Качество',
  target_fps: 'Частота кадров',
  render_api: 'Графический API',
  storage_type: 'Накопитель',
  memory_model: 'Модель памяти',
  upscaling_method: 'Масштабирование',
  network_topology: 'Сетевая топология',
  frame_generation: 'Генерация кадров',
  base_render_fps: 'Базовый FPS',
  streaming_pool_gb: 'Пул стриминга, ГБ',
  draw_call_budget: 'Бюджет вызовов',
  simulation_radius_m: 'Радиус симуляции, м',
  physics_tick_hz: 'Тик физики, Гц',
  audio_complexity: 'Сложность аудио',
  ram_limit_gb: 'Предел RAM, ГБ',
  vram_limit_gb: 'Предел VRAM, ГБ',
  size_limit_gb: 'Предел размера, ГБ',
  deadline_weeks: 'Срок, недель',
  complexity_tolerance: 'Допустимая сложность',
  priority: 'Приоритет',
  cpu_budget: 'Бюджет CPU',
  gpu_budget: 'Бюджет GPU',
  ram_budget: 'Бюджет RAM',
  vram_budget: 'Бюджет VRAM',
};

function formatValue(value: unknown): string {
  if (value === null || value === undefined || value === '') return 'не задано';
  if (Array.isArray(value)) return value.length > 0 ? value.join(', ') : 'пусто';
  if (typeof value === 'boolean') return value ? 'да' : 'нет';
  return String(value);
}

/** Сводка расчёта, которая сохраняется вместе с версией. */
export function summaryOf(result: RecommendationResult | null, basket: string[]): VersionSummary | null {
  if (!result) return null;
  const hardware = result.hardware;
  return {
    algorithm_version: typeof result.meta?.algorithm_version === 'string'
      ? result.meta.algorithm_version
      : null,
    catalog_revision: result.catalog_revision ?? null,
    recommendations: result.recommendations.slice(0, TOP_RECOMMENDATIONS).map((item) => ({
      code: item.method_code,
      name: item.method_name,
      score: item.score,
    })),
    basket_size: basket.length,
    hardware: hardware
      ? {
          reference_cpu: hardware.reference_cpu?.model ?? null,
          reference_gpu: hardware.reference_gpu?.model ?? null,
          estimated_ram_gb: hardware.estimated_ram_gb,
          estimated_vram_gb: hardware.estimated_vram_gb,
          bottleneck_label: hardware.bottleneck_label ?? null,
          confidence_label: hardware.confidence_label ?? null,
        }
      : null,
    conflict_count: result.basket_conflicts.length,
  };
}

function round(value: number | null): number | null {
  return value === null ? null : Math.round(value * 10) / 10;
}

/**
 * Разница между сохранённой версией и текущим состоянием.
 *
 * Сравнивается и набор решений, и профиль: патч часто меняет не только
 * решения, но и цель проекта — разрешение, частоту кадров, платформы.
 */
export function diffVersion(
  version: ProjectVersion,
  profile: ProjectProfile,
  basket: string[],
  result: RecommendationResult | null,
): VersionDiff {
  const previous = new Set(version.basket);
  const current = new Set(basket);

  const profile_changes: VersionDiff['profile_changes'] = [];
  for (const key of Object.keys(PROFILE_LABELS)) {
    const field = key as keyof ProjectProfile;
    const from = version.profile[field];
    const to = profile[field];
    const fromText = formatValue(from);
    const toText = formatValue(to);
    if (Array.isArray(from) && Array.isArray(to)) {
      // Порядок выбора на расчёт не влияет: перестановка кодов не изменение.
      if ([...from].sort().join() === [...to].sort().join()) continue;
    } else if (fromText === toText) {
      continue;
    }
    profile_changes.push({
      field: key,
      label: PROFILE_LABELS[key],
      from: fromText,
      to: toText,
    });
  }

  const summary = summaryOf(result, basket);
  const saved = version.summary?.hardware ?? null;
  const actual = summary?.hardware ?? null;

  return {
    added: [...current].filter((code) => !previous.has(code)),
    removed: [...previous].filter((code) => !current.has(code)),
    kept: [...current].filter((code) => previous.has(code)),
    profile_changes,
    hardware:
      saved && actual
        ? {
            ram_delta_gb:
              actual.estimated_ram_gb === null || saved.estimated_ram_gb === null
                ? null
                : round(actual.estimated_ram_gb - saved.estimated_ram_gb),
            vram_delta_gb:
              actual.estimated_vram_gb === null || saved.estimated_vram_gb === null
                ? null
                : round(actual.estimated_vram_gb - saved.estimated_vram_gb),
            cpu_changed: saved.reference_cpu !== actual.reference_cpu,
            gpu_changed: saved.reference_gpu !== actual.reference_gpu,
            bottleneck_changed: saved.bottleneck_label !== actual.bottleneck_label,
          }
        : null,
  };
}

function isVersion(value: unknown): value is ProjectVersion {
  if (typeof value !== 'object' || value === null) return false;
  const item = value as Record<string, unknown>;
  return (
    typeof item.id === 'string' &&
    typeof item.number === 'number' &&
    Array.isArray(item.basket) &&
    item.basket.every((code) => typeof code === 'string') &&
    typeof item.profile === 'object' &&
    item.profile !== null
  );
}

/** Чтение истории версий: повреждённые записи отбрасываются целиком. */
export function loadVersions(): ProjectVersion[] {
  try {
    const raw = sessionStorage.getItem(STORAGE_KEY);
    if (!raw) return [];
    const parsed: unknown = JSON.parse(raw);
    if (!Array.isArray(parsed)) return [];
    return parsed.filter(isVersion);
  } catch {
    return [];
  }
}

export function saveVersions(versions: ProjectVersion[]): boolean {
  try {
    sessionStorage.setItem(STORAGE_KEY, JSON.stringify(versions));
    return true;
  } catch {
    return false;
  }
}

/** Подпись версии: «Версия 2 · Патч 1.1 · 08.09.2026, 16:40». */
export function versionTitle(version: ProjectVersion): string {
  const date = new Date(version.created_at);
  const stamp = Number.isNaN(date.getTime())
    ? version.created_at
    : date.toLocaleString('ru-RU', { dateStyle: 'short', timeStyle: 'short' });
  return `Версия ${version.number} · ${version.label || 'без названия'} · ${stamp}`;
}

/** Подпись для автоматически сохраняемой версии: «Патч 3». */
export function nextVersionLabel(count: number, stage: string): string {
  return stage === 'post_release' ? `Патч ${count + 1}` : `Версия ${count + 1}`;
}
