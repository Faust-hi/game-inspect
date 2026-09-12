# Волна 6: независимый аудит арифметики и связей между сущностями

Дата: 2026-09-12. Только чтение. Рабочая база не изменялась: все замеры идут по
копии `tmp/wave6_work.db` (снята через `sqlite3.backup`, WAL-консистентно) либо по
памяти стенда. Ни один существующий файл не изменён; созданы только новые стенды
в `tmp/`.

**Стенды (новые):**

| Файл | Что измеряет |
|---|---|
| `tmp/wave6_arith_relations.py` | два канала влияния: курированный `METHOD_SUBSYSTEM_EFFECTS` против БД `methods.impact_*` |
| `tmp/wave6_arith_gpu_pick.py` | фильтр VRAM до/после выбора, ключ «слабейшая прошедшая», квантование, сетка каталога |
| `tmp/wave6_arith_known.py` | подтверждение/опровержение каждого известного пункта |
| `tmp/wave6_arith_constants.py` | константы, клампы, мёртвые ветви, тихо активные связи |
| `tmp/wave6_arith_param_influence.py` | какое поле профиля реально двигает 4 числа |

Сводный вывод: `tmp/wave6_arith_all_output.txt` (301 строка).

Воспроизведение:

```bash
./.dss-venv/Scripts/python.exe -c "import sqlite3;s=sqlite3.connect('backend/gamedev_dss.db');d=sqlite3.connect('tmp/wave6_work.db');s.backup(d)"
./.dss-venv/Scripts/python.exe tmp/wave6_arith_relations.py
./.dss-venv/Scripts/python.exe tmp/wave6_arith_gpu_pick.py
./.dss-venv/Scripts/python.exe tmp/wave6_arith_known.py
./.dss-venv/Scripts/python.exe tmp/wave6_arith_constants.py
./.dss-venv/Scripts/python.exe tmp/wave6_arith_param_influence.py
```

**Про 4 числа.** В постановке 4 числа — это `required_cpu_index`,
`required_gpu_index`, `estimated_ram_gb`, `estimated_vram_gb`. Важно: подбор
карты **не влияет** на `required_gpu_index` (`hardware.py:2555` — индекс берётся
из модели, а не из карты) и не влияет на `estimated_vram_gb` (`hardware.py:2557` —
это требование, а не объём карты). Выбранная карта меняет только
`reference_gpu` и `gpu_class`. Поэтому ниже разделены дефекты «4 числа» и
дефекты «карта/класс».

---

## (a) Известные пункты: подтверждено / опровергнуто

