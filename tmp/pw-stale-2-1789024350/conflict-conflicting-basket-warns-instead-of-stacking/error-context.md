# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: conflict.spec.ts >> conflicting basket warns instead of stacking
- Location: e2e\conflict.spec.ts:8:1

# Error details

```
Error: expect(locator).toBeVisible() failed

Locator: getByRole('button', { name: /Игровые функции/ })
Expected: visible
Timeout: 5000ms
Error: element(s) not found

Call log:
  - Expect "toBeVisible" getByRole('button', { name: /Игровые функции/ }) with timeout 5000ms
  - waiting for getByRole('button', { name: /Игровые функции/ })

```

```yaml
- text: "{\"message\":\"Backend запущен. Frontend не собран: выполните сборку в каталоге frontend.\",\"health\":\"/api/health\"}"
```

# Test source

```ts
  1  | import { test, expect } from '@playwright/test';
  2  | 
  3  | // Видимость конфликта в интерфейсе: несовместимая пара из каталога,
  4  | // положенная в корзину через карточки решений, показывает предупреждение
  5  | // «A ↔ B» в корзине, а не складывает эффекты молча.
  6  | // API используется только для подбора пары, видимой в рекомендациях;
  7  | // само предупреждение проверяется глазами пользователя.
  8  | test('conflicting basket warns instead of stacking', async ({ page }) => {
  9  |   const errors: string[] = [];
  10 |   page.on('pageerror', error => errors.push(error.message));
  11 |   await page.goto('/');
> 12 |   await expect(page.getByRole('button', { name: /Игровые функции/ })).toBeVisible();
     |                                                                       ^ Error: expect(locator).toBeVisible() failed
  13 | 
  14 |   const conflicts = await page.request.get('/api/catalog/conflicts').then(r => r.json());
  15 |   const methods = await page.request.get('/api/catalog/methods').then(r => r.json());
  16 |   const functions = await page.request.get('/api/catalog/functions').then(r => r.json());
  17 |   const byCode = new Map(methods.map((m: { code: string }) => [m.code, m]));
  18 |   const fnName = new Map(functions.map((f: { code: string; name: string }) => [f.code, f.name]));
  19 |   const profile = {
  20 |     format: '3D', world_type: 'open_world', scale: 'large', stage: 'prototype',
  21 |     engine: 'unreal', platforms: ['pc_windows'],
  22 |     target_resolution: '1080p', target_quality: 'high', target_fps: 60,
  23 |   };
  24 | 
  25 |   let pair: { a: { code: string; name: string; function_code: string }; b: { code: string; name: string; function_code: string }; fns: string[] } | null = null;
  26 |   const candidates = conflicts.filter((c: { conflict_type: string }) =>
  27 |     ['hard_conflict', 'risk', 'alternative'].includes(c.conflict_type)).slice(0, 8);
  28 |   for (const c of candidates) {
  29 |     const a = byCode.get(c.a_code);
  30 |     const b = byCode.get(c.b_code);
  31 |     if (!a?.function_code || !b?.function_code) continue;
  32 |     const fns = [...new Set([a.function_code, b.function_code])];
  33 |     const data = await page.request.post('/api/recommend', {
  34 |       data: { profile: { ...profile, functions: fns }, basket: [a.code, b.code] },
  35 |     }).then(r => r.json());
  36 |     const recs = new Set(data.recommendations.map((r: { method_code: string }) => r.method_code));
  37 |     if (recs.has(a.code) && recs.has(b.code) && data.basket_conflicts.length > 0) {
  38 |       pair = { a, b, fns };
  39 |       break;
  40 |     }
  41 |   }
  42 |   expect(pair, 'в каталоге нет конфликтной пары, видимой в рекомендациях').toBeTruthy();
  43 | 
  44 |   // Выбрать функции обоих методов.
  45 |   await page.getByRole('button', { name: /Игровые функции/ }).click();
  46 |   await page.getByRole('button', { name: 'Все', exact: true }).click();
  47 |   for (const fn of pair!.fns) {
  48 |     await page.locator('main button').filter({ has: page.getByText(fnName.get(fn), { exact: true }) }).first().click();
  49 |   }
  50 | 
  51 |   // Положить оба решения в корзину через их карточки.
  52 |   await page.getByRole('button', { name: /Варианты реализации/ }).click();
  53 |   for (const m of [pair!.a, pair!.b]) {
  54 |     const tab = page.locator('.tabs button', { hasText: fnName.get(m.function_code) });
  55 |     await expect(tab).toHaveCount(1);
  56 |     await tab.click();
  57 |     const card = page.locator('main .method-row', { has: page.locator('h3', { hasText: m.name }) });
  58 |     await expect(card.first()).toBeVisible();
  59 |     await card.first().getByRole('button', { name: 'В корзину' }).click();
  60 |     await expect(card.first().getByRole('button', { name: 'Убрать из корзины' })).toBeVisible();
  61 |   }
  62 | 
  63 |   // Корзина показывает предупреждение о несовместимости.
  64 |   await page.getByRole('button', { name: /Корзина решений/ }).click();
  65 |   await expect(page.getByText('↔').first()).toBeVisible();
  66 | 
  67 |   expect(errors).toEqual([]);
  68 | });
  69 | 
```