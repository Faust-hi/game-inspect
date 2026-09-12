# Wave 6 — Инвентаризация репозитория и карта очистки

Дата: 2026-09-12
Режим: **только чтение**. Ничего не перемещалось, не удалялось и не изменялось.
Интерпретатор проб: `C:/Users/user/Desktop/game-inspect/.dss-venv/Scripts/python.exe`.

Правило владельца: после переноса всё, что осталось вне `report/`, — это и есть
рабочий проект, и ничего больше. Всё, что имеет информационную ценность, но не
применяется, переезжает в `report/`; всё, что ценности не имеет, — кандидат на
удаление.

Классы:
- **CORE** — нужно, чтобы запустить и проверить проект.
- **→REPORT** — реальная информационная ценность, но в рантайме не участвует.
- **JUNK** — ценности нет, кандидат на удаление.

Общий размер рабочего дерева (без `.git`): ~1522 MB.

---

## (a) Классификация дерева с размерами

### Верхний уровень

| Объект | Размер | Что это | Нужно для запуска/проверки | Ценность | Вердикт | Причина |
|---|---|---|---|---|---|---|
| `backend/app/` | 5 MB | Исходники FastAPI/SQLAlchemy | да | да | **CORE** | Рантайм-код приложения |
| `backend/tests/` | ~0.3 MB | pytest-набор (24 файла) | да (CI) | да | **CORE** | Проверяет модель и API |
| `backend/alembic/` | ~0.2 MB | 16 миграций | да | да | **CORE** | Схема создаётся миграциями (`alembic check` в CI) |
| `backend/gamedev_dss.db` | 7 MB | Живая SQLite-БД | да | да | **CORE** | Рабочая БД по умолчанию |
| `backend/*.bak-*.db` (+ wal/shm) | **203 MB** | 43 резервные копии БД | нет | дубликат живой БД | **JUNK** | Каждый бэкап — снимок, воспроизводимый заново |
| `backend/requirements*.txt/lock` | ~1 MB | Зависимости | да | да | **CORE** | `requirements.lock` — источник CI/start.bat |
| `backend/run.bat|run.sh`, `wait_for_services.py` | <0.1 MB | Запуск backend | да | да | **CORE** | Вызываются `start.bat` |
| `backend/e2e_server.py` | <0.1 MB | Сервер для Playwright | да | да | **CORE** | `frontend/playwright.config.ts:21` |
| `frontend/src/` | ~2 MB | React/TS исходники | да | да | **CORE** | UI приложения |
| `frontend/e2e/` | <0.1 MB | 2 Playwright-сценария | да | да | **CORE** | `npm run test:e2e` |
| `frontend/package*.json`, `vite/tsconfig` | ~0.2 MB | Конфиг сборки | да | да | **CORE** | Сборка/тесты frontend |
| `frontend/node_modules/` | **114 MB** | npm-зависимости | да | нет | **CORE (env)** | Нужны для запуска UI |
| `frontend/dist/` | 1 MB | Прод-сборка | для e2e | нет | **CORE (артефакт)** | Пересобирается, но нужна e2e |
| `research/packs/` | 4 MB | JSON-паки доказательной базы | **да** | да | **CORE** | `pack_loader.py:33` — `PACK_DIR` рантайма |
| `research/*.md|html|json|pdf` (док-ты) | 5 MB | 49 отчётов | частично | да | **CORE (частично) / →REPORT** | см. ниже |
| `research/workqueue/` | 1 MB | Очереди/планы исследования | нет | да | **→REPORT** | Исторический процесс, не рантайм |
| `research/_mp/` | **466 MB** | Внешние первоисточники (bin/pdf/pptx/html) | нет | нет (воспроизводимо) | **JUNK** | Явно в `.gitignore`: «воспроизводятся скриптами из tools/» |
| `research/_verify_cache/` | 5 MB | Кэш 1011 записей | нет | нет | **JUNK** | Производный кэш, в `.gitignore` |
| `tools/*.py` | 1 MB | 17 CLI-инструментов | частично | да | **CORE / →REPORT** | см. ниже |
| `.github/workflows/ci.yml` | <0.1 MB | CI (3 job) | да | да | **CORE** | Запускает тесты, миграции, сборку |
| `start.bat` / `start.sh` | <0.1 MB | One-click запуск | да | да | **CORE** | Точка входа Windows/Linux |
| `README.md` | 20 KB | Документация | да | да | **CORE** | Описывает запуск и runbook |
| `.venv/` | **161 MB** | venv для PDF-отчёта | да | нет | **CORE (env)** | `start.bat`, `md_to_pdf` |
| `.dss-venv/` | **37 MB** | Рабочий интерпретатор tools/backend | да | нет | **CORE (env)** | Runbook README |
| `.runtime-packages/` | **67 MB** | Вендоренный site-packages | нет | нет | **JUNK** | Нигде не импортируется, в `.gitignore` |
| `.git-safety-backup/` | **58 MB** | Форензик-копия `.git` | нет | нет | **JUNK** | Помечено в `.gitignore` как форензик |
| `.uv-cache/` | 12 MB | Кэш uv | нет | нет | **JUNK** | Регенерируемый кэш пакетов |
| `.pnpm-store/` | 1 MB | Кэш pnpm | нет | нет | **JUNK** | Регенерируемый кэш |
| `.pytest_cache/` | 1 MB | Кэш pytest | нет | нет | **JUNK** | Регенерируемый кэш |
| `.workbuddy-ai/` | 1 MB | Состояние агента | нет | нет | **JUNK** | В `.gitignore`: «не исходники проекта» |
| `__pycache__/` (вне env) | 4 MB | Байткод | нет | нет | **JUNK** | Регенерируется |
| `output/pdf/` | 2 MB | 3 PDF-отчёта | нет | да (2 из 3) | **→REPORT** + 1 **JUNK** | `.bak.pdf` — дубликат |
| `.git/` | 58 MB | История репозитория | да | да | **CORE** | Не трогать |
| `tmp/` | **320 MB** | 337 файлов ручных проб | нет | частично | **→REPORT / JUNK** | см. ниже |

