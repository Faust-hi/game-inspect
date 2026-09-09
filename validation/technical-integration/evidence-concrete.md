# Доказательства влияния — по каждому подходящему решению

Колонки партий: `Реализация` = как сделано, `Цена` = наблюдаемая плата в профиле. Это не замер FPS.
Каталог: `pros/cons/limitations/impact_*` — механизм из вендорной доки + экспертный балл, не импорт чисел из игры.
Правило: совпадение кода != доказательство применения в игре. Числа из партий в коэффициенты не идут.

Всего: 492

## `runtime_stencil_portal_rendering` | партия-01.md:28 | portal_rendering | technical_reference

- Партия: | runtime_stencil_portal_rendering | stencil-буфер DX9 вырезает произвольную форму портала, текстурные координаты и векторы передаются через границу с коррекцией перспективы | Конфликт с водой и reflection (выключают stencil) |
- Каталог: точного метода нет — только тема функции `portal_rendering`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `portal_momentum_conservation` | партия-01.md:29 | physics_simulation | technical_reference

- Партия: | portal_momentum_conservation | импульс сохраняется через математическое преобразование векторов на границе портала | Точность зависит от float-точности углов |
- Каталог: точного метода нет — только тема функции `physics_simulation`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `audio_propagation_through_portals` | партия-01.md:30 | audio_system | technical_reference

- Партия: | audio_propagation_through_portals | звук трассируется через оба портала с собственной аудио-геометрией | Нагрузка на CPU растёт линейно с числом открытых порталов |
- Каталог: точного метода нет — только тема функции `audio_system`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `baked_occlusion_culling` | партия-01.md:31 | open_world_streaming | catalog_method

- Партия: | baked_occlusion_culling (BSP) | статическая видимость, предвычисленная на этапе компиляции карты | Невозможна динамическая деформация стен |
- Каталог `baked_occlusion_culling` (open_world_streaming): Видимость ячеек рассчитывается заранее и сохраняется в данные уровня.
  - Влияет: CPU -1 / GPU -1 / RAM 1 / VRAM 0 / DISK 1 / NET 0 | quality 0 concept -1
  - Плюсы: Почти нулевая стоимость в рантайме; Просто внедрить
  - Минусы: Не учитывает динамические объекты; Требует пересчёта при изменении геометрии
  - Ограничения: Плохо применимо к открытому миру со стримингом; Окклюзию надо проектировать стенами и комнатами: где нечего закрыть, там нечего отсечь
  - Условия: —
  - Проверка: Сравнение числа отрисованных объектов до и после запекания на контрольных точках. [Unity Profiler, Профилировщик Godot] | confidence 0.85 | источник UNITY_OCCLUSION

## `fixed_timestep_physics` | партия-01.md:32 | physics_simulation | catalog_method

- Партия: | fixed_timestep_physics | детерминированный шаг симуляции | Однопоточный скриптовый движок Source |
- Каталог `fixed_timestep_physics` (physics_simulation): Физика обновляется с постоянным шагом, визуальное состояние интерполируется по времени.
  - Влияет: CPU 0 / GPU 0 / RAM 0 / VRAM 0 / DISK 0 / NET 0 | quality 0 concept -1
  - Плюсы: Стабильность и воспроизводимость; Обязательно для сетевой игры
  - Минусы: Сложно внедрить в готовый проект; Добавляет задержку в один шаг
  - Ограничения: Требует интерполяции визуального состояния
  - Условия: —
  - Проверка: Проверка воспроизводимости: одинаковая последовательность входов даёт одинаковый результат. [Unreal Insights, Unity Profiler] | confidence 0.9 | источник GODOT_PHYSICS

## `depth_prepass_early_z` | партия-01.md:33 | post_processing | catalog_method

- Партия: | depth_prepass_early_z | ранний Z-проход для снижения overdraw при множественных порталах | Дополнительный draw pass |
- Каталог `depth_prepass_early_z` (post_processing): Сначала строится буфер глубины, затем основной проход отсекает перекрытые фрагменты.
  - Влияет: CPU 0 / GPU -2 / RAM 0 / VRAM 0 / DISK 0 / NET 0 | quality 0 concept 0
  - Плюсы: Заметно снижает перерисовку; Не требует изменения контента
  - Минусы: Дополнительный проход геометрии стоит времени
  - Ограничения: Эффект минимален при малой перерисовке
  - Условия: —
  - Проверка: Замер overdraw в режиме визуализации перерисовки. [Unreal Insights, Unity Profiler, Профилировщик Godot] | confidence 0.75 | источник WIKI_HSR

## `paintmap_gel_rendering` | партия-01.md:78 | portal_rendering | technical_reference

- Партия: | paintmap_gel_rendering | SDF-сетки (signed distance fields) для физики и рендера гелей; paintmap удваивает lightmap-память | Удвоенная VRAM на лайтмапы; слабые GPU страдают от fill-rate |
- Каталог: точного метода нет — только тема функции `portal_rendering`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `gpu_particle_simulation` | партия-01.md:79 | particle_systems | catalog_method

- Партия: | gpu_particle_simulation | particle-pool для гелей и bubbles в pixel shader с early clip | Однопоточный submit в Source MP |
- Каталог `gpu_particle_simulation` (particle_systems): Позиции и состояние частиц вычисляются вычислительным шейдером, а не на CPU.
  - Влияет: CPU -2 / GPU 1 / RAM 0 / VRAM 1 / DISK 0 / NET 0 | quality 0 concept 0
  - Плюсы: На порядки больше частиц; Снимает нагрузку с CPU
  - Минусы: Сложнее реализовать взаимодействие с игровой логикой; Сложнее отлаживать
  - Ограничения: Нужна поддержка вычислительных шейдеров
  - Условия: —
  - Проверка: Замер времени CPU на обновление частиц и числа активных частиц. [Unreal Insights, Unity Profiler] | confidence 0.85 | источник UE_NIAGARA

## `laser_dynamic_reflection` | партия-01.md:80 | portal_rendering | technical_reference

- Партия: | laser_dynamic_reflection | динамическая трассировка отражений на CPU до 10 переотражений за кадр | Растёт нагрузка CPU при сложных сценах |
- Каталог: точного метода нет — только тема функции `portal_rendering`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `excursion_funnel_force_field` | партия-01.md:81 | physics_simulation | technical_reference

- Партия: | excursion_funnel_force_field | инвертированные зоны гравитации как force-field volumes | Требует пересчёта коллизий каждый кадр |
- Каталог: точного метода нет — только тема функции `physics_simulation`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `deferred_forward_plus_choice` | партия-01.md:82 | post_processing | catalog_method

- Партия: | deferred_forward_plus_choice | гибридный forward+ рендеринг, выбор по сцене | Сложнее дебага |
- Каталог `deferred_forward_plus_choice` (post_processing): Архитектура рендера выбирается под ожидаемую сцену: отложенное затенение или forward+ с кластеризацией.
  - Влияет: CPU 0 / GPU -1 / RAM 0 / VRAM 2 / DISK 0 / NET 0 | quality 0 concept 0
  - Плюсы: Определяет потолок производительности проекта; Влияет на все последующие решения
  - Минусы: Смена архитектуры на поздней стадии крайне дорога
  - Ограничения: Выбор зависит от числа источников света и прозрачности; Стоимость ветвей различается по знаку: без указания выбранной ветви эффект не начисляется
  - Условия: —
  - Проверка: Сравнительный тест двух архитектур на эталонной сцене с целевым числом источников. [Unreal Insights, Unity Profiler] | confidence 0.8 | источник WIKI_DEFERRED

## `audio_convolution_reverb` | партия-01.md:83 | audio_system | catalog_method

- Партия: | audio_convolution_reverb | convolution reverb на основе импульсных характеристик комнат | Высокое потребление CPU в больших зонах |
- Каталог `audio_convolution_reverb` (audio_system): Аудиосигнал обрабатывается импульсным откликом; стоимость зависит от длины IR и числа каналов.
  - Влияет: CPU 1 / GPU 0 / RAM 1 / VRAM 0 / DISK 0 / NET 0 | quality 0 concept 0
  - Плюсы: Воспроизводит акустический отклик помещения
  - Минусы: Дополнительная работа DSP и хранение IR
  - Ограничения: Описание механизма не подтверждает его применение в конкретной игре из партий.; Баллы и аппаратные коэффициенты — экспертные допущения; ускорение и трудоёмкость не измерены.
  - Условия: Не заменяет геометрическую окклюзию звука; Проверить блок обработки, каналы и переходы зон
  - Проверка: Сравнить DSP-время, задержку и память при пике голосов. [Профилировщик движка, Захват CPU/GPU и памяти] | confidence 0.5 | источник TECH_REVERB

## `particle_pooling` | партия-01.md:84 | particle_systems | catalog_method

- Партия: | particle_pooling | пул для дыма, искр, воды (от Left 4 Dead) | Фиксированный пул |
- Каталог `particle_pooling` (particle_systems): Системы частиц создаются заранее и переиспользуются вместо постоянного создания и удаления.
  - Влияет: CPU -1 / GPU 0 / RAM -1 / VRAM 0 / DISK 0 / NET 0 | quality 0 concept 0
  - Плюсы: Устраняет пики сборки мусора; Просто внедрить
  - Минусы: Требует дисциплины при работе с эффектами
  - Ограничения: Не снижает среднюю нагрузку; Пул удерживает объекты: память под него остаётся занятой
  - Условия: —
  - Проверка: Контроль отсутствия аллокаций в профилировщике во время эффектов. [Unity Profiler, Профилировщик Godot] | confidence 0.9 | источник WIKI_OBJECTPOOL

## `lightmap_atlas_baking` | партия-01.md:85 | baked_lighting | catalog_method

- Партия: | lightmap_atlas_baking | единый lightmap-атлас для всех комнат | Удвоенный размер при paintmap |
- Каталог `lightmap_atlas_baking` (baked_lighting): Освещение статической геометрии рассчитывается заранее и сохраняется в текстуры.
  - Влияет: CPU -2 / GPU -2 / RAM 1 / VRAM -2 / DISK 2 / NET 0 | quality -1 concept 0
  - Плюсы: Почти нулевая стоимость в рантайме; Высокое качество с мягкими переотражениями
  - Минусы: Требует статической геометрии; Долгий пересчёт при изменениях
  - Ограничения: Несовместимо с динамическим временем суток
  - Условия: —
  - Проверка: Сравнение времени кадра рендера освещения до и после; контроль размера лайтмапов. [Unity Profiler, Unreal Insights, Профилировщик Godot] | confidence 0.9 | источник WIKI_LIGHTMAP

## `lua_scripting_extension` | партия-01.md:130 | project_architecture | technical_reference

- Партия: | lua_scripting_extension | Lua-VM поверх Source — пользовательская игровая логика без перекомпиляции C++ | Один плохой аддон кладёт серверный тик |
- Каталог: точного метода нет — только тема функции `project_architecture`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `physics_gun_constraints` | партия-01.md:131 | physics_simulation | technical_reference

- Партия: | physics_gun_constraints | wire-constraints (верelet/weld/nocollide/freeze) для манипуляции объектами | Лимиты sbox_max; нужен cleanup |
- Каталог: точного метода нет — только тема функции `physics_simulation`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `single_thread_main_loop` | партия-01.md:132 | rendering_architecture | technical_reference

- Партия: | single_thread_main_loop | net + phys + Lua в одном потоке | Один поток = упор в clock, не в cores |
- Каталог: точного метода нет — только тема функции `rendering_architecture`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `physics_lod_sleeping` | партия-01.md:133 | physics_simulation | catalog_method

- Партия: | physics_lod_sleeping | sleep/wake объектов вне зоны активности | Сложнее профилировать |
- Каталог `physics_lod_sleeping` (physics_simulation): Далёкие и покоящиеся тела переводятся в упрощённый режим или исключаются из симуляции.
  - Влияет: CPU -2 / GPU 0 / RAM 0 / VRAM 0 / DISK 0 / NET 0 | quality -1 concept -1
  - Плюсы: Большой эффект при минимальной стоимости; Практически не влияет на геймплей
  - Минусы: Возможны артефакты при выходе из спячки
  - Ограничения: Требует настройки порогов
  - Условия: —
  - Проверка: Замер времени физики и проверка корректности пробуждения объектов. [Unity Profiler, Профилировщик Godot] | confidence 0.9 | источник UE_CHAOS

## `particle_pooling` | партия-01.md:134 | particle_systems | catalog_method

- Партия: | particle_pooling | пул частиц для explosions/эффектов | Фиксированный пул |
- Каталог `particle_pooling` (particle_systems): Системы частиц создаются заранее и переиспользуются вместо постоянного создания и удаления.
  - Влияет: CPU -1 / GPU 0 / RAM -1 / VRAM 0 / DISK 0 / NET 0 | quality 0 concept 0
  - Плюсы: Устраняет пики сборки мусора; Просто внедрить
  - Минусы: Требует дисциплины при работе с эффектами
  - Ограничения: Не снижает среднюю нагрузку; Пул удерживает объекты: память под него остаётся занятой
  - Условия: —
  - Проверка: Контроль отсутствия аллокаций в профилировщике во время эффектов. [Unity Profiler, Профилировщик Godot] | confidence 0.9 | источник WIKI_OBJECTPOOL

## `headless_dedicated_server` | партия-01.md:135 | multiplayer_netcode | catalog_method

- Партия: | headless_dedicated_server | выделенный сервер без рендера | Требует отдельного бинарника |
- Каталог `headless_dedicated_server` (multiplayer_netcode): Серверная сборка исключает рендер, звук и ввод, оставляя только симуляцию.
  - Влияет: CPU -2 / GPU -2 / RAM -1 / VRAM 0 / DISK 0 / NET 0 | quality 0 concept 0
  - Плюсы: Существенно дешевле эксплуатация; Повышает стабильность сервера
  - Минусы: Требует отдельной сборки иpipeline; Усложняет отладку
  - Ограничения: Требует отделения серверной логики от клиентской
  - Условия: —
  - Проверка: Замер потребления ресурсов сервером на целевом числе игроков. [Unreal Insights, Unity Profiler] | confidence 0.8 | источник UE_NETWORKING

## `tick_hook_timer_replacement` | партия-01.md:136 | multiplayer_netcode | technical_reference

- Партия: | tick_hook_timer_replacement | замена тяжёлых tick-хуков на таймеры | Не все события можно вынести из тика |
- Каталог: точного метода нет — только тема функции `multiplayer_netcode`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `find_in_sphere_hot_path_avoid` | партия-01.md:137 | ai_pathfinding | technical_reference

- Партия: | find_in_sphere_hot_path_avoid | FindInSphere нельзя вызывать в горячем пути | Дисциплина программирования аддонов |
- Каталог: точного метода нет — только тема функции `ai_pathfinding`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `wiremod_visual_programming` | партия-01.md:138 | project_architecture | technical_reference

- Партия: | wiremod_visual_programming | визуальное программирование конструкций через wire/E2 | Ограничение на кап констрейнтов |
- Каталог: точного метода нет — только тема функции `project_architecture`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `fixed_timestep_physics_60fps` | партия-01.md:185 | physics_simulation | technical_reference

- Партия: | fixed_timestep_physics_60fps | жёсткий 60 fps-тайминг; бюджет кадра определяет всё остальное | Ограничение масштабов разрушаемости |
- Каталог: точного метода нет — только тема функции `physics_simulation`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `material_bullet_penetration` | партия-01.md:186 | rendering_architecture | technical_reference

- Партия: | material_bullet_penetration | каждый материал имеет проникающую способность (cover vs concealment) | Больше вариантов материала = больше памяти и CPU |
- Каталог: точного метода нет — только тема функции `rendering_architecture`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `audio_occlusion_reverb` | партия-01.md:187 | audio_system | technical_reference

- Партия: | audio_occlusion_reverb | собственная система окклюзии, унаследованная из CoD2 | Однопоточный sound-движок: перестрелки упираются в 1 ядро |
- Каталог: точного метода нет — только тема функции `audio_system`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `dynamic_lighting_plus_dof` | партия-01.md:188 | dynamic_lighting | technical_reference

- Партия: | dynamic_lighting_plus_dof | depth of field, динамические тени в реальном времени | Нагрузка на GPU растёт с числом источников света |
- Каталог: точного метода нет — только тема функции `dynamic_lighting`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `animation_lod_budget` | партия-01.md:189 | character_animation | catalog_method

- Партия: | animation_lod_budget | скелетная анимация с упрощением на дистанции | Видимые «pops» при переключении LOD |
- Каталог `animation_lod_budget` (character_animation): Частота и детализация обновления анимации снижаются для далёких и второстепенных персонажей.
  - Влияет: CPU -2 / GPU 0 / RAM 0 / VRAM 0 / DISK 0 / NET 0 | quality -1 concept 0
  - Плюсы: Большой эффект при низкой стоимости; Гибко настраивается
  - Минусы: Заметно на средней дистанции
  - Ограничения: Требует настройки порогов дистанции
  - Условия: —
  - Проверка: Замер времени анимации при заполненной сцене и визуальная оценка дальних NPC. [Unreal Insights, Unity Profiler] | confidence 0.85 | источник UE_ANIMBUDGET

## `multiplayer_progression_unlock` | партия-01.md:190 | multiplayer_netcode | technical_reference

- Партия: | multiplayer_progression_unlock | XP-система, prestige, create-a-class — серверная логика | Сервер хранит состояние всех игроков |
- Каталог: точного метода нет — только тема функции `multiplayer_netcode`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `killstreak_server_logic` | партия-01.md:191 | multiplayer_netcode | technical_reference

- Партия: | killstreak_server_logic | ачивки на N фрагов без смерти (3/5/7) | Серверная логика раз в кадр |
- Каталог: точного метода нет — только тема функции `multiplayer_netcode`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `hex_grid_pathfinding` | партия-01.md:235 | ai_pathfinding | technical_reference

- Партия: | hex_grid_pathfinding | гексагональная сетка мира вместо квадратной | Переделка всех AI-решений, карт и интерфейса |
- Каталог: точного метода нет — только тема функции `ai_pathfinding`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `hardware_tessellation_terrain` | партия-01.md:236 | large_scale_terrain | technical_reference

- Партия: | hardware_tessellation_terrain | DX11 tessellation для ландшафта | Требует DX11 GPU |
- Каталог: точного метода нет — только тема функции `large_scale_terrain`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `gpu_raytraced_shadows` | партия-01.md:237 | ray_traced_effects | technical_reference

- Партия: | gpu_raytraced_shadows | тени через ray-tracing на GPU + AA shadow maps | Не масштабируется на старых GPU |
- Каталог: точного метода нет — только тема функции `ray_traced_effects`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `ai_four_layer_hierarchy` | партия-01.md:239 | advanced_npc_ai | technical_reference

- Партия: | ai_four_layer_hierarchy | tactical/operational/strategic/grand-strategic AI | 4 параллельных AI-цикла = нагрузка на CPU |
- Каталог: точного метода нет — только тема функции `advanced_npc_ai`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `ai_flavor_personality_matrix` | партия-01.md:240 | advanced_npc_ai | technical_reference

- Партия: | ai_flavor_personality_matrix | 26 «flavor»-параметров (1–10) на каждого лидера | Признано: AI рандомен между стратегиями |
- Каталог: точного метода нет — только тема функции `advanced_npc_ai`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `deferred_cpu_threading` | партия-01.md:241 | rendering_architecture | technical_reference

