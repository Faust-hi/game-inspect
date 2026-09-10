import { test, expect } from '@playwright/test';

// Основной пользовательский путь: профиль → функции → рекомендации →
// корзина → нагрузка → железо → план → фиксация → восстановление.
// Проверяет отсутствие потери данных между шагами, а не детали алгоритмов
// (варианты алгоритмов покрыты офлайн-тестами сервисов).
test('profile → functions → basket → load → hardware → plan → fix → restore', async ({ page }) => {
  const errors: string[] = [];
  page.on('pageerror', error => errors.push(error.message));
  await page.goto('/');
  // Каталог загрузился: сайдбар этапов виден.
  await expect(page.getByRole('button', { name: /Игровые функции/ })).toBeVisible();

  // Функции: выбрать первую доступную.
  await page.getByRole('button', { name: /Игровые функции/ }).click();
  const functions = page.locator('main button').filter({ has: page.locator('input[type=checkbox]') });
  await expect(functions.first()).toBeVisible();
  await functions.first().click();

  // Рекомендации: положить первое решение в корзину.
  await page.getByRole('button', { name: /Варианты реализации/ }).click();
  await expect(page.getByRole('button', { name: /В корзину/ }).first()).toBeVisible();
  await page.getByRole('button', { name: /В корзину/ }).first().click();

  // Корзина: набор не потерян, совместимость показана.
  await page.getByRole('button', { name: /Корзина решений/ }).click();
  await expect(page.getByText('Корзина проекта')).toBeVisible();

  // Нагрузка: сводный профиль рассчитан.
  await page.getByRole('button', { name: /Профиль нагрузки/ }).click();
  await expect(page.getByText('Сводный профиль нагрузки')).toBeVisible();

  // Железо: референс с оговоркой об ориентировочности.
  await page.getByRole('button', { name: /Оборудование/ }).click();
  await expect(page.getByText('Референсная минимальная конфигурация')).toBeVisible();

  // План: порядок внедрения и сверка с практикой.
  await page.getByRole('button', { name: /Итоговый план/ }).click();
  await expect(page.getByText('Порядок внедрения')).toBeVisible();

  // Фиксация корзины как реализованной основы (сохранение в сеансе).
  await page.getByRole('button', { name: /Корзина решений/ }).click();
  await expect(page.getByRole('button', { name: /Зафиксировать корзину как реализованную/ })).toBeVisible();
  await page.getByRole('button', { name: /Зафиксировать корзину как реализованную/ }).click();
  await expect(page.getByText(/Зафиксировано решений: 1/)).toBeVisible();

  // Восстановление: перезагрузка вкладки не теряет профиль, корзину и основу.
  await page.reload();
  await expect(page.getByRole('button', { name: /Корзина решений/ })).toBeVisible();
  await page.getByRole('button', { name: /Корзина решений/ }).click();
  await expect(page.getByText(/Зафиксировано решений: 1/)).toBeVisible();
  await expect(page.getByText('Корзина проекта')).toBeVisible();

  expect(errors).toEqual([]);
});
