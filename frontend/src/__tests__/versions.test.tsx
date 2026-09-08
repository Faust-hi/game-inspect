/**
 * Проверки версий набора решений.
 *
 * Требование: патч или обновление игры не затирает прежний набор. Подтверждённая
 * версия остаётся в истории, и её можно сравнить с текущей — иначе непонятно,
 * что именно изменил патч и как изменилась аппаратная оценка.
 */
import { act, cleanup, fireEvent, render, renderHook, waitFor } from '@testing-library/react';
import type { ReactNode } from 'react';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { VersionHistory } from '../components/VersionHistory';
import { DEFAULT_PROFILE, StoreProvider, useStore } from '../store';
import { diffVersion, loadVersions, summaryOf } from '../versions';
import type { HardwareEstimate, ProjectProfile, ProjectVersion, RecommendationResult } from '../types';

const mocks = vi.hoisted(() => ({
  recommend: vi.fn(),
  enums: vi.fn(),
  functions: vi.fn(),
  methods: vi.fn(),
  engines: vi.fn(),
  conflicts: vi.fn(),
}));

vi.mock('../api', () => ({
  api: {
    recommend: mocks.recommend,
    enums: mocks.enums,
    functions: mocks.functions,
    methods: mocks.methods,
    engines: mocks.engines,
    conflicts: mocks.conflicts,
    stageGuidance: vi.fn().mockResolvedValue(null),
  },
}));

function wrapper({ children }: { children: ReactNode }) {
  return <StoreProvider>{children}</StoreProvider>;
}

function makeHardware(overrides: Partial<HardwareEstimate> = {}): HardwareEstimate {
  return {
    required_gpu_index: 50,
    required_cpu_index: 50,
    estimated_vram_gb: 8,
    estimated_ram_gb: 16,
    gpu_class: 3,
    cpu_class: 3,
    reference_gpu: null,
    reference_cpu: null,
    alternative_gpus: [],
    alternative_cpus: [],
    confidence: 0.6,
    confidence_label: 'ориентировочно',
    caveats: [],
    required_hw_features: [],
    exceeds_catalog: false,
    unmet_limits: [],
    recommended_storage: 'SSD',
    estimated_draw_calls: 1000,
    modeling_gaps: [],
    non_client_methods: [],
    cpu_main_thread_cost: 1,
    cpu_parallel_cost: 1,
    cpu_subsystems: [],
    gpu_raster_cost: 1,
    gpu_rt_cost: 0,
    gpu_subsystems: [],
    bottleneck: 'gpu',
    bottleneck_label: 'GPU',
    memory_composition: [],
    consequences: [],
    storage_requirement: 'SSD',
    ...overrides,
  } as HardwareEstimate;
}

function makeResult(overrides: Partial<RecommendationResult> = {}): RecommendationResult {
  return {
    profile: DEFAULT_PROFILE,
    risks: [],
    recommendations: [],
    excluded: [],
    load_profile: { cpu: 0, gpu: 0, ram: 0, vram: 0, disk: 0, network: 0, per_resource: {} },
    basket_conflicts: [],
    basket_dependencies: [],
    basket_synergies: [],
    hardware: null,
    practice_check: { status: 'in_development', title: '', message: '', details: [] },
    contributions: { parameters: [], methods: [], assumptions: [], exclusions: [] },
    meta: {},
    input_key: 'key',
    ...overrides,
  };
}

function makeVersion(overrides: Partial<ProjectVersion> = {}): ProjectVersion {
  return {
    id: 'v1',
    number: 1,
    label: 'База',
    note: '',
    created_at: '2026-09-08T10:00:00.000Z',
    profile: DEFAULT_PROFILE,
    basket: [],
    input_key: 'saved',
    summary: null,
    ...overrides,
  };
}

beforeEach(() => {
  localStorage.clear();
  sessionStorage.clear();
  mocks.enums.mockResolvedValue({});
  mocks.functions.mockResolvedValue([]);
  mocks.methods.mockResolvedValue([]);
  mocks.engines.mockResolvedValue([]);
  mocks.conflicts.mockResolvedValue([]);
  mocks.recommend.mockResolvedValue(makeResult());
});

afterEach(() => {
  cleanup();
});

describe('сводка версии', () => {
  it('без расчёта сводки нет', () => {
    expect(summaryOf(null, ['a'])).toBeNull();
  });

  it('сохраняет ориентир оборудования и объём памяти', () => {
    const result = makeResult({
      hardware: makeHardware({
        estimated_ram_gb: 16,
        estimated_vram_gb: 8,
        reference_gpu: { model: 'GeForce RTX 3060' } as never,
      }),
    });

    const summary = summaryOf(result, ['a', 'b']);

    expect(summary?.basket_size).toBe(2);
    expect(summary?.hardware?.estimated_ram_gb).toBe(16);
    expect(summary?.hardware?.reference_gpu).toBe('GeForce RTX 3060');
  });

  it('сохраняет ограниченный список рекомендаций', () => {
    const recommendations = Array.from({ length: 12 }, (_item, index) => ({
      method_code: `m${index}`,
      method_name: `Метод ${index}`,
      score: 0.5,
    })) as RecommendationResult['recommendations'];

    const summary = summaryOf(makeResult({ recommendations }), []);

    expect(summary?.recommendations).toHaveLength(8);
  });
});

