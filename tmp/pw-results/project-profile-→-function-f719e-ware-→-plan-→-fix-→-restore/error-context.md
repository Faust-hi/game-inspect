# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: project.spec.ts >> profile → functions → basket → load → hardware → plan → fix → restore
- Location: e2e\project.spec.ts:7:1

# Error details

```
Error: expect(locator).toBeVisible() failed

Locator: getByRole('button', { name: /Зафиксировать корзину как реализованную/ })
Expected: visible
Timeout: 5000ms
Error: element(s) not found

Call log:
  - Expect "toBeVisible" getByRole('button', { name: /Зафиксировать корзину как реализованную/ }) with timeout 5000ms
  - waiting for getByRole('button', { name: /Зафиксировать корзину как реализованную/ })

```

```yaml
- banner:
  - text: ИС оптимизации разработки игр Новый проект
  - button "Проект"
  - button "Администрирование"
- complementary:
  - text: Этапы работы
  - button "1 Профиль игры"
  - button "2 Стадия и бюджеты"
  - button "3 Игровые функции 1"
  - button "4 Варианты реализации 17"
  - button "5 Риски проекта 0"
  - button "6 Корзина решений 1"
  - button "7 Профиль нагрузки"
  - button "8 Оборудование"
  - button "9 Итоговый план"
- main:
  - heading "Корзина проекта" [level=2]
  - text: "решений: 1 суммарные трудозатраты: 2"
  - button "Пересчитать"
  - button "Очистить"
  - text: После изменения набора система пересчитывает сводный профиль нагрузки и совместимость решений. Эффекты относятся к разным подсистемам и областям работы. Общий процент ускорения без измерений не установлен; оценки каталога используются как экспертные баллы.
  - strong: Пулинг систем частиц
  - text: алгоритм позднее внедрение — низкая
  - paragraph: Системы частиц создаются заранее и переиспользуются вместо постоянного создания и удаления.
  - text: "Рекомендуемая стадия: производство контента. Текущая стадия проекта: прототип. CPU -1 GPU 0 RAM -1 VRAM 0 Диск 0 Сеть 0"
  - button "Карточка"
  - button "Убрать"
  - strong: "Совместимость набора:"
  - text: В выбранном наборе не обнаружено конфликтов и незакрытых зависимостей.
```

# Test source

```ts
  1  | import { test, expect } from '@playwright/test';
  2  | 
  3  | // Основной пользовательский путь: профиль → функции → рекомендации →
  4  | // корзина → нагрузка → железо → план → фиксация → восстановление.
  5  | // Проверяет отсутствие потери данных между шагами, а не детали алгоритмов
  6  | // (варианты алгоритмов покрыты офлайн-тестами сервисов).
  7  | test('profile → functions → basket → load → hardware → plan → fix → restore', async ({ page }) => {
  8  |   const errors: string[] = [];
  9  |   page.on('pageerror', error => errors.push(error.message));
  10 |   await page.goto('/');
  11 |   // Каталог загрузился: сайдбар этапов виден.
  12 |   await expect(page.getByRole('button', { name: /Игровые функции/ })).toBeVisible();
  13 | 
  14 |   // Функции: выбрать первую доступную.
  15 |   await page.getByRole('button', { name: /Игровые функции/ }).click();
  16 |   const functions = page.locator('main button').filter({ has: page.locator('input[type=checkbox]') });
  17 |   await expect(functions.first()).toBeVisible();
  18 |   await functions.first().click();
  19 | 
  20 |   // Рекомендации: положить первое решение в корзину.
  21 |   await page.getByRole('button', { name: /Варианты реализации/ }).click();
  22 |   await expect(page.getByRole('button', { name: /В корзину/ }).first()).toBeVisible();
  23 |   await page.getByRole('button', { name: /В корзину/ }).first().click();
  24 | 
  25 |   // Корзина: набор не потерян, совместимость показана.
  26 |   await page.getByRole('button', { name: /Корзина решений/ }).click();
  27 |   await expect(page.getByText('Корзина проекта')).toBeVisible();
  28 | 
  29 |   // Нагрузка: сводный профиль рассчитан.
  30 |   await page.getByRole('button', { name: /Профиль нагрузки/ }).click();
  31 |   await expect(page.getByText('Сводный профиль нагрузки')).toBeVisible();
  32 | 
  33 |   // Железо: референс с оговоркой об ориентировочности.
  34 |   await page.getByRole('button', { name: /Оборудование/ }).click();
  35 |   await expect(page.getByText('Референсная минимальная конфигурация')).toBeVisible();
  36 | 
  37 |   // План: порядок внедрения и сверка с практикой.
  38 |   await page.getByRole('button', { name: /Итоговый план/ }).click();
  39 |   await expect(page.getByText('Порядок внедрения')).toBeVisible();
  40 | 
  41 |   // Фиксация корзины как реализованной основы (сохранение в сеансе).
  42 |   await page.getByRole('button', { name: /Корзина решений/ }).click();
> 43 |   await expect(page.getByRole('button', { name: /Зафиксировать корзину как реализованную/ })).toBeVisible();
     |                                                                                               ^ Error: expect(locator).toBeVisible() failed
  44 |   await page.getByRole('button', { name: /Зафиксировать корзину как реализованную/ }).click();
  45 |   await expect(page.getByText(/Зафиксировано решений: 1/)).toBeVisible();
  46 | 
  47 |   // Восстановление: перезагрузка вкладки не теряет профиль, корзину и основу.
  48 |   await page.reload();
  49 |   await expect(page.getByRole('button', { name: /Корзина решений/ })).toBeVisible();
  50 |   await page.getByRole('button', { name: /Корзина решений/ }).click();
  51 |   await expect(page.getByText(/Зафиксировано решений: 1/)).toBeVisible();
  52 |   await expect(page.getByText('Корзина проекта')).toBeVisible();
  53 | 
  54 |   expect(errors).toEqual([]);
  55 | });
  56 | 
```