- Партия: | deferred_cpu_threading | 4 уровня AI на отдельных потоках | Синхронизация между слоями |
- Каталог: точного метода нет — только тема функции `rendering_architecture`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `time_sliced_pathfinding` | партия-01.md:242 | ai_pathfinding | catalog_method

- Партия: | time_sliced_pathfinding | pathfinding по тайлам, разнесённый по тикам | Юниты в дальних гексах могут «лагать» |
- Каталог `time_sliced_pathfinding` (ai_pathfinding): Запросы на поиск пути ставятся в очередь с ограничением числа запросов на кадр.
  - Влияет: CPU -1 / GPU 0 / RAM 0 / VRAM 0 / DISK 0 / NET 0 | quality 0 concept -1
  - Плюсы: Сглаживает пики нагрузки; Просто внедрить
  - Минусы: Путь доступен не сразу; Требует обработки задержки
  - Ограничения: Не снижает суммарную нагрузку; Работа переносится на следующие кадры: ответ приходит позже
  - Условия: —
  - Проверка: Замер максимального времени кадра при массовой постановке запросов. [Unity Profiler, Профилировщик Godot] | confidence 0.85 | источник WIKI_NAVMESH

## `community_moddable_dll` | партия-01.md:243 | project_architecture | technical_reference

- Партия: | community_moddable_dll | исходный код DLL выпущен в Fall Patch 2012 | Требует обратной совместимости |
- Каталог: точного метода нет — только тема функции `project_architecture`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `procedural_resource_generation` | партия-01.md:244 | procedural_terrain | technical_reference

- Партия: | procedural_resource_generation | многооктавный шум Перлина для ресурсов/рельефа | Зависимость от seed-детерминизма |
- Каталог: точного метода нет — только тема функции `procedural_terrain`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `voice_acting_native_languages` | партия-01.md:245 | audio_system | technical_reference

- Партия: | voice_acting_native_languages | лидеры говорят на родных языках (Latin, Nahuatl) | Удорожание локализации |
- Каталог: точного метода нет — только тема функции `audio_system`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `dynamic_fire_propagation` | партия-01.md:291 | physics_simulation | technical_reference

- Партия: | dynamic_fire_propagation | объёмное распространение огня от огнемёта (первая CoD с настоящей физикой пламени) | Тяжёлый fillrate при больших пожарах |
- Каталог: точного метода нет — только тема функции `physics_simulation`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `dismemberment_physics` | партия-01.md:292 | destruction_simulation | technical_reference

- Партия: | dismemberment_physics | отрывание конечностей, сгорание кожи | Увеличение числа мелких физ-объектов |
- Каталог: точного метода нет — только тема функции `destruction_simulation`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `audio_occlusion_multilevel` | партия-01.md:293 | audio_system | technical_reference

- Партия: | audio_occlusion_multilevel | многоуровневая окклюзия (различает толстые и тонкие стены) | Расход CPU на sound |
- Каталог: точного метода нет — только тема функции `audio_system`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `audio_flux_field_recording` | партия-01.md:294 | audio_system | technical_reference

- Партия: | audio_flux_field_recording | Flux: полевая запись эха оружия на полигоне для точной локализации звука | Зависит от точных импульсов |
- Каталог: точного метода нет — только тема функции `audio_system`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `extended_destruction` | партия-01.md:295 | destruction_simulation | technical_reference

- Партия: | extended_destruction | разрушаемые стены, песчаные баррикады | Больше динамических мешей в сцене |
- Каталог: точного метода нет — только тема функции `destruction_simulation`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `material_bullet_penetration` | партия-01.md:296 | rendering_architecture | technical_reference

- Партия: | material_bullet_penetration | унаследован от IW 3.0 | Те же ограничения, что и в CoD4 |
- Каталог: точного метода нет — только тема функции `rendering_architecture`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `cooperative_zombies_spawning` | партия-01.md:297 | multiplayer_netcode | technical_reference

- Партия: | cooperative_zombies_spawning | объединённый spawner для волн зомби + entity pooling | Лимит числа зомби на сцене |
- Каталог: точного метода нет — только тема функции `multiplayer_netcode`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `leveled_reactive_ai_director_lite` | партия-01.md:298 | advanced_npc_ai | technical_reference

- Партия: | leveled_reactive_ai_director_lite | ремастеринг на Director-систему из будущей L4D | Упрощённая версия по сравнению с L4D |
- Каталог: точного метода нет — только тема функции `advanced_npc_ai`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `redengine_blinn_phong_rendering` | партия-01.md:341 | rendering_architecture | technical_reference

- Партия: | redengine_blinn_phong_rendering | Blinn-Phong specular/Diffuse через DX9 Shader Model 3.0, мягкие тени, SSAO — **PBR и Forward+ отсутствовали в 2011 году** (появились только в REDengine 3 / Witcher 3 2015) | Упрощённая модель материалов, нет energy conservation |
- Каталог: точного метода нет — только тема функции `rendering_architecture`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `ubersampling_supersampling_4x` | партия-01.md:342 | upscaling_frame_generation | technical_reference

- Партия: | ubersampling_supersampling_4x | Ubersampling = 4x SSAA с пересчётом освещения для каждого субпикселя (extreme supersampling), обрушивал fps на топ-GPU 2011 (GTX 590 ниже 30 fps) | Полная стоимость рендера × 4 на GPU |
- Каталог: точного метода нет — только тема функции `upscaling_frame_generation`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `havok_physics_layer` | партия-01.md:343 | physics_simulation | technical_reference

- Партия: | havok_physics_layer | Havok для ragdoll и тяжёлых тканей | Стоимость лицензии |
- Каталог: точного метода нет — только тема функции `physics_simulation`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `baked_occlusion_culling` | партия-01.md:345 | open_world_streaming | catalog_method

- Партия: | baked_occlusion_culling | precomputed видимость для крупных зон | Не учитывает динамические разрушения |
- Каталог `baked_occlusion_culling` (open_world_streaming): Видимость ячеек рассчитывается заранее и сохраняется в данные уровня.
  - Влияет: CPU -1 / GPU -1 / RAM 1 / VRAM 0 / DISK 1 / NET 0 | quality 0 concept -1
  - Плюсы: Почти нулевая стоимость в рантайме; Просто внедрить
  - Минусы: Не учитывает динамические объекты; Требует пересчёта при изменении геометрии
  - Ограничения: Плохо применимо к открытому миру со стримингом; Окклюзию надо проектировать стенами и комнатами: где нечего закрыть, там нечего отсечь
  - Условия: —
  - Проверка: Сравнение числа отрисованных объектов до и после запекания на контрольных точках. [Unity Profiler, Профилировщик Godot] | confidence 0.85 | источник UNITY_OCCLUSION

## `hierarchical_lod` | партия-01.md:346 | open_world_streaming | catalog_method

- Партия: | hierarchical_lod | несколько уровней детализации для лесов и городов | Перестройка при изменении мира |
- Каталог `hierarchical_lod` (open_world_streaming): Группы удалённых объектов объединяются в один упрощённый прокси-меш и отрисовываются одним вызовом.
  - Влияет: CPU -1 / GPU -2 / RAM 1 / VRAM 1 / DISK 1 / NET 0 | quality -1 concept 0
  - Плюсы: Существенно снижает количество вызовов отрисовки; Хорошо масштабируется
  - Минусы: Требует пересборки при изменении мира; Возможны « pops » при переключении
  - Ограничения: Плохо работает с полностью разрушаемым миром
  - Условия: —
  - Проверка: Замер количества вызовов отрисовки и времени рендер-потока до и после. [Unreal Insights, Unity Profiler] | confidence 0.8 | источник UE_HLOD

## `animation_lod_budget` | партия-01.md:347 | character_animation | catalog_method

- Партия: | animation_lod_budget | упрощение анимации на дистанции | Видимые артефакты при переключении |
- Каталог `animation_lod_budget` (character_animation): Частота и детализация обновления анимации снижаются для далёких и второстепенных персонажей.
  - Влияет: CPU -2 / GPU 0 / RAM 0 / VRAM 0 / DISK 0 / NET 0 | quality -1 concept 0
  - Плюсы: Большой эффект при низкой стоимости; Гибко настраивается
  - Минусы: Заметно на средней дистанции
  - Ограничения: Требует настройки порогов дистанции
  - Условия: —
  - Проверка: Замер времени анимации при заполненной сцене и визуальная оценка дальних NPC. [Unreal Insights, Unity Profiler] | confidence 0.85 | источник UE_ANIMBUDGET

## `havok_ragdoll_quality` | партия-01.md:348 | physics_simulation | technical_reference

- Партия: | havok_ragdoll_quality | качественные ragdoll-смерти через Havok | Нагрузка на CPU в больших битвах |
- Каталог: точного метода нет — только тема функции `physics_simulation`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `precomputed_static_lighting_vrad` | партия-01.md:349 | baked_lighting | technical_reference

- Партия: | precomputed_static_lighting_vrad | радиосити + lightmaps для интерьеров | Долгая компиляция световых карт |
- Каталог: точного метода нет — только тема функции `baked_lighting`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `fp16_hdr_rendering` | партия-01.md:394 | rendering_architecture | technical_reference

- Партия: | fp16_hdr_rendering | HDR с FP16 буферами — одна из первых AAA-реализаций 2006 | Полноэкранный блум на слабых GPU |
- Каталог: точного метода нет — только тема функции `rendering_architecture`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `procedural_terrain_erosion` | партия-01.md:395 | procedural_terrain | technical_reference

- Партия: | procedural_terrain_erosion | эрозионные алгоритмы для генерации ландшафта | Сложнее ручной правки |
- Каталог: точного метода нет — только тема функции `procedural_terrain`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `hierarchical_lod_horizon` | партия-01.md:396 | open_world_streaming | technical_reference

- Партия: | hierarchical_lod_horizon | LOD-система с дальностью прорисовки до горизонта | Видимые переключения при быстром движении |
- Каталог: точного метода нет — только тема функции `open_world_streaming`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `baked_occlusion_culling_vis` | партия-01.md:397 | rendering_architecture | technical_reference

- Партия: | baked_occlusion_culling_vis | vis-расчёт для статической геометрии | Не учитывает динамические объекты |
- Каталог: точного метода нет — только тема функции `rendering_architecture`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `havok_physics_integration` | партия-01.md:398 | physics_simulation | technical_reference

- Партия: | havok_physics_integration | Havok для ragdoll и коллизий | Стоимость лицензии |
- Каталог: точного метода нет — только тема функции `physics_simulation`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `radiant_ai_schedule_graph` | партия-01.md:399 | advanced_npc_ai | technical_reference

- Партия: | radiant_ai_schedule_graph | NPC принимают решения (еда/сон/разговоры) на основе расписания и соседей | Сложность балансировки; позже упрощено в Skyrim |
- Каталог: точного метода нет — только тема функции `advanced_npc_ai`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `full_voice_acting_npc` | партия-01.md:400 | advanced_npc_ai | technical_reference

- Партия: | full_voice_acting_npc | первая TES с полной озвучкой всех NPC | Жёсткое ограничение числа диалогов |
- Каталог: точного метода нет — только тема функции `advanced_npc_ai`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `tree_billboard_to_polygon` | партия-01.md:402 | procedural_vegetation | technical_reference

- Партия: | tree_billboard_to_polygon | полностью полигональная растительность (вместо спрайтов Morrowind) | Больше мешей в сцене |
- Каталог: точного метода нет — только тема функции `procedural_vegetation`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `specular_mapping_materials` | партия-01.md:403 | rendering_architecture | technical_reference

- Партия: | specular_mapping_materials | specular-mapping на материалах | Требования к видеопамяти |
- Каталог: точного метода нет — только тема функции `rendering_architecture`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `detective_vision_postprocess` | партия-01.md:452 | post_processing | technical_reference

- Партия: | detective_vision_postprocess | post-process эффект: синийт, выделение интерактивных объектов | Потеря информации за стенами |
- Каталог: точного метода нет — только тема функции `post_processing`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `garry_point_stealth_anchor` | партия-01.md:453 | advanced_npc_ai | technical_requirement

- Партия: | garry_point_stealth_anchor | точки для подвешивания Бэтмена, динамический ИИ врагов с уровнем страха | Ограниченная свобода перемещения |
- Каталог: точного метода нет — только тема функции `advanced_npc_ai`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `physx_particle_simulation` | партия-01.md:454 | physics_simulation | technical_reference

- Партия: | physx_particle_simulation | NVIDIA PhysX для дыма, листьев, ткани, осыпающихся поверхностей | На AMD/Intel без CUDA спецэффекты отсутствуют |
- Каталог: точного метода нет — только тема функции `physics_simulation`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `post_effect_selective` | партия-01.md:457 | post_processing | catalog_method

- Партия: | post_effect_selective | Detective Vision и другие post-эффекты | Стоимость fillrate при наложении |
- Каталог `post_effect_selective` (post_processing): Дорогие экранные эффекты применяются не ко всему кадру, а к отдельным слоям или с пониженным разрешением.
  - Влияет: CPU 0 / GPU -2 / RAM 0 / VRAM 0 / DISK 0 / NET 0 | quality -1 concept 0
  - Плюсы: Быстро внедряется; Эффект заметен сразу
  - Минусы: Возможны артефакты на границах области действия
  - Ограничения: Не подходит для эффектов, требующих полного кадра
  - Условия: —
  - Проверка: Замер времени проходов постобработки в профилировщике GPU. [Unity Profiler, Профилировщик Godot, Unreal Insights] | confidence 0.85 | источник UNITY_QUALITY

## `cape_animation_700_states` | партия-01.md:458 | cloth_simulation | technical_reference

- Партия: | cape_animation_700_states | 700+ анимаций плаща с физикой | Каждый кадр пересчитывается; дорого для CPU |
- Каталог: точного метода нет — только тема функции `cloth_simulation`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `async_loading_pipeline` | партия-01.md:503 | open_world_streaming | catalog_method

- Партия: | async_loading_pipeline | чанковый стриминг мира для бесшовных переходов | Сложная синхронизация с AI/сессиями |
- Каталог `async_loading_pipeline` (open_world_streaming): Загрузка ресурсов выносится в отдельный поток с ограничением времени работы на кадр.
  - Влияет: CPU 1 / GPU 0 / RAM 0 / VRAM 0 / DISK 1 / NET 0 | quality 0 concept 0
  - Плюсы: Устраняет фризы; Улучшает воспринимаемую плавность
  - Минусы: Требует аккуратной работы с зависимостями; Возможна задержка появления объектов
  - Ограничения: Не снижает среднюю нагрузку, только пиковую
  - Условия: —
  - Проверка: Замер максимального времени кадра в сценарии быстрого перемещения. [Unreal Insights, Unity Profiler, Профилировщик Godot] | confidence 0.85 | источник GODOT_THREADS

## `hierarchical_lod_open_zones` | партия-01.md:504 | open_world_streaming | technical_reference

- Партия: | hierarchical_lod_open_zones | LOD для больших зон с растительностью и городами | Перестройка при каждом expansion |
- Каталог: точного метода нет — только тема функции `open_world_streaming`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `multithreaded_jobs` | партия-01.md:505 | rendering_architecture | technical_reference

- Партия: | multithreaded_jobs | Duty Finder матчмейкинг и инфраструктура на отдельных потоках | Стоимость синхронизации |
- Каталог: точного метода нет — только тема функции `rendering_architecture`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `server_authoritative_state` | партия-01.md:506 | multiplayer_netcode | technical_reference

- Партия: | server_authoritative_state | сервер — единственный источник истины для всех транзакций | Задержки на клиенте при плохом пинге |
- Каталог: точного метода нет — только тема функции `multiplayer_netcode`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `headless_dedicated_server` | партия-01.md:507 | multiplayer_netcode | catalog_method

- Партия: | headless_dedicated_server | выделенные серверы по data-центрам (NA/EU/JP/Oceania) | Высокая стоимость инфраструктуры |
- Каталог `headless_dedicated_server` (multiplayer_netcode): Серверная сборка исключает рендер, звук и ввод, оставляя только симуляцию.
  - Влияет: CPU -2 / GPU -2 / RAM -1 / VRAM 0 / DISK 0 / NET 0 | quality 0 concept 0
  - Плюсы: Существенно дешевле эксплуатация; Повышает стабильность сервера
  - Минусы: Требует отдельной сборки иpipeline; Усложняет отладку
  - Ограничения: Требует отделения серверной логики от клиентской
  - Условия: —
  - Проверка: Замер потребления ресурсов сервером на целевом числе игроков. [Unreal Insights, Unity Profiler] | confidence 0.8 | источник UE_NETWORKING

## `differential_patch_pipeline` | партия-01.md:508 | build_delivery | catalog_method

- Партия: | differential_patch_pipeline | маленькие патчи через разницу в данных | Сложнее rollback при ошибках |
- Каталог `differential_patch_pipeline` (build_delivery): Обновления доставляются разницей, а не полными файлами: патч 1 ГБ превращается в 10–100 МБ.
  - Влияет: CPU 0 / GPU 0 / RAM 0 / VRAM 0 / DISK -1 / NET -2 | quality 0 concept 0
  - Плюсы: Патчи качают, а не откладывают; Дешевле CDN и трафик игроков
  - Минусы: Требует версионирования чанков; Сложнее откат
  - Ограничения: Не чинит архитектуру, только доставку
  - Условия: —
  - Проверка: Размер патча типового хотфикса и время обновления на медленном канале. [Unity Profiler] | confidence 0.75 | источник UNITY_ADDRESSABLES

## `gpu_driven_lighting_cache` | партия-01.md:510 | dynamic_global_illumination | technical_reference

- Партия: | gpu_driven_lighting_cache | запечённое освещение с динамическими слоями | Долгая компиляция световых карт |
- Каталог: точного метода нет — только тема функции `dynamic_global_illumination`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `cross_platform_play` | партия-01.md:511 | multiplayer_netcode | technical_reference

- Партия: | cross_platform_play | единый серверный код для Win/Mac/PS/PS5/Xbox | Различия в DirectX vs OpenGL/Vulkan |
- Каталог: точного метода нет — только тема функции `multiplayer_netcode`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `aabb_quadtree_culling` | партия-01.md:512 | rendering_architecture | technical_reference

- Партия: | aabb_quadtree_culling | агрессивное отсечение невидимых зон | Сложнее для open-zone с динамическими эффектами |
- Каталог: точного метода нет — только тема функции `rendering_architecture`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `instance_partitioning` | партия-01.md:513 | multiplayer_netcode | technical_reference

- Партия: | instance_partitioning | каждый инстанс (данж, рейд) изолирован | Сетевая нагрузка при большом числе групп |
- Каталог: точного метода нет — только тема функции `multiplayer_netcode`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `duty_support_npc_party` | партия-01.md:514 | advanced_npc_ai | technical_reference

- Партия: | duty_support_npc_party | AI-партия для соло-прохождения данжей | Ограниченный AI по сравнению с игроком-человеком |
- Каталог: точного метода нет — только тема функции `advanced_npc_ai`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `active_time_event_fate` | партия-01.md:516 | multiplayer_netcode | technical_requirement

- Партия: | active_time_event_fate | FATE — открытые групповые события в overworld | Серверная синхронизация с производительностью клиента |
- Каталог: точного метода нет — только тема функции `multiplayer_netcode`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `havok_physics_wrapper` | партия-02.md:24 | physics_simulation | technical_reference

- Партия: | havok_physics_wrapper | Havok SDK с собственной обёрткой VPhysics для пропсов, QPhysics для NPC; интеграция в лиц-циклы движка | Стоимость лицензии; overhead конвертации на CPU |
- Каталог: точного метода нет — только тема функции `physics_simulation`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `substance_material_system` | партия-02.md:25 | rendering_architecture | technical_reference

