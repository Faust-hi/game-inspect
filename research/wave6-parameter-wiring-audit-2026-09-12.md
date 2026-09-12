# Волна 6: аудит проводки параметров модели — 2026-09-12

Учебный MVP. Единственный критерий — правдоподобность чисел железа. Отчёт отвечает
на вопрос: **какой параметр где читается, что он реально меняет, и что из этого —
дефект, объявленный пробел или незакрытая связь.**

Метод — измерение, а не чтение глазами:

1. **Инвентарь чтений** (`tmp/wave6_params_inventory.py`, AST-разбор `backend/app`):
   для каждого поля `ProjectProfile` — сколько раз и в каком сервисе оно читается
   (`profile.<field>`, `baseline.profile.<field>`, `getattr(profile, "<field>")`).
2. **Свип в двух контекстах** (`tmp/wave6_params_sweep.py`): каждое поле прогоняется
   по всему диапазону при фиксированных остальных, затем сравниваются выходы.
   * контекст **A** — минимальный профиль, пустая корзина (базовая проводка);
   * контекст **B** — включены условные ветви (мультиплеер, физика, AI, толпа, аудио,
     split-screen, генерация кадров, DLSS, streaming pool, draw-call budget) и
     непустая корзина из 14 реальных рекомендаций.
   Сравниваются: 4 числа (`required_gpu_index`, `required_cpu_index`,
   `estimated_ram_gb`, `estimated_vram_gb`), классы GPU/CPU, `reference_gpu`,
   `bottleneck`, `recommended_storage`, профиль нагрузки (6 полос), порядок и баллы
   TOPSIS, план (p50/календарь/задачи/critical path), счётчики risks/excluded/
   unmet/caveats/target_assessments.
3. **Точечные прогоны** (`tmp/wave6_params_targeted.py`, `tmp/wave6_params_control.py`):
   условные CPU-параметры на профиле с доминирующей параллельной нагрузкой; пределы;
   `size_limit_gb`; точные числа сцены; ловушки; чувствительность множителя
   разрешения (инъекция в память, файлы не менялись).
4. Контрольный AST: `name` не читается нигде; `_AUDIO_CPU_LOAD` больше не существует.

**Границы.** Это дополняет, а не повторяет `research/parameter-audit-2026-09-12.md`,
`research/audit-parameters-2026-09-12.md`, `research/wave4-proposal-verification-2026-09-12.md`.
Новое здесь: (а) поимённый вердикт по всему списку из постановки, включая уровни и
точные числа сцены, и (б) измеренные дельты, которых в тех отчётах не было
(чувствительность множителя разрешения, `managed`, независимость плана, точная
цена знаковой ошибки). База не изменялась: работа шла на копии `tmp/wave6_audit.db`.

---

## 0. Как читать таблицу

* **Где читается** — `сервис:строка`, в скобках число прямых чтений за сервис
  (из `tmp/wave6_params_inventory.json`).
* **Что меняет (измерено)** — какие выходы сдвинулись при свипе. Сокращения:
  `4Ч` — хотя бы одно из четырёх чисел; `GPU`/`CPU` — класс, `ref` — ориентир,
  `bn` — bottleneck, `st` — рекомендуемый накопитель; `нагр` — полосы профиля
  нагрузки; `ранг` — баллы/порядок TOPSIS; `план` — расписание; `текст` — только
  оговорки/предупреждения/списки.
* **Вердикт**: `OK` — меняет числа; `OK-усл` — меняет числа только во включающем
  контексте; `только ранг`; `объявлено-но-мертво`; `дефект`; `не учтено`.

---

## 1. Полная таблица параметров

### 1.1. Поля профиля (49)

