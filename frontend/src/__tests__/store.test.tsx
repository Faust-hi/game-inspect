/**
 * Проверки состояния проекта.
 *
 * Основное требование: результат расчёта всегда относится к данным на экране.
 * Раньше после правки анкеты или корзины на экране оставался прежний расчёт,
 * и разделы рисков, нагрузки и оборудования показывали устаревшие значения.
 */
import { act, cleanup, renderHook, waitFor } from '@testing-library/react';
import type { ReactNode } from 'react';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { DEFAULT_PROFILE, inputKeyOf, StoreProvider, useEnsureResult, useStore } from '../store';
import type { ProjectProfile, RecommendationResult } from '../types';

/** Заглушки запросов: сеть в тестах не используется. */
const mocks = vi.hoisted(() => ({
  recommend: vi.fn(),
  enums: vi.fn(),
  functions: vi.fn(),
  methods: vi.fn(),
  engines: vi.fn(),
  conflicts: vi.fn(),
  examples: vi.fn(),
}));

vi.mock('../api', () => ({
  api: {
    recommend: mocks.recommend,
    enums: mocks.enums,
    functions: mocks.functions,
    methods: mocks.methods,
    engines: mocks.engines,
    conflicts: mocks.conflicts,
    examples: mocks.examples,
  },
}));

function makeResult(inputKey: string): RecommendationResult {
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
    similar_games: [],
    meta: {},
    input_key: inputKey,
  };
}

/** Отложенный ответ: позволяет управлять моментом завершения запроса. */
function deferred<T>() {
  let resolve!: (value: T) => void;
  const promise = new Promise<T>((done) => {
    resolve = done;
  });
  return { promise, resolve };
}

function wrapper({ children }: { children: ReactNode }) {
  return <StoreProvider>{children}</StoreProvider>;
}

/** Обёртка с экраном-заглушкой, который требует результат через `useEnsureResult`. */
function wrapperWithAutoCalculate(enabled = true) {
  return function Wrapper({ children }: { children: ReactNode }) {
    return (
      <StoreProvider>
        {children}
        <AutoCalculateProbe enabled={enabled} />
      </StoreProvider>
    );
  };
}

function AutoCalculateProbe({ enabled }: { enabled: boolean }) {
  useEnsureResult(enabled);
  return null;
}

beforeEach(() => {
  localStorage.clear();
  mocks.enums.mockResolvedValue({});
  mocks.functions.mockResolvedValue([]);
  mocks.methods.mockResolvedValue([]);
  mocks.engines.mockResolvedValue([]);
  mocks.conflicts.mockResolvedValue([]);
  mocks.examples.mockResolvedValue([]);
  mocks.recommend.mockResolvedValue(makeResult('по умолчанию'));
});

afterEach(() => {
  cleanup();
});

describe('inputKeyOf', () => {
  it('не зависит от порядка решений в корзине', () => {
    const direct = inputKeyOf(DEFAULT_PROFILE, ['lod_system', 'occlusion_culling']);
    const reversed = inputKeyOf(DEFAULT_PROFILE, ['occlusion_culling', 'lod_system']);

    expect(direct).toBe(reversed);
  });

  it('различает профиль и корзину', () => {
    const base = inputKeyOf(DEFAULT_PROFILE, ['lod_system']);

    expect(inputKeyOf({ ...DEFAULT_PROFILE, target_fps: 120 }, ['lod_system'])).not.toBe(base);
    expect(inputKeyOf(DEFAULT_PROFILE, ['occlusion_culling'])).not.toBe(base);
    expect(inputKeyOf(DEFAULT_PROFILE, [])).not.toBe(base);
  });

  it('устойчив к перестановке ключей объекта', () => {
    const direct = { name: 'Проект', target_fps: 60 } as unknown as ProjectProfile;
    const flipped = { target_fps: 60, name: 'Проект' } as unknown as ProjectProfile;

    expect(inputKeyOf(direct, [])).toBe(inputKeyOf(flipped, []));
  });
});