### `tmp/` детально (337 файлов)

| Группа | Размер | Вердикт | Причина |
|---|---|---|---|
| `tmp/*.py` (132) | 2 MB | **→REPORT** | Зонды-исследования = база знаний (правило проекта) |
| `tmp/res/` (PDF/TXT/JSON первоисточники) | 24 MB | **→REPORT** | Скачанные первоисточники для верификации |
| `tmp/n2_options/*.json` | 10 MB | **→REPORT** | Артефакты сравнения сценариев |
| `tmp/n2_options/*.db` | 33 MB | **JUNK** | Одноразовые БД прогонов |
| `tmp/*.db` (верхний уровень) | 212 MB | **JUNK** | Одноразовые БД прогонов |
| `tmp/*.json` (выходы проб) | 15 MB | **JUNK** | Транзиентные выходы |
| `tmp/*.png`, `*.log`, `*.db-wal/shm` | ~6 MB | **JUNK** | Временные артефакты |
| `tmp/*.md` | 2 MB | **→REPORT** | Черновики отчётов |

### `research/` верхний уровень — что CORE, что →REPORT

CORE (упомянуты README/tools/CI, правило владельца):
`category_verification.md` (README шаг 7), `reliability-report.md` (README),
`verification_report.json` (README шаг 1), `verification_report.md`,
`game-development-dss-study.md` + `output/pdf/game-development-dss-study.pdf`
(README «Отчёт»), `catalog-coverage-matrix.md` (README «Отчёт»), `packs/`.

→REPORT (весь остальной research): `wave1..wave5-*`, `scenario-*`, `audit-*`,
`defect-diagnosis-*`, `session-report-*`, `spec-compliance-matrix.md`,
`project-scale-*`, `n2-*`, `gpu-spread-*`, `model-floor-*`,
`system-requirements-*`, `task22-*`, `integration-audit-*`, `parameter-audit-*`,
`audit-parameters-*`, `audit_evidence.json`, `RESEARCH_SNAPSHOT.*`, `workqueue/`.

### `tools/` детально

CORE (README runbook / CI / пайплайн паков):
`launch_linux.py`, `smoke_linux_launcher.py` (CI), `verify_sources.py`,
`audit_evidence.py`, `generate_research_report.py`, `check_research_invariants.py`
(README runbook), `md_to_pdf.py`, `repair_dead_links.py` (импортируется
`verify_sources.py`), `gen_pack_tech_nodes.py`, `gen_pack_method_proofs2.py`,
`gen_pack_tool_proofs.py` (генераторы CORE-паков).

