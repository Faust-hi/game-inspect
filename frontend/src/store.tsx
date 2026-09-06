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
  Conflict,
  Engine,
  Enums,
  GameExample,
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
  stage: 'prototype',
  engine: 'unreal',
  engine_version: null,
  platforms: ['pc_windows'],
  object_count_level: 'medium',
  object_count: null,
  npc_count_level: 'medium',
  npc_count: null,
  player_count: 1,
  multiplayer: false,
  functions: [],
  target_resolution: '1080p',
  target_quality: 'high',
  target_fps: 60,
  ram_limit_gb: null,
  vram_limit_gb: null,
  size_limit_gb: null,
  deadline_weeks: null,
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
export function inputKeyOf(profile: ProjectProfile, basket: string[]): string {
  return stableStringify({ profile, basket: [...basket].sort() });
}

function isAbortError(error: unknown): boolean {
  return error instanceof Error && error.name === 'AbortError';
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
  examples: GameExample[];
  loading: boolean;
  error: string | null;
}

interface ProjectStore {
  profile: ProjectProfile;
  basket: string[];
  result: RecommendationResult | null;
  /** Отпечаток входа, для которого получен `result`. */
  resultKey: string | null;
  /** Отпечаток текущего входа: расходится с `resultKey` после правки анкеты. */
  inputKey: string;
  /** Результат есть, но относится к уже изменённым данным. */
  resultStale: boolean;
  catalog: CatalogState;
  calculating: boolean;
  calculateError: string | null;
  updateProfile: (patch: Partial<ProjectProfile>) => void;
  resetProfile: () => void;
  toggleBasket: (code: string) => void;
  setBasket: (codes: string[]) => void;
  clearBasket: () => void;
  calculate: () => Promise<void>;
  reloadCatalog: () => Promise<void>;
  loadProject: (profile: ProjectProfile, basket: string[]) => void;
}

const StoreContext = createContext<ProjectStore | null>(null);

function loadPersisted(): { profile: ProjectProfile; basket: string[] } | null {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return null;
    const parsed = JSON.parse(raw);
    return {
      profile: { ...DEFAULT_PROFILE, ...parsed.profile },
      basket: Array.isArray(parsed.basket) ? parsed.basket : [],
    };
  } catch {
    return null;
  }
}

export function StoreProvider({ children }: { children: ReactNode }) {
  const persisted = useMemo(loadPersisted, []);
  const [profile, setProfile] = useState<ProjectProfile>(persisted?.profile ?? DEFAULT_PROFILE);
  const [basket, setBasketState] = useState<string[]>(persisted?.basket ?? []);
  const [result, setResult] = useState<RecommendationResult | null>(null);
  const [resultKey, setResultKey] = useState<string | null>(null);
  const [calculating, setCalculating] = useState(false);
  const [calculateError, setCalculateError] = useState<string | null>(null);
  const [catalog, setCatalog] = useState<CatalogState>({
    enums: null,
    functions: [],
    methods: [],
    engines: [],
    conflicts: [],
    examples: [],
    loading: true,
    error: null,
  });

  /** Выполняющийся запрос расчёта. Предыдущий отменяется при новом запуске. */
  const inFlight = useRef<AbortController | null>(null);

  const inputKey = useMemo(() => inputKeyOf(profile, basket), [profile, basket]);

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
    setCatalog((prev) => ({ ...prev, loading: true, error: null }));
    try {
      const [enums, functions, methods, engines, conflicts, examples] = await Promise.all([
        api.enums(),
        api.functions(),
        api.methods(),
        api.engines(),
        api.conflicts(),
        api.examples(),
      ]);
      setCatalog({ enums, functions, methods, engines, conflicts, examples, loading: false, error: null });
    } catch (error) {
      setCatalog((prev) => ({
        ...prev,
        loading: false,
        error: errorMessage(error) || 'Не удалось загрузить каталоги',
      }));
    }
  }, []);

  useEffect(() => {
    void reloadCatalog();
  }, [reloadCatalog]);

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify({ profile, basket }));
  }, [profile, basket]);

  // Снятие результата при размонтировании: запрос не должен доживать до
  // обновления состояния уже отсутствующего компонента.
  useEffect(() => () => inFlight.current?.abort(), []);

  const updateProfile = useCallback(
    (patch: Partial<ProjectProfile>) => {
      discardResult();
      setProfile((prev) => ({ ...prev, ...patch }));
    },
    [discardResult],
  );

  const resetProfile = useCallback(() => {
    discardResult();
    setProfile(DEFAULT_PROFILE);
    setBasketState([]);
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

  const loadProject = useCallback(
    (nextProfile: ProjectProfile, nextBasket: string[]) => {
      discardResult();
      setProfile({ ...DEFAULT_PROFILE, ...nextProfile });
      setBasketState(nextBasket);
    },
    [discardResult],
  );

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
    const requestedKey = inputKeyOf(profile, basket);
    setCalculating(true);
    setCalculateError(null);
    try {
      const next = await api.recommend(profile, basket, controller.signal);
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
  }, [profile, basket]);

  const resultStale = result !== null && resultKey !== null && resultKey !== inputKey;

  const value: ProjectStore = useMemo(
    () => ({
      profile,
      basket,
      result,
      resultKey,
      inputKey,
      resultStale,
      catalog,
      calculating,
      calculateError,
      updateProfile,
      resetProfile,
      toggleBasket,
      setBasket,
      clearBasket,
      calculate,
      reloadCatalog,
      loadProject,
    }),
    [
      profile,
      basket,
      result,
      resultKey,
      inputKey,
      resultStale,
      catalog,
      calculating,
      calculateError,
      updateProfile,
      resetProfile,
      toggleBasket,
      setBasket,
      clearBasket,
      calculate,
      reloadCatalog,
      loadProject,
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
  const { result, calculating, calculateError, calculate } = useStore();
  useEffect(() => {
    if (!enabled) return;
    if (result || calculating || calculateError) return;
    void calculate();
  }, [enabled, result, calculating, calculateError, calculate]);
}
