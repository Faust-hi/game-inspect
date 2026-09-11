# ПЛАН ВЕРИФИКАЦИИ КАТЕГОРИЙ 1 И 2 — чек-лист параметров

Сопроводительный файл к `HANDOFF.md` (ЧАСТЬ B.3). Цель: дать новому чату
прямое отображение «параметр → где в БД брать доказательства», чтобы
исследование Категорий 1/2 можно было выполнить без повторной разведки и
ничего не потерять.

> Состояние БД на 2026-09-11 (после починки дефекта «невидимые доказательства»):
> `evidence_claims` = 2562 (published 2539), `evidence_sources` = 936 (все
> published), `game_cases` = 155, `case_evidence` = 375, граф: 0 mandatory-циклов.
> Если числа другие — перезагрузить БД по циклу из HANDOFF §B.5.

---

## КАТЕГОРИЯ 1 — технические параметры
Для каждого: **2–3 глубоких исследования-анализа** с конкретными источниками
(статьи / исследования / проекты / видео / гайды / книги / интервью) + выводы,
подкреплённые **примерами из разных игр** (брать из `game_cases`/`case_evidence`,
не выдумывать).

### 1.1 Игровые функции (entity `game_function`, 40 шт., 267 claims)
| Код функции | Где доказательства | Игровые примеры (искать в case_evidence) |
|---|---|---|
| `open_world_streaming` | claims entity=game_function | потоковая сцена (см. game_cases) |
| `crowd_simulation` | claims entity=game_function | — |
| `ray_traced_effects` | claims entity=game_function | DOOM Eternal, Hunt: Showdown |
| `advanced_npc_ai` | claims entity=game_function | Left 4 Dead (AI Director) |
| `large_scale_terrain` | claims entity=game_function | — |
| `procedural_terrain` | claims entity=game_function | — |
| `audio_system` | claims entity=game_function | — |
| `split_screen_rendering` | claims entity=game_function | — |
| `mesh_shaders` | claims entity=game_function | — |
| `dynamic_lighting` | claims entity=game_function | — |
| … (остальные 30) | `GET /api/catalog/evidence?entity=game_function&code=<code>` | по коду метода в case_evidence |

### 1.2 Методы (entity `method`, 124 шт., 1179 claims)
Каждый метод: вытащить `claims` по `entity=method&code=<code>`. Для каждого
метода нужно 2–3 исследования + ≥2 игровых примера (поле `role: direct|
cross_engine` в case_evidence; прямой пример = shipped-тайтл на том же движке).
Примеры методов с богатым покрытием: `virtual_geometry_clusters`,
`hardware_raytraced_gi`, `gpu_compute_culling`, `world_partition_streaming`,
`virtual_shadow_maps`, `temporal_upscaling`, `meshlet_pipeline_adoption`,
`motion_matching`, `client_prediction_reconciliation`, `directstorage_io`,
`ml_frame_generation`, `tickrate_budgeting`.
Объявленные пробелы adoption помечены `adoption_evidence_gap` (честно, не скрывать).

> **Уточнение маппинга (сессия 3).** Ранее здесь были указаны `nanite_geometry`,
> `lumen_gi`, `gpu_driven_rendering` как методы — это **коды `engine_tool`**
> (`ue_nanite`, `ue_lumen`), а не `method`; запрос
> `entity='method'` их не содержит. Соответствующие методы:
> Nanite → `virtual_geometry_clusters`; Lumen-класс GI → `hardware_raytraced_gi` /
> `screen_space_gi`; GPU-driven → `gpu_compute_culling`.

### 1.3 Вариации реализации / движки (entity `engine`, 7 шт., 50 claims)
UE5, Unity, Godot, CryEngine, Source, HeroEngine, (Bevy — reference). Для каждого:
документация вендора (source_type=official_documentation, 317 шт. в реестре) +
сравнительные статьи + примеры проектов.

### 1.4 Инструменты движков (entity `engine_tool`, 70 шт., 580 claims)
`ue_*`/`u_*` (Unreal/Unity), `c_*` (CryEngine, reference-реализации — НЕ игры),
`g_*` (Godot), `s_*` (Source). 52/70 имеют ≥1 прямой пример; 18 — только
перекрёстные; 21 объявил пробел adoption. Для каждого: исследование инструмента
+ прямой shipped-пример (если есть) или честный пробел.

### 1.5 Конфликты зависимостей (таблица `conflicts`, 458 строк, 7 типов)
7 типов связей (graph relation types, spec-проверены в `spec-compliance-matrix.md`):
`dependency` (обязательная), `hard_conflict` (жёсткая несовместимость),
`risk`, `overlap`, `alternative`, `complement`, `unknown`.
Для категории 1: разобрать выборочно 5–10 ключевых конфликтов (напр.
`motion_matching`↔`animation_lod_budget` hard_conflict; `portal_scene_capture_budget`↔
`split_screen_render_budget`; `baked_occlusion_culling`↔`world_partition_streaming`)
с источниками и примерами игр, подтверждающими конфликт или совместимость.

### 1.6 Связки «метод-инструмент» (таблица `method_engine_links`, 473)
Для каждой связки: подтвердить, что метод реализуется заявленным инструментом
(источник в `Method.source_url` + пример игры). 111 связок без URL помечены
`user_defined` (честно).

