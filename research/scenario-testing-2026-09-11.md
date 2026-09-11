# Тестирование проекта на 25 реалистичных сценариях

**Предмет:** локальная ИС поддержки принятия решений по оптимизации разработки игр (`game-inspect`). **Дата:** 11.09.2026. **Метод:** профиль каждой реальной игры подаётся в движок рекомендаций, результат сопоставляется с документированным поведением оригинала.

> Эталон опирается на доказательный каталог проекта (кейсы и утверждения с источниками) там, где он есть, и на публичную техническую документацию иначе. Каждое утверждение помечено источником. Числа проекта — вывод движка, а не измерение.

## Часть I. Профиль игр

Каталог проекта содержит **155 игровых кейсов**, **40 игровых функций**, **7 движков** и **124 методов**. Привязку к функциям (а значит и к рекомендациям) имеют **44 кейса**; остальные — reference-реализации и возможности движков без прямой привязки.

> **Пробел каталога:** функции `storage_streaming` объявлены, но ни одного метода для них не опубликовано: выбрать способ реализации по ним нельзя.

### I.1. Какие функции реально поддержаны

| Функция | Методов | Кейсов-примеров |
| --- | ---: | ---: |
| `multiplayer_netcode` — Сетевой код мультиплеера | 8 | 4 |
| `advanced_npc_ai` — Поведенческий ИИ NPC | 3 | 3 |
| `audio_system` — Аудиосистема | 3 | 3 |
| `crowd_simulation` — Толпы NPC | 4 | 3 |
| `geometry_pipeline` — Конвейер геометрии | 1 | 3 |
| `open_world_streaming` — Потоковая загрузка открытого мира | 8 | 3 |
| `procedural_terrain` — Процедурная генерация ландшафта и мира | 2 | 3 |
| `rendering_architecture` — Архитектура рендера | 6 | 3 |
| `split_screen_rendering` — Split-screen рендеринг | 1 | 3 |
| `upscaling_frame_generation` — Масштабирование и генерация кадров | 1 | 3 |
| `ai_pathfinding` — ИИ и поиск пути | 4 | 2 |
| `art_pipeline` — Арт-пайплайн | 2 | 2 |
| `baked_lighting` — Запечённое освещение | 4 | 2 |
| `build_delivery` — Сборка и доставка контента | 2 | 2 |
| `character_animation` — Анимация персонажей | 7 | 2 |
| `cloth_simulation` — Симуляция ткани | 2 | 2 |
| `destruction_simulation` — Разрушения и геометрические кэши | 2 | 2 |
| `dynamic_global_illumination` — Динамическое глобальное освещение | 6 | 2 |
| `dynamic_lighting` — Множественные динамические источники света | 2 | 2 |
| `dynamic_shadows` — Динамические тени | 6 | 2 |
| `gameplay_ability_system` — Геймплейные способности и модификаторы | 2 | 2 |
| `hair_rendering` — Волосы: пряди или карточки | 2 | 2 |
| `large_scale_terrain` — Крупномасштабный ландшафт | 5 | 2 |
| `mesh_shaders` — Меш-шейдеры и генерация геометрии на GPU | 2 | 2 |
| `particle_systems` — Системы частиц | 4 | 2 |
| `path_tracing` — Трассировка пути | 2 | 2 |
| `physics_simulation` — Физическая симуляция | 5 | 2 |
| `portal_rendering` — Дополнительные виды и порталы | 1 | 2 |
| `post_processing` — Постобработка изображения | 7 | 2 |
| `procedural_vegetation` — Растительность и объекты окружения | 5 | 2 |
| `project_architecture` — Архитектура проекта | 1 | 2 |
| `ray_traced_effects` — Трассировочные эффекты (тени, отражения, AO) | 2 | 2 |
| `render_scalability` — Масштабирование качества | 1 | 2 |
| `runtime_memory` — Память и сборка мусора | 1 | 2 |
| `runtime_security` — Проверки целостности и античит | 1 | 2 |
| `save_system` — Система сохранений | 2 | 2 |
| `storage_streaming` — Потоковая работа с накопителем | 0 | 2 |
| `vehicle_simulation` — Транспорт и физика движения | 2 | 2 |
| `volumetric_effects` — Объёмные эффекты (туман, облака, дымка) | 2 | 2 |
| `water_simulation` — Водные поверхности | 3 | 2 |

### I.2. Движки и разметка пригодности

Поддержаны движки: `cryengine`, `custom`, `godot`, `heroengine`, `source`, `unity`, `unreal`.
Игра считается **покрытой**, если её движок есть в каталоге и для всех её функций опубликован хотя бы один метод; **частично** — если часть функций без методов; **движок вне каталога** — если движок не поддерживается.

| Год | Игра | Движок | Функции | Покрытие |
| ---: | --- | --- | ---: | --- |
| 2025 | Split Fiction | не указан | 1 | покрыт |
| 2025 | Split Fiction | не указан | 1 | покрыт |
| 2024 | Unity DOTS production examples | Unity | 1 | покрыт |
| 2023 | Alan Wake 2 | не указан | 10 | покрыт |
| 2023 | Alan Wake 2 | не указан | 11 | покрыт |
| 2023 | Counter-Strike 2 | Source / Source 2 | 1 | покрыт |
| 2023 | Cyberpunk 2077 | не указан | 1 | покрыт |
| 2021 | It Takes Two | Unreal Engine | 1 | покрыт |
| 2021 | It Takes Two | не указан | 1 | покрыт |
| 2021 | Returnal | не указан | 2 | покрыт |
| 2021 | Returnal | не указан | 3 | покрыт |
| 2021 | Unreal Engine City Sample | Unreal Engine | 3 | покрыт |
| 2020 | Cyberpunk 2077 | не указан | 1 | покрыт |
| 2020 | Cyberpunk 2077 | не указан | 1 | покрыт |
| 2020 | DOOM Eternal | собственный движок | 1 | покрыт |
| 2020 | DOOM Eternal | не указан | 3 | покрыт |
| 2020 | DOOM Eternal | не указан | 6 | покрыт |
| 2020 | VALORANT | собственный движок | 1 | покрыт |
| 2019 | Hunt: Showdown | CryEngine | 1 | покрыт |
| 2019 | Justice (Ni Shui Han) | не указан | 1 | покрыт |
| 2019 | Metro Exodus | не указан | 1 | покрыт |
| 2018 | Battlefield V | не указан | 2 | покрыт |
| 2018 | Battlefield V | не указан | 1 | покрыт |
| 2018 | Just Cause 4 | не указан | 1 | покрыт |
| 2018 | Just Cause 4 | не указан | 1 | покрыт |
| 2017 | Fortnite Battle Royale | не указан | 1 | покрыт |
| 2017 | Horizon Zero Dawn | не указан | 3 | частично |
| 2017 | Horizon Zero Dawn | не указан | 3 | покрыт |
| 2016 | No Man's Sky | не указан | 2 | частично |
| 2016 | No Man's Sky | не указан | 3 | покрыт |
| 2016 | Overwatch | не указан | 1 | покрыт |
| 2016 | Overwatch | не указан | 2 | покрыт |
| 2016 | Uncharted 4: A Thief's End | не указан | 1 | покрыт |
| 2016 | Uncharted 4: A Thief's End | не указан | 1 | покрыт |
| 2014 | Assassin's Creed Unity | не указан | 1 | покрыт |
| 2011 | Portal 2 | не указан | 2 | покрыт |
| 2010 | Supreme Commander 2 | не указан | 1 | покрыт |
| 2010 | Supreme Commander 2 | не указан | 1 | покрыт |
| 2009 | Red Faction: Guerrilla | не указан | 1 | покрыт |
| 2009 | Red Faction: Guerrilla | не указан | 2 | покрыт |
| 2008 | Left 4 Dead | Source / Source 2 | 1 | покрыт |
| 2008 | Left 4 Dead | не указан | 3 | покрыт |
| 2005 | F.E.A.R. | не указан | 1 | покрыт |
| 2005 | F.E.A.R. | не указан | 1 | покрыт |
| — | Justice (Ni Shui Han) | не указан | 2 | покрыт |
| — | Valley of the Ancient (Epic UE5 sample) | не указан | 1 | покрыт |

### I.3. Отобранные 25 сценариев

Для тестирования выбраны игры, которые (а) документированы публично и (б) ложатся на поддержанные функции каталога. Отмечено, какие из них пригодны для прогона.

| № | Игра | Движок | Функции профиля | Пригодна |
| --- | --- | --- | --- | --- |
| S01 | Left 4 Dead (2008) | Source / Source 2 | `advanced_npc_ai`, `crowd_simulation`, `ai_pathfinding` | да |
| S02 | Counter-Strike 2 (2023) | Source / Source 2 | `multiplayer_netcode` | да |
| S03 | Portal 2 (2011) | Source / Source 2 | `portal_rendering`, `water_simulation` | да |
| S04 | It Takes Two (2021) | Unreal Engine | `split_screen_rendering`, `upscaling_frame_generation`, `post_processing` | да |
| S05 | Split Fiction (2025) | Unreal Engine | `split_screen_rendering`, `multiplayer_netcode`, `dynamic_global_illumination` | да |
| S06 | Unreal Engine City Sample (2021) | Unreal Engine | `open_world_streaming`, `geometry_pipeline`, `procedural_terrain`, `dynamic_global_illumination`, `dynamic_shadows`, `crowd_simulation` | да |
| S07 | Fortnite (2017) | Unreal Engine | `multiplayer_netcode`, `open_world_streaming`, `geometry_pipeline`, `dynamic_shadows` | да |
| S08 | VALORANT (2020) | собственный движок | `multiplayer_netcode`, `runtime_security` | да |
| S09 | DOOM Eternal (2020) | собственный движок | `rendering_architecture`, `mesh_shaders`, `particle_systems`, `destruction_simulation`, `render_scalability` | да |
| S10 | Cyberpunk 2077 (2020) | собственный движок | `open_world_streaming`, `dynamic_global_illumination`, `ray_traced_effects`, `dynamic_shadows` | да |
| S11 | No Man's Sky (2016) | собственный движок | `procedural_terrain`, `open_world_streaming`, `storage_streaming`, `save_system`, `build_delivery` | да |
| S12 | Microsoft Flight Simulator (2020) | собственный движок | `large_scale_terrain`, `open_world_streaming`, `storage_streaming`, `procedural_vegetation` | да |
| S13 | Teardown (2020) | собственный движок | `destruction_simulation`, `physics_simulation`, `geometry_pipeline`, `ray_traced_effects` | да |
| S14 | BeamNG.drive (2015) | собственный движок | `vehicle_simulation`, `physics_simulation`, `destruction_simulation` | да |
| S15 | Ashes of the Singularity (2016) | собственный движок | `crowd_simulation`, `ai_pathfinding`, `particle_systems`, `rendering_architecture` | да |
| S16 | Horizon Zero Dawn (2017) | собственный движок | `open_world_streaming`, `large_scale_terrain`, `procedural_vegetation`, `character_animation` | да |
| S17 | Alan Wake 2 (2023) | собственный движок | `path_tracing`, `dynamic_global_illumination`, `mesh_shaders`, `hair_rendering`, `volumetric_effects`, `rendering_architecture` | да |
| S18 | F.E.A.R. (2005) | собственный движок | `advanced_npc_ai`, `ai_pathfinding`, `dynamic_shadows` | да |
| S19 | Uncharted 4: A Thief's End (2016) | собственный движок | `character_animation`, `art_pipeline`, `post_processing`, `dynamic_shadows` | да |
| S20 | Red Faction: Guerrilla (2009) | собственный движок | `destruction_simulation`, `physics_simulation`, `open_world_streaming`, `vehicle_simulation` | да |
| S21 | Minecraft (2011) | собственный движок | `procedural_terrain`, `runtime_memory`, `save_system`, `storage_streaming` | да |
| S22 | Hunt: Showdown (2019) | CryEngine | `audio_system`, `open_world_streaming`, `procedural_vegetation` | да |
| S23 | V Rising (2022) | Unity | `crowd_simulation`, `ai_pathfinding`, `runtime_memory`, `character_animation` | да |
| S24 | Brotato (2023) | Godot | `crowd_simulation`, `particle_systems`, `render_scalability`, `character_animation`, `save_system` | да |
| S25 | Star Wars: The Old Republic (2011) | HeroEngine | `multiplayer_netcode`, `save_system`, `open_world_streaming`, `character_animation` | да |

## Часть II. Результаты по сценариям

### S01. Left 4 Dead — Valve, 2008

*Движок: Source / Source 2. Source (2008): AI Director управляет темпом, а не сложностью.*

**Сценарий (профиль проекта).** формат 3D, мир linear, масштаб medium, стадия production, цель 1080p/medium/60 FPS, функции: advanced_npc_ai, crowd_simulation, ai_pathfinding.

**Корзина (техники игры):** `ai_director_pacing`, `behaviour_tree_update_budget`, `agent_update_budget`, `time_sliced_pathfinding`.

**Результат проекта.**

