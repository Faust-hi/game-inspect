# DSS-методы → VRAM / RAM / CPU: влияние по данным каталога + доказательства из партий

> Шкала каталога (`methods_data.py`): −2 — сильное снижение нагрузки, 0 — нет влияния, +2 — сильное увеличение.
> Ниже — только методы с ненулевым влиянием на CPU/VRAM/RAM, с привязкой к играм из партий 1–11.
> Верификация партии 11 — в конце файла.

---

## 1. CPU: методы, снижающие нагрузку (отрицательный impact_cpu)

| Метод | CPU | RAM | Что делает | Доказательство (партия/игра) |
|---|---|---|---|---|
| `ecs_data_oriented_crowd` | −2 | −1 | Плотные массивы вместо объектов, кэш-локальность | AC Unity: 30k NPC только так; CP77 2.0 Dogtown 90% CPU без ECS — контрпример |
| `agent_update_budget` | −2 | — | Агенты по приоритету, остальные реже | KCD, BG3 (патч №3: отключение дальних NPC), Arma 3 2.20 (извлечение AI-кусков) |
| `flow_field_pathing` | −2 | +1 | Одно поле на группу, цена не зависит от числа агентов | L4D AAS (сотни из десятков сущностей) |
| `physics_lod_sleeping` | −2 | — | Спящие/далёкие тела не симулируются | Skyrim/FO4 Havok; Arma взрывы lineIntersects |
| `multithreaded_physics_jobs` | −2 | — | Физика по потокам | FH4 (урок FH3), DOOM Eternal compute-кластеризация |
| `broadphase_spatial_partitioning` | −2 | +1 | O(n²) → ~O(n) пар | NFS MW AIGoals, Factorio train pathfinding |
| `gpu_skinning_compute` | −2 | — | Скиннинг в шейдере, не на CPU | AC Unity skel-blend в C++ (гибридный монолит 15.5M строк) |
| `gpu_compute_culling` | −2 | — | Отсечение compute-шейдером (+1 GPU) | Horizon Decima StaticScene async compute; AW2 meshlets |
| `managed_gc_alloc_budget` | −2 | −1 | 0 байт/кадр, пулы вместо GC | Hollow Knight (ноль аллокаций в бою); MC Java GC-статтеры — контрпример |
| `crowd_instancing_impostors` | −1 | — | Инстансинг + билборды (−2 GPU, −1 VRAM) | AC Unity толпа; Hitman Absolution 1200 NPC |
| `time_sliced_pathfinding` | −1 | — | Очередь запросов, без пиков | Civ V лейтгейм-залипание — контрпример (не было slicing) |
| `navmesh_tiling_streaming` | −1 | −1 | Тайлы навмеша со стримингом (+1 disk) | Dying Light тайловый навмеш; KCD |
| `hierarchical_lod` | −1 | +1 RAM/+1 VRAM | Прокси-меши кластеров (−2 GPU) | GTA V HLOD-горизонт; BG3 патч №5 (HLOD с меньшими треугольниками) |
| `network_relevancy_priority` | −1 | — | Только значимое клиенту (−2 сеть) | WoW шардинг/лееры; BF2042 128p relevancy |
| `virtual_geometry_clusters` | −2 | −1 RAM | Кластеры ~128 тр-ков, LOD на GPU (−1 GPU) | UE5 Nanite: Remnant II, Lords of the Fallen |
| `destruction_geometry_cache` | −2 | +1 RAM/+1 VRAM/+2 disk | Houdini→Alembic вместо realtime | DOOM Eternal Destructible Demons |
| `animation_lod_budget` | (настр.) | — | Дальние — реже/дешевле | RE3 Remake half-rate 30fps дальних зомби |

## 2. CPU: методы, повышающие нагрузку (положительный impact_cpu)