| # | Пункт | Вердикт | Замер |
|---|---|---|---|
| 1 | `_supports_ray_tracing` смотрит на `rt_score > 0`, а не на текст `hw_features` | **ПОДТВЕРЖДЁН** | `hardware.py:788`. Карт `rt_score>0` — **49**, с текстом RT — **39**. Разница **10** — это Radeon «Ray Accelerators» (RX 9070 XT/9070/9060 XT/6500 XT) и RTX «RT» (2080/2080 Super). Это **не дефект**, а исправление: текстовая проверка пропускала бы 10 карт |
| 2 | Аудио — безразмерный уровень `_AUDIO_LOAD_LEVEL` (0 / 0.3 / 0.7), переводимый на месте в мс CPU и ГБ RAM | **ПОДТВЕРЖДЁН** | `hardware.py:637, 1242, 1705, 2368`. Замер: `low/medium/high` → `cpu[audio]` = **0.700 / 1.000 / 1.400 мс**, `audio ram` = **0.35 / 0.65 / 1.05 ГБ**. Одно безразмерное число тратится и как мс, и как ГБ с коэффициентом 1.0 |
| 3 | Пределы RAM/VRAM не клампят, хотя блок назван «Обязательные ограничения» | **ПОДТВЕРЖДЁН** | `hardware.py:2623-2656`, `catalog.py:125`. Замер: `ram_limit` 4/8/16/64 → `ram` всегда **13.9**; `vram_limit` 2/4/8/24 → `vram` всегда **8.3**. Меняется только текст `unmet_limits`. Кламп отсутствует |
| 4 | `apply_hardware_raw_values` пишет шесть полей безусловно и вызывается дважды за старт | **ЧАСТИЧНО ОПРОВЕРГНУТ** | Безусловная запись **устранена**: `fixes_v2.py:486-495` теперь под `if _has_raw_value(row): continue` (`fixes_v2.py:381-388`). «Дважды за старт» — **ПОДТВЕРЖДЕНО**: `fixes_v2.py:676` (`apply_all`) и `corrections.py:756` (`declare_evidence_gaps`), обе внутри `sync_function_taxonomy` (`seeder.py:212, 256`). Числового вреда нет |
| 5 | Масштаб проекта (размер команды) не меняет 4 числа; до чисел доходит только `engine`, через корзину | **ОПРОВЕРГНУТ по формулировке** | `project_scale` **меняет RAM**: 12.4 / 13.9 / 15.4 / 15.9 ГБ (small→very_large), CPU/GPU/VRAM не двигаются (`hardware.py:754-762, 1735`). Размер команды (`TeamScenario`) действительно **не доходит** до железа — он только в `planning.schedule`. `engine` доходит до чисел **только через корзину**, и канал крайне узок: `applicable_engines` заполнен у **2 из 124** методов (`managed_gc_alloc_budget` [unity, custom], `srp_batcher_discipline` [unity]) |
| 6 | Пол памяти 5.19 / 6.69 / 8.19 / 8.69 ГБ по масштабу проекта; пол VRAM 1.92 ГБ; постоянная часть ≈56 % вывода | **ПОДТВЕРЖДЁН** | `tmp/model_floor_probe.py` воспроизводит ровно: **5.19 / 6.69 / 8.19 / 8.69 ГБ**, VRAM **1.92 ГБ**. Постоянная часть — **медиана 56 %, размах 42…70 %** на 25 сценариях. Эталонный профиль пола: функции пусты, 720p/low, `audio_complexity=low`, контент обнулён |
| 7 | Узкое место = суммарный GPU (растр + RT) | **ПОДТВЕРЖДЁН** | `hardware.py:2431-2436`: ключ `gpu` = `raster_index + rt_index`, никогда `max`. Отдельного ключа RT в `BOTTLENECK_TITLES` нет (ключи: `cpu_main_thread`, `cpu_parallel`, `gpu`, `memory`) |

**Итог по известным пунктам: подтверждено 5 полностью, 1 частично (п.4), 1 опровергнут по формулировке (п.5).**

---

## (b) Дефекты, упорядоченные по влиянию на 4 числа

### B1. Фильтр VRAM + округление до 0.1 ГБ дают обрыв выбора карты в ~2× растра

**Файл:** `hardware.py:2190` (жёсткий фильтр `g.vram_gb >= vram_gb` **до** порога
производительности), `hardware.py:2265` (`round(vram, 1)`), `hardware.py:2458`
(в `_pick_gpu` уходит уже округлённое значение).

**Замер** (`tmp/wave6_arith_gpu_pick.py`, блок B):

```
raw req=8.04 -> rounded 8.0 -> Radeon RX 580   raster=0.22 vram=8.0
raw req=8.05 -> rounded 8.1 -> GeForce RTX 3060 raster=0.43 vram=12.0
```

**Дельта:** требование меняется на **0.01 ГБ**, а выбранная карта — с растра
**0.22** на **0.43** (+0.21, **+95 %**), класс с 2 на 3, VRAM с 8 на 12 ГБ.
Причина — не только округление: сетка VRAM каталога дискретна
`{0, 2, 4, 6, 8, 10, 11, 12, 16, 20, 24, 32}` (12 значений), а порог `>=`.
Округление до 0.1 ГБ лишь переносит обрыв в «круглую» точку.

**Что это меняет для пользователя:** рекомендация карты скачком удваивается при
изменении оценки VRAM на 10 МБ. На 4 числа не влияет (индекс и требование VRAM
считаются из модели), но это главный источник завышения `reference_gpu`/`gpu_class`
(см. `research/gpu-spread-2026-09-12.md`, там квантование = +0.110 медианы и всегда вверх).

**Проверить/защитить:** сравнивать карту по *неокруглённому* требованию; либо
показывать диапазон карт, а не одну.