- Кандидатов: 32, рекомендовано: 25, исключено: 7.
- Учтено в расчёте: 4 из 4 выбранных техник.
- Первое место по каждой функции: `advanced_npc_ai` → `npc_perception_budget`; `ai_pathfinding` → `rvo_local_avoidance`; `art_pipeline` → `normal_bake_retopology_pipeline`; `audio_system` → `audio_streaming_compression`; `build_delivery` → `differential_patch_pipeline`; `crowd_simulation` → `agent_update_budget`; `geometry_pipeline` → `mesh_index_optimization`; `open_world_streaming` → `baked_occlusion_culling`; `project_architecture` → `composition_bootstrap_architecture`; `render_scalability` → `quality_tier_scalability`; `rendering_architecture` → `tiled_clustered_light_culling`; `upscaling_frame_generation` → `ml_frame_generation`.
- Оборудование: CPU-индекс 0.25 (класс 2, ориентир Core i3-10100), GPU-индекс 0.16 (класс 2, ориентир Radeon RX 580), RAM 11.1 ГБ, VRAM 5.9 ГБ; узкое место — CPU (главный поток).
- Календарь (команда `small_2_5`): трудоёмкость P50 34.23 чел.-дн., P80 51.32; срок P50 21.31 дн., P80 31.93.
- Объявленных пробелов модели: 8.

**Эталонное поведение игры.**

- AI Director оценивает «Survivor Intensity», повышает её событиями и постепенно снижает; регулируется темп (pacing), а не обязательно амплитуда сложности. *(каталог проекта)*
- Директор процедурно управляет населением угроз и предметами между «пиками» и «затишьями», а не расставляет врагов вручную. *(публичная документация)*
- Игра вышла в 2008 году и работала на GPU того времени; CPU-бюджет тратился на поведение десятков заражённых. *(публичная документация)*

**Выявленные отличия.**

- **Расхождение ранга:** игра применяет `ai_director_pacing`, а движок ставит его на 3-е место из 3 в группе `advanced_npc_ai`; первым идёт `npc_perception_budget`. Причина — критерии TOPSIS: у `ai_director_pacing` экспертный балл эффекта 0.3, стоимость внедрения 4, сложность 4, штраф за позднее внедрение `high`.
- **Совпадение:** ключевая техника игры `agent_update_budget` стоит на 1-м месте в своей группе (crowd_simulation).
- **FPS не моделируется:** целевые 60.0 FPS остаются статусом `not_modeled`; сравнить с фактической частотой кадров игры нельзя по устройству модели.

### S02. Counter-Strike 2 — Valve, 2023

*Движок: Source / Source 2. Source 2 (2023): sub-tick обновления — определяющая техника соревновательного шутера.*

**Сценарий (профиль проекта).** формат 3D, мир arena, масштаб small, стадия production, цель 1080p/low/240 FPS, функции: multiplayer_netcode.

**Корзина (техники игры):** `subtick_networking`, `lag_compensation_rewind`, `network_relevancy_priority`, `tickrate_budgeting`.

**Результат проекта.**

- Кандидатов: 27, рекомендовано: 23, исключено: 4.
- Учтено в расчёте: 2 из 4 выбранных техник.
- Первое место по каждой функции: `art_pipeline` → `normal_bake_retopology_pipeline`; `audio_system` → `audio_streaming_compression`; `build_delivery` → `differential_patch_pipeline`; `geometry_pipeline` → `mesh_index_optimization`; `multiplayer_netcode` → `headless_dedicated_server`; `open_world_streaming` → `baked_occlusion_culling`; `project_architecture` → `composition_bootstrap_architecture`; `render_scalability` → `quality_tier_scalability`; `rendering_architecture` → `tiled_clustered_light_culling`; `upscaling_frame_generation` → `ml_frame_generation`.
- Оборудование: CPU-индекс 1.05 (класс 5, ориентир None), GPU-индекс 0.48 (класс 3, ориентир GeForce RTX 3060 Ti), RAM 9.7 ГБ, VRAM 4.6 ГБ; узкое место — CPU (главный поток).
- Календарь (команда `small_2_5`): трудоёмкость P50 64.45 чел.-дн., P80 96.73; срок P50 41.75 дн., P80 62.68.
- Объявленных пробелов модели: 6.

**Эталонное поведение игры.**

- Valve описывает sub-tick updates как механизм, при котором сервер знает точный момент движения, выстрела или броска между тактами. *(каталог проекта)*
- Целевые 240+ FPS и низкая задержка ввода — продуктовое требование, а не следствие оптимизации кадра. *(публичная документация)*
- Реконсиляция и лаг-компенсация — базовые механизмы соревновательного неткода Source 2. *(публичная документация)*

**Выявленные отличия.**

- **Расхождение ранга:** игра применяет `subtick_networking`, а движок ставит его на 8-е место из 8 в группе `multiplayer_netcode`; первым идёт `headless_dedicated_server`. Причина — критерии TOPSIS: у `subtick_networking` экспертный балл эффекта 0.3, стоимость внедрения 4, сложность 5, штраф за позднее внедрение `high`.
- **Расхождение ранга:** игра применяет `lag_compensation_rewind`, а движок ставит его на 7-е место из 8 в группе `multiplayer_netcode`; первым идёт `headless_dedicated_server`. Причина — критерии TOPSIS: у `lag_compensation_rewind` экспертный балл эффекта 0.3, стоимость внедрения 4, сложность 4, штраф за позднее внедрение `high`.
- **Не учтено в расчёте нагрузки:** 2 из 4 выбранных техник (`subtick_networking`, `lag_compensation_rewind`) исключены из профиля нагрузки и оценки оборудования из-за отсутствующих обязательных зависимостей.
- **Ориентир по процессору не выдан:** требуемый CPU-индекс 1.05 превышает максимум каталога — модель насыщается и не может предложить конкретную модель.
- **Выход за область применимости модели:** Целевой FPS 240 выше откалиброванного диапазона (30–144): стоимость кадра экстраполирована.
- **FPS не моделируется:** целевые 240.0 FPS остаются статусом `not_modeled`; сравнить с фактической частотой кадров игры нельзя по устройству модели.

### S03. Portal 2 — Valve, 2011

*Движок: Source / Source 2. Source (2011): порталы требуют дополнительного рендера сцены в текстуру.*

**Сценарий (профиль проекта).** формат 3D, мир linear, масштаб small, стадия production, цель 1080p/high/60 FPS, функции: portal_rendering, water_simulation.

**Корзина (техники игры):** `portal_scene_capture_budget`, `planar_reflection_budget`.

**Результат проекта.**

- Кандидатов: 25, рекомендовано: 19, исключено: 6.
- Учтено в расчёте: 1 из 2 выбранных техник.
- Первое место по каждой функции: `art_pipeline` → `normal_bake_retopology_pipeline`; `audio_system` → `audio_streaming_compression`; `build_delivery` → `differential_patch_pipeline`; `geometry_pipeline` → `mesh_index_optimization`; `open_world_streaming` → `baked_occlusion_culling`; `portal_rendering` → `portal_scene_capture_budget`; `project_architecture` → `composition_bootstrap_architecture`; `render_scalability` → `quality_tier_scalability`; `rendering_architecture` → `tiled_clustered_light_culling`; `upscaling_frame_generation` → `ml_frame_generation`; `water_simulation` → `screen_space_water_simple`.
- Оборудование: CPU-индекс 0.28 (класс 1, ориентир Core i3-8100), GPU-индекс 0.23 (класс 2, ориентир Radeon RX 6500 XT), RAM 10.1 ГБ, VRAM 5.5 ГБ; узкое место — CPU (главный поток).
- Календарь (команда `small_2_5`): трудоёмкость P50 24.45 чел.-дн., P80 36.69; срок P50 17.62 дн., P80 26.44.
- Объявленных пробелов модели: 6.

**Эталонное поведение игры.**

- Портал в Portal 2 — это отдельный вид сцены, отрисованный в текстуру и показанный на плоскости; рекурсия порталов ограничивается бюджетом. *(публичная документация)*
- Вода и отражения в Source — плоские отражения с ограничением по разрешению и числу проходов. *(публичная документация)*

**Выявленные отличия.**

- **Совпадение:** ключевая техника игры `portal_scene_capture_budget` стоит на 1-м месте в своей группе (portal_rendering).
- **Не учтено в расчёте нагрузки:** 1 из 2 выбранных техник (`portal_scene_capture_budget`) исключены из профиля нагрузки и оценки оборудования из-за отсутствующих обязательных зависимостей.
- **FPS не моделируется:** целевые 60.0 FPS остаются статусом `not_modeled`; сравнить с фактической частотой кадров игры нельзя по устройству модели.

### S04. It Takes Two — Hazelight, 2021

*Движок: Unreal Engine. Unreal Engine 4 (2021): split-screen на два вьюпорта.*

**Сценарий (профиль проекта).** формат 3D, мир linear, масштаб medium, стадия production, цель 1080p/high/60 FPS, функции: split_screen_rendering, upscaling_frame_generation, post_processing.

**Корзина (техники игры):** `splitscreen_render_budget`, `temporal_upscaling`, `dynamic_resolution_scaling`.

**Результат проекта.**

- Кандидатов: 28, рекомендовано: 22, исключено: 6.
- Учтено в расчёте: 2 из 3 выбранных техник.
- Первое место по каждой функции: `art_pipeline` → `normal_bake_retopology_pipeline`; `audio_system` → `audio_streaming_compression`; `build_delivery` → `differential_patch_pipeline`; `geometry_pipeline` → `mesh_index_optimization`; `open_world_streaming` → `baked_occlusion_culling`; `post_processing` → `temporal_upscaling`; `project_architecture` → `composition_bootstrap_architecture`; `render_scalability` → `quality_tier_scalability`; `rendering_architecture` → `tiled_clustered_light_culling`; `split_screen_rendering` → `splitscreen_render_budget`; `upscaling_frame_generation` → `ml_frame_generation`.
- Оборудование: CPU-индекс 0.5 (класс 3, ориентир Core i7-8700K), GPU-индекс 0.28 (класс 2, ориентир GeForce RTX 3050), RAM 11.4 ГБ, VRAM 7.1 ГБ; узкое место — CPU (главный поток).
- Календарь (команда `small_2_5`): трудоёмкость P50 32.26 чел.-дн., P80 48.33; срок P50 20.61 дн., P80 30.86.
- Объявленных пробелов модели: 7.

**Эталонное поведение игры.**

- Публичный технический разбор связывает кооперативный split-screen с отдельными видами и стоимостью рендеринга (Digital Foundry). *(каталог проекта)*
- Локальные вьюпорты увеличивают клиентскую работу, но не равны сетевым игрокам: это рендер-нагрузка, а не сетевой трафик. *(каталог проекта)*

**Выявленные отличия.**

- **Совпадение:** ключевая техника игры `splitscreen_render_budget` стоит на 1-м месте в своей группе (split_screen_rendering).
- **Не учтено в расчёте нагрузки:** 1 из 3 выбранных техник (`splitscreen_render_budget`) исключены из профиля нагрузки и оценки оборудования из-за отсутствующих обязательных зависимостей.
- **Выход за область применимости модели:** Количественный прогноз доступен только для Windows/Linux ПК: для платформ (ps4, xbox_one) совместимый аппаратный прогноз не обещается.
- **FPS не моделируется:** целевые 60.0 FPS остаются статусом `not_modeled`; сравнить с фактической частотой кадров игры нельзя по устройству модели.

### S05. Split Fiction — Hazelight, 2025

*Движок: Unreal Engine. Unreal Engine 5 (2025): split-screen кооп с онлайн-синхронизацией.*

**Сценарий (профиль проекта).** формат 3D, мир linear, масштаб large, стадия production, цель 1440p/high/60 FPS, функции: split_screen_rendering, multiplayer_netcode, dynamic_global_illumination.

**Корзина (техники игры):** `splitscreen_render_budget`, `client_prediction_reconciliation`, `network_relevancy_priority`, `hardware_raytraced_gi`.

**Результат проекта.**

- Кандидатов: 33, рекомендовано: 30, исключено: 3.
- Учтено в расчёте: 1 из 4 выбранных техник.
- Первое место по каждой функции: `art_pipeline` → `normal_bake_retopology_pipeline`; `audio_system` → `audio_streaming_compression`; `build_delivery` → `differential_patch_pipeline`; `dynamic_global_illumination` → `screen_space_gi`; `geometry_pipeline` → `mesh_index_optimization`; `multiplayer_netcode` → `headless_dedicated_server`; `open_world_streaming` → `baked_occlusion_culling`; `project_architecture` → `composition_bootstrap_architecture`; `render_scalability` → `quality_tier_scalability`; `rendering_architecture` → `tiled_clustered_light_culling`; `split_screen_rendering` → `splitscreen_render_budget`; `upscaling_frame_generation` → `ml_frame_generation`.
- Оборудование: CPU-индекс 0.53 (класс 3, ориентир Core i7-9700K), GPU-индекс 0.48 (класс 3, ориентир GeForce RTX 5060 Ti), RAM 13.5 ГБ, VRAM 10.6 ГБ; узкое место — CPU (главный поток).
- Календарь (команда `small_2_5`): трудоёмкость P50 117.23 чел.-дн., P80 175.86; срок P50 70.07 дн., P80 105.12.
- Объявленных пробелов модели: 6.

