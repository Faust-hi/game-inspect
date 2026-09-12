/** Состояние проекта: анкета, корзина решений и результат расчёта. */
import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useRef,
  useState,
  type ReactNode,
} from 'react';
import { api } from './api';
import type {
  ImplementationBaseline,
  Conflict,
  Engine,
  Enums,
  GameFunction,
  Method,
  ProjectProfile,
  RecommendationResult,
} from './types';

const STORAGE_KEY = 'gamedev_dss_project_v1';

export const DEFAULT_PROFILE: ProjectProfile = {
  name: 'Новый проект',
  format: '3D',
  world_type: 'open_world',
  scale: 'large',
  project_scale: 'medium',
  stage: 'prototype',
  engine: 'unreal',
  engine_version: null,
  platforms: ['pc_windows'],
  object_count_level: 'medium',
  object_count: null,
  npc_count_level: 'medium',
  npc_count: null,
  player_count: 1,
  local_view_count: null,
  multiplayer: false,
  functions: [],
  target_resolution: '1080p',
  target_quality: 'high',
  target_fps: 60,
  render_api: 'auto',
  storage_type: 'auto',
  memory_model: 'auto',
  upscaling_method: 'auto',
  network_topology: 'auto',
  frame_generation: false,
  base_render_fps: null,
  streaming_pool_gb: null,
  draw_call_budget: null,
  simulation_radius_m: null,
  physics_tick_hz: null,
  audio_complexity: null,
  ram_limit_gb: null,
  vram_limit_gb: null,
  size_limit_gb: null,
  complexity_tolerance: null,
  priority: 'balanced',
  cpu_budget: null,
  gpu_budget: null,
  ram_budget: null,
  vram_budget: null,
};

/** Упорядоченная сериализация: одинаковым данным — одинаковая строка. */
function stableStringify(value: unknown): string {
  if (value === null || value === undefined) return 'null';
  if (typeof value !== 'object') return JSON.stringify(value) ?? 'null';
  if (Array.isArray(value)) return `[${value.map(stableStringify).join(',')}]`;
  const entries = Object.entries(value as Record<string, unknown>)
    .filter(([, item]) => item !== undefined)
    .sort(([a], [b]) => (a < b ? -1 : a > b ? 1 : 0));
  return `{${entries.map(([key, item]) => `${JSON.stringify(key)}:${stableStringify(item)}`).join(',')}}`;
}

/**
 * Отпечаток входа: профиль плюс корзина.
 *
 * Порядок кодов в корзине на расчёт не влияет, поэтому корзина сортируется —
 * иначе перестановка решений выглядела бы как изменение данных.
 */
export function inputKeyOf(profile: ProjectProfile, basket: string[], baseline?: ImplementationBaseline | null): string {
  return stableStringify({ profile: { ...profile,
    functions: [...new Set(profile.functions)].sort(),
    platforms: [...new Set(profile.platforms)].sort(),
    target_resolution: profile.target_resolution === '4k' ? '2160p' : profile.target_resolution,
  }, basket: [...new Set(basket)].sort(), ...(baseline ? { baseline: inputKeyOf(baseline.profile, baseline.basket) } : {}) });
}

function isAbortError(error: unknown): boolean {
  return error instanceof Error && error.name === 'AbortError';
}

/**
 * Согласовать зависимые поля профиля после правки.
 *
 * Поле, потерявшее смысл, обязано очищаться: иначе оно остаётся в профиле и
 * продолжает влиять на расчёт, хотя в анкете уже скрыто. Два случая:
 * число локальных камер учитывается расчётом независимо от функции
 * split-screen, поэтому при её снятии значение сбрасывается; базовый FPS
 * генератора кадров выше целевого FPS — противоречие, которое сервер
 * отклоняет целиком (422), поэтому при снижении целевого FPS оно снимается,
 * а не подменяется другим числом.
 */
function reconcileProfile(prev: ProjectProfile, patch: Partial<ProjectProfile>): ProjectProfile {
  const next = { ...prev, ...patch };
  if (!next.functions.includes('split_screen_rendering')) {
    next.local_view_count = null;
  }
  if (!next.frame_generation) {
    next.base_render_fps = null;
  } else if (next.base_render_fps != null && next.base_render_fps > next.target_fps) {
    next.base_render_fps = null;
  }
  return next;
}

function errorMessage(error: unknown): string {
  if (error instanceof Error) return error.message;
  return 'Расчёт не выполнен';
}

interface CatalogState {
  enums: Enums | null;
  functions: GameFunction[];
  methods: Method[];
  engines: Engine[];
  conflicts: Conflict[];
  loading: boolean;
  error: string | null;
}