---

### B2. Два канала влияния с ПРОТИВОПОЛОЖНОЙ конвенцией знака

**Файлы:** курированный `METHOD_SUBSYSTEM_EFFECTS` — `hardware.py:322-347`,
потребитель `_apply_method_effects` — `hardware.py:1425` (единственный источник
арифметики). БД `methods.impact_*` — потребители `rules.resource_fit`
(`rules.py:318-323`, вызов `recommender.py:512`) и текст `_impact_text`
(`recommender.py:980-981`), качественные `disk/network` (`recommender.py:1057-1059`).

**Конвенции противоположны:**
* курированный: `value >= 0` — **экономия**, `< 0` — наценка (`hardware.py:324-330, 1421-1430`);
* БД: `-2` — **сильное снижение нагрузки**, `+2` — увеличение (`methods_data.py:10-11`).

**Замер** (`tmp/wave6_arith_relations.py`):

| Скоуп | Совпадают | **Расходятся** | БД=0 | нет курированного |
|---|---:|---:|---:|---:|
| CPU | 60 | **8** | 3 | 53 |
| GPU | 51 | **6** | 2 | 65 |

Расхождения знака, CPU: `world_partition_streaming`, `async_loading_pipeline`,
`delta_compression_state`, `tilemap_chunk_streaming`, `deterministic_lockstep`,
`async_incremental_saves`, `chunked_procedural_terrain`, `raycast_vehicle_physics`.
GPU: `gpu_compute_culling`, `hardware_raytraced_gi`, `dynamic_resolution_scaling`,
`full_path_tracing_pipeline`, `selective_ray_traced_effects`, `meshlet_pipeline_adoption`.

Пример: `world_partition_streaming` — БД `impact_cpu=+1` («повышает нагрузку»),
курированный `{"streaming": +0.30, "main_thread": +0.12}` («снижает на 30 %»).
Карточка метода говорит «возможные дополнительные расходы: CPU», а арифметика
начисляет экономию −0.42.

**Что это меняет для пользователя:** направление эффекта в карточке может
противоречить направлению в железе. На 4 числа — **ноль** (БД-канал до чисел не
доходит), но пользователь читает два взаимоисключающих утверждения об одном решении.

**Ещё две несогласованности наличия:** `art_direction_stylization` — есть
курированный эффект (`gpu.shading +0.14`), БД `impact_*` все нули;
`headless_dedicated_server` — курированный `{}` (в арифметике ничего), БД
`impact_cpu=-2, impact_gpu=-2, impact_ram=-1`.

---

### B3. `resource_fit` не учитывает `effect_scope`: серверный метод ранжируется как лучший по ресурсам клиента

**Файлы:** `rules.py:312-325` (использует `method.impact_*` без проверки scope),
вызов `recommender.py:511-512`.

**Замер:**

```
headless_dedicated_server  scope=server  impact_cpu=-2  resource_fit=0.750  ← максимум
hierarchical_lod           scope=client  impact_cpu=-1  resource_fit=0.519
world_partition_streaming  scope=client  impact_cpu=+1  resource_fit=0.369
```

`headless_dedicated_server` (scope=`server`, эффект исключён из клиентской
арифметики через `split_by_effect_scope`) получает **наибольший** `resource_fit`
и поднимается в ранжировании TOPSIS как «наиболее соответствующий дефицитным
ресурсам проекта». Всего таких методов 4 (`server`), у всех ненулевые
`impact_cpu`.

**Что это меняет:** ранжирование рекомендаций (не 4 числа). Пользователь видит
серверное решение первым по критерию «соответствие ресурсным ограничениям» клиента.

---

### B4. `local_view_count` умножает рендер даже без выбранной функции split-screen

**Файлы:** `hardware.py:1061-1071` (`_local_views`), `1254-1257` (CPU `render_prep`),
`1298-1301` (GPU `geometry`), `1749-1752` (буферы вида).

**Замер** (функции пусты, `split_screen_rendering` НЕ выбрана):