**Эталонное поведение игры.**

- Hazelight продолжает схему It Takes Two: два постоянных вьюпорта и обязательная кооперативная механика. *(публичная документация)*
- Онлайн-кооп требует предсказания и реконсиляции, но основная стоимость кадра — двойной рендер, а не сеть. *(публичная документация)*

**Выявленные отличия.**

- **Совпадение:** ключевая техника игры `splitscreen_render_budget` стоит на 1-м месте в своей группе (split_screen_rendering).
- **Не учтено в расчёте нагрузки:** 3 из 4 выбранных техник (`splitscreen_render_budget`, `client_prediction_reconciliation`, `hardware_raytraced_gi`) исключены из профиля нагрузки и оценки оборудования из-за отсутствующих обязательных зависимостей.
- **Выход за область применимости модели:** Количественный прогноз доступен только для Windows/Linux ПК: для платформ (ps5, xbox_series) совместимый аппаратный прогноз не обещается.
- **FPS не моделируется:** целевые 60.0 FPS остаются статусом `not_modeled`; сравнить с фактической частотой кадров игры нельзя по устройству модели.

### S06. Unreal Engine City Sample — Epic Games, 2021

*Движок: Unreal Engine. Unreal Engine 5 City Sample (2021): reference-проект World Partition + Nanite + Lumen + Mass AI.*

**Сценарий (профиль проекта).** формат 3D, мир open_world, масштаб very_large, стадия prototype, цель 1440p/high/30 FPS, функции: open_world_streaming, geometry_pipeline, procedural_terrain, dynamic_global_illumination, dynamic_shadows, crowd_simulation.

**Корзина (техники игры):** `world_partition_streaming`, `virtual_geometry_clusters`, `hierarchical_lod`, `chunked_procedural_terrain`, `hardware_raytraced_gi`, `virtual_shadow_maps`, `ecs_data_oriented_crowd`.

**Результат проекта.**

- Кандидатов: 46, рекомендовано: 35, исключено: 11.
- Учтено в расчёте: 3 из 7 выбранных техник.
- Первое место по каждой функции: `art_pipeline` → `normal_bake_retopology_pipeline`; `audio_system` → `audio_streaming_compression`; `build_delivery` → `differential_patch_pipeline`; `crowd_simulation` → `agent_update_budget`; `dynamic_global_illumination` → `screen_space_gi`; `dynamic_shadows` → `screen_space_contact_shadows`; `geometry_pipeline` → `mesh_index_optimization`; `open_world_streaming` → `gpu_compute_culling`; `procedural_terrain` → `terrain_generation_streaming_budget`; `project_architecture` → `composition_bootstrap_architecture`; `render_scalability` → `quality_tier_scalability`; `rendering_architecture` → `tiled_clustered_light_culling`; `upscaling_frame_generation` → `ml_frame_generation`.
- Оборудование: CPU-индекс 0.22 (класс 1, ориентир Core i3-8100), GPU-индекс 0.43 (класс 3, ориентир Radeon RX 9060 XT), RAM 17.4 ГБ, VRAM 14.4 ГБ; узкое место — GPU (растеризация).
- Календарь (команда `small_2_5`): трудоёмкость P50 151.87 чел.-дн., P80 227.84; срок P50 88.76 дн., P80 133.15.
- Объявленных пробелов модели: 8.

**Эталонное поведение игры.**

- City Sample использует World Partition и on-demand loading cells для большого города. *(каталог проекта)*
- Документация описывает Nanite на static meshes с высокополигональными исходниками и динамическим изменением представления. *(каталог проекта)*
- City Sample PCG documentation содержит процедурную конфигурацию города, PCG graphs и shape grammar assets. *(каталог проекта)*
- Mass AI обслуживает десятки тысяч агентов; Lumen и VSM задают стоимость кадра. *(публичная документация)*

**Выявленные отличия.**

- **Расхождение ранга:** игра применяет `world_partition_streaming`, а движок ставит его на 4-е место из 5 в группе `open_world_streaming`; первым идёт `gpu_compute_culling`. Причина — критерии TOPSIS: у `world_partition_streaming` экспертный балл эффекта 0.75, стоимость внедрения 4, сложность 4, штраф за позднее внедрение `critical`.
- **Не предложено:** техника игры `virtual_geometry_clusters` даже не попала в кандидаты: её функция не выбрана в профиле, а сама она не помечена как сквозная.
- **Расхождение ранга:** игра применяет `hierarchical_lod`, а движок ставит его на 2-е место из 5 в группе `open_world_streaming`; первым идёт `gpu_compute_culling`. Причина — критерии TOPSIS: у `hierarchical_lod` экспертный балл эффекта 0.75, стоимость внедрения 3, сложность 3, штраф за позднее внедрение `medium`.
- **Не учтено в расчёте нагрузки:** 4 из 7 выбранных техник (`world_partition_streaming`, `virtual_geometry_clusters`, `hierarchical_lod`, `hardware_raytraced_gi`) исключены из профиля нагрузки и оценки оборудования из-за отсутствующих обязательных зависимостей.
- **Выход за область применимости модели:** Число NPC (35 000) выше верхней границы модели (10 000): оценка не различает значения внутри этой области, результат является нижней границей диапазона.; Количественный прогноз доступен только для Windows/Linux ПК: для платформ (ps5, xbox_series) совместимый аппаратный прогноз не обещается.
- **FPS не моделируется:** целевые 30.0 FPS остаются статусом `not_modeled`; сравнить с фактической частотой кадров игры нельзя по устройству модели.

### S07. Fortnite — Epic Games, 2017

*Движок: Unreal Engine. Unreal Engine 5 (2017→): 100 игроков, World Partition, выделенные серверы.*

**Сценарий (профиль проекта).** формат 3D, мир open_world, масштаб large, стадия release, цель 1080p/high/60 FPS, функции: multiplayer_netcode, open_world_streaming, geometry_pipeline, dynamic_shadows.

**Корзина (техники игры):** `client_prediction_reconciliation`, `network_relevancy_priority`, `delta_compression_state`, `world_partition_streaming`, `virtual_geometry_clusters`, `virtual_shadow_maps`.

**Результат проекта.**

- Кандидатов: 40, рекомендовано: 32, исключено: 8.
- Учтено в расчёте: 2 из 6 выбранных техник.
- Первое место по каждой функции: `art_pipeline` → `normal_bake_retopology_pipeline`; `audio_system` → `audio_streaming_compression`; `build_delivery` → `differential_patch_pipeline`; `dynamic_shadows` → `screen_space_contact_shadows`; `geometry_pipeline` → `mesh_index_optimization`; `multiplayer_netcode` → `delta_compression_state`; `open_world_streaming` → `gpu_compute_culling`; `project_architecture` → `composition_bootstrap_architecture`; `render_scalability` → `quality_tier_scalability`; `rendering_architecture` → `tiled_clustered_light_culling`; `upscaling_frame_generation` → `ml_frame_generation`.
- Оборудование: CPU-индекс 0.43 (класс 2, ориентир Core i3-10100), GPU-индекс 0.28 (класс 3, ориентир GeForce RTX 3060), RAM 14.7 ГБ, VRAM 9.4 ГБ; узкое место — CPU (главный поток).
- Календарь (команда `small_2_5`): трудоёмкость P50 110.67 чел.-дн., P80 166.09; срок P50 66.41 дн., P80 99.66.
- Объявленных пробелов модели: 8.

**Эталонное поведение игры.**

- Fortnite переведён на UE5 с World Partition и Nanite; карта стримится по ячейкам. *(публичная документация)*
- Battle royale на 100 игроков требует серверной релевантности и приоритизации, а не только дельта-сжатия. *(публичная документация)*
- Эпик описывает выделенные серверы как основу сетевой модели. *(публичная документация)*

**Выявленные отличия.**

- **Расхождение ранга:** игра применяет `world_partition_streaming`, а движок ставит его на 4-е место из 5 в группе `open_world_streaming`; первым идёт `gpu_compute_culling`. Причина — критерии TOPSIS: у `world_partition_streaming` экспертный балл эффекта 0.75, стоимость внедрения 4, сложность 4, штраф за позднее внедрение `critical`.
- **Расхождение ранга:** игра применяет `client_prediction_reconciliation`, а движок ставит его на 7-е место из 8 в группе `multiplayer_netcode`; первым идёт `delta_compression_state`. Причина — критерии TOPSIS: у `client_prediction_reconciliation` экспертный балл эффекта 0.3, стоимость внедрения 5, сложность 5, штраф за позднее внедрение `critical`.
- **Не учтено в расчёте нагрузки:** 4 из 6 выбранных техник (`client_prediction_reconciliation`, `delta_compression_state`, `world_partition_streaming`, `virtual_geometry_clusters`) исключены из профиля нагрузки и оценки оборудования из-за отсутствующих обязательных зависимостей.
- **Выход за область применимости модели:** Число игроков (100) выше порога различения (32): сетевой вклад оценён по насыщению.; Количественный прогноз доступен только для Windows/Linux ПК: для платформ (ps5, switch, xbox_series) совместимый аппаратный прогноз не обещается.
- **FPS не моделируется:** целевые 60.0 FPS остаются статусом `not_modeled`; сравнить с фактической частотой кадров игры нельзя по устройству модели.

### S08. VALORANT — Riot Games, 2020

*Движок: собственный движок. Собственный движок (2020): 128-tick серверная модель.*

**Сценарий (профиль проекта).** формат 3D, мир arena, масштаб small, стадия release, цель 1080p/low/144 FPS, функции: multiplayer_netcode, runtime_security.

**Корзина (техники игры):** `tickrate_budgeting`, `lag_compensation_rewind`, `network_relevancy_priority`, `runtime_security_budget`.

**Результат проекта.**

- Кандидатов: 28, рекомендовано: 25, исключено: 3.
- Учтено в расчёте: 2 из 4 выбранных техник.
- Первое место по каждой функции: `art_pipeline` → `normal_bake_retopology_pipeline`; `audio_system` → `audio_streaming_compression`; `build_delivery` → `differential_patch_pipeline`; `geometry_pipeline` → `mesh_index_optimization`; `multiplayer_netcode` → `delta_compression_state`; `open_world_streaming` → `baked_occlusion_culling`; `project_architecture` → `composition_bootstrap_architecture`; `render_scalability` → `quality_tier_scalability`; `rendering_architecture` → `tiled_clustered_light_culling`; `runtime_memory` → `managed_gc_alloc_budget`; `runtime_security` → `runtime_security_budget`; `upscaling_frame_generation` → `ml_frame_generation`.
- Оборудование: CPU-индекс 0.63 (класс 3, ориентир Core i5-12400F), GPU-индекс 0.29 (класс 2, ориентир GeForce GTX 1660), RAM 9.7 ГБ, VRAM 4.6 ГБ; узкое место — CPU (главный поток).
- Календарь (команда `small_2_5`): трудоёмкость P50 75.89 чел.-дн., P80 113.89; срок P50 47.99 дн., P80 72.03.
- Объявленных пробелов модели: 9.

**Эталонное поведение игры.**

- Riot связывает серверную производительность с задачами hit registration, peeker's advantage и simulation divergence. *(каталог проекта)*
- Публичный материал Riot описывает 128-tick server performance как инженерную цель сервиса VALORANT. *(каталог проекта)*
- Соревновательный шутер сознательно жертвует качеством картинки ради отзывчивости и читаемости. *(публичная документация)*

**Выявленные отличия.**

- **Расхождение ранга:** игра применяет `tickrate_budgeting`, а движок ставит его на 5-е место из 8 в группе `multiplayer_netcode`; первым идёт `delta_compression_state`. Причина — критерии TOPSIS: у `tickrate_budgeting` экспертный балл эффекта 0.6, стоимость внедрения 3, сложность 3, штраф за позднее внедрение `critical`.
- **Расхождение ранга:** игра применяет `lag_compensation_rewind`, а движок ставит его на 6-е место из 8 в группе `multiplayer_netcode`; первым идёт `delta_compression_state`. Причина — критерии TOPSIS: у `lag_compensation_rewind` экспертный балл эффекта 0.3, стоимость внедрения 4, сложность 4, штраф за позднее внедрение `high`.
- **Не учтено в расчёте нагрузки:** 2 из 4 выбранных техник (`lag_compensation_rewind`, `runtime_security_budget`) исключены из профиля нагрузки и оценки оборудования из-за отсутствующих обязательных зависимостей.
- **FPS не моделируется:** целевые 144.0 FPS остаются статусом `not_modeled`; сравнить с фактической частотой кадров игры нельзя по устройству модели.

### S09. DOOM Eternal — id Software, 2020

*Движок: собственный движок. Собственный движок id Tech 7 (2020): целевой frame rate как проектная цель.*

