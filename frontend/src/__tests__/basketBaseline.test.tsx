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

it('разрешает фиксацию при условном риске и учтённых решениях', () => {
  state.result.basket_conflicts[0].conflict_type = 'risk';
  render(<BasketScreen />);
  expect(screen.getByText('Конкуренция за GPU')).toBeTruthy();
  const save = screen.getByRole('button', { name: 'Зафиксировать корзину как реализованную' }) as HTMLButtonElement;
  expect(save.disabled).toBe(false);
  fireEvent.click(save);
  expect(state.saveBaseline).toHaveBeenCalledOnce();
});

it('блокирует фиксацию при неразрешённой несовместимости', () => {
  // Кнопка блокируется любым типом кроме условного риска — проверяется один
  // представитель: ветвления по типу в коде нет, четыре копии тестировали бы
  // одну и ту же проверку `!== 'risk'`.
  state.result.basket_conflicts[0].conflict_type = 'hard_conflict';
  render(<BasketScreen />);
  const save = screen.getByRole('button', { name: 'Зафиксировать корзину как реализованную' }) as HTMLButtonElement;
  expect(save.disabled).toBe(true);
});

it('блокирует фиксацию, если часть решений не учтена расчётом', () => {
  state.result.basket_conflicts[0].conflict_type = 'risk';
  state.result.accounted_method_codes = [];
  render(<BasketScreen />);
  expect((screen.getByRole('button', { name: 'Зафиксировать корзину как реализованную' }) as HTMLButtonElement).disabled).toBe(true);
});

it('разрешает фиксацию, когда обязательная зависимость достроена системой', () => {
  // Раньше гейт сравнивал длины: корзина ['a'] при accounted = ['a', 'b']
  // блокировалась навсегда, хотя весь выбор пользователя учтён, а 'b' — это
  // достроенная зависимость, а не потеря.
  state.result.basket_conflicts[0].conflict_type = 'risk';
  state.result.accounted_method_codes = ['a', 'b'];
  render(<BasketScreen />);
  const save = screen.getByRole('button', { name: 'Зафиксировать корзину как реализованную' }) as HTMLButtonElement;
  expect(save.disabled).toBe(false);
});

it('блокирует фиксацию, когда заявленное решение выпало при совпадении длин', () => {
  // Ложно-разрешённый случай того же гейта: длины совпали (1 = 1), но 'a' вне
  // расчёта, а вместо него учтён другой метод. Проверка длины такой случай
  // пропускала, и основа фиксировалась без решения пользователя.
  state.result.basket_conflicts[0].conflict_type = 'risk';
  state.result.accounted_method_codes = ['b'];
  render(<BasketScreen />);
  const save = screen.getByRole('button', { name: 'Зафиксировать корзину как реализованную' }) as HTMLButtonElement;
  expect(save.disabled).toBe(true);
});
