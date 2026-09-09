# Что подходит под условия, а что нет — на данный момент в проекте

Дата проверки: 2026-09-09. Только проверка, без интеграции.
Критерий включения: влияние на архитектуру, вычислительную нагрузку или потребление ресурсов.
Не критерий: влияние «на игру в целом» (коммерция, сюжет, контент без механизма).

Исключить: монетизацию, дату выхода, сюжетные развилки, количество концовок.
Сохранить: разрушаемость, масштаб мира, NPC, мультиплеер, физику, навигацию, стриминг — как техтребования.

Источник подсчёта партий: `validation/integrate_parties.py` -> `validation/technical-integration/rows.json/summary.json`.
Воспроизводится: `.\.venv\Scripts\python.exe validation\integrate_parties.py`
Факт на момент проверки: 11 файлов, 58 профилей, 980 строк с кодом.

## 1. Партии: подходит — 492 строки

| Группа | Строк | Смысл |
|---|---|---|
| `technical_reference` | 460 | Есть механизм, сопоставлена функция-тема. Не эквивалентность методов, не доказательство применения в игре, без импорта чисел |
| `catalog_method` | 20 | Код совпал с кодом метода каталога (16 уникальных, все `партия-01.md`). Совпадение кода ≠ применение в игре |
| `technical_requirement` | 12 | Механизм только в тексте строки: синхронизация/репликация -> netcode (3), NPC/ИИ -> advanced_npc_ai (9) |
| **Итого подходит** | **492** | `numerical_import=false`, `game_adoption_verified=false` у всех |

Функции с покрытием из партий (37 шт, строк):

- `multiplayer_netcode` 70, `rendering_architecture` 57, `advanced_npc_ai` 51, `project_architecture` 36, `open_world_streaming` 31, `physics_simulation` 29, `volumetric_effects` 20, `post_processing` 19, `destruction_simulation` 17, `character_animation` 16, `audio_system` 13, `large_scale_terrain` 13, `dynamic_lighting` 11, `runtime_memory` 10, `render_scalability` 9, `ai_pathfinding` 6, `crowd_simulation` 5, `hair_rendering` 5, `particle_systems` 5, `path_tracing` 4, `procedural_terrain` 4, `procedural_vegetation` 4, `vehicle_simulation` 4, `runtime_security` 4, `build_delivery` 4, `baked_lighting` 3, `portal_rendering` 3, `cloth_simulation` 3, `save_system` 3, `split_screen_rendering` 3, `water_simulation` 3, `dynamic_global_illumination` 2, `dynamic_shadows` 2, `geometry_pipeline` 2, `upscaling_frame_generation` 5, `art_pipeline` 1

Примеры подходящего (сохранённое):
- разрушаемость: `extended_destruction`, `levolution_dynamic_destruction`, `destructible_demon_systems`, `lego_manhattan_destructible`
- масштаб/стриминг: `open_world_torrent_navigation`, `large_open_world_chunk_loading`, `redengine4_streaming_nightcity`, `megatexture_virtual_texturing`, `async_loading_pipeline`, `hierarchical_lod`
- NPC/ИИ: `crowd_30000_npc`, `radiant_ai_schedule_graph`, `ai_director_2_0`, `npc_daily_routine_full`, `camp_moving_hq`
- сеть: `headless_dedicated_server`, `server_tickrate_optimized`, `subtick_cs2_replaces_tick`, `lag_compensation_rewind`, `dedicated_servers_pvp`
- физика/навигация: `havok_physics_integration`, `euphoria_naturalmotion`, `fixed_timestep_physics`, `hex_grid_pathfinding`, `time_sliced_pathfinding`

20 точных совпадений каталога (подходят, но не доказывают игру):
`baked_occlusion_culling`, `fixed_timestep_physics`, `depth_prepass_early_z`, `gpu_particle_simulation`, `deferred_forward_plus_choice`, `audio_convolution_reverb`, `particle_pooling`, `lightmap_atlas_baking`, `physics_lod_sleeping`, `headless_dedicated_server`, `animation_lod_budget`, `time_sliced_pathfinding`, `hierarchical_lod`, `post_effect_selective`, `async_loading_pipeline`, `differential_patch_pipeline`