**Сценарий (профиль проекта).** формат 3D, мир linear, масштаб medium, стадия production, цель 1080p/high/60 FPS, функции: rendering_architecture, mesh_shaders, particle_systems, destruction_simulation, render_scalability.

**Корзина (техники игры):** `depth_prepass_early_z`, `async_compute_overlap`, `tiled_clustered_light_culling`, `gpu_particle_simulation`, `destruction_geometry_cache`, `pso_precaching_warmup`.

**Результат проекта.**

- Кандидатов: 29, рекомендовано: 21, исключено: 8.
- Учтено в расчёте: 4 из 6 выбранных техник.
- Первое место по каждой функции: `art_pipeline` → `normal_bake_retopology_pipeline`; `audio_system` → `audio_streaming_compression`; `build_delivery` → `differential_patch_pipeline`; `destruction_simulation` → `runtime_fracture_budget`; `geometry_pipeline` → `mesh_index_optimization`; `open_world_streaming` → `baked_occlusion_culling`; `particle_systems` → `particle_pooling`; `project_architecture` → `composition_bootstrap_architecture`; `render_scalability` → `quality_tier_scalability`; `rendering_architecture` → `tiled_clustered_light_culling`; `runtime_memory` → `managed_gc_alloc_budget`; `upscaling_frame_generation` → `ml_frame_generation`.
- Оборудование: CPU-индекс 0.35 (класс 1, ориентир Core i3-8100), GPU-индекс 0.35 (класс 2, ориентир Arc A750), RAM 12.1 ГБ, VRAM 7.0 ГБ; узкое место — GPU (растеризация).
- Календарь (команда `small_2_5`): трудоёмкость P50 73.44 чел.-дн., P80 110.2; срок P50 44.97 дн., P80 67.49.
- Объявленных пробелов модели: 8.

**Эталонное поведение игры.**

- Команда id Software описывает несколько специализированных подсистем рендера и workflow, позволивших удерживать целевую частоту кадров (SIGGRAPH 2020). *(каталог проекта)*
- Geometry caches, gore, decals и material compositing — ключевые подсистемы, а не отдельные оптимизации. *(каталог проекта)*
- Частицы и эффекты горят на GPU; разрушение — часть геймплея, а не декорация. *(публичная документация)*

**Выявленные отличия.**

- **Расхождение ранга:** игра применяет `gpu_particle_simulation`, а движок ставит его на 3-е место из 3 в группе `particle_systems`; первым идёт `particle_pooling`. Причина — критерии TOPSIS: у `gpu_particle_simulation` экспертный балл эффекта 0.7, стоимость внедрения 3, сложность 3, штраф за позднее внедрение `medium`.
- **Исключение:** техника игры `destruction_geometry_cache` исключена — Метод требует наличия функции «physics_simulation», которая не выбрана в профиле..
- **Расхождение ранга:** игра применяет `async_compute_overlap`, а движок ставит его на 5-е место из 5 в группе `rendering_architecture`; первым идёт `tiled_clustered_light_culling`. Причина — критерии TOPSIS: у `async_compute_overlap` экспертный балл эффекта 0.4, стоимость внедрения 4, сложность 5, штраф за позднее внедрение `high`.
- **Не учтено в расчёте нагрузки:** 2 из 6 выбранных техник (`depth_prepass_early_z`, `destruction_geometry_cache`) исключены из профиля нагрузки и оценки оборудования из-за отсутствующих обязательных зависимостей.
- **Выход за область применимости модели:** Количественный прогноз доступен только для Windows/Linux ПК: для платформ (ps4, xbox_one) совместимый аппаратный прогноз не обещается.
- **FPS не моделируется:** целевые 60.0 FPS остаются статусом `not_modeled`; сравнить с фактической частотой кадров игры нельзя по устройству модели.

### S10. Cyberpunk 2077 — CD Projekt Red, 2020

*Движок: собственный движок. Собственный движок REDengine (2020): открытый мир + трассировка лучей (RT Overdrive).*

**Сценарий (профиль проекта).** формат 3D, мир open_world, масштаб very_large, стадия release, цель 1440p/ultra/60 FPS, функции: open_world_streaming, dynamic_global_illumination, ray_traced_effects, dynamic_shadows.

**Корзина (техники игры):** `world_partition_streaming`, `hardware_raytraced_gi`, `selective_ray_traced_effects`, `temporal_radiance_cache`, `dynamic_resolution_scaling`, `virtual_shadow_maps`.

**Результат проекта.**

- Кандидатов: 42, рекомендовано: 33, исключено: 9.
- Учтено в расчёте: 2 из 6 выбранных техник.
- Первое место по каждой функции: `art_pipeline` → `normal_bake_retopology_pipeline`; `audio_system` → `audio_streaming_compression`; `build_delivery` → `differential_patch_pipeline`; `dynamic_global_illumination` → `screen_space_gi`; `dynamic_shadows` → `screen_space_contact_shadows`; `geometry_pipeline` → `mesh_index_optimization`; `open_world_streaming` → `gpu_compute_culling`; `project_architecture` → `composition_bootstrap_architecture`; `ray_traced_effects` → `rt_effect_resolution_budget`; `render_scalability` → `quality_tier_scalability`; `rendering_architecture` → `tiled_clustered_light_culling`; `runtime_memory` → `managed_gc_alloc_budget`; `upscaling_frame_generation` → `ml_frame_generation`.
- Оборудование: CPU-индекс 0.36 (класс 2, ориентир Core i3-10100), GPU-индекс 0.66 (класс 3, ориентир GeForce RTX 5060 Ti), RAM 17.0 ГБ, VRAM 14.4 ГБ; узкое место — GPU (растеризация).
- Календарь (команда `small_2_5`): трудоёмкость P50 104.98 чел.-дн., P80 157.46; срок P50 62.24 дн., P80 93.33.
- Объявленных пробелов модели: 7.

**Эталонное поведение игры.**

- CDPR описывает динамическое глобальное освещение и трассировку пути как основу «RT Overdrive». *(каталог проекта)*
- Стриминг плотного города — определяющая задача; консоли и ПК получают разные профили качества. *(публичная документация)*
- DLSS используется как штатный апскейлер для целевого разрешения. *(публичная документация)*

**Выявленные отличия.**

- **Расхождение ранга:** игра применяет `world_partition_streaming`, а движок ставит его на 4-е место из 5 в группе `open_world_streaming`; первым идёт `gpu_compute_culling`. Причина — критерии TOPSIS: у `world_partition_streaming` экспертный балл эффекта 0.75, стоимость внедрения 4, сложность 4, штраф за позднее внедрение `critical`.
- **Расхождение ранга:** игра применяет `hardware_raytraced_gi`, а движок ставит его на 4-е место из 6 в группе `dynamic_global_illumination`; первым идёт `screen_space_gi`. Причина — критерии TOPSIS: у `hardware_raytraced_gi` экспертный балл эффекта 0.1, стоимость внедрения 4, сложность 4, штраф за позднее внедрение `high`.
- **Не учтено в расчёте нагрузки:** 4 из 6 выбранных техник (`world_partition_streaming`, `hardware_raytraced_gi`, `temporal_radiance_cache`, `dynamic_resolution_scaling`) исключены из профиля нагрузки и оценки оборудования из-за отсутствующих обязательных зависимостей.
- **Выход за область применимости модели:** Количественный прогноз доступен только для Windows/Linux ПК: для платформ (ps5, xbox_series) совместимый аппаратный прогноз не обещается.
- **FPS не моделируется:** целевые 60.0 FPS остаются статусом `not_modeled`; сравнить с фактической частотой кадров игры нельзя по устройству модели.

### S11. No Man's Sky — Hello Games, 2016

*Движок: собственный движок. Собственный движок (2016): процедурная генерация 18 квинтиллионов планет.*

**Сценарий (профиль проекта).** формат 3D, мир procedural, масштаб very_large, стадия release, цель 1080p/high/60 FPS, функции: procedural_terrain, open_world_streaming, storage_streaming, save_system, build_delivery.

**Корзина (техники игры):** `chunked_procedural_terrain`, `terrain_generation_streaming_budget`, `world_origin_shifting`, `async_loading_pipeline`, `async_incremental_saves`.

**Результат проекта.**

- Кандидатов: 32, рекомендовано: 24, исключено: 8.
- Учтено в расчёте: 5 из 5 выбранных техник.
- Первое место по каждой функции: `art_pipeline` → `normal_bake_retopology_pipeline`; `audio_system` → `audio_streaming_compression`; `build_delivery` → `differential_patch_pipeline`; `geometry_pipeline` → `mesh_index_optimization`; `open_world_streaming` → `gpu_compute_culling`; `procedural_terrain` → `terrain_generation_streaming_budget`; `project_architecture` → `composition_bootstrap_architecture`; `render_scalability` → `quality_tier_scalability`; `rendering_architecture` → `tiled_clustered_light_culling`; `runtime_memory` → `managed_gc_alloc_budget`; `save_system` → `snapshot_slot_saves`; `upscaling_frame_generation` → `ml_frame_generation`.
- Оборудование: CPU-индекс 0.34 (класс 2, ориентир Core i5-10400F), GPU-индекс 0.2 (класс 3, ориентир GeForce RTX 3060), RAM 16.2 ГБ, VRAM 10.4 ГБ; узкое место — CPU (главный поток).
- Календарь (команда `small_2_5`): трудоёмкость P50 46.45 чел.-дн., P80 69.72; срок P50 29.4 дн., P80 44.12.
- Объявленных пробелов модели: 7.

**Эталонное поведение игры.**

- Мир генерируется процедурно из чанков и подгружается по мере движения; генерация идёт в фоне, чтобы не блокировать кадр. *(публичная документация)*
- Публичный разбор связывает открытый мир с процедурной генерацией ландшафта и стримингом. *(каталог проекта)*
- Сохранения инкрементальные: мир слишком велик для снапшота целиком. *(публичная документация)*

**Выявленные отличия.**

- **Расхождение ранга:** игра применяет `chunked_procedural_terrain`, а движок ставит его на 2-е место из 2 в группе `procedural_terrain`; первым идёт `terrain_generation_streaming_budget`. Причина — критерии TOPSIS: у `chunked_procedural_terrain` экспертный балл эффекта 0.7, стоимость внедрения 4, сложность 4, штраф за позднее внедрение `critical`.
- **Совпадение:** ключевая техника игры `terrain_generation_streaming_budget` стоит на 1-м месте в своей группе (procedural_terrain).
- **Выход за область применимости модели:** Количественный прогноз доступен только для Windows/Linux ПК: для платформ (ps4, xbox_one) совместимый аппаратный прогноз не обещается.
- **FPS не моделируется:** целевые 60.0 FPS остаются статусом `not_modeled`; сравнить с фактической частотой кадров игры нельзя по устройству модели.

### S12. Microsoft Flight Simulator — Asobo Studio, 2020

*Движок: собственный движок. Собственный движок Asobo (2020): потоковая подгрузка геоданных планеты.*

**Сценарий (профиль проекта).** формат 3D, мир open_world, масштаб very_large, стадия release, цель 1440p/high/60 FPS, функции: large_scale_terrain, open_world_streaming, storage_streaming, procedural_vegetation.

**Корзина (техники игры):** `terrain_clipmap`, `virtual_texturing`, `world_partition_streaming`, `async_loading_pipeline`, `gpu_instancing_vegetation`.

**Результат проекта.**

- Кандидатов: 38, рекомендовано: 29, исключено: 9.
- Учтено в расчёте: 3 из 5 выбранных техник.
- Первое место по каждой функции: `art_pipeline` → `normal_bake_retopology_pipeline`; `audio_system` → `audio_streaming_compression`; `build_delivery` → `differential_patch_pipeline`; `geometry_pipeline` → `mesh_index_optimization`; `large_scale_terrain` → `neural_texture_compression`; `open_world_streaming` → `gpu_compute_culling`; `procedural_vegetation` → `vegetation_atlas_lod`; `project_architecture` → `composition_bootstrap_architecture`; `render_scalability` → `quality_tier_scalability`; `rendering_architecture` → `tiled_clustered_light_culling`; `runtime_memory` → `managed_gc_alloc_budget`; `upscaling_frame_generation` → `ml_frame_generation`.
- Оборудование: CPU-индекс 0.32 (класс 2, ориентир Core i3-10100), GPU-индекс 0.36 (класс 3, ориентир GeForce RTX 3060), RAM 14.9 ГБ, VRAM 9.2 ГБ; узкое место — GPU (растеризация).
- Календарь (команда `small_2_5`): трудоёмкость P50 100.79 чел.-дн., P80 151.18; срок P50 60.48 дн., P80 90.71.
- Объявленных пробелов модели: 7.

**Эталонное поведение игры.**

- Microsoft Flight Simulator стримит Bing-геоданные и фототекстуры по мере полёта; офлайн-режим деградирует качество, но не ломает мир. *(публичная документация)*
- Клипмап и виртуальное текстурирование — штатные механизмы рендера огромного ландшафта. *(публичная документация)*
- Asobo описывает разделение: геометрия и данные подгружаются по дистанции, а не держатся в памяти целиком. *(публичная документация)*

