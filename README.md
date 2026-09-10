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
`backend/app/seed/data/hardware.json`. Список источников находится в
`backend/app/seed/sources.py`.

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
POST /api/recommend
POST /api/load-profile
POST /api/hardware-estimate
```

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
