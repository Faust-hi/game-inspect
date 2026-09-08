import { cleanup, render, screen } from '@testing-library/react';
import { afterEach, expect, it } from 'vitest';
import { HardwareWarnings } from '../components/HardwareWarnings';
import type { HardwareEstimate } from '../types';

afterEach(cleanup);

it('keeps API, memory and modelling limitations in printable content', () => {
  const hardware = {
    exceeds_catalog: true, unmet_limits: ['Нет поддержки API'],
    applicability_limits: ['Платформа вне модели'], modeling_gaps: ['Пик памяти неизвестен'],
    caveats: ['Нет поддержки API', 'Индекс не является измеренным FPS'],
  } as HardwareEstimate;
  render(<HardwareWarnings hardware={hardware} />);
  expect(screen.getAllByText('Нет поддержки API')).toHaveLength(1);
  expect(screen.getByText('Пик памяти неизвестен')).toBeTruthy();
  expect(screen.getByText('Платформа вне модели')).toBeTruthy();
  expect(screen.queryByText(/нагрузка выше самых/)).toBeNull();
});