**Выявленные отличия.**

- **Расхождение ранга:** игра применяет `terrain_clipmap`, а движок ставит его на 3-е место из 5 в группе `large_scale_terrain`; первым идёт `neural_texture_compression`. Причина — критерии TOPSIS: у `terrain_clipmap` экспертный балл эффекта 0.7, стоимость внедрения 4, сложность 4, штраф за позднее внедрение `high`.
- **Расхождение ранга:** игра применяет `virtual_texturing`, а движок ставит его на 5-е место из 5 в группе `large_scale_terrain`; первым идёт `neural_texture_compression`. Причина — критерии TOPSIS: у `virtual_texturing` экспертный балл эффекта 0.6, стоимость внедрения 5, сложность 5, штраф за позднее внедрение `critical`.
- **Не учтено в расчёте нагрузки:** 2 из 5 выбранных техник (`terrain_clipmap`, `gpu_instancing_vegetation`) исключены из профиля нагрузки и оценки оборудования из-за отсутствующих обязательных зависимостей.
- **Выход за область применимости модели:** Количественный прогноз доступен только для Windows/Linux ПК: для платформ (xbox_series) совместимый аппаратный прогноз не обещается.
- **FPS не моделируется:** целевые 60.0 FPS остаются статусом `not_modeled`; сравнить с фактической частотой кадров игры нельзя по устройству модели.

### S13. Teardown — Tuxedo Labs, 2020

*Движок: собственный движок. Собственный воксельный движок (2020): полная разрушаемость и ray marching.*

**Сценарий (профиль проекта).** формат 3D, мир sandbox, масштаб medium, стадия release, цель 1080p/medium/60 FPS, функции: destruction_simulation, physics_simulation, geometry_pipeline, ray_traced_effects.

**Корзина (техники игры):** `runtime_fracture_budget`, `destruction_geometry_cache`, `broadphase_spatial_partitioning`, `gpu_compute_culling`.

**Результат проекта.**

- Кандидатов: 29, рекомендовано: 24, исключено: 5.
- Учтено в расчёте: 2 из 4 выбранных техник.
- Первое место по каждой функции: `art_pipeline` → `normal_bake_retopology_pipeline`; `audio_system` → `audio_streaming_compression`; `build_delivery` → `differential_patch_pipeline`; `destruction_simulation` → `runtime_fracture_budget`; `geometry_pipeline` → `mesh_index_optimization`; `physics_simulation` → `collision_layer_matrix`; `project_architecture` → `composition_bootstrap_architecture`; `ray_traced_effects` → `rt_effect_resolution_budget`; `render_scalability` → `quality_tier_scalability`; `rendering_architecture` → `tiled_clustered_light_culling`; `runtime_memory` → `managed_gc_alloc_budget`; `upscaling_frame_generation` → `ml_frame_generation`.
- Оборудование: CPU-индекс 0.33 (класс 2, ориентир Core i3-10100), GPU-индекс 0.45 (класс 2, ориентир Radeon RX 6600), RAM 12.7 ГБ, VRAM 6.8 ГБ; узкое место — CPU (главный поток).
- Календарь (команда `small_2_5`): трудоёмкость P50 55.11 чел.-дн., P80 82.66; срок P50 34.48 дн., P80 51.72.
- Объявленных пробелов модели: 9.

**Эталонное поведение игры.**

- Teardown строит мир на вокселях и позволяет разрушать почти всё; геометрия обновляется в рантайме. *(публичная документация)*
- Рендер основан на трассировке лучей по воксельной сетке, а не на классической растеризации. *(публичная документация)*
- Физика обломков ограничена бюджетом активных объектов, а не полной симуляцией всей структуры. *(публичная документация)*

**Выявленные отличия.**

- **Совпадение:** ключевая техника игры `runtime_fracture_budget` стоит на 1-м месте в своей группе (destruction_simulation).
- **Расхождение ранга:** игра применяет `destruction_geometry_cache`, а движок ставит его на 2-е место из 2 в группе `destruction_simulation`; первым идёт `runtime_fracture_budget`. Причина — критерии TOPSIS: у `destruction_geometry_cache` экспертный балл эффекта 0.65, стоимость внедрения 4, сложность 4, штраф за позднее внедрение `medium`.
- **Не учтено в расчёте нагрузки:** 2 из 4 выбранных техник (`runtime_fracture_budget`, `gpu_compute_culling`) исключены из профиля нагрузки и оценки оборудования из-за отсутствующих обязательных зависимостей.
- **FPS не моделируется:** целевые 60.0 FPS остаются статусом `not_modeled`; сравнить с фактической частотой кадров игры нельзя по устройству модели.

### S14. BeamNG.drive — BeamNG GmbH, 2015

*Движок: собственный движок. Собственный движок BeamNG (2015): soft-body физика вместо жёстких тел.*

**Сценарий (профиль проекта).** формат 3D, мир sandbox, масштаб medium, стадия release, цель 1080p/high/60 FPS, функции: vehicle_simulation, physics_simulation, destruction_simulation.

**Корзина (техники игры):** `raycast_vehicle_physics`, `vehicle_simulation_lod`, `fixed_timestep_physics`, `multithreaded_physics_jobs`.

**Результат проекта.**

- Кандидатов: 29, рекомендовано: 24, исключено: 5.
- Учтено в расчёте: 3 из 4 выбранных техник.
- Первое место по каждой функции: `art_pipeline` → `normal_bake_retopology_pipeline`; `audio_system` → `audio_streaming_compression`; `build_delivery` → `differential_patch_pipeline`; `destruction_simulation` → `runtime_fracture_budget`; `geometry_pipeline` → `mesh_index_optimization`; `physics_simulation` → `collision_layer_matrix`; `project_architecture` → `composition_bootstrap_architecture`; `render_scalability` → `quality_tier_scalability`; `rendering_architecture` → `tiled_clustered_light_culling`; `runtime_memory` → `managed_gc_alloc_budget`; `upscaling_frame_generation` → `ml_frame_generation`; `vehicle_simulation` → `vehicle_simulation_lod`.
- Оборудование: CPU-индекс 0.24 (класс 2, ориентир Core i3-10100), GPU-индекс 0.19 (класс 2, ориентир Radeon RX 580), RAM 12.1 ГБ, VRAM 6.8 ГБ; узкое место — CPU (главный поток).
- Календарь (команда `small_2_5`): трудоёмкость P50 42.78 чел.-дн., P80 64.18; срок P50 26.72 дн., P80 40.07.
- Объявленных пробелов модели: 8.

**Эталонное поведение игры.**

- BeamNG моделирует автомобиль как систему балок (soft-body), а не как одно жёсткое тело: это и даёт деформацию. *(публичная документация)*
- Физика идёт с фиксированным малым шагом; при просадке шаг дробится, чтобы симуляция не «взорвалась». *(публичная документация)*
- Рейкасты подвески — распространённый, но упрощённый подход; BeamNG идёт дальше, к связанным узлам. *(публичная документация)*

**Выявленные отличия.**

- **Расхождение ранга:** игра применяет `multithreaded_physics_jobs`, а движок ставит его на 4-е место из 5 в группе `physics_simulation`; первым идёт `collision_layer_matrix`. Причина — критерии TOPSIS: у `multithreaded_physics_jobs` экспертный балл эффекта 0.65, стоимость внедрения 4, сложность 4, штраф за позднее внедрение `high`.
- **Расхождение ранга:** игра применяет `fixed_timestep_physics`, а движок ставит его на 5-е место из 5 в группе `physics_simulation`; первым идёт `collision_layer_matrix`. Причина — критерии TOPSIS: у `fixed_timestep_physics` экспертный балл эффекта 0.35, стоимость внедрения 3, сложность 3, штраф за позднее внедрение `critical`.
- **Не учтено в расчёте нагрузки:** 1 из 4 выбранных техник (`vehicle_simulation_lod`) исключены из профиля нагрузки и оценки оборудования из-за отсутствующих обязательных зависимостей.
- **FPS не моделируется:** целевые 60.0 FPS остаются статусом `not_modeled`; сравнить с фактической частотой кадров игры нельзя по устройству модели.

### S15. Ashes of the Singularity — Oxide Games, 2016

*Движок: собственный движок. Собственный движок Nitrous (2016): тысячи юнитов на CPU.*

**Сценарий (профиль проекта).** формат 3D, мир arena, масштаб large, стадия release, цель 1080p/high/60 FPS, функции: crowd_simulation, ai_pathfinding, particle_systems, rendering_architecture.

**Корзина (техники игры):** `ecs_data_oriented_crowd`, `flow_field_pathing`, `agent_update_budget`, `time_sliced_pathfinding`, `multithreaded_physics_jobs`.

**Результат проекта.**

- Кандидатов: 34, рекомендовано: 27, исключено: 7.
- Учтено в расчёте: 4 из 5 выбранных техник.
- Первое место по каждой функции: `ai_pathfinding` → `rvo_local_avoidance`; `art_pipeline` → `normal_bake_retopology_pipeline`; `audio_system` → `audio_streaming_compression`; `build_delivery` → `differential_patch_pipeline`; `crowd_simulation` → `agent_update_budget`; `geometry_pipeline` → `mesh_index_optimization`; `open_world_streaming` → `baked_occlusion_culling`; `particle_systems` → `particle_pooling`; `project_architecture` → `composition_bootstrap_architecture`; `render_scalability` → `quality_tier_scalability`; `rendering_architecture` → `tiled_clustered_light_culling`; `runtime_memory` → `managed_gc_alloc_budget`; `upscaling_frame_generation` → `ml_frame_generation`.
- Оборудование: CPU-индекс 0.36 (класс 2, ориентир Core i3-10100), GPU-индекс 0.29 (класс 3, ориентир GeForce RTX 3060), RAM 14.4 ГБ, VRAM 8.9 ГБ; узкое место — CPU (главный поток).
- Календарь (команда `small_2_5`): трудоёмкость P50 64.89 чел.-дн., P80 97.35; срок P50 38.36 дн., P80 57.51.
- Объявленных пробелов модели: 8.

**Эталонное поведение игры.**

- Ashes of the Singularity изначально проектировалась под многопоточный CPU и тысячи одновременно симулируемых юнитов. *(публичная документация)*
- Движок Nitrous явно распределяет симуляцию по ядрам и использует пакетную обработку юнитов. *(публичная документация)*
- Нагрузка упирается в CPU (главный поток + параллельная симуляция), а не в GPU. *(публичная документация)*

**Выявленные отличия.**

- **Расхождение ранга:** игра применяет `ecs_data_oriented_crowd`, а движок ставит его на 3-е место из 3 в группе `crowd_simulation`; первым идёт `agent_update_budget`. Причина — критерии TOPSIS: у `ecs_data_oriented_crowd` экспертный балл эффекта 0.8, стоимость внедрения 5, сложность 5, штраф за позднее внедрение `critical`.
- **Расхождение ранга:** игра применяет `flow_field_pathing`, а движок ставит его на 3-е место из 4 в группе `ai_pathfinding`; первым идёт `rvo_local_avoidance`. Причина — критерии TOPSIS: у `flow_field_pathing` экспертный балл эффекта 0.7, стоимость внедрения 3, сложность 3, штраф за позднее внедрение `medium`.
- **Не учтено в расчёте нагрузки:** 1 из 5 выбранных техник (`multithreaded_physics_jobs`) исключены из профиля нагрузки и оценки оборудования из-за отсутствующих обязательных зависимостей.
- **FPS не моделируется:** целевые 60.0 FPS остаются статусом `not_modeled`; сравнить с фактической частотой кадров игры нельзя по устройству модели.

### S16. Horizon Zero Dawn — Guerrilla Games, 2017

*Движок: собственный движок. Собственный движок Decima (2017): открытый мир на консоли 2013 года.*

**Сценарий (профиль проекта).** формат 3D, мир open_world, масштаб large, стадия release, цель 1080p/high/30 FPS, функции: open_world_streaming, large_scale_terrain, procedural_vegetation, character_animation.

**Корзина (техники игры):** `world_partition_streaming`, `heightmap_compression`, `gpu_instancing_vegetation`, `impostors_billboards`, `animation_compression`, `animation_lod_budget`.

**Результат проекта.**

- Кандидатов: 45, рекомендовано: 32, исключено: 13.
- Учтено в расчёте: 0 из 6 выбранных техник.
- Первое место по каждой функции: `art_pipeline` → `normal_bake_retopology_pipeline`; `audio_system` → `audio_streaming_compression`; `build_delivery` → `differential_patch_pipeline`; `character_animation` → `animation_lod_budget`; `geometry_pipeline` → `mesh_index_optimization`; `large_scale_terrain` → `neural_texture_compression`; `open_world_streaming` → `gpu_compute_culling`; `procedural_vegetation` → `vegetation_atlas_lod`; `project_architecture` → `composition_bootstrap_architecture`; `render_scalability` → `quality_tier_scalability`; `rendering_architecture` → `tiled_clustered_light_culling`; `runtime_memory` → `managed_gc_alloc_budget`; `upscaling_frame_generation` → `ml_frame_generation`.
- Оборудование: CPU-индекс 0.16 (класс 1, ориентир Core i3-8100), GPU-индекс 0.13 (класс 3, ориентир GeForce RTX 3060), RAM 13.9 ГБ, VRAM 8.3 ГБ; узкое место — CPU (главный поток).
- Календарь (команда `small_2_5`): трудоёмкость P50 125.27 чел.-дн., P80 187.82; срок P50 75.0 дн., P80 112.45.
- Объявленных пробелов модели: 7.