- Партия: | substance_material_system | материал задаёт физические свойства, звук шагов, friction, density автоматически | Ограниченный набор параметров |
- Каталог: точного метода нет — только тема функции `rendering_architecture`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `fixed_timestep_physics_60hz` | партия-02.md:26 | physics_simulation | technical_reference

- Партия: | fixed_timestep_physics_60hz | детерминированный шаг 66.6 Гц для предсказуемой физики | Однопоточный скриптовый движок |
- Каталог: точного метода нет — только тема функции `physics_simulation`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `sleep_wake_states` | партия-02.md:27 | physics_simulation | technical_reference

- Партия: | sleep_wake_states | OBJ_AWAKE/STARTSLEEP/SLEEP — спящие объекты не симулируются | Расход на пробуждение для больших составных объектов |
- Каталог: точного метода нет — только тема функции `physics_simulation`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `superman_gravity_gun_fix` | партия-02.md:28 | physics_simulation | technical_reference

- Партия: | superman_gravity_gun_fix | ручной апдейт массы поднятого объекта для предотвращения бесконечного ускорения | Требует физического тюнинга; не универсально |
- Каталог: точного метода нет — только тема функции `physics_simulation`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `hl2_faceposer_facs` | партия-02.md:29 | character_animation | technical_reference

- Партия: | hl2_faceposer_facs | FACS по Ekman — 40 Action Units, процедурная интерполяция через Channel-weights | Нет универсального фотореализма; видны "маски" |
- Каталог: точного метода нет — только тема функции `character_animation`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `procedural_facial_animation_via_chris` | партия-02.md:30 | character_animation | technical_reference

- Партия: | procedural_facial_animation_via_chris | автоматическая генерация выражений из текста (ранее Phoneme) | Требует тюнинга |
- Каталог: точного метода нет — только тема функции `character_animation`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `navmesh_ai_pathfinding` | партия-02.md:31 | ai_pathfinding | technical_reference

- Партия: | navmesh_ai_pathfinding | навигационная сетка вместо вейпоинтов | Сложно строить для процедурных уровней |
- Каталог: точного метода нет — только тема функции `ai_pathfinding`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `dispatchable_strider_combat` | партия-02.md:33 | advanced_npc_ai | technical_requirement

- Партия: | dispatchable_strider_combat | масштабные враги как конечные боссы уровней (Strider в City17) | Нагрузка на ИИ |
- Каталог: точного метода нет — только тема функции `advanced_npc_ai`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `provokable_ai` | партия-02.md:34 | advanced_npc_ai | technical_reference

- Партия: | provokable_ai (antlion, barnacle) | NPC реагируют на дистанцию/звук/свет, не на скрипты | Сложнее отладки |
- Каталог: точного метода нет — только тема функции `advanced_npc_ai`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `hdr_lighting_lost_coast_demo` | партия-02.md:35 | dynamic_lighting | technical_reference

- Партия: | hdr_lighting_lost_coast_demo | HDR в Lost Coast (2005); stencil-histogram для совместимости с ps_2_b и MSAA | Banding артефакты |
- Каталог: точного метода нет — только тема функции `dynamic_lighting`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `64bit_native_port_2005` | партия-02.md:36 | runtime_memory | technical_reference

- Партия: | 64bit_native_port_2005 | декабрь 2005: нативный 64-bit engine для Windows XP Professional x64 | Не во всех сценах стабильнее 32-bit (Techgage) |
- Каталог: точного метода нет — только тема функции `runtime_memory`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `HDR_FP16_phong_fresnel` | партия-02.md:37 | rendering_architecture | technical_reference

- Партия: | HDR_FP16_phong_fresnel | Phong-spec и Fresnel-rim для Alyx; в пещерах Ep2 — полупрозрачная радиосити | Цена DX9 path, ps_2_b совместимости |
- Каталог: точного метода нет — только тема функции `rendering_architecture`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `full_voice_acting_3_party` | партия-02.md:38 | audio_system | technical_reference

- Партия: | full_voice_acting_3_party | актёры озвучки (Louis Gossett Jr., Robert Guillaume, Robert Culp) | Большой размер файлов локализации |
- Каталог: точного метода нет — только тема функции `audio_system`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `steam_preload_distribution` | партия-02.md:39 | build_delivery | technical_reference

- Партия: | steam_preload_distribution | предзагрузка зашифрованных файлов до релиза, разблокировка в дату выхода | Требование Steam-аккаунта с самого начала |
- Каталог: точного метода нет — только тема функции `build_delivery`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `steam_required_drm` | партия-02.md:40 | runtime_security | technical_reference

- Партия: | steam_required_drm | retail-копии требовали Steam-активацию — скандал 2004 | Потеря offline-игры при проблемах со Steam |
- Каталог: точного метода нет — только тема функции `runtime_security`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `alyx_ai_companion` | партия-02.md:90 | advanced_npc_ai | technical_reference

- Партия: | alyx_ai_companion | Alyx как комбатант с "personality code" — не повторяет фразы, реагирует на действия игрока | Требует тщательной настройки |
- Каталог: точного метода нет — только тема функции `advanced_npc_ai`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `gravity_gun_first_weapon` | партия-02.md:91 | physics_simulation | technical_reference

- Партия: | gravity_gun_first_weapon | gravity gun получаешь сразу (не crowbar как в HL2) — паззл-ориентированный геймплей | Меньше традиционного FPS |
- Каталог: точного метода нет — только тема функции `physics_simulation`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `enemy_tactics_ai_upgrade` | партия-02.md:92 | advanced_npc_ai | technical_reference

- Партия: | enemy_tactics_ai_upgrade | Combine солдаты теперь приседают, чтобы уклониться от огня | Дороже на CPU |
- Каталог: точного метода нет — только тема функции `advanced_npc_ai`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `hdr_lighting_story_moments` | партия-02.md:93 | dynamic_lighting | technical_reference

- Партия: | hdr_lighting_story_moments | HDR используется эпизодически для сюжетных моментов | Banding, требует stencil histogram (8-bit) |
- Каталог: точного метода нет — только тема функции `dynamic_lighting`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `phong_fresnel_spec_alys` | партия-02.md:94 | rendering_architecture | technical_reference

- Партия: | phong_fresnel_spec_alys | Phong-spec и Fresnel-rim для Alyx | Удорожание шейдеров |
- Каталог: точного метода нет — только тема функции `rendering_architecture`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `procedural_facial_animation_v2` | партия-02.md:95 | character_animation | technical_reference

- Партия: | procedural_facial_animation_v2 | обновлённая FACS с динамической интерполяцией | Сложная отладка |
- Каталог: точного метода нет — только тема функции `character_animation`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `dynamic_city17_destruction` | партия-02.md:96 | destruction_simulation | technical_reference

- Партия: | dynamic_city17_destruction | город изменился после HL2 — разрушенные здания, инопланетная Xen-фауна | Долгая сборка уровней |
- Каталог: точного метода нет — только тема функции `destruction_simulation`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `script_driven_companion_cover` | партия-02.md:98 | advanced_npc_ai | technical_reference

- Партия: | script_driven_companion_cover | Alyx занимает укрытия и прикрывает игрока | AI overhead |
- Каталог: точного метода нет — только тема функции `advanced_npc_ai`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `open_world_sections` | партия-02.md:137 | open_world_streaming | technical_reference

- Партия: | open_world_sections | менее линейные зоны (White Forest, леса, шахты) | Больше памяти и бюджет |
- Каталог: точного метода нет — только тема функции `open_world_streaming`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `advanced_vehicle_chase` | партия-02.md:138 | multiplayer_netcode | technical_requirement

- Партия: | advanced_vehicle_chase | длинные погонные секции на багги с физикой | Сложная синхронизация |
- Каталог: точного метода нет — только тема функции `multiplayer_netcode`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `improved_alyx_animations` | партия-02.md:141 | character_animation | technical_reference

- Партия: | improved_alyx_animations | Alyx ранена — сложная анимация на земле с лечением | Больше ключевых кадров |
- Каталог: точного метода нет — только тема функции `character_animation`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `physics_puzzle_bridge` | партия-02.md:142 | physics_simulation | technical_reference

- Партия: | physics_puzzle_bridge | самый большой физический паззл на тот момент (мост) | Узкие места collision detection |
- Каталог: точного метода нет — только тема функции `physics_simulation`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `source_engine_ragdoll_physics` | партия-02.md:186 | physics_simulation | technical_reference

- Партия: | source_engine_ragdoll_physics | ragdoll-физика для тел вместо предопределённых death-animations | Больше расход CPU |
- Каталог: точного метода нет — только тема функции `physics_simulation`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `enhanced_physics_world` | партия-02.md:188 | physics_simulation | technical_reference

- Партия: | enhanced_physics_world | бочки, покрышки, бутылки физические; гранаты реалистично катят и рикошетят | Новая стоимость CPU для коллизий |
- Каталог: точного метода нет — только тема функции `physics_simulation`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `cubemap_reflections` | партия-02.md:189 | post_processing | technical_reference

- Партия: | cubemap_reflections | отражения через cube mapping — прицелы отражают окружение | VRAM cost |
- Каталог: точного метода нет — только тема функции `post_processing`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `3d_skyboxes` | партия-02.md:190 | rendering_architecture | technical_reference

- Партия: | 3d_skyboxes | расширение видимого мира за пределы playable area | Удорожание рендера |
- Каталог: точного метода нет — только тема функции `rendering_architecture`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `bump_normal_specular_maps` | партия-02.md:191 | rendering_architecture | technical_reference

- Партия: | bump_normal_specular_maps | bump/normal/specular mapping через DX9 | Требования к GPU |
- Каталог: точного метода нет — только тема функции `rendering_architecture`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `hdr_lighting_2005_update` | партия-02.md:192 | dynamic_lighting | technical_reference

- Партия: | hdr_lighting_2005_update | HDR введён в декабре 2005, постепенно на картах | Stencil histogram стоимость |
- Каталог: точного метода нет — только тема функции `dynamic_lighting`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `max_64_players` | партия-02.md:193 | multiplayer_netcode | technical_reference

- Партия: | max_64_players | удвоение игроков с 32 (CS 1.6) до 64 | Серверная нагрузка |
- Каталог: точного метода нет — только тема функции `multiplayer_netcode`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `source_engine_2006_transition` | партия-02.md:194 | project_architecture | technical_reference

- Партия: | source_engine_2006_transition | переход на Source 2006 (Episode One) с исправлением багов и новыми фичами | Разрыв комьюнити на v34/новый |
- Каталог: точного метода нет — только тема функции `project_architecture`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `source_engine_2013_mp_transition` | партия-02.md:195 | project_architecture | technical_reference

- Партия: | source_engine_2013_mp_transition | переход на Source 2013 MP branch в апреле 2013 + SteamPipe | Унификация кода |
- Каталог: точного метода нет — только тема функции `project_architecture`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `64bit_migration_2025` | партия-02.md:196 | runtime_memory | technical_reference

- Партия: | 64bit_migration_2025 | 18.02.2025 — переход на x64, обновлённый Source 2013 MP из TF2 | Старая кодовая база |
- Каталог: точного метода нет — только тема функции `runtime_memory`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `ai_director` | партия-02.md:241 | advanced_npc_ai | technical_reference

- Партия: | ai_director | динамическая балансировка врагов и предметов на основе навыка игроков | Сложная калибровка |
- Каталог: точного метода нет — только тема функции `advanced_npc_ai`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `music_director_client_side` | партия-02.md:243 | advanced_npc_ai | technical_reference

- Партия: | music_director_client_side | multi-track система на каждом клиенте; spectator слышит микс teammate | Удорожание памяти |
- Каталог: точного метода нет — только тема функции `advanced_npc_ai`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `multicore_rendering` | партия-02.md:244 | rendering_architecture | technical_reference

- Партия: | multicore_rendering | Source 2008 — многопоточность для анимации, рендера, физики | Сложная синхронизация |
- Каталог: точного метода нет — только тема функции `rendering_architecture`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `physics_based_hair_clothing` | партия-02.md:245 | cloth_simulation | technical_reference

- Партия: | physics_based_hair_clothing | улучшенная анимация волос/тканей для реалистичности | Доп. cost |
- Каталог: точного метода нет — только тема функции `cloth_simulation`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `leaning_curved_paths` | партия-02.md:246 | character_animation | technical_reference

- Партия: | leaning_curved_paths | анимация персонажей наклоняется на поворотах | Удорожание скелетной анимации |
- Каталог: точного метода нет — только тема функции `character_animation`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `self_shadowing_normal_map` | партия-02.md:247 | dynamic_shadows | technical_reference

- Партия: | self_shadowing_normal_map | новые карты теней для освещения | VRAM |
- Каталог: точного метода нет — только тема функции `dynamic_shadows`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `advanced_shadow_rendering` | партия-02.md:248 | dynamic_shadows | technical_reference

- Партия: | advanced_shadow_rendering | для художественной атмосферы | GPU cost |
- Каталог: точного метода нет — только тема функции `dynamic_shadows`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `wet_surfaces_fog` | партия-02.md:249 | volumetric_effects | technical_reference

- Партия: | wet_surfaces_fog | визуальные эффекты воды и тумана для атмосферы | Shader cost |
- Каталог: точного метода нет — только тема функции `volumetric_effects`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `dynamic_color_correction` | партия-02.md:250 | post_processing | technical_reference

- Партия: | dynamic_color_correction | адаптивная цветокоррекция под ситуацию | Pass cost |
- Каталог: точного метода нет — только тема функции `post_processing`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `film_grain_vignetting` | партия-02.md:251 | post_processing | technical_reference

- Партия: | film_grain_vignetting | постпроцесс как в фильмах ужасов | Pass cost |
- Каталог: точного метода нет — только тема функции `post_processing`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `infected_path_follower_ai` | партия-02.md:252 | advanced_npc_ai | technical_reference

- Партия: | infected_path_follower_ai | алгоритм path-follower с оценкой геометрии — краучится/прыгает/лезет | CPU heavy |
- Каталог: точного метода нет — только тема функции `advanced_npc_ai`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `mocap_death_animations` | партия-02.md:253 | character_animation | technical_reference

- Партия: | mocap_death_animations | 100 motion-captured death-анимаций проф. каскадёра + ragdoll blend | Production cost |
- Каталог: точного метода нет — только тема функции `character_animation`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `infected_variation_24000` | партия-02.md:254 | geometry_pipeline | technical_reference

- Партия: | infected_variation_24000 | одна модель с 24 000 вариаций (текстуры/геометрия) | Память снижена на 50% |
- Каталог: точного метода нет — только тема функции `geometry_pipeline`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `common_infected_navigation_constraint` | партия-02.md:255 | ai_pathfinding | technical_reference

- Партия: | common_infected_navigation_constraint | дизайнерское правило: "no place survivor stands that zombie cannot reach" | Ограничивает левел-дизайн |
- Каталог: точного метода нет — только тема функции `ai_pathfinding`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `up_to_4_player_coop` | партия-02.md:257 | multiplayer_netcode | technical_reference

- Партия: | up_to_4_player_coop | до 4 игроков + AI bot замена | Server load |
- Каталог: точного метода нет — только тема функции `multiplayer_netcode`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `versus_8_player` | партия-02.md:258 | multiplayer_netcode | technical_reference

- Партия: | versus_8_player | 4 survivors + 4 infected | Конкурентный баланс |
- Каталог: точного метода нет — только тема функции `multiplayer_netcode`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `l4d_authoring_tools_2009` | партия-02.md:261 | project_architecture | technical_reference

- Партия: | l4d_authoring_tools_2009 | Source SDK плагины для SketchUp импорта | UGC |
- Каталог: точного метода нет — только тема функции `project_architecture`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `ai_director_2_0` | партия-02.md:306 | advanced_npc_ai | technical_reference

- Партия: | ai_director_2_0 | переписанный Director — изменение layout уровня, погодных условий, размещения стен в runtime | Сложнее QA |
- Каталог: точного метода нет — только тема функции `advanced_npc_ai`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `director_encourages_longer_paths` | партия-02.md:307 | advanced_npc_ai | technical_reference

- Партия: | director_encourages_longer_paths | вознаграждение за трудные маршруты через спец-амуницию и tier-2 оружие | Больше инвентаря для управления |
- Каталог: точного метода нет — только тема функции `advanced_npc_ai`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `environmental_hazard_simulation` | партия-02.md:312 | physics_simulation | technical_reference

- Партия: | environmental_hazard_simulation | вода из Houdini 3D animation tool для surface maps; flow вместо scroll для реалистичных болот | Production cost |
- Каталог: точного метода нет — только тема функции `physics_simulation`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `houdini_water_flow_maps` | партия-02.md:313 | water_simulation | technical_reference

- Партия: | houdini_water_flow_maps | созданы для Swamp Fever кампании, переиспользованы в Portal 2 | Pipeline cost |
- Каталог: точного метода нет — только тема функции `water_simulation`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `damage_zone_textures` | партия-02.md:314 | rendering_architecture | technical_reference

- Партия: | damage_zone_textures | текстуры с прозрачностью + ellipsoid culling для видимых повреждений на Infected | 13% памяти от базовой системы |
- Каталог: точного метода нет — только тема функции `rendering_architecture`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `scanner_crosshair_customization` | партия-02.md:317 | hair_rendering | technical_reference

- Партия: | scanner_crosshair_customization | поддержка Workshop для spray/crosshair (после 2014) | UGC |
- Каталог: точного метода нет — только тема функции `hair_rendering`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `scavenge_mode_4v4` | партия-02.md:318 | multiplayer_netcode | technical_reference

- Партия: | scavenge_mode_4v4 | генератор требует топлива, команды 4-на-4 | PvP-баланс |
- Каталог: точного метода нет — только тема функции `multiplayer_netcode`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `mac_cross_play_2010` | партия-02.md:321 | multiplayer_netcode | technical_reference

- Партия: | mac_cross_play_2010 | Mac + Windows кросс-платформа | Тех. сложность |
- Каталог: точного метода нет — только тема функции `multiplayer_netcode`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `glicko_rating_competitive` | партия-02.md:376 | multiplayer_netcode | technical_reference

- Партия: | glicko_rating_competitive | Glicko-2 рейтинг для матчмейкинга | Тонкая калибровка |
- Каталог: точного метода нет — только тема функции `multiplayer_netcode`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `valve_anti_cheat` | партия-02.md:377 | runtime_security | technical_reference

- Партия: | valve_anti_cheat | VAC — серверная защита от читов | Evasion-гонка вооружений |
- Каталог: точного метода нет — только тема функции `runtime_security`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `prime_matchmaking_2016` | партия-02.md:378 | multiplayer_netcode | technical_reference

- Партия: | prime_matchmaking_2016 | верификация по телефону для изоляции от смурфов и читеров | Требование к пользователю |
- Каталог: точного метода нет — только тема функции `multiplayer_netcode`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `trust_factor_2017` | партия-02.md:379 | runtime_security | technical_reference

- Партия: | trust_factor_2017 | комбинация in-game и Steam-активности для оценки поведения | Сложный ML |
- Каталог: точного метода нет — только тема функции `runtime_security`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `source_engine_2_transition` | партия-02.md:382 | project_architecture | technical_reference

- Партия: | source_engine_2_transition | переход на Source 2 в Counter-Strike 2 (сентябрь 2023) | Sub-tick input, новые дымы |
- Каталог: точного метода нет — только тема функции `project_architecture`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `sub_tick_input_cs2` | партия-02.md:383 | multiplayer_netcode | technical_reference

