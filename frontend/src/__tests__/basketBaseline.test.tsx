import { cleanup, fireEvent, render, screen } from '@testing-library/react';
import { afterEach, expect, it, vi } from 'vitest';
import { BasketScreen } from '../screens/BasketScreen';

const state = vi.hoisted(() => ({
  profile: { stage: 'prototype' }, basket: ['a'],
  baseline: { profile: { stage: 'prototype' }, basket: ['a'] },
  catalog: { methods: [], enums: null }, calculating: false,
  saveBaseline: vi.fn(), toggleBasket: vi.fn(), clearBasket: vi.fn(), calculate: vi.fn(),
  result: {
    accounted_method_codes: ['a'], basket_dependencies: [], basket_synergies: [],
    basket_conflicts: [{ a_code: 'a', b_code: 'b', conflict_type: 'risk', conflict_label: 'Риск', severity: 3,
      description: 'Конкуренция за GPU', resolution: 'Проверить профиль очередей', source_url: '' }],
  },
}));
vi.mock('../store', () => ({ useStore: () => state, useEnsureResult: () => {} }));
afterEach(() => { cleanup(); vi.clearAllMocks(); state.result.accounted_method_codes = ['a']; });

it('allows an accounted implementation with a visible conditional risk to be saved', () => {
  state.result.basket_conflicts[0].conflict_type = 'risk';
  render(<BasketScreen />);
  expect(screen.getByText('Конкуренция за GPU')).toBeTruthy();
  const save = screen.getByRole('button', { name: 'Зафиксировать корзину как реализованную' }) as HTMLButtonElement;
  expect(save.disabled).toBe(false);
  fireEvent.click(save);
  expect(state.saveBaseline).toHaveBeenCalledOnce();
});

it.each(['hard_conflict', 'alternative', 'dependency', 'unknown'])('blocks unresolved %s when saving', type => {
  state.result.basket_conflicts[0].conflict_type = type;
  render(<BasketScreen />);
  const save = screen.getByRole('button', { name: 'Зафиксировать корзину как реализованную' }) as HTMLButtonElement;
  expect(save.disabled).toBe(true);
});

it('still blocks a risk-only basket if some implementation could not be accounted', () => {
  state.result.basket_conflicts[0].conflict_type = 'risk';
  state.result.accounted_method_codes = [];
  render(<BasketScreen />);
  expect((screen.getByRole('button', { name: 'Зафиксировать корзину как реализованную' }) as HTMLButtonElement).disabled).toBe(true);
});