**Эталонное поведение игры.**

- Decima стримит мир ячейками и агрессивно использует импосторы и запечённые LOD для дальней растительности. *(публичная документация)*
- Публичный кейс связывает открытый мир с потоковой загрузкой и растительностью окружения. *(каталог проекта)*
- Цель — стабильные 30 FPS на PS4, поэтому бюджет кадра жёстко ограничен. *(публичная документация)*

**Выявленные отличия.**

- **Расхождение ранга:** игра применяет `world_partition_streaming`, а движок ставит его на 4-е место из 5 в группе `open_world_streaming`; первым идёт `gpu_compute_culling`. Причина — критерии TOPSIS: у `world_partition_streaming` экспертный балл эффекта 0.75, стоимость внедрения 4, сложность 4, штраф за позднее внедрение `critical`.
- **Расхождение ранга:** игра применяет `impostors_billboards`, а движок ставит его на 2-е место из 4 в группе `procedural_vegetation`; первым идёт `vegetation_atlas_lod`. Причина — критерии TOPSIS: у `impostors_billboards` экспертный балл эффекта 0.6, стоимость внедрения 2, сложность 2, штраф за позднее внедрение `low`.
- **Расхождение ранга:** игра применяет `gpu_instancing_vegetation`, а движок ставит его на 3-е место из 4 в группе `procedural_vegetation`; первым идёт `vegetation_atlas_lod`. Причина — критерии TOPSIS: у `gpu_instancing_vegetation` экспертный балл эффекта 0.75, стоимость внедрения 3, сложность 3, штраф за позднее внедрение `high`.
- **Не учтено в расчёте нагрузки:** 6 из 6 выбранных техник (`world_partition_streaming`, `heightmap_compression`, `gpu_instancing_vegetation`, `impostors_billboards`, `animation_compression`, `animation_lod_budget`) исключены из профиля нагрузки и оценки оборудования из-за отсутствующих обязательных зависимостей.
- **Профиль нагрузки нейтрален (50/50) при непустой корзине:** ни одна выбранная техника не дошла до расчёта, поэтому числа отражают пустой набор, а не выбранные решения.
- **Выход за область применимости модели:** Количественный прогноз доступен только для Windows/Linux ПК: для платформ (ps4) совместимый аппаратный прогноз не обещается.
- **FPS не моделируется:** целевые 30.0 FPS остаются статусом `not_modeled`; сравнить с фактической частотой кадров игры нельзя по устройству модели.

### S17. Alan Wake 2 — Remedy Entertainment, 2023

*Движок: собственный движок. Собственный движок Northlight (2023): трассировка пути как основной режим на ПК.*

**Сценарий (профиль проекта).** формат 3D, мир hub, масштаб medium, стадия release, цель 1440p/ultra/60 FPS, функции: path_tracing, dynamic_global_illumination, mesh_shaders, hair_rendering, volumetric_effects, rendering_architecture.

**Корзина (техники игры):** `full_path_tracing_pipeline`, `path_tracing_sample_denoiser_budget`, `meshlet_pipeline_adoption`, `hair_strand_simulation`, `froxel_volumetric_fog`.

**Результат проекта.**

- Кандидатов: 36, рекомендовано: 29, исключено: 7.
- Учтено в расчёте: 2 из 5 выбранных техник.
- Первое место по каждой функции: `art_pipeline` → `normal_bake_retopology_pipeline`; `audio_system` → `audio_streaming_compression`; `build_delivery` → `differential_patch_pipeline`; `dynamic_global_illumination` → `screen_space_gi`; `geometry_pipeline` → `mesh_index_optimization`; `hair_rendering` → `hair_cards_lod`; `open_world_streaming` → `baked_occlusion_culling`; `path_tracing` → `path_tracing_sample_denoiser_budget`; `project_architecture` → `composition_bootstrap_architecture`; `render_scalability` → `quality_tier_scalability`; `rendering_architecture` → `tiled_clustered_light_culling`; `runtime_memory` → `managed_gc_alloc_budget`; `upscaling_frame_generation` → `ml_frame_generation`; `volumetric_effects` → `volumetric_half_resolution`.
- Оборудование: CPU-индекс 0.36 (класс 1, ориентир Core i3-8100), GPU-индекс 0.84 (класс 4, ориентир GeForce RTX 4070), RAM 12.6 ГБ, VRAM 9.5 ГБ; узкое место — GPU (растеризация).
- Календарь (команда `small_2_5`): трудоёмкость P50 104.76 чел.-дн., P80 157.17; срок P50 63.37 дн., P80 95.08.
- Объявленных пробелов модели: 8.

**Эталонное поведение игры.**

- Alan Wake 2 — один из первых релизов с полноценной трассировкой пути на ПК; денойзинг и число выборок — ключевой бюджет. *(публичная документация)*
- Движок использует меш-шейдеры и симуляцию прядей волос. *(каталог проекта)*
- Объёмный туман — центральный художественный приём, а не опциональный пост-эффект. *(каталог проекта)*

**Выявленные отличия.**

- **Расхождение ранга:** игра применяет `full_path_tracing_pipeline`, а движок ставит его на 2-е место из 2 в группе `path_tracing`; первым идёт `path_tracing_sample_denoiser_budget`. Причина — критерии TOPSIS: у `full_path_tracing_pipeline` экспертный балл эффекта 0.1, стоимость внедрения 5, сложность 5, штраф за позднее внедрение `critical`.
- **Исключение:** техника игры `meshlet_pipeline_adoption` исключена — Метод не поддерживается на целевых платформах: ps5..
- **Расхождение ранга:** игра применяет `hair_strand_simulation`, а движок ставит его на 2-е место из 2 в группе `hair_rendering`; первым идёт `hair_cards_lod`. Причина — критерии TOPSIS: у `hair_strand_simulation` экспертный балл эффекта 0.5, стоимость внедрения 4, сложность 4, штраф за позднее внедрение `medium`.
- **Не учтено в расчёте нагрузки:** 3 из 5 выбранных техник (`full_path_tracing_pipeline`, `meshlet_pipeline_adoption`, `froxel_volumetric_fog`) исключены из профиля нагрузки и оценки оборудования из-за отсутствующих обязательных зависимостей.
- **Выход за область применимости модели:** Количественный прогноз доступен только для Windows/Linux ПК: для платформ (ps5, xbox_series) совместимый аппаратный прогноз не обещается.
- **FPS не моделируется:** целевые 60.0 FPS остаются статусом `not_modeled`; сравнить с фактической частотой кадров игры нельзя по устройству модели.

### S18. F.E.A.R. — Monolith Productions, 2005

*Движок: собственный движок. Собственный движок LithTech (2005): эталонный ИИ врагов.*

**Сценарий (профиль проекта).** формат 3D, мир linear, масштаб small, стадия release, цель 720p/medium/60 FPS, функции: advanced_npc_ai, ai_pathfinding, dynamic_shadows.

**Корзина (техники игры):** `behaviour_tree_update_budget`, `time_sliced_pathfinding`, `navmesh_tiling_streaming`, `npc_perception_budget`.

**Результат проекта.**

- Кандидатов: 34, рекомендовано: 24, исключено: 10.
- Учтено в расчёте: 3 из 4 выбранных техник.
- Первое место по каждой функции: `advanced_npc_ai` → `npc_perception_budget`; `ai_pathfinding` → `rvo_local_avoidance`; `art_pipeline` → `normal_bake_retopology_pipeline`; `audio_system` → `audio_streaming_compression`; `build_delivery` → `differential_patch_pipeline`; `dynamic_shadows` → `screen_space_contact_shadows`; `geometry_pipeline` → `mesh_index_optimization`; `open_world_streaming` → `baked_occlusion_culling`; `project_architecture` → `composition_bootstrap_architecture`; `render_scalability` → `quality_tier_scalability`; `rendering_architecture` → `tiled_clustered_light_culling`; `runtime_memory` → `managed_gc_alloc_budget`; `upscaling_frame_generation` → `ml_frame_generation`.
- Оборудование: CPU-индекс 0.26 (класс 1, ориентир Core i3-8100), GPU-индекс 0.11 (класс 1, ориентир GeForce GTX 1050 Ti), RAM 9.6 ГБ, VRAM 3.9 ГБ; узкое место — CPU (главный поток).
- Календарь (команда `small_2_5`): трудоёмкость P50 35.0 чел.-дн., P80 52.49; срок P50 22.15 дн., P80 33.21.
- Объявленных пробелов модели: 7.

**Эталонное поведение игры.**

- F.E.A.R. известна планированием действий (goal-oriented action planning), а не деревьями поведения: агенты договариваются о фланкировании. *(публичная документация)*
- Восприятие и коммуникация группы — отдельная подсистема, дающая «умное» поведение при малом числе врагов. *(публичная документация)*
- Публичный кейс связывает игру с поведенческим ИИ и поиском пути. *(каталог проекта)*

**Выявленные отличия.**

- **Совпадение:** ключевая техника игры `npc_perception_budget` стоит на 1-м месте в своей группе (advanced_npc_ai).
- **Расхождение ранга:** игра применяет `time_sliced_pathfinding`, а движок ставит его на 2-е место из 2 в группе `ai_pathfinding`; первым идёт `rvo_local_avoidance`. Причина — критерии TOPSIS: у `time_sliced_pathfinding` экспертный балл эффекта 0.5, стоимость внедрения 2, сложность 2, штраф за позднее внедрение `medium`.
- **Не учтено в расчёте нагрузки:** 1 из 4 выбранных техник (`navmesh_tiling_streaming`) исключены из профиля нагрузки и оценки оборудования из-за отсутствующих обязательных зависимостей.
- **FPS не моделируется:** целевые 60.0 FPS остаются статусом `not_modeled`; сравнить с фактической частотой кадров игры нельзя по устройству модели.

### S19. Uncharted 4: A Thief's End — Naughty Dog, 2016

*Движок: собственный движок. Собственный движок Naughty Dog (2016): motion matching в AAA-производстве.*

**Сценарий (профиль проекта).** формат 3D, мир linear, масштаб medium, стадия release, цель 1080p/high/30 FPS, функции: character_animation, art_pipeline, post_processing, dynamic_shadows.

**Корзина (техники игры):** `motion_matching`, `animation_compression`, `animation_lod_budget`, `normal_bake_retopology_pipeline`, `depth_prepass_early_z`.

**Результат проекта.**

- Кандидатов: 41, рекомендовано: 30, исключено: 11.
- Учтено в расчёте: 0 из 5 выбранных техник.
- Первое место по каждой функции: `art_pipeline` → `normal_bake_retopology_pipeline`; `audio_system` → `audio_streaming_compression`; `build_delivery` → `differential_patch_pipeline`; `character_animation` → `animation_lod_budget`; `dynamic_shadows` → `screen_space_contact_shadows`; `geometry_pipeline` → `mesh_index_optimization`; `open_world_streaming` → `baked_occlusion_culling`; `post_processing` → `screenspace_light_shafts`; `project_architecture` → `composition_bootstrap_architecture`; `render_scalability` → `quality_tier_scalability`; `rendering_architecture` → `tiled_clustered_light_culling`; `runtime_memory` → `managed_gc_alloc_budget`; `upscaling_frame_generation` → `ml_frame_generation`.
- Оборудование: CPU-индекс 0.14 (класс 1, ориентир Core i3-8100), GPU-индекс 0.11 (класс 2, ориентир Radeon RX 580), RAM 11.4 ГБ, VRAM 6.4 ГБ; узкое место — CPU (главный поток).
- Календарь (команда `small_2_5`): трудоёмкость P50 77.13 чел.-дн., P80 115.63; срок P50 47.77 дн., P80 71.64.
- Объявленных пробелов модели: 6.

**Эталонное поведение игры.**

- Uncharted 4 одной из первых применила motion matching: движение выбирается поиском по базе анимаций, а не переходами в графе. *(публичная документация)*
- Это требует больших объёмов анимации и сжатия: без него база движений не влезает в память. *(каталог проекта)*
- Публичный кейс связывает игру с анимацией персонажей и арт-пайплайном. *(каталог проекта)*

**Выявленные отличия.**