| Параметр | Где читается | Что меняет (измерено) | Вердикт | Доказательство |
|---|---|---|---|---|
| `name` | нигде (0) | ничего | объявлено-но-мертво | AST: 0 чтений в `backend/app/**` |
| `format` | hardware:940; rules:110,113 | A: ранг/список рекомендаций; B: **4Ч, CPU, ref, нагр** — но только через состав корзины | не учтено (2D) | 2D=2.5D=3D дают одинаковые 4 числа при фикс. корзине (`control`) |
| `world_type` | hardware:947; recommender:166; rules:116,118 | `ram`, `vram`, `st`, gaps, ранг | OK | A: ram/vram/storage/rank сдвинулись |
| `scale` | hardware:914,938,940,997; recommender:236; rules:335,340 | `4Ч`(ram/vram), `st`, draw_calls, ранг | OK | A: 7 ключей, B: 15 |
| `project_scale` | hardware:772 | только `ram` (базис памяти) | OK | A: ram 13.1→16.6; B: ram 14.3→17.8 |
| `stage` | recommender:141,255,451,452,478,516,588,830,832; planning:314; rules:186; transitions:146 | только ранг/баллы + текст/риски | только ранг | A: scores,n_risks; B: caveats,n_risks,scores |
| `engine` | rules:122; targets:142; recommender:275,851; transitions:43,44; engines:1; recommend.py:5 | только ранг/список (косвенно, через применимость методов корзины) | только ранг (косвенно) | B: gaps,n_excluded,n_rec,scores; 4 числа не двигались в измеренной корзине |
| `engine_version` | recommender:273; transitions:44; engines:100; serializers | только текст (gaps, risks) | объявлено-но-мертво (для чисел) | B: gaps 8→10, n_risks 2→3 |
| `platforms` | hardware:875; recommender:246,353; rules:128,143,149; targets:132; transitions:57 | `4Ч`, классы, `ref`, unmet | OK | A: 13 ключей, B: 12; не-PC цель отсекает подбор |
| `object_count_level` | hardware:925,999,1000 | `4Ч`(ram/vram), нагр, draw_calls | OK | A: 12 ключей |
| `object_count` | hardware:925,999,1083 | `4Ч`, нагр, draw_calls | OK | 0→5e6: content 0.96→1.35, ram 14.9→17.8, vram 8.6→10.9 |
| `npc_count_level` | hardware:926,1001,1002; recommender:195 | `4Ч`, нагр, draw_calls, risks | OK | A: 10 ключей |
| `npc_count` | hardware:926,1001,1084 | `4Ч`, нагр, draw_calls | OK | 0→5e5: ram 14.8→17.5, vram 8.5→10.7 |
| `player_count` | hardware:1230,1112,1995,etc; recommender:205,210 | `cpu_par_cost`, `rcpu`(усл.), risks, ранг | OK-усл | параллельный профиль: rcpu 0.3981→0.4026, насыщение на 32 |
| `multiplayer` | hardware:1229,1859,1992,2283,2288,1021; recommender:205,216; rules:101,169 | `cpu_par`, `load_cpu`, ранг | OK-усл | параллельный профиль: rcpu 0.336→0.4026 (+19.8 %) |
| `local_view_count` | hardware:1067,1068,1117,1119,1254 | `4Ч`, `bn`, draw_calls, нагр | OK | B: 14 ключей |
| `functions` | hardware (19 чтений); recommender:6; rules:1; transitions:2 | `4Ч`, нагр, ранг, draw_calls | OK | 40 функций, каждая через `FEATURE_*_SUBSYSTEM_LOAD` |
| `target_resolution` | hardware:1278,1696,1875,1958; recommender:226 | `4Ч`, `GPU`, нагр, `ref` | дефект (множитель) | 2160p: rgpu 0.4644 (фактор 3.0) → 0.6066 при 4.0 (+30.6 %) |
| `target_quality` | hardware:1279,1697,1959; recommender:226 | `4Ч`(ram/vram), `GPU`, нагр, `ref` | OK | A: 7 ключей |
| `target_fps` | hardware:1097,1762,1781,1805; recommender:246 | `4Ч` линейно, `CPU`/`GPU`, `ref` | OK | 30→240: rgpu/rcpu ровно ×2/×4 |
| `render_api` | hardware:608,861,1260,1303,1877; rules:176,178,180; targets:143 | `rcpu`(усл. seq), `rgpu`, `cpu_seq`, `load_cpu` | OK | A: rcpu 0.2666(auto)→0.2942(dx9); dx12==auto (auto→dx12 на Windows) |
| `storage_type` | hardware:940,1003,1262,2658; rules:— | `cpu_par`/`load_cpu`; `rcpu`(усл.) | OK-усл | параллельный профиль: rcpu 0.4039(hdd)→0.4026(nvme) |
| `memory_model` | hardware:993,995,1723,1820,1911,1943,2462 | `ram`, `vram`, `bn`, текст | дефект (managed) | auto==dedicated==managed (0.1802,0.3057,14.6,8.9); unified: ram 14.6→22.4 |
| `upscaling_method` | hardware:863,1345,1349,1356,2491 | `rgpu`, `gpu_raster`, `ref` | OK | rgpu: auto 0.507 → dlss 0.3772 (−25.6 %) |
| `network_topology` | hardware:106,1021,1232,1234; rules:171,173 | `cpu_par`, `rcpu`(усл.), список методов | OK-усл | параллельный профиль: rcpu 0.4026→0.4079 (lockstep) |
| `frame_generation` | hardware:1030,1785,1881,2296 | `rcpu`, `rgpu`, нагр | OK | B: 10 ключей |
| `base_render_fps` | hardware:1032,1098,1785,1786 | `rcpu`, `rgpu`, нагр | OK-усл | B: 9 ключей (только при `frame_generation=True`) |
| `streaming_pool_gb` | hardware:1005,1660,1662,1707,1711 | `ram`, `vram`, `bn`, `ref` | OK | B: 8 ключей |
| `draw_call_budget` | hardware:1007,2666,2669 | только caveats | объявлено-но-мертво | A/B: меняется только число оговорок; 500/5000/50000 — числа те же |
| `simulation_radius_m` | hardware:1011,1245,1248 | `cpu_par`, `rcpu`(усл.), `load_cpu`, ранг | OK-усл | параллельный профиль: rcpu 0.4009→0.4367 (+8.9 %) |
| `physics_tick_hz` | hardware:1015,1844,1845,2005 | `rcpu`, `CPU`, `bn`, нагр | OK | параллельный профиль: rcpu 0.383→0.756 при 15→240 Гц |
| `audio_complexity` | hardware:1019,1241,1242,1702,1703,2367,2368 | `cpu_par`, `rcpu`(усл.), `ram`, install | OK-усл | параллельный профиль: rcpu 0.3851(None)→0.4026(high); ram 14.6→15.3 |
| `target_1_percent_low_fps` | hardware:1133 | только счётчик `target_assessments` | объявлено-но-мертво | свип: единственный сдвиг — `assess` |
| `max_startup_seconds` | hardware:1134 | то же | объявлено-но-мертво | то же |
| `max_streaming_latency_ms` | hardware:1135 | то же | объявлено-но-мертво | то же |
| `max_save_seconds` | hardware:1136 | то же | объявлено-но-мертво | то же |
| `target_network_latency_ms` | hardware:1137 | то же | объявлено-но-мертво | то же |
| `target_server_tick_hz` | hardware:1138 | то же | объявлено-но-мертво | то же |
| `max_network_kbps` | hardware:1139 | то же | объявлено-но-мертво | то же |
| `ram_limit_gb` | hardware:236,240,2445,2469; recommender:236,240,317 | `bn`, unmet, risks; **числа не клампятся** | дефект контракта | limit 4→32: ram=18.9 неизменно |
| `vram_limit_gb` | hardware:2444,2468,2647 | `bn`, unmet; **числа не клампятся** | дефект контракта | limit 2→24: vram=19.5 неизменно |
| `size_limit_gb` | hardware:2309,2313,2333; rules:100,161,162 | список методов; `4Ч` — косвенно | OK-усл | при limit<2 и методе с impact_disk≥2: rcpu 0.3625→0.4026 |
| `deadline_weeks` | recommender:317,322,326,335 | только risks | объявлено-но-мертво (для чисел) | A: 0; B: только n_risks |
| `complexity_tolerance` | rules:155,157,222 | список рекомендаций, ранг; **в железо не идёт** | только ранг (осознанно) | `rules.py:222` обнуляет поле для `assess_selected_methods` |
| `priority` | recommender:485,672 | веса и баллы TOPSIS | только ранг | `weights` меняются; 4 числа те же |
| `cpu_budget` | rules:96 | баллы TOPSIS (`resource_fit`) | только ранг | свип: только `scores` |
| `gpu_budget` | rules:97 | то же | только ранг | то же |
| `ram_budget` | rules:98 | то же | только ранг | то же |
| `vram_budget` | rules:99 | то же | только ранг | то же |

