# ИС поддержки принятия решений по оптимизации разработки игр

Локальное веб-приложение для выбора способов реализации игровых функций на
стадии проектирования. Оно формирует объяснимые рекомендации по профилю игры,
проверяет совместимость выбранных решений и оценивает референсный класс
оборудования.

Приложение не подключается к проекту движка, не выполняет runtime-профилирование
и ничего не применяет автоматически. Профилировщики и инструменты движков в
каталоге — это источники и подсказки для последующей ручной проверки.

## Быстрый запуск

Требования: Python 3.11+ и Node.js 22+ с npm. СУБД устанавливать не нужно:
по умолчанию используется локальный SQLite-файл.

### Windows

Из корня проекта:

```bat
start.bat
```

Скрипт создаёт `.venv`, устанавливает зависимости backend из
`backend/requirements.lock`, выполняет `npm ci`, запускает оба сервиса в
отдельных окнах и открывает `http://localhost:5173`.

После подготовки сервисы можно запускать отдельно:

```bat
backend\run.bat
frontend\run.bat
```

### Linux

```bash
bash start.sh
```

Скрипт создаёт `.venv-linux`, устанавливает Python-зависимости и frontend,
проверяет готовность обоих HTTP-сервисов и открывает браузер. `Ctrl+C` корректно
останавливает только процессы, запущенные этим скриптом.

Полезные варианты:

```bash
bash start.sh --check                 # проверить версии и свободные порты
bash start.sh --skip-install          # использовать уже установленные зависимости
bash start.sh --no-browser            # запуск без открытия браузера
bash start.sh --service backend       # запустить только backend
bash start.sh --service frontend      # запустить только frontend
```

Для Mint, Kali, Ubuntu и Debian обычно нужны системные пакеты
`python3`, `python3-venv`, `python3-pip` и Node.js 22+:

```bash
sudo apt update
sudo apt install python3 python3-venv python3-pip
```

Если подходящий Python не является системным `python3`, его можно выбрать явно:

```bash
DSS_PYTHON=python3.13 bash start.sh
```

`sudo` для запуска самого приложения не требуется. Отдельные сервисы запускаются
через `bash backend/run.sh` и `bash frontend/run.sh` после подготовки окружения.

## Ручной запуск и настройки

Backend:

```bash
cd backend
python -m venv ../.venv
../.venv/Scripts/python.exe -m pip install -r requirements.txt  # Windows
../.venv/Scripts/python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

В Linux вместо `../.venv/Scripts/python.exe` используется
`../.venv-linux/bin/python`.

Frontend в отдельном терминале:

```bash
cd frontend
npm ci
npm run dev
```

Основные адреса:

| Адрес | Назначение |
| --- | --- |
| `http://localhost:5173` | пользовательский интерфейс Vite |
| `http://127.0.0.1:8000/api/health` | состояние backend и готовность каталога |
| `http://127.0.0.1:8000/api/docs` | интерактивная документация API |

Настройки читаются из окружения и `backend/.env`. Шаблон находится в
`backend/.env.example`.

По умолчанию:

```text
DATABASE_URL=sqlite:///./gamedev_dss.db
AUTO_SEED=true
```

При первом запуске пустая база заполняется демонстрационным каталогом. Повторное
заполнение идемпотентно и не перезаписывает административные правки без явного
флага восстановления.

Поддерживается только SQLite. Для изменения схемы используются миграции Alembic:

```bash
cd backend
python -m alembic upgrade head
python -m alembic check
python -m alembic revision --autogenerate -m "описание изменения"
```

## Что делает система

Пользователь заполняет профиль проекта: формат и масштаб игры, стадию,
движок, платформы, целевые параметры изображения и набор игровых функций.
Затем приложение:

- фильтрует неприменимые решения по ограничениям проекта;
- ранжирует варианты многокритериальным методом TOPSIS;
- показывает причины, источники, ограничения и рекомендуемую стадию внедрения;
- учитывает конфликты, зависимости и синергии в корзине решений;
- строит сводный профиль нагрузки по CPU, GPU, RAM, VRAM, диску и сети;
- оценивает референсный минимальный класс CPU/GPU;
- показывает устойчивость ранжирования к изменению весов и явно отмечает пробелы
  каталога.

В разделе администрирования доступны проверка целостности, заполнение
демоданными, импорт CSV/JSON для поддерживаемых сущностей, просмотр статусов и
переходы `черновик → проверено → опубликовано`. Публичные каталоги используют
только опубликованные записи с источниками.

## Структура проекта