- **Расхождение ранга:** игра применяет `motion_matching`, а движок ставит его на 4-е место из 4 в группе `character_animation`; первым идёт `animation_lod_budget`. Причина — критерии TOPSIS: у `motion_matching` экспертный балл эффекта 0.0, стоимость внедрения 5, сложность 5, штраф за позднее внедрение `high`.
- **Расхождение ранга:** игра применяет `animation_compression`, а движок ставит его на 2-е место из 4 в группе `character_animation`; первым идёт `animation_lod_budget`. Причина — критерии TOPSIS: у `animation_compression` экспертный балл эффекта 0.4, стоимость внедрения 2, сложность 2, штраф за позднее внедрение `low`.
- **Не учтено в расчёте нагрузки:** 5 из 5 выбранных техник (`motion_matching`, `animation_compression`, `animation_lod_budget`, `normal_bake_retopology_pipeline`, `depth_prepass_early_z`) исключены из профиля нагрузки и оценки оборудования из-за отсутствующих обязательных зависимостей.
- **Профиль нагрузки нейтрален (50/50) при непустой корзине:** ни одна выбранная техника не дошла до расчёта, поэтому числа отражают пустой набор, а не выбранные решения.
- **Выход за область применимости модели:** Количественный прогноз доступен только для Windows/Linux ПК: для платформ (ps4) совместимый аппаратный прогноз не обещается.
- **FPS не моделируется:** целевые 30.0 FPS остаются статусом `not_modeled`; сравнить с фактической частотой кадров игры нельзя по устройству модели.

### S20. Red Faction: Guerrilla — Volition, 2009

*Движок: собственный движок. Собственный движок Geo-Mod 2.0 (2009): структурные разрушения.*

**Сценарий (профиль проекта).** формат 3D, мир open_world, масштаб large, стадия release, цель 1080p/high/60 FPS, функции: destruction_simulation, physics_simulation, open_world_streaming, vehicle_simulation.

**Корзина (техники игры):** `destruction_geometry_cache`, `runtime_fracture_budget`, `broadphase_spatial_partitioning`, `multithreaded_physics_jobs`, `world_partition_streaming`.

**Результат проекта.**

- Кандидатов: 36, рекомендовано: 29, исключено: 7.
- Учтено в расчёте: 2 из 5 выбранных техник.
- Первое место по каждой функции: `art_pipeline` → `normal_bake_retopology_pipeline`; `audio_system` → `audio_streaming_compression`; `build_delivery` → `differential_patch_pipeline`; `destruction_simulation` → `runtime_fracture_budget`; `geometry_pipeline` → `mesh_index_optimization`; `open_world_streaming` → `gpu_compute_culling`; `physics_simulation` → `collision_layer_matrix`; `project_architecture` → `composition_bootstrap_architecture`; `render_scalability` → `quality_tier_scalability`; `rendering_architecture` → `tiled_clustered_light_culling`; `runtime_memory` → `managed_gc_alloc_budget`; `upscaling_frame_generation` → `ml_frame_generation`; `vehicle_simulation` → `vehicle_simulation_lod`.
- Оборудование: CPU-индекс 0.32 (класс 2, ориентир Ryzen 5 2600), GPU-индекс 0.23 (класс 3, ориентир GeForce RTX 3060), RAM 15.2 ГБ, VRAM 9.2 ГБ; узкое место — CPU (главный поток).
- Календарь (команда `small_2_5`): трудоёмкость P50 85.77 чел.-дн., P80 128.71; срок P50 50.71 дн., P80 76.06.
- Объявленных пробелов модели: 8.

**Эталонное поведение игры.**

- Red Faction: Guerrilla даёт разрушать несущие конструкции: здание обрушивается, когда теряет опору, а не по скрипту. *(публичная документация)*
- Публичный кейс связывает игру с разрушением, физикой и транспортом в открытом мире. *(каталог проекта)*
- Разрушение и физика — тяжёлая CPU-нагрузка, которую ограничивают бюджетом активных объектов. *(публичная документация)*

**Выявленные отличия.**

- **Расхождение ранга:** игра применяет `destruction_geometry_cache`, а движок ставит его на 2-е место из 2 в группе `destruction_simulation`; первым идёт `runtime_fracture_budget`. Причина — критерии TOPSIS: у `destruction_geometry_cache` экспертный балл эффекта 0.65, стоимость внедрения 4, сложность 4, штраф за позднее внедрение `medium`.
- **Расхождение ранга:** игра применяет `multithreaded_physics_jobs`, а движок ставит его на 4-е место из 5 в группе `physics_simulation`; первым идёт `collision_layer_matrix`. Причина — критерии TOPSIS: у `multithreaded_physics_jobs` экспертный балл эффекта 0.65, стоимость внедрения 4, сложность 4, штраф за позднее внедрение `high`.
- **Не учтено в расчёте нагрузки:** 3 из 5 выбранных техник (`runtime_fracture_budget`, `multithreaded_physics_jobs`, `world_partition_streaming`) исключены из профиля нагрузки и оценки оборудования из-за отсутствующих обязательных зависимостей.
- **Выход за область применимости модели:** Количественный прогноз доступен только для Windows/Linux ПК: для платформ (ps4, xbox_one) совместимый аппаратный прогноз не обещается.
- **FPS не моделируется:** целевые 60.0 FPS остаются статусом `not_modeled`; сравнить с фактической частотой кадров игры нельзя по устройству модели.

### S21. Minecraft — Mojang Studios, 2011

*Движок: собственный движок. Собственный движок на Java (2011): воксельный мир и GC.*

**Сценарий (профиль проекта).** формат 3D, мир procedural, масштаб very_large, стадия release, цель 1080p/low/60 FPS, функции: procedural_terrain, runtime_memory, save_system, storage_streaming.

**Корзина (техники игры):** `chunked_procedural_terrain`, `terrain_generation_streaming_budget`, `managed_gc_alloc_budget`, `async_incremental_saves`.

**Результат проекта.**

- Кандидатов: 25, рекомендовано: 19, исключено: 6.
- Учтено в расчёте: 2 из 4 выбранных техник.
- Первое место по каждой функции: `art_pipeline` → `normal_bake_retopology_pipeline`; `audio_system` → `audio_streaming_compression`; `build_delivery` → `differential_patch_pipeline`; `geometry_pipeline` → `mesh_index_optimization`; `procedural_terrain` → `terrain_generation_streaming_budget`; `project_architecture` → `composition_bootstrap_architecture`; `render_scalability` → `quality_tier_scalability`; `rendering_architecture` → `tiled_clustered_light_culling`; `runtime_memory` → `managed_gc_alloc_budget`; `save_system` → `snapshot_slot_saves`; `upscaling_frame_generation` → `ml_frame_generation`.
- Оборудование: CPU-индекс 0.37 (класс 2, ориентир Core i3-10100), GPU-индекс 0.16 (класс 3, ориентир GeForce RTX 3060), RAM 14.7 ГБ, VRAM 8.3 ГБ; узкое место — CPU (главный поток).
- Календарь (команда `small_2_5`): трудоёмкость P50 47.79 чел.-дн., P80 71.72; срок P50 29.37 дн., P80 44.08.
- Объявленных пробелов модели: 7.

**Эталонное поведение игры.**

- Мир Minecraft состоит из чанков 16×16×384; загрузка и выгрузка чанков — основная потоковая задача. *(публичная документация)*
- Java-версия известна паузами сборщика мусора: управление аллокациями — реальная инженерная проблема. *(публичная документация)*
- Публичный кейс связывает игру с процедурной генерацией и сохранениями. *(каталог проекта)*

**Выявленные отличия.**

- **Расхождение ранга:** игра применяет `chunked_procedural_terrain`, а движок ставит его на 2-е место из 2 в группе `procedural_terrain`; первым идёт `terrain_generation_streaming_budget`. Причина — критерии TOPSIS: у `chunked_procedural_terrain` экспертный балл эффекта 0.7, стоимость внедрения 4, сложность 4, штраф за позднее внедрение `critical`.
- **Совпадение:** ключевая техника игры `managed_gc_alloc_budget` стоит на 1-м месте в своей группе (runtime_memory).
- **Не учтено в расчёте нагрузки:** 2 из 4 выбранных техник (`terrain_generation_streaming_budget`, `managed_gc_alloc_budget`) исключены из профиля нагрузки и оценки оборудования из-за отсутствующих обязательных зависимостей.
- **FPS не моделируется:** целевые 60.0 FPS остаются статусом `not_modeled`; сравнить с фактической частотой кадров игры нельзя по устройству модели.

### S22. Hunt: Showdown — Crytek, 2019

*Движок: CryEngine. CryEngine (2019): пространственный звук как источник читаемости.*

**Сценарий (профиль проекта).** формат 3D, мир open_world, масштаб medium, стадия release, цель 1440p/high/60 FPS, функции: audio_system, open_world_streaming, procedural_vegetation.

**Корзина (техники игры):** `audio_occlusion_propagation`, `audio_convolution_reverb`, `audio_streaming_compression`, `world_partition_streaming`.

**Результат проекта.**

- Кандидатов: 34, рекомендовано: 24, исключено: 10.
- Учтено в расчёте: 3 из 4 выбранных техник.
- Первое место по каждой функции: `art_pipeline` → `normal_bake_retopology_pipeline`; `audio_system` → `audio_streaming_compression`; `build_delivery` → `differential_patch_pipeline`; `geometry_pipeline` → `mesh_index_optimization`; `open_world_streaming` → `gpu_compute_culling`; `procedural_vegetation` → `vegetation_atlas_lod`; `project_architecture` → `composition_bootstrap_architecture`; `render_scalability` → `quality_tier_scalability`; `rendering_architecture` → `tiled_clustered_light_culling`; `upscaling_frame_generation` → `ml_frame_generation`.
- Оборудование: CPU-индекс 0.32 (класс 2, ориентир Core i5-10400F), GPU-индекс 0.29 (класс 3, ориентир GeForce RTX 3060), RAM 12.6 ГБ, VRAM 8.8 ГБ; узкое место — CPU (главный поток).
- Календарь (команда `small_2_5`): трудоёмкость P50 40.77 чел.-дн., P80 61.18; срок P50 26.34 дн., P80 39.51.
- Объявленных пробелов модели: 8.

**Эталонное поведение игры.**

- Для occlusion команда описывает проверку препятствия между emitter и listener и фильтрацию по типу поверхности. *(каталог проекта)*
- Crytek описывает CrySpatial как HRTF-based 3D audio, помогающий различать направление источника. *(каталог проекта)*
- Реализм звука ограничен читаемостью и правилами микса, а не физикой. *(каталог проекта)*

**Выявленные отличия.**

- **Расхождение ранга:** игра применяет `audio_occlusion_propagation`, а движок ставит его на 2-е место из 3 в группе `audio_system`; первым идёт `audio_streaming_compression`. Причина — критерии TOPSIS: у `audio_occlusion_propagation` экспертный балл эффекта 0.3, стоимость внедрения 3, сложность 3, штраф за позднее внедрение `medium`.
- **Расхождение ранга:** игра применяет `audio_convolution_reverb`, а движок ставит его на 3-е место из 3 в группе `audio_system`; первым идёт `audio_streaming_compression`. Причина — критерии TOPSIS: у `audio_convolution_reverb` экспертный балл эффекта 0.5, стоимость внедрения 2, сложность 3, штраф за позднее внедрение `medium`.
- **Не учтено в расчёте нагрузки:** 1 из 4 выбранных техник (`world_partition_streaming`) исключены из профиля нагрузки и оценки оборудования из-за отсутствующих обязательных зависимостей.
- **FPS не моделируется:** целевые 60.0 FPS остаются статусом `not_modeled`; сравнить с фактической частотой кадров игры нельзя по устройству модели.

### S23. V Rising — Stunlock Studios, 2022

*Движок: Unity. Unity DOTS (2022): ECS-симуляция для масштаба.*

**Сценарий (профиль проекта).** формат 3D, мир open_world, масштаб medium, стадия release, цель 1080p/high/60 FPS, функции: crowd_simulation, ai_pathfinding, runtime_memory, character_animation.

**Корзина (техники игры):** `ecs_data_oriented_crowd`, `agent_update_budget`, `crowd_instancing_impostors`, `managed_gc_alloc_budget`.

**Результат проекта.**

- Кандидатов: 36, рекомендовано: 27, исключено: 9.
- Учтено в расчёте: 3 из 4 выбранных техник.
- Первое место по каждой функции: `ai_pathfinding` → `rvo_local_avoidance`; `art_pipeline` → `normal_bake_retopology_pipeline`; `audio_system` → `audio_streaming_compression`; `build_delivery` → `differential_patch_pipeline`; `character_animation` → `animation_lod_budget`; `crowd_simulation` → `agent_update_budget`; `geometry_pipeline` → `mesh_index_optimization`; `project_architecture` → `composition_bootstrap_architecture`; `render_scalability` → `quality_tier_scalability`; `rendering_architecture` → `srp_batcher_discipline`; `runtime_memory` → `managed_gc_alloc_budget`; `upscaling_frame_generation` → `ml_frame_generation`.
- Оборудование: CPU-индекс 0.28 (класс 2, ориентир Core i5-10400F), GPU-индекс 0.16 (класс 2, ориентир Radeon RX 580), RAM 11.9 ГБ, VRAM 6.8 ГБ; узкое место — CPU (главный поток).
- Календарь (команда `small_2_5`): трудоёмкость P50 41.25 чел.-дн., P80 61.88; срок P50 25.64 дн., P80 38.47.
- Объявленных пробелов модели: 8.

