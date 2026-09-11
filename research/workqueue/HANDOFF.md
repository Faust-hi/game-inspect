# HANDOFF — передача контекста в новый чат

Дата последнего обновления: **2026-09-11 (сессия 3)**. Проект: локальная DSS для
проектирования игр (`C:/Users/user/Desktop/game-inspect`).
Спецификация-источник истины: `F:\Downloads\важно.txt` (рус., 423 строки).

Мандат пользователя: *«продолжи исследование, используй себя как оркестратора,
который контролирует работу другого агента, чтобы он не сбился с верного пути»*
и финальное требование: *«в конце всего ты должен сделать проверку всех
аргументов и параметров … на правдивость и достоверность»*.

> **Как читать этот файл.** `ЧАСТЬ A` — исторический контекст (оркестрация,
> паки, инструменты, принципы), собранный в сессии 1 и сохранённый как основа.
> `ЧАСТЬ B` — **самое важное для продолжения**: что сломалось и было починено
> в сессии 2 (дефект «невидимые доказательства» + 19 циклов в графе),
> верифицированное текущее состояние БД, и статус исследования Категорий 1/2,
> которое ещё НЕ оформлено как документ. `ЧАСТЬ B` supersedes устаревшие
> числа из §2 старого файла.

---

# ЧАСТЬ A — исторический контекст (сессия 1, сохранённый)

## A.1 Оркестрация и контракты
| Файл | Роль |
|---|---|
| `F:\Downloads\важно.txt` | Спецификация (20 разделов отчёта, 124 метода, 40 функций, 7 движков, 70 инструментов, 473 ссылки, 37+ конфликтов, 51 CPU / 79 GPU, P50/P80) |
| `research/workqueue/BRIEF.md` | JSON-контракт для сабагентов: SOURCE / ENTITY / CLAIM / GAME_EXAMPLE + 10 HARD RULES |
| `research/workqueue/q_*.json` | Очереди вопросов (functions/engines/graph/method_proofs) |
| `research/workqueue/HANDOFF.md` | Этот файл |

## A.2 Пакеты доказательств (`research/packs/`, 14 шт.)
| Пакет | Что покрывает |
|---|---|
| `pack_functions.json` | 40 игровых функций |
| `pack_engines_ue_unity.json` | Движки UE/Unity, инструменты ue_*/u_* |
| `pack_tools_godot_cry_source.json` | Godot / CryEngine / Source инструменты |
| `pack_tools_heroengine.json` | HeroEngine |
| `pack_rendering.json` | Рендер-методы |
| `pack_netaudio.json` | Сеть и аудио |
| `pack_ai_sim.json` | AI и симуляция |
| `pack_character_content.json` | Персонажи и контент |
| `pack_world_streaming.json` | Стриминг мира |
| `pack_derivations.json` | **Расчётные домены (собственное исследование): стадии, бюджет, нагрузка, hardware, сети — с `formula`+`input_parameters`** |
| `pack_method_proofs.json` | Вторые игровые примеры для методов |
| `pack_method_proofs2.json` | +57 примеров, 36 методов, 2 объявленных пробела |
| `pack_tech_nodes.json` | 20 автономных technology_nodes (api/lib/plugin/sdk) |
| `pack_tool_proofs.json` | 60 примеров для 37 инструментов + 21 объявленный пробел adoption |

## A.3 Инструменты (`tools/`) — см. §B.4 про рантаймы
| Файл | Назначение / ключевые правки сессии 1 |
|---|---|
| `tools/verify_sources.py` | Механическая проверка паков и БД + HTTP-достоверность URL. Правки: регистрозависимость URL (`url_original`), кросс-паковая резолвция (`all_source_codes`), `DECLARED_GAP_FIELDS`, колонки БД: `conflicts`/`dependency_edges` без `code` → `id` |
| `tools/audit_evidence.py` | Аудит покрытия: ≥3 claims, ≥2 источника с локатором, ≥2 игровых примера. `declared_gaps` по всем сущностям; direct vs cross_engine |
| `tools/gen_pack_tech_nodes.py` / `gen_pack_method_proofs2.py` / `gen_pack_tool_proofs.py` | Генераторы паков; `classify()` → `role: direct|cross_engine`; `gap_claim()` — объявленные пробелы (`source: null`) |
| `tools/repair_dead_links.py` | Замена/объявление недоступных URL (никогда не выдумывать) |
| `tools/repair_verification_findings.py` | Закрывает находки верификатора; реклассификация `derived`-без-формулы → `unknown`/`documented` |
| `tools/generate_research_report.py` | Генератор отчёта (MD + PDF + matrix). PDF требует `reportlab` из `.venv`, НЕ из `.dss-venv` |