describe('сравнение версий', () => {
  it('находит добавленные и убранные решения', () => {
    const version = makeVersion({ basket: ['lod_system', 'occlusion_culling'] });

    const diff = diffVersion(version, DEFAULT_PROFILE, ['lod_system', 'texture_streaming'], null);

    expect(diff.added).toEqual(['texture_streaming']);
    expect(diff.removed).toEqual(['occlusion_culling']);
    expect(diff.kept).toEqual(['lod_system']);
  });

  it('перестановка решений не считается изменением', () => {
    const version = makeVersion({ basket: ['lod_system', 'occlusion_culling'] });

    const diff = diffVersion(version, DEFAULT_PROFILE, ['occlusion_culling', 'lod_system'], null);

    expect(diff.added).toEqual([]);
    expect(diff.removed).toEqual([]);
    expect(diff.kept).toHaveLength(2);
  });

  it('показывает изменение анкеты с понятной подписью', () => {
    const version = makeVersion({ profile: { ...DEFAULT_PROFILE, target_fps: 60 } });
    const current: ProjectProfile = { ...DEFAULT_PROFILE, target_fps: 120 };

    const diff = diffVersion(version, current, [], null);

    expect(diff.profile_changes).toEqual([
      { field: 'target_fps', label: 'Частота кадров', from: '60', to: '120' },
    ]);
  });

  it('перестановка функций в анкете не считается изменением', () => {
    const version = makeVersion({ profile: { ...DEFAULT_PROFILE, functions: ['a', 'b'] } });
    const current = { ...DEFAULT_PROFILE, functions: ['b', 'a'] };

    expect(diffVersion(version, current, [], null).profile_changes).toEqual([]);
  });

  it('показывает изменение аппаратной оценки', () => {
    const version = makeVersion({
      summary: summaryOf(
        makeResult({ hardware: makeHardware({ estimated_ram_gb: 16, estimated_vram_gb: 8 }) }),
        [],
      ),
    });
    const current = makeResult({
      hardware: makeHardware({ estimated_ram_gb: 12, estimated_vram_gb: 8 }),
    });

    const diff = diffVersion(version, DEFAULT_PROFILE, [], current);

    expect(diff.hardware?.ram_delta_gb).toBe(-4);
    expect(diff.hardware?.vram_delta_gb).toBe(0);
  });

  it('без сводки в версии сравнение оборудования недоступно', () => {
    const version = makeVersion({ summary: null });

    const diff = diffVersion(version, DEFAULT_PROFILE, [], makeResult({ hardware: makeHardware() }));

    expect(diff.hardware).toBeNull();
  });
});

describe('интерфейс истории версий', () => {
  it('показывает сохранённую версию и её сравнение с текущей', () => {
    const saved = renderWithHistory();

    fireEvent.click(saved.getByRole('button', { name: 'Подтвердить изменения' }));

    expect(saved.getByText(/Версия 1/)).toBeTruthy();
    expect(saved.getByText(/решений: 0/)).toBeTruthy();

    fireEvent.click(saved.getByRole('button', { name: 'Сравнить с текущей' }));
    expect(saved.getByText(/Изменений нет/)).toBeTruthy();

    fireEvent.click(saved.getByRole('button', { name: 'Скрыть сравнение' }));
    expect(saved.queryByText(/Изменений нет/)).toBeNull();
  });

  it('в сравнении показывает добавленные и убранные решения', () => {
    const saved = renderWithHistory();

    fireEvent.click(saved.getByRole('button', { name: 'Подтвердить изменения' }));
    fireEvent.click(saved.getByRole('button', { name: 'Добавить решение' }));
    fireEvent.click(saved.getByRole('button', { name: 'Сравнить с текущей' }));

    expect(saved.getByText('добавлено: 1')).toBeTruthy();
    expect(saved.getByText('lod_system')).toBeTruthy();
  });

  it('показывает предупреждение о несохранённых изменениях', () => {
    const saved = renderWithHistory();

    fireEvent.click(saved.getByRole('button', { name: 'Подтвердить изменения' }));
    expect(saved.queryByText(/Есть несохранённые изменения/)).toBeNull();

    fireEvent.click(saved.getByRole('button', { name: 'Добавить решение' }));
    expect(saved.getByText(/Есть несохранённые изменения/)).toBeTruthy();
  });
});

/** Стенд: действия состояния и история версий в одном провайдере. */
function renderWithHistory() {
  function Harness() {
    const store = useStore();
    return (
      <>
        <button onClick={() => store.toggleBasket('lod_system')}>Добавить решение</button>
        <VersionHistory />
      </>
    );
  }
  const view = render(
    <StoreProvider>
      <Harness />
    </StoreProvider>,
  );
  return view;
}