**Эталонное поведение игры.**

- Unity описывает DOTS/Entities как стек для более масштабной обработки и приводит production examples с ECS, включая V Rising. *(каталог проекта)*
- Переход с GameObjects на ECS имеет стоимость миграции и зависит от контракта данных и job safety. *(каталог проекта)*
- Управляемая куча Unity делает бюджет аллокаций отдельной задачей. *(публичная документация)*

**Выявленные отличия.**

- **Расхождение ранга:** игра применяет `ecs_data_oriented_crowd`, а движок ставит его на 3-е место из 3 в группе `crowd_simulation`; первым идёт `agent_update_budget`. Причина — критерии TOPSIS: у `ecs_data_oriented_crowd` экспертный балл эффекта 0.8, стоимость внедрения 5, сложность 5, штраф за позднее внедрение `critical`.
- **Совпадение:** ключевая техника игры `managed_gc_alloc_budget` стоит на 1-м месте в своей группе (runtime_memory).
- **Не учтено в расчёте нагрузки:** 1 из 4 выбранных техник (`managed_gc_alloc_budget`) исключены из профиля нагрузки и оценки оборудования из-за отсутствующих обязательных зависимостей.
- **FPS не моделируется:** целевые 60.0 FPS остаются статусом `not_modeled`; сравнить с фактической частотой кадров игры нельзя по устройству модели.

### S24. Brotato — Blobfish, 2023

*Движок: Godot. Godot 4 (2023): 2D-арена с сотнями врагов.*

**Сценарий (профиль проекта).** формат 2D, мир arena, масштаб small, стадия release, цель 1080p/low/60 FPS, функции: crowd_simulation, particle_systems, render_scalability, character_animation, save_system.

**Корзина (техники игры):** `crowd_2d_instancing`, `sprite_atlas_batching`, `sprite_particle_atlas`, `quality_tier_scalability`.

**Результат проекта.**

- Кандидатов: 38, рекомендовано: 19, исключено: 19.
- Учтено в расчёте: 3 из 4 выбранных техник.
- Первое место по каждой функции: `art_pipeline` → `art_direction_stylization`; `audio_system` → `audio_streaming_compression`; `build_delivery` → `differential_patch_pipeline`; `character_animation` → `sprite_sheet_compression`; `crowd_simulation` → `crowd_2d_instancing`; `particle_systems` → `sprite_particle_atlas`; `project_architecture` → `composition_bootstrap_architecture`; `render_scalability` → `quality_tier_scalability`; `rendering_architecture` → `pso_precaching_warmup`; `save_system` → `snapshot_slot_saves`.
- Оборудование: CPU-индекс 0.26 (класс 2, ориентир Core i3-10100), GPU-индекс 0.21 (класс 2, ориентир GeForce GTX 1060 6GB), RAM 10.8 ГБ, VRAM 5.3 ГБ; узкое место — CPU (главный поток).
- Календарь (команда `small_2_5`): трудоёмкость P50 36.71 чел.-дн., P80 55.04; срок P50 22.69 дн., P80 34.01.
- Объявленных пробелов модели: 6.

**Эталонное поведение игры.**

- Brotato — 2D-арена с волнами врагов; производительность определяется числом спрайтов и эффектов, а не геометрией. *(публичная документация)*
- Godot 4 на Vulkan/Forward+ и поддерживает 2D-батчинг; каталог проекта заявляет для Godot Vulkan/OpenGL/D3D12. *(каталог проекта)*
- Список shipped-титулов Godot подтверждает применение движка в коммерческих 2D-играх. *(каталог проекта)*

**Выявленные отличия.**

- **Совпадение:** ключевая техника игры `crowd_2d_instancing` стоит на 1-м месте в своей группе (crowd_simulation).
- **Расхождение ранга:** игра применяет `sprite_atlas_batching`, а движок ставит его на 4-е место из 5 в группе `character_animation`; первым идёт `sprite_sheet_compression`. Причина — критерии TOPSIS: у `sprite_atlas_batching` экспертный балл эффекта 0.7, стоимость внедрения 2, сложность 2, штраф за позднее внедрение `high`.
- **Совпадение:** ключевая техника игры `sprite_particle_atlas` стоит на 1-м месте в своей группе (particle_systems).
- **Не учтено в расчёте нагрузки:** 1 из 4 выбранных техник (`sprite_atlas_batching`) исключены из профиля нагрузки и оценки оборудования из-за отсутствующих обязательных зависимостей.
- **Выход за область применимости модели:** Количественный прогноз доступен только для Windows/Linux ПК: для платформ (android, ios, switch) совместимый аппаратный прогноз не обещается.
- **FPS не моделируется:** целевые 60.0 FPS остаются статусом `not_modeled`; сравнить с фактической частотой кадров игры нельзя по устройству модели.

### S25. Star Wars: The Old Republic — BioWare, 2011

*Движок: HeroEngine. HeroEngine (2011): MMO-платформа с клиент-серверной моделью.*

**Сценарий (профиль проекта).** формат 3D, мир open_world, масштаб large, стадия release, цель 1080p/medium/60 FPS, функции: multiplayer_netcode, save_system, open_world_streaming, character_animation.

**Корзина (техники игры):** `client_prediction_reconciliation`, `network_relevancy_priority`, `delta_compression_state`, `async_incremental_saves`.

**Результат проекта.**

- Кандидатов: 43, рекомендовано: 34, исключено: 9.
- Учтено в расчёте: 2 из 4 выбранных техник.
- Первое место по каждой функции: `art_pipeline` → `normal_bake_retopology_pipeline`; `audio_system` → `audio_streaming_compression`; `build_delivery` → `differential_patch_pipeline`; `character_animation` → `animation_lod_budget`; `geometry_pipeline` → `mesh_index_optimization`; `multiplayer_netcode` → `delta_compression_state`; `open_world_streaming` → `gpu_compute_culling`; `project_architecture` → `composition_bootstrap_architecture`; `render_scalability` → `quality_tier_scalability`; `rendering_architecture` → `tiled_clustered_light_culling`; `save_system` → `snapshot_slot_saves`; `upscaling_frame_generation` → `ml_frame_generation`.
- Оборудование: CPU-индекс 0.35 (класс 2, ориентир Ryzen 5 1600), GPU-индекс 0.15 (класс 2, ориентир Radeon RX 580), RAM 14.0 ГБ, VRAM 7.8 ГБ; узкое место — CPU (главный поток).
- Календарь (команда `small_2_5`): трудоёмкость P50 56.01 чел.-дн., P80 84.1; срок P50 35.38 дн., P80 53.13.
- Объявленных пробелов модели: 8.

**Эталонное поведение игры.**

- Star Wars: The Old Republic — крупная MMO на HeroEngine; сервер держит множество игроков в общих зонах. *(публичная документация)*
- Каталог проекта заявляет HeroEngine как поддерживаемый движок с серверной моделью. *(каталог проекта)*
- Сетевой трафик и сохранения — определяющие подсистемы MMO, а не рендер. *(публичная документация)*

**Выявленные отличия.**

- **Расхождение ранга:** игра применяет `client_prediction_reconciliation`, а движок ставит его на 7-е место из 8 в группе `multiplayer_netcode`; первым идёт `delta_compression_state`. Причина — критерии TOPSIS: у `client_prediction_reconciliation` экспертный балл эффекта 0.3, стоимость внедрения 5, сложность 5, штраф за позднее внедрение `critical`.
- **Расхождение ранга:** игра применяет `network_relevancy_priority`, а движок ставит его на 3-е место из 8 в группе `multiplayer_netcode`; первым идёт `delta_compression_state`. Причина — критерии TOPSIS: у `network_relevancy_priority` экспертный балл эффекта 0.7, стоимость внедрения 4, сложность 4, штраф за позднее внедрение `critical`.
- **Не учтено в расчёте нагрузки:** 2 из 4 выбранных техник (`client_prediction_reconciliation`, `delta_compression_state`) исключены из профиля нагрузки и оценки оборудования из-за отсутствующих обязательных зависимостей.
- **Выход за область применимости модели:** Число игроков (100) выше порога различения (32): сетевой вклад оценён по насыщению.
- **FPS не моделируется:** целевые 60.0 FPS остаются статусом `not_modeled`; сравнить с фактической частотой кадров игры нельзя по устройству модели.

## Часть III. Сводка расхождений

- **Совпадение с реальностью:** хотя бы одна ключевая техника игры стоит на 1-м месте в своей группе в **21 из 25** сценариев.
- **Полнота учёта:** в расчёт нагрузки и оборудования дошли **60 из 114** выбранных техник (53%). Остальные отброшены отсутствующими обязательными зависимостями.
- **«Сверка с практикой» пуста** в **0 из 25** сценариев.
- **FPS не моделируется нигде:** целевая частота кадров всегда остаётся статусом `not_modeled`, поэтому прямое сравнение с фактической производительностью оригинала по построению невозможно.

### Систематические расхождения

**Ранжирование систематически понижает определяющие техники.** TOPSIS максимизирует отношение «экспертный эффект / стоимость и риск». Дорогие, поздние и архитектурные техники (sub-tick в CS2 — 8-е место из 8; World Partition в City Sample — 4-е из 5; GPU-частицы в DOOM Eternal — 3-е из 3) проигрывают дешёвым оптимизациям, хотя именно они делают игру такой, какая она есть.

**Сквозные методы попадают в функции, которых нет в профиле.** 20 методов всегда входят в кандидаты. Для CS2 (мир — арена, функция — только сеть) движок всё равно выдаёт рекомендацию по `open_world_streaming`.

**Половина выбранных техник не доходит до расчёта нагрузки.** 54 из 114 техник отброшены обязательными зависимостями. В сценариях Horizon Zero Dawn и Uncharted 4 не учтена ни одна техника: профиль нагрузки остаётся нейтральным 50/50, что читается как «решения не влияют», а не «решения не посчитаны».

**Каскадный обрыв из-за одной отсутствующей зависимости.** Отсутствие `gpu_skinning_compute` обнуляет всю цепочку `animation_lod_budget` → `motion_matching` → `animation_compression`.

**Противоречивые рёбра каталога.** Между `motion_matching` и `animation_lod_budget` одновременно объявлены **hard_conflict** («оставить один») и **обязательная dependency** («сохранять оба»). Два взаимоисключающих указания на одну пару.

**Тип связи `dependency` не распознаётся проверкой корзины.** В ответе появляется «тип связи «dependency» не распознан. Связь не учтена в расчёте», хотя тип объявлен в модели предметной области.

**Словарь аппаратных возможностей не покрывает базовые требования.** Требование «Compute Shaders» (`gpu_particle_simulation`, `gerstner_fft_water`, `gpu_compute_culling`) не может выполнить ни одна карта каталога: оценка оборудования возвращает «нет GPU» и пустой ориентир (сценарий DOOM Eternal).

**Матрица платформ неполна для меш-шейдеров.** `meshlet_pipeline_adoption` и `gpu_meshlet_culling_budget` объявлены только для `pc_windows` и `xbox_series`; PS5 отсутствует, поэтому Alan Wake 2 (титул PS5) теряет мешлет-методы.

**Расхождение таксономии: Nanite привязан не к той функции.** `virtual_geometry_clusters` числится под `large_scale_terrain`, а его же кейс-доказательство ссылается на функцию `geometry_pipeline`. Выбор `geometry_pipeline` Nanite не предлагает.

**Сверка с практикой не видит функциональные доказательства.** 84 из 375 записей доказательств привязаны к функции, а не к методу; сопоставление идёт только по коду метода, поэтому флагманские кейсы (AI Director в Left 4 Dead, рендер DOOM Eternal, трассировка пути Alan Wake 2) не показываются.

**Оценка оборудования не учитывает эпоху игры.** Каталог карт охватывает 2013–2025 годы, поэтому для F.E.A.R. (2005) ориентиром становится GTX 1050 Ti, а для Left 4 Dead (2008) — RX 580. Это «минимальный класс сегодня», а не исторические требования, и сравнение с ними некорректно.

**Целевой FPS никогда не проверяется.** Ни один сценарий не получил статуса `meets`/`at_risk` по частоте кадров: все — `not_modeled`. Движок честно отказывается прогнозировать FPS, но это же исключает проверку главного пользовательского ожидания.

### Что работает корректно

- Профиль нагрузки и подбор оборудования используют одну модель стоимости кадра: числа не расходятся между разделами.
- `P80 ≥ P50`, разделение клиентских/серверных/производственных эффектов, несуммирование RAM и VRAM, раздельный учёт трассировки и растеризации — инварианты соблюдены во всех 25 прогонах.
- Неизвестные входы не подменяются: отсутствие графического API, модели памяти или накопителя отражается в `modeling_gaps`, а не молчаливым значением.
- Неподдерживаемые платформы (PS4, Xbox One, Switch) не получают численного прогноза — выводится явная оговорка, а не выдуманное число.
- Детерминизм: повторный прогон тех же 25 профилей даёт те же результаты.