### 1.2. Производные и входы запроса

| Параметр | Где читается | Что меняет | Вердикт | Доказательство |
|---|---|---|---|---|
| `object_count_effective` | hardware:925; transitions:54 | работа на кадр | OK | `_active_scene` 917-927 |
| `npc_count_effective` | hardware:926,961; transitions:53 | работа на кадр | OK | то же |
| `basket` (методы) | hardware/rules/recommender/planning | `4Ч`, нагр, ранг, план | OK | ядро расчёта |
| `baseline` | recommender/transitions | статус переходов, ранг | только ранг | `transitions.assess` |
| `team` | planning:101,307 | план (календарь) | OK (для плана) | `_schedule_tasks` |
| `include_dependencies` | planning:185 | состав задач плана | OK (для плана) | `_methods_with_dependencies` |

### 1.3. Компоненты конвейера из списка постановки

| Компонент | Где | Что меняет | Вердикт | Доказательство |
|---|---|---|---|---|
| структура мира / тип мира | `world_type` | см. 1.1 | OK | hardware:947 |
| масштаб мира | `scale` | см. 1.1 | OK | hardware:914 |
| движок | `engine` | состав методов, цели | только ранг | rules:122; targets:142 |
| масштаб проекта | `project_scale` | базис RAM | OK | hardware:772,1735 |
| платформа | `platforms` | `4Ч`, unmet | OK | targets:136 |
| целевые разрешение/качество/FPS | 3 поля | `4Ч` | OK | hardware:1278-1283 |
| графический API / RHI | `render_api` | `cpu_seq`, `rgpu` | OK | `_API_FACTORS` 608-615 |
| накопитель | `storage_type` | streaming CPU | OK-усл | 616-617,1262 |
| модель памяти | `memory_model` | RAM/VRAM | дефект (`managed`) | 1723 |
| масштабирование (апскейл) | `upscaling_method` | `rgpu` | OK | 1332-1368 |
| streaming pool | `streaming_pool_gb` | RAM/VRAM | OK | 1649-1713 |
| draw-call budget | `draw_call_budget` | текст | объявлено-но-мертво | 2666 |
| радиус симуляции | `simulation_radius_m` | CPU AI | OK-усл | 1245-1250 |
| такт физики | `physics_tick_hz` | `rcpu` | OK | 1844-1858 |
| сложность аудио | `audio_complexity` | CPU/CPU-RAM/install | OK-усл | 1241,1705,2375 |
| генерация кадров | `frame_generation`+`base_render_fps` | `rcpu`,`rgpu` | OK | 1783-1787,1881-1892 |
| предел размера игры | `size_limit_gb` | исключение методов | OK-усл | rules:161 |
| пределы RAM/VRAM | `ram_limit_gb`,`vram_limit_gb` | `bn`/unmet | дефект контракта | 2468-2469,2647-2656 |
| срок / допустимая сложность | `deadline_weeks`,`complexity_tolerance` | risks / список | только ранг/текст | recommender:317; rules:222 |
| сетевой режим | `multiplayer`,`player_count`,`network_topology` | CPU сеть | OK-усл | 1229-1238 |
| масштаб сцены (объекты/NPC) | `object_count(_level)`,`npc_count(_level)` | `4Ч` | OK | 917-927 |
| стадия разработки | `stage` | ранг/риски | только ранг | recommender:141 |
| проектные бюджеты | 4 × `*_budget` | баллы TOPSIS | только ранг | rules:96-99,312-325 |
| игровые функции | `functions` | `4Ч` | OK | 1216-1218,1274-1276 |
| реализации функций | `basket` | `4Ч`, план | OK | ядро |
| доказательства и переносимость | `evidence.py`,`publication.py` | ничего в числах | объявлено-но-мертво | `practice_check` всегда `not_calibrated` |
| зависимости/конфликты/альтернативы | `rules.assess_selected_methods`,`transitions`,`basket_compatibility` | состав корзины → числа | OK-усл | rules:213-309 |
| риски проекта | `recommender.detect_risks` | только список | текст | recommender:129-340 |
| корзина решений | `basket` | `4Ч`, нагр, план | OK | — |
| профиль нагрузки | `recommender.aggregate_load` | выход из той же модели | OK | recommender:995-1097 |
| железо | `hardware.estimate_hardware` | выход | OK | hardware:2441-2610 |
| финальный план | `planning.schedule` | зависит только от корзины+команды | не учтено | planning:314 — единственное чтение профиля |