- Партия: | sub_tick_input_cs2 | сервер знает точный момент выстрела/прыжка между тиками — latency -3.4мс | Психологическая адаптация игроков |
- Каталог: точного метода нет — только тема функции `multiplayer_netcode`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `panorama_ui_replacement` | партия-02.md:384 | project_architecture | technical_reference

- Партия: | panorama_ui_replacement | замена Scaleform на собственную Panorama UI (декабрь 2018) | Унификация UI |
- Каталог: точного метода нет — только тема функции `project_architecture`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `interconnected_world_no_warping` | партия-03.md:26 | open_world_streaming | technical_reference

- Партия: | interconnected_world_no_warping | единый мир Lordran без warping, только unlockable shortcuts | Сложная навигация для игрока |
- Каталог: точного метода нет — только тема функции `open_world_streaming`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `bonfire_checkpoint_system` | партия-03.md:27 | save_system | technical_reference

- Партия: | bonfire_checkpoint_system | костёр = checkpoint + restore + level-up + respawn врагов | Дисциплина левел-дизайна (точки размещения) |
- Каталог: точного метода нет — только тема функции `save_system`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `humanity_online_state` | партия-03.md:28 | multiplayer_netcode | technical_requirement

- Партия: | humanity_online_state | форма human/hollow определяет доступ к co-op и invasion | Доп. состояние для синхронизации |
- Каталог: точного метода нет — только тема функции `multiplayer_netcode`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `bloodstain_player_messages` | партия-03.md:30 | multiplayer_netcode | technical_reference

- Партия: | bloodstain_player_messages | оставлять сообщения "try jumping", показывать как умерли другие игроки | Серверная логика; abuse-модерация |
- Каталог: точного метода нет — только тема функции `multiplayer_netcode`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `invasion_asymmetric_multiplayer` | партия-03.md:31 | multiplayer_netcode | technical_reference

- Партия: | invasion_asymmetric_multiplayer | PvP-инвазия в SP через matchmaking | Несбалансированный опыт у вторгнутого |
- Каталог: точного метода нет — только тема функции `multiplayer_netcode`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `soul_memory_matchmaking` | партия-03.md:84 | runtime_memory | technical_reference

- Партия: | soul_memory_matchmaking | matchmaking по общему количеству собранных souls | Сложная балансировка при soul-farming |
- Каталог: точного метода нет — только тема функции `runtime_memory`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `mtx_frame_rate_bug` | партия-03.md:88 | physics_simulation | technical_reference

- Партия: | mtx_frame_rate_bug | frame-rate зависимое durability оружия — баг, не исправлен до апреля 2015 | Известный долгоиграющий баг |
- Каталог: точного метода нет — только тема функции `physics_simulation`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `dx11_renderer_sotfs` | партия-03.md:89 | rendering_architecture | technical_reference

- Партия: | dx11_renderer_sotfs | переход на DX11 с DX9 | Дополнительный код-путь |
- Каталог: точного метода нет — только тема функции `rendering_architecture`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `six_player_multiplayer_sotfs` | партия-03.md:90 | multiplayer_netcode | technical_reference

- Партия: | six_player_multiplayer_sotfs | до 6 игроков в кооп (с 4 в оригинале) | Серверная нагрузка |
- Каталог: точного метода нет — только тема функции `multiplayer_netcode`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `hex_grid_ai_navigation` | партия-03.md:92 | advanced_npc_ai | technical_reference

- Партия: | hex_grid_ai_navigation | логика навигации AI на гексах (по аналогии с Civ) | Сложнее debug |
- Каталог: точного метода нет — только тема функции `advanced_npc_ai`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `larger_zones_fewer_count` | партия-03.md:140 | open_world_streaming | technical_reference

- Партия: | larger_zones_fewer_count | меньше зон, но больше по масштабу (под влиянием Zelda BotW) | Длиннее переходы |
- Каталог: точного метода нет — только тема функции `open_world_streaming`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `integrated_multiplayer_scaling` | партия-03.md:144 | multiplayer_netcode | technical_reference

- Партия: | integrated_multiplayer_scaling | matchmaking с password для друзей + язык | Удобство кооп |
- Каталог: точного метода нет — только тема функции `multiplayer_netcode`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `color_grading_per_area` | партия-03.md:145 | post_processing | technical_reference

- Партия: | color_grading_per_area | цветовая палитра по зоне (Fextrlands — пурпур, Ashes — бело-красный) | Удорожание art-pipeline |
- Каталог: точного метода нет — только тема функции `post_processing`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `no_online_multiplayer` | партия-03.md:197 | multiplayer_netcode | technical_reference

- Партия: | no_online_multiplayer | полностью single-player (Miyazaki намеренно) | Нет replayability через PvP |
- Каталог: точного метода нет — только тема функции `multiplayer_netcode`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `mod_support_easy_mode` | партия-03.md:199 | project_architecture | technical_reference

- Партия: | mod_support_easy_mode | моддеры создали easy-mode моды через замедление персонажа | Скандал (FromSoftware не одобрили) |
- Каталог: точного метода нет — только тема функции `project_architecture`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `open_world_torrent_navigation` | партия-03.md:239 | open_world_streaming | technical_reference

- Партия: | open_world_torrent_navigation | открытый мир с лошадью Torrent для перемещения | Удвоенная работа левел-дизайна |
- Каталог: точного метода нет — только тема функции `open_world_streaming`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `sites_of_grace_checkpoints` | партия-03.md:240 | save_system | technical_reference

- Партия: | sites_of_grace_checkpoints | Site of Grace вместо bonfire, плюс Stakes of Marika (опциональные respawn у места смерти) | Переработка respawn-логики |
- Каталог: точного метода нет — только тема функции `save_system`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `spirit_summon_ash` | партия-03.md:242 | advanced_npc_ai | technical_requirement

- Партия: | spirit_summon_ash | призыв NPC-духов как companions (аналог Half-life) | AI overhead, баланс summon-урона |
- Каталог: точного метода нет — только тема функции `advanced_npc_ai`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `large_open_world_chunk_loading` | партия-03.md:245 | open_world_streaming | technical_reference

- Партия: | large_open_world_chunk_loading | стриминг мира на PS4 с ограниченной RAM | Узкое место памяти на старых консолях |
- Каталог: точного метода нет — только тема функции `open_world_streaming`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `dynamic_lighting_per_area` | партия-03.md:247 | dynamic_lighting | technical_reference

- Партия: | dynamic_lighting_per_area | каждая зона имеет уникальную цветовую палитру и lighting (Caelid красный, Liurnia голубой) | Удвоение art-pipeline |
- Каталог: точного метода нет — только тема функции `dynamic_lighting`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `open_world_boss_design` | партия-03.md:249 | open_world_streaming | technical_reference

- Партия: | open_world_boss_design | боссы спрятаны по всему миру, не линейная последовательность | Нелинейный баланс сложности |
- Каталог: точного метода нет — только тема функции `open_world_streaming`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `first_fromsoftware_open_world` | партия-03.md:250 | open_world_streaming | technical_reference

- Партия: | first_fromsoftware_open_world | первая попытка open-world (раньше были только связанные зоны) | Новые паттерны memory management |
- Каталог: точного метода нет — только тема функции `open_world_streaming`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `ray_tracing_dlss_sottr` | партия-03.md:251 | ray_traced_effects | technical_reference

- Партия: | ray_tracing_dlss_sottr | ray tracing (обновление 2024) + DLSS/FSR | Только на новых платформах |
- Каталог: точного метода нет — только тема функции `ray_traced_effects`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `asynchronous_multiplayer` | партия-03.md:253 | multiplayer_netcode | technical_reference

- Партия: | asynchronous_multiplayer | messages + bloodstains + invasions как в Souls | Унаследовано |
- Каталог: точного метода нет — только тема функции `multiplayer_netcode`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `ranked_matchmaking_added` | партия-03.md:302 | multiplayer_netcode | technical_reference

- Партия: | ranked_matchmaking_added | PvP matchmaking добавлен позже (изначально только private lobbies) | Позднее улучшение |
- Каталог: точного метода нет — только тема функции `multiplayer_netcode`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `crowd_30000_npc` | партия-04.md:24 | crowd_simulation | technical_reference

- Партия: | crowd_30000_npc | до 30,000 NPC в одной сцене с индивидуальным AI | Рекордная нагрузка на CPU |
- Каталог: точного метода нет — только тема функции `crowd_simulation`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `paris_1_to_1_scale` | партия-04.md:25 | open_world_streaming | technical_reference

- Партия: | paris_1_to_1_scale | реальные размеры Парижа | Сложнее навигации и оптимизации |
- Каталог: точного метода нет — только тема функции `open_world_streaming`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `crowd_activities_interaction` | партия-04.md:28 | crowd_simulation | technical_reference

- Партия: | crowd_activities_interaction | NPC органично предлагают действия | AI overhead |
- Каталог: точного метода нет — только тема функции `crowd_simulation`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `coop_mission_4p` | партия-04.md:30 | multiplayer_netcode | technical_reference

- Партия: | coop_mission_4p | кооперативные миссии до 4 игроков | Дополнительный netcode |
- Каталог: точного метода нет — только тема функции `multiplayer_netcode`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `hair_works_fur` | партия-04.md:32 | hair_rendering | technical_reference

- Партия: | hair_works_fur | GameWorks hair/fur (после исправлений) | Изначально баг — удалили |
- Каталог: точного метода нет — только тема функции `hair_rendering`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `day_night_cycle_paris` | партия-04.md:33 | volumetric_effects | technical_reference

- Партия: | day_night_cycle_paris | 24-часовой цикл в большом городе | Стоимость симуляции NPC |
- Каталог: точного метода нет — только тема функции `volumetric_effects`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `procedural_paris_buildings` | партия-04.md:34 | procedural_vegetation | technical_reference

- Партия: | procedural_paris_buildings | некоторые здания созданы процедурно | Уникальные баги |
- Каталог: точного метода нет — только тема функции `procedural_vegetation`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `weather_time_anomalies` | партия-04.md:35 | volumetric_effects | technical_reference

- Партия: | weather_time_anomalies | путешествие во времени через разные эпохи | Требует отдельных уровней |
- Каталог: точного метода нет — только тема функции `volumetric_effects`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `noshader_optimization` | партия-04.md:37 | rendering_architecture | technical_reference

- Партия: | noshader_optimization | сначала DX11, но оптимизировано под 900p на консолях | Ограниченный бюджет на рендер |
- Каталог: точного метода нет — только тема функции `rendering_architecture`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `hitbox_combat_system` | партия-04.md:81 | physics_simulation | technical_reference

- Партия: | hitbox_combat_system | hit-box вместо paired animation (как в Souls) | Удорожание AI и анимаций |
- Каталог: точного метода нет — только тема функции `physics_simulation`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `procedural_world_generation` | партия-04.md:82 | procedural_terrain | technical_reference

- Партия: | procedural_world_generation | procedural generation для пустынь и NPC поведения | Доп. QA |
- Каталог: точного метода нет — только тема функции `procedural_terrain`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `eagle_senu_companion` | партия-04.md:83 | advanced_npc_ai | technical_reference

- Партия: | eagle_senu_companion | орёл Сену вместо Eagle Vision — отдельный AI | Удвоенный render для sky+terrain |
- Каталог: точного метода нет — только тема функции `advanced_npc_ai`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `engwe_sensua_animations` | партия-04.md:87 | character_animation | technical_reference

- Партия: | engwe_sensua_animations | новая система анимации от Ubisoft (Sensua) | Удвоенный объём анимаций |
- Каталог: точного метода нет — только тема функции `character_animation`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `dynamic_schedule_npcs` | партия-04.md:88 | advanced_npc_ai | technical_reference

- Партия: | dynamic_schedule_npcs | NPC имеют ежедневный распорядок (работа → сон) | AI overhead, но оправдано |
- Каталог: точного метода нет — только тема функции `advanced_npc_ai`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `underwater_exploration_first_time` | партия-04.md:93 | water_simulation | technical_reference

- Партия: | underwater_exploration_first_time | первое подводное плавание в серии со времён Black Flag | Доп. cost |
- Каталог: точного метода нет — только тема функции `water_simulation`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `hitbox_combat_refined` | партия-04.md:141 | physics_simulation | technical_reference

- Партия: | hitbox_combat_refined | улучшенный из Origins; добавили dodge | Доп. анимации |
- Каталог: точного метода нет — только тема функции `physics_simulation`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `mercenary_nemesis_system` | партия-04.md:144 | advanced_npc_ai | technical_reference

- Партия: | mercenary_nemesis_system | наёмники выслеживают игрока за преступления (а-ля Shadow of Mordor) | AI overhead |
- Каталог: точного метода нет — только тема функции `advanced_npc_ai`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `eagle_ikaros_companion` | партия-04.md:150 | advanced_npc_ai | technical_reference

- Партия: | eagle_ikaros_companion | Орел Икарос как scout (аналог Senu) | Доп. AI |
- Каталог: точного метода нет — только тема функции `advanced_npc_ai`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `settlement_building_management` | партия-04.md:201 | advanced_npc_ai | technical_reference

- Партия: | settlement_building_management | Ravensthorpe — главная база, разблокируемые здания | Доп. AI/simulation |
- Каталог: точного метода нет — только тема функции `advanced_npc_ai`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `jomsviking_shared_npc` | партия-04.md:207 | advanced_npc_ai | technical_reference

- Партия: | jomsviking_shared_npc | созданный викинг отправляется в чужие игры | Серверная инфраструктура |
- Каталог: точного метода нет — только тема функции `advanced_npc_ai`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `day_night_doesnt_affect_mission` | партия-04.md:215 | volumetric_effects | technical_reference

- Партия: | day_night_doesnt_affect_mission | time-of-day не блокирует миссии (vs Unity) | Упрощение прогрессии |
- Каталог: точного метода нет — только тема функции `volumetric_effects`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `faction_war_meta_game` | партия-04.md:268 | multiplayer_netcode | technical_reference

- Партия: | faction_war_meta_game | territory control между 3 фракциями с разными картами | Серверная инфраструктура |
- Каталог: точного метода нет — только тема функции `multiplayer_netcode`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `dedicated_servers_pvp` | партия-04.md:272 | multiplayer_netcode | technical_reference

- Партия: | dedicated_servers_pvp | dedicated servers (P2P в 2017 → dedicated позднее) | Стоимость серверов |
- Каталог: точного метода нет — только тема функции `multiplayer_netcode`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `faction_war_persistent_meta` | партия-04.md:273 | multiplayer_netcode | technical_reference

- Партия: | faction_war_persistent_meta | территория переходит в 6-часовых циклах | Серверная нагрузка |
- Каталог: точного метода нет — только тема функции `multiplayer_netcode`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `for_honor_dedicated_servers` | партия-04.md:274 | multiplayer_netcode | technical_reference

- Партия: | for_honor_dedicated_servers | DED серверы для ranked | Server cost |
- Каталог: точного метода нет — только тема функции `multiplayer_netcode`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `external_animations_5000` | партия-04.md:277 | character_animation | technical_reference

- Партия: | external_animations_5000 | кастомные анимации для каждого Hero | Дороже content creation |
- Каталог: точного метода нет — только тема функции `character_animation`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `4k_60fps_next_gen_update` | партия-04.md:279 | render_scalability | technical_reference

- Партия: | 4k_60fps_next_gen_update | 4K/60 на PS5/Xbox Series | Улучшение разрешения |
- Каталог: точного метода нет — только тема функции `render_scalability`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `radiant_ai_updated` | партия-05.md:24 | advanced_npc_ai | technical_reference

- Партия: | radiant_ai_updated | NPC "делают что хотят под дополнительными параметрами" (Howard) | AI overhead |
- Каталог: точного метода нет — только тема функции `advanced_npc_ai`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `havok_behavior_toolset` | партия-05.md:26 | character_animation | technical_reference

- Партия: | havok_behavior_toolset | плавный переход walk→run→sprint | Лицензия Havok |
- Каталог: точного метода нет — только тема функции `character_animation`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `snow_ash_weather_volumetric` | партия-05.md:29 | volumetric_effects | technical_reference

- Партия: | snow_ash_weather_volumetric | первый в серии с продвинутыми погодными эффектами | Удвоенный workload |
- Каталог: точного метода нет — только тема функции `volumetric_effects`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `dynamic_lighting_snowfall` | партия-05.md:30 | volumetric_effects | technical_reference

- Партия: | dynamic_lighting_snowfall | снег динамически рендерится, не текстура | GPU cost |
- Каталог: точного метода нет — только тема функции `volumetric_effects`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `wind_weighted_trees_branches` | партия-05.md:31 | procedural_vegetation | technical_reference

- Партия: | wind_weighted_trees_branches | физ-ветви деревьев реагируют на ветер | Production cost |
- Каталог: точного метода нет — только тема функции `procedural_vegetation`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `water_surface_flow` | партия-05.md:32 | water_simulation | technical_reference

- Партия: | water_surface_flow | течение воды через surface maps | Удороажние Houdini pipeline |
- Каталог: точного метода нет — только тема функции `water_simulation`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `procedural_side_quests` | партия-05.md:33 | advanced_npc_ai | technical_requirement

- Партия: | procedural_side_quests | уникальные квесты через NPC-schedule | Контент |
- Каталог: точного метода нет — только тема функции `advanced_npc_ai`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `dragon_encounter_random` | партия-05.md:34 | advanced_npc_ai | technical_reference

- Партия: | dragon_encounter_random | драконы появляются случайно в мире | CPU overhead |
- Каталог: точного метода нет — только тема функции `advanced_npc_ai`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `dialogue_facial_animation_FACS` | партия-05.md:36 | character_animation | technical_reference

- Партия: | dialogue_facial_animation_FACS | улучшенные lip-sync | Лицензия |
- Каталог: точного метода нет — только тема функции `character_animation`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `havok_animation_pathfinding` | партия-05.md:39 | ai_pathfinding | technical_reference

- Партия: | havok_animation_pathfinding | стандарт в индустрии | Лицензия |
- Каталог: точного метода нет — только тема функции `ai_pathfinding`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `modding_creation_kit` | партия-05.md:43 | project_architecture | technical_reference

- Партия: | modding_creation_kit | официальный SDK для модов | UGC-экосистема |
- Каталог: точного метода нет — только тема функции `project_architecture`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `layered_armor_system` | партия-05.md:102 | geometry_pipeline | technical_reference

- Партия: | layered_armor_system | слои брони вместо цельного меша | Память |
- Каталог: точного метода нет — только тема функции `geometry_pipeline`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `settlement_building_anywhere` | партия-05.md:106 | advanced_npc_ai | technical_reference

- Партия: | settlement_building_anywhere | C.A.M.P. в F76 / 30+ settlements в F4 | Дополнительный simulation overhead |
- Каталог: точного метода нет — только тема функции `advanced_npc_ai`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `fully_voiced_protagonist_first_time` | партия-05.md:108 | audio_system | technical_reference

- Партия: | fully_voiced_protagonist_first_time | 111,000 строк диалогов | Огромный voice acting |
- Каталог: точного метода нет — только тема функции `audio_system`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `npc_settlement_simulation` | партия-05.md:109 | crowd_simulation | technical_reference

- Партия: | npc_settlement_simulation | жители симулируют потребности (еда, вода, кровати) | AI overhead |
- Каталог: точного метода нет — только тема функции `crowd_simulation`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `volumetric_lighting_nvidia` | партия-05.md:111 | volumetric_effects | technical_reference

