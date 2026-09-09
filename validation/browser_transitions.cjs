// Real browser workflow against an isolated SQLite database and built frontend.
const { chromium, expect } = require('../frontend/node_modules/@playwright/test');
const { spawn } = require('node:child_process');
const { mkdtempSync, writeFileSync } = require('node:fs');
const { tmpdir } = require('node:os');
const { join, resolve } = require('node:path');
const net = require('node:net');

(async () => {
  const root = resolve(__dirname, '..');
  const temp = mkdtempSync(join(tmpdir(), 'game-inspect-transitions-'));
  const listener = net.createServer();
  await new Promise(done => listener.listen(0, '127.0.0.1', done));
  const port = listener.address().port;
  await new Promise(done => listener.close(done));
  const server = spawn(join(root, '.venv/Scripts/python.exe'), ['-m', 'uvicorn', 'app.main:app', '--host', '127.0.0.1', '--port', String(port)], {
    cwd: join(root, 'backend'), windowsHide: true,
    env: { ...process.env, DATABASE_URL: 'sqlite:///' + join(temp, 'test.db').replaceAll('\\', '/'), AUTO_SEED: 'true' },
    stdio: ['ignore', 'pipe', 'pipe'],
  });
  let log = '';
  server.stdout.on('data', value => { log += value; });
  server.stderr.on('data', value => { log += value; });
  const base = `http://127.0.0.1:${port}`;
  let browser;
  try {
    for (let attempt = 0; ; attempt++) {
      if (server.exitCode !== null) throw new Error('Server exited: ' + log);
      try {
        const health = await fetch(base + '/api/health');
        if (health.ok && (await health.json()).status === 'ok') break;
      } catch {}
      if (attempt > 60) throw new Error('Server readiness timeout: ' + log);
      await new Promise(done => setTimeout(done, 500));
    }
    browser = await chromium.launch({ headless: true, channel: 'chrome' });
    const context = await browser.newContext({ viewport: { width: 1440, height: 1000 } });
    const page = await context.newPage();
    const errors = [];
    page.on('pageerror', error => errors.push(error.message));
    await page.goto(base);
    const navigate = name => page.locator('.step-item').filter({ hasText: name }).click();
    await navigate('Игровые функции');
    await page.getByRole('button').filter({ hasText: 'Симуляция ткани' }).click();
    await navigate('Варианты реализации');
    await page.locator('.method-row').filter({ hasText: 'Ткань с ограничениями и коллизиями' }).first()
      .getByRole('button', { name: 'В корзину', exact: true }).click();
    await navigate('Корзина решений');
    const save = page.getByRole('button', { name: 'Зафиксировать корзину как реализованную', exact: true });
    await expect(save).toBeEnabled();
    await save.click();
    await expect(page.getByText('Уже реализовано: без повторного внедрения', { exact: true })).toBeVisible();
    await navigate('Стадия и бюджеты');
    await page.getByRole('button', { name: 'релиз', exact: true }).click();
    await navigate('Корзина решений');
    await expect(page.getByText('Уже реализовано: без повторного внедрения', { exact: true })).toBeVisible();
    await page.locator('.method-row').filter({ hasText: 'Ткань с ограничениями и коллизиями' })
      .getByRole('button', { name: 'Убрать', exact: true }).click();
    await navigate('Варианты реализации');
    await page.locator('.method-row').filter({ hasText: 'Подготовленное движение ткани' }).first()
      .getByRole('button', { name: 'В корзину', exact: true }).click();
    await navigate('Корзина решений');
    await expect(page.getByText('Замена реализации: переработка реализации', { exact: true })).toBeVisible();
    const read = () => page.evaluate(() => JSON.parse(sessionStorage.getItem('gamedev_dss_project_v1')));
    const before = await read();
    expect(before.baseline.basket).toEqual(['cloth_constraint_simulation']);
    expect(before.basket).toEqual(['cloth_baked_animation']);
    expect(before.profile.stage).toBe('release');
    await page.reload();
    await navigate('Корзина решений');
    await expect(page.getByText('Замена реализации: переработка реализации', { exact: true })).toBeVisible();
    expect(await read()).toEqual(before);
    await page.screenshot({ path: join(root, 'validation/technical-integration/basket-browser.png'), fullPage: true });
    await navigate('Итоговый план');
    await expect(page.getByText('Замена реализации: переработка реализации', { exact: true })).toBeVisible();
    await expect(page.getByText('Вывод прежних решений из реализации', { exact: true })).toBeVisible();
    const fresh = await browser.newContext();
    const freshPage = await fresh.newPage();
    await freshPage.goto(base);
    await expect(freshPage.locator('.step-item').filter({ hasText: 'Игровые функции' })).toBeEnabled();
    expect(await freshPage.evaluate(() => JSON.parse(sessionStorage.getItem('gamedev_dss_project_v1'))?.baseline)).toBeNull();
    freshPage.on('pageerror', error => errors.push(error.message));
    const freshNavigate = name => freshPage.locator('.step-item').filter({ hasText: name }).click();
    await freshNavigate('Профиль игры');
    await freshPage.getByRole('checkbox', { name: 'Мультиплеер предусмотрен' }).check();
    const [methods, functions] = await Promise.all(['/api/catalog/methods', '/api/catalog/functions'].map(async path => {
      const response = await fetch(base + path);
      if (!response.ok) throw new Error('Catalog request failed: ' + response.status);
      return response.json();
    }));
    const catalog = { methods, functions };
    const reviewedCodes = ['ai_director_pacing', 'subtick_networking', 'lag_compensation_rewind', 'directstorage_io', 'async_compute_overlap'];
    const reviewed = catalog.methods.filter(method => reviewedCodes.includes(method.code));
    expect(reviewed).toHaveLength(5);
    await freshNavigate('Игровые функции');
    await freshPage.getByRole('button', { name: 'Все', exact: true }).click();
    for (const code of new Set(reviewed.map(method => method.function_code))) {
      const fn = catalog.functions.find(fn => fn.code === code);
      await freshPage.getByRole('button').filter({ hasText: fn.name }).click();
    }
    await freshNavigate('Варианты реализации');
    for (const method of reviewed) {
      const fn = catalog.functions.find(fn => fn.code === method.function_code);
      await freshPage.locator('.tabs button').filter({ hasText: fn.name }).click();
      await freshPage.locator('.method-row').filter({ hasText: method.name }).first()
        .getByRole('button', { name: 'В корзину', exact: true }).click();
    }
    await freshNavigate('Корзина решений');
    const freshSave = freshPage.getByRole('button', { name: 'Зафиксировать корзину как реализованную', exact: true });
    await expect(freshSave).toBeEnabled();
    await freshSave.click();
    await expect(freshPage.getByText('Уже реализовано: без повторного внедрения', { exact: true })).toHaveCount(5);
    await freshPage.reload();
    await freshNavigate('Корзина решений');
    await expect(freshPage.getByText('Уже реализовано: без повторного внедрения', { exact: true })).toHaveCount(5);
    await freshPage.screenshot({ path: join(root, 'validation/technical-integration/reviewed-basket-browser.png'), fullPage: true });
    expect(errors).toEqual([]);
    const result = { passed: true, checks: ['choose technical function', 'implement and save basket', 'later stage retains implementation',
      'replace implementation', 'reload preserves baseline and draft', 'plan includes removal and replacement', 'new browser context starts clean',
      'all five reviewed methods selectable through UI', 'all five saved as implemented and retained after reload'],
      pageErrors: errors };
    writeFileSync(join(root, 'validation/technical-integration/browser.json'), JSON.stringify(result, null, 2) + '\n');
    console.log(JSON.stringify(result));
  } finally {
    if (browser) await browser.close();
    server.kill();
    await new Promise(done => server.exitCode !== null ? done() : server.once('exit', done));
    writeFileSync(join(temp, 'server.log'), log);
  }
})().catch(error => { console.error(error); process.exitCode = 1; });