### 1.7 Technology nodes (entity `technology_node`, 221, 99 claims)
Автономные узлы графа: api/lib/plugin/sdk (NVMe, DX12, SM6, Vulkan, …).
Для каждого: документация/спецификация (source_type=api_specification/
official_documentation) + пример игры, использующей узел.

---

## КАТЕГОРИЯ 2 — параметры проектирования
Для каждого: глубокие исследования + **СОБСТВЕННОЕ исследование проекта с
расчётами** (пример на игре недостаточен для доказательства корректности внутри
проекта). 208 `derived` claims с `formula`+`input_parameters` уже в БД и в
`research/packs/pack_derivations.json`.

### 2.1 Стадии и бюджет (entity `stage_budget`, 56 claims)
Стадии: concept / preproduction / prototype / production / alpha / beta.
Расчёт: множитель позднего внедрения (Бом 1981, `late_introduction_multiplier_x`),
бюджет этапа. Собственное: пересчитать по модели команды проекта; сверить с
work_packages (1794).

### 2.2 Целевые платформы (entity `target_platform`, 24)
pc_windows / pc_linux / console_reference / mobile_reference. Исследование:
ограничения платформы (spec: «non-PC цели не попадают в количественную PC-модель»).
Собственное: проверить, что оценка не применяет PC-числа к консоли/мобайлу.

### 2.3 Масштаб сцены (в `load_profile` + функции `open_world_streaming`/`large_scale_terrain`)
Исследование: потоковая генерация (разные игры). **Собственное (важно):** доказать,
что масштаб сцены меняет **нагрузку/стриминг**, а НЕ стоимость кадра
(см. тест `test_scene_scale_changes_load_not_frame_cost`, mutation-проверен).

### 2.4 Сетевой режим (entity `network_mode`, 33)
single / coop / dedicated_server / p2p / listen_server / mmo_sharded. Исследование:
netcode (Valorant 128 Гц, CS2, L4D). Собственное: сетевой бюджет 26640 Б/с,
период тика 7,8125 мс — пересчитать под целевой tickrate проекта.

### 2.5 Целевые показатели качества и производительности (entity `target_metric`, 56)
frame_budget_ms (16,6667), target_fps, one_percent_low, resolution (pixel ratio 4,0),
quality_level, ram_limit. Собственное: бюджет кадра `1000/fps`, разложение по
подсистемам (raster/rt/compute/…), закон Амдала 2,1053 для параллельного
ускорения.

### 2.6 Риски проекта (entity `risk_factor`, 44)
scope_creep / late_technology_adoption / content_scale_underestimate /
performance_regression / platform_api_breakage / dependency_abandonment.
Исследование: postmortem-ы (source_type=postmortem). Собственное: вероятность/
влияние по метрикам проекта; PERT `(O+4M+P)/6` = 4,6667 чел-дней.

### 2.7 Корзины (baskets) — связано с `method_engine_links` + recommend API
Исследование: как методы группируются в рабочие корзины; hard_conflict не попадает
в корзину (spec-инвариант). Собственное: проверить, что recommend не предлагает
несовместимое.

### 2.8 Профиль нагрузки (entity `load_profile`, 24)
client_runtime / server_runtime / editor_workflow / build_cook /
development_workstation. **Собственное (важно):** область эффекта
(`effect_scope`): серверная экономия не удешевляет клиент (см.
`test_server_effect_does_not_discount_player_pc`); out-of-frame молча не учитывается.

### 2.9 Оборудование (entity `hardware_cpu` 51 / `hardware_gpu` 79)
Benchmarks: PassMark (source_type=hardware_benchmark, 129). Нормализованные
индексы 0..1. Собственное: память 6,12 GiB headroom; required_gpu_index /
required_cpu_index из суммы подсистем.

### 2.10 Итоговый план (entity `work_packages`, 1794)
work_packages со стоимостью; критический путь (longest-path DAG, длина 21);
team size ≠ person-days (38,44 чел-дней независимо от размера команды).
Собственное: пересчитать критический путь и календарь под выбранный профиль
команды (small/large/custom).

---

## ФОРМАТ ИТОГОВОГО ДОКУМЕНТА
`research/category_verification.md`, по одному разделу на параметр:
`Параметр | Источники (коды SRC-*) | Ключевые выводы | Расчёт (formula+inputs) |
Примеры игр | Сверка с планом: ВЫПОЛНЕНО / ТРЕБУЕТ ДОРАБОТКИ`.
Плюс PDF (через `.venv` + `generate_research_report.py` или отдельный билд).

## КАК ВЫТАЩИТЬ ДОКАЗАТЕЛЬСТВА ИЗ БД (примеры)
```python
# из backend/ через .dss-venv
import sys; sys.path.insert(0,'.')
from app.database import SessionLocal
from app.models.entities import EvidenceClaim, EvidenceSource
from sqlalchemy import select
db=SessionLocal()
# все published claims по методу
claims = db.scalars(select(EvidenceClaim).where(
    EvidenceClaim.entity=='method', EvidenceClaim.entity_code=='nanite_geometry',
    EvidenceClaim.status=='published')).all()
for c in claims:
    src = db.get(EvidenceSource, c.source_id) if c.source_id else None
    print(c.code, '|', c.basis, '|', c.formula, '|', src.url if src else None)
```
API: `GET /api/catalog/evidence?entity=method&code=nanite_geometry` →
список с полями `source` (объект), `basis`, `formula`, `input_parameters`, `locator`.