→REPORT (одноразовые, ссылки только в research/):
`repair_db.py`, `repair_packs.py`, `repair_verification_findings.py`,
`check_seed_convergence.py`, `dump_digest.py`, `extract_category_evidence.py`.

### Итоги по классам (приблизительно)

| Класс | Размер | Доля |
|---|---|---|
| **CORE** (вкл. env-окружения ~312 MB) | ~333 MB | 22 % |
| **→REPORT** | ~34 MB | 2 % |
| **JUNK** | ~1084 MB | 71 % |
| `.git/` (не трогаем) | 58 MB | 4 % |
| Прочее (misc, округление) | ~13 MB | 1 % |

---

## (b) Cut map: `game_cases`/`case_evidence` и `work_packages`/`team_scenarios`

Полная карта следов. **Ничего не вырезано** — только карта.

### Модели БД

| Файл:строка | Что |
|---|---|
| `backend/app/models/entities.py:460-481` | `GameCase` → таблица `game_cases` |
| `backend/app/models/entities.py:484-505` | `CaseEvidence` → таблица `case_evidence` |
| `backend/app/models/entities.py:552-582` | `WorkPackage` → таблица `work_packages` |
| `backend/app/models/entities.py:585-602` | `TeamScenario` → таблица `team_scenarios` |
| `backend/app/models/__init__.py` | реэкспорт моделей (см. grep) |

### Миграции

| Файл:строка | Что |
|---|---|
| `backend/alembic/versions/20260910_dss_evidence01.py:80-190` | `create_table` всех 4 таблиц |
| `backend/alembic/versions/20260910_dss_evidence01.py:225` | цикл `drop_table` в `downgrade` |
| `backend/alembic/versions/20260911_sync01_model_indexes.py` | индексы моделей |
| `backend/alembic/versions/20260911_wpstagenote01_work_package_stage_note.py` | колонка `work_packages.stage_note` |
| `backend/app/db_migrate.py:87-88` | список «ожидаемых» таблиц схемы |

### Seed-данные

| Файл:строка | Что |
|---|---|
| `backend/app/seed/evidence_catalog.py:17-19` | импорты 4 моделей |
| `backend/app/seed/evidence_catalog.py:580-727` | `CASE_RECORDS` (данные кейсов) |
| `backend/app/seed/evidence_catalog.py:728-762` | `TEAM_RECORDS` (профили команд) |
| `backend/app/seed/evidence_catalog.py:767-814` | `sync_cases` |
| `backend/app/seed/evidence_catalog.py:977-1091` | `sync_work_packages` |
| `backend/app/seed/evidence_catalog.py:1097-1104` | вызовы из `sync_all` |
| `backend/app/seed/pack_loader.py:20-21` | импорты моделей |
| `backend/app/seed/pack_loader.py:333-368` | `_upsert_case` |
| `backend/app/seed/pack_loader.py:554-560` | карта `cases → (game_case, case_code)` |
| `backend/app/seed/pack_loader.py:700-745` | game examples → `GameCase`+`CaseEvidence` |
| `backend/app/seed/pack_loader.py:836-890` | дубль ветки game examples |
| `backend/app/seed/pack_loader.py:915-919` | retire `WP_*` work packages |
| `backend/app/seed/pack_loader.py:632-642` | счётчики `cases/case_evidence/work_packages` |
| `backend/app/seed/seeder.py:22` | импорт моделей |

### Репозитории

| Файл:строка | Что |
|---|---|
| `backend/app/repositories.py:19-20` | импорты моделей |
| `backend/app/repositories.py:113-118` | `snapshot_counts` (4 счётчика) |
| `backend/app/repositories.py:141-146` | `game_cases()` / `game_case()` |
| `backend/app/repositories.py:149-152` | `case_evidence()` |
| `backend/app/repositories.py:164-168` | `work_packages()` |
| `backend/app/repositories.py:171-176` | `team_scenarios()` / `team_scenario()` |

### Сервисы