## 2. Партии: не подходит — 488 строк

| Причина | Строк | Что это |
|---|---|---|
| `no_stated_architecture_compute_or_resource_mechanism` | 421 | Контент/сюжет/геймплей без механизма нагрузки: квесты, способности без цены, лор, боссы как контент |
| `monetization` | 28 | Магазины, пассы, валюты, цены, продажи, копии |
| `narrative` | 25 | Ветки сюжета, концовки, диалоги, выборы, протагонисты |
| `release_event` | 14 | Даты, релизы, делісты, отмены, эксклюзивы, закрытия серверов |
| **Итого не подходит** | **488** | В модель не идёт, коэффициенты не меняет |

## 3. Каталог проекта: подходит — 40 функций / 119 методов

Все функции каталога заданы по критерию (архитектура/нагрузка/ресурсы), `backend/app/seed/functions_data.py` + `technical_extensions.py`:

`open_world_streaming` 7, `large_scale_terrain` 5, `procedural_vegetation` 5, `dynamic_global_illumination` 6, `baked_lighting` 4, `dynamic_shadows` 6, `particle_systems` 4, `physics_simulation` 5, `character_animation` 7, `crowd_simulation` 4, `ai_pathfinding` 4, `water_simulation` 3, `volumetric_effects` 2, `post_processing` 7, `rendering_architecture` 5, `render_scalability` 1, `geometry_pipeline` 1, `upscaling_frame_generation` 1, `audio_system` 3, `build_delivery` 2, `runtime_memory` 1, `destruction_simulation` 2, `project_architecture` 1, `art_pipeline` 2, `split_screen_rendering` 1, `multiplayer_netcode` 6, `save_system` 2, `path_tracing` 2, `ray_traced_effects` 2, `dynamic_lighting` 2, `mesh_shaders` 2, `procedural_terrain` 2, `gameplay_ability_system` 2, `vehicle_simulation` 2, `advanced_npc_ai` 2, `portal_rendering` 1, `hair_rendering` 2, `cloth_simulation` 2, `runtime_security` 1

Рекомендации считаются только внутри функции (`backend/app/services/recommender.py:519-530`), `resource_fit` изолирован (`486-499`). Безусловных причинных выводов нет — только хедж (`recommender.py:181,198,434-441,505-507,810-812`, `stage_guidance.py:18-24,190`, `rules.py:305-309`).

Доводы: источники описывают механизм (Epic/Unity/Wiki + 6 TECH), числа — экспертные допущения (`technical_extensions.py:1-5`, `hardware.py:71-73`), `confidence=0.5` у новых 8 против `0.7-0.85` у старых, 3/8 численно 0 с `note`.

## 4. В проекте нет на данный момент (разрывы, не норма)

1. `storage_streaming` — функция есть, методов 0. Выбрать её в анкете не к чему применить, TOPSIS сравнивать нечего. Темы SSD/DirectStorage/VPK/пулы из партий лежат в `open_world_streaming`/`build_delivery`/`large_scale_terrain`, а не здесь.
2. `mesh_shaders`, `gameplay_ability_system` — методы есть (по 2), но в `function-map.json` 0 строк: классификатор глотает `mesh_shader` в `rendering_architecture`, способности в общие семьи. Связь партии->функция для них не видна.
3. Одноэлементные группы (`render_scalability`, `geometry_pipeline`, `upscaling_frame_generation`, `project_architecture`, `portal_rendering`, `runtime_security`, `runtime_memory`) — сравнение внутри функции невозможно, вилка устойчивости — прочерк. Это честно, но не ранжирование.
4. Утверждение «именно так сделано в этой игре» — ни для одной из 980 строк не подтверждено (`game_adoption_verified=false`). Для подтверждения нужен отдельный источник по игре, автоматом коэффициенты не меняются.