```text
.
├── backend/
│   ├── app/
│   │   ├── api/              # каталог, расчёт и администрирование
│   │   ├── models/           # SQLAlchemy-модели и перечисления
│   │   ├── schemas/          # Pydantic-контракты API
│   │   ├── services/         # правила, TOPSIS, рекомендации, оборудование
│   │   └── seed/             # каталог методов, функций, движков и hardware.json
│   ├── alembic/              # история миграций схемы
│   └── tests/                # backend-тесты pytest
├── frontend/
│   ├── src/components/       # переиспользуемые элементы интерфейса
│   ├── src/screens/          # экраны пользовательского и admin-разделов
│   ├── src/__tests__/        # модульные тесты Vitest
│   └── e2e/                  # браузерные сценарии Playwright
├── tools/
│   ├── launch_linux.py       # Linux-запуск и управление дочерними процессами
│   └── smoke_linux_launcher.py # smoke-проверка Linux-запуска для CI
├── .github/workflows/ci.yml  # backend, frontend и startup-проверки
├── start.bat                 # запуск в Windows
├── start.sh                  # запуск в Linux
└── README.md
```

Данные сида разделены по назначению: методы, функции, движки и связи описаны в
`backend/app/seed/*_data.py`, а характеристики оборудования — в
`backend/app/seed/data/hardware.json`. Список базовых источников находится в
`backend/app/seed/sources.py`; дополнительный доказательный каталог, игровые
кейсы, claims, узлы зависимостей и сценарии трудоёмкости — в
`backend/app/seed/evidence_catalog.py`. Миграция создаёт отдельные таблицы
`EvidenceSource`, `EvidenceClaim`, `GameCase`, `CaseEvidence`,
`TechnologyNode`, `DependencyEdge`, `WorkPackage` и `TeamScenario`, не удаляя
legacy-поля источников.

## Отчёт

Исследовательский отчёт можно пересобрать из корня проекта:

```bash
python tools/generate_research_report.py
```

Команда создаёт русскую Markdown-версию в
`research/game-development-dss-study.md` и PDF в
`output/pdf/game-development-dss-study.pdf`, а также построчную матрицу
покрытия в `research/catalog-coverage-matrix.md`. Если рабочая база ещё не прошла
новую миграцию, отчёт честно помечает её как legacy-снимок и показывает
ожидаемый seed-каталог вместо выдуманных чисел.

> Сборка PDF требует `reportlab`. Он установлен в `.venv`; интерпретатор
> `.dss-venv` его не содержит. Markdown-часть собирается любым из двух.

## Эксплуатационный runbook

Пайплайн доказательной базы состоит из четырёх независимых проверок. Каждая
запись каталога обязана пройти их без выдуманных данных: источник либо
подтверждён, либо явно объявлен пробелом.

### Рантаймы

| Задача | Интерпретатор |
| --- | --- |
| Инструменты `tools/` | `.dss-venv/Scripts/python.exe` (или системный Python) |
| Бэкенд, аудит, отчёты (MD) | `.dss-venv/Scripts/python.exe` (SQLAlchemy 2.0) |
| PDF-сборка | `.venv/Scripts/python.exe` (нужен `reportlab`) |

### Порядок операций

```bash
# 1. Схема-проверка паков без сети (быстро, безопасно)
python tools/verify_sources.py --packs-only --no-net

# 2. Загрузка паков в БД (бэкап создаётся перед загрузкой)
cd backend && cp gamedev_dss.db gamedev-dss.bak-$(date +%Y%m%d-%H%M%S).db
./../.dss-venv/Scripts/python.exe -c "import sys;sys.path.insert(0,'.');\
from app.database import SessionLocal; from app.seed.pack_loader import sync_packs;\
db=SessionLocal(); print(sync_packs(db)); db.commit()"

# 3. Аудит покрытия (≥3 claims, ≥2 источника с локатором, ≥2 игровых примера)
cd .. && ./.dss-venv/Scripts/python.exe tools/audit_evidence.py

# 4. Полная HTTP-проверка всех URL (паки + БД, ~1 мин)
./.dss-venv/Scripts/python.exe tools/verify_sources.py

# 5. Перегенерация отчёта (MD + PDF + матрица)
./.venv/Scripts/python.exe tools/generate_research_report.py

# 6. Тесты
cd backend && ../.dss-venv/Scripts/python.exe -m pytest tests/ -q
cd ../frontend && npm test && npm run build
```

> Внимание: шаг 1 перезаписывает `research/verification_report.json` без сетевых
> полей. Если он нужен для итоговых артефактов, после него выполните шаг 4.

### Приёмка доказательной базы

Итоговый статус достоверности собран в `research/reliability-report.md`. Он
обязан подтверждать нулевые значения по следующим проверкам:

| Проверка | Инвариант |
| --- | --- |
| `claim_dangling_source` | 0 — нет ссылок на несуществующий источник |
| `derived_missing_formula_or_inputs` | 0 — у каждого `derived` есть формула и входы |
| `numeric_claim_without_source` | 0 — числа без источника не публикуются |
| `claim_missing_locator` | 0 — у каждого утверждения есть локатор |
| `work_package_p80_lt_p50` | 0 — P80 не меньше P50 |
| `conflict_without_url` | 0 |
| молчаливые дыры (`entities_unproven_and_undeclared`) | 0 — пробел либо доказан, либо объявлен |

Явно объявленные остатки (не дефекты): `declared_gap_claims` — пробелы без
shipped-подтверждения; `dependency_edge_without_source` — плановые зависимости,
помеченные `expert_estimate`; `method_engine_link_without_url` — связи,
помеченные `user_defined`; `url_error` / `protected` — сетевые ограничения
прокси и бот-стены, не мёртвые ссылки.

### Правила, которые нельзя нарушать

1. **Отсутствие источника не считается совместимостью.** Нет доказательства —
   создаётся запись-пробел `field='adoption_evidence_gap'`, `basis='unknown'`,
   `evidence_level='low'`, `source=None`.
2. **`derived` требует формулу и входные параметры.** Качественное рассуждение —
   это `documented` или `unknown`.
3. **URL никогда не выдумывается.** Замена — только на пробитый 2xx-эквивалент.
4. **Прямой пример ≠ перекрёстный.** Инструмент без прямого примера обязан
   объявить пробел; reference-реализации не считаются игровыми примерами.
5. **Регистр URL важен.** Дедупликация без учёта регистра, проба — с оригиналом.

### Воспроизводимость

Отчёт фиксирует ревизию каталога (`revision`) в шапке. Одинаковый вход, версия
алгоритма и ревизия каталога дают одинаковый результат. Проверки детерминизма и
обязательные инварианты модели (масштаб сцены → нагрузка, разрешение → GPU,
NPC → CPU, RT не заменяет raster, RAM/VRAM не складываются, P80 ≥ P50)
покрыты `backend/tests/`.


## API

Основные публичные маршруты:

```text
GET  /api/health
GET  /api/meta/enums
GET  /api/catalog/functions
GET  /api/catalog/methods
GET  /api/catalog/methods/{code}
GET  /api/catalog/engines
GET  /api/catalog/conflicts
GET  /api/catalog/hardware
GET  /api/catalog/stage-guidance
GET  /api/catalog/sources
GET  /api/catalog/evidence
GET  /api/catalog/evidence/{entity}/{code}
GET  /api/catalog/evidence-summary
GET  /api/catalog/cases
GET  /api/catalog/cases/{code}
GET  /api/catalog/dependencies
GET  /api/catalog/teams
POST /api/recommend
POST /api/load-profile
POST /api/hardware-estimate
POST /api/schedule
POST /api/report-data
GET  /api/report-data
```

`/api/report-data` в GET-форме принимает профиль query-параметрами и повторяемый
`basket` с кодами методов; POST-форма предназначена для полного JSON-профиля и
baseline. Отчётный снимок включает рекомендации, доказательства, кейсы,
зависимости и сценарный план.

### Профили команды для `/api/schedule`

| Код | Размер | Потоки | Комментарий |
| --- | --- | --- | --- |
| `solo` | 1 | 1 | один специалист, узкие роли последовательно |
| `small_2_5` | 4 | 2 | общая QA/production ёмкость |
| `custom` | 6 | 3 | нетиповая команда; значения — экспертное допущение, переопределяются |
| `mid_6_15` | 10 | 5 | специализированные роли |
| `large_16_plus` | 24 | 12 | срок ограничен зависимостями и quality gates |

Неизвестный код не подменяется похожим профилем: он возвращается под своим
кодом, а в описании явно сообщается о подстановке. Размер команды меняет
календарь, но не сумму person-days.

Полный контракт запросов и ответов публикуется автоматически в Swagger по
адресу `/api/docs`. Административные маршруты находятся под `/api/admin`;
доступ к ним рассчитан на локальный режим приложения.

## Проверки

Backend:

```bash
cd backend
python -m pytest -q
```

Frontend:

```bash
cd frontend
npm run typecheck
npm test
npm run build
```

Playwright сам запускает временный backend на порту `8769` и перед прогоном
собирает frontend, если сборка устарела:

```bash
npm run test:e2e
```

CI дополнительно проверяет синтаксис shell-скриптов, устанавливает зависимости
из lock-файлов, запускает Linux smoke-сценарий с проверкой готовности и
остановки сервисов, выполняет миграции и production-сборку frontend.