## A.4 Выходные артефакты (сессия 1)
| Файл | Содержимое |
|---|---|
| `research/game-development-dss-study.md` | Отчёт, 20 разделов |
| `output/pdf/game-development-dss-study.pdf` | PDF (~104 стр.), кириллица ок |
| `research/reliability-report.md` | Итоговый отчёт о достоверности (финальное требование мандата) |
| `research/verification_report.json` / `.md` | HTTP-проверка всех URL |
| `research/audit_evidence.json` | Полный аудит покрытия |
| `research/catalog-coverage-matrix.md` | Матрица покрытия каталога |
| `research/spec-compliance-matrix.md` | **Построчный аудит спеки: 234 пункта, 234 ВЫПОЛНЕНО / 0 не выполнено / 0 требует уточнения** |

## A.5 Ключевые принципы (не нарушать!)
1. **Отсутствие источника ≠ совместимость.** Нет доказательства → запись-пробел
   `field='adoption_evidence_gap'`, `basis='unknown'`, `evidence_level='low'`, `source=None`.
2. **`derived` требует формулу + входные параметры.** Качественное рассуждение — это
   `documented` или `unknown`, не `derived`.
3. **Никогда не выдумывать URL.** Замена только на пробитый 2xx-эквивалент;
   иначе — честная пометка недоступности.
4. **Прямой vs перекрёстный пример.** `ue_*`/`u_*`/`c_*` — семейство движка из префикса;
   пример с другого движка доказывает возможность, НЕ adoption инструмента.
5. **Reference-реализации (Godot/Bevy/The Forge/mimalloc) — не игровые примеры.**
6. **Регистр URL важен** (Wikipedia, docs.unity3d.com, learn.microsoft.com): дедуп — без
   учёта регистра, проба — с оригиналом.
7. **403/429 = бот-стена (protected), не «мёртвая» ссылка.** 502/tunnel = сетевая ошибка прокси.

---

# ЧАСТЬ B — текущее состояние и что делать дальше (сессия 2)

## B.1 ЧТО БЫЛО НАЙДЕНО И ИСПРАВЛЕНО В ЭТОЙ СЕССИИ

### B.1.1 Дефект №1 — «невидимые доказательства» (самый критичный)
**Симптом.** Свежая загрузка (`seed_all`) создавала только **438 claims**, хотя
повторный `sync_packs` давал **2562**. То есть 2124 утверждения (98,8 %) были
`draft` и не попадали ни в API `/api/catalog/evidence`, ни в отчёт, ни в PDF.
Целые семейства были полностью невидимы: `engine_tool` (580), `engine` (50),
`technology_node` (99), и все шесть семейств Категории 2 (237).

**Коренная причина.** В `backend/app/seed/pack_loader.py` в `_upsert_claim`
стояло `status=DRAFT` всегда, когда у claim не было *внутрипакетного*
локального источника. Но spec line 412 прямо требует: *«запись без
обязательного источника не публикуется»* — то есть публикуется ВСЁ, что
источник ИМЕЕТ. 98,8 % паковых claims источник содержат, значит должны быть
`published`.

**Фикс.** `status = PUBLISHED if src is not None else DRAFT` в `_upsert_claim`
(оба места: основное и case_evidence). Бэкфил: 2101 claim + 364 case_evidence
переведены в published. Публичных claims: **438 → 2539**.

### B.1.2 Дефект №2 — источники-черновики обнуляли ссылку
**Симптом.** Даже у published claim в ответе API поле `source` было `null`.

**Коренная причина.** `EvidenceSource(**payload)` по умолчанию получал
`status='draft'` (модельный дефолт). `source_to_out()` возвращает `None` для
не-published источника. Итого **646 из 935** источников были draft → ссылка
обнулялась, и published claim выглядел как «без источника» (ложное нарушение
того же правила line 412).