describe('состояние проекта', () => {
  it('после расчёта отпечаток результата совпадает с текущим входом', async () => {
    const view = renderHook(() => useStore(), { wrapper });

    await act(async () => {
      await view.result.current.calculate();
    });

    expect(view.result.current.result).not.toBeNull();
    expect(view.result.current.resultKey).toBe(view.result.current.inputKey);
    expect(view.result.current.resultStale).toBe(false);
    expect(view.result.current.calculating).toBe(false);
    expect(view.result.current.calculateError).toBeNull();
  });

  it('после правки анкеты и пересчёта отпечаток снова совпадает', async () => {
    const view = renderHook(() => useStore(), { wrapper });

    await act(async () => {
      await view.result.current.calculate();
    });
    const firstKey = view.result.current.inputKey;

    await act(async () => {
      view.result.current.updateProfile({ target_fps: 144 });
    });
    expect(view.result.current.inputKey).not.toBe(firstKey);

    mocks.recommend.mockResolvedValue(makeResult('второй'));
    await act(async () => {
      await view.result.current.calculate();
    });

    expect(view.result.current.resultKey).toBe(view.result.current.inputKey);
    expect(view.result.current.resultStale).toBe(false);
  });

  const resets: { name: string; run: (store: ReturnType<typeof useStore>) => void }[] = [
    { name: 'updateProfile', run: (store) => store.updateProfile({ target_fps: 120 }) },
    { name: 'toggleBasket', run: (store) => store.toggleBasket('lod_system') },
    { name: 'setBasket', run: (store) => store.setBasket(['lod_system', 'occlusion_culling']) },
    { name: 'clearBasket', run: (store) => store.clearBasket() },
    { name: 'resetProfile', run: (store) => store.resetProfile() },
    {
      name: 'loadProject',
      run: (store) => store.loadProject({ ...DEFAULT_PROFILE, name: 'Загруженный' }, ['lod_system']),
    },
  ];

  for (const item of resets) {
    it(`сбрасывает прежний результат при изменении входа: ${item.name}`, async () => {
      const view = renderHook(() => useStore(), { wrapper });

      await act(async () => {
        await view.result.current.calculate();
      });
      expect(view.result.current.result).not.toBeNull();

      await act(async () => {
        item.run(view.result.current);
      });

      expect(view.result.current.result).toBeNull();
      expect(view.result.current.resultKey).toBeNull();
      expect(view.result.current.calculating).toBe(false);
      expect(view.result.current.calculateError).toBeNull();
    });
  }

  it('поздний ответ на устаревшие данные не перезаписывает актуальный результат', async () => {
    const slow = deferred<RecommendationResult>();
    mocks.recommend.mockImplementationOnce(() => slow.promise);

    const view = renderHook(() => useStore(), { wrapper });

    let pending: Promise<void> = Promise.resolve();
    act(() => {
      pending = view.result.current.calculate();
    });
    expect(view.result.current.calculating).toBe(true);

    // Пользователь меняет анкету, пока первый запрос ещё выполняется.
    await act(async () => {
      view.result.current.updateProfile({ target_fps: 120 });
    });
    expect(view.result.current.result).toBeNull();

    mocks.recommend.mockResolvedValue(makeResult('актуальный'));
    await act(async () => {
      await view.result.current.calculate();
    });
    expect(view.result.current.result?.input_key).toBe('актуальный');

    // Первый запрос завершается уже после второго — его данные никому не нужны.
    await act(async () => {
      slow.resolve(makeResult('устаревший'));
      await pending;
    });

    expect(mocks.recommend).toHaveBeenCalledTimes(2);
    expect(view.result.current.result?.input_key).toBe('актуальный');
    expect(view.result.current.resultKey).toBe(view.result.current.inputKey);
    expect(view.result.current.resultStale).toBe(false);
  });

  it('отменяет выполняющийся запрос при изменении входа', async () => {
    const signals: AbortSignal[] = [];
    const gate = deferred<RecommendationResult>();
    mocks.recommend.mockImplementation(
      (_profile: ProjectProfile, _basket: string[], signal?: AbortSignal) => {
        if (signal) signals.push(signal);
        return gate.promise;
      },
    );

    const view = renderHook(() => useStore(), { wrapper });
    act(() => {
      void view.result.current.calculate();
    });
    expect(signals).toHaveLength(1);

    await act(async () => {
      view.result.current.updateProfile({ target_fps: 120 });
    });

    expect(signals[0]?.aborted).toBe(true);
  });

  it('сохраняет текст ошибки и снимает признак расчёта', async () => {
    mocks.recommend.mockRejectedValue(new Error('сервис недоступен'));

    const view = renderHook(() => useStore(), { wrapper });
    await act(async () => {
      await view.result.current.calculate();
    });

    expect(view.result.current.result).toBeNull();
    expect(view.result.current.calculateError).toBe('сервис недоступен');
    expect(view.result.current.calculating).toBe(false);
  });
});

describe('useEnsureResult', () => {
  it('выполняет расчёт автоматически, когда результата нет', async () => {
    mocks.recommend.mockResolvedValue(makeResult('авто'));

    const view = renderHook(() => useStore(), { wrapper: wrapperWithAutoCalculate() });

    await waitFor(() => {
      expect(view.result.current.result?.input_key).toBe('авто');
    });
    expect(mocks.recommend).toHaveBeenCalledTimes(1);
  });

  it('не повторяет запрос после ошибки', async () => {
    mocks.recommend.mockRejectedValue(new Error('сбой расчёта'));

    const view = renderHook(() => useStore(), { wrapper: wrapperWithAutoCalculate() });

    await waitFor(() => {
      expect(view.result.current.calculateError).toBe('сбой расчёта');
    });
    const callsAfterFailure = mocks.recommend.mock.calls.length;

    // Повторение на каждом рендере превратило бы одну ошибку в бесконечный цикл.
    await new Promise((done) => setTimeout(done, 30));

    expect(mocks.recommend.mock.calls.length).toBe(callsAfterFailure);
  });

  it('бездействует, когда расчёт не нужен', async () => {
    const view = renderHook(() => useStore(), { wrapper: wrapperWithAutoCalculate(false) });

    await act(async () => {
      await new Promise((done) => setTimeout(done, 20));
    });

    expect(mocks.recommend).not.toHaveBeenCalled();
    expect(view.result.current.result).toBeNull();
  });

  it('пересчитывает результат после изменения входа', async () => {
    mocks.recommend.mockResolvedValue(makeResult('первый'));

    const view = renderHook(() => useStore(), { wrapper: wrapperWithAutoCalculate() });
    await waitFor(() => {
      expect(view.result.current.result?.input_key).toBe('первый');
    });

    mocks.recommend.mockResolvedValue(makeResult('второй'));
    await act(async () => {
      view.result.current.updateProfile({ target_fps: 120 });
    });

    await waitFor(() => {
      expect(view.result.current.result?.input_key).toBe('второй');
    });
    expect(view.result.current.resultStale).toBe(false);
  });
});
