# Матрица покрытия каталога и provenance

Снимок: `C:\Users\user\Desktop\game-inspect\backend\gamedev_dss.db`. Матрица создана генератором отчёта `f0ce995`.

Это аудит полноты полей, а не утверждение, что 124 метода уже прошли глубокую предметную рецензию. `yes` означает заполненное поле каталога; доказательность механизма/числа проверяется в EvidenceClaim.

## Методы

| Код | Функция | Вид | Источник | Confidence | Conditions | Engine filter | Platform filter | HW feature | Verification |
| --- | --- | --- | --- | ---: | --- | --- | --- | --- | --- |
| ai_director_pacing: Контроллер популяции NPC по интенсивности событий | advanced_npc_ai | implementation | [The AI Systems of Left 4 Dead — Michael Booth, Valve](https://cdn.akamai.steamstatic.com/apps/valve/2009/ai_systems_of_l4d_mike_booth.pdf) | 0.85 | yes | gap | gap | gap | Прогоны с одинаковым seed: активные NPC, пики спавна, CPU контроллера/ИИ и память. |
| behaviour_tree_update_budget: Деревья поведений с бюджетом обновления | advanced_npc_ai | implementation | [Behavior tree (artificial intelligence, robotics and control)](https://en.wikipedia.org/wiki/Behavior_tree_(artificial_intelligence,_robotics_and_control)) | 0.75 | yes | gap | gap | gap | Стресс-сцена: замер времени ИИ и задержки реакции NPC. |
| npc_perception_budget: Бюджет восприятия NPC | advanced_npc_ai | implementation | [Video game artificial intelligence](https://en.wikipedia.org/wiki/Video_game_artificial_intelligence) | 0.80 | yes | gap | gap | gap | Замер времени восприятия и задержки обнаружения на стресс-сцене. |
| flow_field_pathing: Поле направлений (flow field) | ai_pathfinding | implementation | [Crowd Pathfinding and Steering Using Flow Field Tiles — Elijah Emerson](https://www.gameaipro.com/GameAIPro/GameAIPro_Chapter23_Crowd_Pathfinding_and_Steering_Using_Flow_Field_Tiles.pdf) | 0.70 | yes | gap | gap | gap | Замер времени навигации при росте числа агентов. |
| navmesh_tiling_streaming: Тайловая навмеш со стримингом | ai_pathfinding | implementation | [Navigation mesh](https://en.wikipedia.org/wiki/Navigation_mesh) | 0.75 | yes | gap | gap | gap | Замер памяти на навигационные данные и времени пересборки тайла. |
| rvo_local_avoidance: Локальное избегание агентов (RVO/ORCA) | ai_pathfinding | implementation | [Optimal Reciprocal Collision Avoidance (van den Berg et al., UNC Gamma)](https://gamma.cs.unc.edu/ORCA/) | 0.85 | yes | gap | gap | gap | Стресс-сцена: время избегания на агента и отсутствие застреваний. |
| time_sliced_pathfinding: Поиск пути с распределением по кадрам | ai_pathfinding | optimization | [Navigation mesh](https://en.wikipedia.org/wiki/Navigation_mesh) | 0.85 | yes | gap | gap | gap | Замер максимального времени кадра при массовой постановке запросов. |
| art_direction_stylization: Стилизация вместо фотореализма | art_pipeline | optimization | [Unity — Managing GPU usage for PC and console games](https://unity.com/how-to/gpu-optimization) | 0.70 | yes | gap | gap | gap | Сравнение бюджета кадра стилизованной и реалистичной вертикали. |
| normal_bake_retopology_pipeline: Запекание нормалей и ретопология | art_pipeline | optimization | [Unity Manual: Optimizing Graphics Performance](https://docs.unity3d.com/Manual/OptimizingGraphicsPerformance.html) | 0.85 | yes | gap | gap | gap | Сравнение числа треугольников и времени кадра до и после. |
| audio_convolution_reverb: Свёрточная реверберация | audio_system | implementation | [Epic: Convolution Reverb](https://dev.epicgames.com/documentation/unreal-engine/convolution-reverb-in-unreal-engine) | 0.80 | yes | gap | gap | gap | Сравнить DSP-время, задержку и память при пике голосов. |
| audio_occlusion_propagation: Аудио-окклюзия лучами и HRTF | audio_system | optimization | [Hunt: Showdown — Audio readability, realism and consistency](https://www.huntshowdown.com/news/hunt-audio-readability-realism-and-consistency) | 0.80 | yes | gap | gap | gap | Отладочная отрисовка лучей и затухания; слепой тест слышимости. |
| audio_streaming_compression: Потоковое сжатие аудио | audio_system | optimization | [Hunt: Showdown — Audio readability, realism and consistency](https://www.huntshowdown.com/news/hunt-audio-readability-realism-and-consistency) | 0.80 | yes | gap | gap | gap | Вес аудиобанков и пики памяти на сценах с озвучкой. |
| gpu_lightmap_baking: GPU-ускоренный пересчёт освещения | baked_lighting | optimization | [Unity Manual: Progressive Lightmapper](https://docs.unity3d.com/Manual/progressive-lightmapper.html) | 0.85 | yes | gap | gap | gap | Замер времени пересчёта освещения эталонного уровня. |
| lightmap_2d_baking: Запекание 2D-освещения в текстуры | baked_lighting | implementation | [Unity Manual: Progressive Lightmapper](https://docs.unity3d.com/Manual/progressive-lightmapper.html) | 0.85 | yes | gap | gap | gap | Сравнение времени кадра до и после запекания на эталонном уровне. |
| lightmap_atlas_baking: Запекание освещения в лайтмапы | baked_lighting | implementation | [Lightmap](https://en.wikipedia.org/wiki/Lightmap) | 0.90 | yes | gap | gap | gap | Сравнение времени кадра рендера освещения до и после; контроль размера лайтмапов. |
| lightmap_compression_streaming: Сжатие и потоковая подкачка лайтмапов | baked_lighting | optimization | [Unreal Engine: Virtual Texturing](https://dev.epicgames.com/documentation/en-us/unreal-engine/virtual-texturing-in-unreal-engine) | 0.80 | yes | gap | gap | gap | Замер объёма VRAM и визуальная проверка градиентов освещения. |
| build_size_startup_budgets: Бюджеты размера сборки и старта | build_delivery | optimization | [Unity Manual: Addressables](https://docs.unity3d.com/Manual/com.unity.addressables.html) | 0.80 | yes | gap | gap | gap | Вес сборки по категориям и время холодного старта на min-spec. |
| differential_patch_pipeline: Дифференциальные патчи | build_delivery | optimization | [Unity Manual: Addressables](https://docs.unity3d.com/Manual/com.unity.addressables.html) | 0.75 | yes | gap | gap | gap | Размер патча типового хотфикса и время обновления на медленном канале. |
| animation_compression: Сжатие анимационных данных | character_animation | optimization | [Skinning](https://en.wikipedia.org/wiki/Skinning) | 0.85 | yes | gap | gap | gap | Сравнение объёма памяти и визуальная проверка анимаций. |
| animation_lod_budget: LOD анимации и бюджет обновлений | character_animation | optimization | [Unreal Engine: Animation Budget Allocator](https://dev.epicgames.com/documentation/en-us/unreal-engine/animation-budget-allocator-in-unreal-engine) | 0.85 | yes | gap | gap | gap | Замер времени анимации при заполненной сцене и визуальная оценка дальних NPC. |
| gpu_skinning_compute: Скиннинг на GPU | character_animation | implementation | [Skinning](https://en.wikipedia.org/wiki/Skinning) | 0.75 | yes | gap | gap | gap | Замер времени CPU на анимацию при максимальном числе персонажей. |
| motion_matching: Motion matching | character_animation | implementation | [Motion Matching in Unreal Engine](https://dev.epicgames.com/documentation/en-us/unreal-engine/motion-matching-in-unreal-engine) | 0.60 | yes | gap | gap | gap | Замер времени поиска и объёма памяти базы движений. |
| skeletal_2d_deform: Скелетная 2D-анимация вместо покадровой | character_animation | implementation | [Skinning](https://en.wikipedia.org/wiki/Skinning) | 0.80 | yes | gap | gap | gap | Сравнение занимаемой памяти и времени анимации на эталонной сцене. |
| sprite_atlas_batching: Атласы спрайтов и пакетная отрисовка | character_animation | implementation | [Texture atlas](https://en.wikipedia.org/wiki/Texture_atlas) | 0.90 | yes | gap | gap | gap | Замер числа вызовов отрисовки в профилировщике до и после упаковки. |
| sprite_sheet_compression: Сжатие листов спрайтов и мип-уровни | character_animation | optimization | [Mipmap](https://en.wikipedia.org/wiki/Mipmap) | 0.85 | yes | gap | gap | gap | Контроль занимаемой текстурной памяти в профилировщике и размера сборки. |
| cloth_baked_animation: Подготовленное движение ткани | cloth_simulation | implementation | [Unity 6: Cloth](https://docs.unity3d.com/6000.0/Documentation/Manual/class-Cloth.html) | 0.65 | yes | gap | gap | gap | Проверить переходы, память и контакт с окружением. |
| cloth_constraint_simulation: Ткань с ограничениями и коллизиями | cloth_simulation | implementation | [Unity 6: Cloth](https://docs.unity3d.com/6000.0/Documentation/Manual/class-Cloth.html) | 0.65 | yes | gap | gap | gap | Проверить быстрые движения, коллизии и группу персонажей. |
| agent_update_budget: Распределение бюджета обновлений агентов | crowd_simulation | optimization | [Unreal Engine: Significance Manager](https://dev.epicgames.com/documentation/en-us/unreal-engine/significance-manager-in-unreal-engine) | 0.85 | yes | gap | gap | gap | Замер времени обновления агентов и проверка реакции ближайших NPC. |
| crowd_2d_instancing: Массовая отрисовка 2D-агентов одним батчем | crowd_simulation | implementation | [Unity Manual: GPU Instancing](https://docs.unity3d.com/Manual/GPUInstancing.html) | 0.80 | yes | gap | gap | gap | Замер числа вызовов отрисовки и времени обновления на сцене с целевым числом агентов. |
| crowd_instancing_impostors: Инстансинг и импосторы для толпы | crowd_simulation | optimization | [Unreal Engine: Mass Entity](https://dev.epicgames.com/documentation/en-us/unreal-engine/mass-entity-in-unreal-engine) | 0.80 | yes | gap | gap | gap | Замер числа вызовов отрисовки и времени GPU при максимальной толпе. |
| ecs_data_oriented_crowd: Толпа на ECS / Data-Oriented архитектуре | crowd_simulation | implementation | [Entity component system](https://en.wikipedia.org/wiki/Entity_component_system) | 0.70 | yes | gap | gap | gap | Замер времени обновления агентов при росте их числа до целевого. |
| destruction_geometry_cache: Запечённые кэши разрушений | destruction_simulation | optimization | [Rendering the Hellscape of Doom Eternal (SIGGRAPH 2020)](https://advances.realtimerendering.com/s2020/RenderingDoomEternal.pdf) | 0.70 | yes | gap | gap | gap | Сравнение времени симуляции и воспроизведения; контроль размера кэша на диске. |
| runtime_fracture_budget: Разрушение с бюджетом активных обломков | destruction_simulation | implementation | [Epic: Destruction Overview](https://dev.epicgames.com/documentation/unreal-engine/destruction-overview?lang=en-US) | 0.70 | yes | gap | gap | gap | Проверить физику, навигацию, эффекты и сетевую синхронизацию. |
| hardware_raytraced_gi: Глобальное освещение на аппаратной трассировке лучей | dynamic_global_illumination | implementation | [Unreal Engine: Lumen Global Illumination and Reflections](https://dev.epicgames.com/documentation/en-us/unreal-engine/lumen-global-illumination-and-reflections-in-unreal-engine) | 0.80 | yes | gap | yes | yes | Замер времени GPU на RT-проход и проверка на минимальной поддерживаемой видеокарте. |
| irradiance_volume_probes: Зонды освещённости (irradiance volume) | dynamic_global_illumination | implementation | [Unity Manual: Light Probes](https://docs.unity3d.com/Manual/LightProbes.html) | 0.85 | yes | gap | gap | gap | Визуальная проверка на контрольных сценах и замер времени обновления зондов. |
| screen_space_gi: Экранное глобальное освещение (SSGI) | dynamic_global_illumination | optimization | [Ambient occlusion](https://en.wikipedia.org/wiki/Ambient_occlusion) | 0.80 | yes | gap | gap | gap | Визуальная оценка на краях экрана и замер времени GPU. |
| sdf_global_illumination: Глобальное освещение на дистанционных полях (SDF) | dynamic_global_illumination | implementation | [Signed distance function](https://en.wikipedia.org/wiki/Signed_distance_function) | 0.70 | yes | gap | gap | gap | Замер времени GPU на проход ГО и визуальная проверка стабильности. |
| temporal_radiance_cache: Кэш излучения с временным накоплением | dynamic_global_illumination | optimization | [Unreal Engine: Lumen Global Illumination and Reflections](https://dev.epicgames.com/documentation/en-us/unreal-engine/lumen-global-illumination-and-reflections-in-unreal-engine) | 0.65 | yes | gap | gap | gap | Замер времени GPU и проверка реакции на резкую смену освещения. |
| voxel_cone_tracing: Воксельный конусный трейсинг | dynamic_global_illumination | implementation | [Interactive Indirect Illumination Using Voxel Cone Tracing — Crassin et al.](https://research.nvidia.com/labs/rtr/publication/crassin2011givoxels/) | 0.60 | yes | gap | gap | gap | Замер времени вокселизации и трассировки, визуальная оценка артефактов. |
| dynamic_light_priority_budget: Приоритезация и бюджет динамических источников | dynamic_lighting | implementation | [Global illumination](https://en.wikipedia.org/wiki/Global_illumination) | 0.85 | yes | gap | gap | gap | Замер времени прохода освещения и проверка отсутствия вспышек. |
| light_range_attenuation_lod: Упрощение затухания источников по дистанции | dynamic_lighting | implementation | [Global illumination](https://en.wikipedia.org/wiki/Global_illumination) | 0.80 | yes | gap | gap | gap | Покадровое сравнение и замер стоимости освещения на эталонной сцене. |
| cascaded_shadow_maps: Каскадные карты теней | dynamic_shadows | implementation | [Shadow mapping](https://en.wikipedia.org/wiki/Shadow_mapping) | 0.90 | yes | gap | gap | gap | Замер времени рендера теней и визуальная оценка переходов каскадов. |
| distance_field_shadows: Тени на дистанционных полях (SDF) | dynamic_shadows | implementation | [Unreal Engine: Using Distance Field Shadows](https://dev.epicgames.com/documentation/unreal-engine/using-distance-field-shadows-in-unreal-engine?lang=en-US) | 0.70 | yes | gap | gap | gap | Замер памяти на поля и времени трассировки теней. |
| screen_space_contact_shadows: Контактные тени в экранном пространстве | dynamic_shadows | optimization | [Ambient occlusion](https://en.wikipedia.org/wiki/Ambient_occlusion) | 0.85 | yes | gap | gap | gap | Визуальная оценка контактов объектов и замер времени прохода. |
| shadow_caster_2d_limits: Ограничение 2D-отбрасывателей теней | dynamic_shadows | optimization | [Godot Docs: Lights and Shadows](https://docs.godotengine.org/en/stable/tutorials/3d/lights_and_shadows.html) | 0.80 | yes | gap | gap | gap | Замер времени кадра при максимальном числе источников на эталонной сцене. |
| static_shadow_caching: Кэширование теней от статических объектов | dynamic_shadows | optimization | [Unreal Engine: Virtual Shadow Maps](https://dev.epicgames.com/documentation/en-us/unreal-engine/virtual-shadow-maps-in-unreal-engine) | 0.80 | yes | gap | gap | gap | Замер времени рендера теней при неподвижной камере. |
| virtual_shadow_maps: Виртуальные карты теней (VSM) | dynamic_shadows | implementation | [Unreal Engine: Virtual Shadow Maps](https://dev.epicgames.com/documentation/en-us/unreal-engine/virtual-shadow-maps-in-unreal-engine) | 0.85 | yes | gap | gap | gap | Замер времени shadow-прохода, пиков VRAM и количества обновляемых страниц в сценах с разной плотностью геометрии и источников света. |
| ability_visual_effect_budget: Бюджет визуальных эффектов способностей | gameplay_ability_system | implementation | [Unreal Engine: Niagara Visual Effects](https://dev.epicgames.com/documentation/en-us/unreal-engine/niagara-visual-effects-in-unreal-engine) | 0.80 | yes | gap | gap | gap | Замер GPU и CPU в сцене с максимальным числом одновременных способностей. |
| data_driven_ability_system: Данные-ориентированная система способностей | gameplay_ability_system | implementation | [Game Programming Patterns: State](https://gameprogrammingpatterns.com/state.html) | 0.70 | yes | gap | gap | gap | Стресс-сцена с максимальным числом активных способностей: замер CPU. |
| mesh_index_optimization: Оптимизация индексов меша (vertex cache / overdraw) | geometry_pipeline | optimization | [meshoptimizer: mesh optimization library](https://github.com/zeux/meshoptimizer) | 0.80 | yes | gap | gap | gap | Метрики ACMR/ATVR через meshopt_analyze и замер времени кадра. |
| hair_cards_lod: Карточки волос и уровни детализации | hair_rendering | implementation | [Epic: Hair Rendering and Simulation](https://dev.epicgames.com/documentation/unreal-engine/hair-rendering-and-simulation-in-unreal-engine?lang=en-US) | 0.70 | yes | gap | gap | gap | Сравнить силуэт, overdraw и память с прядями. |
| hair_strand_simulation: Волосы из прядей с симуляцией | hair_rendering | implementation | [Epic: Hair Rendering and Simulation](https://dev.epicgames.com/documentation/unreal-engine/hair-rendering-and-simulation-in-unreal-engine?lang=en-US) | 0.70 | yes | gap | gap | gap | Замерить крупный план и группу персонажей. |
| heightmap_compression: Сжатие карт высот и материалов ландшафта | large_scale_terrain | optimization | [Mipmap](https://en.wikipedia.org/wiki/Mipmap) | 0.85 | yes | gap | gap | gap | Сравнение размера сборки и визуальное сравнение рельефа на контрольных участках. |
| neural_texture_compression: Нейросжатие текстур | large_scale_terrain | optimization | [NVIDIA RTX Neural Texture Compression (RTXNTC)](https://github.com/NVIDIA-RTX/Rtxntc) | 0.60 | yes | gap | gap | gap | Замер занятой видеопамяти и времени кадра на пилотном наборе. |
| terrain_clipmap: Клипмап / CDLOD ландшафта | large_scale_terrain | implementation | [Level of detail (computer graphics)](https://en.wikipedia.org/wiki/Level_of_detail_(computer_graphics)) | 0.75 | yes | gap | gap | gap | Замер времени рендера ландшафта при максимальной дальности обзора. |
| virtual_geometry_clusters: Виртуализированная геометрия (кластеризованный LOD) | large_scale_terrain | implementation | [Unreal Engine: Nanite Virtualized Geometry](https://dev.epicgames.com/documentation/en-us/unreal-engine/nanite-virtualized-geometry-in-unreal-engine) | 0.65 | yes | gap | yes | yes | Замер числа треугольников и времени рендера на эталонных кадрах. |
| virtual_texturing: Виртуальное текстурирование | large_scale_terrain | implementation | [Unreal Engine: Virtual Texturing](https://dev.epicgames.com/documentation/en-us/unreal-engine/virtual-texturing-in-unreal-engine) | 0.70 | yes | gap | gap | gap | Контроль объёма VRAM и отсутствия «замыленных» текстур при движении. |
| gpu_meshlet_culling_budget: Бюджет отсечения мешлетов на GPU | mesh_shaders | implementation | [DirectX mesh shader specification](https://microsoft.github.io/DirectX-Specs/d3d/MeshShader.html) | 0.70 | yes | gap | yes | gap | Замер числа выживших примитивов и времени геометрического прохода. |
| meshlet_pipeline_adoption: Конвейер мешлетов на меш-шейдерах | mesh_shaders | implementation | [DirectX mesh shader specification](https://microsoft.github.io/DirectX-Specs/d3d/MeshShader.html) | 0.60 | yes | gap | yes | yes | Замер времени подготовки кадра и геометрического прохода до и после. |
| client_prediction_reconciliation: Предсказание на клиенте и реконсиляция | multiplayer_netcode | implementation | [Client-side prediction](https://en.wikipedia.org/wiki/Client-side_prediction) | 0.75 | yes | gap | gap | gap | Тест с искусственной задержкой и потерями пакетов; контроль корректности коррекции. |
| delta_compression_state: Дельта-компрессия сетевого состояния | multiplayer_netcode | optimization | [Delta encoding](https://en.wikipedia.org/wiki/Delta_encoding) | 0.75 | yes | gap | gap | gap | Замер объёма трафика до и после внедрения. |
| deterministic_lockstep: Детерминированный lockstep | multiplayer_netcode | optimization | [Fix Your Timestep! (Gaffer on Games)](https://gafferongames.com/post/fix_your_timestep/) | 0.85 | yes | gap | gap | gap | Двойной прогон реплея с побайтовым сравнением; CRC каждого тика. |
| headless_dedicated_server: Выделенный сервер без графики | multiplayer_netcode | implementation | [Unreal Engine: Networking and Multiplayer](https://dev.epicgames.com/documentation/en-us/unreal-engine/networking-and-multiplayer-in-unreal-engine) | 0.80 | yes | gap | gap | gap | Замер потребления ресурсов сервером на целевом числе игроков. |
| lag_compensation_rewind: Серверная проверка попаданий по истории состояния | multiplayer_netcode | implementation | [Valve Source SDK — player_lagcompensation.cpp](https://github.com/ValveSoftware/source-sdk-2013/blob/master/src/game/server/player_lagcompensation.cpp) | 0.85 | yes | gap | gap | gap | Два клиента с разной задержкой: сверить историю коллизий, хитлог, память и серверное время обработки. |
| network_relevancy_priority: Сетевая релевантность и приоритизация | multiplayer_netcode | implementation | [Unreal Engine: Replication Graph](https://dev.epicgames.com/documentation/en-us/unreal-engine/replication-graph-in-unreal-engine) | 0.80 | yes | gap | gap | gap | Замер трафика и времени сетевого обновления при целевом числе игроков. |
| subtick_networking: Временные метки ввода внутри сетевого такта | multiplayer_netcode | implementation | [Counter-Strike 2 — sub-tick updates, Valve](https://www.counter-strike.net/cs2) | 0.80 | yes | gap | gap | gap | Сетевой стенд: ошибка времени события, задержка ответа, CPU очереди и байты команд при разных тактах. |
| tickrate_budgeting: Бюджетирование серверного тикрейта | multiplayer_netcode | optimization | [Valorant 128-tick servers (Riot Engineering)](https://www.riotgames.com/en/news/valorants-128-tick-servers) | 0.85 | yes | gap | gap | gap | Стабильность тика p50/p99, gunfire delay, packet loss по регионам. |
| async_loading_pipeline: Асинхронная загрузка без блокировки кадра | open_world_streaming | optimization | [Godot Docs: Using Multiple Threads](https://docs.godotengine.org/en/stable/tutorials/performance/using_multiple_threads.html) | 0.85 | yes | gap | gap | gap | Замер максимального времени кадра в сценарии быстрого перемещения. |
| baked_occlusion_culling: Запечённое отсечение по окклюзии | open_world_streaming | optimization | [Unity Manual: Occlusion Culling](https://docs.unity3d.com/Manual/OcclusionCulling.html) | 0.85 | yes | gap | gap | gap | Сравнение числа отрисованных объектов до и после запекания на контрольных точках. |
| directstorage_io: DirectStorage: очереди I/O и выбор декомпрессии | open_world_streaming | implementation | [Microsoft DirectStorage — Developer Guidance](https://github.com/microsoft/DirectStorage/blob/main/Docs/DeveloperGuidance.md) | 0.90 | yes | gap | yes | gap | GpuDecompressionBenchmark с проверкой данных и трасса игры: I/O latency, CPU, GPU queues, staging и пики кадра. |
| gpu_compute_culling: Отсечение объектов на GPU (compute) | open_world_streaming | optimization | [Unreal Engine: Nanite Virtualized Geometry](https://dev.epicgames.com/documentation/en-us/unreal-engine/nanite-virtualized-geometry-in-unreal-engine) | 0.75 | yes | gap | gap | yes | Сравнение времени CPU на отсечение и полного времени кадра. |
| hierarchical_lod: Иерархические LOD (HLOD) | open_world_streaming | optimization | [Unreal Engine: Hierarchical Level of Detail](https://dev.epicgames.com/documentation/en-us/unreal-engine/hierarchical-level-of-detail-in-unreal-engine) | 0.80 | yes | gap | gap | gap | Замер количества вызовов отрисовки и времени рендер-потока до и после. |
| tilemap_chunk_streaming: Чанковая подгрузка тайловой карты | open_world_streaming | implementation | [Unity Manual: Addressables](https://docs.unity3d.com/Manual/com.unity.addressables.html) | 0.85 | yes | gap | gap | gap | Профилирование пиков времени кадра при быстром перемещении по миру. |
| world_origin_shifting: Сдвиг начала координат (origin rebasing) | open_world_streaming | implementation | [Unreal Engine: Large World Coordinates](https://dev.epicgames.com/documentation/en-us/unreal-engine/large-world-coordinates-in-unreal-engine) | 0.80 | yes | gap | gap | gap | Тест на границе мира: контроль дрожания геометрии и стабильности коллизий. |
| world_partition_streaming: Разбиение мира на ячейки с потоковой загрузкой | open_world_streaming | implementation | [Unreal Engine: World Partition](https://dev.epicgames.com/documentation/en-us/unreal-engine/world-partition-in-unreal-engine) | 0.85 | yes | gap | gap | gap | Профилирование пиков времени кадра при быстром перемещении; контроль отсутствия кадров дольше бюджета на загрузку. |
| flipbook_particles: Flipbook-текстуры вместо симуляции | particle_systems | optimization | [Particle system](https://en.wikipedia.org/wiki/Particle_system) | 0.85 | yes | gap | gap | gap | Сравнение времени кадра и визуальная оценка эффекта. |
| gpu_particle_simulation: Симуляция частиц на GPU | particle_systems | implementation | [Unreal Engine: Niagara Visual Effects](https://dev.epicgames.com/documentation/en-us/unreal-engine/niagara-visual-effects-in-unreal-engine) | 0.85 | yes | gap | gap | yes | Замер времени CPU на обновление частиц и числа активных частиц. |
| particle_pooling: Пулинг систем частиц | particle_systems | optimization | [Object pool pattern](https://en.wikipedia.org/wiki/Object_pool_pattern) | 0.90 | yes | gap | gap | gap | Контроль отсутствия аллокаций в профилировщике во время эффектов. |
| sprite_particle_atlas: Атласные частицы со сниженной точностью | particle_systems | optimization | [Particle system](https://en.wikipedia.org/wiki/Particle_system) | 0.80 | yes | gap | gap | gap | Замер времени обновления частиц и числа вызовов отрисовки. |
| full_path_tracing_pipeline: Трассировка пути как основное освещение | path_tracing | implementation | [Path tracing](https://en.wikipedia.org/wiki/Path_tracing) | 0.70 | yes | gap | yes | yes | Замер времени RT-прохода и сравнение качества с растровым освещением. |
| path_tracing_sample_denoiser_budget: Бюджет выборок и денойзинг трассировки пути | path_tracing | implementation | [Path tracing](https://en.wikipedia.org/wiki/Path_tracing) | 0.75 | yes | gap | yes | yes | Замер времени прохода и оценка шума на статичной и динамичной сцене. |
| broadphase_spatial_partitioning: Оптимизация широкой фазы (BVH / spatial hash) | physics_simulation | optimization | [Bounding volume hierarchy](https://en.wikipedia.org/wiki/Bounding_volume_hierarchy) | 0.80 | yes | gap | gap | gap | Замер времени широкой фазы при росте числа тел. |
| collision_layer_matrix: Матрица слоёв коллизий | physics_simulation | optimization | [Godot Docs: Physics Introduction](https://docs.godotengine.org/en/stable/tutorials/physics/physics_introduction.html) | 0.90 | yes | gap | gap | gap | Замер времени широкой фазы и числа проверяемых пар в профилировщике. |
| fixed_timestep_physics: Фиксированный шаг физики с интерполяцией | physics_simulation | implementation | [Godot Docs: Physics Introduction](https://docs.godotengine.org/en/stable/tutorials/physics/physics_introduction.html) | 0.90 | yes | gap | gap | gap | Проверка воспроизводимости: одинаковая последовательность входов даёт одинаковый результат. |
| multithreaded_physics_jobs: Многопоточная физика на системе задач | physics_simulation | optimization | [Unity Manual: Job System](https://docs.unity3d.com/Manual/JobSystem.html) | 0.70 | yes | gap | gap | gap | Замер времени шага физики при разном числе задействованных потоков. |
| physics_lod_sleeping: LOD физики и спящие тела | physics_simulation | optimization | [Unreal Engine: Chaos Physics](https://dev.epicgames.com/documentation/en-us/unreal-engine/chaos-physics-in-unreal-engine) | 0.90 | yes | gap | gap | gap | Замер времени физики и проверка корректности пробуждения объектов. |
| portal_scene_capture_budget: Порталы через рендер в текстуру | portal_rendering | implementation | [Epic: Scene Capture](https://dev.epicgames.com/documentation/unreal-engine/BlueprintAPI/Rendering/SceneCapture/CaptureScene?lang=en-US) | 0.60 | yes | gap | gap | gap | Измерить CPU/GPU и render targets при входе в портал. |
| deferred_forward_plus_choice: Выбор архитектуры рендера (deferred / forward+) | post_processing | implementation | [Deferred shading](https://en.wikipedia.org/wiki/Deferred_shading) | 0.80 | yes | gap | gap | gap | Сравнительный тест двух архитектур на эталонной сцене с целевым числом источников. |
| depth_prepass_early_z: Предварительный проход глубины (early-Z) | post_processing | optimization | [Hidden-surface determination](https://en.wikipedia.org/wiki/Hidden-surface_determination) | 0.75 | yes | gap | gap | gap | Замер overdraw в режиме визуализации перерисовки. |
| dynamic_resolution_scaling: Динамическое разрешение рендера | post_processing | optimization | [Unity Manual: Quality Settings](https://docs.unity3d.com/Manual/class-QualitySettings.html) | 0.90 | yes | gap | gap | gap | Проверка удержания целевого FPS на минимальной конфигурации. |
| post_effect_selective: Выборочное применение экранных эффектов | post_processing | optimization | [Unity Manual: Quality Settings](https://docs.unity3d.com/Manual/class-QualitySettings.html) | 0.85 | yes | gap | gap | gap | Замер времени проходов постобработки в профилировщике GPU. |
| screenspace_light_shafts: Экранные световые валы (пост-процесс) | post_processing | implementation | [GPU Gems 3, Ch.13: Volumetric Light Scattering as a Post-Process (Mitchell)](https://developer.nvidia.com/gpugems/gpugems3/part-ii-light-and-shadows/chapter-13-volumetric-light-scattering-post-process) | 0.80 | yes | gap | gap | gap | Скриншот-тест и замер времени прохода до и после. |
| temporal_upscaling: Временное масштабирование изображения | post_processing | optimization | [FidelityFX Super Resolution](https://en.wikipedia.org/wiki/FidelityFX_Super_Resolution) | 0.90 | yes | gap | gap | gap | Сравнение времени GPU и визуальной резкости при разных коэффициентах масштабирования. |
| variable_rate_shading: Переменная частота затенения (VRS) | post_processing | optimization | [Variable Rate Shading | DirectX-Specs](https://microsoft.github.io/DirectX-Specs/d3d/VariableRateShading.html) | 0.65 | yes | gap | yes | yes | Замер времени GPU и визуальная проверка на границах зон. |
| chunked_procedural_terrain: Чанковая генерация процедурного ландшафта | procedural_terrain | implementation | [Procedural generation](https://en.wikipedia.org/wiki/Procedural_generation) | 0.85 | yes | gap | gap | gap | Профиль главного потока при движении и замер времени генерации чанка. |
| terrain_generation_streaming_budget: Бюджет генерации и кэш чанков | procedural_terrain | implementation | [Procedural generation](https://en.wikipedia.org/wiki/Procedural_generation) | 0.80 | yes | gap | gap | gap | Профиль кадра при движении на максимальной скорости и замер попаданий в кэш. |
| gpu_instancing_vegetation: GPU-инстансинг растительности | procedural_vegetation | implementation | [Unity Manual: GPU Instancing](https://docs.unity3d.com/Manual/GPUInstancing.html) | 0.90 | yes | gap | gap | gap | Замер количества вызовов отрисовки и времени CPU на рендер. |
| gpu_procedural_placement: Процедурное размещение на GPU | procedural_vegetation | implementation | [Unreal Engine: Instanced Static Mesh](https://dev.epicgames.com/documentation/en-us/unreal-engine/instanced-static-mesh-in-unreal-engine) | 0.70 | yes | gap | gap | yes | Замер времени генерации ячейки и объёма занимаемой памяти. |
| impostors_billboards: Импосторы и билборды для дальнего плана | procedural_vegetation | optimization | [Impostor (computer graphics)](https://en.wikipedia.org/wiki/Impostor_(computer_graphics)) | 0.85 | yes | gap | gap | gap | Замер времени GPU и визуальная оценка на дистанции переключения. |
| tilemap_layer_culling: Отсечение слоёв и чанков тайловой карты | procedural_vegetation | optimization | [Godot Docs: Optimizing 3D Performance](https://docs.godotengine.org/en/stable/tutorials/performance/optimizing_3d_performance.html) | 0.85 | yes | gap | gap | gap | Замер числа вызовов отрисовки и времени рендер-потока. |
| vegetation_atlas_lod: Атласы и запечённые LOD растительности | procedural_vegetation | optimization | [Texture atlas](https://en.wikipedia.org/wiki/Texture_atlas) | 0.85 | yes | gap | gap | gap | Замер числа смен состояния материалов и времени GPU. |
| composition_bootstrap_architecture: Композиционный каркас проекта | project_architecture | optimization | [Entity component system](https://en.wikipedia.org/wiki/Entity_component_system) | 0.70 | yes | gap | gap | gap | Время добавления контрольной механики и связность графа зависимостей. |
| rt_effect_resolution_budget: Половинное разрешение и кэш трассировочных эффектов | ray_traced_effects | implementation | [Ray tracing (graphics)](https://en.wikipedia.org/wiki/Ray_tracing_(graphics)) | 0.80 | yes | gap | yes | yes | Замер времени RT-эффектов до и после и проверка «смаза» на движении. |
| selective_ray_traced_effects: Выборочная трассировка отдельных эффектов | ray_traced_effects | implementation | [Ray tracing (graphics)](https://en.wikipedia.org/wiki/Ray_tracing_(graphics)) | 0.80 | yes | gap | yes | yes | Покадровое сравнение растрового и трассировочного варианта каждого эффекта. |
| quality_tier_scalability: Тиры качества и scalability-группы | render_scalability | optimization | [Unity Manual: Quality Settings](https://docs.unity3d.com/Manual/class-QualitySettings.html) | 0.90 | yes | gap | gap | gap | Прогон на трёх тирах устройств от 15 минут; frametime-гистограммы. |
| async_compute_overlap: Перекрытие графики и асинхронных вычислений GPU | rendering_architecture | implementation | [Khronos Vulkan Samples — Using async compute to saturate GPU](https://docs.vulkan.org/samples/latest/samples/performance/async_compute/README.html) | 0.80 | yes | gap | gap | gap | Одна сцена с async on/off: GPU timeline, p95/p99 кадра, задержка и validation layers. |
| bindless_uber_shaders: Bindless-ресурсы и uber-шейдеры | rendering_architecture | optimization | [Doom Eternal graphics study (Simon Coenen)](https://www.simoncoenen.com/blog/programming/graphics/DoomEternalStudy) | 0.70 | yes | gap | gap | yes | Подсчёт draws и state changes в захвате кадра; дескрипторная статистика. |
| hiz_software_occlusion: Программное отсечение по Hi-Z | rendering_architecture | optimization | [Hidden-surface determination](https://en.wikipedia.org/wiki/Hidden-surface_determination) | 0.75 | yes | gap | gap | gap | Сравнение overdraw и числа вызовов отрисовки до и после; захват кадра. |
| pso_precaching_warmup: Предкомпиляция и прогрев PSO | rendering_architecture | optimization | [Unity Manual: Optimizing Shader Load Time](https://docs.unity3d.com/6000.0/Documentation/Manual/shader-loading.html) | 0.85 | yes | gap | gap | gap | Hitch-детект при первом обходе мира; трассировка загрузки и компиляции. |
| srp_batcher_discipline: SRP Batcher и дисциплина материалов (URP/HDRP) | rendering_architecture | optimization | [Unity Manual: SRP Batcher](https://docs.unity3d.com/Manual/SRPBatcher.html) | 0.85 | yes | yes | gap | gap | Счётчик SetPass calls и время рендер-потока до и после. |
| tiled_clustered_light_culling: Тайловое и кластерное отсечение источников света | rendering_architecture | optimization | [Clustered Deferred and Forward Shading (Olsson, Billeter, Assarsson)](https://www.cse.chalmers.se/~uffe/clustered_shading_preprint.pdf) | 0.80 | yes | gap | gap | gap | Время прохода освещения при целевом числе источников. |
| managed_gc_alloc_budget: Нулевой бюджет аллокаций в горячем цикле | runtime_memory | optimization | [Unity Manual: Garbage collection best practices](https://docs.unity3d.com/2023.1/Documentation/Manual/performance-garbage-collection-best-practices.html) | 0.80 | yes | yes | gap | gap | Колонка GC.Alloc профилировщика: 0 байт на кадр; отсутствие пиков GC.Collect. |
| runtime_security_budget: Интеграция проверок с отдельным бюджетом | runtime_security | implementation | [Epic: Anti-Cheat Interfaces](https://dev.epicgames.com/docs/epic-online-services/trust-and-safety/anti-cheat-interfaces) | 0.60 | yes | gap | gap | gap | Замерить запуск, CPU, память и сеть с включёнными проверками и без них. |
| async_incremental_saves: Асинхронные инкрементальные автосейвы | save_system | implementation | [Save Systems & Persistence (Andrews Notebook)](https://andrewaltimit.github.io/Documentation/docs/gamedev/save-systems.html) | 0.80 | yes | gap | gap | gap | Профайлинг кадра в момент автосейва; краш-тест записи и восстановление. |
| snapshot_slot_saves: Слотовые снапшоты мира (синхронная запись) | save_system | implementation | [Unreal Engine: Saving and Loading Your Game](https://docs.unrealengine.com/4.27/en-US/InteractiveExperiences/SaveGame/) | 0.85 | yes | gap | gap | gap | Замер фриза записи и размера файла; загрузка сейва прошлой версии. |
| splitscreen_render_budget: Бюджетирование split-screen | split_screen_rendering | optimization | [It Takes Two tech analysis (Digital Foundry)](https://www.digitalfoundry.net/articles/digitalfoundry-2021-it-takes-two-tech-analysis) | 0.80 | yes | gap | gap | gap | Замер thread-bound и времени кадра на каждый вьюпорт отдельно. |
| ml_frame_generation: ML-генерация кадров | upscaling_frame_generation | optimization | [Deep learning super sampling](https://en.wikipedia.org/wiki/Deep_learning_super_sampling) | 0.75 | yes | gap | gap | gap | ICAT-сравнение и FrameView-замер задержки; slowed-video на shimmer. |
| raycast_vehicle_physics: Физика транспорта на рейкастах подвески | vehicle_simulation | implementation | [Vehicle dynamics](https://en.wikipedia.org/wiki/Vehicle_dynamics) | 0.80 | yes | gap | gap | gap | Замер времени физического такта при максимальном числе единиц транспорта. |
| vehicle_simulation_lod: Уровни детализации симуляции транспорта | vehicle_simulation | implementation | [Vehicle dynamics](https://en.wikipedia.org/wiki/Vehicle_dynamics) | 0.80 | yes | gap | gap | gap | Замер времени физического такта и проверка плавности переходов. |
| froxel_volumetric_fog: Объёмный туман на froxel-сетке | volumetric_effects | implementation | [Volumetric rendering](https://en.wikipedia.org/wiki/Volumetric_rendering) | 0.75 | yes | gap | gap | gap | Замер времени прохода объёмов при разном разрешении сетки. |
| volumetric_half_resolution: Расчёт объёмов в пониженном разрешении | volumetric_effects | optimization | [Volumetric rendering](https://en.wikipedia.org/wiki/Volumetric_rendering) | 0.90 | yes | gap | gap | gap | Замер времени GPU и сравнение качества при разном разрешении. |
| gerstner_fft_water: Волны Герстнера и FFT на GPU | water_simulation | implementation | [Gerstner wave](https://en.wikipedia.org/wiki/Gerstner_wave) | 0.75 | yes | gap | gap | yes | Замер времени расчёта и обновления поверхности воды. |
| planar_reflection_budget: Бюджет плоских отражений | water_simulation | optimization | [Unreal Engine: Lumen Global Illumination and Reflections](https://dev.epicgames.com/documentation/en-us/unreal-engine/lumen-global-illumination-and-reflections-in-unreal-engine) | 0.80 | yes | gap | gap | gap | Замер времени кадра с отражениями и без на контрольной точке. |
| screen_space_water_simple: Упрощённая вода в экранном пространстве | water_simulation | implementation | [Gerstner wave](https://en.wikipedia.org/wiki/Gerstner_wave) | 0.85 | yes | gap | gap | gap | Замер времени рендера воды и визуальная оценка. |

## Связи метод-инструмент

| Метод | Tool | Relation | Own source URL | Note |
| --- | --- | --- | --- | --- |
| ability_visual_effect_budget | c_manual | alternative | gap | Бюджет эффектов реализуется кодом проекта. |
| ability_visual_effect_budget | g_gpu_particles | partial | yes | Лимиты частиц задаются настройками систем частиц. |
| ability_visual_effect_budget | u_vfxgraph | partial | yes | Лимиты и приоритеты эффектов настраиваются в VFX Graph. |
| ability_visual_effect_budget | ue_niagara | partial | yes | Niagara Significance и масштабируемость ограничивают эффекты. |
| agent_update_budget | c_job_system | alternative | gap | Собственный планировщик приоритетов. |
| agent_update_budget | g_visibility | partial | yes | Ручное управление обновлением. |
| agent_update_budget | u_quality | partial | yes | Требуется собственная реализация приоритизации. |
| agent_update_budget | ue_significance | direct | yes | Significance Manager распределяет бюджет. |
| animation_compression | c_manual | missing | gap | Реализуется полностью самостоятельно. |
| animation_compression | g_mesh_lod | partial | yes | Ограниченные настройки. |
| animation_compression | u_quality | direct | yes | Настройки сжатия в импортере анимаций. |
| animation_compression | ue_lod | direct | yes | Настройки сжатия анимаций в редакторе. |
| animation_lod_budget | c_job_system | alternative | gap | Собственное распределение бюджета. |
| animation_lod_budget | g_visibility | partial | yes | Ручное управление через слои и видимость. |
| animation_lod_budget | u_quality | partial | yes | Требуется собственная реализация. |
| animation_lod_budget | ue_anim_budget | direct | yes | Animation Budget Allocator. |
| art_direction_stylization | c_manual | partial | gap | Стиль полностью в руках команды. |
| art_direction_stylization | g_visibility | partial | yes | Стиль держится дистанциями и ручным светом. |
| art_direction_stylization | u_srp | partial | yes | Стиль собирается настройками URP/HDRP и шейдерами. |
| art_direction_stylization | ue_lumen | missing | yes | Стиль задаётся артом, а не движком; Lumen подстраивается под него. |
| async_incremental_saves | c_profiler | diagnostic | gap | Замер фриза автосейва через Tracy. |
| async_incremental_saves | g_profiler | diagnostic | yes | Замер фриза автосейва в профилировщике. |
| async_incremental_saves | u_profiler | diagnostic | yes | Замер фриза автосейва в Profiler. |
| async_incremental_saves | ue_insights | diagnostic | yes | Замер фриза автосейва в Insights. |
| async_loading_pipeline | c_streaming | missing | gap | Требуется собственный конвейер загрузки. |
| async_loading_pipeline | ce_merged | partial | yes | Стриминг через merged-группы и LOD-дистанции. |
| async_loading_pipeline | g_bg_loading | direct | yes | ResourceLoader.load_threaded в отдельном потоке. |
| async_loading_pipeline | h_instancing | alternative | yes | Вместо бесшовного стриминга — инстансинг планет. |
| async_loading_pipeline | s_vphysics | missing | yes | Конвейера стриминга нет: BSP-хабы грузятся целиком. |
| async_loading_pipeline | u_addressables | direct | yes | Асинхронная загрузка через Addressables. |
| async_loading_pipeline | ue_world_partition | automation | yes | Стриминг ячеек из коробки. |
| audio_occlusion_propagation | c_manual | missing | gap | Аудио-трассировка пишется самостоятельно. |
| audio_occlusion_propagation | ce_audio | direct | yes | Трассировка слышимости по геометрии и HRTF. |
| audio_occlusion_propagation | g_physics_server | missing | yes | Лучи только для физики, не для звука. |
| audio_occlusion_propagation | h_hsl | missing | yes | Считается скриптами, не движком. |
| audio_occlusion_propagation | s_vphysics | missing | yes | Звуковой окклюзии нет. |
| audio_occlusion_propagation | ue_chaos | missing | yes | Аудио-окклюзии нет — Chaos только физика. |
| audio_streaming_compression | c_manual | partial | gap | Ogg/Opus-стриминг пишется самостоятельно. |
| audio_streaming_compression | g_bg_loading | partial | yes | Аудиопотоки через фоновый загрузчик. |
| audio_streaming_compression | u_addressables | partial | yes | Аудиобанки в Addressables со стримингом. |
| audio_streaming_compression | ue_insights | diagnostic | yes | Контроль памяти аудиобанков через Insights. |
| baked_occlusion_culling | c_manual | missing | gap | Реализуется полностью самостоятельно. |
| baked_occlusion_culling | g_occluder | direct | yes | Окклюдеры расставляются вручную в редакторе. |
| baked_occlusion_culling | u_occlusion | direct | yes | Встроенная система запечённой окклюзии с порталами. |
| baked_occlusion_culling | ue_hlod | partial | yes | Используется предпросчитанная видимость и HLOD. |
| behaviour_tree_update_budget | c_ecs | alternative | gap | Деревья или автоматы поверх собственного ECS. |
| behaviour_tree_update_budget | g_navigation | partial | yes | Поведение на узлах и скриптах, бюджет обновления — кодом. |
| behaviour_tree_update_budget | u_navmesh | partial | yes | Поведение собирается из NavMeshComponents и собственных стейт-машин. |
| behaviour_tree_update_budget | ue_behavior_tree | direct | yes | Деревья поведений с настройкой интервалов обновления. |
| bindless_uber_shaders | c_render_graph | direct | gap | Bindless-дескрипторы в собственном графе. |
| bindless_uber_shaders | g_multimesh | missing | yes | Bindless нет, только MultiMesh. |
| bindless_uber_shaders | s_vulkan | partial | yes | Vulkan-бэкенд с дескрипторами. |
| bindless_uber_shaders | u_srp_batcher | partial | yes | SRP Batcher режет смены состояний. |
| bindless_uber_shaders | ue_nanite | alternative | yes | Nanite решает мерж иначе — кластерами. |
| broadphase_spatial_partitioning | c_ecs | alternative | gap | Собственная структура в ECS. |
| broadphase_spatial_partitioning | g_physics_server | automation | yes | Реализовано внутри PhysicsServer3D. |
| broadphase_spatial_partitioning | s_vphysics | partial | yes | Широкая фаза внутри VPhysics, без отдельного API. |
| broadphase_spatial_partitioning | u_dots | automation | yes | Реализовано внутри Unity Physics. |
| broadphase_spatial_partitioning | ue_chaos | automation | yes | Реализовано внутри Chaos. |
| build_size_startup_budgets | c_streaming | partial | gap | Бюджеты размера в собственном стриминге. |
| build_size_startup_budgets | g_bg_loading | partial | yes | Фоновая загрузка смягчает старт, бюджеты — вручную. |
| build_size_startup_budgets | u_addressables | direct | yes | Группы Addressables и бюджеты размера. |
| build_size_startup_budgets | ue_insights | diagnostic | yes | Аудит размера и времени старта через Insights. |
| cascaded_shadow_maps | c_render_graph | alternative | gap | Проход теней в собственном графе рендера. |
| cascaded_shadow_maps | ce_svogi | partial | yes | Каскады есть, дальний план закрывает воксельное затенение. |
| cascaded_shadow_maps | g_shadows | direct | yes | PSSM-каскады в настройках DirectionalLight3D. |
| cascaded_shadow_maps | u_quality | direct | yes | Настройка каскадов в Quality Settings. |
| cascaded_shadow_maps | ue_vsm | alternative | yes | Virtual Shadow Maps заменяют каскады. |
| chunked_procedural_terrain | c_streaming | alternative | gap | Собственная подсистема стриминга и генерации чанков. |
| chunked_procedural_terrain | g_bg_loading | partial | yes | Чанки грузятся фоновым загрузчиком, генератор — кодом. |
| chunked_procedural_terrain | u_addressables | partial | yes | Чанки как отдельные сцены и адресуемые ресурсы. |
| chunked_procedural_terrain | ue_world_partition | partial | yes | World Partition даёт чанки, но генератор пишется самостоятельно. |
| client_prediction_reconciliation | c_manual | missing | gap | Реализуется полностью самостоятельно. |
| client_prediction_reconciliation | g_multiplayer | partial | yes | Базовый API, предсказание реализуется вручную. |
| client_prediction_reconciliation | h_cloud | partial | yes | Предикт поверх авторитетного HeroCloud-сервера. |
| client_prediction_reconciliation | s_netcode | direct | yes | Предикт, интерполяция и компенсация задержек; в CS2 — sub-tick. |
| client_prediction_reconciliation | u_netcode | direct | yes | Предсказание в Netcode for Entities. |
| client_prediction_reconciliation | ue_networking | direct | yes | CharacterMovementComponent с предсказанием и реконсиляцией. |
| collision_layer_matrix | c_manual | missing | gap | Реализуется полностью самостоятельно. |
| collision_layer_matrix | g_physics_server | direct | yes | Слои и маски коллизий PhysicsServer. |
| collision_layer_matrix | u_quality | direct | yes | Матрица столкновений слоёв в настройках физики. |
| collision_layer_matrix | ue_chaos | direct | yes | Настройка профилей коллизий Chaos. |
| composition_bootstrap_architecture | c_ecs | direct | gap | Собственный ECS и DI-контейнер. |
| composition_bootstrap_architecture | g_threads | partial | yes | Сервисы на автозагрузке и пуле потоков. |
| composition_bootstrap_architecture | u_dots | partial | yes | Entities и субсцены как каркас, сервисы — кодом. |
| composition_bootstrap_architecture | ue_mass | partial | yes | MassEntity задаёт ECS-каркас, сервисы и DI — кодом. |
| crowd_2d_instancing | c_render_graph | alternative | gap | Реализуется в собственном графе рендера. |
| crowd_2d_instancing | g_multimesh | direct | yes | MultiMeshInstance2D для массовой отрисовки. |
| crowd_2d_instancing | u_instancing | direct | yes | GPU Instancing и BatchRendererGroup для 2D. |
| crowd_2d_instancing | ue_ism | partial | yes | Инстансинг применим к 2D-спрайтам с ограничениями. |
| crowd_instancing_impostors | c_render_graph | alternative | gap | Инстансинг в собственном графе рендера. |
| crowd_instancing_impostors | g_multimesh | direct | yes | MultiMeshInstance3D для толпы. |
| crowd_instancing_impostors | u_instancing | direct | yes | GPU Instancing персонажей толпы. |
| crowd_instancing_impostors | ue_mass | complement | yes | Используется вместе с Mass Entity. |
| data_driven_ability_system | c_ecs | alternative | gap | Система способностей поверх собственного ECS. |
| data_driven_ability_system | g_visibility | missing | yes | Готовой системы способностей нет, собирается из узлов и ресурсов. |
| data_driven_ability_system | u_dots | partial | yes | ECS-каркас задаёт данные-ориентированную основу, система способностей — кодом. |
| data_driven_ability_system | ue_gas | direct | yes | Gameplay Ability System: атрибуты, эффекты, теги и кулдауны из данных. |
| deferred_forward_plus_choice | c_render_graph | direct | gap | Архитектура определяется графом рендера. |
| deferred_forward_plus_choice | g_gi | direct | yes | Конвейер Godot 4 — forward+, выбирается настройками. |
| deferred_forward_plus_choice | u_srp | direct | yes | Выбор между URP (forward+) и HDRP (deferred). |
| deferred_forward_plus_choice | ue_lumen | direct | yes | Отложенное затенение используется по умолчанию. |
| delta_compression_state | c_manual | missing | gap | Реализуется полностью самостоятельно. |
| delta_compression_state | g_multiplayer | partial | yes | Требуется собственная реализация. |
| delta_compression_state | s_netcode | partial | yes | Дельта-снапшоты и сжатие состояния в тиках. |
| delta_compression_state | u_netcode | direct | yes | Встроенная дельта-компрессия. |
| delta_compression_state | ue_replication_graph | complement | yes | Дополняет граф репликации. |
| depth_prepass_early_z | c_render_graph | direct | gap | Проход глубины в собственном графе рендера. |
| depth_prepass_early_z | g_occluder | partial | yes | Прямого управления порядком меньше, чем в коммерческих движках. |
| depth_prepass_early_z | u_srp | direct | yes | Настраивается в URP и HDRP как depth prepass. |
| depth_prepass_early_z | ue_nanite | automation | yes | Nanite автоматически формирует проход глубины. |
| destruction_geometry_cache | c_streaming | partial | gap | Кэши идут общим конвейером стриминга. |
| destruction_geometry_cache | g_bg_loading | partial | yes | Кэши подгружаются фоновым загрузчиком. |
| destruction_geometry_cache | u_addressables | partial | yes | Кэши стримятся бандлами. |
| destruction_geometry_cache | ue_chaos | alternative | yes | Chaos — realtime-фрактура вместо запечённого playback. |
| deterministic_lockstep | c_manual | missing | gap | Фикс-точка и RNG пишутся самостоятельно. |
| deterministic_lockstep | g_multiplayer | partial | yes | Детерминизм собирается вручную поверх API. |
| deterministic_lockstep | h_cloud | alternative | yes | Авторитетный сим вместо lockstep. |
| deterministic_lockstep | s_netcode | alternative | yes | Valve-модель — снапшоты и предикт, а не lockstep. |
| deterministic_lockstep | u_netcode | partial | yes | Netcode for Entities ближе к детерминизму. |
| differential_patch_pipeline | c_streaming | partial | gap | Дифф-патчи поверх собственного стриминга. |
| differential_patch_pipeline | g_bg_loading | partial | yes | Докачка ресурсов фоновым загрузчиком. |
| differential_patch_pipeline | u_addressables | direct | yes | Content Update: дифференциальные бандлы. |
| differential_patch_pipeline | ue_insights | diagnostic | yes | Контроль размера чанков пакетов. |
| distance_field_shadows | c_manual | missing | gap | Реализуется полностью самостоятельно. |
| distance_field_shadows | g_shadows | partial | yes | Частично реализуется через SDFGI. |
| distance_field_shadows | u_srp | limited | yes | Ограниченная поддержка в HDRP. |
| distance_field_shadows | ue_vsm | direct | yes | Virtual Shadow Maps и дистанционные поля. |
| dynamic_light_priority_budget | c_manual | alternative | gap | Приоритезация источников реализуется кодом проекта. |
| dynamic_light_priority_budget | g_visibility | partial | yes | Приоритет задаётся дистанциями и слоями видимости вручную. |
| dynamic_light_priority_budget | u_quality | partial | yes | Число пиксельных источников задаётся настройками качества. |
| dynamic_light_priority_budget | ue_significance | direct | yes | Significance Manager задаёт приоритет объектов и источников. |
| dynamic_resolution_scaling | c_render_graph | alternative | gap | Собственное управление разрешением. |
| dynamic_resolution_scaling | g_profiler | direct | yes | Масштабирование viewport с контролем через профилировщик. |
| dynamic_resolution_scaling | u_quality | direct | yes | Dynamic Resolution в URP/HDRP. |
| dynamic_resolution_scaling | ue_insights | diagnostic | yes | Unreal Insights помогает подобрать пороги. |
| ecs_data_oriented_crowd | c_ecs | alternative | gap | Собственный ECS. |
| ecs_data_oriented_crowd | g_threads | partial | yes | Можно распараллелить через WorkerThreadPool. |
| ecs_data_oriented_crowd | u_dots | direct | yes | Entities и Unity Physics. |
| ecs_data_oriented_crowd | ue_mass | direct | yes | Mass Entity — ECS-фреймворк для толпы. |
| fixed_timestep_physics | c_job_system | alternative | gap | Собственный планировщик с фиксированным шагом. |
| fixed_timestep_physics | g_physics_server | direct | yes | PhysicsServer3D с фиксированным шагом. |
| fixed_timestep_physics | h_hsl | missing | yes | Фикс-тик задаётся скриптами, не движком. |
| fixed_timestep_physics | s_vphysics | direct | yes | Фиксированный шаг VPhysics/Rubikon с интерполяцией. |
| fixed_timestep_physics | u_dots | direct | yes | Fixed Step в настройках физики и DOTS. |
| fixed_timestep_physics | ue_chaos | direct | yes | Chaos работает с фиксированным шагом и интерполяцией. |
| flipbook_particles | c_manual | missing | gap | Реализуется полностью самостоятельно. |
| flipbook_particles | g_gpu_particles | partial | yes | Реализуется через анимацию текстуры. |
| flipbook_particles | u_vfxgraph | direct | yes | Поддерживается Visual Effect Graph. |
| flipbook_particles | ue_niagara | direct | yes | Поддерживается материалами с flipbook. |
| flow_field_pathing | c_ecs | alternative | gap | Собственная реализация в ECS. |
| flow_field_pathing | g_navigation | partial | yes | Требуется собственная реализация. |
| flow_field_pathing | u_dots | direct | yes | Удобно реализовывать на ECS с Burst. |
| flow_field_pathing | ue_mass | partial | yes | Возможна реализация на Mass Entity. |
| froxel_volumetric_fog | c_render_graph | alternative | gap | Проход объёмов в графе рендера. |
| froxel_volumetric_fog | g_shadows | partial | yes | Ограниченная поддержка объёмов. |
| froxel_volumetric_fog | u_srp | direct | yes | Volumetric Fog в HDRP. |
| froxel_volumetric_fog | ue_lumen | direct | yes | Объёмный туман интегрирован в конвейер. |
| full_path_tracing_pipeline | c_render_graph | alternative | gap | Собственный проход трассировки пути в графе рендера. |
| full_path_tracing_pipeline | g_gi | missing | yes | Полной трассировки пути нет: только SDFGI и VoxelGI. |
| full_path_tracing_pipeline | u_srp | partial | yes | Path Tracing в HDRP есть, но рассчитан на офлайн-режим и узкий набор сцен. |
| full_path_tracing_pipeline | ue_lumen | partial | yes | Lumen на аппаратной трассировке близок к PT, но остаётся гибридом с растровыми кэшами. |
| gerstner_fft_water | c_render_graph | alternative | gap | Проход воды в графе рендера. |
| gerstner_fft_water | g_gpu_particles | partial | yes | Шейдер воды, GPU-частицы для брызг. |
| gerstner_fft_water | u_srp | partial | yes | Шейдер воды в URP/HDRP. |
| gerstner_fft_water | ue_niagara | partial | yes | Реализуется шейдером воды, Niagara для пены. |
| gpu_compute_culling | c_render_graph | alternative | gap | Реализуется как проход собственного графа рендера. |
| gpu_compute_culling | ce_merged | missing | yes | GPU-driven culling нет, только merged-батчи и дистанции. |
| gpu_compute_culling | g_multimesh | partial | yes | Частично решается MultiMesh, без compute-отсечения. |
| gpu_compute_culling | u_instancing | partial | yes | Требуется собственная реализация через compute-шейдеры. |
| gpu_compute_culling | ue_nanite | direct | yes | Nanite выполняет кластеризованное отсечение на GPU. |
| gpu_instancing_vegetation | c_render_graph | alternative | gap | Инстансинг реализуется в собственном графе рендера. |
| gpu_instancing_vegetation | ce_vegetation | direct | yes | Инстансинг и покраска вегетации по маскам. |
| gpu_instancing_vegetation | g_multimesh | direct | yes | MultiMeshInstance3D с массивом трансформаций. |
| gpu_instancing_vegetation | u_instancing | direct | yes | GPU Instancing и BatchRendererGroup. |
| gpu_instancing_vegetation | ue_ism | direct | yes | Instanced и Hierarchical Static Mesh компоненты. |
| gpu_lightmap_baking | c_manual | missing | gap | Реализуется полностью самостоятельно. |
| gpu_lightmap_baking | g_gi | partial | yes | Запекание выполняется на CPU. |
| gpu_lightmap_baking | u_lightmapper | direct | yes | GPU-бэкенд Progressive Lightmapper. |
| gpu_lightmap_baking | ue_lumen | partial | yes | GPU Lightmass используется как внешний инструмент. |
| gpu_meshlet_culling_budget | c_render_graph | alternative | gap | Отсечение мешлетов реализуется в compute-проходе. |
| gpu_meshlet_culling_budget | g_occluder | partial | yes | Окклюзионные отсекатели вместо мешлетов. |
| gpu_meshlet_culling_budget | u_srp | missing | yes | Отсечения мешлетов на GPU нет. |
| gpu_meshlet_culling_budget | ue_nanite | partial | yes | Кластерное отсечение встроено в Nanite, но не настраивается отдельно. |
| gpu_particle_simulation | c_manual | missing | gap | Реализуется полностью самостоятельно. |
| gpu_particle_simulation | g_gpu_particles | direct | yes | GPUParticles3D. |
| gpu_particle_simulation | u_vfxgraph | direct | yes | Visual Effect Graph с GPU-симуляцией. |
| gpu_particle_simulation | ue_niagara | direct | yes | Niagara с GPU-симуляцией. |
| gpu_procedural_placement | c_manual | missing | gap | Реализуется полностью самостоятельно. |
| gpu_procedural_placement | g_threads | partial | yes | Возможна генерация в потоке, без GPU-размещения. |
| gpu_procedural_placement | u_dots | alternative | yes | Удобно совмещать с ECS и Burst. |
| gpu_procedural_placement | ue_ism | partial | yes | Через procedural foliage и HISM, но генерация в основном на CPU. |
| gpu_skinning_compute | c_render_graph | alternative | gap | Проход скиннинга в графе рендера. |
| gpu_skinning_compute | g_gpu_particles | missing | yes | Встроенного GPU-скиннинга нет. |
| gpu_skinning_compute | u_dots | partial | yes | Требует собственной реализации через compute. |
| gpu_skinning_compute | ue_anim_budget | partial | yes | Частично автоматизировано, требуется настройка. |
| hardware_raytraced_gi | c_render_graph | alternative | gap | Требуется собственная интеграция RT API. |
| hardware_raytraced_gi | g_shadows | missing | yes | Встроенного аппаратного RT нет. |
| hardware_raytraced_gi | u_srp | limited | yes | Ограниченная поддержка в HDRP. |
| hardware_raytraced_gi | ue_lumen | direct | yes | Lumen использует аппаратную трассировку при включённом режиме. |
| headless_dedicated_server | c_manual | direct | gap | Собственная серверная сборка. |
| headless_dedicated_server | g_multiplayer | direct | yes | Экспорт без графики с MultiplayerAPI. |
| headless_dedicated_server | h_cloud | direct | yes | HeroCloud: симуляционные серверы как сервис. |
| headless_dedicated_server | s_netcode | direct | yes | Выделенные серверы без графики — стандарт Source. |
| headless_dedicated_server | u_netcode | direct | yes | Сборка Dedicated Server Build. |
| headless_dedicated_server | ue_networking | direct | yes | Сборка Dedicated Server. |
| heightmap_compression | c_manual | missing | gap | Реализуется полностью самостоятельно. |
| heightmap_compression | g_mesh_lod | partial | yes | Требуется ручная настройка форматов. |
| heightmap_compression | u_texture_streaming | complement | yes | Дополняет стриминг мип-уровней. |
| heightmap_compression | ue_virtual_texturing | complement | yes | Хорошо сочетается с виртуальным текстурированием. |
| hierarchical_lod | c_manual | missing | gap | Реализуется полностью самостоятельно. |
| hierarchical_lod | ce_merged | direct | yes | Merged Meshes и LOD-цепочки для открытого мира. |
| hierarchical_lod | g_mesh_lod | partial | yes | Есть автоматический LOD мешей, но не объединение кластеров. |
| hierarchical_lod | u_lod_group | partial | yes | Готового HLOD нет, требуется ручная сборка или сторонний пакет. |
| hierarchical_lod | ue_hlod | direct | yes | HLOD генерируется и собирается средствами редактора. |
| hiz_software_occlusion | c_render_graph | direct | gap | Hi-Z проход в собственном графе рендера. |
| hiz_software_occlusion | ce_merged | missing | yes | Отдельного Hi-Z нет, только merged-батчи и дистанции. |
| hiz_software_occlusion | g_occluder | partial | yes | Окклюдеры расставляются вручную. |
| hiz_software_occlusion | h_hsl | missing | yes | Отсечение не строится, только дистанции. |
| hiz_software_occlusion | s_vulkan | missing | yes | Программного Hi-Z нет, только areaportals. |
| hiz_software_occlusion | u_occlusion | partial | yes | Запечённая окклюзия покрывает статику, динамики — нет. |
| hiz_software_occlusion | ue_nanite | partial | yes | Nanite делает двухпроходное отсечение внутри, отдельного Hi-Z нет. |
| impostors_billboards | c_manual | missing | gap | Реализуется полностью самостоятельно. |
| impostors_billboards | g_multimesh | partial | yes | Реализуется вручную через билборды. |
| impostors_billboards | u_lod_group | partial | yes | Реализуется как последний уровень LOD. |
| impostors_billboards | ue_ism | complement | yes | Дополняет инстансинг растительности. |
| irradiance_volume_probes | c_manual | missing | gap | Реализуется полностью самостоятельно. |
| irradiance_volume_probes | g_gi | direct | yes | VoxelGI и LightmapGI с зондами. |
| irradiance_volume_probes | u_light_probes | direct | yes | Light Probes и Adaptive Probe Volumes. |
| irradiance_volume_probes | ue_lumen | partial | yes | Работает вместе с зондами освещённости. |
| light_range_attenuation_lod | c_manual | alternative | gap | Пороги и упрощённая кривая задаются кодом проекта. |
| light_range_attenuation_lod | g_shadows | partial | yes | Дистанции теней и затухание задаются по каждому свету. |
| light_range_attenuation_lod | u_light_probes | partial | yes | Дальние источники заменяются зондами и упрощённым затуханием. |
| light_range_attenuation_lod | ue_lod | partial | yes | Дальность и тени источника задаются в его настройках. |
| lightmap_2d_baking | c_manual | missing | gap | Реализуется полностью самостоятельно. |
| lightmap_2d_baking | g_gi | partial | yes | LightmapGI применим к 2D с ручной настройкой. |
| lightmap_2d_baking | u_lightmapper | direct | yes | Progressive Lightmapper поддерживает 2D-сцены. |
| lightmap_2d_baking | ue_lumen | missing | yes | Для 2D-освещения встроенного запекания нет. |
| lightmap_atlas_baking | c_manual | missing | gap | Реализуется полностью самостоятельно. |
| lightmap_atlas_baking | g_gi | direct | yes | LightmapGI с запеканием в редакторе. |
| lightmap_atlas_baking | u_lightmapper | direct | yes | Progressive Lightmapper с CPU и GPU бэкендом. |
| lightmap_atlas_baking | ue_lumen | alternative | yes | Альтернатива динамическому ГО Lumen. |
| lightmap_compression_streaming | c_manual | missing | gap | Реализуется полностью самостоятельно. |
| lightmap_compression_streaming | g_gi | partial | yes | Требуется ручная настройка форматов. |
| lightmap_compression_streaming | u_texture_streaming | partial | yes | Стриминг текстур, лайтмапы требуют настройки. |
| lightmap_compression_streaming | ue_virtual_texturing | direct | yes | Лайтмапы подгружаются через виртуальное текстурирование. |
| managed_gc_alloc_budget | c_profiler | diagnostic | gap | Маркеры аллокаций горячего цикла в Tracy. |
| managed_gc_alloc_budget | u_profiler | diagnostic | yes | GC.Alloc-колонка CPU Usage Profiler и руководство по best practices. |
| mesh_index_optimization | c_memory | partial | gap | meshoptimizer подключается как библиотека ассет-пайплайна. |
| mesh_index_optimization | g_mesh_lod | direct | yes | Автогенерация LOD в Godot 4 построена на meshoptimizer. |
| mesh_index_optimization | u_lod_group | partial | yes | LOD Group плюс прогон meshoptimizer в пайплайне. |
| mesh_index_optimization | ue_lod | partial | yes | LOD-цепочки строятся поверх оптимизированных индексов. |
| meshlet_pipeline_adoption | c_render_graph | alternative | gap | Task/mesh-стадии подключаются в собственном графе рендера. |
| meshlet_pipeline_adoption | g_mesh_lod | missing | yes | Меш-шейдеров нет, только LOD и MultiMesh. |
| meshlet_pipeline_adoption | u_srp | missing | yes | Конвейера меш-шейдеров в URP/HDRP нет. |
| meshlet_pipeline_adoption | ue_nanite | partial | yes | Nanite использует кластеризованную геометрию, но свой растеризатор, а не открытый конвейер меш-шейдеров. |
| ml_frame_generation | c_profiler | diagnostic | gap | Замер latency через Tracy. |
| ml_frame_generation | g_profiler | diagnostic | yes | Замер latency генерации. |
| ml_frame_generation | s_vprof | diagnostic | yes | Замер pacing. |
| ml_frame_generation | u_profiler | diagnostic | yes | Замер latency генерации. |
| ml_frame_generation | ue_insights | diagnostic | yes | Замер latency генерации. |
| motion_matching | c_ecs | missing | gap | Реализуется полностью самостоятельно. |
| motion_matching | g_threads | missing | yes | Встроенного решения нет. |
| motion_matching | u_dots | alternative | yes | Удобно реализовывать на ECS с Burst. |
| motion_matching | ue_anim_budget | missing | yes | Встроенного решения нет, требуется плагин или своя реализация. |
| multithreaded_physics_jobs | c_job_system | alternative | gap | Собственная система задач. |
| multithreaded_physics_jobs | g_threads | partial | yes | WorkerThreadPool, физика ограничена. |
| multithreaded_physics_jobs | u_jobs | direct | yes | C# Job System и Unity Physics. |
| multithreaded_physics_jobs | ue_chaos | direct | yes | Chaos использует систему задач движка. |
| navmesh_tiling_streaming | c_manual | missing | gap | Реализуется полностью самостоятельно. |
| navmesh_tiling_streaming | g_navigation | partial | yes | NavigationServer3D, стриминг вручную. |
| navmesh_tiling_streaming | u_navmesh | partial | yes | NavMesh Components с рантайм-сборкой. |
| navmesh_tiling_streaming | ue_navmesh | direct | yes | Навмеш со стримингом ячеек мира. |
| network_relevancy_priority | c_manual | missing | gap | Реализуется полностью самостоятельно. |
| network_relevancy_priority | ce_audio | missing | yes | Графа релевантности нет, только дистанции и LOD. |
| network_relevancy_priority | g_multiplayer | partial | yes | MultiplayerAPI, релевантность вручную. |
| network_relevancy_priority | h_instancing | partial | yes | Релевантность через инстансы и фазы вместо бесшовки. |
| network_relevancy_priority | s_netcode | partial | yes | Релевантность через PVS и дистанции, без графа зон. |
| network_relevancy_priority | u_netcode | direct | yes | Netcode for Entities с приоритизацией. |
| network_relevancy_priority | ue_replication_graph | direct | yes | Replication Graph для массовой репликации. |
| neural_texture_compression | c_manual | partial | gap | Подключается через нейроускорение самостоятельно. |
| neural_texture_compression | g_visibility | missing | yes | Нейросжатия текстур нет. |
| neural_texture_compression | u_texture_streaming | partial | yes | Стриминг мипов из коробки, NTC — внешним плагином. |
| neural_texture_compression | ue_virtual_texturing | complement | yes | Нейросжатие тайлов дополняет виртуальное текстурирование. |
| normal_bake_retopology_pipeline | c_manual | partial | gap | Ретопология и бейк во внешнем DCC. |
| normal_bake_retopology_pipeline | g_mesh_lod | partial | yes | Бейк во внешнем DCC, LOD автоматический. |
| normal_bake_retopology_pipeline | u_lod_group | partial | yes | Бейк во внешнем DCC, раскладка — группой LOD. |
| normal_bake_retopology_pipeline | ue_lod | partial | yes | Запечённые нормали живут на LOD-цепочках. |
| npc_perception_budget | c_manual | alternative | gap | Очередь запросов восприятия реализуется кодом проекта. |
| npc_perception_budget | g_visibility | partial | yes | Видимость через VisibilityNotifier и слои, квоты — кодом. |
| npc_perception_budget | u_navmesh | missing | yes | Готовой системы восприятия нет, пишется кодом. |
| npc_perception_budget | ue_behavior_tree | partial | yes | Восприятие через AI Perception с настройкой интервалов. |
| particle_pooling | c_memory | alternative | gap | Собственные пулы объектов. |
| particle_pooling | g_visibility | partial | yes | Ручное управление пулом узлов. |
| particle_pooling | u_dots | partial | yes | Удобно совмещать с ECS без сборки мусора. |
| particle_pooling | ue_niagara | complement | yes | Пул компонентов Niagara. |
| path_tracing_sample_denoiser_budget | c_render_graph | alternative | gap | Денойзер и бюджет выборок пишутся в собственном проходе. |
| path_tracing_sample_denoiser_budget | g_gi | missing | yes | Денойзера для трассировки пути нет. |
| path_tracing_sample_denoiser_budget | u_srp | partial | yes | Накопление и денойзер HDRP с настройкой числа кадров истории. |
| path_tracing_sample_denoiser_budget | ue_lumen | partial | yes | Число выборок и радиус денойзера задаются консольными переменными Lumen. |
| physics_lod_sleeping | c_job_system | alternative | gap | Собственная логика LOD. |
| physics_lod_sleeping | g_physics_server | direct | yes | Настройки областей и сна. |
| physics_lod_sleeping | s_vphysics | direct | yes | Сон и пробуждение тел — базовый механизм VPhysics. |
| physics_lod_sleeping | u_quality | direct | yes | Пороги сна в настройках физики. |
| physics_lod_sleeping | ue_chaos | direct | yes | Chaos поддерживает спящие тела и LOD. |
| planar_reflection_budget | c_manual | partial | gap | Проход отражения пишется в графе рендера. |
| planar_reflection_budget | g_visibility | partial | yes | ReflectionProbe вручную, бюджет planar — настройкой. |
| planar_reflection_budget | u_srp | direct | yes | Planar Reflection Probe в URP и HDRP. |
| planar_reflection_budget | ue_lumen | partial | yes | Lumen-отражения вместо плоских; planar — отдельной настройкой. |
| post_effect_selective | c_render_graph | alternative | gap | Проходы эффектов в собственном графе рендера. |
| post_effect_selective | g_visibility | partial | yes | Частично через слои и области видимости. |
| post_effect_selective | u_srp | direct | yes | Настраиваемые проходы URP и HDRP. |
| post_effect_selective | ue_niagara | missing | yes | Требуется собственная настройка области эффекта. |
| pso_precaching_warmup | c_profiler | direct | gap | Tracy-маркеры прогревов и CLI-захват. |
| pso_precaching_warmup | g_profiler | diagnostic | yes | Контроль компиляции конвейеров. |
| pso_precaching_warmup | s_vprof | diagnostic | yes | Замер hitch при загрузке карт. |
| pso_precaching_warmup | u_profiler | diagnostic | yes | Замер shader load time в Profiler. |
| pso_precaching_warmup | ue_insights | diagnostic | yes | Hitch-детект и контроль прогрева по Insights. |
| quality_tier_scalability | c_manual | missing | gap | Тиры и адаптивный cap пишутся самостоятельно. |
| quality_tier_scalability | g_visibility | missing | yes | Тиров нет, только ручные дистанции. |
| quality_tier_scalability | u_quality | direct | yes | Тиры качества и per-platform overrides. |
| quality_tier_scalability | ue_insights | missing | yes | Scalability Groups настраиваются вручную. |
| raycast_vehicle_physics | c_manual | alternative | gap | Модель подвески и сцепления пишется кодом. |
| raycast_vehicle_physics | g_physics_server | partial | yes | VehicleBody3D даёт упрощённую модель, тонкая настройка ограничена. |
| raycast_vehicle_physics | u_quality | missing | yes | Встроенной физики транспорта нет, только WheelCollider и свои модели. |
| raycast_vehicle_physics | ue_vehicles | direct | yes | Chaos Vehicles: подвеска на рейкастах, сцепление и привод. |
| rt_effect_resolution_budget | c_render_graph | alternative | gap | Масштаб буферов и накопление задаются в собственном проходе. |
| rt_effect_resolution_budget | g_gi | missing | yes | Настраиваемого бюджета трассировочных эффектов нет. |
| rt_effect_resolution_budget | u_srp | partial | yes | Половинное разрешение эффектов настраивается в HDRP. |
| rt_effect_resolution_budget | ue_lumen | partial | yes | Разрешение трассировки и накопление задаются масштабом Lumen. |
| rvo_local_avoidance | c_manual | partial | gap | Открытая RVO2/ORCA-библиотека подключается кодом. |
| rvo_local_avoidance | g_navigation | direct | yes | RVO-библиотека внутри NavigationServer. |
| rvo_local_avoidance | u_navmesh | partial | yes | RVO-стиринг агента: качество и приоритет избегания. |
| rvo_local_avoidance | ue_navmesh | partial | yes | Крауд-избегание детура поверх навмеша. |
| screen_space_contact_shadows | c_render_graph | alternative | gap | Проход в собственном графе рендера. |
| screen_space_contact_shadows | g_shadows | partial | yes | Частично через экранное затенение. |
| screen_space_contact_shadows | u_srp | direct | yes | Contact Shadows в HDRP. |
| screen_space_contact_shadows | ue_vsm | complement | yes | Дополняет основные тени. |
| screen_space_gi | c_render_graph | alternative | gap | Проход в собственном графе рендера. |
| screen_space_gi | g_shadows | partial | yes | Ограниченная поддержка экранных эффектов. |
| screen_space_gi | u_srp | partial | yes | Экранное затенение и отражения доступны в URP/HDRP. |
| screen_space_gi | ue_lumen | complement | yes | Используется как дополнение к основному ГО. |
| screen_space_water_simple | c_render_graph | alternative | gap | Проход воды в графе рендера. |
| screen_space_water_simple | g_visibility | partial | yes | Простой материал воды. |
| screen_space_water_simple | u_srp | direct | yes | Готовый шейдер воды в URP. |
| screen_space_water_simple | ue_niagara | partial | yes | Материал воды с экранными эффектами. |
| screenspace_light_shafts | c_render_graph | direct | gap | Радиальный блур-проход в собственном графе рендера. |
| screenspace_light_shafts | g_visibility | missing | yes | Встроенных крепускулярных лучей нет. |
| screenspace_light_shafts | u_srp | partial | yes | Кастомный fullscreen-проход в URP. |
| screenspace_light_shafts | ue_lumen | missing | yes | Отдельного screen-space пасса валов нет. |
| sdf_global_illumination | c_manual | missing | gap | Реализуется полностью самостоятельно. |
| sdf_global_illumination | ce_svogi | direct | yes | SVOGI/SVOTI: конусная трассировка по вокселям. |
| sdf_global_illumination | g_gi | partial | yes | VoxelGI и SDFGI дают упрощённый аналог. |
| sdf_global_illumination | u_srp | limited | yes | Требует HDRP и собственной настройки. |
| sdf_global_illumination | ue_lumen | direct | yes | Lumen использует дистанционные поля для ГО. |
| selective_ray_traced_effects | c_render_graph | alternative | gap | Отдельные RT-проходы в собственном графе рендера. |
| selective_ray_traced_effects | g_gi | missing | yes | Выборочной аппаратной трассировки нет. |
| selective_ray_traced_effects | u_srp | partial | yes | Трассировочные эффекты HDRP настраиваются по объёмам и слоям. |
| selective_ray_traced_effects | ue_lumen | direct | yes | Отражения, тени и AO на трассировке включаются независимо. |
| shadow_caster_2d_limits | c_manual | missing | gap | Реализуется полностью самостоятельно. |
| shadow_caster_2d_limits | g_shadows | direct | yes | Настройки 2D-освещения и теней в проекте. |
| shadow_caster_2d_limits | u_quality | direct | yes | Настройки качества 2D-теней и лимиты источников. |
| shadow_caster_2d_limits | ue_vsm | missing | yes | Встроенного 2D-теневого решения нет. |
| skeletal_2d_deform | c_manual | missing | gap | Реализуется полностью самостоятельно. |
| skeletal_2d_deform | g_mesh_lod | partial | yes | Skeleton2D и Polygon2D, без полноценного скелетного пакета. |
| skeletal_2d_deform | u_lod_group | partial | yes | 2D Animation пакет, интеграция со скинингом. |
| skeletal_2d_deform | ue_lod | missing | yes | Встроенного 2D-скелетного решения нет. |
| snapshot_slot_saves | c_manual | direct | gap | Сериализация, слоты и миграции пишутся под проект. |
| snapshot_slot_saves | g_bg_loading | missing | yes | Слотов нет; запись через ResourceSaver/FileAccess своими слотами. |
| snapshot_slot_saves | u_addressables | missing | yes | Готового сейв-слоя нет; слоты и сериализация — кодом поверх JsonUtility. |
| splitscreen_render_budget | c_render_graph | alternative | gap | Два вью в собственном графе. |
| splitscreen_render_budget | g_visibility | partial | yes | Ручное управление видимостью на вью. |
| splitscreen_render_budget | u_occlusion | partial | yes | Окклюзия на две камеры. |
| splitscreen_render_budget | ue_hlod | partial | yes | HLOD и proxy-LOD режут двойные draw calls. |
| sprite_atlas_batching | c_render_graph | alternative | gap | Реализуется как проход собственного графа рендера. |
| sprite_atlas_batching | g_multimesh | partial | yes | Готового атласного батчинга нет, частично через MultiMesh. |
| sprite_atlas_batching | u_srp_batcher | direct | yes | SRP Batcher и Sprite Atlas собирают слои в батчи. |
| sprite_atlas_batching | ue_ism | partial | yes | Paper2D и инстансинг спрайтов дают частичный аналог упаковки. |
| sprite_particle_atlas | c_manual | missing | gap | Реализуется полностью самостоятельно. |
| sprite_particle_atlas | g_gpu_particles | partial | yes | GPUParticles2D с текстурой из атласа. |
| sprite_particle_atlas | u_vfxgraph | limited | yes | VFX Graph ориентирован на 3D; для 2D применяется ограниченно. |
| sprite_particle_atlas | ue_niagara | partial | yes | Niagara рассчитан на 3D, для 2D требуется адаптация. |
| sprite_sheet_compression | c_manual | missing | gap | Реализуется полностью самостоятельно. |
| sprite_sheet_compression | g_mesh_lod | missing | yes | Настраивается вручную через параметры импорта. |
| sprite_sheet_compression | u_texture_streaming | direct | yes | Настройки импорта текстур и форматы сжатия. |
| sprite_sheet_compression | ue_lod | missing | yes | Требуется ручная настройка форматов текстур. |
| srp_batcher_discipline | c_render_graph | alternative | gap | Персистентные буферы в собственном графе. |
| srp_batcher_discipline | g_multimesh | missing | yes | Батчера состояний нет, только MultiMesh. |
| srp_batcher_discipline | u_srp_batcher | direct | yes | SRP Batcher включается в настройках конвейера. |
| srp_batcher_discipline | ue_nanite | missing | yes | SRP Batcher — механизм Unity, аналога нет. |
| static_shadow_caching | c_render_graph | alternative | gap | Реализуется в графе рендера. |
| static_shadow_caching | g_shadows | partial | yes | Требуется ручная настройка статики. |
| static_shadow_caching | u_quality | partial | yes | Режим статических теней с кэшированием. |
| static_shadow_caching | ue_vsm | direct | yes | Кэширование страниц виртуальных карт теней. |
| temporal_radiance_cache | c_manual | missing | gap | Реализуется полностью самостоятельно. |
| temporal_radiance_cache | g_gi | partial | yes | Частично решается SDFGI. |
| temporal_radiance_cache | u_srp | partial | yes | Требует собственной реализации. |
| temporal_radiance_cache | ue_lumen | direct | yes | Кэш освещённости Lumen с временным накоплением. |
| temporal_upscaling | c_render_graph | missing | gap | Реализуется полностью самостоятельно. |
| temporal_upscaling | g_visibility | partial | yes | Ограниченная поддержка, требуется настройка. |
| temporal_upscaling | h_hsl | missing | yes | Апскейлеров нет, только снижение разрешения. |
| temporal_upscaling | s_vulkan | missing | yes | Временного апскейлера нет, только MSAA и downscale. |
| temporal_upscaling | u_srp | direct | yes | Встроенные апскейлеры в URP/HDRP. |
| temporal_upscaling | ue_lumen | complement | yes | Работает совместно с временным накоплением. |
| terrain_clipmap | c_render_graph | alternative | gap | Собственный проход ландшафта в графе рендера. |
| terrain_clipmap | g_mesh_lod | partial | yes | Базовый LOD мешей, клипмап реализуется вручную. |
| terrain_clipmap | u_lod_group | partial | yes | Требуется собственная реализация или сторонний ассет. |
| terrain_clipmap | ue_nanite | alternative | yes | Nanite частично заменяет клипмап для статичной геометрии. |
| terrain_generation_streaming_budget | c_job_system | direct | gap | Собственная система задач с бюджетом на кадр. |
| terrain_generation_streaming_budget | g_threads | direct | yes | Генерация в потоках с приоритетом по дистанции. |
| terrain_generation_streaming_budget | u_jobs | direct | yes | Генерация в C# Job System с распределением по кадрам. |
| terrain_generation_streaming_budget | ue_world_partition | partial | yes | Приоритет и радиус загрузки задаются настройками партиции. |
| tickrate_budgeting | c_manual | missing | gap | Тик и bandwidth считаются самостоятельно. |
| tickrate_budgeting | g_multiplayer | partial | yes | Тик настраивается поверх API. |
| tickrate_budgeting | h_cloud | partial | yes | Тик серверов HeroCloud. |
| tickrate_budgeting | s_netcode | direct | yes | Тикрейт, interp и lagcomp — ядро netcode. |
| tickrate_budgeting | u_netcode | direct | yes | Тикрейт Netcode-пакетов. |
| tiled_clustered_light_culling | c_render_graph | direct | gap | Тайловая классификация и сетка источников в собственном графе. |
| tiled_clustered_light_culling | g_visibility | partial | yes | Кластеризация уже внутри Forward+, настраивать нечего. |
| tiled_clustered_light_culling | u_srp | direct | yes | Forward+ в URP: кластеризованное назначение источников. |
| tiled_clustered_light_culling | ue_lumen | missing | yes | Отдельного tiled-culling нет; много источников — через Lumen/Deferred. |
| tilemap_chunk_streaming | c_streaming | missing | gap | Требуется собственный конвейер загрузки. |
| tilemap_chunk_streaming | g_bg_loading | direct | yes | ResourceLoader.load_threaded для фоновой подгрузки чанков. |
| tilemap_chunk_streaming | u_addressables | direct | yes | Addressables и сцены с чанками карты. |
| tilemap_chunk_streaming | ue_world_partition | partial | yes | World Partition рассчитан на 3D, для 2D требуется адаптация. |
| tilemap_layer_culling | c_render_graph | alternative | gap | Отсечение реализуется в графе рендера. |
| tilemap_layer_culling | g_visibility | direct | yes | Ручное управление видимостью слоёв и нод. |
| tilemap_layer_culling | u_occlusion | limited | yes | Окклюзия рассчитана на 3D, для 2D применяется ограниченно. |
| tilemap_layer_culling | ue_ism | partial | yes | Частично решается инстансингом и ручным управлением слоями. |
| time_sliced_pathfinding | c_job_system | alternative | gap | Собственная очередь запросов. |
| time_sliced_pathfinding | g_navigation | partial | yes | Ограничение числа запросов вручную. |
| time_sliced_pathfinding | u_jobs | direct | yes | Поиск пути в C# Job System. |
| time_sliced_pathfinding | ue_navmesh | partial | yes | Ограничение запросов настраивается. |
| variable_rate_shading | c_render_graph | missing | gap | Реализуется полностью самостоятельно. |
| variable_rate_shading | g_profiler | missing | yes | Встроенной поддержки нет. |
| variable_rate_shading | u_srp | limited | yes | Ограниченная поддержка в HDRP. |
| variable_rate_shading | ue_insights | diagnostic | yes | Unreal Insights для оценки выигрыша. |
| vegetation_atlas_lod | c_manual | missing | gap | Реализуется полностью самостоятельно. |
| vegetation_atlas_lod | g_mesh_lod | direct | yes | Автоматическая генерация LOD. |
| vegetation_atlas_lod | u_lod_group | direct | yes | LOD Group и настройка атласов. |
| vegetation_atlas_lod | ue_lod | direct | yes | LOD-цепочки и атласы собираются редактором. |
| vehicle_simulation_lod | c_job_system | alternative | gap | Уровни симуляции задаются в собственной системе задач. |
| vehicle_simulation_lod | g_physics_server | partial | yes | Переключение уровня симуляции — кодом на PhysicsServer. |
| vehicle_simulation_lod | u_quality | partial | yes | Пороги упрощения задаются настройками качества и скриптами. |
| vehicle_simulation_lod | ue_vehicles | partial | yes | LOD симуляции собирается из настроек и Significance Manager. |
| virtual_geometry_clusters | c_manual | missing | gap | Реализуется полностью самостоятельно. |
| virtual_geometry_clusters | g_mesh_lod | missing | yes | Встроенного аналога нет. |
| virtual_geometry_clusters | u_lod_group | missing | yes | Встроенного аналога нет. |
| virtual_geometry_clusters | ue_nanite | direct | yes | Прямая реализация виртуализированной геометрии. |
| virtual_shadow_maps | c_render_graph | alternative | gap | Реализуется как виртуализированный конвейер страниц теней в графе рендера. |
| virtual_shadow_maps | g_shadows | missing | yes | Полного встроенного аналога VSM нет; требуется собственная реализация. |
| virtual_shadow_maps | u_srp | missing | yes | Полного встроенного аналога VSM нет; требуется другой теневой конвейер или пакет. |
| virtual_shadow_maps | ue_vsm | direct | yes | Virtual Shadow Maps — встроенный конвейер виртуальных карт теней Unreal Engine. |
| virtual_texturing | c_manual | missing | gap | Реализуется полностью самостоятельно. |
| virtual_texturing | g_visibility | missing | yes | Встроенного аналога нет. |
| virtual_texturing | u_texture_streaming | partial | yes | Стриминг мип-уровней, но не полноценное виртуальное текстурирование. |
| virtual_texturing | ue_virtual_texturing | direct | yes | Встроенное виртуальное текстурирование. |
| volumetric_half_resolution | c_render_graph | alternative | gap | Проход в пониженном разрешении. |
| volumetric_half_resolution | ce_fog | direct | yes | Объёмный туман и облака с половинным разрешением. |
| volumetric_half_resolution | g_shadows | partial | yes | Требуется собственная реализация. |
| volumetric_half_resolution | u_quality | direct | yes | Настройка разрешения объёмного тумана в HDRP. |
| volumetric_half_resolution | ue_lumen | complement | yes | Настройка разрешения объёмов. |
| voxel_cone_tracing | c_manual | missing | gap | Реализуется полностью самостоятельно. |
| voxel_cone_tracing | g_gi | direct | yes | VoxelGI — прямая реализация подхода. |
| voxel_cone_tracing | u_srp | limited | yes | Требует собственной реализации в HDRP. |
| voxel_cone_tracing | ue_lumen | alternative | yes | Lumen решает ту же задачу другими средствами. |
| world_origin_shifting | c_streaming | alternative | gap | Реализуется вместе с подсистемой стриминга. |
| world_origin_shifting | g_visibility | missing | yes | Встроенного решения нет, требуется ручной сдвиг. |
| world_origin_shifting | u_quality | missing | yes | Встроенного решения нет, требуется собственный origin rebasing. |
| world_origin_shifting | ue_lwc | direct | yes | Large World Coordinates решает проблему точности на уровне движка. |
| world_partition_streaming | c_streaming | missing | gap | Подсистему стриминга необходимо реализовать самостоятельно. |
| world_partition_streaming | g_bg_loading | partial | yes | Требуется самостоятельная организация плиток и приоритетов загрузки. |
| world_partition_streaming | h_instancing | alternative | yes | Бесшовной партиции нет: мир режется на инстансы планет. |
| world_partition_streaming | u_addressables | direct | yes | Addressables обеспечивает адресную загрузку сцен и ассетов. |
| world_partition_streaming | ue_world_partition | direct | yes | World Partition автоматически стримит ячейки мира. |

## Движки и инструменты

| Engine | Engine docs | Tool | Tool docs | Min version |
| --- | --- | --- | --- | --- |
| cryengine: CryEngine | yes | CryAudio + окклюзия | yes | — |
| cryengine: CryEngine | yes | Volumetric Fog / Clouds | yes | — |
| cryengine: CryEngine | yes | Merged Meshes / HLOD | yes | — |
| cryengine: CryEngine | yes | SVOGI / SVOTI | yes | — |
| cryengine: CryEngine | yes | Vegetation + Touch Bending | yes | — |
| custom: Собственный движок | gap | Собственный ECS | gap | — |
| custom: Собственный движок | gap | Система задач (job system) | gap | — |
| custom: Собственный движок | gap | Реализация вручную | gap | — |
| custom: Собственный движок | gap | Аллокатор и пулинг памяти | gap | — |
| custom: Собственный движок | gap | Встроенный профилировщик / Tracy | gap | — |
| custom: Собственный движок | gap | Граф рендера | gap | — |
| custom: Собственный движок | gap | Подсистема стриминга | gap | — |
| godot: Godot | yes | ResourceLoader (фоновое загрузка) | yes | — |
| godot: Godot | yes | VoxelGI / LightmapGI / SDFGI | yes | — |
| godot: Godot | yes | GPUParticles3D | yes | — |
| godot: Godot | yes | Automatic Mesh LOD | yes | — |
| godot: Godot | yes | MultiMeshInstance3D | yes | — |
| godot: Godot | yes | MultiplayerAPI | yes | — |
| godot: Godot | yes | NavigationServer3D | yes | — |
| godot: Godot | yes | OccluderInstance3D | yes | — |
| godot: Godot | yes | PhysicsServer3D | yes | — |
| godot: Godot | yes | Профилировщик Godot | yes | — |
| godot: Godot | yes | DirectionalLight3D Shadows | yes | — |
| godot: Godot | yes | Thread / WorkerThreadPool | yes | — |
| godot: Godot | yes | Ручное управление видимостью | yes | — |
| heroengine: HeroEngine | yes | HeroBlade | yes | — |
| heroengine: HeroEngine | yes | HeroCloud | yes | — |
| heroengine: HeroEngine | yes | HeroScript (HSL) | yes | — |
| heroengine: HeroEngine | yes | Инстансинг планет / шардинг | yes | — |
| source: Source / Source 2 | yes | Tick / Interp / Lagcomp | yes | — |
| source: Source / Source 2 | yes | Stencil-порталы / BSP | yes | — |
| source: Source / Source 2 | yes | VPhysics / Rubikon | yes | — |
| source: Source / Source 2 | yes | VProf / net_graph | yes | — |
| source: Source / Source 2 | yes | Source 2 Vulkan-рендер | yes | — |
| unity: Unity | yes | Addressables | yes | — |
| unity: Unity | yes | Entities / DOTS | yes | — |
| unity: Unity | yes | GPU Instancing | yes | — |
| unity: Unity | yes | C# Job System | yes | — |
| unity: Unity | yes | Light Probes | yes | — |
| unity: Unity | yes | Progressive Lightmapper | yes | — |
| unity: Unity | yes | LOD Group | yes | — |
| unity: Unity | yes | NavMesh | yes | — |
| unity: Unity | yes | Netcode for Entities | yes | — |
| unity: Unity | yes | Occlusion Culling | yes | — |
| unity: Unity | yes | Profiler | yes | — |
| unity: Unity | yes | Quality Settings | yes | — |
| unity: Unity | yes | URP / HDRP | yes | — |
| unity: Unity | yes | SRP Batcher | yes | — |
| unity: Unity | yes | Mipmap Streaming | yes | — |
| unity: Unity | yes | Visual Effect Graph | yes | — |
| unreal: Unreal Engine | yes | Animation Budget Allocator | yes | — |
| unreal: Unreal Engine | yes | Behavior Tree | yes | — |
| unreal: Unreal Engine | yes | Chaos Physics | yes | — |
| unreal: Unreal Engine | yes | Gameplay Ability System | yes | — |
| unreal: Unreal Engine | yes | HLOD | yes | — |
| unreal: Unreal Engine | yes | Unreal Insights | yes | — |
| unreal: Unreal Engine | yes | Instanced / Hierarchical Static Mesh | yes | — |
| unreal: Unreal Engine | yes | Static Mesh LOD | yes | — |
| unreal: Unreal Engine | yes | Lumen | yes | 5.0 |
| unreal: Unreal Engine | yes | Large World Coordinates | yes | 5.0 |
| unreal: Unreal Engine | yes | Mass Entity | yes | 5.0 |
| unreal: Unreal Engine | yes | Nanite | yes | 5.0 |
| unreal: Unreal Engine | yes | Navigation Mesh | yes | — |
| unreal: Unreal Engine | yes | Networking and Multiplayer | yes | — |
| unreal: Unreal Engine | yes | Niagara | yes | — |
| unreal: Unreal Engine | yes | Replication Graph | yes | — |
| unreal: Unreal Engine | yes | Significance Manager | yes | — |
| unreal: Unreal Engine | yes | Chaos Vehicles | yes | — |
| unreal: Unreal Engine | yes | Virtual Texturing | yes | — |
| unreal: Unreal Engine | yes | Virtual Shadow Maps | yes | 5.0 |
| unreal: Unreal Engine | yes | World Partition | yes | 5.0 |

## Связи между решениями

| A | B | Type | Severity | Source URL | Description |
| --- | --- | --- | ---: | --- | --- |
| ability_visual_effect_budget | animation_lod_budget | risk | 2 | yes | Effects attached to sockets or bones (contrails, weapon trails, footstep dust) read animation state; when animation update rate is throttled, the attachment point updates at the throttled rate and the effect visibly detaches. |
| ability_visual_effect_budget | art_direction_stylization | complement | 1 | yes | A stylized look with flat, readable silhouettes tolerates aggressive VFX scaling (fewer particles, sprite LODs, cheaper renderers) far better than a photoreal look, so the art direction determines how low the budget can go before players notice. |
| ability_visual_effect_budget | data_driven_ability_system | dependency | 3 | yes | In a GAS project the ability system is the VFX spawn source: Gameplay Cues are tag-matched and fire automatically, so an unbounded ability set is an unbounded VFX spawn rate. The budget must be enforced on the cue side, not only in Niagara. |
| ability_visual_effect_budget | tilemap_layer_culling | complement | 1 | yes | In a 2D game, both are fill-rate and instance-count problems; culling offscreen layers and capping live effects attack the same frame-time budget from different sides. |
| agent_update_budget | behaviour_tree_update_budget | overlap | 1 | yes | Behaviour-tree tick throttling is the decision-logic slice of the same budget. |
| agent_update_budget | crowd_instancing_impostors | complement | 1 | yes | Update budgeting bounds CPU; instancing/impostors bound GPU. Both are needed for thousands of NPCs. |
| agent_update_budget | crowd_instancing_impostors | risk | 1 | yes | Снижение частоты обновления дальних агентов совместимо с их упрощённой отрисовкой, но независимость экономии AI и рендера внутри одной группы не доказана: заметность задержки требует проверки. |
| agent_update_budget | ecs_data_oriented_crowd | alternative | 1 | yes | Restructuring to a data-oriented framework can remove the need for a budget by making per-agent update cheap. |
| ai_director_pacing | agent_update_budget | complement | 1 | yes | A director that can spawn hundreds of NPCs only works if per-agent update cost is also budgeted; L4D pairs population control with a small set of reused entities. |
| ai_director_pacing | behaviour_tree_update_budget | complement | 2 | yes | Управление популяцией и бюджет поведения решают разные задачи. |
| ai_director_pacing | behaviour_tree_update_budget | overlap | 1 | yes | Both bound how much AI runs per frame; the director bounds how many agents exist, the budget bounds how often each thinks. |
| ai_director_pacing | navmesh_tiling_streaming | risk | 2 | yes | Спавн на неготовом навигационном тайле может нарушить достижимость. |
| ai_director_pacing | npc_perception_budget | complement | 2 | yes | Популяция и квота восприятия могут применяться совместно. |
| animation_compression | animation_lod_budget | overlap | 1 | yes | Both target animation memory/CPU, but at different layers: compression reduces per-clip cost, LOD/budgeting reduces how many clips get evaluated per frame. Neither substitutes for the other. |
| animation_compression | motion_matching | dependency | 3 | yes | Motion matching stores far more animation than a state machine, so memory per clip is the binding constraint; LMM exists precisely because motion-matching memory 'scales linearly with the amount of data used'. |
| animation_compression | normal_bake_retopology_pipeline | risk | 2 | yes | ACL's error is measured on a virtual vertex 3cm from each bone as a proxy for the real mesh; if the real mesh has long limbs or extreme proportions, that proxy is wrong and visible error appears where the metric reports none. |
| animation_lod_budget | animation_compression | complement | 1 | yes | Compression lowers the per-character evaluation cost (smaller working set, faster sampling), which directly raises how many characters fit inside a fixed budget. |
| animation_lod_budget | data_driven_ability_system | risk | 2 | yes | Abilities that drive montages or read animation state on tick inherit the throttled rate; a throttled character can activate an ability whose montage callback is delayed, which is a gameplay bug, not a visual one. |
| animation_lod_budget | gpu_skinning_compute | dependency | 3 | yes | Метод «animation_lod_budget» требует предварительного метода «gpu_skinning_compute». |
| animation_lod_budget | motion_matching | risk | 2 | yes | Motion matching searches the database on tick; throttling the tick rate throttles responsiveness, and root-motion locomotion blocks the parallel-update path entirely, which removes one of the two ways to pay for motion matching in a crowd. |
| art_direction_stylization | ability_visual_effect_budget | dependency | 3 | yes | The VFX language is part of the style; a stylized game usually needs fewer, larger, more readable effects, which directly changes the particle/instance budget rather than just the look. |
| art_direction_stylization | sprite_atlas_batching | complement | 1 | yes | 2D/vector and frame-by-frame styles put extreme pressure on sprite memory and atlas packing instead of on geometry and materials. |
| art_direction_stylization | sprite_sheet_compression | risk | 2 | yes | Flat-colour and hard-edged stylized art is exactly the content that block-compression artefacts damage most; compression choice is an art-direction decision in a 2D game. |
| async_compute_overlap | bindless_uber_shaders | complement | 1 | yes | AMD: 'we recommend to implement a compute path for as many render workloads as possible in order to have more freedom in determining which tasks to overlap'. |
| async_compute_overlap | hiz_software_occlusion | complement | 1 | yes | GPU occlusion culling is a natural compute-queue workload, and it enables the geometry savings that make the rest of the frame cheaper. |
| async_compute_overlap | pso_precaching_warmup | complement | 2 | yes | Прогрев PSO не заменяет синхронизацию очередей и не является её условием. |
| async_compute_overlap | pso_precaching_warmup | risk | 2 | yes | Splitting the frame across queues multiplies the number of PSOs that must be warm. |
| async_compute_overlap | quality_tier_scalability | risk | 2 | yes | Async behaviour is hardware-specific; a tier that assumes overlap on desktop may regress on mobile TBDR. |
| async_compute_overlap | tiled_clustered_light_culling | complement | 2 | yes | Отсечение уменьшает работу; перекрытие планирует оставшиеся проходы. |
| async_incremental_saves | composition_bootstrap_architecture | risk | 2 | yes | Component-graph entity models make consistent snapshots and load-order reconstruction harder; the save model must be designed with the entity model. |
| async_incremental_saves | navmesh_tiling_streaming | overlap | 1 | yes | Both are chunked, incremental persistence/loading problems with the same consistency concerns. |
| async_incremental_saves | particle_pooling | alternative | 1 | yes | Unrelated technically, but both are examples of moving burst work off the frame; the discipline transfers. |
| async_incremental_saves | snapshot_slot_saves | complement | 1 | yes | Slot-based snapshots are what async saving writes; incremental writes are an optimisation of the same data. |
| async_loading_pipeline | build_size_startup_budgets | complement | 1 | yes | Compression block size (Epic recommends 256 KB for Oodle) sets the minimum IO granularity that the loader can request. |
| async_loading_pipeline | virtual_geometry_clusters | overlap | 1 | yes | Nanite's streaming is an async pipeline with a fixed 128 KB page and a persistent culling shader generating requests. |
| async_loading_pipeline | virtual_texturing | overlap | 1 | yes | VT is a specialised async pipeline with GPU-driven requests and a fixed physical page pool - the same architecture, applied to texels. |
| async_loading_pipeline | world_partition_streaming | complement | 1 | yes | Partitioning decides what to load; the async pipeline decides how it is loaded without hitching. |
| audio_convolution_reverb | audio_occlusion_propagation | dependency | 3 | yes | Reverb is computed from the same reflection simulation as propagation, and shares the ray/bounce budget directly. |
| audio_convolution_reverb | headless_dedicated_server | complement | 1 | yes | A headless server should not run any of this; excluding audio entirely from the server build is free performance. |
| audio_convolution_reverb | managed_gc_alloc_budget | risk | 2 | yes | IR loading and per-frame effect state are a common source of managed allocations in engines with a GC; a hitch in the reverb path is immediately audible. |
| audio_occlusion_propagation | audio_convolution_reverb | complement | 1 | yes | Reverb is the tail of propagation; both are computed from the same reflection simulation and both share the ray/bounce budget. |
| audio_occlusion_propagation | audio_streaming_compression | complement | 1 | yes | Propagation adds per-source DSP cost, which competes with decoding cost for the same audio thread / CPU budget. |
| audio_occlusion_propagation | managed_gc_alloc_budget | risk | 2 | yes | Per-source audio simulation state allocated per frame in a managed engine produces GC pressure exactly where a hitch is most audible. |
| audio_occlusion_propagation | network_relevancy_priority | unknown | 2 | yes | Epic's relevancy guidance mentions actors that 'can potentially be seen or heard', implying audio should feed relevancy, but I found no source documenting how to wire audio relevance to network relevance. Recorded as unknown. |
| audio_streaming_compression | audio_convolution_reverb | risk | 2 | yes | Reverb and decoding share the audio thread; adding heavy convolution reverb reduces the headroom available for decoding and vice versa. |
| audio_streaming_compression | audio_occlusion_propagation | risk | 2 | yes | Same audio-thread contention: per-source occlusion queries plus decode plus reverb must fit in one frame's audio budget. |
| audio_streaming_compression | headless_dedicated_server | complement | 1 | yes | A headless server should carry no audio assets or audio runtime at all - the Dedicated Server build target is where that saving is realised. |
| audio_streaming_compression | managed_gc_alloc_budget | complement | 1 | yes | Streaming decoders are a classic source of per-frame allocations in managed engines; a zero-allocation decode path is part of this budget. |
| baked_occlusion_culling | hierarchical_lod | alternative | 1 | yes | For open worlds HLOD, not PVS, is the mechanism for reducing what is drawn at distance. |
| baked_occlusion_culling | virtual_geometry_clusters | alternative | 1 | yes | Nanite's two-phase HZB occlusion solves the same problem dynamically, including for moving objects; it supersedes baked PVS wherever Nanite is usable. |
| baked_occlusion_culling | world_partition_streaming | hard_conflict | 3 | yes | Documented: precomputed visibility 'Does not handle streaming levels efficiently. All data is stored in the persistent Level.' Baked PVS and a partitioned streamed world are effectively mutually exclusive. |
| behaviour_tree_update_budget | agent_update_budget | overlap | 1 | yes | Both bound per-frame agent work; this method is the decision-logic slice, agent_update_budget is the whole-agent slice including movement/animation. |
| behaviour_tree_update_budget | ecs_data_oriented_crowd | alternative | 1 | yes | Restructuring agents into a data-oriented ECS can remove the need for throttling by making per-agent evaluation cheap; it is a much larger change. |
| behaviour_tree_update_budget | npc_perception_budget | complement | 1 | yes | Perception is usually the more expensive per-agent subsystem; both are throttled from the same significance value. |
| bindless_uber_shaders | meshlet_pipeline_adoption | complement | 1 | yes | Both are parts of the same GPU-driven pipeline; mesh shading removes the index-buffer barrier and bindless removes the material barrier to merging draws. |
| bindless_uber_shaders | pso_precaching_warmup | complement | 1 | yes | Collapsing permutations with uber shaders is the cheapest way to shrink the PSO precache problem; id Tech 7 reportedly ships 'about ~500 pipeline states and a dozen descriptor layouts'. |
| bindless_uber_shaders | srp_batcher_discipline | complement | 1 | yes | The CPU-side analogue: both approaches reduce per-draw setup by making material data persistent and by minimising shader-variant changes. Unity: 'In SRP Batcher context, the SetShaderPass is called for each new shader variant.' |
| broadphase_spatial_partitioning | collision_layer_matrix | complement | 1 | yes | Layer/mask filtering is cheaper than spatial rejection and runs first; the two stack. |
| broadphase_spatial_partitioning | multithreaded_physics_jobs | complement | 1 | yes | Parallelising physics only pays if the broadphase itself scales; PhysX exposes parallel SAP variants for exactly this reason. |
| broadphase_spatial_partitioning | physics_lod_sleeping | complement | 1 | yes | Sleeping removes bodies from the active set, which is the cheapest possible broadphase win. |
| broadphase_spatial_partitioning | runtime_fracture_budget | risk | 2 | yes | Destruction produces bursts of thousands of small bodies in one region - the worst case for most broadphases and the reason fragment caps exist. |
| build_size_startup_budgets | differential_patch_pipeline | complement | 1 | yes | Pack layout is the single biggest determinant of patch size; the two are one decision viewed from the developer side and the player side. |
| build_size_startup_budgets | directstorage_io | dependency | 3 | yes | Compressed packages only reach the CPU fast if the IO path can saturate the device; DirectStorage is the Windows mechanism for that. |
| cascaded_shadow_maps | distance_field_shadows | complement | 1 | yes | В Unreal Engine каскадные карты могут обслуживать ближнюю область, а Distance Field Shadows — область за пределом дистанции каскадов. Совместимость зависит от выбранного пути рендера; снижение стоимости не гарантируется. |
| cascaded_shadow_maps | screen_space_contact_shadows | complement | 1 | yes | Contact shadows add the detail that a wide cascade cannot resolve. |
| cascaded_shadow_maps | static_shadow_caching | complement | 1 | yes | Caching static casters removes most of the per-frame cascade cost. |
| cascaded_shadow_maps | virtual_shadow_maps | alternative | 1 | yes | UE5 VSM replaces CSM; Epic lists 'Cascaded Shadow Maps (CSMs)' among the methods VSM replaces. |
| chunked_procedural_terrain | heightmap_compression | complement | 1 | yes | Chunked storage is what makes it practical to compress and store only the chunks that were actually visited. |
| chunked_procedural_terrain | terrain_generation_streaming_budget | complement | 1 | yes | Chunks define the unit; the budget defines how many can be produced per second. They must be designed together. |
| client_prediction_reconciliation | deterministic_lockstep | alternative | 1 | yes | Lockstep removes misprediction entirely by never predicting - everyone waits. Overwatch explicitly declined full RTS-style determinism and relies on server correction instead. |
| client_prediction_reconciliation | headless_dedicated_server | dependency | 3 | yes | Метод «client_prediction_reconciliation» требует предварительного метода «headless_dedicated_server». |
| client_prediction_reconciliation | runtime_security_budget | risk | 2 | yes | Prediction means the client runs authoritative simulation code and knows more than it should; Riot's answer is server authority over the outcome, never trusting the client's view of the world. |
| client_prediction_reconciliation | tickrate_budgeting | dependency | 3 | yes | The replay window is measured in command frames, so the tick rate directly sets how many frames of input must be stored and re-simulated. |
| cloth_baked_animation | destruction_geometry_cache | overlap | 1 | yes | Same principle - pre-authored states played back instead of runtime simulation - applied to damage rather than cloth. |
| cloth_baked_animation | hair_cards_lod | overlap | 1 | yes | Both are LOD fallbacks replacing a per-element simulation with pre-authored approximations. |
| cloth_constraint_simulation | cloth_baked_animation | alternative | 2 | yes | Решатель и подготовленное движение — альтернативы для одного участка ткани. |
| cloth_constraint_simulation | fixed_timestep_physics | dependency | 3 | yes | Spring-based cloth is timestep-sensitive; a stable fixed step or substepping is required to avoid stretching and explosions. |
| cloth_constraint_simulation | hair_strand_simulation | overlap | 1 | yes | Both are per-entity soft-body solves with LOD and budget controls; skills and budget policy transfer, solvers do not. |
| cloth_constraint_simulation | physics_lod_sleeping | complement | 1 | yes | The same disable-by-distance policy that parks rigid bodies also parks cloth instances. |
| collision_layer_matrix | npc_perception_budget | overlap | 1 | yes | Both are filtering systems where a wrongly set bit silently removes behaviour with no error. |
| collision_layer_matrix | physics_lod_sleeping | complement | 1 | yes | Sleeping and layer filtering are both ways of removing pairs from the simulation, and both need care to not remove gameplay-relevant pairs. |
| collision_layer_matrix | runtime_fracture_budget | complement | 1 | yes | Debris should generally not collide with debris; a layer bit is the cheapest way to make that true. |
| composition_bootstrap_architecture | ai_director_pacing | complement | 1 | yes | A director/significance system reads and writes entity state through the component model, so the model's access conventions determine how easy it is. |
| composition_bootstrap_architecture | ecs_data_oriented_crowd | dependency | 3 | yes | A full ECS/data-oriented architecture is the same composition decision taken to its performance-oriented conclusion; you cannot adopt the crowd approach without the architectural one. |
| composition_bootstrap_architecture | multithreaded_physics_jobs | complement | 1 | yes | Jobified physics needs data laid out for parallel access, which the ECS variant of composition provides. |
| composition_bootstrap_architecture | snapshot_slot_saves | risk | 2 | yes | Whatever the entity model is, the save system must be able to reconstruct it: component-graph entity models make consistent snapshots and load-order reconstruction harder, so the save model must be designed with the entity model. |
| crowd_2d_instancing | agent_update_budget | risk | 1 | yes | Батчинг и расписание AI — разные виды работы. Не доказано, что снижение частоты обновления агентов всегда остаётся незаметным при массовой отрисовке одним батчем. |
| crowd_2d_instancing | crowd_instancing_impostors | overlap | 1 | yes | Same batching idea; crowd_2d_instancing is the sprite/quad case, crowd_instancing_impostors is the 3D mesh/impostor case. |
| crowd_2d_instancing | ecs_data_oriented_crowd | complement | 1 | yes | Data-oriented storage makes writing the instance buffer a single linear pass. |
| crowd_2d_instancing | flipbook_particles | complement | 1 | yes | Flipbook frame index as per-instance data is the shared mechanism for cheap per-agent animation. |
| crowd_instancing_impostors | crowd_2d_instancing | overlap | 1 | yes | Same batching principle applied to sprite quads rather than 3D meshes/impostors. |
| crowd_instancing_impostors | ecs_data_oriented_crowd | complement | 1 | yes | Data-oriented agent storage is what makes writing instance buffers cheap at crowd scale. |
| crowd_instancing_impostors | hair_cards_lod | overlap | 1 | yes | Both replace expensive per-element geometry (strands / skinned meshes) with card approximations at distance; Epic documents cards as the traditional real-time fallback. |
| data_driven_ability_system | ability_visual_effect_budget | complement | 1 | yes | Gameplay Cues are the join between the ability system and VFX; because cues are tag-matched and unreliable, an unbounded cue set is an unbounded VFX budget. |
| deferred_forward_plus_choice | bindless_uber_shaders | risk | 2 | yes | Uber-shader/bindless material models interact strongly with G-buffer packing and permutations. |
| deferred_forward_plus_choice | depth_prepass_early_z | complement | 1 | yes | A depth prepass reduces forward overdraw, which is forward+'s main weakness. |
| deferred_forward_plus_choice | dynamic_light_priority_budget | dependency | 3 | yes | Light budgets are expressed through whichever architecture is chosen. |
| deferred_forward_plus_choice | tiled_clustered_light_culling | complement | 1 | yes | Clustering is the technique that makes both deferred and forward+ scale to many lights. |
| delta_compression_state | client_prediction_reconciliation | overlap | 1 | yes | Both depend on the same acknowledgement bookkeeping; input windows and state deltas share an ack stream. |
| delta_compression_state | deterministic_lockstep | alternative | 1 | yes | Lockstep compresses by sending commands instead of state - the extreme end of the same idea - and trades input delay for it. |
| delta_compression_state | headless_dedicated_server | dependency | 3 | yes | The delta baseline state lives on the authoritative server, so server memory and CPU planning are part of this decision. |
| delta_compression_state | network_relevancy_priority | dependency | 3 | yes | Метод «delta_compression_state» требует предварительного метода «network_relevancy_priority». |
| delta_compression_state | tickrate_budgeting | risk | 2 | yes | Delta cost is per tick; doubling tick rate doubles delta production work even if bandwidth per packet halves. |
| depth_prepass_early_z | deferred_forward_plus_choice | dependency | 3 | yes | The value of the prepass depends on whether the renderer is forward (high overdraw) or deferred. |
| depth_prepass_early_z | hiz_software_occlusion | complement | 1 | yes | Both attack work that will not be visible; Hi-Z works at object level, early-Z at fragment level. |
| depth_prepass_early_z | meshlet_pipeline_adoption | overlap | 1 | yes | GPU-driven meshlet culling subsumes part of what a prepass achieves. |
| destruction_geometry_cache | fixed_timestep_physics | risk | 2 | yes | A cache recorded at one timestep and replayed at another will drift or pop; the bake step and runtime step must agree. |
| destruction_geometry_cache | physics_lod_sleeping | complement | 1 | yes | Fragments that have come to rest should be parked by the same deactivation policy as other rigid bodies; otherwise the cache saving is lost to still-simulating debris. |
| destruction_geometry_cache | runtime_fracture_budget | complement | 1 | yes | Caching removes cost from the steady state; a runtime fracture budget still bounds the parts that must stay live. They solve different halves of the same problem. |
| destruction_geometry_cache | runtime_fracture_budget | overlap | 1 | yes | Both are budget-oriented destructible policies; if you already bound live fracture tightly you may not need caching, and vice versa. |
| deterministic_lockstep | multithreaded_physics_jobs | risk | 3 | yes | Параллельная физика требует детерминированного порядка и математики: иначе результат зависит от планировщика и lockstep расходится. Проблема условная, а не запрет всех многопоточных реализаций физики. |
| deterministic_lockstep | runtime_security_budget | complement | 1 | yes | Out-of-sync detection is anti-cheat for free, but it replaces detection-and-ban with stop-the-game, which is a different product decision. |
| deterministic_lockstep | tickrate_budgeting | overlap | 1 | yes | A 'turn' is a tick with an explicit delivery deadline; the budgeting problem is the same but the cost of missing the budget is a stall rather than a hitch. |
| differential_patch_pipeline | async_loading_pipeline | risk | 2 | yes | Reordering assets to improve load order is a patch-size regression; the two optimisations directly conflict and must be traded off explicitly. |
| differential_patch_pipeline | directstorage_io | overlap | 1 | yes | Both are about the cost of moving bytes from disk into the game; one optimises the first delivery, the other the per-load path. |
| differential_patch_pipeline | mesh_index_optimization | risk | 2 | yes | Re-encoding every mesh in a build changes the bytes of every mesh, which defeats chunk matching even though almost nothing changed visually. |
| differential_patch_pipeline | world_partition_streaming | risk | 2 | yes | Streaming units and downloadable units are not the same thing; if chunk assignment follows the wrong one, a small content change invalidates a large download. |
| directstorage_io | async_compute_overlap | risk | 3 | yes | GPU-декомпрессия и рендер/compute могут конкурировать за ресурсы. |
| directstorage_io | async_loading_pipeline | complement | 2 | yes | DirectStorage может обслуживать запросы асинхронного загрузчика. |
| directstorage_io | async_loading_pipeline | dependency | 3 | yes | DirectStorage only pays off if the loading layer can keep many requests in flight; the two must be designed together. |
| directstorage_io | build_size_startup_budgets | complement | 1 | yes | Cheaper decompression changes the tradeoff between storing assets compressed and reading them raw, which is an install-size decision as much as a load-time one. |
| directstorage_io | differential_patch_pipeline | overlap | 1 | yes | Both concern moving bytes from disk into the game efficiently; one optimises the delivery, the other the per-load path, and both are affected by how assets are packed and compressed. |
| directstorage_io | terrain_generation_streaming_budget | dependency | 3 | yes | When a streamed or generated world is IO-bound, the achievable bytes per second is the ceiling on the streaming budget. |
| directstorage_io | virtual_texturing | complement | 2 | yes | Очереди I/O могут подавать тайлы виртуальных текстур. |
| distance_field_shadows | build_size_startup_budgets | complement | 1 | yes | Generated distance fields are cooked data: they add to install size and to the atlas memory budget in the same way compressed textures do. |
| distance_field_shadows | gpu_instancing_vegetation | complement | 1 | yes | Instanced static meshes use instanced distance fields; the foliage tool's Affect Distance Field Lighting flag is what decides whether a foliage type participates, and getting it wrong overflows the tile culling buffer. |
| distance_field_shadows | sdf_global_illumination | dependency | 3 | yes | Метод «distance_field_shadows» требует предварительного метода «sdf_global_illumination». |
| distance_field_shadows | virtual_geometry_clusters | risk | 2 | yes | A virtualized-geometry pipeline already owns triangle-scale LOD and its own shadow approach; adding a second, offline-generated scene representation duplicates build time and memory. |
| distance_field_shadows | world_partition_streaming | risk | 2 | yes | Fields are generated offline, so any world that streams actors in and out must ensure the streamed content has fields built and resident; a missing field is a missing shadow, not an error. |
| dynamic_light_priority_budget | deferred_forward_plus_choice | complement | 1 | yes | Forward+ is the architecture that made huge light counts practical without a G-buffer. |
| dynamic_light_priority_budget | light_range_attenuation_lod | complement | 1 | yes | Distance-based simplification reduces the number of lights that need to be in the list at all. |
| dynamic_light_priority_budget | selective_ray_traced_effects | risk | 2 | yes | Adding RT shadows/GI per light multiplies the per-light cost and invalidates a purely-raster light budget. |
| dynamic_light_priority_budget | tiled_clustered_light_culling | dependency | 3 | yes | Priority budgeting is a policy layered on top of the culling structure. |
| dynamic_resolution_scaling | quality_tier_scalability | complement | 1 | yes | Static tiers set the range; DRS moves within it. |
| dynamic_resolution_scaling | temporal_upscaling | complement | 1 | yes | DRS supplies a varying input resolution; the temporal upscaler reconstructs it. |
| dynamic_resolution_scaling | temporal_upscaling | dependency | 3 | yes | Метод «dynamic_resolution_scaling» требует предварительного метода «temporal_upscaling». |
| ecs_data_oriented_crowd | composition_bootstrap_architecture | complement | 1 | yes | ECS is the extreme form of composition; the Component pattern's caveats (communication, ordering) apply to both. |
| ecs_data_oriented_crowd | multithreaded_physics_jobs | complement | 1 | yes | Both rely on a job system and on declaring read/write access for safe parallelism. |
| fixed_timestep_physics | cloth_constraint_simulation | complement | 1 | yes | Spring-based cloth stretches and explodes under variable deltas; it needs a stable step. |
| fixed_timestep_physics | multithreaded_physics_jobs | complement | 1 | yes | A fixed step makes the physics tick a predictable unit of work, which is what makes it schedulable and async-safe. |
| fixed_timestep_physics | raycast_vehicle_physics | dependency | 3 | yes | Suspension feel is timestep-dependent; without a fixed step, handling changes with framerate. |
| flipbook_particles | gpu_particle_simulation | alternative | 1 | yes | The bake is the fallback when GPU simulation is unaffordable on the target device; Epic frames it exactly this way. |
| flipbook_particles | particle_pooling | complement | 1 | yes | Flipbook emitters are usually the cheap, numerous ones, so they benefit most from pooling and instance caps. |
| flipbook_particles | screen_space_water_simple | overlap | 1 | yes | Both replace a real simulation with a cheaper approximation that holds up only under constrained viewing conditions. |
| flipbook_particles | sprite_particle_atlas | dependency | 3 | yes | Flipbooks are the animated case of the sprite atlas; the same power-of-two and packing discipline applies. |
| flow_field_pathing | crowd_instancing_impostors | complement | 1 | yes | Flow fields make very large agent counts feasible on the movement side; instancing makes them feasible on the render side. |
| flow_field_pathing | navmesh_tiling_streaming | alternative | 1 | yes | Polygon navmesh + per-agent A* vs grid flow fields. Flow fields win when many agents share few goals; navmesh wins for few agents with individual long paths and for precise polygon-level movement. |
| flow_field_pathing | rvo_local_avoidance | complement | 1 | yes | Flow fields give global direction; local avoidance handles agent-agent and agent-wall contact. The chapter explicitly relies on physics/steering once agents can move in any direction. |
| froxel_volumetric_fog | async_compute_overlap | complement | 1 | yes | Wronski explicitly suggests running the pass on async compute once shadow maps are ready. |
| froxel_volumetric_fog | deferred_forward_plus_choice | dependency | 3 | yes | Метод «froxel_volumetric_fog» требует предварительного метода «deferred_forward_plus_choice». |
| froxel_volumetric_fog | temporal_upscaling | risk | 2 | yes | Epic notes TSR's flicker analysis can be triggered by fog/clouds ('TSR.Flickering.Luminance' pass). |
| froxel_volumetric_fog | volumetric_half_resolution | complement | 1 | yes | The froxel grid already IS a reduced-resolution representation; the two are the same idea at different granularity. |
| full_path_tracing_pipeline | hardware_raytraced_gi | alternative | 1 | yes | Cached-surface RT GI is the real-time compromise; PT is the reference. |
| full_path_tracing_pipeline | ml_frame_generation | complement | 1 | yes | CDPR and Remedy both ship path tracing together with frame generation - the two are practically coupled in shipped titles. |
| full_path_tracing_pipeline | path_tracing_sample_denoiser_budget | dependency | 3 | yes | Without a spp/denoiser budget the mode is not interactive. |
| full_path_tracing_pipeline | selective_ray_traced_effects | dependency | 3 | yes | Метод «full_path_tracing_pipeline» требует предварительного метода «selective_ray_traced_effects». |
| full_path_tracing_pipeline | temporal_upscaling | dependency | 3 | yes | Метод «full_path_tracing_pipeline» требует предварительного метода «temporal_upscaling». |
| gerstner_fft_water | flipbook_particles | overlap | 1 | yes | Both are 'bake an expensive simulation into a texture' strategies, used for water displacement and for VFX respectively. |
| gerstner_fft_water | gpu_particle_simulation | overlap | 1 | yes | Both push work onto the GPU and both end up bounded by bandwidth/overdraw rather than by raw ALU. |
| gerstner_fft_water | planar_reflection_budget | complement | 1 | yes | Water is the main consumer of reflection budget; the two must be budgeted together. |
| gerstner_fft_water | screen_space_water_simple | alternative | 1 | yes | Cheap screen-space/normal-map water is the fallback when the GPU budget cannot accommodate a spectrum water pipeline. |
| gpu_compute_culling | baked_occlusion_culling | alternative | 1 | yes | Two answers to the same question: runtime depth-pyramid culling vs offline PVS. Runtime scales to dynamic worlds; baked is cheaper but static-only. |
| gpu_compute_culling | distance_field_shadows | risk | 2 | yes | Shadow cost in a GPU-driven pipeline scales with shadow pixels and lights per pixel, not scene complexity - so culling savings do not automatically translate to shadow passes. |
| gpu_compute_culling | gpu_instancing_vegetation | complement | 1 | yes | Cluster culling is what lets an instanced-vegetation batch be culled at sub-instance granularity instead of culling the whole batch. |
| gpu_compute_culling | mesh_index_optimization | complement | 1 | yes | Cluster/meshlet locality only pays if the index order within each cluster is cache-optimal; the two are built in the same preprocessing pass. |
| gpu_compute_culling | mesh_index_optimization | dependency | 3 | yes | Метод «gpu_compute_culling» требует предварительного метода «mesh_index_optimization». |
| gpu_compute_culling | virtual_geometry_clusters | overlap | 1 | yes | Nanite is GPU culling plus a cluster LOD DAG plus a software rasteriser; gpu_compute_culling is the shared foundation. |
| gpu_instancing_vegetation | distance_field_shadows | risk | 2 | yes | Enabling 'Affect Distance Field Lighting' on dense foliage can overflow the tile culling buffer and cause artefacts, so it is off by default. |
| gpu_instancing_vegetation | gpu_compute_culling | dependency | 3 | yes | Per-instance and per-cluster culling on the GPU is what makes large instance counts affordable. |
| gpu_instancing_vegetation | impostors_billboards | complement | 1 | yes | Imposters are the terminal LOD for instanced foliage at distance; Unreal's instancing HLOD layer explicitly targets them. |
| gpu_instancing_vegetation | vegetation_atlas_lod | complement | 1 | yes | Instancing reduces submission; atlasing/LOD reduces state changes and per-instance material cost. You need both. |
| gpu_lightmap_baking | full_path_tracing_pipeline | overlap | 1 | yes | Both use the same RT/GI kernel; Epic explicitly shares architecture between Path Tracer and GPU Lightmass. |
| gpu_lightmap_baking | lightmap_atlas_baking | dependency | 3 | yes | It is the same bake, moved to a different processor. |
| gpu_lightmap_baking | lightmap_compression_streaming | complement | 1 | yes | Faster bakes are more valuable once large lightmap sets are being produced. |
| gpu_meshlet_culling_budget | async_compute_overlap | unknown | 2 | yes | No verified source measures meshlet culling on an async queue. |
| gpu_meshlet_culling_budget | bindless_uber_shaders | complement | 1 | yes | Surviving meshlets are only cheap if they can be drawn without per-material state changes. |
| gpu_meshlet_culling_budget | hiz_software_occlusion | complement | 1 | yes | Meshlet bounds are tested against the same Hi-Z pyramid used for object-level occlusion. |
| gpu_meshlet_culling_budget | meshlet_pipeline_adoption | dependency | 3 | yes | Per-meshlet culling requires the meshlet pipeline; Khronos notes that without a measured win the pipeline itself may not pay off. |
| gpu_particle_simulation | particle_pooling | complement | 1 | yes | CPU-пулинг и GPU-симуляция затрагивают разную работу: пулинг устраняет аллокации при создании систем, симуляция переносит расчёт на GPU. Абстрактные скидки не перемножаются. |
| gpu_particle_simulation | screen_space_water_simple | overlap | 1 | yes | Both are GPU-side approximations that trade physical accuracy for fill-rate-bounded cost. |
| gpu_particle_simulation | sprite_particle_atlas | complement | 1 | yes | GPU simulation raises particle counts, which makes per-particle texture binding a real cost; atlases remove it. |
| gpu_procedural_placement | chunked_procedural_terrain | complement | 1 | yes | Chunks give placement a natural scope and a deterministic key. |
| gpu_procedural_placement | gpu_instancing_vegetation | dependency | 3 | yes | Placement produces instance transforms; without instancing the output cannot be rendered. |
| gpu_procedural_placement | hierarchical_lod | overlap | 1 | yes | Both address the far field: HLOD bakes static proxies, runtime placement generates live content. Where placement runs continuously, HLOD proxies can go stale against it. |
| gpu_procedural_placement | lightmap_atlas_baking | risk | 2 | yes | Запечённые данные существуют только для заранее известной геометрии, поэтому размещаемые в рантайме объекты остаются без лайтмапа. Ограничение распространяется на процедурную часть сцены: остальные объекты могут оставаться запечёнными. |
| gpu_procedural_placement | terrain_clipmap | complement | 1 | yes | Slope/altitude legality masks derive from the same heightfield that drives the terrain LOD. |
| gpu_procedural_placement | world_partition_streaming | complement | 1 | yes | Placement scoped to streaming cells is what makes it affordable at open-world scale. |
| gpu_skinning_compute | animation_compression | complement | 1 | yes | Smaller/faster-decompressing clips feed the evaluation stage that produces the matrices the skinner consumes; compression affects CPU, skinning affects GPU. |
| gpu_skinning_compute | animation_lod_budget | complement | 1 | yes | Skin Cache removes per-vertex deformation cost; the animation budget allocator removes evaluation cost. You normally need both for crowds, because the cache does not make animation evaluation cheaper. |
| gpu_skinning_compute | motion_matching | risk | 2 | yes | Motion matching jumps between arbitrary frames, so poses can change abruptly; if the skin cache budget is exceeded the fallback path makes quality non-deterministic under exactly the conditions where motion matching is most visible. |
| gpu_skinning_compute | normal_bake_retopology_pipeline | risk | 2 | yes | Retopology decisions set vertex counts and influence counts, which directly set Skin Cache VRAM occupancy and the 4/8/12-influence path a mesh takes. |
| hair_cards_lod | cloth_baked_animation | overlap | 1 | yes | Both are bake-away-the-simulation strategies selected by distance/importance. |
| hair_cards_lod | crowd_instancing_impostors | overlap | 1 | yes | Both are 'replace expensive geometry with a cheap textured proxy at distance' and share the pop-mitigation problem. |
| hair_cards_lod | hair_strand_simulation | complement | 1 | yes | Cards are the LOD fallback for strands; a complete hair solution is strands-near + cards-far, not one or the other. |
| hair_strand_simulation | cloth_constraint_simulation | overlap | 1 | yes | Both are per-entity soft-body solves with LOD and budget controls; the discipline transfers, the solvers do not. |
| hair_strand_simulation | crowd_instancing_impostors | alternative | 1 | yes | For distant characters, an impostor/card proxy is a cheaper answer than a strand budget that scales with character count. |
| hair_strand_simulation | fixed_timestep_physics | risk | 2 | yes | Strand physics is a spring system; variable timesteps produce jitter and stretching. |
| hair_strand_simulation | hair_cards_lod | alternative | 2 | yes | Альтернативные представления одного LOD волос; разные LOD могут использовать разные представления. |
| hardware_raytraced_gi | deferred_forward_plus_choice | dependency | 3 | yes | Метод «hardware_raytraced_gi» требует предварительного метода «deferred_forward_plus_choice». |
| hardware_raytraced_gi | full_path_tracing_pipeline | risk | 2 | yes | Moving from cached-surface RT GI to full path tracing changes cost by an order of magnitude; CDPR gates it to top-tier GPUs and ships it off by default. |
| hardware_raytraced_gi | screen_space_gi | overlap | 1 | yes | SSGI is a cheaper subset that is often combined with, rather than replacing, hardware RT GI. |
| hardware_raytraced_gi | sdf_global_illumination | alternative | 1 | yes | Distance-field (software) tracing is Epic's documented fallback when hardware RT is unavailable. |
| hardware_raytraced_gi | selective_ray_traced_effects | dependency | 3 | yes | Метод «hardware_raytraced_gi» требует предварительного метода «selective_ray_traced_effects». |
| hardware_raytraced_gi | temporal_radiance_cache | complement | 1 | yes | Temporal accumulation of probe radiance is what makes the per-frame ray count affordable. |
| hardware_raytraced_gi | temporal_upscaling | dependency | 3 | yes | Метод «hardware_raytraced_gi» требует предварительного метода «temporal_upscaling». |
| hardware_raytraced_gi | voxel_cone_tracing | alternative | 1 | yes | Voxel cone tracing is an older, non-RT approach to the same one/two-bounce diffuse GI problem. |
| headless_dedicated_server | deterministic_lockstep | alternative | 1 | yes | Lockstep peer-to-peer removes the dedicated server cost entirely - which is exactly why RTS games chose it - at the price of input delay and no host authority. |
| headless_dedicated_server | managed_gc_alloc_budget | risk | 2 | yes | A headless server running hundreds of instances makes any per-frame allocation or GC pause visible as a hitch multiplied across every game on the host. |
| headless_dedicated_server | network_relevancy_priority | dependency | 3 | yes | Relevancy cost is paid on the dedicated server, so server CPU density决定了 relevancy is worth engineering. |
| headless_dedicated_server | runtime_security_budget | complement | 1 | yes | The dedicated server is where the authoritative anti-cheat and server-authoritative validation live; EAC requires a server interface and per-client registration. |
| headless_dedicated_server | tickrate_budgeting | dependency | 3 | yes | Server tick rate and instance density are the same equation: Riot derives a 2.34 ms frame budget from 128 tick and 3 games per core. |
| heightmap_compression | build_size_startup_budgets | dependency | 3 | yes | Terrain is usually the biggest single contributor to build size, so its codec choice dominates the distribution budget. |
| heightmap_compression | chunked_procedural_terrain | alternative | 1 | yes | Compress-and-store vs generate-on-demand: the former costs disk and preprocessing, the latter costs runtime CPU/GPU and determinism. |
| heightmap_compression | neural_texture_compression | unknown | 2 | yes | Learned, per-material compression of texture sets is the same bet applied to texels rather than height samples; both trade encoder time and tooling risk for rate. |
| heightmap_compression | terrain_clipmap | complement | 1 | yes | Regular-grid compression is what lets a clipmap fit in core memory; the two are one design. |
| hierarchical_lod | distance_field_shadows | risk | 2 | yes | Epic notes 'Allow Distance Fields' can be disabled for HLOD proxies purely to save memory, which changes what the distance-field shadow/AO system can see at distance. |
| hierarchical_lod | impostors_billboards | complement | 1 | yes | The Instancing layer type is explicitly described as ideal for imposter meshes, and has an 'Include Imposters' merge option. |
| hierarchical_lod | vegetation_atlas_lod | complement | 1 | yes | Baked proxy atlas settings (target lightmap resolution, gutter size, texture binning) are the same parameter family as vegetation atlas packing. |
| hierarchical_lod | virtual_geometry_clusters | overlap | 1 | yes | If the whole world is Nanite, per-cluster LOD already provides sub-linear geometry scaling; HLOD then competes with rather than complements Nanite and may be unnecessary for opaque rigid geometry. |
| hierarchical_lod | world_partition_streaming | dependency | 3 | yes | HLOD exists to visualise unloaded World Partition cells; without partitioning there is nothing to proxy. |
| hiz_software_occlusion | froxel_volumetric_fog | risk | 2 | yes | Volumetric fog needs depth for every pixel, so aggressively culled geometry can produce shadows/fog that disagree with the visible set. |
| hiz_software_occlusion | meshlet_pipeline_adoption | complement | 1 | yes | Remedy's GPU-driven pipeline combines mesh shaders with 'meshlet culling' and 'single-pixel occlusion precision'. |
| impostors_billboards | vegetation_atlas_lod | dependency | 3 | yes | Impostor captures are stored in and sampled from an atlas; the two are one asset pipeline. |
| irradiance_volume_probes | hardware_raytraced_gi | alternative | 1 | yes | Dynamic GI removes the bake but costs far more GPU. |
| irradiance_volume_probes | lightmap_atlas_baking | complement | 1 | yes | Lightmaps handle static surfaces, probes handle dynamic objects - the classic shipped pairing. |
| irradiance_volume_probes | lightmap_atlas_baking | dependency | 3 | yes | Метод «irradiance_volume_probes» требует предварительного метода «lightmap_atlas_baking». |
| irradiance_volume_probes | temporal_radiance_cache | overlap | 1 | yes | Both are spatial caches of irradiance; a radiance cache is the dynamic, temporal version. |
| lag_compensation_rewind | client_prediction_reconciliation | complement | 2 | yes | Серверная проверка и предсказание на клиенте могут сосуществовать. |
| lag_compensation_rewind | client_prediction_reconciliation | dependency | 3 | yes | Метод «lag_compensation_rewind» требует предварительного метода «client_prediction_reconciliation». |
| lag_compensation_rewind | network_relevancy_priority | dependency | 3 | yes | Метод «lag_compensation_rewind» требует предварительного метода «network_relevancy_priority». |
| lag_compensation_rewind | runtime_security_budget | risk | 2 | yes | Rewind is the classic latency-abuse surface; Riot's documented answer is a tuned bound on how far the server will rewind. |
| lag_compensation_rewind | subtick_networking | complement | 2 | yes | Метки могут уточнять историческую проверку; rewind работает и без sub-tick. |
| lag_compensation_rewind | subtick_networking | dependency | 3 | yes | Evaluating an action at a sub-tick instant requires reconstructing that instant, which is rewind. Sub-tick is a consumer of this machinery, not a replacement. |
| lag_compensation_rewind | tickrate_budgeting | risk | 2 | yes | History length in seconds times tick rate is the history buffer size, so raising tick rate raises rewind memory and rewind CPU linearly. |
| light_range_attenuation_lod | dynamic_light_priority_budget | dependency | 3 | yes | Метод «light_range_attenuation_lod» требует предварительного метода «dynamic_light_priority_budget». |
| light_range_attenuation_lod | quality_tier_scalability | complement | 1 | yes | LOD distances are a natural per-tier knob. |
| light_range_attenuation_lod | shadow_caster_2d_limits | overlap | 1 | yes | Both are about limiting how many casters/sources participate. |
| lightmap_2d_baking | dynamic_light_priority_budget | complement | 1 | yes | The hybrid variant is exactly a priority budget: baked = free, dynamic = limited count. |
| lightmap_2d_baking | lightmap_atlas_baking | overlap | 1 | yes | Same idea in 3D: precompute static irradiance into an atlas. The 2D case is much simpler because there is no UV-unwrap problem. |
| lightmap_2d_baking | post_effect_selective | complement | 1 | yes | Освещение и постобработка — независимые проходы: каждый учитывается своей стоимостью. Дополнительного бонуса только от совместного выбора нет. |
| lightmap_2d_baking | shadow_caster_2d_limits | complement | 1 | yes | Whatever is not baked still needs a per-light budget; Godot exposes Max Distance and PCF5/PCF13 for that. |
| lightmap_atlas_baking | hardware_raytraced_gi | alternative | 3 | yes | Условная альтернатива для одной области освещения: запечённый свет и полностью динамическое освещение решают одну задачу разными способами. Смешанная сцена допустима — статичные объекты могут оставаться запечёнными, поэтому универсального запрета пара не образует. |
| lightmap_atlas_baking | lightmap_compression_streaming | dependency | 3 | yes | Without compression/streaming the disk and VRAM cost is unshippable on large worlds. |
| lightmap_atlas_baking | static_shadow_caching | overlap | 1 | yes | Baked shadows are the extreme form of static shadow caching. |
| lightmap_compression_streaming | lightmap_atlas_baking | complement | 1 | yes | Nothing to compress/stream without baked atlases. |
| lightmap_compression_streaming | quality_tier_scalability | complement | 1 | yes | Lightmap resolution per tier is a standard memory knob. |
| managed_gc_alloc_budget | tickrate_budgeting | dependency | 3 | yes | Метод «managed_gc_alloc_budget» требует предварительного метода «tickrate_budgeting». |
| managed_gc_alloc_budget | tickrate_budgeting | risk | 2 | yes | A GC pause longer than one tick interval directly breaks the derived per-frame server budget (Riot's 2.34 ms target leaves no room for one). |
| mesh_index_optimization | build_size_startup_budgets | complement | 1 | yes | Encoded buffers reduce both install size and the number of bytes the loader must read; whether that also reduces load time depends on the decode-vs-IO tradeoff. |
| mesh_index_optimization | directstorage_io | risk | 2 | yes | On very fast storage, decoding compressed buffers on the CPU can cost more than the IO it saves; the tradeoff must be measured against the actual storage path. |
| mesh_index_optimization | hierarchical_lod | complement | 1 | yes | The simplifier and its relative-error metric are what generate the LOD chain that HLOD and automatic LOD systems consume. |
| mesh_index_optimization | virtual_geometry_clusters | complement | 1 | yes | Meshlet generation is the shared primitive: both cluster culling and virtualised geometry need clusters that maximise internal vertex reuse and minimise radius. |
| meshlet_pipeline_adoption | async_compute_overlap | unknown | 2 | yes | No source found that measures mesh-shader work on an async queue. |
| meshlet_pipeline_adoption | gpu_meshlet_culling_budget | complement | 1 | yes | The pipeline exists to make per-meshlet culling possible; adoption without culling is the case Khronos warns may not win. |
| ml_frame_generation | client_prediction_reconciliation | risk | 2 | yes | Генерация кадров добавляет задержку и может давать визуальные артефакты при пересборке состояния. Генерация и предсказание не являются универсально несовместимыми алгоритмами. |
| ml_frame_generation | dynamic_resolution_scaling | risk | 2 | yes | Varying render resolution changes the generator's input statistics; the two heuristics can fight. |
| ml_frame_generation | quality_tier_scalability | complement | 1 | yes | Multiplier/mode selection should be exposed as a user-facing tier. |
| ml_frame_generation | temporal_upscaling | dependency | 3 | yes | Метод «ml_frame_generation» требует предварительного метода «temporal_upscaling». |
| motion_matching | animation_compression | complement | 1 | yes | Motion matching ships an order of magnitude more animation than a state machine; without compression the database is unshippable, and LMM exists because 'the memory usage of such methods generally scales linearly with the amount of data used'. |
| motion_matching | animation_compression | risk | 2 | yes | Риск относится к конкретной степени сжатия: искажённые позы ухудшают точность поиска в базе движений. Универсальной несовместимости motion matching и сжатия анимаций нет. |
| motion_matching | animation_lod_budget | dependency | 3 | yes | Метод «motion_matching» требует предварительного метода «animation_lod_budget». |
| motion_matching | animation_lod_budget | hard_conflict | 3 | yes | Root motion is mandatory for UE motion matching but also blocks parallel animation update, removing the main thread-scaling lever; you are left with tick-rate throttling, which throttles responsiveness. |
| motion_matching | data_driven_ability_system | complement | 1 | yes | A tag-driven ability system can swap Pose Search Normalization Sets on gameplay events (e.g. combat vs exploration databases), which is the natural integration point between the two systems. |
| motion_matching | normal_bake_retopology_pipeline | overlap | 1 | yes | Both are 'capture more than you need, then reduce' pipelines; they differ in that one reduces geometry/texture offline and the other reduces animation at query time. |
| multithreaded_physics_jobs | ecs_data_oriented_crowd | overlap | 1 | yes | Both require data laid out for parallel access; the refactor is largely the same work. |
| multithreaded_physics_jobs | fixed_timestep_physics | dependency | 3 | yes | A predictable fixed step is what makes the physics tick schedulable and safe to run off-thread. |
| multithreaded_physics_jobs | physics_lod_sleeping | complement | 1 | yes | Sleeping shrinks the parallel workload, so it still pays even after jobification. |
| navmesh_tiling_streaming | runtime_fracture_budget | complement | 1 | yes | Destruction requires navmesh rebake; R6 Siege documents navlink updates for trapdoors and breachable walls. |
| navmesh_tiling_streaming | time_sliced_pathfinding | complement | 1 | yes | Both bound navigation cost per frame; tiling bounds memory and rebake scope, time-slicing bounds query cost. |
| network_relevancy_priority | delta_compression_state | complement | 1 | yes | Relevancy и дельта-кодирование уменьшают разные части трафика: первое сокращает набор передаваемых объектов, второе — размер каждого обновления. Нужна единая модель набора и байтов; сравнение и упаковка добавляют CPU. |
| network_relevancy_priority | deterministic_lockstep | alternative | 1 | yes | Lockstep avoids replication entirely by sending only commands, which sidesteps relevancy - at the cost of an input delay and strict determinism. |
| network_relevancy_priority | headless_dedicated_server | complement | 1 | yes | The relevancy pass runs on the authoritative server; a listen-server topology changes who pays the cost and who gets the latency advantage. |
| network_relevancy_priority | lag_compensation_rewind | risk | 2 | yes | Rewinding requires retained history for the rewound entity; if relevancy culled or never sent that entity's state, the rewind silently degrades. |
| network_relevancy_priority | tickrate_budgeting | risk | 2 | yes | Relevancy cost is paid per tick, so raising tick rate multiplies it. Riot's 2.34 ms/frame server budget leaves essentially no room for an O(actors x clients) scan. |
| neural_texture_compression | build_size_startup_budgets | complement | 1 | yes | Texture bytes are usually the largest single term in both install size and patch size; a lower texture rate reduces both. |
| neural_texture_compression | directstorage_io | risk | 2 | yes | If the format is sampled or transcoded on the GPU, it competes for the same decompression and bandwidth budget that DirectStorage is meant to saturate. |
| neural_texture_compression | virtual_geometry_clusters | unknown | 2 | yes | Same strategic move in a different domain: replace a fixed-rate representation with a fitted/compressed one and pay decode cost at runtime. Nanite ships; NTC does not yet. |
| neural_texture_compression | virtual_texturing | complement | 1 | yes | Both exist to decouple texel density from resident memory: VT decides which texels are resident, NTC decides how many bytes each texel costs. They compose rather than compete. |
| normal_bake_retopology_pipeline | art_direction_stylization | alternative | 1 | yes | A flat/vector art direction can skip high-to-low baking entirely; choosing stylization early removes this whole pipeline rather than optimising it. |
| normal_bake_retopology_pipeline | gpu_skinning_compute | dependency | 3 | yes | Retopology sets the vertex count and the influence count, which select the 4/8/12-influence path and set Skin Cache VRAM occupancy per character. |
| normal_bake_retopology_pipeline | sprite_sheet_compression | complement | 1 | yes | Baked map sets are the dominant texture memory in a PBR character pipeline, so the texture-compression choice determines whether the bake detail survives to the screen. |
| npc_perception_budget | collision_layer_matrix | complement | 1 | yes | Collision layer filtering reduces which objects perception raycasts must consider. |
| particle_pooling | agent_update_budget | overlap | 1 | yes | Both are 'cap concurrency, recycle the oldest' budget policies applied to different object types. |
| particle_pooling | sprite_particle_atlas | complement | 1 | yes | Pooling removes spawn cost; atlases remove per-instance texture/binding cost. Together they make high effect density affordable. |
| path_tracing_sample_denoiser_budget | full_path_tracing_pipeline | complement | 1 | yes | The budget only exists because path tracing is being used. |
| path_tracing_sample_denoiser_budget | selective_ray_traced_effects | overlap | 1 | yes | The same denoiser stack serves selective RT effects. |
| path_tracing_sample_denoiser_budget | temporal_upscaling | complement | 1 | yes | Both accumulate over time and both fail on disocclusion; they must be tuned together. |
| physics_lod_sleeping | agent_update_budget | overlap | 1 | yes | Significance-driven LOD is the same policy engine applied to AI rather than to rigid bodies. |
| physics_lod_sleeping | runtime_fracture_budget | complement | 1 | yes | Debris that never sleeps will consume the entire destruction budget; sleeping is what makes debris affordable. |
| planar_reflection_budget | crowd_instancing_impostors | overlap | 1 | yes | Both are 'render a cheaper version of the scene into a buffer' techniques with resolution and update-rate budgets. |
| planar_reflection_budget | gpu_particle_simulation | risk | 2 | yes | Transparent particles and reflections interact badly: Doom Eternal needs a dedicated before-water alpha target precisely because of this. |
| planar_reflection_budget | screen_space_gi | unknown | 1 | yes | Экранное GI — непрямое освещение, а не экранные отражения (SSR): утверждение, будто экранное GI уже считает плоские отражения, ошибочно. Запрета пара не образует, но совместная стоимость двух проходов не подтверждена измерением отдельно. |
| planar_reflection_budget | screen_space_water_simple | complement | 1 | yes | Screen-space water and screen-space reflections share the same failure mode (missing off-screen information) and the same mitigation. |
| portal_scene_capture_budget | depth_prepass_early_z | complement | 1 | yes | A depth prepass makes each extra portal render cheaper by removing overdraw. |
| portal_scene_capture_budget | dynamic_resolution_scaling | complement | 1 | yes | DRS can absorb the portal cost dynamically instead of dropping quality permanently. |
| portal_scene_capture_budget | froxel_volumetric_fog | risk | 2 | yes | Volumetrics are computed per view; each portal iteration pays for another froxel volume unless shared. |
| portal_scene_capture_budget | quality_tier_scalability | dependency | 3 | yes | Portal resolution and recursion depth must be tier knobs, or low-end hardware cannot run the mechanic at all. |
| portal_scene_capture_budget | splitscreen_render_budget | hard_conflict | 3 | yes | Both multiply the number of scene renders; split screen + portals is the worst case for the frame budget. |
| post_effect_selective | quality_tier_scalability | dependency | 3 | yes | Selective application is expressed through scalability groups. |
| post_effect_selective | temporal_upscaling | risk | 2 | yes | Effects after the upscaler cost full display resolution - a common hidden budget leak. |
| post_effect_selective | variable_rate_shading | alternative | 1 | yes | VRS achieves a similar saving spatially via hardware rather than by buffer resizing. |
| post_effect_selective | volumetric_half_resolution | overlap | 1 | yes | Same reduced-resolution tactic. |
| pso_precaching_warmup | async_loading_pipeline | complement | 1 | yes | Оба решения уменьшают разные источники пауз: прогрев устраняет компиляцию шейдеров, асинхронная загрузка — ожидание чтения. Ни одно из них не гарантирует отсутствия всех пауз и не даёт постоянного бонуса FPS. |
| pso_precaching_warmup | quality_tier_scalability | risk | 2 | yes | Each quality tier is a different permutation set; the coverage run must visit all of them. |
| pso_precaching_warmup | selective_ray_traced_effects | risk | 2 | yes | Epic states RT PSOs could not be cached in UE 5.0, so RT features reintroduce exactly the hitch this method removes. |
| pso_precaching_warmup | srp_batcher_discipline | complement | 1 | yes | Both are about minimising shader-variant switches: 'In SRP Batcher context, the SetShaderPass is called for each new shader variant.' |
| quality_tier_scalability | hardware_raytraced_gi | complement | 1 | yes | Scalability выбирает реальный набор настроек, а не удешевляет уже рассчитанную трассировку: отдельной скидки к стоимости RT только от наличия тиров нет. |
| quality_tier_scalability | post_effect_selective | complement | 1 | yes | Post-process quality is one of the tiered groups. |
| quality_tier_scalability | splitscreen_render_budget | complement | 1 | yes | Epic explicitly names split screen as a reason to scale graphics. |
| raycast_vehicle_physics | collision_layer_matrix | complement | 1 | yes | Vehicle raycasts should test only drivable surfaces; layer filtering is the cheapest way to guarantee that. |
| raycast_vehicle_physics | fixed_timestep_physics | complement | 1 | yes | Suspension feel and stability are timestep-dependent; without a fixed step, handling changes with framerate. |
| raycast_vehicle_physics | multithreaded_physics_jobs | complement | 1 | yes | Unreal documents async physics support for Chaos Vehicles specifically to improve determinism, which matters for replicated vehicles. |
| raycast_vehicle_physics | vehicle_simulation_lod | complement | 1 | yes | A cheap raycast model is what makes it affordable to run many vehicles and to simulate distant ones at reduced fidelity. |
| rt_effect_resolution_budget | selective_ray_traced_effects | dependency | 3 | yes | There is nothing to budget until an RT effect exists. |
| rt_effect_resolution_budget | temporal_radiance_cache | complement | 1 | yes | Caching is the temporal axis of the same amortisation idea. |
| rt_effect_resolution_budget | volumetric_half_resolution | overlap | 1 | yes | Same reduced-resolution pattern applied to a different pass. |
| runtime_fracture_budget | baked_occlusion_culling | risk | 3 | yes | Изменение геометрии может сделать предвычисленную видимость устаревшей. |
| runtime_fracture_budget | broadphase_spatial_partitioning | dependency | 3 | yes | A few thousand small fragments is precisely the workload a good broadphase exists to absorb; a bad one makes the budget unachievable. |
| runtime_fracture_budget | destruction_geometry_cache | alternative | 2 | yes | Симуляция и воспроизведение кэша решают одну задачу разрушения по-разному. |
| runtime_fracture_budget | navmesh_tiling_streaming | risk | 2 | yes | После разрушения проходимость может измениться; готовая навигация не обязательно описывает новое состояние. |
| runtime_fracture_budget | particle_pooling | complement | 1 | yes | Fragment and debris pools share the same allocation-avoidance discipline as particle pools. |
| runtime_fracture_budget | physics_lod_sleeping | dependency | 3 | yes | Fragments at rest must actually stop costing; without deactivation the fragment cap only delays the stall. |
| runtime_security_budget | headless_dedicated_server | dependency | 3 | yes | Client-server anti-cheat mode requires a server interface, per-client registration on the dedicated server, and server-side event logging. |
| rvo_local_avoidance | fixed_timestep_physics | risk | 2 | yes | Local avoidance is typically non-deterministic and client-authoritative; using it in a deterministic lockstep title creates divergence risk. A fixed physics/simulation timestep is a prerequisite for determinism but does not by itself make avoidance deterministic. |
| rvo_local_avoidance | navmesh_tiling_streaming | complement | 1 | yes | DetourCrowd in the Recast family provides agent movement and collision avoidance alongside tiled navmesh queries. |
| screen_space_contact_shadows | deferred_forward_plus_choice | dependency | 3 | yes | Метод «screen_space_contact_shadows» требует предварительного метода «deferred_forward_plus_choice». |
| screen_space_contact_shadows | dynamic_light_priority_budget | complement | 1 | yes | Contact shadows let you drop expensive real shadow casters from the light budget. |
| screen_space_contact_shadows | screen_space_gi | overlap | 1 | yes | Same screen-space family and artefact class. |
| screen_space_contact_shadows | virtual_shadow_maps | alternative | 1 | yes | VSM's resolution makes contact shadows unnecessary on high tiers. |
| screen_space_gi | deferred_forward_plus_choice | dependency | 3 | yes | Метод «screen_space_gi» требует предварительного метода «deferred_forward_plus_choice». |
| screen_space_gi | hardware_raytraced_gi | complement | 1 | yes | Epic ships SSGI as an additional trace source inside Lumen rather than as a replacement for it. |
| screen_space_gi | irradiance_volume_probes | alternative | 1 | yes | Probe volumes cover off-screen information that SSGI structurally cannot. |
| screen_space_gi | quality_tier_scalability | complement | 1 | yes | SSGI is an obvious low-tier substitute for world-space GI. |
| screen_space_gi | screen_space_contact_shadows | overlap | 1 | yes | Same screen-space-family technique and the same artefact class. |
| screen_space_gi | temporal_upscaling | dependency | 3 | yes | Метод «screen_space_gi» требует предварительного метода «temporal_upscaling». |
| screen_space_water_simple | crowd_instancing_impostors | overlap | 1 | yes | Same philosophy: a cheap proxy selected by distance/importance, judged entirely by whether the transition is noticeable. |
| screen_space_water_simple | flipbook_particles | overlap | 1 | yes | Both replace a real simulation with a cheap, camera-facing approximation that holds up only under constrained viewing conditions. |
| screenspace_light_shafts | froxel_volumetric_fog | complement | 1 | yes | If volumetrics exist, shafts should come from them rather than from a separate hack. |
| screenspace_light_shafts | post_effect_selective | dependency | 3 | yes | Shafts are one of the passes to be tiered and down-res'd. |
| screenspace_light_shafts | volumetric_half_resolution | complement | 1 | yes | Shafts tolerate low resolution well. |
| sdf_global_illumination | distance_field_shadows | complement | 1 | yes | The same distance field serves both GI tracing and long-range shadows. |
| sdf_global_illumination | hardware_raytraced_gi | dependency | 3 | yes | Метод «sdf_global_illumination» требует предварительного метода «hardware_raytraced_gi». |
| sdf_global_illumination | meshlet_pipeline_adoption | risk | 2 | yes | Nanite-style virtualised geometry changes the SDF generation path; Epic ties SDF generation specifically to Static Meshes. |
| sdf_global_illumination | voxel_cone_tracing | overlap | 1 | yes | Both are volumetric approximations; SDF avoids the voxelisation step but carries less material information. |
| selective_ray_traced_effects | full_path_tracing_pipeline | alternative | 1 | yes | Selective RT is the incremental path; full PT is the all-in path. |
| selective_ray_traced_effects | hardware_raytraced_gi | overlap | 1 | yes | RTGI is one of the selectable effects. |
| selective_ray_traced_effects | rt_effect_resolution_budget | complement | 1 | yes | Half-res + caching is how a selective RT effect becomes affordable. |
| shadow_caster_2d_limits | light_range_attenuation_lod | overlap | 1 | yes | Both reduce how many sources/casters participate at distance. |
| shadow_caster_2d_limits | post_effect_selective | overlap | 1 | yes | Same discipline: cap per-effect cost rather than globally. |
| shadow_caster_2d_limits | quality_tier_scalability | complement | 1 | yes | Filter mode and Max Distance are obvious per-tier knobs. |
| skeletal_2d_deform | animation_lod_budget | overlap | 1 | yes | Spine's round-robin subset update is a hand-rolled equivalent of an animation update-rate budget; the 3D engines ship it as a plugin (Animation Budget Allocator) and the 2D tool leaves it to you. |
| skeletal_2d_deform | art_direction_stylization | risk | 2 | yes | A hand-drawn frame-by-frame art direction is fundamentally incompatible with skeletal deformation; this is a concept-stage conflict, not a tuning problem. |
| skeletal_2d_deform | gpu_skinning_compute | alternative | 1 | yes | Structurally the same problem (deform a mesh from a bone hierarchy) solved on the opposite processor: 2D tools deform on the CPU and re-upload, 3D engines deform on the GPU and cache. Choose by art style, not by performance folklore. |
| skeletal_2d_deform | sprite_atlas_batching | complement | 1 | yes | Атлас повышает эффективность батчинга скелетной 2D-анимации, но не является обязательным условием: скелетная анимация работает и без общего атласа, просто с большим числом вызовов отрисовки. |
| skeletal_2d_deform | sprite_sheet_compression | risk | 1 | yes | Риск качества при конкретном сжатии: потери заметнее на деформируемых частях тела, чем на готовых кадрах покадровой анимации. Это не несовместимость скелетной анимации и сжатия как таковых. |
| snapshot_slot_saves | agent_update_budget | overlap | 1 | yes | Both are 'what do we persist/recompute and how much' budget decisions about entity state. |
| snapshot_slot_saves | navmesh_tiling_streaming | overlap | 1 | yes | Both are load/rebuild-from-data problems where order and consistency dominate the difficulty. |
| splitscreen_render_budget | dynamic_resolution_scaling | complement | 1 | yes | DRS absorbs the doubled load without a hard quality cliff. |
| splitscreen_render_budget | post_effect_selective | dependency | 3 | yes | Post is per-view, so it is the first place to cut when splitting. |
| splitscreen_render_budget | quality_tier_scalability | dependency | 3 | yes | Epic explicitly ties scalability to split screen; a project without tiers has no lever to pull. |
| splitscreen_render_budget | temporal_upscaling | complement | 1 | yes | Rendering each view below native and upscaling is the main way to keep quality while paying for two views. |
| sprite_atlas_batching | art_direction_stylization | risk | 2 | yes | Frame-by-frame stylized art multiplies sprite count (Cuphead: 50,000 frames), which turns atlas layout from a configuration task into a pipeline-scale problem. |
| sprite_atlas_batching | sprite_sheet_compression | dependency | 3 | yes | Atlas page size and format together determine VRAM; compressing an atlas page also determines whether bleeding at low mips is visible. |
| sprite_atlas_batching | tilemap_layer_culling | dependency | 3 | yes | Chunk batching only collapses to one draw call if all tiles in a chunk share an atlas page, so tile atlas layout must be designed with chunk layout in mind. |
| sprite_particle_atlas | crowd_2d_instancing | overlap | 1 | yes | Both are batching-by-shared-texture strategies for large numbers of small, similar draws. |
| sprite_particle_atlas | flipbook_particles | overlap | 1 | yes | A flipbook is an atlas whose tiles are animation frames; the packing rules and the jitter failure mode are identical. |
| sprite_sheet_compression | sprite_atlas_batching | complement | 1 | yes | Atlas page format determines VRAM per page; compressing an under-filled page wastes less VRAM but does not recover the wasted area. |
| sprite_sheet_compression | tilemap_layer_culling | complement | 1 | yes | In a fill-rate-bound 2D scene, lower bpp reduces texture bandwidth per covered pixel, which compounds with culling's reduction in covered pixels. |
| srp_batcher_discipline | bindless_uber_shaders | overlap | 1 | yes | Same goal by different means: persistent material data and minimal shader variants. Unity's own advice for a custom SRP is to 'write generic "uber" shader with minimum keywords'. |
| srp_batcher_discipline | tiled_clustered_light_culling | unknown | 2 | yes | Independent axes (CPU submission vs GPU light assignment); no source found that measures them together. |
| static_shadow_caching | hardware_raytraced_gi | risk | 2 | yes | Кэш теней рассчитан на неизменное освещение, а трассировка пересчитывает его заново: выигрыш кэша зависит от доли статичных источников. Разные виды света и теней могут сосуществовать, поэтому запрета пара не образует. |
| static_shadow_caching | lightmap_atlas_baking | alternative | 1 | yes | Baking is static caching taken to zero runtime cost at the price of all dynamism. |
| static_shadow_caching | quality_tier_scalability | complement | 1 | yes | Caching can be reduced or disabled on low tiers to save VRAM. |
| static_shadow_caching | virtual_shadow_maps | dependency | 3 | yes | Static caching is a built-in VSM feature in UE5. |
| subtick_networking | client_prediction_reconciliation | complement | 2 | yes | Время ввода и предсказание клиента — разные части протокола. |
| subtick_networking | client_prediction_reconciliation | dependency | 3 | yes | Метод «subtick_networking» требует предварительного метода «client_prediction_reconciliation». |
| subtick_networking | deterministic_lockstep | unknown | 2 | yes | No source found relating sub-tick timestamping to lockstep command scheduling, although both are about ordering inputs in time. Recorded as unknown rather than guessed. |
| subtick_networking | runtime_security_budget | risk | 2 | yes | Client-supplied timestamps are a new input the server must not trust; bounding them is a security decision, not a networking detail. |
| subtick_networking | tickrate_budgeting | complement | 2 | yes | Метки ввода не отменяют выбор частоты симуляции. |
| temporal_radiance_cache | deferred_forward_plus_choice | dependency | 3 | yes | Метод «temporal_radiance_cache» требует предварительного метода «deferred_forward_plus_choice». |
| temporal_radiance_cache | hardware_raytraced_gi | dependency | 3 | yes | Метод «temporal_radiance_cache» требует предварительного метода «hardware_raytraced_gi». |
| temporal_radiance_cache | quality_tier_scalability | complement | 1 | yes | Update speed is a natural scalability knob. |
| temporal_radiance_cache | selective_ray_traced_effects | complement | 1 | yes | Sharing one trace across effects is the same amortisation idea at effect level. |
| temporal_radiance_cache | temporal_upscaling | overlap | 1 | yes | Both rely on temporal history and both suffer from the same disocclusion/ghosting failure modes. |
| temporal_upscaling | full_path_tracing_pipeline | complement | 1 | yes | Real-time path tracing at interactive rates is only possible with aggressive upscaling. |
| temporal_upscaling | hardware_raytraced_gi | complement | 2 | yes | Upscaler, denoiser и ray reconstruction — разные проходы со своей стоимостью. Совместимость апскейлера с трассировкой не даёт ещё одной скидки поверх стоимости реконструкции. |
| temporal_upscaling | ml_frame_generation | complement | 1 | yes | Frame generation is layered on top of super resolution in shipped titles. |
| temporal_upscaling | quality_tier_scalability | complement | 1 | yes | Screen percentage is a first-class scalability knob. |
| temporal_upscaling | variable_rate_shading | alternative | 1 | yes | VRS saves pixels spatially; upscaling saves them globally. |
| terrain_clipmap | chunked_procedural_terrain | alternative | 1 | yes | Nested regular grids (clipmaps) vs chunked bintree hierarchies (BDAM/chunked LOD): the former is simpler and fully in-core, the latter is adaptive but out-of-core. C-BDAM exists to get both. |
| terrain_clipmap | distance_field_shadows | overlap | 1 | yes | Unreal's Global Distance Field is explicitly implemented as camera-centred clipmaps, and Nanite's directional VSMs use Nx clipmaps - same structure, different payload. |
| terrain_clipmap | heightmap_compression | dependency | 3 | yes | The residual stream is the compressed heightfield; compression rate decides whether the clipmap fits in memory or needs out-of-core management. |
| terrain_clipmap | terrain_generation_streaming_budget | complement | 1 | yes | Clipmaps bound the render/update cost; the generation budget bounds how fast new terrain data can be produced to feed them. |
| terrain_generation_streaming_budget | async_loading_pipeline | dependency | 3 | yes | Generation is only off the frame if there is an async path with cancellation and priority; without it the budget is paid in hitches. |
| terrain_generation_streaming_budget | directstorage_io | complement | 1 | yes | When the budget is IO-bound, the small-read throughput of the storage path is the ceiling, and DirectStorage exists for exactly that traffic shape. |
| terrain_generation_streaming_budget | heightmap_compression | complement | 1 | yes | Compressed height data lowers the bytes-per-chunk term in the budget, which is the term that scales with storage speed. |
| terrain_generation_streaming_budget | world_partition_streaming | overlap | 1 | yes | Same rate arithmetic at different granularity: cells per second with a loading range, versus chunks per second with a streaming ring. |
| tickrate_budgeting | client_prediction_reconciliation | complement | 1 | yes | Prediction hides the tick rate from the local player, which is why moderate tick rates are acceptable in games with good prediction. |
| tickrate_budgeting | headless_dedicated_server | complement | 1 | yes | The budget is a per-instance hosting budget; density and tick rate are one decision. |
| tickrate_budgeting | lag_compensation_rewind | complement | 1 | yes | Rewind hides the tick rate from the shooter; the amount of history you must retain scales with tick rate (Valve: 1 second). |
| tickrate_budgeting | subtick_networking | alternative | 1 | yes | Sub-tick attacks the same input-quantisation error without raising tick rate - Valve's stated claim is that tick rate stops mattering for input registration. |
| tiled_clustered_light_culling | depth_prepass_early_z | risk | 2 | yes | Часть алгоритмов light culling использует вход глубины, но обязательный полный depth pre-pass для всей категории не требуется: это условие конкретной реализации, а не свойство подхода. |
| tiled_clustered_light_culling | dynamic_light_priority_budget | complement | 1 | yes | Culling raises the ceiling; a priority budget keeps the worst case bounded. |
| tiled_clustered_light_culling | hiz_software_occlusion | complement | 1 | yes | Fewer visible objects means smaller cluster lists; both are GPU-driven culling. |
| tilemap_chunk_streaming | art_direction_stylization | complement | 1 | yes | 2D tile worlds are the main consumer of this method; the streaming decision interacts with how much unique tile art the direction demands. |
| tilemap_chunk_streaming | data_driven_ability_system | risk | 2 | yes | Abilities that modify tiles (terraforming, destructible terrain) write state into chunks that may be unloaded; the ability system must write through a world-state layer, not into the chunk. |
| tilemap_chunk_streaming | sprite_atlas_batching | risk | 2 | yes | If each chunk references a different atlas page, streaming a chunk also means streaming/binding a texture, which can turn a cheap tile load into a texture load and a batch break. |
| tilemap_chunk_streaming | tilemap_layer_culling | dependency | 3 | yes | Streaming only pays off if the renderer can draw per-chunk batches and cull them; Unity's Chunk mode plus Chunk Culling Bounds is the engine-side half of the pair. |
| tilemap_layer_culling | art_direction_stylization | risk | 2 | yes | Tile art that deliberately overflows its cell (common in hand-painted 2D styles) inflates culling bounds and quietly disables the culling win. |
| tilemap_layer_culling | sprite_atlas_batching | complement | 1 | yes | Chunk batching only reduces draw calls if the tiles in a chunk share an atlas page; atlas layout and chunk layout have to be designed together. |
| tilemap_layer_culling | tilemap_chunk_streaming | complement | 1 | yes | Culling bounds what you draw; streaming bounds what you hold. Streaming without culling wastes memory, culling without streaming wastes load time; neither replaces the other. |
| time_sliced_pathfinding | flow_field_pathing | alternative | 1 | yes | Sharing one flow field across many agents removes the per-agent query entirely, which can make slicing unnecessary for crowd-scale movement. |
| time_sliced_pathfinding | multithreaded_physics_jobs | alternative | 1 | yes | Moving queries to worker threads is the alternative to slicing them within a frame; the two can also be combined. |
| variable_rate_shading | deferred_forward_plus_choice | dependency | 3 | yes | Метод «variable_rate_shading» требует предварительного метода «deferred_forward_plus_choice». |
| variable_rate_shading | dynamic_resolution_scaling | alternative | 1 | yes | DRS lowers resolution globally; VRS lowers shading rate locally. |
| variable_rate_shading | meshlet_pipeline_adoption | complement | 1 | yes | Per-primitive VRS from a mesh shader is explicitly supported behind a cap. |
| variable_rate_shading | temporal_upscaling | complement | 1 | yes | Different axes of the same saving; they compose. |
| vegetation_atlas_lod | distance_field_shadows | risk | 2 | yes | Canopies need two-sided distance fields, which Epic says come at a higher ray-marching cost. |
| vegetation_atlas_lod | gpu_instancing_vegetation | dependency | 3 | yes | Atlasing only pays if instances are actually batched; the two are one optimisation. |
| vegetation_atlas_lod | hierarchical_lod | overlap | 1 | yes | HLOD's merge material settings (gutter, binning, merge-equivalent-materials) are the same parameter family, applied to baked proxies instead of to a species library. |
| vegetation_atlas_lod | impostors_billboards | complement | 1 | yes | The impostor is the last link of the chain and lets the atlas stop at a sane resolution. |
| vegetation_atlas_lod | neural_texture_compression | complement | 1 | yes | NTC compresses whole material texture sets together, which is a natural fit for an atlased vegetation material. |
| vehicle_simulation_lod | agent_update_budget | overlap | 1 | yes | Same policy shape: evaluate significance, allocate a budget of fully-simulated entities, degrade the rest. |
| vehicle_simulation_lod | crowd_instancing_impostors | complement | 1 | yes | Rendering LOD (impostors) and simulation LOD usually share the same distance thresholds and should be tuned together. |
| vehicle_simulation_lod | physics_lod_sleeping | dependency | 3 | yes | Vehicle LOD reuses the general deactivation mechanism; without it, distant vehicles keep costing. |
| virtual_geometry_clusters | directstorage_io | complement | 1 | yes | Page streaming plus hardware LZ is the intended IO path; Nanite's own slide says hardware LZ is 'On its way to PC with DirectStorage'. |
| virtual_geometry_clusters | gpu_compute_culling | dependency | 3 | yes | Cluster hierarchy culling and two-phase HZB occlusion are the foundation Nanite is built on. |
| virtual_geometry_clusters | gpu_instancing_vegetation | hard_conflict | 3 | yes | Nanite is 'Not great with aggregates' such as grass, leaves and hair, so foliage still needs an instancing/atlasing path rather than virtualised geometry. |
| virtual_geometry_clusters | hierarchical_lod | overlap | 1 | yes | Both give you far-field geometry cheaply; Nanite's per-cluster LOD removes much of the need for baked HLOD proxies on rigid opaque geometry. |
| virtual_geometry_clusters | impostors_billboards | complement | 1 | yes | Nanite's own solution to tiny instances is 'Visibility buffer imposters' (12x12 directions, 40.5 KB per mesh, always resident) - impostors are the escape hatch when the DAG root is reached. |
| virtual_geometry_clusters | mesh_index_optimization | dependency | 3 | yes | Метод «virtual_geometry_clusters» требует предварительного метода «mesh_index_optimization». |
| virtual_shadow_maps | distance_field_shadows | complement | 1 | yes | 'Distance Field Shadows are not replaced and can be used in tandem with VSMs'. |
| virtual_shadow_maps | froxel_volumetric_fog | risk | 2 | yes | Volumetric fog forces coarse pages, which Epic warns can hurt performance with non-Nanite dynamic geometry. |
| virtual_shadow_maps | selective_ray_traced_effects | risk | 2 | yes | 'Ray-traced shadows still take precedence over VSMs' - enabling RT shadows removes the VSM cost but replaces it with an RT pass cost. |
| virtual_shadow_maps | static_shadow_caching | complement | 1 | yes | VSM's static/dynamic split is a built-in form of static shadow caching. |
| virtual_texturing | async_loading_pipeline | dependency | 3 | yes | VT is an async pipeline specialised to texels: GPU requests, CPU fulfilment, fixed pool, priority eviction. |
| virtual_texturing | heightmap_compression | complement | 1 | yes | Совместимые форматы тайлов дополняют виртуальное текстурирование: сжатие повышает эффективность кэша и снижает трафик подкачки. Выигрыш зависит от формата, размера кэша и стоимости декодирования и не даётся автоматически. |
| virtual_texturing | neural_texture_compression | alternative | 1 | yes | NTC attacks the same VRAM/disk pressure by shrinking the texels rather than by virtualising the address space; the two can compose (compressed pages in a VT cache). |
| virtual_texturing | terrain_clipmap | complement | 1 | yes | Clipmaps handle terrain geometry; VT handles terrain surfacing - a shipped terrain needs both. |
| virtual_texturing | virtual_geometry_clusters | complement | 1 | yes | Nanite's author states geometry virtualisation is 'conceptually similar to virtual texturing' but harder, because geometry detail directly affects render cost and geometry is not trivially filterable. |
| volumetric_half_resolution | froxel_volumetric_fog | dependency | 3 | yes | Метод «volumetric_half_resolution» требует предварительного метода «froxel_volumetric_fog». |
| volumetric_half_resolution | post_effect_selective | overlap | 1 | yes | Both reduce per-effect cost; half-res is the finer-grained tool. |
| volumetric_half_resolution | variable_rate_shading | alternative | 1 | yes | VRS reduces shading rate spatially instead of reducing buffer resolution - different artefact profile, similar goal. |
| voxel_cone_tracing | deferred_forward_plus_choice | dependency | 3 | yes | Метод «voxel_cone_tracing» требует предварительного метода «deferred_forward_plus_choice». |
| voxel_cone_tracing | froxel_volumetric_fog | overlap | 1 | yes | Both need a volumetric scene representation; sharing is possible but couples two systems' resolution budgets. |
| voxel_cone_tracing | irradiance_volume_probes | alternative | 1 | yes | Probes are far cheaper and far lower frequency. |
| voxel_cone_tracing | sdf_global_illumination | alternative | 1 | yes | SDF tracing avoids voxelisation and is Epic's documented non-RT path. |
| world_origin_shifting | chunked_procedural_terrain | risk | 2 | yes | Chunked generation keys content by absolute chunk coordinate; rebasing must not change the chunk key or the same chunk will regenerate differently. |
| world_origin_shifting | distance_field_shadows | risk | 2 | yes | Distance-field/global-distance-field volumes are camera-following clipmaps; a rebasing event that moves the camera discretely invalidates their cached update region. |
| world_origin_shifting | terrain_clipmap | risk | 2 | yes | Clipmap/terrain LOD schemes centre on the viewer; an origin shift changes the centre and must be applied to the terrain frame in the same event or the terrain will visibly jump. |
| world_origin_shifting | world_partition_streaming | complement | 1 | yes | Partitioning bounds what is resident; origin handling bounds how precisely it can be placed. Independent problems that both scale with world extent. |
| world_partition_streaming | async_loading_pipeline | dependency | 3 | yes | Cell streaming is only as smooth as the background loader behind it; partition without async IO just moves the hitch. |
| world_partition_streaming | build_size_startup_budgets | risk | 2 | yes | OFPA's editor file explosion is separate from cook size; teams frequently conflate the two and mis-diagnose build-size regressions. |
| world_partition_streaming | directstorage_io | complement | 1 | yes | Cell streaming produces exactly the many-small-reads workload DirectStorage targets. |
| world_partition_streaming | hierarchical_lod | complement | 1 | yes | HLOD is what makes unloaded World Partition cells still visible; the two are documented as one system. |
| world_partition_streaming | world_origin_shifting | overlap | 1 | yes | Both address 'the world is bigger than the engine's comfortable coordinates'; partitioning bounds residency, origin shifting bounds precision. A very large world needs both. |

## Оборудование

| Type | Model | Source title | Source URL |
| --- | --- | --- | --- |
| CPU | Core i3-10100 | [PassMark CPU Benchmarks — Intel Core i3-10100](https://www.cpubenchmark.net/cpu.php?cpu=Intel+Core+i3-10100&id=3717) | yes |
| CPU | Core i3-8100 | [PassMark CPU Benchmarks — Intel Core i3-8100](https://www.cpubenchmark.net/cpu.php?cpu=Intel+Core+i3-8100&id=3103) | yes |
| CPU | Core i5-10400F | [PassMark CPU Benchmarks — Intel Core i5-10400F](https://www.cpubenchmark.net/cpu.php?cpu=Intel+Core+i5-10400F&id=3767) | yes |
| CPU | Core i5-11400F | [PassMark Intel Core i5-11400F Benchmark — CPU Mark 16869, Single 2979](https://www.cpubenchmark.net/cpu.php?cpu=Intel+Core+i5-11400F+%40+2.60GHz&id=4226) | yes |
| CPU | Core i5-12400F | [PassMark CPU Benchmarks — Intel Core i5-12400F](https://www.cpubenchmark.net/cpu.php?cpu=Intel+Core+i5-12400F&id=4681) | yes |
| CPU | Core i5-12600K | [PassMark Intel Core i5-12600K Benchmark — CPU Mark 27512, Single 3917](https://www.cpubenchmark.net/cpu.php?cpu=Intel+Core+i5-12600K&id=4603) | yes |
| CPU | Core i5-13400F | [PassMark Intel Core i5-13400F Benchmark — CPU Mark 24891, Single 3628](https://www.cpubenchmark.net/cpu.php?cpu=Intel+Core+i5-13400F&id=5166) | yes |
| CPU | Core i5-13600K | [PassMark CPU Benchmarks — Intel Core i5-13600K](https://www.cpubenchmark.net/cpu.php?cpu=Intel+Core+i5-13600K&id=5008) | yes |
| CPU | Core i5-14400F | [PassMark Intel Core i5-14400F Benchmark — CPU Mark 25440, Single 3700](https://www.cpubenchmark.net/cpu.php?cpu=Intel+Core+i5-14400F&id=5837) | yes |
| CPU | Core i5-14600K | [PassMark Intel Core i5-14600K Benchmark — CPU Mark 38402, Single 4267](https://www.cpubenchmark.net/cpu.php?cpu=Intel+Core+i5-14600K&id=5720) | yes |
| CPU | Core i5-8400 | [PassMark CPU Benchmarks — Intel Core i5-8400](https://www.cpubenchmark.net/cpu.php?cpu=Intel+Core+i5-8400&id=3097) | yes |
| CPU | Core i5-9400F | [PassMark CPU Benchmarks — Intel Core i5-9400F](https://www.cpubenchmark.net/cpu.php?cpu=Intel+Core+i5-9400F&id=3397) | yes |
| CPU | Core i7-10700K | [PassMark Intel Core i7-10700K Benchmark — CPU Mark 18501, Single 3036](https://www.cpubenchmark.net/cpu.php?cpu=Intel+Core+i7-10700K+%40+3.80GHz&id=3733) | yes |
| CPU | Core i7-11700K | [PassMark CPU Benchmarks — Intel Core i7-11700K](https://www.cpubenchmark.net/cpu.php?cpu=Intel+Core+i7-11700K&id=3896) | yes |
| CPU | Core i7-11800H | [PassMark Intel Core i7-11800H Benchmark — CPU Mark 19596, Single 3007](https://www.cpubenchmark.net/cpu.php?cpu=Intel+Core+i7-11800H+%40+2.30GHz&id=4358) | yes |
| CPU | Core i7-12700H | [PassMark Intel Core i7-12700H Benchmark — CPU Mark 24995, Single 3484](https://www.cpubenchmark.net/cpu.php?cpu=Intel+Core+i7-12700H&id=4721) | yes |
| CPU | Core i7-12700K | [PassMark CPU Benchmarks — Intel Core i7-12700K](https://www.cpubenchmark.net/cpu.php?cpu=Intel+Core+i7-12700K&id=4609) | yes |
| CPU | Core i7-13700H | [PassMark Intel Core i7-13700H Benchmark — CPU Mark 25860, Single 3552](https://www.cpubenchmark.net/cpu.php?cpu=Intel+Core+i7-13700H&id=5226) | yes |
| CPU | Core i7-13700K | [PassMark CPU Benchmarks — Intel Core i7-13700K](https://www.cpubenchmark.net/cpu.php?cpu=Intel+Core+i7-13700K&id=5060) | yes |
| CPU | Core i7-14700K | [PassMark Intel Core i7-14700K Benchmark — CPU Mark 51958, Single 4456](https://www.cpubenchmark.net/cpu.php?cpu=Intel+Core+i7-14700K&id=5719) | yes |
| CPU | Core i7-7700 | [PassMark Intel Core i7-7700 Benchmark — CPU Mark 8640, Single 2441](https://www.cpubenchmark.net/cpu.php?cpu=Intel+Core+i7-7700+%40+3.60GHz&id=2905) | yes |
| CPU | Core i7-8700K | [PassMark CPU Benchmarks — Intel Core i7-8700K](https://www.cpubenchmark.net/cpu.php?cpu=Intel+Core+i7-8700K&id=3098) | yes |
| CPU | Core i7-9700K | [PassMark CPU Benchmarks — Intel Core i7-9700K](https://www.cpubenchmark.net/cpu.php?cpu=Intel+Core+i7-9700K&id=3335) | yes |
| CPU | Core i9-12900K | [PassMark CPU Benchmarks — Intel Core i9-12900K](https://www.cpubenchmark.net/cpu.php?cpu=Intel+Core+i9-12900K&id=4597) | yes |
| CPU | Core i9-13900K | [PassMark CPU Benchmarks — Intel Core i9-13900K](https://www.cpubenchmark.net/cpu.php?cpu=Intel+Core+i9-13900K&id=5022) | yes |
| CPU | Core i9-14900K | [PassMark CPU Benchmarks — Intel Core i9-14900K](https://www.cpubenchmark.net/cpu.php?cpu=Intel+Core+i9-14900K&id=5717) | yes |
| CPU | Ryzen 3 1200 | [PassMark CPU Benchmarks — AMD Ryzen 3 1200](https://www.cpubenchmark.net/cpu.php?cpu=AMD+Ryzen+3+1200&id=3029) | yes |
| CPU | Ryzen 3 3100 | [PassMark CPU Benchmarks — AMD Ryzen 3 3100](https://www.cpubenchmark.net/cpu.php?cpu=AMD+Ryzen+3+3100&id=3715) | yes |
| CPU | Ryzen 5 1600 | [PassMark CPU Benchmarks — AMD Ryzen 5 1600](https://www.cpubenchmark.net/cpu.php?cpu=AMD+Ryzen+5+1600&id=2984) | yes |
| CPU | Ryzen 5 2600 | [PassMark CPU Benchmarks — AMD Ryzen 5 2600](https://www.cpubenchmark.net/cpu.php?cpu=AMD+Ryzen+5+2600&id=3243) | yes |
| CPU | Ryzen 5 3600 | [PassMark CPU Benchmarks — AMD Ryzen 5 3600](https://www.cpubenchmark.net/cpu.php?cpu=AMD+Ryzen+5+3600&id=3481) | yes |
| CPU | Ryzen 5 5500 | [PassMark CPU Benchmarks — AMD Ryzen 5 5500](https://www.cpubenchmark.net/cpu.php?cpu=AMD+Ryzen+5+5500&id=4807) | yes |
| CPU | Ryzen 5 5600 | [PassMark AMD Ryzen 5 5600 Benchmark — CPU Mark 21494, Single 3253](https://www.cpubenchmark.net/cpu.php?cpu=AMD+Ryzen+5+5600&id=4811) | yes |
| CPU | Ryzen 5 5600X | [PassMark CPU Benchmarks — AMD Ryzen 5 5600X](https://www.cpubenchmark.net/cpu.php?cpu=AMD+Ryzen+5+5600X&id=3859) | yes |
| CPU | Ryzen 5 7500F | [PassMark AMD Ryzen 5 7500F Benchmark — CPU Mark 26537, Single 3825](https://www.cpubenchmark.net/cpu.php?cpu=AMD+Ryzen+5+7500F&id=5648) | yes |
| CPU | Ryzen 5 7600 | [PassMark AMD Ryzen 5 7600 Benchmark — CPU Mark 26975, Single 3908](https://www.cpubenchmark.net/cpu.php?cpu=AMD+Ryzen+5+7600&id=5172) | yes |
| CPU | Ryzen 5 7600X | [PassMark CPU Benchmarks — AMD Ryzen 5 7600X](https://www.cpubenchmark.net/cpu.php?cpu=AMD+Ryzen+5+7600X&id=5033) | yes |
| CPU | Ryzen 7 3700X | [PassMark CPU Benchmarks — AMD Ryzen 7 3700X](https://www.cpubenchmark.net/cpu.php?cpu=AMD+Ryzen+7+3700X&id=3485) | yes |
| CPU | Ryzen 7 5700X | [PassMark AMD Ryzen 7 5700X Benchmark — CPU Mark 26561, Single 3386](https://www.cpubenchmark.net/cpu.php?cpu=AMD+Ryzen+7+5700X&id=4814) | yes |
| CPU | Ryzen 7 5700X3D | [PassMark AMD Ryzen 7 5700X3D Benchmark — CPU Mark 26302, Single 2968](https://www.cpubenchmark.net/cpu.php?cpu=AMD+Ryzen+7+5700X3D&id=5884) | yes |
| CPU | Ryzen 7 5800X3D | [PassMark CPU Benchmarks — AMD Ryzen 7 5800X3D](https://www.cpubenchmark.net/cpu.php?cpu=AMD+Ryzen+7+5800X3D&id=4823) | yes |
| CPU | Ryzen 7 7700X | [PassMark CPU Benchmarks — AMD Ryzen 7 7700X](https://www.cpubenchmark.net/cpu.php?cpu=AMD+Ryzen+7+7700X&id=5036) | yes |
| CPU | Ryzen 7 7800X3D | [PassMark AMD Ryzen 7 7800X3D Benchmark — CPU Mark 34277, Single 3759](https://www.cpubenchmark.net/cpu.php?cpu=AMD+Ryzen+7+7800X3D&id=5299) | yes |
| CPU | Ryzen 7 8745H | [PassMark AMD Ryzen 7 8745H Benchmark — CPU Mark 29058, Single 3675](https://www.cpubenchmark.net/cpu.php?cpu=AMD+Ryzen+7+8745H&id=6289) | yes |
| CPU | Ryzen 7 9800X3D | [PassMark AMD Ryzen 7 9800X3D Benchmark — CPU Mark 39927, Single 4421](https://www.cpubenchmark.net/cpu.php?cpu=AMD+Ryzen+7+9800X3D&id=6344) | yes |
| CPU | Ryzen 9 3900X | [PassMark CPU Benchmarks — AMD Ryzen 9 3900X](https://www.cpubenchmark.net/cpu.php?cpu=AMD+Ryzen+9+3900X&id=3493) | yes |
| CPU | Ryzen 9 5900X | [PassMark CPU Benchmarks — AMD Ryzen 9 5900X](https://www.cpubenchmark.net/cpu.php?cpu=AMD+Ryzen+9+5900X&id=3870) | yes |
| CPU | Ryzen 9 5950X | [PassMark AMD Ryzen 9 5950X Benchmark — CPU Mark 45259, Single 3476](https://www.cpubenchmark.net/cpu.php?cpu=AMD+Ryzen+9+5950X&id=3862) | yes |
| CPU | Ryzen 9 7900X | [PassMark CPU Benchmarks — AMD Ryzen 9 7900X](https://www.cpubenchmark.net/cpu.php?cpu=AMD+Ryzen+9+7900X&id=5027) | yes |
| CPU | Ryzen 9 7950X | [PassMark CPU Benchmarks — AMD Ryzen 9 7950X](https://www.cpubenchmark.net/cpu.php?cpu=AMD+Ryzen+9+7950X&id=5031) | yes |
| CPU | Van Gogh (Steam Deck Custom APU) | [PassMark AMD Custom APU 0932 (Steam Deck) Benchmark — CPU Mark 9411, Single 2214](https://www.cpubenchmark.net/cpu.php?cpu=AMD+Custom+APU+0932&id=6154) | yes |
| GPU | AMD Radeon 780M Graphics | [PassMark - Radeon 780M - Price performance comparison](https://www.videocardbenchmark.net/gpu.php?gpu=Radeon+780M&id=4818) | yes |
| GPU | AMD Radeon Vega 3 Graphics | [PassMark - Radeon Vega 3 - Price performance comparison](https://www.videocardbenchmark.net/gpu.php?gpu=Radeon+Vega+3&id=3926) | yes |
| GPU | AMD Radeon Vega 8 Graphics | [PassMark - Radeon Vega 8 - Price performance comparison](https://www.videocardbenchmark.net/gpu.php?gpu=Radeon+Vega+8&id=3895) | yes |
| GPU | Arc A750 | [PassMark Video Card Benchmarks — Intel Arc A750](https://www.videocardbenchmark.net/gpu.php?gpu=Intel+Arc+A750&id=4612) | yes |
| GPU | Arc A770 | [PassMark Video Card Benchmarks — Intel Arc A770](https://www.videocardbenchmark.net/gpu.php?gpu=Intel+Arc+A770&id=4605) | yes |
| GPU | GeForce GT 1030 | [PassMark - GeForce GT 1030 - Price performance comparison](https://www.videocardbenchmark.net/gpu.php?gpu=GeForce+GT+1030&id=3757) | yes |
| GPU | GeForce GT 730 | [PassMark - GeForce GT 730 - Price performance comparison](https://www.videocardbenchmark.net/gpu.php?gpu=GeForce+GT+730&id=2906) | yes |
| GPU | GeForce GTX 1050 | [PassMark - GeForce GTX 1050 - Price performance comparison](https://www.videocardbenchmark.net/gpu.php?gpu=GeForce+GTX+1050&id=3596) | yes |
| GPU | GeForce GTX 1050 Ti | [PassMark Video Card Benchmarks — GeForce GTX 1050 Ti](https://www.videocardbenchmark.net/gpu.php?gpu=GeForce+GTX+1050+Ti&id=3595) | yes |
| GPU | GeForce GTX 1060 | [PassMark - GeForce GTX 1060 - Price performance comparison](https://www.videocardbenchmark.net/gpu.php?gpu=GeForce+GTX+1060&id=3548) | yes |
| GPU | GeForce GTX 1060 6GB | [PassMark Video Card Benchmarks — GeForce GTX 1060](https://www.videocardbenchmark.net/gpu.php?gpu=GeForce+GTX+1060&id=3548) | yes |
| GPU | GeForce GTX 1070 | [PassMark - GeForce GTX 1070 - Price performance comparison](https://www.videocardbenchmark.net/gpu.php?gpu=GeForce+GTX+1070&id=3521) | yes |
| GPU | GeForce GTX 1070 Ti | [PassMark - GeForce GTX 1070 Ti - Price performance comparison](https://www.videocardbenchmark.net/gpu.php?gpu=GeForce+GTX+1070+Ti&id=3842) | yes |
| GPU | GeForce GTX 1080 | [PassMark - GeForce GTX 1080 - Price performance comparison](https://www.videocardbenchmark.net/gpu.php?gpu=GeForce+GTX+1080&id=3502) | yes |
| GPU | GeForce GTX 1080 Ti | [PassMark Video Card Benchmarks — GeForce GTX 1080 Ti](https://www.videocardbenchmark.net/gpu.php?gpu=GeForce+GTX+1080+Ti&id=3699) | yes |
| GPU | GeForce GTX 1650 | [PassMark Video Card Benchmarks — GeForce GTX 1650](https://www.videocardbenchmark.net/gpu.php?gpu=GeForce+GTX+1650&id=4078) | yes |
| GPU | GeForce GTX 1660 | [PassMark Video Card Benchmarks — GeForce GTX 1660](https://www.videocardbenchmark.net/gpu.php?gpu=GeForce+GTX+1660&id=4062) | yes |
| GPU | GeForce GTX 1660 Super | [PassMark Video Card Benchmarks — GeForce GTX 1660 SUPER](https://www.videocardbenchmark.net/gpu.php?gpu=GeForce+GTX+1660+SUPER&id=4159) | yes |
| GPU | GeForce GTX 1660 Ti | [PassMark Video Card Benchmarks — GeForce GTX 1660 Ti](https://www.videocardbenchmark.net/gpu.php?gpu=GeForce+GTX+1660+Ti&id=4045) | yes |
| GPU | GeForce GTX 750 Ti | [PassMark - GeForce GTX 750 Ti - Price performance comparison](https://www.videocardbenchmark.net/gpu.php?gpu=GeForce+GTX+750+Ti&id=2815) | yes |
| GPU | GeForce GTX 960 | [PassMark - GeForce GTX 960 - Price performance comparison](https://www.videocardbenchmark.net/gpu.php?gpu=GeForce+GTX+960&id=3114) | yes |
| GPU | GeForce GTX 970 | [PassMark - GeForce GTX 970 - Price performance comparison](https://www.videocardbenchmark.net/gpu.php?gpu=GeForce+GTX+970&id=2954) | yes |
| GPU | GeForce RTX 2050 | [PassMark Video Card Benchmarks — GeForce RTX 2050](https://www.videocardbenchmark.net/gpu.php?gpu=GeForce+RTX+2050&id=4501) | yes |
| GPU | GeForce RTX 2060 | [PassMark Video Card Benchmarks — GeForce RTX 2060](https://www.videocardbenchmark.net/gpu.php?gpu=GeForce+RTX+2060&id=4037) | yes |
| GPU | GeForce RTX 2070 Super | [PassMark Video Card Benchmarks — GeForce RTX 2070 SUPER](https://www.videocardbenchmark.net/gpu.php?gpu=GeForce+RTX+2070+SUPER&id=4116) | yes |
| GPU | GeForce RTX 2080 | [PassMark - GeForce RTX 2080 - Price performance comparison](https://www.videocardbenchmark.net/gpu.php?gpu=GeForce+RTX+2080&id=3989) | yes |
| GPU | GeForce RTX 2080 Super | [PassMark - GeForce RTX 2080 SUPER - Price performance comparison](https://www.videocardbenchmark.net/gpu.php?gpu=GeForce+RTX+2080+SUPER&id=4123) | yes |
| GPU | GeForce RTX 2080 Ti | [PassMark - GeForce RTX 2080 Ti - Price performance comparison](https://www.videocardbenchmark.net/gpu.php?gpu=GeForce+RTX+2080+Ti&id=3991) | yes |
| GPU | GeForce RTX 3050 | [PassMark Video Card Benchmarks — GeForce RTX 3050 8GB](https://www.videocardbenchmark.net/gpu.php?gpu=GeForce+RTX+3050+8GB&id=4495) | yes |
| GPU | GeForce RTX 3050 6GB Laptop GPU | [PassMark Video Card Benchmarks — GeForce RTX 3050 6GB Laptop GPU](https://www.videocardbenchmark.net/gpu.php?gpu=GeForce+RTX+3050+6GB+Laptop+GPU&id=4782) | yes |
| GPU | GeForce RTX 3050 Laptop GPU | [PassMark Video Card Benchmarks — GeForce RTX 3050 Laptop GPU](https://www.videocardbenchmark.net/gpu.php?gpu=GeForce+RTX+3050+Laptop+GPU&id=6486) | yes |
| GPU | GeForce RTX 3050 Ti Laptop GPU | [PassMark Video Card Benchmarks — GeForce RTX 3050 Ti Laptop GPU](https://www.videocardbenchmark.net/gpu.php?gpu=GeForce+RTX+3050+Ti+Laptop+GPU&id=4393) | yes |
| GPU | GeForce RTX 3060 | [PassMark Video Card Benchmarks — GeForce RTX 3060](https://www.videocardbenchmark.net/gpu.php?gpu=GeForce+RTX+3060&id=6498) | yes |
| GPU | GeForce RTX 3060 Ti | [PassMark Video Card Benchmarks — GeForce RTX 3060 Ti](https://www.videocardbenchmark.net/gpu.php?gpu=GeForce+RTX+3060+Ti&id=4318) | yes |
| GPU | GeForce RTX 3070 | [PassMark Video Card Benchmarks — GeForce RTX 3070](https://www.videocardbenchmark.net/gpu.php?gpu=GeForce+RTX+3070&id=4283) | yes |
| GPU | GeForce RTX 3080 | [PassMark Video Card Benchmarks — GeForce RTX 3080](https://www.videocardbenchmark.net/gpu.php?gpu=GeForce+RTX+3080&id=4282) | yes |
| GPU | GeForce RTX 3090 | [PassMark Video Card Benchmarks — GeForce RTX 3090](https://www.videocardbenchmark.net/gpu.php?gpu=GeForce+RTX+3090&id=4284) | yes |
| GPU | GeForce RTX 4050 Laptop GPU | [PassMark Video Card Benchmarks — GeForce RTX 4050 Laptop GPU](https://www.videocardbenchmark.net/gpu.php?gpu=GeForce+RTX+4050+Laptop+GPU&id=4763) | yes |
| GPU | GeForce RTX 4060 | [PassMark Video Card Benchmarks — GeForce RTX 4060](https://www.videocardbenchmark.net/gpu.php?gpu=GeForce+RTX+4060&id=4850) | yes |
| GPU | GeForce RTX 4070 | [PassMark Video Card Benchmarks — GeForce RTX 4070](https://www.videocardbenchmark.net/gpu.php?gpu=GeForce+RTX+4070&id=4795) | yes |
| GPU | GeForce RTX 4080 | [PassMark Video Card Benchmarks — GeForce RTX 4080](https://www.videocardbenchmark.net/gpu.php?gpu=GeForce+RTX+4080&id=4622) | yes |
| GPU | GeForce RTX 4090 | [PassMark Video Card Benchmarks — GeForce RTX 4090](https://www.videocardbenchmark.net/gpu.php?gpu=GeForce+RTX+4090&id=4606) | yes |
| GPU | GeForce RTX 5050 | [PassMark Video Card Benchmarks — GeForce RTX 5050](https://www.videocardbenchmark.net/gpu.php?gpu=GeForce+RTX+5050&id=6668) | yes |
| GPU | GeForce RTX 5050 Laptop GPU | [PassMark Video Card Benchmarks — GeForce RTX 5050 Laptop GPU](https://www.videocardbenchmark.net/gpu.php?gpu=GeForce+RTX+5050+Laptop+GPU&id=6552) | yes |
| GPU | GeForce RTX 5060 | [PassMark Video Card Benchmarks — GeForce RTX 5060](https://www.videocardbenchmark.net/gpu.php?gpu=GeForce+RTX+5060&id=5602) | yes |
| GPU | GeForce RTX 5060 Laptop GPU | [PassMark Video Card Benchmarks — GeForce RTX 5060 Laptop GPU](https://www.videocardbenchmark.net/gpu.php?gpu=GeForce+RTX+5060+Laptop+GPU&id=6330) | yes |
| GPU | GeForce RTX 5060 Ti | [PassMark Video Card Benchmarks — GeForce RTX 5060 Ti 16GB](https://www.videocardbenchmark.net/gpu.php?gpu=GeForce+RTX+5060+Ti+16GB&id=6160) | yes |
| GPU | GeForce RTX 5070 | [PassMark Video Card Benchmarks — GeForce RTX 5070](https://www.videocardbenchmark.net/gpu.php?gpu=GeForce+RTX+5070&id=5940) | yes |
| GPU | GeForce RTX 5070 Laptop GPU | [PassMark Video Card Benchmarks — GeForce RTX 5070 Laptop GPU](https://www.videocardbenchmark.net/gpu.php?gpu=GeForce+RTX+5070+Laptop+GPU&id=6260) | yes |
| GPU | GeForce RTX 5070 Ti | [PassMark Video Card Benchmarks — GeForce RTX 5070 Ti](https://www.videocardbenchmark.net/gpu.php?gpu=GeForce+RTX+5070+Ti&id=5878) | yes |
| GPU | GeForce RTX 5070 Ti Laptop GPU | [PassMark Video Card Benchmarks — GeForce RTX 5070 Ti Laptop GPU](https://www.videocardbenchmark.net/gpu.php?gpu=GeForce+RTX+5070+Ti+Laptop+GPU&id=6216) | yes |
| GPU | GeForce RTX 5080 | [PassMark Video Card Benchmarks — GeForce RTX 5080](https://www.videocardbenchmark.net/gpu.php?gpu=GeForce+RTX+5080&id=5721) | yes |
| GPU | GeForce RTX 5090 | [PassMark Video Card Benchmarks — GeForce RTX 5090](https://www.videocardbenchmark.net/gpu.php?gpu=GeForce+RTX+5090&id=5725) | yes |
| GPU | Intel HD Graphics 4600 | [PassMark - Intel HD 4600 - Price performance comparison](https://www.videocardbenchmark.net/gpu.php?gpu=Intel+HD+4600&id=2451) | yes |
| GPU | Intel HD Graphics 520 | [PassMark - Intel HD 520 - Price performance comparison](https://www.videocardbenchmark.net/gpu.php?gpu=Intel+HD+520&id=3255) | yes |
| GPU | Intel HD Graphics 620 | [PassMark - Intel HD Graphics 620 - Price performance comparison](https://www.videocardbenchmark.net/gpu.php?gpu=Intel+HD+Graphics+620&id=3592) | yes |
| GPU | Intel Iris Xe Graphics | [PassMark - Intel Iris Xe - Price performance comparison](https://www.videocardbenchmark.net/gpu.php?gpu=Intel+Iris+Xe&id=4265) | yes |
| GPU | Intel UHD Graphics 620 | [PassMark - Intel UHD Graphics 620 - Price performance comparison](https://www.videocardbenchmark.net/gpu.php?gpu=Intel+UHD+Graphics+620&id=3805) | yes |
| GPU | Intel UHD Graphics 630 | [PassMark - Intel UHD Graphics 630 - Price performance comparison](https://www.videocardbenchmark.net/gpu.php?gpu=Intel+UHD+Graphics+630&id=3826) | yes |
| GPU | Radeon RX 550 | [PassMark - Radeon RX 550 - Price performance comparison](https://www.videocardbenchmark.net/gpu.php?gpu=Radeon+RX+550&id=3761) | yes |
| GPU | Radeon RX 5600 XT | [PassMark Video Card Benchmarks — Radeon RX 5600 XT](https://www.videocardbenchmark.net/gpu.php?gpu=Radeon+RX+5600+XT&id=4186) | yes |
| GPU | Radeon RX 570 | [PassMark Video Card Benchmarks — Radeon RX 470/570](https://www.videocardbenchmark.net/gpu.php?gpu=Radeon+RX+470%2F570&id=3558) | yes |
| GPU | Radeon RX 580 | [PassMark Video Card Benchmarks — Radeon RX 580](https://www.videocardbenchmark.net/gpu.php?gpu=Radeon+RX+580&id=3736) | yes |
| GPU | Radeon RX 6500 XT | [PassMark Video Card Benchmarks — Radeon RX 6500 XT](https://www.videocardbenchmark.net/gpu.php?gpu=Radeon+RX+6500+XT&id=4488) | yes |
| GPU | Radeon RX 6600 | [PassMark Video Card Benchmarks — Radeon RX 6600](https://www.videocardbenchmark.net/gpu.php?gpu=Radeon+RX+6600&id=4465) | yes |
| GPU | Radeon RX 6650 XT | [PassMark Video Card Benchmarks — Radeon RX 6650 XT](https://www.videocardbenchmark.net/gpu.php?gpu=Radeon+RX+6650+XT&id=4541) | yes |
| GPU | Radeon RX 6700 XT | [PassMark Video Card Benchmarks — Radeon RX 6700 XT](https://www.videocardbenchmark.net/gpu.php?gpu=Radeon+RX+6700+XT&id=4369) | yes |
| GPU | Radeon RX 6750 XT | [PassMark - Radeon RX 6750 XT - Price performance comparison](https://www.videocardbenchmark.net/gpu.php?gpu=Radeon+RX+6750+XT&id=4543) | yes |
| GPU | Radeon RX 6800 | [PassMark - Radeon RX 6800 - Price performance comparison](https://www.videocardbenchmark.net/gpu.php?gpu=Radeon+RX+6800&id=4314) | yes |
| GPU | Radeon RX 6800 XT | [PassMark Video Card Benchmarks — Radeon RX 6800 XT](https://www.videocardbenchmark.net/gpu.php?gpu=Radeon+RX+6800+XT&id=4312) | yes |
| GPU | Radeon RX 6900 XT | [PassMark Video Card Benchmarks — Radeon RX 6900 XT](https://www.videocardbenchmark.net/gpu.php?gpu=Radeon+RX+6900+XT&id=4322) | yes |
| GPU | Radeon RX 7600 | [PassMark Video Card Benchmarks — Radeon RX 7600](https://www.videocardbenchmark.net/gpu.php?gpu=Radeon+RX+7600&id=4832) | yes |
| GPU | Radeon RX 7700 XT | [PassMark - Radeon RX 7700 XT - Price performance comparison](https://www.videocardbenchmark.net/gpu.php?gpu=Radeon+RX+7700+XT&id=4919) | yes |
| GPU | Radeon RX 7800 XT | [PassMark Video Card Benchmarks — Radeon RX 7800 XT](https://www.videocardbenchmark.net/gpu.php?gpu=Radeon+RX+7800+XT&id=4917) | yes |
| GPU | Radeon RX 7900 XT | [PassMark Video Card Benchmarks — Radeon RX 7900 XT](https://www.videocardbenchmark.net/gpu.php?gpu=Radeon+RX+7900+XT&id=4646) | yes |
| GPU | Radeon RX 7900 XTX | [PassMark Video Card Benchmarks — Radeon RX 7900 XTX](https://www.videocardbenchmark.net/gpu.php?gpu=Radeon+RX+7900+XTX&id=4644) | yes |
| GPU | Radeon RX 9060 XT | [PassMark Video Card Benchmarks — Radeon RX 9060 XT 16GB](https://www.videocardbenchmark.net/gpu.php?gpu=Radeon+RX+9060+XT+16GB&id=5957) | yes |
| GPU | Radeon RX 9070 | [PassMark Video Card Benchmarks — Radeon RX 9070](https://www.videocardbenchmark.net/gpu.php?gpu=Radeon+RX+9070&id=5958) | yes |
| GPU | Radeon RX 9070 XT | [PassMark Video Card Benchmarks — Radeon RX 9070 XT](https://www.videocardbenchmark.net/gpu.php?gpu=Radeon+RX+9070+XT&id=5956) | yes |