```
local_view_count=None  cpu_index=0.2469 gpu_index=0.1515 ram=13.9 vram=8.3
local_view_count=2     cpu_index=0.3572 gpu_index=0.1758 ram=13.9 vram=8.7
local_view_count=4     cpu_index=0.5779 gpu_index=0.2243 ram=13.9 vram=9.6
```

**Дельта:** `cpu_index` **+134 %** (0.2469→0.5779), `gpu_index` **+48 %**,
`vram` **+1.3 ГБ**. В модели подсистемы `render_prep` и `geometry` умножаются на
число видов (1.956→7.825 и 0.396→1.586 мс).

**Что это меняет:** поле тихо и сильно двигает 4 числа, хотя связь «`local_view_count`
→ нагрузка» нигде не объявлена обязательной от выбора функции. Если UI отдаёт
поле только для split-screen, расхождение не проявится; если поле доступно
всегда — это тихий множитель ×4.

---

### B5. Пределы RAM/VRAM не клампят (дефект контракта)

**Файлы:** `hardware.py:2647-2656`, `catalog.py:125` («Обязательные ограничения»).

Замер в (a) п.3. На 4 числа — **ноль**; меняется только `unmet_limits` и (по
`research/wave4-proposal-verification-2026-09-12.md` §6) может переключиться
`bottleneck` (предел входит в знаменатель `_memory_pressure`, `hardware.py:2468-2469`).
Подтверждено, решение за пользователем (клампить / переименовать / объявить границей).

---

### B6. `size_limit_gb` жёстко исключает методы только при значении < 2 ГБ

**Файл:** `rules.py:161`: `if profile.size_limit_gb is not None and profile.size_limit_gb < 2 and method.impact_disk >= 2`.
Схема допускает предел до 4096 ГБ (`catalog.py:128`). Предел ≥ 2 ГБ не исключает
ни одного метода и лишь добавляет строку в `_storage_requirement`
(`hardware.py:2333-2337`). На 4 числа — ноль. Класс уже объявлен в
`research/wave4-proposal-verification-2026-09-12.md` §6, здесь подтверждён
порогом `< 2`.

---

### B7. Клампы, которые никогда не срабатывают (инертные константы)

**Файлы:** `hardware.py:663` (`MAX_SUBSYSTEM_SAVING=0.70`), `668-669`
(`MEMORY_MAX_SAVING=0.70`, `MEMORY_MAX_INCREASE=3.0`).

**Замер** (`tmp/wave6_arith_constants.py`, блок C): максимальная одиночная
экономия CPU/GPU в каталоге — **0.55** (не 0.70); самая отрицательная `mem` —
**−0.45** (не −0.70); максимальный положительный `mem` — **0.35** (не 3.0).
Ни один одиночный кламп не срабатывает; `MEMORY_MAX_INCREASE` может связать
только сумма приращений. На 4 числа — ноль, но константы создают ложное
впечатление ограничения.

---

### B8. `perf_class` как первичный ключ выбора может выбрать НЕ слабейшую прошедшую карту

**Файл:** `hardware.py:2204`: `min(chosen, key=lambda g: (g.perf_class, g.raster_score))`.

`perf_class` — целое 1..5 (1 слабейший). Замер: 2 пары, где меньший `perf_class`
имеет **больший** растр — `RTX 5060 Ti` (class 3, raster 0.59) и
`RTX 5070 Ti Laptop` (class 3, 0.59) против `Radeon RX 6800` (class 4, 0.58).
На сетке порогов найдено **2 точки**, где выбор «по классу» даёт не тот же
результат, что выбор «по растру»:

```
vram>=12 raster>=0.55: class-first=RTX 5060 Ti (c3, r0.59) vs raster-first=RX 6800 (c4, r0.58)
vram>=16 raster>=0.55: то же
```

**Дельта:** +0.01 растра. Это **опровергает буквальное «выбор по классу не даёт
ничего»** из `gpu-spread-2026-09-12.md` §2 (там измерялись 15 игр, и выбранная
карта не менялась). Дефектом не является: расхождение мало, но правило
«слабейшая прошедшая» формально не выполняется.

---

### B9. `_alternatives` не применяет предпочтение десктопных карт

**Файл:** `hardware.py:2811-2816` (`_alternatives`) против `hardware.py:2202`
(`_pick_gpu`, где есть `desktop = [g for g in candidates if not _is_mobile_gpu(g)]`).