**Фикс.**
- `backend/app/seed/pack_loader.py`: `EvidenceSource(..., status=PUBLISHED)` при
  создании из пакета.
- `backend/app/seed/fixes_v2.py`: PassMark-источник тоже `status="published"`.
- `backend/app/seed/corrections.py`: новая `correct_source_publication(db)` —
  публикует только те источники, на которые уже ссылается published claim/fact
  (для уже существующих БД; иначе фикс проявился бы только при пересоздании).
- `backend/app/seed/seeder.py`: подключена `correct_source_publication`; в
  `validate_knowledge_base` добавлено предупреждение, когда published claim
  ссылается на draft-источник (ловит этот класс дефекта в будущем).

### B.1.3 Дефект №3 — 19 циклов обязательных зависимостей в графе
**Симптом.** `GET /api/catalog/graph-checks` возвращал `cyclic_mandatory` ×
19 (ошибка). Цикл обязательной зависимости неразрешим: ни один метод в нём
нельзя поставить в план.

**Коренные причины (две).**
1. **Повторная загрузка паков** (добавленная чтобы устранить дефект №1)
   заново создавала method→method связи, часть которых — взаимные обязательные
   зависимости (`A requires B` И `B requires A`). `break_dependency_cycles`
   понижал строку `Conflict`, но `sync_dependency_graph` уже материализовал
   ОБА ребра как `mandatory` в `dependency_edges`, а цикл-брейкер не трогал
   `dependency_edges` — поэтому проверка графа продолжала видеть цикл.
2. **Дубликаты в обратном порядке.** «A complements B» из одного пакета и
   «B complements A» из другого создавали две строки об одном и том же
   отношении; брейкер понижал только одну, вторая продолжала требовать
   взаимности.

**Фиксы.**
- `backend/app/seed/pack_loader.py`: `_upsert_relation` теперь детектирует
  симметричный дубликат по обратной паре для `complement/alternative/
  hard_conflict/risk` (`_SYMMETRIC_RELATIONS`).
- `backend/app/seed/dependency_graph.py`: `break_dependency_cycles` теперь
  вызывает `_follow_edge_demotion` — понижает/удаляет и материализованное ребро
  графа в соответствии с пониженной связью.

**Результат.** Граф ацикличен: осталась только 1 `info`-уровня проблема
(`version_unknown` — отсутствие версии движка в анкете, штатная), 0 ошибок,
0 mandatory-циклов.

### B.1.4 Тесты бэкенда: 76 → 86 passed
- 7 регрессионных падений от convergence-прохода **устранены** (defects №1–№3).
- Ещё 5 падений оказались **предсуществующими на чистом baseline** (до моих
  правок) и вызваны *корректным* поведением гейтинга зависимостей, которое
  тесты не учитывали. Исправлены сами тесты (не продакшн-код):
  - `backend/tests/test_combined_effects.py`: добавлена `with_prerequisites()`
    — транзитивное замыкание обязательных предусловий (напр.
    `hardware_raytraced_gi → selective_ray_traced_effects → ...`,
    `heightmap_compression → build_size_startup_budgets → directstorage_io → ...`);
    в профили добавлены требуемые функции (`ray_traced_effects`,
    `dynamic_lighting`, `procedural_terrain`). В `test_frame_generation_*` сравнение
    переведено на подсистему «Генерация кадров» (поле и карточка начисляют
    синтез один раз, не дважды — что и проверяет тест; растр меняется из-за
    `temporal_upscaling`, законного предусловия карточки).
  - `backend/tests/test_engine_versions.py`: `test_directstorage_needs_windows_and_modern_api`
    теперь подставляет предусловия (`async_loading_pipeline`,
    `terrain_generation_streaming_budget`) и функцию `procedural_terrain`, чтобы
    измерять платформенное условие, а не срабатывание правила зависимостей.
  - `backend/tests/test_evidence_publication.py`: поле ответа — `source`
    (объект), а не `source_id`; derived-утверждение валидно при
    `source OR (formula AND input_parameters)` — в точности по spec line 412.

## B.2 ВЕРИФИЦИРОВАННОЕ ТЕКУЩЕЕ СОСТОЯНИЕ БД (production `backend/gamedev_dss.db`, пересобрана 2026-09-11)

Получено прямым запросом к пересобранной БД (не из самоотчёта):

