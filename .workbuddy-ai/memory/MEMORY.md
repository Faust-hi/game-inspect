# Долговременные заметки по проекту inspect-op

## Что за проект

Информационная система поддержки принятия решений по оптимизации разработки игр
(дипломная / исследовательская работа). Backend FastAPI + SQLAlchemy + Pydantic,
frontend React 18 + TypeScript + Vite. Все тексты интерфейса, комментарии и
документация — **на русском языке**.

## Соглашения проекта

- Язык кода-комментариев, docstring и UI — русский.
- Перечисления предметной области хранятся в БД как строки (совместимость SQLite/PostgreSQL).
- В публичных рекомендациях участвуют только записи со статусом `published` **и** указанным
  `source_url`. Это проверяется тестами — не ослаблять.
- Аппаратная оценка всегда ориентировочная: обязательны `caveats` и `confidence_label`,
  гарантировать FPS нельзя.
- Windows: `.bat`-файлы пишутся **только ASCII** (кириллица в консоли искажается).

## Как запускать

- `start.bat` в корне — полный запуск (venv → pip → npm → backend → frontend → браузер).
- Отдельно: `backend\run.bat`, `frontend\run.bat`.
- Backend: `http://127.0.0.1:8000`, frontend: `http://localhost:5173`.
- Административный раздел: заголовок `x-admin-token`, по умолчанию `admin`.

## Проверка

- `cd backend && ../.venv/Scripts/python.exe -m pytest -q` — 452 теста (+2 пропущено).
- `cd backend && ../.venv/Scripts/python.exe smoke_check.py --base http://127.0.0.1:8000`
  — 85 проверок работающего сервиса (нужно `no_proxy=127.0.0.1,localhost`,
  иначе urllib уходит в системный прокси и скрипт не видит localhost).
- `cd frontend && npm test` — 34 теста (vitest + jsdom + testing-library).
- `cd frontend && npm run typecheck` — проверка типов; `npm run build` — сборка.
- `cd backend && ../.venv/Scripts/python.exe -m alembic check` — сверка моделей со схемой.
- CI: `.github/workflows/ci.yml` (backend: pytest + миграции; frontend: типы, тесты, сборка).

## Схема базы

Управляется Alembic (`backend/alembic/`); головная ревизия — `7a1toolvers`
(`engine_tools.min_version`). Старые базы распознаются в `db_migrate.py` по
маркерным столбцам (`LEGACY_MARKER_COLUMNS`) и докатываются до head.
Новая база поднимается `alembic upgrade head`; старую, созданную `create_all`,
нужно отметить `alembic stamp head`. При запуске backend пишет в журнал состояние
миграций. В `alembic/env.py` для SQLite соединение переведено в `AUTOCOMMIT` и
миграции обёрнуты в `PRAGMA foreign_keys=OFF/ON` — иначе batch-режим (пересоздание
таблиц) падает на `FOREIGN KEY constraint failed`.

## Структура ответа API (важно)

- Элемент рекомендации — **плоский**: `method_code`, `method_name`, `flags`, `flag_labels`,
  `reasons`, `criteria`. Вложенного объекта `method` нет.
- Профиль нагрузки: `cpu`, `gpu`, `ram`, `vram` — числовая шкала 0..100 (50 — без
  изменений, считается по стоимости кадра). **`disk` и `network` — качественные**:
  всегда нейтральные 50, а смысл в `per_resource[key]` → `quantitative: False`,
  `level` (уровень влияния), `explanation`, `raw` (суммарный экспертный балл).
  Не показывать их как «проценты нагрузки» и не умножать балл на коэффициент.
- Аппаратная оценка: `reference_cpu`, `reference_gpu`, `estimated_vram_gb`,
  `estimated_ram_gb`, `confidence`, `confidence_label`, `caveats`, `exceeds_catalog`.
  Ключей `cpu` / `gpu` / `disclaimer` **нет**.
- Связь метода с инструментом движка: `tool_min_version`, `available`
  (True/False/None — отсутствие данных не считается доступностью),
  `availability_note`. У `EngineTool` есть `min_version` (UE 5.0-инструменты:
  Nanite, Lumen, World Partition, VSM, Mass, LWC).

## Правила честности модели (не нарушать)

- UMA (`memory_model="unified"`): общие страницы объединяются
  (`UNIFIED_SHARED_SHARE=0.85`), резерв VRAM не вычитается дважды, потребность
  RAM растёт — GPU-резидентные ресурсы живут в том же пуле.
- Состав установки на диске — именованные части (`_install_size_parts`),
  отдельные от резидентного набора; запас под обновления/ОС явно не входит.
- Seed каталога не должен мутировать исходные словари (никаких `pop` —
  повторное наполнение в одном процессе ломалось).

## Консистентность результата во frontend (не нарушать)

Любое изменение входа (`updateProfile`, `resetProfile`, `setBasket`, `toggleBasket`,
`clearBasket`, `loadProject`) обязано сбрасывать `result` через `discardResult()`.
Отпечаток входа считается функцией `inputKeyOf(profile, basket)` (корзина сортируется —
порядок выбора на расчёт не влияет). В `calculate()` ключ берётся **синхронно из
замыкания**, не из ref, обновляемого в эффекте: эффекты экранов выполняются раньше
эффектов провайдера, иначе свежий результат отбрасывается как устаревший (этот баг
уже был и исправлен — есть тест).

## Текущее состояние

Реализованы все разделы плана 1–9 и 11. Наполнение MVP: 36 функций, 111 методов,
7 движков, 70 инструментов. Документация: `README.md` в корне, план и ход
исправлений — `docs/research/CONTINUATION-2026-09-09.md` (§10).

Все пункты §10.2 плана исправлений закрыты (09.09.2026): версия движка у
инструментов, UMA, состав установки, качественные сеть/диск в сводке, seed
без `pop`. Осталось вне кода: пользовательская проверка восстановления ввода
в свежей вкладке; 51 источник Wikipedia (массово не заменять).

Замечания код-ревью закрыты, кроме трёх пунктов, зафиксированных в README как
направления развития: сквозной Playwright-сценарий визарда, генерация типов frontend
из OpenAPI вместо ручного дублирования в `types.ts`, property-based тесты.