| Файл:строка | Что |
|---|---|
| `backend/app/services/evidence.py:13-14` | импорты схем |
| `backend/app/services/evidence.py:46-68` | `cases_to_out` |
| `backend/app/services/evidence.py:70-78` | `cases_for_methods` |
| `backend/app/services/evidence.py:105-136` | `practice_check` |
| `backend/app/services/evidence.py:145-168` | `case_count` в сводке |
| `backend/app/services/planning.py` | **весь модуль**: планирование на `WorkPackage`+`TeamScenario` |
| `backend/app/services/planning.py:15,18` | импорты |
| `backend/app/services/planning.py:91-114` | `team_for` |
| `backend/app/services/planning.py:153-183` | `_db_packages` |
| `backend/app/services/planning.py:293-324` | `schedule` |
| `backend/app/services/planning.py:326-360` | `effort_for_methods` |

### API-маршруты

| Файл:строка | Что |
|---|---|
| `backend/app/api/catalog.py:22-23` | импорты `GameCaseOut`, `TeamScenarioOut` |
| `backend/app/api/catalog.py:172-184` | `GET /catalog/cases`, `GET /catalog/cases/{code}` |
| `backend/app/api/catalog.py:212-231` | `GET /catalog/teams` |
| `backend/app/api/recommend.py:11,55-60` | `POST /schedule` |
| `backend/app/api/recommend.py:69` | параметр `team` |
| `backend/app/api/recommend.py:84` | `cases=` в отчёте |
| `backend/app/api/recommend.py:88` | `schedule=` в отчёте |
| `backend/app/api/recommend.py:93-98` | `report_data` (cases/schedule) |

### Pydantic-схемы

| Файл:строка | Что |
|---|---|
| `backend/app/schemas/catalog.py:810-811` | `case_count`, `case_codes` |
| `backend/app/schemas/catalog.py:857-883` | `CaseEvidenceOut`, `GameCaseOut` |
| `backend/app/schemas/catalog.py:932-955` | `WorkPackageOut`, `EffortEstimateOut.packages` |
| `backend/app/schemas/catalog.py:957-967` | `TeamScenarioOut` |
| `backend/app/schemas/catalog.py:969-1008` | `ScheduleTaskOut`, `ScheduleOut` |
| `backend/app/schemas/catalog.py:310` | `ScheduleRequest` |
| `backend/app/schemas/catalog.py:1120` | `practice_check` |
| `backend/app/schemas/catalog.py:1191,1193` | `cases`, `schedule` в `ReportDataOut` |

### Frontend

| Файл:строка | Что |
|---|---|
| `frontend/src/screens/CasesScreen.tsx` | **экран целиком** (кейсы) |
| `frontend/src/screens/ScheduleScreen.tsx` | **экран целиком** (пакеты работ/команды) |
| `frontend/src/screens/PlanScreen.tsx:20,59-99,134-180` | блок планирования/команды |
| `frontend/src/screens/EvidenceScreen.tsx:6,8,14,57-...` | вкладка «Кейсы» |
| `frontend/src/App.tsx:17,19` | импорты экранов |
| `frontend/src/App.tsx:28,30,49,51,103,105,163-168` | nav/роутинг `cases`, `schedule` |
| `frontend/src/api.ts:13,19,22,134,144,155-159` | `cases()`, `teams()`, `schedule()` |
| `frontend/src/types.ts:507-508,601-625,679-732` | `GameCase`, `CaseEvidence`, `TeamScenario`, `Schedule` |
| `frontend/src/components/Evidence.tsx:12,43` | подпись basis `case_evidence` |
| `frontend/src/types.ts:149` | basis-строка `case_evidence` |

### Тесты

| Файл | Что |
|---|---|
| `backend/tests/test_case_publication.py` | публикация кейсов (весь файл) |
| `backend/tests/test_evidence_api.py` | API кейсов |
| `backend/tests/test_pack_reconciliation.py` | сверка паков/кейсов |
| `backend/tests/test_relation_resolutions.py` | связи кейсов |
| `backend/tests/test_scientific.py` | упоминает сущности |
| `backend/tests/test_stage_integrity.py` | упоминает сущности |

### Tools и research

| Файл | Что |
|---|---|
| `tools/audit_evidence.py`, `tools/verify_sources.py`, `tools/generate_research_report.py`, `tools/repair_packs.py`, `tools/extract_category_evidence.py` | оперируют кейсами/пакетами работ |
| `research/` — **37 файлов** | ссылаются на эти сущности (список — в grep-доказательстве ниже) |

Оценка размера следа (код+тесты+данные, без research): ~0.6 MB исходников и
~35 табличных сущностей/маршрутов/экранов. С учётом research-документов —
~40 файлов-упоминаний.