---

## 2. Сводка по вердиктам

| Класс | Число | Поля |
|---|---:|---|
| Меняет ≥1 из 4 чисел (OK / OK-усл) | **28** | format(косв.), world_type, scale, project_scale, platforms, object_count_level, object_count, npc_count_level, npc_count, player_count, multiplayer, local_view_count, functions, target_resolution, target_quality, target_fps, render_api, storage_type, memory_model, upscaling_method, network_topology, frame_generation, base_render_fps, streaming_pool_gb, simulation_radius_m, physics_tick_hz, audio_complexity, size_limit_gb(косв.) |
| Меняет только ранжирование | **8** | stage, engine, complexity_tolerance, priority, cpu_budget, gpu_budget, ram_budget, vram_budget |
| Только текст / объявлено-но-мертво | **13** | name(полностью мёртв), engine_version, draw_call_budget, 7 целевых метрик, deadline_weeks, ram_limit_gb, vram_limit_gb |
| Итого полей профиля | **49** | — |

Из 28 «железных» полей **17** меняют числа безусловно, **11** — только во включающем
контексте (условные CPU-ветви, апскейл, split-screen, генерация кадров и т. п.);
это не дефект, а конструкция модели.

---

## 3. Настоящие дефекты — по влиянию на 4 числа железа

