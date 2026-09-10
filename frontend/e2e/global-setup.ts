import { execSync } from 'node:child_process';
import { existsSync, statSync } from 'node:fs';
import { readdir } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

/**
 * Сборка перед браузерными сценариями — только если она устарела.
 *
 * Контур раздаёт готовую сборку `frontend/dist`, поэтому без пересборки
 * сценарии проверяют устаревший код: новая функциональность не попала в
 * бандл, сценарий молча проходит там, где поведение ещё не изменилось,
 * и падает на элементах, которых в старом бандле нет. Такая проверка не
 * защищает, а создаёт ложную уверенность.
 *
 * Сборка выполняется здесь, а не в команде запуска, чтобы любой способ
 * вызова (`npx playwright test` или `npm run test:e2e`) был безопасным.
 * globalSetup выполняется до подъёма сервера, поэтому сервер уже раздаёт
 * свежие файлы.
 *
 * Пересборка только при устаревании: полная сборка очищает `dist` и идёт
 * около секунды, а прогон запускают часто. Свежая сборка не пересобирается.
 */
// Каталог проекта — по расположению файла, а не по process.cwd():
// прогон должен работать и при вызове из другого каталога.
const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const DIST_INDEX = path.join(ROOT, 'dist', 'index.html');
const WATCHED = ['src', 'index.html', 'vite.config.ts', 'tsconfig.json'];

async function newestSourceMtime(dir: string): Promise<number> {
  let newest = 0;
  for (const entry of await readdir(dir, { withFileTypes: true })) {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      newest = Math.max(newest, await newestSourceMtime(full));
    } else {
      newest = Math.max(newest, statSync(full).mtimeMs);
    }
  }
  return newest;
}

export default async function globalSetup(): Promise<void> {
  let sources = 0;
  for (const item of WATCHED) {
    const full = path.join(ROOT, item);
    if (!existsSync(full)) continue;
    sources = Math.max(
      sources,
      statSync(full).isDirectory() ? await newestSourceMtime(full) : statSync(full).mtimeMs,
    );
  }

  const distMtime = existsSync(DIST_INDEX) ? statSync(DIST_INDEX).mtimeMs : 0;
  if (distMtime >= sources) {
    console.log('[e2e] сборка свежая — пересборка не требуется');
    return;
  }

  console.log('[e2e] сборка устарела или отсутствует — выполняется npm run build');
  execSync('npm run build', { stdio: 'inherit', cwd: ROOT });
}