| Метод | CPU | Комментарий |
|---|---|---|
| `tickrate_budgeting` | +2 (+2 сеть) | 128 Гц = ~125 КБ/с upload; CS 64 vs 128 decade-спор; BF4 10/30 Гц → CTE 60–120 |
| `world_partition_streaming` | +1 (+1 RAM, +1 disk) | Управление ячейками стоит CPU; STALKER 2 traversal-статтеры; Hogwarts Legacy |
| `client_prediction_reconciliation` | +1 (−1 сеть) | Пересчёт и коррекция; Fall Guys гибрид (локально + валидация) |
| `delta_compression_state` | +1 (−2 сеть) | CPU за компрессию вместо bandwidth; BattleBit 254 игрока |
| `pso_precaching_warmup` | +1 (+1 disk) | Компиляция при старте; TLoU Part I (часы), Elden Ring JIT 0.25с — контрпримеры |
| `animation_compression` | +1 (−2 RAM, −2 disk) | Декомпрессия в рантайме; DMC5 фотоскан 190k полигонов |
| `cascaded_shadow_maps` | (+1 GPU, +1 VRAM) | CPU — подача каскадов; Diablo IV: SSAO High→Medium +12% fps |
| `audio_occlusion_propagation` | +1 | Лучи на эмиттер; Hunt: Showdown (звук как механика) |

## 3. VRAM: что растит и что режет

**Растят VRAM (+):**
- `hardware_raytraced_gi` (+1, GPU +2): AW2 PT (RTX 3080 → ~30 fps), CP77 Overdrive, Metro EE RT-only
- `virtual_shadow_maps` (+2, GPU +2): UE5 VSM — Silent Hill 2, Lords of the Fallen
- `temporal_upscaling` (+1, GPU −2): история кадров; Diablo IV Ultra-текстуры = 16 ГБ VRAM (ComputerBase: 4070 12 ГБ < 6800 XT 16 ГБ)
- `ml_frame_generation` (+1, GPU +1): буферы истории; AW2 41→80 fps, но +лаг
- `distance_field_shadows` (+2, CPU −1, GPU −1): SDF-тени дешёвые в кадре, дорогие в памяти; Portal 2 paintmaps
- `deferred_forward_plus_choice` (+2, GPU −1): G-буфер 250+ МБ — причина forward в DOOM Eternal
- `splitscreen_render_budget` (+1, GPU +2): 2x targets; It Takes Two

**Режут VRAM (−):**
- `virtual_texturing` (−2, RAM +1, disk +1): только видимые тайлы; Rage MegaTexture (vt_maxPPF — контрпример без пула); Indiana Jones Texture Cache 8/10/12 ГБ
- `lightmap_atlas_baking` (−2 CPU/−2 GPU, disk +2, RAM +1): рантайм почти free; Metro EE **удалил** лайтмапы ради RT-only
- `lightmap_compression_streaming` (−2, disk −2): сжатые лайтмапы по частям; Genshin каскады по расписанию
- `heightmap_compression` (−1, disk −2): рельеф в блоках; RDR2 Terrain Clipmapping
- `hierarchical_lod` (см. выше): GTA V HLOD

## 4. RAM: ключевые факты

- `deterministic_lockstep` (данные сети, не RAM): Factorio — только инпуты, все пиры симулируют; нулевой трафик от числа объектов
- `animation_compression` −2 RAM: Persona 5 Royal тысячи спрайтов меню; DMC4 SE
- `managed_gc_alloc_budget` −1 RAM: Rust GC-стопы каждые 10–15 сек — контрпример (Mono без бюджета)
- `snapshot_slot_saves` / `async_incremental_saves`: Skyrim сейв-БД 5.5+ МБ → 0 fps на PS3 split-памяти; Subnautica CellsCache-раздутие
- `build_size_startup_budgets`: Genshin гигабайты обновлений; Payday 2 86→32 ГБ (Diesel 3.0)

## 5. Карта «игра → главный налог» (партии 1–11)