- Партия: | volumetric_lighting_nvidia | NVIDIA Volumetric Lighting (gameworks) | Vendor lock-in |
- Каталог: точного метода нет — только тема функции `volumetric_effects`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `temporal_anti_aliasing` | партия-05.md:112 | post_processing | technical_reference

- Партия: | temporal_anti_aliasing | TAA | Без cost |
- Каталог: точного метода нет — только тема функции `post_processing`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `height_fog_dynamic` | партия-05.md:113 | volumetric_effects | technical_reference

- Партия: | height_fog_dynamic | динамический туман | Удобство в мире |
- Каталог: точного метода нет — только тема функции `volumetric_effects`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `screen_space_reflections` | партия-05.md:114 | post_processing | technical_reference

- Партия: | screen_space_reflections | SSR | Reflection на блестящих поверхностях |
- Каталог: точного метода нет — только тема функции `post_processing`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `dynamic_dismemberment` | партия-05.md:115 | destruction_simulation | technical_reference

- Партия: | dynamic_dismemberment | динамическое разрушение тел | GPU cost |
- Каталог: точного метода нет — только тема функции `destruction_simulation`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `wet_surfaces_material` | партия-05.md:116 | rendering_architecture | technical_reference

- Партия: | wet_surfaces_material | материалы реагируют на дождь | Удвоенный рендер-путь |
- Каталог: точного метода нет — только тема функции `rendering_architecture`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `motion_blur` | партия-05.md:117 | post_processing | technical_reference

- Партия: | motion_blur | размытие в движении | Удобство |
- Каталог: точного метода нет — только тема функции `post_processing`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `filmic_tone_mapping` | партия-05.md:118 | post_processing | technical_reference

- Партия: | filmic_tone_mapping | кинематографический тон | Удобство |
- Каталог: точного метода нет — только тема функции `post_processing`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `creation_engine_multiplayer` | партия-05.md:168 | multiplayer_netcode | technical_reference

- Партия: | creation_engine_multiplayer | первый мультиплеер в истории Creation Engine | Огромный porting effort |
- Каталог: точного метода нет — только тема функции `multiplayer_netcode`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `quake_netcode_retrofit` | партия-05.md:169 | multiplayer_netcode | technical_reference

- Партия: | quake_netcode_retrofit | использование netcode из Quake для мультиплеера | Не оптимально для современной игры |
- Каталог: точного метода нет — только тема функции `multiplayer_netcode`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `no_human_npcs_initially` | партия-05.md:170 | advanced_npc_ai | technical_reference

- Партия: | no_human_npcs_initially | все NPC — игроки или боты; текстовые holotapes вместо диалогов | Потеря immersion |
- Каталог: точного метода нет — только тема функции `advanced_npc_ai`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `dedicated_servers_always_on` | партия-05.md:172 | multiplayer_netcode | technical_reference

- Партия: | dedicated_servers_always_on | выделенные серверы Bethesda | Серверные расходы |
- Каталог: точного метода нет — только тема функции `multiplayer_netcode`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `later_npc_humans_wastelanders` | партия-05.md:181 | advanced_npc_ai | technical_reference

- Партия: | later_npc_humans_wastelanders | обновление 2020: полноценные NPC, диалоги, квесты | Спасли игру |
- Каталог: точного метода нет — только тема функции `advanced_npc_ai`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `mod_support_season_7_2024` | партия-05.md:187 | project_architecture | technical_reference

- Партия: | mod_support_season_7_2024 | Creation Club-like поддержка | UGC |
- Каталог: точного метода нет — только тема функции `project_architecture`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `creation_engine_2_first_game` | партия-05.md:237 | project_architecture | technical_reference

- Партия: | creation_engine_2_first_game | новая версия движка (текстуры 4K+ и т.д.) | Удвоенный development cost |
- Каталог: точного метода нет — только тема функции `project_architecture`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `procedural_planet_generation` | партия-05.md:238 | procedural_terrain | technical_reference

- Партия: | procedural_planet_generation | 1000+ планет через procgen с handcrafted POI | Дороже чем handcraft all |
- Каталог: точного метода нет — только тема функции `procedural_terrain`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `1000_planets_landable` | партия-05.md:240 | open_world_streaming | technical_reference

- Партия: | 1000_planets_landable | 1000+ планет, можно приземлиться | Уникальный scale |
- Каталог: точного метода нет — только тема функции `open_world_streaming`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `ship_power_allocation` | партия-05.md:242 | runtime_memory | technical_reference

- Партия: | ship_power_allocation | система распределения энергии в бою | Доп. UI/AI |
- Каталог: точного метода нет — только тема функции `runtime_memory`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `mod_support_creation_kit` | партия-05.md:251 | project_architecture | technical_reference

- Партия: | mod_support_creation_kit | Creation Kit for Starfield (2024) | UGC |
- Каталог: точного метода нет — только тема функции `project_architecture`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `fov_slider_added_late` | партия-05.md:253 | render_scalability | technical_reference

- Партия: | fov_slider_added_late | добавлен в патче 1.8.86 (ноябрь 2023) | Отсутствовал на старте |
- Каталог: точного метода нет — только тема функции `render_scalability`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `hdr_pc_late` | партия-05.md:254 | post_processing | technical_reference

- Партия: | hdr_pc_late | HDR для PC добавлен позже | Консоль имела HDR с релиза |
- Каталог: точного метода нет — только тема функции `post_processing`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `directstorage_support` | партия-05.md:255 | build_delivery | technical_reference

- Партия: | directstorage_support | Xbox Series X поддерживает DirectStorage | Быстрая загрузка |
- Каталог: точного метода нет — только тема функции `build_delivery`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `broken_space_travel_loading_screens` | партия-05.md:256 | open_world_streaming | technical_reference

- Партия: | broken_space_travel_loading_screens | путешествие между планетами = загрузочный экран (НЕ seamless) | Огромный скандал на старте |
- Каталог: точного метода нет — только тема функции `open_world_streaming`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `no_real_seamless_space` | партия-05.md:257 | open_world_streaming | technical_reference

- Партия: | no_real_seamless_space | нет бесшовного космоса между планетами | Разочарование критиков |
- Каталог: точного метода нет — только тема функции `open_world_streaming`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `procedurally_generated_loadouts` | партия-05.md:258 | advanced_npc_ai | technical_requirement

- Партия: | procedurally_generated_loadouts | randomised NPC loadouts | Repetition risk |
- Каталог: точного метода нет — только тема функции `advanced_npc_ai`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `locked_dlss_controversy` | партия-05.md:259 | upscaling_frame_generation | technical_reference

- Партия: | locked_dlss_controversy | на старте нет DLSS — только AMD FSR | Скандал (анти-конкурент) |
- Каталог: точного метода нет — только тема функции `upscaling_frame_generation`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `euphoria_naturalmotion` | партия-06.md:24 | physics_simulation | technical_reference

- Партия: | euphoria_naturalmotion | ragdoll-подобная физика анимации тела (NaturalMotion) | Лицензия + overhead |
- Каталог: точного метода нет — только тема функции `physics_simulation`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `realistic_car_physics` | партия-06.md:25 | vehicle_simulation | technical_reference

- Партия: | realistic_car_physics | более реалистичная физика автомобилей (vs GTA SA) | Игроки жаловались на управление |
- Каталог: точного метода нет — только тема функции `vehicle_simulation`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `100000_photos_new_york` | партия-06.md:32 | art_pipeline | technical_reference

- Партия: | 100000_photos_new_york | 100K фото Нью-Йорка для исследований | Production cost |
- Каталог: точного метода нет — только тема функции `art_pipeline`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `custom_music_station_pc` | партия-06.md:36 | audio_system | technical_reference

- Партия: | custom_music_station_pc | импорт своей музыки на радио | Удобство |
- Каталог: точного метода нет — только тема функции `audio_system`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `multiplayer_32_players` | партия-06.md:37 | multiplayer_netcode | technical_reference

- Партия: | multiplayer_32_players | увеличение с 16 до 32 на PC | Серверная нагрузка |
- Каталог: точного метода нет — только тема функции `multiplayer_netcode`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `physx_optional` | партия-06.md:39 | physics_simulation | technical_reference

- Партия: | physx_optional | опциональная PhysX-физика | Vendor lock-in (Nvidia) |
- Каталог: точного метода нет — только тема функции `physics_simulation`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `dense_ecosystem_wildlife` | партия-06.md:88 | crowd_simulation | technical_reference

- Партия: | dense_ecosystem_wildlife | охота, животные в мире | Доп. AI overhead |
- Каталог: точного метода нет — только тема функции `crowd_simulation`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `dynamic_music_radio` | партия-06.md:91 | audio_system | technical_reference

- Партия: | dynamic_music_radio | 241+ лицензированных треков в 15 станциях + DJ Green Lantern | Огромный лицензионный cost |
- Каталог: точного метода нет — только тема функции `audio_system`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `euphobia_ragdoll_physics` | партия-06.md:92 | physics_simulation | technical_reference

- Партия: | euphobia_ragdoll_physics | NaturalMotion Euphoria для всех NPC | Лицензия |
- Каталог: точного метода нет — только тема функции `physics_simulation`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `bullet_software_rendering` | партия-06.md:93 | rendering_architecture | technical_reference

- Партия: | bullet_software_rendering | дополнительные post-process (depth of field, motion blur) | Удорожание pipeline |
- Каталог: точного метода нет — только тема функции `rendering_architecture`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `flight_simulation_models` | партия-06.md:94 | vehicle_simulation | technical_reference

- Партия: | flight_simulation_models | самолёты, вертолёты, парашюты | Доп. физика |
- Каталог: точного метода нет — только тема функции `vehicle_simulation`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `directx_11_renderer` | партия-06.md:95 | rendering_architecture | technical_reference

- Партия: | directx_11_renderer | DX11 на PC, переделанный рендер | Удороажние портирования |
- Каталог: точного метода нет — только тема функции `rendering_architecture`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `gta_online_separate_client` | партия-06.md:98 | project_architecture | technical_reference

- Партия: | gta_online_separate_client | 1 октября 2013 — онлайн выделен в отдельный продукт | Серверная нагрузка |
- Каталог: точного метода нет — только тема функции `project_architecture`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `nvidia_dlss_added_2025` | партия-06.md:104 | upscaling_frame_generation | technical_reference

- Партия: | nvidia_dlss_added_2025 | апдейт марта 2025 — DLSS для PC | Vendor support |
- Каталог: точного метода нет — только тема функции `upscaling_frame_generation`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `unprecedented_detail_simulation` | партия-06.md:151 | physics_simulation | technical_reference

- Партия: | unprecedented_detail_simulation | знаменитая детализация — ядро лошади при 30° C, шерсть реагирует на ветер | Огромный CPU/HDD cost |
- Каталог: точного метода нет — только тема функции `physics_simulation`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `dynamic_weather_day_night` | партия-06.md:152 | volumetric_effects | technical_reference

- Партия: | dynamic_weather_day_night | полный цикл день/ночь + погода | Доп. overhead |
- Каталог: точного метода нет — только тема функции `volumetric_effects`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `camp_moving_hq` | партия-06.md:153 | advanced_npc_ai | technical_requirement

- Партия: | camp_moving_hq | передвижной лагерь как живой hub | Доп. AI/NPC simulation |
- Каталог: точного метода нет — только тема функции `advanced_npc_ai`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `hair_growth_realistic` | партия-06.md:161 | hair_rendering | technical_reference

- Партия: | hair_growth_realistic | волосы растут со временем | Удороажние |
- Каталог: точного метода нет — только тема функции `hair_rendering`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `ecology_realistic` | партия-06.md:163 | advanced_npc_ai | technical_reference

- Партия: | ecology_realistic | животные взаимодействуют (привлечение хищников, стаи) | Доп. AI |
- Каталог: точного метода нет — только тема функции `advanced_npc_ai`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `ambient_weather_lighting` | партия-06.md:164 | volumetric_effects | technical_reference

- Партия: | ambient_weather_lighting | молнии, туман, дождь, снег динамически | Доп. cost |
- Каталог: точного метода нет — только тема функции `volumetric_effects`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `dynamic_horse_realtime` | партия-06.md:172 | vehicle_simulation | technical_reference

- Партия: | dynamic_horse_realtime | лошади реагируют в реальном времени | Доп. physics |
- Каталог: точного метода нет — только тема функции `vehicle_simulation`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `stranger_random_encounters` | партия-06.md:174 | advanced_npc_ai | technical_requirement

- Партия: | stranger_random_encounters | случайные события с NPC | Доп. контент |
- Каталог: точного метода нет — только тема функции `advanced_npc_ai`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `rd_online_separate_client` | партия-06.md:179 | project_architecture | technical_reference

- Партия: | rd_online_separate_client | 1 декабря 2020 — выделен в отдельный продукт | Серверы |
- Каталог: точного метода нет — только тема функции `project_architecture`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `lighting_environment_improvements` | партия-06.md:229 | dynamic_lighting | technical_reference

- Партия: | lighting_environment_improvements | современные эффекты освещения | Дороже |
- Каталог: точного метода нет — только тема функции `dynamic_lighting`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `high_resolution_textures` | партия-06.md:230 | render_scalability | technical_reference

- Партия: | high_resolution_textures | текстуры 4K | Память |
- Каталог: точного метода нет — только тема функции `render_scalability`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `4k_60_fps_current_gen` | партия-06.md:232 | render_scalability | technical_reference

- Партия: | 4k_60_fps_current_gen | улучшенный фреймрейт на PS5/Xbox Series | Доп. cost |
- Каталог: точного метода нет — только тема функции `render_scalability`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `rockstar_launcher_required` | партия-06.md:234 | runtime_security | technical_reference

- Партия: | rockstar_launcher_required | требуется Launcher | DRM |
- Каталог: точного метода нет — только тема функции `runtime_security`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `apex_engine_grove_street` | партия-06.md:240 | project_architecture | technical_reference

- Партия: | apex_engine_grove_street | не RAGE — UE4 | Архитектурное отличие |
- Каталог: точного метода нет — только тема функции `project_architecture`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `procedural_megawad_snapmap` | партия-07.md:26 | project_architecture | technical_reference

- Партия: | procedural_megawad_snapmap | level editor для community-контента (SnapMap) | Удороажние |
- Каталог: точного метода нет — только тема функции `project_architecture`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `id_tech_6_new_geometry_pipeline` | партия-07.md:27 | rendering_architecture | technical_reference

- Партия: | id_tech_6_new_geometry_pipeline | новая геометрия pipeline | Дороже разработки |
- Каталог: точного метода нет — только тема функции `rendering_architecture`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `id_tech_6_streaming_textures` | партия-07.md:28 | open_world_streaming | technical_reference

- Партия: | id_tech_6_streaming_textures | мега-текстуры через стриминг | Дорого на HDD |
- Каталог: точного метода нет — только тема функции `open_world_streaming`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `async_compute_vulkan` | партия-07.md:29 | rendering_architecture | technical_reference

- Партия: | async_compute_vulkan | async compute через Vulkan API | Vendor-специфично |
- Каталог: точного метода нет — только тема функции `rendering_architecture`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `hdr_pbr_lighting` | партия-07.md:30 | dynamic_lighting | technical_reference

- Партия: | hdr_pbr_lighting | HDR + PBR | Требования к GPU |
- Каталог: точного метода нет — только тема функции `dynamic_lighting`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `gpu_particles_hell_skull` | партия-07.md:31 | particle_systems | technical_reference

- Партия: | gpu_particles_hell_skull | GPU-based частицы | Удороажние эффектов |
- Каталог: точного метода нет — только тема функции `particle_systems`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `pentagram_powerups` | партия-07.md:34 | runtime_memory | technical_reference

- Партия: | pentagram_powerups | pickup на основе классической Doom-механики | Контент-дизайн |
- Каталог: точного метода нет — только тема функции `runtime_memory`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `multiplayer_loadout_2_weapons` | партия-07.md:35 | multiplayer_netcode | technical_reference

- Партия: | multiplayer_loadout_2_weapons | загрузка 2 оружия + модули | Дороже UI |
- Каталог: точного метода нет — только тема функции `multiplayer_netcode`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `vulkan_api_post_launch_patch` | партия-07.md:38 | rendering_architecture | technical_reference

- Партия: | vulkan_api_post_launch_patch | Vulkan API добавлен в патче 11 июля 2016 — **первое в AAA-индустрии внедрение аппаратных очередей асинхронных вычислений (Async Compute) через Vulkan**, на архитектуре AMD GCN (Radeon) прирост производительности **+30–66%** (DF/AMD-блог). Это стало одним из ключевых технических достижений 2016 года | AMD оптимизация |
- Каталог: точного метода нет — только тема функции `rendering_architecture`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `hdr_bloom_2d_array` | партия-07.md:42 | post_processing | technical_reference

- Партия: | hdr_bloom_2d_array | HDR + bloom через 2D array | Дороже |
- Каталог: точного метода нет — только тема функции `post_processing`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `destructible_demon_systems` | партия-07.md:89 | destruction_simulation | technical_reference

- Партия: | destructible_demon_systems | враги разрушаются постепенно с обнажением слабых мест | Дороже анимаций |
- Каталог: точного метода нет — только тема функции `destruction_simulation`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `battlemode_asymmetric_1v2` | партия-07.md:91 | multiplayer_netcode | technical_reference

- Партия: | battlemode_asymmetric_1v2 | 1 Doom Slayer vs 2 player-демонов | Дорого балансировать |
- Каталог: точного метода нет — только тема функции `multiplayer_netcode`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `destructible_demon_armor_strip` | партия-07.md:96 | destruction_simulation | technical_reference

- Партия: | destructible_demon_armor_strip | снятие брони открывает уязвимости | Дороже AI state machine |
- Каталог: точного метода нет — только тема функции `destruction_simulation`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `destructible_demon_critical_state` | партия-07.md:97 | destruction_simulation | technical_reference

- Партия: | destructible_demon_critical_state | критические части тела | Дороже hit-detection |
- Каталог: точного метода нет — только тема функции `destruction_simulation`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `ai_chess_piece_targeting` | партия-07.md:98 | advanced_npc_ai | technical_reference

- Партия: | ai_chess_piece_targeting | враги как шахматные фигуры — нужен правильный порядок | Дороже AI |
- Каталог: точного метода нет — только тема функции `advanced_npc_ai`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `id_tech_7_extended_vulkan_support` | партия-07.md:101 | rendering_architecture | technical_reference

- Партия: | id_tech_7_extended_vulkan_support | Vulkan + RT (PS5/XSX) | Дороже shader compilation |
- Каталог: точного метода нет — только тема функции `rendering_architecture`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `ray_tracing_consoles` | партия-07.md:102 | ray_traced_effects | technical_reference

- Партия: | ray_tracing_consoles | PS5/XSX — RT отражения и освещение | Vendor-specific |
- Каталог: точного метода нет — только тема функции `ray_traced_effects`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `destructible_demo_macro_destructible` | партия-07.md:104 | destruction_simulation | technical_reference

- Партия: | destructible_demo_macro_destructible | macro-разрушение (разрывание врагов) | Дороже шейдеров |
- Каталог: точного метода нет — только тема функции `destruction_simulation`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `destructible_decrement_demon_health` | партия-07.md:106 | destruction_simulation | technical_reference

- Партия: | destructible_decrement_demon_health | Destructible Demon уменьшает health постепенно | Дороже AI |
- Каталог: точного метода нет — только тема функции `destruction_simulation`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `ai_chess_advisor` | партия-07.md:108 | advanced_npc_ai | technical_reference

