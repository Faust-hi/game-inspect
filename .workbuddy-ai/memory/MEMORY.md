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

- `cd backend && ../.venv/Scripts/python.exe -m pytest -q` — 163 теста (+2 пропущено).
- `cd backend && ../.venv/Scripts/python.exe smoke_check.py --base http://127.0.0.1:8000`
  — 83 проверки работающего сервиса (8 сценариев раздела 8 плана, TOPSIS, источники,
  корзина, оборудование, проекты, админка).
- `cd frontend && npm test` — 24 теста (vitest + jsdom + testing-library).
- `cd frontend && npm run typecheck` — проверка типов; `npm run build` — сборка.
- `cd backend && ../.venv/Scripts/python.exe -m alembic check` — сверка моделей со схемой.
- CI: `.github/workflows/ci.yml` (backend: pytest + миграции; frontend: типы, тесты, сборка).

## Схема базы

Управляется Alembic (`backend/alembic/`, две ревизии: `cdf89f70b108` — первичная схема,
`0c7ee9887f46` — ограничения целостности для баз, созданных до миграций).
Новая база поднимается `alembic upgrade head`; старую, созданную `create_all`,
нужно отметить `alembic stamp head`. При запуске backend пишет в журнал состояние
миграций. В `alembic/env.py` для SQLite соединение переведено в `AUTOCOMMIT` и
миграции обёрнуты в `PRAGMA foreign_keys=OFF/ON` — иначе batch-режим (пересоздание
таблиц) падает на `FOREIGN KEY constraint failed`.

## Структура ответа API (важно)

- Элемент рекомендации — **плоский**: `method_code`, `method_name`, `flags`, `flag_labels`,
  `reasons`, `criteria`. Вложенного объекта `method` нет.
- Профиль нагрузки: `cpu`, `gpu`, `ram`, `vram`, `disk`, `network`, `per_resource`.
- Аппаратная оценка: `reference_cpu`, `reference_gpu`, `estimated_vram_gb`,
  `estimated_ram_gb`, `confidence`, `confidence_label`, `caveats`, `exceeds_catalog`.
  Ключей `cpu` / `gpu` / `disclaimer` **нет**.

## Консистентность результата во frontend (не нарушать)

Любое изменение входа (`updateProfile`, `resetProfile`, `setBasket`, `toggleBasket`,
`clearBasket`, `loadProject`) обязано сбрасывать `result` через `discardResult()`.
Отпечаток входа считается функцией `inputKeyOf(profile, basket)` (корзина сортируется —
порядок выбора на расчёт не влияет). В `calculate()` ключ берётся **синхронно из
замыкания**, не из ref, обновляемого в эффекте: эффекты экранов выполняются раньше
эффектов провайдера, иначе свежий результат отбрасывается как устаревший (этот баг
уже был и исправлен — есть тест).

## Текущее состояние

Реализованы все разделы плана 1–9 и 11. Наполнение MVP: 15 функций, 68 методов,
4 движка, 15 примеров игр, 30 CPU, 30 GPU, 19 конфликтов, 53 инструмента, 270 связей.
Документация: `README.md` в корне.

Замечания код-ревью закрыты, кроме трёх пунктов, зафиксированных в README как
направления развития: сквозной Playwright-сценарий визарда, генерация типов frontend
из OpenAPI вместо ручного дублирования в `types.ts`, property-based тесты.
