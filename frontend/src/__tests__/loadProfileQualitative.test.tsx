/** Накопитель и сеть в сводке нагрузки: качественная оценка, а не проценты. */
import { cleanup, render, screen, within } from '@testing-library/react';
import { afterEach, describe, expect, it, vi } from 'vitest';
import { LoadProfileScreen } from '../screens/LoadProfileScreen';
import type { LoadProfile } from '../types';

vi.mock('../store', () => ({
  useStore: () => ({
    result: {
      load_profile: load(),
      selected_methods: [],
      accounted_method_codes: [],
    },
    basket: [],
    catalog: { methods: [] },
    calculating: false,
  }),
  useEnsureResult: () => {},
}));

function load(): LoadProfile {
  const quantitative = (raw: number) => ({
    raw,
    normalized: 50,
    label: 'CPU',
    direction: 'не влияет',
    quantitative: true,
  });
  return {
    notes: ['Накопитель и сеть оценены качественно.'],
    cpu: 50,
    gpu: 50,
    ram: 50,
    vram: 50,
    disk: 50,
    network: 50,
    per_resource: {
      cpu: quantitative(0),
      gpu: quantitative(0),
      ram: quantitative(0),
      vram: quantitative(0),
      disk: {
        raw: 4,
        normalized: 50,
        label: 'накопитель',
        direction: 'повышает',
        quantitative: false,
        level: 'умеренное',
        explanation:
          'Набор повышает требования к накопителю. Это качественная оценка: модель не оценивает объём данных.',
      },
      network: {
        raw: -2,
        normalized: 50,
        label: 'сеть',
        direction: 'снижает',
        quantitative: false,
        level: 'небольшое',
        explanation: 'Набор снижает требования к сети: модель не оценивает трафик.',
      },
    },
  };
}

describe('качественные ресурсы сводки нагрузки', () => {
  afterEach(cleanup);

  it('показывает уровень и пояснение вместо числа на шкале', () => {
    render(<LoadProfileScreen />);

    expect(screen.getByText('умеренное')).toBeTruthy();
    expect(screen.getByText('небольшое')).toBeTruthy();
    expect(screen.getByText(/качественная оценка: модель не оценивает объём/)).toBeTruthy();
    expect(screen.getByText(/оценены качественно/)).toBeTruthy();
  });

  it('числовая шкала и экспертный балл не меняются местами', () => {
    // Свойство вместо точного подсчёта: если ресурс сменят тип измерения,
    // подпись обязана переехать вместе с ним, а не остаться числом.
    render(<LoadProfileScreen />);

    for (const label of ['CPU', 'GPU', 'RAM', 'VRAM']) {
      const row = screen.getByText(label, { selector: 'strong' }).closest('div');
      expect(within(row as HTMLElement).queryByText(/изменение стоимости кадра/)).toBeTruthy();
      expect(within(row as HTMLElement).queryByText(/экспертный балл/)).toBeNull();
    }
    for (const label of ['Накопитель', 'Сеть']) {
      const row = screen.getByText(label, { selector: 'strong' }).closest('div');
      expect(within(row as HTMLElement).queryByText(/экспертный балл/)).toBeTruthy();
      expect(within(row as HTMLElement).queryByText(/изменение стоимости кадра/)).toBeNull();
    }
  });
});