interface ProjectStore {
  baseline: ImplementationBaseline | null;
  saveBaseline: () => void;
  profile: ProjectProfile;
  basket: string[];
  result: RecommendationResult | null;
  /** Отпечаток входа, для которого получен `result`. */
  resultKey: string | null;
  /** Отпечаток текущего входа: расходится с `resultKey` после правки анкеты. */
  inputKey: string;
  catalog: CatalogState;
  calculating: boolean;
  calculateError: string | null;
  storageError: string | null;
  updateProfile: (patch: Partial<ProjectProfile>) => void;
  resetProfile: () => void;
  toggleBasket: (code: string) => void;
  setBasket: (codes: string[]) => void;
  clearBasket: () => void;
  calculate: () => Promise<void>;
  reloadCatalog: () => Promise<void>;
}

const StoreContext = createContext<ProjectStore | null>(null);

function loadPersisted(value?: string, allowBaseline = true): { profile: ProjectProfile; basket: string[]; baseline: ImplementationBaseline | null } | null {
  try {
    const raw = value ?? sessionStorage.getItem(STORAGE_KEY);
    if (!raw) return null;
    const parsed: unknown = JSON.parse(raw);
    if (!parsed || typeof parsed !== 'object' || !('profile' in parsed) || !('basket' in parsed)) return null;
    if (!parsed.profile || typeof parsed.profile !== 'object' || Array.isArray(parsed.profile)) return null;
    if (!Array.isArray(parsed.basket) || !parsed.basket.every(code => typeof code === 'string')) return null;
    const restored = { ...DEFAULT_PROFILE };
    for (const [key, value] of Object.entries(parsed.profile)) {
      if (!(key in DEFAULT_PROFILE)) continue;
      const defaultValue = DEFAULT_PROFILE[key as keyof ProjectProfile];
      const valid = Array.isArray(defaultValue)
        ? Array.isArray(value) && value.every(item => typeof item === 'string')
        : defaultValue === null
          ? value === null || (['engine_version', 'audio_complexity', 'cpu_budget', 'gpu_budget', 'ram_budget', 'vram_budget'].includes(key)
            ? typeof value === 'string' : typeof value === 'number' && Number.isFinite(value) && value >= 0)
          : typeof value === typeof defaultValue && (typeof value !== 'number' || Number.isFinite(value));
      if (!valid) return null;
      Object.assign(restored, { [key]: value });
    }
    let baseline: ImplementationBaseline | null = null;
    if (allowBaseline && 'baseline' in parsed && parsed.baseline != null) {
      const saved = loadPersisted(JSON.stringify(parsed.baseline), false);
      if (!saved) return null;
      baseline = { profile: saved.profile, basket: saved.basket };
    }
    // Псевдоним разрешения. Модель принимает и `4k`, и `2160p`, но анкета
    // предлагает только `2160p`. Без приведения сохранённый профиль с `4k`
    // показывал пустое поле выбора, хотя значение продолжало участвовать в
    // расчёте: отпечаток входа нормализует `4k`, а само поле — нет.
    if (restored.target_resolution === '4k') restored.target_resolution = '2160p';
    return {
      baseline,
      profile: restored,
      basket: [...new Set(parsed.basket)],
    };
  } catch {
    return null;
  }
}