Замер: эталон `GeForce RTX 3060` (десктоп), альтернативы —
`[Radeon RX 9060 XT, GeForce RTX 5060 Ti, GeForce RTX 5070 Ti Laptop GPU, Arc A770]`.
Мобильная карта попадает в «тот же класс». Только отображение.

---

### B10. `apply_hardware_raw_values` вызывается дважды за старт

**Файлы:** `fixes_v2.py:676`, `corrections.py:756`. Второй вызов — no-op
(все строки уже имеют `benchmark_raw_value`). На 4 числа — ноль. Гигиена.

---

## (c) Связи, которые проект не запрещает, но молча игнорирует (без объявленной причины)

Замер — `tmp/wave6_arith_param_influence.py`. Классификация: **A** — двигает
4 числа, **B** — двигает модель, но замаскировано `max()` в индексе, **C** — не
двигает ничего.

| Поле | Класс | Что происходит | Причина задокументирована? |
|---|---|---|---|
| `resource_fit` ↔ `effect_scope` | — | `resource_fit` использует `impact_*` серверных методов (B3) | **НЕТ** |
| `local_view_count` без split-screen | A | ×2/×4 к render_prep/geometry (B4) | **НЕТ** |
| `size_limit_gb` ≥ 2 ГБ | C | только текст, методов не исключает (B6) | частично (wave4 §6) |
| `ram_limit_gb`/`vram_limit_gb` | C (только `bottleneck`) | не клампят (B5) | **НЕТ** (контракт обещает обратное) |
| `multiplayer`, `player_count`, `network_topology` | B | меняют `cpu_parallel_ms`/`network`, но `cpu_index=max(st,mt)` маскирует | частично |
| `physics_tick_hz`, `simulation_radius_m` | B | меняют `physics`/`ai`, маскируется `max()` | **НЕТ** |
| `storage_type` | B | множит `streaming` (0.98…1.12), маскируется | да (`wave4` §3) |
| `frame_generation` / `base_render_fps` | C поодиночке | работают только **парой**; `frame_generation=True, base_render_fps=30` → cpu 0.2904→0.1452, gpu 0.1886→0.1303 | да (`_render_fps`) |
| `draw_call_budget` | C | только предупреждение | да (`hardware.py:933-938`) |
| `deadline_weeks` | C | только risk-карточка | да (wave4 §6) |
| `complexity_tolerance` | C | в корзине железа снимается (`rules.py:222`), влияет только на выдачу рекомендаций | да |
| `cpu/gpu/ram/vram_budget` | C | только критерий `resource_fit` TOPSIS | да (wave4 §6) |
| `stage`, `priority` | C | только порядок/текст | да |
| `engine_version` | C | только `modeling_gaps` | да |
| `engine` | C при фиксированной корзине | до чисел — только через 2 метода с `applicable_engines` | **НЕТ** (узость канала не объявлена) |
| 7 эхо-целей (`target_1_percent_low_fps`, `max_startup_seconds`, `max_streaming_latency_ms`, `max_save_seconds`, `target_network_latency_ms`, `target_server_tick_hz`, `max_network_kbps`) | C | `status=not_modeled` | да (wave4 §3) |

**Итого:** 16 полей двигают сами 4 числа; ещё 2 (`ram_limit_gb`/`vram_limit_gb`)
двигают только `bottleneck` (проверено: сигнатура из 4 чисел даёт 1 уникальное
значение при 8/64 ГБ и 4/32 ГБ); 4 — двигают модель, но маскируются `max()`;
23 — не двигают ничего (из них большинство объявлено; без причины —
`effect_scope↔resource_fit`, `local_view_count`, `ram/vram_limit` как контракт,
узость канала `engine`, маскировка `physics_tick_hz`/`simulation_radius_m`).

---

## (d) Что КОРРЕКТНО (повторно не аудировать)

1. **`_supports_ray_tracing` по `rt_score > 0`** (`hardware.py:788`) — правильнее
   текстовой проверки; 10 карт (Radeon «Ray Accelerators», RTX «RT») находились бы
   неверно. Оговорка в докстринге про Radeon 780M (`rt_score=0` при наличии текста
   `rt`) подтверждена.