### D1. Множитель разрешения не пропорционален пикселям — единственный дефект, сдвигающий 4 числа

`RESOLUTION_FACTOR` (`hardware.py:95-98`) применяется только к пиксельным стадиям
(`GPU_PIXEL_SUBSYSTEMS`, `hardware.py:1282-1283`) и к проходу RT (`rt_scale`,
`hardware.py:1874-1878`). Для этих стадий стоимость линейна по числу пикселей, но
множитель этому не следует:

| Разрешение | Множитель в коде | Отношение пикселей | Отклонение |
|---|---:|---:|---:|
| 720p | 0.62 | 0.444 | +40 % (завышает) |
| 1440p | 1.60 | 1.778 | −10 % |
| 2160p / 4k | 3.00 | 4.000 | −25 % (занижает) |

**Измерено** (инъекция `RESOLUTION_FACTOR['2160p']=4.0` в память, файлы не менялись):
`required_gpu_index` 0.4644 → **0.6066 (+30.6 %)**, `estimated_vram_gb` 15.5 → **18.8 (+21.3 %)**.
Для 720p обратный эффект: rgpu 0.1262 → 0.1012 (−19.8 %).
Это прямое занижение требований на 4K — самой дорогой цели. Оговорка: остальные
GPU-стадии (геометрия, compute) от пикселей не зависят, поэтому полный эффект меньше
чисто пиксельного; но множитель применяется именно к пиксельным стадиям, и там он
обязан совпадать с отношением пикселей.

### D2. Модель памяти `managed` объявлена, но не отличается от `dedicated`

`MemoryModel.MANAGED` есть в перечислении (`models/enums.py:412`), в схеме
(`schemas/catalog.py:104`) и в анкете (`ProfileScreen.tsx:202-208`). В арифметике
специально обрабатывается только `unified` (`hardware.py:1723`, `2462`, `2467`).
**Измерено**: `auto`, `dedicated`, `managed` дают одинаковые 4 числа
(0.1802, 0.3057, 14.6, 8.9). Пользователь, выбравший «управляемая куча / GC»,
не получает никакой реакции. Влияние на числа — 0 (поле мертво), но это ложное
обещание в контракте анкеты.

### D3. Пределы RAM/VRAM не ограничивают результат

`ram_limit_gb`/`vram_limit_gb` идут только в нормализацию давления
(`hardware.py:2468-2469`) и в текст `unmet_limits` (`hardware.py:2647-2656`).
**Измерено** (`tmp/wave6_params_targeted.py`): при 2160p/ultra/very_large
`ram_limit` 4 → 32 даёт **ram = 18.9 ГБ неизменно**; `vram_limit` 2 → 24 даёт
**vram = 19.5 ГБ неизменно**. Меняется только `bottleneck` (при vram_limit=24
память перестаёт быть узким местом) и текст. При этом блок схемы называется
«Обязательные ограничения» (`schemas/catalog.py:125`), а `unmet_limits` —
«список невыполненных обязательных ограничений» (`schemas/catalog.py:746-749`).
Контракт обещает ограничение, которого нет. Анкета при этом честна: раздел
назван «Пределы для проверки» (`ProfileScreen.tsx:325-327`).

### D4. Размер установки зависит от разрешения — противоречит собственному комментарию

