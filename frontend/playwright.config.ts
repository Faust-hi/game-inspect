import { defineConfig } from '@playwright/test';
import { existsSync } from 'node:fs';

const localPython = process.platform === 'win32' ? '../.venv/Scripts/python.exe' : '../.venv-linux/bin/python';
const python = existsSync(localPython) ? localPython : 'python';

export default defineConfig({
  testDir: './e2e',
  // Сборка перед прогоном: контур раздаёт dist, иначе сценарии проверяют
  // устаревший код (см. e2e/global-setup.ts).
  globalSetup: './e2e/global-setup.ts',
  workers: 1,
  timeout: 60_000,
  use: {
    baseURL: 'http://127.0.0.1:8769',
    headless: true,
    channel: process.env.PW_CHANNEL || undefined,
    trace: 'retain-on-failure',
  },
  webServer: {
    command: `"${python}" ../backend/e2e_server.py`,
    url: 'http://127.0.0.1:8769/api/health',
    reuseExistingServer: false,
    timeout: 90_000,
  },
});