describe('чтение истории', () => {
  it('отбрасывает повреждённые записи', () => {
    sessionStorage.setItem(
      'gamedev_dss_versions_v1',
      JSON.stringify([{ id: 'ok', number: 1, basket: [], profile: {} }, { id: 'broken' }]),
    );

    expect(loadVersions()).toHaveLength(1);
  });

  it('переживает некорректный JSON', () => {
    sessionStorage.setItem('gamedev_dss_versions_v1', '{не json');

    expect(loadVersions()).toEqual([]);
  });
});

describe('история версий в состоянии', () => {
  it('подтверждение изменений сохраняет версию и оставляет прежнюю', async () => {
    const view = renderHook(() => useStore(), { wrapper });
    await waitFor(() => expect(view.result.current.catalog.loading).toBe(false));

    await act(async () => {
      view.result.current.toggleBasket('lod_system');
    });
    await act(async () => {
      view.result.current.saveVersion('База');
    });
    await act(async () => {
      view.result.current.toggleBasket('occlusion_culling');
    });
    await act(async () => {
      view.result.current.saveVersion('Патч 1');
    });

    expect(view.result.current.versions.map((item) => item.number)).toEqual([1, 2]);
    expect(view.result.current.versions[0].basket).toEqual(['lod_system']);
    expect(view.result.current.versions[1].basket).toEqual(['lod_system', 'occlusion_culling']);
  });

  it('сохранение не сбрасывает результат расчёта', async () => {
    const view = renderHook(() => useStore(), { wrapper });
    await act(async () => {
      await view.result.current.calculate();
    });
    expect(view.result.current.result).not.toBeNull();

    await act(async () => {
      view.result.current.saveVersion('База');
    });

    expect(view.result.current.result).not.toBeNull();
  });

  it('отмечает несохранённые изменения и снимает отметку после подтверждения', async () => {
    const view = renderHook(() => useStore(), { wrapper });
    await waitFor(() => expect(view.result.current.catalog.loading).toBe(false));

    await act(async () => {
      view.result.current.saveVersion('База');
    });
    expect(view.result.current.hasUnsavedChanges).toBe(false);

    await act(async () => {
      view.result.current.toggleBasket('lod_system');
    });
    expect(view.result.current.hasUnsavedChanges).toBe(true);
  });

  it('восстановление возвращает набор и анкету версии', async () => {
    const view = renderHook(() => useStore(), { wrapper });
    await waitFor(() => expect(view.result.current.catalog.loading).toBe(false));

    await act(async () => {
      view.result.current.setBasket(['lod_system', 'occlusion_culling']);
    });
    await act(async () => {
      view.result.current.updateProfile({ target_fps: 120 });
    });
    await act(async () => {
      view.result.current.saveVersion('База');
    });
    await act(async () => {
      view.result.current.setBasket([]);
    });
    await act(async () => {
      view.result.current.updateProfile({ target_fps: 30 });
    });

    await act(async () => {
      view.result.current.restoreVersion(view.result.current.versions[0].id);
    });

    expect(view.result.current.basket).toEqual(['lod_system', 'occlusion_culling']);
    expect(view.result.current.profile.target_fps).toBe(120);
  });

  it('номер версии не повторяется после удаления', async () => {
    const view = renderHook(() => useStore(), { wrapper });
    await waitFor(() => expect(view.result.current.catalog.loading).toBe(false));

    await act(async () => {
      view.result.current.saveVersion('Первая');
    });
    await act(async () => {
      view.result.current.toggleBasket('lod_system');
    });
    await act(async () => {
      view.result.current.saveVersion('Вторая');
    });
    // Удаляется первая версия: номер второй должен остаться, а следующая
    // версия не вправе получить освободившийся номер — иначе «версия 2»
    // появится в истории дважды и сравнение станет неоднозначным.
    await act(async () => {
      view.result.current.deleteVersion(view.result.current.versions[0].id);
    });
    await act(async () => {
      view.result.current.saveVersion('Третья');
    });

    const numbers = view.result.current.versions.map((item) => item.number);
    expect(numbers).toEqual([2, 3]);
    expect(new Set(numbers).size).toBe(numbers.length);
  });

  it('сброс проекта очищает историю версий', async () => {
    const view = renderHook(() => useStore(), { wrapper });
    await waitFor(() => expect(view.result.current.catalog.loading).toBe(false));

    await act(async () => {
      view.result.current.saveVersion('База');
    });
    expect(view.result.current.versions).toHaveLength(1);

    await act(async () => {
      view.result.current.resetProfile();
    });

    expect(view.result.current.versions).toEqual([]);
  });

  it('история версий сохраняется в браузере', async () => {
    const view = renderHook(() => useStore(), { wrapper });
    await waitFor(() => expect(view.result.current.catalog.loading).toBe(false));

    await act(async () => {
      view.result.current.saveVersion('База');
    });

    expect(loadVersions()).toHaveLength(1);
    expect(loadVersions()[0].label).toBe('База');
  });
});