`_install_size_parts` (`hardware.py:2354-2376`) берёт текстуры из
`model.memory["textures"]["vram"]` (`hardware.py:2364`), а тот несёт множитель
разрешения `tex_res` (`hardware.py:1699`, `1741`). Комментарий `hardware.py:2341-2345`
объявляет установку упакованным контентом со всей пирамидой мипов, то есть от
разрешения не зависящим. **Измерено**: установка 1080p = **24.4 ГБ** → 2160p =
**27.4 ГБ (+12.3 %)**. На 4 числа не влияет, но пользователь видит противоречие.

### D5. Draw calls считаются по объёму мира, а не по активной сцене

`_estimated_draw_calls` (`hardware.py:953-970`) получает `content` как
`model.world_content` (`hardware.py:2473`), то есть активная сцена × размер мира.
Это противоречит доктрине `_active_scene`/`_world_content` (`hardware.py:917-932`):
размер мира не должен множить работу кадра. **Измерено**: scale small = **27 490** →
very_large = **48 317 (+75.8 %)**. Влияет только на предупреждение
`draw_call_budget` (`hardware.py:2666-2670`), не на 4 числа.

### D6. Знак текста `_consequences` расходится с арифметикой — ровно 1 метод

`_consequences` (`hardware.py:2282-2287`) суммирует `impact_network` из базы,
а арифметика читает курируемую таблицу `METHOD_SUBSYSTEM_EFFECTS`. **Измерено**
(`tmp/wave6_params_targeted.py`): расхождение одно —
`client_prediction_reconciliation`: `impact_network = −1` («снижает трафик»),
таблица `hardware.py:509` даёт `cpu.network = −0.16` (наценка). Уточнение к
прошлому аудиту: второй его пример, `tickrate_budgeting`, **не** расходится —
`impact_network = +2` («повышает») и таблица `hardware.py:513` `−0.24` (наценка)
согласованы по направлению. На 4 числа не влияет.

### D7. Формат 2D не снижает нагрузку рендера

`format` читается в арифметике ровно один раз — `hardware.py:940` (класс
накопителя), плюс `rules.py:110-114` (применимость методов). **Измерено**:
при фиксированной корзине `2D`, `2.5D`, `3D` дают **одинаковые 4 числа**
(0.1802, 0.3057, 14.6, 8.9). Двумерный проект оценивается по трёхмерному
конвейеру; объяснения этому в коде нет. Влияние потенциально большое
(2D-игра, вероятно, требует меньше), но эталона для дельты в модели нет.

### D8. Финальный план не зависит ни от одного параметра профиля

`planning.schedule` (`planning.py:293-323`) читает профиль ровно один раз —
`profile.stage` (`planning.py:314`) — и только для текстовой строки
«Поздняя стадия увеличивает риск переработки». **Измерено**: ни один из 49
параметров не сдвинул `plan_p50`, `plan_calendar.p50`, число задач или critical path.
План определяется исключительно корзиной и командой. Это осознанно для трудоёмкости
(она берётся из пакетов работ), но означает, что `project_scale`, `deadline_weeks`
и стадия на календарь не влияют — стоит проговорить это в отчёте, чтобы пользователь
не ждал иного.

---

## 4. Что объявлено, но не реализовано (контракт)

1. **Семь целевых метрик** (`target_1_percent_low_fps`, `max_startup_seconds`,
   `max_streaming_latency_ms`, `max_save_seconds`, `target_network_latency_ms`,
   `target_server_tick_hz`, `max_network_kbps`) — принимаются схемой
   (`schemas/catalog.py:117-123`), возвращаются со статусом `not_modeled`
   (`hardware.py:1129-1151`), но **ни с чем не сравниваются**. В анкете их нет
   (в `frontend/src/types.ts` отсутствуют), поэтому это обещание уровня API,
   а не интерфейса. Свип: единственный сдвиг — счётчик `target_assessments`.
2. **`draw_call_budget`** — только предупреждение о риске
   (`hardware.py:2666-2670`); это прямо объявлено в докстринге `hardware.py:953-958`,
   поэтому пробел не скрыт.
3. **`deadline_weeks`** — только риск-карточка (`recommender.py:317-338`); на числа,
   ранжирование и план не влияет.
4. **`complexity_tolerance`** — анкета обещает «решения со сложностью выше N будут
   исключены» (`ProfileScreen.tsx:303-304`). Они действительно исключаются из
   **списка рекомендаций** (`rules.py:155-158`), но не из **оценки железа**:
   `assess_selected_methods` намеренно обнуляет поле (`rules.py:222`, комментарий
   «A planning preference cannot remove the runtime work of a selected
   implementation»). Для пользователя: решение, лежащее в корзине, продолжит
   считаться в железе, даже если оно «слишком сложное».