---

## (c) Мёртвый код (с grep-доказательствами)

Метод: AST-разбор всех top-level `def`/`class` в `backend/app` и `tools`
(717 определений), поиск имени по всему дереву (включая собственный файл) с
исключением строки определения. Декораторы (FastAPI-роуты, валидаторы) и
`test_*` исключены как регистрируемые фреймворком. Сервисные модули проверены
отдельно на импорт — все 16 сервисов достижимы.

**Единственный мёртвый кандидат:**

1. `backend/app/logging_setup.py:35` — `log_event(logger, level, message, **fields)`

   Доказательство (grep по всему дереву, исключая node_modules/venv):
   ```
   $ grep -rn "log_event" --include=*.py .
   ./backend/app/logging_setup.py:35:def log_event(...)   # только определение
   ```
   Единственные прочие совпадения — SQLAlchemy-метод `_log_event`
   (`.runtime-packages/sqlalchemy/engine/interfaces.py:2768`), не связанный.

   Вывод: структурный логгер с `extra_fields` был написан, но ни разу не
   подключён — «фикс, который не долетел». Модуль `logging_setup` при этом жив:
   `configure_logging` вызывается из `backend/app/main.py:27`.

**Скрипты без рантайм-ссылок (не «мёртвые», а одноразовые → →REPORT):**
`tools/repair_db.py`, `tools/repair_packs.py`,
`tools/repair_verification_findings.py`, `tools/check_seed_convergence.py`,
`tools/dump_digest.py`, `tools/extract_category_evidence.py` — упоминаются
только в `research/*` и `RESEARCH_SNAPSHOT.md`; в README/CI/`start.bat` их нет.

**Подтверждённо живые (проверено дважды, чтобы не объявить живой код мёртвым):**
- `backend/e2e_server.py` — `frontend/playwright.config.ts:21`.
- `backend/wait_for_services.py` — `start.bat:84`.
- `backend/app/services/targets.py` — импортируется `hardware.py:92`
  (первичный grep по имени модуля давал ложный «0 ссылок»).
- `backend/app/services/transitions.py` — импортируется
  `recommender.py:37`, используется на строках 381-382, 411.
- Все 16 модулей `backend/app/services/*` достижимы.

---

## (d) Упрощения (без изменения чисел модели)

1. **`backend/app/services/hardware.py` (~2900 строк)** — крупнейший модуль;
   содержит десятки приватных хелперов (`_project_scale_factor:765`,
   `_resolution_factor:791`, `_mirror_memory:1757`, `_target_models:2020`,
   `_estimate_install_size:2379` и др.). Разбить на подмодули по подсистемам
   (scale/resolution, memory, targets, storage) с реэкспортом. Числа не меняются
   — только перемещение функций.
2. **Дублирование в `backend/app/seed/pack_loader.py`** — построение
   `case_code = f"CASE_{ex['game']...}"` и вставка `CaseEvidence` повторены
   дважды: `700-745` и `836-890`. Вынести в один хелпер.
3. **Дублирование на frontend**: `PlanScreen.tsx:88-99` и
   `ScheduleScreen.tsx:151-166` независимо вызывают `api.schedule` и рисуют
   таблицу задач (`PlanScreen.tsx:162-179`, `ScheduleScreen.tsx:43-124`).
   Общий хук/компонент уберёт расхождение.
4. **`backend/app/api/admin.py` (~750 строк, 15+ приватных `_helper`)** —
   сгруппировать импорт/валидацию в отдельный модуль `admin_imports.py`.
5. **`backend/app/schemas/catalog.py` (~1200 строк)** — десятки мелких `*Out`;
   сгруппировать по домену комментариями-секциями.
6. **`backend/app/seed/methods_data.py` (~4100 строк)** и
   `tools/generate_research_report.py` (~160 KB) — данные/шаблоны; вынести
   данные в JSON рядом с модулем (читаемость, нулевой риск для чисел).
7. **Мёртвый `log_event`** (`logging_setup.py:35`) — либо подключить, либо
   удалить (см. (c)).
8. **Мёртвая ветка после cut** — строковые литералы basis `case_evidence`
   (`frontend/src/types.ts:149`, `components/Evidence.tsx:43`,
   `pack_loader.py:810`) перестанут быть достижимы; убрать вместе с cut.
