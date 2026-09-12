/** Область применимости и вердикт по пределам в экране оборудования (D06/D18). */
import { cleanup, render, screen } from '@testing-library/react';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { HardwareScreen } from '../screens/HardwareScreen';
import type { HardwareEstimate } from '../types';

const state = vi.hoisted(() => ({ hw: {} as unknown as HardwareEstimate }));

vi.mock('../store', () => ({
  useStore: () => ({ result: { hardware: state.hw }, calculating: false }),
  useEnsureResult: () => {},
}));

function hardware(): HardwareEstimate {
  return {
    required_gpu_index: 0.3,
    required_cpu_index: 0.4,
    estimated_vram_gb: 6,
    estimated_ram_gb: 16,
    gpu_class: 5,
    cpu_class: 5,
    reference_gpu: null,
    reference_cpu: null,
    alternative_gpus: [],
    alternative_cpus: [],
    confidence: 0.4,
    confidence_label: 'низкая',
    caveats: [],
    required_hw_features: [],
    exceeds_catalog: true,
    // Пределы профиля не заданы: выход за область применимости — не то же
    // самое, что нарушенное ограничение, и живёт в отдельном поле.
    constraints_satisfied: true,
    unmet_limits: [],
    recommended_storage: 'sata_ssd',
    estimated_draw_calls: 1000,
    modeling_gaps: [],
    applicability_limits: ['Количественный прогноз доступен только для Windows/Linux ПК.'],
    non_client_methods: [],
    cpu_main_thread_cost: 0,
    cpu_parallel_cost: 0,
    cpu_subsystems: [],
    gpu_raster_cost: 0,
    gpu_rt_cost: 0,
    gpu_subsystems: [],
    bottleneck: '',
    bottleneck_label: '',
    memory_composition: [],
    consequences: [],
    storage_requirement: '',
  };
}

describe('область применимости оборудования', () => {
  beforeEach(() => {
    Object.assign(state.hw, hardware());
  });
  afterEach(cleanup);

  it('показывает отказ прогноза вместо PC-ориентира', () => {
    render(<HardwareScreen />);
    expect(screen.getByText(/Вне области применимости модели/)).toBeTruthy();
    expect(screen.getAllByText(/только для Windows\/Linux ПК/).length).toBeGreaterThanOrEqual(1);
  });

  it('показывает вердикт по пределам, когда они нарушены', () => {
    state.hw.constraints_satisfied = false;
    state.hw.unmet_limits = ['Требуется 8.2 ГБ видеопамяти при заданном пределе 2.0 ГБ.'];
    render(<HardwareScreen />);
    expect(screen.getByText(/Заданные пределы не выполнены/)).toBeTruthy();
    expect(screen.getAllByText(/при заданном пределе 2.0 ГБ/).length).toBeGreaterThanOrEqual(1);
  });

  it('не скрывает нарушение, если вердикт разошёлся со списком', () => {
    // Вердикт — машинное поле, список — человеческая расшифровка. Если они
    // разойдутся, нарушение показывается: скрыть его за положительным
    // вердиктом значило бы выдать непригодную конфигурацию за подходящую.
    state.hw.constraints_satisfied = true;
    state.hw.unmet_limits = ['Требуется 8.2 ГБ видеопамяти при заданном пределе 2.0 ГБ.'];
    render(<HardwareScreen />);
    expect(screen.getByText(/Заданные пределы не выполнены/)).toBeTruthy();
  });
});