```
functions        40      methods           124     engines            7
engine_tools      70      method_engine_links 473    conflicts         458
hardware          130     game_cases         155     case_evidence     375
work_packages    1794     technology_nodes   221

evidence_claims   2562  (published 2539, draft 23 — 23 это source-less, честно)
evidence_sources  935   (ALL published 935)
dependency_edges  929   (mandatory 164)

graph_checks: edges 929, nodes 221, mandatory_edges 164,
              issues = 1 (info: version_unknown), errors = 0, cyclic = 0
```

**Распределение claims по `entity` (где искать доказательства для Категорий):**
| entity | claims | | entity | claims |
|---|---|---|---|---|
| method | 1179 | | stage_budget | 56 |
| engine_tool | 580 | | target_metric | 56 |
| game_function | 267 | | hardware_cpu | 51 |
| technology_node | 99 | | engine | 50 |
| hardware_gpu | 79 | | risk_factor | 44 |
| | | | network_mode | 33 |
| | | | load_profile | 24 |
| | | | target_platform | 24 |
| | | | research | 20 |

**Распределение claims по `basis`:** documented 1580 · case_evidence 244 ·
unknown 239 · derived 208 · expert_estimate 164 · measured 104.

**Источники по типу (935):** official_documentation 317 · secondary 311 ·
hardware_benchmark 129 · conference_talk 39 · open_source 33 · book 26 ·
engineering_blog 21 · vendor_press_release 14 · + ещё ~20 типов (interview 5,
api_specification 5, academic_paper 5, standard 4, postmortem 1, …).

**Это состояние — надёжный фундамент.** До сессии 2 оно было ложным
(98,8 % claims invisible), поэтому любой анализ «по базе» в сессии 1 мог опираться
на пустоту. Теперь `GET /api/catalog/evidence` отдаёт реальные 2539 published
claims с заполненным `source`.

## B.3 ИССЛЕДОВАНИЕ КАТЕГОРИЙ 1 И 2 — СТАТУС: **ВЫПОЛНЕНО** (сессия 3)

> **ОБНОВЛЕНО 2026-09-11 (сессия 3).** Сводный документ создан:
> `research/category_verification.md` (+ PDF
> `output/pdf/category-verification.pdf`, 16 стр.). Фундамент данных
> перепроверен по §B.5: 2539 published claims / 935 published sources,
> 0 mandatory-циклов, тесты green. Пройдены все 17 параметров
> (Категория 1: 1.1–1.7; Категория 2: 2.1–2.10): **17/17 ВЫПОЛНЕНО**.
> **Пробелы деклараций устранены** (были: 111 связок без URL, 30 конфликтов
> без URL, 24 ребра без декларации, пустой `benchmark_raw_value` у 51/79
> железа, 3 висячих derived-claim). Причина — проходы нормализации в
> `seed_methods` шли раньше создания инструментов/связей/железа; добавлена
> `corrections.declare_evidence_gaps()`, вызываемая последней в `seed_all`.
> Аудит теперь: `method_engine_links pct_ok 100 %`, `conflicts undeclared 0`,
> `dependency_edges undeclared 0`, `benchmark_raw_value 0 пустых`,
> `dangling claims 0`. Тесты: **86 → 91 passed** (новый
> `tests/test_evidence_declarations.py`, 5 тестов, mutation-проверены).
> Извлечение и живые расчёты: `tools/extract_category_evidence.py`,
> `tools/dump_digest.py`, `tools/md_to_pdf.py`.
> Ниже — исторический контекст сессии 2 (сохранён).

Это была **основная незавершённая задача** (запрос пользователя: «проверь выполнение
условий из плана … две категории параметров … для каждого параметра укажи:
источники, ключевые выводы, расчёты, примеры из игр … сверь с пунктами плана»).

Готово: **фундамент данных** (B.2). Не готово: **сводный документ по параметрам**.
План параметров и где брать по ним доказательства — в
`research/workqueue/CATEGORY_VERIFICATION_PLAN.md` (создан вместе с этим файлом).