- Партия: | ai_chess_advisor | приоритезация через AI Advisor | Доп. AI state |
- Каталог: точного метода нет — только тема функции `advanced_npc_ai`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `megatexture_virtual_texturing` | партия-07.md:154 | large_scale_terrain | technical_reference

- Партия: | megatexture_virtual_texturing | id Tech 5 — огромные виртуальные текстуры через стриминг | 1 ТБ uncompressed build (по словам Carmack) |
- Каталог: точного метода нет — только тема функции `large_scale_terrain`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `procedural_textures_partially` | партия-07.md:155 | rendering_architecture | technical_reference

- Партия: | procedural_textures_partially | частично процедурные текстуры | Удороажние pipeline |
- Каталог: точного метода нет — только тема функции `rendering_architecture`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `streaming_from_optical_media` | партия-07.md:156 | open_world_streaming | technical_reference

- Партия: | streaming_from_optical_media | оптимизированный стриминг с Blu-ray/3 DVD | DVD на 360, Blu-ray на PS3 |
- Каталог: точного метода нет — только тема функции `open_world_streaming`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `60hz_optional_oculus_rift_dev_kit` | партия-07.md:157 | split_screen_rendering | technical_reference

- Партия: | 60hz_optional_oculus_rift_dev_kit | оригинальная версия для Oculus Rift DK1 | Удороажние VR |
- Каталог: точного метода нет — только тема функции `split_screen_rendering`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `id_tech_5_animation_mega_file` | партия-07.md:158 | character_animation | technical_reference

- Партия: | id_tech_5_animation_mega_file | анимации в мега-файле (модель персонажа в одном файле) | Удороажние pipeline |
- Каталог: точного метода нет — только тема функции `character_animation`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `open_world_fps_driving` | партия-07.md:159 | open_world_streaming | technical_reference

- Партия: | open_world_fps_driving | гибрид FPS + driving (Mad Max-стиль) | Дороже pipeline |
- Каталог: точного метода нет — только тема функции `open_world_streaming`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `open_world_light_wasteland` | партия-07.md:160 | open_world_streaming | technical_reference

- Партия: | open_world_light_wasteland | открытый мир (для 2011 года — большая редкость) | Удороажние streaming |
- Каталог: точного метода нет — только тема функции `open_world_streaming`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `procedural_lighting_ambient_occlusion` | партия-07.md:161 | dynamic_lighting | technical_reference

- Партия: | procedural_lighting_ambient_occlusion | screen-space ambient occlusion | Удороажние |
- Каталог: точного метода нет — только тема функции `dynamic_lighting`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `multiplayer_road_rage_coop` | партия-07.md:163 | multiplayer_netcode | technical_reference

- Партия: | multiplayer_road_rage_coop | 2 мультиплеер-режима (Road Rage, Legends of the Wasteland) | Доп. контент |
- Каталог: точного метода нет — только тема функции `multiplayer_netcode`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `mac_os_x_no_multiplayer` | партия-07.md:164 | multiplayer_netcode | technical_reference

- Партия: | mac_os_x_no_multiplayer | OS X версия — single-player only | Сокращение пути |
- Каталог: точного метода нет — только тема функции `multiplayer_netcode`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `wingstick_boomerang` | партия-07.md:166 | multiplayer_netcode | technical_reference

- Партия: | wingstick_boomerang | wingstick как стелс-оружие | Контент |
- Каталог: точного метода нет — только тема функции `multiplayer_netcode`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `destruction_box_car_smg` | партия-07.md:170 | destruction_simulation | technical_reference

- Партия: | destruction_box_car_smg | деструкция ящиков/машин | Дороже physics |
- Каталог: точного метода нет — только тема функции `destruction_simulation`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `level_geometry_corrupt_glass` | партия-07.md:171 | rendering_architecture | technical_reference

- Партия: | level_geometry_corrupt_glass | уровни генерируют corruption для визуала | Дороже shader work |
- Каталог: точного метода нет — только тема функции `rendering_architecture`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `id_studio_modding_tools_2013` | партия-07.md:172 | project_architecture | technical_reference

- Партия: | id_studio_modding_tools_2013 | официальный modding набор (Steam) | Удороажние pipeline |
- Каталог: точного метода нет — только тема функции `project_architecture`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `competitive_multiplayer_skirmish` | партия-07.md:174 | multiplayer_netcode | technical_reference

- Партия: | competitive_multiplayer_skirmish | skirmish mode через 2P co-op | Дороже |
- Каталог: точного метода нет — только тема функции `multiplayer_netcode`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `craters_pipeline_shaders` | партия-07.md:177 | rendering_architecture | technical_reference

- Партия: | craters_pipeline_shaders | новый shader pipeline | Удороажние |
- Каталог: точного метода нет — только тема функции `rendering_architecture`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `normal_map_baked_ambient` | партия-07.md:178 | baked_lighting | technical_reference

- Партия: | normal_map_baked_ambient | baked normal maps + ambient occlusion | Удороажние |
- Каталог: точного метода нет — только тема функции `baked_lighting`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `texture_streaming_world_gen` | партия-07.md:179 | open_world_streaming | technical_reference

- Партия: | texture_streaming_world_gen | мировые текстуры генерируются при загрузке | Удороажние memory |
- Каталог: точного метода нет — только тема функции `open_world_streaming`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `saber3d_engine_hybrid` | партия-07.md:225 | project_architecture | technical_reference

- Партия: | saber3d_engine_hybrid | гибрид id Tech + Saber3D (вместо id Tech 6) | Удороажние |
- Каталог: точного метода нет — только тема функции `project_architecture`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `modding_support_none` | партия-07.md:227 | project_architecture | technical_reference

- Партия: | modding_support_none | без моддинга (огромное разочарование) | Нет UGC |
- Каталог: точного метода нет — только тема функции `project_architecture`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `hybrid_idtech_saber_engine` | партия-07.md:236 | project_architecture | technical_reference

- Партия: | hybrid_idtech_saber_engine | редкий гибрид движков | Удороажние поддержки |
- Каталог: точного метода нет — только тема функции `project_architecture`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `server_tickrate_optimized` | партия-07.md:238 | multiplayer_netcode | technical_reference

- Партия: | server_tickrate_optimized | оптимизирован под 120 Hz серверы | Дороже серверов |
- Каталог: точного метода нет — только тема функции `multiplayer_netcode`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `wulf_glass_engine_2017` | партия-07.md:239 | project_architecture | technical_reference

- Партия: | wulf_glass_engine_2017 | community mode (Warfork fork) | UGC |
- Каталог: точного метода нет — только тема функции `project_architecture`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `binoculars_with_electronic_tagging` | партия-08.md:27 | advanced_npc_ai | technical_requirement

- Партия: | binoculars_with_electronic_tagging | бинокль с маркировкой NPC | Удороажние shader |
- Каталог: точного метода нет — только тема функции `advanced_npc_ai`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `procedural_vegetation` | партия-08.md:28 | procedural_vegetation | technical_reference

- Партия: | procedural_vegetation | CryEngine 2 — процедурная растительность | Удороажние pipeline |
- Каталог: точного метода нет — только тема функции `procedural_vegetation`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `volumetric_lighting_volumetric_fog` | партия-08.md:29 | volumetric_effects | technical_reference

- Партия: | volumetric_lighting_volumetric_fog | volumetric lighting + volumetric fog (пионер) | Удороажние cost |
- Каталог: точного метода нет — только тема функции `volumetric_effects`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `soft_shadows_pcss` | партия-08.md:30 | dynamic_shadows | technical_reference

- Партия: | soft_shadows_pcss | PCSS (Percentage Closer Soft Shadows) | Удороажние shader |
- Каталог: точного метода нет — только тема функции `dynamic_shadows`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `motion_blur_object_motion` | партия-08.md:31 | post_processing | technical_reference

- Партия: | motion_blur_object_motion | object motion blur (DX10) | Удороажние |
- Каталог: точного метода нет — только тема функции `post_processing`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `depth_of_field_bokeh` | партия-08.md:32 | post_processing | technical_reference

- Партия: | depth_of_field_bokeh | depth of field с bokeh | Дороже |
- Каталог: точного метода нет — только тема функции `post_processing`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `parallax_occlusion_mapping` | партия-08.md:33 | large_scale_terrain | technical_reference

- Партия: | parallax_occlusion_mapping | parallax occlusion mapping для рельефа | Удороажние |
- Каталог: точного метода нет — только тема функции `large_scale_terrain`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `megatextures_like_id_tech5` | партия-08.md:34 | large_scale_terrain | technical_reference

- Партия: | megatextures_like_id_tech5 | virtual texturing аналог id Tech 5 (CryEngine V) | Дорого на старте |
- Каталог: точного метода нет — только тема функции `large_scale_terrain`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `tesselation_hardware_direct3d11` | партия-08.md:35 | large_scale_terrain | technical_reference

- Партия: | tesselation_hardware_direct3d11 | hardware tessellation (DX11) | Дороже shader |
- Каталог: точного метода нет — только тема функции `large_scale_terrain`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `sandbox_level_editor` | партия-08.md:37 | project_architecture | technical_reference

- Партия: | sandbox_level_editor | Sandbox2 editor — тот же, что Crytek использовали для разработки | Удороажние |
- Каталог: точного метода нет — только тема функции `project_architecture`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `hardware_tessellation_pc` | партия-08.md:38 | large_scale_terrain | technical_reference

- Партия: | hardware_tessellation_pc | hardware tessellation (DX11) | Удороажние shader |
- Каталог: точного метода нет — только тема функции `large_scale_terrain`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `deferred_shading_lighting` | партия-08.md:39 | dynamic_lighting | technical_reference

- Партия: | deferred_shading_lighting | deferred shading (DX10/11) | Удороажние |
- Каталог: точного метода нет — только тема функции `dynamic_lighting`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `1gb_texture_data_85k_shaders` | партия-08.md:40 | runtime_memory | technical_reference

- Партия: | 1gb_texture_data_85k_shaders | 1 ГБ текстур + 85,000 шейдеров | Память |
- Каталог: точного метода нет — только тема функции `runtime_memory`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `dx9_dx10_dual_mode` | партия-08.md:45 | rendering_architecture | technical_reference

- Партия: | dx9_dx10_dual_mode | DX9 режим + DX10 режим (новая технология 2007) | Дороже QA |
- Каталог: точного метода нет — только тема функции `rendering_architecture`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `dx9_very_high_cheat` | партия-08.md:48 | rendering_architecture | technical_reference

- Партия: | dx9_very_high_cheat | обход через конфиг — DX9 Very High ~ DX10 | Бесплатно для хакеров |
- Каталог: точного метода нет — только тема функции `rendering_architecture`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `multiplayer_2014_terminated` | партия-08.md:49 | multiplayer_netcode | technical_reference

- Партия: | multiplayer_2014_terminated | multiplayer отключён 30.05.2014 (закрытие GameSpy) | Потеря функционала |
- Каталог: точного метода нет — только тема функции `multiplayer_netcode`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `console_2011_no_multiplayer_no_dlc` | партия-08.md:50 | multiplayer_netcode | technical_reference

- Партия: | console_2011_no_multiplayer_no_dlc | консоли без multiplayer и без Warhead и без "Ascension" | Упрощение |
- Каталог: точного метода нет — только тема функции `multiplayer_netcode`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `tessellation_dx11_pc` | партия-08.md:106 | large_scale_terrain | technical_reference

- Партия: | tessellation_dx11_pc | DX11 с tessellation (PC патч 1.9) | Vendor lock-in (Nvidia bias) |
- Каталог: точного метода нет — только тема функции `large_scale_terrain`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `hrtf_audio_oculus_2` | партия-08.md:107 | split_screen_rendering | technical_reference

- Партия: | hrtf_audio_oculus_2 | HRTF audio для позиционного звука | Дороже audio |
- Каталог: точного метода нет — только тема функции `split_screen_rendering`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `stereo_3d_support` | партия-08.md:108 | split_screen_rendering | technical_reference

- Партия: | stereo_3d_support | native stereoscopic 3D на PC/PS3 | Дороже pipeline |
- Каталог: точного метода нет — только тема функции `split_screen_rendering`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `lego_manhattan_destructible` | партия-08.md:111 | destruction_simulation | technical_reference

- Партия: | lego_manhattan_destructible | разрушаемость Manhattan | Удороажние physics |
- Каталог: точного метода нет — только тема функции `destruction_simulation`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `steamworks_pc_multiplayer` | партия-08.md:112 | multiplayer_netcode | technical_reference

- Партия: | steamworks_pc_multiplayer | Steamworks integration (PC) | Удороажние network |
- Каталог: точного метода нет — только тема функции `multiplayer_netcode`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `directx_11_high_res_textures` | партия-08.md:113 | rendering_architecture | technical_reference

- Партия: | directx_11_high_res_textures | DX11 Ultra Upgrade (патч 1.9) | Дороже |
- Каталог: точного метода нет — только тема функции `rendering_architecture`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `high_resolution_texture_pack` | партия-08.md:114 | render_scalability | technical_reference

- Партия: | high_resolution_texture_pack | high-res текстуры (768 MB+ VRAM) | Память |
- Каталог: точного метода нет — только тема функции `render_scalability`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `4gb_gddr3_pc_recommended` | партия-08.md:115 | runtime_memory | technical_reference

- Партия: | 4gb_gddr3_pc_recommended | Crytek рекомендовала 4 GB RAM (DDR3) | Дорого |
- Каталог: точного метода нет — только тема функции `runtime_memory`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `multiplayer_hacked_beta_leak` | партия-08.md:117 | multiplayer_netcode | technical_reference

- Партия: | multiplayer_hacked_beta_leak | бета утекла 11.02.2011 (Cevat Yerli: "deeply disappointed") | Промо-проблема |
- Каталог: точного метода нет — только тема функции `multiplayer_netcode`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `multiplayer_servers_killed_2014` | партия-08.md:118 | multiplayer_netcode | technical_reference

- Партия: | multiplayer_servers_killed_2014 | GameSpy killed 30.05.2014 — мультиплеер мёртв | Потеря функционала |
- Каталог: точного метода нет — только тема функции `multiplayer_netcode`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `tesselation_abuse_criticism` | партия-08.md:122 | large_scale_terrain | technical_reference

- Партия: | tesselation_abuse_criticism | избыточная тесселяция (исключительно Nvidia) | Критика |
- Каталог: точного метода нет — только тема функции `large_scale_terrain`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `seven_wonders_open_levels` | партия-08.md:173 | open_world_streaming | technical_reference

- Партия: | seven_wonders_open_levels | 7 открытых уровней (Seven Wonders) | Дороже production |
- Каталог: точного метода нет — только тема функции `open_world_streaming`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `performance_capture_prophet` | партия-08.md:176 | character_animation | technical_reference

- Партия: | performance_capture_prophet | performance capture (впервые для серии) | Дороже |
- Каталог: точного метода нет — только тема функции `character_animation`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `dx11_pc_required` | партия-08.md:179 | rendering_architecture | technical_reference

- Партия: | dx11_pc_required | PC-версия требует DX11 | Исключает старые GPU |
- Каталог: точного метода нет — только тема функции `rendering_architecture`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `per_voxel_lighting_hbao_etc` | партия-08.md:180 | dynamic_lighting | technical_reference

- Партия: | per_voxel_lighting_hbao_etc | per-voxel освещение (HBAO+) | Удороажние cost |
- Каталог: точного метода нет — только тема функции `dynamic_lighting`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `dynamic_music_aggression` | партия-08.md:188 | audio_system | technical_reference

- Партия: | dynamic_music_aggression | музыка реагирует на стиль игры | Удороажние audio |
- Каталог: точного метода нет — только тема функции `audio_system`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `ray_tracing_2024` | партия-08.md:238 | ray_traced_effects | technical_reference

- Партия: | ray_tracing_2024 | hardware RT в обновлении "1896" | Удороажние |
- Каталог: точного метода нет — только тема функции `ray_traced_effects`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `4k_ps5_xsx_support` | партия-08.md:241 | render_scalability | technical_reference

- Партия: | 4k_ps5_xsx_support | полная 4K на PS5/Xbox Series | Доп. cost |
- Каталог: точного метода нет — только тема функции `render_scalability`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `improved_engine_2024` | партия-08.md:242 | project_architecture | technical_reference

- Партия: | improved_engine_2024 | CryEngine 5.11+ обновление | Удороажние pipeline |
- Каталог: точного метода нет — только тема функции `project_architecture`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `ambient_zombie_spawn` | партия-08.md:245 | advanced_npc_ai | technical_reference

- Партия: | ambient_zombie_spawn | ambient zombie spawn для напряжения | Дороже AI |
- Каталог: точного метода нет — только тема функции `advanced_npc_ai`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `multi_hunter_2v12` | партия-08.md:247 | multiplayer_netcode | technical_reference

- Партия: | multi_hunter_2v12 | до 12 игроков в Bounty Hunt, 18 в Soul Survivor | Серверная нагрузка |
- Каталог: точного метода нет — только тема функции `multiplayer_netcode`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `no_crossplay_ps4_xbox` | партия-08.md:252 | multiplayer_netcode | technical_reference

- Партия: | no_crossplay_ps4_xbox | нет crossplay между PS4/Xbox (только PC + консоль одного семейства) | Серверная архитектура |
- Каталог: точного метода нет — только тема функции `multiplayer_netcode`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `levolution_dynamic_destruction` | партия-09.md:24 | destruction_simulation | technical_reference

- Партия: | levolution_dynamic_destruction | уровни меняются от действий игроков (разрушение зданий) | Дороже physics |
- Каталог: точного метода нет — только тема функции `destruction_simulation`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `networked_water_simulation` | партия-09.md:25 | multiplayer_netcode | technical_reference

- Партия: | networked_water_simulation | вода синхронизирована между всеми игроками | Серверный overhead |
- Каталог: точного метода нет — только тема функции `multiplayer_netcode`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `64_player_multiplayer` | партия-09.md:27 | multiplayer_netcode | technical_reference

- Партия: | 64_player_multiplayer | до 64 игроков (PC/PS4/XB1), 24 на PS3/360 | Серверный overhead |
- Каталог: точного метода нет — только тема функции `multiplayer_netcode`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `amd_mantle_partnership` | партия-09.md:31 | rendering_architecture | technical_reference

- Партия: | amd_mantle_partnership | партнёрство с AMD для Mantle API | Vendor-specific (заброшено) |
- Каталог: точного метода нет — только тема функции `rendering_architecture`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `tessellation_overhaul` | партия-09.md:32 | large_scale_terrain | technical_reference

- Партия: | tessellation_overhaul | тесселяция в Frostbite 3 переделана | Удороажние shader |
- Каталог: точного метода нет — только тема функции `large_scale_terrain`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `dynamic_weather_volumetric` | партия-09.md:33 | volumetric_effects | technical_reference

- Партия: | dynamic_weather_volumetric | объёмные облака и погода | Удороажние |
- Каталог: точного метода нет — только тема функции `volumetric_effects`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `destruction_2` | партия-09.md:34 | destruction_simulation | technical_reference

- Партия: | destruction_2.0_levolution | 2.0 версия разрушений (ранее в Frostbite 2 Bad Company 2) | Дороже physics |
- Каталог: точного метода нет — только тема функции `destruction_simulation`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `networked_water_full_wave_simulation` | партия-09.md:35 | multiplayer_netcode | technical_reference