| Игра | Главный налог | Метод-доказательство |
|---|---|---|
| AC Unity | CPU draw calls 50k+ | `crowd_instancing_impostors` отсутствует как надо; DX11 монопоток |
| CP77 2.0 | CPU 90% на 8 ядрах (BVH + толпа) | `hardware_raytraced_gi` + `ecs_data_oriented_crowd` нет |
| Dragon's Dogma 2 | CPU мастер-поток, 25–35 fps на 14900K | `agent_update_budget` = 0 (все NPC полный цикл) |
| Arma 3 | CPU single-thread 90–95% | 2.20 Enfusion graph + корутины — частичное лечение |
| Starfield | CPU New Atlantis/Akila | `temporal_upscaling` обязателен (DLSS/XeSS патчи) |
| Diablo IV | VRAM 15 ГБ Ultra-текстуры | `temporal_upscaling` + `virtual_texturing` нет |
| Elden Ring | Shader JIT 0.25с | `pso_precaching_warmup` отсутствует; Deck Fossilize — лечение |
| TLoU Part I | PSO часы + OOM | `pso_precaching_warmup` + `async_loading_pipeline` без бюджета |
| MC Java | GC Stop-the-World | `managed_gc_alloc_budget`; Sodium — community-фикс |
| Factorio | Сеть O(n²) | `deterministic_lockstep` — эталон решения |
| WoW AQ | 2.2M пакетов при 1500 игроках | `network_relevancy_priority` + деградация facing-апдейтов |
| CS2 | Джиттер при 64 Гц снапшотах | `tickrate_budgeting` → метрика джиттер/tick-miss |

---

## Верификация партии 11 (перепроверка 2026-09-07)

| # | Утверждение в партии 11 | Статус | Источник |
|---|---|---|---|
| CP77 2.0 | SMT Ryzen нативно, SSD mandatory, 90% CPU на 8 ядрах | ✅ Подтверждено | Pierściński (X, 09.2023) via Tom's/KitGuru/Guru3D |
| CP77 2.11 | Hybrid CPU Utilization (Auto/Prioritize P-Cores) + RX Vega фикс | ✅ Подтверждено | CDPR 2.11 notes via TheFPSReview 01.2024 |
| CP77 2.12 | Фикс микростаттеров 2.11 | ✅ Подтверждено | Tom's Hardware (тест 13900K+4080S, upd 03.2024) |
| OW2 | Engine 2.0 свой, не UE5; netcode −30% | ✅ Подтверждено | OW2Hub (dev docs), Tweaktown (BlizzCon 2019) |
| OW2 6v6 | Возврат требует сезонов оптимизации (Switch/PS4) | ✅ Подтверждено | Polygon 07.2024, Keller Director's Take (дословно) |
| MC Sodium | Рендер-фикс, Fabric, Lithium/Phosphor-компаньоны | ✅ Подтверждено + уточнено | Modrinth: 221.8M загрузок, GL 4.5+, NeoForge/Quilt, Vulkan 0.9.x для MC 26.2 |
| MC Java 17/21, sim distance | Миграции и разделение дистанций | ⚠️ Частично (знания модели) | Требует DF/DSOG-кроссчека |
| CS2 sub-tick, снапшоты 64 Гц | Точность без удвоения тика | ⚠️ Из прошлого аудита | Dignitas/Varidata/DotEsports (в аудите) |
| CS:GO legacy 4465480 | 03.2026 unlisted, community 128 Hz | ⚠️ Из партии 2 | CritFeed/SkinRadar (в партии 2) |
| Arma 1.68 x64 | Снятие 2–3 ГБ лимита | ✅ Подтверждено | Bohemia SITREP 1.68 (03.2017), OPREP Biely |
| Arma 1.56 Eden | 3D-редактор, audio, Occluder | ✅ Подтверждено | Bohemia SPOTREP 1.56, arma3.com Eden |
| Arma 2.20 | Enfusion job graph, корутины AI, VS2022/C++23, дроп 32-bit | ✅ Подтверждено | Bohemia OPREP Dedmen 06.2025 (первоисточник, полный текст) |
| Arma −cpuCount/−enableHT | Гайд параметров | ✅ Подтверждено | Тот же OPREP (дословно) |

**Внесённые правки в партию-11.md:** Sodium (цифры Modrinth + Vulkan-бэкенд), CP77 2.11 (детали Tom's: 13900K микростаттеры), Arma 2.20 (Enfusion graph + корутины + ping-pong взрывов), верификационная секция расширена.