### B.3.1 Категория 1 — технические параметры (нужны глубокие исследования + игровые примеры)
Для каждого параметра: 2–3 глубоких исследования-анализа с конкретными
источниками (статьи/исследования/проекты/видео/гайды/книги/интервью) + выводы,
подкреплённые примерами из **разных** игр.
- Параметры → сущности БД: `method` (124 метода, 1179 claims), `engine_tool`
  (70, 580 claims), `engine` (7, 50 claims), `technology_node` (221, 99 claims),
  `game_function` (40, 267 claims), `conflicts` (458 строк, 7 типов связей:
  dependency / hard_conflict / risk / overlap / alternative / complement / unknown),
  `method_engine_links` (473 связки «метод-инструмент»).
- Игровые примеры уже в БД: `game_cases` (155) + `case_evidence` (375). Это
  курируемая подборка (L4D, CS2, Valorant, It Takes Two, DOOM Eternal,
  Hunt: Showdown, потоковая сцена, процедурная генерация и др.) — брать оттуда,
  не выдумывать.

### B.3.2 Категория 2 — параметры проектирования (нужны НЕ ТОЛЬКО исследования, но и СОБСТВЕННОЕ исследование с расчётами)
Для каждого параметра: глубокие исследования + **собственное исследование
проекта, подкреплённое расчётами и дополнительными доказательствами**
(пример на игре не является достаточным доказательством корректности внутри
проекта).
- Параметры → сущности БД: `stage_budget` (56), `target_metric` (56),
  `load_profile` (24), `network_mode` (33), `risk_factor` (44),
  `target_platform` (24), `hardware_cpu` (51), `hardware_gpu` (79),
  `work_packages` (1794, итоговый план).
- **Собственное исследование уже есть как 208 `derived` claims** с `formula` +
  `input_parameters` (в БД и в `research/packs/pack_derivations.json`). Ключевые
  расчёты (независимо перепроверены в сессии 2, совпали с БД):
  - Бюджет кадра: `frame_budget_ms = 1000 / target_fps` → 16,6667 мс при 60 fps.
  - Pixel ratio: `render_px / reference_px` → 4,0 (4K vs 1080p).
  - Закон Амдала: `1 / ((1-p) + p/s)` → 2,1053 (p=0,9, s=8).
  - Сетевой бюджет: 26640 Б/с (bandwidth derivation).
  - Период тика сервера: 7,8125 мс (128 Гц).
  - Память: 6,12 GiB (headroom derivation).
  - PERT: `(O+4M+P)/6` → 4,6667 чел-дней.
  - Критический путь: длина 21 (longest-path DAG).
- Команда: инвариант «team size влияет на календарь, но НЕ на person-days»
  проверен живьём: effort = 38,44 чел-дней при любом размере команды, календарь
  падает 37,92 → 5,79 дней (solo → large).

### B.3.3 Формат итогового документа (рекомендованный)
`research/category_verification.md` (+ PDF через `generate_research_report.py`
или отдельный билд), по одной таблице/разделу на параметр:
`Параметр | Источники (коды SRC-*) | Ключевые выводы | Расчёт (где применимо) |
Примеры игр | Сверка с планом: ВЫПОЛНЕНО / ТРЕБУЕТ ДОРАБОТКИ`.

## B.4 РАНТАЙМЫ (не перепутать!)
- Инструменты паков: системный `python` / managed `3.13.12`.
- Бэкенд/аудит (SQLAlchemy 2.0): `C:/Users/user/Desktop/game-inspect/.dss-venv/Scripts/python.exe`
- **PDF-сборка требует `reportlab` из `.venv`** (`C:/Users/user/Desktop/game-inspect/.venv/Scripts/python.exe`),
  НЕ из `.dss-venv` (там нет reportlab).
- Импорт БД: `from app.database import SessionLocal`, запускать из `backend/`.
- API-ответ claims: поле `source` — **объект** (`{code,title,url,...}`) или `null`,
  НЕ числовой `source_id`.