9. **`backend/app/seed/evidence_catalog.py`** — инлайн-данные `CASE_RECORDS`
   (580-727) и `TEAM_RECORDS` (728-762) вынести в отдельные модули данных.

---

## (e) Предлагаемая раскладка `report/`

Цель: вне `report/` остаётся только рантайм. `research/packs/` и CORE-документы
research **остаются на месте**.

```
report/
├── README.md                      # что здесь лежит и почему
├── research-docs/                 # исторические исследования (не CORE)
│   ├── waves/                     # wave1..wave5-verification/audit
│   ├── scenarios/                 # scenario-*.md/html
│   ├── audits/                    # audit-*, defect-diagnosis-*, integration-audit-*,
│   │                              #   project-scale-*, parameter-*, gpu-spread-*,
│   │                              #   model-floor-*, system-requirements-*,
│   │                              #   task22-*, n2-*, spec-compliance-matrix.md
│   ├── session/                   # session-report-*, RESEARCH_SNAPSHOT.*
│   └── workqueue/                 # research/workqueue/ целиком
├── probes/                        # tmp/*.py, tmp/*.md, tmp/res/*
│                                  #   (зонды-исследования и первоисточники)
├── tools-once/                    # repair_db.py, repair_packs.py,
│                                  #   repair_verification_findings.py,
│                                  #   check_seed_convergence.py,
│                                  #   dump_digest.py, extract_category_evidence.py
└── artifacts/                     # output/pdf/category-verification.pdf,
                                   #   output/pdf/game-development-dss-study.pdf,
                                   #   tmp/n2_options/*.json
```

Почему так:
- `research-docs/` отделён от `research/packs/` (CORE) — паки остаются
  источником данных рантайма (`pack_loader.py:33`).
- `probes/` сохраняет правило проекта: `tmp/*.py` — база знаний.
- `tools-once/` — скрипты, чьи эффекты уже применены к данным; ценность — в
  воспроизводимости разовых починок.
- `artifacts/` — сгенерированные PDF/JSON, не нужные для запуска.

Остаются вне `report/` (CORE): `backend/`, `frontend/`, `research/packs/`,
CORE-документы research (`category_verification.md`, `reliability-report.md`,
`verification_report.json/md`, `game-development-dss-study.md`,
`catalog-coverage-matrix.md`), CORE-tools, `.github/`, `start.*`, `README.md`,
`.venv/`, `.dss-venv/`, `frontend/node_modules/`.

---

## (f) Список на удаление (JUNK)

| Объект | Размер | Причина |
|---|---|---|
| `research/_mp/` | 466 MB | Внешние первоисточники, воспроизводимы из tools/ (`.gitignore`) |
| `tmp/*.db` (верхний уровень, 39 шт.) | 212 MB | Одноразовые БД прогонов |
| `backend/*.bak-*.db` (+wal/shm, 43 шт.) | 203 MB | Дубликаты живой БД |
| `.runtime-packages/` | 67 MB | Вендоренный site-packages, нигде не импортируется |
| `.git-safety-backup/` | 58 MB | Форензик-копия `.git` (`.gitignore`) |
| `tmp/n2_options/*.db` | 33 MB | Одноразовые БД сценариев |
| `tmp/*.json` (верхний уровень) | 15 MB | Транзиентные выходы проб |
| `.uv-cache/` | 12 MB | Регенерируемый кэш uv |
| `research/_verify_cache/` | 5 MB | Производный кэш (`.gitignore`) |
| `tmp/*.png`, `*.log`, `*.db-wal/shm` | ~6 MB | Временные артефакты |
| `__pycache__/` (вне env) | 4 MB | Байткод |
| `.pnpm-store/` | 1 MB | Регенерируемый кэш pnpm |
| `.pytest_cache/` | 1 MB | Регенерируемый кэш pytest |
| `.workbuddy-ai/` | 1 MB | Состояние агента (`.gitignore`) |
| `output/pdf/game-development-dss-study.bak.pdf` | 0.5 MB | Устаревший дубликат отчёта |
| **ИТОГО** | **~1085 MB** | ~71 % рабочего дерева |

Примечание: после переноса в `report/` суммарный размер `report/` составит
~34 MB; рабочий проект (CORE) — ~333 MB, из которых ~312 MB — это
окружения (`node_modules`, `.venv`, `.dss-venv`), регенерируемые штатным
`start.bat`/`start.sh`.
