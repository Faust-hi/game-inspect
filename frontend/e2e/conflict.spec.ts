import { test, expect } from '@playwright/test';

// Видимость конфликта в интерфейсе: несовместимая пара из каталога,
// положенная в корзину через карточки решений, показывает предупреждение
// «A ↔ B» в корзине, а не складывает эффекты молча.
// API используется только для подбора пары, видимой в рекомендациях;
// само предупреждение проверяется глазами пользователя.
test('conflicting basket warns instead of stacking', async ({ page }) => {
  const errors: string[] = [];
  page.on('pageerror', error => errors.push(error.message));
  await page.goto('/');
  await expect(page.getByRole('button', { name: /Игровые функции/ })).toBeVisible();

  const conflicts = await page.request.get('/api/catalog/conflicts').then(r => r.json());
  const methods = await page.request.get('/api/catalog/methods').then(r => r.json());
  const functions = await page.request.get('/api/catalog/functions').then(r => r.json());
  const byCode = new Map(methods.map((m: { code: string }) => [m.code, m]));
  const fnName = new Map(functions.map((f: { code: string; name: string }) => [f.code, f.name]));
  const profile = {
    format: '3D', world_type: 'open_world', scale: 'large', stage: 'prototype',
    engine: 'unreal', platforms: ['pc_windows'],
    target_resolution: '1080p', target_quality: 'high', target_fps: 60,
  };

  let pair: { a: { code: string; name: string; function_code: string }; b: { code: string; name: string; function_code: string }; fns: string[] } | null = null;
  const candidates = conflicts.filter((c: { conflict_type: string }) =>
    ['hard_conflict', 'risk', 'alternative'].includes(c.conflict_type)).slice(0, 8);
  for (const c of candidates) {
    const a = byCode.get(c.a_code);
    const b = byCode.get(c.b_code);
    if (!a?.function_code || !b?.function_code) continue;
    const fns = [...new Set([a.function_code, b.function_code])];
    const data = await page.request.post('/api/recommend', {
      data: { profile: { ...profile, functions: fns }, basket: [a.code, b.code] },
    }).then(r => r.json());
    const recs = new Set(data.recommendations.map((r: { method_code: string }) => r.method_code));
    if (recs.has(a.code) && recs.has(b.code) && data.basket_conflicts.length > 0) {
      pair = { a, b, fns };
      break;
    }
  }
  expect(pair, 'в каталоге нет конфликтной пары, видимой в рекомендациях').toBeTruthy();

  // Выбрать функции обоих методов.
  await page.getByRole('button', { name: /Игровые функции/ }).click();
  await page.getByRole('button', { name: 'Все', exact: true }).click();
  for (const fn of pair!.fns) {
    await page.locator('main button').filter({ has: page.getByText(fnName.get(fn), { exact: true }) }).first().click();
  }

  // Положить оба решения в корзину через их карточки.
  await page.getByRole('button', { name: /Варианты реализации/ }).click();
  for (const m of [pair!.a, pair!.b]) {
    const tab = page.locator('.tabs button', { hasText: fnName.get(m.function_code) });
    await expect(tab).toHaveCount(1);
    await tab.click();
    const card = page.locator('main .method-row', { has: page.locator('h3', { hasText: m.name }) });
    await expect(card.first()).toBeVisible();
    await card.first().getByRole('button', { name: 'В корзину' }).click();
    await expect(card.first().getByRole('button', { name: 'Убрать из корзины' })).toBeVisible();
  }

  // Корзина показывает предупреждение о несовместимости.
  await page.getByRole('button', { name: /Корзина решений/ }).click();
  await expect(page.getByText('↔').first()).toBeVisible();

  expect(errors).toEqual([]);
});