export function StoreProvider({ children }: { children: ReactNode }) {
  const persisted = useMemo(() => loadPersisted(), []);
  const [baseline, setBaseline] = useState<ImplementationBaseline | null>(persisted?.baseline ?? null);
  const [profile, setProfile] = useState<ProjectProfile>(persisted?.profile ?? DEFAULT_PROFILE);
  const [basket, setBasketState] = useState<string[]>(persisted?.basket ?? []);
  const [result, setResult] = useState<RecommendationResult | null>(null);
  const [resultKey, setResultKey] = useState<string | null>(null);
  const [calculating, setCalculating] = useState(false);
  const [calculateError, setCalculateError] = useState<string | null>(null);
  const [storageError, setStorageError] = useState<string | null>(null);
  const [catalog, setCatalog] = useState<CatalogState>({
    enums: null,
    functions: [],
    methods: [],
    engines: [],
    conflicts: [],
    loading: true,
    error: null,
  });

  /** Выполняющийся запрос расчёта. Предыдущий отменяется при новом запуске. */
  const inFlight = useRef<AbortController | null>(null);

  const inputKey = useMemo(() => inputKeyOf(profile, basket, baseline), [profile, basket, baseline]);

  /**
   * Сбрасывает результат и отменяет выполняющийся запрос.
   *
   * Любое изменение входа делает прежний результат не относящимся к данным на
   * экране. Раньше результат сохранялся, и разделы рисков, нагрузки и
   * оборудования показывали расчёт для предыдущих значений профиля и корзины.
   */
  const discardResult = useCallback(() => {
    inFlight.current?.abort();
    inFlight.current = null;
    setResult(null);
    setResultKey(null);
    setCalculating(false);
    setCalculateError(null);
  }, []);

  const reloadCatalog = useCallback(async () => {
    discardResult();
    setCatalog((prev) => ({ ...prev, loading: true, error: null }));
    try {
      const [enums, functions, methods, engines, conflicts] = await Promise.all([
        api.enums(),
        api.functions(),
        api.methods(),
        api.engines(),
        api.conflicts(),
      ]);
      setCatalog({ enums, functions, methods, engines, conflicts, loading: false, error: null });
    } catch (error) {
      setCatalog((prev) => ({
        ...prev,
        loading: false,
        error: errorMessage(error) || 'Не удалось загрузить каталоги',
      }));
    }
  }, [discardResult]);

  useEffect(() => {
    void reloadCatalog();
  }, [reloadCatalog]);

  useEffect(() => {
    try {
      sessionStorage.setItem(STORAGE_KEY, JSON.stringify({ profile, basket, baseline }));
      setStorageError(null);
    } catch {
      setStorageError('Автосохранение в браузере недоступно.');
    }
  }, [profile, basket, baseline]);

  // Снятие результата при размонтировании: запрос не должен доживать до
  // обновления состояния уже отсутствующего компонента.
  useEffect(() => () => inFlight.current?.abort(), []);

  const updateProfile = useCallback(
    (patch: Partial<ProjectProfile>) => {
      discardResult();
      setProfile((prev) => reconcileProfile(prev, patch));
    },
    [discardResult],
  );

  const resetProfile = useCallback(() => {
    discardResult();
    setProfile(DEFAULT_PROFILE);
    setBasketState([]);
    setBaseline(null);
  }, [discardResult]);

  const setBasket = useCallback(
    (codes: string[]) => {
      discardResult();
      setBasketState(codes);
    },
    [discardResult],
  );

  const toggleBasket = useCallback(
    (code: string) => {
      discardResult();
      setBasketState((prev) => (prev.includes(code) ? prev.filter((c) => c !== code) : [...prev, code]));
    },
    [discardResult],
  );

  const clearBasket = useCallback(() => {
    discardResult();
    setBasketState([]);
  }, [discardResult]);

  const calculate = useCallback(async () => {
    // Прежний запрос отменяется: его результат уже никому не нужен.
    inFlight.current?.abort();
    const controller = new AbortController();
    inFlight.current = controller;

    // Ключ берётся из этой же области видимости: он заведомо соответствует
    // данным, которые уходят в запросе. Хранить текущий ключ в ref и обновлять
    // его в эффекте нельзя — эффекты вложенных экранов выполняются раньше
    // эффектов провайдера и получили бы ещё не обновлённое значение, из-за чего
    // автоматический пересчёт после правки анкеты отбрасывался бы как устаревший.
    const requestedKey = inputKeyOf(profile, basket, baseline);
    setCalculating(true);
    setCalculateError(null);
    try {
      const next = await api.recommend(profile, basket, controller.signal, baseline);
      // Гонка: пока выполнялся запрос, входные данные могли измениться, и тогда
      // `discardResult` обнулил `inFlight`. Медленный ответ на прежние данные
      // не должен перезаписывать актуальный результат.
      if (inFlight.current !== controller) return;
      setResult(next);
      setResultKey(requestedKey);
      setCalculating(false);
    } catch (error) {
      if (inFlight.current !== controller) return;
      if (isAbortError(error)) return;
      setCalculateError(errorMessage(error));
      setCalculating(false);
    }
  }, [profile, basket, baseline]);

  const saveBaseline = useCallback(() => {
    discardResult();
    setBaseline({ profile: structuredClone(profile), basket: [...new Set(basket)] });
  }, [profile, basket, discardResult]);

  const value: ProjectStore = useMemo(
    () => ({
      baseline,
      saveBaseline,
      profile,
      basket,
      result,
      resultKey,
      inputKey,
      catalog,
      calculating,
      calculateError,
      storageError,
      updateProfile,
      resetProfile,
      toggleBasket,
      setBasket,
      clearBasket,
      calculate,
      reloadCatalog,
    }),
    [
      baseline,
      saveBaseline,
      profile,
      basket,
      result,
      resultKey,
      inputKey,
      catalog,
      calculating,
      calculateError,
      storageError,
      updateProfile,
      resetProfile,
      toggleBasket,
      setBasket,
      clearBasket,
      calculate,
      reloadCatalog,
    ],
  );

  return <StoreContext.Provider value={value}>{children}</StoreContext.Provider>;
}

export function useStore(): ProjectStore {
  const context = useContext(StoreContext);
  if (!context) throw new Error('useStore должен использоваться внутри StoreProvider');
  return context;
}

/**
 * Автоматически выполняет расчёт, когда результата нет.
 *
 * Экран получает данные, относящиеся к текущему профилю и корзине: после правки
 * результат сбрасывается, и этот вызов запускает пересчёт без нажатия кнопки.
 * Повторного запуска после ошибки нет — иначе неудачный запрос повторялся бы
 * на каждом рендере.
 */
export function useEnsureResult(enabled = true): void {
  const { result, calculating, calculateError, calculate, catalog } = useStore();
  useEffect(() => {
    if (!enabled || catalog.loading) return;
    if (result || calculating || calculateError) return;
    void calculate();
  }, [enabled, result, calculating, calculateError, calculate, catalog.loading]);
}
