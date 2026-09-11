# Доказательное исследование и DSS для проектирования игр

Дата генерации: 2026-09-11  
Ревизия репозитория: `efa8962`  
Снимок базы: `C:\Users\user\Desktop\game-inspect\backend\gamedev_dss.db` — полный локальный снимок

> Принцип отчёта: ни одно число не публикуется как измерение, если у него нет
> опубликованного источника с локатором или явной формулы с входными параметрами.
> Отсутствие данных даёт статус `unknown`, а не ноль и не «совместимо».

## 1. Область применимости и ограничения

Система — локальное PC-ориентированное приложение поддержки инженерных решений.
Оно связывает игровые функции, варианты реализации, движки и инструменты,
конфликты, технологические зависимости, цели качества, нагрузочный профиль,
референсный класс оборудования и план работ. Исследование универсальное: реальные
игры используются как проверяемые кейсы механизма, но не как паспорта
производительности для чужого проекта.

Количественная модель ограничена Windows PC и Linux PC. Целевой FPS, разрешение,
quality, RAM/VRAM, streaming pool, draw-call budget, simulation radius, physics
tick, сетевой latency/tick и storage задаются профилем. Если runtime-профиля
конкретного проекта нет, система не обещает точный FPS, точную latency или
календарную дату.

Вне текущего результата: прямое подключение к Unreal Insights/Unity Profiler,
импорт runtime-метрик, денежный бюджет, полноценная multi-user авторизация и
автоматическое изменение проекта движка.

### 1.1 Что система утверждает и чего не утверждает

| Утверждение | Статус | Основание |
| --- | --- | --- |
| Механизм метода подтверждён | documented / case_evidence | Документация, книга, спецификация или материал проекта с локатором |
| Число является измерением | measured | Опубликованное измерение с условиями и контекстом |
| Число вычислено из входов | derived | Явная формула и сохранённые входные параметры |
| Сценарный балл для ранжирования | expert_estimate | Помечается как сценарный, не как измерение |
| Точный FPS/latency/дата чужого проекта | не утверждается | Требуется runtime-профиль и трассы проекта |
| Совместимость без источника | не утверждается | Даёт `unknown`, а не `supported` |

## 2. Методология источников

### 2.1 Что считается источником

Источник — любой проверяемый носитель, где можно установить механизм,
ограничение, числовой результат или контекст. Реестр не ограничен статьями или
интервью. Поддерживаются официальная документация, книги и отдельные издания,
стандарты и спецификации, академические статьи, материалы конференций и видео,
инженерные postmortem, исходный код и открытые проекты, бенчмарки, интервью,
учебники, технические анализы и вторичные материалы.

Книга хранится с автором, издателем, изданием и главой. Спецификация — с версией и
разделом. Видео или доклад — с названием, датой и timestamp/слайдами. Для
исходного кода фиксируется репозиторий, commit/tag и путь к файлу. URL сам по себе
недостаточен: claim обязан иметь локатор.

### 2.2 Типы источников в реестре

| Тип источника | Записей |
| --- | --- |
| official_documentation | 317 |
| secondary | 311 |
| hardware_benchmark | 130 |
| conference_talk | 39 |
| open_source | 33 |
| book | 26 |
| engineering_blog | 21 |
| vendor_press_release | 14 |
| engineering_article | 7 |
| interview | 5 |
| api_specification | 5 |
| academic_paper | 5 |
| standard | 4 |
| studio_engineering | 2 |
| research | 2 |
| benchmark | 2 |
| technical_report | 1 |
| technical_guidance | 1 |
| studio_information | 1 |
| studio_engineering_article | 1 |
| practice_standard | 1 |
| postmortem | 1 |
| official_game_material | 1 |
| official_developer_resource | 1 |
| official_case_study | 1 |
| official_case_index | 1 |
| engineering_talk | 1 |
| conference_paper | 1 |
| benchmark_methodology | 1 |

### 2.3 Основание (basis) утверждений

| basis | Claims |
| --- | --- |
| documented | 1581 |
| unknown | 263 |
| case_evidence | 244 |
| derived | 208 |
| expert_estimate | 164 |
| measured | 104 |

- `measured` — опубликовано измерение с условиями;
- `documented` — механизм или ограничение прямо указаны в документации/книге/спецификации;
- `derived` — значение вычислено из явно сохранённых входных параметров и формулы;
- `case_evidence` — подтверждено материалом реального проекта;
- `expert_estimate` — сценарный балл для ранжирования или планирования;
- `unknown` — данных недостаточно.

Публикация без источника и локатора считается неполной. Отсутствие источника не
считается совместимостью. Конфликтующие материалы сохраняются одновременно, а
различие контекста показывается пользователю.

### 2.4 Методы с наименьшим числом claims

| Метод | Claims |
| --- | --- |
| path_tracing_sample_denoiser_budget | 6 |
| agent_update_budget | 7 |
| behaviour_tree_update_budget | 7 |
| crowd_instancing_impostors | 7 |
| dynamic_light_priority_budget | 7 |
| dynamic_resolution_scaling | 7 |
| froxel_volumetric_fog | 7 |
| full_path_tracing_pipeline | 7 |
| gpu_procedural_placement | 7 |
| light_range_attenuation_lod | 7 |
| ml_frame_generation | 7 |
| npc_perception_budget | 7 |
| post_effect_selective | 7 |
| screen_space_gi | 7 |
| splitscreen_render_budget | 7 |

Все 124 метода каталога покрыты минимум шестью claims. Большее число
claims не означает автоматически более высокую достоверность: важны наличие
измерений, локаторов и условий применения, а не количество строк.

### 2.5 Сила доказательства: прямой пример, перекрёстный пример, объявленный пробел

| Класс доказательства | Сущностей | Комментарий |
| --- | --- | --- |
| Инструмент движка: прямой пример (тот же движок) | 52 | из 71: shipped-тайтл на той же платформе, что и инструмент |
| Инструмент движка: только перекрёстный пример | 18 | возможность подтверждена на другом движке, adoption не подтверждён |
| Инструмент движка: adoption не подтверждён, пробел объявлен | 22 | поле adoption_evidence_gap, basis=unknown — пробел виден, а не заполнен |
| Технологические узлы с объявленным пробелом | 4 | исследовательские техники без shipped-тайтла |
| Методы с объявленным пробелом | 2 | нет второго независимого shipped-примера |

Покрытие «71 из 71» по игровым примерам означает лишь то, что к каждому инструменту приложен хотя бы один shipped-тайтл, где эта возможность работает. Это более слабое утверждение, чем «инструмент применён в показанной игре». Разделение ведётся явно:

- **прямой пример** — тайтл на том же движке, что и инструмент (52 сущностей);
- **перекрёстный пример** — тайтл на другом движке: подтверждает возможность, но не adoption (18 сущностей);
- **объявленный пробел** — shipped-подтверждения нет, и это зафиксировано полем `adoption_evidence_gap` с `basis=unknown` (22 сущностей).

Сущностей, у которых нет прямого примера и при этом пробел не объявлен: **0**. Это целевое значение — ноль: молчаливая дыра недопустима, потому что она indistinguishable от проверенного факта.

Правило для всех сущностей: **отсутствие источника не считается совместимостью**.
Если shipped-подтверждение найти не удалось, создаётся явная запись-пробел, а не
подбирается «похожий» пример. Пробел с `basis=unknown` и `evidence_level=low`
виден пользователю и в аудите; скрытая дыра — нет, поэтому она запрещена.

## 3. Классификация игровых функций

### 3.1 Категории и состав

| Категория | Функций |
| --- | --- |
| Рендер | 7 |
| Освещение | 6 |
| Мир и загрузка | 5 |
| Симуляция | 5 |
| Технические подсистемы | 4 |
| Визуальные эффекты | 3 |
| Персонажи | 2 |
| Производство | 2 |
| Геймплей | 1 |
| Звук | 1 |
| Прогресс и данные | 1 |
| Производительность | 1 |
| Производство контента | 1 |
| Сеть | 1 |

### 3.2 Полный перечень функций

| Код | Название | Категория | Форматы | Типы мира | Опорный источник |
| --- | --- | --- | --- | --- | --- |
| open_world_streaming | Потоковая загрузка открытого мира | Мир и загрузка | ["3D", "2.5D", "2D"] | ["open_world", "procedural", "sandbox"] | Unreal Engine: World Partition |
| large_scale_terrain | Крупномасштабный ландшафт | Мир и загрузка | ["3D", "2.5D"] | ["open_world", "procedural", "sandbox", "hub"] | Unreal Engine: Nanite Virtualized Geometry |
| procedural_terrain | Процедурная генерация ландшафта и мира | Мир и загрузка | ["3D", "2.5D", "2D"] | ["procedural", "open_world", "sandbox"] | Procedural generation |
| procedural_vegetation | Растительность и объекты окружения | Мир и загрузка | ["3D", "2.5D", "2D"] | ["open_world", "procedural", "sandbox", "linear"] | Unreal Engine: Instanced Static Mesh |
| storage_streaming | Потоковая работа с накопителем | Мир и загрузка | ["3D", "2.5D", "2D"] | ["open_world", "procedural", "sandbox", "linear", "hub"] | Unity Manual: Texture Streaming |
| dynamic_global_illumination | Динамическое глобальное освещение | Освещение | ["3D", "2.5D"] | ["open_world", "linear", "hub", "arena", "procedural", "sandbox"] | Unreal Engine: Lumen Global Illumination and Reflections |
| path_tracing | Трассировка пути | Освещение | ["3D"] | ["linear", "hub", "arena", "open_world"] | Path tracing |
| ray_traced_effects | Трассировочные эффекты (тени, отражения, AO) | Освещение | ["3D"] | ["linear", "hub", "arena", "open_world"] | Ray tracing (graphics) |
| dynamic_lighting | Множественные динамические источники света | Освещение | ["3D", "2.5D", "2D"] | ["open_world", "linear", "hub", "arena", "sandbox"] | Global illumination |
| baked_lighting | Запечённое освещение | Освещение | ["3D", "2.5D", "2D"] | ["linear", "hub", "arena"] | Lightmap |
| dynamic_shadows | Динамические тени | Освещение | ["3D", "2.5D", "2D"] | ["open_world", "linear", "hub", "arena", "procedural", "sandbox"] | Shadow mapping |
| particle_systems | Системы частиц | Визуальные эффекты | ["3D", "2.5D", "2D"] | ["open_world", "linear", "hub", "arena", "procedural", "sandbox"] | Particle system |
| physics_simulation | Физическая симуляция | Симуляция | ["3D", "2.5D", "2D"] | ["open_world", "linear", "hub", "arena", "procedural", "sandbox"] | Unreal Engine: Chaos Physics |
| vehicle_simulation | Транспорт и физика движения | Симуляция | ["3D", "2.5D"] | ["open_world", "arena", "sandbox", "linear"] | Vehicle dynamics |
| character_animation | Анимация персонажей | Персонажи | ["3D", "2.5D", "2D"] | ["open_world", "linear", "hub", "arena", "procedural", "sandbox"] | Skinning |
| gameplay_ability_system | Геймплейные способности и модификаторы | Геймплей | ["3D", "2.5D", "2D"] | ["open_world", "linear", "hub", "arena", "sandbox"] | Game Programming Patterns: State |
| crowd_simulation | Толпы NPC | Персонажи | ["3D", "2.5D", "2D"] | ["open_world", "linear", "hub", "sandbox"] | Unreal Engine: Mass Entity |
| ai_pathfinding | ИИ и поиск пути | Симуляция | ["3D", "2.5D", "2D"] | ["open_world", "linear", "hub", "arena", "procedural", "sandbox"] | Navigation mesh |
| advanced_npc_ai | Поведенческий ИИ NPC | Симуляция | ["3D", "2.5D", "2D"] | ["open_world", "linear", "hub", "arena", "sandbox"] | Video game artificial intelligence |
| water_simulation | Водные поверхности | Визуальные эффекты | ["3D", "2.5D", "2D"] | ["open_world", "procedural", "sandbox", "linear"] | Gerstner wave |
| volumetric_effects | Объёмные эффекты (туман, облака, дымка) | Визуальные эффекты | ["3D", "2.5D", "2D"] | ["open_world", "linear", "hub", "arena", "procedural", "sandbox"] | Volumetric rendering |
| post_processing | Постобработка изображения | Рендер | ["3D", "2.5D", "2D"] | ["open_world", "linear", "hub", "arena", "procedural", "sandbox"] | Temporal anti-aliasing |
| rendering_architecture | Архитектура рендера | Рендер | ["3D", "2.5D", "2D"] | ["open_world", "linear", "hub", "arena", "procedural", "sandbox"] | Deferred shading |
| render_scalability | Масштабирование качества | Рендер | ["3D", "2.5D", "2D"] | ["open_world", "linear", "hub", "arena", "procedural", "sandbox"] | Unreal Engine: Scalability Reference |
| geometry_pipeline | Конвейер геометрии | Рендер | ["3D", "2.5D"] | ["open_world", "linear", "hub", "arena", "procedural", "sandbox"] | meshoptimizer: mesh optimization library |
| upscaling_frame_generation | Масштабирование и генерация кадров | Рендер | ["3D", "2.5D"] | ["open_world", "linear", "hub", "arena", "procedural", "sandbox"] | Deep learning super sampling |
| mesh_shaders | Меш-шейдеры и генерация геометрии на GPU | Рендер | ["3D", "2.5D"] | ["open_world", "linear", "hub", "arena", "procedural", "sandbox"] | DirectX mesh shader specification |
| multiplayer_netcode | Сетевой код мультиплеера | Сеть | ["3D", "2.5D", "2D"] | ["open_world", "arena", "hub", "sandbox", "procedural"] | Client-side prediction |
| save_system | Система сохранений | Прогресс и данные | ["3D", "2.5D", "2D"] | ["open_world", "linear", "hub", "arena", "procedural", "sandbox"] | Unreal Engine: Saving and Loading Your Game |
| audio_system | Аудиосистема | Звук | ["3D", "2.5D", "2D"] | ["open_world", "linear", "hub", "arena", "procedural", "sandbox"] | Hunt: Showdown — Audio readability, realism and consistency |
| build_delivery | Сборка и доставка контента | Производство | ["3D", "2.5D", "2D"] | ["open_world", "linear", "hub", "arena", "procedural", "sandbox"] | Unity Manual: Addressables |
| runtime_memory | Память и сборка мусора | Производительность | ["3D", "2.5D", "2D"] | ["open_world", "linear", "hub", "arena", "procedural", "sandbox"] | Unity Manual: Garbage collection best practices |
| destruction_simulation | Разрушения и геометрические кэши | Симуляция | ["3D", "2.5D"] | ["open_world", "linear", "hub", "arena", "sandbox"] | Rendering the Hellscape of Doom Eternal (SIGGRAPH 2020) |
| project_architecture | Архитектура проекта | Производство | ["3D", "2.5D", "2D"] | ["open_world", "linear", "hub", "arena", "procedural", "sandbox"] | Data-oriented design |
| art_pipeline | Арт-пайплайн | Производство контента | ["3D", "2.5D", "2D"] | ["open_world", "linear", "hub", "arena", "procedural", "sandbox"] | Lightmap |
| split_screen_rendering | Split-screen рендеринг | Рендер | ["3D", "2.5D"] | ["linear", "hub", "arena", "sandbox"] | It Takes Two tech analysis (Digital Foundry) |
| portal_rendering | Дополнительные виды и порталы | Технические подсистемы | ["3D", "2.5D", "2D"] | [] | Epic: Scene Capture |
| hair_rendering | Волосы: пряди или карточки | Технические подсистемы | ["3D", "2.5D", "2D"] | [] | Epic: Hair Rendering and Simulation |
| cloth_simulation | Симуляция ткани | Технические подсистемы | ["3D", "2.5D", "2D"] | [] | Unity 6: Cloth |
| runtime_security | Проверки целостности и античит | Технические подсистемы | ["3D", "2.5D", "2D"] | [] | Epic: Anti-Cheat Interfaces |

## 4. Варианты реализации по подсистемам

### 4.1 Подсистемы и что измерять

| Подсистема | Варианты | Что измерять/проверять | Опорные источники |
| --- | --- | --- | --- |
| World and streaming | World Partition / HLOD / tile streaming / procedural generation | active cells, geometry, IO, decompression, memory and traversal hitches | S01, S18 |
| Rendering | Nanite or conventional geometry, raster, RT, VRS, upscaling, frame generation | main thread, draw/mesh preparation, raster/RT, VRAM and quality trade-offs | S02-S06, S19-S21 |
| Simulation and AI | fixed-step physics, ECS/jobs, relevance, budgets, director | simulation tick, parallel work, memory layout and content authoring | S07-S09, S11, S18, S20 |
| Networking | authoritative client/server, replication relevance, delta compression, sub-tick | server tick, serialization, bandwidth, latency and divergence validation | S12-S14, S22 |
| Audio | occlusion, material filtering, HRTF/spatial audio, mix readability | rays/queries, CPU, middleware cost, device variability and perception | S17, S18 |
| Build and delivery | asset bundles, patching, compression, cache and storage streaming | cook time, disk space, IO latency and release regression | S01, S07, S18 |

### 4.2 Implementation и optimization по категориям

| Категория | Implementation | Optimization | Всего |
| --- | --- | --- | --- |
| Освещение | 15 | 7 | 22 |
| Рендер | 6 | 14 | 20 |
| Мир и загрузка | 10 | 9 | 19 |
| Симуляция | 10 | 6 | 16 |
| Персонажи | 6 | 5 | 11 |
| Визуальные эффекты | 4 | 5 | 9 |
| Сеть | 5 | 3 | 8 |
| Технические подсистемы | 6 | 0 | 6 |
| Звук | 1 | 2 | 3 |
| Производство | 0 | 3 | 3 |
| Геймплей | 2 | 0 | 2 |
| Прогресс и данные | 2 | 0 | 2 |
| Производство контента | 0 | 2 | 2 |
| Производительность | 0 | 1 | 1 |

В каталоге 67 implementation и 57 optimization методов. Модель не выбирает один «лучший движок»
глобально. TOPSIS сравнивает сопоставимые альтернативы внутри функции, а
применимость проверяется до ранжирования по формату, миру, масштабу, платформе,
движку, железным возможностям, версии и условиям. Уверенность оценки — отдельный
критерий и не является процентом ускорения.

## 5. Сравнение движков и инструментов

| Движок/подход | Инструменты и механизмы | Проверка применимости | Доказательства |
| --- | --- | --- | --- |
| Unreal | World Partition, Nanite, Lumen, VSM, Mass, Replication Graph | Версия, RHI, SM6/RT, streaming range and asset compatibility require a prototype. | S01-S04 |
| Unity | Job System, Entities/DOTS, Addressables, Netcode | Package versions and migration boundary are part of the dependency contract. | S07-S09 |
| Godot | scene/visibility optimization, high-level multiplayer, custom scripts | Open-source flexibility does not remove project-specific profiling. | S10 |
| CryEngine | renderer, audio and streaming capabilities | The case evidence is stronger for audio than for a universal hardware budget. | S17 |
| Source / Source 2 | network simulation, tick/sub-tick, established multiplayer workflows | Valve case materials document mechanisms, not a transferable project estimate. | S11-S14 |
| HeroEngine | shared-world/editor-oriented workflows from the existing catalog | Public evidence and current-version compatibility must be reviewed per tool. | catalog claims |
| Custom | own runtime, network, renderer or service | Every mechanism needs a project-owned design record and measurement plan. | expert boundary |

Legacy-движок `custom` и его инструменты помечаются пользовательскими. Пустая
связь с инструментом не означает «поддерживается»: для engine-independent решения
хранится отдельный признак, а для неизвестной версии доступность получает статус
`unknown`.

## 6. Версия и платформенная совместимость

| Платформа / ветка | Что доступно | Ограничение проверки | Источники |
| --- | --- | --- | --- |
| Windows PC (D3D12, SM6) | Nanite, Lumen HW path, VSM, VRS, mesh shaders, RT tiers | D3D12 feature level задаёт функциональность, но не производительность; опции проверяются через CheckFeatureSupport | S04, S38, S39, S40 |
| Windows PC (D3D12, SM5) | часть методов недоступна или требует fallback | Отсутствие возможности не считается совместимостью: метод либо помечается недоступным, либо требует явного fallback-плана | S04 |
| Windows PC (Vulkan) | RT, mesh shaders, VRS через расширения Vulkan | Расширения и очереди объявляются при создании устройства; нужен отдельный capability-профиль | S22 |
| Linux PC (Vulkan) | RT и compute-пути, отличные от D3D12-ветки | Количественная граница модели ограничена Windows/Linux PC; результаты не переносятся на консоли и мобильные | S22 |
| Non-PC (console/mobile/cloud) | остаются в профиле для полноты | Не получают совместимый аппаратный ориентир; помечаются `not_modeled`, а не приближённой оценкой | expert boundary |
| Server / dedicated | replication, tick, relevance, serialization | Server-only стоимость не уменьшает требования client PC и не суммируется с ними | S26, S27 |

Поддержка движка — это не бинарный `engine=yes`. Она включает version,
package/plugin, target platform/API, scope (`runtime`, `editor`, `build`, `server`,
`development`), tool relation и свежесть доказательства. HeroEngine оставлен в
каталоге из-за фиксированного охвата, но его public applicability —
`legacy/needs_review`, а не подтверждённая текущая совместимость.

## 7. Зависимости, конфликты и альтернативы

Граф состоит из методов, движков, инструментов, API, SDK и библиотек. Ребро
направлено и хранит mandatory, min/max version, platform, scope, severity,
источник, описание и workaround.

### 7.1 Типы связей между решениями

| Тип связи | Записей |
| --- | --- |
| complement | 181 |
| dependency | 77 |
| risk | 74 |
| overlap | 67 |
| alternative | 41 |
| unknown | 8 |
| hard_conflict | 4 |

### 7.2 Состав узлов графа

| Тип узла | Узлов |
| --- | --- |
| method | 124 |
| tool | 71 |
| plugin | 8 |
| engine | 7 |
| lib | 6 |
| api | 4 |
| sdk | 2 |

### 7.3 Обязательные и условные рёбра (выборка)

| Источник | Цель | Тип | Обязательность | Мин. версия | Платформа | Severity | Источник |
| --- | --- | --- | --- | --- | --- | --- | --- |
| method:cloth_constraint_simulation | method:fixed_timestep_physics | dependency | обязательная | — | — | 3 | Physics Sub-Stepping in Unreal Engine |
| method:runtime_fracture_budget | method:physics_lod_sleeping | dependency | обязательная | — | — | 3 | Godot Engine - RigidBody3D class reference |
| method:runtime_fracture_budget | method:broadphase_spatial_partitioning | dependency | обязательная | — | — | 3 | GPU Gems 3, Chapter 32: Broad-Phase Collision Detection with CUDA |
| method:flipbook_particles | method:sprite_particle_atlas | dependency | обязательная | — | — | 3 | Niagara Flipbook Baker Quick Start Guide in Unreal Engine |
| method:fixed_timestep_physics | method:raycast_vehicle_physics | dependency | обязательная | — | — | 3 | Godot Engine - VehicleBody3D class reference |
| method:multithreaded_physics_jobs | method:fixed_timestep_physics | dependency | обязательная | — | — | 3 | Physics Sub-Stepping in Unreal Engine |
| method:composition_bootstrap_architecture | method:ecs_data_oriented_crowd | dependency | обязательная | — | — | 3 | Unity DOTS product page |
| method:vehicle_simulation_lod | method:physics_lod_sleeping | dependency | обязательная | — | — | 3 | Godot Engine - RigidBody3D class reference |
| method:animation_compression | method:motion_matching | dependency | обязательная | — | — | 3 | Learned Motion Matching (project page + abstract) |
| method:animation_lod_budget | method:gpu_skinning_compute | dependency | обязательная | — | — | 3 | нет публичного источника |
| method:normal_bake_retopology_pipeline | method:gpu_skinning_compute | dependency | обязательная | — | — | 3 | Skeletal Mesh Rendering Paths in Unreal Engine (Unreal Engine 5.8 Documentation) |
| method:art_direction_stylization | method:ability_visual_effect_budget | dependency | обязательная | — | — | 3 | Scalability and Best Practices for Niagara (Unreal Engine 5.8 Documentation) |
| method:tilemap_chunk_streaming | method:tilemap_layer_culling | dependency | обязательная | — | — | 3 | Unity Manual - Tilemap Renderer component reference |
| method:sprite_atlas_batching | method:sprite_sheet_compression | dependency | обязательная | — | — | 3 | Block Compression (Direct3D 10) - Microsoft Learn |
| method:sprite_atlas_batching | method:tilemap_layer_culling | dependency | обязательная | — | — | 3 | Unity Manual - Tilemap Renderer component reference |
| method:ability_visual_effect_budget | method:data_driven_ability_system | dependency | обязательная | — | — | 3 | Understanding the Unreal Engine Gameplay Ability System (Unreal Engine 5.8 Documentation) |
| method:client_prediction_reconciliation | method:tickrate_budgeting | dependency | обязательная | — | — | 3 | Source Multiplayer Networking (Valve Developer Community wiki) |
| method:client_prediction_reconciliation | method:headless_dedicated_server | dependency | обязательная | — | — | 3 | нет публичного источника |
| method:delta_compression_state | method:headless_dedicated_server | dependency | обязательная | — | — | 3 | Setting Up Dedicated Servers in Unreal Engine (UE 5.8 Documentation) |
| method:delta_compression_state | method:network_relevancy_priority | dependency | обязательная | — | — | 3 | нет публичного источника |
| method:headless_dedicated_server | method:tickrate_budgeting | dependency | обязательная | — | — | 3 | VALORANT's 128-Tick Servers (Riot Games tech blog) |
| method:headless_dedicated_server | method:network_relevancy_priority | dependency | обязательная | — | — | 3 | Replication Graph in Unreal Engine (UE 5.8 Documentation) |
| method:subtick_networking | method:client_prediction_reconciliation | dependency | обязательная | — | — | 3 | нет публичного источника |
| method:lag_compensation_rewind | method:subtick_networking | dependency | обязательная | — | — | 3 | Lag Compensation (Valve Developer Community wiki) |
| method:lag_compensation_rewind | method:client_prediction_reconciliation | dependency | обязательная | — | — | 3 | нет публичного источника |
| method:lag_compensation_rewind | method:network_relevancy_priority | dependency | обязательная | — | — | 3 | нет публичного источника |
| method:audio_convolution_reverb | method:audio_occlusion_propagation | dependency | обязательная | — | — | 3 | Steam Audio - Programmer's Guide (C API) |
| method:runtime_security_budget | method:headless_dedicated_server | dependency | обязательная | — | — | 3 | Using the Anti-Cheat Interfaces (Epic Online Services / Easy Anti-Cheat) |
| method:managed_gc_alloc_budget | method:tickrate_budgeting | dependency | обязательная | — | — | 3 | нет публичного источника |
| method:hardware_raytraced_gi | method:deferred_forward_plus_choice | dependency | обязательная | — | — | 3 | нет публичного источника |
| method:hardware_raytraced_gi | method:temporal_upscaling | dependency | обязательная | — | — | 3 | нет публичного источника |
| method:hardware_raytraced_gi | method:selective_ray_traced_effects | dependency | обязательная | — | — | 3 | нет публичного источника |
| method:screen_space_gi | method:deferred_forward_plus_choice | dependency | обязательная | — | — | 3 | нет публичного источника |
| method:screen_space_gi | method:temporal_upscaling | dependency | обязательная | — | — | 3 | нет публичного источника |
| method:irradiance_volume_probes | method:lightmap_atlas_baking | dependency | обязательная | — | — | 3 | нет публичного источника |
| method:temporal_radiance_cache | method:hardware_raytraced_gi | dependency | обязательная | — | — | 3 | нет публичного источника |
| method:temporal_radiance_cache | method:deferred_forward_plus_choice | dependency | обязательная | — | — | 3 | нет публичного источника |
| method:voxel_cone_tracing | method:deferred_forward_plus_choice | dependency | обязательная | — | — | 3 | нет публичного источника |
| method:dynamic_light_priority_budget | method:tiled_clustered_light_culling | dependency | обязательная | — | — | 3 | Clustered Deferred and Forward Shading |
| method:light_range_attenuation_lod | method:dynamic_light_priority_budget | dependency | обязательная | — | — | 3 | нет публичного источника |
| method:distance_field_shadows | method:sdf_global_illumination | dependency | обязательная | — | — | 3 | нет публичного источника |
| method:screen_space_contact_shadows | method:deferred_forward_plus_choice | dependency | обязательная | — | — | 3 | нет публичного источника |
| method:static_shadow_caching | method:virtual_shadow_maps | dependency | обязательная | — | — | 3 | Virtual Shadow Maps (Unreal Engine 5.8 Documentation) |
| method:lightmap_atlas_baking | method:lightmap_compression_streaming | dependency | обязательная | — | — | 3 | Real-Time Rendering, 4th edition |
| method:gpu_lightmap_baking | method:lightmap_atlas_baking | dependency | обязательная | — | — | 3 | Lightmap (Wikipedia) |
| method:froxel_volumetric_fog | method:deferred_forward_plus_choice | dependency | обязательная | — | — | 3 | нет публичного источника |
| method:volumetric_half_resolution | method:froxel_volumetric_fog | dependency | обязательная | — | — | 3 | нет публичного источника |
| method:rt_effect_resolution_budget | method:selective_ray_traced_effects | dependency | обязательная | — | — | 3 | Exploring Ray Traced Future in Metro Exodus (GTC 2019) |
| method:full_path_tracing_pipeline | method:path_tracing_sample_denoiser_budget | dependency | обязательная | — | — | 3 | Path Tracer (Unreal Engine 5.8 Documentation) |
| method:full_path_tracing_pipeline | method:temporal_upscaling | dependency | обязательная | — | — | 3 | нет публичного источника |
| method:deferred_forward_plus_choice | method:dynamic_light_priority_budget | dependency | обязательная | — | — | 3 | Rendering the Hellscape of Doom Eternal |
| method:depth_prepass_early_z | method:deferred_forward_plus_choice | dependency | обязательная | — | — | 3 | Real-Time Rendering, 4th edition |
| method:dynamic_resolution_scaling | method:temporal_upscaling | dependency | обязательная | — | — | 3 | нет публичного источника |
| method:post_effect_selective | method:quality_tier_scalability | dependency | обязательная | — | — | 3 | Scalability (Unreal Engine 5.8 Documentation) |
| method:screenspace_light_shafts | method:post_effect_selective | dependency | обязательная | — | — | 3 | Volumetric Fog: Unified, compute shader based solution to atmospheric scattering |
| method:variable_rate_shading | method:deferred_forward_plus_choice | dependency | обязательная | — | — | 3 | нет публичного источника |
| method:ml_frame_generation | method:temporal_upscaling | dependency | обязательная | — | — | 3 | нет публичного источника |
| method:portal_scene_capture_budget | method:quality_tier_scalability | dependency | обязательная | — | — | 3 | Scalability (Unreal Engine 5.8 Documentation) |
| method:splitscreen_render_budget | method:quality_tier_scalability | dependency | обязательная | — | — | 3 | Scalability (Unreal Engine 5.8 Documentation) |
| method:splitscreen_render_budget | method:post_effect_selective | dependency | обязательная | — | — | 3 | Scalability (Unreal Engine 5.8 Documentation) |
| method:gpu_meshlet_culling_budget | method:meshlet_pipeline_adoption | dependency | обязательная | — | — | 3 | VK_EXT_mesh_shader proposal (Vulkan Documentation Project) |
| method:world_partition_streaming | method:async_loading_pipeline | dependency | обязательная | — | — | 3 | Asynchronous Asset Loading in Unreal Engine |
| method:hierarchical_lod | method:world_partition_streaming | dependency | обязательная | — | — | 3 | World Partition - Hierarchical Level of Detail in Unreal Engine |
| method:gpu_compute_culling | method:mesh_index_optimization | dependency | обязательная | — | — | 3 | нет публичного источника |
| method:terrain_clipmap | method:heightmap_compression | dependency | обязательная | — | — | 3 | C-BDAM - Compressed Batched Dynamic Adaptive Meshes for Terrain Rendering |
| method:virtual_texturing | method:async_loading_pipeline | dependency | обязательная | — | — | 3 | Nanite: A Deep Dive (SIGGRAPH 2021, Advances in Real-Time Rendering in Games) |
| method:heightmap_compression | method:build_size_startup_budgets | dependency | обязательная | — | — | 3 | Oodle Data (Unreal Engine Documentation) |
| method:virtual_geometry_clusters | method:gpu_compute_culling | dependency | обязательная | — | — | 3 | Nanite: A Deep Dive (SIGGRAPH 2021, Advances in Real-Time Rendering in Games) |
| method:virtual_geometry_clusters | method:mesh_index_optimization | dependency | обязательная | — | — | 3 | нет публичного источника |
| method:gpu_instancing_vegetation | method:gpu_compute_culling | dependency | обязательная | — | — | 3 | GPU-Driven Rendering Pipelines (SIGGRAPH 2015, Advances in Real-Time Rendering in Games) |
| method:gpu_procedural_placement | method:gpu_instancing_vegetation | dependency | обязательная | — | — | 3 | GPU-Based Procedural Placement in Horizon Zero Dawn (GDC 2017) |
| method:impostors_billboards | method:vegetation_atlas_lod | dependency | обязательная | — | — | 3 | GPU Gems 3, Chapter 4: Next-Generation SpeedTree Rendering |
| method:vegetation_atlas_lod | method:gpu_instancing_vegetation | dependency | обязательная | — | — | 3 | Instanced Static Mesh in Unreal Engine |
| method:terrain_generation_streaming_budget | method:async_loading_pipeline | dependency | обязательная | — | — | 3 | Asynchronous Asset Loading in Unreal Engine |
| method:build_size_startup_budgets | method:directstorage_io | dependency | обязательная | — | — | 3 | DirectStorage (Win32 apps) - Microsoft Learn |
| method:directstorage_io | method:async_loading_pipeline | dependency | обязательная | — | — | 3 | Asynchronous Asset Loading in Unreal Engine |
| method:directstorage_io | method:terrain_generation_streaming_budget | dependency | обязательная | — | — | 3 | DirectStorage (Win32 apps) - Microsoft Learn |
| tool:ue_vsm | api:directx12 | runtime_api | обязательная | SM6 | pc_windows | 2 | Supported Features by Rendering Path for Desktop |
| tool:ue_replication_graph | engine:unreal | engine_tool | обязательная | — | — | 2 | Unreal Engine: Replication Graph |
| tool:u_dots | engine:unity | engine_tool | обязательная | — | — | 2 | Unity Manual: Entities (DOTS) |
| tool:u_netcode | tool:u_dots | package | обязательная | 1.0 | pc_windows,pc_linux | 2 | Unity Manual: Netcode |
| tool:ue_nanite | api:vulkan | runtime_api | обязательная | SM6 | pc_linux | 2 | Supported Features by Rendering Path for Desktop |
| tool:u_dots | plugin:unity.entities | package | обязательная | 1.0 | pc_windows,pc_linux | 2 | Unity Manual: Entities (DOTS) |
| tool:u_dots | plugin:unity.burst | package | обязательная | 1.0 | pc_windows,pc_linux | 2 | Unity Manual: Entities (DOTS) |
| tool:u_netcode | plugin:unity.entities | package | обязательная | 1.0 | pc_windows,pc_linux | 2 | Unity Manual: Netcode |
| tool:u_netcode | plugin:unity.transport | package | обязательная | 1.0 | pc_windows,pc_linux | 2 | Unity Manual: Netcode |
| tool:u_addressables | plugin:unity.addressables | package | обязательная | 1.0 | pc_windows,pc_linux | 2 | Unity Manual: Addressables |
| tool:u_srp | plugin:unity.srp | package | обязательная | 1.0 | pc_windows,pc_linux | 2 | Unity Manual: Optimizing Graphics Performance |
| method:directstorage_io | sdk:directstorage | sdk | обязательная | — | pc_windows | 2 | DirectStorage API Now Available on PC (DirectX Developer Blog) |
| tool:ue_nanite | api:directx12 | runtime_api | обязательная | SM6 | pc_windows | 1 | Supported Features by Rendering Path for Desktop |
| tool:u_addressables | engine:unity | engine_tool | обязательная | — | — | 1 | Unity Manual: Addressables |
| tool:ue_nanite | engine:unreal | engine | обязательная | — | — | 1 | Nanite Virtualized Geometry Overview (Unreal Engine 5.8 Documentation) |
| tool:ue_lumen | engine:unreal | engine | обязательная | — | — | 1 | Lumen Global Illumination and Reflections (Unreal Engine 5.8 Documentation) |
| tool:ue_world_partition | engine:unreal | engine | обязательная | — | — | 1 | World Partition (Unreal Engine 5.8 Documentation) |
| tool:ue_vsm | engine:unreal | engine | обязательная | — | — | 1 | Virtual Shadow Maps (Unreal Engine 5.8 Documentation) |
| tool:ue_niagara | engine:unreal | engine | обязательная | — | — | 1 | Unreal Engine: Niagara Visual Effects |
| tool:ue_chaos | engine:unreal | engine | обязательная | — | — | 1 | Unreal Engine: Chaos Physics |
| tool:ue_hlod | engine:unreal | engine | обязательная | — | — | 1 | Hierarchical Level of Detail in Unreal Engine (Epic official documentation) |
| tool:ue_virtual_texturing | engine:unreal | engine | обязательная | — | — | 1 | Virtual Texturing in Unreal Engine |
| tool:ue_insights | engine:unreal | engine | обязательная | — | — | 1 | Unreal Insights |
| tool:ue_navmesh | engine:unreal | engine | обязательная | — | — | 1 | Unreal Engine: Navigation Mesh |
| tool:ue_replication_graph | engine:unreal | engine | обязательная | — | — | 1 | Replication Graph in Unreal Engine |
| tool:ue_significance | engine:unreal | engine | обязательная | — | — | 1 | Significance Manager |
| tool:ue_anim_budget | engine:unreal | engine | обязательная | — | — | 1 | Animation Budget Allocator |
| tool:ue_ism | engine:unreal | engine | обязательная | — | — | 1 | Instanced Static Mesh in Unreal Engine |
| tool:ue_mass | engine:unreal | engine | обязательная | — | — | 1 | MassEntity in Unreal Engine |
| tool:ue_lwc | engine:unreal | engine | обязательная | — | — | 1 | Unreal Engine: Large World Coordinates |
| tool:ue_lod | engine:unreal | engine | обязательная | — | — | 1 | Unreal Engine: Level of Detail |
| tool:ue_gas | engine:unreal | engine | обязательная | — | — | 1 | Gameplay Ability System in Unreal Engine (Epic official documentation) |
| tool:ue_behavior_tree | engine:unreal | engine | обязательная | — | — | 1 | Behavior Trees |
| tool:ue_vehicles | engine:unreal | engine | обязательная | — | — | 1 | нет публичного источника |
| tool:u_dots | engine:unity | engine | обязательная | — | — | 1 | Unity Entities package manual |
| tool:u_jobs | engine:unity | engine | обязательная | — | — | 1 | Unity Manual - Write multithreaded code with the job system |
| tool:u_addressables | engine:unity | engine | обязательная | — | — | 1 | Unity Manual: Addressables |
| tool:u_srp | engine:unity | engine | обязательная | — | — | 1 | Unity Manual: Optimizing Graphics Performance |
| tool:u_instancing | engine:unity | engine | обязательная | — | — | 1 | Introduction to GPU instancing |
| tool:u_occlusion | engine:unity | engine | обязательная | — | — | 1 | Occlusion Culling (Unity official documentation) |
| tool:u_lightmapper | engine:unity | engine | обязательная | — | — | 1 | Progressive Lightmapper (Unity Manual) |
| tool:u_light_probes | engine:unity | engine | обязательная | — | — | 1 | Light Probes (Unity official documentation) |
| tool:u_vfxgraph | engine:unity | engine | обязательная | — | — | 1 | Unity Manual: Optimizing Graphics Performance |

В выборке обязательных рёбер: 120; с публичным источником:
92. Рёбра без публичного источника несут явную пометку «нет
публичного источника», а не молчаливую совместимость.

### 7.4 Проверки графа

| Проверка | Что обнаруживает | Реакция системы |
| --- | --- | --- |
| missing_node | ребро ссылается на узел, которого нет в графе | ребро помечается unresolved |
| cyclic_mandatory | цикл обязательных зависимостей | цикл не скрывается; одно ребро детерминированно понижается до complement с записью resolution |
| unsupported_version | версия ниже/выше поддерживаемой | метод помечается неприменимым для этой версии |
| version_unknown | версия не указана | статус `unknown`, а не «совместимо» |
| api_incompatibility | требуется API/feature, которого нет на цели | метод отфильтровывается до ранжирования |
| basket_hard_conflict | в корзине есть hard conflict | hard conflict исключается из рабочей корзины |
| unresolved_dependency | транзитивная зависимость не закрыта | корзина помечается неполной |
| unknown_relation | связь типа unknown | показывается пользователю как открытый вопрос |
| user_defined_tool | пользовательский движок/инструмент | помечается user_defined; публичный источник не требуется, но нужен project-owned design record |

При расчёте корзины система проверяет hard conflict, risk, alternative,
dependency, complement, overlap и unknown отдельно. Обязательные зависимости
расширяются транзитивно; неизвестный узел остаётся unresolved. Цикл обязательных
зависимостей не скрывается. Дополнение описывает совместное применение, но не
создаёт неподтверждённого прироста.

## 8. Масштаб сцены

| Параметр | Единицы/входы | Что определяет | Источники |
| --- | --- | --- | --- |
| Размер мира | km², число cell/grid, loading range | потоковые запросы, IO-байты, activation time, RAM/VRAM residency | S01, S24 |
| Плотность контента | instances/клетка, плотность PCG-вывода | cook/build time, draw/mesh preparation, proxy-несоответствие | S25 |
| Дальность видимости | view distance, HLOD-уровни | GPU raster/RT, raster-pass cost, VRAM потоковой подкачки | S24, S19 |
| Число активных агентов | NPC, physics bodies, dynamic lights | simulation tick, navigation, animation, parallel CPU | S07, S31 |
| Плотность эффектов | particles, decals, post-проходы | GPU raster, overdraw, transient memory | S19, S21 |

Размер мира сам по себе не является числом для FPS. Управляемые переменные —
размер ячейки, loading range, число источников, HLOD-представление, размер чанка,
скорость чтения, декомпрессия и время активации. Поэтому в DSS они отдельные поля,
а не один scalar `open_world=true`.

## 9. CPU, GPU, RAM, VRAM и накопитель

| Ось | Состав | Правило моделирования | Источники |
| --- | --- | --- | --- |
| CPU main-thread | game logic, render-thread, IO completion, activation | никогда не суммируется с parallel и не складывается в один scalar | S18, S47 |
| CPU parallel | jobs/ECS, physics, animation, culling, worker threads | верхняя граница задаётся Amdahl, а не числом ядер | S31, S37 |
| GPU raster | geometry pass, shading, decals, particles, post | зависит от внутреннего разрешения и shading-rate | S19, S05 |
| GPU RT | RT GI/reflections/shadows, BVH build/refit | отдельная ось от raster; tier проверяется перед выбором | S03, S40 |
| RAM | textures, geometry, audio, streaming pool, transient | не складывается с VRAM в одну величину | S18, S54 |
| VRAM | residency текстур/геометрии, render targets, RT structures | ограничивается одновременно raster, RT и streaming pool | S54, S55 |
| Storage / IO | read throughput, decompression, cold/warm cache | быстрый носитель не компенсирует плохую приоритизацию ассетов | S23, S52 |
| Network | bandwidth, tick, relevance set, serialization | моделируется отдельно от render FPS и input latency | S12, S26 |

### 9.1 Пример композиции памяти

| Компонент | Входы | Результат | Основание |
| --- | --- | --- | --- |
| Textures / geometry | 2.4 + 1.1 | 3.5 GiB | scenario input |
| Render targets / transient | 0.8 + 0.6 | 1.4 GiB | scenario input |
| Audio / other | 0.2 | 0.2 GiB | scenario input |
| Subtotal | 3.5 + 1.4 + 0.2 | 5.1 GiB | sum, no headroom |
| 20% safety/headroom | 5.1 × 1.20 | 6.12 GiB | derived planning allowance |

RAM и VRAM не складываются в одну величину. Память состоит из текстур, геометрии,
render targets, streaming pool, audio, временных буферов и возможных CPU-копий.
GPU подбирается одновременно по raster, RT, VRAM, API и обязательным feature
flags; CPU — по single-thread и multi-thread. Physics и AI пересчитываются по
собственному fixed tick и не считаются как дополнительный FPS. Апскейлинг изменяет
внутреннее разрешение; frame generation добавляет собственный проход и не делает
уже отрисованный кадр бесплатным.

## 10. Сетевые режимы

| Режим | Модель | Ограничение | Источники |
| --- | --- | --- | --- |
| Single-player / local | нет сети; стоимость кадра только локальная | не получает сетевого бюджета и не вычитает его | expert boundary |
| Local co-op / split-screen | несколько видов на одном устройстве | несколько камер/видов умножают raster-работу; FPS не является нормативом | S15 |
| Listen / host-authoritative | хост считает симуляцию и рендерит | server-нагрузка и client-нагрузка складываются на одном устройстве | S26, S27 |
| Dedicated authoritative | выделенный сервер, клиент только предсказывает | server frame и client frame моделируются раздельно | S12, S14 |
| Competitive high-tick | 128 Hz-класс симуляции, prediction/rewind | высокий tick — свойство сервиса, а не универсальная рекомендация | S13, S14 |
| Sub-tick / event-timed | точный момент события внутри такта | sub-tick, prediction и rewind — дополняющие части протокола, а не три скидки | S12 |
| P2P / relay | relay-маршрутизация без выделенного сервера | latency и loss зависят от маршрута; требуется измерение, а не оценка | S30, S53 |

### 10.1 Примеры воспроизводимых сетевых расчётов

| Scenario | Inputs | Derived result | Limits |
| --- | --- | --- | --- |
| Server → 9 clients | C=9, f=20/s, payload=120 B, IPv4+UDP H=28 B | 9×20×(120+28)=26,640 B/s ≈ 26.0 KiB/s ≈ 213 kbps | derived; excludes encryption, retransmits and other traffic |
| 128 Hz server frame | 1 / 128 s | 7.8125 ms per tick | published VALORANT case S14; not universal target |
| Riot 3 games/core target | 7.8125 / 3 | 2.6042 ms; ×0.90 = 2.3438 ms | published case S14; host/game-specific |

Server tick, render FPS, input latency, buffering, relevance set, serialization,
packet loss и bandwidth моделируются раздельно. Пример Epic с Fortnite —
документация механизма, а не лимит нового проекта. Число игроков без частоты
обновлений и размера состояния не определяет traffic.

## 11. Целевые показатели качества и производительности

### 11.1 Статусы оценки цели

| Статус | Значение | Правило | Основание |
| --- | --- | --- | --- |
| meets | сценарий укладывается в frame-time budget при заданных условиях | применяется к p95/p99 frame-time, а не к одной средней частоте кадров | derived |
| at_risk | сценарий близок к границе или зависит от непроверенного условия | показывает, какой именно ресурс на границе и что нужно измерить | derived |
| unknown | данных недостаточно для вывода | не заменяется нулём, средним или «похожей картой» | expert_estimate |
| not_modeled | цель вне количественной границы модели (non-PC, latency, 1% low без измерения) | остаётся в профиле, но без числового ориентира | expert boundary |

### 11.2 Бюджет кадра

| Target FPS | Frame budget, ms | Интерпретация |
| --- | --- | --- |
| 30 | 33.333 | low/quality-first target |
| 60 | 16.667 | common responsiveness target |
| 90 | 11.111 | high-refresh baseline |
| 120 | 8.333 | high-refresh target |
| 144 | 6.944 | competitive/high-refresh case |
| 240 | 4.167 | very high-refresh case; content-dependent |

### 11.3 Пиксельная нагрузка разрешения

| Разрешение | Pixel ratio | База |
| --- | --- | --- |
| 1280x720 | 0.444 | relative to 1920x1080 |
| 1920x1080 | 1.000 | baseline |
| 2560x1440 | 1.778 | relative to 1080p |
| 3840x2160 | 4.000 | relative to 1080p; 2.25x 1440p |

`frame_budget_ms = 1000 / target_fps`. Сценарные цели показываются как `meets`,
`at_risk`, `unknown` или `not_modeled`. Для 1% low FPS, startup, streaming
latency, save time, network latency, server tick и traffic не создаётся значение,
если оно не введено пользователем или не подтверждено измерением. Критерий `meets`
применяется к frame-time budget, а не к одной средней частоте кадров.

## 12. Стадии и work packages

| Тип пакета | Пакетов | Мин. P50 | Сред. P50 | Сред. P80 | Основание |
| --- | --- | --- | --- | --- | --- |
| content | 124 | 0.47 | 2.87 | 5.32 | expert_estimate |
| design | 124 | 0.44 | 2.41 | 4.48 | expert_estimate |
| feasibility | 58 | 0.7 | 5.04 | 9.24 | expert_estimate |
| integration | 124 | 0.98 | 5.55 | 10.31 | expert_estimate |
| optimization | 124 | 0.44 | 2.62 | 4.86 | expert_estimate |
| qa | 124 | 0.44 | 2.51 | 4.66 | expert_estimate |
| release | 124 | 0.24 | 1.32 | 2.46 | expert_estimate |

План строится из work packages: design, feasibility/prototype, integration,
content/assets, optimization, QA/regression, release stabilization,
documentation/maintenance. Каждый пакет имеет min, P50, P80, роль,
параллелизуемость, стадию, late factor, зависимости и основание. Legacy
`implementation_cost` сохранён для совместимости, но не является основой плана.

## 13. Трудоёмкость P50/P80 и календарь для разных команд

### 13.1 Профили команд

| Код | Название | Размер | Параллельные потоки | Коммуникации | Непредвиденное |
| --- | --- | --- | --- | --- | --- |
| solo | Solo | 1 | 1 | 5% | 25% |
| small_2_5 | Малая команда (2-5) | 4 | 2 | 12% | 18% |
| custom | Собственный состав | 6 | 3 | 15% | 16% |
| mid_6_15 | Средняя команда (6-15) | 10 | 5 | 18% | 15% |
| large_16_plus | Большая команда (16+) | 24 | 12 | 25% | 12% |

P50/P80 выражены в человеко-днях и не являются отраслевым нормативом. P50 —
наиболее вероятный сценарий при описанных допущениях; P80 — более осторожный
сценарий с неопределённостью. Команда влияет на календарную ёмкость, но не
уменьшает сумму person-days.

### 13.2 Трёхточечная оценка

| Inputs | Calculation | Статус |
| --- | --- | --- |
| O=2, M=4, P=10 человеко-дней | (2 + 4×4 + 10) / 6 = 4.667 | beta/PERT expected duration |
| Тот же диапазон | σ = (10 − 2) / 6 = 1.333 | approximate spread; not a calibrated percentile |
| P80 proxy, only if explicitly assumed normal | 4.667 + 0.8416×1.333 = 5.789 | derived scenario, not a measurement |

### 13.3 Предел параллелизации (Amdahl)

| Workers | Speedup | Допущение |
| --- | --- | --- |
| N=1 | 1.000 | baseline |
| N=2 | 1.429 | s=0.40, idealized |
| N=4 | 1.818 | s=0.40, idealized |
| N=8 | 2.105 | s=0.40, idealized |
| N=16 | 2.353 | s=0.40, idealized |
| N→∞ | 2.500 | serial ceiling 1/s |

### 13.4 Critical path (пример)

| Task | Duration | Predecessors | Path result |
| --- | --- | --- | --- |
| A Design | 3 | — | A-B-D-E / A-C-D-E |
| B Prototype | 5 | A | A-B-D-E = 18 |
| C Content/asset prep | 8 | A | A-C-D-E = 21; critical |
| D Integration | 6 | B,C | merge waits for max(B,C) |
| E QA/release gate | 4 | D | longest path ends at 21 |

Календарь вычисляется по dependency DAG и доступности роли. Независимые задачи
могут идти параллельно; integration, QA, release gates и узкие роли формируют
critical path. Поздняя стадия не убирает метод из выдачи, а добавляет
rework/late-risk note.

## 14. Профили нагрузки

| Профиль | Состав | Доминирующие оси | Источники |
| --- | --- | --- | --- |
| Открытый мир | streaming + HLOD + большая дальность | IO, decompression, VRAM residency, traversal hitches | S01, S24, S28 |
| Арена / линейный | ограниченный набор ячеек, много эффектов | GPU raster, overdraw, transient memory | S16, S19 |
| Симуляция/стратегия | много агентов, ECS/jobs, navigation | parallel CPU, simulation tick, cache locality | S07, S31 |
| Соревновательный сетевой | высокий tick, prediction/rewind, relevance | server frame, serialization, bandwidth, divergence | S12, S14 |
| Кооперативный кампанийный | несколько видов, адаптивный pacing | несколько камер, AI director, physics | S11, S15 |
| Аудио-насыщенный | много источников, occlusion, DSP | ray/query count, DSP time, output latency | S17, S29 |

Стоимость кадра складывается из CPU main-thread, CPU parallel, GPU raster, GPU RT
и состава RAM/VRAM. Профиль нагрузки задаёт, какие оси доминируют и какие метрики
обязательны к измерению до того, как система выдаст сценарную оценку.

## 15. Оборудование

### 15.1 Покрытие и основание

| Тип | basis | Записей |
| --- | --- | --- |
| CPU | measured | 49 |
| CPU | derived | 2 |
| GPU | measured | 62 |
| GPU | derived | 17 |

| Тип | Класс | Записей |
| --- | --- | --- |
| CPU | 1 | 2 |
| CPU | 2 | 9 |
| CPU | 3 | 23 |
| CPU | 4 | 11 |
| CPU | 5 | 6 |
| GPU | 1 | 18 |
| GPU | 2 | 21 |
| GPU | 3 | 22 |
| GPU | 4 | 13 |
| GPU | 5 | 5 |

Всего: 51 CPU / 79 GPU. Индекс CPU/GPU — нормализованный anchor, а не FPS. В карточке
оборудования хранятся benchmark name, raw value, context, normalization note,
evidence basis и source link. Если каталог не содержит устройства, одновременно
покрывающего условия, результат сообщает `exceeds_catalog` и не подставляет
похожую карту молча.

### 15.2 CPU (верхняя часть по single-thread)

| Модель | Single-thread | Multi-thread | Класс | Benchmark | Basis |
| --- | --- | --- | --- | --- | --- |
| Core i9-14900K | 1.00 | 0.94 | 5 | PassMark CPU Mark (multi-thread) | measured |
| Core i9-13900K | 0.98 | 0.93 | 5 | PassMark CPU Mark (multi-thread) | measured |
| Core i7-14700K | 0.95 | 0.84 | 5 | PassMark CPU Mark (multi-thread) | measured |
| Ryzen 7 9800X3D | 0.94 | 0.64 | 5 | PassMark CPU Mark (multi-thread) | measured |
| Core i7-13700K | 0.92 | 0.73 | 4 | PassMark CPU Mark (multi-thread) | measured |
| Ryzen 9 7950X | 0.91 | 1.00 | 5 | PassMark CPU Mark (multi-thread) | measured |
| Core i5-14600K | 0.91 | 0.62 | 4 | PassMark CPU Mark (multi-thread) | derived |
| Ryzen 9 7900X | 0.90 | 0.82 | 5 | PassMark CPU Mark (multi-thread) | measured |
| Ryzen 7 7700X | 0.89 | 0.57 | 4 | PassMark CPU Mark (multi-thread) | measured |
| Core i5-13600K | 0.88 | 0.60 | 4 | PassMark CPU Mark (multi-thread) | derived |
| Core i9-12900K | 0.88 | 0.66 | 4 | PassMark CPU Mark (multi-thread) | measured |
| Ryzen 5 7600X | 0.88 | 0.46 | 4 | PassMark CPU Mark (multi-thread) | measured |

### 15.3 GPU (верхняя часть по raster)

| Модель | Raster | RT | VRAM, GB | Класс | Benchmark |
| --- | --- | --- | --- | --- | --- |
| GeForce RTX 4090 | 1.00 | 1.00 | 24 | 5 | PassMark G3D Mark (raster) |
| GeForce RTX 5090 | 1.00 | 1.00 | 32 | 5 | PassMark G3D Mark (raster) |
| GeForce RTX 5080 | 0.94 | 0.94 | 16 | 5 | PassMark G3D Mark (raster) |
| GeForce RTX 4080 | 0.87 | 0.91 | 16 | 5 | PassMark G3D Mark (raster) |
| Radeon RX 7900 XTX | 0.86 | 0.83 | 24 | 5 | PassMark G3D Mark (raster) |
| GeForce RTX 5070 Ti | 0.85 | 0.85 | 16 | 4 | PassMark G3D Mark (raster) |
| Radeon RX 7900 XT | 0.78 | 0.77 | 20 | 4 | PassMark G3D Mark (raster) |
| GeForce RTX 5070 | 0.75 | 0.75 | 12 | 4 | PassMark G3D Mark (raster) |
| Radeon RX 9070 XT | 0.71 | 0.71 | 16 | 4 | PassMark G3D Mark (raster) |
| GeForce RTX 3090 | 0.70 | 0.70 | 24 | 4 | PassMark G3D Mark (raster) |
| Radeon RX 6900 XT | 0.70 | 0.70 | 16 | 4 | PassMark G3D Mark (raster) |
| GeForce RTX 3080 | 0.68 | 0.66 | 10 | 4 | PassMark G3D Mark (raster) |

## 16. Реальные игровые кейсы

| Кейс | Студия | Технология / год | Сценарий | Подтверждаемый факт / механизм | Ограничение переноса |
| --- | --- | --- | --- | --- | --- |
| Age of Empires | Ensemble Studios | Genie Engine / 1997 |  ·  | A completely different anti-cheat model with no client trust problem at all: because every peer must run an identical simulation, any divergence is tagged 'out of sync' and the game stops, which Bettner says made hacking a client or its communication stream ex | This only works because lockstep has no server authority and no hidden information by design. You cannot add out-of-sync detection to a client-server shooter - and 'stop the match' is a very different product response to cheating than 'ban  |
| Age of Empires (and Age of Empires II) | Ensemble Studios | Genie Engine / 1997 |  ·  | Shipped a peer-to-peer synchronous (lockstep) simulation on a 28.8 kbps modem with 8 players: 200 ms turns, commands scheduled two turns ahead, 2-byte speed control, out-of-sync detection as anti-cheat, and deterministic recordings used as bug repros. | The 200 ms turn, the 250-unit wall and the 250-500 ms latency tolerance were all derived from 28.8 kbps modems, 15 fps and 1997 CPUs. None of them is a modern constant - but the relationship (bandwidth per unit vs bandwidth per command) and |
| Alan Wake 2 | Remedy Entertainment | Northlight / 2023 | open_world · single | Remedy states AW2's GPU-driven mesh-shader pipeline does occlusion culling down to single-pixel precision and uses everything in a scene as an occluder. | Do not copy the single-pixel occlusion claim to hardware without mesh shaders and a GPU-driven pipeline. |
| Alan Wake 2 | Remedy Entertainment | Northlight / 2023 | open_world · single | Remedy's own write-up states the shipped game uses mesh shaders and culls meshlets, showing individual meshlets around Cauldron Lake fed into the renderer. | Do not copy the meshlet sizing or culling scheme without Remedy's mesh-shader-capable minimum hardware. |
| Alan Wake 2 | Remedy Entertainment | Northlight / 2023 |  ·  | Ships 'Path Traced Indirect Lighting' alongside DLSS Frame Generation and DLSS Ray Reconstruction on PC, i.e. RT GI layered on top of a raster pipeline rather than replacing it. | Remedy paired PT indirect lighting with a specific upscaler/denoiser stack and specific content. No frame-time figures were published, so no performance number can be transferred. |
| Ashes of the Singularity | Oxide Games / Stardock | Nitrous / 2016 |  ·  | AMD's GPU trace of the benchmark scene shows it 'makes heavy use of the compute queue': 'The asynchronous compute queue is used for most of the frame. It can be seen from the trace that the graphics queue is not stalled while waiting on the compute queue.' | AMD's trace shows queue behaviour only - no frame-time or FPS number is published, and nothing about this title's async strategy transfers to another engine. |
| Assassin's Creed IV: Black Flag | Ubisoft | AnvilNext / 2013 |  ·  | Bart Wronski's SIGGRAPH 2014 presentation ships the froxel volumetric fog solution in AC4 and reports: 'Total cost was surprisingly small, around 1.1ms. Calculating it in double resolution had a cost of 1.6ms. Most costly part was building density and lighting | Measured on PS3/PS4-era hardware and AC4 content; the ms values must not be transferred, only the ratio between resolution and cost. |
| Assassin's Creed Unity | Ubisoft | AnvilNext (Ubisoft in-house) / 2014 | open_world · single | Ships a crowd system with AI level-of-detail and pooling that swaps low-res NPCs to high-res ones; with a cap of 40 real AIs and 120 high-res models the team reports a scene with 10,000 crowd NPCs on screen simultaneously. | 10,000 on-screen NPCs with 40 real AIs is that game's crowd budget for a Paris street scene on PS4/Xbox One. It is not a performance number and does not transfer: the acceptable ratio of 'real' to 'fake' NPCs depends entirely on how closely |
| Assassin's Creed Unity | Ubisoft Montreal | AnvilNext / 2014 | open_world · single | The GDC 2015 session describes an AI level-of-detail recycling/pooling system that let the shipped game put 10,000 crowd NPCs on screen using 40 real AIs and 120 high-resolution models. | Do not copy the 40-real-AI / 120-high-res-model split: it is specific to Unity's crowd scale and hardware targets. |
| Baldur's Gate 3 | Larian Studios | Divinity 4.0 (in-house) / 2023 |  ·  | Listed by the meshoptimizer maintainer among commercial games that use the library. The listing documents use of the library; it does not say which optimisations are enabled, at what settings, or what was measured. | A usage credit, not a measurement. No ACMR, bytes-per-triangle, decode throughput or frame-time figure is published for this title, and a credit tells you nothing about which parts of the library were used or how much they bought. |
| Battlefield V | DICE (EA) | Frostbite / 2018 | open_world · dedicated_server | DICE's GDC session is documented as covering the nitty-gritty details of the studio's ray-traced reflection implementation, and the NVIDIA GTC 2019 deck states Battlefield V was the first DXR game released. | Reflections only, at 1080p with a limited effect list, on first-generation RT hardware; that scope does not transfer to a full ray-traced lighting pipeline. |
| Battlefield V | DICE (EA) | Frostbite / 2018 | open_world · dedicated_server | DICE's GDC session is documented as a technical presentation on ray-traced reflections in a large multiplayer shooter, establishing only the dedicated-server context. | No anti-cheat fact is evidenced by this source; it is listed only to make the gap explicit. |
| BeamNG.drive | BeamNG | In-house (Torque 3D-derived) / 2015 |  ·  | BeamNG documents a soft-body, node-and-beam vehicle simulation in which the vehicle structure itself deforms, with named beam parameter pairs for suspension, structural members and steering - the high-fidelity pole of vehicle simulation rather than a raycast m | This is the opposite approach to a raycast vehicle, and it is a studio marketing/documentation page rather than a technical paper. The soft-body approach is affordable because the whole product is about vehicle simulation; it does not trans |
| Black Myth: Wukong | Game Science | Unreal Engine 5 / 2024 | linear · single | Digital Foundry reports 'a very distinct shadow cascade line' near the main character when Virtual Shadow Maps are excised without Full RT, with distant shadows blobbing out. | Do not copy the VSM-excised fallback configuration: it produces visible cascade seams that reviewers flagged. |
| Black Myth: Wukong | Game Science | Unreal Engine 5 / 2024 | linear · single | Digital Foundry reports the game forgoes Virtual Shadow Maps unless Full RT is enabled because VSMs are expensive on non-Nanite foliage, producing more shadow issues than other UE5 titles. | Do not copy the decision to disable VSMs in a foliage-heavy game unless you accept the shadow artifacts it caused here. |
| Black Myth: Wukong | Game Science | Unreal Engine 5 / 2024 | linear · single | Digital Foundry reports that without Full RT the shipped game uses software Lumen on PC for diffuse GI and specular reflections, i.e. distance-field-based tracing. | Do not copy software Lumen as equivalent to hardware RT here; the review notes reflections differ most. |
| CMU motion capture database (academic corpus, not a shipped game) | Carnegie Mellon University | n/a / 2003 |  ·  | Open benchmark for the same codec: 2534 clips at 24 FPS, 9h 49m 37.58s, 1429.38 MB raw -> 65.66 MB (21.77:1), max error 0.0495 cm, 99.96% of samples below threshold. | Academic mocap at 24 FPS with no game-specific authoring (no root-motion cleanup, no exotic clips). Its max error is 80x lower than Paragon's, which is a statement about the content, not about the codec. |
| Call of Duty (SIGGRAPH 2020 talk, cited by The Coalition) | Infinity Ward / Activision | Call of Duty engine / 2020 | linear · dedicated_server | The Coalition's write-up points to 'Software-Based Variable Rate Shading in Call of Duty' (SIGGRAPH 2020) which emulates VRS via MSAA on platforms without hardware VRS and uses ExecuteDispatchIndirect for compute passes. | Do not copy software VRS emulation unless you can afford the de-blocking pass; it is a workaround for hardware without VRS support. |
| Chunked LOD reference implementation (Puget Sound demo) | Thatcher Ulrich (independent) | Public-domain reference implementation / 2002 |  ·  | Flew a 16K x 16K USGS Puget Sound dataset (512 MB raw) from a preprocessed 214 MB chunk file at 4 m error tolerance, and generated a 32K x 32K quadtree-tiled texture (9 levels of 128x128 JPEG nodes, ~61 MB) to surface it, at ~30 fps on a 1 GHz Pentium 3 with a | 2002 hardware and a public-domain research implementation. The 512 MB -> 214 MB ratio applies to that dataset at that tolerance on that codec; it is not a general compression ratio. The ~30 fps figure is a 1 GHz P3/GeForce2Go number and mus |
| Counter-Strike 2 | Valve | Source 2 / 2023 | соревновательные арены · authoritative multiplayer | Sub-tick architecture records the instant of relevant input events independently of the old tick-only framing. | Официальное описание не задаёт переносимый бюджет трафика или задержки для другой игры. |
| Counter-Strike 2 | Valve Corporation | Source 2 / 2023 |  ·  | A competitive title receiving frequent, small client updates where download size directly affects how quickly the player base can join a match. | No patch-size or delta-ratio figures are published, so this does not quantify patch efficiency. |
| Counter-Strike 2 | Valve Corporation | Source 2 / 2023 |  ·  | The only shipped game I could find with a sub-tick architecture: Valve claims tick rate no longer matters for moving, shooting or throwing, and that grenades will always land the same way - while the VDC wiki records the server as hard-coded 64 tick with sub-t | Everything. Valve published the intent and nothing else: no wire format, no measurement, no error budget. You cannot copy this - you can only re-derive it and measure it yourself. Also note that a 64+sub-tick server is not automatically che |
| Cuphead | StudioMDHR | Unity / 2017 |  ·  | A fully hand-drawn style executed as an asset pipeline problem: '50,000 frames of amazing hand-drawn animation', drawn and inked on paper and coloured in Photoshop, authored at '24 frames-per-second' while 'the game runs at a sparkling 60 frames-per-second'. U | The 24fps-animation/60fps-game split is an authored art decision, not a performance result. 50,000 frames is a statement about StudioMDHR's art budget across the whole game - it does not scale down to a smaller team, and it says nothing abo |
| Cuphead | StudioMDHR | Unity / 2017 |  ·  | The deliberate opposite choice, included because it defines the boundary of this method: '50,000 frames of amazing hand-drawn animation', authored at '24 frames-per-second' while the game runs at 60. This is the art direction that skeletal 2D deformation canno | A counter-example, not a comparable implementation. The frame count is a studio art-budget fact, not a performance result, and it tells you nothing about the CPU cost of a skeletal 2D system. |
| Cuphead | StudioMDHR | Unity / 2017 |  ·  | The extreme end of the atlas problem: '50,000 frames of amazing hand-drawn animation', with Unity's 'Sprite Renderer, Sprite Packer, 2D Physics, and particle effects' named as the tools that 'help[ed] StudioMDHR process the massive amount of their exquisite ar | 50,000 frames is StudioMDHR's art budget for one game, not a performance figure. Their animation runs at 24fps while the game runs at 60fps, so frame reuse rather than per-frame draw cost is the interesting property here. Nothing about thei |
| Cyberpunk 2077 | CD Projekt Red | REDengine 4 / 2020 | open_world · single | A shipped open-city title with a very large and heterogeneous material set, and a later path-traced mode that stresses shader variety across the whole scene. | REDengine 4 is a bespoke engine; its material system and permutation strategy are not transferable, and this source does not state that bindless binding is used. |
| Cyberpunk 2077 | CD Projekt Red | REDengine 4 / 2020 | open_world · single | A shipped title with a very large install footprint, representing the high end of the same range. | Install size here reflects a specific content scope and audio localisation set; it is an anchor point, not a target. |
| Cyberpunk 2077 | CD PROJEKT RED | REDengine 4 / 2023 | open_world · single | NVIDIA documents the Ray Tracing: Overdrive technology preview for Cyberpunk 2077 as shipping with DLSS 3, letting GeForce RTX 40-series players run the mode at 4K. | The combination of full path tracing with DLSS 3 frame generation is a PC-only showcase; the resulting latency and quality trade-offs do not transfer to console targets. |
| DOOM Eternal | id Software | id Tech 7 / 2020 | сегментированные боевые уровни · single-player with online modes | Доклад SIGGRAPH 2020 описывает geometry caches, gore, decals, material compositing и workflow вокруг целевого frame rate. | Собственный движок, ассеты и платформенный порт делают детали непереносимыми без повторного измерения. |
| DOOM Eternal | id Software | id Tech 7 / 2020 | arena · single | The shipped game bins lights and decals with a hybrid cluster+tile scheme because artists wanted more dynamic lights and decals while the binning budget stayed under 500us. | Do not copy the <500us binning budget without id Tech 7's compute-raster pipeline and bindless resource model. |
| DOOM Eternal | id Software | id Tech 7 / 2020 | arena · single | Doom Eternal's GPU triangle culling is budgeted for 3M visible triangles with only ~1M reaching the rasterizer, removing ~70% of submitted triangles. | Do not treat id Tech 7's triangle-culling budget as a meshlet budget: Doom Eternal is not a meshlet renderer. |
| Dawn (NVIDIA real-time tech demo) | NVIDIA | custom Cg/HLSL renderer / 2003 |  ·  | The canonical published GPU-skinning implementation: a skeleton of 98 bones driving a mesh of more than 180,000 triangles with four bone matrices per vertex, bone palette in vertex-shader constants. | A single hero character on 2004 hardware, no crowd, no multi-pass reuse, no cache budget. It demonstrates the algorithm, not the economics of a modern 100-character scene. |
| Diplomacy is Not an Option | Door 407 | Unity (ECS for Unity / DOTS) / 2022 |  ·  | Unity documents that the studio uses DOTS 'almost everywhere' in this real-time strategy game and finds it 'especially useful for pathfinding and optimizing our gameplay logic' - the data-oriented foundation that makes large-unit-count 2D/RTS crowd rendering t | This is a vendor marketing page quoting the developer. It confirms DOTS usage for gameplay/pathfinding, not specifically 2D crowd instancing, and gives no unit counts or frametime numbers. |
| Doom Eternal | id Software | id Tech 7 / 2020 |  ·  | The SIGGRAPH 2020 presentation states the game holds 60 FPS on consoles, and its results section reports up to 5 ms of GPU savings in dense scenes from triangle culling and merging - evidence of an explicit, measured frame budget culture rather than a physics- | The 5 ms figure is for triangle culling/merging, not for physics timestep, and the 60 FPS target is that game's own target on its own hardware. Neither number transfers to another project; the transferable observation is that a shipped AAA  |
| F.E.A.R. | Monolith Productions | F.E.A.R. engine (LithTech Jupiter EX) / 2005 | linear · single | The shipped game's AI uses a 3-state FSM plus A* planning over data-driven actions/SmartObjects, so behaviour is composed from database entries rather than a large hand-written FSM. | Do not copy F.E.A.R.'s 3-state FSM as an ability system: it is a goal-oriented action planner, not a cooldown/effect ability framework. |
| F.E.A.R. | Monolith Productions | LithTech Jupiter EX / 2005 | linear · single | The GDC 2006 paper states A* is used to find paths through the navigational mesh as well as to plan action sequences, and that when an AI crawls under an obstacle it first searches for a navigational path and then for a plan to overcome the obstacle. | F.E.A.R.'s navmesh and cover-node density are tuned for small indoor combat spaces; the same node budget does not transfer to a large open world. |
| For Honor | Ubisoft Montreal | Ubisoft in-house (AnvilNext-derived pipeline; animation system custom) / 2017 |  ·  | Motion matching was presented by Ubisoft Montreal's Simon Clavet at GDC 2016 as the studio's next-gen animation approach. The published pipeline is: 'Mocap is tweaked, imported, and marked up'; 'At runtime Gameplay makes a request (desired trajectory and event | The talk publishes no database size, no search time, and no CPU budget - the optimisation slide explicitly defers to 'a future talk'. Also, this is a melee-combat game where weapon position and stance matching matter; a shooter or a third-p |
| Forspoken | Luminous Productions | Luminous Engine (in-house) / 2023 |  ·  | In the DirectX blog post announcing DirectStorage availability on PC, Microsoft points readers to 'the GDC talk presented by Luminous Productions about their integration of DirectStorage in Forspoken' - the only shipped title named in the material I verified. | I verified only that Microsoft points to the talk; I did not access the talk itself, so no load time, throughput or CPU figure is asserted. Any number from Forspoken's integration would be its own hardware, its own asset layout and its own  |
| Fortnite | Epic Games | Unreal Engine 4/5 / 2017 |  ·  | Epic's own documentation uses Fortnite's modular characters as the motivating case: characters are 'comprised of several Skeletal Meshes (heads, bodies, backpacks, etc.) all of which can be ticking at a given time', and the budgeter shows per-mesh rate numbers | Modular characters multiply component count per character, which is why budgeting mattered there. A monolithic-mesh character project has a much smaller per-character component count and may not need the allocator at the same crowd size. Ep |
| Fortnite Battle Royale | Epic Games | Unreal Engine 4 / 2017 | open_world · dedicated_server | Epic built and shipped the Replication Graph plugin specifically because Fortnite starts each match with 100 players and about 50,000 replicated actors, and documents the tree/dormancy/always-relevant node split using Fortnite as the worked example. | The 100-player / 50,000-actor figures describe Fortnite's content density and actor granularity. A game with 100 players but 2,000 replicated actors has a different problem and may not need a replication graph at all; a game with 5,000 acto |
| GPU geometry clipmap reference implementation (NVIDIA / Microsoft Research) | NVIDIA / Microsoft Research (Arul Asirvatham, Hugues Hoppe) | Direct3D 9 sample / 2005 |  ·  | Rendered a ~20.2-billion-sample US terrain dataset compressed >100x into 355 MB at 130 fps (60M triangles/sec) at 1024x768 on a GeForce 6800 GT - the canonical measured demonstration of the method. | 2005 hardware (Pentium 4 2.4 GHz, 1 GB RAM, GeForce 6800 GT) at 1024x768. Neither the fps nor the ms update figures are usable as a modern budget. The transferable content is the structural result: ~71 draw calls for 11 levels, ~5-pixel tri |
| Gears 5 / Gears Tactics | The Coalition | Unreal Engine 4 / 2020 | linear · coop | The Coalition states the games use Dynamic Resolution Scaling to hit a smooth 60 FPS, rendering the next frame at lower resolution when near budget. | Do not copy the DRS thresholds or the 10% figure to a different engine/hardware target. |
| Gears 5 / Gears Tactics | The Coalition | Unreal Engine 4 / 2020 | linear · coop | VRS texture generation runs on the Async Compute Queue, overlapping the next frame's depth pass; the studio had already moved the post-process chain to overlap the next frame's depth pass. | Do not copy the overlap window: it depends on where VRS texture generation sits in the post chain (tonemapping here). |
| Gears 5 / Gears Tactics (Hivebusters) | The Coalition | Unreal Engine 4 / 2020 | linear · coop | The Coalition's own VRS write-up states the Xbox Series X\\|S launch of Gears 5/Tactics and the Hivebusters DLC 'added new rendering features including contact shadows and screen space global illumination'. | Do not copy the pass list blindly: Gears applied VRS to contact-shadow-bearing passes under a specific budget that depends on its own target framerate. |
| General shipped practice (Game Programming Patterns) | Robert Nystrom (pattern catalogue) | engine-agnostic / 2014 |  ·  | The Object Pool pattern is documented as a standard optimisation pattern for games, motivated by memory fragmentation and allocation cost on consoles and in languages with garbage collection. | This is a design-pattern reference, not evidence of a specific shipped game's results. It establishes that the technique is standard practice; it provides no measurement and no shipped-title confirmation. |
| Godot 4 (engine feature) | Godot Engine contributors | Godot 4.x / 2024 |  ·  | Godot offers a double-precision build for physics/rendering and documents origin shifting as the alternative path for platforms where doubles are too expensive - an independent engine making the same trade-off Epic documents. | Cross-engine confirmation of the design space only. Godot's double build, its performance cost, and its origin-shifting helper are not transferable to Unreal or to a custom engine; do not copy any constant. |
| Godot-based shipped titles (engine capability) | Godot contributors (engine) | Godot 4.x / 2023 |  ·  | Godot exposes 32 physics layers with per-object layer and mask bitmasks as the standard, documented mechanism for filtering both collision simulation and queries. | Engine capability, not a shipped-game result. No pair counts, timings, or layer taxonomy transfers to another project or engine. |
| Godot-based titles using VehicleBody3D | Godot contributors (engine) | Godot 4.x / 2023 |  ·  | Godot ships a raycast vehicle system as a built-in node and documents plainly that it is not designed for realistic vehicle physics, directing advanced users to write their own integration. | Engine capability with a published scope limit, not a shipped-game result. No handling metrics or cost figures transfer; the transferable content is the scope limit itself. |
| Godot-based titles using the documented save pattern | Godot contributors (engine documentation) | Godot 4.x / 2023 |  ·  | Godot documents a complete snapshot save/load pattern (FileAccess to a named user:// path, JSON or binary serialisation, staged loading of nested objects) as the engine's reference approach. | Engine tutorial, not a shipped-game result. No save sizes or load times transfer, and the tutorial's simplified model (no nested Persist children) is explicitly called out as a limitation that real projects must solve. |
| Hi-Fi RUSH | Tango Gameworks | Customized Unreal Engine 4 / 2023 |  ·  | A shipped stylized 3D game held to 60fps at native resolution, built on a deferred toon renderer composed from customized UE4 passes plus added passes, combined in deferred post-process volumes; the session covers comic shaders, toon lights, dynamic and static | The 60fps-at-native-resolution result is a property of this game's scene complexity, content density and target hardware. It does not predict the cost of a deferred toon renderer in a different scene or on different hardware, and no per-pas |
| Hitman: Absolution | IO Interactive | Glacier 2 / 2012 |  ·  | IO Interactive's GDC talk describes the techniques and optimisations used to achieve 1200-character crowds in a real production level while running at 30 fps on current-gen consoles, with every character individually interactable and influenceable. | '1200 characters at 30fps on current-gen consoles' is a 2012 PS3/Xbox 360 target for that game's specific crowd density and camera. Neither the agent count nor the frame rate transfers to other hardware or to a different crowd/interaction d |
| Horizon Zero Dawn | Guerrilla Games | Decima / 2017 | open_world · single | Guerrilla's own talk description states the shipped game uses low-level and high-level streaming systems with dedicated memory management and scheduling. | Do not copy Decima's streaming tiers without its asset conversion pipeline and memory allocators, which the talk presents as a coupled system. |
| Horizon Zero Dawn | Guerrilla Games | Decima / 2017 | open_world · single | A large open world with dense vegetation and long view distances, requiring distant objects to be merged and simplified to stay within the draw budget. | Decima's streaming and LOD pipeline is bespoke; the具体实现 is not documented in enough detail to copy. |
| Hunt: Showdown | Crytek | CryEngine / 2019 | большие PvPvE-карты · competitive multiplayer | Команда Hunt описывает occlusion rays, material-dependent filtering, HRTF/CrySpatial и аудио как источник игровой читаемости. | Число emitters, лучей и стоимость CPU/аудио-потока зависят от карты и middleware. |
| Hunt: Showdown | Crytek | CryEngine (not stated in the cited post) / 2019 |  ·  | Crytek published a dedicated developer-insight post on Hunt's audio ('Did you hear that?') covering how players should read audio cues - evidence that propagation/occlusion is treated as a core competitive mechanic rather than polish. | The post publishes NO ray counts, CPU cost or memory budget, so nothing about Hunt's implementation can be copied or used as a performance target. Only the product stance (audio is a competitive information channel) transfers. |
| Hunt: Showdown | Crytek | CryEngine (not stated in the cited post) / 2019 |  ·  | Crytek treats audio - including how spaces colour sound - as a competitive information channel, publishing a dedicated developer post on reading audio cues. | The post is about players reading cues, not about implementation. It publishes no reverb configuration, IR data or budget, and must not be cited as evidence for any technical choice. |
| IXION | Kasedo Games | Unity (ECS for Unity / DOTS) / 2022 |  ·  | Unity documents that Kasedo Games used ECS for Unity 'to power heavy NPC simulation' for IXION, a city-builder/survival/space-exploration title - the closest documented match to a crowd-scale ECS workload in this pack. | Vendor page, no numbers. 'Heavy NPC simulation' is not quantified, so no agent count or frametime transfers. |
| It Takes Two | Hazelight | Unreal Engine 4 / 2021 | линейные кооперативные сцены · local/online co-op | Технический анализ Digital Foundry рассматривает split-screen и две точки зрения как часть рендер-пайплайна. | Результат зависит от сцены, разрешения, качества и конкретной реализации; FPS не переносится. |
| It Takes Two | Hazelight Studios | Unreal Engine 4 / 2021 | linear · coop | The Hazelight interview and the EA press release both identify It Takes Two as the studio's previous co-op title (23 million units sold, 2021 Game of the Year) whose workflow and tooling the team built on for Split Fiction. Neither source states the word split | This is co-op lineage evidence, not a verified split-screen implementation statement for It Takes Two; it must not be cited as proof that It Takes Two renders two viewports, and no cost may be inferred. |
| Just Cause 4 | Avalanche Studios | Avalanche engine / 2018 | open_world · single | A large open world with many vehicles, aircraft and physics props, where only nearby vehicles can be fully simulated. | The talk covers full-detail vehicle physics, not the LOD policy; the degradation strategy is not documented. |
| Just Cause 4 | Avalanche Studios | Avalanche engine / 2018 | open_world · single | Avalanche's GDC talk is documented as covering how Just Cause 4 copes with a wide range of vehicles and player styles through the design of its tire dynamics, and how those relate to the overall vehicle gameplay experience. | The talk is about vehicle handling models, not general rigidbody simulation; its tire model does not transfer to non-vehicle physics. |
| Justice (Ni Shui Han) | NetEase | Unreal Engine (TressFX patch) /  | open_world · dedicated_server | AMD's TressFX page credits NetEase's Justice (Ni Shui Han) with a screenshot and states TressFX is a GPU-based hair/fur rendering and simulation library with an LOD system and an Unreal Engine patch. The source does not state the game's release year, so it is  | The source proves GPU strand hair, not cloth; it is included only as evidence that GPU-simulated strands ship in a game, and no cloth figure may be inferred. |
| Justice (Ni Shui Han) | NetEase | Unreal Engine (TressFX patch) / 2019 | open_world · dedicated_server | AMD's TressFX page shows a screenshot credited to NetEase's Chinese martial-arts game Justice (Ni Shui Han) as a shipped use of the GPU strand hair library. | Strand hair at this fidelity is GPU-budget-heavy and was shipped with vendor library support; the strand counts are not published and must not be assumed. |
| Left 4 Dead | Valve | Source / 2008 | линейные кооперативные кампании · 4-player co-op | AI Director модулирует драматический темп по оценке интенсивности команды. | Не переносит количество заражённых, FPS или сложность кампании в другой проект. |
| Left 4 Dead | Valve | Source / 2008 | linear · coop | Ships the AI Director: an adaptive dramatic pacing controller with Build Up / Sustain Peak / Peak Fade / Relax phases, plus procedural population driven by navmesh flow distance, the Active Area Set and potentially-visible sets. | The 3-5 s / 30-45 s phase timings, the 20-30 mob size, the 90-180 s interval and the 75%-from-behind rule are L4D's tuned constants for a 4-player co-op survival-horror loop. They are not portable budgets; a different team size, TTK or map  |
| Left 4 Dead | Valve | Source / 2008 | linear · coop | Uses the contrasted approach - A* through a navigation mesh plus reactive path following toward a look-ahead point with local obstacle avoidance - and documents that this yields a path 'reasonably close to optimized' while making (re)pathing cheap. | This is the alternative, not the method. It shows the trade-off space (per-agent A* + local avoidance instead of shared flow fields) in a 4-player co-op game with tens of agents, not thousands. No cost figure transfers. |
| Lords of the Fallen | Hexworks | Unreal Engine 5 / 2023 | linear · coop | Digital Foundry notes Virtual Shadow Maps add a lot to the visuals of Lords of the Fallen and questions why VSM cannot be toggled in the game's menu. | Do not copy the shipped configuration that omits a user-facing VSM toggle; that is a menu-policy choice, not a technical requirement. |
| Lords of the Fallen | Hexworks | Unreal Engine 5 / 2023 | linear · coop | Digital Foundry measures the shipped PS5/Series X build at a dynamic 1152p with a 648p lower bound in performance mode. | Do not copy the 1152p/648p bounds; they are specific to this title's quality mode and hardware. |
| Lords of the Fallen | Hexworks | Unreal Engine 5 / 2023 | linear · coop | Digital Foundry observes that at 30fps the shipped game's volumetric lighting runs at a higher resolution, reducing stair-stepping across streaks of light (the game's visible light-shaft-like effect). | Do not treat volumetric lighting as equivalent to a screen-space post-process light-shaft pass; the review describes volumetrics, not a radial-blur god-ray pass. |
| Lumen in the Land of Nanite (Epic demo) | Epic Games | Unreal Engine 5 (early access) / 2021 |  ·  | The demo's geometry (~882M Nanite triangles, 4.61 GB compressed on disk with Kraken level 5) is streamed through a fixed-page, GPU-request-driven pipeline whose root page is always resident and whose GPU transcode runs at ~50 GB/s on PS5 - i.e. the whole scene | 4.61 GB on disk and 5.6 bytes per Nanite triangle are measurements of one Epic demo scene compressed with a specific codec at a specific level. They are not a general 'bytes per triangle' constant. The 50 GB/s transcode is a PS5 figure. Do  |
| Lumen in the Land of Nanite (Epic technology demo) | Epic Games | Unreal Engine 5 (early access) / 2021 |  ·  | The demo that produced the published Nanite numbers: 433M source triangles -> 882M Nanite triangles, 25.90 GB raw -> 7.67 GB memory format -> 4.61 GB compressed disk, i.e. 5.6 bytes per Nanite triangle with Kraken level 5, rendered with no manual LOD authoring | One demo scene, one codec, one compression level. '5.6 bytes per Nanite triangle' is NOT a universal constant - it depends on topology regularity, attribute count and the LZ backend. Do not size a project's disk budget from it without measu |
| Lyra (Epic sample game) | Epic Games | Unreal Engine 5 / 2022 |  ·  | Epic points at Lyra as the worked example for migrating an existing animation system to the thread-safe/Fast Path model: 'For a workflow example of optimizing an Unreal Engine project to use Thread Safe functions, see the Adapting Lyra Animation to your UE5 Ga | Lyra is a small-scale sample; it demonstrates the migration technique, not the crowd budget that makes it necessary. |
| Lyra (starter game sample) | Epic Games | Unreal Engine 5 / 2022 |  ·  | Lyra is the shipped reference for Systems as a Service: 'Lyra impacts are managed by the B_WeaponImpacts class ... Having a separate object owning impacts solved an issue where impacts would despawn when switching weapons. B_WeaponImpacts has a default system  | No measurement is published: there is no impact-per-second figure, no live-instance count and no frame-time cost for Lyra's impacts. The sample proves the pattern and names the owning class and the surface-template-per-type design; it does  |
| Lyra Starter Game (Unreal sample) | Epic Games | Unreal Engine 5 / 2022 |  ·  | Epic ships a full worked example of building, cooking and testing a dedicated server plus two clients, including the separate Server/Client Target.cs files and separate cook targets - the reference implementation for the build-side work. | Lyra is a small-scale shooter sample. It demonstrates the build mechanics, not the density economics - a working Lyra server says nothing about whether your game is affordable at scale. |
| Metro Exodus | 4A Games | 4A Engine (DXR) / 2019 | linear · single | Metro Exodus sorts ray-tracing instances by accumulated per-frame priority and throttles BLAS updates, keeping the queue in a 'balanced' state of about 5k-6k outdated instances out of 20k+. | Do not copy the instance-priority throttling numbers: they budget ray-tracing BLAS work, not dynamic punctual lights. |
| Metro Exodus | 4A Games | 4A Engine (DXR) / 2019 | linear · single | The shipped game had a 'super-lazy-realtime grid of probes for GI' and voxel GI before RTGI, and its RTGI path stores per-pixel irradiance as L1 spherical harmonics. | Do not copy the 96-bit/pixel SH irradiance encoding without Metro's two-pass denoiser and its HDR range assumptions. |
| Metro Exodus | 4A Games | 4A Engine (DXR) / 2019 | linear · single | BLAS/TLAS management runs as async compute hidden behind the pre-trace and SSR compute shaders, with both a compute-queue and a parallel-to-GBuffer mode implemented. | Do not copy the 'statistically insignificant difference' between Metro's two async modes without re-measuring on your hardware. |
| Minecraft | Mojang Studios | Java Edition (in-house) / 2011 |  ·  | The world is persisted per region/chunk rather than as one monolithic save file, so saving an arbitrarily large world only rewrites the regions that actually changed. | Minecraft's chunk format is a bespoke, simple record layout. It does not model Unity/Unreal serialized objects, and its write amplification behaviour will not match a GameObject or UObject save graph. |
| No Man's Sky | Hello Games | No Man's Sky engine / 2016 | open_world · single | The GDC 2017 session abstract states the game transitions seamlessly from space to an interactive populated terrain and generates planets continuously in real time. | Do not copy a procedural-streaming architecture to a hand-authored world; NMS's approach is procedural by necessity. |
| No Man's Sky | Hello Games | Hello Games in-house / 2016 | open_world · single | Planetary-scale rendering where an entire planet must be representable from orbit down to surface detail, forcing many levels of distance-based reduction. | Procedural planets generate LODs differently from authored meshes; the HLOD tooling is not transferable. |
| No shipped title documented | n/a - research prototype plus NVIDIA RTXNTC SDK | NVIDIA RTXNTC SDK (beta) / 2023 |  ·  | There is no shipped game to cite. NTC is a SIGGRAPH 2023 research result with an NVIDIA SDK; the strongest published claim is the project page teaser - 16x the texels of BC high at 30% less memory - and no runtime decode cost is published in the material I cou | Nothing can be transferred from a non-existent shipped title. The paper's numbers are the authors' own measurements on their own material set, and the per-texel reduction above is my arithmetic on two summary figures, not a published rate.  |
| Overwatch | Blizzard Entertainment | Blizzard in-house / 2016 | arena · dedicated_server | Blizzard's GDC 2017 talk states Overwatch uses an Entity Component System architecture, and that the team 'leverages ECS to curtail complexity, even as they continue to add new crazy features'; the same talk covers how the networked simulation uses determinism | Confirms ECS shipped in a hero shooter, but Overwatch's entity count is small (dozens of actors) - the motivation there was complexity management and determinism for netcode, not crowd scale. That motivation does not transfer to a project w |
| Overwatch | Blizzard Entertainment | In-house (Overwatch engine) / 2016 | arena · dedicated_server | Blizzard presented the game's gameplay architecture and netcode at GDC 2017, documenting a component-based entity administration for a shipped game with dozens of heroes and heavily recombining ability behaviour. | This confirms the approach was used and was worth a GDC talk for a networked hero shooter. It does not transfer Overwatch's specific component taxonomy, replication model, or performance results - those are bound to that game's networking m |
| Paragon | Epic Games | Unreal Engine 4 / 2018 |  ·  | ACL's reference shipped-game corpus: 6558 clips / 7h 00m 45.27s / 4276.11 MB raw, compressed to 181.25 MB (23.59:1) at a max error of 3.9834 cm. The data is used for research under NDA and is not publicly available. | The ratio is a property of Paragon's clip mix (including very short clips, 2 FPS clips, world-space clips and heavy scale animation). A project with mostly short looping cycles will not reproduce 23.59:1, and the 3.98cm max error is concent |
| PhysX-integrated titles (engine middleware) | NVIDIA (middleware) | PhysX SDK (used by Unreal, Unity and many in-house engines) / 2018 |  ·  | PhysX exposes an explicitly selectable broadphase (sweep-and-prune, multibox pruning, parallel variants, and a GPU broadphase), so broadphase selection is a documented, tunable production decision in shipped engines. | Confirms the mechanism is exposed in shipping middleware, not that any particular game chose any particular type. No game-specific body counts or timings transfer. |
| Portal | Valve | Source engine / 2007 | linear · single | Valve's own commentary states the shipped game renders the through-portal view with a virtual camera, switched to recursive frame-buffer rendering for antialiasing and memory reasons, and supports up to nine recursive portal views. | Do not copy the nine-view recursion cap or the offscreen-texture decision; the commentary presents them as trade-offs specific to Portal's hardware era. |
| Portal 2 | Valve Corporation | Source engine / 2011 | linear · coop | A shipped puzzle game built entirely around recursive portal rendering, where each visible portal requires re-rendering part of the scene. | Source's portal rendering is integrated into the engine's vis/rendering pipeline; a render-target-based approach in a modern engine has a different cost profile. |
| Quake II RTX | NVIDIA Lightspeed Studios | Q2VKPT (Vulkan, VKRay) / 2019 |  ·  | A fully ray-traced remaster in which reflections are resolved globally rather than by re-rendering a mirrored view per surface. | Q2VKPT is a research-grade renderer requiring RTX hardware; it is not a substitute for a planar reflection path on mid-range GPUs. |
| Quake II RTX | NVIDIA Lightspeed Studios | Q2VKPT (Vulkan, VKRay) / 2019 |  ·  | 'Quake II RTX is a pure ray-traced game. That means all lighting, reflections, shadows and VFX are ray-traced, with no traditional effects or techniques utilized.' NVIDIA's newsroom calls it 'the world's first game that is fully path-traced'. | The content is a 1997-era game with very low geometric density; it proves viability, not affordability for a modern open-world asset budget. |
| Quake III Arena | id Software | id Tech 3 / 1999 |  ·  | The reference implementation of snapshot/delta state sync against a per-client acknowledged baseline is public: id's GPL release contains the server-side snapshot builder (sv_snapshot.c) that diffs entity state and writes a client snapshot. | The code is the right thing to read to understand the mechanism, but its field-level encoding, baseline retention policy and packet sizes were designed for 1999 modems. Do not copy the wire format; copy the bookkeeping model. |
| RAGE | id Software | id Tech 5 / 2011 |  ·  | id Software published the software virtual texture architecture it shipped - page table, physical page cache, GPU feedback/page-ID pass, anisotropic trilinear filtering with page borders, transcode on load and cache eviction - the productionisation of the mega | This is an architecture reference, not a performance result. No frame time, no VRAM figure and no texture resolution from RAGE is asserted here because I did not extract a verified number from the paper. Do not quote a 'megatexture size' fo |
| Rainbow Six Siege | Ubisoft Montreal | AnvilNext + RealBlast / 2015 |  ·  | AI visibility is explicitly coupled to destruction state ('AI visibility through partially broken walls'), and the destruction event system warns that listeners must be asynchronous. | Shows the integration requirement (perception must be invalidated by world change) in a destructible multiplayer shooter. It does not transfer a perception query budget, and the coupling to RealBlast is specific to that engine. |
| Rainbow Six Siege | Ubisoft Montreal | AnvilNext + RealBlast / 2015 |  ·  | Procedural destruction is integrated with AI navigation: the game updates navlinks for trapdoors, breachable walls and floors as the environment changes. | Confirms the requirement (nav must follow destruction), not a tiling or streaming implementation. R6 Siege is a small-map multiplayer game, so its navigation footprint is not comparable to an open world; no memory or bake-time figure transf |
| Ratchet & Clank: Rift Apart | Insomniac Games / Nixxes Software | Insomniac Engine / 2023 |  ·  | The Windows port of a title built around instantaneous world transitions, delivered on PC with an SSD-oriented streaming path. | The specific IO API used by the port is not documented in this source; this evidences the pattern, not the API call. |
| Rayman Legends | Ubisoft Montpellier | UbiArt Framework / 2013 |  ·  | A counter-example that is useful for scoping: UbiArt is a 2D engine whose GDC 2014 session focuses on 'the design team's approach' and on 'the engine's role in improving prototyping and level design pre-production processes', i.e. art and design iteration, not | The session overview confirms tooling and prototyping benefits only. It does NOT confirm any deformation, bake or streaming technique, and a 2D/vector art pipeline is not evidence about a PBR character pipeline - it is evidence that one cla |
| Rayman Legends | Ubisoft Montpellier | UbiArt Framework / 2013 |  ·  | Very high on-screen sprite counts including effect frames, requiring atlased sources. | Same limitation: bespoke 2D pipeline, no published batching figures. |
| Red Faction: Guerrilla | Volition | Geo-Mod 2.0 / Havok / 2009 | open_world · single | A former Volition physics lead states the shipped Geo-Mod 2.0 system fragments buildings into thousands of independent debris pieces at runtime, which precluded pre-baked lighting and forced navmesh rebuilds. | Do not copy fully dynamic destruction into a production that depends on baked lighting or precomputed navigation; this title had to give both up. |
| Red Faction: Guerrilla | Volition | Geo-Mod 2.0 / 2009 | open_world · dedicated_server | Volition's GDC session is documented as describing how the multiplayer level design process had to account for destructible environments, including how to avoid being abused by them. | Geo-Mod 2.0 allows destruction of almost all structures; that level of destructibility forced bespoke level-design rules that do not transfer to a game with selective destructibility. |
| Remnant 2 | Gunfire Games | Unreal Engine 5 / 2023 | linear · coop | Digital Foundry's UE5 survey states Remnant 2 does not use Lumen and instead falls back to SDFAO (signed-distance-field ambient occlusion) and other raster techniques. | Do not copy the SDFAO fallback as a visual target: it is the cheaper non-Lumen path, not an equivalent GI solution. |
| Remnant 2 | Gunfire Games | Unreal Engine 5 / 2023 | linear · coop | Digital Foundry's UE5 survey states Remnant 2 does not use Lumen and falls back to SDFAO and other raster techniques. | Do not treat SDFAO fallback as GI: it is ambient occlusion, not a global-illumination solution. |
| Returnal | Housemarque | Unreal Engine 4 / 2021 | arena · single | A bullet-hell shooter with extremely dense particle effects, where the number of simultaneous emitters makes per-frame simulation of every effect unaffordable. | The talk covers Housemarque's own VFX pipeline; it does not state which effects are flipbooks versus simulated. |
| Returnal | Housemarque | Unreal Engine 4 / 2021 | arena · single | Dense atmospheric particle and light-shaft effects layered on top of heavy combat VFX. | The talk does not separate the cost of light shafts from other VFX. |
| Roco Kingdom: World | Tencent Games / MoreFun Studios | Unreal Engine 4 (custom) / 2026 | open_world · dedicated_server | The shipped 8km x 8km cross-platform title uses baked PRT lightmaps for static lighting and dynamic indirect lighting, with Forward+ reserved for dynamic local lighting. | Do not copy the PRT/lightmap split to a game with fully dynamic lighting or destructive environments; this pipeline assumes static local lighting. |
| Roco Kingdom: World | Tencent Games / MoreFun Studios | Unreal Engine 4 (custom) / 2026 | open_world · dedicated_server | The shipped game stores baked PRT probe lighting in a Cascade Lighting Volume with 4 LODs, 4 m outdoor / 2 m indoor probe intervals, streamed and interpolated on the GPU. | Do not copy the 4 m / 2 m probe intervals or the 4-LOD CLV without re-deriving them from your world scale and memory budget. |
| Senua's Saga: Hellblade 2 | Ninja Theory | Unreal Engine 5 / 2024 | linear · single | Digital Foundry states the game's Nanite geometry 'is nicely enhanced by the use of virtual shadow maps', a key UE5 feature used to raise shadow resolution for dense geometry. | Do not assume the VSM cost model of Hellblade 2 (narrow linear scenes) transfers to open worlds with heavy non-Nanite foliage. |
| Senua's Saga: Hellblade 2 | Ninja Theory | Unreal Engine 5 / 2024 | linear · single | Digital Foundry reports Hellblade 2 supports dynamic resolution scaling, but only when using UE5 TSR upscaling, not with DLSS, XeSS or FSR2 in the menu. | Do not copy the menu restriction that couples DRS to TSR only; the upscaler SDKs support DRS independently. |
| Senua's Saga: Hellblade 2 | Ninja Theory | Unreal Engine 5 / 2024 | linear · single | Digital Foundry praises Hellblade 2's graphics menu for exposing multiple reconstruction and frame-generation options and per-setting frame-time trade-offs. | Do not copy the menu's restriction that locks DRS to TSR; that was a UX decision flagged as a nitpick. |
| Senua's Saga: Hellblade II | Ninja Theory | Unreal Engine 5 / 2024 |  ·  | Character fidelity is a primary deliverable, requiring high-detail source sculpts reduced to a shippable real-time mesh. | Ninja Theory used photogrammetry and bespoke tooling; the pipeline cost is not transferable and no mesh budgets are published. |
| Senua's Saga: Hellblade II | Ninja Theory | Unreal Engine 5 (not stated in the cited source) / 2024 |  ·  | Ninja Theory presented a GDC 2025 talk specifically on ambience design and acoustic systems, i.e. the acoustic space itself is a designed, authored system in a shipped game. | Only the session record was verified; no slide content, parameter values or budgets were retrieved. The value here is as evidence that authored acoustic systems ship at AAA quality, not as a source of technique or numbers. |
| SpeedTree-based foliage (middleware reference) | IDV Inc. / NVIDIA | Direct3D 10, GeForce 8800 / 2007 |  ·  | GPU Gems 3 documents the production vegetation representation used by SpeedTree: leaf cards and silhouette fins extruded and traced with a height map for detailed silhouettes, plus relief mapping on trunks - i.e. the detail-per-triangle techniques that make a  | This is a representation/middleware reference, not a game. The public page confirms the techniques; I quote no numbers from it. 2007-era D3D10 constraints (GeForce 8800) shaped the specific choices and are irrelevant to a modern target. |
| Split Fiction | Hazelight Studios | Unreal Engine 5 / 2025 | linear · coop | Lead Programmer Jonas Mauritzsson: 'the graphics side is always a challenge, since we need to render both players' views at the same time, which imposes more limitations. This demands good communication between tech and art to find creative solutions.' The tea | No frame time, resolution or FPS figure is published. Hazelight's scale, art direction and UE5 customisations are their own; none of the cost transfers to another project. |
| Split Fiction | Hazelight Studios | Unreal Engine 5 / 2025 | linear · coop | Hazelight states networking is always an extra challenge because many of the usual shortcuts do not work when the other player's screen is visible, and that the studio built a good foundation for networking its gameplay systems from the start. | Hazelight's networking is a bespoke, split-screen-first design with custom engine changes; the approach and any latency behaviour are not published and do not transfer to a dedicated-server shooter. |
| Supreme Commander 2 | Gas Powered Games | Supreme Commander 2 engine (in-house) / 2010 | open_world · single | The flow field tile technique was built for and shipped in Supreme Commander 2: sector/portal world layout, cost/integration/flow fields, flow field cache, cost stamps for player-built structures, and a time-sliced rebuild priority queue. | The 50-70% clear-space ratio, the 10x10 sector grid, the 24/40-bit integration field and the 8-bit flow field are parameters of that RTS's terrain and memory budget. They are not performance numbers and do not transfer to a different world  |
| Supreme Commander 2 | Gas Powered Games | Supreme Commander 2 engine / 2010 | arena · single | Agents push each other and slide along walls using physics rather than a reciprocal-avoidance solver; this enabled explosions that push units back and super-large robots that push back a hundred tanks. | This is the physics-based alternative to RVO/ORCA, not an ORCA implementation. The specific gameplay scenarios (whirlwind structures, robots pushing a hundred tanks) depend on that game's physics integration and unit mass model; no avoidanc |
| Team Fortress 2 | Valve | Source / 2007 |  ·  | The reference case for art direction as an engineering specification: a peer-reviewed NPAR paper co-authored by engineers and the art director, in which the illustrative style ('early 20th century commercial illustration with 1960s industrial design elements') | A 2007 multiplayer shooter with nine character silhouettes and small maps. The readability requirement (identify a player at a glance across a map) does not transfer to a single-player game where the camera and the subject are authored, and |
| Team Fortress 2 / Counter-Strike (Source engine) | Valve Corporation | Source / 2004 |  ·  | Valve's shipped Source games run prediction at a default 15 ms timestep with cl_predict, smooth residual error over cl_smoothtime, and expose cl_showerror and sv_showimpacts so teams can see exactly when prediction and lag compensation disagree. | The default 15 ms timestep and 100 ms interpolation are 2004-era broadband assumptions (Valve's own rate recommendations top out at 10000 bytes/second). Reusing the tuning, as opposed to the technique, would be wrong today. |
| Team Fortress 2 / Counter-Strike (Source engine) | Valve Corporation | Source / 2004 |  ·  | The reference shipped implementation: one second of history, players-only by default, three selectable rewind scopes, an explicit 'use sparingly' warning for all-entity rewind, and shipped debug views (sv_showimpacts, sv_showlagcompensation) that let teams see | The one-second history is a 2004 latency assumption. On modern connections a shorter window is defensible; on a game with faster movement a longer one may be needed. The API shape and the debug tooling are the transferable parts. |
| Team Fortress 2 / Counter-Strike: Source (Source engine) | Valve Corporation | Source / 2004 |  ·  | Valve's counter-position: ship at 66 tick (15 ms), document that tickrate 100 costs ~1.5x CPU, and explicitly state that running higher than 66 is not suggested - while cs:go official servers settled at 64. | This is a 2004-era stance shaped by 2004 hosting economics and a 2004 player base. It is valuable as evidence that high tick rate is a choice with a documented cost, not as a recommendation for a 2026 competitive shooter. |
| Teardown | Tuxedo Labs (Voxagon) | In-house voxel engine / 2020 |  ·  | The studio's engine is voxel-based, so destruction is structural modification of the world rather than a pre-fractured, cached simulation - the contrasting architecture to a geometry cache. | This is the opposite approach, not an instance of geometry caching. A voxel world has different memory and authoring characteristics entirely; nothing about Teardown's performance or visual result transfers to a mesh-fracture pipeline. Also |
| Teardown | Tuxedo Labs | In-house voxel engine / 2020 |  ·  | A shipped game whose world is a voxel grid, i.e. the scene representation that voxel-based GI techniques operate on directly. | Teardown does not implement voxel cone tracing; this evidences the data representation, not the algorithm. |
| Terrain Rendering in 'Far Cry 5' | Ubisoft Montreal | Dunia / 2018 |  ·  | A shipped AAA open-world terrain built on a GPU-driven pipeline where the CPU does streaming and the GPU does the terrain work (grid generation in compute, deferred texturing, cliff/rock shading) - the architecture lineage of the GPU clipmap approach. | I could not open the slides or video, so I assert no numbers from this talk at all - not a frame time, not a grid size, not a draw-call count. It is cited only as evidence that a shipped open-world game uses a GPU-driven terrain pipeline. A |
| The Tomorrow Children | Q-Games | Q-Games engine / 2016 | open_world · dedicated_server | The shipped PS4 title lit everything by tracing cones through six cascades of voxel 3D textures, occluding with screen-space directional occlusion and spherical occluders. | Do not copy the six-cascade voxel structure or the 16-direction cone set to hardware without the same memory/bandwidth budget. |
| Titanfall 2 | Respawn Entertainment | Titanfall 2 engine (Source-derived) / 2016 | linear · dedicated_server | Digital Foundry's breakdown observes a shadow 'filtering cascade' line on the floor on PS4/Xbox One and states console shadow quality is lower, with the PC retaining quality further out. | Do not copy console shadow-cascade split distances or the low-quality filtering cascade; PC/console budgets differ per platform. |
| Tom Clancy's Rainbow Six Siege | Ubisoft Montreal | AnvilNext 2 / 2015 | arena · dedicated_server | The team published hard destruction budgets - roughly 6 ms of simulation for a wall, about 25 MB GPU memory, about 200 MB of data plus 150 MB engine overhead in RAM - and treat destruction as a designed, budgeted system with asynchronous event listeners. | These are Siege's own budgets for its destructible scope (mostly walls/hatches) on its target consoles. They do not transfer as targets: a game with whole-building destruction, a different fragmentation density, or a different platform has  |
| Tom Clancy's Rainbow Six: Siege | Ubisoft Montreal | RealBlast / AnvilNext / 2015 | arena · dedicated_server | The shipped game time-slices its procedural destruction, splitting functions into steps that are rescheduled if unfinished, to avoid 60 ms spikes. | Do not copy destruction time-slicing as a pathfinding technique; here it bounds destruction CPU, and the studio warns time-sliced multi-threaded code is hard to debug. |
| Tomb Raider | Crystal Dynamics | Crystal Engine (with AMD TressFX) / 2013 |  ·  | AMD's press release states the Crystal Dynamics collaboration delivered, with the launch of Tomb Raider, the world's first in-game implementation of a real-time, per-strand hair physics system. | This is a vendor press release: it confirms a per-strand hair system shipped in a major 2013 title, but it is not an independent measurement, gives no cost or strand count, and its 'world's first' framing is marketing. Nothing about the har |
| Trials / RedLynx in-house engine | RedLynx (Ubisoft) | RedLynx in-house / 2015 |  ·  | Motivated by a modular in-game level editor where 'background [is] built from small objects' with high draw distance and no baked lighting, RedLynx pushed to a single draw call for the whole viewport and culls 250,000 moving objects with two DrawInstancedIndir | Achieved on a DirectX 11 path without ExecuteIndirect/MultiDrawIndirect, using 64-vertex strip clusters. The specific trick set (virtual deferred texturing, the 8xMSAA trick) exists to fit 2013-2015 console memory bandwidth budgets and is n |
| Trials-series in-house engine (RedLynx) | RedLynx (Ubisoft) | RedLynx in-house / 2015 |  ·  | Used virtual texturing primarily to eliminate texture-based batching, achieving a viewport rendered in a single draw call (x2) with a constant memory footprint, and built virtual deferred texturing and a virtual shadow map (128k^2, 256^2 pages) on the same pag | The 256k^2 / 8k^2 / 128^2 numbers are one team's configuration for a 2015 console memory budget on a specific engine. They are not recommended values. The measured 'up to 3.5x faster than SDSM' figure is for their virtual shadow map in comp |
| Uncharted 4: A Thief's End | Naughty Dog | Naughty Dog engine / 2016 | linear · single | Naughty Dog's GDC talk is documented as a deep dive into vertex shader pipelines and process using features implemented at Naughty Dog for Uncharted 4, covering wind systems, interactivity, ambient animations and optimisations. | Vertex-shader authoring for a linear, tightly authored game does not transfer to an open-world content pipeline with procedural placement. |
| Uncharted 4: A Thief's End | Naughty Dog | Naughty Dog engine / 2016 | linear · single | Naughty Dog's GDC talk is documented as a deep dive into vertex shader pipelines used at Naughty Dog for Uncharted 4, covering wind systems, interactivity, ambient animations and optimisations. | Vertex-shader secondary animation is used to avoid CPU work in a linear, tightly authored game; it does not replace a general-purpose animation graph. |
| Unity DOTS production examples | Unity and partner studios | Unity DOTS / Entities / 2024 | large-scale multiplayer and simulation examples · varies by project | Unity's official DOTS page lists production examples including V Rising, Megacity Metro and IXION. | Список showcase подтверждает применение, но не доказывает одинаковый выигрыш производительности для всех проектов. |
| Unity Netcode for Entities (DOTS sample stack) | Unity Technologies | Unity (ECS / DOTS) / 2022 |  ·  | Unity's DOTS netcode is a server-authoritative + client-prediction framework built directly on ECS, requiring Unity 2022.2.0f1 or higher, and marks predicted ghosts with a PredictedGhost component - i.e. the entire replication and prediction path operates on u | This is an engine capability, not a shipped game, so there is no player-facing result to copy. It also does not make allocation disappear - it moves it. Gameplay code that allocates per frame inside a system will still create garbage regard |
| Unreal Engine 5 (engine feature, adopted by LWC-enabled projects) | Epic Games | Unreal Engine 5.x / 2022 |  ·  | Epic shipped Large World Coordinates as the engine-level answer, raising default WORLD_MAX from 21 km to 88 million km and converting core engine types to doubles, while keeping the GPU path in floats through camera-relative translation. | This is an engine feature, not a shipped game's tuning. The 21 km / 88 million km figures are Epic's engine constants, not a recommendation for your world size. The fact that Epic flags LWC as Beta is the decision-relevant part. |
| Unreal Engine 5 Niagara-based titles (engine guidance) | Epic Games | Unreal Engine 5 (Niagara) / 2022 |  ·  | Epic publishes a dedicated Niagara scalability and best-practices page that treats GPU simulation as a scalability decision and warns that GPU particle cost is quantised (1 particle can cost the same as 64), i.e. GPU simulation is not a free win at low counts. | Engine guidance, not a shipped-game measurement. The 64-particle granularity figure is specific to a GPU dispatch model and is not a portable constant; it does not transfer as a budget to another engine or hardware generation. |
| Unreal Engine 5 projects using Niagara Fluids baked to flipbooks | Epic Games (engine feature) | Unreal Engine 5 (Niagara + Niagara Fluids plugin) / 2023 |  ·  | Epic's own worked example bakes the Grid 3D Gas Colored Smoke Niagara Fluids template - a 3D fluid effect - to a flipbook and re-applies it to a 2D sprite emitter, explicitly because the 3D effect cannot be run in real time on the target platform. | This is a documented engine workflow demonstrated on a template effect, not a shipped game. The 8x8/1024 defaults and the 30 fps default are starting points, not tuned values; the actual memory and performance result for another effect or p |
| Unreal Engine 5 sample 'Open World' / converted World Partition worlds | Epic Games | Unreal Engine 5.x / 2021 |  ·  | The Open World default map ships with World Partition, One File Per Actor, Data Layers and Hierarchical LOD all enabled by default, and contains a 2 km x 2 km sample Landscape - i.e. Epic's own template treats partitioning + OFPA + Data Layers + HLOD as one ma | This is a template, not a shipped game. The 2 km x 2 km landscape and the four-by-default features are a starting configuration for an Epic sample; they are not a validated budget for any real project and should be treated as a demonstratio |
| Unreal Engine 5 titles using Chaos Vehicles | Epic Games (engine feature) | Unreal Engine 5 (Chaos) / 2022 |  ·  | Unreal documents that Chaos Vehicles support the engine's Asynchronous Physics mode, and markets it primarily as improving determinism and predictability rather than raw throughput. | Engine capability, not a shipped-game result. No measured speedup, thread count, or body count transfers, and the determinism benefit is a property of that engine mode, not of async physics in general. |
| Unreal Engine City Sample | Epic Games | Unreal Engine 5 / 2021 | 4 km x 4 km city sample · technical demo | Официальная документация City Sample связывает World Partition, Nanite, Lumen, VSM, Mass AI, Chaos и MetaSounds. | Это демонстрационный проект; его polygon/asset counts и требования не являются минимальными требованиями для любой игры. |
| Unreal Engine Landscape (shipped engine terrain) | Epic Games | Unreal Engine 4/5 / 2014 |  ·  | Ships the simple, predictable option instead of an exotic codec: 16-bit height over a fixed range with a project Z scale, plus a component/section structure whose dimensions are constrained to (A*Quads+1, B*Quads+1) and capped at 1024 components - i.e. Epic tr | The 1024-component recommendation and the -256..255.992 range are Epic's constraints for its Landscape actor. They are not a compression scheme and have no bearing on a custom terrain codec beyond illustrating the trade-off between rate and |
| Unreal Engine MetaHuman grooms | Epic Games | Unreal Engine 5 / 2021 |  ·  | Unreal's own groom documentation illustrates a MetaHuman character with grooms rendered as strands (left) and as cards (right), i.e. Epic's reference character pipeline ships both representations of the same groom. | This confirms the dual-representation workflow is shipped by Epic, but it is an engine demo asset, not a game shipping on a specific platform. No cost, hair count, or swap distance transfers. |
| Unreal Engine Niagara sprite renderer (engine capability) | Epic Games | Unreal Engine 5 (Niagara) / 2023 |  ·  | Unreal's Sprite Renderer exposes Sub Image Size and works with a Sub UVAnimation module, i.e. the engine has first-class support for tiled particle atlases and documents the correct sizing rules. | Engine capability, not a shipped-game result. No draw-call count, saving, or visual outcome transfers. |
| Unreal Engine groom samples / MetaHumans | Epic Games | Unreal Engine 5 / 2021 |  ·  | Unreal ships a documented strand-based groom pipeline with dedicated pages for enabling physics simulation on grooms, groom interpolation, and groom caches, and states strands require an allocated budget and are not supported on all platforms. | Engine capability, not a shipped game result. No cost, strand count, or platform outcome transfers to another project. |
| Unreal Engine shipped titles using Chaos Cloth | Epic Games (engine feature) | Unreal Engine 5 (Chaos) / 2020 |  ·  | The engine ships a documented, in-editor cloth authoring and simulation pipeline (Chaos Cloth solver, painted masks with Max Distance / Backstop / Anim Drive targets, Physics-Asset-driven collision) rather than each studio writing its own solver. | This confirms the technique is productionised in a shipping engine, but it is not a specific game, and no cost, particle count or visual result transfers to another title. The engine feature existing says nothing about whether a given proje |
| Unreal Engine third-person template worked example | Epic Games | Unreal Engine (Lightmass) / 2019 |  ·  | Epic's own documentation walks through deriving PlayAreaHeight from gameplay: measure the camera's highest rotational point (~395 units), add jump height (~210 units), and add buffer to reach 650, noting that higher values cost more runtime memory because more | The 395 / 210 / 650 numbers are properties of Epic's ThirdPerson template character rig and camera. They are not a recommended PlayAreaHeight; the transferable content is the derivation method (max camera height + max jump + buffer). |
| Unreal Engine titles using SaveGame (engine guidance) | Epic Games | Unreal Engine 5 / 2022 |  ·  | Unreal ships a documented save/load framework with an explicitly recommended async save path and a stated caveat that synchronous saving is only sufficient for small save formats. | Engine guidance, not a shipped-game measurement. No save size, duration, or hitch figure transfers; storage performance is platform-specific. |
| V Rising | Stunlock Studios | Unity (ECS for Unity / DOTS) / 2022 | open_world · dedicated_server | Unity documents that Stunlock Studios used ECS throughout development of V Rising, an open-world multiplayer survival game; ECS is the data-oriented alternative to per-agent throttling. | This is a vendor production page. It confirms ECS adoption, not that V Rising used a behaviour-tree update budget, and it reports no agent counts or frametime numbers. |
| V Rising | Stunlock Studios | Unity (ECS for Unity / DOTS) / 2022 | open_world · dedicated_server | Unity documents that Stunlock Studios used ECS throughout the development of V Rising, an open-world multiplayer survival game, including world building in the Editor with custom visual scripting and scalable open-world streaming. | Vendor production page. Confirms full-project ECS adoption in a shipped multiplayer survival game, but reports no entity counts, no frametime, and no evidence about crowd-specific use. Adoption by one studio is not evidence that ECS is the  |
| VALORANT | Riot Games | собственная серверная инфраструктура / 2020 | соревновательные арены · authoritative 128-tick server | Инженерный материал Riot разбирает серверную производительность и сетевую модель VALORANT. | 128 tick - свойство описанного сервиса, а не универсальная рекомендация для каждой игры. |
| VALORANT | Riot Games | Unreal Engine 4 (not stated in the cited Riot article) / 2020 |  ·  | Riot hit the replication scan as a server CPU cost while chasing a 2.34 ms per-frame budget at 128 tick, and responded partly by moving state off replicated variables onto RPCs, reporting 100x-10000x improvements in many cases. | VALORANT is a 10-player fixed-arena game; it never had a relevancy problem in the battle-royale sense, only a per-frame scan problem. Their 'use an RPC instead' answer is a 10-client answer - it does not scale to 100 clients the way a relev |
| VALORANT | Riot Games | Unreal Engine 4 (not stated in the cited Riot article) / 2020 |  ·  | Riot published the full economics of their dedicated servers: 128 tick, a 2.34 ms per-frame budget derived from 3 games per core, 36-core hosts running 108 games, and a 50 ms -> sub-2 ms frame-time optimisation programme including NUMA binding, C-state limitin | Every number here is a function of Riot's game (10 players, fixed arena, 128 Hz), their hardware (36-core hosts) and their scale. Nothing about the 2.34 ms budget or 108 games/host transfers to a 100-player BR or a 32-player co-op game; wha |
| Valley of the Ancient | Epic Games | Unreal Engine / 2017 |  ·  | Epic's own shipped GAS sample is documented in the primary GAS page itself: '## Valley of the Ancient Sample' with a '### Walking Animation Example' and a '### Charge Attack Example', i.e. the reference implementation demonstrates abilities driving both locomo | It is a technology sample, not a shipped game with a measured ability count, and no performance figure is published for it. It proves the framework is complete enough to drive animation and combat; it says nothing about how many concurrent  |
| Valley of the Ancient (Epic UE5 sample) | Epic Games | Unreal Engine 5 /  | open_world · single | The Gameplay Ability System page states that Echo's charge-and-attack animation and the walking animation in the Valley of the Ancient sample are examples of a Gameplay Ability. | This is a first-party tech sample, not a shipped commercial title; its ability setup does not represent production content scale. |
| Valley of the Ancient (Epic sample project) | Epic Games | Unreal Engine 5 / 2022 |  ·  | Epic's own GAS/animation sample is the reference project for the shipped UE5 character pipeline, i.e. the GPUSkinVertexFactory / Skin Cache paths described in the rendering-paths documentation, rather than a bespoke skinner. | A sample project with one hero character says nothing about crowd-scale skin-cache VRAM pressure, which is the actual failure mode of this method. |
| Warhammer 40,000: Space Marine | Relic Entertainment | Relic in-house (Essence) / 2011 |  ·  | The RVO2 Library maintainers state the library 'has been licensed for the video game Warhammer 40,000: Space Marine from developer Relic', and quote a Daily Telegraph review noting that with many orks on screen 'the framerate never takes a hit'. | Confirms the library was licensed for a shipped title, but not which agent counts or subsystems used it, nor the integration cost. The newspaper quote is a review impression, not a measurement, and does not transfer as a performance number. |
| World Partition HLOD reference workflow (Unreal Engine 5) | Epic Games | Unreal Engine 5.x / 2021 |  ·  | Epic's own shipped workflow demonstrates the class split: a merged-mesh default layer for architecture with baked lightmaps and materials, and a separate Instancing layer for a Blueprint tree class (HLODLayersForActorClasses maps Base_Tree_C to HLODLayer_Tree) | The LoadingRange=30000 and TargetLightMapResolution=256 in Epic's example are placeholder demonstration values. They encode nothing about a real game's draw distance or art density; treat the pattern (separate layers per content class on se |

Кейс подтверждает факт применения, устройство или компромисс. Он не переносит
FPS, количество активных сущностей, tick rate, latency, размер команды или
требования к железу. Поэтому карточка хранит `relevance` и `transfer_limits`, а
`/recommend` показывает кейсы как практическую сверку со статусом
`not_calibrated`.

## 17. Риски

| Риск | Почему важен | Контроль |
| --- | --- | --- |
| Evidence drift | A page or package changes while a claim stays published. | checked_at, version, locator, availability and review status; re-review before release. |
| False numerical precision | An expert score looks like FPS or benchmark data. | basis is explicit; measured/documented/derived are separated from expert_estimate and unknown. |
| Hidden dependency | A method appears available because an API, package, plugin or version was not modeled. | directed graph, transitive closure, unresolved edge list and version checks. |
| Late architecture change | A sound method is selected after content and tools are locked. | late_factor, stage warning, feasibility package and P50/P80 rework range. |
| Resource double counting | CPU/GPU/memory effects are multiplied or the same savings are counted twice. | one FrameModel; sequential/parallel CPU, raster/RT GPU and memory composition are separate. |
| Case over-transfer | A successful game is treated as a template with the same FPS or team size. | case evidence records relevance and transfer limits; no automatic numeric bonus. |

## 18. Итоговый план внедрения

1. Зафиксировать revision, входной профиль и опубликованный snapshot.
2. Прогнать Alembic и проверить резервную копию SQLite.
3. Выполнить seed доказательств; проверить claims без источника, локатора и версии.
4. Ревизовать 40 функций, 124 методов, движки, инструменты, method-tool links, conflicts и hardware anchors.
5. Для выбранной корзины закрыть prerequisites, version/API compatibility и hard conflicts.
6. Запустить feasibility/prototype с трассами CPU/GPU/IO/network; сохранить условия измерения.
7. Обновить raw benchmark anchors только вместе с контекстом и датой.
8. Пересчитать P50/P80 и critical path по фактическим ролям команды.
9. Проверить минимальную конфигурацию на Windows и Linux, затем пройти QA/regression/release gates.

## 19. Ограничения модели, критерии приёмки и аудит

### 19.1 Ограничения

Без исходного кода, ассетов и runtime-профиля невозможно честно вывести точный
FPS, универсальную latency, точный размер RAM/VRAM или календарную дату. Публичная
документация и книги подтверждают устройство механизма, но не обещают его
результат в другом проекте. Нормализованные hardware indices пригодны для
ранжирования внутри каталога и сценарного сравнения; это не замена измерению.

Статус калибровки: `not_calibrated`. Процент точности не показывается. Чтобы
изменить статус, нужна реальная выборка: одинаковый профиль, версия движка, commit
ассетов, target platform/API, measured frame-time percentiles, memory, IO and
network metrics, а также правило train/test split.

### 19.2 Критерии приёмки

- одинаковый вход, algorithm version и catalog revision дают одинаковый результат;
- увеличение объекта/NPC count, resolution или quality не уменьшает соответствующую нагрузку;
- CPU main/parallel, GPU raster/RT, RAM/VRAM и storage/network не смешиваются без подписи;
- неизвестная зависимость не считается закрытой;
- hard conflict не попадает в рабочую корзину;
- complement не даёт числовой бонус без измерения;
- удаление prerequisite делает метод явно неприменимым;
- team size меняет календарь, но не person-days;
- critical path строится по DAG, P80 >= P50;
- отсутствие числовых данных получает `unknown`/`expert_estimate`;
- non-PC цели не попадают в PC quantitative hardware estimate;
- source title, authors/publisher, type, version and locator видны пользователю;
- Markdown и PDF проходят текстовый и визуальный QA.

### 19.3 Аудит покрытия каталога

| Проверка | Значение | Интерпретация |
| --- | --- | --- |
| methods: implementation / optimization | 67 / 57 | catalogue snapshot |
| methods: confidence < 0.70 | 11 | manual review queue |
| methods: no explicit conditions | 0 | applicability gap |
| methods: no engine/platform/HW filter | 122 / 114 / 111 | transferability gap |
| method-tool links without own source_url | 111 / 475 | relationship provenance gap |
| engines/tools without docs_url | 1 / 7 | version/tooling gap |
| relations: alternative/complement/risk/unknown | 41 / 181 / 74 / 8 | conflict graph |
| distinct method source URLs | 91 | source reuse is not claim coverage |

### 19.4 Глубокие исследовательские карточки

### Потоковая загрузка мира и HLOD

**Факт и источник.** Epic описывает World Partition как единый persistent level, разделённый на grid cells, которые загружаются и выгружаются по streaming sources и runtime grid [S01](https://dev.epicgames.com/documentation/en-us/unreal-engine/world-partition-in-unreal-engine). HLOD заменяет дальние выгруженные ячейки proxy mesh/material и имеет отдельные режимы Instancing, Merged Mesh и Simplified Mesh [S24](https://dev.epicgames.com/documentation/en-us/unreal-engine/world-partition---hierarchical-level-of-detail-in-unreal-engine). PCG может назначать сгенерированные актёры в Data Layers и HLOD Layers [S25](https://dev.epicgames.com/documentation/en-us/unreal-engine/using-pcg-with-world-partition-in-unreal-engine?lang=en-US). В CryEngine документирован асинхронный StartRead: запрос проходит I/O, decompression threads, callback threads и затем main-thread completion; порядок запросов сортируется для эффективного чтения [S28](https://www.cryengine.com/docs/static/engines/cryengine-5/categories/23756813/pages/23306430).

**Синтез для DSS.** Синтез: размер мира сам по себе не является числом для FPS. Управляемые переменные — размер ячейки, loading range, число источников, HLOD-представление, размер чанка, скорость чтения, декомпрессия и время активации. Поэтому в DSS они должны быть отдельными полями, а не одним scalar `open_world=true`. HLOD уменьшает видимую работу дальних объектов, но добавляет cook/build и риск несоответствия proxy исходной геометрии. PCG создаёт повторяемый content pipeline, но не гарантирует дешёвую runtime-сцену.

**Проверка в проекте.** Проверка: прогнать один маршрут и телепорт с cold/warm cache на Windows и Linux; сохранить active/loaded/visible cells, объём запрошенных байтов, I/O latency p50/p95/p99, decompression time, activation time, RAM/VRAM и frame-time spikes. Отдельно сравнить HLOD off/instancing/merged/simplified и PCG-generated/static content; в отчёте хранить commit ассетов и настройки grid/range.

Источники: `S01, S24, S25, S28`.

### Рендеринг: геометрия, освещение, тени и API-возможности

**Факт и источник.** Nanite описан Epic как virtualized geometry с fine-grained streaming и автоматическим LOD; документация перечисляет поддерживаемые типы контента и практические ограничения [S02](https://dev.epicgames.com/documentation/en-us/unreal-engine/nanite-virtualized-geometry-in-unreal-engine). Lumen предназначен для динамического GI/reflections, но стоимость зависит от детализации, view distance, hardware/software path и числа экземпляров [S03](https://dev.epicgames.com/documentation/en-us/unreal-engine/lumen-global-illumination-and-reflections-in-unreal-engine). Таблица rendering paths связывает Nanite/VSM/Lumen с RHI, Shader Model и RT-возможностями [S04](https://dev.epicgames.com/documentation/en-us/unreal-engine/supported-features-by-rendering-path-for-desktop-with-unreal-engine). VRS имеет tiered capability и ограничения по shading-rate [S05](https://microsoft.github.io/DirectX-Specs/d3d/VariableRateShading.html), а mesh shaders заменяют традиционный VS/HS/DS/GS pipeline только на устройствах с нужной поддержкой [S06](https://microsoft.github.io/DirectX-Specs/d3d/MeshShader.html).

**Синтез для DSS.** Синтез: `GPU raster`, `GPU RT`, `VRAM`, `API` и `feature flags` — независимые оси. Нельзя суммировать Nanite, VSM, Lumen, VRS и upscaling как проценты экономии: часть методов меняет объём работы, часть — способ её планирования, часть — качество/разрешение. Ветка capability должна предшествовать TOPSIS: D3D12 feature level задаёт функциональность, но не производительность [S38](https://learn.microsoft.com/en-us/windows/win32/direct3d12/hardware-feature-levels); конкретные опциональные возможности запрашиваются через CheckFeatureSupport [S39](https://learn.microsoft.com/en-us/windows/win32/api/d3d12/ne-d3d12-d3d12_feature), а RT tier — отдельная проверка [S40](https://learn.microsoft.com/en-us/windows/win32/api/d3d12/ne-d3d12-d3d12_raytracing_tier).

**Проверка в проекте.** Проверка: фиксировать сцену, camera path, draw resolution, internal resolution, upscaler, RT on/off, Nanite/VSM/Lumen/VRS flags и driver/API. Снять CPU main/render thread, GPU passes, raster/RT queue, shader/mesh preparation, VRAM residency and p99 frame time в packaged build. Критерий `meets` применять к frame-time budget, а не к одной средней частоте кадров.

Источники: `S02, S03, S04, S05, S06, S19, S20, S21, S38, S39, S40`.

### Симуляция, ECS/Jobs и адаптивный AI

**Факт и источник.** Unity Job System запускает пользовательскую многопоточную работу на worker threads и строит dependency chains; документация отдельно предупреждает о главном потоке, Complete и маркере WaitForJobGroup [S31](https://docs.unity3d.com/6000.0/Manual/job-system-overview.html), [S46](https://docs.unity3d.com/2023.2/Documentation/Manual/JobSystemJobDependencies.html), [S58](https://docs.unity3d.com/es/2021.1/Manual/JobSystemTroubleshooting.html). Unity перечисляет production cases DOTS: V Rising, IXION, Zenith: The Last City и Detonation Racing [S32](https://unity.com/dots). В докладе Valve по Left 4 Dead описаны Survivor Intensity, tracking peak intensity, threat population и паузы между пиками [S11](https://steamcdn-a.akamaihd.net/apps/valve/2009/ai_systems_of_l4d_mike_booth.pdf). Godot рекомендует frustum/occlusion culling, LOD/HLOD, MultiMesh и измерение стоимости animation/physics/lighting [S10](https://docs.godotengine.org/en/stable/tutorials/performance/optimizing_3d_performance.html).

**Синтез для DSS.** Синтез: ECS/Jobs может уменьшить последовательную часть и улучшить locality, но добавляет копирование, dependency barriers, ownership и миграцию данных. AI Director управляет пиками популяции и драматическим pacing; он не уменьшает автоматически стоимость одного NPC. В DSS это разные узлы: `population_control`, `behaviour_update`, `navigation`, `perception`, `animation`, `physics`. Нельзя переносить рекламное описание DOTS или поведение L4D в проценты ускорения другого проекта.

**Проверка в проекте.** Проверка: выбрать фиксированный seed и нагрузочные точки N=50/100/200/500 агентов; сравнить baseline, jobs/ECS и director on/off. Снимать main-thread, worker timeline, wait/barrier time, allocations, cache-sensitive data where available, navmesh queries, animation/physics, peak active NPC and frame-time p99. Для determinism/networked simulation добавить повторные прогоны и checksum состояния.

Источники: `S07, S08, S09, S10, S11, S31, S32, S46, S58`.

### Сетевое моделирование и релевантность

**Факт и источник.** Valve объясняет в CS2 sub-tick updates как передачу точного момента движения, выстрела или броска внутри серверного такта [S12](https://www.counter-strike.net/cs2). Riot фиксирует для VALORANT simulation timestep 128 Hz, работу prediction/correction и влияние client/server buffering [S13](https://www.riotgames.com/en/news/peeking-valorants-netcode). В отдельной статье Riot приводит расчёт: 128 Hz = 7.8125 ms, при трёх играх на ядро целевой бюджет 2.6 ms, после резерва 10% — 2.34 ms на игру [S14](https://www.riotgames.com/en/news/valorants-128-tick-servers). Epic показывает, что Replication Graph строит списки актёров для каждого соединения, а Actor Relevancy отсекает невлияющие объекты [S26](https://dev.epicgames.com/documentation/en-us/unreal-engine/replication-graph-in-unreal-engine), [S27](https://dev.epicgames.com/documentation/en-us/unreal-engine/actor-relevancy-in-unreal-engine). Godot high-level multiplayer использует UDP/ENet и разные каналы для сообщений с разной надёжностью [S30](https://docs.godotengine.org/en/stable/tutorials/networking/high_level_multiplayer.html).

**Синтез для DSS.** Синтез: server tick, render FPS, input latency, buffering, relevance set, serialization, packet loss и bandwidth должны моделироваться раздельно. Sub-tick, prediction и rewind — дополняющие части протокола, а не три независимые скидки. Пример Epic с Fortnite (100 players/около 50 000 replicated actors) — документация механизма, а не лимит нового проекта. Число игроков без частоты обновлений и размера состояния не определяет traffic.

**Проверка в проекте.** Проверка: стенд 1/2/4/8/16 клиентов с controlled RTT, jitter, loss, reordering и bandwidth cap; сравнить fixed tick 30/60/128, relevance on/off и aggregation. Логировать server frame p50/p95/p99, simulation divergence, hit validation, snapshot/input bytes, packets, queueing/buffering и client input-to-photon proxy. Server-only costs не включать в PC client hardware row.

Источники: `S12, S13, S14, S26, S27, S30, S53`.

### Аудио, окклюзия и читаемость

**Факт и источник.** CryEngine документирует режимы No Ray, SingleRay и MultipleRay; MultipleRay следует включать только если точности одного raycast недостаточно. Raycasts пропускаются для объектов без активного audio trigger [S29](https://www.cryengine.com/docs/static/engines/cryengine-5/categories/23756816/pages/44964914). Там же описаны surface obstruction, отдельные occlusion/obstruction значения и отключение расчёта за `s_OcclusionMaxDistance`. Crytek в материале Hunt: Showdown связывает реалистичность с readability and consistency [S17](https://www.huntshowdown.com/news/hunt-audio-readability-realism-and-consistency).

**Синтез для DSS.** Синтез: бюджет аудио зависит от числа активных источников, ray policy, частоты обновления, surface materials, DSP/middleware and mix graph. Один параметр `spatial_audio=true` скрывает важные trade-offs. Более точная окклюзия может улучшить физическую правдоподобность, но не обязательно UX; читаемость — отдельная quality goal. Поэтому `audio_quality`, `audio_cpu`, `ray_queries` и `device/output` нельзя объединять в один балл.

**Проверка в проекте.** Проверка: записать одинаковую сцену со статическими/динамическими преградами и 10/50/200 активными источниками; сравнить No Ray/Single/Multiple, distance cutoff и material classes. Снимать ray/query count, DSP time, CPU, memory, output latency и blinded listening/UX result. Хранить устройство вывода и микс, иначе сравнение не воспроизводится.

Источники: `S17, S18, S29`.

### Сборка, cooking, чанки и I/O

**Факт и источник.** Unreal описывает packaging как последовательность Build, Cook, Stage, Package, с необязательными Deploy/Run; cooking конвертирует и оптимизирует ассеты под платформу, исключает неиспользуемые данные и создаёт Pak-файлы [S23](https://dev.epicgames.com/documentation/en-us/unreal-engine/packaging-your-project). Chunking разделяет контент для DLC/patch/streaming installation [S23](https://dev.epicgames.com/documentation/en-us/unreal-engine/packaging-your-project). Microsoft DirectStorage guidance требует проверять capability, compression path, staging and fallback, а GPU decompression конкурирует за GPU resources [S52](https://github.com/microsoft/DirectStorage/blob/main/Docs/DeveloperGuidance.md). Unreal texture metrics различают pool usage, wanted mips and streaming updates [S54](https://dev.epicgames.com/documentation/en-us/unreal-engine/texture-streaming-metrics-in-unreal-engine), [S55](https://dev.epicgames.com/documentation/en-us/unreal-engine/texture-streaming-configuration).

**Синтез для DSS.** Синтез: build-time, install size, cold-start, streaming bandwidth, decompression CPU/GPU and runtime memory are different metrics. Chunking can improve delivery and patch granularity but creates dependency/packaging checks. A faster storage device cannot compensate for insufficient asset prioritization or activation work. DSS therefore keeps storage as an independent resource axis and marks DirectStorage as conditional capability, not universal optimization.

**Проверка в проекте.** Проверка: clean checkout and incremental cook; report code compile, shader compile, cook, stage, package, patch size, installed bytes, cold/warm startup, first-use hitch, read/decompress/activate latency, CPU/GPU queues and pool/wanted mips. Compare NVMe/SATA SSD/HDD only on the same build, OS cache policy and content commit; record fallback path.

Источники: `S23, S28, S52, S54, S55`.

### Движки, инструменты, версии и переносимость

**Факт и источник.** Unity documents Jobs, Entities/DOTS, Addressables and Netcode as versioned packages/workflows; DOTS production examples show that the tool is used in different game classes, but not that one numeric gain transfers [S31](https://docs.unity3d.com/6000.0/Manual/job-system-overview.html), [S32](https://unity.com/dots). Unreal publishes a rendering-path matrix and separate hardware/software requirements [S04](https://dev.epicgames.com/documentation/en-us/unreal-engine/supported-features-by-rendering-path-for-desktop-with-unreal-engine), [S41](https://dev.epicgames.com/documentation/en-us/unreal-engine/hardware-and-software-specifications-for-unreal-engine). Valve's developer resource shows that Hammer/Authoring Tools are branch/game-specific, with Source 2 tooling distributed through particular games [S43](https://developer.valvesoftware.com/wiki/Valve_Hammer_Editor). TGS now labels HeroEngine as legacy and its current site warns about official domains/status [S44](https://tgs.tech/solutions/heroengine-legacy), [S45](https://tgs.tech/apex-videos).

**Синтез для DSS.** Синтез: поддержка движка — это не бинарный `engine=yes`. Она должна включать version, package/plugin, target platform/API, scope (runtime/editor/build/server), tool relation and evidence freshness. HeroEngine оставлен в каталоге из-за фиксированного охвата, но его public applicability — `legacy/needs_review`, а не подтверждённая текущая совместимость. Custom всегда требует project-owned design record. Branch-specific tools нельзя связывать с методом без source_url and locator.

**Проверка в проекте.** Проверка: для каждой пары method-tool зафиксировать engine version, tool/plugin version, platform, scope, docs URL, minimal reproduction and owner. Проверять upgrade/downgrade, clean install and package lock. Unknown/missing source должен дать `unknown`, а не `supported`; incompatible capability отфильтровывается до ranking.

Источники: `S04, S31, S32, S41, S43, S44, S45`.

### Выбор по качеству, бенчмаркам и evidence hierarchy

**Факт и источник.** ISO/IEC 25010:2023 задаёт модель качества продукта с характеристиками и подхарактеристиками для specification, measurement and evaluation [S33](https://www.iso.org/standard/78176.html). ISO/IEC 20741 отдельно описывает purpose-oriented evaluation and selection of software engineering tools и предлагает учитывать capabilities и quality characteristics [S34](https://www.iso.org/obp/ui?_escaped_fragment_=iso%3Astd%3Aiso-iec%3A20741%3Aed-1%3Av1%3Aen). PassMark предупреждает, что CPU Mark — агрегат тестов, single-thread полезнее для плохо распараллеливаемых приложений, а benchmark не воспроизводит каждую нагрузку [S49](https://www.cpubenchmark.net/singleThread.html), [S50](https://passmark.com/support/performancetest_faq/understanding-results.php). 3DMark позволяет сравнивать связки CPU/GPU и смотреть frame rate/температуры, но не заменяет game-specific workload [S51](https://benchmarks.ul.com/3dmark).

**Синтез для DSS.** Синтез: TOPSIS оправдан как прозрачное сравнение альтернатив при заданных весах, но его score — decision utility, не измерение. ISO-подход означает сначала определить quality goals и measurable acceptance criteria, затем выбрать метод/инструмент. Hardware benchmark anchor должен хранить raw value, тест, дату, API/resolution/RT context and normalization formula. Confidence — качество evidence, не процент FPS.

**Проверка в проекте.** Проверка: прогнать sensitivity weights ±10%, добавить/убрать один критерий, сравнить ranking stability and reason codes. Для hardware собрать same-game or same-engine trace on target devices; до этого выводить class/range and gap list. Separate benchmark source from evidence claim and attach locator/context.

Источники: `S33, S34, S49, S50, S51`.

### Оценка сроков, PERT и critical path

**Факт и источник.** PMI описывает three-point estimating и различает triangular `cE=(O+M+P)/3` и beta/PERT `cE=(O+4M+P)/6` [S35](https://www.pmi.org/-/media/pmi/documents/public/pdf/pmbok-standards/errata-sheet-qas-6th.pdf). NASA описывает PERT/CPM через precedence network, три оценки activity, mean/variance and longest-path critical path, а также ограничения метода [S36](https://ntrs.nasa.gov/api/citations/19870020777/downloads/19870020777.pdf). NASA glossary определяет critical path как longest path and отдельно предупреждает о double counting uncertainty/risk [S57](https://www.nasa.gov/ocfo/ppc-corner/ppc-glossary/). Amdahl формализует верхнюю границу ускорения как `S(N)=(Ts+Tp)/(Ts+Tp/N)` и отмечает parallel overhead [S37](https://www.usenix.org/legacy/publications/library/proceedings/als00/2000papers/papers/full_papers/brownrobert/brownrobert_html/node3.html).

**Синтез для DSS.** Синтез: person-days и calendar duration — разные показатели. Команда может распараллелить независимые пакеты, но не отменяет dependencies, integration, QA или scarce roles. P50/P80 текущего DSS — scenario estimates; пока нет исторической выборки, нельзя называть их статистически калиброванными percentiles. Риски не должны второй раз прибавляться к уже расширенному P80.

**Проверка в проекте.** Проверка: хранить O/M/P, formula, assumptions and role capacity per package; строить DAG and longest path. Для примера из отчёта вычислить PERT mean/sigma, затем сопоставить фактическое завершение с prediction interval. После нескольких проектов заменить шаблонные коэффициенты empirical calibration, сохранив train/test split and revision.

Источники: `S35, S36, S37, S57`.

Каждая карточка разделяет наблюдаемый факт, аналитический синтез и план проверки.
Ссылка или showcase подтверждает только тот механизм и контекст, который указан в
локаторе; внешний проект не превращается в эталон производительности.

### 19.5 Воспроизводимые расчёты (сводка)

### Бюджет кадра

| Target FPS | Frame budget, ms | Интерпретация |
| --- | --- | --- |
| 30 | 33.333 | low/quality-first target |
| 60 | 16.667 | common responsiveness target |
| 90 | 11.111 | high-refresh baseline |
| 120 | 8.333 | high-refresh target |
| 144 | 6.944 | competitive/high-refresh case |
| 240 | 4.167 | very high-refresh case; content-dependent |

### Пиксельная нагрузка разрешения

| Разрешение | Pixel ratio | База |
| --- | --- | --- |
| 1280x720 | 0.444 | relative to 1920x1080 |
| 1920x1080 | 1.000 | baseline |
| 2560x1440 | 1.778 | relative to 1080p |
| 3840x2160 | 4.000 | relative to 1080p; 2.25x 1440p |

### Предел параллелизации

| Workers | Speedup | Допущение |
| --- | --- | --- |
| N=1 | 1.000 | baseline |
| N=2 | 1.429 | s=0.40, idealized |
| N=4 | 1.818 | s=0.40, idealized |
| N=8 | 2.105 | s=0.40, idealized |
| N=16 | 2.353 | s=0.40, idealized |
| N→∞ | 2.500 | serial ceiling 1/s |

### Трёхточечная оценка

| Inputs | Calculation | Статус |
| --- | --- | --- |
| O=2, M=4, P=10 человеко-дней | (2 + 4×4 + 10) / 6 = 4.667 | beta/PERT expected duration |
| Тот же диапазон | σ = (10 − 2) / 6 = 1.333 | approximate spread; not a calibrated percentile |
| P80 proxy, only if explicitly assumed normal | 4.667 + 0.8416×1.333 = 5.789 | derived scenario, not a measurement |

### Critical path

| Task | Duration | Predecessors | Path result |
| --- | --- | --- | --- |
| A Design | 3 | — | A-B-D-E / A-C-D-E |
| B Prototype | 5 | A | A-B-D-E = 18 |
| C Content/asset prep | 8 | A | A-C-D-E = 21; critical |
| D Integration | 6 | B,C | merge waits for max(B,C) |
| E QA/release gate | 4 | D | longest path ends at 21 |

### Сеть

| Scenario | Inputs | Derived result | Limits |
| --- | --- | --- | --- |
| Server → 9 clients | C=9, f=20/s, payload=120 B, IPv4+UDP H=28 B | 9×20×(120+28)=26,640 B/s ≈ 26.0 KiB/s ≈ 213 kbps | derived; excludes encryption, retransmits and other traffic |
| 128 Hz server frame | 1 / 128 s | 7.8125 ms per tick | published VALORANT case S14; not universal target |
| Riot 3 games/core target | 7.8125 / 3 | 2.6042 ms; ×0.90 = 2.3438 ms | published case S14; host/game-specific |

### Память

| Component | Inputs | Result | Basis |
| --- | --- | --- | --- |
| Textures / geometry | 2.4 + 1.1 | 3.5 GiB | scenario input |
| Render targets / transient | 0.8 + 0.6 | 1.4 GiB | scenario input |
| Audio / other | 0.2 | 0.2 GiB | scenario input |
| Subtotal | 3.5 + 1.4 + 0.2 | 5.1 GiB | sum, no headroom |
| 20% safety/headroom | 5.1 × 1.20 | 6.12 GiB | derived planning allowance |

Таблицы выше — собственные вычисления DSS из явно указанных входов. Они
демонстрируют структуру бюджета и верхние/сценарные границы, но не являются
измерением конкретной игры. Для чисел, выведенных из документации (например,
128 Hz), сохранены и исходный источник, и формула.

### 19.6 Публичный API

- `GET /api/catalog/sources`, `/catalog/evidence`, `/catalog/evidence-summary`;
- `GET /api/catalog/cases`, `/catalog/cases/{code}`;
- `GET /api/catalog/dependencies`, `/catalog/teams`, `/catalog/graph-checks`;
- `POST /api/schedule`;
- `POST /api/report-data`, `GET /api/report-data`;
- расширенные `/recommend` и `/hardware-estimate` с evidence summary, cases, P50/P80, target assessments и unresolved items.

UI содержит экраны «Доказательства», «Кейсы игр», «Зависимости и конфликты»,
«Трудоёмкость и календарный план»; badges показывают documented, measured,
derived, case_evidence, expert_estimate и unknown. Все открываемые материалы
остаются ссылками на исходный источник.

## 20. Полный список источников

Всего в реестре 936 источников; ниже — полный перечень с типом, датой
проверки, версией, платформой, локатором и доступностью.

| Код | Название | Автор / издатель | Тип | Дата | Проверен | Версия | Платформа | Локатор | Доступность |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| BOOK_GAME_ENGINE_ARCHITECTURE | Game Engine Architecture, Third Edition | Jason Gregory | book | 2018-07-01 | 2026-09-10 | 3rd edition |  | chapters 3-4, 16: engine architecture, runtime, resource systems | available |
| BOOK_GAME_PROGRAMMING_PATTERNS | Game Programming Patterns | Robert Nystrom | book | 2014-11-13 | 2026-09-10 | online edition |  | chapters: Data Locality, Object Pool, State | available |
| BOOK_GPU_GEMS_3 | GPU Gems 3: Programming Techniques for High-Performance Graphics | NVIDIA contributors | book | 2007-08-01 | 2026-09-10 | GPU Gems 3 |  | chapters on volumetric lighting, shadows and post-processing | available |
| BOOK_REAL_TIME_RENDERING | Real-Time Rendering, Fourth Edition | Tomas Akenine-Moller; Eric Haines; Naty Hoffman | book | 2018-08-01 | 2026-09-10 | 4th edition |  | chapters 2-3, 8: rendering pipeline, transformations, shadows | available |
| CLUSTERED_SHADING | Clustered Deferred and Forward Shading (Olsson, Billeter, Assarsson) |  | research | 2012 | 2026-09-10 |  |  | overview page | available |
| COENEN_DOOM | Doom Eternal graphics study (Simon Coenen) |  | secondary | 2024 | 2026-09-10 |  |  | overview page | available |
| CS2_SUBTICK | Counter-Strike 2: Moving Beyond Tick Rate |  | official_game_material | 2023-09-27 | 2026-09-10 |  |  | section: Sub-tick updates | available |
| DF_ITTakesTWO | It Takes Two tech analysis (Digital Foundry) |  | secondary | 2021-03-27 | 2026-09-10 |  |  | section: split-screen rendering and performance analysis | available |
| DOOM_ETERNAL | Rendering the Hellscape of Doom Eternal (SIGGRAPH 2020) |  | research | 2020-08-25 | 2026-09-10 |  |  | slides: geometry caches, gore, material compositing, target frame rate | available |
| GAFFER_TIMESTEP | Fix Your Timestep! (Gaffer on Games) |  | secondary | n/a | 2026-09-10 |  |  | overview page | available |
| GAME_AI_FLOW_FIELDS | Crowd Pathfinding and Steering Using Flow Field Tiles — Elijah Emerson |  | secondary | 2013 | 2026-09-10 |  |  | overview page | available |
| GODOT_DECALS | Godot Docs: Using Decals |  | official_documentation | n/a | 2026-09-10 |  |  | overview page | available |
| GODOT_LIGHTS | Godot Docs: Lights and Shadows |  | official_documentation | n/a | 2026-09-10 |  |  | overview page | available |
| GODOT_MESHLOD | Godot Docs: Mesh Level of Detail |  | official_documentation | n/a | 2026-09-10 |  |  | overview page | available |
| GODOT_MULTIMESH | Godot Docs: MultiMeshInstance3D |  | official_documentation | n/a | 2026-09-10 |  |  | overview page | available |
| GODOT_MULTIPLAYER | Godot Docs: High-level Multiplayer |  | official_documentation | n/a | 2026-09-10 |  |  | section: High-level multiplayer | available |
| GODOT_OCCLUSION | Godot Docs: Occlusion Culling |  | official_documentation | n/a | 2026-09-10 |  |  | overview page | available |
| GODOT_PARTICLES | Godot Docs: 3D Particles |  | official_documentation | n/a | 2026-09-10 |  |  | overview page | available |
| GODOT_PERF | Godot Docs: Optimizing 3D Performance |  | official_documentation | n/a | 2026-09-10 |  |  | section: Optimizing 3D Performance | available |
| GODOT_PHYSICS | Godot Docs: Physics Introduction |  | official_documentation | n/a | 2026-09-10 |  |  | overview page | available |
| GODOT_THREADS | Godot Docs: Using Multiple Threads |  | official_documentation | n/a | 2026-09-10 |  |  | overview page | available |
| GPP_DATALOCALITY | Game Programming Patterns: Data Locality |  | book | n/a | 2026-09-10 |  |  | overview page | available |
| GPP_OBJECTPOOL | Game Programming Patterns: Object Pool |  | book | n/a | 2026-09-10 |  |  | overview page | available |
| GPP_STATE | Game Programming Patterns: State |  | book | n/a | 2026-09-10 |  |  | overview page | available |
| GPU_GEMS_SHAFTS | GPU Gems 3, Ch.13: Volumetric Light Scattering as a Post-Process (Mitchell) |  | engineering_article | 2008 | 2026-09-10 |  |  | overview page | available |
| HUNT_AUDIO | Hunt: Showdown — Audio readability, realism and consistency |  | engineering_article | 2024 | 2026-09-10 |  |  | sections: Occlusion and Realism, Feedback and Readability | available |
| HUNT_AUDIO_2025 | Dev Insight - A deep dive into 3D Audio in Hunt |  | studio_engineering_article | 2025-05-09 | 2026-09-10 |  |  | section: CrySpatial | available |
| KHRONOS_ASYNC_COMPUTE | Khronos Vulkan Samples — Using async compute to saturate GPU |  | secondary | n/a | 2026-09-10 |  |  | overview page | available |
| L4D_AI_DIRECTOR | The AI Systems of Left 4 Dead |  | engineering_talk | 2009-09-01 | 2026-09-10 |  |  | section: Adaptive Dramatic Pacing | available |
| MESHOPT | meshoptimizer: mesh optimization library |  | open_source | n/a | 2026-09-10 |  |  | overview page | available |
| MS_DIRECTSTORAGE_GUIDANCE | Microsoft DirectStorage — Developer Guidance |  | open_source | n/a | 2026-09-10 |  |  | overview page | available |
| MS_MESH_SHADER | DirectX mesh shader specification |  | official_documentation | n/a | 2026-09-10 |  | Windows/Linux PC | section: Required Support from the device | available |
| MS_VRS | Variable Rate Shading \| DirectX-Specs |  | official_documentation | n/a | 2026-09-10 |  | Windows/Linux PC | sections: Specifying Shading Rate, Feature Tiering | available |
| NVIDIA_NTC | NVIDIA RTXNTC SDK |  | engineering_article | n/a | 2026-09-10 |  |  | overview page | available |
| NVIDIA_VOXEL_CONES | Interactive Indirect Illumination Using Voxel Cone Tracing — Crassin et al. |  | engineering_article | 2011-09 | 2026-09-10 |  |  | overview page | available |
| ORCA_RVO | Optimal Reciprocal Collision Avoidance (van den Berg et al., UNC Gamma) |  | secondary | 2011 | 2026-09-10 |  |  | overview page | available |
| PASSMARK_2026_09 | PassMark PerformanceTest V10 — CPU and GPU Benchmarks |  | hardware_benchmark | 2026-09-10 | 2026-09-10 |  |  | common_cpus / high_end_gpus / per-model pages | accessible |
| RESEARCH_S23_PACKAGING | Unreal Engine: Packaging Your Project |  | official_documentation | n/a | 2026-09-10 |  | Windows/Linux PC | sections: Build, Cook, Stage, Package; Chunking | available |
| RESEARCH_S24_HLOD | Unreal Engine: World Partition HLOD |  | official_documentation | n/a | 2026-09-10 |  | Windows/Linux PC | sections: HLOD layers and proxy mesh methods | available |
| RESEARCH_S25_PCG | Using PCG with World Partition |  | official_documentation | n/a | 2026-09-10 |  | Windows/Linux PC | sections: PCG Data Layers and HLOD Layers | available |
| RESEARCH_S27_RELEVANCY | Unreal Engine: Actor Relevancy |  | official_documentation | n/a | 2026-09-10 |  | Windows/Linux PC | sections: actor relevancy and distance | available |
| RESEARCH_S28_CRY_STREAMING | CRYENGINE: Streaming System |  | official_documentation | n/a | 2026-09-10 |  | Windows PC | sections: asynchronous reads, decompression and main-thread completion | available |
| RESEARCH_S29_CRY_AUDIO | CRYENGINE: Audio & Occlusion |  | official_documentation | n/a | 2026-09-10 |  | Windows PC | sections: No Ray, SingleRay, MultipleRay and distance limits | available |
| RESEARCH_S31_UNITY_JOB_OVERVIEW | Unity Manual: Job System Overview |  | official_documentation | n/a | 2026-09-10 |  | Windows/Linux PC | sections: worker threads, cores, work stealing and safety | available |
| RESEARCH_S33_ISO_25010 | ISO/IEC 25010:2023 Product Quality Model |  | standard | 2023 | 2026-09-10 | 2023 |  | product quality model and evaluation characteristics | available |
| RESEARCH_S34_ISO_20741 | ISO/IEC 20741:2017 Software Engineering Tool Evaluation |  | standard | 2017 | 2026-09-10 | 2017 |  | purpose-oriented tool selection and quality characteristics | available |
| RESEARCH_S35_PMI_PERT | Practice Standard for Scheduling - Second Edition |  | practice_standard | 2011 | 2026-09-10 |  |  | three-point estimating: triangular and beta/PERT formulas | available |
| RESEARCH_S36_NASA_SCHEDULE | Analytical Technique for Schedule Risk Assessment |  | technical_report | 1987 | 2026-09-10 |  |  | PERT/CPM precedence network and critical path sections | available |
| RESEARCH_S37_AMDAHL | Amdahl's Law & Parallel Speedup |  | conference_paper | 2000 | 2026-09-10 |  |  | serial/parallel speedup and overhead | available |
| RESEARCH_S38_D3D_FEATURE_LEVELS | Direct3D Hardware Feature Levels |  | official_documentation | n/a | 2026-09-10 |  | Windows PC | feature-level functionality versus performance | available |
| RESEARCH_S39_D3D_CHECK_FEATURE | ID3D12Device::CheckFeatureSupport |  | official_documentation | n/a | 2026-09-10 |  | Windows PC | syntax, remarks and ray-tracing capability query | available |
| RESEARCH_S40_D3D_RT_TIER | D3D12 Raytracing Tier |  | official_documentation | n/a | 2026-09-10 |  | Windows PC | ray-tracing tier capability | available |
| RESEARCH_S41_UE_SPECS | Hardware and Software Specifications for Unreal Engine |  | official_documentation | n/a | 2026-09-10 |  | Windows/Linux PC | editor requirements and rendering-path constraints | available |
| RESEARCH_S42_RIOT_SCALABILITY | VALORANT: Scalability and Load Testing |  | studio_engineering | 2020-12-15 | 2026-09-10 |  | server | sections: server scalability and 128-tick load test | available |
| RESEARCH_S43_HAMMER | Valve Hammer Editor / Source SDK |  | official_developer_resource | n/a | 2026-09-10 |  |  | branch-specific Hammer/Source SDK tooling | available |
| RESEARCH_S44_HEROENGINE_LEGACY | HeroEngine Legacy |  | studio_information | n/a | 2026-09-10 |  |  | legacy status and current applicability warning | available |
| RESEARCH_S45_HEROENGINE_VIDEOS | HeroEngine Legacy Platform Videos |  | studio_engineering | n/a | 2026-09-10 |  |  | historical live collaboration and integration examples | available |
| RESEARCH_S46_UNITY_JOB_DEPENDENCIES | Unity Job Dependencies |  | official_documentation | n/a | 2026-09-10 |  | Windows/Linux PC | job dependencies and synchronization | available |
| RESEARCH_S49_PASSMARK_SINGLE | PassMark CPU Single Thread Chart |  | benchmark | n/a | 2026-09-10 |  | Windows/Linux PC | single-thread comparison chart and notes | available |
| RESEARCH_S50_PASSMARK_FAQ | PassMark PerformanceTest FAQ |  | benchmark_methodology | n/a | 2026-09-10 |  | Windows/Linux PC | benchmark limits and workload caveat | available |
| RESEARCH_S51_3DMARK | UL 3DMark |  | benchmark | n/a | 2026-09-10 |  | Windows PC | GPU/CPU comparison and frame-rate context | available |
| RESEARCH_S53_QUIC_RFC | RFC 9000: QUIC |  | standard | 2021-05-01 | 2026-09-10 | RFC 9000 | Windows/Linux PC | packet format and transport assumptions | available |
| RESEARCH_S54_UE_TEXTURE_METRICS | Unreal Engine: Texture Streaming Metrics |  | official_documentation | n/a | 2026-09-10 |  | Windows/Linux PC | wanted mips, pool usage and streaming metrics | available |
| RESEARCH_S55_UE_TEXTURE_CONFIG | Unreal Engine: Texture Streaming Configuration |  | official_documentation | n/a | 2026-09-10 |  | Windows/Linux PC | pool sizing and update behavior | available |
| RESEARCH_S57_NASA_GLOSSARY | NASA PP&C Glossary: Critical Path and Double Counting |  | technical_guidance | n/a | 2026-09-10 |  |  | critical path, uncertainty and double-counting entries | available |
| RESEARCH_S58_UNITY_JOB_TROUBLESHOOTING | Unity Job System Troubleshooting |  | official_documentation | n/a | 2026-09-10 |  | Windows/Linux PC | WaitForJobGroup and Complete synchronization | available |
| RIOT_NETCODE | Peeking into VALORANT's Netcode |  | engineering_article | 2020-04-16 | 2026-09-10 |  |  | sections: peeker's advantage and simulation divergence | available |
| RIOT_TICK | Valorant 128-tick servers (Riot Engineering) |  | engineering_article | 2020-04-16 | 2026-09-10 |  |  | section: 128-tick servers | available |
| SAVE_PATTERNS | Save Systems & Persistence (Andrews Notebook) |  | secondary | n/a | 2026-09-10 |  |  | overview page | available |
| SHADOWGAMBIT_SAVE | Deep dive: save system of Shadow Gambit (GameDeveloper) |  | secondary | 2023-12-06 | 2026-09-10 |  |  | overview page | available |
| SRC-AIS-001 | The AI Systems of Left 4 Dead | Michael Booth, Valve (GDC 2009) | conference_talk | 2009 | 2026-09-10 | Source (Left 4 Dead) | PC/Xbox 360 | PDF p.64 (mob size/interval), p.65 (population categories), p.70 (75% behind), p.74 (boss events), p.78-82 (adaptive dramatic pacing), p.55-60 (AAS/flow distance/PVS), p.37-38 (Actor = Locomotion/Body/Vision/Intention) | verified_downloaded_text_extra |
| SRC-AIS-002 | Crowd Pathfinding and Steering Using Flow Field Tiles (Game AI Pro, Chapter 23) | Elijah Emerson; Game AI Pro (CRC Press) | book | 2013 | 2026-09-10 | Supreme Commander 2 engine (Gas Powered Games) | PC | pp.307-308 (intro/motivation), p.309 (integration field 24-bit, flow field 8-bit, 50-70% clear space, 10x10 sector grid), p.310 (merging A*), p.313 (flow field cache), p.314 (cost stamps, priority rebuild queue with fixed ms time slice) | verified_downloaded_text_extra |
| SRC-AIS-003 | Optimal Reciprocal Collision Avoidance (ORCA) | Jur van den Berg, Stephen J. Guy, Jamie Snape, Ming C. Lin, Dinesh Manocha, UNC Chapel Hill Gamma group | academic_paper | 2011 | 2026-09-10 | algorithm (no engine) | n/a | Description section: 'compute collision-free actions for all of them in only a few milliseconds'; 'several dense and complex simulation scenarios in both 2D and 3D workspaces involving thousands of agents' | verified |
| SRC-AIS-004 | RVO2 Library: Reciprocal Collision Avoidance for Real-Time Multi-Agent Simulation | UNC Chapel Hill Gamma group (maintained by Jamie Snape) | open_source | 2016-05-04 | 2026-09-10 | C++ library, Apache 2.0 (open sourced 2016) | cross-platform | News section: 'RVO2 Library has been licensed for the video game Warhammer 40,000: Space Marine from developer Relic'; Introduction: OpenMP parallelisation | verified |
| SRC-AIS-005 | Game Programming Patterns - Object Pool (Optimization Patterns) | Robert Nystrom | book | 2014 | 2026-09-10 | language-agnostic | n/a | Sections 'The Curse of Fragmentation', 'Free List', 'O(1) complexity'; caveats 'A pile of wasted memory', 'Unused objects remain in memory' | verified |
| SRC-AIS-006 | Game Programming Patterns - Component (Decoupling Patterns) | Robert Nystrom | book | 2014 | 2026-09-10 | language-agnostic | n/a | Intent 'Allow a single entity to span multiple domains without coupling the domains to each other'; caveats 'How do the components communicate?' and 'Ordering dependencies' | verified |
| SRC-AIS-007 | Gerstner wave (Trochoidal wave) | Wikipedia | secondary | accessed 2026-09-10 | 2026-09-10 | n/a | n/a | Section 'In computer graphics': multi-component parametric form; dispersion omega^2 = g*k*tanh(k*h); 'sharper crests and flat troughs'; cites Tessendorf 2001 | verified |
| SRC-AIS-008 | Rendering the Hellscape of Doom Eternal (Advances in Real-Time Rendering, SIGGRAPH 2020) | Jean Geffroy, Axel Gneiting, Yixin Wang (id Software) | conference_talk | 2020 | 2026-09-10 | id Tech 7 | PC/consoles | PDF p.54 (GORE SYSTEM: 'Separate mesh for each wound', 'Up to 12+ active wounds on 16 active enemies with multiple base materials'), p.53 (RESULTS: 'Up to 5ms GPU savings in dense scenes with triangle culling+merging'), p.56-61 (WATER RENDERING: Tessendorf 2001 displacement map, Johanson 2004 projec | verified_downloaded_text_extra |
| SRC-AIS-009 | Hair Rendering and Simulation in Unreal Engine | Epic Games (Unreal Engine 5.8 Documentation) | official_documentation | accessed 2026-09-10 | 2026-09-10 | Unreal Engine 5.8 | cross-platform | Intro: 'strand-based workflow ... simulate and render hundreds of thousands (or more) photo-real hairs in real-time'; 'Traditionally, hair created for use in real-time projects has been created using card-based techniques'; section list: Groom Strands, Setting Up Level of Detail for Grooms, Setting | verified |
| SRC-AIS-010 | Groom Scalability and Performance with Unreal Engine | Epic Games (Unreal Engine 5.8 Documentation) | official_documentation | accessed 2026-09-10 | 2026-09-10 | Unreal Engine 5.8 | cross-platform | Sections 'Geometry Scalability' (strands need 'an allocated performance budget and is not supported on all platforms'; cards as fallback), 'Strands Pipeline Overview' (Simulation/Interpolation/Voxelization/Primary Visibility/Lighting/Composition), 'Shadowing' (r.HairStrands.Voxelization.VoxelSizeInP | verified |
| SRC-AIS-011 | Recast Navigation (recastnav.com) | Mikko Mononen / Recast Navigation project | open_source | accessed 2026-09-10 | 2026-09-10 | Recast & Detour (C++98, ZLib license) | cross-platform | Sections: 'How it Works' (voxel rasterization -> walkable filtering -> regions -> re-triangulation); 'Recast/ Detour/ DetourTileCache/ DetourCrowd/'; 'Tiled meshes enable advance Detour features like re-baking, hierarchical path-planning, and navmesh data-streaming'; 'Recast powers AI navigation fea | verified |
| SRC-AIS-012 | RecastNavigation - Detour/Include/DetourNavMeshQuery.h (source) | recastnavigation (GitHub, main branch) | open_source | accessed 2026-09-10 | 2026-09-10 | Detour (main branch) | cross-platform | Lines 213-244: '@name Sliced Pathfinding Functions', initSlicedFindPath(), updateSlicedFindPath(const int maxIter, int* doneIters), finalizeSlicedFindPath(), finalizeSlicedFindPathPartial() | verified_source_fetched |
| SRC-AIS-013 | Godot Engine - Physics introduction | Godot Engine contributors | official_documentation | accessed 2026-09-10 | 2026-09-10 | Godot 4.7 | cross-platform | Section 'Collision layers and masks' (32 layers, collision_layer vs collision_mask, bitmask 0b1101 example); 'The physics engine runs at a fixed rate (a default of 60 iterations per second)'; '_physics_process() ... called before each physics step'; note '_integrate_forces() is not called when the r | verified |
| SRC-AIS-014 | Saving and Loading Your Game in Unreal Engine | Epic Games (Unreal Engine 5.8 Documentation) | official_documentation | accessed 2026-09-10 | 2026-09-10 | Unreal Engine 5.8 | cross-platform | Sections 'Asynchronous Saving' ('AsyncSaveGameToSlot is the recommended method ... prevents a sudden framerate hitch ... avoiding a possible certification issue on some platforms'), 'Synchronous Saving' ('SaveGameToSlot is sufficient for small SaveGame formats, and for saving the game while paused o | verified |
| SRC-AIS-015 | Significance Manager in Unreal Engine | Epic Games (Unreal Engine 5.8 Documentation) | official_documentation | accessed 2026-09-10 | 2026-09-10 | Unreal Engine 5.8 (plugin) | cross-platform | Intro ('The Significance Manager itself does not actually improve performance; rather, it provides a system that can be overridden'); 'running complex AI code less frequently'; 'grouping similar Actors together and enacting a per-Actor-type budget'; RegisterObject/UnregisterObject, GetSignificance/Q | verified |
| SRC-AIS-016 | MassEntity in Unreal Engine | Epic Games (Unreal Engine 5.8 Documentation) | official_documentation | accessed 2026-09-10 | 2026-09-10 | Unreal Engine 5.8 | cross-platform | 'MassEntity is a gameplay-focused framework for data-oriented calculations.'; child pages: Mass Avoidance ('force-based avoidance system integrated with MassEntity'), MassEntity Overview, MassGameplay Overview, Mass Debugger Overview, Simplified Mass Processor/Query API | verified_index_page_only |
| SRC-AIS-017 | Scalability and Best Practices for Niagara | Epic Games (Unreal Engine 5.8 Documentation) | official_documentation | accessed 2026-09-10 | 2026-09-10 | Unreal Engine 5.8 (Niagara) | cross-platform | Sections 'GPU vs CPU' ('Particle scripts have the largest opportunity for parallelization ... in most cases GPU sims are more performant'; 'a simulation of 1 particle can potentially take up the same resources as one with 64 particles'; 'on some platforms the GPU is the bottleneck'); 'Pooling: Memor | verified |
| SRC-AIS-018 | Massive Crowd on Assassin's Creed Unity: AI Recycling (GDC 2015) | Francois Cournoyer, Ubisoft (GDC Vault) | conference_talk | 2015 | 2026-09-10 | Ubisoft internal (AnvilNext) | PS4/Xbox One/PC | Session Overview: 'With the limit of 40 real AIs and 120 high resolution models, we could successfully create a scene where 10,000 crowd NPCs are on screen at the same time.'; 'pooling system that allowed us to swap from low-res NPCs to high-res NPCs without the player noticing' | verified |
| SRC-AIS-019 | The Art of Destruction in Rainbow Six: Siege (GDC 2016) | Julien L'Heureux, Ubisoft Montreal (GDC Vault PDF) | conference_talk | 2016 | 2026-09-10 | Ubisoft RealBlast / AnvilNext | PC/PS4/Xbox One | PDF p.3 (procedural vs pre-fragmented definition), p.15 ('First shipped destruction with AC IV: Black Flag'), p.29-32 (destruction model: hierarchical decomposition, connection-based leaf graph), p.58 ('Destruction Budgets': CPU 'Given roughly 6ms for a wall (2 procedural layers + pre-fragmented)', | verified_downloaded_text_extra |
| SRC-AIS-020 | Year summary (Voxagon Blog) - Teardown engine | Dennis Gustafsson, Tuxedo Labs / Voxagon | engineering_blog | 2024-12-29 | 2026-09-10 | Teardown engine (custom) / next-gen voxel engine | PC | Section 'Sparse voxel objects': 'Teardown uses a dense voxel format, where every shape stores voxel data in an uncompressed, regular 3D grid. This is very fast to access, but ... regions of empty space within an object take up the same amount of memory as regions that actually contain voxels. This r | verified |
| SRC-AIS-021 | Fix Your Timestep! | Glenn Fiedler, Gaffer on Games | secondary | 2004-06-10 | 2026-09-10 | language-agnostic | n/a | Sections 'Fixed delta time' (dt=1/60), 'Variable delta time', 'Semi-fixed timestep' ('spiral of death'), 'Free the physics' (accumulator, const double dt = 0.01), 'The final touch' (alpha = accumulator / dt; 'if (frameTime > 0.25) frameTime = 0.25;'; slerp for orientations) | verified |
| SRC-AIS-022 | Crest Ocean System (GitHub: wave-harmonic/crest) | Wave Harmonic (open source) | open_source | accessed 2026-09-10 | 2026-09-10 | Unity 2022.3.62f3+, shader target 4.5+ | PC/consoles (not OpenGL/WebGL) | README: 'An advanced water system implemented in Unity'; Crest Water 4/5; Requirements (Unity version, shader compilation target 4.5 or above, 'does not support OpenGL or WebGL backends'); Showcase list of shipped games (FAR: Changing Tides, Windbound, Wavetale, Critter Cove, Vertigo 2) | verified |
| SRC-AIS-023 | NVIDIA Blast (GitHub: NVIDIAGameWorks/Blast) | NVIDIA GameWorks | open_source | 2019-09-17 (last act | 2026-09-10 | Blast 1.1.5; UE4.19/UE4.20 plugin branches | PC (console support via developer.nvidia.com) | README: 'A modular destruction SDK designed for performance and flexibility, replacing APEX destruction.'; 'There is no physics or collision representation. There is no graphics representation.'; ExtAuthoring (Voronoi fracturing, hierarchical splitting); damage via 'user-supplied shader functions'; | verified |
| SRC-AIS-024 | Chaos Destruction in Unreal Engine | Epic Games (Unreal Engine 5.8 Documentation) | official_documentation | accessed 2026-09-10 | 2026-09-10 | Unreal Engine 5.8 (Chaos) | cross-platform | 'Chaos is Unreal Engine's high-performance physics and destruction system.'; child topics: Geometry Collections User Guide, Fracturing Geometry Collections, Cluster Geometry Collections, Chaos Fields User Guide, Dataflow for Destruction | verified |
| SRC-AIS-025 | Clothing Tool in Unreal Engine (Chaos Cloth) | Epic Games (Unreal Engine 5.8 Documentation) | official_documentation | accessed 2026-09-10 | 2026-09-10 | Unreal Engine 5.8 (Chaos Cloth solver) | cross-platform | 'Unreal Engine uses Chaos Cloth solver which is a low-level clothing solver responsible for the particle simulation that runs clothing.'; Masks section: 'Max Distance is the maximum distance any point on the cloth can move from its animated position', Backstop Distance/Radius, Anim Drive Multiplier | verified |
| SRC-AIS-026 | Chaos Vehicles (Unreal Engine) | Epic Games (Unreal Engine 5.8 Documentation) | official_documentation | accessed 2026-09-10 | 2026-09-10 | Unreal Engine 5.8 (Chaos Physics Solver) | cross-platform | 'Chaos Vehicles is Unreal Engine's lightweight system for performing vehicle physics simulations.'; child topics: How to Set up Vehicles, How to Convert PhysX Vehicles to Chaos, Vehicle Debug Commands, How to Build a Double Wishbone Suspension Vehicle, Vehicle Art Setup | verified |
| SRC-AIS-027 | PxBroadPhaseType - PhysX SDK Documentation | NVIDIA (PhysX SDK 5.6.1 API docs) | official_documentation | 2025-07-22 | 2026-09-10 | PhysX 5.6.1 | cross-platform | enum eSAP ('3-axes sweep-and-prune'), eMBP ('Multi box pruning'), eABP ('Automatic box pruning'), ePABP ('Parallel automatic box pruning'), eGPU ('GPU broad phase'); prose: eSAP 'great performance when many objects are sleeping. Performance can degrade significantly though, when all objects are movi | verified |
| SRC-AIS-028 | GPU Gems 3, Chapter 32: Broad-Phase Collision Detection with CUDA | Scott Le Grand, NVIDIA (GPU Gems 3) | book | 2007 | 2026-09-10 | CUDA / GeForce 8800 GTX | PC (GeForce 8800 GTX, 16 multiprocessors) | Results: '30,720 objects' -> broad phase prunes ~450,000,000 potential pairs down to ~203,000; ~79 fps; '~26x faster' than the contemporaneous CPU implementation; peak 487 fps at 3,072 objects; uniform grid spatial subdivision with 2^d=8 passes under Gauss-Seidel physics | verified |
| SRC-AIS-029 | Advanced Graphics Techniques Tutorial: Wakes, Explosions and Lighting - Interactive Water Simulation in 'Atlas' (GDC 2014) | Mark Mihelich (Studio Wildcard), Tim Tcheblokov (NVIDIA) - GDC Vault | conference_talk | 2014 | 2026-09-10 | Unreal-based 'Atlas' (Studio Wildcard) | PC | Session Overview: 'challenges ... during the implementation of simulation of water surfaces for Atlas, a new massive multiplayer online game by Studio WildCard ... including simulating and rendering ocean surfaces and the interactive effects ... as well as synchronizing multiple servers and players' | verified |
| SRC-AIS-030 | 'Overwatch' Gameplay Architecture and Netcode (GDC 2017) | Timothy Ford, Blizzard Entertainment (GDC Vault) | conference_talk | 2017 | 2026-09-10 | Blizzard in-house engine | PC/PS4/Xbox One | Session Overview: 'Overwatch uses a cutting-edge Entity Component System (ECS) architecture ... Blizzard's team leverages ECS to curtail complexity, even as they continue to add new crazy features.' | verified |
| SRC-AIS-031 | Crowds in Hitman: Absolution (GDC Vault) | Kasper Fauerby, IO Interactive | conference_talk | 2012 | 2026-09-10 | IO Interactive Glacier 2 | PS3/Xbox 360/PC | Session Overview: 'the techniques and optimizations used to achieve the 1200 character crowds present in Hitman: Absolution while still running at 30fps on current-gen consoles' | verified |
| SRC-AIS-032 | Godot Engine - Saving games | Godot Engine contributors | official_documentation | accessed 2026-09-10 | 2026-09-10 | Godot 4.x | cross-platform | Sections 'Identifying persistent objects' (Persist group), 'Serializing' (JSON.stringify, store_line per object), 'Loading and saving games', caveats: JSON cannot parse 'Vector2, Vector3, Color, Rect2, and Quaternion'; binary serialization 'Only properties that have the PROPERTY_USAGE_STORAGE flag s | verified |
| SRC-AIS-033 | Unity Manual - Cloth | Unity Technologies | official_documentation | accessed 2026-09-10 | 2026-09-10 | Unity 6.0 (6000.0) | cross-platform | Page resolves to the Unity Manual shell; the article body was NOT extracted (OneTrust cookie-consent interstitial). No content claim is made from this source. | available_partial_cookie_wall |
| SRC-AIS-034 | Unity Manual - Wheel collider component reference | Unity Technologies | official_documentation | accessed 2026-09-10 | 2026-09-10 | Unity 6.6 | cross-platform | Page resolves to the Unity Manual shell; body NOT extracted (cookie-consent interstitial). No content claim is made from this source. | available_partial_cookie_wall |
| SRC-AIS-035 | Unity Manual - Write multithreaded code with the job system | Unity Technologies | official_documentation | accessed 2026-09-10 | 2026-09-10 | Unity 6.6 | cross-platform | Page resolves; only navigation chrome was returned by automated fetch (content is client-rendered). No content claim is made from this source. | available_partial_client_rende |
| SRC-AIS-036 | AMD and Crystal Dynamics Collaboration ... With the Launch of 'Tomb Raider' (press release) | Advanced Micro Devices (AMD Investor Relations) | vendor_press_release | 2013-03-05 | 2026-09-10 | AMD TressFX Hair, DirectX 11 | PC (AMD Radeon HD 7000 series) | 'TressFX Hair, the world's first in-game implementation of a real-time, per-strand hair physics system'; 'imparts one of the most iconic video game characters, Lara Croft' | verified |
| SRC-AIS-037 | Soft-body Physics - BeamNG.drive | BeamNG GmbH | official_documentation | accessed 2026-09-10 | 2026-09-10 | BeamNG custom soft-body engine | PC | Sections 'Node-Beam Structure' (nodes have mass; beams are springs with no mass; 'In BeamNG, there is no angular friction holding any of these Beams at a certain angle'); 'Beam Spring and Damp Values' (typical values: suspension springs beamSpring 40000 / beamDamp 0; structural components 8000000/12 | verified |
| SRC-AIS-038 | DOTS - Unity's Data-Oriented Technology Stack | Unity Technologies | vendor_press_release | accessed 2026-09-10 | 2026-09-10 | Unity 6 / ECS for Unity, Burst, C# Job System | cross-platform | 'DOTS in Production' section: Stunlock Studios used ECS throughout development of V Rising; Door 407 (Diplomacy is Not an Option): 'We're using DOTS almost everywhere in our game, and we're finding it especially useful for pathfinding and optimizing our gameplay logic'; Kasedo Games used ECS 'to pow | verified |
| SRC-AIS-039 | Unity Manual - Introduction to GPU instancing | Unity Technologies | official_documentation | accessed 2026-09-10 | 2026-09-10 | Unity 6.6 | cross-platform | Page resolves to the Unity Manual shell; body NOT extracted (cookie-consent interstitial). No content claim is made from this source. | available_partial_cookie_wall |
| SRC-AIS-040 | Godot Engine - RigidBody3D class reference | Godot Engine contributors | official_documentation | 2026 (stable / 4.x) | 2026-09-10 | Godot 4.x | cross-platform | Properties 'can_sleep' ('If true, the body can enter sleep mode when there is no movement.'), 'sleeping' ('If true, the body will not move and will not calculate forces until woken up by another body through, for example, a collision, or by using the apply_impulse() or apply_force() methods.'), sign | verified |
| SRC-AIS-041 | Physics in Unreal Engine (Chaos Physics overview) | Epic Games | official_documentation | 2026 (UE 5.8 docs) | 2026-09-10 | Unreal Engine 5.x (Chaos) | cross-platform | Section 'Rigid Body Dynamics' ('Chaos Physics provides many features for rigid-body dynamics. This includes collision responses, physics constraints, and damping and friction. In addition, it provides asynchronous physics simulation and networked physics.'); section 'Destruction' cache paragraph ('T | verified |
| SRC-AIS-042 | Water System in Unreal Engine | Epic Games | official_documentation | 2026 (UE 5.8 docs) | 2026-09-10 | Unreal Engine 5.x (Water plugin) | cross-platform | Intro ('The Water system unifies the shading and mesh rendering pipeline, with surfaces that support physics interactions and fluid simulation with gameplay, such as ripples caused by footsteps or the wake behind a boat moving through the water.'); 'The Water system is a self-contained plugin that c | verified |
| SRC-AIS-043 | AMD TressFX (GitHub: GPUOpen-Effects/TressFX) | AMD (GPUOpen) | open_source | 2019-2020 (TressFX 4 | 2026-09-10 | TressFX 4.1; DirectX 12 / Vulkan; Unreal Engine 4.22 integration branch | Windows; AMD GCN/RDNA or any SM6-capable DX12/Vulkan GPU | README 'New in TressFX 4.1' bullet list: 'Optimized physics simulation shaders allowing more hair to be simulated in real-time', 'faster Velocity Shock Propagation, simplified Local Shape Constraints, a reorganization of dispatches', 'New Level of Detail (LOD) system'; also 'Prerequisites' (AMD GCN | verified |
| SRC-AIS-044 | Godot Engine - VehicleBody3D class reference | Godot Engine contributors | official_documentation | 2026 (stable / 4.x) | 2026-09-10 | Godot 4.x | cross-platform | Description: 'It is based on the raycast vehicle system commonly found in physics engines.'; 'you must also add a VehicleWheel3D node for each wheel'; 'This class has known issues and isn't designed to provide realistic 3D vehicle physics. If you want advanced vehicle physics, you may have to write | verified |
| SRC-AIS-045 | Godot Engine - GPUParticles3D class reference | Godot Engine contributors | official_documentation | 2026 (stable / 4.x) | 2026-09-10 | Godot 4.x | cross-platform | Property 'amount' ('Higher values will increase GPU requirements, even if not all particles are visible at a given time or if amount_ratio is decreased.'); property 'amount_ratio' ('Reducing the amount_ratio has no performance benefit, since resources need to be allocated and processed for the total | verified |
| SRC-AIS-046 | Physics Sub-Stepping in Unreal Engine | Epic Games | official_documentation | 2026 (UE 5.8 docs) | 2026-09-10 | Unreal Engine 5.x (Chaos) | cross-platform (explicitly not mobile) | Intro ('By using physics Sub-stepping you can get physics simulations that are more accurate and stable, however, this comes at the expense of performance.'); 'Max Substep Delta Time' worked example (0.05 s full step with 0.025 s max substep = 2 sub-steps; 'Max Physics Delta Time limits how long a p | verified |
| SRC-AIS-047 | Niagara Flipbook Baker Quick Start Guide in Unreal Engine | Epic Games | official_documentation | 2026 (UE 5.8 docs) | 2026-09-10 | Unreal Engine 5.x (Niagara) | cross-platform | Intro ('At times, you may create a nice effect, but find it takes up too much memory to use on a target device. One solution to this is to bake out the Niagara simulation to a flipbook. This creates a tiled image that can then be loaded onto any material.'); motivation ('This way, you have very effi | verified |
| SRC-CHC-001 | Animation Budget Allocator (Unreal Engine 5.8 Documentation) | Epic Games / Epic Developer Community | secondary | 2026 (UE 5.8 page, v | 2026-09-10 | Unreal Engine 5.8 | PC (Windows), consoles | Sections: '# Animation Budget Allocator', '#### Prerequisites', '## Set Up the Animation Budget Allocator', '## Using the Animation Budget Allocator' (stat list: Initial Tick, Demand, Num Ticked Components, Throttled, Budget, Interpolated, SmoothedBudgetPressure, Always Tick, Num Registered Componen | verified |
| SRC-CHC-002 | Animation Optimization in Unreal Engine (Unreal Engine 5.8 Documentation) | Epic Games / Epic Developer Community | secondary | 2026 (UE 5.8 page, v | 2026-09-10 | Unreal Engine 5.8 | PC (Windows), consoles | Sections: '# Animation Optimization', '## Overview', '## Using Multi-Threaded Animation Updates', '## Animation Fast Path', '## Animation Optimization Tools', '## General Tips' -> Update Rate Optimizations (URO) bullet, '### Other Considerations' | verified |
| SRC-CHC-003 | Skeletal Mesh LODs in Unreal Engine (Unreal Engine 5.8 Documentation) | Epic Games / Epic Developer Community | secondary | 2026 (UE 5.8 page, v | 2026-09-10 | Unreal Engine 5.8 | PC (Windows), consoles | Sections: '# Skeletal Mesh LODs', '## Creating LODs', '## Reducing Bones', '## Console Commands', '## Properties Reference' -> '### LOD Info' (Bones to Remove, Bake Bose, Bake Pose Override, LOD Hysteresis), '### Skeletal Mesh Reduction Tool' (Max Bone Influence, Enforce Bone Boundaries, Merge Coinc | verified |
| SRC-CHC-004 | Animation Compression Library (acl) - repository README | Nicholas Frechette / ACL contributors | secondary | 2025 (README last up | 2026-09-10 | ACL 2.1.0 (header-only C++11); UE plugin shipped since UE 5.13 per README | Windows VS2022 x86/x64/ARM64/ARM64EC, Linux GCC12+/Clang15+, macOS XCode15+ ARM64, WASM, iOS/Android | Sections: '# Animation Compression Library', '## Goals', '## Philosophy', '## Supported platforms', '## Getting started', '## Performance metrics' (links to cmu_performance.md, paragon_performance.md, fight_scene_performance.md, decompression_performance.md) | verified |
| SRC-CHC-005 | ACL - Paragon database performance | Nicholas Frechette | secondary | 2017-2021 (ACL v1.3. | 2026-09-10 | ACL v2.1.0 / v2.0.0 / v1.3.0 | Ryzen 2950X (v1.3.0+), Intel i7 6850K (earlier) | '# Paragon database performance' results table (v2.1.0 column) and '# Data and method used' -> 'Number of clips: 6558', 'Total duration: 7h 0m 45.27s', 'Raw size: 4276.11 MB', error measured 3cm from each bone, default error threshold 0.01cm | verified |
| SRC-CHC-006 | ACL - Carnegie-Mellon University database performance | Nicholas Frechette | secondary | 2017-2021 (ACL v1.3. | 2026-09-10 | ACL v2.1.0 / v2.0.0 / v1.3.0 | Ryzen 2950X (v1.3.0+) | '# Carnegie-Mellon University database performance' results table and '# Data and method used' -> 'Number of clips: 2534', 'Sample rate: 24 FPS', 'Total duration: 9h 49m 37.58s', 'Raw size: 1429.38 MB' | verified |
| SRC-CHC-007 | ACL - Decompression performance | Nicholas Frechette | secondary | 2021 (ACL v2.1.0) | 2026-09-10 | ACL 2.1.0, acl_decompressor tool | Ryzen 2950X @ 3.5 GHz; Android Pixel 7 @ 2.85 GHz; iPad Pro 10.5in @ 2.39 GHz | '# Decompression performance' -> '## Uniformly sampled algorithm' -> median decompress_pose with cold CPU cache table (104_30 / Trooper_1 / Trooper_Main, forward/backward/random on iPad) | verified |
| SRC-CHC-008 | Animation Compression Library in Unreal Engine (Unreal Engine 5.8 Documentation) | Epic Games / Epic Developer Community | secondary | 2026 (UE 5.8 page, v | 2026-09-10 | Unreal Engine 5.8, Animation Compression Library plugin | PC (Windows), consoles | Sections: plugin enable path, 'Anim Compress ACL' / 'Anim Compress Custom ACL' / 'Anim Compress ACL Database' codec descriptions, 'Error Threshold' (0.01cm default), 'Default Virtual Vertex Distance' (3cm), 'Safe Virtual Vertex Distance', Compression level ('five available levels'), 'Highest/Medium/ | verified |
| SRC-CHC-009 | Animation Compression Codec Reference in Unreal Engine (Unreal Engine 5.8 Documentation) | Epic Games / Epic Developer Community | secondary | 2026 (UE 5.8 page, v | 2026-09-10 | Unreal Engine 5.8 | PC (Windows), consoles | Sections: '# Animation Compression Codec Reference', '### Bone Compression Codec Reference' (Bitwise Compress Only, Least Destructive, Per Track Compression, Removes Every Second Key, Remove Linear Keys, Removes Trivial Keys), '### Bitwise Compression Format Reference' (ACF None, ACF Float 96No W, A | verified |
| SRC-CHC-010 | Motion Matching in Unreal Engine (Unreal Engine 5.8 Documentation) | Epic Games / Epic Developer Community | secondary | 2026 (UE 5.8 page, v | 2026-09-10 | Unreal Engine 5.8, Pose Search plugin | PC (Windows), consoles | Sections: '# Motion Matching', '## Motion Matching Setup', '### Create a Pose Search Schema Asset', '### Channels', '### Create a Pose Search Database Asset', '### Motion Matching Node' (Blend Time, Pose Jump Threshold Time, Pose Reselect History, Search Throttle Time, Max Active Blends, Store Blend | verified |
| SRC-CHC-011 | Motion Matching and The Road to Next-Gen Animation (GDC 2016 slides) | Simon Clavet, Ubisoft Montreal (GDC 2016) | secondary | 2016 | 2026-09-10 | Ubisoft in-house animation system (For Honor era) | PC / consoles | Slides: 39-41 ('Introducing Motion Matching', 'A ridiculously brute-force approach', 'Algorithm: Every frame, look at all mocap and jump at the best place'), 51-52 ('Trick 1: Posematch only a few bones', 'Precompute and save with the animation'), 55-57 ('Trick 2', 'Trajectory Matching'), 62 ('Optimi | verified |
| SRC-CHC-012 | Learned Motion Matching (project page + abstract) | Daniel Holden (theorangeduck.com) | secondary | 2020-08-01 | 2026-09-10 | Research prototype; reference implementation at github.com/orangeduck/Motion-Mat | PC | Page body paragraph ('training three specialized neural networks to replace three specific components'... 'does not rely on keeping any animation data in memory') and verbatim Abstract | verified |
| SRC-CHC-013 | Learned motion matching, ACM Transactions on Graphics 39(4) | Daniel Holden, Oussama Kanoun, Maksym Perepichka, Tiberiu Popa (Ubisoft La Forge / Concordia University) | secondary | 2020-08-12 | 2026-09-10 | n/a (research) | n/a | Abstract; ACM DL landing page. Full text was behind ACM's paywall at verification time - only the abstract could be read. | unverified |
| SRC-CHC-014 | Skeletal Mesh Rendering Paths in Unreal Engine (Unreal Engine 5.8 Documentation) | Epic Games / Epic Developer Community | secondary | 2026 (UE 5.8 page, v | 2026-09-10 | Unreal Engine 5.8 | PC (Windows), consoles, mobile | Sections: '# Skeletal Mesh Rendering Paths', '## How Skeletal Meshes are Rendered', '### 8-bit and 16-bit Bone Indexes', '### Max Bones Per Section', '## GPU Skinned Vertex Factory', '### Unlimited Bone Influence Mode', '## Skin Cache System', '### Recompute Tangents', '## Deformer Graph Plugin' | verified |
| SRC-CHC-015 | GPU Gems, Chapter 4: Animation in the 'Dawn' Demo | Curtis Beeson, Kevin Bjorke / NVIDIA (GPU Gems, Addison-Wesley) | secondary | 2004 | 2026-09-10 | Cg / HLSL vertex shaders (GeForce FX era) | PC (Windows), DirectX 9-class GPU | Sections: '## 4.4 Skinning', '#### 4.3.2 Morph Target Implementation', '#### 4.4.1 Accumulated Matrix Skinning' | verified |
| SRC-CHC-016 | ozz-animation - open source C++ 3D skeletal animation library (documentation, Overview) | Guillaume Blanchet | secondary | 2026 (site last upda | 2026-09-10 | ozz-animation (MIT), renderer-agnostic | PC (Windows/Linux), consoles | Sections: '# What ozz-animation is', '# What it's not', '# License' | verified |
| SRC-CHC-017 | Blender Manual - Render Baking (Cycles) | Blender Foundation / blender.org | secondary | 2026 (Blender 5.2 LT | 2026-09-10 | Blender 5.2 LTS, Cycles | PC (Windows/Linux/macOS) | Sections: '# Render Baking', '## Setup', '## Settings' -> 'Bake Type', '### Influence' -> 'Normal' -> 'Space' (Object/Tangent) and 'Swizzle R, G, B', '### Selected to Active' -> 'Cage', 'Cage Object', 'Cage Extrusion', 'Max Ray Distance', '### Output', '### Margin' -> 'Type' (Extend / Adjacent Faces | verified |
| SRC-CHC-018 | MikkTSpace - a common standard for tangent space used in baking tools | Morten S. Mikkelsen (mmikk) | secondary | 2020 (repo, last com | 2026-09-10 | n/a (tangent-space generation algorithm; used by xNormal, Blender, Substance, gl | any | README.md: 'A common standard for tangent space used in baking tools to produce normal maps. More information can be found at http://www.mikktspace.com/' | verified |
| SRC-CHC-019 | Block Compression (Direct3D 10) - Microsoft Learn | Microsoft | secondary | 2019 (page, verified | 2026-09-10 | Direct3D 10/11, BC1-BC5 | PC (Windows) | Sections: block-size statements, 'Compression Algorithms' table, 'BC1' (48 bytes -> 8 bytes per 4x4 block), 'BC2' and 'BC3' (64 -> 16 bytes), 'BC4' (16 -> 8 bytes, 'a 50-percent memory savings'), 'BC5' (32 -> 16 bytes), general statement 'up to 75 percent smaller' | verified |
| SRC-CHC-020 | Basis Universal GPU Texture Codec (repository README) | Binomial LLC | secondary | 2025-2026 (README fo | 2026-09-10 | Basis Universal v2.5, .basis / .KTX2 / .DDS | PC (Windows), consoles, mobile, WASM | Sections: intro ('.KTX2 ... rapid transcoding'), 'Supported LDR GPU Texture Formats' / 'Supported HDR GPU Texture Formats' lists, ETC1S mode ('roughly .3-3bpp'), UASTC LDR 4x4 ('An 8 bits/pixel LDR high quality mode'), ASTC HDR 6x6 ('3.56 bits/pixel'), XUASTC LDR ('1.15-3.5 bpp (typical ~2.25 bpp)' | verified |
| SRC-CHC-021 | Unity Manual - Sprite Atlas (class-SpriteAtlas) | Unity Technologies | secondary | 2019 (Unity 2019.4 m | 2026-09-10 | Unity 2019.4 | PC (Windows), consoles, mobile | Intro paragraph: 'A Sprite Atlas is an Asset that consolidates several Textures into a single combined Texture. Unity can call this single texture to issue a single draw call instead of multiple draw calls...' | unverified |
| SRC-CHC-022 | Unity Manual - Sprite Atlas reference | Unity Technologies | secondary | 2026 (Unity 6000.2 m | 2026-09-10 | Unity 6.2 (6000.2) | PC (Windows), consoles, mobile | 'Allow Rotation' property description: 'Check this box to allow the Sprites to rotate when Unity packs them into the Sprite Atlas. This maximizes the density...' | unverified |
| SRC-CHC-023 | Unity Manual - Sprite Atlas workflow | Unity Technologies | secondary | 2022 (Unity 2022.1 m | 2026-09-10 | Unity 2022.1 | PC (Windows), consoles, mobile | 'Include in Build' paragraph: 'Enable or disable the Include in Build property to control which Sprite Atlases are included in the Project build.' | unverified |
| SRC-CHC-024 | Unity Manual - Tilemap Renderer component reference | Unity Technologies | secondary | 2026 (Unity 6000.5 m | 2026-09-10 | Unity 6.5 | PC (Windows), consoles, mobile | 'Mode' property description: 'Chunk: Renders multiple tiles together in single batches. This approach increases performance and ensures tiles sort correctly, but...' | unverified |
| SRC-CHC-025 | Unity Manual - Tilemap Renderer | Unity Technologies | secondary | 2024 (docs.unity.cn | 2026-09-10 | Unity 2022.3 | PC (Windows), consoles, mobile | 'Detect Chunk Culling Bounds' / 'Chunk Culling Bounds' description: 'Determines how the Render detects the bounds used for the culling of Tilemap chunks. These bounds expand the...' | unverified |
| SRC-CHC-026 | Tiled Documentation - JSON Map Format reference | Thorbjorn Lindeijer / mapeditor.org | secondary | 2026 (Tiled 1.12.2 d | 2026-09-10 | Tiled 1.12.2 JSON format | any (editor + data format) | Sections: 'Layer' field table rows for 'chunks', 'compression' (zlib, gzip, zstd since 1.3 or empty), 'data', 'encoding' (csv default or base64), 'startx'/'starty'; 'Chunk' field table (data, height, width, x, y); 'Chunk Example'; 'Map' row 'compressionlevel' (defaults to -1) | verified |
| SRC-CHC-027 | Tiled Documentation - Using Infinite Maps | Thorbjorn Lindeijer / mapeditor.org | secondary | 2026 (Tiled 1.12.2 d | 2026-09-10 | Tiled 1.12.2 | any | Sections: '# Using Infinite Maps', '## Creating an Infinite Map', '## Editing an Infinite Map', '## Converting Between Infinite And Fixed-Size Maps' | verified |
| SRC-CHC-028 | Spine User Guide - Mesh attachments | Esoteric Software | secondary | 2026 (user guide, ve | 2026-09-10 | Spine (Editor + Runtimes) | PC, mobile, web | Sections: 'Mesh attachments' intro and 'Setup', 'Deformation', 'Edges', 'Transform tools', 'Hull size' -> 'Hull edges' / 'Holes', 'Vertex count', 'Linked meshes' | verified |
| SRC-CHC-029 | Spine User Guide - Metrics view | Esoteric Software | secondary | 2026 (user guide, ve | 2026-09-10 | Spine (Editor + Runtimes) | PC, mobile, web | Sections: '# Metrics view', '## Bones' (Nexus 4 ~2000 bones at 60fps note), '## Vertex transforms', '## Performance' -> '## CPU usage', '## Fill rate' (hull / transparent pixels), '## Draw calls' (atlas reduces texture switches) | verified |
| SRC-CHC-030 | Unity 2D Animation package - Skinning Editor | Unity Technologies | secondary | 2023 (2D Animation 7 | 2026-09-10 | com.unity.2d.animation 7.0 | PC (Windows), consoles, mobile | Sections: '# Skinning Editor' (intro: 'create the bones of your actor's skeleton, generate and edit its mesh geometry, and adjust the weights that bind the bones to the meshes'), '## Opening the Skinning Editor', '## How to select a Sprite in the editor' | verified |
| SRC-CHC-031 | Unity 2D Animation package - Actor skinning and weighting workflow | Unity Technologies | secondary | 2023 (2D Animation 7 | 2026-09-10 | com.unity.2d.animation 7.0 | PC (Windows), consoles, mobile | Workflow steps 1-7, in particular step 2 (Auto Geometry), step 4 ('The Auto Weights tool only generates weights for Sprites that have both a geometry Mesh, and bones intersecting their Mesh'), step 6 (Bone Influence panel Add/Remove) | verified |
| SRC-CHC-032 | Gameplay Ability System for Unreal Engine (Unreal Engine 5.8 Documentation) | Epic Games / Epic Developer Community | secondary | 2026 (UE 5.8 page, v | 2026-09-10 | Unreal Engine 5.8, GameplayAbilities plugin | PC (Windows), consoles | Sections: '# Gameplay Ability System' ('a framework for building attributes, abilities, and interactions that an Actor can own and trigger'), bullet list (Ability System Component, Gameplay Abilities, Attributes and Attribute Sets, Gameplay Effects, Ability Tasks), '## Valley of the Ancient Sample' | verified |
| SRC-CHC-033 | Understanding the Unreal Engine Gameplay Ability System (Unreal Engine 5.8 Documentation) | Epic Games / Epic Developer Community | secondary | 2026 (UE 5.8 page, v | 2026-09-10 | Unreal Engine 5.8 | PC (Windows), consoles | Sections: '# Gameplay Ability System Overview', '## Components of the Gameplay Ability System', '### Tracking Ownership', '#### Controlling Activation' ('four main methods'), '### Handling Cosmetic Effects' (Gameplay Cues, 'do not use reliable replication'), '## Supporting Network Multiplayer' -> '# | verified |
| SRC-CHC-034 | Gameplay Ability Tasks in Unreal Engine (Unreal Engine 5.8 Documentation) | Epic Games / Epic Developer Community | secondary | 2026 (UE 5.8 page, v | 2026-09-10 | Unreal Engine 5.8, UAbilityTask | PC (Windows), consoles | '# Ability Tasks' body: async work, EndTask, 'prevents phantom Ability Tasks from running, effectively leaking CPU cycles and memory', 'guaranteed to end, at latest, when the main Ability ends', networking paragraph | verified |
| SRC-CHC-035 | Gameplay Ability System Component and Gameplay Attributes in Unreal Engine | Epic Games / Epic Developer Community | secondary | 2026 (UE 5.8 page, v | 2026-09-10 | Unreal Engine 5.8 | PC (Windows), consoles | Intro: the Ability System Component (UAbilitySystemComponent) is the bridge between an Actor and the Gameplay Ability System | unverified |
| SRC-CHC-036 | Scalability and Best Practices for Niagara (Unreal Engine 5.8 Documentation) | Epic Games / Epic Developer Community | secondary | 2026 (UE 5.8 page, v | 2026-09-10 | Unreal Engine 5.8, Niagara | PC (Windows), consoles, mobile | Sections: '# Scalability and Best Practices', '## Instance Counts', '### Scalability and Effect Types', '### System as a Service', '## Emitter Counts' ('a simulation of 1 particle can potentially take up the same resources as one with 64 particles'), '#### Spawn Index' (Fortnite contrails example), | verified |
| SRC-CHC-037 | Optimizing Niagara (Unreal Engine 5.8 Documentation) | Epic Games / Epic Developer Community | secondary | 2026 (UE 5.8 page, v | 2026-09-10 | Unreal Engine 5.8, Niagara | PC (Windows), consoles | '# Optimizing Niagara' hub page and its three child links: Measuring Performance, Scalability and Best Practices, Systems as a Service ('two different approaches used by the Lyra project to dynamically spawn weapon impacts into Niagara systems') | verified |
| SRC-CHC-038 | Niagara Systems as a Service (Unreal Engine 5.8 Documentation) | Epic Games / Epic Developer Community | secondary | 2026 (UE 5.8 page, v | 2026-09-10 | Unreal Engine 5.8, Niagara | PC (Windows), consoles | Sections: '# Systems as a Service' -> 'Overview' (one-to-one vs many-to-one, activation and instance-count cost, array-based trade-off, Niagara Data Channels and the Islands Data Channel, Lyra as both example cases), '## User Parameter SaaS' (tracers still array-based), '## Lyra Impacts from Arrays' | verified |
| SRC-CHC-039 | 3D Toon Rendering in 'Hi-Fi RUSH' (GDC 2024 session) | Kosuke Tanaka, Takashi Komada, Tango Gameworks (GDC 2024, Visual Arts track) | secondary | 2024 | 2026-09-10 | Customized Unreal Engine 4 | PC (Windows), Xbox | Session overview text: '60fps rhythm action game rendered in a stylish 3D toon art style using a customized Unreal Engine 4', 'toon shading for the entire world, both character and environment ... all at 60fps at native resolution', 'deferred toon renderer ... Comic shaders, toon lights, dynamic sha | verified |
| SRC-CHC-040 | Illustrative Rendering in Team Fortress 2 (NPAR 2007) | Jason Mitchell, Moby Francke, Dhabih Eng (Valve) | secondary | 2007-08-04 | 2026-09-10 | Source engine | PC (Windows), Xbox 360, PS3 | Page 1: Abstract ('a set of artistic choices and novel real-time shading techniques which support each other'), '1 Introduction' ('Grounded in the conventions of early 20th century commercial illustration with 1960s industrial design elements ... the result of close collaboration between artists and | verified |
| SRC-CHC-041 | Rayman Legends: The Design Process Within the UbiArt Framework (GDC 2014 session) | Chris McEntee, Ubisoft Montpellier (GDC 2014, Visual Arts track) | secondary | 2014 | 2026-09-10 | UbiArt Framework (Ubisoft in-house 2D engine) | PC, Wii U, PS3, Xbox 360, PS Vita | Session overview text: 'an engine originally developed for the game's predecessor, Rayman Origins', 'The engine's role in improving prototyping and level design pre-production processes will be demonstrated through case studies' | verified |
| SRC-CHC-042 | Game Engine Architecture, 4th Edition (two-volume set) | Jason Gregory (CRC Press / Routledge) | book | 2025 (4th edition) | 2026-09-10 | n/a | n/a | Publisher/author landing page: 'New to the Fourth Edition' -> 'motion matching animation techniques'; 'Topics Include' -> 'engine subsystems including ... character animation', 'tools pipelines and the game asset database' | verified |
| SRC-CHC-043 | Game Programming Patterns | Robert Nystrom | secondary | 2014 (1st edition, c | 2026-09-10 | n/a | n/a | Table of contents: '11. Bytecode', '12. Subclass Sandbox', '13. Type Object', '14. Component', '15. Event Queue', '17. Data Locality', '19. Object Pool' | verified |
| SRC-CHC-044 | Unity Manual - Animation tab (AnimationClip import settings) | Unity Technologies | secondary | 2020 (Unity 2020.1 m | 2026-09-10 | Unity 2020.1 | PC (Windows), consoles, mobile | 'Anim. Compression' -> 'Off' description: 'This means that Unity doesn't reduce keyframe count on import, which leads to the highest precision animations' | unverified |
| SRC-CHC-045 | Unity Manual - Recommended, default, and supported texture compression formats, by platform | Unity Technologies | secondary | 2023 (Unity 2023.3 m | 2026-09-10 | Unity 2023.3 | PC (Windows), consoles, mobile | Statement: 'For devices with DirectX 11 or better class GPUs, where support for BC7 and BC6H formats is guaranteed to be...' | unverified |
| SRC-CHC-046 | Cuphead - A Game \| Made with Unity (Unity customer story) | Unity Technologies (with StudioMDHR quotes) | secondary | 2026 (page, verified | 2026-09-10 | Unity (2D toolset: Sprite Renderer, Sprite Packer, 2D Physics) | PC (Windows), Xbox One | Sections: '# Cuphead', '## They bet everything on a game', '## What happens when Betty Boop meets the Gunstar Heroes?', '## 50,000 frames of amazing hand-drawn animation' ('StudioMDHR then sets the animation at 24 frames-per-second ... while the game runs at a sparkling 60 frames-per-second', 'Unity | verified |
| SRC-DER-001 | Steam Hardware & Software Survey | Valve Corporation | official_documentation | 2026-08 | 2026-09-10 | n/a (client telemetry) | Windows PC / Linux PC / macOS | sections 'Operating System Version' (Windows 11 64 bit 70.97%, Windows 10 64 bit 22.90%, Windows 93.95%), 'System RAM' (16 GB 41.20%, 32 GB 37.45%, 8 GB 7.46%), 'Video Memory (VRAM)' (16 GB 26.92%, 8 GB 25.74%), 'Primary Display Resolution' (1920x1080 50.52%, 2560x1440 21.86%, 3840x2160 4.98%) | verified_fetched |
| SRC-DER-002 | Steam Hardware & Software Survey - PC Video Card Usage Details | Valve Corporation | official_documentation | 2026-08 | 2026-09-10 | n/a (client telemetry) | Windows PC / Linux PC | section 'PC VIDEO CARD USAGE DETAILS -> OVERALL DISTRIBUTION OF CARDS': 'DirectX 12 GPUs' AUG = 91.45% (+0.08%), 'DirectX 11 GPUs' = 0.41%, 'DirectX 10 GPUs' = 0.21%, 'DirectX 8 GPUs and below' = 7.46%; section 'ALL VIDEO CARDS': 'NVIDIA GeForce RTX 3060' AUG = 3.92% | verified_fetched |
| SRC-DER-003 | Source Multiplayer Networking | Valve Developer Community | official_documentation | n.d. (wiki with roll | 2026-09-10 | Source 1 / Source 2 (CS:GO, CS2, TF2, L4D2) | Windows PC / Linux PC | sections 'Tickrate' (default timestep 15ms = 66.666 ticks/s; minimum tickrate 11; CS:GO 64 official / 128 community; CS2 hardcoded 64; TF2/CSS 66; L4D/L4D2 30; CS 1.6/HL1 60), 'Snapshot rate' (cl_updaterate default 20 -> ~50 ms), 'Command rate' (cl_cmdrate ~30), 'Interpolation' (cl_interp 0.1 = 100 | verified_fetched |
| SRC-DER-004 | What Every Programmer Needs To Know About Game Networking | Glenn Fiedler (Gaffer On Games) | engineering_blog | 2010-02-24 | 2026-09-10 | engine-agnostic | cross-platform | sections 'Peer-to-Peer Lockstep', 'Client/Server', 'Client-Side Prediction' (Carmack QuakeWorld quote; 'if it takes 100ms from client to server and 100ms back, then any server correction ... will appear to be 200ms in the past'; circular buffer rewind-and-replay); Tim Sweeney 'The Server Is The Man' | verified_fetched |
| SRC-DER-005 | Snapshot Interpolation | Glenn Fiedler (Gaffer On Games) | engineering_blog | 2014-11-30 | 2026-09-10 | engine-agnostic | cross-platform | sections 'Snapshots' (CubeState = 225 bits / 28.1 bytes per cube; 900 cubes -> ~25 kB per snapshot; 25312.5 B payload + 28 B IP/UDP + 2 B sequence = 25342.5 B per packet), 'Jitter and Hitches' (60 pps -> 11.6 Mbit/s; 10 pps -> ~2 Mbit/s), 'Handling Real World Conditions' (interpolation buffer = 3x p | verified_fetched |
| SRC-DER-006 | Direct3D 12 programming guide | Microsoft (Microsoft Learn) | official_documentation | 2024 | 2026-09-10 | Direct3D 12 (Windows 10/11) | Windows PC | intro paragraph ('Direct3D 12 provides an API and platform ... for PCs equipped with one or more Direct3D 12-compatible GPUs') and topic list (work submission, resource binding, memory management, multi-adapter, Advanced Shader Delivery, performance measurement, D3D11on12 interop) | verified_fetched |
| SRC-DER-007 | Advanced Shader Delivery overview | Microsoft (Microsoft Learn) | official_documentation | 2025 | 2026-09-10 | Windows 11 Direct3D 12 | Windows PC | sections 'Advanced Shader Delivery' (on-device launch/JIT shader compilation -> longer load times, in-game shader compilation stutter, higher power consumption), 'How Advanced Shader Delivery works' (State Object Database SODB -> Precompiled Shader Database PSDB -> storefront deploy), 'Benefits' (fa | verified_fetched |
| SRC-DER-008 | Work submission in Direct3D 12 (command queues and command lists) | Microsoft (Microsoft Learn) | official_documentation | 2024 | 2026-09-10 | Direct3D 12 | Windows PC | intro: 'Direct3D 12 no longer supports an immediate context ... apps record and then submit command lists ... submitted from multiple threads to one or more command queues ... increases single-threaded efficiency ... takes advantage of multi-core systems by spreading rendering work across multiple t | verified_fetched |
| SRC-DER-009 | Memory management in Direct3D 12 | Microsoft (Microsoft Learn) | official_documentation | 2024 | 2026-09-10 | Direct3D 12 | Windows PC | intro: 'Moving to D3D12 involves doing proper synchronization and management of memory residency. Managing memory residency means even more synchronization must be done. This section covers memory management strategies, and suballocation within heaps and buffers.' | verified_fetched |
| SRC-DER-010 | Engine class reference (Engine.max_fps, Engine.physics_ticks_per_second) | Godot Engine documentation | official_documentation | 2026 | 2026-09-10 | Godot 4.7 | Windows PC / Linux PC / cross-platform | Engine class properties: physics_ticks_per_second = 60 ('The number of fixed iterations per second'), max_fps = 0 ('A value of 0 means the framerate is uncapped'), max_physics_steps_per_frame = 8, physics_jitter_fix = 0.5, time_scale = 1.0 | verified_fetched |
| SRC-DER-011 | Upgrading from Godot 3 to Godot 4 | Godot Engine documentation | official_documentation | 2026 | 2026-09-10 | Godot 3.x -> 4.x | Windows PC / Linux PC / cross-platform | sections 'Should I upgrade to Godot 4?', 'List of automatically renamed methods, properties, signals and constants', 'Updating shaders', 'ArrayMesh resource compatibility breakage'; statement that the engine was 'rewritten in many aspects, some features have unfortunately been lost in the process' ( | verified_fetched |
| SRC-DER-012 | Setting Up Dedicated Servers in Unreal Engine | Epic Games (Epic Developer Community) | official_documentation | 2026 | 2026-09-10 | Unreal Engine 5.8 | Windows PC / Linux PC | sections 'Overview' (client-server model, 'authoritative host', 'autonomous proxy'), 'Dedicated Server' (headless; listen server = a client hosts and is the authoritative host, 'This gives them an advantage over the connected clients'); default listen port 7777 on 127.0.0.1 | verified_fetched |
| SRC-DER-013 | Networking Overview for Unreal Engine | Epic Games (Epic Developer Community) | official_documentation | 2026 | 2026-09-10 | Unreal Engine 5.8 | Windows PC / Linux PC | sections on replication ('most actors do not replicate by default'; bReplicates, bReplicateMovement), network modes enum NM_Standalone / NM_DedicatedServer / NM_ListenServer / NM_Client, three replication systems (Generic, Replication Graph, Iris), qualitative 'Network connection speeds and bandwidt | verified_fetched |
| SRC-DER-014 | Performance Guidelines for Mobile Devices in Unreal Engine | Epic Games (Epic Developer Community) | official_documentation | 2023 | 2026-09-10 | Unreal Engine 5.x (mobile renderer) | Android / iOS (NOT PC) | section 'Draw Calls' ('Draw calls of the entire scene should be <=700 for any single view'), section 'Triangle Count' ('<=500k for any view ... the maximum poly count that can hit 30fps on both iPad4 and iPad Air'), note that Bloom/Depth of Field 'can cost 60 milliseconds or more with the default se | verified_fetched |
| SRC-DER-015 | Common Memory and CPU Performance Considerations in Unreal Engine | Epic Games (Epic Developer Community) | official_documentation | 2026 | 2026-09-10 | Unreal Engine 5.8 | Windows PC / Linux PC / consoles | sections 'Garbage Collection' (processing spikes when the GC runs), 'Threads' (six named engine threads: Game, Rendering, RHI, Task Pools, Audio, Loading), 'Shader Compilation / PSO caching' ('compiling shaders can result in significant processing spikes ... framerate hitches'; PSO precaching 'drama | verified_fetched |
| SRC-DER-016 | Timing Insights in Unreal Engine | Epic Games (Epic Developer Community) | official_documentation | 2026 | 2026-09-10 | Unreal Engine 5.8 | Windows PC / Linux PC / consoles | intro ('displays per-frame performance data ... including separate tracks for the CPU and GPU'), 'Frames Panel' ('total time taken by each frame ... identifying ... framerate drops'), 'Timing Panel' ('detailed view of CPU/GPU usage organized into separate tracks for each thread'), trace channels Con | verified_fetched |
| SRC-DER-017 | Introduction to Performance Profiling and Configuration in Unreal Engine | Epic Games (Epic Developer Community) | official_documentation | 2026 | 2026-09-10 | Unreal Engine 5.8 | Windows PC / Linux PC | statements: 'Generally, applications will target 30, 60, and 120 frames per second when considering their performance budget and target hardware'; CPU-bound / GPU-bound / display-bound definitions; 'Running your game with a profiler attached will cause it to have slightly worse performance'; tools U | verified_fetched |
| SRC-DER-018 | Saving and Loading Your Game in Unreal Engine | Epic Games (Epic Developer Community) | official_documentation | 2026 | 2026-09-10 | Unreal Engine 5.8 | Windows PC / Linux PC / consoles | sections 'Creating a SaveGame Object' (USaveGame, Kismet/GameplayStatics.h), 'Asynchronous Saving' ('AsyncSaveGameToSlot is the recommended method ... Running asynchronously prevents a sudden framerate hitch, making it less noticeable to players and avoiding a possible certification issue on some pl | verified_fetched |
| SRC-DER-019 | Unreal Engine Optimization Guide: Profiling Fundamentals | Intel | engineering_blog | 2025-03-17 | 2026-09-10 | Unreal Engine 5.x | Windows PC | sections 'Frame Time (MPF)', 'Frame Budget' ('33.33ms for 30 FPS', '16.66ms for 60 FPS'), conversions ('Frame Rate = 1000 / Frame Time (e.g., 60 FPS = 1000 / 16.67ms)'), 'CPU-Bound vs GPU-Bound' ('the value that means we are GPU-Bound is 95% GPU Utilization and above'; 'If Draw Time is ~95% of Frame | verified_fetched |
| SRC-DER-020 | What do 1% percentile statistics mean in PresentMon (issue #219) | Intel / GameTechDev (GitHub) | open_source | 2024-04 | 2026-09-10 | PresentMon 2.0 | Windows PC | Intel maintainer reply (2024-04-05): 'In 2.0.0, the percentile statistic is not context-aware. 1%ile will show the value where 1% of samples are less than or equal to that value ... So 1%tile FPS will be the slower frames, but 1%ile frametime will be the faster frames.'; also 'the 99th percentile of | verified_fetched |
| SRC-DER-021 | Vulkan 1.4.362 Specification (with all registered extensions) | Khronos Vulkan Working Group | secondary | 2026-09-04 | 2026-09-10 | Vulkan 1.4.362 | Windows PC / Linux PC / cross-platform | Preamble (version 1.4.362, generated 2026-09-04); section 2 'Vulkan is a C99 API designed for explicit control of low-level graphics and compute functionality'; 3.2.1 command buffers ('Many commands for queues are recorded into command buffers first, before the command buffers are then submitted to | verified_fetched |
| SRC-DER-022 | Steam Deck OLED - Tech Specs | Valve Corporation | official_documentation | 2023-11 | 2026-09-10 | SteamOS 3 (Arch-based) | Linux PC (handheld) | section 'Speeds and Feeds': CPU 'Zen 2 4c/8t, 2.4-3.5GHz (up to 448 GFlops FP32)', GPU '8 RDNA 2 CUs, 1.6GHz (1.6 TFlops FP32)', 'APU power: 4-15W', RAM '16 GB LPDDR5 on-board RAM (6400 MT/s quad 32-bit channels)', Storage '512GB/1TB NVMe SSD', Display 'Resolution 1280 x 800', 'Refresh rate up to 90 | verified_fetched |
| SRC-DER-023 | Steam Deck and Steam Machine Compatibility Review | Valve / Steamworks Documentation | official_documentation | 2026 | 2026-09-10 | SteamOS / Proton | Linux PC (Steam Deck / Steam Machine) | 'Performance' requirement: 'the game must ship with a default configuration that results in a playable framerate. On Steam Deck, this is 30fps at 800p, and on Steam Machine this is 30fps at 1080p'; 'Display Resolution Support: the game must run at a resolution supported by Steam Deck. (Recommendatio | verified_fetched |
| SRC-DER-024 | Steam Networking | Valve / Steamworks Documentation | official_documentation | 2026 | 2026-09-10 | Steamworks SDK (ISteamNetworkingSockets / ISteamNetworkingMessages) | Windows PC / Linux PC | intro ('Our newest APIs relay packets through the Valve network by default ... It also supports ordinary UDP connectivity'); ISteamNetworkingMessages ('Because it is very similar to UDP, it may be the easiest API to port existing UDP code'); Steam Datagram Relay ('prevents IP addresses from being re | verified_fetched |
| SRC-DER-025 | Steam Datagram Relay | Valve / Steamworks Documentation | official_documentation | 2024 | 2026-09-10 | Steamworks SDK (SDR) | Windows PC / Linux PC | 'Relaying the traffic protects your servers and players from DoS attack, because IP addresses are never revealed'; 'All traffic you receive is authenticated, encrypted, and rate-limited'; latency ('for a surprisingly high number of players, we can also find a faster route through our network, which | verified_fetched |
| SRC-DER-026 | The Mythical Man-Month (encyclopedia article summarising Brooks, 1975) | Wikipedia (secondary) | secondary | 2026 | 2026-09-10 | n/a | cross-platform | section 'The mythical man-month': 'Adding manpower to a late software project makes it later'; 'Complex programming ... 1,225 channels of communication' (n(n-1)/2 for n=50); 'The second-system effect'; 'Progress tracking': 'How does a large software project get to be one year late? Answer: One day a | verified_fetched |
| SRC-DER-027 | Game Engine Architecture - official table of contents (3rd and 4th editions) | Jason Gregory / gameenginebook.com (A K Peters/CRC Press) | book | 2025 | 2026-09-10 | 3rd ed. (2018) / 4th ed. (2025) | cross-platform | 3rd ed. TOC: Ch.2 'Tools of the Trade' incl. 2.3 'Profiling Tools'; Ch.4 'Parallelism and Concurrent Programming'; Ch.6 'Engine Support Systems' incl. 6.2 'Memory Management'; Ch.7 'Resources and the File System' incl. 7.1 'File System', 7.2 'The Resource Manager'; Ch.8 'The Game Loop and Real-Time | verified_fetched |
| SRC-DER-028 | GeForce RTX 4060 / RTX 4060 Ti graphics cards - specifications | NVIDIA Corporation | vendor_press_release | 2023-05 | 2026-09-10 | Ada Lovelace (RTX 40 series) | Windows PC | specification block: '8 GB GDDR6' memory, 128-bit memory interface, 3072 CUDA cores (RTX 4060) | verified_fetched |
| SRC-DER-029 | Quality project settings reference | Unity Technologies | official_documentation | 2026 | 2026-09-10 | Unity 6.6 | Windows PC / Linux PC / cross-platform | sections 'Quality levels matrix' (per-platform quality levels, default level per platform, Add Quality Level duplicates the highlighted level), 'Anti Aliasing' (MSAA; 'the higher the antialiasing level ... the more processing time needed on the GPU'; forward rendering only), 'Shadow Distance' (metre | verified_fetched |
| SRC-DER-030 | Application.targetFrameRate | Unity Technologies (Scripting API) | official_documentation | 2026 | 2026-09-10 | Unity 6.6 | Windows PC / Linux PC / cross-platform | 'the frame rate at which Unity tries to render your application'; 'With vSyncCount = 0 and Application.targetFrameRate = -1 ... content is rendered at the native display refresh rate' (desktop); worked example: setting targetFrameRate = 25 on a 60 Hz display renders at 20 fps because 20 is the highe | verified_fetched |
| SRC-DER-031 | Developer Satisfaction Survey 2023 - Summary Report | International Game Developers Association (IGDA) with Western University | academic_paper | 2024-05 | 2026-09-10 | n/a | cross-platform | section 'Snapshot: Hours of Work': 'Across all respondents, 28% said their job involved crunch time and a further 25% said that their job required periods of long hours ... that they just didn't call crunch'; 'Most employees (49%) worked 40-44 hours per week'; 'Among those who experienced crunch, 63 | verified_fetched |
| SRC-DER-032 | As Anthem shuts down, the game's executive producer has released a nearly four-hour post-mortem | Video Games Chronicle (VGC) | secondary | 2026-01-14 | 2026-09-10 | n/a (BioWare proprietary, Frostbite) | Windows PC / consoles | article reporting Mark Darrah's video post-mortem: Anthem 'rendered unplayable this week, 7 years after the game was released'; the game was pitched to EA as a 'new BioWare' pursuing an always-online model; after launch, 'a small group of developers at BioWare were working on a soft reboot of the ga | verified_fetched |
| SRC-DER-033 | VALORANT's 128-Tick Servers | Riot Games (engineering blog) | engineering_blog | 2020-08-31 | 2026-09-10 | Riot proprietary server stack (Linux, 36-core hosts) | Windows PC (dedicated server) | 'We need to be able to process an entire frame within 7.8125ms, but if we do that, a single game would take up an entire CPU core!'; 'we knew we needed to do better than 3 games per core (gpc)'; 'we generally run 36 core hosts, so each physical game server needed to host 108 games or 1080 players'; | verified_fetched |
| SRC-DER-034 | Peeking into VALORANT's Netcode | Riot Games (engineering blog) | engineering_blog | 2020-07-29 | 2026-09-10 | Riot proprietary (128 Hz fixed timestep) | Windows PC | 'a smooth 128 server tickrate'; 'clients and servers always update movement, physics ... with a fixed timestep: exactly 128 times per second'; 'a client running a 30hz physics simulation will slowly drift from a server running its physics at 128hz'; 'aiming to deliver 35ms ping to 70% of our player | verified_fetched |
| SRC-DER-035 | Game Loop (Game Programming Patterns, chapter) | Robert Nystrom | book | 2014 | 2026-09-10 | engine-agnostic | cross-platform | sections 'Take a Little Nap' ('Say you want your game to run at 60 FPS. That gives you about 16 milliseconds per frame.'; code comment '1000 ms / FPS = ms per frame'; 'If it takes longer than 16ms to update and render the frame, your sleep time goes negative'), 'Variable Time Step' ('we've made the | verified_fetched |
| SRC-DER-036 | Boehm Cost of Change Curve: What the 1981 Data Actually Shows | ReworkCost.com | secondary | 2026-08 | 2026-09-10 | n/a | cross-platform | table 'Relative cost to fix one defect by the phase it is caught' (Boehm 1981): Requirements 1x; Design 3x-8x; Code 5x-20x; Test (development) 10x-50x; Test (acceptance/UAT) 30x-100x; Operations (production) 50x-200x; plus the Boehm & Basili 2001 revision (small agile/CI projects flatten toward ~5:1 | verified_fetched |
| SRC-DER-037 | Unreal Build Tool in Unreal Engine | Epic Games (Epic Developer Community) | official_documentation | 2026 | 2026-09-10 | Unreal Engine 5.8 | Windows PC / Linux PC | intro: 'UnrealBuildTool (UBT) is a custom tool that manages the process of building Unreal Engine (UE) source code across a variety of build configurations' | verified_fetched |
| SRC-ENG-001 | Nanite Virtualized Geometry Overview | Epic Games / Epic Developer Community | official_documentation | 2024 (UE 5.4/5.5 doc | 2026-09-10 | Unreal Engine 5.4-5.5 | Windows PC / consoles (DX12 SM6) | sections 'Nanite Virtualized Geometry Overview', 'Benefits of Nanite', 'Features of Nanite', 'Materials', 'Rendering', 'Supported Platforms' | verified_fetched |
| SRC-ENG-002 | Lumen Global Illumination and Reflections | Epic Games / Epic Developer Community | official_documentation | 2024 (UE 5.4/5.5 doc | 2026-09-10 | Unreal Engine 5.4-5.5 | Windows PC / PS5 / Xbox Series S\|X | sections 'Lumen Global Illumination and Reflections', 'Getting Started with Lumen', 'Additional Notes' | verified_fetched |
| SRC-ENG-003 | Virtual Shadow Maps | Epic Games / Epic Developer Community | official_documentation | 2024 (UE 5.4/5.5 doc | 2026-09-10 | Unreal Engine 5.4-5.5 | Windows PC / consoles | sections 'Goals of Virtual Shadow Maps', 'Soft Shadows with Shadow Map Ray Tracing', 'Limitations of Shadow Map Ray Tracing', 'Clipmaps for Directional Light' | verified_fetched |
| SRC-ENG-004 | Virtual Texturing | Epic Games / Epic Developer Community | official_documentation | 2024 (UE 5.4/5.5 doc | 2026-09-10 | Unreal Engine 5.4-5.5 | Windows PC / consoles | sections 'Virtual Texturing Methods', 'Runtime Virtual Texturing', 'Streaming Virtual Texturing', 'Virtual Texture Lightmaps' | verified_fetched |
| SRC-ENG-005 | World Partition | Epic Games / Epic Developer Community | official_documentation | 2024 (UE 5.4/5.5 doc | 2026-09-10 | Unreal Engine 5.4-5.5 | Windows PC / consoles | sections 'World Partition', 'Enabling World Partition', 'Using the Open World Default Map', 'Streaming Sources' | verified_fetched |
| SRC-ENG-006 | Hierarchical Level of Detail | Epic Games / Epic Developer Community | official_documentation | 2024 (UE 5.4/5.5 doc | 2026-09-10 | Unreal Engine 5.4-5.5 | Windows PC / consoles | section 'Hierarchical Level of Detail' (overview paragraph) | verified_fetched |
| SRC-ENG-007 | Large World Coordinates in Unreal Engine 5 | Epic Games / Epic Developer Community | official_documentation | 2024 (UE5 docs, veri | 2026-09-10 | Unreal Engine 5.x (Beta feature) | Windows PC / consoles | sections 'Large World Coordinates', 'Experimenting with Large Worlds', 'Rendering' | verified_fetched |
| SRC-ENG-008 | Instanced Static Mesh Component | Epic Games / Epic Developer Community | official_documentation | 2024 (UE 5.4/5.5 doc | 2026-09-10 | Unreal Engine 5.4-5.5 | Windows PC / consoles | sections 'Instanced Static Mesh', 'Hierarchical Instanced Static Mesh', 'Static Mesh Component Stats' | verified_fetched |
| SRC-ENG-009 | Static Mesh Automatic LOD Generation | Epic Games / Epic Developer Community | official_documentation | 2024 (UE5 docs, veri | 2026-09-10 | Unreal Engine 5.x | Windows PC / consoles | sections 'Static Mesh Automatic LOD Generation', 'Using LOD Groups' | verified_fetched |
| SRC-ENG-010 | Niagara Overview | Epic Games / Epic Developer Community | official_documentation | 2024 (UE5 docs, veri | 2026-09-10 | Unreal Engine 5.x | Windows PC / consoles | sections 'Core Niagara Components', 'Emitters', 'Modules', 'Parameters and Parameter Types' | verified_fetched |
| SRC-ENG-011 | Chaos Physics Overview | Epic Games / Epic Developer Community | official_documentation | 2020 (UE 4.27 page, | 2026-09-10 | Unreal Engine 4.27 (Chaos lineage into UE5) | Windows PC / consoles | page 'Chaos Physics Overview' | verified_fetched |
| SRC-ENG-012 | Chaos Vehicles | Epic Games / Epic Developer Community | official_documentation | 2024 (UE 5.4/5.5 doc | 2026-09-10 | Unreal Engine 5.4-5.5 | Windows PC / consoles | page 'Chaos Vehicles' (overview paragraph) | verified_fetched |
| SRC-ENG-013 | Gameplay Ability System | Epic Games / Epic Developer Community | official_documentation | 2024 (UE5 docs, veri | 2026-09-10 | Unreal Engine 5.x | Windows PC / consoles | sections 'Gameplay Ability System', 'Valley of the Ancient Sample' | verified_fetched |
| SRC-ENG-014 | MassEntity Overview | Epic Games / Epic Developer Community | official_documentation | 2024 (UE5 docs, veri | 2026-09-10 | Unreal Engine 5.x | Windows PC / consoles | sections 'Basic Concepts', 'Processing the Entities', 'Subsystems', 'Traits' | verified_fetched |
| SRC-ENG-015 | Behavior Trees | Epic Games / Epic Developer Community | official_documentation | 2024 (UE5 docs, veri | 2026-09-10 | Unreal Engine 5.x | Windows PC / consoles | section 'Behavior Trees' (overview paragraph) | verified_fetched |
| SRC-ENG-016 | Navigation System | Epic Games / Epic Developer Community | official_documentation | 2024 (UE5 docs, veri | 2026-09-10 | Unreal Engine 5.x | Windows PC / consoles | section 'Navigation System' (overview paragraph) | verified_fetched |
| SRC-ENG-017 | Replication Graph | Epic Games / Epic Developer Community | official_documentation | 2024 (UE5 docs, veri | 2026-09-10 | Unreal Engine 5.x | Windows PC / consoles | sections 'Replication Graph', 'Structure', 'Enabling The System' | verified_fetched |
| SRC-ENG-018 | Significance Manager | Epic Games / Epic Developer Community | official_documentation | 2024 (UE5 docs, veri | 2026-09-10 | Unreal Engine 5.x | Windows PC / consoles | sections 'Significance Manager', 'Setup', 'Significance Manager Base Functionality' | verified_fetched |
| SRC-ENG-019 | Animation Budget Allocator | Epic Games / Epic Developer Community | official_documentation | 2024 (UE5 docs, veri | 2026-09-10 | Unreal Engine 5.x | Windows PC / consoles | sections 'Animation Budget Allocator', 'Prerequisites', 'Set Up the Animation Budget Allocator' | verified_fetched |
| SRC-ENG-020 | Unreal Insights | Epic Games / Epic Developer Community | official_documentation | 2024 (UE5 docs, veri | 2026-09-10 | Unreal Engine 5.x | Windows / Mac / Linux | sections 'Unreal Insights', 'Setting Up Unreal Insights', 'Configuring the Unreal Trace Server' | verified_fetched |
| SRC-ENG-021 | Unreal Engine 5.0 Release Notes | Epic Games / Epic Developer Community | official_documentation | 2022-04 (UE 5.0, ver | 2026-09-10 | Unreal Engine 5.0 | Windows PC / consoles | sections 'Rendering' (Nanite, Lumen, Virtual Shadow Maps, Virtual Texturing), 'World Building' (World Partition, HLOD, Large World Coordinates), 'Niagara', 'Chaos', 'MassEntity', 'Behavior Trees', 'Unreal Insights' | verified_fetched |
| SRC-ENG-022 | Unreal Engine 5.4 Release Notes | Epic Games / Epic Developer Community | official_documentation | 2024-04 (UE 5.4, ver | 2026-09-10 | Unreal Engine 5.4 | Windows PC / consoles | sections 'Rendering', 'World Building', 'Platforms' | verified_fetched |
| SRC-ENG-023 | Physics in Unreal Engine | Epic Games / Epic Developer Community | official_documentation | 2024 (UE5 docs, veri | 2026-09-10 | Unreal Engine 5.x | Windows PC / consoles | page 'Physics in Unreal Engine' (Chaos overview sections) | verified_fetched |
| SRC-ENG-024 | Chaos Destruction | Epic Games / Epic Developer Community | official_documentation | 2024 (UE5 docs, veri | 2026-09-10 | Unreal Engine 5.x | Windows PC / consoles | page 'Chaos Destruction' (overview) | verified_fetched |
| SRC-ENG-025 | Universal Render Pipeline overview | Unity Technologies | official_documentation | 2025 (URP 14.0 docs, | 2026-09-10 | Unity URP 14.0 (Unity 2022 LTS+) | cross-platform (mobile to console/PC) | section 'Universal Render Pipeline overview' | verified_fetched |
| SRC-ENG-026 | High Definition Render Pipeline overview | Unity Technologies | official_documentation | 2025 (HDRP 14.0 docs | 2026-09-10 | Unity HDRP 14.0 (Unity 2022 LTS+) | modern compute-shader-capable platforms | section 'High Definition Render Pipeline overview' | verified_fetched |
| SRC-ENG-027 | Scriptable Render Pipeline Batcher in URP | Unity Technologies | official_documentation | 2025 (Unity 6.6 manu | 2026-09-10 | Unity 6.6 (6000.6) manual | cross-platform | section 'Scriptable Render Pipeline Batcher in URP' | verified_fetched |
| SRC-ENG-028 | Introduction to GPU instancing | Unity Technologies | official_documentation | 2025 (Unity 6.6 manu | 2026-09-10 | Unity 6.6 (6000.6) manual | cross-platform (better on mobile) | sections 'Introduction to GPU instancing', 'Render pipeline compatibility' | verified_fetched |
| SRC-ENG-029 | LOD Group component reference | Unity Technologies | official_documentation | 2025 (Unity 6.6 manu | 2026-09-10 | Unity 6.6 (6000.6) manual | cross-platform | section 'LOD Group component reference' | verified_fetched |
| SRC-ENG-030 | Excluding hidden objects with occlusion culling | Unity Technologies | official_documentation | 2025 (Unity 6.6 manu | 2026-09-10 | Unity 6.6 (6000.6) manual | cross-platform | section 'Occlusion culling' | verified_fetched |
| SRC-ENG-031 | Precalculating indirect light with Light Probes | Unity Technologies | official_documentation | 2025 (Unity 6.6 manu | 2026-09-10 | Unity 6.6 (6000.6) manual | cross-platform | section 'Light Probes' | verified_fetched |
| SRC-ENG-032 | Choose a light baking backend | Unity Technologies | official_documentation | 2025 (Unity 6.6 manu | 2026-09-10 | Unity 6.6 (6000.6) manual | cross-platform (GPU/CPU dependent) | section 'Choose a light baking backend' | verified_fetched |
| SRC-ENG-033 | Job system overview | Unity Technologies | official_documentation | 2025 (Unity 6.6 manu | 2026-09-10 | Unity 6.6 (6000.6) manual | cross-platform (core-count dependent) | sections 'Job system overview', 'Multithreading' | verified_fetched |
| SRC-ENG-034 | Addressables package overview | Unity Technologies | official_documentation | 2024 (Addressables 1 | 2026-09-10 | Unity Addressables 1.21 | cross-platform | section 'Addressables package' | verified_fetched |
| SRC-ENG-035 | Optimizing GPU texture memory with mipmap streaming | Unity Technologies | official_documentation | 2025 (Unity 6.6 manu | 2026-09-10 | Unity 6.6 (6000.6) manual | cross-platform | sections 'Introduction to mipmap streaming', 'Configure mipmap streaming' | verified_fetched |
| SRC-ENG-036 | Navigation System in Unity | Unity Technologies | official_documentation | 2021 (Unity 2021.3 m | 2026-09-10 | Unity 2021.3 manual | cross-platform | section 'Navigation System in Unity' | verified_fetched |
| SRC-ENG-037 | Visual Effect Graph | Unity Technologies | official_documentation | 2024 (VFX Graph 16.0 | 2026-09-10 | Unity VFX Graph 16.0 | cross-platform | section 'Visual Effect Graph' | verified_fetched |
| SRC-ENG-038 | Unity Profiler | Unity Technologies | official_documentation | 2025 (Unity 6.6 manu | 2026-09-10 | Unity 6.6 (6000.6) manual | cross-platform | section 'Unity Profiler' | verified_fetched |
| SRC-ENG-039 | Quality project settings reference | Unity Technologies | official_documentation | 2025 (Unity 6.6 manu | 2026-09-10 | Unity 6.6 (6000.6) manual | cross-platform | sections 'Quality project settings reference', 'Quality levels matrix' | verified_fetched |
| SRC-ENG-040 | Entities overview (DOTS) | Unity Technologies | official_documentation | 2024 (Entities 1.0 d | 2026-09-10 | Unity Entities 1.0 (Unity 2022.3.0f1+) | cross-platform | sections 'Entities overview', 'Package installation' | verified_fetched |
| SRC-ENG-041 | Unity Netcode for Entities | Unity Technologies | official_documentation | 2024 (Netcode for En | 2026-09-10 | Unity Netcode for Entities 1.0 | cross-platform | sections 'Unity Netcode for Entities', 'Requirements' | verified_fetched |
| SRC-ENG-042 | AI Navigation package | Unity Technologies | official_documentation | 2025 (Unity 6.6 manu | 2026-09-10 | Unity 6.6 (6000.6) manual | cross-platform | page 'AI Navigation' (package listing) | verified_fetched |
| SRC-ENG-043 | DOTS - Unity's Data-Oriented Technology Stack | Unity Technologies | engineering_blog | 2024 (page, verified | 2026-09-10 | Unity 6 | cross-platform | sections 'DOTS in Production' (V Rising / Zenith / Detonation Racing / IXION / Hardspace: Shipbreaker) | verified_fetched |
| SRC-ENG-044 | Addressables: Planning and best practices | Jeff Riesenmy / Unity Technologies | engineering_blog | 2023-02-08 | 2026-09-10 | Unity Addressables 1.21 | cross-platform | sections 'Addressables: Planning and best practices', 'Introduction' | verified_fetched |
| SRC-ENG-045 | V Rising: Behind the vampire realm built on 1,600 ECS systems | Stunlock Studios / Unity Technologies | postmortem | 2024-12-09 | 2026-09-10 | Unity DOTS + HDRP (Unity 2022/6) | Windows PC / PlayStation 5 | sections 'The challenge', 'The results' | verified_fetched |
| SRC-ENG-046 | Unity render pipeline features (URP / HDRP) | Unity Technologies | vendor_press_release | 2025 (page, verified | 2026-09-10 | Unity 6 | cross-platform | sections 'Universal Render Pipeline (URP)', 'High-Definition Render Pipeline (HDRP)' | verified_fetched |
| SRC-ENG-047 | Unity Engine product page | Unity Technologies | vendor_press_release | 2026 (page, verified | 2026-09-10 | Unity 6 | cross-platform | sections 'Deploy - Multiplatform', 'Frequently asked questions' | verified_fetched |
| SRC-ENG-048 | Unity plans and pricing | Unity Technologies | vendor_press_release | 2026 (page, verified | 2026-09-10 | Unity 6 | cross-platform | plan cards 'Personal', 'Pro', 'Enterprise' | verified_fetched |
| SRC-ENG-049 | Unity (game engine) - Wikipedia | Wikipedia contributors | secondary | 2026 (page, verified | 2026-09-10 | Unity 6 | cross-platform | infobox 'Written in' / 'License' | verified_fetched |
| SRC-ENG-050 | Unity-Technologies/EntityComponentSystemSamples | Unity Technologies | open_source | 2026 (repository, ve | 2026-09-10 | Unity Entities / Netcode | cross-platform | repository README (Entities samples, Netcode samples, Physics samples, Entities.Graphics HDRP samples) | verified_url_only |
| SRC-ENG-052 | Unreal Engine - Wikipedia | Wikipedia contributors | secondary | 2026 (page, verified | 2026-09-10 | Unreal Engine 5 | cross-platform | infobox ('Written in C++', 'License', 'Operating system') and lead section | verified_fetched |
| SRC-ENG-053 | Godot Engine home | Godot Foundation | official_documentation | 2026 (page, latest 4 | 2026-09-10 | Godot 4.7.2 / 3.6.x LTS | Windows / macOS / Linux / web / mobile | sections 'Script with an object-oriented API', 'Exemplary XR support', 'Release on all platforms' | verified_fetched |
| SRC-ENG-054 | Godot Engine documentation (stable) | Godot Foundation | official_documentation | 2026 (stable docs, v | 2026-09-10 | Godot 4.x stable | cross-platform | table of contents (Rendering, 2D/3D graphics, 2D/3D physics, GDExtension, FAQ) | verified_fetched |
| SRC-ENG-055 | Godot (game engine) - Wikipedia | Wikipedia contributors | secondary | 2026 (page, verified | 2026-09-10 | Godot 4.x | cross-platform | infobox ('License: MIT', 'Written in C++') and section 'Notable video games made with Godot' | verified_fetched |
| SRC-ENG-056 | godotengine/godot | Godot Foundation | open_source | 2026 (repository, ve | 2026-09-10 | Godot 4.x | cross-platform | repository header (86,319 commits on the default branch) | verified_url_only |
| SRC-ENG-057 | CRYENGINE home | Crytek | official_documentation | 2026 (page, verified | 2026-09-10 | CRYENGINE V (5.x) | Windows / consoles | page 'Features' / 'CRYENGINE Documentation' | verified_fetched |
| SRC-ENG-058 | CRYENGINE Documentation | Crytek | official_documentation | 2026 (page, verified | 2026-09-10 | CRYENGINE 3 / CRYENGINE V | Windows / consoles | sections 'CRYENGINE 3', 'CRYENGINE V', 'CRYENGINE V Manual', 'CRYENGINE Launcher Reference' | verified_fetched |
| SRC-ENG-059 | CryEngine - Wikipedia | Wikipedia contributors | secondary | 2026 (page, verified | 2026-09-10 | CryEngine 1 - 5.7.1 | Windows / Linux / consoles | infobox ('Written in', 'License', 'Platform', 'Stable release') and section 'History' | verified_fetched |
| SRC-ENG-060 | Source (game engine) - Wikipedia | Wikipedia contributors | secondary | 2026 (page, verified | 2026-09-10 | Source 1 (2004-2013) | Windows / Linux / macOS / consoles | infobox ('Written in C++', 'License: Source-available', 'Release October 2004') and lead | verified_fetched |
| SRC-ENG-061 | Source 2 - Wikipedia | Wikipedia contributors | secondary | 2026 (page, verified | 2026-09-10 | Source 2 (2015+) | Windows / Linux / macOS / consoles / VR | infobox ('Release September 2015', 'License: Proprietary') and section 'Games' | verified_fetched |
| SRC-ENG-062 | HeroEngine home | Idea Fabrik Plc / Laniatus | vendor_press_release | 2024 (page, verified | 2026-09-10 | HeroEngine 2.x | Windows / macOS | landing page / HeroCloud login | verified_fetched |
| SRC-ENG-063 | HeroEngine - Wikipedia | Wikipedia contributors | secondary | 2026 (page, verified | 2026-09-10 | HeroEngine 2.074 | Windows / macOS | infobox ('Written in', 'License', 'Stable release') and sections 'HeroCloud', 'Games developed using HeroEngine' | verified_fetched |
| SRC-ENG-064 | bevyengine/bevy | Bevy contributors | open_source | 2026 (repository, ve | 2026-09-10 | Bevy (Rust, ECS) | Windows / macOS / Linux / web | repository header (12,166 commits on the default branch) | verified_url_only |
| SRC-ENG-065 | Rockstar Advanced Game Engine - Wikipedia | Wikipedia contributors | secondary | 2026 (page, verified | 2026-09-10 | RAGE (proprietary in-house) | Windows / consoles / mobile | infobox ('License: Proprietary') and lead | verified_fetched |
| SRC-ENG-066 | CD Projekt - Wikipedia | Wikipedia contributors | secondary | 2026 (page, verified | 2026-09-10 | REDengine (in-house) | Windows / consoles | section 'Games developed' (The Witcher 2/3, Cyberpunk 2077) | verified_fetched |
| SRC-ENG-067 | Black Myth: Wukong wows with UE5 early access visuals | Jimmy Thang / Epic Games | interview | 2021-09-22 | 2026-09-10 | Unreal Engine 5 (Early Access) | Windows PC | Q&A 'Does the team have any favorite Unreal Engine 5 features?' (Zhao Wenyong) | verified_fetched |
| SRC-ENG-068 | Drop into the Next Generation of Fortnite Battle Royale, Powered by Unreal Engine 5.1 | Epic Games | vendor_press_release | 2022-12-04 | 2026-09-10 | Unreal Engine 5.1 | PS5 / Xbox Series X\|S / PC / cloud | sections 'Nanite', 'Lumen', 'Virtual Shadow Maps', 'What are the minimum PC specifications to run Nanite?' | verified_fetched |
| SRC-ENG-069 | Battle-testing Unreal Engine 5.1's new features on Fortnite Battle Royale Chapter 4 | Epic Games | engineering_blog | 2023-01-26 | 2026-09-10 | Unreal Engine 5.1 | PS5 / Xbox Series X\|S / PC / cloud | feature list (Lumen, Nanite, Virtual Shadow Maps, Niagara, World Partition, Automatic HLODs, Navmesh static+dynamic, 100,000+ Actor files, 60 fps target) | verified_fetched |
| SRC-ENG-070 | The making of Senua's Saga: Hellblade 2 - the big tech interview | Digital Foundry (Alex Battaglia / Ninja Theory) | interview | 2024-08-08 | 2026-09-10 | Unreal Engine 5 | Xbox Series X\|S / PC | Q&A on moving from UE4 to UE5 (Mark Slater-Tunstill, Dan Atwell) | verified_fetched |
| SRC-ENG-071 | Fortnite Battle Royale - Wikipedia | Wikipedia contributors | secondary | 2026 (page, verified | 2026-09-10 | Unreal Engine 5 | cross-platform | infobox 'Engine: Unreal Engine 5' | verified_fetched |
| SRC-ENG-072 | Netcode for GameObjects - About | Unity Technologies | official_documentation | 2026 (NGO 2.13 docs, | 2026-09-10 | Unity Netcode for GameObjects 2.13 | Windows/macOS/Linux, iOS/Android, XR, consoles, WebGL | sections 'Netcode for GameObjects', 'Before you begin' | verified_fetched |
| SRC-ENG-073 | Black Myth: Wukong - the PC tech review | Digital Foundry (Alex Battaglia) | secondary | 2024-08-19 | 2026-09-10 | Unreal Engine 5 | Windows PC | sections on Nanite, foliage LOD, Virtual Shadow Maps and software Lumen | verified_fetched |
| SRC-ENG-074 | Brilliant visuals and growing pains: examining the first generation of Unreal Engine 5 games | Digital Foundry | secondary | 2023-10-28 | 2026-09-10 | Unreal Engine 5 | Windows PC / consoles | sections on Lumen, Nanite and Virtual Shadow Maps across UE5 titles (The Talos Principle 2, Jusant, Remnant 2, Immortals of Aveum, Lords of the Fallen) | verified_fetched |
| SRC-ENG-075 | Lords of the Fallen is a stunning UE5 Soulslike with ongoing tech issues | Digital Foundry | secondary | 2023-11-10 | 2026-09-10 | Unreal Engine 5 | PS5 / Xbox Series X\|S / PC | paragraphs on the game's heavy use of Nanite and Lumen | verified_fetched |
| SRC-FUNC-001 | Lumen Global Illumination and Reflections in Unreal Engine | Epic Games | official_documentation | 2026 | 2026-09-10 | UE 5.8 | cross-platform | section 'Lumen Global Illumination and Reflections' (page intro) | verified_fetched |
| SRC-FUNC-002 | Lumen Technical Details in Unreal Engine | Epic Games | official_documentation | 2026 | 2026-09-10 | UE 5.8 | cross-platform | section 'Lumen Technical Details' intro + 'Surface Cache' | verified_fetched |
| SRC-FUNC-003 | Lumen Performance Guide for Unreal Engine | Epic Games | official_documentation | 2026 | 2026-09-10 | UE 5.8 | cross-platform | page intro + section 'Scalability Settings' | verified_fetched |
| SRC-FUNC-004 | World Partition in Unreal Engine | Epic Games | official_documentation | 2026 | 2026-09-10 | UE 5.8 | cross-platform | section 'World Partition' (page intro) | verified_fetched |
| SRC-FUNC-005 | Nanite Virtualized Geometry Overview | Epic Games | official_documentation | 2026 | 2026-09-10 | UE 5.8 | cross-platform | section 'Nanite Virtualized Geometry Overview' + 'Benefits of Nanite' | verified_fetched |
| SRC-FUNC-006 | Virtual Shadow Maps in Unreal Engine | Epic Games | official_documentation | 2026 | 2026-09-10 | UE 5.8 | cross-platform | sections 'Goals of Virtual Shadow Maps' and 'Soft Shadows with Shadow Map Ray Tracing' | verified_fetched |
| SRC-FUNC-007 | Render Dependency Graph in Unreal Engine | Epic Games | official_documentation | 2026 | 2026-09-10 | UE 5.8 | cross-platform | section 'Render Dependency Graph' (page intro) + feature list | verified_fetched |
| SRC-FUNC-008 | Temporal Super Resolution in Unreal Engine | Epic Games | official_documentation | 2026 | 2026-09-10 | UE 5.8 | cross-platform | section 'Temporal Super Resolution' (page intro) | verified_fetched |
| SRC-FUNC-009 | Dynamic Resolution in Unreal Engine | Epic Games | official_documentation | 2026 | 2026-09-10 | UE 5.8 | cross-platform | section 'Dynamic Resolution' (page intro) | verified_fetched |
| SRC-FUNC-010 | Path Tracer in Unreal Engine | Epic Games | official_documentation | 2026 | 2026-09-10 | UE 5.8 | cross-platform | section 'Path Tracer' (page intro) + 'Benefits of the Path Tracer' | verified_fetched |
| SRC-FUNC-011 | Lightmass Basics in Unreal Engine | Epic Games | official_documentation | 2026 | 2026-09-10 | UE 5.8 | cross-platform | section 'Lightmass Basics' + 'Lightmass Importance Volume' | verified_fetched |
| SRC-FUNC-012 | Foliage Mode in Unreal Engine | Epic Games | official_documentation | 2026 | 2026-09-10 | UE 5.8 | cross-platform | sections 'Foliage Types', 'Culling Settings', 'Foliage Scalability', 'Using Foliage with World Partition' | verified_fetched |
| SRC-FUNC-013 | Landscape Technical Guide | Epic Games | official_documentation | 2026 | 2026-09-10 | UE 5.8 | cross-platform | sections 'Landscape Components' and 'Landscape Dimensions' | verified_fetched |
| SRC-FUNC-014 | Mesh Drawing Pipeline | Epic Games | official_documentation | 2026 | 2026-09-10 | UE 5.8 | cross-platform | sections 'Mesh Drawing Pipeline' intro and 'FPrimitiveSceneProxy' | verified_fetched |
| SRC-FUNC-015 | Skeletal Mesh LODs | Epic Games | official_documentation | 2026 | 2026-09-10 | UE 5.8 | cross-platform | section 'Creating LODs' | verified_fetched |
| SRC-FUNC-016 | Memory Insights | Epic Games | official_documentation | 2026 | 2026-09-10 | UE 5.8 | cross-platform | sections 'Investigation - Allocation Queries' and 'Call Stack Symbol Resolving' | verified_fetched |
| SRC-FUNC-017 | Audio Mixer Overview | Epic Games | official_documentation | 2026 | 2026-09-10 | UE 5.8 | cross-platform | section 'Audio Mixer Overview' (page intro) | verified_fetched |
| SRC-FUNC-018 | Post Process Effects | Epic Games | official_documentation | 2026 | 2026-09-10 | UE 5.8 | cross-platform | section 'Post Process Effects' (page intro) | verified_fetched |
| SRC-FUNC-019 | Volumetric Fog | Epic Games | official_documentation | 2026 | 2026-09-10 | UE 5.8 | cross-platform | section 'Volumetric Fog' (page intro) | verified_fetched |
| SRC-FUNC-020 | Large World Coordinates | Epic Games | official_documentation | 2026 | 2026-09-10 | UE 5.8 (Beta) | cross-platform | section 'Large World Coordinates' (page intro) | verified_fetched |
| SRC-FUNC-021 | Saving and Loading Your Game | Epic Games | official_documentation | 2026 | 2026-09-10 | UE 5.8 | cross-platform | section 'Saving and Loading Your Game' (page intro) | verified_fetched |
| SRC-FUNC-022 | UnrealBuildTool | Epic Games | official_documentation | 2026 | 2026-09-10 | UE 5.8 | cross-platform | section 'UnrealBuildTool' + 'Modular Architecture' | verified_fetched |
| SRC-FUNC-023 | Multiplayer Programming Quick Start | Epic Games | official_documentation | 2026 | 2026-09-10 | UE 5.8 | cross-platform | sections 'Replicating Variables' and 'Remote Procedure Calls' | verified_fetched |
| SRC-FUNC-024 | Modeling Mode Overview | Epic Games | official_documentation | 2026 | 2026-09-10 | UE 5.8 (Beta) | cross-platform | section 'Modeling Mode Overview' (page intro) | verified_fetched |
| SRC-FUNC-025 | Hair Rendering and Simulation | Epic Games | official_documentation | 2026 | 2026-09-10 | UE 5.8 | cross-platform | section 'Hair Rendering and Simulation' (page intro) | verified_fetched |
| SRC-FUNC-026 | Water System | Epic Games | official_documentation | 2026 | 2026-09-10 | UE 5.8 | cross-platform | section 'Water System' (page intro) | verified_fetched |
| SRC-FUNC-027 | MassEntity Overview | Epic Games | official_documentation | 2026 | 2026-09-10 | UE 5.8 | cross-platform | section 'MassEntity Overview' (page intro) | verified_fetched |
| SRC-FUNC-028 | Gameplay Ability System | Epic Games | official_documentation | 2026 | 2026-09-10 | UE 5.8 | cross-platform | section 'Gameplay Ability System' (page intro) | verified_fetched |
| SRC-FUNC-029 | Split Screen (Unreal Engine 4.27) | Epic Games | official_documentation | 2021 | 2026-09-10 | UE 4.27 | cross-platform | sections 'Detail Mode Overview' and 'How do I determine Draw Calls?' | verified_fetched |
| SRC-FUNC-030 | Stat Commands | Epic Games | official_documentation | 2026 | 2026-09-10 | UE 5.8 | cross-platform | section 'Stat Commands' command reference | verified_fetched |
| SRC-FUNC-031 | Unreal Insights | Epic Games | official_documentation | 2026 | 2026-09-10 | UE 5.8 | cross-platform | sections 'Recording a Session' and 'Timing View' | verified_fetched |
| SRC-FUNC-032 | Chaos Destruction | Epic Games | official_documentation | 2026 | 2026-09-10 | UE 5.8 | cross-platform | section 'Chaos Destruction' (page intro) | verified_fetched |
| SRC-FUNC-033 | Geometry Collections User Guide | Epic Games | official_documentation | 2026 | 2026-09-10 | UE 5.8 | cross-platform | section 'Geometry Collections User Guide' (page intro) | verified_fetched |
| SRC-FUNC-034 | Quality project settings reference (Unity Manual) | Unity Technologies | official_documentation | 2026 | 2026-09-10 | Unity 6.6 (6000.6) | cross-platform | section 'Quality' project settings reference | verified_fetched |
| SRC-FUNC-035 | Cloth (Unity Manual) | Unity Technologies | official_documentation | 2026 | 2026-09-10 | Unity 6.6 (6000.6) | cross-platform | section 'Cloth' (page intro) | verified_fetched |
| SRC-FUNC-036 | Terrain (Unity Manual) | Unity Technologies | official_documentation | 2026 | 2026-09-10 | Unity 6.6 (6000.6) | cross-platform | section 'Creating and editing Terrains' | verified_fetched |
| SRC-FUNC-037 | Lightmapping (Unity Manual) | Unity Technologies | official_documentation | 2026 | 2026-09-10 | Unity 6.6 (6000.6) | cross-platform | section 'Lightmapping' (page intro) | verified_fetched |
| SRC-FUNC-038 | Animator (Unity Manual) | Unity Technologies | official_documentation | 2026 | 2026-09-10 | Unity 6.6 (6000.6) | cross-platform | section 'Animator' (page intro) | verified_fetched |
| SRC-FUNC-039 | Physics Overview (Unity Manual) | Unity Technologies | official_documentation | 2026 | 2026-09-10 | Unity 6.6 (6000.6) | cross-platform | section 'Physics' overview | verified_fetched |
| SRC-FUNC-040 | Wheel Collider (Unity Manual) | Unity Technologies | official_documentation | 2026 | 2026-09-10 | Unity 6.6 (6000.6) | cross-platform | section 'Wheel Collider' (page intro) | verified_fetched |
| SRC-FUNC-041 | Introduction to AssetBundles (Unity Manual) | Unity Technologies | official_documentation | 2026 | 2026-09-10 | Unity 6.6 (6000.6) | cross-platform | section 'Introduction to AssetBundles' (page intro) | verified_fetched |
| SRC-FUNC-042 | Memory in Unity: managed memory (Unity Manual) | Unity Technologies | official_documentation | 2026 | 2026-09-10 | Unity 6.6 (6000.6) | cross-platform | section 'Memory in Unity introduction' | verified_fetched |
| SRC-FUNC-043 | LOD Group (Unity Manual) | Unity Technologies | official_documentation | 2026 | 2026-09-10 | Unity 6.6 (6000.6) | cross-platform | section 'LOD Group' (page intro) | verified_fetched |
| SRC-FUNC-044 | Post-processing (Unity Manual) | Unity Technologies | official_documentation | 2026 | 2026-09-10 | Unity 6.6 (6000.6) | cross-platform | section 'Post-processing' overview | verified_fetched |
| SRC-FUNC-045 | Render pipelines overview (Unity Manual) | Unity Technologies | official_documentation | 2026 | 2026-09-10 | Unity 6.6 (6000.6) | cross-platform | section 'Render pipelines' overview | verified_fetched |
| SRC-FUNC-046 | Particle System (Unity Manual) | Unity Technologies | official_documentation | 2026 | 2026-09-10 | Unity 6.6 (6000.6) | cross-platform | section 'Particle System' (page intro) | verified_fetched |
| SRC-FUNC-047 | Build Settings (Unity Manual) | Unity Technologies | official_documentation | 2026 | 2026-09-10 | Unity 6.6 (6000.6) | cross-platform | section 'Build Settings' (page intro) | verified_fetched |
| SRC-FUNC-048 | Skinned Mesh Renderer (Unity Manual) | Unity Technologies | official_documentation | 2026 | 2026-09-10 | Unity 6.6 (6000.6) | cross-platform | section 'Skinned Mesh Renderer' (page intro) | verified_fetched |
| SRC-FUNC-049 | Trees (Unity Terrain, Unity Manual) | Unity Technologies | official_documentation | 2026 | 2026-09-10 | Unity 6.6 (6000.6) | cross-platform | section 'Trees' (page intro) | verified_fetched |
| SRC-FUNC-050 | Multi-scene editing (Unity Manual) | Unity Technologies | official_documentation | 2026 | 2026-09-10 | Unity 6.6 (6000.6) | cross-platform | section 'Multi-scene editing' (page intro) | verified_fetched |
| SRC-FUNC-051 | The AI Systems of Left 4 Dead | Michael Booth / Valve | conference_talk | 2009 | 2026-09-10 | Source engine (2008) | cross-platform | slides 'AI Director', 'Relax period', 'Peak Fade', 'Two concurrent Behavior systems' | verified_fetched |
| SRC-FUNC-052 | Three States and a Plan: The A.I. of F.E.A.R. | Jeff Orkin / Monolith Productions (GDC 2006) | conference_talk | 2006 | 2026-09-10 | F.E.A.R. (LithTech Jupiter EX) | cross-platform | pp.1-14 (three states, GOAP, cost per action, world-state array, squad behaviours) | verified_fetched |
| SRC-FUNC-053 | Crowd Pathfinding and Steering Using Flow Field Tiles (Game AI Pro, ch.23) | Elijah Emerson / Game AI Pro | book | 2013 | 2026-09-10 | Supreme Commander 2 (2010) | cross-platform | pp.307+ (sections 23.1-23.4: cost fields, integration fields, flow fields) | verified_fetched |
| SRC-FUNC-054 | Rendering 'DOOM Eternal' (Advances in Real-Time Rendering, SIGGRAPH 2020) | Jean Geffroy, Axel Gneiting, Yixin Wang / id Software | conference_talk | 2020 | 2026-09-10 | id Tech 7 | cross-platform | slides on forward rendering, light binning budget and GPU-driven geometry | verified_fetched |
| SRC-FUNC-055 | Streaming the World of Horizon Zero Dawn | Jan-Jaap / Guerrilla Games | engineering_blog | 2023 | 2026-09-10 | Decima Engine | cross-platform | talk abstract, 'Description' block | verified_fetched |
| SRC-FUNC-056 | Massive Crowd on Assassin's Creed Unity: AI Recycling | Francois Cournoyer / Ubisoft (GDC 2015) | conference_talk | 2015 | 2026-09-10 | AnvilNext 2.0 | cross-platform | session 'Overview' text | verified_fetched |
| SRC-FUNC-057 | Continuous World Generation in 'No Man's Sky' | Innes McKendrick / Hello Games (GDC 2017) | conference_talk | 2017 | 2026-09-10 | No Man's Sky engine | cross-platform | session 'Overview' text | verified_fetched |
| SRC-FUNC-058 | 'Overwatch' Gameplay Architecture and Netcode | Timothy Ford / Blizzard (GDC 2017) | conference_talk | 2017 | 2026-09-10 | Overwatch engine | cross-platform | session 'Overview' text | verified_fetched |
| SRC-FUNC-059 | NVIDIA DLSS: Your Questions, Answered | Andrew Edelsten / NVIDIA | engineering_blog | 2019 | 2026-09-10 | DLSS 1.x (Turing) | cross-platform | Q&A on how DLSS works, where it helps and 4K vs 1080p input pixel counts | verified_fetched |
| SRC-FUNC-060 | DirectStorage Overview (Microsoft Game Development Kit) | Microsoft | official_documentation | 2025 | 2026-09-10 | GDK DirectStorage | cross-platform | sections 'High CPU usage', 'Insufficient maximum bandwidth', 'No hardware accelerated decompression' | verified_fetched |
| SRC-FUNC-061 | Generating Complex Procedural Terrains Using the GPU (GPU Gems 3, ch.1) | Ryan Geiss / NVIDIA | book | 2007 | 2026-09-10 | DirectX 10 | cross-platform | sections on marching cubes case tables and geometry-shader polygon generation | verified_fetched |
| SRC-FUNC-062 | Summed-Area Variance Shadow Maps (GPU Gems 3, ch.8) | Andrew Lauritzen / NVIDIA | book | 2007 | 2026-09-10 | DirectX 10 | cross-platform | chapter sections on variance shadow maps and SAT filtering | verified_fetched |
| SRC-FUNC-063 | Portals and Mirrors: Simple, Fast Evaluation of Potentially Visible Sets | David Luebke, Chris Georges (1995 Symposium on Interactive 3D Graphics) | academic_paper | 1995 | 2026-09-10 | n/a (algorithmic) | cross-platform | Abstract + 'Introduction' (cells, portals, PVS) | verified_fetched |
| SRC-FUNC-064 | How Northlight makes Alan Wake 2 shine | Remedy Entertainment | engineering_blog | 2023-11-06 | 2026-09-10 | Northlight (Alan Wake 2) | cross-platform | sections 'Core engine', 'Graphics and rendering', 'Ray tracing', 'Transparency and atmospheric effects' | verified_fetched |
| SRC-FUNC-065 | Multiplayer Level Design in Red Faction Guerrilla | Volition (GDC 2009) | conference_talk | 2009 | 2026-09-10 | Geo-Mod 2.0 | cross-platform | session 'Overview' text | verified_fetched |
| SRC-FUNC-066 | AMD TressFX (GPUOpen) | AMD / GPUOpen | official_documentation | 2026 | 2026-09-10 | TressFX 4.1 / 5.0 (UE 4.26-5.4) | cross-platform | sections 'Hair rendering and simulation', 'Features', 'Meet AMD TressFX 5.0' | verified_fetched |
| SRC-FUNC-067 | Visual Effects Summit: Can We Do It with Particles? VFX Learnings from 'Returnal' | Risto Jankkila, Sharman Jagadeesan / Housemarque (GDC 2022) | conference_talk | 2022 | 2026-09-10 | Unreal Engine 4 (Returnal) | cross-platform | session 'Overview' text | verified_fetched |
| SRC-FUNC-068 | Uncharted Animation: An In-depth Look at the Character Animation Workflow and Pipeline | Jeremy Lai-Yates, Judd Simantov / Naughty Dog (GDC 2008) | conference_talk | 2008 | 2026-09-10 | Naughty Dog engine (Uncharted) | cross-platform | session listing (title, speakers, track, GDC 2008) | verified_url_only |
| SRC-FUNC-069 | Technical Art Techniques of Naughty Dog: Vertex Shaders and Beyond | Andrew Maximov / Naughty Dog (GDC) | conference_talk | 2017 | 2026-09-10 | Uncharted 4 | cross-platform | session 'Overview' text | verified_fetched |
| SRC-FUNC-070 | Making and Using Non-Standard Textures | Alex Grimes / Valve (GDC 2011) | conference_talk | 2011 | 2026-09-10 | Source engine (Portal 2) | cross-platform | slides 2-4 (Portal 2 water rendering, flow data generation, gels) | verified_fetched |
| SRC-FUNC-071 | Vehicle Physics and Tire Dynamics in 'Just Cause 4' | Hamish Young / Avalanche Studios (GDC) | conference_talk | 2019 | 2026-09-10 | Avalanche engine (Just Cause 4) | cross-platform | session 'Overview' text | verified_fetched |
| SRC-FUNC-072 | NVIDIA PhysX SDK | NVIDIA | official_documentation | 2026 | 2026-09-10 | PhysX 5 (open source) | cross-platform | sections 'NVIDIA PhysX' intro and 'Key Benefits' | verified_fetched |
| SRC-FUNC-073 | Component (Game Programming Patterns) | Robert Nystrom | book | 2014 | 2026-09-10 | n/a | cross-platform | chapter 'Component' | verified_fetched |
| SRC-FUNC-074 | Object Pool (Game Programming Patterns) | Robert Nystrom | book | 2014 | 2026-09-10 | n/a | cross-platform | chapter 'Object Pool' | verified_fetched |
| SRC-FUNC-075 | Spatial Partition (Game Programming Patterns) | Robert Nystrom | book | 2014 | 2026-09-10 | n/a | cross-platform | chapter 'Spatial Partition' | verified_fetched |
| SRC-FUNC-076 | Game Loop (Game Programming Patterns) | Robert Nystrom | book | 2014 | 2026-09-10 | n/a | cross-platform | chapter 'Game Loop' | verified_fetched |
| SRC-FUNC-077 | Cyberpunk 2077: Technology Preview Of New Ray Tracing Overdrive Mode Out Now | Andrew Burnes / NVIDIA | engineering_blog | 2023-04-11 | 2026-09-10 | REDengine 4 / RTX 40 Series | cross-platform | article body (Ray Tracing: Overdrive Mode, path tracing, DLSS 3, RTXDI) | verified_fetched |
| SRC-FUNC-078 | It Just Works: Ray-Traced Reflections in 'Battlefield V' | Yasin Uludag, Johannes Deligiannis / DICE (GDC) | conference_talk | 2019 | 2026-09-10 | Frostbite / DXR | cross-platform | session 'Overview' text | verified_fetched |
| SRC-FUNC-079 | 'It Just Works': Ray-Traced Reflections in 'Battlefield V' (GTC 2019) | NVIDIA / DICE | conference_talk | 2019 | 2026-09-10 | Frostbite / DXR | cross-platform | slides on ray divergence, DXR primer and Battlefield V release facts | verified_fetched |
| SRC-FUNC-080 | Virtual Shadow Maps in 'Fortnite Battle Royale' Chapter 4 | Andrew Lauritzen, Ola Olsson / Epic Games | engineering_blog | 2023-01-26 | 2026-09-10 | UE 5.1 / Fortnite Chapter 4 | cross-platform | sections on VSM-Nanite coupling, caching challenges, coarse pages and one-pass projection (1.56 ms -> 1.08 ms) | verified_fetched |
| SRC-FUNC-081 | Visibility Preprocessing for Interactive Walkthroughs | Seth J. Teller, Carlo H. Sequin (SIGGRAPH 1991) | academic_paper | 1991 | 2026-09-10 | n/a (algorithmic) | cross-platform | Abstract and the interactive walkthrough phase description (cells, portals, adjacency graph, eye-to-cell visibility) | verified_fetched |
| SRC-FUNC-082 | Anti-cheat middleware (PCGamingWiki) | PCGamingWiki community | secondary | 2026 | 2026-09-10 | n/a | cross-platform | sections 'Anti-cheat middleware' intro and 'nProtect GameGuard' | verified_fetched |
| SRC-FUNC-083 | Set up split-screen rendering in URP (Unity Manual) | Unity Technologies | official_documentation | 2024 | 2026-09-10 | Unity 6.0 (6000.0) / URP | cross-platform | section 'Set up split-screen rendering in URP' | verified_fetched |
| SRC-FUNC-084 | Sci-fi and fantasy worlds collide in UE5-powered co-op adventure Split Fiction | Epic Games / Hazelight Studios (interview with Josef Fares and Jonas Mauritzsson) | interview | 2025-02-25 | 2026-09-10 | Unreal Engine 5 / Split Fiction | cross-platform | Q&A on split-screen co-op technical challenges and the custom capabilities system | verified_fetched |
| SRC-GCS-001 | Background loading | Godot Engine documentation team | official_documentation | 2026 | 2026-09-10 | Godot 4.x (stable docs, 2026-06/08 crawl) | Windows / Linux / macOS / mobile / web | Sections 'Background loading', 'Using ResourceLoader' | verified_fetched |
| SRC-GCS-002 | Global illumination | Godot Engine documentation team | official_documentation | 2026 | 2026-09-10 | Godot 4.x (stable docs, 2026-06/08 crawl) | Forward+ / Mobile / Compatibility renderers | Page TOC listing 'Using Voxel global illumination', 'Signed distance field global illumination (SDFGI)', 'Using Lightmap global illumination' | verified_fetched |
| SRC-GCS-003 | Using Voxel global illumination | Godot Engine documentation team | official_documentation | 2026 | 2026-09-10 | Godot 4.x (stable docs, 2026-06/08 crawl) | Forward+ renderer only | Sections 'Using Voxel global illumination', 'VoxelGI node properties', 'VoxelGI interaction with lights and objects' | verified_fetched |
| SRC-GCS-004 | Signed distance field global illumination (SDFGI) | Godot Engine documentation team | official_documentation | 2026 | 2026-09-10 | Godot 4.x (stable docs, 2026-06/08 crawl) | Forward+ renderer only | Sections 'Signed distance field global illumination (SDFGI)', 'Environment SDFGI properties' (Cascades, Min Cell Size, Use Occlusion, Bounce Feedback) | verified_fetched |
| SRC-GCS-005 | Using Lightmap global illumination | Godot Engine documentation team | official_documentation | 2026 | 2026-09-10 | Godot 4.x (stable docs, 2026-06/08 crawl) | all renderers incl. mobile/web (bake on desktop only) | Sections 'Using Lightmap global illumination' (intro), 'Setting up' (UV2, Lightmap Texel Size default 0.2) | verified_fetched |
| SRC-GCS-006 | Particle systems (3D) | Godot Engine documentation team | official_documentation | 2026 | 2026-09-10 | Godot 4.x (stable docs, 2026-06/08 crawl) | GPU particles require modern GPU; CPU particles wider hardware support | Section 'Node overview' (GPUParticles3D vs CPUParticles3D, attractor and collision nodes) | verified_fetched |
| SRC-GCS-007 | Optimization using MultiMeshes | Godot Engine documentation team | official_documentation | 2026 | 2026-09-10 | Godot 4.x (stable docs, 2026-06/08 crawl) | all renderers | Sections 'MultiMeshes', example 'extends MultiMeshInstance3D' (instance_count / visible_instance_count) | verified_fetched |
| SRC-GCS-008 | High-level multiplayer | Godot Engine documentation team | official_documentation | 2026 | 2026-09-10 | Godot 4.x (stable docs, 2026-06/08 crawl) | cross-platform; HTML5 limited to WebSocket/WebRTC | Sections 'Mid-level abstraction', 'Hosting considerations', 'Initializing the network', 'Managing connections', 'Remote procedure calls' | verified_fetched |
| SRC-GCS-009 | Occlusion culling | Godot Engine documentation team | official_documentation | 2026 | 2026-09-10 | Godot 4.x (stable docs, 2026-06/08 crawl) | all renderers (biggest win on Mobile) | Sections 'Why use occlusion culling', 'How occlusion culling works in Godot', 'Setting up occlusion culling' | verified_fetched |
| SRC-GCS-010 | Mesh level of detail (LOD) | Godot Engine documentation team | official_documentation | 2026 | 2026-09-10 | Godot 4.x (stable docs, 2026-06/08 crawl) | all renderers | Sections 'Introduction', 'Generating mesh LOD', 'Configuring mesh LOD performance and quality', 'Using mesh LOD with MultiMesh and particles' | verified_fetched |
| SRC-GCS-011 | Visibility ranges (HLOD) | Godot Engine documentation team | official_documentation | 2026 | 2026-09-10 | Godot 4.x (stable docs, 2026-06/08 crawl) | all renderers | Sections 'How it works', 'Visibility range properties', 'Fade mode' | verified_fetched |
| SRC-GCS-012 | Optimization using Servers | Godot Engine documentation team | official_documentation | 2026 | 2026-09-10 | Godot 4.x (stable docs, 2026-06/08 crawl) | all platforms | Sections 'Optimization using Servers', 'Servers', 'RIDs' (including the RID reference-counting warning) | verified_fetched |
| SRC-GCS-013 | The Profiler | Godot Engine documentation team | official_documentation | 2026 | 2026-09-10 | Godot 4.x (stable docs, 2026-06/08 crawl) | editor-only (debug builds) | Sections 'An overview of the profiler', 'The measured data' (frame time, physics frame, idle time, physics time; 16.66 ms default) | verified_fetched |
| SRC-GCS-014 | 3D lights and shadows | Godot Engine documentation team | official_documentation | 2026 | 2026-09-10 | Godot 4.x (stable docs, 2026-06/08 crawl) | Forward+ / Mobile / Compatibility | Sections 'Shadow mapping', 'Directional light', 'Directional shadow mapping' (PSSM, 4 splits, 8 DirectionalLights limit, Angular Distance) | verified_fetched |
| SRC-GCS-015 | Using NavigationServer | Godot Engine documentation team | official_documentation | 2026 | 2026-09-10 | Godot 4.x (stable docs, 2026-06/08 crawl) | all platforms | Sections 'Threading and Synchronization', 'Waiting for synchronization' | verified_fetched |
| SRC-GCS-016 | Using multiple threads | Godot Engine documentation team | official_documentation | 2026 | 2026-09-10 | Godot 4.x (stable docs, 2026-06/08 crawl) | all platforms | Sections 'Threads', 'Creating a Thread' (warning about slow thread creation on Windows, mutex cost), 'Mutexes' | verified_fetched |
| SRC-GCS-017 | Thread-safe APIs | Godot Engine documentation team | official_documentation | 2026 | 2026-09-10 | Godot 4.x (stable docs, 2026-06/08 crawl) | all platforms | Sections 'Global scope', 'Scene tree', 'Rendering', 'Physics', 'Navigation', 'Resources' | verified_fetched |
| SRC-GCS-018 | GPUParticles3D class reference | Godot Engine documentation team | secondary | 2026 | 2026-09-10 | Godot 4.x (stable docs, 2026-06/08 crawl) | Forward+ / Mobile / Compatibility | Class description and Property Descriptions for amount, amount_ratio, fixed_fps, interpolate, fract_delta, collision_base_size, MAX_DRAW_PASSES, visibility_aabb | verified_fetched |
| SRC-GCS-019 | MultiMeshInstance3D class reference | Godot Engine documentation team | secondary | 2026 | 2026-09-10 | Godot 4.x (stable docs, 2026-06/08 crawl) | all renderers | Class description ('Fastest way to render the same mesh in large quantities') | verified_fetched |
| SRC-GCS-020 | WorkerThreadPool class reference | Godot Engine documentation team | secondary | 2026 | 2026-09-10 | Godot 4.x (stable docs, 2026-06/08 crawl) | all platforms | Class description; Methods add_task / add_group_task (tasks_needed = -1); Note on negative performance impact | verified_fetched |
| SRC-GCS-021 | PhysicsServer3D class reference | Godot Engine documentation team | secondary | 2026 | 2026-09-10 | Godot 4.x (stable docs, 2026-06/08 crawl) | all platforms | Class description (space / shape / body / area / joint model; nodes use the server internally) | verified_fetched |
| SRC-GCS-022 | NavigationServer3D class reference | Godot Engine documentation team | secondary | 2026 | 2026-09-10 | Godot 4.x (stable docs, 2026-06/08 crawl) | all platforms | Class description (Experimental marker; edge_connection_margin; collision avoidance ignores regions; sync-phase execution) | verified_fetched |
| SRC-GCS-023 | ResourceLoader class reference | Godot Engine documentation team | secondary | 2026 | 2026-09-10 | Godot 4.x (stable docs, 2026-06/08 crawl) | all platforms | Methods load_threaded_request (use_sub_threads, cache_mode), load_threaded_get, load_threaded_get_status; enums ThreadLoadStatus and CacheMode | verified_fetched |
| SRC-GCS-024 | Using physics interpolation | Godot Engine documentation team | official_documentation | 2026 | 2026-09-10 | Godot 4.x (stable docs, 2026-06/08 crawl) | Godot 4.4+ (project setting 'Physics Interpolation') | Sections 'Turn on the physics interpolation setting', 'Move (almost) all game logic from _process to _physics_process' | verified_fetched |
| SRC-GCS-025 | Performance class reference | Godot Engine documentation team | secondary | 2026 | 2026-09-10 | Godot 4.x (stable docs, 2026-06/08 crawl) | all platforms | Class description and Notes (debug-only monitors, up to 1 second update delay); Monitor enum TIME_FPS/TIME_PROCESS/TIME_PHYSICS_PROCESS/TIME_NAVIGATION_PROCESS | verified_fetched |
| SRC-GCS-026 | DirectionalLight3D class reference | Godot Engine documentation team | secondary | 2026 | 2026-09-10 | Godot 4.x (stable docs, 2026-06/08 crawl) | Forward+ / Mobile / Compatibility | ShadowMode enum (SHADOW_ORTHOGONAL / SHADOW_PARALLEL_2_SPLITS / SHADOW_PARALLEL_4_SPLITS) and shadow properties | verified_fetched |
| SRC-GCS-027 | MultiplayerAPI class reference | Godot Engine documentation team | secondary | 2026 | 2026-09-10 | Godot 4.x (stable docs, 2026-06/08 crawl) | all platforms | Class description; inherited by SceneMultiplayer and MultiplayerAPIExtension; SceneTree.set_multiplayer() override | verified_fetched |
| SRC-GCS-028 | OccluderInstance3D class reference | Godot Engine documentation team | secondary | 2026 | 2026-09-10 | Godot 4.x (stable docs, 2026-06/08 crawl) | all renderers | Class description (CPU parallel rasterisation with Embree, mostly-static system, background recomputation) | verified_fetched |
| SRC-GCS-029 | ENetMultiplayerPeer class reference | Godot Engine documentation team | secondary | 2026 | 2026-09-10 | Godot 4.x (stable docs, 2026-06/08 crawl) | all platforms (UDP) | Class description; create_server(port, max_clients = 32, max_channels = 0, in_bandwidth = 0, out_bandwidth = 0); create_mesh | verified_fetched |
| SRC-GCS-030 | Controlling thousands of fish with Particles (godot-docs source, RST) | Godot Engine documentation team | official_documentation | 2026 | 2026-09-10 | Godot 4.x (stable docs, 2026-06/08 crawl) | all renderers | Section 'Controlling thousands of fish with Particles' (particle shader start()/process(), TRANSFORM/COLOR/CUSTOM persistence) | verified_fetched |
| SRC-GCS-031 | Godot Engine Showcase | Godot Engine project | vendor_press_release | 2026 | 2026-09-10 | Godot 4.x (stable docs, 2026-06/08 crawl) | Windows / Mac / Linux / Web / Android / iOS / consoles / VR | Showcase listing 'Made with Godot' (e.g. 'Slay the Spire 2 - Mega Crit', 'Cassette Beasts - Bytten Studio', 'Brotato - Blobfish', 'Cruelty Squad - Consumer Softproducts') | verified_fetched |
| SRC-GCS-032 | Godot 4.0 sets sail: All aboard for new horizons | Godot Engine project (release announcement) | vendor_press_release | 2023-03-01 | 2026-09-10 | Godot 4.0 | cross-platform | Sections 'Global illumination' (SDFGI, VoxelGI replaces GIProbe), 'Navigation Server-Based Navigation System', 'Networking & Multiplayer', 'Physics / Game-Specific Physics Engine', 'Multithreading & Performance Optimization', 'automatic occlusion culling / automatic mesh LOD / manual HLOD visibility | verified_fetched |
| SRC-GCS-033 | Voxel-Based Global Illumination (SVOGI) | Crytek GmbH (CRYENGINE V Manual) | official_documentation | CRYENGINE 5.x manual | 2026-09-10 | CRYENGINE 5.x | PC / Xbox One | Sections 'Overview', 'How It Works', 'Performance' (3-4 ms Xbox One, 2-3 ms average PC, <2 ms AO-only), 'Current Limitations' | verified_fetched |
| SRC-GCS-034 | Volumetric Fog | Crytek GmbH (CRYENGINE V Manual) | official_documentation | CRYENGINE 5.x manual | 2026-09-10 | CRYENGINE 5.x | PC / consoles | Sections 'Overview' (voxel buffer, ray-marching vs analytical fog), 'Volumetric Fog', 'Sun Radial Scattering Setup'; CVar e_VolumetricFog | verified_fetched |
| SRC-GCS-035 | Vegetation 02 Grass (Merged Meshes) - CRYENGINE | Crytek GmbH (CRYENGINE V Manual tutorial) | official_documentation | CRYENGINE 5.x manual | 2026-09-10 | CRYENGINE 5.x | PC | Sections 'Asset Setup in CRYENGINE', 'Material Settings' (Vegetation shader/surface type), 'Opacity Settings' (AlphaTest 40) | verified_fetched |
| SRC-GCS-036 | Bending Setup (CRYENGINE 3 Manual, Vegetation) | Crytek GmbH | official_documentation | CRYENGINE 3.5+ manua | 2026-09-10 | CRYENGINE 3.5+ | PC / consoles | Sections 'Overview' (Touch / Detail / Automerged bending), 'AutoMerged Vegetation' (e_MergedMeshes 0/1, drawcall reduction, sector merging) | verified_fetched |
| SRC-GCS-037 | CRYENGINE 5.7 Documentation mirror - Vegetation 02 Grass (Merged Meshes) | Crytek GmbH docs mirrored by GitHub user z060142 | secondary | 2026 (mirror of CRYE | 2026-09-10 | CRYENGINE 5.7 | PC | Section 'Overview' (MM combines vegetation/physics/explosions/wind; simplistic geometry required; 'Scene from Crysis 3 merged mesh grass') | verified_fetched |
| SRC-GCS-038 | Audio & Occlusion | Crytek GmbH (CRYENGINE V Manual) | official_documentation | CRYENGINE 5.x manual | 2026-09-10 | CRYENGINE 5.x | PC / consoles | Sections 'Overview' (SoundObstructionType: Ignore / SingleRay / MultipleRay), 'Sound Obstruction/Occlusion', 'Obstruction'; CVar s_OcclusionMaxDistance = 150 example | verified_fetched |
| SRC-GCS-039 | CRYENGINE 5.7 Documentation mirror - Procedural Volumetric Clouds | Crytek GmbH docs mirrored by GitHub user z060142 | secondary | 2026 (mirror of CRYE | 2026-09-10 | CRYENGINE 5.7 | PC / consoles | Sections 'Overview', 'Usage' (r_VolumetricClouds, e_Clouds), 'CloudBlocker entity' (up to 4 per level), 'CVars' (r_VolumetricCloudsRaymarchStepNum default 64, range 16-256; shadow resolution 64) | verified_fetched |
| SRC-GCS-040 | Touch Bending (CRYENGINE 3 Manual, Vegetation) | Crytek GmbH | official_documentation | CRYENGINE 3 manual ( | 2026-09-10 | CRYENGINE 3.x | PC / consoles | Sections 'Overview' (rope setup, merged mesh deform alternative), 'Setup of Instances (UV Layout)', 'Joint Setup', 'Naming Convention', 'Volume Proxy' | verified_fetched |
| SRC-GCS-041 | Voxel-Based Global Illumination (CRYENGINE 3 Manual) | Crytek GmbH | official_documentation | CRYENGINE 3 manual ( | 2026-09-10 | CRYENGINE 3.x | PC / Xbox One | Sections 'Performance' (4-5 ms Xbox One, 2-3 ms on GTX 780, ~2.5 ms AO-only on Xbox One), parameter table (Diffuse cone width, Cone max length, Min node size, VoxelPoolResolution, Low spec mode) | verified_fetched |
| SRC-GCS-042 | CRYENGINE 5.7 Documentation mirror - Audio CVars & Console Commands | Crytek GmbH docs mirrored by GitHub user z060142 | secondary | 2026 (mirror of CRYE | 2026-09-10 | CRYENGINE 5.7 | PC / consoles | Sections 's_OcclusionAccumulate', 's_OcclusionGlobalType' (0-5 granularity), 's_OcclusionHighDistance' (default 10 m), 's_DrawDebug' occlusion ray flags | verified_fetched |
| SRC-GCS-043 | CryEngine (encyclopedia article) | Wikipedia contributors | secondary | 2026 (article revisi | 2026-09-10 | CRYENGINE 5.7.1 | cross-platform | Infobox 'latest release version 5.7.1'; body text on Warhorse Studios' modified CryEngine for Kingdom Come: Deliverance and on Sniper: Ghost Warrior 2 / SNOW | verified_fetched |
| SRC-GCS-044 | Valve Vulkan Session (GDC 2015, Khronos session deck) | Valve Corporation / Khronos Group | conference_talk | 2015-03 | 2026-09-10 | Vulkan alpha (2015), Source 2 | Windows / Linux (Steam Machines) | Slide 18 'Vulkan is here' ('Source 2 supports Vulkan alpha today', Valve Intel driver, Steam Machines); slides 13-17 (multi-threading, SPIR-V, command buffers, developer responsibility) | verified_fetched |
| SRC-GCS-045 | Counter-Strike 2 update notes (Steam news API for app 730) | Valve Corporation | vendor_press_release | 2025-09-26 / 2026-01 | 2026-09-10 | Counter-Strike 2 (Source 2) | Windows / Linux | News item gid 1811772772259703 (2025-09-26): 'sv_subtick_movement_view_angles will now only send subtick view angles to the server with other subtick events...' and 'Enabled Vulkan defragmentation to help alleviate texture streaming overhead'; gid 1822556746157780 (2026-01-21): 'Landing time is now | verified_fetched |
| SRC-GCS-046 | source-sdk-2013 - src/public/bspfile.h | Valve Corporation (Source SDK 2013) | open_source | 2013 (SDK release), | 2026-09-10 | Source SDK 2013 | Windows / Linux | Lump enum (LUMP_VISIBILITY=4, LUMP_NODES=5, LUMP_LEAFS=10, LUMP_AREAS=20, LUMP_AREAPORTALS=21); struct dvis_t (DVIS_PVS/DVIS_PAS, numclusters, bitofs); struct dareaportal_t (m_PortalKey, otherarea, m_FirstClipPortalVert, m_nClipPortalVerts, planenum) and its 'when portals are closed' comment | verified_fetched |
| SRC-GCS-047 | source-sdk-2013 - src/public/vphysics_interface.h | Valve Corporation (Source SDK 2013) | open_source | 2013 (SDK release), | 2026-09-10 | Source SDK 2013, VPhysics031 | Windows / Linux | VPHYSICS_INTERFACE_VERSION 'VPhysics031'; abstract_class IPhysicsEnvironment (SetGravity in in/s^2, SetAirDensity in kg/m^3, CreatePolyObject/Static/Sphere, CreateFluidController, CreateSpring, ragdoll/hinge/fixed/sliding/ballsocket/pulley/length constraints, Simulate(deltaTime), Get/SetSimulationTi | verified_fetched |
| SRC-GCS-048 | source-sdk-2013 - src/public/tier0/vprof.h | Valve Corporation (Source SDK 2013) | open_source | 2013 (SDK release), | 2026-09-10 | Source SDK 2013 | Windows / Linux / X360 | Header comment 'Real-Time Hierarchical Profiling'; '#define MAXCOUNTERS 256'; '#define VPROF_ENABLED' (all configs except X360 Retail); VPROF_BUDGETGROUP_* budget groups; VPROF_PIX / VPROF_VTUNE_GROUP | verified_fetched |
| SRC-GCS-049 | source-sdk-2013 - src/game/client/prediction.cpp | Valve Corporation (Source SDK 2013) | open_source | 2013 (SDK release), | 2026-09-10 | Source SDK 2013 | Windows / Linux | Top-of-file ConVars: cl_predictweapons ('1'), cl_lagcompensation ('1', 'Perform server side lag compensation of weapon firing events.'), cl_showerror, cl_pred_optimize ('2'); CPrediction members m_nCommandsPredicted / m_nServerCommandsAcknowledged | verified_fetched |
| SRC-GCS-050 | source-sdk-2013 - src/game/client/clientleafsystem.cpp | Valve Corporation (Source SDK 2013) | open_source | 2013 (SDK release), | 2026-09-10 | Source SDK 2013 | Windows / Linux | ConVars r_PortalTestEnts ('1', 'Clip entities against portal frustums.'), r_portalsopenall ('0', 'Open all portals'), cl_threaded_client_leaf_system ('0'); class CClientLeafSystem (leaf enumeration, translucent leaf computation, shadow projection) | verified_fetched |
| SRC-GCS-051 | source-sdk-2013 - src/game/client/vgui_netgraphpanel.cpp | Valve Corporation (Source SDK 2013) | open_source | 2013 (SDK release), | 2026-09-10 | Source SDK 2013 | Windows / Linux | ConVars net_graph, net_graphmsecs ('400', 'The latency graph represents this many milliseconds.'), net_graphshowlatency, net_graphshowinterp, net_scale ('5'), net_graphheight ('64'); '#define NUM_LATENCY_SAMPLES 8'; '#define LERP_HEIGHT 24'; cl_updaterate / cl_cmdrate (ConVar_ServerBounded); cmd_ler | verified_fetched |
| SRC-GCS-052 | source-sdk-2013 - src/game/shared/usercmd.h | Valve Corporation (Source SDK 2013) | open_source | 2013 (SDK release), | 2026-09-10 | Source SDK 2013 | Windows / Linux | class CUserCmd fields command_number, tick_count ('the tick the client created this command'), viewangles, forwardmove/sidemove/upmove, buttons, impulse, weaponselect, random_seed, hasbeenpredicted; GetChecksum() CRC32 over those fields; MakeInert() | verified_fetched |
| SRC-GCS-053 | source-sdk-2013 - src/public/dt_common.h | Valve Corporation (Source SDK 2013) | open_source | 2013 (SDK release), | 2026-09-10 | Source SDK 2013 | Windows / Linux | Defines MAX_DATATABLES 1024, MAX_DATATABLE_PROPS 4096, MAX_ARRAY_ELEMENTS 2048, DT_MAX_STRING_BITS 9, SPROP_ENCODED_AGAINST_TICKCOUNT | verified_fetched |
| SRC-GCS-054 | source-sdk-2013 - src/game/shared/physics_shared.cpp | Valve Corporation (Source SDK 2013) | open_source | 2013 (SDK release), | 2026-09-10 | Source SDK 2013 | Windows / Linux | g_PhysDefaultObjectParams initialiser (mass 1.0, inertia 1.0, damping 0.1, rotdamping 0.1, rotIntertiaLimit 0.05, drag coefficient 1.0, collisions enabled); globals physics / physenv / physenv_main / physcollision / physprops; includes vphysics/object_hash.h, vphysics/friction.h | verified_fetched |
| SRC-GCS-055 | Cassette Beasts Steam news (news API for app 1321440) | Bytten Studio / Raw Fury (published via Steam) | vendor_press_release | 2024-05-20 (Multipla | 2026-09-10 | Cassette Beasts (Godot 3.x/4.x title) | Windows / consoles | News item gid 5747233970433069427 'Multiplayer Update - Now Live!' (2024-05-20); gid 1785774543498342 (patch notes: 'desync errors in multiplayer activities') | verified_fetched |
| SRC-GCS-056 | Brotato Steam news (news API for app 1942280) | Blobfish (published via Steam) | vendor_press_release | 2024-10-25 (Local Co | 2026-09-10 | Brotato (Godot title) | Windows / consoles / mobile | News item gid 6212245217911850965 'Update 1.1' - 'Local multiplayer for up to 4 playe[rs]'; gid 6212245217911850992 'Brotato Local Co-Op Update & Abyssal Terrors DLC - Out Now!' (2024-10-25) | verified_fetched |
| SRC-GCS-057 | Source 2 (encyclopedia article) | Wikipedia contributors | secondary | 2026 (article revisi | 2026-09-10 | Source 2 (Sept 2015) | Windows / Linux / consoles | Infobox 'Release September 2015'; body text: 'the first game to use it, Dota 2, being ported from Source that same year', other titles 'Artifact, Dota Underlords, Half-Life: Alyx, Counter-Strike 2, and Deadlock'; 'Valve also stated that it would support the Vulkan graphics API and use a new in-house | verified_fetched |
| SRC-GCS-058 | Tracy Profiler README | Bartosz Taudul (wolfpld) | open_source | 2026 (master branch, | 2026-09-10 | Tracy (master) | Windows / Linux / macOS / consoles | README body: 'A real time, nanosecond resolution, remote telemetry, hybrid frame and sampling profiler'; CPU support for C/C++/Lua/Python/Fortran; GPU APIs OpenGL, Vulkan, D3D11/12, Metal, OpenCL, CUDA, WebGPU; memory allocations, locks, context switches; tracy.pdf in releases | verified_fetched |
| SRC-GCS-059 | Bevy README | Bevy Foundation / Bevy contributors | open_source | 2026 (main branch, r | 2026-09-10 | Bevy (main) | Windows / Linux / macOS / web | Sections 'What is Bevy?', 'Design Goals' ('Data Focused: Data-oriented architecture using the Entity Component System paradigm', 'Modular: Use only what you need. Replace what you don't like', 'Fast: app logic should run quickly, and when possible, in parallel'); WARNING 'Bevy is still in the early | verified_fetched |
| SRC-GCS-060 | Hazel README | Yan Chernikov (TheCherno) | open_source | 2026 (master branch, | 2026-09-10 | Hazel (master) | Windows | README body: 'Hazel is primarily an early-stage interactive application and rendering engine for Windows. Currently not much is implemented'; 'The Plan' section (Vulkan SDK prerequisite, 2D-then-3D roadmap) | verified_fetched |
| SRC-GCS-061 | The Forge README | The Forge Interactive Inc. | open_source | 2026 (master branch; | 2026-09-10 | The Forge 1.63/1.64 | Windows / Steam Deck / Android / iOS / macOS / Quest / consoles | Sections 'Game Layer / App / Renderer - Scene (not provided) / Resource Streaming (not provided) / Resource Loading / Animation'; 'What is not there: Physics / Networking / Sound'; 'Resource Loader capable to load textures, buffers and geometry data asynchronously'; 'Fast Entity Component System bas | verified_fetched |
| SRC-GCS-062 | EnTT README | Michele Caini (skypjack) | open_source | 2026 (master branch, | 2026-09-10 | EnTT (master) | cross-platform | README intro: 'header-only, tiny and easy to use library for game programming'; 'it's used in Minecraft by Mojang, the ArcGIS Runtime SDKs by Esri and the amazing Ragdoll' | verified_fetched |
| SRC-GCS-063 | FrameGraph README | Andrey Zhirnov (azhirnov) | open_source | 2026 (master branch, | 2026-09-10 | FrameGraph (master) | Windows / Linux / Android | Sections 'Features' (multithreaded command buffer building and submission; hides memory allocation, host-device transfers, synchronizations; async compute and async transfer queues; all render tasks are stateless), 'Used vulkan features and extensions' | verified_fetched |
| SRC-GCS-064 | FrameGraph - docs/Multithreading.md | Andrey Zhirnov (azhirnov) | open_source | 2026 (master branch, | 2026-09-10 | FrameGraph (master) | Windows / Linux / Android | Sections 'Validation' (FG_ENABLE_DATA_RACE_CHECK), 'CPU thread synchronization examples' (Begin/Execute/Flush, AddDependency, double buffering), 'Resource creation and destruction' (ReleaseResource, Wait) | verified_fetched |
| SRC-GCS-065 | FrameGraph - docs/Introduction.md | Andrey Zhirnov (azhirnov) | open_source | 2026 (master branch, | 2026-09-10 | FrameGraph (master) | Windows / Linux / Android | Sections 'Initialization' (IFrameGraph::CreateFrameGraph, CreateSwapchain), 'Shader compilation' (IPipelineCompiler extension, VKSL/SPIRV/GLSL formats) | verified_fetched |
| SRC-GCS-066 | Bevy ECS README | Bevy Foundation / Bevy contributors | open_source | 2026 (main branch, r | 2026-09-10 | bevy_ecs (main) | Windows / Linux / macOS / web | Sections 'What is Bevy ECS?' ('aims to be simple to use, ergonomic, fast, massively parallel, opinionated, and featureful'), 'ECS', 'Concepts' (Components are normal Rust structs, stored in a World) | verified_fetched |
| SRC-GCS-067 | Bevy Tasks README | Bevy Foundation / Bevy contributors | open_source | 2026 (main branch, r | 2026-09-10 | bevy_tasks (main) | Windows / Linux / macOS / web (Wasm single-threaded) | README body: 'simple threadpool with minimal dependencies. The main usecase is a scoped fork-join'; 'makes no attempt to ensure fairness or ordering of spawned tasks'; 'three different thread pools' - ComputeTaskPool, AsyncComputeTaskPool, IoTaskPool, selected by latency requirements | verified_fetched |
| SRC-GCS-068 | mimalloc readme | Microsoft Research (Daan Leijen) | open_source | 2026 (main branch; l | 2026-09-10 | mimalloc v3.4.5 | Windows / macOS / Linux / WASM / BSD / Haiku / MUSL | README body: 'free list sharding' (per mimalloc page, 'usually 64KiB on a 64-bit system'), 'free list multi-sharding', 'eager page purging', 'secure' mode ('performance penalty is usually around 10% on average'), 'bounded space overhead (~0.2% meta-data)' | verified_fetched |
| SRC-HE-001 | HeroEngine (official product homepage) | Idea Fabrik Plc / Laniatus LLC | official_documentation | 2024 | 2026-09-11 | HeroEngine 3.0 (page footer) | Windows PC / cloud | Footer line: 'Last Updated: 09.27.2024 12:20 PM Version: 3.0'; copyright line naming Idea Fabrik Plc and Laniatus LLC | verified_fetched |
| SRC-HE-002 | HeroEngine (encyclopedia article) | Wikipedia contributors | secondary | 2026 | 2026-09-11 | HeroEngine 2.074 | Windows, macOS | Infobox 'Stable release 2.074 / January 19, 2024'; sections 'Features', 'HeroCloud', 'Games developed using HeroEngine' | verified_fetched |
| SRC-HE-003 | BioWare Licenses HeroEngine For Star Wars: The Old Republic MMO | Game Developer (Gamasutra), Eric Caoili | secondary | 2008-12-10 | 2026-09-11 | HeroEngine (2008, pre-1.x) | Windows PC | Body paragraph beginning 'MMO technology company Simutronics and BioWare announced'; quote by Gordon Walton, BioWare co-studio director | verified_fetched |
| SRC-HE-004 | HeroEngine - The Cloud-Based MMO Game Engine Behind SWTOR | MYCPLUS (Muhammad Saqib) | secondary | 2020-08-07 | 2026-09-11 | HeroEngine 2.x | Windows PC | Sections 'Licensing and Pricing', 'Is HeroEngine Still Used Today?', 'Games Made with HeroEngine' | verified_fetched |
| SRC-HE-005 | HeroEngine homepage (Internet Archive snapshot, 2013) | Idea Fabrik Plc | official_documentation | 2013 | 2026-09-11 | HeroEngine 1.x era | Windows PC / cloud | Homepage banner block 'GET THE HEROENGINE, NOW FOR ONLY $99 A YEAR' and bullet list 'UP AND RUNNING in the cloud immediately'; footer 'Wiki' link to hewiki.heroengine.com | verified_fetched |
| SRC-HE-006 | HeroBlade \| HeroEngine (Internet Archive snapshot, 2014) | Idea Fabrik Plc | official_documentation | 2013 | 2026-09-11 | HeroEngine 1.x era | Windows PC | Sections 'All-in-one Development Environment', 'Massively Collaborative', 'Some of HeroBlade's Integrated Features', 'Project Management Tools', 'Asset Library', 'HeroSense' | verified_fetched |
| SRC-HE-007 | World Building \| HeroEngine (Internet Archive snapshot, 2013-12-27) | Idea Fabrik Plc | official_documentation | 2013 | 2026-09-11 | HeroEngine 1.x era | Windows PC | Sections 'Real-time Collaborative World Building', 'Seamless Worlds', 'Terrain and Heightmaps', 'Texture Layers', 'Seamless World and Instances', 'Dynamic Light and Environmental Schemes' | verified_fetched |
| SRC-HE-008 | Server Systems \| HeroEngine (Internet Archive snapshot, 2013) | Idea Fabrik Plc | official_documentation | 2013 | 2026-09-11 | HeroEngine 1.x era | Windows / Linux (CentOS) server | Intro paragraphs ('Segregate your geography into individual area servers...'), sections 'Data Replication System', 'Live Update and World Push', 'Physics Server', 'Master Control Console' | verified_fetched |
| SRC-HE-009 | Game Systems \| HeroEngine (Internet Archive snapshot, 2013) | Idea Fabrik Plc | official_documentation | 2013 | 2026-09-11 | HeroEngine 1.x era | Windows PC / server | Sections 'Game Systems Built for Real-Time Environments', 'HeroScript', 'MMO Foundation Framework' | verified_fetched |
| SRC-HE-010 | Licensing Options \| HeroEngine (Internet Archive snapshot, 2013) | Idea Fabrik Plc | official_documentation | 2013 | 2026-09-11 | HeroEngine 1.x era | Windows PC / cloud | Sections 'HeroCloud: HeroEngine in the Cloud, ONLY $99 a year' and 'HeroEngine Source Code' | verified_fetched |
| SRC-HE-011 | HEWIKI Main Page (Internet Archive snapshot, 2014; page last modified 2013-02-08) | Idea Fabrik Plc | official_documentation | 2013 | 2026-09-11 | HeroEngine / HeroCloud documentation wiki | Windows PC / server | Navigation sections 'World Building', 'Scripting', 'Engine Architecture Level Information'; Scripting page list ('Your First HSL Script', 'HSL for programmers', 'Commands Syntax Reference', 'Script Entry Points') | verified_fetched |
| SRC-HE-012 | Scalability and Building For Massive Multiplayer Audiences (HEWIKI, Internet Archive snapshot; page last modified 2011-10-18) | Idea Fabrik Plc (HEWIKI) | official_documentation | 2011 | 2026-09-11 | HeroEngine 1.x era | Windows / Linux server cluster | Sections 'Terminology', 'Per Physical Server', 'Per Area Instance', 'Instancing', 'Designing for Scalability', 'Release-day example' | verified_fetched |
| SRC-HE-013 | HeroCloud Tech Features \| HeroEngine (Internet Archive snapshot, 2014) | Idea Fabrik Plc | official_documentation | 2013 | 2026-09-11 | HeroEngine / HeroCloud | Windows PC / cloud | Blocks 'HeroCloud gets you a license to the HeroEngine for just $99 per year', 'Focus on building your game, not the back end', 'Real time updates' | verified_fetched |
| SRC-HE-015 | SWTOR DirectX 12 Spring 2026 Update (official developer blog) | Broadsword / SWTOR Technical Team | engineering_blog | 2026-03-31 | 2026-09-11 | SWTOR Engine (HeroEngine-derived), DirectX 12 | Windows PC | Section 'Next Steps', paragraph beginning 'SWTOR was originally created in HeroEngine' | verified_fetched |
| SRC-HE-016 | Idea Fabrik, the company behind Hero Engine and The Repopulation, disappears from the internet | Massively Overpowered (Chris Neal) | secondary | 2023-04-29 | 2026-09-11 | HeroEngine (legacy) | Windows PC | Opening paragraphs naming Idea Fabrik as holder of the Hero Engine (originally Simutronics) and describing The Repopulation's Kickstarter, 2014 Steam early access and HeroEngine dispute | verified_fetched |
| SRC-HE-017 | Software:Faxion Online (encyclopedia article, Wikipedia mirror) | HandWiki (mirrors Wikipedia) | secondary | 2022-07-24 | 2026-09-11 | HeroEngine (launch) | Windows PC | Infobox field 'Engine: HeroEngine'; sentence 'It makes use of the engine HeroEngine'; release 26 May 2011, shutdown 24 August 2011 | verified_fetched |
| SRC-HE-018 | Laniatus Cloud Tech (official company site) | Laniatus LLC | vendor_press_release | 2026 | 2026-09-11 | Laniatus in-house engine | Windows PC / cloud | Sections 'We build the engine beneath the game', 'The platform / Engine runtime', 'Our games / PlayM2M' | verified_fetched |
| SRC-HE-019 | PlayM2M on Steam (store page) | Valve / Laniatus LLC | secondary | 2025 | 2026-09-11 | not stated on page | Windows PC | Store metadata block: Developer 'Laniatus LLC', Publisher 'Laniatus LLC', Release Date '28 Mar, 2025', 'Early Access Release Date: 28 Mar, 2025' | verified_fetched |
| SRC-HE-020 | Idea Fabrik PLC (official corporate site) | Idea Fabrik Plc | official_documentation | 2017 | 2026-09-11 | HeroEngine / HeroCloud | Windows PC / cloud | Blocks 'Agile Development', 'Disruptive Development', 'Game Development' ('We manage servers, bandwidth, hosting, billing, etc.'); news list entry 'Friday, 13 January 2017: Idea Fabrik acquires The Repopulation' | verified_fetched |
| SRC-MPR-001 | Rendering the Hellscape of Doom Eternal (Advances in Real-Time Rendering, SIGGRAPH 2020) | id Software (Geffroy, Gneiting, Wang) | conference_talk | 2020 | 2026-09-10 | id Tech 7 | Windows PC / consoles | slides 3, 4, 9, 14, 24, 44, 45, 49, 53, 57, 62, 66, 72, 76 | verified_fetched |
| SRC-MPR-002 | Exploring Ray Traced Future in Metro Exodus (NVIDIA GTC 2019) | 4A Games / NVIDIA (Shyshkovtsov, Karmalsky, Archard, Zhdan) | conference_talk | 2019 | 2026-09-10 | 4A Engine (DXR) | Windows PC | slides 8, 9, 22, 26, 27, 28, 32, 40, 48, 73, 76, 87 | verified_fetched |
| SRC-MPR-003 | How Northlight makes Alan Wake 2 shine | Remedy Entertainment | engineering_blog | 2023-11-06 | 2026-09-10 | Northlight | Windows PC / PS5 / Xbox Series X\|S | sections 'GPU-driven rendering and meshlets', 'Character-style rigs on foliage', 'Motion Matching', 'Realistic wind', 'Ray tracing' | verified_fetched |
| SRC-MPR-004 | Moving Gears to Tier 2 Variable Rate Shading (DirectX Developer Blog, guest post by The Coalition) | Microsoft / The Coalition (Chris Wallis) | engineering_blog | 2021-01-12 | 2026-09-10 | DirectX 12 Ultimate / UE4 | Windows PC / Xbox Series X\|S | sections 'Moving to Tier 2', 'VRS Texture Generation', 'Working with Dynamic Resolution Scaling', 'Performance Results' | verified_fetched |
| SRC-MPR-005 | Face-Off: Titanfall 2 (Digital Foundry) | Digital Foundry / Eurogamer | secondary | 2016-11-04 | 2026-09-10 | Titanfall 2 engine (Source-derived) | Windows PC / PS4 / Xbox One | section 'Shadow quality', 'PC vs console' | verified_fetched |
| SRC-MPR-006 | Brilliant visuals and growing pains: analysing Unreal Engine 5 first-generation games (Digital Foundry) | Digital Foundry | secondary | 2023-12-30 | 2026-09-10 | UE5 | Windows PC / consoles | sections on Lumen/Nanite/VSM adoption, 'RT quality levels', texture quality | verified_fetched |
| SRC-MPR-007 | Black Myth: Wukong - the PC tech review (Digital Foundry) | Digital Foundry | secondary | 2024-08-20 | 2026-09-10 | UE5 | Windows PC | sections on Nanite, Lumen, virtual shadow maps, full RT / ReSTIR path tracing, GPU particles | verified_fetched |
| SRC-MPR-008 | Lords of the Fallen is a stunning UE5 soulslike with ongoing tech issues (Digital Foundry) | Digital Foundry | secondary | 2023-10-14 | 2026-09-10 | UE5 | Windows PC / PS5 / Xbox Series X\|S | sections on virtual shadow maps, dynamic resolution, volumetric lighting quality modes, FSR2/TAAU | verified_fetched |
| SRC-MPR-009 | Senua's Saga: Hellblade 2 is a defining moment in the evolution of real-time graphics (Digital Foundry) | Digital Foundry | secondary | 2024-05-21 | 2026-09-10 | UE5 | Xbox Series X\|S / Windows PC | sections on Nanite, virtual shadow maps, Lumen, volumetric fog, digital-human hair | verified_fetched |
| SRC-MPR-010 | Senua's Saga: Hellblade 2 PC tech review (Digital Foundry) | Digital Foundry | secondary | 2024-06-14 | 2026-09-10 | UE5 | Windows PC | sections on upscaling/TSR, dynamic resolution, frame generation, graphics menu | verified_fetched |
| SRC-MPR-011 | The AI Systems of Left 4 Dead (GDC 2009) | Valve (Michael Booth) | conference_talk | 2009 | 2026-09-10 | Source engine | Windows PC / Xbox 360 | slides 53-56, 59, 64-75, 78-82 | verified_fetched |
| SRC-MPR-012 | Three States and a Plan: The A.I. of F.E.A.R. (GDC 2006) | Monolith Productions (Jeff Orkin) | conference_talk | 2006 | 2026-09-10 | F.E.A.R. engine (LithTech Jupiter EX) | Windows PC / consoles | pages 1-4, sections 'Managing Complexity', 'FSMs vs Planning' | verified_fetched |
| SRC-MPR-013 | Crowd Pathfinding and Steering Using Flow Field Tiles (Game AI Pro, Chapter 23) | Elijah Emerson (Game AI Pro, CRC Press) | book | 2013 | 2026-09-10 | Supreme Commander 2 engine | Windows PC / Xbox 360 | sections 23.3-23.8, 23.14, 23.15 | verified_fetched |
| SRC-MPR-014 | The Art of Destruction in Rainbow Six: Siege (GDC 2016) | Ubisoft Montreal (Julien L'Heureux) | conference_talk | 2016 | 2026-09-10 | RealBlast / AnvilNext | Windows PC / PS4 / Xbox One | slides 54-55, 57-58, 61-68, 73-74 | verified_fetched |
| SRC-MPR-015 | Massive Crowd on Assassin's Creed Unity: AI Recycling (GDC 2015, session page) | Ubisoft (Francois Cournoyer) / GDC Vault | conference_talk | 2015 | 2026-09-10 | AnvilNext | Windows PC / PS4 / Xbox One | session abstract | verified_fetched |
| SRC-MPR-016 | Continuous World Generation in 'No Man's Sky' (GDC 2017, session page) | Hello Games (Innes McKendrick) / GDC Vault | conference_talk | 2017 | 2026-09-10 | No Man's Sky engine | Windows PC / PS4 / Xbox One | session abstract | verified_fetched |
| SRC-MPR-017 | Graphics Deep Dive: Cascaded voxel cone tracing in The Tomorrow Children (Game Developer / Gamasutra) | Q-Games (James McLaren) / Game Developer | interview | 2016-11-28 | 2026-09-10 | Q-Games engine | PlayStation 4 | sections 'What: Cascaded voxel cone tracing', 'Why: A totally dynamic world' | verified_fetched |
| SRC-MPR-018 | Interactive Indirect Illumination Using Voxel Cone Tracing (Pacific Graphics 2011) | Crassin, Neyret, Sainz, Green, Eisemann / NVIDIA Research | academic_paper | 2011-09 | 2026-09-10 | NVIDIA VXGI | Windows PC | abstract | verified_fetched |
| SRC-MPR-019 | GPU Gems 3, Chapter 13: Volumetric Light Scattering as a Post-Process | Kenny Mitchell / NVIDIA | book | 2007 | 2026-09-10 | GPU Gems 3 | cross-platform | section 13.2 'Crepuscular Rays', 13.6 'Caveats' | verified_fetched |
| SRC-MPR-020 | Decima Engine: Advances in Lighting and AA (Guerrilla, SIGGRAPH 2017 talk page) | Guerrilla Games | conference_talk | 2017-07-31 | 2026-09-10 | Decima | PS4 / PS4 Pro | abstract | verified_fetched |
| SRC-MPR-021 | Streaming the World of Horizon Zero Dawn (Guerrilla talk page) | Guerrilla Games (Jan-Jaap) | conference_talk | 2023-03-21 | 2026-09-10 | Decima | PS4 | abstract | verified_fetched |
| SRC-MPR-022 | GPU-Based Procedural Placement in Horizon Zero Dawn (Guerrilla talk page) | Guerrilla Games (Jaap van Muijden) | conference_talk | 2017-03-01 | 2026-09-10 | Decima | PS4 | abstract | verified_fetched |
| SRC-MPR-023 | Virtual Shadow Maps in Unreal Engine (Epic official documentation) | Epic Games | official_documentation | 2024 | 2026-09-10 | UE 5.4 | Windows PC / consoles | sections 'Shadow Cache Invalidation Behavior', 'Contact Shadows', 'Performance' | verified_fetched |
| SRC-MPR-024 | Lumen Technical Details in Unreal Engine (Epic official documentation) | Epic Games | official_documentation | 2024 | 2026-09-10 | UE 5.4 | Windows PC / consoles | sections 'Surface Cache', 'Radiance Cache', 'Distance Field', 'Software Ray Tracing' | verified_fetched |
| SRC-MPR-025 | Lightmass Basics in Unreal Engine (Epic official documentation) | Epic Games | official_documentation | 2024 | 2026-09-10 | UE 5.4 | Windows PC / consoles | sections 'Lightmass Importance Volume', 'Lightmaps' | verified_fetched |
| SRC-MPR-026 | Optimizing Rendering with PSO Caches in Unreal Engine (Epic official documentation) | Epic Games | official_documentation | 2024 | 2026-09-10 | UE 5.4 | Windows PC / consoles | sections 'Terminology and Supported PSO Types', 'Generate PSO Caches' | verified_fetched |
| SRC-MPR-027 | Scalability in Unreal Engine (Epic official documentation) | Epic Games | official_documentation | 2024 | 2026-09-10 | UE 5.4 | Windows PC / consoles | sections 'Scalability Levels', 'Quality Levels' | verified_fetched |
| SRC-MPR-028 | Dynamic Resolution in Unreal Engine (Epic official documentation) | Epic Games | official_documentation | 2024 | 2026-09-10 | UE 5.4 | Windows PC / consoles | sections 'How Dynamic Resolution Works', 'FAQ' | verified_fetched |
| SRC-MPR-029 | Hierarchical Level of Detail in Unreal Engine (Epic official documentation) | Epic Games | official_documentation | 2024 | 2026-09-10 | UE 5.4 | Windows PC / consoles | section 'Hierarchical Level of Detail' | verified_fetched |
| SRC-MPR-030 | Hair Rendering and Simulation in Unreal Engine (Epic official documentation) | Epic Games | official_documentation | 2024 | 2026-09-10 | UE 5.4 | Windows PC / consoles | sections 'Groom', 'Card-based hair', 'Level of Detail' | verified_fetched |
| SRC-MPR-031 | Water System in Unreal Engine (Epic official documentation) | Epic Games | official_documentation | 2024 | 2026-09-10 | UE 5.4 | Windows PC / consoles | sections 'Water Bodies', 'Simulating Waves Using the Water Waves Asset' | verified_fetched |
| SRC-MPR-032 | Scriptable Render Pipeline Batcher in URP (Unity official documentation) | Unity Technologies | official_documentation | 2024 | 2026-09-10 | Unity 6 / URP & HDRP | cross-platform | sections 'How the SRP Batcher works', 'Requirements and compatibility' | verified_fetched |
| SRC-MPR-033 | Quality Settings (Unity official documentation) | Unity Technologies | official_documentation | 2024 | 2026-09-10 | Unity 6 | cross-platform | sections 'Shadow Cascades', 'Cascade splits', 'Shadowmask mode' | verified_fetched |
| SRC-MPR-034 | Lightmapping (Unity official documentation) | Unity Technologies | official_documentation | 2024 | 2026-09-10 | Unity 6 | cross-platform | sections 'Precalculating surface lighting with lightmaps', 'Baking lightmaps before runtime' | verified_fetched |
| SRC-MPR-035 | The Progressive Lightmapper (Unity official documentation) | Unity Technologies | official_documentation | 2024 | 2026-09-10 | Unity 6 | cross-platform | sections 'Progressive CPU Lightmapper', 'Progressive GPU Lightmapper' | verified_fetched |
| SRC-MPR-036 | Light Probes (Unity official documentation) | Unity Technologies | official_documentation | 2024 | 2026-09-10 | Unity 6 | cross-platform | sections 'Precalculating indirect light with Light Probes', 'Light Probes and moving GameObjects' | verified_fetched |
| SRC-MPR-037 | V Rising: Behind the vampire realm built on 1,600 ECS systems (Unity case study) | Unity Technologies / Stunlock Studios | engineering_blog | 2024-12-09 | 2026-09-10 | Unity DOTS / HDRP | Windows PC / PS5 | sections 'The challenge', 'Scaling up operations with DOTS', results list | verified_fetched |
| SRC-MPR-038 | Using SDFGI (Godot official documentation) | Godot Engine contributors | official_documentation | 2024 | 2026-09-10 | Godot 4 | cross-platform | sections 'Cascades', 'Cascade 0 Distance', 'SDFGI caveats' | verified_fetched |
| SRC-MPR-039 | 2D lights and shadows (Godot official documentation) | Godot Engine contributors | official_documentation | 2024 | 2026-09-10 | Godot 4 | cross-platform | sections 'LightOccluder2D', 'Item Cull Mask', 'Limitations' | verified_fetched |
| SRC-MPR-040 | Using LightmapGI (Godot official documentation) | Godot Engine contributors | official_documentation | 2024 | 2026-09-10 | Godot 4 | cross-platform | sections 'LightmapGI', 'Shadowmasking' | verified_fetched |
| SRC-MPR-041 | Variable Rate Shading (Microsoft Direct3D 12 documentation) | Microsoft | secondary | 2023 | 2026-09-10 | Direct3D 12 | Windows PC / Xbox Series X\|S | sections 'Variable Rate Shading Tiers', 'Shading Rate Image' | verified_fetched |
| SRC-MPR-042 | DirectStorage overview (Microsoft Game Development Kit documentation) | Microsoft | official_documentation | 2024 | 2026-09-10 | Microsoft GDK / DirectStorage | Windows PC / Xbox Series X\|S | sections 'DirectStorage overview', 'Decompression' | verified_fetched |
| SRC-MPR-043 | GPU Lightmass Global Illumination in Unreal Engine (Epic official documentation) | Epic Games | official_documentation | 2024 | 2026-09-10 | UE 5.4 | Windows PC | sections 'GPU Lightmass', 'Enabling GPU Lightmass' | verified_fetched |
| SRC-MPR-044 | Distance Field Soft Shadows in Unreal Engine (Epic official documentation) | Epic Games | official_documentation | 2024 | 2026-09-10 | UE 5.4 | Windows PC / consoles | sections 'Distance Field Soft Shadows', 'Distance Field Ambient Occlusion' | verified_fetched |
| SRC-MPR-045 | Saving and Loading Your Game in Unreal Engine (Epic official documentation) | Epic Games | official_documentation | 2024 | 2026-09-10 | UE 5.4 | Windows PC / consoles | sections 'SaveGame', 'SaveGameToSlot', 'Async Saving' | verified_fetched |
| SRC-MPR-046 | Audio Mixer Overview in Unreal Engine (Epic official documentation) | Epic Games | official_documentation | 2024 | 2026-09-10 | UE 5.4 | Windows PC / consoles | sections 'Audio Mixer', 'Sound Waves' | verified_fetched |
| SRC-MPR-047 | Gameplay Ability System in Unreal Engine (Epic official documentation) | Epic Games | official_documentation | 2024 | 2026-09-10 | UE 5.4 | Windows PC / consoles | sections 'Gameplay Abilities', 'Gameplay Effects', 'Gameplay Attributes' | verified_fetched |
| SRC-MPR-048 | The creators of the Havok engine discouraged the authors of Red Faction: Guerrilla from destructibility, calling it impossible (Studio AtticSalt) | Studio AtticSalt (Aaron Hall), reporting an interview with Eric Arnold | secondary | 2026-09-08 | 2026-09-10 | Geo-Mod 2.0 / Havok | Windows PC / PS3 / Xbox 360 | article body, paragraphs on Geo-Mod 2.0 and its rendering/AI costs | verified_fetched |
| SRC-MPR-049 | Using Light Shafts in Unreal Engine (Epic official documentation) | Epic Games | official_documentation | 2024 | 2026-09-10 | UE 4.x/5.x | Windows PC / consoles | sections 'Occlusion Method', 'Bloom Method', 'GPU Cost' | verified_fetched |
| SRC-MPR-050 | Volumetric Fog in Unreal Engine (Epic official documentation) | Epic Games | official_documentation | 2024 | 2026-09-10 | UE 5.4 | Windows PC / consoles | sections 'Volumetric Fog', 'Froxel Grid', 'Performance' | verified_fetched |
| SRC-MPR-051 | Portal developer commentary (Portal Wiki transcription of Valve in-game commentary) | Valve (commentary); Portal Wiki transcription | secondary | 2007 | 2026-09-10 | Source engine | Windows PC / consoles | commentary entries on portal rendering and recursive portal views | verified_fetched |
| SRC-MPR-052 | Occlusion Culling (Unity official documentation) | Unity Technologies | official_documentation | 2024 | 2026-09-10 | Unity 6 | cross-platform | sections 'Occlusion Culling', 'Occlusion Culling data' | verified_fetched |
| SRC-MPR-053 | Occlusion culling (Godot official documentation) | Godot Engine contributors | official_documentation | 2024 | 2026-09-10 | Godot 4 | cross-platform | sections 'Why use occlusion culling', 'How occlusion culling works in Godot' | verified_fetched |
| SRC-MPR-054 | Mesh level of detail (LOD) (Godot official documentation) | Godot Engine contributors | official_documentation | 2024 | 2026-09-10 | Godot 4 | cross-platform | sections 'Automatic mesh LOD', 'Visibility ranges (HLOD)' | verified_fetched |
| SRC-MPR-055 | Using physics interpolation (Godot official documentation) | Godot Engine contributors | official_documentation | 2024 | 2026-09-10 | Godot 4 | cross-platform | sections 'What is physics interpolation', 'Setup' | verified_fetched |
| SRC-MPR-056 | Reflections Captures in Unreal Engine (Epic official documentation) | Epic Games | official_documentation | 2024 | 2026-09-10 | UE 5.4 | Windows PC / consoles | sections 'Scene Capture', 'Planar Reflections', 'Reflection Captures' | verified_fetched |
| SRC-MPR-057 | Overview of Niagara Effects in Unreal Engine (Epic official documentation) | Epic Games | official_documentation | 2024 | 2026-09-10 | UE 5.4 | Windows PC / consoles | sections 'Niagara', 'GPU Particles', 'SubUV / Flipbook' | verified_fetched |
| SRC-MPR-058 | Cloth (Unity official documentation) | Unity Technologies | official_documentation | 2024 | 2026-09-10 | Unity 6 | cross-platform | sections 'Cloth component', 'Constraints' | verified_fetched |
| SRC-MPR-059 | Job System overview (Unity official documentation) | Unity Technologies | official_documentation | 2024 | 2026-09-10 | Unity 6 | cross-platform | sections 'Job System', 'Safety system' | verified_fetched |
| SRC-MPR-060 | Sprite Atlas (Unity official documentation) | Unity Technologies | official_documentation | 2024 | 2026-09-10 | Unity 6 | cross-platform | sections 'Sprite Atlas', 'Sprite packing' | verified_fetched |
| SRC-MPR-061 | True Impostors (GPU Gems 3, Chapter 21) | Ryan Geiss / NVIDIA | book | 2007 | 2026-09-10 | GPU Gems 3 | cross-platform | chapter body, section on impostor rendering | verified_fetched |
| SRC-MPR-062 | Baking Normal Maps on the GPU (GPU Gems 3, Chapter 22) | NVIDIA | book | 2007 | 2026-09-10 | GPU Gems 3 | cross-platform | chapter body | verified_fetched |
| SRC-MPR-063 | Chaos Physics Overview in Unreal Engine (Epic official documentation) | Epic Games | official_documentation | 2024 | 2026-09-10 | UE 5.4 | Windows PC / consoles | sections 'Chaos Physics', 'Scene Queries' | verified_fetched |
| SRC-MPR-064 | Motion Matching in Unreal Engine (Epic official documentation) | Epic Games | official_documentation | 2024 | 2026-09-10 | UE 5.4 | Windows PC / consoles | sections 'Motion Matching', 'Pose Search' | verified_fetched |
| SRC-MPR-065 | 3D lights and shadows (Godot official documentation) | Godot Engine contributors | official_documentation | 2024 | 2026-09-10 | Godot 4 | cross-platform | sections 'Shadow mapping', 'Shadow bias' | verified_fetched |
| SRC-MPR-066 | Illuminating Roco's Legacy: Scalable Global Illumination from Theory to Practice (GDC 2026) | Tencent Games / MoreFun Studios (Sheng Feng) | conference_talk | 2026-03 | 2026-09-10 | Unreal Engine 4 (custom) | cross-platform (mobile + PC) | slides 5, 9, 15-17, 23-24, 28-31, 33-34, 36, 52 | verified_fetched |
| SRC-NTA-001 | Source Multiplayer Networking (Valve Developer Community wiki) | Valve / Valve Developer Community | secondary | ongoing; revision ci | 2026-09-10 | Source / Source 2 | PC (Windows/Linux) | Sections: '## Basic networking', '## Servers for these games that support altering Tickrate' -> '#### 64 Tickrate, with Sub-tick', '## Entity interpolation', '## Input prediction', '## Lag compensation', '## Net graph', '## Optimizations' | verified |
| SRC-NTA-002 | Lag Compensation (Valve Developer Community wiki) | Valve / Valve Developer Community | secondary | ongoing; verified 20 | 2026-09-10 | Source (2007 / Alien Swarm and later APIs) | PC | Sections: '# Lag Compensation' (intro paragraph), '## Configuration' (sv_unlag, sv_maxunlag rows), '## Invocation' (StartLagCompensation/FinishLagCompensation code), '## Lag Compensation Type' (LAG_COMPENSATE_BOUNDS / HITBOXES / HITBOXES_ALONG_RAY) | verified |
| SRC-NTA-003 | Latency Compensating Methods in Client/Server In-game Protocol Design and Optimization (Yahn Bernier, GDC 2001) | Yahn Bernier, Valve / Valve Developer Community wiki reprint | secondary | 2001 | 2026-09-10 | Half-Life / GoldSrc era | PC | Linked from the Lag Compensation page ('You may be looking for Yahn Bernier's 2001 paper on game engine networking'); full text not retrieved this pass | available |
| SRC-NTA-004 | 'Overwatch' Gameplay Architecture and Netcode (GDC 2017) | Timothy Ford, Blizzard Entertainment (GDC Vault) | conference_talk | 2017 | 2026-09-10 | Overwatch / in-house engine | PC / console | Session page: 'Session Name: 'Overwatch' Gameplay Architecture and Netcode'; 'Speaker(s): Timothy Ford'; 'Track / Format: Programming'; Overview paragraph | verified |
| SRC-NTA-005 | Replay Technology in 'Overwatch': Kill Cam, Gameplay, and Highlights (GDC 2017) | Philip Orwig, Blizzard Entertainment (GDC Vault) | conference_talk | 2017 | 2026-09-10 | Overwatch / in-house engine | PC / console | Session page title + abstract ('kill cams ... Highlights and plays of the game') | available |
| SRC-NTA-006 | VALORANT's 128-Tick Servers (Riot Games tech blog) | Riot Games | secondary | 2020-08-31 | 2026-09-10 | VALORANT server (Unreal Engine 4 based client) | PC (Linux game servers, 36-core hosts) | Body sections: '# VALORANT's 128-Tick Servers', frame-budget derivation paragraph ('Let's take that 7.8125ms, divide it by 3 gpc ... target budget of just 2.34ms per frame'), animation-cost section, NUMA section, hyperthreading section, 'Ghost Story' section | verified |
| SRC-NTA-007 | Peeking into VALORANT's Netcode (Riot Games tech blog) | Riot Games | secondary | 2020-07-29 | 2026-09-10 | VALORANT (server-authoritative, 128 Hz) | PC | Body sections: server-authoritative note, fixed-timestep paragraph ('exactly 128 times per second'), buffering paragraph ('two frames of server buffering', 'three frames' on client), peeker's-advantage baseline paragraph ('~141ms'), Riot Direct / '~40ms (28%)', 144 FPS '~71ms (a 49% reduction)', hit | verified |
| SRC-NTA-008 | 1500 Archers on a 28.8: Network Programming in Age of Empires and Beyond | Paul Bettner, Ensemble Studios (Game Developer / Gamasutra) | secondary | 2001-03-22 | 2026-09-10 | Genie Engine / Age of Empires 1-2 | PC (Pentium 90, 16MB, 28.8 kbps modem) | Sections: '## Simultaneous Simulations', '## "Speed Control"', '## Guaranteed Delivery', '## Hidden Benefits', '## Hidden Problems', '## Lessons Learned', '## Improvements for Age of Empires 2' | verified |
| SRC-NTA-009 | 1500 Archers on a 28.8 (PDF mirror with tables and diagrams) | Paul Bettner / GameDevs.org upload | secondary | 2001 (PDF upload dat | 2026-09-10 | Genie Engine / Age of Empires | PC | Same section titles as the HTML version; the PDF carries the original GDC tables/figures. No stable page numbers used - located by section title | available |
| SRC-NTA-010 | Fast-Paced Multiplayer (Part I): Client-Server Game Architecture (PDF) | Gabriel Gambetta | secondary | 2013-2014 series; PD | 2026-09-10 | engine-agnostic | PC | Article I body: authoritative server / dumb client section and the 'update loop' pseudo-code | available |
| SRC-NTA-011 | Client-Side Prediction and Server Reconciliation (Fast-Paced Multiplayer Part II) | Gabriel Gambetta | secondary | series; page dated 2 | 2026-09-10 | engine-agnostic | PC | Article body: 'Client-Side Prediction and Server Reconciliation' sections and the sequence diagrams | available |
| SRC-NTA-012 | Counter-Strike 2 official feature page ('What you see is what you get' / sub-tick) | Valve Corporation | secondary | 2023 | 2026-09-10 | Source 2 / Counter-Strike 2 | PC | Section: 'Counter-Strike 2: What you see is what you get' - 'Tick rate no longer matters for moving, shooting, or throwing. Sub-tick updates are the heart of Counter-Strike 2.' | verified |
| SRC-NTA-013 | Sub-tick (Counter-Strike community wiki) | counterstrikewiki.com (community) | secondary | 2023-2026 | 2026-09-10 | Source 2 / Counter-Strike 2 | PC | Sections: 'Mechanics of the Sub-tick System', 'Implementation and Server Performance', 'Network Implications' | available |
| SRC-NTA-014 | Replication Graph in Unreal Engine (UE 5.8 Documentation) | Epic Games / Epic Developer Community | secondary | 2026 (UE 5.8 page); | 2026-09-10 | Unreal Engine 5.8 | PC / server | Sections: '# Replication Graph' (intro with the Fortnite 100 players / ~50,000 replicated Actors example), '## Structure', '## Enabling The System' (DefaultEngine.ini ReplicationDriverClassName), '## High-Level Example' (grid cells, dormant Actors, carried items, always-relevant list, team-reveal li | verified |
| SRC-NTA-015 | Setting Up Dedicated Servers in Unreal Engine (UE 5.8 Documentation) | Epic Games / Epic Developer Community | secondary | 2026 (UE 5.8 page); | 2026-09-10 | Unreal Engine 5.8 (Lyra Starter Game sample) | PC (WindowsServer) | Sections: '## Overview' -> '### Dedicated Server' (headless definition and advantages), '## Tutorial' -> '#### Server' / '#### Client' (Target.cs, Development Server configuration), '### Cook' -> '#### Server Content', '## Test' -> '#### Start the Dedicated Server' (127.0.0.1:7777, -port=) | verified |
| SRC-NTA-016 | Iris Replication System in Unreal Engine (UE 5.8 Documentation) | Epic Games / Epic Developer Community | secondary | 2026 (UE 5.8 page) | 2026-09-10 | Unreal Engine 5.8 (Iris) | PC / server | Page: '# Iris Replication System' - 'The Iris Replication System is a replication system for networking in Unreal Engine' | available |
| SRC-NTA-017 | Unity Netcode for Entities (package manual 1.0.17) | Unity Technologies | secondary | 2026 (package 1.0.17 | 2026-09-10 | Unity Netcode for Entities 1.0.17 (DOTS/ECS) | PC / server | Sections: '# Unity Netcode for Entities' (intro: 'server authoritive with client prediction framework'), '## Requirements' ('Unity version 2022.2.0f1 or higher') | verified |
| SRC-NTA-018 | Introduction to prediction (Netcode for Entities 7.0 manual) | Unity Technologies | secondary | 2026 (Netcode for En | 2026-09-10 | Unity Netcode for Entities 7.0 | PC / server | Section: '# Introduction to prediction' - 'Client prediction allows clients to use their own inputs to locally simulate the game, without waiting for the server's simulation result.' | available |
| SRC-NTA-019 | Unity's netcode packages (Unity Multiplayer docs) | Unity Technologies | secondary | 2026 | 2026-09-10 | Netcode for Entities / Netcode for GameObjects | PC / server | Page: 'Unity has two netcode frameworks for creating real-time synchronized gameplay in multiplayer games.' | available |
| SRC-NTA-020 | Steam Audio - Programmer's Guide (C API) | Valve Corporation | secondary | 2026 (Steam Audio 4. | 2026-09-10 | Steam Audio (C API, phonon/ipl) | Windows / Linux / macOS / Android / iOS | Sections: 'Initialization' -> 'Memory Allocation', 'HRTF', 'Direct Effect' -> 'Occlusion and transmission', 'Scene' -> 'Static geometry' / 'Dynamic geometry', 'Simulation' -> 'Simulating occlusion and transmission', 'Reflections' -> 'Initializing a simulator for reflections' / 'Reverb', 'Baking' -> | verified |
| SRC-NTA-021 | Steam Audio core documentation (GitHub, index.rst) | ValveSoftware / steam-audio repository | secondary | 2026 (master branch) | 2026-09-10 | Steam Audio | cross-platform | Top of document: overview bullets including 'Steam Audio can calculate convolution reverb, which results in compelling environments...' | available |
| SRC-NTA-022 | Using Features: Occlusion (Wwise documentation) | Audiokinetic | secondary | 2025-2026 (Wwise 202 | 2026-09-10 | Wwise (UE4/Unity integrations) | PC / console | Section: 'Obstruction and Occlusion' - describes how the service works without Spatial Audio, then 'Occlusion and Spatial Audio' | available |
| SRC-NTA-023 | Wwise Acoustics Concepts (Spatial Audio concepts) | Audiokinetic | secondary | 2025-2026 (Wwise 202 | 2026-09-10 | Wwise SDK | cross-platform | Section: acoustic concepts - 'Wwise maps obstruction and occlusion values to properties (Volume, LPF, HPF, and DSF) through curves.'; Rooms/Portals and Reflect sections | available |
| SRC-NTA-024 | Obstruction and Occlusion (Wwise Unity documentation mirror) | Audiokinetic (hosted mirror: documentation.help) | secondary | 2026 (mirror dated 2 | 2026-09-10 | Wwise Unity integration | PC | Sections: '# Obstruction and Occlusion', '## A. Emitter Obstruction/Occlusion' (Ak Emitter Obstruction Occlusion component, Layer Mask), '## B. Portal Obstruction' (Ak Room Portal Obstruction component) | verified |
| SRC-NTA-025 | Wwise Spatial Audio (product page) | Audiokinetic | secondary | 2026 | 2026-09-10 | Wwise | PC / console | Product overview: 'Use the Unity or Unreal editors to design Spatial Audio Rooms and Portals, use different mesh surfaces for different acoustic effects...' | available |
| SRC-NTA-026 | FMOD - Core API: Using DSP Effects | Firelight Technologies (FMOD) | secondary | 2026 (FMOD 2.03 docs | 2026-09-10 | FMOD Core API 2.03 | cross-platform | Page: DSP effects can be inserted into the graph with functions like DSP::addInput; effect parameter reference | available |
| SRC-NTA-027 | FMOD API - FMOD_DSP_CONVOLUTION_REVERB | Firelight Technologies (FMOD) | secondary | 2026 (FMOD 2.x API r | 2026-09-10 | FMOD Core API | cross-platform | Page: FMOD_DSP_CONVOLUTION_REVERB parameter list (wet/dry mix, IR, channel configuration) | available |
| SRC-NTA-028 | Steam Datagram Relay (Steamworks Documentation) | Valve / Steamworks | secondary | 2026 | 2026-09-10 | Steamworks SDK / ISteamNetworkingSockets | PC | Page: Steam Datagram Relay overview and identity requirements for clients/gameservers | available |
| SRC-NTA-029 | Steam Datagram Relay (Valve Developer Community wiki) | Valve / Valve Developer Community | secondary | 2024 (last wiki revi | 2026-09-10 | Steamworks SDK | PC | Page intro: 'Using our APIs, you can not only carry your game traffic over the Valve backbone that is dedicated for game content...' | available |
| SRC-NTA-030 | Using the Anti-Cheat Interfaces (Epic Online Services / Easy Anti-Cheat) | Epic Games | secondary | 2026; verified 2026- | 2026-09-10 | EOS SDK 1.15+ (Easy Anti-Cheat) | Windows / Linux / macOS (64-bit); Linux ARM64 client not supported | Sections: '# Using the Anti-Cheat Interfaces', '### Client Module Setup and Updates', '### Anti-Cheat Integrity Tool Configuration', '### Launch Configuration', '### Registering Callbacks' -> '#### Client-Server Mode' / '#### Peer-to-Peer Mode', '### Protected Game Session Notifications', '### Defin | verified |
| SRC-NTA-031 | Anti-Cheat Interfaces (Epic Online Services, Trust & Safety) | Epic Games | secondary | 2026 | 2026-09-10 | EOS SDK (Easy Anti-Cheat) | Windows / Linux / macOS | Page: 'Integrate the Anti-Cheat Interfaces (also known as "Easy Anti-Cheat") into your game...' | available |
| SRC-NTA-032 | Vanguard On-Demand - Anti-Cheat Update (Riot Games) | Riot Games | secondary | 2026-06-24 | 2026-09-10 | Riot Vanguard | Windows | Article: 'Starting later today, ... Vanguard, will begin to support on-demand sessions...' | available |
| SRC-NTA-033 | Riot Vanguard FAQ (Riot Games Support) | Riot Games | secondary | 2026-06-02 (page rev | 2026-09-10 | Riot Vanguard | Windows | Page: 'Riot Vanguard is Riot Games' custom game security software, designed to uphold the highest levels of competitive...' | available |
| SRC-NTA-034 | Garbage collection modes (Unity Manual, Unity 6 / 6000.0) | Unity Technologies | secondary | 2026 (Unity 6.0 manu | 2026-09-10 | Unity 6.0 (6000.0) | all Unity targets | Page: '# Garbage collection modes' - 'Incremental garbage collection spreads out the process of garbage collection over multiple frames. This is the default garbage...' and 'Incremental mode doesn't make garbage collection faster, but reduces performance spikes related to garbage collection...'; sub | partial |
| SRC-NTA-035 | Garbage Collection Settings in the Unreal Engine Project Settings (UE 5.8 Documentation) | Epic Games / Epic Developer Community | secondary | 2026 (UE 5.8 page) | 2026-09-10 | Unreal Engine 5.8 | all | Reference rows including 'Minimum GC Cluster Size' and 'Maximum Object Count Not Considered By GC' (visible in the indexed EN/ZH page contents) | available |
| SRC-NTA-036 | Migrate to Iris in Unreal Engine (UE 5.8 Documentation) | Epic Games / Epic Developer Community | secondary | 2026 (UE 5.8 page) | 2026-09-10 | Unreal Engine 5.8 (Iris) | PC / server | Page: 'Learn what has changed between Unreal Engine's existing replication systems and Iris.' | available |
| SRC-NTA-037 | Quake 3 Network Protocol | jfedor.org (protocol reverse-engineering documentation) | secondary | ongoing; verified 20 | 2026-09-10 | id Tech 3 / Quake III Arena | PC | Page: protocol overview (snapshot / delta against a baseline frame, reliable and unreliable command streams) | available |
| SRC-NTA-038 | Quake-III-Arena / code/server/sv_snapshot.c (id Software GPL source release) | id Software | secondary | 2005 (GPL release of | 2026-09-10 | id Tech 3 | PC | Source file: snapshot generation / delta logic (SV_BuildClientSnapshot, SV_WriteSnapshotToClient, entity state delta against the client's last acknowledged baseline) | available |
| SRC-NTA-039 | GameNetworkingSockets (ValveSoftware) | Valve Corporation | secondary | ongoing (master bran | 2026-09-10 | Steamworks ISteamNetworkingSockets | Windows / Linux / macOS | Repository README: 'Reliable ...' message-oriented connection library backing Steamworks networking | available |
| SRC-NTA-040 | Ambience Design and Acoustic Systems in 'Senua's Saga: Hellblade II' (GDC 2025) | Pablo Canas, Ninja Theory (GDC Vault) | conference_talk | 2025 | 2026-09-10 | Unreal Engine 5 (reported) / Ninja Theory in-house audio | PC / Xbox | Session page: 'Sound Designer Pablo Canas explains the process involved in the creation of ambience sounds for Hellblade II, from inception to...' | available |
| SRC-NTA-041 | How Ninja Theory created Hellblade II's unsettling soundscape (Game Developer) | Game Developer (GDC 2025 coverage) | secondary | 2025-03-31 | 2026-09-10 | Hellblade II | PC / Xbox | Article lede: 'During the 2025 Game Developers Conference, Ninja Theory principal sound designer...' | available |
| SRC-NTA-042 | Developer Insight - Did you hear that? (Hunt: Showdown, Crytek) | Crytek | secondary | 2025 | 2026-09-10 | CryEngine (Hunt: Showdown) | PC / console | Post intro: 'With the help of our audio engineers, we have compiled the guide below to answer some of your most frequently asked questions...' (audio cue / listening setup guidance) | available |
| SRC-NTA-043 | Dedicated Server (Unity Manual) | Unity Technologies | secondary | 2026 (Unity 6 manual | 2026-09-10 | Unity 6 | Linux / Windows headless | Page: 'Unity provides support for development of games and applications on the Dedicated Server platform.' | available |
| SRC-NTA-044 | Build your application for Dedicated Server (Unity Manual) | Unity Technologies | secondary | 2026 (Unity 6 manual | 2026-09-10 | Unity 6 | Linux / Windows headless | Page: 'When you build for the dedicated server platform, Unity defines the UNITY_SERVER scripting define. You can use this symbol in your scripts to compile server-only code.'; '-standaloneBuildSubtarget Server' command-line argument | available |
| SRC-NTA-045 | Why Bullets "Miss": An Analysis of the CS2 Subtick System | csgo-news.com (community analysis) | secondary | 2024-2026 | 2026-09-10 | Source 2 / Counter-Strike 2 | PC | Sections: 'What Is Tickrate and Why It Matters', 'Why CS2 Sends More Data Than CS:GO', 'Does CS2 Still Run on 64 Ticks?' | available |
| SRC-NTA-046 | Lag compensation (Official Team Fortress Wiki) | Team Fortress Wiki (community) | secondary | 2026 (revision cited | 2026-09-10 | Source (Team Fortress 2) | PC | Page: 'Team Fortress 2, being a Source Engine game, is generally configured to make use of lag compensation.' | available |
| SRC-NTA-047 | VAN: Limiting and Closing the Vanguard Pre-Boot Motherboard Security Gap (Riot Games) | Riot Games | secondary | 2025-12-18 | 2026-09-10 | Riot Vanguard | Windows | Article: 'In the near future, Vanguard will enforce stricter system pre-boot security checks for some players.' | available |
| SRC-NTA-048 | Fan translation/summary of 'Overwatch Gameplay Architecture and Netcode' (GDC 2017) | ZzzRemake (secondary translation of Timothy Ford's GDC talk) | secondary | 2025-10-18 (blog pos | 2026-09-10 | Overwatch / in-house engine | PC / console | Sections covering the command-frame timing ('16ms ... 7ms'), client clock lead ('RTT 160ms ... Client Clock ahead by 96ms'), time dilation ('16ms ... 15.2ms'), the 220ms hit-prediction cutoff, backwards reconciliation, and the Q&A on determinism and 60 fps | verified |
| SRC-NTA-049 | 'Overwatch' Gameplay Architecture and Netcode (full talk video) | GDC / Blizzard Entertainment | secondary | 2017 | 2026-09-10 | Overwatch / in-house engine | PC / console | Linked as the original talk from SRC-NTA-048; no timestamp verification performed in this pass | unverified |
| SRC-NTA-050 | Audio file compression in Unity (Unity Manual) | Unity Technologies | secondary | 2026 (Unity 6.0 manu | 2026-09-10 | Unity 6.0 | all | Page: '# Audio file compression in Unity' - format sections (PCM / ADPCM / Vorbis / MP3), the indexed sentence 'Like PCM, ADPCM lets you automatically optimize or manually adjust the sample rate to further reduce file size' | partial |
| SRC-NTA-051 | Conversion Settings Editor (Wwise documentation) | Audiokinetic | secondary | 2025 (Wwise 2025.1 d | 2026-09-10 | Wwise 2025.1 | cross-platform | Page: 'In each ShareSet you can define various conversion settings, including channel count, audio format, quality and sample rate.' | partial |
| SRC-NTA-052 | Prediction (Netcode for Entities documentation, GitHub mirror) | Unity Technologies (mirror: needle-mirror/com.unity.netcode) | secondary | 2026 (master branch) | 2026-09-10 | Unity Netcode for Entities | PC / server | Document: 'Unity adds the PredictedGhost component to all predicted ghosts on the client, and to all ghosts on the server.' | available |
| SRC-RND-001 | Lumen Global Illumination and Reflections (Unreal Engine 5.8 Documentation) | Epic Games / Epic Developer Community | secondary | 2026 (UE 5.8 page, v | 2026-09-10 | Unreal Engine 5.8 | Windows / PS5 / Xbox Series S\|X | Sections: '# Lumen Global Illumination and Reflections', '## Getting Started with Lumen', '### Lumen Project Settings', '### Post Process Settings', '## Additional Notes' | available |
| SRC-RND-002 | Virtual Shadow Maps (Unreal Engine 5.8 Documentation) | Epic Games / Epic Developer Community | secondary | 2026 (UE 5.8 page, v | 2026-09-10 | Unreal Engine 5.8 | Windows / PS5 / Xbox Series S\|X | Sections: '# Virtual Shadow Maps', '## Clipmaps for Directional Light', '## Caching', '### Managing Cache Invalidations', '### Separate Static Caching', '## Coarse Pages', '## GPU Profiling and Optimization', '### Shadow Depths', '### Shadow Projection', '## Issues and Limitations', '### Overflow of | available |
| SRC-RND-003 | Nanite Virtualized Geometry Overview (Unreal Engine 5.8 Documentation) | Epic Games / Epic Developer Community | secondary | 2026 (UE 5.8 page, v | 2026-09-10 | Unreal Engine 5.8 | DX12 SM6 desktop + current consoles | Sections: '## How does Nanite work?', '## Benefits of Nanite', '## Supported Features of Nanite', '### Geometry', '### Materials', '#### Mesh Deformation', '### Nanite Skeletal Mesh', '### Supported Platforms' | available |
| SRC-RND-004 | Temporal Super Resolution (Unreal Engine 5.8 Documentation) | Epic Games / Epic Developer Community | secondary | 2026 (UE 5.8 page, v | 2026-09-10 | Unreal Engine 5.8 | DX11/DX12/Vulkan/Metal SM5+, PS5, Xbox Series S\|X | Sections: '# Temporal Super Resolution', '### Understanding the Caveats of Temporal Accumulation of Details', '### Upscaling GPU Cost', '### Hidden GPU Costs of Temporal Upscaling', '#### TSR Nyquist-Shannon History', '### TSR History', '## Supported Platforms', '## Troubleshooting Ghosting Issues w | available |
| SRC-RND-005 | Render Dependency Graph (Unreal Engine 5.8 Documentation) | Epic Games / Epic Developer Community | secondary | 2026 (UE 5.8 page, v | 2026-09-10 | Unreal Engine 5.8 | DX12 / Vulkan / Metal | Sections: '# Render Dependency Graph', '#### Transient Resources', '##### Resources Dependency Management', '##### Asynchronous Compute', '### Resource Transition Debugging', '#### Setup and Execute Timelines', '### RDG Insights Plugin' | available |
| SRC-RND-006 | Dynamic Resolution (Unreal Engine 5.8 Documentation) | Epic Games / Epic Developer Community | secondary | 2026 (UE 5.8 page, v | 2026-09-10 | Unreal Engine 5.8 | Xbox One/Series, PS4/PS5, Switch, PC (DX12/Vulkan) | Sections: '# Dynamic Resolution', '## Dynamic Resolution Cruising', '### Over Budget Panic', '### Controlling Dynamic Resolution With Operation Mode', '## Replacing Dynamic Resolution Heuristic in C++', '## Limitations of Dynamic Resolution', '## Supported Platforms for Dynamic Resolution' | available |
| SRC-RND-007 | Path Tracer (Unreal Engine 5.8 Documentation) | Epic Games / Epic Developer Community | secondary | 2026 (UE 5.8 page, v | 2026-09-10 | Unreal Engine 5.8 | Windows 10 1809+, DX12, NVIDIA RTX / DXR GTX | Sections: '# Path Tracer', '### Path Tracer Post Process Volume Settings', '### Denoising Options', '## Using the Path Tracer with Movie Render Queue', '## Limitations of the Path Tracer', '## Useful Console Variables' | available |
| SRC-RND-008 | Scalability (Unreal Engine 5.8 Documentation) | Epic Games / Epic Developer Community | secondary | 2026 (UE 5.8 page, v | 2026-09-10 | Unreal Engine 5.8 | all | Sections: '# Scalability'; linked 'Scalability Reference' (sg.* console variables and BaseScalability.ini groups) | available |
| SRC-RND-009 | PSO Caches (Unreal Engine 5.8 Documentation) | Epic Games / Epic Developer Community | secondary | 2026 (UE 5.8 page, v | 2026-09-10 | Unreal Engine 5.8 | D3D12 / Vulkan / Metal | Sections: '# PSO Caches', '## Terminology and Supported PSO Types', '## Generate PSO Caches' | available |
| SRC-RND-010 | NVIDIA DLSS (developer landing page) | NVIDIA Corporation | secondary | 2026 (page updated J | 2026-09-10 | DLSS 4 / 4.5, Streamline 2.11.1, NGX 310.6.0 | GeForce RTX | Sections: '## DLSS AI Technologies', '## Key Benefits' -> '### Performance Multiplier', '## Get Started With DLSS Through Streamline' | available |
| SRC-RND-011 | Accelerating Ultra-Realistic Game Development with NVIDIA DLSS 3 and NVIDIA RTX Path Tracing | Ike Nnoli, NVIDIA (Technical Blog) | secondary | 2022-09-21 | 2026-09-10 | DLSS 3, RTX 40 Series | GeForce RTX 40 | Sections: '## A revolution in neural graphics' (Figure 1 caption), '## Accelerate lighting production with NVIDIA RTX Path Tracing' (Figure 3 caption), '## New graphics primitives built for the future of games' (Figure 4 caption) | available |
| SRC-RND-012 | FidelityFX Super Resolution 2 (FSR 2.2.1) README | AMD / GPUOpen-Effects | secondary | 2023 (FSR 2.2.1 rele | 2026-09-10 | FSR 2.2.1 | DirectX 12, Vulkan; HLSL CS_6_2 (CS_6_6 for 64-wide wavefronts) | Sections: 'Scaling modes' (per-dimension factors table), 'Camera jitter' (sequence length table), 'Mipmap biasing', 'Input resources' table, 'Memory usage' (RX 6700XT DX12 table), 'Supported platforms / APIs' | available |
| SRC-RND-013 | Intel XeSS Super Resolution (XeSS-SR) Developer Guide 2.0 | Intel Corporation | secondary | 2025-2026 (XeSS SDK | 2026-09-10 | XeSS 1.3+ / SDK 3.0.2 | DirectX 12, DirectX 11, Vulkan 1.1; SM 6.4 DP4a cross-vendor | Sections: quality-preset table (fixed resolution scaling), 'Inputs'/'XeSS-SR inputs', 'Jitter', 'Jitter sequence length', 'Mip bias', 'Supported APIs', hardware-requirement bullets | available |
| SRC-RND-014 | DirectX Raytracing (DXR) Functional Spec, v1.48 | Microsoft (DirectX-Specs) | api_specification | 2026-09-08 (v1.48) | 2026-09-10 | DXR 1.48 / D3D12 | Windows | Sections: '# Walkthrough' -> '## Geometry and acceleration structures', '## Ray generation shaders', '## Closest hit shaders', '## Any hit shaders', '## Miss shaders', '## Intersection shaders', '## Callable shaders', '## Hit groups', '## Shader identifier', '## Shader record', '## Shader tables', ' | available |
| SRC-RND-015 | Ray Tracing (Vulkan Documentation Project / Khronos guide) | Khronos Vulkan Documentation Project | secondary | 2026 (guide, verifie | 2026-09-10 | VK_KHR_acceleration_structure, VK_KHR_ray_tracing_pipeline, VK_KHR_ray_query, VK | Vulkan | Sections: extension list ('A set of five interrelated extensions'), ray tracing shader stages, 'Acceleration structure creation' (device vs host build), 'Ray tracing best practices' (device-local memory, 32-bit systems, ray query count) | available |
| SRC-RND-016 | VK_EXT_mesh_shader proposal (Vulkan Documentation Project) | Khronos Vulkan Documentation Project | secondary | 2022-01-20 (extensio | 2026-09-10 | VK_EXT_mesh_shader | Vulkan (multi-vendor, DX12-compatible) | Sections: '2. Solution Space', '3.1.1' (mesh shaders), '3.1.2' (task shaders), '3.2.1', '3.2.4' (draw commands), '3.2.5' (properties/preferences), 'Issue 4.2', 'Issue 4.4' | available |
| SRC-RND-017 | Variable Rate Shading (VRS) Functional Spec | Microsoft (DirectX-Specs) | api_specification | 2019 (D3D12 VRS, 19H | 2026-09-10 | D3D12 VRS Tier 1 / Tier 2, HLSL SM 6.4 | Windows 10 19H1+ | Sections: '## Feature Tiering', '### Tier 1', '### Tier 2', '#### Coarse pixel size support', '### Screen Space Image (image-based):', '### Per-Primitive Attribute', '#### Tile size', '#### Screen space image size', '## Combining Shading Rate Factors', '## Depth and Stencil' | available |
| SRC-RND-018 | Interactive Indirect Illumination Using Voxel Cone Tracing | Cyril Crassin, Fabrice Neyret, Miguel Sainz, Simon Green, Elmar Eisemann (NVIDIA / INRIA) | secondary | 2011-09 | 2026-09-10 | n/a (research prototype) | GPU (paper-era hardware) | Abstract (quoted verbatim): 'Our approach can manage two light bounces for both Lambertian and glossy materials at interactive framerates (25-70FPS).' | available |
| SRC-RND-019 | Volumetric Fog: Unified, compute shader based solution to atmospheric scattering | Bart Wronski (Ubisoft), SIGGRAPH 2014 | secondary | 2014-08 | 2026-09-10 | n/a (shipped in Assassin's Creed IV: Black Flag) | PS3/PS4/Xbox 360-era consoles | PDF pages: p.25 (frustum-aligned froxel volume, exponential depth slices), p.27 ('The resolution of our volume textures may seem extremely low, but it is sufficient'), p.45 (application = 3D-texture lookup + FMA), p.47 ('Total cost was surprisingly small, around 1.1ms. Calculating it in double resol | available |
| SRC-RND-020 | Clustered Deferred and Forward Shading | Ola Olsson, Markus Billeter, Ulf Assarsson (Chalmers University of Technology) | secondary | 2012 | 2026-09-10 | n/a (research implementation) | GPU (paper-era hardware) | p.1 Figure 1 caption ('~2400 light sources ... rendered in 17ms ... 2.3ms for clustering, 1.5ms for light assignment and 5.6ms for shading'); p.4 (exponential view-space depth subdivision, 32x32 pixel screen tiles); p.8 Table 2 (light assignment time vs #lights) and Figure 10 caption ('Deferred take | available |
| SRC-RND-021 | FrameGraph: Extensible Rendering Architecture in Frostbite | Yuriy O'Donnell (Frostbite / Electronic Arts), GDC 2017 | secondary | 2017 | 2026-09-10 | Frostbite | Battlefield-era consoles/PC | Session page: 'Session Name: FrameGraph: Extensible Rendering Architecture in Frostbite', 'Speaker(s): Yuriy O'Donnell', 'Company Name(s): Frostbite / Electronic Arts', 'Track / Format: Programming', Overview text | available |
| SRC-RND-022 | Rendering the Hellscape of Doom Eternal | Jean Geffroy, Axel Gneiting, Yixin Wang (id Software), SIGGRAPH 2020 Advances | conference_talk | 2020 | 2026-09-10 | idTech 7 | PC + consoles (60 FPS target) | PDF pages: p.1 (title/authors), p.3 ('IDTECH 7 - Fully forward rendered ... Still 60FPS on consoles at same resolutions'), p.4 ('HYBRID BINNING - Used Clustered Binning in Doom [Olson12]'), p.9 ('Very tight budget (<500us)'), p.16-19 ('LIGHT LIST SELECTION - Each fragment invocation checks both its | available |
| SRC-RND-023 | How Northlight makes Alan Wake 2 shine | Remedy Entertainment (Northlight team) | secondary | 2023-11-06 | 2026-09-10 | Northlight | PC / PS5 / Xbox Series S\|X | Sections: '### New GPU-driven rendering pipeline' (mesh shaders, single-pixel occlusion precision, meshlet culling), '### Character-style rigs on foliage' ('almost 300,000 bones in Cauldron Lake being processed every frame'), '### Transparency and atmospheric effects' (MBOIT, three resolutions), '## | available |
| SRC-RND-024 | Path Tracing & Overdrive Mode - Requirements & How-To (Cyberpunk 2077 support) | CD PROJEKT RED S.A. | secondary | 2023 (Patch 1.62); p | 2026-09-10 | REDengine 4 | PC (NVIDIA RTX) | Body text: 'With Patch 1.62 we've introduced Ray Tracing: Overdrive Mode ... recommended on NVIDIA GeForce RTX 40 Series (4070 Ti and up) ... on NVIDIA GeForce RTX 3090 (1080p, 30 fps) ... set to "off" by default'; VRAM table (1080p 8 GB / 1440p 10 GB / 2160p 12 GB); Photo Mode render time 'between | available |
| SRC-RND-025 | Quake II RTX: Re-Engineering a Classic with Ray Tracing Effects on Vulkan | NVIDIA (GeForce news) | secondary | 2019-03 (GDC 2019); | 2026-09-10 | Q2VKPT -> Quake II RTX, Vulkan VKRay | PC (Vulkan, GeForce RTX) | Body text: 'Quake II RTX is a pure ray-traced game. That means all lighting, reflections, shadows and VFX are ray-traced, with no traditional effects or techniques utilized.' Also NVIDIA newsroom 2019-06-06: 'the world's first game that is fully path-traced'. | available |
| SRC-RND-026 | Global Illumination in Metro Exodus: An Artist's Point of View | NVIDIA Developer Blog | secondary | 2019-05-14 | 2026-09-10 | 4A Engine | PC (DXR) | Article body discussing ray-traced GI in a shipped game from the art/level-authoring side | available |
| SRC-RND-027 | Exploring Ray Traced Future in Metro Exodus (GTC 2019) | 4A Games (NVIDIA GTC 2019 presentation) | conference_talk | 2019 | 2026-09-10 | 4A Engine | PC (DXR) | Slide agenda items: 'Added buffer to cache raytrace data for use in RTAO and RTGI passes', 'Why do it 1000 times when once will do?', 'Raytracing in screen space', 'DENOISING - Spatial component / Temporal component', 'Distance weight', 'Fetch heavy data only if weight is non-zero' | available |
| SRC-RND-028 | Decima Engine: Advances in Lighting and AA | Guerrilla Games (SIGGRAPH 2017) | conference_talk | 2017-07-31 | 2026-09-10 | Decima | PS4 / PS4 Pro | Abstract: 'our 2-frame temporal anti-aliasing solution for 1080p, and finally our optimized 2160p checkerboard rendering and 'tangram' resolve strategy used on the PS4 Pro' | available |
| SRC-RND-029 | 2D lights and shadows (Godot Engine documentation) | Godot Engine project | secondary | 2026 (stable branch, | 2026-09-10 | Godot 4.x stable | all | Sections: '# 2D lights and shadows', '## Nodes', '## Point lights', '## Directional light', '## Common light properties', '## Setting up shadows', '## Using additive sprites as a faster alternative to 2D lights' | available |
| SRC-RND-030 | "A Dive into Render Graphs" (SIGGRAPH 2023) - NOT LOCATED | n/a | secondary | n/a | 2026-09-10 | n/a | n/a | Full-text scan of the SIGGRAPH Advances in Real-Time Rendering index pages for 2019-2025 found zero occurrences of 'render graph' / 'frame graph' / 'Dive into Render Graphs'; the 2023 syllabus lists HypeHype Mobile Rendering Architecture, The Callisto Protocol, Substrate and CoD terrain instead. | unavailable |
| SRC-RND-031 | Real-Time Rendering, 4th edition | Tomas Akenine-Moller, Eric Haines, Naty Hoffman (A K Peters / CRC Press) | book | 2018 | 2026-09-10 | n/a (textbook) | n/a | Standard reference chapters on shadow mapping / cascaded shadow maps, image-space (screen-space) effects, deferred vs forward architectures and tone mapping. Used here as a conceptual anchor only; no numeric claim is taken from it without a page citation. | available (publisher page reac |
| SRC-RND-032 | Shadow mapping (Wikipedia) | Wikipedia contributors | secondary | accessed 2026-09-10 | 2026-09-10 | n/a | n/a | Article body on shadow map aliasing and cascaded shadow maps | available |
| SRC-RND-033 | Ambient occlusion (Wikipedia) | Wikipedia contributors | secondary | accessed 2026-09-10 | 2026-09-10 | n/a | n/a | Article body on screen-space ambient occlusion and derived screen-space contact effects | available |
| SRC-RND-034 | Lightmap (Wikipedia) | Wikipedia contributors | secondary | accessed 2026-09-10 | 2026-09-10 | n/a | n/a | Article body on precomputed lightmaps and their memory/lighting trade-offs | available |
| SRC-RND-035 | Progressive Lightmapper (Unity Manual) | Unity Technologies | secondary | 2026 (Unity 6 page) | 2026-09-10 | Unity 6.6 | Unity platforms | n/a - request redirected to 'Choose a light baking backend' and returned only the OneTrust consent banner | unavailable (consent-gated) |
| SRC-RND-036 | Scriptable Render Pipeline Batcher (Unity Manual) | Unity Technologies | secondary | 2026 (Unity 6 page) | 2026-09-10 | Unity 6.6 / URP / HDRP | Unity platforms | n/a - returned only the OneTrust consent banner | unavailable (consent-gated) |
| SRC-RND-037 | Scene Capture 2D (Unreal Engine documentation) | Epic Games | secondary | 2026 (UE 5.8) | 2026-09-10 | Unreal Engine 5.8 | all | n/a - URL redirected to the documentation index (page not found) | unavailable (404 / redirect) |
| SRC-RND-038 | GPU Lightmass (Unreal Engine documentation) | Epic Games | secondary | 2026 (UE 5.8) | 2026-09-10 | Unreal Engine 5.8 | Windows DX12 | n/a - URL redirected to the documentation index (page not found) | unavailable (404 / redirect) |
| SRC-RND-039 | SRP Batcher: Speed up your rendering! | Arnaud Carre, Unity Technologies | engineering_blog | 2019-02-28 | 2026-09-10 | Unity 2018.3+ / LWRP / HDRP / custom SRP | almost all Unity platforms | Sections: 'How SRP Batcher works', 'How to enable SRP Batcher', 'SRP Batcher compatibility', 'The Art of profiling' (SRPBatcherProfiler.cs), 'Various scenes benchmark', 'How to check SRP Batcher efficiency', 'Per Material variables' / 'Per Object variables' (UnityPerMaterial, UnityPerDraw), 'Common | available |
| SRC-RND-040 | Hierarchical-Z map based occlusion culling | Daniel Rakos, RasterGrid | engineering_blog | 2010-10 | 2026-09-10 | OpenGL 4.0 reference implementation | GPU (Radeon HD5770 for the quoted timing) | Sections: 'Introduction', 'Motivation', 'The algorithm' -> 'Hi-Z map construction', 'Culling with the Hi-Z map', 'Conclusion' | available |
| SRC-RND-041 | Leveraging Asynchronous Queues for Concurrent Execution | Stephan Hodes, AMD (GPUOpen) | secondary | 2016-12-01 | 2026-09-10 | DirectX 12 / Vulkan, GCN | Windows | Sections: 'Why concurrency is important', 'Improved performance through higher GPU utilization', 'Build a task graph based engine', 'How to check if queues are working as expected', 'What could possibly go wrong?' | available |
| SRC-RND-042 | Sci-fi and fantasy worlds collide in UE5-powered co-op adventure Split Fiction (developer interview) | Josef Fares and Jonas Mauritzsson, Hazelight Studios / Epic Games | interview | 2025-02-25 | 2026-09-10 | Unreal Engine 5 | PC / PS5 / Xbox Series S\|X | Section: 'Are there particular technical challenges you face when crafting split-screen co-op experiences? If so, how do you approach them?' - answer by Jonas Mauritzsson, Lead Programmer | available |
| SRC-RND-043 | Portals \| Part 6 - Portal Recursion | Daniel Ilett | engineering_blog | 2020-01-19 | 2026-09-10 | Unity (built-in render pipeline), HLSL/C# | PC | Sections: 'Portal recursion', 'Recursive portal shader', 'Recursive portal scripting', 'Conclusion' | available |
| SRC-RND-044 | Mesh Shader Functional Spec (D3D12) | Microsoft (DirectX-Specs) | api_specification | v0.86 (verified 2026 | 2026-09-10 | D3D12 mesh/amplification shaders | Windows (D3D12 only) | Sections: 'Intro', 'Motivation for adding Mesh Shader', 'Conceptual high level overview', 'Amplification shader and Mesh shader' (Required Support table), 'Mesh shader output size limits', 'Rasterization order', 'Vertex Indices', 'Vertex Attributes', 'Programmable Primitive Amplification', 'Streamou | available |
| SRC-RND-045 | DOOM Eternal - Graphics Study | Simon Coenen | secondary | 2020 | 2026-09-10 | idTech 7 (Vulkan) | PC + consoles | Sections: 'Introduction', '# A frame in Doom Eternal', '## Opaque Forward pass' -> '### Bindless resources', '### Dynamic draw call merging', '## Mesh Decals', '## Particles' -> '### Lighting' | available |
| SRC-RND-046 | Using async compute to saturate GPU (Vulkan Samples) | Khronos Vulkan Samples project | secondary | verified 2026-09-10 | 2026-09-10 | Vulkan (multiple queues) | TBDR mobile GPUs (Mali) and desktop | Sections: 'Overview', 'Compute all the things - a post processing case study', 'The challenge of compute shader post processing on tile-based deferred renderers (TBDR)', 'A note on compute post-processing on TBDR vs immediate mode (IMR) desktop GPUs', 'Using multiple graphics queues to pop the bubbl | available |
| SRC-RND-047 | HLSL Dynamic Resources (Shader Model 6.6) | Microsoft (DirectX-Specs) | api_specification | v1.00, 2021-04-20 | 2026-09-10 | Shader Model 6.6, D3D12 Resource Binding Tier 3 | Windows | Sections: 'HLSL Changes' -> 'ResourceDescriptorHeap and SamplerDescriptorHeap', 'Root Signature Changes' -> 'SetDescriptorHeaps and Set*RootSignature', 'Descriptor and Data Volatility', 'Device Capability' -> 'Shader Feature Requirement Flags' | available |
| SRC-RND-048 | It Takes Two tech analysis (Digital Foundry) | Digital Foundry / Eurogamer | secondary | 2021 (URL in catalog | 2026-09-10 | Unreal Engine 4 | consoles / PC | n/a - server returned '404 Not Found' | verified_fetched |
| SRC-TN-001 | DirectX 12 programming guide (Windows Win32) | Microsoft | official_documentation | 2026 | 2026-09-11 | DirectX 12 | Windows 10/11 PC | Landing page of the Win32 Direct3D 12 programming guide section | verified_fetched |
| SRC-TN-002 | Command queues and command lists (Direct3D 12) | Microsoft | official_documentation | 2026 | 2026-09-11 | DirectX 12 | Windows 10/11 PC | Section overview describing ID3D12CommandQueue / ID3D12CommandList and the ExecuteCommandLists submission model | verified_fetched |
| SRC-TN-003 | Direct3D 11 graphics (table of contents) | Microsoft | official_documentation | 2026 | 2026-09-11 | Direct3D 11 | Windows 7 SP1 and later | Table of contents of the Direct3D 11 graphics documentation set | verified_fetched |
| SRC-TN-004 | Direct3D 11 programming reference (Win32 API index) | Microsoft | secondary | 2026 | 2026-09-11 | Direct3D 11 | Windows 7 SP1 and later | API index page for the ID3D11Device / ID3D11DeviceContext interface family | verified_fetched |
| SRC-TN-005 | Vulkan Specification (latest, HTML) | Khronos Group | secondary | 2026 | 2026-09-11 | Vulkan 1.3+ (rolling 'latest') | Windows, Linux, Android | Full normative specification document (vkspec.html) | verified_fetched |
| SRC-TN-006 | Vulkan-Docs (Khronos Group repository) | Khronos Group | secondary | 2026 | 2026-09-11 | Vulkan 1.3+ | Cross-platform | Repository root README describing the spec/refpages/XML sources | verified_fetched |
| SRC-TN-007 | DirectX Raytracing (DXR) functional specification overview | Microsoft | official_documentation | 2026 | 2026-09-11 | DXR (DirectX 12 Ultimate) | Windows 10 1809+ / DXR-capable GPU | Overview section introducing raytracing pipelines, acceleration structures and shader stages | verified_fetched |
| SRC-TN-008 | HLSL reference for DirectX Raytracing | Microsoft | secondary | 2026 | 2026-09-11 | DXR / Shader Model 6.x | Windows 10 1809+ / DXR-capable GPU | Reference listing of raytracing-specific HLSL intrinsics and system-value semantics | verified_fetched |
| SRC-TN-009 | acl - Animation Compression Library | Nicholas Frechette | secondary | 2026 | 2026-09-11 | ACL 2.x (develop) | Cross-platform C++11 header-only | Repository README: purpose, feature list and design goals | verified_fetched |
| SRC-TN-010 | Animation Compression Library in Unreal Engine | Epic Games | official_documentation | 2026 | 2026-09-11 | Unreal Engine 5.3+ | Windows / all UE platforms | Engine documentation page for the ACL plugin and its compression settings assets | verified_fetched |
| SRC-TN-011 | meshoptimizer - mesh optimization library | Arseny Kapoulkine (zeux) | secondary | 2026 | 2026-09-11 | meshoptimizer (master) | Cross-platform C/C++ | Repository root: algorithm list (index/vertex-cache/overdraw/fetch optimization, simplification, encoders) | verified_fetched |
| SRC-TN-012 | meshoptimizer README | Arseny Kapoulkine (zeux) | official_documentation | 2026 | 2026-09-11 | meshoptimizer (master) | Cross-platform C/C++ | README body describing each algorithm, its purpose and its expected effect | verified_fetched |
| SRC-TN-013 | RVO2 Library: documentation (2.0) | University of North Carolina at Chapel Hill, Gamma Lab | official_documentation | 2012 | 2026-09-11 | RVO2 2.0 | Cross-platform C++ / C# | Documentation index and API reference for RVO2 2.0 (Agent, Simulator, KdTree) | verified_fetched |
| SRC-TN-014 | RVO2 Library - project page | UNC Chapel Hill, Gamma Lab | secondary | 2012 | 2026-09-11 | RVO2 2.0 | Cross-platform | Project landing page with the abstract of the underlying ORCA paper | verified_fetched |
| SRC-TN-015 | Tracy Profiler | Bartlomiej Płociennik (wolfpld) | secondary | 2026 | 2026-09-11 | Tracy (master) | Windows / Linux / macOS, C++ (also C, Rust, Lua bindings) | Repository root describing the hybrid instrumentation + sampling profiler | verified_fetched |
| SRC-TN-016 | Tracy Profiler README | Bartlomiej Płociennik (wolfpld) | official_documentation | 2026 | 2026-09-11 | Tracy (master) | Cross-platform | README describing features, supported GPU APIs and integration model | verified_fetched |
| SRC-TN-017 | Opus Codec - official site | Xiph.Org Foundation / IETF codec WG | official_documentation | 2026 | 2026-09-11 | Opus (RFC 6716) | Cross-platform | Landing page stating the intended application range (VoIP, videoconferencing, in-game chat, live music) | verified_fetched |
| SRC-TN-018 | RFC 6716 - Definition of the Opus Audio Codec | IETF (JM Valin et al.) | secondary | 2012 | 2026-09-11 | RFC 6716 | Standards track | Normative RFC defining the codec, its modes (SILK/CELT hybrid) and algorithmic latency classes | verified_fetched |
| SRC-TN-019 | PhysX (NVIDIA-Omniverse) repository | NVIDIA | secondary | 2026 | 2026-09-11 | PhysX 5.x | Windows / Linux / macOS / consoles | Repository root: SDK scope, build instructions, feature summary | verified_fetched |
| SRC-TN-020 | NVIDIA PhysX SDK developer page | NVIDIA | secondary | 2026 | 2026-09-11 | PhysX SDK | Cross-platform | Product page describing the SDK and its platform/feature coverage | verified_fetched |
| SRC-TN-021 | Unity DOTS product page | Unity Technologies | secondary | 2026 | 2026-09-11 | Unity 6 / Entities 1.x | Cross-platform | Product page defining DOTS as the combination of Entities, Burst, Jobs and the C# Job System | verified_fetched |
| SRC-TN-022 | Unity Entities package manual | Unity Technologies | official_documentation | 2026 | 2026-09-11 | com.unity.entities 1.0 | Cross-platform | Package documentation landing page (ECS concepts, worlds, systems, baking) | verified_fetched |
| SRC-TN-023 | Unity Netcode for Entities manual | Unity Technologies | official_documentation | 2026 | 2026-09-11 | com.unity.netcode 1.0 | Cross-platform | Package documentation landing page (client/server prediction, ghost replication) | verified_fetched |
| SRC-TN-024 | Unity Transport package manual | Unity Technologies | official_documentation | 2026 | 2026-09-11 | com.unity.transport 1.5 | Cross-platform | Package documentation landing page (connections, pipelines, drivers) | verified_fetched |
| SRC-TN-025 | Unity Addressables package manual | Unity Technologies | official_documentation | 2026 | 2026-09-11 | com.unity.addressables 1.21 | Cross-platform | Package documentation landing page (groups, labels, build and load by address) | verified_fetched |
| SRC-TN-026 | Unity Burst compiler package manual | Unity Technologies | official_documentation | 2026 | 2026-09-11 | com.unity.burst 1.8 | Cross-platform | Package documentation landing page (LLVM backend, [BurstCompile], restrictions on managed code) | verified_fetched |
| SRC-TN-027 | Universal Render Pipeline package manual | Unity Technologies | official_documentation | 2026 | 2026-09-11 | com.unity.render-pipelines.universal 14.0 | Cross-platform | Package documentation landing page for the Scriptable Render Pipeline implementation | verified_fetched |
| SRC-TN-028 | World Partition in Unreal Engine | Epic Games | official_documentation | 2026 | 2026-09-11 | Unreal Engine 5 | Windows / all UE platforms | Documentation page describing the grid-based partitioning, streaming cells and One File Per Actor | verified_fetched |
| SRC-TN-029 | Replication Graph in Unreal Engine | Epic Games | official_documentation | 2026 | 2026-09-11 | Unreal Engine 4.20+ / UE5 | Windows / all UE platforms | Documentation page describing the replication graph node classes and the motivation (large player counts) | verified_fetched |
| SRC-TN-030 | Steamworks SDK documentation | Valve Corporation | official_documentation | 2026 | 2026-09-11 | Steamworks SDK (rolling) | Windows / macOS / Linux | SDK landing page listing the API surface and integration requirements | verified_fetched |
| SRC-TN-031 | Steamworks Features overview | Valve Corporation | official_documentation | 2026 | 2026-09-11 | Steamworks SDK (rolling) | Windows / macOS / Linux | Feature index page enumerating Steamworks subsystems | verified_fetched |
| SRC-TN-032 | Microsoft DirectStorage repository | Microsoft | secondary | 2026 | 2026-09-11 | DirectStorage 1.x | Windows 10/11 + NVMe SSD | Repository root: runtime + tools, GDeflate codec, staging buffer model | verified_fetched |
| SRC-TN-033 | DirectStorage README | Microsoft | official_documentation | 2026 | 2026-09-11 | DirectStorage 1.x | Windows 10/11 + NVMe SSD | README describing requirements, supported decompression codecs and the sample | verified_fetched |
| SRC-TN-040 | Ashes of the Singularity (Wikipedia) | Wikipedia contributors | secondary | 2026 | 2026-09-11 | 2016 | Windows PC | Game article: release, developer, and engine/API notes | verified_fetched |
| SRC-TN-041 | Civilization VI (Wikipedia) | Wikipedia contributors | secondary | 2026 | 2026-09-11 | 2016 | Windows PC / macOS / Linux | Game article: release, developer, platforms | verified_fetched |
| SRC-TN-042 | The Witcher 3: Wild Hunt (Wikipedia) | Wikipedia contributors | secondary | 2026 | 2026-09-11 | 2015 | Windows PC / consoles | Game article: release, developer, engine and platform notes | verified_fetched |
| SRC-TN-043 | Grand Theft Auto V (Wikipedia) | Wikipedia contributors | secondary | 2026 | 2026-09-11 | 2015 (PC) | Windows PC / consoles | Game article: PC release and engine notes | verified_fetched |
| SRC-TN-044 | Doom (2016 video game) | Wikipedia contributors | secondary | 2026 | 2026-09-11 | 2016 | Windows PC / consoles | Game article including the development/technology notes on the id Tech 6 renderer | verified_fetched |
| SRC-TN-045 | Doom Eternal (Wikipedia) | Wikipedia contributors | secondary | 2026 | 2026-09-11 | 2020 | Windows PC / consoles | Game article including technology notes on the id Tech 7 renderer | verified_fetched |
| SRC-TN-046 | Battlefield V (Wikipedia) | Wikipedia contributors | secondary | 2026 | 2026-09-11 | 2018 | Windows PC / consoles | Game article including the ray tracing / DXR section | verified_fetched |
| SRC-TN-047 | Metro Exodus (Wikipedia) | Wikipedia contributors | secondary | 2026 | 2026-09-11 | 2019 | Windows PC / consoles | Game article including the ray tracing technology section | verified_fetched |
| SRC-TN-048 | Batman: Arkham Asylum (Wikipedia) | Wikipedia contributors | secondary | 2026 | 2026-09-11 | 2009 | Windows PC / consoles | Game article including the PhysX technology notes | verified_fetched |
| SRC-TN-049 | Mafia II (Wikipedia) | Wikipedia contributors | secondary | 2026 | 2026-09-11 | 2010 | Windows PC / consoles | Game article including the PhysX technology notes | verified_fetched |
| SRC-TN-050 | Team Fortress 2 (Wikipedia) | Wikipedia contributors | secondary | 2026 | 2026-09-11 | 2007 | Windows PC / macOS / Linux | Game article including engine (Source) and platform notes | verified_fetched |
| SRC-TN-051 | Counter-Strike 2 (Wikipedia) | Wikipedia contributors | secondary | 2026 | 2026-09-11 | 2023 | Windows PC / Linux | Game article including engine (Source 2) and release/platform notes | verified_fetched |
| SRC-TN-052 | Fortnite (Wikipedia) | Wikipedia contributors | secondary | 2026 | 2026-09-11 | 2017 | Windows PC / consoles / mobile | Game article including engine (Unreal Engine) and mode (Battle Royale) notes | verified_fetched |
| SRC-TN-053 | V Rising (Wikipedia) | Wikipedia contributors | secondary | 2026 | 2026-09-11 | 2022 | Windows PC | Game article: developer (Stunlock Studios), engine (Unity), release | verified_fetched |
| SRC-TN-054 | Ratchet & Clank: Rift Apart (Wikipedia) | Wikipedia contributors | secondary | 2026 | 2026-09-11 | 2023 (PC port) | Windows PC / PS5 | Game article including the PC port technology notes | verified_fetched |
| SRC-TN-055 | Forspoken (Wikipedia) | Wikipedia contributors | secondary | 2026 | 2026-09-11 | 2023 | Windows PC / PS5 | Game article including the PC technology/streaming notes | verified_fetched |
| SRC-TN-056 | Portal 2 (Wikipedia) | Wikipedia contributors | secondary | 2026 | 2026-09-11 |  | Windows PC / macOS / Linux / consoles | Game article: release, developer, engine and portal gameplay sections | verified_fetched |
| SRC-WRS-001 | World Partition (Unreal Engine 5.8 Documentation) | Epic Games / Epic Developer Community | secondary | 2026 (UE 5.8 page, v | 2026-09-10 | Unreal Engine 5.8 | PC (Windows) / current consoles | Sections: '# World Partition', '## Enabling World Partition', '## Using World Partition', '### Actors in World Partition', '### Streaming Sources', '### Using the Player as a Streaming Source', '### Runtime Grid Settings', '### Cooking a World Partition world', '## Testing a Partitioned World', '### | verified |
| SRC-WRS-002 | World Partition - Data Layers in Unreal Engine | Epic Games / Epic Developer Community | secondary | 2026 (UE 5.8 page, v | 2026-09-10 | Unreal Engine 5.8 | PC (Windows) / current consoles | Sections: '# Data Layers', '## Creating Data Layers', '## ...Data Layer Assets', '## Assigning Actors to Data Layers', '## Runtime Data Layer States', '## Data Layers and World Partition streaming interaction' | verified |
| SRC-WRS-003 | One File Per Actor in Unreal Engine | Epic Games / Epic Developer Community | secondary | 2026 (UE 5.8 page, v | 2026-09-10 | Unreal Engine 5.8 | PC (Windows) / current consoles | Sections: '# One File Per Actor', '## Enabling One File Per Actor', '## Converting Sublevels', '## Using OFPA With Source Control' | verified |
| SRC-WRS-004 | World Partition - Hierarchical Level of Detail in Unreal Engine | Epic Games / Epic Developer Community | secondary | 2026 (UE 5.8 page, v | 2026-09-10 | Unreal Engine 5.8 | PC (Windows) / current consoles | Sections: '# World Partition - Hierarchical Level of Detail', '## Creating HLOD Layers', '### Choosing a Layer Type', '### Mesh Merge Settings', '### Proxy Settings', '## Using HLOD Layers', '### Adding Actors', '### Generating HLODs Using the Commandlet', '## Visualizing HLODs'; ini example blocks | verified |
| SRC-WRS-005 | Large World Coordinates in Unreal Engine 5 | Epic Games / Epic Developer Community | secondary | 2026 (UE 5.8 page, v | 2026-09-10 | Unreal Engine 5.8 | PC (Windows) / all | Sections: '# Large World Coordinates' (marked Beta), '## Upgrading your Project to Unreal Engine 5', '## Experimenting with Large Worlds' ('The default WORLD_MAX size is 88 million kilometers ... If you want to use the UE4 WORLD_MAX size of 21 kilometers, you can set the global value UE_USE_UE4_WORL | verified |
| SRC-WRS-006 | Large World Coordinates Rendering in Unreal Engine 5 | Epic Games / Epic Developer Community | secondary | 2026 (UE 5.8 page, v | 2026-09-10 | Unreal Engine 5.8 | PC (Windows) / all | Sections: '# Large World Coordinates Rendering', '## ...HLSL types', '## LargeWorldCoordinates.ush', shader-side FLWC / FDF* helper types and the camera-relative translation into the shader constants | verified |
| SRC-WRS-007 | Nanite Virtualized Geometry Overview (Unreal Engine 5.8 Documentation) | Epic Games / Epic Developer Community | secondary | 2026 (UE 5.8 page, v | 2026-09-10 | Unreal Engine 5.8 | DX12 SM6 desktop + current consoles | Sections: '## How does Nanite work?', '## Benefits of Nanite', '## Supported Features of Nanite', '### Geometry', '### Materials', '#### Mesh Deformation', '### Nanite Skeletal Mesh', '### Supported Platforms' | verified |
| SRC-WRS-008 | Virtual Texturing in Unreal Engine | Epic Games / Epic Developer Community | secondary | 2026 (UE 5.8 page, v | 2026-09-10 | Unreal Engine 5.8 | PC (Windows) / current consoles | Sections: '# Virtual Texturing', '## Virtual Texturing Methods' (RVT vs SVT comparison bullets), '### Runtime Virtual Texturing', '### Streaming Virtual Texturing', '#### Virtual Texture Lightmaps' (r.IncludeNonVirtualTexturedLightmaps, r.VT.EnableLossyCompressLightmaps), '## Virtual Texture Topics' | verified |
| SRC-WRS-009 | Streaming Virtual Texturing in Unreal Engine | Epic Games / Epic Developer Community | secondary | 2026 (UE 5.8 page, v | 2026-09-10 | Unreal Engine 5.8 | PC (Windows) / current consoles | Sections: '# Streaming Virtual Texturing', '## Enabling Streaming Virtual Texturing', '## Using Streaming Virtual Textures', '## ...UDIM', '## Limitations' (single vs double indirection, anisotropic filtering cost, feedback buffer latency) | verified |
| SRC-WRS-010 | Runtime Virtual Texturing in Unreal Engine | Epic Games / Epic Developer Community | secondary | 2026 (UE 5.8 page, v | 2026-09-10 | Unreal Engine 5.8 | PC (Windows) / current consoles | Sections: '# Runtime Virtual Texturing', '## Setting Up Runtime Virtual Textures', '## Runtime Virtual Texture Assets', '## ...Landscape', '## Limitations' | verified |
| SRC-WRS-011 | Virtual Texture Memory Pools in Unreal Engine | Epic Games / Epic Developer Community | secondary | 2026 (UE 5.8 page, v | 2026-09-10 | Unreal Engine 5.8 | PC (Windows) / current consoles | Sections: '# Virtual Texture Memory Pools', '## Physical Memory Pool', '## Residency graph', '## Fixed pool sizes per format group', '## Overflow behaviour' | verified |
| SRC-WRS-012 | Texture Streaming in Unreal Engine | Epic Games / Epic Developer Community | secondary | 2026 (UE 5.8 page, v | 2026-09-10 | Unreal Engine 5.8 | PC (Windows) / all | Sections: '# Texture Streaming', '## ...Mip-based streaming', '## ...Pool size', '## ...r.Streaming.PoolSize', '## ...Limitations' | verified |
| SRC-WRS-013 | Mesh Distance Fields in Unreal Engine | Epic Games / Epic Developer Community | secondary | 2026 (UE 5.8 page, v | 2026-09-10 | Unreal Engine 5.8 | DX11+ (feature level 5) | Sections: '# Mesh Distance Fields', '## How does it work?', '## Scene Representation', '### Quality' ('The maximum size volume texture any single mesh can have is 8 megabytes with a resolution of 128x128x128'), '### Global Distance Field', '### Foliage', '#### Two-Sided Distance Field', '#### Foliag | verified |
| SRC-WRS-014 | Distance Field Soft Shadows in Unreal Engine | Epic Games / Epic Developer Community | secondary | 2026 (UE 5.8 page, v | 2026-09-10 | Unreal Engine 5.8 | DX11+ (feature level 5) | Sections: '# Distance Field Soft Shadows', '## Setting Up Distance Field Soft Shadows', '## ...Ray Start Offset / Trace Distance', '## ...Limitations' | verified |
| SRC-WRS-015 | Precomputed Visibility Volumes in Unreal Engine | Epic Games / Epic Developer Community | secondary | 2026 (UE 5.8 page, v | 2026-09-10 | Unreal Engine 5.8 | PC (Windows) / mobile / current consoles | Sections: '# Precomputed Visibility Volumes', '## Setup and Usage', '### Visibility Cells', '### Setting Cell Play Area Height for Gameplay' ([DevOptions.PrecomputedVisibility] ini block: NumCellDistributionBuckets=800, PlayAreaHeight=220, MeshBoundsScale=1.2, MinMeshSamples=14, MaxMeshSamples=40, N | verified |
| SRC-WRS-016 | Visibility and Occlusion Culling in Unreal Engine | Epic Games / Epic Developer Community | secondary | 2026 (UE 5.8 page, v | 2026-09-10 | Unreal Engine 5.8 | PC (Windows) / all | Sections: '# Visibility and Occlusion Culling', '## Culling Methods' (distance / view frustum / dynamic occlusion / precomputed visibility), '## ...Choosing a method' | verified |
| SRC-WRS-017 | Landscape Technical Guide in Unreal Engine | Epic Games / Epic Developer Community | secondary | 2026 (UE 5.8 page, v | 2026-09-10 | Unreal Engine 5.8 | PC (Windows) / all | Sections: '# Landscape Technical Guide', '## Landscape Components', '## Component Sections', '## Landscape Component UI', '## Performance Considerations' ('Each Landscape Component has a render-thread CPU processing cost and each section is a draw call ... Epic recommends a maximum of 1024 Landscape | verified |
| SRC-WRS-018 | Asynchronous Asset Loading in Unreal Engine | Epic Games / Epic Developer Community | secondary | 2026 (UE 5.8 page, v | 2026-09-10 | Unreal Engine 5.8 | PC (Windows) / all | Sections: '# Asynchronous Asset Loading', '## FSoftObjectPaths and TSoftObjectPtr', '## The Asset Registry and Object Libraries', '## StreamableManager and Asynchronous Loading' (SynchronousLoad vs RequestAsyncLoad; 'StreamableManager keeps hard references to any assets it loads until the delegate i | verified |
| SRC-WRS-019 | Oodle Data (Unreal Engine Documentation) | Epic Games / Epic Developer Community (RAD Game Tools technology) | secondary | 2026 (UE 5.x page, v | 2026-09-10 | Unreal Engine 5.x (Oodle 2.9.x) | PC (Windows) / consoles | Sections: '# Oodle Data', '## Key Concepts for Oodle Data', '## Compression Methods' (Kraken / Mermaid / Selkie / Leviathan table), '## Compression Level (Effort Level)' (level -4 HyperFast4 to 9 Optimal5), '## Enabling Oodle Data', '## Properties / Settings' (PakFileCompressionFormats=Oodle, -compr | verified |
| SRC-WRS-020 | Cooking and Chunking in Unreal Engine | Epic Games / Epic Developer Community | secondary | 2026 (UE 5.8 page, v | 2026-09-10 | Unreal Engine 5.8 | PC (Windows) / all | Sections: '# Cooking and Chunking', '## ...Chunking', '## ...Chunk IDs', '## ...Primary Asset Labels', '## ...Chunking in World Partition' | verified |
| SRC-WRS-021 | Foliage Mode in Unreal Engine | Epic Games / Epic Developer Community | secondary | 2026 (UE 5.8 page, v | 2026-09-10 | Unreal Engine 5.8 | PC (Windows) / all | Sections: '# Foliage Mode', '## Painting Foliage', '## Foliage Types', '## ...Instance Settings' (density, cull distance, LOD settings), '## ...Affect Distance Field Lighting' | verified |
| SRC-WRS-022 | Instanced Static Mesh in Unreal Engine | Epic Games / Epic Developer Community | secondary | 2026 (UE 5.8 page, v | 2026-09-10 | Unreal Engine 5.8 | PC (Windows) / all | Sections: '# Instanced Static Mesh', '## ...Creating an ISM', '## ...Instance Count / Transforms', '## ...Per-instance LOD and cull distance' | verified |
| SRC-WRS-023 | Hierarchical Instanced Static Mesh in Unreal Engine | Epic Games / Epic Developer Community | secondary | 2026 (UE 5.8 page, v | 2026-09-10 | Unreal Engine 5.8 | PC (Windows) / all | Sections: '# Hierarchical Instanced Static Mesh', '## ...Cluster tree', '## ...Per-cluster culling and LOD', '## ...When to use HISM vs ISM' | verified |
| SRC-WRS-024 | Automatic Static Mesh LOD Generation in Unreal Engine | Epic Games / Epic Developer Community | secondary | 2026 (UE 5.8 page, v | 2026-09-10 | Unreal Engine 5.8 | PC (Windows) / all | Sections: '# Automatic Static Mesh LOD Generation', '## ...Reduction Settings', '## ...Screen Size per LOD', '## ...Generating LODs' | verified |
| SRC-WRS-025 | Procedural Content Generation Overview (Unreal Engine) | Epic Games / Epic Developer Community | secondary | 2026 (UE 5.8 page, v | 2026-09-10 | Unreal Engine 5.8 | PC (Windows) / all | Sections: '# Procedural Content Generation Overview', '## PCG Graph', '## PCG Component', '## ...Static vs Dynamic generation', '## ...Determinism and seeding' | verified |
| SRC-WRS-026 | Nanite: A Deep Dive (SIGGRAPH 2021, Advances in Real-Time Rendering in Games) | Brian Karis, Rune Stubbe, Graham Wihlidal (Epic Games) | secondary | 2021-08-10 | 2026-09-10 | Unreal Engine 5 (early access) | PC (DX12 SM6) + PS5/Xbox Series | Slides: p.16 'Triangle cluster culling'; p.17 'Occlusion culling' (test against lowest HZB mip where screen rect <= 4x4); p.28 'Cluster hierarchy'; p.44 'Explicit dependency / Quick-VDR / Batched Multi-Triangulation'; p.47 'DAG'; p.49 METIS graph partitioning; p.67 'Seamless LOD' (if < 1 pixel error | verified |
| SRC-WRS-027 | GPU-Driven Rendering Pipelines (SIGGRAPH 2015, Advances in Real-Time Rendering in Games) | Ulrich Haar (Ubisoft Montreal), Sebastian Aaltonen (RedLynx, Ubisoft) | secondary | 2015-08-13 | 2026-09-10 | DirectX 11 (console) + DX12 notes; Assassin's Creed Unity / RedLynx in-house eng | PS4 / Xbox One / PC | Slides: p.9 AC Unity '~10x instances compared to previous Assassin's Creed games'; p.10 'Mesh Cluster Rendering' (fixed topology 64 vertex strip); p.12 '64 triangles per cluster'; p.13 pipeline diagram (MULTI-DRAW -> INSTANCE CULLING -> CLUSTER CHUNK EXPANSION -> CLUSTER CULLING -> INDEX BUFFER COMP | verified |
| SRC-WRS-028 | GPU Gems 2, Chapter 2: Terrain Rendering Using GPU-Based Geometry Clipmaps | Arul Asirvatham and Hugues Hoppe (NVIDIA / Microsoft Research), Addison-Wesley | secondary | 2005 | 2026-09-10 | Direct3D 9 (vertex textures), GeForce 6800 GT | PC (Windows) | Sections: '2.1 Review of Geometry Clipmaps', '2.2 Overview of GPU Implementation' ('2.2.1 Data Structures', '2.2.2 Clipmap Size'), '2.3 Rendering' ('2.3.1 Active Levels', '2.3.2 Vertex and Index Buffers', '2.3.3 View Frustum Culling', '2.3.4 DrawPrimitive Calls', '2.3.5 The Vertex Shader', '2.3.6 Th | verified |
| SRC-WRS-029 | GPU Gems 3, Chapter 4: Next-Generation SpeedTree Rendering | NVIDIA / IDV Inc. (SpeedTree), Addison-Wesley | secondary | 2007 | 2026-09-10 | Direct3D 10, GeForce 8800 | PC (Windows) | Sections: 'Chapter 4. Next-Generation SpeedTree Rendering', '4.1 ...' core/branch/frond/leaf geometry, silhouette fins with height-map tracing, relief mapping, leaf-card and billboard LOD discussion, ambient/spherical-harmonic lighting of foliage | verified |
| SRC-WRS-030 | Chunked LOD (SIGGRAPH 2002 'Super-size it! Scaling up to Massive Virtual Worlds' course notes + site) | Thatcher Ulrich | secondary | 2002 | 2026-09-10 | OpenGL / Direct3D 8-era, public-domain reference implementation | PC (Win32 / Linux) | Sections: 'Chunked LOD' overview, 'News' dated entries (23 June 2002: 32K x 32K quadtree-tiled texture, 9-level quadtree of 128 x 128 jpeg-compressed nodes, ~61 MB jpeg, 1024x768, ~30 fps on 1 GHz P3 with GeForce2Go; 31 March 2002: 16K x 16K Puget Sound dataset, raw heightmap 16K x 16K x 16 bits = 5 | verified |
| SRC-WRS-031 | C-BDAM - Compressed Batched Dynamic Adaptive Meshes for Terrain Rendering | Enrico Gobbetti, Fabio Marton, Paolo Cignoni, Marco Di Benedetto, Fabio Ganovelli (CRS4 / CNR), Eurographics 2006 | secondary | 2006 | 2026-09-10 | GPU batched out-of-core terrain renderer (research) | PC (Windows) | p.1 abstract and 'Contribution' / 'Advantages' sections; Figure 1 caption: 'View of the Earth near Guadalajara. This 29G samples sparse global dataset is compressed to 0.25bps.'; comparison paragraph contrasting out-of-core chunked bintree methods (BDAM, P-BDAM) with in-core nested regular grids (Ge | verified |
| SRC-WRS-032 | Sparse Virtual Textures (GDC 2008 talk, slides + public-domain demo source) | Sean Barrett | secondary | 2008 | 2026-09-10 | OpenGL, Windows research codebase (public domain) | PC (Windows) | Page sections: '# Sparse Virtual Textures' (technique description: 'downloading only the data that is needed, and using a pixel shader to map from the virtual large texture to the actual physical texture'), '## Forum', '## Links' (id Software whitepapers on Real-Time Texture Streaming Decompression | verified |
| SRC-WRS-033 | Software Virtual Textures | J.M.P. van Waveren (id Software) | secondary | 2012 | 2026-09-10 | id Tech 5 (RAGE) era | PC (Windows) / Xbox 360 / PS3 | Paper: page table and physical page cache architecture, virtual texture feedback and page-id rendering pass, anisotropic trilinear filtering with page borders, transcode/decompression on load, cache eviction policy (figures/tables throughout) | verified |
| SRC-WRS-034 | DirectStorage (Win32 apps) - Microsoft Learn | Microsoft | secondary | 2025-03-12 (page dat | 2026-09-10 | DirectStorage for Windows (dstorage.h) | PC (Windows) | Sections: '# DirectStorage' ('intended to allow games to make full use of high-speed storage (such as NVMe SSDs) that can deliver multiple gigabytes a second of small (for example, 64kb) data reads with minimal CPU overhead'), topic table linking 'Using DirectStorage' and 'DirectStorage API referenc | verified |
| SRC-WRS-035 | Using DirectStorage - Microsoft Learn | Microsoft | secondary | 2023-06-12 (page dat | 2026-09-10 | DirectStorage for Windows | PC (Windows) | Sections: 'Using DirectStorage' walkthrough: queue creation, request enqueue, fence-based completion, decompression (GDeflate) option, and the requirement to batch many small reads rather than one large read | verified |
| SRC-WRS-036 | microsoft/DirectStorage (GitHub) - GDeflate README | Microsoft | secondary | 2026 (repo state, ve | 2026-09-10 | GDeflate (DirectStorage bulk decompression format) | PC (Windows) | Sections: '# GDeflate' description of the bitstream ('designed to allow for concurrent decoding of symbols from different sub-streams in a bulk-synchronous ...'), sub-stream structure and decompression interface | verified |
| SRC-WRS-037 | Tiled resources (Direct3D 11.2) - Microsoft Learn | Microsoft | api_specification | 2019 (page date), ve | 2026-09-10 | Direct3D 11.2 / 12 (reserved resources) | PC (Windows) | Sections: '# Tiled resources', '## Why use tiled resources?', '## Tile pool', '## Tiled resource creation', '## Mapping and unmapping', '## Limitations' (tile granularity, no filtering across tile boundaries within a partially mapped resource) | verified |
| SRC-WRS-038 | Terrain Rendering in 'Far Cry 5' (GDC 2018) | Ubisoft Montreal (GDC Vault) | secondary | 2018 | 2026-09-10 | Dunia engine | PC (Windows) / PS4 / Xbox One | GDC Vault session page abstract; the talk's described structure (GPU-driven terrain pipeline, deferred texturing, cliff/rock shading) is reported in secondary write-ups - I could not open the slides, so no slide numbers or measured ms figures are cited | verified |
| SRC-WRS-039 | GPU-Based Procedural Placement in Horizon Zero Dawn (GDC 2017) | Jaap van Muijden, Guerrilla Games (GDC 2017 / guerrilla-games.com) | secondary | 2017-03-01 | 2026-09-10 | Decima engine | PS4 / PC (Windows) | Studio page abstract: 'Jaap van Muijden describes the GPU based procedural placement system that dynamically creates the world of Horizon Zero Dawn around the player... assembles fully-fledged environments while the player walks through them, complete with sounds, effects, wildlife and game-play ele | verified |
| SRC-WRS-040 | Continuous World Generation in 'No Man's Sky' (GDC 2017) | Hello Games (GDC Vault) | secondary | 2017 | 2026-09-10 | Hello Games in-house engine | PC (Windows) / PS4 | GDC Vault session page abstract ('Giving insight into the challenges Hello Games faced in developing a vast game-world as a small team...') | verified |
| SRC-WRS-041 | Chunk format - Minecraft Wiki | Minecraft Wiki community | secondary | 2026 (wiki state, ve | 2026-09-10 | Minecraft Java Edition (Anvil format, 1.18+) | PC (Windows / Linux / macOS) | Sections: '# Chunk format', '## NBT structure' (chunk = 16x384x16 blocks in the Overworld, 16x256x16 in Nether/End; each section is a 16x16x16-block area; block_states.data = Long Array of 4096 packed indices, min 4 bits, palette up to 4096 entries; biomes.data = 64 packed indices for 4x4x4 cells; h | verified |
| SRC-WRS-042 | Chunk - Minecraft Wiki | Minecraft Wiki community | secondary | 2026 (wiki state, ve | 2026-09-10 | Minecraft Java Edition | PC | Sections: '# Chunk' (definition: 16x16 columns of blocks extending the full world height, the unit of world generation, loading and terrain population), generation/loading lifecycle discussion | verified |
| SRC-WRS-043 | Simulation distance - Minecraft Wiki | Minecraft Wiki community | secondary | 2026 (wiki state, ve | 2026-09-10 | Minecraft Java Edition | PC | Sections: '# Simulation distance' (definition and its separation from render distance; chunk ticking radius in chunks) | verified |
| SRC-WRS-044 | meshoptimizer (GitHub README) | Arseny Kapoulkine (zeux) | secondary | 2026 (repo state, ve | 2026-09-10 | meshoptimizer (C/C++, header + source) | PC / any | README sections: '# Vertex cache optimization' ('The worst-case ACMR is 3'; 'on regular grids the optimal ACMR approaches 0.5'; 'On real meshes it usually is in [0.5..1.5] range'; 'Historically, GPUs used a small fixed-size post-transform cache (16-32 vertices)'), '# Overdraw optimization' (threshol | verified |
| SRC-WRS-045 | Random-Access Neural Compression of Material Textures (project page, SIGGRAPH 2023) | Karthik Vaidyanathan, Marco Salvi, Bartlomiej Wronski, Tomas Akenine-Moller, Pontus Ebelin, Aaron Lefohn (NVIDIA) | secondary | 2023 | 2026-09-10 | NTC (neural texture compression) | PC (DX12 / Vulkan) | Page sections: title/authors ('Accepted to Siggraph 2023'), teaser caption ('NTC provides a 4x higher resolution (16X texels) compared to BC high, despite using 30% less memory'), 'Abstract' ('We unlock two more levels of detail, i.e., 16X more texels, using low bitrate compression, with image quali | verified |
| SRC-WRS-046 | Random-Access Neural Compression of Material Textures (author's version, PDF) | Vaidyanathan, Salvi, Wronski, Akenine-Moller, Ebelin, Lefohn (NVIDIA), SIGGRAPH 2023 | secondary | 2023 | 2026-09-10 | NTC | PC (DX12 / Vulkan) | Paper sections: abstract, network architecture and per-material fitting, on-demand transcode/decode path for random access, training speed vs PyTorch ('surpasses that of general frameworks, like PyTorch, by an order of magnitude'), results tables (PSNR / FLIP vs BCn, AVIF, JPEG XL) | verified |
| SRC-WRS-047 | NVIDIA-RTX/RTXNTC: NVIDIA Neural Texture Compression SDK | NVIDIA (GitHub) | secondary | 2026 (repo state, ve | 2026-09-10 | RTXNTC SDK (v0.9.x beta at time of check) | PC (DX12 / Vulkan), UE plugin | README sections: '# Neural Texture Compression' ('NTC is an algorithm designed to compress all PBR textures used for a single material...'), supported APIs, integration notes, and the beta status / known issues in Releases | verified |
| SRC-WRS-048 | Octahedral Impostors | Ryan Brucks (shaderbits.com) | secondary | 2018 (Nanite referen | 2026-09-10 | Unreal Engine 4 (octahedral impostor shader) | PC (Windows) | Article: octahedral mapping of view direction to atlas location, dithered direction quantisation, orthogonal capture projection fitted to the mesh AABB, depth+normal storage, ray-marched parallax correction between directions | verified |
| SRC-WRS-049 | Large world coordinates - Godot Engine (4.4) documentation | Godot Engine contributors | secondary | 2025-04-14 (page dat | 2026-09-10 | Godot 4.4 (double-precision builds) | PC / all | Sections: '# Large world coordinates', '## Why use large world coordinates?' (float precision loss at large coordinates), '## ...' enabling double precision, and the note that 'On low-end platforms, an origin shifting approach can be used instead to allow for large worlds without using' double preci | verified |
| SRC-WRS-050 | Updating Game Build (Steamworks Documentation) | Valve (Steamworks) | secondary | 2026 (page state, ve | 2026-09-10 | Steamworks SDK / SteamPipe | PC (Windows / Linux / macOS) | Sections: 'Updating Game Build' ('To update your game or software build, simply follow the same instructions for creating your initial builds in SteamPipe...'), depot/branch handling when pushing an update | verified (page returns 200; fu |
| SRC-WRS-051 | Building Worlds Using Math(s) (GDC 2017, No Man's Sky) | Hello Games (GDC Vault) | secondary | 2017 | 2026-09-10 | Hello Games in-house engine | PC / PS4 | GDC Vault session page abstract (procedural generation of a near-infinite universe) | verified |
| SRC-WRS-052 | DirectStorage GpuDecompressionBenchmark sample (GitHub) | Microsoft | secondary | 2026 (repo state, ve | 2026-09-10 | DirectStorage for Windows | PC (Windows) | README: 'This sample provides a quick way to see the DirectStorage runtime decompression performance by reading the contents of a file...' (i.e. it is a measurement harness, not a published result) | verified |
| SRC-WRS-053 | SteamPipe / Uploading to Steam (Steamworks Documentation) | Valve (Steamworks) | secondary | undated (verified 20 | 2026-09-10 | SteamPipe | PC (Steam) | Sections: 'SteamPipe' ('SteamPipe initially splits each file into roughly one megabyte (MB) chunks...'), build/upload process ('Each file is scanned and divided into small chunks of about 1MB...'), pack-file guidance ('limit the size of pack files. Probably one or two gigabytes (GB)...'), Unreal pad | verified (page returns 200; fu |
| SRC-WRS-054 | DirectStorage API Now Available on PC (DirectX Developer Blog) | Microsoft (Cassie Hoef) | secondary | 2022-03-14 | 2026-09-10 | DirectStorage for Windows (1.0) | PC (Windows 10/11) | '# DirectStorage API Now Available on PC': 'Starting today, Windows games can ship with DirectStorage.'; 'What's Next?' ('GPU decompression is next on our roadmap...'); 'Getting Started - Gamers' ('installing games to an NVMe SSD will maximize your IO performance'); developer section pointing to 'th | verified |
| SRC-WRS-055 | meshoptimizer users (maintainer's list of commercial games and engines) | Arseny Kapoulkine (zeux) | secondary | 2025-11-18 (discussi | 2026-09-10 | meshoptimizer | PC and multi-platform | 'Games' list (Alan Wake 2, Baldur's Gate 3, Counter-Strike 2, Cyberpunk 2077, Dota 2, Half-Life: Alyx and others); 'Engines' list; opening note ('This list is very incomplete, as often commercial projects use meshoptimizer in internal content pipelines and don't always report/credit the usage') | verified |
| STANDARD_VULKAN_SPEC | Vulkan 1.3 Extensions Specification | Khronos Vulkan Working Group | standard | 2022 | 2026-09-10 | 1.3 extensions |  | chapters: device features, queues, synchronization | available |
| TECH_CAPTURE | Epic: Scene Capture |  | official_documentation | n/a | 2026-09-10 |  |  | overview page | available |
| TECH_CLOTH | Unity 6: Cloth |  | official_documentation | n/a | 2026-09-10 |  |  | overview page | available |
| TECH_DESTRUCTION | Epic: Destruction Overview |  | official_documentation | n/a | 2026-09-10 |  |  | overview page | available |
| TECH_HAIR | Epic: Hair Rendering and Simulation |  | official_documentation | n/a | 2026-09-10 |  |  | overview page | available |
| TECH_REVERB | Epic: Convolution Reverb |  | official_documentation | n/a | 2026-09-10 |  |  | overview page | available |
| TECH_SECURITY | Epic: Anti-Cheat Interfaces |  | official_documentation | n/a | 2026-09-10 |  |  | overview page | available |
| UE_ANIMBUDGET | Unreal Engine: Animation Budget Allocator |  | official_documentation | n/a | 2026-09-10 |  |  | overview page | available |
| UE_CHAOS | Unreal Engine: Chaos Physics |  | official_documentation | n/a | 2026-09-10 |  |  | overview page | available |
| UE_CITY_SAMPLE | City Sample Project Unreal Engine Demonstration |  | official_case_study | n/a | 2026-09-10 |  |  | sections: World Partition, Nanite Virtualized Geometry, Mass AI | available |
| UE_CITY_SAMPLE_PCG | City Sample PCG for Unreal Engine |  | official_documentation | n/a | 2026-09-10 |  |  | section: procedural city and PCG graph examples | available |
| UE_DISTANCE_SHADOWS | Unreal Engine: Using Distance Field Shadows |  | official_documentation | n/a | 2026-09-10 |  |  | overview page | available |
| UE_FEATURE_MATRIX | Supported Features by Rendering Path for Desktop |  | official_documentation | n/a | 2026-09-10 |  |  | table: Supported Features by Rendering Path | available |
| UE_HLOD | Unreal Engine: Hierarchical Level of Detail |  | official_documentation | n/a | 2026-09-10 |  |  | overview page | available |
| UE_INSIGHTS | Unreal Engine: Unreal Insights |  | official_documentation | n/a | 2026-09-10 |  |  | overview page | available |
| UE_ISM | Unreal Engine: Instanced Static Mesh |  | official_documentation | n/a | 2026-09-10 |  |  | overview page | available |
| UE_LOD | Unreal Engine: Level of Detail |  | official_documentation | n/a | 2026-09-10 |  |  | overview page | available |
| UE_LUMEN | Unreal Engine: Lumen Global Illumination and Reflections |  | official_documentation | n/a | 2026-09-10 |  |  | section: Lumen Global Illumination and Reflections | available |
| UE_LWC | Unreal Engine: Large World Coordinates |  | official_documentation | n/a | 2026-09-10 |  |  | overview page | available |
| UE_MASS | Unreal Engine: Mass Entity |  | official_documentation | n/a | 2026-09-10 |  |  | overview page | available |
| UE_MOTION_MATCHING | Motion Matching in Unreal Engine |  | official_documentation | n/a | 2026-09-10 |  |  | overview page | available |
| UE_NANITE | Unreal Engine: Nanite Virtualized Geometry |  | official_documentation | n/a | 2026-09-10 |  |  | section: Nanite Virtualized Geometry overview | available |
| UE_NAVMESH | Unreal Engine: Navigation Mesh |  | official_documentation | n/a | 2026-09-10 |  |  | overview page | available |
| UE_NETWORKING | Unreal Engine: Networking and Multiplayer |  | official_documentation | n/a | 2026-09-10 |  |  | overview page | available |
| UE_NIAGARA | Unreal Engine: Niagara Visual Effects |  | official_documentation | n/a | 2026-09-10 |  |  | overview page | available |
| UE_REPGRAPH | Unreal Engine: Replication Graph |  | official_documentation | n/a | 2026-09-10 |  |  | overview page | available |
| UE_SAVEGAME | Unreal Engine: Saving and Loading Your Game |  | official_documentation | n/a | 2026-09-10 |  |  | overview page | available |
| UE_SCALABILITY | Unreal Engine: Scalability Reference |  | official_documentation | n/a | 2026-09-10 |  |  | overview page | available |
| UE_SIGNIFICANCE | Unreal Engine: Significance Manager |  | official_documentation | n/a | 2026-09-10 |  |  | overview page | available |
| UE_VIRTUALTEXTURING | Unreal Engine: Virtual Texturing |  | official_documentation | n/a | 2026-09-10 |  |  | overview page | available |
| UE_VSM | Unreal Engine: Virtual Shadow Maps |  | official_documentation | n/a | 2026-09-10 |  |  | section: Virtual Shadow Maps | available |
| UE_WORLDPARTITION | Unreal Engine: World Partition |  | official_documentation | n/a | 2026-09-10 |  |  | sections: World Partition, Streaming Sources | available |
| UNITY_ADDRESSABLES | Unity Manual: Addressables |  | official_documentation | n/a | 2026-09-10 |  |  | section: Addressables overview | available |
| UNITY_DOTS_PRODUCTION | Unity DOTS - Data-Oriented Technology Stack |  | official_case_index | 2024 | 2026-09-10 |  |  | section: DOTS in Production | available |
| UNITY_DRAW_CALLS | Unity Manual: Choose a method for optimizing draw calls |  | official_documentation | n/a | 2026-09-10 |  |  | overview page | available |
| UNITY_ENTITIES | Unity Manual: Entities (DOTS) |  | official_documentation | n/a | 2026-09-10 |  |  | section: Entities overview | available |
| UNITY_GC_BEST_PRACTICES | Unity Manual: Garbage collection best practices |  | official_documentation | n/a | 2026-09-10 |  |  | overview page | available |
| UNITY_GFX_PERF | Unity Manual: Optimizing Graphics Performance |  | official_documentation | n/a | 2026-09-10 |  |  | overview page | available |
| UNITY_GPU_BUDGETS | Unity — Managing GPU usage for PC and console games |  | official_documentation | n/a | 2026-09-10 |  |  | overview page | available |
| UNITY_INSTANCING | Unity Manual: GPU Instancing |  | official_documentation | n/a | 2026-09-10 |  |  | overview page | available |
| UNITY_JOBS | Unity Manual: Job System |  | official_documentation | n/a | 2026-09-10 |  |  | section: Job System overview | available |
| UNITY_LIGHTMAPPER | Unity Manual: Progressive Lightmapper |  | official_documentation | n/a | 2026-09-10 |  |  | overview page | available |
| UNITY_LIGHTMAPUV | Unity Manual: Generating Lightmapping UVs |  | official_documentation | n/a | 2026-09-10 |  |  | overview page | available |
| UNITY_LIGHTPROBES | Unity Manual: Light Probes |  | official_documentation | n/a | 2026-09-10 |  |  | overview page | available |
| UNITY_NETCODE | Unity Manual: Netcode |  | official_documentation | n/a | 2026-09-10 |  |  | section: Netcode for Entities overview | available |
| UNITY_OCCLUSION | Unity Manual: Occlusion Culling |  | official_documentation | n/a | 2026-09-10 |  |  | overview page | available |
| UNITY_PROFILER | Unity Manual: Profiler |  | official_documentation | n/a | 2026-09-10 |  |  | overview page | available |
| UNITY_QUALITY | Unity Manual: Quality Settings |  | official_documentation | n/a | 2026-09-10 |  |  | overview page | available |
| UNITY_SHADERLOAD | Unity Manual: Optimizing Shader Load Time |  | official_documentation | n/a | 2026-09-10 |  |  | overview page | available |
| UNITY_SRP_BATCHER | Unity Manual: SRP Batcher |  | official_documentation | n/a | 2026-09-10 |  |  | overview page | available |
| UNITY_TEXTURE_STREAMING | Unity Manual: Texture Streaming |  | official_documentation | n/a | 2026-09-10 |  |  | overview page | available |
| VALVE_DIRECTOR | The AI Systems of Left 4 Dead — Michael Booth, Valve |  | secondary | 2009 | 2026-09-10 |  |  | overview page | available |
| VALVE_REWIND | Valve Source SDK — player_lagcompensation.cpp |  | open_source | n/a | 2026-09-10 |  |  | overview page | available |
| VALVE_SUBTICK | Counter-Strike 2 — sub-tick updates, Valve |  | engineering_article | 2023-03-22 | 2026-09-10 |  |  | overview page | available |
| WIKI_AO | Ambient occlusion |  | secondary | n/a | 2026-09-10 |  |  | overview page | available |
| WIKI_ATLAS | Texture atlas |  | secondary | n/a | 2026-09-10 |  |  | overview page | available |
| WIKI_BEHAVIOR_TREE | Behavior tree (artificial intelligence, robotics and control) |  | secondary | n/a | 2026-09-10 |  |  | overview page | available |
| WIKI_BVH | Bounding volume hierarchy |  | secondary | n/a | 2026-09-10 |  |  | overview page | available |
| WIKI_DEFERRED | Deferred shading |  | secondary | n/a | 2026-09-10 |  |  | overview page | available |
| WIKI_DELTA | Delta encoding |  | secondary | n/a | 2026-09-10 |  |  | overview page | available |
| WIKI_DLSS | Deep learning super sampling |  | secondary | n/a | 2026-09-10 |  |  | overview page | available |
| WIKI_DOD | Data-oriented design |  | secondary | n/a | 2026-09-10 |  |  | overview page | available |
| WIKI_ECS | Entity component system |  | secondary | n/a | 2026-09-10 |  |  | overview page | available |
| WIKI_FFT | Fast Fourier transform |  | secondary | n/a | 2026-09-10 |  |  | overview page | available |
| WIKI_FSM | Finite-state machine |  | secondary | n/a | 2026-09-10 |  |  | overview page | available |
| WIKI_FSR | FidelityFX Super Resolution |  | secondary | n/a | 2026-09-10 |  |  | overview page | available |
| WIKI_GAME_AI | Video game artificial intelligence |  | secondary | n/a | 2026-09-10 |  |  | overview page | available |
| WIKI_GERSTNER | Gerstner wave |  | secondary | n/a | 2026-09-10 |  |  | overview page | available |
| WIKI_GLOBAL_ILLUMINATION | Global illumination |  | secondary | n/a | 2026-09-10 |  |  | overview page | available |
| WIKI_HSR | Hidden-surface determination |  | secondary | n/a | 2026-09-10 |  |  | overview page | available |
| WIKI_IK | Inverse kinematics |  | secondary | n/a | 2026-09-10 |  |  | overview page | available |
| WIKI_IMPOSTOR | Impostor (computer graphics) |  | secondary | n/a | 2026-09-10 |  |  | overview page | available |
| WIKI_LIGHTMAP | Lightmap |  | secondary | n/a | 2026-09-10 |  |  | overview page | available |
| WIKI_LOD | Level of detail (computer graphics) |  | secondary | n/a | 2026-09-10 |  |  | overview page | available |
| WIKI_MIPMAP | Mipmap |  | secondary | n/a | 2026-09-10 |  |  | overview page | available |
| WIKI_NAVMESH | Navigation mesh |  | secondary | n/a | 2026-09-10 |  |  | overview page | available |
| WIKI_OBJECTPOOL | Object pool pattern |  | secondary | n/a | 2026-09-10 |  |  | overview page | available |
| WIKI_PARTICLES | Particle system |  | secondary | n/a | 2026-09-10 |  |  | overview page | available |
| WIKI_PATH_TRACING | Path tracing |  | secondary | n/a | 2026-09-10 |  |  | overview page | available |
| WIKI_PREDICTION | Client-side prediction |  | secondary | n/a | 2026-09-10 |  |  | overview page | available |
| WIKI_PROCEDURAL | Procedural generation |  | secondary | n/a | 2026-09-10 |  |  | overview page | available |
| WIKI_RAGDOLL | Ragdoll physics |  | secondary | n/a | 2026-09-10 |  |  | overview page | available |
| WIKI_RAY_TRACING | Ray tracing (graphics) |  | secondary | n/a | 2026-09-10 |  |  | overview page | available |
| WIKI_RIGID_BODY | Rigid body dynamics |  | secondary | n/a | 2026-09-10 |  |  | overview page | available |
| WIKI_SDF | Signed distance function |  | secondary | n/a | 2026-09-10 |  |  | overview page | available |
| WIKI_SHADOWMAP | Shadow mapping |  | secondary | n/a | 2026-09-10 |  |  | overview page | available |
| WIKI_SKINNING | Skinning |  | secondary | n/a | 2026-09-10 |  |  | overview page | available |
| WIKI_SVO | Sparse voxel octree |  | secondary | n/a | 2026-09-10 |  |  | overview page | available |
| WIKI_TAA | Temporal anti-aliasing |  | secondary | n/a | 2026-09-10 |  |  | overview page | available |
| WIKI_VEHICLE_DYNAMICS | Vehicle dynamics |  | secondary | n/a | 2026-09-10 |  |  | overview page | available |
| WIKI_VOLUMETRIC | Volumetric rendering |  | secondary | n/a | 2026-09-10 |  |  | overview page | available |
| hardware:00acf849ec56 | PassMark Video Card Benchmarks — Radeon RX 7900 XT |  | hardware_benchmark | 2026-09-02 | 2026-09-10 |  | PC | benchmark page | available |
| hardware:04891bb1e6c7 | PassMark Intel Core i7-11800H Benchmark — CPU Mark 19596, Single 3007 |  | hardware_benchmark | 2026-09-06 | 2026-09-10 |  | PC | benchmark page | available |
| hardware:05e7e544759d | PassMark Video Card Benchmarks — GeForce RTX 3050 6GB Laptop GPU |  | hardware_benchmark | 2026-09-06 | 2026-09-10 |  | PC | benchmark page | available |
| hardware:064fe7ca5e68 | PassMark CPU Benchmarks — AMD Ryzen 5 5500 |  | hardware_benchmark | 2026-09-02 | 2026-09-10 |  | PC | benchmark page | available |
| hardware:06d672d982fc | PassMark CPU Benchmarks — Intel Core i7-9700K |  | hardware_benchmark | 2026-09-02 | 2026-09-10 |  | PC | benchmark page | available |
| hardware:080bb8b4f6d1 | PassMark Intel Core i7-13700H Benchmark — CPU Mark 25860, Single 3552 |  | hardware_benchmark | 2026-09-06 | 2026-09-10 |  | PC | benchmark page | available |
| hardware:0ae6626d2565 | PassMark Video Card Benchmarks — GeForce RTX 5050 Laptop GPU |  | hardware_benchmark | 2026-09-06 | 2026-09-10 |  | PC | benchmark page | available |
| hardware:0b39637c4ec8 | PassMark Video Card Benchmarks — GeForce RTX 2060 |  | hardware_benchmark | 2026-09-02 | 2026-09-10 |  | PC | benchmark page | available |
| hardware:0c09a16c68f9 | PassMark AMD Ryzen 5 7500F Benchmark — CPU Mark 26537, Single 3825 |  | hardware_benchmark | 2026-09-06 | 2026-09-10 |  | PC | benchmark page | available |
| hardware:0ff0fa934e0c | PassMark CPU Benchmarks — Intel Core i3-10100 |  | hardware_benchmark | 2026-09-02 | 2026-09-10 |  | PC | benchmark page | available |
| hardware:1059383223be | PassMark Intel Core i5-11400F Benchmark — CPU Mark 16869, Single 2979 |  | hardware_benchmark | 2026-09-06 | 2026-09-10 |  | PC | benchmark page | available |
| hardware:13a9cace366f | PassMark - Radeon Vega 3 - Price performance comparison |  | hardware_benchmark | 2026-09-06 | 2026-09-10 |  | PC | benchmark page | available |
| hardware:1440e3fdc3aa | PassMark Video Card Benchmarks — GeForce GTX 1650 |  | hardware_benchmark | 2026-09-02 | 2026-09-10 |  | PC | benchmark page | available |
| hardware:15733d23becf | PassMark CPU Benchmarks — Intel Core i5-10400F |  | hardware_benchmark | 2026-09-02 | 2026-09-10 |  | PC | benchmark page | available |
| hardware:15b098956b50 | PassMark AMD Ryzen 9 5950X Benchmark — CPU Mark 45259, Single 3476 |  | hardware_benchmark | 2026-09-06 | 2026-09-10 |  | PC | benchmark page | available |
| hardware:1655dac07397 | PassMark Video Card Benchmarks — GeForce GTX 1050 Ti |  | hardware_benchmark | 2026-09-02 | 2026-09-10 |  | PC | benchmark page | available |
| hardware:1663f825c7f5 | PassMark Video Card Benchmarks — GeForce RTX 3070 |  | hardware_benchmark | 2026-09-02 | 2026-09-10 |  | PC | benchmark page | available |
| hardware:1997146c058f | PassMark Video Card Benchmarks — GeForce RTX 2070 SUPER |  | hardware_benchmark | 2026-09-02 | 2026-09-10 |  | PC | benchmark page | available |
| hardware:1adf7bbcc286 | PassMark CPU Benchmarks — AMD Ryzen 5 3600 |  | hardware_benchmark | 2026-09-02 | 2026-09-10 |  | PC | benchmark page | available |
| hardware:1c641b1616ea | PassMark CPU Benchmarks — AMD Ryzen 3 1200 |  | hardware_benchmark | 2026-09-02 | 2026-09-10 |  | PC | benchmark page | available |
| hardware:1cd7069270e3 | PassMark Video Card Benchmarks — GeForce RTX 3050 8GB |  | hardware_benchmark | 2026-09-06 | 2026-09-10 |  | PC | benchmark page | available |
| hardware:1f99ebff4ca8 | PassMark CPU Benchmarks — AMD Ryzen 9 5900X |  | hardware_benchmark | 2026-09-02 | 2026-09-10 |  | PC | benchmark page | available |
| hardware:213472decf76 | PassMark - Radeon 780M - Price performance comparison |  | hardware_benchmark | 2026-09-06 | 2026-09-10 |  | PC | benchmark page | available |
| hardware:22f84720ecb7 | PassMark Video Card Benchmarks — GeForce GTX 1660 Ti |  | hardware_benchmark | 2026-09-06 | 2026-09-10 |  | PC | benchmark page | available |
| hardware:23eb35a6cdef | PassMark Video Card Benchmarks — Radeon RX 580 |  | hardware_benchmark | 2026-09-02 | 2026-09-10 |  | PC | benchmark page | available |
| hardware:24823f308139 | PassMark - Radeon RX 7700 XT - Price performance comparison |  | hardware_benchmark | 2026-09-06 | 2026-09-10 |  | PC | benchmark page | available |
| hardware:2e59fdf3fded | PassMark - GeForce GT 1030 - Price performance comparison |  | hardware_benchmark | 2026-09-06 | 2026-09-10 |  | PC | benchmark page | available |
| hardware:2f0ce84b7851 | PassMark - GeForce GTX 1050 - Price performance comparison |  | hardware_benchmark | 2026-09-06 | 2026-09-10 |  | PC | benchmark page | available |
| hardware:2f4c6f21f764 | PassMark Intel Core i7-10700K Benchmark — CPU Mark 18501, Single 3036 |  | hardware_benchmark | 2026-09-06 | 2026-09-10 |  | PC | benchmark page | available |
| hardware:32c454082048 | PassMark - GeForce RTX 2080 SUPER - Price performance comparison |  | hardware_benchmark | 2026-09-06 | 2026-09-10 |  | PC | benchmark page | available |
| hardware:32c984630655 | PassMark - Intel UHD Graphics 630 - Price performance comparison |  | hardware_benchmark | 2026-09-06 | 2026-09-10 |  | PC | benchmark page | available |
| hardware:39023f2f2854 | PassMark CPU Benchmarks — Intel Core i7-13700K |  | hardware_benchmark | 2026-09-02 | 2026-09-10 |  | PC | benchmark page | available |
| hardware:3981b71516d5 | PassMark - GeForce RTX 2080 - Price performance comparison |  | hardware_benchmark | 2026-09-06 | 2026-09-10 |  | PC | benchmark page | available |
| hardware:3a1abc3aed60 | PassMark Video Card Benchmarks — Radeon RX 6650 XT |  | hardware_benchmark | 2026-09-02 | 2026-09-10 |  | PC | benchmark page | available |
| hardware:3a9a732e872b | PassMark Video Card Benchmarks — GeForce RTX 5060 |  | hardware_benchmark | 2026-09-06 | 2026-09-10 |  | PC | benchmark page | available |
| hardware:3c9600f567cf | PassMark Video Card Benchmarks — GeForce RTX 5060 Ti 16GB |  | hardware_benchmark | 2026-09-06 | 2026-09-10 |  | PC | benchmark page | available |
| hardware:4089384ecd15 | PassMark Video Card Benchmarks — GeForce RTX 5070 Ti |  | hardware_benchmark | 2026-09-06 | 2026-09-10 |  | PC | benchmark page | available |
| hardware:485542379b36 | PassMark CPU Benchmarks — Intel Core i5-8400 |  | hardware_benchmark | 2026-09-02 | 2026-09-10 |  | PC | benchmark page | available |
| hardware:497f54760950 | PassMark Intel Core i5-13400F Benchmark — CPU Mark 24891, Single 3628 |  | hardware_benchmark | 2026-09-06 | 2026-09-10 |  | PC | benchmark page | available |
| hardware:509fd48b901b | PassMark Video Card Benchmarks — GeForce RTX 3090 |  | hardware_benchmark | 2026-09-02 | 2026-09-10 |  | PC | benchmark page | available |
| hardware:549aac87930e | PassMark - Radeon RX 550 - Price performance comparison |  | hardware_benchmark | 2026-09-06 | 2026-09-10 |  | PC | benchmark page | available |
| hardware:54a1d0ca2092 | PassMark Video Card Benchmarks — GeForce GTX 1660 |  | hardware_benchmark | 2026-09-06 | 2026-09-10 |  | PC | benchmark page | available |
| hardware:5530b216b0c2 | PassMark Video Card Benchmarks — Radeon RX 7800 XT |  | hardware_benchmark | 2026-09-02 | 2026-09-10 |  | PC | benchmark page | available |
| hardware:560fb8a216cf | PassMark CPU Benchmarks — AMD Ryzen 7 3700X |  | hardware_benchmark | 2026-09-02 | 2026-09-10 |  | PC | benchmark page | available |
| hardware:56cc05a182df | PassMark AMD Ryzen 5 5600 Benchmark — CPU Mark 21494, Single 3253 |  | hardware_benchmark | 2026-09-06 | 2026-09-10 |  | PC | benchmark page | available |
| hardware:572e0cbae2d3 | PassMark - Intel HD 4600 - Price performance comparison |  | hardware_benchmark | 2026-09-06 | 2026-09-10 |  | PC | benchmark page | available |
| hardware:5837988cc683 | PassMark Video Card Benchmarks — GeForce RTX 4060 |  | hardware_benchmark | 2026-09-02 | 2026-09-10 |  | PC | benchmark page | available |
| hardware:5946562912cb | PassMark Video Card Benchmarks — GeForce RTX 5080 |  | hardware_benchmark | 2026-09-06 | 2026-09-10 |  | PC | benchmark page | available |
| hardware:5a14b3ed7af2 | PassMark - GeForce GTX 750 Ti - Price performance comparison |  | hardware_benchmark | 2026-09-06 | 2026-09-10 |  | PC | benchmark page | available |
| hardware:62699f3b35fb | PassMark Video Card Benchmarks — GeForce GTX 1060 |  | hardware_benchmark | 2026-09-02 | 2026-09-10 |  | PC | benchmark page | available |
| hardware:67dc4c02a2fb | PassMark CPU Benchmarks — AMD Ryzen 9 3900X |  | hardware_benchmark | 2026-09-02 | 2026-09-10 |  | PC | benchmark page | available |
| hardware:67de7e601b40 | PassMark - GeForce RTX 2080 Ti - Price performance comparison |  | hardware_benchmark | 2026-09-06 | 2026-09-10 |  | PC | benchmark page | available |
| hardware:6aa408b0f708 | PassMark Intel Core i7-12700H Benchmark — CPU Mark 24995, Single 3484 |  | hardware_benchmark | 2026-09-06 | 2026-09-10 |  | PC | benchmark page | available |
| hardware:6d9377fa7453 | PassMark Video Card Benchmarks — GeForce RTX 4050 Laptop GPU |  | hardware_benchmark | 2026-09-06 | 2026-09-10 |  | PC | benchmark page | available |
| hardware:6f7108f11cd3 | PassMark Video Card Benchmarks — Radeon RX 470/570 |  | hardware_benchmark | 2026-09-02 | 2026-09-10 |  | PC | benchmark page | available |
| hardware:70abaad3db6f | PassMark - GeForce GTX 970 - Price performance comparison |  | hardware_benchmark | 2026-09-06 | 2026-09-10 |  | PC | benchmark page | available |
| hardware:70c608c01ca0 | PassMark Video Card Benchmarks — Radeon RX 9070 |  | hardware_benchmark | 2026-09-06 | 2026-09-10 |  | PC | benchmark page | available |
| hardware:7591010c1bc0 | PassMark CPU Benchmarks — Intel Core i9-14900K |  | hardware_benchmark | 2026-09-02 | 2026-09-10 |  | PC | benchmark page | available |
| hardware:77f7921c463e | PassMark CPU Benchmarks — AMD Ryzen 7 7700X |  | hardware_benchmark | 2026-09-02 | 2026-09-10 |  | PC | benchmark page | available |
| hardware:7888397167eb | PassMark Video Card Benchmarks — GeForce RTX 5090 |  | hardware_benchmark | 2026-09-06 | 2026-09-10 |  | PC | benchmark page | available |
| hardware:79f489f9e9ec | PassMark CPU Benchmarks — Intel Core i7-8700K |  | hardware_benchmark | 2026-09-02 | 2026-09-10 |  | PC | benchmark page | available |
| hardware:7e2d8d5bf5f3 | PassMark Intel Core i5-14400F Benchmark — CPU Mark 25440, Single 3700 |  | hardware_benchmark | 2026-09-06 | 2026-09-10 |  | PC | benchmark page | available |
| hardware:81c4287af43b | PassMark - Intel Iris Xe - Price performance comparison |  | hardware_benchmark | 2026-09-06 | 2026-09-10 |  | PC | benchmark page | available |
| hardware:836a9fba84c4 | PassMark CPU Benchmarks — AMD Ryzen 9 7900X |  | hardware_benchmark | 2026-09-02 | 2026-09-10 |  | PC | benchmark page | available |
| hardware:840ef9ea050b | PassMark - GeForce GT 730 - Price performance comparison |  | hardware_benchmark | 2026-09-06 | 2026-09-10 |  | PC | benchmark page | available |
| hardware:848d487dc667 | PassMark AMD Custom APU 0932 (Steam Deck) Benchmark — CPU Mark 9411, Single 2214 |  | hardware_benchmark | 2026-09-06 | 2026-09-10 |  | PC | benchmark page | available |
| hardware:8660240c2073 | PassMark Video Card Benchmarks — GeForce RTX 4090 |  | hardware_benchmark | 2026-09-02 | 2026-09-10 |  | PC | benchmark page | available |
| hardware:890bf8c8bc53 | PassMark Video Card Benchmarks — Radeon RX 6800 XT |  | hardware_benchmark | 2026-09-02 | 2026-09-10 |  | PC | benchmark page | available |
| hardware:89cbc8278eca | PassMark CPU Benchmarks — AMD Ryzen 5 5600X |  | hardware_benchmark | 2026-09-02 | 2026-09-10 |  | PC | benchmark page | available |
| hardware:8ab47fd159d4 | PassMark CPU Benchmarks — Intel Core i9-12900K |  | hardware_benchmark | 2026-09-02 | 2026-09-10 |  | PC | benchmark page | available |
| hardware:8bacc05d7fc8 | PassMark Video Card Benchmarks — GeForce RTX 4070 |  | hardware_benchmark | 2026-09-02 | 2026-09-10 |  | PC | benchmark page | available |
| hardware:8d936bf26c17 | PassMark Video Card Benchmarks — GeForce RTX 5070 Ti Laptop GPU |  | hardware_benchmark | 2026-09-06 | 2026-09-10 |  | PC | benchmark page | available |
| hardware:8e7744a9be93 | PassMark CPU Benchmarks — AMD Ryzen 9 7950X |  | hardware_benchmark | 2026-09-02 | 2026-09-10 |  | PC | benchmark page | available |
| hardware:93986f7bde58 | PassMark Video Card Benchmarks — GeForce RTX 3060 |  | hardware_benchmark | 2026-09-02 | 2026-09-10 |  | PC | benchmark page | available |
| hardware:9a24b670ca22 | PassMark - Intel HD Graphics 620 - Price performance comparison |  | hardware_benchmark | 2026-09-06 | 2026-09-10 |  | PC | benchmark page | available |
| hardware:9b457cb5c826 | PassMark CPU Benchmarks — AMD Ryzen 7 5800X3D |  | hardware_benchmark | 2026-09-02 | 2026-09-10 |  | PC | benchmark page | available |
| hardware:9b567a14b843 | PassMark Video Card Benchmarks — GeForce RTX 2050 |  | hardware_benchmark | 2026-09-06 | 2026-09-10 |  | PC | benchmark page | available |
| hardware:9b7841f454f7 | PassMark AMD Ryzen 7 9800X3D Benchmark — CPU Mark 39927, Single 4421 |  | hardware_benchmark | 2026-09-06 | 2026-09-10 |  | PC | benchmark page | available |
| hardware:9c5901396f3d | PassMark Video Card Benchmarks — GeForce GTX 1660 SUPER |  | hardware_benchmark | 2026-09-02 | 2026-09-10 |  | PC | benchmark page | available |
| hardware:9f4761331ae8 | PassMark Video Card Benchmarks — GeForce RTX 5070 Laptop GPU |  | hardware_benchmark | 2026-09-06 | 2026-09-10 |  | PC | benchmark page | available |
| hardware:9fd08f6b5c8a | PassMark AMD Ryzen 7 8745H Benchmark — CPU Mark 29058, Single 3675 |  | hardware_benchmark | 2026-09-06 | 2026-09-10 |  | PC | benchmark page | available |
| hardware:a195c699bec6 | PassMark CPU Benchmarks — Intel Core i5-9400F |  | hardware_benchmark | 2026-09-02 | 2026-09-10 |  | PC | benchmark page | available |
| hardware:a3ccb503c8b3 | PassMark CPU Benchmarks — Intel Core i9-13900K |  | hardware_benchmark | 2026-09-02 | 2026-09-10 |  | PC | benchmark page | available |
| hardware:a4f5c1213fb9 | PassMark - Intel HD 520 - Price performance comparison |  | hardware_benchmark | 2026-09-06 | 2026-09-10 |  | PC | benchmark page | available |
| hardware:a565eaa9a35f | PassMark CPU Benchmarks — Intel Core i7-12700K |  | hardware_benchmark | 2026-09-02 | 2026-09-10 |  | PC | benchmark page | available |
| hardware:a9dda230b9dd | PassMark CPU Benchmarks — AMD Ryzen 5 2600 |  | hardware_benchmark | 2026-09-02 | 2026-09-10 |  | PC | benchmark page | available |
| hardware:a9f7d96a856b | PassMark - GeForce GTX 960 - Price performance comparison |  | hardware_benchmark | 2026-09-06 | 2026-09-10 |  | PC | benchmark page | available |
| hardware:ab9c0bf794b3 | PassMark Video Card Benchmarks — GeForce RTX 3050 Laptop GPU |  | hardware_benchmark | 2026-09-06 | 2026-09-10 |  | PC | benchmark page | available |
| hardware:ae2fbdf7314d | PassMark Video Card Benchmarks — Radeon RX 7900 XTX |  | hardware_benchmark | 2026-09-02 | 2026-09-10 |  | PC | benchmark page | available |
| hardware:b01112378bcb | PassMark Video Card Benchmarks — GeForce RTX 5070 |  | hardware_benchmark | 2026-09-06 | 2026-09-10 |  | PC | benchmark page | available |
| hardware:b4f43214ca49 | PassMark - Radeon RX 6750 XT - Price performance comparison |  | hardware_benchmark | 2026-09-06 | 2026-09-10 |  | PC | benchmark page | available |
| hardware:b8eca4bb9b58 | PassMark Video Card Benchmarks — GeForce RTX 5060 Laptop GPU |  | hardware_benchmark | 2026-09-06 | 2026-09-10 |  | PC | benchmark page | available |
| hardware:b95413f9cceb | PassMark Video Card Benchmarks — Radeon RX 7600 |  | hardware_benchmark | 2026-09-02 | 2026-09-10 |  | PC | benchmark page | available |
| hardware:bbbc1eae1809 | PassMark CPU Benchmarks — Intel Core i7-11700K |  | hardware_benchmark | 2026-09-02 | 2026-09-10 |  | PC | benchmark page | available |
| hardware:bc7ca35ed973 | PassMark Video Card Benchmarks — Intel Arc A750 |  | hardware_benchmark | 2026-09-02 | 2026-09-10 |  | PC | benchmark page | available |
| hardware:bcf37f7e5b92 | PassMark AMD Ryzen 7 5700X Benchmark — CPU Mark 26561, Single 3386 |  | hardware_benchmark | 2026-09-06 | 2026-09-10 |  | PC | benchmark page | available |
| hardware:bf9c50614fe8 | PassMark - Radeon Vega 8 - Price performance comparison |  | hardware_benchmark | 2026-09-06 | 2026-09-10 |  | PC | benchmark page | available |
| hardware:c04777fc31fd | PassMark Video Card Benchmarks — Intel Arc A770 |  | hardware_benchmark | 2026-09-02 | 2026-09-10 |  | PC | benchmark page | available |
| hardware:c430a7d5ed8e | PassMark Video Card Benchmarks — Radeon RX 6600 |  | hardware_benchmark | 2026-09-02 | 2026-09-10 |  | PC | benchmark page | available |
| hardware:c4f6951eccff | PassMark AMD Ryzen 5 7600 Benchmark — CPU Mark 26975, Single 3908 |  | hardware_benchmark | 2026-09-06 | 2026-09-10 |  | PC | benchmark page | available |
| hardware:c6cc8afb6ebc | PassMark CPU Benchmarks — Intel Core i5-13600K |  | hardware_benchmark | 2026-09-02 | 2026-09-10 |  | PC | benchmark page | available |
| hardware:c7b836ca6f4e | PassMark - GeForce GTX 1080 - Price performance comparison |  | hardware_benchmark | 2026-09-06 | 2026-09-10 |  | PC | benchmark page | available |
| hardware:c9938a31b45b | PassMark Video Card Benchmarks — GeForce RTX 4080 |  | hardware_benchmark | 2026-09-02 | 2026-09-10 |  | PC | benchmark page | available |
| hardware:cd4a51d804a1 | PassMark Intel Core i7-7700 Benchmark — CPU Mark 8640, Single 2441 |  | hardware_benchmark | 2026-09-06 | 2026-09-10 |  | PC | benchmark page | available |
| hardware:ce50b64b1067 | PassMark Video Card Benchmarks — GeForce RTX 5050 |  | hardware_benchmark | 2026-09-06 | 2026-09-10 |  | PC | benchmark page | available |
| hardware:ceefabb71294 | PassMark - Intel UHD Graphics 620 - Price performance comparison |  | hardware_benchmark | 2026-09-06 | 2026-09-10 |  | PC | benchmark page | available |
| hardware:d1496a7a3bae | PassMark Video Card Benchmarks — Radeon RX 9060 XT 16GB |  | hardware_benchmark | 2026-09-06 | 2026-09-10 |  | PC | benchmark page | available |
| hardware:d1758b433170 | PassMark - GeForce GTX 1070 Ti - Price performance comparison |  | hardware_benchmark | 2026-09-06 | 2026-09-10 |  | PC | benchmark page | available |
| hardware:d23f22993b28 | PassMark Video Card Benchmarks — Radeon RX 6700 XT |  | hardware_benchmark | 2026-09-02 | 2026-09-10 |  | PC | benchmark page | available |
| hardware:d271088a60c5 | PassMark - GeForce GTX 1070 - Price performance comparison |  | hardware_benchmark | 2026-09-06 | 2026-09-10 |  | PC | benchmark page | available |
| hardware:d39e7ced2250 | PassMark CPU Benchmarks — AMD Ryzen 5 7600X |  | hardware_benchmark | 2026-09-02 | 2026-09-10 |  | PC | benchmark page | available |
| hardware:d4075fe02279 | PassMark Intel Core i5-14600K Benchmark — CPU Mark 38402, Single 4267 |  | hardware_benchmark | 2026-09-06 | 2026-09-10 |  | PC | benchmark page | available |
| hardware:d55d08a9d426 | PassMark AMD Ryzen 7 5700X3D Benchmark — CPU Mark 26302, Single 2968 |  | hardware_benchmark | 2026-09-06 | 2026-09-10 |  | PC | benchmark page | available |
| hardware:d5b349a295a2 | PassMark Video Card Benchmarks — Radeon RX 5600 XT |  | hardware_benchmark | 2026-09-02 | 2026-09-10 |  | PC | benchmark page | available |
| hardware:d91278fcebd3 | PassMark AMD Ryzen 7 7800X3D Benchmark — CPU Mark 34277, Single 3759 |  | hardware_benchmark | 2026-09-06 | 2026-09-10 |  | PC | benchmark page | available |
| hardware:de567ffb48ae | PassMark Video Card Benchmarks — GeForce GTX 1080 Ti |  | hardware_benchmark | 2026-09-02 | 2026-09-10 |  | PC | benchmark page | available |
| hardware:df2b757155c9 | PassMark Intel Core i5-12600K Benchmark — CPU Mark 27512, Single 3917 |  | hardware_benchmark | 2026-09-06 | 2026-09-10 |  | PC | benchmark page | available |
| hardware:e97887202ea5 | PassMark Video Card Benchmarks — Radeon RX 6500 XT |  | hardware_benchmark | 2026-09-06 | 2026-09-10 |  | PC | benchmark page | available |
| hardware:eb15eee5c39e | PassMark CPU Benchmarks — Intel Core i5-12400F |  | hardware_benchmark | 2026-09-02 | 2026-09-10 |  | PC | benchmark page | available |
| hardware:ed4189e76f39 | PassMark Video Card Benchmarks — GeForce RTX 3080 |  | hardware_benchmark | 2026-09-02 | 2026-09-10 |  | PC | benchmark page | available |
| hardware:ef05e429b7a4 | PassMark CPU Benchmarks — AMD Ryzen 3 3100 |  | hardware_benchmark | 2026-09-02 | 2026-09-10 |  | PC | benchmark page | available |
| hardware:ef3fed8afcb2 | PassMark Video Card Benchmarks — Radeon RX 6900 XT |  | hardware_benchmark | 2026-09-02 | 2026-09-10 |  | PC | benchmark page | available |
| hardware:f2d3732fd926 | PassMark Intel Core i7-14700K Benchmark — CPU Mark 51958, Single 4456 |  | hardware_benchmark | 2026-09-06 | 2026-09-10 |  | PC | benchmark page | available |
| hardware:f3d9708ed9f4 | PassMark CPU Benchmarks — AMD Ryzen 5 1600 |  | hardware_benchmark | 2026-09-02 | 2026-09-10 |  | PC | benchmark page | available |
| hardware:f3e9327afe75 | PassMark CPU Benchmarks — Intel Core i3-8100 |  | hardware_benchmark | 2026-09-02 | 2026-09-10 |  | PC | benchmark page | available |
| hardware:f5e8e9acc2ec | PassMark - Radeon RX 6800 - Price performance comparison |  | hardware_benchmark | 2026-09-06 | 2026-09-10 |  | PC | benchmark page | available |
| hardware:f84c1215e206 | PassMark Video Card Benchmarks — Radeon RX 9070 XT |  | hardware_benchmark | 2026-09-06 | 2026-09-10 |  | PC | benchmark page | available |
| hardware:f991632d00d5 | PassMark Video Card Benchmarks — GeForce RTX 3050 Ti Laptop GPU |  | hardware_benchmark | 2026-09-06 | 2026-09-10 |  | PC | benchmark page | available |
| hardware:fb999a0301a9 | PassMark Video Card Benchmarks — GeForce RTX 3060 Ti |  | hardware_benchmark | 2026-09-02 | 2026-09-10 |  | PC | benchmark page | available |

### 20.1 Ссылки

- `BOOK_GAME_ENGINE_ARCHITECTURE` — Game Engine Architecture, Third Edition — https://www.gameenginebook.com/
- `BOOK_GAME_PROGRAMMING_PATTERNS` — Game Programming Patterns — https://gameprogrammingpatterns.com/
- `BOOK_GPU_GEMS_3` — GPU Gems 3: Programming Techniques for High-Performance Graphics — https://developer.nvidia.com/gpugems/gpugems3/
- `BOOK_REAL_TIME_RENDERING` — Real-Time Rendering, Fourth Edition — https://www.realtimerendering.com/
- `CLUSTERED_SHADING` — Clustered Deferred and Forward Shading (Olsson, Billeter, Assarsson) — https://www.cse.chalmers.se/~uffe/clustered_shading_preprint.pdf
- `COENEN_DOOM` — Doom Eternal graphics study (Simon Coenen) — https://www.simoncoenen.com/blog/programming/graphics/DoomEternalStudy
- `CS2_SUBTICK` — Counter-Strike 2: Moving Beyond Tick Rate — https://www.counter-strike.net/cs2
- `DF_ITTakesTWO` — It Takes Two tech analysis (Digital Foundry) — https://www.digitalfoundry.net/articles/digitalfoundry-2021-it-takes-two-tech-analysis
- `DOOM_ETERNAL` — Rendering the Hellscape of Doom Eternal (SIGGRAPH 2020) — https://advances.realtimerendering.com/s2020/RenderingDoomEternal.pdf
- `GAFFER_TIMESTEP` — Fix Your Timestep! (Gaffer on Games) — https://gafferongames.com/post/fix_your_timestep/
- `GAME_AI_FLOW_FIELDS` — Crowd Pathfinding and Steering Using Flow Field Tiles — Elijah Emerson — https://www.gameaipro.com/GameAIPro/GameAIPro_Chapter23_Crowd_Pathfinding_and_Steering_Using_Flow_Field_Tiles.pdf
- `GODOT_DECALS` — Godot Docs: Using Decals — https://docs.godotengine.org/en/stable/tutorials/3d/using_decals.html
- `GODOT_LIGHTS` — Godot Docs: Lights and Shadows — https://docs.godotengine.org/en/stable/tutorials/3d/lights_and_shadows.html
- `GODOT_MESHLOD` — Godot Docs: Mesh Level of Detail — https://docs.godotengine.org/en/stable/tutorials/3d/mesh_lod.html
- `GODOT_MULTIMESH` — Godot Docs: MultiMeshInstance3D — https://docs.godotengine.org/en/stable/classes/class_multimeshinstance3d.html
- `GODOT_MULTIPLAYER` — Godot Docs: High-level Multiplayer — https://docs.godotengine.org/en/stable/tutorials/networking/high_level_multiplayer.html
- `GODOT_OCCLUSION` — Godot Docs: Occlusion Culling — https://docs.godotengine.org/en/stable/tutorials/3d/occlusion_culling.html
- `GODOT_PARTICLES` — Godot Docs: 3D Particles — https://docs.godotengine.org/en/stable/tutorials/3d/particles/index.html
- `GODOT_PERF` — Godot Docs: Optimizing 3D Performance — https://docs.godotengine.org/en/stable/tutorials/performance/optimizing_3d_performance.html
- `GODOT_PHYSICS` — Godot Docs: Physics Introduction — https://docs.godotengine.org/en/stable/tutorials/physics/physics_introduction.html
- `GODOT_THREADS` — Godot Docs: Using Multiple Threads — https://docs.godotengine.org/en/stable/tutorials/performance/using_multiple_threads.html
- `GPP_DATALOCALITY` — Game Programming Patterns: Data Locality — https://gameprogrammingpatterns.com/data-locality.html
- `GPP_OBJECTPOOL` — Game Programming Patterns: Object Pool — https://gameprogrammingpatterns.com/object-pool.html
- `GPP_STATE` — Game Programming Patterns: State — https://gameprogrammingpatterns.com/state.html
- `GPU_GEMS_SHAFTS` — GPU Gems 3, Ch.13: Volumetric Light Scattering as a Post-Process (Mitchell) — https://developer.nvidia.com/gpugems/gpugems3/part-ii-light-and-shadows/chapter-13-volumetric-light-scattering-post-process
- `HUNT_AUDIO` — Hunt: Showdown — Audio readability, realism and consistency — https://www.huntshowdown.com/news/hunt-audio-readability-realism-and-consistency
- `HUNT_AUDIO_2025` — Dev Insight - A deep dive into 3D Audio in Hunt — https://www.huntshowdown.com/news/dev-insight-a-deep-dive-into-3d-audio-in-hunt
- `KHRONOS_ASYNC_COMPUTE` — Khronos Vulkan Samples — Using async compute to saturate GPU — https://docs.vulkan.org/samples/latest/samples/performance/async_compute/README.html
- `L4D_AI_DIRECTOR` — The AI Systems of Left 4 Dead — https://steamcdn-a.akamaihd.net/apps/valve/2009/ai_systems_of_l4d_mike_booth.pdf
- `MESHOPT` — meshoptimizer: mesh optimization library — https://github.com/zeux/meshoptimizer
- `MS_DIRECTSTORAGE_GUIDANCE` — Microsoft DirectStorage — Developer Guidance — https://github.com/microsoft/DirectStorage/blob/main/Docs/DeveloperGuidance.md
- `MS_MESH_SHADER` — DirectX mesh shader specification — https://microsoft.github.io/DirectX-Specs/d3d/MeshShader.html
- `MS_VRS` — Variable Rate Shading \| DirectX-Specs — https://microsoft.github.io/DirectX-Specs/d3d/VariableRateShading.html
- `NVIDIA_NTC` — NVIDIA RTXNTC SDK — https://github.com/NVIDIA-RTX/Rtxntc
- `NVIDIA_VOXEL_CONES` — Interactive Indirect Illumination Using Voxel Cone Tracing — Crassin et al. — https://research.nvidia.com/labs/rtr/publication/crassin2011givoxels/
- `ORCA_RVO` — Optimal Reciprocal Collision Avoidance (van den Berg et al., UNC Gamma) — https://gamma.cs.unc.edu/ORCA/
- `PASSMARK_2026_09` — PassMark PerformanceTest V10 — CPU and GPU Benchmarks — https://www.cpubenchmark.net/
- `RESEARCH_S23_PACKAGING` — Unreal Engine: Packaging Your Project — https://dev.epicgames.com/documentation/en-us/unreal-engine/packaging-your-project
- `RESEARCH_S24_HLOD` — Unreal Engine: World Partition HLOD — https://dev.epicgames.com/documentation/en-us/unreal-engine/world-partition---hierarchical-level-of-detail-in-unreal-engine
- `RESEARCH_S25_PCG` — Using PCG with World Partition — https://dev.epicgames.com/documentation/en-us/unreal-engine/using-pcg-with-world-partition-in-unreal-engine?lang=en-US
- `RESEARCH_S27_RELEVANCY` — Unreal Engine: Actor Relevancy — https://dev.epicgames.com/documentation/en-us/unreal-engine/actor-relevancy-in-unreal-engine
- `RESEARCH_S28_CRY_STREAMING` — CRYENGINE: Streaming System — https://www.cryengine.com/docs/static/engines/cryengine-5/categories/23756813/pages/23306430
- `RESEARCH_S29_CRY_AUDIO` — CRYENGINE: Audio & Occlusion — https://www.cryengine.com/docs/static/engines/cryengine-5/categories/23756816/pages/44964914
- `RESEARCH_S31_UNITY_JOB_OVERVIEW` — Unity Manual: Job System Overview — https://docs.unity3d.com/6000.0/Documentation/Manual/job-system-overview.html
- `RESEARCH_S33_ISO_25010` — ISO/IEC 25010:2023 Product Quality Model — https://www.iso.org/standard/78176.html
- `RESEARCH_S34_ISO_20741` — ISO/IEC 20741:2017 Software Engineering Tool Evaluation — https://www.iso.org/obp/ui?_escaped_fragment_=iso%3Astd%3Aiso-iec%3A20741%3Aed-1%3Av1%3Aen
- `RESEARCH_S35_PMI_PERT` — Practice Standard for Scheduling - Second Edition — https://www.pmi.org/-/media/pmi/documents/public/pdf/certifications/practice-standard-scheduling.pdf?v=c7ca2721-8c26-4e07-ba47-069d0987bc0c
- `RESEARCH_S36_NASA_SCHEDULE` — Analytical Technique for Schedule Risk Assessment — https://ntrs.nasa.gov/api/citations/19870020777/downloads/19870020777.pdf
- `RESEARCH_S37_AMDAHL` — Amdahl's Law & Parallel Speedup — https://www.usenix.org/legacy/publications/library/proceedings/als00/2000papers/papers/full_papers/brownrobert/brownrobert_html/node3.html
- `RESEARCH_S38_D3D_FEATURE_LEVELS` — Direct3D Hardware Feature Levels — https://learn.microsoft.com/en-us/windows/win32/direct3d12/hardware-feature-levels
- `RESEARCH_S39_D3D_CHECK_FEATURE` — ID3D12Device::CheckFeatureSupport — https://learn.microsoft.com/en-us/windows/win32/api/d3d12/nf-d3d12-id3d12device-checkfeaturesupport
- `RESEARCH_S40_D3D_RT_TIER` — D3D12 Raytracing Tier — https://learn.microsoft.com/en-us/windows/win32/api/d3d12/ne-d3d12-d3d12_raytracing_tier
- `RESEARCH_S41_UE_SPECS` — Hardware and Software Specifications for Unreal Engine — https://dev.epicgames.com/documentation/en-us/unreal-engine/hardware-and-software-specifications-for-unreal-engine
- `RESEARCH_S42_RIOT_SCALABILITY` — VALORANT: Scalability and Load Testing — https://www.riotgames.com/en/news/scalability-and-load-testing-valorant
- `RESEARCH_S43_HAMMER` — Valve Hammer Editor / Source SDK — https://developer.valvesoftware.com/wiki/Valve_Hammer_Editor
- `RESEARCH_S44_HEROENGINE_LEGACY` — HeroEngine Legacy — https://tgs.tech/solutions/heroengine-legacy
- `RESEARCH_S45_HEROENGINE_VIDEOS` — HeroEngine Legacy Platform Videos — https://tgs.tech/apex-videos
- `RESEARCH_S46_UNITY_JOB_DEPENDENCIES` — Unity Job Dependencies — https://docs.unity3d.com/2023.2/Documentation/Manual/JobSystemJobDependencies.html
- `RESEARCH_S49_PASSMARK_SINGLE` — PassMark CPU Single Thread Chart — https://www.cpubenchmark.net/singleThread.html
- `RESEARCH_S50_PASSMARK_FAQ` — PassMark PerformanceTest FAQ — https://passmark.com/support/performancetest_faq/understanding-results.php
- `RESEARCH_S51_3DMARK` — UL 3DMark — https://benchmarks.ul.com/3dmark
- `RESEARCH_S53_QUIC_RFC` — RFC 9000: QUIC — https://www.ietf.org/rfc/rfc9000.pdf
- `RESEARCH_S54_UE_TEXTURE_METRICS` — Unreal Engine: Texture Streaming Metrics — https://dev.epicgames.com/documentation/en-us/unreal-engine/texture-streaming-metrics-in-unreal-engine
- `RESEARCH_S55_UE_TEXTURE_CONFIG` — Unreal Engine: Texture Streaming Configuration — https://dev.epicgames.com/documentation/en-us/unreal-engine/texture-streaming-configuration
- `RESEARCH_S57_NASA_GLOSSARY` — NASA PP&C Glossary: Critical Path and Double Counting — https://www.nasa.gov/ocfo/ppc-corner/ppc-glossary/
- `RESEARCH_S58_UNITY_JOB_TROUBLESHOOTING` — Unity Job System Troubleshooting — https://docs.unity3d.com/es/2021.1/Manual/JobSystemTroubleshooting.html
- `RIOT_NETCODE` — Peeking into VALORANT's Netcode — https://technology.riotgames.com/news/peeking-valorants-netcode
- `RIOT_TICK` — Valorant 128-tick servers (Riot Engineering) — https://www.riotgames.com/en/news/valorants-128-tick-servers
- `SAVE_PATTERNS` — Save Systems & Persistence (Andrews Notebook) — https://andrewaltimit.github.io/Documentation/docs/gamedev/save-systems.html
- `SHADOWGAMBIT_SAVE` — Deep dive: save system of Shadow Gambit (GameDeveloper) — https://www.gamedeveloper.com/programming/deep-dive-creating-and-fine-tuning-the-save-system-of-_shadow-gambit_
- `SRC-AIS-001` — The AI Systems of Left 4 Dead — https://cdn.akamai.steamstatic.com/apps/valve/2009/ai_systems_of_l4d_mike_booth.pdf
- `SRC-AIS-002` — Crowd Pathfinding and Steering Using Flow Field Tiles (Game AI Pro, Chapter 23) — https://www.gameaipro.com/GameAIPro/GameAIPro_Chapter23_Crowd_Pathfinding_and_Steering_Using_Flow_Field_Tiles.pdf
- `SRC-AIS-003` — Optimal Reciprocal Collision Avoidance (ORCA) — https://gamma.cs.unc.edu/ORCA/
- `SRC-AIS-004` — RVO2 Library: Reciprocal Collision Avoidance for Real-Time Multi-Agent Simulation — https://gamma.cs.unc.edu/RVO2/
- `SRC-AIS-005` — Game Programming Patterns - Object Pool (Optimization Patterns) — https://gameprogrammingpatterns.com/object-pool.html
- `SRC-AIS-006` — Game Programming Patterns - Component (Decoupling Patterns) — https://gameprogrammingpatterns.com/component.html
- `SRC-AIS-007` — Gerstner wave (Trochoidal wave) — https://en.wikipedia.org/wiki/Gerstner_wave
- `SRC-AIS-008` — Rendering the Hellscape of Doom Eternal (Advances in Real-Time Rendering, SIGGRAPH 2020) — https://advances.realtimerendering.com/s2020/RenderingDoomEternal.pdf
- `SRC-AIS-009` — Hair Rendering and Simulation in Unreal Engine — https://dev.epicgames.com/documentation/en-us/unreal-engine/hair-rendering-and-simulation-in-unreal-engine
- `SRC-AIS-010` — Groom Scalability and Performance with Unreal Engine — https://dev.epicgames.com/documentation/en-us/unreal-engine/groom-scalability-and-performance-with-unreal-engine
- `SRC-AIS-011` — Recast Navigation (recastnav.com) — https://recastnav.com/
- `SRC-AIS-012` — RecastNavigation - Detour/Include/DetourNavMeshQuery.h (source) — https://raw.githubusercontent.com/recastnavigation/recastnavigation/main/Detour/Include/DetourNavMeshQuery.h
- `SRC-AIS-013` — Godot Engine - Physics introduction — https://docs.godotengine.org/en/stable/tutorials/physics/physics_introduction.html
- `SRC-AIS-014` — Saving and Loading Your Game in Unreal Engine — https://dev.epicgames.com/documentation/en-us/unreal-engine/saving-and-loading-your-game-in-unreal-engine
- `SRC-AIS-015` — Significance Manager in Unreal Engine — https://dev.epicgames.com/documentation/en-us/unreal-engine/significance-manager-in-unreal-engine
- `SRC-AIS-016` — MassEntity in Unreal Engine — https://dev.epicgames.com/documentation/en-us/unreal-engine/mass-entity-in-unreal-engine
- `SRC-AIS-017` — Scalability and Best Practices for Niagara — https://dev.epicgames.com/documentation/en-us/unreal-engine/scalability-and-best-practices-for-niagara
- `SRC-AIS-018` — Massive Crowd on Assassin's Creed Unity: AI Recycling (GDC 2015) — https://www.gdcvault.com/play/1022411/
- `SRC-AIS-019` — The Art of Destruction in Rainbow Six: Siege (GDC 2016) — https://media.gdcvault.com/gdc2016/Presentations/LHeureux_Julien_Art_Of_Destruction.pdf
- `SRC-AIS-020` — Year summary (Voxagon Blog) - Teardown engine — https://blog.voxagon.se/2024/12/29/year-summary.html
- `SRC-AIS-021` — Fix Your Timestep! — https://gafferongames.com/post/fix_your_timestep/
- `SRC-AIS-022` — Crest Ocean System (GitHub: wave-harmonic/crest) — https://github.com/wave-harmonic/crest
- `SRC-AIS-023` — NVIDIA Blast (GitHub: NVIDIAGameWorks/Blast) — https://github.com/NVIDIAGameWorks/Blast
- `SRC-AIS-024` — Chaos Destruction in Unreal Engine — https://dev.epicgames.com/documentation/en-us/unreal-engine/chaos-destruction-in-unreal-engine
- `SRC-AIS-025` — Clothing Tool in Unreal Engine (Chaos Cloth) — https://dev.epicgames.com/documentation/en-us/unreal-engine/clothing-tool-in-unreal-engine
- `SRC-AIS-026` — Chaos Vehicles (Unreal Engine) — https://dev.epicgames.com/documentation/en-us/unreal-engine/chaos-vehicles
- `SRC-AIS-027` — PxBroadPhaseType - PhysX SDK Documentation — https://nvidia-omniverse.github.io/PhysX/physx/5.6.1/_api_build/structPxBroadPhaseType.html
- `SRC-AIS-028` — GPU Gems 3, Chapter 32: Broad-Phase Collision Detection with CUDA — https://developer.nvidia.com/gpugems/gpugems3/part-v-physics-simulation/chapter-32-broad-phase-collision-detection-cuda
- `SRC-AIS-029` — Advanced Graphics Techniques Tutorial: Wakes, Explosions and Lighting - Interactive Water Simulation in 'Atlas' (GDC 2014) — https://gdcvault.com/play/1025819/Advanced-Graphics-Techniques-Tutorial-Wakes
- `SRC-AIS-030` — 'Overwatch' Gameplay Architecture and Netcode (GDC 2017) — https://gdcvault.com/play/1024001/
- `SRC-AIS-031` — Crowds in Hitman: Absolution (GDC Vault) — https://www.gdcvault.com/play/1015315/Crowds-in-Hitman
- `SRC-AIS-032` — Godot Engine - Saving games — https://docs.godotengine.org/en/stable/tutorials/io/saving_games.html
- `SRC-AIS-033` — Unity Manual - Cloth — https://docs.unity3d.com/6000.0/Documentation/Manual/class-Cloth.html
- `SRC-AIS-034` — Unity Manual - Wheel collider component reference — https://docs.unity3d.com/Manual/class-WheelCollider.html
- `SRC-AIS-035` — Unity Manual - Write multithreaded code with the job system — https://docs.unity3d.com/Manual/JobSystem.html
- `SRC-AIS-036` — AMD and Crystal Dynamics Collaboration ... With the Launch of 'Tomb Raider' (press release) — https://ir.amd.com/news-events/press-releases/detail/218/amd-and-crystal-dynamics-collaboration-thrusts-gamers-into-one-of-the-most-realistic-pc-gaming-experience-ever-with-the-launch-of-tomb-raider
- `SRC-AIS-037` — Soft-body Physics - BeamNG.drive — https://www.beamng.com/game/about/physics/
- `SRC-AIS-038` — DOTS - Unity's Data-Oriented Technology Stack — https://unity.com/dots
- `SRC-AIS-039` — Unity Manual - Introduction to GPU instancing — https://docs.unity3d.com/Manual/GPUInstancing.html
- `SRC-AIS-040` — Godot Engine - RigidBody3D class reference — https://docs.godotengine.org/en/stable/classes/class_rigidbody3d.html
- `SRC-AIS-041` — Physics in Unreal Engine (Chaos Physics overview) — https://dev.epicgames.com/documentation/en-us/unreal-engine/physics-in-unreal-engine
- `SRC-AIS-042` — Water System in Unreal Engine — https://dev.epicgames.com/documentation/en-us/unreal-engine/water-system-in-unreal-engine
- `SRC-AIS-043` — AMD TressFX (GitHub: GPUOpen-Effects/TressFX) — https://github.com/GPUOpen-Effects/TressFX
- `SRC-AIS-044` — Godot Engine - VehicleBody3D class reference — https://docs.godotengine.org/en/stable/classes/class_vehiclebody3d.html
- `SRC-AIS-045` — Godot Engine - GPUParticles3D class reference — https://docs.godotengine.org/en/stable/classes/class_gpuparticles3d.html
- `SRC-AIS-046` — Physics Sub-Stepping in Unreal Engine — https://dev.epicgames.com/documentation/unreal-engine/physics-sub-stepping-in-unreal-engine
- `SRC-AIS-047` — Niagara Flipbook Baker Quick Start Guide in Unreal Engine — https://dev.epicgames.com/documentation/en-us/unreal-engine/niagara-flipbook-baker-quick-start-guide-in-unreal-engine
- `SRC-CHC-001` — Animation Budget Allocator (Unreal Engine 5.8 Documentation) — https://dev.epicgames.com/documentation/en-us/unreal-engine/animation-budget-allocator-in-unreal-engine
- `SRC-CHC-002` — Animation Optimization in Unreal Engine (Unreal Engine 5.8 Documentation) — https://dev.epicgames.com/documentation/unreal-engine/animation-optimization-in-unreal-engine?lang=en-US
- `SRC-CHC-003` — Skeletal Mesh LODs in Unreal Engine (Unreal Engine 5.8 Documentation) — https://dev.epicgames.com/documentation/en-us/unreal-engine/skeletal-mesh-lods-in-unreal-engine
- `SRC-CHC-004` — Animation Compression Library (acl) - repository README — https://github.com/nfrechette/acl
- `SRC-CHC-005` — ACL - Paragon database performance — https://github.com/nfrechette/acl/blob/develop/docs/paragon_performance.md
- `SRC-CHC-006` — ACL - Carnegie-Mellon University database performance — https://github.com/nfrechette/acl/blob/develop/docs/cmu_performance.md
- `SRC-CHC-007` — ACL - Decompression performance — https://github.com/nfrechette/acl/blob/develop/docs/decompression_performance.md
- `SRC-CHC-008` — Animation Compression Library in Unreal Engine (Unreal Engine 5.8 Documentation) — https://dev.epicgames.com/documentation/en-us/unreal-engine/animation-compression-library-in-unreal-engine
- `SRC-CHC-009` — Animation Compression Codec Reference in Unreal Engine (Unreal Engine 5.8 Documentation) — https://dev.epicgames.com/documentation/en-us/unreal-engine/animation-compression-codec-reference-in-unreal-engine
- `SRC-CHC-010` — Motion Matching in Unreal Engine (Unreal Engine 5.8 Documentation) — https://dev.epicgames.com/documentation/en-us/unreal-engine/motion-matching-in-unreal-engine
- `SRC-CHC-011` — Motion Matching and The Road to Next-Gen Animation (GDC 2016 slides) — https://media.gdcvault.com/gdc2016/Presentations/Clavet_Simon_MotionMatching.pdf
- `SRC-CHC-012` — Learned Motion Matching (project page + abstract) — https://theorangeduck.com/page/learned-motion-matching
- `SRC-CHC-013` — Learned motion matching, ACM Transactions on Graphics 39(4) — https://dl.acm.org/doi/abs/10.1145/3386569.3392440
- `SRC-CHC-014` — Skeletal Mesh Rendering Paths in Unreal Engine (Unreal Engine 5.8 Documentation) — https://dev.epicgames.com/documentation/en-us/unreal-engine/skeletal-mesh-rendering-paths-in-unreal-engine
- `SRC-CHC-015` — GPU Gems, Chapter 4: Animation in the 'Dawn' Demo — https://developer.nvidia.com/gpugems/gpugems/part-i-natural-effects/chapter-4-animation-dawn-demo
- `SRC-CHC-016` — ozz-animation - open source C++ 3D skeletal animation library (documentation, Overview) — https://guillaumeblanc.github.io/ozz-animation/documentation/
- `SRC-CHC-017` — Blender Manual - Render Baking (Cycles) — https://docs.blender.org/manual/en/latest/render/cycles/baking.html
- `SRC-CHC-018` — MikkTSpace - a common standard for tangent space used in baking tools — https://github.com/mmikk/MikkTSpace
- `SRC-CHC-019` — Block Compression (Direct3D 10) - Microsoft Learn — https://learn.microsoft.com/en-us/windows/win32/direct3d10/d3d10-graphics-programming-guide-resources-block-compression
- `SRC-CHC-020` — Basis Universal GPU Texture Codec (repository README) — https://github.com/BinomialLLC/basis_universal
- `SRC-CHC-021` — Unity Manual - Sprite Atlas (class-SpriteAtlas) — https://docs.unity.cn/2019.4/Documentation/Manual/class-SpriteAtlas.html
- `SRC-CHC-022` — Unity Manual - Sprite Atlas reference — https://docs.unity3d.com/6000.2/Documentation/Manual/sprite/atlas/sprite-atlas-reference.html
- `SRC-CHC-023` — Unity Manual - Sprite Atlas workflow — https://docs.unity.cn/2022.1/Documentation/Manual/SpriteAtlasWorkflow.html
- `SRC-CHC-024` — Unity Manual - Tilemap Renderer component reference — https://docs.unity3d.com/6000.5/Documentation/Manual/tilemaps/work-with-tilemaps/tilemap-renderer-reference.html
- `SRC-CHC-025` — Unity Manual - Tilemap Renderer — https://docs.unity.cn/Manual/class-TilemapRenderer.html
- `SRC-CHC-026` — Tiled Documentation - JSON Map Format reference — https://docs.mapeditor.org/en/latest/reference/json-map-format/
- `SRC-CHC-027` — Tiled Documentation - Using Infinite Maps — https://docs.mapeditor.org/en/latest/manual/using-infinite-maps/
- `SRC-CHC-028` — Spine User Guide - Mesh attachments — http://esotericsoftware.com/spine-meshes
- `SRC-CHC-029` — Spine User Guide - Metrics view — https://esotericsoftware.com/spine-metrics
- `SRC-CHC-030` — Unity 2D Animation package - Skinning Editor — https://docs.unity.cn/Packages/com.unity.2d.animation@7.0/manual/SkinningEditor.html
- `SRC-CHC-031` — Unity 2D Animation package - Actor skinning and weighting workflow — https://docs.unity.cn/Packages/com.unity.2d.animation@7.0/manual/CharacterRig.html
- `SRC-CHC-032` — Gameplay Ability System for Unreal Engine (Unreal Engine 5.8 Documentation) — https://dev.epicgames.com/documentation/en-us/unreal-engine/gameplay-ability-system-for-unreal-engine
- `SRC-CHC-033` — Understanding the Unreal Engine Gameplay Ability System (Unreal Engine 5.8 Documentation) — https://dev.epicgames.com/documentation/en-us/unreal-engine/understanding-the-unreal-engine-gameplay-ability-system
- `SRC-CHC-034` — Gameplay Ability Tasks in Unreal Engine (Unreal Engine 5.8 Documentation) — https://dev.epicgames.com/documentation/en-us/unreal-engine/gameplay-ability-tasks-in-unreal-engine
- `SRC-CHC-035` — Gameplay Ability System Component and Gameplay Attributes in Unreal Engine — https://dev.epicgames.com/documentation/en-us/unreal-engine/gameplay-ability-system-component-and-gameplay-attributes-in-unreal-engine
- `SRC-CHC-036` — Scalability and Best Practices for Niagara (Unreal Engine 5.8 Documentation) — https://dev.epicgames.com/documentation/unreal-engine/scalability-and-best-practices-for-niagara
- `SRC-CHC-037` — Optimizing Niagara (Unreal Engine 5.8 Documentation) — https://dev.epicgames.com/documentation/unreal-engine/optimizing-niagara
- `SRC-CHC-038` — Niagara Systems as a Service (Unreal Engine 5.8 Documentation) — https://dev.epicgames.com/documentation/en-us/unreal-engine/niagara-systems-as-a-service
- `SRC-CHC-039` — 3D Toon Rendering in 'Hi-Fi RUSH' (GDC 2024 session) — https://gdcvault.com/play/1034251/3D-Toon-Rendering-in-Hi
- `SRC-CHC-040` — Illustrative Rendering in Team Fortress 2 (NPAR 2007) — https://cdn.fastly.steamstatic.com/apps/valve/2007/NPAR07_IllustrativeRenderingInTeamFortress2.pdf
- `SRC-CHC-041` — Rayman Legends: The Design Process Within the UbiArt Framework (GDC 2014 session) — https://gdcvault.com/play/1020398/Rayman-Legends-The-Design-Process
- `SRC-CHC-042` — Game Engine Architecture, 4th Edition (two-volume set) — https://gameenginebook.com/
- `SRC-CHC-043` — Game Programming Patterns — https://gameprogrammingpatterns.com/
- `SRC-CHC-044` — Unity Manual - Animation tab (AnimationClip import settings) — https://docs.unity3d.com/2020.1/Documentation/Manual/class-AnimationClip.html
- `SRC-CHC-045` — Unity Manual - Recommended, default, and supported texture compression formats, by platform — https://docs.unity.cn/2023.3/Documentation/Manual/class-TextureImporterOverride.html
- `SRC-CHC-046` — Cuphead - A Game \| Made with Unity (Unity customer story) — https://unity.com/made-with-unity/cuphead
- `SRC-DER-001` — Steam Hardware & Software Survey — https://store.steampowered.com/hwsurvey/
- `SRC-DER-002` — Steam Hardware & Software Survey - PC Video Card Usage Details — https://store.steampowered.com/hwsurvey/videocard/
- `SRC-DER-003` — Source Multiplayer Networking — https://developer.valvesoftware.com/wiki/Source_Multiplayer_Networking
- `SRC-DER-004` — What Every Programmer Needs To Know About Game Networking — https://gafferongames.com/post/what_every_programmer_needs_to_know_about_game_networking/
- `SRC-DER-005` — Snapshot Interpolation — https://gafferongames.com/post/snapshot_interpolation/
- `SRC-DER-006` — Direct3D 12 programming guide — https://learn.microsoft.com/en-us/windows/win32/direct3d12/directx-12-programming-guide
- `SRC-DER-007` — Advanced Shader Delivery overview — https://learn.microsoft.com/en-us/windows/win32/direct3d12/advanced-shader-delivery
- `SRC-DER-008` — Work submission in Direct3D 12 (command queues and command lists) — https://learn.microsoft.com/en-us/windows/win32/direct3d12/command-queues-and-command-lists
- `SRC-DER-009` — Memory management in Direct3D 12 — https://learn.microsoft.com/en-us/windows/win32/direct3d12/memory-management
- `SRC-DER-010` — Engine class reference (Engine.max_fps, Engine.physics_ticks_per_second) — https://docs.godotengine.org/en/stable/classes/class_engine.html
- `SRC-DER-011` — Upgrading from Godot 3 to Godot 4 — https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.html
- `SRC-DER-012` — Setting Up Dedicated Servers in Unreal Engine — https://dev.epicgames.com/documentation/en-us/unreal-engine/setting-up-dedicated-servers-in-unreal-engine
- `SRC-DER-013` — Networking Overview for Unreal Engine — https://dev.epicgames.com/documentation/en-us/unreal-engine/networking-overview-for-unreal-engine
- `SRC-DER-014` — Performance Guidelines for Mobile Devices in Unreal Engine — https://dev.epicgames.com/documentation/en-us/unreal-engine/performance-guidelines-for-mobile-devices-in-unreal-engine
- `SRC-DER-015` — Common Memory and CPU Performance Considerations in Unreal Engine — https://dev.epicgames.com/documentation/en-us/unreal-engine/common-memory-and-cpu-performance-considerations-in-unreal-engine
- `SRC-DER-016` — Timing Insights in Unreal Engine — https://dev.epicgames.com/documentation/unreal-engine/timing-insights-in-unreal-engine?lang=en-US
- `SRC-DER-017` — Introduction to Performance Profiling and Configuration in Unreal Engine — https://dev.epicgames.com/documentation/unreal-engine/introduction-to-performance-profiling-and-configuration-in-unreal-engine?lang=en-US
- `SRC-DER-018` — Saving and Loading Your Game in Unreal Engine — https://dev.epicgames.com/documentation/en-us/unreal-engine/saving-and-loading-your-game-in-unreal-engine
- `SRC-DER-019` — Unreal Engine Optimization Guide: Profiling Fundamentals — https://www.intel.com/content/www/us/en/developer/articles/technical/unreal-engine-optimization-profiling-fundamentals.html
- `SRC-DER-020` — What do 1% percentile statistics mean in PresentMon (issue #219) — https://github.com/GameTechDev/PresentMon/issues/219
- `SRC-DER-021` — Vulkan 1.4.362 Specification (with all registered extensions) — https://registry.khronos.org/vulkan/specs/1.3-extensions/html/vkspec.html
- `SRC-DER-022` — Steam Deck OLED - Tech Specs — https://www.steamdeck.com/en/tech/oled
- `SRC-DER-023` — Steam Deck and Steam Machine Compatibility Review — https://partner.steamgames.com/doc/steamdeck/compat
- `SRC-DER-024` — Steam Networking — https://partner.steamgames.com/doc/features/multiplayer/networking
- `SRC-DER-025` — Steam Datagram Relay — https://partner.steamgames.com/doc/features/multiplayer/steamdatagramrelay
- `SRC-DER-026` — The Mythical Man-Month (encyclopedia article summarising Brooks, 1975) — https://en.wikipedia.org/wiki/The_Mythical_Man-Month
- `SRC-DER-027` — Game Engine Architecture - official table of contents (3rd and 4th editions) — https://www.gameenginebook.com/toc.html
- `SRC-DER-028` — GeForce RTX 4060 / RTX 4060 Ti graphics cards - specifications — https://www.nvidia.com/en-us/geforce/graphics-cards/40-series/rtx-4060-4060ti/
- `SRC-DER-029` — Quality project settings reference — https://docs.unity3d.com/Manual/class-QualitySettings.html
- `SRC-DER-030` — Application.targetFrameRate — https://docs.unity3d.com/ScriptReference/Application-targetFrameRate.html
- `SRC-DER-031` — Developer Satisfaction Survey 2023 - Summary Report — https://files.gameindustrylibrary.com/documents/developer-satisfaction-survey-2023.pdf
- `SRC-DER-032` — As Anthem shuts down, the game's executive producer has released a nearly four-hour post-mortem — https://www.videogameschronicle.com/news/as-anthem-shuts-down-the-games-executive-producer-has-released-a-nearly-four-hour-post-mortem/
- `SRC-DER-033` — VALORANT's 128-Tick Servers — https://www.riotgames.com/en/news/valorants-128-tick-servers
- `SRC-DER-034` — Peeking into VALORANT's Netcode — https://www.riotgames.com/en/news/peeking-valorants-netcode
- `SRC-DER-035` — Game Loop (Game Programming Patterns, chapter) — https://www.gameprogrammingpatterns.com/game-loop.html
- `SRC-DER-036` — Boehm Cost of Change Curve: What the 1981 Data Actually Shows — https://reworkcost.com/boehm-cost-of-change-curve
- `SRC-DER-037` — Unreal Build Tool in Unreal Engine — https://dev.epicgames.com/documentation/en-us/unreal-engine/unreal-build-tool-in-unreal-engine
- `SRC-ENG-001` — Nanite Virtualized Geometry Overview — https://dev.epicgames.com/documentation/en-us/unreal-engine/nanite-virtualized-geometry-in-unreal-engine
- `SRC-ENG-002` — Lumen Global Illumination and Reflections — https://dev.epicgames.com/documentation/en-us/unreal-engine/lumen-global-illumination-and-reflections-in-unreal-engine
- `SRC-ENG-003` — Virtual Shadow Maps — https://dev.epicgames.com/documentation/en-us/unreal-engine/virtual-shadow-maps-in-unreal-engine
- `SRC-ENG-004` — Virtual Texturing — https://dev.epicgames.com/documentation/en-us/unreal-engine/virtual-texturing-in-unreal-engine
- `SRC-ENG-005` — World Partition — https://dev.epicgames.com/documentation/en-us/unreal-engine/world-partition-in-unreal-engine
- `SRC-ENG-006` — Hierarchical Level of Detail — https://dev.epicgames.com/documentation/en-us/unreal-engine/hierarchical-level-of-detail-in-unreal-engine
- `SRC-ENG-007` — Large World Coordinates in Unreal Engine 5 — https://dev.epicgames.com/documentation/en-us/unreal-engine/large-world-coordinates-in-unreal-engine-5
- `SRC-ENG-008` — Instanced Static Mesh Component — https://dev.epicgames.com/documentation/en-us/unreal-engine/instanced-static-mesh-component-in-unreal-engine
- `SRC-ENG-009` — Static Mesh Automatic LOD Generation — https://dev.epicgames.com/documentation/en-us/unreal-engine/static-mesh-automatic-lod-generation-in-unreal-engine
- `SRC-ENG-010` — Niagara Overview — https://dev.epicgames.com/documentation/en-us/unreal-engine/overview-of-niagara-effects-for-unreal-engine
- `SRC-ENG-011` — Chaos Physics Overview — https://dev.epicgames.com/documentation/en-us/unreal-engine/chaos-physics-overview?application_version=4.27
- `SRC-ENG-012` — Chaos Vehicles — https://dev.epicgames.com/documentation/en-us/unreal-engine/chaos-vehicles
- `SRC-ENG-013` — Gameplay Ability System — https://dev.epicgames.com/documentation/en-us/unreal-engine/gameplay-ability-system-for-unreal-engine
- `SRC-ENG-014` — MassEntity Overview — https://dev.epicgames.com/documentation/en-us/unreal-engine/overview-of-mass-entity-in-unreal-engine
- `SRC-ENG-015` — Behavior Trees — https://dev.epicgames.com/documentation/en-us/unreal-engine/behavior-trees-in-unreal-engine
- `SRC-ENG-016` — Navigation System — https://dev.epicgames.com/documentation/en-us/unreal-engine/navigation-system-in-unreal-engine
- `SRC-ENG-017` — Replication Graph — https://dev.epicgames.com/documentation/en-us/unreal-engine/replication-graph-in-unreal-engine
- `SRC-ENG-018` — Significance Manager — https://dev.epicgames.com/documentation/en-us/unreal-engine/significance-manager-in-unreal-engine
- `SRC-ENG-019` — Animation Budget Allocator — https://dev.epicgames.com/documentation/en-us/unreal-engine/animation-budget-allocator-in-unreal-engine
- `SRC-ENG-020` — Unreal Insights — https://dev.epicgames.com/documentation/en-us/unreal-engine/unreal-insights-in-unreal-engine
- `SRC-ENG-021` — Unreal Engine 5.0 Release Notes — https://dev.epicgames.com/documentation/en-us/unreal-engine/unreal-engine-5.0-release-notes?application_version=5.0
- `SRC-ENG-022` — Unreal Engine 5.4 Release Notes — https://dev.epicgames.com/documentation/unreal-engine/unreal-engine-5.4-release-notes?application_version=5.4&lang=en-US
- `SRC-ENG-023` — Physics in Unreal Engine — https://dev.epicgames.com/documentation/en-us/unreal-engine/physics-in-unreal-engine
- `SRC-ENG-024` — Chaos Destruction — https://dev.epicgames.com/documentation/en-us/unreal-engine/chaos-destruction-in-unreal-engine
- `SRC-ENG-025` — Universal Render Pipeline overview — https://docs.unity3d.com/Packages/com.unity.render-pipelines.universal@14.0/manual/index.html
- `SRC-ENG-026` — High Definition Render Pipeline overview — https://docs.unity3d.com/Packages/com.unity.render-pipelines.high-definition@14.0/manual/index.html
- `SRC-ENG-027` — Scriptable Render Pipeline Batcher in URP — https://docs.unity3d.com/Manual/SRPBatcher.html
- `SRC-ENG-028` — Introduction to GPU instancing — https://docs.unity3d.com/Manual/GPUInstancing.html
- `SRC-ENG-029` — LOD Group component reference — https://docs.unity3d.com/Manual/class-LODGroup.html
- `SRC-ENG-030` — Excluding hidden objects with occlusion culling — https://docs.unity3d.com/Manual/OcclusionCulling.html
- `SRC-ENG-031` — Precalculating indirect light with Light Probes — https://docs.unity3d.com/Manual/LightProbes.html
- `SRC-ENG-032` — Choose a light baking backend — https://docs.unity3d.com/Manual/progressive-lightmapper.html
- `SRC-ENG-033` — Job system overview — https://docs.unity3d.com/Manual/JobSystemOverview.html
- `SRC-ENG-034` — Addressables package overview — https://docs.unity3d.com/Packages/com.unity.addressables@1.21/manual/index.html
- `SRC-ENG-035` — Optimizing GPU texture memory with mipmap streaming — https://docs.unity3d.com/Manual/TextureStreaming.html
- `SRC-ENG-036` — Navigation System in Unity — https://docs.unity3d.com/2021.3/Documentation/Manual/nav-NavigationSystem.html
- `SRC-ENG-037` — Visual Effect Graph — https://docs.unity3d.com/Packages/com.unity.visualeffectgraph@16.0/manual/index.html
- `SRC-ENG-038` — Unity Profiler — https://docs.unity3d.com/Manual/Profiler.html
- `SRC-ENG-039` — Quality project settings reference — https://docs.unity3d.com/Manual/class-QualitySettings.html
- `SRC-ENG-040` — Entities overview (DOTS) — https://docs.unity3d.com/Packages/com.unity.entities@1.0/manual/index.html
- `SRC-ENG-041` — Unity Netcode for Entities — https://docs.unity3d.com/Packages/com.unity.netcode@1.0/manual/index.html
- `SRC-ENG-042` — AI Navigation package — https://docs.unity3d.com/Manual/com.unity.ai.navigation.html
- `SRC-ENG-043` — DOTS - Unity's Data-Oriented Technology Stack — https://unity.com/dots
- `SRC-ENG-044` — Addressables: Planning and best practices — https://unity.com/blog/engine-platform/addressables-planning-and-best-practices
- `SRC-ENG-045` — V Rising: Behind the vampire realm built on 1,600 ECS systems — https://unity.com/resources/stunlock-studios-v-rising
- `SRC-ENG-046` — Unity render pipeline features (URP / HDRP) — https://unity.com/features/srp/high-definition-render-pipeline
- `SRC-ENG-047` — Unity Engine product page — https://unity.com/products/unity-engine
- `SRC-ENG-048` — Unity plans and pricing — https://unity.com/pricing
- `SRC-ENG-049` — Unity (game engine) - Wikipedia — https://en.wikipedia.org/wiki/Unity_(game_engine)
- `SRC-ENG-050` — Unity-Technologies/EntityComponentSystemSamples — https://github.com/Unity-Technologies/EntityComponentSystemSamples
- `SRC-ENG-052` — Unreal Engine - Wikipedia — https://en.wikipedia.org/wiki/Unreal_Engine
- `SRC-ENG-053` — Godot Engine home — https://godotengine.org/
- `SRC-ENG-054` — Godot Engine documentation (stable) — https://docs.godotengine.org/en/stable/
- `SRC-ENG-055` — Godot (game engine) - Wikipedia — https://en.wikipedia.org/wiki/Godot_(game_engine)
- `SRC-ENG-056` — godotengine/godot — https://github.com/godotengine/godot
- `SRC-ENG-057` — CRYENGINE home — https://www.cryengine.com/
- `SRC-ENG-058` — CRYENGINE Documentation — https://docs.cryengine.com/
- `SRC-ENG-059` — CryEngine - Wikipedia — https://en.wikipedia.org/wiki/CryEngine
- `SRC-ENG-060` — Source (game engine) - Wikipedia — https://en.wikipedia.org/wiki/Source_(game_engine)
- `SRC-ENG-061` — Source 2 - Wikipedia — https://en.wikipedia.org/wiki/Source_2
- `SRC-ENG-062` — HeroEngine home — https://www.heroengine.com/
- `SRC-ENG-063` — HeroEngine - Wikipedia — https://en.wikipedia.org/wiki/HeroEngine
- `SRC-ENG-064` — bevyengine/bevy — https://github.com/bevyengine/bevy
- `SRC-ENG-065` — Rockstar Advanced Game Engine - Wikipedia — https://en.wikipedia.org/wiki/Rockstar_Advanced_Game_Engine
- `SRC-ENG-066` — CD Projekt - Wikipedia — https://en.wikipedia.org/wiki/CD_Projekt
- `SRC-ENG-067` — Black Myth: Wukong wows with UE5 early access visuals — https://www.unrealengine.com/developer-interviews/black-myth-wukong-wows-with-ue5-early-access-visuals
- `SRC-ENG-068` — Drop into the Next Generation of Fortnite Battle Royale, Powered by Unreal Engine 5.1 — https://www.fortnite.com/news/drop-into-the-next-generation-of-fortnite-battle-royale-powered-by-unreal-engine-5-1
- `SRC-ENG-069` — Battle-testing Unreal Engine 5.1's new features on Fortnite Battle Royale Chapter 4 — https://www.unrealengine.com/blog/battle-testing-unreal-engine-5-1-s-new-features-on-fortnite-battle-royale-chapter-4
- `SRC-ENG-070` — The making of Senua's Saga: Hellblade 2 - the big tech interview — https://www.digitalfoundry.net/articles/digitalfoundry-2024-the-big-senuas-saga-hellblade-2-tech-interview
- `SRC-ENG-071` — Fortnite Battle Royale - Wikipedia — https://en.wikipedia.org/wiki/Fortnite_Battle_Royale
- `SRC-ENG-072` — Netcode for GameObjects - About — https://docs-multiplayer.unity3d.com/netcode/current/about/
- `SRC-ENG-073` — Black Myth: Wukong - the PC tech review — https://www.digitalfoundry.net/articles/digitalfoundry-2024-black-myth-wukong-the-pc-tech-review
- `SRC-ENG-074` — Brilliant visuals and growing pains: examining the first generation of Unreal Engine 5 games — https://www.digitalfoundry.net/articles/digitalfoundry-2023-brilliant-visuals-and-growing-pains-analysing-unreal-engine-5-first-generation-games
- `SRC-ENG-075` — Lords of the Fallen is a stunning UE5 Soulslike with ongoing tech issues — https://www.digitalfoundry.net/articles/digitalfoundry-2023-lords-of-the-fallen-is-a-stunning-ue5-soulslike-with-ongoing-tech-issues
- `SRC-FUNC-001` — Lumen Global Illumination and Reflections in Unreal Engine — https://dev.epicgames.com/documentation/en-us/unreal-engine/lumen-global-illumination-and-reflections-in-unreal-engine
- `SRC-FUNC-002` — Lumen Technical Details in Unreal Engine — https://dev.epicgames.com/documentation/en-us/unreal-engine/lumen-technical-details-in-unreal-engine
- `SRC-FUNC-003` — Lumen Performance Guide for Unreal Engine — https://dev.epicgames.com/documentation/unreal-engine/lumen-performance-guide-for-unreal-engine
- `SRC-FUNC-004` — World Partition in Unreal Engine — https://dev.epicgames.com/documentation/en-us/unreal-engine/world-partition-in-unreal-engine
- `SRC-FUNC-005` — Nanite Virtualized Geometry Overview — https://dev.epicgames.com/documentation/en-us/unreal-engine/nanite-virtualized-geometry-in-unreal-engine
- `SRC-FUNC-006` — Virtual Shadow Maps in Unreal Engine — https://dev.epicgames.com/documentation/en-us/unreal-engine/virtual-shadow-maps-in-unreal-engine
- `SRC-FUNC-007` — Render Dependency Graph in Unreal Engine — https://dev.epicgames.com/documentation/en-us/unreal-engine/render-dependency-graph-in-unreal-engine
- `SRC-FUNC-008` — Temporal Super Resolution in Unreal Engine — https://dev.epicgames.com/documentation/en-us/unreal-engine/temporal-super-resolution-in-unreal-engine
- `SRC-FUNC-009` — Dynamic Resolution in Unreal Engine — https://dev.epicgames.com/documentation/en-us/unreal-engine/dynamic-resolution-in-unreal-engine
- `SRC-FUNC-010` — Path Tracer in Unreal Engine — https://dev.epicgames.com/documentation/en-us/unreal-engine/path-tracer-in-unreal-engine
- `SRC-FUNC-011` — Lightmass Basics in Unreal Engine — https://dev.epicgames.com/documentation/en-us/unreal-engine/lightmass-basics-in-unreal-engine
- `SRC-FUNC-012` — Foliage Mode in Unreal Engine — https://dev.epicgames.com/documentation/en-us/unreal-engine/foliage-mode-in-unreal-engine
- `SRC-FUNC-013` — Landscape Technical Guide — https://dev.epicgames.com/documentation/en-us/unreal-engine/landscape-technical-guide-in-unreal-engine
- `SRC-FUNC-014` — Mesh Drawing Pipeline — https://dev.epicgames.com/documentation/en-us/unreal-engine/mesh-drawing-pipeline-in-unreal-engine
- `SRC-FUNC-015` — Skeletal Mesh LODs — https://dev.epicgames.com/documentation/en-us/unreal-engine/skeletal-mesh-lods-in-unreal-engine
- `SRC-FUNC-016` — Memory Insights — https://dev.epicgames.com/documentation/en-us/unreal-engine/memory-insights-in-unreal-engine
- `SRC-FUNC-017` — Audio Mixer Overview — https://dev.epicgames.com/documentation/en-us/unreal-engine/audio-mixer-overview-in-unreal-engine
- `SRC-FUNC-018` — Post Process Effects — https://dev.epicgames.com/documentation/en-us/unreal-engine/post-process-effects-in-unreal-engine
- `SRC-FUNC-019` — Volumetric Fog — https://dev.epicgames.com/documentation/en-us/unreal-engine/volumetric-fog-in-unreal-engine
- `SRC-FUNC-020` — Large World Coordinates — https://dev.epicgames.com/documentation/en-us/unreal-engine/large-world-coordinates-in-unreal-engine-5
- `SRC-FUNC-021` — Saving and Loading Your Game — https://dev.epicgames.com/documentation/en-us/unreal-engine/saving-and-loading-your-game-in-unreal-engine
- `SRC-FUNC-022` — UnrealBuildTool — https://dev.epicgames.com/documentation/en-us/unreal-engine/unreal-build-tool-in-unreal-engine
- `SRC-FUNC-023` — Multiplayer Programming Quick Start — https://dev.epicgames.com/documentation/en-us/unreal-engine/multiplayer-programming-quick-start-for-unreal-engine
- `SRC-FUNC-024` — Modeling Mode Overview — https://dev.epicgames.com/documentation/en-us/unreal-engine/modeling-mode-in-unreal-engine
- `SRC-FUNC-025` — Hair Rendering and Simulation — https://dev.epicgames.com/documentation/en-us/unreal-engine/hair-rendering-and-simulation-in-unreal-engine
- `SRC-FUNC-026` — Water System — https://dev.epicgames.com/documentation/en-us/unreal-engine/water-system-in-unreal-engine
- `SRC-FUNC-027` — MassEntity Overview — https://dev.epicgames.com/documentation/en-us/unreal-engine/overview-of-mass-entity-in-unreal-engine
- `SRC-FUNC-028` — Gameplay Ability System — https://dev.epicgames.com/documentation/en-us/unreal-engine/gameplay-ability-system-for-unreal-engine
- `SRC-FUNC-029` — Split Screen (Unreal Engine 4.27) — https://dev.epicgames.com/documentation/en-us/unreal-engine/split-screen?application_version=4.27
- `SRC-FUNC-030` — Stat Commands — https://dev.epicgames.com/documentation/en-us/unreal-engine/stat-commands-in-unreal-engine
- `SRC-FUNC-031` — Unreal Insights — https://dev.epicgames.com/documentation/en-us/unreal-engine/unreal-insights-in-unreal-engine
- `SRC-FUNC-032` — Chaos Destruction — https://dev.epicgames.com/documentation/en-us/unreal-engine/chaos-destruction-in-unreal-engine
- `SRC-FUNC-033` — Geometry Collections User Guide — https://dev.epicgames.com/documentation/en-us/unreal-engine/geometry-collections-user-guide
- `SRC-FUNC-034` — Quality project settings reference (Unity Manual) — https://docs.unity3d.com/Manual/class-QualitySettings.html
- `SRC-FUNC-035` — Cloth (Unity Manual) — https://docs.unity3d.com/Manual/class-Cloth.html
- `SRC-FUNC-036` — Terrain (Unity Manual) — https://docs.unity3d.com/Manual/terrain-UsingTerrains.html
- `SRC-FUNC-037` — Lightmapping (Unity Manual) — https://docs.unity3d.com/Manual/Lightmapping.html
- `SRC-FUNC-038` — Animator (Unity Manual) — https://docs.unity3d.com/Manual/Animator.html
- `SRC-FUNC-039` — Physics Overview (Unity Manual) — https://docs.unity3d.com/Manual/PhysicsOverview.html
- `SRC-FUNC-040` — Wheel Collider (Unity Manual) — https://docs.unity3d.com/Manual/class-WheelCollider.html
- `SRC-FUNC-041` — Introduction to AssetBundles (Unity Manual) — https://docs.unity3d.com/Manual/AssetBundlesIntro.html
- `SRC-FUNC-042` — Memory in Unity: managed memory (Unity Manual) — https://docs.unity3d.com/Manual/UnderstandingAutomaticMemoryManagement.html
- `SRC-FUNC-043` — LOD Group (Unity Manual) — https://docs.unity3d.com/Manual/class-LODGroup.html
- `SRC-FUNC-044` — Post-processing (Unity Manual) — https://docs.unity3d.com/Manual/PostProcessingOverview.html
- `SRC-FUNC-045` — Render pipelines overview (Unity Manual) — https://docs.unity3d.com/Manual/render-pipelines-overview.html
- `SRC-FUNC-046` — Particle System (Unity Manual) — https://docs.unity3d.com/Manual/class-ParticleSystem.html
- `SRC-FUNC-047` — Build Settings (Unity Manual) — https://docs.unity3d.com/Manual/BuildSettings.html
- `SRC-FUNC-048` — Skinned Mesh Renderer (Unity Manual) — https://docs.unity3d.com/Manual/class-SkinnedMeshRenderer.html
- `SRC-FUNC-049` — Trees (Unity Terrain, Unity Manual) — https://docs.unity3d.com/Manual/terrain-Trees.html
- `SRC-FUNC-050` — Multi-scene editing (Unity Manual) — https://docs.unity3d.com/Manual/MultiSceneEditing.html
- `SRC-FUNC-051` — The AI Systems of Left 4 Dead — https://steamcdn-a.akamaihd.net/apps/valve/2009/ai_systems_of_l4d_mike_booth.pdf
- `SRC-FUNC-052` — Three States and a Plan: The A.I. of F.E.A.R. — https://www.gamedevs.org/uploads/three-states-plan-ai-of-fear.pdf
- `SRC-FUNC-053` — Crowd Pathfinding and Steering Using Flow Field Tiles (Game AI Pro, ch.23) — https://www.gameaipro.com/GameAIPro/GameAIPro_Chapter23_Crowd_Pathfinding_and_Steering_Using_Flow_Field_Tiles.pdf
- `SRC-FUNC-054` — Rendering 'DOOM Eternal' (Advances in Real-Time Rendering, SIGGRAPH 2020) — https://advances.realtimerendering.com/s2020/RenderingDoomEternal.pdf
- `SRC-FUNC-055` — Streaming the World of Horizon Zero Dawn — https://www.guerrilla-games.com/read/Streaming-the-World-of-Horizon-Zero-Dawn
- `SRC-FUNC-056` — Massive Crowd on Assassin's Creed Unity: AI Recycling — https://www.gdcvault.com/play/1022411/Massive-Crowd-on-Assassin-s
- `SRC-FUNC-057` — Continuous World Generation in 'No Man's Sky' — https://www.gdcvault.com/play/1024265/Continuous-World-Generation-in-No
- `SRC-FUNC-058` — 'Overwatch' Gameplay Architecture and Netcode — https://www.gdcvault.com/play/1024001/The-Power-of-Player-Feedback
- `SRC-FUNC-059` — NVIDIA DLSS: Your Questions, Answered — https://www.nvidia.com/en-us/geforce/news/nvidia-dlss-your-questions-answered/
- `SRC-FUNC-060` — DirectStorage Overview (Microsoft Game Development Kit) — https://learn.microsoft.com/en-us/gaming/gdk/docs/features/console/storage/directstorage/directstorage-overview?view=gdk-2604
- `SRC-FUNC-061` — Generating Complex Procedural Terrains Using the GPU (GPU Gems 3, ch.1) — https://developer.nvidia.com/gpugems/gpugems3/part-i-geometry/chapter-1-generating-complex-procedural-terrains-using-gpu
- `SRC-FUNC-062` — Summed-Area Variance Shadow Maps (GPU Gems 3, ch.8) — https://developer.nvidia.com/gpugems/gpugems3/part-ii-light-and-shadows/chapter-8-summed-area-variance-shadow-maps
- `SRC-FUNC-063` — Portals and Mirrors: Simple, Fast Evaluation of Potentially Visible Sets — https://luebke.us/publications/pdf/portals.pdf
- `SRC-FUNC-064` — How Northlight makes Alan Wake 2 shine — https://www.remedygames.com/article/how-northlight-makes-alan-wake-2-shine
- `SRC-FUNC-065` — Multiplayer Level Design in Red Faction Guerrilla — https://gdcvault.com/play/1012330/Multiplayer-Level-Design-in-Red
- `SRC-FUNC-066` — AMD TressFX (GPUOpen) — https://gpuopen.com/tressfx/
- `SRC-FUNC-067` — Visual Effects Summit: Can We Do It with Particles? VFX Learnings from 'Returnal' — https://gdcvault.com/play/1027742/Visual-Effects-Summit-Can-We
- `SRC-FUNC-068` — Uncharted Animation: An In-depth Look at the Character Animation Workflow and Pipeline — https://www.gdcvault.com/play/314/Uncharted-Animation-An-In-depth
- `SRC-FUNC-069` — Technical Art Techniques of Naughty Dog: Vertex Shaders and Beyond — https://gdcvault.com/play/1024103/Technical-Art-Techniques-of-Naughty
- `SRC-FUNC-070` — Making and Using Non-Standard Textures — https://cdn.cloudflare.steamstatic.com/apps/valve/2011/gdc_2011_grimes_nonstandard_textures.pdf
- `SRC-FUNC-071` — Vehicle Physics and Tire Dynamics in 'Just Cause 4' — https://www.gdcvault.com/play/1026468/Vehicle-Physics-and-Tire-Dynamics
- `SRC-FUNC-072` — NVIDIA PhysX SDK — https://developer.nvidia.com/physx-sdk
- `SRC-FUNC-073` — Component (Game Programming Patterns) — https://gameprogrammingpatterns.com/component.html
- `SRC-FUNC-074` — Object Pool (Game Programming Patterns) — https://gameprogrammingpatterns.com/object-pool.html
- `SRC-FUNC-075` — Spatial Partition (Game Programming Patterns) — https://gameprogrammingpatterns.com/spatial-partition.html
- `SRC-FUNC-076` — Game Loop (Game Programming Patterns) — https://gameprogrammingpatterns.com/game-loop.html
- `SRC-FUNC-077` — Cyberpunk 2077: Technology Preview Of New Ray Tracing Overdrive Mode Out Now — https://www.nvidia.com/en-us/geforce/news/cyberpunk-2077-ray-tracing-overdrive-update-launches-april-11/
- `SRC-FUNC-078` — It Just Works: Ray-Traced Reflections in 'Battlefield V' — https://www.gdcvault.com/play/1026282/A-B-Testing-for-Game
- `SRC-FUNC-079` — 'It Just Works': Ray-Traced Reflections in 'Battlefield V' (GTC 2019) — https://developer.download.nvidia.com/video/gputechconf/gtc/2019/presentation/s91023-it-just-works-ray-traced-reflections-in-battlefield-v.pdf
- `SRC-FUNC-080` — Virtual Shadow Maps in 'Fortnite Battle Royale' Chapter 4 — https://www.unrealengine.com/tech-blog/virtual-shadow-maps-in-fortnite-battle-royale-chapter-4
- `SRC-FUNC-081` — Visibility Preprocessing for Interactive Walkthroughs — https://people.csail.mit.edu/teller/pubs/siggraph91.pdf
- `SRC-FUNC-082` — Anti-cheat middleware (PCGamingWiki) — https://www.pcgamingwiki.com/wiki/Anti-cheat_middleware
- `SRC-FUNC-083` — Set up split-screen rendering in URP (Unity Manual) — https://docs.unity3d.com/6000.0/Documentation/Manual/urp/rendering-to-the-same-render-target.html
- `SRC-FUNC-084` — Sci-fi and fantasy worlds collide in UE5-powered co-op adventure Split Fiction — https://www.unrealengine.com/developer-interviews/sci-fi-and-fantasy-worlds-collide-in-ue5-powered-co-op-adventure-split-fiction
- `SRC-GCS-001` — Background loading — https://docs.godotengine.org/en/stable/tutorials/io/background_loading.html
- `SRC-GCS-002` — Global illumination — https://docs.godotengine.org/en/stable/tutorials/3d/global_illumination/index.html
- `SRC-GCS-003` — Using Voxel global illumination — https://docs.godotengine.org/en/stable/tutorials/3d/global_illumination/using_voxel_gi.html
- `SRC-GCS-004` — Signed distance field global illumination (SDFGI) — https://docs.godotengine.org/en/stable/tutorials/3d/global_illumination/using_sdfgi.html
- `SRC-GCS-005` — Using Lightmap global illumination — https://docs.godotengine.org/en/stable/tutorials/3d/global_illumination/using_lightmap_gi.html
- `SRC-GCS-006` — Particle systems (3D) — https://docs.godotengine.org/en/stable/tutorials/3d/particles/index.html
- `SRC-GCS-007` — Optimization using MultiMeshes — https://docs.godotengine.org/en/stable/tutorials/performance/using_multimesh.html
- `SRC-GCS-008` — High-level multiplayer — https://docs.godotengine.org/en/stable/tutorials/networking/high_level_multiplayer.html
- `SRC-GCS-009` — Occlusion culling — https://docs.godotengine.org/en/stable/tutorials/3d/occlusion_culling.html
- `SRC-GCS-010` — Mesh level of detail (LOD) — https://docs.godotengine.org/en/stable/tutorials/3d/mesh_lod.html
- `SRC-GCS-011` — Visibility ranges (HLOD) — https://docs.godotengine.org/en/stable/tutorials/3d/visibility_ranges.html
- `SRC-GCS-012` — Optimization using Servers — https://docs.godotengine.org/en/stable/tutorials/performance/using_servers.html
- `SRC-GCS-013` — The Profiler — https://docs.godotengine.org/en/stable/tutorials/scripting/debug/the_profiler.html
- `SRC-GCS-014` — 3D lights and shadows — https://docs.godotengine.org/en/stable/tutorials/3d/lights_and_shadows.html
- `SRC-GCS-015` — Using NavigationServer — https://docs.godotengine.org/en/stable/tutorials/navigation/navigation_using_navigationservers.html
- `SRC-GCS-016` — Using multiple threads — https://docs.godotengine.org/en/stable/tutorials/performance/using_multiple_threads.html
- `SRC-GCS-017` — Thread-safe APIs — https://docs.godotengine.org/en/stable/tutorials/performance/thread_safe_apis.html
- `SRC-GCS-018` — GPUParticles3D class reference — https://docs.godotengine.org/en/stable/classes/class_gpuparticles3d.html
- `SRC-GCS-019` — MultiMeshInstance3D class reference — https://docs.godotengine.org/en/stable/classes/class_multimeshinstance3d.html
- `SRC-GCS-020` — WorkerThreadPool class reference — https://docs.godotengine.org/en/stable/classes/class_workerthreadpool.html
- `SRC-GCS-021` — PhysicsServer3D class reference — https://docs.godotengine.org/en/stable/classes/class_physicsserver3d.html
- `SRC-GCS-022` — NavigationServer3D class reference — https://docs.godotengine.org/en/stable/classes/class_navigationserver3d.html
- `SRC-GCS-023` — ResourceLoader class reference — https://docs.godotengine.org/en/stable/classes/class_resourceloader.html
- `SRC-GCS-024` — Using physics interpolation — https://docs.godotengine.org/en/stable/tutorials/physics/interpolation/using_physics_interpolation.html
- `SRC-GCS-025` — Performance class reference — https://docs.godotengine.org/en/stable/classes/class_performance.html
- `SRC-GCS-026` — DirectionalLight3D class reference — https://docs.godotengine.org/en/stable/classes/class_directionallight3d.html
- `SRC-GCS-027` — MultiplayerAPI class reference — https://docs.godotengine.org/en/stable/classes/class_multiplayerapi.html
- `SRC-GCS-028` — OccluderInstance3D class reference — https://docs.godotengine.org/en/stable/classes/class_occluderinstance3d.html
- `SRC-GCS-029` — ENetMultiplayerPeer class reference — https://docs.godotengine.org/en/stable/classes/class_enetmultiplayerpeer.html
- `SRC-GCS-030` — Controlling thousands of fish with Particles (godot-docs source, RST) — https://raw.githubusercontent.com/godotengine/godot-docs/master/tutorials/performance/vertex_animation/controlling_thousands_of_fish.rst
- `SRC-GCS-031` — Godot Engine Showcase — https://godotengine.org/showcase/
- `SRC-GCS-032` — Godot 4.0 sets sail: All aboard for new horizons — https://godotengine.org/article/godot-4-0-sets-sail/
- `SRC-GCS-033` — Voxel-Based Global Illumination (SVOGI) — https://www.cryengine.com/docs/static/engines/cryengine-5/categories/23756816/pages/25535599
- `SRC-GCS-034` — Volumetric Fog — https://www.cryengine.com/docs/static/engines/cryengine-5/categories/23756816/pages/26215326
- `SRC-GCS-035` — Vegetation 02 Grass (Merged Meshes) - CRYENGINE — https://www.cryengine.com/docs/static/engines/cryengine-5/categories/23756816/pages/24285892
- `SRC-GCS-036` — Bending Setup (CRYENGINE 3 Manual, Vegetation) — https://www.cryengine.com/docs/static/engines/cryengine-3/categories/1114113/pages/1310890
- `SRC-GCS-037` — CRYENGINE 5.7 Documentation mirror - Vegetation 02 Grass (Merged Meshes) — https://raw.githubusercontent.com/z060142/CRYENGINE-5.7-Documents/main/Manual/Tutorials/Game%20and%20Level%20Design/Vegetation%20Tutorials/Tutorial%20-%20Vegetation%20Asset%20Creation/Vegetation%2002%20Grass%20(Merged%20Meshes).md
- `SRC-GCS-038` — Audio & Occlusion — https://www.cryengine.com/docs/static/engines/cryengine-5/categories/23756816/pages/44964914
- `SRC-GCS-039` — CRYENGINE 5.7 Documentation mirror - Procedural Volumetric Clouds — https://raw.githubusercontent.com/z060142/CRYENGINE-5.7-Documents/main/Manual/Graphics%20%26%20Rendering/Lighting/Lighting%20Overview/Procedural%20Volumetric%20Clouds.md
- `SRC-GCS-040` — Touch Bending (CRYENGINE 3 Manual, Vegetation) — https://www.cryengine.com/docs/static/engines/cryengine-3/categories/1114113/pages/1310750
- `SRC-GCS-041` — Voxel-Based Global Illumination (CRYENGINE 3 Manual) — https://www.cryengine.com/docs/static/engines/cryengine-3/categories/1114113/pages/19377157
- `SRC-GCS-042` — CRYENGINE 5.7 Documentation mirror - Audio CVars & Console Commands — https://raw.githubusercontent.com/z060142/CRYENGINE-5.7-Documents/main/Manual/Audio/Audio%20Overview/Audio%20CVars%20%26%20Console%20Commands.md
- `SRC-GCS-043` — CryEngine (encyclopedia article) — https://en.wikipedia.org/wiki/CryEngine
- `SRC-GCS-044` — Valve Vulkan Session (GDC 2015, Khronos session deck) — https://www.khronos.org/assets/uploads/developers/library/2015-gdc/Valve-Vulkan-Session-GDC_Mar15.pdf
- `SRC-GCS-045` — Counter-Strike 2 update notes (Steam news API for app 730) — https://api.steampowered.com/ISteamNews/GetNewsForApp/v2/?appid=730&count=100&maxlength=0
- `SRC-GCS-046` — source-sdk-2013 - src/public/bspfile.h — https://raw.githubusercontent.com/ValveSoftware/source-sdk-2013/master/src/public/bspfile.h
- `SRC-GCS-047` — source-sdk-2013 - src/public/vphysics_interface.h — https://raw.githubusercontent.com/ValveSoftware/source-sdk-2013/master/src/public/vphysics_interface.h
- `SRC-GCS-048` — source-sdk-2013 - src/public/tier0/vprof.h — https://raw.githubusercontent.com/ValveSoftware/source-sdk-2013/master/src/public/tier0/vprof.h
- `SRC-GCS-049` — source-sdk-2013 - src/game/client/prediction.cpp — https://raw.githubusercontent.com/ValveSoftware/source-sdk-2013/master/src/game/client/prediction.cpp
- `SRC-GCS-050` — source-sdk-2013 - src/game/client/clientleafsystem.cpp — https://raw.githubusercontent.com/ValveSoftware/source-sdk-2013/master/src/game/client/clientleafsystem.cpp
- `SRC-GCS-051` — source-sdk-2013 - src/game/client/vgui_netgraphpanel.cpp — https://raw.githubusercontent.com/ValveSoftware/source-sdk-2013/master/src/game/client/vgui_netgraphpanel.cpp
- `SRC-GCS-052` — source-sdk-2013 - src/game/shared/usercmd.h — https://raw.githubusercontent.com/ValveSoftware/source-sdk-2013/master/src/game/shared/usercmd.h
- `SRC-GCS-053` — source-sdk-2013 - src/public/dt_common.h — https://raw.githubusercontent.com/ValveSoftware/source-sdk-2013/master/src/public/dt_common.h
- `SRC-GCS-054` — source-sdk-2013 - src/game/shared/physics_shared.cpp — https://raw.githubusercontent.com/ValveSoftware/source-sdk-2013/master/src/game/shared/physics_shared.cpp
- `SRC-GCS-055` — Cassette Beasts Steam news (news API for app 1321440) — https://api.steampowered.com/ISteamNews/GetNewsForApp/v2/?appid=1321440&count=100&maxlength=0
- `SRC-GCS-056` — Brotato Steam news (news API for app 1942280) — https://api.steampowered.com/ISteamNews/GetNewsForApp/v2/?appid=1942280&count=100&maxlength=0
- `SRC-GCS-057` — Source 2 (encyclopedia article) — https://en.wikipedia.org/wiki/Source_2
- `SRC-GCS-058` — Tracy Profiler README — https://raw.githubusercontent.com/wolfpld/tracy/master/README.md
- `SRC-GCS-059` — Bevy README — https://raw.githubusercontent.com/bevyengine/bevy/main/README.md
- `SRC-GCS-060` — Hazel README — https://raw.githubusercontent.com/TheCherno/Hazel/master/README.md
- `SRC-GCS-061` — The Forge README — https://raw.githubusercontent.com/ConfettiFX/The-Forge/master/README.md
- `SRC-GCS-062` — EnTT README — https://raw.githubusercontent.com/skypjack/entt/master/README.md
- `SRC-GCS-063` — FrameGraph README — https://raw.githubusercontent.com/azhirnov/FrameGraph/master/README.md
- `SRC-GCS-064` — FrameGraph - docs/Multithreading.md — https://raw.githubusercontent.com/azhirnov/FrameGraph/master/docs/Multithreading.md
- `SRC-GCS-065` — FrameGraph - docs/Introduction.md — https://raw.githubusercontent.com/azhirnov/FrameGraph/master/docs/Introduction.md
- `SRC-GCS-066` — Bevy ECS README — https://raw.githubusercontent.com/bevyengine/bevy/main/crates/bevy_ecs/README.md
- `SRC-GCS-067` — Bevy Tasks README — https://raw.githubusercontent.com/bevyengine/bevy/main/crates/bevy_tasks/README.md
- `SRC-GCS-068` — mimalloc readme — https://raw.githubusercontent.com/microsoft/mimalloc/main/readme.md
- `SRC-HE-001` — HeroEngine (official product homepage) — https://www.heroengine.com/
- `SRC-HE-002` — HeroEngine (encyclopedia article) — https://en.wikipedia.org/wiki/HeroEngine
- `SRC-HE-003` — BioWare Licenses HeroEngine For Star Wars: The Old Republic MMO — https://www.gamedeveloper.com/game-platforms/bioware-licenses-heroengine-for-i-star-wars-the-old-republic-i-mmo
- `SRC-HE-004` — HeroEngine - The Cloud-Based MMO Game Engine Behind SWTOR — https://www.mycplus.com/game-development/game-engines/heroengine/
- `SRC-HE-005` — HeroEngine homepage (Internet Archive snapshot, 2013) — https://web.archive.org/web/2013/http://www.heroengine.com/
- `SRC-HE-006` — HeroBlade \| HeroEngine (Internet Archive snapshot, 2014) — https://web.archive.org/web/2014/http://www.heroengine.com/heroengine/heroblade/
- `SRC-HE-007` — World Building \| HeroEngine (Internet Archive snapshot, 2013-12-27) — https://web.archive.org/web/20131227161309/http://www.heroengine.com/heroengine/world-building/
- `SRC-HE-008` — Server Systems \| HeroEngine (Internet Archive snapshot, 2013) — https://web.archive.org/web/2013/http://www.heroengine.com/features/server-systems/
- `SRC-HE-009` — Game Systems \| HeroEngine (Internet Archive snapshot, 2013) — https://web.archive.org/web/2013/http://www.heroengine.com/heroengine/game-systems/
- `SRC-HE-010` — Licensing Options \| HeroEngine (Internet Archive snapshot, 2013) — https://web.archive.org/web/2013/http://www.heroengine.com/heroengine/licensing-options/
- `SRC-HE-011` — HEWIKI Main Page (Internet Archive snapshot, 2014; page last modified 2013-02-08) — https://web.archive.org/web/2014/http://hewiki.heroengine.com/wiki/Main_Page
- `SRC-HE-012` — Scalability and Building For Massive Multiplayer Audiences (HEWIKI, Internet Archive snapshot; page last modified 2011-10-18) — https://web.archive.org/web/2014/http://hewiki.heroengine.com/wiki/Scalability_and_Building_For_Massive_Multiplayer_Audiences
- `SRC-HE-013` — HeroCloud Tech Features \| HeroEngine (Internet Archive snapshot, 2014) — https://web.archive.org/web/2014/http://www.heroengine.com/herocloud/tech-features/
- `SRC-HE-015` — SWTOR DirectX 12 Spring 2026 Update (official developer blog) — https://www.swtor.com/info/news/%5Bnews-category%5D/20260331
- `SRC-HE-016` — Idea Fabrik, the company behind Hero Engine and The Repopulation, disappears from the internet — https://massivelyop.com/2023/04/29/idea-fabrik-creator-of-the-hero-engine-and-the-repopulation-disappears-from-the-internet/
- `SRC-HE-017` — Software:Faxion Online (encyclopedia article, Wikipedia mirror) — https://handwiki.org/wiki/Software:Faxion_Online
- `SRC-HE-018` — Laniatus Cloud Tech (official company site) — https://www.laniatus.com/
- `SRC-HE-019` — PlayM2M on Steam (store page) — https://store.steampowered.com/app/2292370/PlayM2M/
- `SRC-HE-020` — Idea Fabrik PLC (official corporate site) — http://www.ideafabrik.com/
- `SRC-MPR-001` — Rendering the Hellscape of Doom Eternal (Advances in Real-Time Rendering, SIGGRAPH 2020) — https://advances.realtimerendering.com/s2020/RenderingDoomEternal.pdf
- `SRC-MPR-002` — Exploring Ray Traced Future in Metro Exodus (NVIDIA GTC 2019) — https://developer.download.nvidia.com/video/gputechconf/gtc/2019/presentation/s9985-exploring-ray-traced-future-in-metro-exodus.pdf
- `SRC-MPR-003` — How Northlight makes Alan Wake 2 shine — https://www.remedygames.com/article/how-northlight-makes-alan-wake-2-shine
- `SRC-MPR-004` — Moving Gears to Tier 2 Variable Rate Shading (DirectX Developer Blog, guest post by The Coalition) — https://devblogs.microsoft.com/directx/gears-vrs-tier2/
- `SRC-MPR-005` — Face-Off: Titanfall 2 (Digital Foundry) — https://www.digitalfoundry.net/articles/digitalfoundry-2016-titanfall-2-face-off
- `SRC-MPR-006` — Brilliant visuals and growing pains: analysing Unreal Engine 5 first-generation games (Digital Foundry) — https://www.digitalfoundry.net/articles/digitalfoundry-2023-brilliant-visuals-and-growing-pains-analysing-unreal-engine-5-first-generation-games
- `SRC-MPR-007` — Black Myth: Wukong - the PC tech review (Digital Foundry) — https://www.digitalfoundry.net/articles/digitalfoundry-2024-black-myth-wukong-the-pc-tech-review
- `SRC-MPR-008` — Lords of the Fallen is a stunning UE5 soulslike with ongoing tech issues (Digital Foundry) — https://www.digitalfoundry.net/articles/digitalfoundry-2023-lords-of-the-fallen-is-a-stunning-ue5-soulslike-with-ongoing-tech-issues
- `SRC-MPR-009` — Senua's Saga: Hellblade 2 is a defining moment in the evolution of real-time graphics (Digital Foundry) — https://www.digitalfoundry.net/articles/digitalfoundry-2024-senuas-saga-hellblade-2-is-a-defining-moment-in-the-evolution-of-real-time-graphics
- `SRC-MPR-010` — Senua's Saga: Hellblade 2 PC tech review (Digital Foundry) — https://www.digitalfoundry.net/articles/digitalfoundry-2024-senuas-saga-hellblade-2-pc-tech-review
- `SRC-MPR-011` — The AI Systems of Left 4 Dead (GDC 2009) — https://cdn.akamai.steamstatic.com/apps/valve/2009/ai_systems_of_l4d_mike_booth.pdf
- `SRC-MPR-012` — Three States and a Plan: The A.I. of F.E.A.R. (GDC 2006) — https://www.gamedevs.org/uploads/three-states-plan-ai-of-fear.pdf
- `SRC-MPR-013` — Crowd Pathfinding and Steering Using Flow Field Tiles (Game AI Pro, Chapter 23) — https://www.gameaipro.com/GameAIPro/GameAIPro_Chapter23_Crowd_Pathfinding_and_Steering_Using_Flow_Field_Tiles.pdf
- `SRC-MPR-014` — The Art of Destruction in Rainbow Six: Siege (GDC 2016) — https://media.gdcvault.com/gdc2016/Presentations/LHeureux_Julien_Art_Of_Destruction.pdf
- `SRC-MPR-015` — Massive Crowd on Assassin's Creed Unity: AI Recycling (GDC 2015, session page) — https://www.gdcvault.com/play/1022411/Massive-Crowd-on-Assassin-s
- `SRC-MPR-016` — Continuous World Generation in 'No Man's Sky' (GDC 2017, session page) — https://www.gdcvault.com/play/1024265/Continuous-World-Generation-in-No
- `SRC-MPR-017` — Graphics Deep Dive: Cascaded voxel cone tracing in The Tomorrow Children (Game Developer / Gamasutra) — https://www.gamedeveloper.com/programming/graphics-deep-dive-cascaded-voxel-cone-tracing-in-i-the-tomorrow-children-i-
- `SRC-MPR-018` — Interactive Indirect Illumination Using Voxel Cone Tracing (Pacific Graphics 2011) — https://research.nvidia.com/labs/rtr/publication/crassin2011givoxels/
- `SRC-MPR-019` — GPU Gems 3, Chapter 13: Volumetric Light Scattering as a Post-Process — https://developer.nvidia.com/gpugems/gpugems3/part-ii-light-and-shadows/chapter-13-volumetric-light-scattering-post-process
- `SRC-MPR-020` — Decima Engine: Advances in Lighting and AA (Guerrilla, SIGGRAPH 2017 talk page) — https://www.guerrilla-games.com/read/decima-engine-advances-in-lighting-and-aa
- `SRC-MPR-021` — Streaming the World of Horizon Zero Dawn (Guerrilla talk page) — https://www.guerrilla-games.com/read/streaming-the-world-of-horizon-zero-dawn
- `SRC-MPR-022` — GPU-Based Procedural Placement in Horizon Zero Dawn (Guerrilla talk page) — https://www.guerrilla-games.com/read/gpu-based-procedural-placement-in-horizon-zero-dawn
- `SRC-MPR-023` — Virtual Shadow Maps in Unreal Engine (Epic official documentation) — https://dev.epicgames.com/documentation/en-us/unreal-engine/virtual-shadow-maps-in-unreal-engine
- `SRC-MPR-024` — Lumen Technical Details in Unreal Engine (Epic official documentation) — https://dev.epicgames.com/documentation/en-us/unreal-engine/lumen-technical-details-in-unreal-engine
- `SRC-MPR-025` — Lightmass Basics in Unreal Engine (Epic official documentation) — https://dev.epicgames.com/documentation/en-us/unreal-engine/lightmass-basics-in-unreal-engine
- `SRC-MPR-026` — Optimizing Rendering with PSO Caches in Unreal Engine (Epic official documentation) — https://dev.epicgames.com/documentation/unreal-engine/optimizing-rendering-with-pso-caches-in-unreal-engine?lang=en-US
- `SRC-MPR-027` — Scalability in Unreal Engine (Epic official documentation) — https://dev.epicgames.com/documentation/en-us/unreal-engine/scalability-in-unreal-engine
- `SRC-MPR-028` — Dynamic Resolution in Unreal Engine (Epic official documentation) — https://dev.epicgames.com/documentation/en-us/unreal-engine/dynamic-resolution-in-unreal-engine
- `SRC-MPR-029` — Hierarchical Level of Detail in Unreal Engine (Epic official documentation) — https://dev.epicgames.com/documentation/en-us/unreal-engine/hierarchical-level-of-detail-in-unreal-engine
- `SRC-MPR-030` — Hair Rendering and Simulation in Unreal Engine (Epic official documentation) — https://dev.epicgames.com/documentation/en-us/unreal-engine/hair-rendering-and-simulation-in-unreal-engine
- `SRC-MPR-031` — Water System in Unreal Engine (Epic official documentation) — https://dev.epicgames.com/documentation/en-us/unreal-engine/water-system-in-unreal-engine
- `SRC-MPR-032` — Scriptable Render Pipeline Batcher in URP (Unity official documentation) — https://docs.unity3d.com/Manual/SRPBatcher.html
- `SRC-MPR-033` — Quality Settings (Unity official documentation) — https://docs.unity3d.com/Manual/class-QualitySettings.html
- `SRC-MPR-034` — Lightmapping (Unity official documentation) — https://docs.unity3d.com/Manual/Lightmapping.html
- `SRC-MPR-035` — The Progressive Lightmapper (Unity official documentation) — https://docs.unity3d.com/Manual/progressive-lightmapper.html
- `SRC-MPR-036` — Light Probes (Unity official documentation) — https://docs.unity3d.com/Manual/LightProbes.html
- `SRC-MPR-037` — V Rising: Behind the vampire realm built on 1,600 ECS systems (Unity case study) — https://unity.com/resources/stunlock-studios-v-rising
- `SRC-MPR-038` — Using SDFGI (Godot official documentation) — https://docs.godotengine.org/en/stable/tutorials/3d/global_illumination/using_sdfgi.html
- `SRC-MPR-039` — 2D lights and shadows (Godot official documentation) — https://docs.godotengine.org/en/stable/tutorials/2d/2d_lights_and_shadows.html
- `SRC-MPR-040` — Using LightmapGI (Godot official documentation) — https://docs.godotengine.org/en/stable/tutorials/3d/global_illumination/using_lightmap_gi.html
- `SRC-MPR-041` — Variable Rate Shading (Microsoft Direct3D 12 documentation) — https://learn.microsoft.com/en-us/windows/win32/direct3d12/vrs
- `SRC-MPR-042` — DirectStorage overview (Microsoft Game Development Kit documentation) — https://learn.microsoft.com/en-us/gaming/gdk/docs/features/console/storage/directstorage/directstorage-overview?view=gdk-2604
- `SRC-MPR-043` — GPU Lightmass Global Illumination in Unreal Engine (Epic official documentation) — https://dev.epicgames.com/documentation/en-us/unreal-engine/gpu-lightmass-global-illumination-in-unreal-engine
- `SRC-MPR-044` — Distance Field Soft Shadows in Unreal Engine (Epic official documentation) — https://dev.epicgames.com/documentation/en-us/unreal-engine/distance-field-soft-shadows-in-unreal-engine
- `SRC-MPR-045` — Saving and Loading Your Game in Unreal Engine (Epic official documentation) — https://dev.epicgames.com/documentation/en-us/unreal-engine/saving-and-loading-your-game-in-unreal-engine
- `SRC-MPR-046` — Audio Mixer Overview in Unreal Engine (Epic official documentation) — https://dev.epicgames.com/documentation/en-us/unreal-engine/audio-mixer-overview-in-unreal-engine
- `SRC-MPR-047` — Gameplay Ability System in Unreal Engine (Epic official documentation) — https://dev.epicgames.com/documentation/en-us/unreal-engine/gameplay-ability-system-for-unreal-engine
- `SRC-MPR-048` — The creators of the Havok engine discouraged the authors of Red Faction: Guerrilla from destructibility, calling it impossible (Studio AtticSalt) — https://www.studioatticsalt.com/the-creators-of-the-havok-engine-discouraged-the-authors-of-red-faction-guerrilla-from-destructibility-calling-it-impossible/
- `SRC-MPR-049` — Using Light Shafts in Unreal Engine (Epic official documentation) — https://dev.epicgames.com/documentation/unreal-engine/using-light-shafts-in-unreal-engine?lang=en-US
- `SRC-MPR-050` — Volumetric Fog in Unreal Engine (Epic official documentation) — https://dev.epicgames.com/documentation/en-us/unreal-engine/volumetric-fog-in-unreal-engine
- `SRC-MPR-051` — Portal developer commentary (Portal Wiki transcription of Valve in-game commentary) — https://theportalwiki.com/wiki/Portal_developer_commentary
- `SRC-MPR-052` — Occlusion Culling (Unity official documentation) — https://docs.unity3d.com/Manual/OcclusionCulling.html
- `SRC-MPR-053` — Occlusion culling (Godot official documentation) — https://docs.godotengine.org/en/stable/tutorials/3d/occlusion_culling.html
- `SRC-MPR-054` — Mesh level of detail (LOD) (Godot official documentation) — https://docs.godotengine.org/en/stable/tutorials/3d/mesh_lod.html
- `SRC-MPR-055` — Using physics interpolation (Godot official documentation) — https://docs.godotengine.org/en/stable/tutorials/physics/interpolation/using_physics_interpolation.html
- `SRC-MPR-056` — Reflections Captures in Unreal Engine (Epic official documentation) — https://dev.epicgames.com/documentation/en-us/unreal-engine/reflections-captures-in-unreal-engine
- `SRC-MPR-057` — Overview of Niagara Effects in Unreal Engine (Epic official documentation) — https://dev.epicgames.com/documentation/en-us/unreal-engine/overview-of-niagara-effects-for-unreal-engine
- `SRC-MPR-058` — Cloth (Unity official documentation) — https://docs.unity3d.com/Manual/class-Cloth.html
- `SRC-MPR-059` — Job System overview (Unity official documentation) — https://docs.unity3d.com/Manual/JobSystemOverview.html
- `SRC-MPR-060` — Sprite Atlas (Unity official documentation) — https://docs.unity3d.com/Manual/class-SpriteAtlas.html
- `SRC-MPR-061` — True Impostors (GPU Gems 3, Chapter 21) — https://developer.nvidia.com/gpugems/gpugems3/part-iv-image-effects/chapter-21-true-impostors
- `SRC-MPR-062` — Baking Normal Maps on the GPU (GPU Gems 3, Chapter 22) — https://developer.nvidia.com/gpugems/gpugems3/part-iv-image-effects/chapter-22-baking-normal-maps-gpu
- `SRC-MPR-063` — Chaos Physics Overview in Unreal Engine (Epic official documentation) — https://dev.epicgames.com/documentation/en-us/unreal-engine/chaos-physics-overview
- `SRC-MPR-064` — Motion Matching in Unreal Engine (Epic official documentation) — https://dev.epicgames.com/documentation/en-us/unreal-engine/motion-matching-in-unreal-engine
- `SRC-MPR-065` — 3D lights and shadows (Godot official documentation) — https://docs.godotengine.org/en/stable/tutorials/3d/lights_and_shadows.html
- `SRC-MPR-066` — Illuminating Roco's Legacy: Scalable Global Illumination from Theory to Practice (GDC 2026) — https://media.gdcvault.com/gdc2026/Slides/Sheng_Feng_IlluminatingRocosLegacyScalableGlobalIlluminationfromTheorytoPractice.pdf
- `SRC-NTA-001` — Source Multiplayer Networking (Valve Developer Community wiki) — https://developer.valvesoftware.com/wiki/Source_Multiplayer_Networking
- `SRC-NTA-002` — Lag Compensation (Valve Developer Community wiki) — https://developer.valvesoftware.com/wiki/Lag_Compensation
- `SRC-NTA-003` — Latency Compensating Methods in Client/Server In-game Protocol Design and Optimization (Yahn Bernier, GDC 2001) — https://developer.valvesoftware.com/wiki/Latency_Compensating_Methods_in_Client/Server_In-game_Protocol_Design_and_Optimization
- `SRC-NTA-004` — 'Overwatch' Gameplay Architecture and Netcode (GDC 2017) — https://www.gdcvault.com/play/1024001/-Overwatch-Gameplay-Architecture-and
- `SRC-NTA-005` — Replay Technology in 'Overwatch': Kill Cam, Gameplay, and Highlights (GDC 2017) — https://www.gdcvault.com/play/1024053/Replay-Technology-in-Overwatch-Kill
- `SRC-NTA-006` — VALORANT's 128-Tick Servers (Riot Games tech blog) — https://www.riotgames.com/en/news/valorants-128-tick-servers
- `SRC-NTA-007` — Peeking into VALORANT's Netcode (Riot Games tech blog) — https://www.riotgames.com/en/news/peeking-valorants-netcode
- `SRC-NTA-008` — 1500 Archers on a 28.8: Network Programming in Age of Empires and Beyond — https://www.gamedeveloper.com/programming/1500-archers-on-a-28-8-network-programming-in-age-of-empires-and-beyond
- `SRC-NTA-009` — 1500 Archers on a 28.8 (PDF mirror with tables and diagrams) — https://www.gamedevs.org/uploads/1500-archers-age-of-empires-network-programming.pdf
- `SRC-NTA-010` — Fast-Paced Multiplayer (Part I): Client-Server Game Architecture (PDF) — https://radwan92.github.io/assets/pdfs/Fast-Paced%20Multiplayer%20-%20Gabriel%20Gambetta.pdf
- `SRC-NTA-011` — Client-Side Prediction and Server Reconciliation (Fast-Paced Multiplayer Part II) — https://www.gabrielgambetta.com/client-side-prediction-server-reconciliation.html
- `SRC-NTA-012` — Counter-Strike 2 official feature page ('What you see is what you get' / sub-tick) — https://www.counter-strike.net/cs2/hardware?l=english
- `SRC-NTA-013` — Sub-tick (Counter-Strike community wiki) — https://counterstrikewiki.com/Sub-tick
- `SRC-NTA-014` — Replication Graph in Unreal Engine (UE 5.8 Documentation) — https://dev.epicgames.com/documentation/unreal-engine/replication-graph-in-unreal-engine?lang=en-US
- `SRC-NTA-015` — Setting Up Dedicated Servers in Unreal Engine (UE 5.8 Documentation) — https://dev.epicgames.com/documentation/unreal-engine/setting-up-dedicated-servers-in-unreal-engine?lang=en-US
- `SRC-NTA-016` — Iris Replication System in Unreal Engine (UE 5.8 Documentation) — https://dev.epicgames.com/documentation/zh-cn/unreal-engine/iris-replication-system-in-unreal-engine
- `SRC-NTA-017` — Unity Netcode for Entities (package manual 1.0.17) — https://docs.unity3d.com/Packages/com.unity.netcode@1.0/manual/index.html
- `SRC-NTA-018` — Introduction to prediction (Netcode for Entities 7.0 manual) — https://docs.unity3d.com/Packages/com.unity.netcode@7.0/manual/intro-to-prediction.html
- `SRC-NTA-019` — Unity's netcode packages (Unity Multiplayer docs) — https://docs.unity.com/en-us/multiplayer/netcode/netcode
- `SRC-NTA-020` — Steam Audio - Programmer's Guide (C API) — https://valvesoftware.github.io/steam-audio/doc/capi/guide.html
- `SRC-NTA-021` — Steam Audio core documentation (GitHub, index.rst) — https://github.com/ValveSoftware/steam-audio/blob/master/core/doc/index.rst
- `SRC-NTA-022` — Using Features: Occlusion (Wwise documentation) — https://www.audiokinetic.com/library/edge/?source=UE4&id=using_features_occlusion.html
- `SRC-NTA-023` — Wwise Acoustics Concepts (Spatial Audio concepts) — https://www.audiokinetic.com/library/edge/?source=SDK&id=spatial_audio_concepts.html
- `SRC-NTA-024` — Obstruction and Occlusion (Wwise Unity documentation mirror) — https://documentation.help/Wwise-Unity/pg__obs__occ.html
- `SRC-NTA-025` — Wwise Spatial Audio (product page) — https://www.audiokinetic.com/en/wwise/wwise-spatial-audio/
- `SRC-NTA-026` — FMOD - Core API: Using DSP Effects — https://www.fmod.com/docs/2.03/api/using-dsp-effects-in-the-core-api.html
- `SRC-NTA-027` — FMOD API - FMOD_DSP_CONVOLUTION_REVERB — https://www.fmod.com/resources/documentation-api?version=1.10&page=content/generated/FMOD_DSP_CONVOLUTION_REVERB.html
- `SRC-NTA-028` — Steam Datagram Relay (Steamworks Documentation) — https://partner.steamgames.com/doc/features/multiplayer/steamdatagramrelay
- `SRC-NTA-029` — Steam Datagram Relay (Valve Developer Community wiki) — https://developer.valvesoftware.com/wiki/Steam_Datagram_Relay
- `SRC-NTA-030` — Using the Anti-Cheat Interfaces (Epic Online Services / Easy Anti-Cheat) — https://dev.epicgames.com/docs/game-services/anti-cheat/using-anti-cheat
- `SRC-NTA-031` — Anti-Cheat Interfaces (Epic Online Services, Trust & Safety) — https://dev.epicgames.com/docs/epic-online-services/trust-and-safety/anti-cheat-interfaces/anti-cheat-interfaces
- `SRC-NTA-032` — Vanguard On-Demand - Anti-Cheat Update (Riot Games) — https://www.riotgames.com/en/news/vanguard-on-demand
- `SRC-NTA-033` — Riot Vanguard FAQ (Riot Games Support) — https://support.riotgames.com/en-us/league-of-legends/performance/riot-vanguard-faq-league-of-legends/
- `SRC-NTA-034` — Garbage collection modes (Unity Manual, Unity 6 / 6000.0) — https://docs.unity3d.com/6000.0/Documentation/Manual/performance-incremental-garbage-collection.html
- `SRC-NTA-035` — Garbage Collection Settings in the Unreal Engine Project Settings (UE 5.8 Documentation) — https://dev.epicgames.com/documentation/unreal-engine/garbage-collection-settings-in-the-unreal-engine-project-settings?lang=en-US
- `SRC-NTA-036` — Migrate to Iris in Unreal Engine (UE 5.8 Documentation) — https://dev.epicgames.com/documentation/en-us/unreal-engine/migrate-to-iris-in-unreal-engine
- `SRC-NTA-037` — Quake 3 Network Protocol — https://www.jfedor.org/quake3/
- `SRC-NTA-038` — Quake-III-Arena / code/server/sv_snapshot.c (id Software GPL source release) — https://github.com/id-Software/Quake-III-Arena/blob/master/code/server/sv_snapshot.c
- `SRC-NTA-039` — GameNetworkingSockets (ValveSoftware) — https://github.com/ValveSoftware/GameNetworkingSockets
- `SRC-NTA-040` — Ambience Design and Acoustic Systems in 'Senua's Saga: Hellblade II' (GDC 2025) — https://gdcvault.com/play/1035513/Ambience-Design-and-Acoustic-Systems
- `SRC-NTA-041` — How Ninja Theory created Hellblade II's unsettling soundscape (Game Developer) — https://www.gamedeveloper.com/audio/how-ninja-theory-created-hellblade-ii-s-unsettling-soundscape
- `SRC-NTA-042` — Developer Insight - Did you hear that? (Hunt: Showdown, Crytek) — https://devtrackers.gg/hunt-showdown/p/e4016122-developer-insight-did-you-hear-that
- `SRC-NTA-043` — Dedicated Server (Unity Manual) — https://docs.unity.cn/Manual//dedicated-server.html
- `SRC-NTA-044` — Build your application for Dedicated Server (Unity Manual) — https://docs.unity3d.org.cn/Manual/dedicated-server-build.html
- `SRC-NTA-045` — Why Bullets "Miss": An Analysis of the CS2 Subtick System — https://csgo-news.com/en/guides/why-bullets-miss-an-analysis-of-the-cs2-subtick-system
- `SRC-NTA-046` — Lag compensation (Official Team Fortress Wiki) — https://wiki.teamfortress.com/wiki/Lag_compensation
- `SRC-NTA-047` — VAN: Limiting and Closing the Vanguard Pre-Boot Motherboard Security Gap (Riot Games) — https://www.riotgames.com/zh-cn/news/vanguard-security-update-motherboard-zh-cn
- `SRC-NTA-048` — Fan translation/summary of 'Overwatch Gameplay Architecture and Netcode' (GDC 2017) — https://zzzremake.github.io/site/blog/translate-overwatch-architecture-netcode/
- `SRC-NTA-049` — 'Overwatch' Gameplay Architecture and Netcode (full talk video) — https://www.youtube.com/watch?v=Ks98kE3cs30
- `SRC-NTA-050` — Audio file compression in Unity (Unity Manual) — https://docs.unity3d.com/6000.0/Documentation/Manual/AudioFiles-compression.html
- `SRC-NTA-051` — Conversion Settings Editor (Wwise documentation) — https://www.audiokinetic.com/zh/public-library/2025.1.9_9197/?source=Help&id=conversion_settings_editor
- `SRC-NTA-052` — Prediction (Netcode for Entities documentation, GitHub mirror) — https://github.com/needle-mirror/com.unity.netcode/blob/master/Documentation%7E/prediction-n4e.md
- `SRC-RND-001` — Lumen Global Illumination and Reflections (Unreal Engine 5.8 Documentation) — https://dev.epicgames.com/documentation/en-us/unreal-engine/lumen-global-illumination-and-reflections-in-unreal-engine
- `SRC-RND-002` — Virtual Shadow Maps (Unreal Engine 5.8 Documentation) — https://dev.epicgames.com/documentation/en-us/unreal-engine/virtual-shadow-maps-in-unreal-engine
- `SRC-RND-003` — Nanite Virtualized Geometry Overview (Unreal Engine 5.8 Documentation) — https://dev.epicgames.com/documentation/en-us/unreal-engine/nanite-virtualized-geometry-in-unreal-engine
- `SRC-RND-004` — Temporal Super Resolution (Unreal Engine 5.8 Documentation) — https://dev.epicgames.com/documentation/en-us/unreal-engine/temporal-super-resolution-in-unreal-engine
- `SRC-RND-005` — Render Dependency Graph (Unreal Engine 5.8 Documentation) — https://dev.epicgames.com/documentation/en-us/unreal-engine/render-dependency-graph-in-unreal-engine
- `SRC-RND-006` — Dynamic Resolution (Unreal Engine 5.8 Documentation) — https://dev.epicgames.com/documentation/en-us/unreal-engine/dynamic-resolution-in-unreal-engine
- `SRC-RND-007` — Path Tracer (Unreal Engine 5.8 Documentation) — https://dev.epicgames.com/documentation/en-us/unreal-engine/path-tracer-in-unreal-engine
- `SRC-RND-008` — Scalability (Unreal Engine 5.8 Documentation) — https://dev.epicgames.com/documentation/en-us/unreal-engine/scalability-in-unreal-engine
- `SRC-RND-009` — PSO Caches (Unreal Engine 5.8 Documentation) — https://dev.epicgames.com/documentation/unreal-engine/optimizing-rendering-with-pso-caches-in-unreal-engine?lang=en-US
- `SRC-RND-010` — NVIDIA DLSS (developer landing page) — https://developer.nvidia.com/dlss
- `SRC-RND-011` — Accelerating Ultra-Realistic Game Development with NVIDIA DLSS 3 and NVIDIA RTX Path Tracing — https://developer.nvidia.com/blog/accelerating-ultrarealistic-game-development-with-nvidia-dlss-3-and-rtx-path-tracing/
- `SRC-RND-012` — FidelityFX Super Resolution 2 (FSR 2.2.1) README — https://github.com/GPUOpen-Effects/FidelityFX-FSR2
- `SRC-RND-013` — Intel XeSS Super Resolution (XeSS-SR) Developer Guide 2.0 — https://github.com/intel/xess/blob/main/doc/xess_sr_developer_guide_english.md
- `SRC-RND-014` — DirectX Raytracing (DXR) Functional Spec, v1.48 — https://github.com/microsoft/DirectX-Specs/blob/master/d3d/Raytracing.md
- `SRC-RND-015` — Ray Tracing (Vulkan Documentation Project / Khronos guide) — https://docs.vulkan.org/guide/latest/extensions/ray_tracing.html
- `SRC-RND-016` — VK_EXT_mesh_shader proposal (Vulkan Documentation Project) — https://docs.vulkan.org/features/latest/features/proposals/VK_EXT_mesh_shader.html
- `SRC-RND-017` — Variable Rate Shading (VRS) Functional Spec — https://github.com/microsoft/DirectX-Specs/blob/master/d3d/VariableRateShading.md
- `SRC-RND-018` — Interactive Indirect Illumination Using Voxel Cone Tracing — https://research.nvidia.com/labs/rtr/publication/crassin2011givoxels/
- `SRC-RND-019` — Volumetric Fog: Unified, compute shader based solution to atmospheric scattering — https://bartwronski.com/wp-content/uploads/2014/08/bwronski_volumetric_fog_siggraph2014.pdf
- `SRC-RND-020` — Clustered Deferred and Forward Shading — https://www.cse.chalmers.se/~uffe/clustered_shading_preprint.pdf
- `SRC-RND-021` — FrameGraph: Extensible Rendering Architecture in Frostbite — https://www.gdcvault.com/play/1024045/FrameGraph-Extensible-Rendering-Architecture-in
- `SRC-RND-022` — Rendering the Hellscape of Doom Eternal — https://advances.realtimerendering.com/s2020/RenderingDoomEternal.pdf
- `SRC-RND-023` — How Northlight makes Alan Wake 2 shine — https://www.remedygames.com/article/how-northlight-makes-alan-wake-2-shine
- `SRC-RND-024` — Path Tracing & Overdrive Mode - Requirements & How-To (Cyberpunk 2077 support) — https://support.cdprojektred.com/en/cyberpunk/pc/sp-technical/issue/2383/path-tracing-overdrive-mode-requirements-how-to
- `SRC-RND-025` — Quake II RTX: Re-Engineering a Classic with Ray Tracing Effects on Vulkan — https://www.nvidia.com/en-us/geforce/news/quake-ii-rtx-ray-tracing-vulkan-vkray-geforce-rtx/
- `SRC-RND-026` — Global Illumination in Metro Exodus: An Artist's Point of View — https://developer.nvidia.com/blog/global-illumination-in-metro-exodus/
- `SRC-RND-027` — Exploring Ray Traced Future in Metro Exodus (GTC 2019) — https://developer.download.nvidia.com/video/gputechconf/gtc/2019/presentation/s9985-exploring-ray-traced-future-in-metro-exodus.pdf
- `SRC-RND-028` — Decima Engine: Advances in Lighting and AA — https://www.guerrilla-games.com/read/decima-engine-advances-in-lighting-and-aa
- `SRC-RND-029` — 2D lights and shadows (Godot Engine documentation) — https://docs.godotengine.org/en/stable/tutorials/2d/2d_lights_and_shadows.html
- `SRC-RND-030` — "A Dive into Render Graphs" (SIGGRAPH 2023) - NOT LOCATED — https://advances.realtimerendering.com/s2023/index.html
- `SRC-RND-031` — Real-Time Rendering, 4th edition — https://www.realtimerendering.com/
- `SRC-RND-032` — Shadow mapping (Wikipedia) — https://en.wikipedia.org/wiki/Shadow_mapping
- `SRC-RND-033` — Ambient occlusion (Wikipedia) — https://en.wikipedia.org/wiki/Ambient_occlusion
- `SRC-RND-034` — Lightmap (Wikipedia) — https://en.wikipedia.org/wiki/Lightmap
- `SRC-RND-035` — Progressive Lightmapper (Unity Manual) — https://docs.unity3d.com/Manual/progressive-lightmapper.html
- `SRC-RND-036` — Scriptable Render Pipeline Batcher (Unity Manual) — https://docs.unity3d.com/Manual/SRPBatcher.html
- `SRC-RND-037` — Scene Capture 2D (Unreal Engine documentation) — https://dev.epicgames.com/documentation/en-us/unreal-engine/scene-capture-2d-in-unreal-engine
- `SRC-RND-038` — GPU Lightmass (Unreal Engine documentation) — https://dev.epicgames.com/documentation/en-us/unreal-engine/gpu-lightmass-in-unreal-engine
- `SRC-RND-039` — SRP Batcher: Speed up your rendering! — https://unity.com/blog/engine-platform/srp-batcher-speed-up-your-rendering
- `SRC-RND-040` — Hierarchical-Z map based occlusion culling — https://www.rastergrid.com/blog/2010/10/hierarchical-z-map-based-occlusion-culling/
- `SRC-RND-041` — Leveraging Asynchronous Queues for Concurrent Execution — https://gpuopen.com/learn/concurrent-execution-asynchronous-queues/
- `SRC-RND-042` — Sci-fi and fantasy worlds collide in UE5-powered co-op adventure Split Fiction (developer interview) — https://www.unrealengine.com/developer-interviews/sci-fi-and-fantasy-worlds-collide-in-ue5-powered-co-op-adventure-split-fiction
- `SRC-RND-043` — Portals \| Part 6 - Portal Recursion — https://danielilett.com/2020-01-19-tut4-6-portal-recursion/
- `SRC-RND-044` — Mesh Shader Functional Spec (D3D12) — https://microsoft.github.io/DirectX-Specs/d3d/MeshShader.html
- `SRC-RND-045` — DOOM Eternal - Graphics Study — https://www.simoncoenen.com/blog/programming/graphics/DoomEternalStudy
- `SRC-RND-046` — Using async compute to saturate GPU (Vulkan Samples) — https://docs.vulkan.org/samples/latest/samples/performance/async_compute/README.html
- `SRC-RND-047` — HLSL Dynamic Resources (Shader Model 6.6) — https://microsoft.github.io/DirectX-Specs/d3d/HLSL_SM_6_6_DynamicResources.html
- `SRC-RND-048` — It Takes Two tech analysis (Digital Foundry) — https://en.wikipedia.org/wiki/It_Takes_Two_(video_game)
- `SRC-TN-001` — DirectX 12 programming guide (Windows Win32) — https://learn.microsoft.com/en-us/windows/win32/direct3d12/directx-12-programming-guide
- `SRC-TN-002` — Command queues and command lists (Direct3D 12) — https://learn.microsoft.com/en-us/windows/win32/direct3d12/command-queues-and-command-lists
- `SRC-TN-003` — Direct3D 11 graphics (table of contents) — https://learn.microsoft.com/en-us/windows/win32/direct3d11/atoc-dx-graphics-direct3d-11
- `SRC-TN-004` — Direct3D 11 programming reference (Win32 API index) — https://learn.microsoft.com/en-us/windows/win32/api/_direct3d11/
- `SRC-TN-005` — Vulkan Specification (latest, HTML) — https://registry.khronos.org/vulkan/specs/latest/html/vkspec.html
- `SRC-TN-006` — Vulkan-Docs (Khronos Group repository) — https://github.com/KhronosGroup/Vulkan-Docs
- `SRC-TN-007` — DirectX Raytracing (DXR) functional specification overview — https://learn.microsoft.com/en-us/windows/win32/direct3d12/direct3d-12-raytracing
- `SRC-TN-008` — HLSL reference for DirectX Raytracing — https://learn.microsoft.com/en-us/windows/win32/direct3d12/direct3d-12-raytracing-hlsl-reference
- `SRC-TN-009` — acl - Animation Compression Library — https://github.com/nfrechette/acl
- `SRC-TN-010` — Animation Compression Library in Unreal Engine — https://dev.epicgames.com/documentation/en-us/unreal-engine/animation-compression-library-in-unreal-engine
- `SRC-TN-011` — meshoptimizer - mesh optimization library — https://github.com/zeux/meshoptimizer
- `SRC-TN-012` — meshoptimizer README — https://github.com/zeux/meshoptimizer/blob/master/README.md
- `SRC-TN-013` — RVO2 Library: documentation (2.0) — https://gamma.cs.unc.edu/RVO2/documentation/2.0/
- `SRC-TN-014` — RVO2 Library - project page — https://gamma.cs.unc.edu/RVO2/
- `SRC-TN-015` — Tracy Profiler — https://github.com/wolfpld/tracy
- `SRC-TN-016` — Tracy Profiler README — https://github.com/wolfpld/tracy/blob/master/README.md
- `SRC-TN-017` — Opus Codec - official site — https://opus-codec.org
- `SRC-TN-018` — RFC 6716 - Definition of the Opus Audio Codec — https://datatracker.ietf.org/doc/html/rfc6716
- `SRC-TN-019` — PhysX (NVIDIA-Omniverse) repository — https://github.com/NVIDIA-Omniverse/PhysX
- `SRC-TN-020` — NVIDIA PhysX SDK developer page — https://developer.nvidia.com/physx-sdk
- `SRC-TN-021` — Unity DOTS product page — https://unity.com/dots
- `SRC-TN-022` — Unity Entities package manual — https://docs.unity3d.com/Packages/com.unity.entities@1.0/manual/index.html
- `SRC-TN-023` — Unity Netcode for Entities manual — https://docs.unity3d.com/Packages/com.unity.netcode@1.0/manual/index.html
- `SRC-TN-024` — Unity Transport package manual — https://docs.unity3d.com/Packages/com.unity.transport@1.5/manual/index.html
- `SRC-TN-025` — Unity Addressables package manual — https://docs.unity3d.com/Packages/com.unity.addressables@1.21/manual/index.html
- `SRC-TN-026` — Unity Burst compiler package manual — https://docs.unity3d.com/Packages/com.unity.burst@1.8/manual/index.html
- `SRC-TN-027` — Universal Render Pipeline package manual — https://docs.unity3d.com/Packages/com.unity.render-pipelines.universal@14.0/manual/index.html
- `SRC-TN-028` — World Partition in Unreal Engine — https://dev.epicgames.com/documentation/en-us/unreal-engine/world-partition-in-unreal-engine
- `SRC-TN-029` — Replication Graph in Unreal Engine — https://dev.epicgames.com/documentation/en-us/unreal-engine/replication-graph-in-unreal-engine
- `SRC-TN-030` — Steamworks SDK documentation — https://partner.steamgames.com/doc/sdk
- `SRC-TN-031` — Steamworks Features overview — https://partner.steamgames.com/doc/features
- `SRC-TN-032` — Microsoft DirectStorage repository — https://github.com/microsoft/DirectStorage
- `SRC-TN-033` — DirectStorage README — https://github.com/microsoft/DirectStorage/blob/main/README.md
- `SRC-TN-040` — Ashes of the Singularity (Wikipedia) — https://en.wikipedia.org/wiki/Ashes_of_the_Singularity
- `SRC-TN-041` — Civilization VI (Wikipedia) — https://en.wikipedia.org/wiki/Civilization_VI
- `SRC-TN-042` — The Witcher 3: Wild Hunt (Wikipedia) — https://en.wikipedia.org/wiki/The_Witcher_3:_Wild_Hunt
- `SRC-TN-043` — Grand Theft Auto V (Wikipedia) — https://en.wikipedia.org/wiki/Grand_Theft_Auto_V
- `SRC-TN-044` — Doom (2016 video game) — https://en.wikipedia.org/wiki/Doom_(2016_video_game)
- `SRC-TN-045` — Doom Eternal (Wikipedia) — https://en.wikipedia.org/wiki/Doom_Eternal
- `SRC-TN-046` — Battlefield V (Wikipedia) — https://en.wikipedia.org/wiki/Battlefield_V
- `SRC-TN-047` — Metro Exodus (Wikipedia) — https://en.wikipedia.org/wiki/Metro_Exodus
- `SRC-TN-048` — Batman: Arkham Asylum (Wikipedia) — https://en.wikipedia.org/wiki/Batman:_Arkham_Asylum
- `SRC-TN-049` — Mafia II (Wikipedia) — https://en.wikipedia.org/wiki/Mafia_II
- `SRC-TN-050` — Team Fortress 2 (Wikipedia) — https://en.wikipedia.org/wiki/Team_Fortress_2
- `SRC-TN-051` — Counter-Strike 2 (Wikipedia) — https://en.wikipedia.org/wiki/Counter-Strike_2
- `SRC-TN-052` — Fortnite (Wikipedia) — https://en.wikipedia.org/wiki/Fortnite
- `SRC-TN-053` — V Rising (Wikipedia) — https://en.wikipedia.org/wiki/V_Rising
- `SRC-TN-054` — Ratchet & Clank: Rift Apart (Wikipedia) — https://en.wikipedia.org/wiki/Ratchet_and_Clank:_Rift_Apart
- `SRC-TN-055` — Forspoken (Wikipedia) — https://en.wikipedia.org/wiki/Forspoken
- `SRC-TN-056` — Portal 2 (Wikipedia) — https://en.wikipedia.org/wiki/Portal_2
- `SRC-WRS-001` — World Partition (Unreal Engine 5.8 Documentation) — https://dev.epicgames.com/documentation/en-us/unreal-engine/world-partition-in-unreal-engine
- `SRC-WRS-002` — World Partition - Data Layers in Unreal Engine — https://dev.epicgames.com/documentation/en-us/unreal-engine/world-partition---data-layers-in-unreal-engine
- `SRC-WRS-003` — One File Per Actor in Unreal Engine — https://dev.epicgames.com/documentation/en-us/unreal-engine/one-file-per-actor-in-unreal-engine
- `SRC-WRS-004` — World Partition - Hierarchical Level of Detail in Unreal Engine — https://dev.epicgames.com/documentation/en-us/unreal-engine/world-partition---hierarchical-level-of-detail-in-unreal-engine
- `SRC-WRS-005` — Large World Coordinates in Unreal Engine 5 — https://dev.epicgames.com/documentation/en-us/unreal-engine/large-world-coordinates-in-unreal-engine-5
- `SRC-WRS-006` — Large World Coordinates Rendering in Unreal Engine 5 — https://dev.epicgames.com/documentation/en-us/unreal-engine/large-world-coordinates-rendering-in-unreal-engine-5
- `SRC-WRS-007` — Nanite Virtualized Geometry Overview (Unreal Engine 5.8 Documentation) — https://dev.epicgames.com/documentation/en-us/unreal-engine/nanite-virtualized-geometry-in-unreal-engine
- `SRC-WRS-008` — Virtual Texturing in Unreal Engine — https://dev.epicgames.com/documentation/en-us/unreal-engine/virtual-texturing-in-unreal-engine
- `SRC-WRS-009` — Streaming Virtual Texturing in Unreal Engine — https://dev.epicgames.com/documentation/en-us/unreal-engine/streaming-virtual-texturing-in-unreal-engine
- `SRC-WRS-010` — Runtime Virtual Texturing in Unreal Engine — https://dev.epicgames.com/documentation/en-us/unreal-engine/runtime-virtual-texturing-in-unreal-engine
- `SRC-WRS-011` — Virtual Texture Memory Pools in Unreal Engine — https://dev.epicgames.com/documentation/en-us/unreal-engine/virtual-texture-memory-pools-in-unreal-engine
- `SRC-WRS-012` — Texture Streaming in Unreal Engine — https://dev.epicgames.com/documentation/en-us/unreal-engine/texture-streaming-in-unreal-engine
- `SRC-WRS-013` — Mesh Distance Fields in Unreal Engine — https://dev.epicgames.com/documentation/en-us/unreal-engine/mesh-distance-fields-in-unreal-engine
- `SRC-WRS-014` — Distance Field Soft Shadows in Unreal Engine — https://dev.epicgames.com/documentation/en-us/unreal-engine/distance-field-soft-shadows-in-unreal-engine
- `SRC-WRS-015` — Precomputed Visibility Volumes in Unreal Engine — https://dev.epicgames.com/documentation/en-us/unreal-engine/precomputed-visibility-volumes-in-unreal-engine
- `SRC-WRS-016` — Visibility and Occlusion Culling in Unreal Engine — https://dev.epicgames.com/documentation/en-us/unreal-engine/visibility-and-occlusion-culling-in-unreal-engine
- `SRC-WRS-017` — Landscape Technical Guide in Unreal Engine — https://dev.epicgames.com/documentation/en-us/unreal-engine/landscape-technical-guide-in-unreal-engine
- `SRC-WRS-018` — Asynchronous Asset Loading in Unreal Engine — https://dev.epicgames.com/documentation/en-us/unreal-engine/asynchronous-asset-loading-in-unreal-engine
- `SRC-WRS-019` — Oodle Data (Unreal Engine Documentation) — https://dev.epicgames.com/documentation/en-us/unreal-engine/oodle-data
- `SRC-WRS-020` — Cooking and Chunking in Unreal Engine — https://dev.epicgames.com/documentation/en-us/unreal-engine/cooking-and-chunking-in-unreal-engine
- `SRC-WRS-021` — Foliage Mode in Unreal Engine — https://dev.epicgames.com/documentation/en-us/unreal-engine/foliage-mode-in-unreal-engine
- `SRC-WRS-022` — Instanced Static Mesh in Unreal Engine — https://dev.epicgames.com/documentation/en-us/unreal-engine/instanced-static-mesh-in-unreal-engine
- `SRC-WRS-023` — Hierarchical Instanced Static Mesh in Unreal Engine — https://dev.epicgames.com/documentation/en-us/unreal-engine/hierarchical-instanced-static-mesh-in-unreal-engine
- `SRC-WRS-024` — Automatic Static Mesh LOD Generation in Unreal Engine — https://dev.epicgames.com/documentation/en-us/unreal-engine/automatic-static-mesh-lod-generation-in-unreal-engine
- `SRC-WRS-025` — Procedural Content Generation Overview (Unreal Engine) — https://dev.epicgames.com/documentation/en-us/unreal-engine/procedural-content-generation-overview-in-unreal-engine
- `SRC-WRS-026` — Nanite: A Deep Dive (SIGGRAPH 2021, Advances in Real-Time Rendering in Games) — https://advances.realtimerendering.com/s2021/Karis_Nanite_SIGGRAPH_Advances_2021_final.pdf
- `SRC-WRS-027` — GPU-Driven Rendering Pipelines (SIGGRAPH 2015, Advances in Real-Time Rendering in Games) — https://www.advances.realtimerendering.com/s2015/aaltonenhaar_siggraph2015_combined_final_footer_220dpi.pdf
- `SRC-WRS-028` — GPU Gems 2, Chapter 2: Terrain Rendering Using GPU-Based Geometry Clipmaps — https://developer.nvidia.com/gpugems/gpugems2/part-i-geometric-complexity/chapter-2-terrain-rendering-using-gpu-based-geometry
- `SRC-WRS-029` — GPU Gems 3, Chapter 4: Next-Generation SpeedTree Rendering — https://developer.nvidia.com/gpugems/gpugems3/part-i-geometry/chapter-4-next-generation-speedtree-rendering
- `SRC-WRS-030` — Chunked LOD (SIGGRAPH 2002 'Super-size it! Scaling up to Massive Virtual Worlds' course notes + site) — https://tulrich.com/geekstuff/chunklod.html
- `SRC-WRS-031` — C-BDAM - Compressed Batched Dynamic Adaptive Meshes for Terrain Rendering — https://www.crs4.it/vic/data/papers/eg2006-cbdam.pdf
- `SRC-WRS-032` — Sparse Virtual Textures (GDC 2008 talk, slides + public-domain demo source) — https://silverspaceship.com/src/svt/
- `SRC-WRS-033` — Software Virtual Textures — https://mrelusive.com/publications/papers/Software-Virtual-Textures.pdf
- `SRC-WRS-034` — DirectStorage (Win32 apps) - Microsoft Learn — https://learn.microsoft.com/en-us/windows/win32/dstorage/dstorage-portal
- `SRC-WRS-035` — Using DirectStorage - Microsoft Learn — https://learn.microsoft.com/en-us/windows/win32/dstorage/using-dstorage
- `SRC-WRS-036` — microsoft/DirectStorage (GitHub) - GDeflate README — https://github.com/microsoft/DirectStorage/blob/main/GDeflate/GDeflate/README.md
- `SRC-WRS-037` — Tiled resources (Direct3D 11.2) - Microsoft Learn — https://learn.microsoft.com/en-us/windows/win32/direct3d11/tiled-resources
- `SRC-WRS-038` — Terrain Rendering in 'Far Cry 5' (GDC 2018) — https://gdcvault.com/play/1025480/Terrain-Rendering-in-Far-Cry
- `SRC-WRS-039` — GPU-Based Procedural Placement in Horizon Zero Dawn (GDC 2017) — https://www.guerrilla-games.com/read/gpu-based-procedural-placement-in-horizon-zero-dawn
- `SRC-WRS-040` — Continuous World Generation in 'No Man's Sky' (GDC 2017) — https://gdcvault.com/play/1024265/Continuous-World-Generation-in-No
- `SRC-WRS-041` — Chunk format - Minecraft Wiki — https://minecraft.wiki/w/Chunk_format
- `SRC-WRS-042` — Chunk - Minecraft Wiki — https://minecraft.wiki/w/Chunk
- `SRC-WRS-043` — Simulation distance - Minecraft Wiki — https://minecraft.wiki/w/Simulation_distance
- `SRC-WRS-044` — meshoptimizer (GitHub README) — https://github.com/zeux/meshoptimizer
- `SRC-WRS-045` — Random-Access Neural Compression of Material Textures (project page, SIGGRAPH 2023) — https://research.nvidia.com/labs/rtr/neural_texture_compression/
- `SRC-WRS-046` — Random-Access Neural Compression of Material Textures (author's version, PDF) — https://research.nvidia.com/labs/rtr/neural_texture_compression/assets/ntc_medium_size.pdf
- `SRC-WRS-047` — NVIDIA-RTX/RTXNTC: NVIDIA Neural Texture Compression SDK — https://github.com/NVIDIA-RTX/Rtxntc
- `SRC-WRS-048` — Octahedral Impostors — https://shaderbits.com/blog/octahedral-impostors
- `SRC-WRS-049` — Large world coordinates - Godot Engine (4.4) documentation — https://docs.godotengine.org/en/4.4/tutorials/physics/large_world_coordinates.html
- `SRC-WRS-050` — Updating Game Build (Steamworks Documentation) — https://partner.steamgames.com/doc/sdk/updating
- `SRC-WRS-051` — Building Worlds Using Math(s) (GDC 2017, No Man's Sky) — https://gdcvault.com/play/1024514/Building-Worlds-Using
- `SRC-WRS-052` — DirectStorage GpuDecompressionBenchmark sample (GitHub) — https://github.com/microsoft/DirectStorage/blob/main/Samples/GpuDecompressionBenchmark/README.md
- `SRC-WRS-053` — SteamPipe / Uploading to Steam (Steamworks Documentation) — https://partner.steamgames.com/doc/sdk/uploading
- `SRC-WRS-054` — DirectStorage API Now Available on PC (DirectX Developer Blog) — https://devblogs.microsoft.com/directx/directstorage-api-available-on-pc/
- `SRC-WRS-055` — meshoptimizer users (maintainer's list of commercial games and engines) — https://github.com/zeux/meshoptimizer/discussions/986
- `STANDARD_VULKAN_SPEC` — Vulkan 1.3 Extensions Specification — https://registry.khronos.org/vulkan/specs/1.3-extensions/html/
- `TECH_CAPTURE` — Epic: Scene Capture — https://dev.epicgames.com/documentation/unreal-engine/BlueprintAPI/Rendering/SceneCapture/CaptureScene?lang=en-US
- `TECH_CLOTH` — Unity 6: Cloth — https://docs.unity3d.com/6000.0/Documentation/Manual/class-Cloth.html
- `TECH_DESTRUCTION` — Epic: Destruction Overview — https://dev.epicgames.com/documentation/unreal-engine/destruction-overview?lang=en-US
- `TECH_HAIR` — Epic: Hair Rendering and Simulation — https://dev.epicgames.com/documentation/unreal-engine/hair-rendering-and-simulation-in-unreal-engine?lang=en-US
- `TECH_REVERB` — Epic: Convolution Reverb — https://dev.epicgames.com/documentation/unreal-engine/convolution-reverb-in-unreal-engine
- `TECH_SECURITY` — Epic: Anti-Cheat Interfaces — https://dev.epicgames.com/docs/epic-online-services/trust-and-safety/anti-cheat-interfaces
- `UE_ANIMBUDGET` — Unreal Engine: Animation Budget Allocator — https://dev.epicgames.com/documentation/en-us/unreal-engine/animation-budget-allocator-in-unreal-engine
- `UE_CHAOS` — Unreal Engine: Chaos Physics — https://dev.epicgames.com/documentation/en-us/unreal-engine/chaos-physics-in-unreal-engine
- `UE_CITY_SAMPLE` — City Sample Project Unreal Engine Demonstration — https://dev.epicgames.com/documentation/en-us/unreal-engine/city-sample-project-unreal-engine-demonstration
- `UE_CITY_SAMPLE_PCG` — City Sample PCG for Unreal Engine — https://dev.epicgames.com/documentation/en-us/unreal-engine/city-sample-pcg-for-unreal-engine?lang=en-US
- `UE_DISTANCE_SHADOWS` — Unreal Engine: Using Distance Field Shadows — https://dev.epicgames.com/documentation/unreal-engine/using-distance-field-shadows-in-unreal-engine?lang=en-US
- `UE_FEATURE_MATRIX` — Supported Features by Rendering Path for Desktop — https://dev.epicgames.com/documentation/en-us/unreal-engine/supported-features-by-rendering-path-for-desktop-with-unreal-engine
- `UE_HLOD` — Unreal Engine: Hierarchical Level of Detail — https://dev.epicgames.com/documentation/en-us/unreal-engine/hierarchical-level-of-detail-in-unreal-engine
- `UE_INSIGHTS` — Unreal Engine: Unreal Insights — https://dev.epicgames.com/documentation/en-us/unreal-engine/unreal-insights-in-unreal-engine
- `UE_ISM` — Unreal Engine: Instanced Static Mesh — https://dev.epicgames.com/documentation/en-us/unreal-engine/instanced-static-mesh-in-unreal-engine
- `UE_LOD` — Unreal Engine: Level of Detail — https://dev.epicgames.com/documentation/en-us/unreal-engine/level-of-detail-in-unreal-engine
- `UE_LUMEN` — Unreal Engine: Lumen Global Illumination and Reflections — https://dev.epicgames.com/documentation/en-us/unreal-engine/lumen-global-illumination-and-reflections-in-unreal-engine
- `UE_LWC` — Unreal Engine: Large World Coordinates — https://dev.epicgames.com/documentation/en-us/unreal-engine/large-world-coordinates-in-unreal-engine
- `UE_MASS` — Unreal Engine: Mass Entity — https://dev.epicgames.com/documentation/en-us/unreal-engine/mass-entity-in-unreal-engine
- `UE_MOTION_MATCHING` — Motion Matching in Unreal Engine — https://dev.epicgames.com/documentation/en-us/unreal-engine/motion-matching-in-unreal-engine
- `UE_NANITE` — Unreal Engine: Nanite Virtualized Geometry — https://dev.epicgames.com/documentation/en-us/unreal-engine/nanite-virtualized-geometry-in-unreal-engine
- `UE_NAVMESH` — Unreal Engine: Navigation Mesh — https://dev.epicgames.com/documentation/en-us/unreal-engine/navigation-mesh-in-unreal-engine
- `UE_NETWORKING` — Unreal Engine: Networking and Multiplayer — https://dev.epicgames.com/documentation/en-us/unreal-engine/networking-and-multiplayer-in-unreal-engine
- `UE_NIAGARA` — Unreal Engine: Niagara Visual Effects — https://dev.epicgames.com/documentation/en-us/unreal-engine/niagara-visual-effects-in-unreal-engine
- `UE_REPGRAPH` — Unreal Engine: Replication Graph — https://dev.epicgames.com/documentation/en-us/unreal-engine/replication-graph-in-unreal-engine
- `UE_SAVEGAME` — Unreal Engine: Saving and Loading Your Game — https://docs.unrealengine.com/4.27/en-US/InteractiveExperiences/SaveGame/
- `UE_SCALABILITY` — Unreal Engine: Scalability Reference — https://dev.epicgames.com/documentation/en-us/unreal-engine/scalability-in-unreal-engine
- `UE_SIGNIFICANCE` — Unreal Engine: Significance Manager — https://dev.epicgames.com/documentation/en-us/unreal-engine/significance-manager-in-unreal-engine
- `UE_VIRTUALTEXTURING` — Unreal Engine: Virtual Texturing — https://dev.epicgames.com/documentation/en-us/unreal-engine/virtual-texturing-in-unreal-engine
- `UE_VSM` — Unreal Engine: Virtual Shadow Maps — https://dev.epicgames.com/documentation/en-us/unreal-engine/virtual-shadow-maps-in-unreal-engine
- `UE_WORLDPARTITION` — Unreal Engine: World Partition — https://dev.epicgames.com/documentation/en-us/unreal-engine/world-partition-in-unreal-engine
- `UNITY_ADDRESSABLES` — Unity Manual: Addressables — https://docs.unity3d.com/Manual/com.unity.addressables.html
- `UNITY_DOTS_PRODUCTION` — Unity DOTS - Data-Oriented Technology Stack — https://unity.com/dots
- `UNITY_DRAW_CALLS` — Unity Manual: Choose a method for optimizing draw calls — https://docs.unity3d.com/Manual/optimizing-draw-calls-choose-method.html
- `UNITY_ENTITIES` — Unity Manual: Entities (DOTS) — https://docs.unity3d.com/Packages/com.unity.entities@1.0/manual/index.html
- `UNITY_GC_BEST_PRACTICES` — Unity Manual: Garbage collection best practices — https://docs.unity3d.com/2023.1/Documentation/Manual/performance-garbage-collection-best-practices.html
- `UNITY_GFX_PERF` — Unity Manual: Optimizing Graphics Performance — https://docs.unity3d.com/Manual/OptimizingGraphicsPerformance.html
- `UNITY_GPU_BUDGETS` — Unity — Managing GPU usage for PC and console games — https://unity.com/how-to/gpu-optimization
- `UNITY_INSTANCING` — Unity Manual: GPU Instancing — https://docs.unity3d.com/Manual/GPUInstancing.html
- `UNITY_JOBS` — Unity Manual: Job System — https://docs.unity3d.com/Manual/JobSystem.html
- `UNITY_LIGHTMAPPER` — Unity Manual: Progressive Lightmapper — https://docs.unity3d.com/Manual/progressive-lightmapper.html
- `UNITY_LIGHTMAPUV` — Unity Manual: Generating Lightmapping UVs — https://docs.unity3d.com/Manual/LightingGiUvs-GeneratingLightmappingUVs.html
- `UNITY_LIGHTPROBES` — Unity Manual: Light Probes — https://docs.unity3d.com/Manual/LightProbes.html
- `UNITY_NETCODE` — Unity Manual: Netcode — https://docs.unity3d.com/Packages/com.unity.netcode@1.0/manual/index.html
- `UNITY_OCCLUSION` — Unity Manual: Occlusion Culling — https://docs.unity3d.com/Manual/OcclusionCulling.html
- `UNITY_PROFILER` — Unity Manual: Profiler — https://docs.unity3d.com/Manual/Profiler.html
- `UNITY_QUALITY` — Unity Manual: Quality Settings — https://docs.unity3d.com/Manual/class-QualitySettings.html
- `UNITY_SHADERLOAD` — Unity Manual: Optimizing Shader Load Time — https://docs.unity3d.com/6000.0/Documentation/Manual/shader-loading.html
- `UNITY_SRP_BATCHER` — Unity Manual: SRP Batcher — https://docs.unity3d.com/Manual/SRPBatcher.html
- `UNITY_TEXTURE_STREAMING` — Unity Manual: Texture Streaming — https://docs.unity3d.com/Manual/TextureStreaming.html
- `VALVE_DIRECTOR` — The AI Systems of Left 4 Dead — Michael Booth, Valve — https://cdn.akamai.steamstatic.com/apps/valve/2009/ai_systems_of_l4d_mike_booth.pdf
- `VALVE_REWIND` — Valve Source SDK — player_lagcompensation.cpp — https://github.com/ValveSoftware/source-sdk-2013/blob/master/src/game/server/player_lagcompensation.cpp
- `VALVE_SUBTICK` — Counter-Strike 2 — sub-tick updates, Valve — https://www.counter-strike.net/cs2
- `WIKI_AO` — Ambient occlusion — https://en.wikipedia.org/wiki/Ambient_occlusion
- `WIKI_ATLAS` — Texture atlas — https://en.wikipedia.org/wiki/Texture_atlas
- `WIKI_BEHAVIOR_TREE` — Behavior tree (artificial intelligence, robotics and control) — https://en.wikipedia.org/wiki/Behavior_tree_(artificial_intelligence,_robotics_and_control)
- `WIKI_BVH` — Bounding volume hierarchy — https://en.wikipedia.org/wiki/Bounding_volume_hierarchy
- `WIKI_DEFERRED` — Deferred shading — https://en.wikipedia.org/wiki/Deferred_shading
- `WIKI_DELTA` — Delta encoding — https://en.wikipedia.org/wiki/Delta_encoding
- `WIKI_DLSS` — Deep learning super sampling — https://en.wikipedia.org/wiki/Deep_learning_super_sampling
- `WIKI_DOD` — Data-oriented design — https://en.wikipedia.org/wiki/Data-oriented_design
- `WIKI_ECS` — Entity component system — https://en.wikipedia.org/wiki/Entity_component_system
- `WIKI_FFT` — Fast Fourier transform — https://en.wikipedia.org/wiki/Fast_Fourier_transform
- `WIKI_FSM` — Finite-state machine — https://en.wikipedia.org/wiki/Finite-state_machine
- `WIKI_FSR` — FidelityFX Super Resolution — https://en.wikipedia.org/wiki/FidelityFX_Super_Resolution
- `WIKI_GAME_AI` — Video game artificial intelligence — https://en.wikipedia.org/wiki/Video_game_artificial_intelligence
- `WIKI_GERSTNER` — Gerstner wave — https://en.wikipedia.org/wiki/Gerstner_wave
- `WIKI_GLOBAL_ILLUMINATION` — Global illumination — https://en.wikipedia.org/wiki/Global_illumination
- `WIKI_HSR` — Hidden-surface determination — https://en.wikipedia.org/wiki/Hidden-surface_determination
- `WIKI_IK` — Inverse kinematics — https://en.wikipedia.org/wiki/Inverse_kinematics
- `WIKI_IMPOSTOR` — Impostor (computer graphics) — https://en.wikipedia.org/wiki/Impostor_(computer_graphics)
- `WIKI_LIGHTMAP` — Lightmap — https://en.wikipedia.org/wiki/Lightmap
- `WIKI_LOD` — Level of detail (computer graphics) — https://en.wikipedia.org/wiki/Level_of_detail_(computer_graphics)
- `WIKI_MIPMAP` — Mipmap — https://en.wikipedia.org/wiki/Mipmap
- `WIKI_NAVMESH` — Navigation mesh — https://en.wikipedia.org/wiki/Navigation_mesh
- `WIKI_OBJECTPOOL` — Object pool pattern — https://en.wikipedia.org/wiki/Object_pool_pattern
- `WIKI_PARTICLES` — Particle system — https://en.wikipedia.org/wiki/Particle_system
- `WIKI_PATH_TRACING` — Path tracing — https://en.wikipedia.org/wiki/Path_tracing
- `WIKI_PREDICTION` — Client-side prediction — https://en.wikipedia.org/wiki/Client-side_prediction
- `WIKI_PROCEDURAL` — Procedural generation — https://en.wikipedia.org/wiki/Procedural_generation
- `WIKI_RAGDOLL` — Ragdoll physics — https://en.wikipedia.org/wiki/Ragdoll_physics
- `WIKI_RAY_TRACING` — Ray tracing (graphics) — https://en.wikipedia.org/wiki/Ray_tracing_(graphics)
- `WIKI_RIGID_BODY` — Rigid body dynamics — https://en.wikipedia.org/wiki/Rigid_body_dynamics
- `WIKI_SDF` — Signed distance function — https://en.wikipedia.org/wiki/Signed_distance_function
- `WIKI_SHADOWMAP` — Shadow mapping — https://en.wikipedia.org/wiki/Shadow_mapping
- `WIKI_SKINNING` — Skinning — https://en.wikipedia.org/wiki/Skinning
- `WIKI_SVO` — Sparse voxel octree — https://en.wikipedia.org/wiki/Sparse_voxel_octree
- `WIKI_TAA` — Temporal anti-aliasing — https://en.wikipedia.org/wiki/Temporal_anti-aliasing
- `WIKI_VEHICLE_DYNAMICS` — Vehicle dynamics — https://en.wikipedia.org/wiki/Vehicle_dynamics
- `WIKI_VOLUMETRIC` — Volumetric rendering — https://en.wikipedia.org/wiki/Volumetric_rendering
- `hardware:00acf849ec56` — PassMark Video Card Benchmarks — Radeon RX 7900 XT — https://www.videocardbenchmark.net/gpu.php?gpu=Radeon+RX+7900+XT&id=4646
- `hardware:04891bb1e6c7` — PassMark Intel Core i7-11800H Benchmark — CPU Mark 19596, Single 3007 — https://www.cpubenchmark.net/cpu.php?cpu=Intel+Core+i7-11800H+%40+2.30GHz&id=4358
- `hardware:05e7e544759d` — PassMark Video Card Benchmarks — GeForce RTX 3050 6GB Laptop GPU — https://www.videocardbenchmark.net/gpu.php?gpu=GeForce+RTX+3050+6GB+Laptop+GPU&id=4782
- `hardware:064fe7ca5e68` — PassMark CPU Benchmarks — AMD Ryzen 5 5500 — https://www.cpubenchmark.net/cpu.php?cpu=AMD+Ryzen+5+5500&id=4807
- `hardware:06d672d982fc` — PassMark CPU Benchmarks — Intel Core i7-9700K — https://www.cpubenchmark.net/cpu.php?cpu=Intel+Core+i7-9700K&id=3335
- `hardware:080bb8b4f6d1` — PassMark Intel Core i7-13700H Benchmark — CPU Mark 25860, Single 3552 — https://www.cpubenchmark.net/cpu.php?cpu=Intel+Core+i7-13700H&id=5226
- `hardware:0ae6626d2565` — PassMark Video Card Benchmarks — GeForce RTX 5050 Laptop GPU — https://www.videocardbenchmark.net/gpu.php?gpu=GeForce+RTX+5050+Laptop+GPU&id=6552
- `hardware:0b39637c4ec8` — PassMark Video Card Benchmarks — GeForce RTX 2060 — https://www.videocardbenchmark.net/gpu.php?gpu=GeForce+RTX+2060&id=4037
- `hardware:0c09a16c68f9` — PassMark AMD Ryzen 5 7500F Benchmark — CPU Mark 26537, Single 3825 — https://www.cpubenchmark.net/cpu.php?cpu=AMD+Ryzen+5+7500F&id=5648
- `hardware:0ff0fa934e0c` — PassMark CPU Benchmarks — Intel Core i3-10100 — https://www.cpubenchmark.net/cpu.php?cpu=Intel+Core+i3-10100&id=3717
- `hardware:1059383223be` — PassMark Intel Core i5-11400F Benchmark — CPU Mark 16869, Single 2979 — https://www.cpubenchmark.net/cpu.php?cpu=Intel+Core+i5-11400F+%40+2.60GHz&id=4226
- `hardware:13a9cace366f` — PassMark - Radeon Vega 3 - Price performance comparison — https://www.videocardbenchmark.net/gpu.php?gpu=Radeon+Vega+3&id=3926
- `hardware:1440e3fdc3aa` — PassMark Video Card Benchmarks — GeForce GTX 1650 — https://www.videocardbenchmark.net/gpu.php?gpu=GeForce+GTX+1650&id=4078
- `hardware:15733d23becf` — PassMark CPU Benchmarks — Intel Core i5-10400F — https://www.cpubenchmark.net/cpu.php?cpu=Intel+Core+i5-10400F&id=3767
- `hardware:15b098956b50` — PassMark AMD Ryzen 9 5950X Benchmark — CPU Mark 45259, Single 3476 — https://www.cpubenchmark.net/cpu.php?cpu=AMD+Ryzen+9+5950X&id=3862
- `hardware:1655dac07397` — PassMark Video Card Benchmarks — GeForce GTX 1050 Ti — https://www.videocardbenchmark.net/gpu.php?gpu=GeForce+GTX+1050+Ti&id=3595
- `hardware:1663f825c7f5` — PassMark Video Card Benchmarks — GeForce RTX 3070 — https://www.videocardbenchmark.net/gpu.php?gpu=GeForce+RTX+3070&id=4283
- `hardware:1997146c058f` — PassMark Video Card Benchmarks — GeForce RTX 2070 SUPER — https://www.videocardbenchmark.net/gpu.php?gpu=GeForce+RTX+2070+SUPER&id=4116
- `hardware:1adf7bbcc286` — PassMark CPU Benchmarks — AMD Ryzen 5 3600 — https://www.cpubenchmark.net/cpu.php?cpu=AMD+Ryzen+5+3600&id=3481
- `hardware:1c641b1616ea` — PassMark CPU Benchmarks — AMD Ryzen 3 1200 — https://www.cpubenchmark.net/cpu.php?cpu=AMD+Ryzen+3+1200&id=3029
- `hardware:1cd7069270e3` — PassMark Video Card Benchmarks — GeForce RTX 3050 8GB — https://www.videocardbenchmark.net/gpu.php?gpu=GeForce+RTX+3050+8GB&id=4495
- `hardware:1f99ebff4ca8` — PassMark CPU Benchmarks — AMD Ryzen 9 5900X — https://www.cpubenchmark.net/cpu.php?cpu=AMD+Ryzen+9+5900X&id=3870
- `hardware:213472decf76` — PassMark - Radeon 780M - Price performance comparison — https://www.videocardbenchmark.net/gpu.php?gpu=Radeon+780M&id=4818
- `hardware:22f84720ecb7` — PassMark Video Card Benchmarks — GeForce GTX 1660 Ti — https://www.videocardbenchmark.net/gpu.php?gpu=GeForce+GTX+1660+Ti&id=4045
- `hardware:23eb35a6cdef` — PassMark Video Card Benchmarks — Radeon RX 580 — https://www.videocardbenchmark.net/gpu.php?gpu=Radeon+RX+580&id=3736
- `hardware:24823f308139` — PassMark - Radeon RX 7700 XT - Price performance comparison — https://www.videocardbenchmark.net/gpu.php?gpu=Radeon+RX+7700+XT&id=4919
- `hardware:2e59fdf3fded` — PassMark - GeForce GT 1030 - Price performance comparison — https://www.videocardbenchmark.net/gpu.php?gpu=GeForce+GT+1030&id=3757
- `hardware:2f0ce84b7851` — PassMark - GeForce GTX 1050 - Price performance comparison — https://www.videocardbenchmark.net/gpu.php?gpu=GeForce+GTX+1050&id=3596
- `hardware:2f4c6f21f764` — PassMark Intel Core i7-10700K Benchmark — CPU Mark 18501, Single 3036 — https://www.cpubenchmark.net/cpu.php?cpu=Intel+Core+i7-10700K+%40+3.80GHz&id=3733
- `hardware:32c454082048` — PassMark - GeForce RTX 2080 SUPER - Price performance comparison — https://www.videocardbenchmark.net/gpu.php?gpu=GeForce+RTX+2080+SUPER&id=4123
- `hardware:32c984630655` — PassMark - Intel UHD Graphics 630 - Price performance comparison — https://www.videocardbenchmark.net/gpu.php?gpu=Intel+UHD+Graphics+630&id=3826
- `hardware:39023f2f2854` — PassMark CPU Benchmarks — Intel Core i7-13700K — https://www.cpubenchmark.net/cpu.php?cpu=Intel+Core+i7-13700K&id=5060
- `hardware:3981b71516d5` — PassMark - GeForce RTX 2080 - Price performance comparison — https://www.videocardbenchmark.net/gpu.php?gpu=GeForce+RTX+2080&id=3989
- `hardware:3a1abc3aed60` — PassMark Video Card Benchmarks — Radeon RX 6650 XT — https://www.videocardbenchmark.net/gpu.php?gpu=Radeon+RX+6650+XT&id=4541
- `hardware:3a9a732e872b` — PassMark Video Card Benchmarks — GeForce RTX 5060 — https://www.videocardbenchmark.net/gpu.php?gpu=GeForce+RTX+5060&id=5602
- `hardware:3c9600f567cf` — PassMark Video Card Benchmarks — GeForce RTX 5060 Ti 16GB — https://www.videocardbenchmark.net/gpu.php?gpu=GeForce+RTX+5060+Ti+16GB&id=6160
- `hardware:4089384ecd15` — PassMark Video Card Benchmarks — GeForce RTX 5070 Ti — https://www.videocardbenchmark.net/gpu.php?gpu=GeForce+RTX+5070+Ti&id=5878
- `hardware:485542379b36` — PassMark CPU Benchmarks — Intel Core i5-8400 — https://www.cpubenchmark.net/cpu.php?cpu=Intel+Core+i5-8400&id=3097
- `hardware:497f54760950` — PassMark Intel Core i5-13400F Benchmark — CPU Mark 24891, Single 3628 — https://www.cpubenchmark.net/cpu.php?cpu=Intel+Core+i5-13400F&id=5166
- `hardware:509fd48b901b` — PassMark Video Card Benchmarks — GeForce RTX 3090 — https://www.videocardbenchmark.net/gpu.php?gpu=GeForce+RTX+3090&id=4284
- `hardware:549aac87930e` — PassMark - Radeon RX 550 - Price performance comparison — https://www.videocardbenchmark.net/gpu.php?gpu=Radeon+RX+550&id=3761
- `hardware:54a1d0ca2092` — PassMark Video Card Benchmarks — GeForce GTX 1660 — https://www.videocardbenchmark.net/gpu.php?gpu=GeForce+GTX+1660&id=4062
- `hardware:5530b216b0c2` — PassMark Video Card Benchmarks — Radeon RX 7800 XT — https://www.videocardbenchmark.net/gpu.php?gpu=Radeon+RX+7800+XT&id=4917
- `hardware:560fb8a216cf` — PassMark CPU Benchmarks — AMD Ryzen 7 3700X — https://www.cpubenchmark.net/cpu.php?cpu=AMD+Ryzen+7+3700X&id=3485
- `hardware:56cc05a182df` — PassMark AMD Ryzen 5 5600 Benchmark — CPU Mark 21494, Single 3253 — https://www.cpubenchmark.net/cpu.php?cpu=AMD+Ryzen+5+5600&id=4811
- `hardware:572e0cbae2d3` — PassMark - Intel HD 4600 - Price performance comparison — https://www.videocardbenchmark.net/gpu.php?gpu=Intel+HD+4600&id=2451
- `hardware:5837988cc683` — PassMark Video Card Benchmarks — GeForce RTX 4060 — https://www.videocardbenchmark.net/gpu.php?gpu=GeForce+RTX+4060&id=4850
- `hardware:5946562912cb` — PassMark Video Card Benchmarks — GeForce RTX 5080 — https://www.videocardbenchmark.net/gpu.php?gpu=GeForce+RTX+5080&id=5721
- `hardware:5a14b3ed7af2` — PassMark - GeForce GTX 750 Ti - Price performance comparison — https://www.videocardbenchmark.net/gpu.php?gpu=GeForce+GTX+750+Ti&id=2815
- `hardware:62699f3b35fb` — PassMark Video Card Benchmarks — GeForce GTX 1060 — https://www.videocardbenchmark.net/gpu.php?gpu=GeForce+GTX+1060&id=3548
- `hardware:67dc4c02a2fb` — PassMark CPU Benchmarks — AMD Ryzen 9 3900X — https://www.cpubenchmark.net/cpu.php?cpu=AMD+Ryzen+9+3900X&id=3493
- `hardware:67de7e601b40` — PassMark - GeForce RTX 2080 Ti - Price performance comparison — https://www.videocardbenchmark.net/gpu.php?gpu=GeForce+RTX+2080+Ti&id=3991
- `hardware:6aa408b0f708` — PassMark Intel Core i7-12700H Benchmark — CPU Mark 24995, Single 3484 — https://www.cpubenchmark.net/cpu.php?cpu=Intel+Core+i7-12700H&id=4721
- `hardware:6d9377fa7453` — PassMark Video Card Benchmarks — GeForce RTX 4050 Laptop GPU — https://www.videocardbenchmark.net/gpu.php?gpu=GeForce+RTX+4050+Laptop+GPU&id=4763
- `hardware:6f7108f11cd3` — PassMark Video Card Benchmarks — Radeon RX 470/570 — https://www.videocardbenchmark.net/gpu.php?gpu=Radeon+RX+470%2F570&id=3558
- `hardware:70abaad3db6f` — PassMark - GeForce GTX 970 - Price performance comparison — https://www.videocardbenchmark.net/gpu.php?gpu=GeForce+GTX+970&id=2954
- `hardware:70c608c01ca0` — PassMark Video Card Benchmarks — Radeon RX 9070 — https://www.videocardbenchmark.net/gpu.php?gpu=Radeon+RX+9070&id=5958
- `hardware:7591010c1bc0` — PassMark CPU Benchmarks — Intel Core i9-14900K — https://www.cpubenchmark.net/cpu.php?cpu=Intel+Core+i9-14900K&id=5717
- `hardware:77f7921c463e` — PassMark CPU Benchmarks — AMD Ryzen 7 7700X — https://www.cpubenchmark.net/cpu.php?cpu=AMD+Ryzen+7+7700X&id=5036
- `hardware:7888397167eb` — PassMark Video Card Benchmarks — GeForce RTX 5090 — https://www.videocardbenchmark.net/gpu.php?gpu=GeForce+RTX+5090&id=5725
- `hardware:79f489f9e9ec` — PassMark CPU Benchmarks — Intel Core i7-8700K — https://www.cpubenchmark.net/cpu.php?cpu=Intel+Core+i7-8700K&id=3098
- `hardware:7e2d8d5bf5f3` — PassMark Intel Core i5-14400F Benchmark — CPU Mark 25440, Single 3700 — https://www.cpubenchmark.net/cpu.php?cpu=Intel+Core+i5-14400F&id=5837
- `hardware:81c4287af43b` — PassMark - Intel Iris Xe - Price performance comparison — https://www.videocardbenchmark.net/gpu.php?gpu=Intel+Iris+Xe&id=4265
- `hardware:836a9fba84c4` — PassMark CPU Benchmarks — AMD Ryzen 9 7900X — https://www.cpubenchmark.net/cpu.php?cpu=AMD+Ryzen+9+7900X&id=5027
- `hardware:840ef9ea050b` — PassMark - GeForce GT 730 - Price performance comparison — https://www.videocardbenchmark.net/gpu.php?gpu=GeForce+GT+730&id=2906
- `hardware:848d487dc667` — PassMark AMD Custom APU 0932 (Steam Deck) Benchmark — CPU Mark 9411, Single 2214 — https://www.cpubenchmark.net/cpu.php?cpu=AMD+Custom+APU+0932&id=6154
- `hardware:8660240c2073` — PassMark Video Card Benchmarks — GeForce RTX 4090 — https://www.videocardbenchmark.net/gpu.php?gpu=GeForce+RTX+4090&id=4606
- `hardware:890bf8c8bc53` — PassMark Video Card Benchmarks — Radeon RX 6800 XT — https://www.videocardbenchmark.net/gpu.php?gpu=Radeon+RX+6800+XT&id=4312
- `hardware:89cbc8278eca` — PassMark CPU Benchmarks — AMD Ryzen 5 5600X — https://www.cpubenchmark.net/cpu.php?cpu=AMD+Ryzen+5+5600X&id=3859
- `hardware:8ab47fd159d4` — PassMark CPU Benchmarks — Intel Core i9-12900K — https://www.cpubenchmark.net/cpu.php?cpu=Intel+Core+i9-12900K&id=4597
- `hardware:8bacc05d7fc8` — PassMark Video Card Benchmarks — GeForce RTX 4070 — https://www.videocardbenchmark.net/gpu.php?gpu=GeForce+RTX+4070&id=4795
- `hardware:8d936bf26c17` — PassMark Video Card Benchmarks — GeForce RTX 5070 Ti Laptop GPU — https://www.videocardbenchmark.net/gpu.php?gpu=GeForce+RTX+5070+Ti+Laptop+GPU&id=6216
- `hardware:8e7744a9be93` — PassMark CPU Benchmarks — AMD Ryzen 9 7950X — https://www.cpubenchmark.net/cpu.php?cpu=AMD+Ryzen+9+7950X&id=5031
- `hardware:93986f7bde58` — PassMark Video Card Benchmarks — GeForce RTX 3060 — https://www.videocardbenchmark.net/gpu.php?gpu=GeForce+RTX+3060&id=6498
- `hardware:9a24b670ca22` — PassMark - Intel HD Graphics 620 - Price performance comparison — https://www.videocardbenchmark.net/gpu.php?gpu=Intel+HD+Graphics+620&id=3592
- `hardware:9b457cb5c826` — PassMark CPU Benchmarks — AMD Ryzen 7 5800X3D — https://www.cpubenchmark.net/cpu.php?cpu=AMD+Ryzen+7+5800X3D&id=4823
- `hardware:9b567a14b843` — PassMark Video Card Benchmarks — GeForce RTX 2050 — https://www.videocardbenchmark.net/gpu.php?gpu=GeForce+RTX+2050&id=4501
- `hardware:9b7841f454f7` — PassMark AMD Ryzen 7 9800X3D Benchmark — CPU Mark 39927, Single 4421 — https://www.cpubenchmark.net/cpu.php?cpu=AMD+Ryzen+7+9800X3D&id=6344
- `hardware:9c5901396f3d` — PassMark Video Card Benchmarks — GeForce GTX 1660 SUPER — https://www.videocardbenchmark.net/gpu.php?gpu=GeForce+GTX+1660+SUPER&id=4159
- `hardware:9f4761331ae8` — PassMark Video Card Benchmarks — GeForce RTX 5070 Laptop GPU — https://www.videocardbenchmark.net/gpu.php?gpu=GeForce+RTX+5070+Laptop+GPU&id=6260
- `hardware:9fd08f6b5c8a` — PassMark AMD Ryzen 7 8745H Benchmark — CPU Mark 29058, Single 3675 — https://www.cpubenchmark.net/cpu.php?cpu=AMD+Ryzen+7+8745H&id=6289
- `hardware:a195c699bec6` — PassMark CPU Benchmarks — Intel Core i5-9400F — https://www.cpubenchmark.net/cpu.php?cpu=Intel+Core+i5-9400F&id=3397
- `hardware:a3ccb503c8b3` — PassMark CPU Benchmarks — Intel Core i9-13900K — https://www.cpubenchmark.net/cpu.php?cpu=Intel+Core+i9-13900K&id=5022
- `hardware:a4f5c1213fb9` — PassMark - Intel HD 520 - Price performance comparison — https://www.videocardbenchmark.net/gpu.php?gpu=Intel+HD+520&id=3255
- `hardware:a565eaa9a35f` — PassMark CPU Benchmarks — Intel Core i7-12700K — https://www.cpubenchmark.net/cpu.php?cpu=Intel+Core+i7-12700K&id=4609
- `hardware:a9dda230b9dd` — PassMark CPU Benchmarks — AMD Ryzen 5 2600 — https://www.cpubenchmark.net/cpu.php?cpu=AMD+Ryzen+5+2600&id=3243
- `hardware:a9f7d96a856b` — PassMark - GeForce GTX 960 - Price performance comparison — https://www.videocardbenchmark.net/gpu.php?gpu=GeForce+GTX+960&id=3114
- `hardware:ab9c0bf794b3` — PassMark Video Card Benchmarks — GeForce RTX 3050 Laptop GPU — https://www.videocardbenchmark.net/gpu.php?gpu=GeForce+RTX+3050+Laptop+GPU&id=6486
- `hardware:ae2fbdf7314d` — PassMark Video Card Benchmarks — Radeon RX 7900 XTX — https://www.videocardbenchmark.net/gpu.php?gpu=Radeon+RX+7900+XTX&id=4644
- `hardware:b01112378bcb` — PassMark Video Card Benchmarks — GeForce RTX 5070 — https://www.videocardbenchmark.net/gpu.php?gpu=GeForce+RTX+5070&id=5940
- `hardware:b4f43214ca49` — PassMark - Radeon RX 6750 XT - Price performance comparison — https://www.videocardbenchmark.net/gpu.php?gpu=Radeon+RX+6750+XT&id=4543
- `hardware:b8eca4bb9b58` — PassMark Video Card Benchmarks — GeForce RTX 5060 Laptop GPU — https://www.videocardbenchmark.net/gpu.php?gpu=GeForce+RTX+5060+Laptop+GPU&id=6330
- `hardware:b95413f9cceb` — PassMark Video Card Benchmarks — Radeon RX 7600 — https://www.videocardbenchmark.net/gpu.php?gpu=Radeon+RX+7600&id=4832
- `hardware:bbbc1eae1809` — PassMark CPU Benchmarks — Intel Core i7-11700K — https://www.cpubenchmark.net/cpu.php?cpu=Intel+Core+i7-11700K&id=3896
- `hardware:bc7ca35ed973` — PassMark Video Card Benchmarks — Intel Arc A750 — https://www.videocardbenchmark.net/gpu.php?gpu=Intel+Arc+A750&id=4612
- `hardware:bcf37f7e5b92` — PassMark AMD Ryzen 7 5700X Benchmark — CPU Mark 26561, Single 3386 — https://www.cpubenchmark.net/cpu.php?cpu=AMD+Ryzen+7+5700X&id=4814
- `hardware:bf9c50614fe8` — PassMark - Radeon Vega 8 - Price performance comparison — https://www.videocardbenchmark.net/gpu.php?gpu=Radeon+Vega+8&id=3895
- `hardware:c04777fc31fd` — PassMark Video Card Benchmarks — Intel Arc A770 — https://www.videocardbenchmark.net/gpu.php?gpu=Intel+Arc+A770&id=4605
- `hardware:c430a7d5ed8e` — PassMark Video Card Benchmarks — Radeon RX 6600 — https://www.videocardbenchmark.net/gpu.php?gpu=Radeon+RX+6600&id=4465
- `hardware:c4f6951eccff` — PassMark AMD Ryzen 5 7600 Benchmark — CPU Mark 26975, Single 3908 — https://www.cpubenchmark.net/cpu.php?cpu=AMD+Ryzen+5+7600&id=5172
- `hardware:c6cc8afb6ebc` — PassMark CPU Benchmarks — Intel Core i5-13600K — https://www.cpubenchmark.net/cpu.php?cpu=Intel+Core+i5-13600K&id=5008
- `hardware:c7b836ca6f4e` — PassMark - GeForce GTX 1080 - Price performance comparison — https://www.videocardbenchmark.net/gpu.php?gpu=GeForce+GTX+1080&id=3502
- `hardware:c9938a31b45b` — PassMark Video Card Benchmarks — GeForce RTX 4080 — https://www.videocardbenchmark.net/gpu.php?gpu=GeForce+RTX+4080&id=4622
- `hardware:cd4a51d804a1` — PassMark Intel Core i7-7700 Benchmark — CPU Mark 8640, Single 2441 — https://www.cpubenchmark.net/cpu.php?cpu=Intel+Core+i7-7700+%40+3.60GHz&id=2905
- `hardware:ce50b64b1067` — PassMark Video Card Benchmarks — GeForce RTX 5050 — https://www.videocardbenchmark.net/gpu.php?gpu=GeForce+RTX+5050&id=6668
- `hardware:ceefabb71294` — PassMark - Intel UHD Graphics 620 - Price performance comparison — https://www.videocardbenchmark.net/gpu.php?gpu=Intel+UHD+Graphics+620&id=3805
- `hardware:d1496a7a3bae` — PassMark Video Card Benchmarks — Radeon RX 9060 XT 16GB — https://www.videocardbenchmark.net/gpu.php?gpu=Radeon+RX+9060+XT+16GB&id=5957
- `hardware:d1758b433170` — PassMark - GeForce GTX 1070 Ti - Price performance comparison — https://www.videocardbenchmark.net/gpu.php?gpu=GeForce+GTX+1070+Ti&id=3842
- `hardware:d23f22993b28` — PassMark Video Card Benchmarks — Radeon RX 6700 XT — https://www.videocardbenchmark.net/gpu.php?gpu=Radeon+RX+6700+XT&id=4369
- `hardware:d271088a60c5` — PassMark - GeForce GTX 1070 - Price performance comparison — https://www.videocardbenchmark.net/gpu.php?gpu=GeForce+GTX+1070&id=3521
- `hardware:d39e7ced2250` — PassMark CPU Benchmarks — AMD Ryzen 5 7600X — https://www.cpubenchmark.net/cpu.php?cpu=AMD+Ryzen+5+7600X&id=5033
- `hardware:d4075fe02279` — PassMark Intel Core i5-14600K Benchmark — CPU Mark 38402, Single 4267 — https://www.cpubenchmark.net/cpu.php?cpu=Intel+Core+i5-14600K&id=5720
- `hardware:d55d08a9d426` — PassMark AMD Ryzen 7 5700X3D Benchmark — CPU Mark 26302, Single 2968 — https://www.cpubenchmark.net/cpu.php?cpu=AMD+Ryzen+7+5700X3D&id=5884
- `hardware:d5b349a295a2` — PassMark Video Card Benchmarks — Radeon RX 5600 XT — https://www.videocardbenchmark.net/gpu.php?gpu=Radeon+RX+5600+XT&id=4186
- `hardware:d91278fcebd3` — PassMark AMD Ryzen 7 7800X3D Benchmark — CPU Mark 34277, Single 3759 — https://www.cpubenchmark.net/cpu.php?cpu=AMD+Ryzen+7+7800X3D&id=5299
- `hardware:de567ffb48ae` — PassMark Video Card Benchmarks — GeForce GTX 1080 Ti — https://www.videocardbenchmark.net/gpu.php?gpu=GeForce+GTX+1080+Ti&id=3699
- `hardware:df2b757155c9` — PassMark Intel Core i5-12600K Benchmark — CPU Mark 27512, Single 3917 — https://www.cpubenchmark.net/cpu.php?cpu=Intel+Core+i5-12600K&id=4603
- `hardware:e97887202ea5` — PassMark Video Card Benchmarks — Radeon RX 6500 XT — https://www.videocardbenchmark.net/gpu.php?gpu=Radeon+RX+6500+XT&id=4488
- `hardware:eb15eee5c39e` — PassMark CPU Benchmarks — Intel Core i5-12400F — https://www.cpubenchmark.net/cpu.php?cpu=Intel+Core+i5-12400F&id=4681
- `hardware:ed4189e76f39` — PassMark Video Card Benchmarks — GeForce RTX 3080 — https://www.videocardbenchmark.net/gpu.php?gpu=GeForce+RTX+3080&id=4282
- `hardware:ef05e429b7a4` — PassMark CPU Benchmarks — AMD Ryzen 3 3100 — https://www.cpubenchmark.net/cpu.php?cpu=AMD+Ryzen+3+3100&id=3715
- `hardware:ef3fed8afcb2` — PassMark Video Card Benchmarks — Radeon RX 6900 XT — https://www.videocardbenchmark.net/gpu.php?gpu=Radeon+RX+6900+XT&id=4322
- `hardware:f2d3732fd926` — PassMark Intel Core i7-14700K Benchmark — CPU Mark 51958, Single 4456 — https://www.cpubenchmark.net/cpu.php?cpu=Intel+Core+i7-14700K&id=5719
- `hardware:f3d9708ed9f4` — PassMark CPU Benchmarks — AMD Ryzen 5 1600 — https://www.cpubenchmark.net/cpu.php?cpu=AMD+Ryzen+5+1600&id=2984
- `hardware:f3e9327afe75` — PassMark CPU Benchmarks — Intel Core i3-8100 — https://www.cpubenchmark.net/cpu.php?cpu=Intel+Core+i3-8100&id=3103
- `hardware:f5e8e9acc2ec` — PassMark - Radeon RX 6800 - Price performance comparison — https://www.videocardbenchmark.net/gpu.php?gpu=Radeon+RX+6800&id=4314
- `hardware:f84c1215e206` — PassMark Video Card Benchmarks — Radeon RX 9070 XT — https://www.videocardbenchmark.net/gpu.php?gpu=Radeon+RX+9070+XT&id=5956
- `hardware:f991632d00d5` — PassMark Video Card Benchmarks — GeForce RTX 3050 Ti Laptop GPU — https://www.videocardbenchmark.net/gpu.php?gpu=GeForce+RTX+3050+Ti+Laptop+GPU&id=4393
- `hardware:fb999a0301a9` — PassMark Video Card Benchmarks — GeForce RTX 3060 Ti — https://www.videocardbenchmark.net/gpu.php?gpu=GeForce+RTX+3060+Ti&id=4318

Библиографические и иные носители могут добавляться без изменения схемы:
`source_type` — расширяемое поле, а обязательное требование к публикации задаётся
не видом носителя, а наличием проверяемого claim и локатора.