- Партия: | networked_water_full_wave_simulation | вода с полной симуляцией волн | Удороажние |
- Каталог: точного метода нет — только тема функции `multiplayer_netcode`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `full_hd_rendering_pc` | партия-09.md:36 | render_scalability | technical_reference

- Партия: | full_hd_rendering_pc | нативный 1080p на PC | Память |
- Каталог: точного метода нет — только тема функции `render_scalability`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `parallax_occlusion_mapping_frostbite` | партия-09.md:37 | large_scale_terrain | technical_reference

- Партия: | parallax_occlusion_mapping_frostbite | POM в Frostbite | Удороажние shader |
- Каталог: точного метода нет — только тема функции `large_scale_terrain`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `hbao_horizon_based_ao` | партия-09.md:38 | post_processing | technical_reference

- Партия: | hbao_horizon_based_ao | HBAO+ на PC | Дороже |
- Каталог: точного метода нет — только тема функции `post_processing`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `tesselated_displacement_maps` | партия-09.md:39 | large_scale_terrain | technical_reference

- Партия: | tesselated_displacement_maps | displacement mapping с тесселяцией | Дороже |
- Каталог: точного метода нет — только тема функции `large_scale_terrain`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `deferred_renderer_modular` | партия-09.md:40 | rendering_architecture | technical_reference

- Партия: | deferred_renderer_modular | модульный deferred renderer | Дороже |
- Каталог: точного метода нет — только тема функции `rendering_architecture`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `4d_dissolve_transitions` | партия-09.md:41 | character_animation | technical_reference

- Партия: | 4d_dissolve_transitions | 4D dissolve для анимаций (seamless transitions) | Удороажние |
- Каталог: точного метода нет — только тема функции `character_animation`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `volumetrics_indoor_outdoor` | партия-09.md:42 | volumetric_effects | technical_reference

- Партия: | volumetrics_indoor_outdoor | volumetric lighting (HDR volumetric) | Удороажние |
- Каталог: точного метода нет — только тема функции `volumetric_effects`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `surface_tessellation_displacement` | партия-09.md:43 | large_scale_terrain | technical_reference

- Партия: | surface_tessellation_displacement | surface displacement через тесселяцию | Дороже |
- Каталог: точного метода нет — только тема функции `large_scale_terrain`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `dynamic_resolution_optional` | партия-09.md:44 | render_scalability | technical_reference

- Партия: | dynamic_resolution_optional | динамическое разрешение на PS4/XB1 | Удороажние |
- Каталог: точного метода нет — только тема функции `render_scalability`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `rich_presence_landscape` | партия-09.md:45 | open_world_streaming | technical_reference

- Партия: | rich_presence_landscape | обширные ландшафты (China Rising, Naval Strike и т.д.) | Память |
- Каталог: точного метода нет — только тема функции `open_world_streaming`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `cloud_destruction_debris` | партия-09.md:46 | destruction_simulation | technical_reference

- Партия: | cloud_destruction_debris | облачные системы разрушения | Дороже |
- Каталог: точного метода нет — только тема функции `destruction_simulation`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `25_hz_tickrate` | партия-09.md:47 | multiplayer_netcode | technical_reference

- Партия: | 25_hz_tickrate | сетевой тикрейт 25 Hz на 64 игроков | Серверный overhead |
- Каталог: точного метода нет — только тема функции `multiplayer_netcode`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `amd_mantle_api_debut_2013` | партия-09.md:48 | rendering_architecture | technical_reference

- Партия: | amd_mantle_api_debut_2013 | **исторический дебют API AMD Mantle на ПК в декабре 2013** — позволил обойти избыточные накладные расходы драйвера DirectX 11; лёг в основу стандартов Vulkan и DirectX 12 | Удороажние QA/драйверов |
- Каталог: точного метода нет — только тема функции `rendering_architecture`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `hd_texture_pool` | партия-09.md:50 | rendering_architecture | technical_reference

- Партия: | hd_texture_pool | HD текстурный пул 4K | Память |
- Каталог: точного метода нет — только тема функции `rendering_architecture`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `ww1_destruction_expanded` | партия-09.md:95 | destruction_simulation | technical_reference

- Партия: | ww1_destruction_expanded | расширенная WWI-разрушаемость (траншеи, укрепления) | Дороже physics |
- Каталог: точного метода нет — только тема функции `destruction_simulation`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `operations_multi_map_mode` | партия-09.md:97 | multiplayer_netcode | technical_reference

- Партия: | operations_multi_map_mode | Operations — несколько карт подряд (50+ игроков) | Дороже серверной логики |
- Каталог: точного метода нет — только тема функции `multiplayer_netcode`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `horses_in_multiplayer` | партия-09.md:101 | multiplayer_netcode | technical_reference

- Партия: | horses_in_multiplayer | лошади как транспорт (новая механика для серии) | Дороже physics |
- Каталог: точного метода нет — только тема функции `multiplayer_netcode`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `dynamic_weather_dust_storm` | партия-09.md:102 | volumetric_effects | technical_reference

- Партия: | dynamic_weather_dust_storm | динамическая погода (песчаные бури на Sinai) | Дороже эффектов |
- Каталог: точного метода нет — только тема функции `volumetric_effects`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `voice_overs_native_language` | партия-09.md:110 | audio_system | technical_reference

- Партия: | voice_overs_native_language | озвучка War Stories на родном языке (англ., франц., итал., арабск.) | Дороже |
- Каталог: точного метода нет — только тема функции `audio_system`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `real_time_ray_tracing_reflections` | партия-09.md:161 | ray_traced_effects | technical_reference

- Партия: | real_time_ray_tracing_reflections | DXR RT-отражения (только Nvidia RTX) | Дорого на HW |
- Каталог: точного метода нет — только тема функции `ray_traced_effects`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `dlss_deep_learning_super_sampling` | партия-09.md:162 | upscaling_frame_generation | technical_reference

- Партия: | dlss_deep_learning_super_sampling | DLSS upscaling (только RTX) | Vendor-specific |
- Каталог: точного метода нет — только тема функции `upscaling_frame_generation`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `fortification_system` | партия-09.md:167 | destruction_simulation | technical_reference

- Партия: | fortification_system | укрепления с аммо, минами | Дороже контента |
- Каталог: точного метода нет — только тема функции `destruction_simulation`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `ray_tracing_dxr` | партия-09.md:168 | ray_traced_effects | technical_reference

- Партия: | ray_tracing_dxr | Microsoft DXR API | Vendor-specific |
- Каталог: точного метода нет — только тема функции `ray_traced_effects`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `combined_arms_coop` | партия-09.md:171 | multiplayer_netcode | technical_reference

- Партия: | combined_arms_coop | 4-player coop | Дороже networking |
- Каталог: точного метода нет — только тема функции `multiplayer_netcode`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `animation_procedural_motion` | партия-09.md:174 | character_animation | technical_reference

- Партия: | animation_procedural_motion | процедурные анимации движения | Дороже |
- Каталог: точного метода нет — только тема функции `character_animation`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `dxr_ray_traced_reflections_dx12` | партия-09.md:175 | ray_traced_effects | technical_reference

- Партия: | dxr_ray_traced_reflections_dx12 | DXR через DX12 (Windows 10) — **первый коммерческий релиз с поддержкой гибридной аппаратной трассировки лучей DXR (отражения) + DLSS 1.0 в ноябре 2018** | Vendor-specific |
- Каталог: точного метода нет — только тема функции `ray_traced_effects`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `physical_based_rendering` | партия-09.md:177 | rendering_architecture | technical_reference

- Партия: | physical_based_rendering | PBR для всех материалов | Стандарт |
- Каталог: точного метода нет — только тема функции `rendering_architecture`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `hdr_display_support` | партия-09.md:178 | post_processing | technical_reference

- Партия: | hdr_display_support | HDR-выход | Vendor-specific |
- Каталог: точного метода нет — только тема функции `post_processing`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `no_ray_tracing_consoles` | партия-09.md:179 | ray_traced_effects | technical_reference

- Партия: | no_ray_tracing_consoles | RT только на PC с RTX | Консольное упрощение |
- Каталог: точного метода нет — только тема функции `ray_traced_effects`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `shaders_dx12_async_compute` | партия-09.md:180 | rendering_architecture | technical_reference

- Партия: | shaders_dx12_async_compute | async compute через DX12 | Дороже |
- Каталог: точного метода нет — только тема функции `rendering_architecture`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `voxel_gi_approximation` | партия-09.md:181 | dynamic_global_illumination | technical_reference

- Партия: | voxel_gi_approximation | voxel-based GI approximation | Удороажние |
- Каталог: точного метода нет — только тема функции `dynamic_global_illumination`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `wave_destruction_advanced` | партия-09.md:182 | destruction_simulation | technical_reference

- Партия: | wave_destruction_advanced | расширенная разрушаемость зданий | Дороже physics |
- Каталог: точного метода нет — только тема функции `destruction_simulation`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `firestorm_64_players_br` | партия-09.md:184 | multiplayer_netcode | technical_reference

- Партия: | firestorm_64_players_br | 64 игрока в Firestorm BR | Дороже server |
- Каталог: точного метода нет — только тема функции `multiplayer_netcode`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `128_player_multiplayer_pc_nextgen` | партия-09.md:228 | multiplayer_netcode | technical_reference

- Партия: | 128_player_multiplayer_pc_nextgen | 128 игроков на PC/PS5/XSX (64 на PS4/XB1) | Серверный overhead |
- Каталог: точного метода нет — только тема функции `multiplayer_netcode`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `extreme_weather_tornado_sandstorm` | партия-09.md:230 | volumetric_effects | technical_reference

- Партия: | extreme_weather_tornado_sandstorm | экстремальная погода (торнадо, песчаные бури) | Дороже physics |
- Каталог: точного метода нет — только тема функции `volumetric_effects`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `battlefield_portal_modding` | партия-09.md:233 | project_architecture | technical_reference

- Партия: | battlefield_portal_modding | Battlefield Portal — community rules modification (логика правил) | Дороже UI |
- Каталог: точного метода нет — только тема функции `project_architecture`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `cross_play_first_battlefield` | партия-09.md:235 | multiplayer_netcode | technical_reference

- Партия: | cross_play_first_battlefield | первый Battlefield с кросс-играем (PS5/Win/XSX) | Удороажние network |
- Каталог: точного метода нет — только тема функции `multiplayer_netcode`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `map_clustering_design` | партия-09.md:237 | open_world_streaming | technical_reference

- Партия: | map_clustering_design | карты "несколько меньших, сшитых вместе" | Дороже дизайна |
- Каталог: точного метода нет — только тема функции `open_world_streaming`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `weather_affects_gameplay` | партия-09.md:241 | volumetric_effects | technical_reference

- Партия: | weather_affects_gameplay | погода влияет на геймплей (торнадо поднимает технику) | Дороже physics |
- Каталог: точного метода нет — только тема функции `volumetric_effects`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `no_mod_tools` | партия-09.md:247 | project_architecture | technical_reference

- Партия: | no_mod_tools | нет mod-tools для PC (в отличие от BF4) | Потеря community |
- Каталог: точного метода нет — только тема функции `project_architecture`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `heroes_vs_villains_4v4` | партия-09.md:307 | multiplayer_netcode | technical_reference

- Партия: | heroes_vs_villains_4v4 | 4v4 Heroes-only режим | Дороже |
- Каталог: точного метода нет — только тема функции `multiplayer_netcode`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `extraction_2v2` | партия-09.md:308 | multiplayer_netcode | technical_reference

- Партия: | extraction_2v2 | 2v2 extraction | Дороже |
- Каталог: точного метода нет — только тема функции `multiplayer_netcode`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `cel_shading_pbr` | партия-09.md:311 | rendering_architecture | technical_reference

- Партия: | cel_shading_pbr | сочетание cel-shading и PBR | Дороже rendering |
- Каталог: точного метода нет — только тема функции `rendering_architecture`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `ray_tracing_post_launch` | партия-09.md:312 | ray_traced_effects | technical_reference

- Партия: | ray_tracing_post_launch | RT добавлен в пост-запуске (Xbox Series X) | Vendor-specific |
- Каталог: точного метода нет — только тема функции `ray_traced_effects`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `physicalized_hud_no_minimap` | партия-10.md:23 | project_architecture | technical_reference

- Партия: | physicalized_hud_no_minimap | информация на запястье (часы), маске, фонарике — без минимапы | Дороже контента |
- Каталог: точного метода нет — только тема функции `project_architecture`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `human_npc_karma_system` | партия-10.md:31 | advanced_npc_ai | technical_reference

- Партия: | human_npc_karma_system | моральные выборы влияют на концовку | Дороже контента |
- Каталог: точного метода нет — только тема функции `advanced_npc_ai`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `weather_time_dynamic_weather` | партия-10.md:32 | volumetric_effects | technical_reference

- Партия: | weather_time_dynamic_weather | цикл день/ночь + динамическая погода | Дороже physics |
- Каталог: точного метода нет — только тема функции `volumetric_effects`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `day_night_affects_npc_behavior` | партия-10.md:33 | advanced_npc_ai | technical_reference

- Партия: | day_night_affects_npc_behavior | враги в лагере днём бодрствуют, ночью спят | Дороже AI |
- Каталог: точного метода нет — только тема функции `advanced_npc_ai`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `rain_masks_footsteps` | партия-10.md:34 | audio_system | technical_reference

- Партия: | rain_masks_footsteps | дождь маскирует шаги (для стелса) | Удороажние audio |
- Каталог: точного метода нет — только тема функции `audio_system`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `open_areas_with_aurora_train` | партия-10.md:36 | open_world_streaming | technical_reference

- Партия: | open_areas_with_aurora_train | открытые зоны с поездом Aurora как хаб | Удороажние streaming |
- Каталог: точного метода нет — только тема функции `open_world_streaming`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `realistic_dynamic_weather_storms` | партия-10.md:44 | volumetric_effects | technical_reference

- Партия: | realistic_dynamic_weather_storms | песчаные бури, дождь, снег | Дороже physics |
- Каталог: точного метода нет — только тема функции `volumetric_effects`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `minimal_subsurface_rendering` | партия-10.md:45 | rendering_architecture | technical_reference

- Партия: | minimal_subsurface_rendering | RT на Enhanced Edition | Vendor-specific |
- Каталог: точного метода нет — только тема функции `rendering_architecture`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `global_illumination_dlss` | партия-10.md:46 | upscaling_frame_generation | technical_reference

- Партия: | global_illumination_dlss | DLSS + GI на Enhanced Edition | Vendor-specific |
- Каталог: точного метода нет — только тема функции `upscaling_frame_generation`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `ray_tracing_xbox_series_x` | партия-10.md:47 | ray_traced_effects | technical_reference

- Партия: | ray_tracing_xbox_series_x | RT на next-gen консолях | Vendor-specific |
- Каталог: точного метода нет — только тема функции `ray_traced_effects`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `steam_workshop_mod_support` | партия-10.md:49 | project_architecture | technical_reference

- Партия: | steam_workshop_mod_support | официальный SDK (январь 2023) | Удороажние |
- Каталог: точного метода нет — только тема функции `project_architecture`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `fully_ray_traced_enhanced_2021` | партия-10.md:54 | path_tracing | technical_reference

- Партия: | fully_ray_traced_enhanced_2021 | Enhanced Edition (14.06.2021) — **полностью удалён растеризованный конвейер освещения**: из сборника 2021 года **полностью вырезаны запечённые световые карты (lightmaps) и традиционные точечные растеризованные источники света и теневые буферы**, сделав графический пайплайн **чисто аппаратно-трассируемым (RT-only)** — DDGI + VRS Tier 1 + DLSS 2.1 + Vulkan; обязательное требование RT-карты (NVIDIA RTX или AMD RDNA 2) | Дороже рендера |
- Каталог: точного метода нет — только тема функции `path_tracing`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `physicalized_ui_minimal_hud` | партия-10.md:104 | project_architecture | technical_reference

- Партия: | physicalized_ui_minimal_hud | информация в игровом мире, а не на HUD | Дороже production |
- Каталог: точного метода нет — только тема функции `project_architecture`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `social_engagement_detector_aug` | партия-10.md:111 | advanced_npc_ai | technical_requirement

- Партия: | social_engagement_detector_aug | Social Aug — анализ мимики NPC | Дороже AI |
- Каталог: точного метода нет — только тема функции `advanced_npc_ai`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `npc_dynamic_ai` | партия-10.md:112 | advanced_npc_ai | technical_reference

- Партия: | npc_dynamic_ai | NPC меняют поведение по ситуации (днём/ночью) | Дороже AI |
- Каталог: точного метода нет — только тема функции `advanced_npc_ai`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `prague_hub_open_world` | партия-10.md:113 | open_world_streaming | technical_reference

- Партия: | prague_hub_open_world | Прага как открытый hub с малыми районами | Удороажние streaming |
- Каталог: точного метода нет — только тема функции `open_world_streaming`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `city_xploration_day_night` | партия-10.md:117 | volumetric_effects | technical_reference

- Партия: | city_xploration_day_night | NPC поведение меняется днём/ночью | Дороже AI |
- Каталог: точного метода нет — только тема функции `volumetric_effects`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `pbr_physically_based_rendering` | партия-10.md:118 | rendering_architecture | technical_reference

- Партия: | pbr_physically_based_rendering | PBR для всех материалов | Удороажние rendering |
- Каталог: точного метода нет — только тема функции `rendering_architecture`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `directx_12_pc` | партия-10.md:119 | rendering_architecture | technical_reference

- Партия: | directx_12_pc | DX12 на PC (оптимизация Nixxes) | Vendor-specific |
- Каталог: точного метода нет — только тема функции `rendering_architecture`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `tressfx_hair_amd` | партия-10.md:120 | hair_rendering | technical_reference

- Партия: | tressfx_hair_amd | TressFX для волос (сотрудничество с AMD) | Vendor-specific |
- Каталог: точного метода нет — только тема функции `hair_rendering`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `aofx_bokeh_dof` | партия-10.md:121 | post_processing | technical_reference

- Партия: | aofx_bokeh_dof | AMD AOFX для боке/DoF | Vendor-specific |
- Каталог: точного метода нет — только тема функции `post_processing`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `entity_system_glacier_2` | партия-10.md:122 | rendering_architecture | technical_reference

- Партия: | entity_system_glacier_2 | entity-driven архитектура (**Dawn Engine = форк Glacier 2** — студия Eidos-Montréal лицензировала исходный код у IO Interactive после релиза Hitman: Absolution, глубоко модернизировав подсистемы рендеринга) | Дороже AI |
- Каталог: точного метода нет — только тема функции `rendering_architecture`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `ai_subsystem_dedicated` | партия-10.md:123 | advanced_npc_ai | technical_reference

- Партия: | ai_subsystem_dedicated | отдельный AI subsystem | Дороже |
- Каталог: точного метода нет — только тема функции `advanced_npc_ai`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `prague_realistic_lighting` | партия-10.md:124 | dynamic_lighting | technical_reference

- Партия: | prague_realistic_lighting | реалистичное освещение (время суток) | Дороже rendering |
- Каталог: точного метода нет — только тема функции `dynamic_lighting`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `advanced_tessellation` | партия-10.md:125 | large_scale_terrain | technical_reference

- Партия: | advanced_tessellation | тесселяция для адаптивной геометрии | Дороже |
- Каталог: точного метода нет — только тема функции `large_scale_terrain`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `amd_purehair_tressfx_3_0` | партия-10.md:126 | hair_rendering | technical_reference