2. **Пол памяти и VRAM воспроизводятся точно**: 5.19 / 6.69 / 8.19 / 8.69 и
   1.92 ГБ; постоянная часть — медиана 56 % (42…70 %). Пол объявлен допущением
   (`hardware.py:711-719`), не дефект.
3. **Узкое место — сумма растра и RT** (`hardware.py:2431-2436`), RT не имеет
   отдельного ключа. Согласовано с подбором (`gpu_index = raster + rt`).
4. **Перекрытие эффектов**: экономии берётся `max`, наценки складываются; в памяти
   приращения складываются, экономии — `max` (`hardware.py:1486-1616`). Направление верное.
5. **Масштаб шкалы памяти**: дефицит ГБ переводится в мс подкачки и сравнивается
   с бюджетом кадра (`_memory_pressure`, `hardware.py:2384-2416`). Смешения ГБ и мс нет.
6. **Апскейлинг не даёт двойного счёта RT**: база `rt` = 0 (`GPU_BASE_COST`),
   `_apply_upscaling` множит пиксельные стадии, а `rt_ms` вводится позже и
   масштабируется `rt_scale` (`hardware.py:1874-1878`) ровно один раз.
7. **`effect_scope` корректно делит арифметику**: `split_by_effect_scope`
   (`rules.py:34-49`), в `_apply_method_effects` идут только клиентские
   (`hardware.py:1797, 1881`). Единственная щель — `resource_fit` (B3).
8. **`apply_hardware_raw_values` теперь идемпотентен** — защита `_has_raw_value`
   (`fixes_v2.py:381-388`). Безусловная запись из N10 устранена.
9. **`_consequences` включает `critical`** (`hardware.py:2312`) — прежний пропуск
   `critical` (комментарий 2306-2311) закрыт.
10. **`_target_assessments` возвращает 8 строк, включая `target_fps`**
    (`hardware.py:1131-1151`); `target_fps` реально задаёт бюджет кадра
    (`_render_fps` → `budget_ms`). Замечание wave4 §3 учтено.
11. **Память unified без двойного счёта**: резерв VRAM рабочего стола и зеркало
    не считаются дважды (`hardware.py:1723-1730, 1774`), `_memory_totals` складывает
    пулы (`hardware.py:2247-2252`).
12. **Единая модель для нагрузки и подбора**: `build_model` — единственный источник
    (`hardware.py:60-64, 1790`); `aggregate_load` читает ту же модель
    (`recommender.py:1022`). Расхождения «экран ↔ экран» структурно нет.
13. **Нет маркеров `TODO/FIXME/placeholder`** в `hardware.py` (grep — 0 совпадений).
14. **Мёртвые ветви в `_pick_references`, объявленные в комментариях, действительно
    удалены** (`hardware.py:2752-2757`): проверки «карта меньше требуемой VRAM» и
    недостижимой ветки RT нет.

---

## Приложение. Что осталось непроверенным

* Внешняя калибровка чисел (`CPU_FEATURE_MS=10.0`, `GPU_FEATURE_MS=6.2`,
  `PARALLEL_SPEEDUP=2.4`, `MEMORY_DEFICIT_STALL_MS=6.0`) не выполнялась — сеть не
  использовалась. Направление проверено, величина — нет.
* Разложение памяти `mirror` (RAM = `meshes.ram` + `textures.ram` +
  `0.25·(meshes.vram+textures.vram)`, замер 1.09 + 0.96 + 1.23 ГБ) — **объявленное
  допущение** (`hardware.py:1760-1772`), а не дефект. Вопрос «не двойной ли счёт
  CPU-копий» остаётся открытым для калибровки, но по правилу проекта объявленная
  граница не чинится.
* Компонент `streaming` в памяти — константа 0.9/0.25 ГБ, не масштабируется
  размером мира, тогда как докстринг `_memory_components` говорит «резидентные
  ресурсы растут с размером мира». Наблюдение, не дефект.
* `MEMORY_MAX_INCREASE=3.0` связывает только сумму приращений; сумм, близких к
  порогу, в текущем каталоге нет.
