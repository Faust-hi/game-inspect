/** Область применимости в экране оборудования (D06/D18). */
import { cleanup, render, screen } from '@testing-library/react';
import { afterEach, describe, expect, it, vi } from 'vitest';
import { HardwareScreen } from '../screens/HardwareScreen';
import type { HardwareEstimate } from '../types';

vi.mock('../store', () => ({
  useStore: () => ({ result: { hardware: hardware() }, calculating: false }),
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
    unmet_limits: ['Количественный прогноз доступен только для Windows/Linux ПК.'],
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
  afterEach(cleanup);

  it('показывает отказ прогноза вместо PC-ориентира', () => {
    render(<HardwareScreen />);
    expect(screen.getByText(/Вне области применимости модели/)).toBeTruthy();
    expect(screen.getAllByText(/только для Windows\/Linux ПК/).length).toBeGreaterThanOrEqual(1);
  });
});