- Партия: | amd_purehair_tressfx_3_0 | **интеграция технологии симуляции волос AMD PureHair (глубокая модернизация TressFX)** силами Nixxes Software под DX12 — приводила к **экстремальной нагрузке на блоки выборки текстур и расчёт прозрачности (alpha blend overdraw)** | Дороже fillrate |
- Каталог: точного метода нет — только тема функции `hair_rendering`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `realistic_combat_physics` | партия-10.md:171 | physics_simulation | technical_reference

- Партия: | realistic_combat_physics | физика боя на основе веса и скорости | Дороже physics |
- Каталог: точного метода нет — только тема функции `physics_simulation`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `clothing_wear_dirt_blood` | партия-10.md:173 | cloth_simulation | technical_reference

- Партия: | clothing_wear_dirt_blood | одежда изнашивается, пачкается, кровоточит | Дороже анимаций |
- Каталог: точного метода нет — только тема функции `cloth_simulation`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `npc_daily_routine_full` | партия-10.md:180 | advanced_npc_ai | technical_reference

- Партия: | npc_daily_routine_full | у NPC есть полное расписание дня | Дороже AI |
- Каталог: точного метода нет — только тема функции `advanced_npc_ai`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `npc_responses_player_actions` | партия-10.md:181 | advanced_npc_ai | technical_reference

- Партия: | npc_responses_player_actions | NPC реагируют на действия игрока | Дороже AI |
- Каталог: точного метода нет — только тема функции `advanced_npc_ai`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `horse_ai_independent` | партия-10.md:185 | advanced_npc_ai | technical_reference

- Партия: | horse_ai_independent | лошади с собственным AI | Дороже physics |
- Каталог: точного метода нет — только тема функции `advanced_npc_ai`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `real_archery_bow_physics` | партия-10.md:188 | physics_simulation | technical_reference

- Партия: | real_archery_bow_physics | реалистичная физика стрел | Дороже physics |
- Каталог: точного метода нет — только тема функции `physics_simulation`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `historical_real_materials` | партия-10.md:189 | rendering_architecture | technical_reference

- Партия: | historical_real_materials | реальные материалы 15-го века (брони, одежда) | Дороже контента |
- Каталог: точного метода нет — только тема функции `rendering_architecture`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `save_only_at_beds_or_saves` | партия-10.md:194 | save_system | technical_reference

- Партия: | save_only_at_beds_or_saves | сохранение только в кроватях или save (controversial) | Дороже UI |
- Каталог: точного метода нет — только тема функции `save_system`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `night_cycle_full` | партия-10.md:200 | volumetric_effects | technical_reference

- Партия: | night_cycle_full | полный цикл день/ночь (1:3) | Дороже AI |
- Каталог: точного метода нет — только тема функции `volumetric_effects`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `modding_tools_october_2019` | партия-10.md:201 | project_architecture | technical_reference

- Партия: | modding_tools_october_2019 | официальные modding tools (4A Engine) | Удороажние |
- Каталог: точного метода нет — только тема функции `project_architecture`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `mesh_shaders_first_game` | партия-10.md:252 | rendering_architecture | technical_reference

- Партия: | mesh_shaders_first_game | первая игра с native mesh shaders | Дороже shader compilation |
- Каталог: точного метода нет — только тема функции `rendering_architecture`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `ray_traced_global_illumination` | партия-10.md:253 | ray_traced_effects | technical_reference

- Партия: | ray_traced_global_illumination | RT GI в реальном времени | Дорого (без RTX = плохая производительность) |
- Каталог: точного метода нет — только тема функции `ray_traced_effects`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `path_tracing_optional` | партия-10.md:254 | path_tracing | technical_reference

- Партия: | path_tracing_optional | path tracing для next-gen PC | Vendor-specific |
- Каталог: точного метода нет — только тема функции `path_tracing`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `dlss_3_5_ray_reconstruction` | партия-10.md:255 | ray_traced_effects | technical_reference

- Партия: | dlss_3_5_ray_reconstruction | DLSS 3.5 с Ray Reconstruction (Nvidia) | Vendor-specific |
- Каталог: точного метода нет — только тема функции `ray_traced_effects`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `meshlet_cluster_renderer` | партия-10.md:267 | rendering_architecture | technical_reference

- Партия: | meshlet_cluster_renderer | разбиение геометрии на meshlets для параллельного рендеринга | Дороже rendering |
- Каталог: точного метода нет — только тема функции `rendering_architecture`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `path_tracing_consoles_excluded` | партия-10.md:268 | path_tracing | technical_reference

- Партия: | path_tracing_consoles_excluded | path tracing только на PC (next-gen консоли слишком слабые) | Vendor-specific |
- Каталог: точного метода нет — только тема функции `path_tracing`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `gtx_10_series_poor_optimization` | партия-10.md:269 | rendering_architecture | technical_reference

- Партия: | gtx_10_series_poor_optimization | GTX 10 серия (NVIDIA Pascal) = серьёзные проблемы (без mesh shaders). **Техническая природа: архитектура Northlight перенесла отсечение невидимой геометрии в стадию меш-шейдеров; отсутствие аппаратных блоков приводило к сбросу на программный транслятор драйвера, обрушивая производительность до 8–12 fps** вне зависимости от разрешения. Аналогичная ситуация с **AMD Polaris (Radeon RX 400/500)** | Vendor-specific |
- Каталог: точного метода нет — только тема функции `rendering_architecture`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `gtx_10_optimization_patch_2024` | партия-10.md:270 | rendering_architecture | technical_reference

- Партия: | gtx_10_optimization_patch_2024 | патч марта 2024 улучшил GTX 10 (оптимизированный резервный путь рендеринга) | Vendor-specific |
- Каталог: точного метода нет — только тема функции `rendering_architecture`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `no_hud_physicalized` | партия-10.md:273 | project_architecture | technical_reference

- Партия: | no_hud_physicalized | часы, маски, фонарики вместо HUD | Дороже production |
- Каталог: точного метода нет — только тема функции `project_architecture`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `ps5_xsx_4k_native` | партия-10.md:275 | render_scalability | technical_reference

- Партия: | ps5_xsx_4k_native | нативно 4K на PS5 и XSX | Vendor-specific |
- Каталог: точного метода нет — только тема функции `render_scalability`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `redengine4_streaming_nightcity` | партия-11.md:23 | open_world_streaming | technical_reference

- Партия: | redengine4_streaming_nightcity | потоковый Night City без швов, district-чанки + вертикальные слои | CPU-bound на HDD |
- Каталог: точного метода нет — только тема функции `open_world_streaming`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `crowd_traffic_density_system` | партия-11.md:24 | crowd_simulation | technical_reference

- Партия: | crowd_traffic_density_system | сотни NPC + трафик с LOD поведения | Главный потребитель CPU |
- Каталог: точного метода нет — только тема функции `crowd_simulation`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `rt_overdrive_path_tracing` | партия-11.md:25 | path_tracing | technical_reference

- Партия: | rt_overdrive_path_tracing | RT Overdrive (патч 2023): полный path tracing вместо гибридного RT | Только RTX 40xx + DLSS 3 FG для 60 fps |
- Каталог: точного метода нет — только тема функции `path_tracing`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `dlss3_fg_ray_reconstruction` | партия-11.md:26 | ray_traced_effects | technical_reference

- Партия: | dlss3_fg_ray_reconstruction | DLSS 3.5 Ray Reconstruction + Frame Generation | Vendor lock-in NVIDIA |
- Каталог: точного метода нет — только тема функции `ray_traced_effects`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `smt_ryzen_fix_2_0` | партия-11.md:27 | rendering_architecture | technical_reference

- Партия: | smt_ryzen_fix_2_0 | патч 2.0: нативная поддержка SMT на Ryzen (раньше требовался мод) | Перебалансировка тредов |
- Каталог: точного метода нет — только тема функции `rendering_architecture`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `hybrid_cpu_p_governor_2_11` | партия-11.md:28 | rendering_architecture | technical_reference

- Партия: | hybrid_cpu_p_governor_2_11 | патч 2.11 (01.2024): Hybrid CPU Utilization — Auto / Prioritize P-Cores для Intel 12/13/14 gen (Gameplay → Performance) + фикс RX Vega; в 2.11 на i9-13900K+RTX 4080 Super — микростаттеры (Tom's Hardware), пофикшены в 2.12 | Ручной оверрайд планировщика Windows |
- Каталог: точного метода нет — только тема функции `rendering_architecture`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `police_system_rework_2_0` | партия-11.md:29 | advanced_npc_ai | technical_reference

- Партия: | police_system_rework_2_0 | переписанная полиция + погони (Phantom Liberty) | Дороже AI |
- Каталог: точного метода нет — только тема функции `advanced_npc_ai`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `vehicle_combat_rework` | партия-11.md:30 | vehicle_simulation | technical_reference

- Партия: | vehicle_combat_rework | стрельба из машин, quickhack в движении | Доп. анимации |
- Каталог: точного метода нет — только тема функции `vehicle_simulation`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `hdd_to_ssd_mandatory` | партия-11.md:31 | open_world_streaming | technical_reference

- Партия: | hdd_to_ssd_mandatory | после 2.0 HDD официально не поддерживается — только SSD | Отсечение слабого железа |
- Каталог: точного метода нет — только тема функции `open_world_streaming`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `ow_engine_2_rebuild` | партия-11.md:78 | project_architecture | technical_reference

- Партия: | ow_engine_2_rebuild | 4 года апгрейда движка: большие PvE-карты, новые враги, улучшенный рендер | Только для OW2, OW1 остался на старом |
- Каталог: точного метода нет — только тема функции `project_architecture`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `netcode_rebuilt_30pct_latency` | партия-11.md:79 | multiplayer_netcode | technical_reference

- Партия: | netcode_rebuilt_30pct_latency | переписанный неткод: −30% latency, меньше ability sync errors | Совместимость со старыми реплеями потеряна |
- Каталог: точного метода нет — только тема функции `multiplayer_netcode`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `format_6v6_to_5v5` | партия-11.md:80 | multiplayer_netcode | technical_reference

- Партия: | format_6v6_to_5v5 | 12→10 игроков: убран второй танк, очереди танков душили матчмейкинг | Баланс всех героев переписан |
- Каталог: точного метода нет — только тема функции `multiplayer_netcode`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `favor_the_shooter` | партия-11.md:81 | multiplayer_netcode | technical_reference

- Партия: | favor_the_shooter | преимущество стреляющему ценой смертей за углом | Вечный налог дизайна |
- Каталог: точного метода нет — только тема функции `multiplayer_netcode`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `ecs_determinism` | партия-11.md:82 | rendering_architecture | technical_reference

- Партия: | ecs_determinism | ECS + детерминированная симуляция (GDC Tim Ford) | Сложность отладки |
- Каталог: точного метода нет — только тема функции `rendering_architecture`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `tick_63hz_comp_120hz` | партия-11.md:83 | multiplayer_netcode | technical_reference

- Партия: | tick_63hz_comp_120hz | 63 Гц клиент, до 120 Гц в соревновательных | Серверный overhead |
- Каталог: точного метода нет — только тема функции `multiplayer_netcode`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `dynamic_texture_scaling` | партия-11.md:84 | rendering_architecture | technical_reference

- Партия: | dynamic_texture_scaling | автоскейл текстур под сеть и устройство (Switch/PS4) | Мыло на слабом железе |
- Каталог: точного метода нет — только тема функции `rendering_architecture`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `kernel_anticheat_in_engine` | партия-11.md:85 | project_architecture | technical_reference

- Партия: | kernel_anticheat_in_engine | kernel-level античит встроен в движок (не болт-он) | Конфликты с драйверами |
- Каталог: точного метода нет — только тема функции `project_architecture`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `java_gc_stutter_early` | партия-11.md:130 | runtime_memory | technical_reference

- Партия: | java_gc_stutter_early | ранние версии: Java GC-паузы + single-thread чанки → просадки на слабом железе | Родовая боль Java |
- Каталог: точного метода нет — только тема функции `runtime_memory`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `rewrite_chunk_render_1_8_1_15` | партия-11.md:131 | open_world_streaming | technical_reference

- Партия: | rewrite_chunk_render_1_8_1_15 | 1.8–1.15: переписывание чанк-рендера, VBO, frustum culling | Ломало моды (OptiFine) |
- Каталог: точного метода нет — только тема функции `open_world_streaming`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `sodium_lithium_modern_fix` | партия-11.md:132 | rendering_architecture | technical_reference

- Партия: | sodium_lithium_modern_fix | Sodium (рендер, 221.8M загрузок на Modrinth) + Lithium (тик) + Phosphor (<1.19): кратный рост fps на том же железе без потери картинки; 0.9.x (06.2026) — ранний Vulkan-бэкенд | Только Fabric/NeoForge/Quilt, GL 4.5+; Android/ARM через трансляторы не поддерживается |
- Каталог: точного метода нет — только тема функции `rendering_architecture`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `bedrock_renderdragon_rewrite` | партия-11.md:133 | rendering_architecture | technical_reference

- Партия: | bedrock_renderdragon_rewrite | Bedrock: RenderDragon (DX12/GL) вместо старого GL — +fps, но сломал шейдеры | Потеря кастомных шейдеров |
- Каталог: точного метода нет — только тема функции `rendering_architecture`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `java_17_21_migration` | партия-11.md:134 | project_architecture | technical_reference

- Партия: | java_17_21_migration | 1.18+ → Java 17, 1.21+ → Java 21: ZGC/Generational GC, меньше пауз | Требования к лаунчеру |
- Каталог: точного метода нет — только тема функции `project_architecture`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `simulation_distance_split` | партия-11.md:135 | advanced_npc_ai | technical_reference

- Партия: | simulation_distance_split | разделение render distance / simulation distance (тикаются только ближние чанки) | Сложность для ферм |
- Каталог: точного метода нет — только тема функции `advanced_npc_ai`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `village_pillage_raid_lag` | партия-11.md:136 | advanced_npc_ai | technical_reference

- Партия: | village_pillage_raid_lag | рейды + сотни сущностей в одном чанке → TPS-просадки даже на серверах | Вечный налог песочницы |
- Каталог: точного метода нет — только тема функции `advanced_npc_ai`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `tick_64mm_128faceit_split` | партия-11.md:182 | multiplayer_netcode | technical_reference

- Партия: | tick_64mm_128faceit_split | GO: 64 tick MM vs 128 tick FACEIT/турниры — раскол decade-спора | Недоверие к MM |
- Каталог: точного метода нет — только тема функции `multiplayer_netcode`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `lag_compensation_rewind` | партия-11.md:183 | multiplayer_netcode | technical_reference

- Партия: | lag_compensation_rewind | перемотка мира на пинг+интерп для честного хитрега | Peekers advantage неустраним |
- Каталог: точного метода нет — только тема функции `multiplayer_netcode`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `subtick_cs2_replaces_tick` | партия-11.md:184 | multiplayer_netcode | technical_reference

- Партия: | subtick_cs2_replaces_tick | CS2: sub-tick — сервер знает точный момент выстрела внутри тика (снапшоты 64 Гц) | Споры «ватности», удаление cl_interp |
- Каталог: точного метода нет — только тема функции `multiplayer_netcode`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `volumetric_smoke_dynamic` | партия-11.md:185 | particle_systems | technical_reference

- Партия: | volumetric_smoke_dynamic | Source 2 volumetric дым: пули/HE взаимодействуют, раскрывается | GPU cost |
- Каталог: точного метода нет — только тема функции `particle_systems`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `vpk_packed_assets` | партия-11.md:186 | build_delivery | technical_reference

- Партия: | vpk_packed_assets | VPK-контейнеры с предкэшем строк/шейдеров | Патчи одним VPK |
- Каталог: точного метода нет — только тема функции `build_delivery`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `panorama_ui_replace_scaleform` | партия-11.md:187 | project_architecture | technical_reference

- Партия: | panorama_ui_replace_scaleform | Panorama вместо Scaleform (2018) | Перепись HUD |
- Каталог: точного метода нет — только тема функции `project_architecture`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `rv4_single_thread_bottleneck` | партия-11.md:233 | rendering_architecture | technical_reference

- Партия: | rv4_single_thread_bottleneck | главный поток + DX11-драйверный overhead: 90–95% работы на одном потоке | GPU-апгрейд не лечит |
- Каталог: точного метода нет — только тема функции `rendering_architecture`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `view_distance_cpu_linear` | партия-11.md:234 | open_world_streaming | technical_reference

- Партия: | view_distance_cpu_linear | дальность отрисовки линейно грузит CPU (объекты + тени + AI) | Настройка Objects/Terrain/Visibility — главный рычаг |
- Каталог: точного метода нет — только тема функции `open_world_streaming`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `shadows_gpu_vs_cpu_split` | партия-11.md:235 | dynamic_shadows | technical_reference

- Партия: | shadows_gpu_vs_cpu_split | тени Standard = на GPU, Low = на CPU (инверсия!) | Контринтуитивный твик |
- Каталог: точного метода нет — только тема функции `dynamic_shadows`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `x64_1_68_memory_unbottleneck` | партия-11.md:236 | runtime_memory | technical_reference

- Партия: | x64_1_68_memory_unbottleneck | **патч 1.68 (03.2017): 64-bit executables** — снятие 2–3 ГБ лимита, кэш больших дистанций, меньше OOM | Слом драйверного переключения GPU (iGPU vs discrete) |
- Каталог: точного метода нет — только тема функции `runtime_memory`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `eden_3d_editor_1_56` | партия-11.md:237 | project_architecture | technical_reference

- Партия: | eden_3d_editor_1_56 | Eden Update 1.56 (02.2016): 3D-редактор + audio overhaul + Geometric Occluder (из DayZ) | Переучивание миссионеров |
- Каталог: точного метода нет — только тема функции `project_architecture`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `multithread_overhaul_2_20` | партия-11.md:238 | rendering_architecture | technical_reference

- Партия: | multithread_overhaul_2_20 | **патч 2.20 (06.2025, Dedmen OPREP)**: замена Fork-Join job system (со времён Arma 2) на графовый Enfusion job system + корутины для извлечения параллельных кусков AI (scan/pathfinding) из синглтред-FSM; взрывы — lineIntersects параллельно с ping-pong синглтред-обработчиков; VS2013→VS2022, C++14→C++23 (>1M строк); цель — мин. fps и лаг-спайки (макс. fps может упасть) | Скриптовые моды не ускоряются; симуляция объектов не тронута (риск крашей с модами) |
- Каталог: точного метода нет — только тема функции `rendering_architecture`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `ai_lag_spike_dominant` | партия-11.md:239 | advanced_npc_ai | technical_reference

- Партия: | ai_lag_spike_dominant | самые большие лаг-спайки — в AI-расчётах (группы, pathfinding), не в рендере | Script-heavy моды упираются |
- Каталог: точного метода нет — только тема функции `advanced_npc_ai`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `dedicated_server_linux` | партия-11.md:240 | multiplayer_netcode | technical_reference

- Партия: | dedicated_server_linux | headless dedicated Win/Linux + Eden + Workshop | Серверный AI ест fps миссии |
- Каталог: точного метода нет — только тема функции `multiplayer_netcode`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.

## `32bit_deprecation_2_20` | партия-11.md:241 | runtime_memory | technical_reference

- Партия: | 32bit_deprecation_2_20 | 2.20 — последний релиз с 32-bit (frozen legacy branch, без MP-совместимости); дроп Win7/8 | Отсечение легаси |
- Каталог: точного метода нет — только тема функции `runtime_memory`. Плюсы/минусы = `Цена` из партии + инженерный вывод, числом не подтверждены. Нужен замер на прототипе.
