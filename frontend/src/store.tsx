/** Состояние проекта: анкета, корзина решений и результат расчёта. */
import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
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
  geometry_detail: null,
  texture_quality: null,
  view_distance: null,
  lighting_complexity: null,
  physics_complexity: null,
  simulation_complexity: null,
  npc_update_rate: null,
  network_update_rate: null,
};

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
        error: error instanceof Error ? error.message : 'Не удалось загрузить каталоги',
      }));
    }
  }, []);

  useEffect(() => {
    void reloadCatalog();
  }, [reloadCatalog]);

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify({ profile, basket }));
  }, [profile, basket]);

  const updateProfile = useCallback((patch: Partial<ProjectProfile>) => {
    setProfile((prev) => ({ ...prev, ...patch }));
  }, []);

  const resetProfile = useCallback(() => {
    setProfile(DEFAULT_PROFILE);
    setBasketState([]);
    setResult(null);
  }, []);

  const setBasket = useCallback((codes: string[]) => setBasketState(codes), []);

  const toggleBasket = useCallback((code: string) => {
    setBasketState((prev) => (prev.includes(code) ? prev.filter((c) => c !== code) : [...prev, code]));
  }, []);

  const clearBasket = useCallback(() => setBasketState([]), []);

  const loadProject = useCallback((nextProfile: ProjectProfile, nextBasket: string[]) => {
    setProfile({ ...DEFAULT_PROFILE, ...nextProfile });
    setBasketState(nextBasket);
    setResult(null);
  }, []);

  const calculate = useCallback(async () => {
    setCalculating(true);
    setCalculateError(null);
    try {
      const next = await api.recommend(profile, basket);
      setResult(next);
    } catch (error) {
      setCalculateError(error instanceof Error ? error.message : 'Расчёт не выполнен');
    } finally {
      setCalculating(false);
    }
  }, [profile, basket]);

  const value: ProjectStore = {
    profile,
    basket,
    result,
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
  };

  return <StoreContext.Provider value={value}>{children}</StoreContext.Provider>;
}

export function useStore(): ProjectStore {
  const context = useContext(StoreContext);
  if (!context) throw new Error('useStore должен использоваться внутри StoreProvider');
  return context;
}
