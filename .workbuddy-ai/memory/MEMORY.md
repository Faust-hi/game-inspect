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

- `cd backend && ../.venv/Scripts/python.exe -m pytest -q` — 50 тестов.
- `cd backend && ../.venv/Scripts/python.exe smoke_check.py --base http://127.0.0.1:8000`
  — 83 проверки работающего сервиса (8 сценариев раздела 8 плана, TOPSIS, источники,
  корзина, оборудование, проекты, админка).

## Структура ответа API (важно)

- Элемент рекомендации — **плоский**: `method_code`, `method_name`, `flags`, `flag_labels`,
  `reasons`, `criteria`. Вложенного объекта `method` нет.
- Профиль нагрузки: `cpu`, `gpu`, `ram`, `vram`, `disk`, `network`, `per_resource`.
- Аппаратная оценка: `reference_cpu`, `reference_gpu`, `estimated_vram_gb`,
  `estimated_ram_gb`, `confidence`, `confidence_label`, `caveats`, `exceeds_catalog`.
  Ключей `cpu` / `gpu` / `disclaimer` **нет**.

## Текущее состояние

Реализованы все разделы плана 1–9 и 11. Наполнение MVP: 15 функций, 68 методов,
4 движка, 15 примеров игр, 30 CPU, 30 GPU, 19 конфликтов, 53 инструмента, 270 связей.
Документация: `README.md` в корне.