5. **`name`** — не читается нигде (AST: 0).

---

## 5. Связи, не учтённые без объяснения

1. **2D-формат** (D7): единственная ось, где модель сознательно не различает
   значения, а объяснения нет.
2. **`storage_type`** — это множитель CPU-стоимости потоковой загрузки
   (`_STORAGE_CPU_FACTOR`, `hardware.py:616-617`, применение `1262-1263`), а не
   модель диска: ни IOPS, ни МБ/с, ни времени чтения в модели нет. UI обещает
   «Накопитель», влияние на числа — доли процента (rcpu 0.4039→0.4026).
3. **`network_topology`** — только ×1.08 (lockstep) / ×1.04 (p2p) на стоимость
   сетевой подсистемы (`hardware.py:1232-1235`). Заявленная «разная цена схем»
   выражена двумя коэффициентами; измеренный эффект на rcpu — +1.3 %.
4. **`engine`** не влияет на физическую нагрузку напрямую: только через состав
   методов (`rules.py:122-125`) и цели сборки (`targets.py:142`). Прямого
   объяснения в коде нет, связь косвенная.
5. **Аудио `low` тождественно «не указано»**: `_AUDIO_LOAD_LEVEL["low"] = 0.0`
   (`hardware.py:637`). Измерено: `None` и `low` дают одинаковые rcpu/ram
   (0.3122 / 14.6). Различие уровней начинается только с `medium`.

---

## 6. Что подтверждено как исправленное или корректное

* **RT-отсечение** — `_supports_ray_tracing` теперь по `rt_score > 0`
  (`hardware.py:774-788`); прежний дефект закрыт.
* **Аудио в трёх единицах** — `_AUDIO_CPU_LOAD` больше не существует (проверено
  `hasattr` → False); единицы разделены (`_AUDIO_LOAD_LEVEL` 637, `AUDIO_RAM_BASE_GB`
  640, `AUDIO_RAM_GB_PER_LEVEL` 641). Числа сохранены намеренно (1 уровень = 1 мс
  CPU и 1 ГБ RAM), но теперь это явные константы, а не одна переменная.
* **Линейность по FPS** — rgpu/rcpu растут ровно ×2 при 60→120 (`control`).
* **Монотонность сцены** — `object_count` 0→5e6: content 0.96→1.35, ram 14.9→17.8;
  `npc_count` 0→5e5: ram 14.8→17.5. Отрицательных и нулевых компонентов нет.
* **Насыщение игроков на 32** (`hardware.py:1045`, `1230`) — измерено: 32/64/256
  дают одинаковый rcpu; объявлено в `applicability_limits` (`hardware.py:1112-1116`).
* **Мультиплеер как отдельная подсистема** — при `multiplayer=False` сетевой вклад
  обнуляется (`hardware.py:1236-1238`); измерено +19.8 % rcpu при включении.
* **`unified` память** — учитывается один раз, без двойного счёта
  (`hardware.py:1718-1723`, `1757-1780`, `2244-2252`).

---

## 7. Воспроизведение

```bash
# база — копия; working DB не трогается
cp backend/gamedev_dss.db tmp/wave6_audit.db
./.dss-venv/Scripts/python.exe tmp/wave6_params_inventory.py   # чтения полей (AST)
./.dss-venv/Scripts/python.exe tmp/wave6_params_sweep.py       # свип A/B, ~2 мин
./.dss-venv/Scripts/python.exe tmp/wave6_params_targeted.py    # условные CPU, пределы, ловушки
./.dss-venv/Scripts/python.exe tmp/wave6_params_control.py     # managed/2D/FPS/разрешение/аудио
```

Артефакты: `tmp/wave6_params_inventory.json`, `tmp/wave6_params_sweep.json`,
`tmp/wave6_params_targeted.json`. Все пробники — новые файлы; существующие не
изменялись, в базу ничего не писалось.

**Приоритет правок (по влиянию на 4 числа).** Единственная правка, меняющая сами
числа, — множитель разрешения (D1). Далее по важности для доверия пользователя:
мёртвый `managed` (D2), неограничивающие пределы RAM/VRAM (D3), установочный размер
от разрешения (D4). Остальное (D5–D8) числа не двигает и требует либо одной строки
в реестре, либо переформулировки текста.