## B.5 ТИПОВОЙ ЦИКЛ ОРКЕСТРАТОРА (для продолжения)
```
# 0. Бэкап БД перед любой перезагрузкой
cd backend && cp gamedev_dss.db gamedev-dss.bak-$(date +%Y%m%d-%H%M%S).db

# 1. Проверить паки без сети
python tools/verify_sources.py --packs-only --no-net

# 2. Перезагрузить БД (из backend/, через .dss-venv)
./../.dss-venv/Scripts/python.exe -c "
import sys; sys.path.insert(0,'.')
from app.database import Base, SessionLocal, engine
from app.seed import seeder
Base.metadata.create_all(bind=engine)
s=SessionLocal(); print(seeder.seed_all(s, validate=True)); s.commit()"

# 3. Аудит покрытия
cd .. && ./.dss-venv/Scripts/python.exe tools/audit_evidence.py

# 4. Полная проверка с сетью (~4 мин)
python tools/verify_sources.py

# 5. Граф-инварианты (обязан быть 0 mandatory-циклов)
./../.dss-venv/Scripts/python.exe -c "
import sys; sys.path.insert(0,'.')
from app.database import SessionLocal
from app.services.graph import graph_checks
db=SessionLocal(); r=graph_checks(db)
print([i['check'] for i in r['issues']])"

# 6. Прогон тестов (ожидается 86 passed)
cd backend && ../.dss-venv/Scripts/python.exe -m pytest -q

# 7. Перегенерация отчёта (PDF — через .venv)
cd .. && ./.venv/Scripts/python.exe tools/generate_research_report.py
```
Правило оркестратора: **не верить самоотчётам агентов** — только механическая
проверка схемы + HTTP-проба + аудит покрытия + graph_checks. Всё, что агент
заявил, перепроверять инструментом.

## B.6 УРОКИ СЕССИИ 2 (критично для продолжения)
- **Дефект «невидимые доказательства» был маскировщиком**: до его починки
  `audit_evidence` и любой анализ «по БД» работали по ~1 % данных. Если новый чат
  видит мало claims — первым делом проверить `status='published'` в
  `evidence_claims` (ожидается 2539) и `status='published'` в `evidence_sources`
  (ожидается 935). Если меньше — перезагрузить БД по циклу B.5.
- **Convergence-проход в `seed_all` хрупок**: вторая `sync_packs` нужна, чтобы
  паки, ссылающиеся на сущности из более поздних разделов, не терялись. Не
  удалять её без замены на идемпотентную догрузку по первому проходу.
- **Цикл-брейкер и граф-ребра — две разные таблицы**: понижение `Conflict` не
  трогает `dependency_edges`. Любое изменение гейта публикации claims/sources
  обязано сопровождаться проверкой `graph_checks` на 0 mandatory-циклов.
- **Тесты, падающие на baseline, — не регрессия продакшна**: перед починкой
  дефекта через `git stash` убедиться, что падение не предсуществовало.
- **Сеть песочницы через прокси** `127.0.0.1:<port>`: `502`/`403`/`429` — среда,
  не мёртвые ссылки. Спорные URL перепроверять независимо.

## B.7 ЧТО ДЕЛАТЬ В НОВОМ ЧАТЕ (пошагово, чтобы ничего не потерять)
1. Прочитать `ЧАСТЬ A` + `ЧАСТЬ B` этого файла целиком.
2. Проверить состояние БД по B.5 шаг 0–5 (ожидается: 2539 published claims,
   935 published sources, 0 mandatory-циклов, 86 тестов green). Если расходится —
   перезагрузить по B.5.
3. Взять `research/workqueue/CATEGORY_VERIFICATION_PLAN.md` как чек-лист
   параметров. Для каждого: вытащить claims из БД (`GET /api/catalog/evidence`
   или прямой запрос), написать 2–3 глубоких исследования с конкретными
   источниками, добавить игровые примеры (из `game_cases`/`case_evidence`).
4. Для Категории 2: явно выписать расчёт (формула + входные из `pack_derivations`
   или пересчитать самим) и сделать дополнительный анализ проекта (напр.
   пересчёт инварианта команды, влияние масштаба сцены на нагрузку, а не на
   стоимость кадра — см. тест `test_scene_scale_changes_load_not_frame_cost`).
5. Сверить каждый параметр с пунктами плана; зафиксировать ВЫПОЛНЕНО /
   ТРЕБУЕТ ДОРАБОТКИ.
6. Оформить `research/category_verification.md` (+ PDF) и обновить этот HANDOFF
   (раздел B.3 → «ВЫПОЛНЕНО»).
7. Финально: перекрестная проверка аргументов на правдивость (мандат) —
   HTTP-проба URL, mutation-проба инвариантов, сопоставление с
   `spec-compliance-matrix.md`.
