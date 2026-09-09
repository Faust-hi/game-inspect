# Технические решения из партий — подходят под условия

Условия: влияние на архитектуру, вычислительную нагрузку или потребление ресурсов.
Исключены: монетизация, дата выхода, сюжетные развилки, количество концовок.
Сохранены: разрушаемость, масштаб мира, NPC, мультиплеер, физика, навигация, стриминг.

Всего подходят: 492 из 980. Ниже — конкретно по функциям: код | где | что делает | цена.

## advanced_npc_ai — 51

- `ai_four_layer_hierarchy` | партия-01.md:239 | | ai_four_layer_hierarchy | tactical/operational/strategic/grand-strategic AI | 4 параллельных AI-цикла = нагрузка на CPU |
- `ai_flavor_personality_matrix` | партия-01.md:240 | | ai_flavor_personality_matrix | 26 «flavor»-параметров (1–10) на каждого лидера | Признано: AI рандомен между стратегиями |
- `leveled_reactive_ai_director_lite` | партия-01.md:298 | | leveled_reactive_ai_director_lite | ремастеринг на Director-систему из будущей L4D | Упрощённая версия по сравнению с L4D |
- `radiant_ai_schedule_graph` | партия-01.md:399 | | radiant_ai_schedule_graph | NPC принимают решения (еда/сон/разговоры) на основе расписания и соседей | Сложность балансировки; позже упрощено в Skyrim |
- `full_voice_acting_npc` | партия-01.md:400 | | full_voice_acting_npc | первая TES с полной озвучкой всех NPC | Жёсткое ограничение числа диалогов |
- `garry_point_stealth_anchor` | партия-01.md:453 | | garry_point_stealth_anchor | точки для подвешивания Бэтмена, динамический ИИ врагов с уровнем страха | Ограниченная свобода перемещения |
- `duty_support_npc_party` | партия-01.md:514 | | duty_support_npc_party | AI-партия для соло-прохождения данжей | Ограниченный AI по сравнению с игроком-человеком |
- `dispatchable_strider_combat` | партия-02.md:33 | | dispatchable_strider_combat | масштабные враги как конечные боссы уровней (Strider в City17) | Нагрузка на ИИ |
- `provokable_ai` | партия-02.md:34 | | provokable_ai (antlion, barnacle) | NPC реагируют на дистанцию/звук/свет, не на скрипты | Сложнее отладки |
- `alyx_ai_companion` | партия-02.md:90 | | alyx_ai_companion | Alyx как комбатант с "personality code" — не повторяет фразы, реагирует на действия игрока | Требует тщательной настройки |
- `enemy_tactics_ai_upgrade` | партия-02.md:92 | | enemy_tactics_ai_upgrade | Combine солдаты теперь приседают, чтобы уклониться от огня | Дороже на CPU |
- `script_driven_companion_cover` | партия-02.md:98 | | script_driven_companion_cover | Alyx занимает укрытия и прикрывает игрока | AI overhead |
- `ai_director` | партия-02.md:241 | | ai_director | динамическая балансировка врагов и предметов на основе навыка игроков | Сложная калибровка |
- `music_director_client_side` | партия-02.md:243 | | music_director_client_side | multi-track система на каждом клиенте; spectator слышит микс teammate | Удорожание памяти |
- `infected_path_follower_ai` | партия-02.md:252 | | infected_path_follower_ai | алгоритм path-follower с оценкой геометрии — краучится/прыгает/лезет | CPU heavy |
- `ai_director_2_0` | партия-02.md:306 | | ai_director_2_0 | переписанный Director — изменение layout уровня, погодных условий, размещения стен в runtime | Сложнее QA |
- `director_encourages_longer_paths` | партия-02.md:307 | | director_encourages_longer_paths | вознаграждение за трудные маршруты через спец-амуницию и tier-2 оружие | Больше инвентаря для управления |
- `hex_grid_ai_navigation` | партия-03.md:92 | | hex_grid_ai_navigation | логика навигации AI на гексах (по аналогии с Civ) | Сложнее debug |
- `spirit_summon_ash` | партия-03.md:242 | | spirit_summon_ash | призыв NPC-духов как companions (аналог Half-life) | AI overhead, баланс summon-урона |
- `eagle_senu_companion` | партия-04.md:83 | | eagle_senu_companion | орёл Сену вместо Eagle Vision — отдельный AI | Удвоенный render для sky+terrain |
- `dynamic_schedule_npcs` | партия-04.md:88 | | dynamic_schedule_npcs | NPC имеют ежедневный распорядок (работа → сон) | AI overhead, но оправдано |
- `mercenary_nemesis_system` | партия-04.md:144 | | mercenary_nemesis_system | наёмники выслеживают игрока за преступления (а-ля Shadow of Mordor) | AI overhead |
- `eagle_ikaros_companion` | партия-04.md:150 | | eagle_ikaros_companion | Орел Икарос как scout (аналог Senu) | Доп. AI |
- `settlement_building_management` | партия-04.md:201 | | settlement_building_management | Ravensthorpe — главная база, разблокируемые здания | Доп. AI/simulation |
- `jomsviking_shared_npc` | партия-04.md:207 | | jomsviking_shared_npc | созданный викинг отправляется в чужие игры | Серверная инфраструктура |
- `radiant_ai_updated` | партия-05.md:24 | | radiant_ai_updated | NPC "делают что хотят под дополнительными параметрами" (Howard) | AI overhead |
- `procedural_side_quests` | партия-05.md:33 | | procedural_side_quests | уникальные квесты через NPC-schedule | Контент |
- `dragon_encounter_random` | партия-05.md:34 | | dragon_encounter_random | драконы появляются случайно в мире | CPU overhead |
- `settlement_building_anywhere` | партия-05.md:106 | | settlement_building_anywhere | C.A.M.P. в F76 / 30+ settlements в F4 | Дополнительный simulation overhead |
- `no_human_npcs_initially` | партия-05.md:170 | | no_human_npcs_initially | все NPC — игроки или боты; текстовые holotapes вместо диалогов | Потеря immersion |
- `later_npc_humans_wastelanders` | партия-05.md:181 | | later_npc_humans_wastelanders | обновление 2020: полноценные NPC, диалоги, квесты | Спасли игру |
- `procedurally_generated_loadouts` | партия-05.md:258 | | procedurally_generated_loadouts | randomised NPC loadouts | Repetition risk |
- `camp_moving_hq` | партия-06.md:153 | | camp_moving_hq | передвижной лагерь как живой hub | Доп. AI/NPC simulation |
- `ecology_realistic` | партия-06.md:163 | | ecology_realistic | животные взаимодействуют (привлечение хищников, стаи) | Доп. AI |
- `stranger_random_encounters` | партия-06.md:174 | | stranger_random_encounters | случайные события с NPC | Доп. контент |
- `ai_chess_piece_targeting` | партия-07.md:98 | | ai_chess_piece_targeting | враги как шахматные фигуры — нужен правильный порядок | Дороже AI |
- `ai_chess_advisor` | партия-07.md:108 | | ai_chess_advisor | приоритезация через AI Advisor | Доп. AI state |
- `binoculars_with_electronic_tagging` | партия-08.md:27 | | binoculars_with_electronic_tagging | бинокль с маркировкой NPC | Удороажние shader |
- `ambient_zombie_spawn` | партия-08.md:245 | | ambient_zombie_spawn | ambient zombie spawn для напряжения | Дороже AI |
- `human_npc_karma_system` | партия-10.md:31 | | human_npc_karma_system | моральные выборы влияют на концовку | Дороже контента |
- `day_night_affects_npc_behavior` | партия-10.md:33 | | day_night_affects_npc_behavior | враги в лагере днём бодрствуют, ночью спят | Дороже AI |
- `social_engagement_detector_aug` | партия-10.md:111 | | social_engagement_detector_aug | Social Aug — анализ мимики NPC | Дороже AI |
- `npc_dynamic_ai` | партия-10.md:112 | | npc_dynamic_ai | NPC меняют поведение по ситуации (днём/ночью) | Дороже AI |
- `ai_subsystem_dedicated` | партия-10.md:123 | | ai_subsystem_dedicated | отдельный AI subsystem | Дороже |
- `npc_daily_routine_full` | партия-10.md:180 | | npc_daily_routine_full | у NPC есть полное расписание дня | Дороже AI |
- `npc_responses_player_actions` | партия-10.md:181 | | npc_responses_player_actions | NPC реагируют на действия игрока | Дороже AI |
- `horse_ai_independent` | партия-10.md:185 | | horse_ai_independent | лошади с собственным AI | Дороже physics |
- `police_system_rework_2_0` | партия-11.md:29 | | police_system_rework_2_0 | переписанная полиция + погони (Phantom Liberty) | Дороже AI |
- `simulation_distance_split` | партия-11.md:135 | | simulation_distance_split | разделение render distance / simulation distance (тикаются только ближние чанки) | Сложность для ферм |
- `village_pillage_raid_lag` | партия-11.md:136 | | village_pillage_raid_lag | рейды + сотни сущностей в одном чанке → TPS-просадки даже на серверах | Вечный налог песочницы |
- `ai_lag_spike_dominant` | партия-11.md:239 | | ai_lag_spike_dominant | самые большие лаг-спайки — в AI-расчётах (группы, pathfinding), не в рендере | Script-heavy моды упираются |

## ai_pathfinding — 6

- `find_in_sphere_hot_path_avoid` | партия-01.md:137 | | find_in_sphere_hot_path_avoid | FindInSphere нельзя вызывать в горячем пути | Дисциплина программирования аддонов |
- `hex_grid_pathfinding` | партия-01.md:235 | | hex_grid_pathfinding | гексагональная сетка мира вместо квадратной | Переделка всех AI-решений, карт и интерфейса |
- `time_sliced_pathfinding` | партия-01.md:242 | | time_sliced_pathfinding | pathfinding по тайлам, разнесённый по тикам | Юниты в дальних гексах могут «лагать» |
- `navmesh_ai_pathfinding` | партия-02.md:31 | | navmesh_ai_pathfinding | навигационная сетка вместо вейпоинтов | Сложно строить для процедурных уровней |
- `common_infected_navigation_constraint` | партия-02.md:255 | | common_infected_navigation_constraint | дизайнерское правило: "no place survivor stands that zombie cannot reach" | Ограничивает левел-дизайн |
- `havok_animation_pathfinding` | партия-05.md:39 | | havok_animation_pathfinding | стандарт в индустрии | Лицензия |

## art_pipeline — 1

- `100000_photos_new_york` | партия-06.md:32 | | 100000_photos_new_york | 100K фото Нью-Йорка для исследований | Production cost |

## audio_system — 13

- `audio_propagation_through_portals` | партия-01.md:30 | | audio_propagation_through_portals | звук трассируется через оба портала с собственной аудио-геометрией | Нагрузка на CPU растёт линейно с числом открытых порталов |
- `audio_convolution_reverb` | партия-01.md:83 | | audio_convolution_reverb | convolution reverb на основе импульсных характеристик комнат | Высокое потребление CPU в больших зонах |
- `audio_occlusion_reverb` | партия-01.md:187 | | audio_occlusion_reverb | собственная система окклюзии, унаследованная из CoD2 | Однопоточный sound-движок: перестрелки упираются в 1 ядро |
- `voice_acting_native_languages` | партия-01.md:245 | | voice_acting_native_languages | лидеры говорят на родных языках (Latin, Nahuatl) | Удорожание локализации |
- `audio_occlusion_multilevel` | партия-01.md:293 | | audio_occlusion_multilevel | многоуровневая окклюзия (различает толстые и тонкие стены) | Расход CPU на sound |
- `audio_flux_field_recording` | партия-01.md:294 | | audio_flux_field_recording | Flux: полевая запись эха оружия на полигоне для точной локализации звука | Зависит от точных импульсов |
- `full_voice_acting_3_party` | партия-02.md:38 | | full_voice_acting_3_party | актёры озвучки (Louis Gossett Jr., Robert Guillaume, Robert Culp) | Большой размер файлов локализации |
- `fully_voiced_protagonist_first_time` | партия-05.md:108 | | fully_voiced_protagonist_first_time | 111,000 строк диалогов | Огромный voice acting |
- `custom_music_station_pc` | партия-06.md:36 | | custom_music_station_pc | импорт своей музыки на радио | Удобство |
- `dynamic_music_radio` | партия-06.md:91 | | dynamic_music_radio | 241+ лицензированных треков в 15 станциях + DJ Green Lantern | Огромный лицензионный cost |
- `dynamic_music_aggression` | партия-08.md:188 | | dynamic_music_aggression | музыка реагирует на стиль игры | Удороажние audio |
- `voice_overs_native_language` | партия-09.md:110 | | voice_overs_native_language | озвучка War Stories на родном языке (англ., франц., итал., арабск.) | Дороже |
- `rain_masks_footsteps` | партия-10.md:34 | | rain_masks_footsteps | дождь маскирует шаги (для стелса) | Удороажние audio |

## baked_lighting — 3

- `lightmap_atlas_baking` | партия-01.md:85 | | lightmap_atlas_baking | единый lightmap-атлас для всех комнат | Удвоенный размер при paintmap |
- `precomputed_static_lighting_vrad` | партия-01.md:349 | | precomputed_static_lighting_vrad | радиосити + lightmaps для интерьеров | Долгая компиляция световых карт |
- `normal_map_baked_ambient` | партия-07.md:178 | | normal_map_baked_ambient | baked normal maps + ambient occlusion | Удороажние |

## build_delivery — 4

- `differential_patch_pipeline` | партия-01.md:508 | | differential_patch_pipeline | маленькие патчи через разницу в данных | Сложнее rollback при ошибках |
- `steam_preload_distribution` | партия-02.md:39 | | steam_preload_distribution | предзагрузка зашифрованных файлов до релиза, разблокировка в дату выхода | Требование Steam-аккаунта с самого начала |
- `directstorage_support` | партия-05.md:255 | | directstorage_support | Xbox Series X поддерживает DirectStorage | Быстрая загрузка |
- `vpk_packed_assets` | партия-11.md:186 | | vpk_packed_assets | VPK-контейнеры с предкэшем строк/шейдеров | Патчи одним VPK |

## character_animation — 16

- `animation_lod_budget` | партия-01.md:189 | | animation_lod_budget | скелетная анимация с упрощением на дистанции | Видимые «pops» при переключении LOD |
- `animation_lod_budget` | партия-01.md:347 | | animation_lod_budget | упрощение анимации на дистанции | Видимые артефакты при переключении |
- `hl2_faceposer_facs` | партия-02.md:29 | | hl2_faceposer_facs | FACS по Ekman — 40 Action Units, процедурная интерполяция через Channel-weights | Нет универсального фотореализма; видны "маски" |
- `procedural_facial_animation_via_chris` | партия-02.md:30 | | procedural_facial_animation_via_chris | автоматическая генерация выражений из текста (ранее Phoneme) | Требует тюнинга |
- `procedural_facial_animation_v2` | партия-02.md:95 | | procedural_facial_animation_v2 | обновлённая FACS с динамической интерполяцией | Сложная отладка |
- `improved_alyx_animations` | партия-02.md:141 | | improved_alyx_animations | Alyx ранена — сложная анимация на земле с лечением | Больше ключевых кадров |
- `leaning_curved_paths` | партия-02.md:246 | | leaning_curved_paths | анимация персонажей наклоняется на поворотах | Удорожание скелетной анимации |
- `mocap_death_animations` | партия-02.md:253 | | mocap_death_animations | 100 motion-captured death-анимаций проф. каскадёра + ragdoll blend | Production cost |
- `engwe_sensua_animations` | партия-04.md:87 | | engwe_sensua_animations | новая система анимации от Ubisoft (Sensua) | Удвоенный объём анимаций |
- `external_animations_5000` | партия-04.md:277 | | external_animations_5000 | кастомные анимации для каждого Hero | Дороже content creation |
- `havok_behavior_toolset` | партия-05.md:26 | | havok_behavior_toolset | плавный переход walk→run→sprint | Лицензия Havok |
- `dialogue_facial_animation_FACS` | партия-05.md:36 | | dialogue_facial_animation_FACS | улучшенные lip-sync | Лицензия |
- `id_tech_5_animation_mega_file` | партия-07.md:158 | | id_tech_5_animation_mega_file | анимации в мега-файле (модель персонажа в одном файле) | Удороажние pipeline |
- `performance_capture_prophet` | партия-08.md:176 | | performance_capture_prophet | performance capture (впервые для серии) | Дороже |
- `4d_dissolve_transitions` | партия-09.md:41 | | 4d_dissolve_transitions | 4D dissolve для анимаций (seamless transitions) | Удороажние |
- `animation_procedural_motion` | партия-09.md:174 | | animation_procedural_motion | процедурные анимации движения | Дороже |

## cloth_simulation — 3

- `cape_animation_700_states` | партия-01.md:458 | | cape_animation_700_states | 700+ анимаций плаща с физикой | Каждый кадр пересчитывается; дорого для CPU |
- `physics_based_hair_clothing` | партия-02.md:245 | | physics_based_hair_clothing | улучшенная анимация волос/тканей для реалистичности | Доп. cost |
- `clothing_wear_dirt_blood` | партия-10.md:173 | | clothing_wear_dirt_blood | одежда изнашивается, пачкается, кровоточит | Дороже анимаций |

## crowd_simulation — 5

- `crowd_30000_npc` | партия-04.md:24 | | crowd_30000_npc | до 30,000 NPC в одной сцене с индивидуальным AI | Рекордная нагрузка на CPU |
- `crowd_activities_interaction` | партия-04.md:28 | | crowd_activities_interaction | NPC органично предлагают действия | AI overhead |
- `npc_settlement_simulation` | партия-05.md:109 | | npc_settlement_simulation | жители симулируют потребности (еда, вода, кровати) | AI overhead |
- `dense_ecosystem_wildlife` | партия-06.md:88 | | dense_ecosystem_wildlife | охота, животные в мире | Доп. AI overhead |
- `crowd_traffic_density_system` | партия-11.md:24 | | crowd_traffic_density_system | сотни NPC + трафик с LOD поведения | Главный потребитель CPU |

## destruction_simulation — 17

- `dismemberment_physics` | партия-01.md:292 | | dismemberment_physics | отрывание конечностей, сгорание кожи | Увеличение числа мелких физ-объектов |
- `extended_destruction` | партия-01.md:295 | | extended_destruction | разрушаемые стены, песчаные баррикады | Больше динамических мешей в сцене |
- `dynamic_city17_destruction` | партия-02.md:96 | | dynamic_city17_destruction | город изменился после HL2 — разрушенные здания, инопланетная Xen-фауна | Долгая сборка уровней |
- `dynamic_dismemberment` | партия-05.md:115 | | dynamic_dismemberment | динамическое разрушение тел | GPU cost |
- `destructible_demon_systems` | партия-07.md:89 | | destructible_demon_systems | враги разрушаются постепенно с обнажением слабых мест | Дороже анимаций |
- `destructible_demon_armor_strip` | партия-07.md:96 | | destructible_demon_armor_strip | снятие брони открывает уязвимости | Дороже AI state machine |
- `destructible_demon_critical_state` | партия-07.md:97 | | destructible_demon_critical_state | критические части тела | Дороже hit-detection |
- `destructible_demo_macro_destructible` | партия-07.md:104 | | destructible_demo_macro_destructible | macro-разрушение (разрывание врагов) | Дороже шейдеров |
- `destructible_decrement_demon_health` | партия-07.md:106 | | destructible_decrement_demon_health | Destructible Demon уменьшает health постепенно | Дороже AI |
- `destruction_box_car_smg` | партия-07.md:170 | | destruction_box_car_smg | деструкция ящиков/машин | Дороже physics |
- `lego_manhattan_destructible` | партия-08.md:111 | | lego_manhattan_destructible | разрушаемость Manhattan | Удороажние physics |
- `levolution_dynamic_destruction` | партия-09.md:24 | | levolution_dynamic_destruction | уровни меняются от действий игроков (разрушение зданий) | Дороже physics |
- `destruction_2` | партия-09.md:34 | | destruction_2.0_levolution | 2.0 версия разрушений (ранее в Frostbite 2 Bad Company 2) | Дороже physics |
- `cloud_destruction_debris` | партия-09.md:46 | | cloud_destruction_debris | облачные системы разрушения | Дороже |
- `ww1_destruction_expanded` | партия-09.md:95 | | ww1_destruction_expanded | расширенная WWI-разрушаемость (траншеи, укрепления) | Дороже physics |
- `fortification_system` | партия-09.md:167 | | fortification_system | укрепления с аммо, минами | Дороже контента |
- `wave_destruction_advanced` | партия-09.md:182 | | wave_destruction_advanced | расширенная разрушаемость зданий | Дороже physics |

## dynamic_global_illumination — 2

- `gpu_driven_lighting_cache` | партия-01.md:510 | | gpu_driven_lighting_cache | запечённое освещение с динамическими слоями | Долгая компиляция световых карт |
- `voxel_gi_approximation` | партия-09.md:181 | | voxel_gi_approximation | voxel-based GI approximation | Удороажние |

## dynamic_lighting — 11

- `dynamic_lighting_plus_dof` | партия-01.md:188 | | dynamic_lighting_plus_dof | depth of field, динамические тени в реальном времени | Нагрузка на GPU растёт с числом источников света |
- `hdr_lighting_lost_coast_demo` | партия-02.md:35 | | hdr_lighting_lost_coast_demo | HDR в Lost Coast (2005); stencil-histogram для совместимости с ps_2_b и MSAA | Banding артефакты |
- `hdr_lighting_story_moments` | партия-02.md:93 | | hdr_lighting_story_moments | HDR используется эпизодически для сюжетных моментов | Banding, требует stencil histogram (8-bit) |
- `hdr_lighting_2005_update` | партия-02.md:192 | | hdr_lighting_2005_update | HDR введён в декабре 2005, постепенно на картах | Stencil histogram стоимость |
- `dynamic_lighting_per_area` | партия-03.md:247 | | dynamic_lighting_per_area | каждая зона имеет уникальную цветовую палитру и lighting (Caelid красный, Liurnia голубой) | Удвоение art-pipeline |
- `lighting_environment_improvements` | партия-06.md:229 | | lighting_environment_improvements | современные эффекты освещения | Дороже |
- `hdr_pbr_lighting` | партия-07.md:30 | | hdr_pbr_lighting | HDR + PBR | Требования к GPU |
- `procedural_lighting_ambient_occlusion` | партия-07.md:161 | | procedural_lighting_ambient_occlusion | screen-space ambient occlusion | Удороажние |
- `deferred_shading_lighting` | партия-08.md:39 | | deferred_shading_lighting | deferred shading (DX10/11) | Удороажние |
- `per_voxel_lighting_hbao_etc` | партия-08.md:180 | | per_voxel_lighting_hbao_etc | per-voxel освещение (HBAO+) | Удороажние cost |
- `prague_realistic_lighting` | партия-10.md:124 | | prague_realistic_lighting | реалистичное освещение (время суток) | Дороже rendering |

## dynamic_shadows — 4

- `self_shadowing_normal_map` | партия-02.md:247 | | self_shadowing_normal_map | новые карты теней для освещения | VRAM |
- `advanced_shadow_rendering` | партия-02.md:248 | | advanced_shadow_rendering | для художественной атмосферы | GPU cost |
- `soft_shadows_pcss` | партия-08.md:30 | | soft_shadows_pcss | PCSS (Percentage Closer Soft Shadows) | Удороажние shader |
- `shadows_gpu_vs_cpu_split` | партия-11.md:235 | | shadows_gpu_vs_cpu_split | тени Standard = на GPU, Low = на CPU (инверсия!) | Контринтуитивный твик |

## geometry_pipeline — 2

- `infected_variation_24000` | партия-02.md:254 | | infected_variation_24000 | одна модель с 24 000 вариаций (текстуры/геометрия) | Память снижена на 50% |
- `layered_armor_system` | партия-05.md:102 | | layered_armor_system | слои брони вместо цельного меша | Память |

## hair_rendering — 5

- `scanner_crosshair_customization` | партия-02.md:317 | | scanner_crosshair_customization | поддержка Workshop для spray/crosshair (после 2014) | UGC |
- `hair_works_fur` | партия-04.md:32 | | hair_works_fur | GameWorks hair/fur (после исправлений) | Изначально баг — удалили |
- `hair_growth_realistic` | партия-06.md:161 | | hair_growth_realistic | волосы растут со временем | Удороажние |
- `tressfx_hair_amd` | партия-10.md:120 | | tressfx_hair_amd | TressFX для волос (сотрудничество с AMD) | Vendor-specific |
- `amd_purehair_tressfx_3_0` | партия-10.md:126 | | amd_purehair_tressfx_3_0 | **интеграция технологии симуляции волос AMD PureHair (глубокая модернизация TressFX)** силами Nixxes Software под DX12 — приводила к **экстремальной нагрузке на блоки выборки текстур и расчёт прозрачности (alpha blend overdraw)** | Дороже fillrate |

## large_scale_terrain — 13

- `hardware_tessellation_terrain` | партия-01.md:236 | | hardware_tessellation_terrain | DX11 tessellation для ландшафта | Требует DX11 GPU |
- `megatexture_virtual_texturing` | партия-07.md:154 | | megatexture_virtual_texturing | id Tech 5 — огромные виртуальные текстуры через стриминг | 1 ТБ uncompressed build (по словам Carmack) |
- `parallax_occlusion_mapping` | партия-08.md:33 | | parallax_occlusion_mapping | parallax occlusion mapping для рельефа | Удороажние |
- `megatextures_like_id_tech5` | партия-08.md:34 | | megatextures_like_id_tech5 | virtual texturing аналог id Tech 5 (CryEngine V) | Дорого на старте |
- `tesselation_hardware_direct3d11` | партия-08.md:35 | | tesselation_hardware_direct3d11 | hardware tessellation (DX11) | Дороже shader |
- `hardware_tessellation_pc` | партия-08.md:38 | | hardware_tessellation_pc | hardware tessellation (DX11) | Удороажние shader |
- `tessellation_dx11_pc` | партия-08.md:106 | | tessellation_dx11_pc | DX11 с tessellation (PC патч 1.9) | Vendor lock-in (Nvidia bias) |
- `tesselation_abuse_criticism` | партия-08.md:122 | | tesselation_abuse_criticism | избыточная тесселяция (исключительно Nvidia) | Критика |
- `tessellation_overhaul` | партия-09.md:32 | | tessellation_overhaul | тесселяция в Frostbite 3 переделана | Удороажние shader |
- `parallax_occlusion_mapping_frostbite` | партия-09.md:37 | | parallax_occlusion_mapping_frostbite | POM в Frostbite | Удороажние shader |
- `tesselated_displacement_maps` | партия-09.md:39 | | tesselated_displacement_maps | displacement mapping с тесселяцией | Дороже |
- `surface_tessellation_displacement` | партия-09.md:43 | | surface_tessellation_displacement | surface displacement через тесселяцию | Дороже |
- `advanced_tessellation` | партия-10.md:125 | | advanced_tessellation | тесселяция для адаптивной геометрии | Дороже |

## multiplayer_netcode — 70

- `headless_dedicated_server` | партия-01.md:135 | | headless_dedicated_server | выделенный сервер без рендера | Требует отдельного бинарника |
- `tick_hook_timer_replacement` | партия-01.md:136 | | tick_hook_timer_replacement | замена тяжёлых tick-хуков на таймеры | Не все события можно вынести из тика |
- `multiplayer_progression_unlock` | партия-01.md:190 | | multiplayer_progression_unlock | XP-система, prestige, create-a-class — серверная логика | Сервер хранит состояние всех игроков |
- `killstreak_server_logic` | партия-01.md:191 | | killstreak_server_logic | ачивки на N фрагов без смерти (3/5/7) | Серверная логика раз в кадр |
- `cooperative_zombies_spawning` | партия-01.md:297 | | cooperative_zombies_spawning | объединённый spawner для волн зомби + entity pooling | Лимит числа зомби на сцене |
- `server_authoritative_state` | партия-01.md:506 | | server_authoritative_state | сервер — единственный источник истины для всех транзакций | Задержки на клиенте при плохом пинге |
- `headless_dedicated_server` | партия-01.md:507 | | headless_dedicated_server | выделенные серверы по data-центрам (NA/EU/JP/Oceania) | Высокая стоимость инфраструктуры |
- `cross_platform_play` | партия-01.md:511 | | cross_platform_play | единый серверный код для Win/Mac/PS/PS5/Xbox | Различия в DirectX vs OpenGL/Vulkan |
- `instance_partitioning` | партия-01.md:513 | | instance_partitioning | каждый инстанс (данж, рейд) изолирован | Сетевая нагрузка при большом числе групп |
- `active_time_event_fate` | партия-01.md:516 | | active_time_event_fate | FATE — открытые групповые события в overworld | Серверная синхронизация с производительностью клиента |
- `advanced_vehicle_chase` | партия-02.md:138 | | advanced_vehicle_chase | длинные погонные секции на багги с физикой | Сложная синхронизация |
- `max_64_players` | партия-02.md:193 | | max_64_players | удвоение игроков с 32 (CS 1.6) до 64 | Серверная нагрузка |
- `up_to_4_player_coop` | партия-02.md:257 | | up_to_4_player_coop | до 4 игроков + AI bot замена | Server load |
- `versus_8_player` | партия-02.md:258 | | versus_8_player | 4 survivors + 4 infected | Конкурентный баланс |
- `scavenge_mode_4v4` | партия-02.md:318 | | scavenge_mode_4v4 | генератор требует топлива, команды 4-на-4 | PvP-баланс |
- `mac_cross_play_2010` | партия-02.md:321 | | mac_cross_play_2010 | Mac + Windows кросс-платформа | Тех. сложность |
- `glicko_rating_competitive` | партия-02.md:376 | | glicko_rating_competitive | Glicko-2 рейтинг для матчмейкинга | Тонкая калибровка |
- `prime_matchmaking_2016` | партия-02.md:378 | | prime_matchmaking_2016 | верификация по телефону для изоляции от смурфов и читеров | Требование к пользователю |
- `sub_tick_input_cs2` | партия-02.md:383 | | sub_tick_input_cs2 | сервер знает точный момент выстрела/прыжка между тиками — latency -3.4мс | Психологическая адаптация игроков |
- `humanity_online_state` | партия-03.md:28 | | humanity_online_state | форма human/hollow определяет доступ к co-op и invasion | Доп. состояние для синхронизации |
- `bloodstain_player_messages` | партия-03.md:30 | | bloodstain_player_messages | оставлять сообщения "try jumping", показывать как умерли другие игроки | Серверная логика; abuse-модерация |
- `invasion_asymmetric_multiplayer` | партия-03.md:31 | | invasion_asymmetric_multiplayer | PvP-инвазия в SP через matchmaking | Несбалансированный опыт у вторгнутого |
- `six_player_multiplayer_sotfs` | партия-03.md:90 | | six_player_multiplayer_sotfs | до 6 игроков в кооп (с 4 в оригинале) | Серверная нагрузка |
- `integrated_multiplayer_scaling` | партия-03.md:144 | | integrated_multiplayer_scaling | matchmaking с password для друзей + язык | Удобство кооп |
- `no_online_multiplayer` | партия-03.md:197 | | no_online_multiplayer | полностью single-player (Miyazaki намеренно) | Нет replayability через PvP |
- `asynchronous_multiplayer` | партия-03.md:253 | | asynchronous_multiplayer | messages + bloodstains + invasions как в Souls | Унаследовано |
- `ranked_matchmaking_added` | партия-03.md:302 | | ranked_matchmaking_added | PvP matchmaking добавлен позже (изначально только private lobbies) | Позднее улучшение |
- `coop_mission_4p` | партия-04.md:30 | | coop_mission_4p | кооперативные миссии до 4 игроков | Дополнительный netcode |
- `faction_war_meta_game` | партия-04.md:268 | | faction_war_meta_game | territory control между 3 фракциями с разными картами | Серверная инфраструктура |
- `dedicated_servers_pvp` | партия-04.md:272 | | dedicated_servers_pvp | dedicated servers (P2P в 2017 → dedicated позднее) | Стоимость серверов |
- `faction_war_persistent_meta` | партия-04.md:273 | | faction_war_persistent_meta | территория переходит в 6-часовых циклах | Серверная нагрузка |
- `for_honor_dedicated_servers` | партия-04.md:274 | | for_honor_dedicated_servers | DED серверы для ranked | Server cost |
- `creation_engine_multiplayer` | партия-05.md:168 | | creation_engine_multiplayer | первый мультиплеер в истории Creation Engine | Огромный porting effort |
- `quake_netcode_retrofit` | партия-05.md:169 | | quake_netcode_retrofit | использование netcode из Quake для мультиплеера | Не оптимально для современной игры |
- `dedicated_servers_always_on` | партия-05.md:172 | | dedicated_servers_always_on | выделенные серверы Bethesda | Серверные расходы |
- `multiplayer_32_players` | партия-06.md:37 | | multiplayer_32_players | увеличение с 16 до 32 на PC | Серверная нагрузка |
- `multiplayer_loadout_2_weapons` | партия-07.md:35 | | multiplayer_loadout_2_weapons | загрузка 2 оружия + модули | Дороже UI |
- `battlemode_asymmetric_1v2` | партия-07.md:91 | | battlemode_asymmetric_1v2 | 1 Doom Slayer vs 2 player-демонов | Дорого балансировать |
- `multiplayer_road_rage_coop` | партия-07.md:163 | | multiplayer_road_rage_coop | 2 мультиплеер-режима (Road Rage, Legends of the Wasteland) | Доп. контент |
- `mac_os_x_no_multiplayer` | партия-07.md:164 | | mac_os_x_no_multiplayer | OS X версия — single-player only | Сокращение пути |
- `wingstick_boomerang` | партия-07.md:166 | | wingstick_boomerang | wingstick как стелс-оружие | Контент |
- `competitive_multiplayer_skirmish` | партия-07.md:174 | | competitive_multiplayer_skirmish | skirmish mode через 2P co-op | Дороже |
- `server_tickrate_optimized` | партия-07.md:238 | | server_tickrate_optimized | оптимизирован под 120 Hz серверы | Дороже серверов |
- `multiplayer_2014_terminated` | партия-08.md:49 | | multiplayer_2014_terminated | multiplayer отключён 30.05.2014 (закрытие GameSpy) | Потеря функционала |
- `console_2011_no_multiplayer_no_dlc` | партия-08.md:50 | | console_2011_no_multiplayer_no_dlc | консоли без multiplayer и без Warhead и без "Ascension" | Упрощение |
- `steamworks_pc_multiplayer` | партия-08.md:112 | | steamworks_pc_multiplayer | Steamworks integration (PC) | Удороажние network |
- `multiplayer_hacked_beta_leak` | партия-08.md:117 | | multiplayer_hacked_beta_leak | бета утекла 11.02.2011 (Cevat Yerli: "deeply disappointed") | Промо-проблема |
- `multiplayer_servers_killed_2014` | партия-08.md:118 | | multiplayer_servers_killed_2014 | GameSpy killed 30.05.2014 — мультиплеер мёртв | Потеря функционала |
- `multi_hunter_2v12` | партия-08.md:247 | | multi_hunter_2v12 | до 12 игроков в Bounty Hunt, 18 в Soul Survivor | Серверная нагрузка |
- `no_crossplay_ps4_xbox` | партия-08.md:252 | | no_crossplay_ps4_xbox | нет crossplay между PS4/Xbox (только PC + консоль одного семейства) | Серверная архитектура |
- `networked_water_simulation` | партия-09.md:25 | | networked_water_simulation | вода синхронизирована между всеми игроками | Серверный overhead |
- `64_player_multiplayer` | партия-09.md:27 | | 64_player_multiplayer | до 64 игроков (PC/PS4/XB1), 24 на PS3/360 | Серверный overhead |
- `networked_water_full_wave_simulation` | партия-09.md:35 | | networked_water_full_wave_simulation | вода с полной симуляцией волн | Удороажние |
- `25_hz_tickrate` | партия-09.md:47 | | 25_hz_tickrate | сетевой тикрейт 25 Hz на 64 игроков | Серверный overhead |
- `operations_multi_map_mode` | партия-09.md:97 | | operations_multi_map_mode | Operations — несколько карт подряд (50+ игроков) | Дороже серверной логики |
- `horses_in_multiplayer` | партия-09.md:101 | | horses_in_multiplayer | лошади как транспорт (новая механика для серии) | Дороже physics |
- `combined_arms_coop` | партия-09.md:171 | | combined_arms_coop | 4-player coop | Дороже networking |
- `firestorm_64_players_br` | партия-09.md:184 | | firestorm_64_players_br | 64 игрока в Firestorm BR | Дороже server |
- `128_player_multiplayer_pc_nextgen` | партия-09.md:228 | | 128_player_multiplayer_pc_nextgen | 128 игроков на PC/PS5/XSX (64 на PS4/XB1) | Серверный overhead |
- `cross_play_first_battlefield` | партия-09.md:235 | | cross_play_first_battlefield | первый Battlefield с кросс-играем (PS5/Win/XSX) | Удороажние network |
- `heroes_vs_villains_4v4` | партия-09.md:307 | | heroes_vs_villains_4v4 | 4v4 Heroes-only режим | Дороже |
- `extraction_2v2` | партия-09.md:308 | | extraction_2v2 | 2v2 extraction | Дороже |
- `netcode_rebuilt_30pct_latency` | партия-11.md:79 | | netcode_rebuilt_30pct_latency | переписанный неткод: −30% latency, меньше ability sync errors | Совместимость со старыми реплеями потеряна |
- `format_6v6_to_5v5` | партия-11.md:80 | | format_6v6_to_5v5 | 12→10 игроков: убран второй танк, очереди танков душили матчмейкинг | Баланс всех героев переписан |
- `favor_the_shooter` | партия-11.md:81 | | favor_the_shooter | преимущество стреляющему ценой смертей за углом | Вечный налог дизайна |
- `tick_63hz_comp_120hz` | партия-11.md:83 | | tick_63hz_comp_120hz | 63 Гц клиент, до 120 Гц в соревновательных | Серверный overhead |
- `tick_64mm_128faceit_split` | партия-11.md:182 | | tick_64mm_128faceit_split | GO: 64 tick MM vs 128 tick FACEIT/турниры — раскол decade-спора | Недоверие к MM |
- `lag_compensation_rewind` | партия-11.md:183 | | lag_compensation_rewind | перемотка мира на пинг+интерп для честного хитрега | Peekers advantage неустраним |
- `subtick_cs2_replaces_tick` | партия-11.md:184 | | subtick_cs2_replaces_tick | CS2: sub-tick — сервер знает точный момент выстрела внутри тика (снапшоты 64 Гц) | Споры «ватности», удаление cl_interp |
- `dedicated_server_linux` | партия-11.md:240 | | dedicated_server_linux | headless dedicated Win/Linux + Eden + Workshop | Серверный AI ест fps миссии |

## open_world_streaming — 31

- `baked_occlusion_culling` | партия-01.md:31 | | baked_occlusion_culling (BSP) | статическая видимость, предвычисленная на этапе компиляции карты | Невозможна динамическая деформация стен |
- `baked_occlusion_culling` | партия-01.md:345 | | baked_occlusion_culling | precomputed видимость для крупных зон | Не учитывает динамические разрушения |
- `hierarchical_lod` | партия-01.md:346 | | hierarchical_lod | несколько уровней детализации для лесов и городов | Перестройка при изменении мира |
- `hierarchical_lod_horizon` | партия-01.md:396 | | hierarchical_lod_horizon | LOD-система с дальностью прорисовки до горизонта | Видимые переключения при быстром движении |
- `async_loading_pipeline` | партия-01.md:503 | | async_loading_pipeline | чанковый стриминг мира для бесшовных переходов | Сложная синхронизация с AI/сессиями |
- `hierarchical_lod_open_zones` | партия-01.md:504 | | hierarchical_lod_open_zones | LOD для больших зон с растительностью и городами | Перестройка при каждом expansion |
- `open_world_sections` | партия-02.md:137 | | open_world_sections | менее линейные зоны (White Forest, леса, шахты) | Больше памяти и бюджет |
- `interconnected_world_no_warping` | партия-03.md:26 | | interconnected_world_no_warping | единый мир Lordran без warping, только unlockable shortcuts | Сложная навигация для игрока |
- `larger_zones_fewer_count` | партия-03.md:140 | | larger_zones_fewer_count | меньше зон, но больше по масштабу (под влиянием Zelda BotW) | Длиннее переходы |
- `open_world_torrent_navigation` | партия-03.md:239 | | open_world_torrent_navigation | открытый мир с лошадью Torrent для перемещения | Удвоенная работа левел-дизайна |
- `large_open_world_chunk_loading` | партия-03.md:245 | | large_open_world_chunk_loading | стриминг мира на PS4 с ограниченной RAM | Узкое место памяти на старых консолях |
- `open_world_boss_design` | партия-03.md:249 | | open_world_boss_design | боссы спрятаны по всему миру, не линейная последовательность | Нелинейный баланс сложности |
- `first_fromsoftware_open_world` | партия-03.md:250 | | first_fromsoftware_open_world | первая попытка open-world (раньше были только связанные зоны) | Новые паттерны memory management |
- `paris_1_to_1_scale` | партия-04.md:25 | | paris_1_to_1_scale | реальные размеры Парижа | Сложнее навигации и оптимизации |
- `1000_planets_landable` | партия-05.md:240 | | 1000_planets_landable | 1000+ планет, можно приземлиться | Уникальный scale |
- `broken_space_travel_loading_screens` | партия-05.md:256 | | broken_space_travel_loading_screens | путешествие между планетами = загрузочный экран (НЕ seamless) | Огромный скандал на старте |
- `no_real_seamless_space` | партия-05.md:257 | | no_real_seamless_space | нет бесшовного космоса между планетами | Разочарование критиков |
- `id_tech_6_streaming_textures` | партия-07.md:28 | | id_tech_6_streaming_textures | мега-текстуры через стриминг | Дорого на HDD |
- `streaming_from_optical_media` | партия-07.md:156 | | streaming_from_optical_media | оптимизированный стриминг с Blu-ray/3 DVD | DVD на 360, Blu-ray на PS3 |
- `open_world_fps_driving` | партия-07.md:159 | | open_world_fps_driving | гибрид FPS + driving (Mad Max-стиль) | Дороже pipeline |
- `open_world_light_wasteland` | партия-07.md:160 | | open_world_light_wasteland | открытый мир (для 2011 года — большая редкость) | Удороажние streaming |
- `texture_streaming_world_gen` | партия-07.md:179 | | texture_streaming_world_gen | мировые текстуры генерируются при загрузке | Удороажние memory |
- `seven_wonders_open_levels` | партия-08.md:173 | | seven_wonders_open_levels | 7 открытых уровней (Seven Wonders) | Дороже production |
- `rich_presence_landscape` | партия-09.md:45 | | rich_presence_landscape | обширные ландшафты (China Rising, Naval Strike и т.д.) | Память |
- `map_clustering_design` | партия-09.md:237 | | map_clustering_design | карты "несколько меньших, сшитых вместе" | Дороже дизайна |
- `open_areas_with_aurora_train` | партия-10.md:36 | | open_areas_with_aurora_train | открытые зоны с поездом Aurora как хаб | Удороажние streaming |
- `prague_hub_open_world` | партия-10.md:113 | | prague_hub_open_world | Прага как открытый hub с малыми районами | Удороажние streaming |
- `redengine4_streaming_nightcity` | партия-11.md:23 | | redengine4_streaming_nightcity | потоковый Night City без швов, district-чанки + вертикальные слои | CPU-bound на HDD |
- `hdd_to_ssd_mandatory` | партия-11.md:31 | | hdd_to_ssd_mandatory | после 2.0 HDD официально не поддерживается — только SSD | Отсечение слабого железа |
- `rewrite_chunk_render_1_8_1_15` | партия-11.md:131 | | rewrite_chunk_render_1_8_1_15 | 1.8–1.15: переписывание чанк-рендера, VBO, frustum culling | Ломало моды (OptiFine) |
- `view_distance_cpu_linear` | партия-11.md:234 | | view_distance_cpu_linear | дальность отрисовки линейно грузит CPU (объекты + тени + AI) | Настройка Objects/Terrain/Visibility — главный рычаг |

## particle_systems — 5

- `gpu_particle_simulation` | партия-01.md:79 | | gpu_particle_simulation | particle-pool для гелей и bubbles в pixel shader с early clip | Однопоточный submit в Source MP |
- `particle_pooling` | партия-01.md:84 | | particle_pooling | пул для дыма, искр, воды (от Left 4 Dead) | Фиксированный пул |
- `particle_pooling` | партия-01.md:134 | | particle_pooling | пул частиц для explosions/эффектов | Фиксированный пул |
- `gpu_particles_hell_skull` | партия-07.md:31 | | gpu_particles_hell_skull | GPU-based частицы | Удороажние эффектов |
- `volumetric_smoke_dynamic` | партия-11.md:185 | | volumetric_smoke_dynamic | Source 2 volumetric дым: пули/HE взаимодействуют, раскрывается | GPU cost |

## path_tracing — 4

- `fully_ray_traced_enhanced_2021` | партия-10.md:54 | | fully_ray_traced_enhanced_2021 | Enhanced Edition (14.06.2021) — **полностью удалён растеризованный конвейер освещения**: из сборника 2021 года **полностью вырезаны запечённые световые карты (lightmaps) и традиционные точечные растеризованные источники света и теневые буферы**,…
- `path_tracing_optional` | партия-10.md:254 | | path_tracing_optional | path tracing для next-gen PC | Vendor-specific |
- `path_tracing_consoles_excluded` | партия-10.md:268 | | path_tracing_consoles_excluded | path tracing только на PC (next-gen консоли слишком слабые) | Vendor-specific |
- `rt_overdrive_path_tracing` | партия-11.md:25 | | rt_overdrive_path_tracing | RT Overdrive (патч 2023): полный path tracing вместо гибридного RT | Только RTX 40xx + DLSS 3 FG для 60 fps |

## physics_simulation — 29

- `portal_momentum_conservation` | партия-01.md:29 | | portal_momentum_conservation | импульс сохраняется через математическое преобразование векторов на границе портала | Точность зависит от float-точности углов |
- `fixed_timestep_physics` | партия-01.md:32 | | fixed_timestep_physics | детерминированный шаг симуляции | Однопоточный скриптовый движок Source |
- `excursion_funnel_force_field` | партия-01.md:81 | | excursion_funnel_force_field | инвертированные зоны гравитации как force-field volumes | Требует пересчёта коллизий каждый кадр |
- `physics_gun_constraints` | партия-01.md:131 | | physics_gun_constraints | wire-constraints (верelet/weld/nocollide/freeze) для манипуляции объектами | Лимиты sbox_max; нужен cleanup |
- `physics_lod_sleeping` | партия-01.md:133 | | physics_lod_sleeping | sleep/wake объектов вне зоны активности | Сложнее профилировать |
- `fixed_timestep_physics_60fps` | партия-01.md:185 | | fixed_timestep_physics_60fps | жёсткий 60 fps-тайминг; бюджет кадра определяет всё остальное | Ограничение масштабов разрушаемости |
- `dynamic_fire_propagation` | партия-01.md:291 | | dynamic_fire_propagation | объёмное распространение огня от огнемёта (первая CoD с настоящей физикой пламени) | Тяжёлый fillrate при больших пожарах |
- `havok_physics_layer` | партия-01.md:343 | | havok_physics_layer | Havok для ragdoll и тяжёлых тканей | Стоимость лицензии |
- `havok_ragdoll_quality` | партия-01.md:348 | | havok_ragdoll_quality | качественные ragdoll-смерти через Havok | Нагрузка на CPU в больших битвах |
- `havok_physics_integration` | партия-01.md:398 | | havok_physics_integration | Havok для ragdoll и коллизий | Стоимость лицензии |
- `physx_particle_simulation` | партия-01.md:454 | | physx_particle_simulation | NVIDIA PhysX для дыма, листьев, ткани, осыпающихся поверхностей | На AMD/Intel без CUDA спецэффекты отсутствуют |
- `havok_physics_wrapper` | партия-02.md:24 | | havok_physics_wrapper | Havok SDK с собственной обёрткой VPhysics для пропсов, QPhysics для NPC; интеграция в лиц-циклы движка | Стоимость лицензии; overhead конвертации на CPU |
- `fixed_timestep_physics_60hz` | партия-02.md:26 | | fixed_timestep_physics_60hz | детерминированный шаг 66.6 Гц для предсказуемой физики | Однопоточный скриптовый движок |
- `sleep_wake_states` | партия-02.md:27 | | sleep_wake_states | OBJ_AWAKE/STARTSLEEP/SLEEP — спящие объекты не симулируются | Расход на пробуждение для больших составных объектов |
- `superman_gravity_gun_fix` | партия-02.md:28 | | superman_gravity_gun_fix | ручной апдейт массы поднятого объекта для предотвращения бесконечного ускорения | Требует физического тюнинга; не универсально |
- `gravity_gun_first_weapon` | партия-02.md:91 | | gravity_gun_first_weapon | gravity gun получаешь сразу (не crowbar как в HL2) — паззл-ориентированный геймплей | Меньше традиционного FPS |
- `physics_puzzle_bridge` | партия-02.md:142 | | physics_puzzle_bridge | самый большой физический паззл на тот момент (мост) | Узкие места collision detection |
- `source_engine_ragdoll_physics` | партия-02.md:186 | | source_engine_ragdoll_physics | ragdoll-физика для тел вместо предопределённых death-animations | Больше расход CPU |
- `enhanced_physics_world` | партия-02.md:188 | | enhanced_physics_world | бочки, покрышки, бутылки физические; гранаты реалистично катят и рикошетят | Новая стоимость CPU для коллизий |
- `environmental_hazard_simulation` | партия-02.md:312 | | environmental_hazard_simulation | вода из Houdini 3D animation tool для surface maps; flow вместо scroll для реалистичных болот | Production cost |
- `mtx_frame_rate_bug` | партия-03.md:88 | | mtx_frame_rate_bug | frame-rate зависимое durability оружия — баг, не исправлен до апреля 2015 | Известный долгоиграющий баг |
- `hitbox_combat_system` | партия-04.md:81 | | hitbox_combat_system | hit-box вместо paired animation (как в Souls) | Удорожание AI и анимаций |
- `hitbox_combat_refined` | партия-04.md:141 | | hitbox_combat_refined | улучшенный из Origins; добавили dodge | Доп. анимации |
- `euphoria_naturalmotion` | партия-06.md:24 | | euphoria_naturalmotion | ragdoll-подобная физика анимации тела (NaturalMotion) | Лицензия + overhead |
- `physx_optional` | партия-06.md:39 | | physx_optional | опциональная PhysX-физика | Vendor lock-in (Nvidia) |
- `euphobia_ragdoll_physics` | партия-06.md:92 | | euphobia_ragdoll_physics | NaturalMotion Euphoria для всех NPC | Лицензия |
- `unprecedented_detail_simulation` | партия-06.md:151 | | unprecedented_detail_simulation | знаменитая детализация — ядро лошади при 30° C, шерсть реагирует на ветер | Огромный CPU/HDD cost |
- `realistic_combat_physics` | партия-10.md:171 | | realistic_combat_physics | физика боя на основе веса и скорости | Дороже physics |
- `real_archery_bow_physics` | партия-10.md:188 | | real_archery_bow_physics | реалистичная физика стрел | Дороже physics |

## portal_rendering — 3

- `runtime_stencil_portal_rendering` | партия-01.md:28 | | runtime_stencil_portal_rendering | stencil-буфер DX9 вырезает произвольную форму портала, текстурные координаты и векторы передаются через границу с коррекцией перспективы | Конфликт с водой и reflection (выключают stencil) |
- `paintmap_gel_rendering` | партия-01.md:78 | | paintmap_gel_rendering | SDF-сетки (signed distance fields) для физики и рендера гелей; paintmap удваивает lightmap-память | Удвоенная VRAM на лайтмапы; слабые GPU страдают от fill-rate |
- `laser_dynamic_reflection` | партия-01.md:80 | | laser_dynamic_reflection | динамическая трассировка отражений на CPU до 10 переотражений за кадр | Растёт нагрузка CPU при сложных сценах |

## post_processing — 19

- `depth_prepass_early_z` | партия-01.md:33 | | depth_prepass_early_z | ранний Z-проход для снижения overdraw при множественных порталах | Дополнительный draw pass |
- `deferred_forward_plus_choice` | партия-01.md:82 | | deferred_forward_plus_choice | гибридный forward+ рендеринг, выбор по сцене | Сложнее дебага |
- `detective_vision_postprocess` | партия-01.md:452 | | detective_vision_postprocess | post-process эффект: синийт, выделение интерактивных объектов | Потеря информации за стенами |
- `post_effect_selective` | партия-01.md:457 | | post_effect_selective | Detective Vision и другие post-эффекты | Стоимость fillrate при наложении |
- `cubemap_reflections` | партия-02.md:189 | | cubemap_reflections | отражения через cube mapping — прицелы отражают окружение | VRAM cost |
- `dynamic_color_correction` | партия-02.md:250 | | dynamic_color_correction | адаптивная цветокоррекция под ситуацию | Pass cost |
- `film_grain_vignetting` | партия-02.md:251 | | film_grain_vignetting | постпроцесс как в фильмах ужасов | Pass cost |
- `color_grading_per_area` | партия-03.md:145 | | color_grading_per_area | цветовая палитра по зоне (Fextrlands — пурпур, Ashes — бело-красный) | Удорожание art-pipeline |
- `temporal_anti_aliasing` | партия-05.md:112 | | temporal_anti_aliasing | TAA | Без cost |
- `screen_space_reflections` | партия-05.md:114 | | screen_space_reflections | SSR | Reflection на блестящих поверхностях |
- `motion_blur` | партия-05.md:117 | | motion_blur | размытие в движении | Удобство |
- `filmic_tone_mapping` | партия-05.md:118 | | filmic_tone_mapping | кинематографический тон | Удобство |
- `hdr_pc_late` | партия-05.md:254 | | hdr_pc_late | HDR для PC добавлен позже | Консоль имела HDR с релиза |
- `hdr_bloom_2d_array` | партия-07.md:42 | | hdr_bloom_2d_array | HDR + bloom через 2D array | Дороже |
- `motion_blur_object_motion` | партия-08.md:31 | | motion_blur_object_motion | object motion blur (DX10) | Удороажние |
- `depth_of_field_bokeh` | партия-08.md:32 | | depth_of_field_bokeh | depth of field с bokeh | Дороже |
- `hbao_horizon_based_ao` | партия-09.md:38 | | hbao_horizon_based_ao | HBAO+ на PC | Дороже |
- `hdr_display_support` | партия-09.md:178 | | hdr_display_support | HDR-выход | Vendor-specific |
- `aofx_bokeh_dof` | партия-10.md:121 | | aofx_bokeh_dof | AMD AOFX для боке/DoF | Vendor-specific |

## procedural_terrain — 4

- `procedural_resource_generation` | партия-01.md:244 | | procedural_resource_generation | многооктавный шум Перлина для ресурсов/рельефа | Зависимость от seed-детерминизма |
- `procedural_terrain_erosion` | партия-01.md:395 | | procedural_terrain_erosion | эрозионные алгоритмы для генерации ландшафта | Сложнее ручной правки |
- `procedural_world_generation` | партия-04.md:82 | | procedural_world_generation | procedural generation для пустынь и NPC поведения | Доп. QA |
- `procedural_planet_generation` | партия-05.md:238 | | procedural_planet_generation | 1000+ планет через procgen с handcrafted POI | Дороже чем handcraft all |

## procedural_vegetation — 4

- `tree_billboard_to_polygon` | партия-01.md:402 | | tree_billboard_to_polygon | полностью полигональная растительность (вместо спрайтов Morrowind) | Больше мешей в сцене |
- `procedural_paris_buildings` | партия-04.md:34 | | procedural_paris_buildings | некоторые здания созданы процедурно | Уникальные баги |
- `wind_weighted_trees_branches` | партия-05.md:31 | | wind_weighted_trees_branches | физ-ветви деревьев реагируют на ветер | Production cost |
- `procedural_vegetation` | партия-08.md:28 | | procedural_vegetation | CryEngine 2 — процедурная растительность | Удороажние pipeline |

## project_architecture — 36

- `lua_scripting_extension` | партия-01.md:130 | | lua_scripting_extension | Lua-VM поверх Source — пользовательская игровая логика без перекомпиляции C++ | Один плохой аддон кладёт серверный тик |
- `wiremod_visual_programming` | партия-01.md:138 | | wiremod_visual_programming | визуальное программирование конструкций через wire/E2 | Ограничение на кап констрейнтов |
- `community_moddable_dll` | партия-01.md:243 | | community_moddable_dll | исходный код DLL выпущен в Fall Patch 2012 | Требует обратной совместимости |
- `source_engine_2006_transition` | партия-02.md:194 | | source_engine_2006_transition | переход на Source 2006 (Episode One) с исправлением багов и новыми фичами | Разрыв комьюнити на v34/новый |
- `source_engine_2013_mp_transition` | партия-02.md:195 | | source_engine_2013_mp_transition | переход на Source 2013 MP branch в апреле 2013 + SteamPipe | Унификация кода |
- `l4d_authoring_tools_2009` | партия-02.md:261 | | l4d_authoring_tools_2009 | Source SDK плагины для SketchUp импорта | UGC |
- `source_engine_2_transition` | партия-02.md:382 | | source_engine_2_transition | переход на Source 2 в Counter-Strike 2 (сентябрь 2023) | Sub-tick input, новые дымы |
- `panorama_ui_replacement` | партия-02.md:384 | | panorama_ui_replacement | замена Scaleform на собственную Panorama UI (декабрь 2018) | Унификация UI |
- `mod_support_easy_mode` | партия-03.md:199 | | mod_support_easy_mode | моддеры создали easy-mode моды через замедление персонажа | Скандал (FromSoftware не одобрили) |
- `modding_creation_kit` | партия-05.md:43 | | modding_creation_kit | официальный SDK для модов | UGC-экосистема |
- `mod_support_season_7_2024` | партия-05.md:187 | | mod_support_season_7_2024 | Creation Club-like поддержка | UGC |
- `creation_engine_2_first_game` | партия-05.md:237 | | creation_engine_2_first_game | новая версия движка (текстуры 4K+ и т.д.) | Удвоенный development cost |
- `mod_support_creation_kit` | партия-05.md:251 | | mod_support_creation_kit | Creation Kit for Starfield (2024) | UGC |
- `gta_online_separate_client` | партия-06.md:98 | | gta_online_separate_client | 1 октября 2013 — онлайн выделен в отдельный продукт | Серверная нагрузка |
- `rd_online_separate_client` | партия-06.md:179 | | rd_online_separate_client | 1 декабря 2020 — выделен в отдельный продукт | Серверы |
- `apex_engine_grove_street` | партия-06.md:240 | | apex_engine_grove_street | не RAGE — UE4 | Архитектурное отличие |
- `procedural_megawad_snapmap` | партия-07.md:26 | | procedural_megawad_snapmap | level editor для community-контента (SnapMap) | Удороажние |
- `id_studio_modding_tools_2013` | партия-07.md:172 | | id_studio_modding_tools_2013 | официальный modding набор (Steam) | Удороажние pipeline |
- `saber3d_engine_hybrid` | партия-07.md:225 | | saber3d_engine_hybrid | гибрид id Tech + Saber3D (вместо id Tech 6) | Удороажние |
- `modding_support_none` | партия-07.md:227 | | modding_support_none | без моддинга (огромное разочарование) | Нет UGC |
- `hybrid_idtech_saber_engine` | партия-07.md:236 | | hybrid_idtech_saber_engine | редкий гибрид движков | Удороажние поддержки |
- `wulf_glass_engine_2017` | партия-07.md:239 | | wulf_glass_engine_2017 | community mode (Warfork fork) | UGC |
- `sandbox_level_editor` | партия-08.md:37 | | sandbox_level_editor | Sandbox2 editor — тот же, что Crytek использовали для разработки | Удороажние |
- `improved_engine_2024` | партия-08.md:242 | | improved_engine_2024 | CryEngine 5.11+ обновление | Удороажние pipeline |
- `battlefield_portal_modding` | партия-09.md:233 | | battlefield_portal_modding | Battlefield Portal — community rules modification (логика правил) | Дороже UI |
- `no_mod_tools` | партия-09.md:247 | | no_mod_tools | нет mod-tools для PC (в отличие от BF4) | Потеря community |
- `physicalized_hud_no_minimap` | партия-10.md:23 | | physicalized_hud_no_minimap | информация на запястье (часы), маске, фонарике — без минимапы | Дороже контента |
- `steam_workshop_mod_support` | партия-10.md:49 | | steam_workshop_mod_support | официальный SDK (январь 2023) | Удороажние |
- `physicalized_ui_minimal_hud` | партия-10.md:104 | | physicalized_ui_minimal_hud | информация в игровом мире, а не на HUD | Дороже production |
- `modding_tools_october_2019` | партия-10.md:201 | | modding_tools_october_2019 | официальные modding tools (4A Engine) | Удороажние |
- `no_hud_physicalized` | партия-10.md:273 | | no_hud_physicalized | часы, маски, фонарики вместо HUD | Дороже production |
- `ow_engine_2_rebuild` | партия-11.md:78 | | ow_engine_2_rebuild | 4 года апгрейда движка: большие PvE-карты, новые враги, улучшенный рендер | Только для OW2, OW1 остался на старом |
- `kernel_anticheat_in_engine` | партия-11.md:85 | | kernel_anticheat_in_engine | kernel-level античит встроен в движок (не болт-он) | Конфликты с драйверами |
- `java_17_21_migration` | партия-11.md:134 | | java_17_21_migration | 1.18+ → Java 17, 1.21+ → Java 21: ZGC/Generational GC, меньше пауз | Требования к лаунчеру |
- `panorama_ui_replace_scaleform` | партия-11.md:187 | | panorama_ui_replace_scaleform | Panorama вместо Scaleform (2018) | Перепись HUD |
- `eden_3d_editor_1_56` | партия-11.md:237 | | eden_3d_editor_1_56 | Eden Update 1.56 (02.2016): 3D-редактор + audio overhaul + Geometric Occluder (из DayZ) | Переучивание миссионеров |

## ray_traced_effects — 13

- `gpu_raytraced_shadows` | партия-01.md:237 | | gpu_raytraced_shadows | тени через ray-tracing на GPU + AA shadow maps | Не масштабируется на старых GPU |
- `ray_tracing_dlss_sottr` | партия-03.md:251 | | ray_tracing_dlss_sottr | ray tracing (обновление 2024) + DLSS/FSR | Только на новых платформах |
- `ray_tracing_consoles` | партия-07.md:102 | | ray_tracing_consoles | PS5/XSX — RT отражения и освещение | Vendor-specific |
- `ray_tracing_2024` | партия-08.md:238 | | ray_tracing_2024 | hardware RT в обновлении "1896" | Удороажние |
- `real_time_ray_tracing_reflections` | партия-09.md:161 | | real_time_ray_tracing_reflections | DXR RT-отражения (только Nvidia RTX) | Дорого на HW |
- `ray_tracing_dxr` | партия-09.md:168 | | ray_tracing_dxr | Microsoft DXR API | Vendor-specific |
- `dxr_ray_traced_reflections_dx12` | партия-09.md:175 | | dxr_ray_traced_reflections_dx12 | DXR через DX12 (Windows 10) — **первый коммерческий релиз с поддержкой гибридной аппаратной трассировки лучей DXR (отражения) + DLSS 1.0 в ноябре 2018** | Vendor-specific |
- `no_ray_tracing_consoles` | партия-09.md:179 | | no_ray_tracing_consoles | RT только на PC с RTX | Консольное упрощение |
- `ray_tracing_post_launch` | партия-09.md:312 | | ray_tracing_post_launch | RT добавлен в пост-запуске (Xbox Series X) | Vendor-specific |
- `ray_tracing_xbox_series_x` | партия-10.md:47 | | ray_tracing_xbox_series_x | RT на next-gen консолях | Vendor-specific |
- `ray_traced_global_illumination` | партия-10.md:253 | | ray_traced_global_illumination | RT GI в реальном времени | Дорого (без RTX = плохая производительность) |
- `dlss_3_5_ray_reconstruction` | партия-10.md:255 | | dlss_3_5_ray_reconstruction | DLSS 3.5 с Ray Reconstruction (Nvidia) | Vendor-specific |
- `dlss3_fg_ray_reconstruction` | партия-11.md:26 | | dlss3_fg_ray_reconstruction | DLSS 3.5 Ray Reconstruction + Frame Generation | Vendor lock-in NVIDIA |

## render_scalability — 9

- `4k_60fps_next_gen_update` | партия-04.md:279 | | 4k_60fps_next_gen_update | 4K/60 на PS5/Xbox Series | Улучшение разрешения |
- `fov_slider_added_late` | партия-05.md:253 | | fov_slider_added_late | добавлен в патче 1.8.86 (ноябрь 2023) | Отсутствовал на старте |
- `high_resolution_textures` | партия-06.md:230 | | high_resolution_textures | текстуры 4K | Память |
- `4k_60_fps_current_gen` | партия-06.md:232 | | 4k_60_fps_current_gen | улучшенный фреймрейт на PS5/Xbox Series | Доп. cost |
- `high_resolution_texture_pack` | партия-08.md:114 | | high_resolution_texture_pack | high-res текстуры (768 MB+ VRAM) | Память |
- `4k_ps5_xsx_support` | партия-08.md:241 | | 4k_ps5_xsx_support | полная 4K на PS5/Xbox Series | Доп. cost |
- `full_hd_rendering_pc` | партия-09.md:36 | | full_hd_rendering_pc | нативный 1080p на PC | Память |
- `dynamic_resolution_optional` | партия-09.md:44 | | dynamic_resolution_optional | динамическое разрешение на PS4/XB1 | Удороажние |
- `ps5_xsx_4k_native` | партия-10.md:275 | | ps5_xsx_4k_native | нативно 4K на PS5 и XSX | Vendor-specific |

## rendering_architecture — 57

- `single_thread_main_loop` | партия-01.md:132 | | single_thread_main_loop | net + phys + Lua в одном потоке | Один поток = упор в clock, не в cores |
- `material_bullet_penetration` | партия-01.md:186 | | material_bullet_penetration | каждый материал имеет проникающую способность (cover vs concealment) | Больше вариантов материала = больше памяти и CPU |
- `deferred_cpu_threading` | партия-01.md:241 | | deferred_cpu_threading | 4 уровня AI на отдельных потоках | Синхронизация между слоями |
- `material_bullet_penetration` | партия-01.md:296 | | material_bullet_penetration | унаследован от IW 3.0 | Те же ограничения, что и в CoD4 |
- `redengine_blinn_phong_rendering` | партия-01.md:341 | | redengine_blinn_phong_rendering | Blinn-Phong specular/Diffuse через DX9 Shader Model 3.0, мягкие тени, SSAO — **PBR и Forward+ отсутствовали в 2011 году** (появились только в REDengine 3 / Witcher 3 2015) | Упрощённая модель материалов, нет energy conservation |
- `fp16_hdr_rendering` | партия-01.md:394 | | fp16_hdr_rendering | HDR с FP16 буферами — одна из первых AAA-реализаций 2006 | Полноэкранный блум на слабых GPU |
- `baked_occlusion_culling_vis` | партия-01.md:397 | | baked_occlusion_culling_vis | vis-расчёт для статической геометрии | Не учитывает динамические объекты |
- `specular_mapping_materials` | партия-01.md:403 | | specular_mapping_materials | specular-mapping на материалах | Требования к видеопамяти |
- `multithreaded_jobs` | партия-01.md:505 | | multithreaded_jobs | Duty Finder матчмейкинг и инфраструктура на отдельных потоках | Стоимость синхронизации |
- `aabb_quadtree_culling` | партия-01.md:512 | | aabb_quadtree_culling | агрессивное отсечение невидимых зон | Сложнее для open-zone с динамическими эффектами |
- `substance_material_system` | партия-02.md:25 | | substance_material_system | материал задаёт физические свойства, звук шагов, friction, density автоматически | Ограниченный набор параметров |
- `HDR_FP16_phong_fresnel` | партия-02.md:37 | | HDR_FP16_phong_fresnel | Phong-spec и Fresnel-rim для Alyx; в пещерах Ep2 — полупрозрачная радиосити | Цена DX9 path, ps_2_b совместимости |
- `phong_fresnel_spec_alys` | партия-02.md:94 | | phong_fresnel_spec_alys | Phong-spec и Fresnel-rim для Alyx | Удорожание шейдеров |
- `3d_skyboxes` | партия-02.md:190 | | 3d_skyboxes | расширение видимого мира за пределы playable area | Удорожание рендера |
- `bump_normal_specular_maps` | партия-02.md:191 | | bump_normal_specular_maps | bump/normal/specular mapping через DX9 | Требования к GPU |
- `multicore_rendering` | партия-02.md:244 | | multicore_rendering | Source 2008 — многопоточность для анимации, рендера, физики | Сложная синхронизация |
- `damage_zone_textures` | партия-02.md:314 | | damage_zone_textures | текстуры с прозрачностью + ellipsoid culling для видимых повреждений на Infected | 13% памяти от базовой системы |
- `dx11_renderer_sotfs` | партия-03.md:89 | | dx11_renderer_sotfs | переход на DX11 с DX9 | Дополнительный код-путь |
- `noshader_optimization` | партия-04.md:37 | | noshader_optimization | сначала DX11, но оптимизировано под 900p на консолях | Ограниченный бюджет на рендер |
- `wet_surfaces_material` | партия-05.md:116 | | wet_surfaces_material | материалы реагируют на дождь | Удвоенный рендер-путь |
- `bullet_software_rendering` | партия-06.md:93 | | bullet_software_rendering | дополнительные post-process (depth of field, motion blur) | Удорожание pipeline |
- `directx_11_renderer` | партия-06.md:95 | | directx_11_renderer | DX11 на PC, переделанный рендер | Удороажние портирования |
- `id_tech_6_new_geometry_pipeline` | партия-07.md:27 | | id_tech_6_new_geometry_pipeline | новая геометрия pipeline | Дороже разработки |
- `async_compute_vulkan` | партия-07.md:29 | | async_compute_vulkan | async compute через Vulkan API | Vendor-специфично |
- `vulkan_api_post_launch_patch` | партия-07.md:38 | | vulkan_api_post_launch_patch | Vulkan API добавлен в патче 11 июля 2016 — **первое в AAA-индустрии внедрение аппаратных очередей асинхронных вычислений (Async Compute) через Vulkan**, на архитектуре AMD GCN (Radeon) прирост производительности **+30–66%** (DF/AMD-блог). Это стал…
- `id_tech_7_extended_vulkan_support` | партия-07.md:101 | | id_tech_7_extended_vulkan_support | Vulkan + RT (PS5/XSX) | Дороже shader compilation |
- `procedural_textures_partially` | партия-07.md:155 | | procedural_textures_partially | частично процедурные текстуры | Удороажние pipeline |
- `level_geometry_corrupt_glass` | партия-07.md:171 | | level_geometry_corrupt_glass | уровни генерируют corruption для визуала | Дороже shader work |
- `craters_pipeline_shaders` | партия-07.md:177 | | craters_pipeline_shaders | новый shader pipeline | Удороажние |
- `dx9_dx10_dual_mode` | партия-08.md:45 | | dx9_dx10_dual_mode | DX9 режим + DX10 режим (новая технология 2007) | Дороже QA |
- `dx9_very_high_cheat` | партия-08.md:48 | | dx9_very_high_cheat | обход через конфиг — DX9 Very High ~ DX10 | Бесплатно для хакеров |
- `directx_11_high_res_textures` | партия-08.md:113 | | directx_11_high_res_textures | DX11 Ultra Upgrade (патч 1.9) | Дороже |
- `dx11_pc_required` | партия-08.md:179 | | dx11_pc_required | PC-версия требует DX11 | Исключает старые GPU |
- `amd_mantle_partnership` | партия-09.md:31 | | amd_mantle_partnership | партнёрство с AMD для Mantle API | Vendor-specific (заброшено) |
- `deferred_renderer_modular` | партия-09.md:40 | | deferred_renderer_modular | модульный deferred renderer | Дороже |
- `amd_mantle_api_debut_2013` | партия-09.md:48 | | amd_mantle_api_debut_2013 | **исторический дебют API AMD Mantle на ПК в декабре 2013** — позволил обойти избыточные накладные расходы драйвера DirectX 11; лёг в основу стандартов Vulkan и DirectX 12 | Удороажние QA/драйверов |
- `hd_texture_pool` | партия-09.md:50 | | hd_texture_pool | HD текстурный пул 4K | Память |
- `physical_based_rendering` | партия-09.md:177 | | physical_based_rendering | PBR для всех материалов | Стандарт |
- `shaders_dx12_async_compute` | партия-09.md:180 | | shaders_dx12_async_compute | async compute через DX12 | Дороже |
- `cel_shading_pbr` | партия-09.md:311 | | cel_shading_pbr | сочетание cel-shading и PBR | Дороже rendering |
- `minimal_subsurface_rendering` | партия-10.md:45 | | minimal_subsurface_rendering | RT на Enhanced Edition | Vendor-specific |
- `pbr_physically_based_rendering` | партия-10.md:118 | | pbr_physically_based_rendering | PBR для всех материалов | Удороажние rendering |
- `directx_12_pc` | партия-10.md:119 | | directx_12_pc | DX12 на PC (оптимизация Nixxes) | Vendor-specific |
- `entity_system_glacier_2` | партия-10.md:122 | | entity_system_glacier_2 | entity-driven архитектура (**Dawn Engine = форк Glacier 2** — студия Eidos-Montréal лицензировала исходный код у IO Interactive после релиза Hitman: Absolution, глубоко модернизировав подсистемы рендеринга) | Дороже AI |
- `historical_real_materials` | партия-10.md:189 | | historical_real_materials | реальные материалы 15-го века (брони, одежда) | Дороже контента |
- `mesh_shaders_first_game` | партия-10.md:252 | | mesh_shaders_first_game | первая игра с native mesh shaders | Дороже shader compilation |
- `meshlet_cluster_renderer` | партия-10.md:267 | | meshlet_cluster_renderer | разбиение геометрии на meshlets для параллельного рендеринга | Дороже rendering |
- `gtx_10_series_poor_optimization` | партия-10.md:269 | | gtx_10_series_poor_optimization | GTX 10 серия (NVIDIA Pascal) = серьёзные проблемы (без mesh shaders). **Техническая природа: архитектура Northlight перенесла отсечение невидимой геометрии в стадию меш-шейдеров; отсутствие аппаратных блоков приводило к сбросу на программный тр…
- `gtx_10_optimization_patch_2024` | партия-10.md:270 | | gtx_10_optimization_patch_2024 | патч марта 2024 улучшил GTX 10 (оптимизированный резервный путь рендеринга) | Vendor-specific |
- `smt_ryzen_fix_2_0` | партия-11.md:27 | | smt_ryzen_fix_2_0 | патч 2.0: нативная поддержка SMT на Ryzen (раньше требовался мод) | Перебалансировка тредов |
- `hybrid_cpu_p_governor_2_11` | партия-11.md:28 | | hybrid_cpu_p_governor_2_11 | патч 2.11 (01.2024): Hybrid CPU Utilization — Auto / Prioritize P-Cores для Intel 12/13/14 gen (Gameplay → Performance) + фикс RX Vega; в 2.11 на i9-13900K+RTX 4080 Super — микростаттеры (Tom's Hardware), пофикшены в 2.12 | Ручной оверрайд планировщ…
- `ecs_determinism` | партия-11.md:82 | | ecs_determinism | ECS + детерминированная симуляция (GDC Tim Ford) | Сложность отладки |
- `dynamic_texture_scaling` | партия-11.md:84 | | dynamic_texture_scaling | автоскейл текстур под сеть и устройство (Switch/PS4) | Мыло на слабом железе |
- `sodium_lithium_modern_fix` | партия-11.md:132 | | sodium_lithium_modern_fix | Sodium (рендер, 221.8M загрузок на Modrinth) + Lithium (тик) + Phosphor (<1.19): кратный рост fps на том же железе без потери картинки; 0.9.x (06.2026) — ранний Vulkan-бэкенд | Только Fabric/NeoForge/Quilt, GL 4.5+; Android/ARM через трансляторы не п…
- `bedrock_renderdragon_rewrite` | партия-11.md:133 | | bedrock_renderdragon_rewrite | Bedrock: RenderDragon (DX12/GL) вместо старого GL — +fps, но сломал шейдеры | Потеря кастомных шейдеров |
- `rv4_single_thread_bottleneck` | партия-11.md:233 | | rv4_single_thread_bottleneck | главный поток + DX11-драйверный overhead: 90–95% работы на одном потоке | GPU-апгрейд не лечит |
- `multithread_overhaul_2_20` | партия-11.md:238 | | multithread_overhaul_2_20 | **патч 2.20 (06.2025, Dedmen OPREP)**: замена Fork-Join job system (со времён Arma 2) на графовый Enfusion job system + корутины для извлечения параллельных кусков AI (scan/pathfinding) из синглтред-FSM; взрывы — lineIntersects параллельно с ping-pon…

## runtime_memory — 10

- `64bit_native_port_2005` | партия-02.md:36 | | 64bit_native_port_2005 | декабрь 2005: нативный 64-bit engine для Windows XP Professional x64 | Не во всех сценах стабильнее 32-bit (Techgage) |
- `64bit_migration_2025` | партия-02.md:196 | | 64bit_migration_2025 | 18.02.2025 — переход на x64, обновлённый Source 2013 MP из TF2 | Старая кодовая база |
- `soul_memory_matchmaking` | партия-03.md:84 | | soul_memory_matchmaking | matchmaking по общему количеству собранных souls | Сложная балансировка при soul-farming |
- `ship_power_allocation` | партия-05.md:242 | | ship_power_allocation | система распределения энергии в бою | Доп. UI/AI |
- `pentagram_powerups` | партия-07.md:34 | | pentagram_powerups | pickup на основе классической Doom-механики | Контент-дизайн |
- `1gb_texture_data_85k_shaders` | партия-08.md:40 | | 1gb_texture_data_85k_shaders | 1 ГБ текстур + 85,000 шейдеров | Память |
- `4gb_gddr3_pc_recommended` | партия-08.md:115 | | 4gb_gddr3_pc_recommended | Crytek рекомендовала 4 GB RAM (DDR3) | Дорого |
- `java_gc_stutter_early` | партия-11.md:130 | | java_gc_stutter_early | ранние версии: Java GC-паузы + single-thread чанки → просадки на слабом железе | Родовая боль Java |
- `x64_1_68_memory_unbottleneck` | партия-11.md:236 | | x64_1_68_memory_unbottleneck | **патч 1.68 (03.2017): 64-bit executables** — снятие 2–3 ГБ лимита, кэш больших дистанций, меньше OOM | Слом драйверного переключения GPU (iGPU vs discrete) |
- `32bit_deprecation_2_20` | партия-11.md:241 | | 32bit_deprecation_2_20 | 2.20 — последний релиз с 32-bit (frozen legacy branch, без MP-совместимости); дроп Win7/8 | Отсечение легаси |

## runtime_security — 4

- `steam_required_drm` | партия-02.md:40 | | steam_required_drm | retail-копии требовали Steam-активацию — скандал 2004 | Потеря offline-игры при проблемах со Steam |
- `valve_anti_cheat` | партия-02.md:377 | | valve_anti_cheat | VAC — серверная защита от читов | Evasion-гонка вооружений |
- `trust_factor_2017` | партия-02.md:379 | | trust_factor_2017 | комбинация in-game и Steam-активности для оценки поведения | Сложный ML |
- `rockstar_launcher_required` | партия-06.md:234 | | rockstar_launcher_required | требуется Launcher | DRM |

## save_system — 3

- `bonfire_checkpoint_system` | партия-03.md:27 | | bonfire_checkpoint_system | костёр = checkpoint + restore + level-up + respawn врагов | Дисциплина левел-дизайна (точки размещения) |
- `sites_of_grace_checkpoints` | партия-03.md:240 | | sites_of_grace_checkpoints | Site of Grace вместо bonfire, плюс Stakes of Marika (опциональные respawn у места смерти) | Переработка respawn-логики |
- `save_only_at_beds_or_saves` | партия-10.md:194 | | save_only_at_beds_or_saves | сохранение только в кроватях или save (controversial) | Дороже UI |

## split_screen_rendering — 3

- `60hz_optional_oculus_rift_dev_kit` | партия-07.md:157 | | 60hz_optional_oculus_rift_dev_kit | оригинальная версия для Oculus Rift DK1 | Удороажние VR |
- `hrtf_audio_oculus_2` | партия-08.md:107 | | hrtf_audio_oculus_2 | HRTF audio для позиционного звука | Дороже audio |
- `stereo_3d_support` | партия-08.md:108 | | stereo_3d_support | native stereoscopic 3D на PC/PS3 | Дороже pipeline |

## upscaling_frame_generation — 5

- `ubersampling_supersampling_4x` | партия-01.md:342 | | ubersampling_supersampling_4x | Ubersampling = 4x SSAA с пересчётом освещения для каждого субпикселя (extreme supersampling), обрушивал fps на топ-GPU 2011 (GTX 590 ниже 30 fps) | Полная стоимость рендера × 4 на GPU |
- `locked_dlss_controversy` | партия-05.md:259 | | locked_dlss_controversy | на старте нет DLSS — только AMD FSR | Скандал (анти-конкурент) |
- `nvidia_dlss_added_2025` | партия-06.md:104 | | nvidia_dlss_added_2025 | апдейт марта 2025 — DLSS для PC | Vendor support |
- `dlss_deep_learning_super_sampling` | партия-09.md:162 | | dlss_deep_learning_super_sampling | DLSS upscaling (только RTX) | Vendor-specific |
- `global_illumination_dlss` | партия-10.md:46 | | global_illumination_dlss | DLSS + GI на Enhanced Edition | Vendor-specific |

## vehicle_simulation — 4

- `realistic_car_physics` | партия-06.md:25 | | realistic_car_physics | более реалистичная физика автомобилей (vs GTA SA) | Игроки жаловались на управление |
- `flight_simulation_models` | партия-06.md:94 | | flight_simulation_models | самолёты, вертолёты, парашюты | Доп. физика |
- `dynamic_horse_realtime` | партия-06.md:172 | | dynamic_horse_realtime | лошади реагируют в реальном времени | Доп. physics |
- `vehicle_combat_rework` | партия-11.md:30 | | vehicle_combat_rework | стрельба из машин, quickhack в движении | Доп. анимации |

## volumetric_effects — 20

- `wet_surfaces_fog` | партия-02.md:249 | | wet_surfaces_fog | визуальные эффекты воды и тумана для атмосферы | Shader cost |
- `day_night_cycle_paris` | партия-04.md:33 | | day_night_cycle_paris | 24-часовой цикл в большом городе | Стоимость симуляции NPC |
- `weather_time_anomalies` | партия-04.md:35 | | weather_time_anomalies | путешествие во времени через разные эпохи | Требует отдельных уровней |
- `day_night_doesnt_affect_mission` | партия-04.md:215 | | day_night_doesnt_affect_mission | time-of-day не блокирует миссии (vs Unity) | Упрощение прогрессии |
- `snow_ash_weather_volumetric` | партия-05.md:29 | | snow_ash_weather_volumetric | первый в серии с продвинутыми погодными эффектами | Удвоенный workload |
- `dynamic_lighting_snowfall` | партия-05.md:30 | | dynamic_lighting_snowfall | снег динамически рендерится, не текстура | GPU cost |
- `volumetric_lighting_nvidia` | партия-05.md:111 | | volumetric_lighting_nvidia | NVIDIA Volumetric Lighting (gameworks) | Vendor lock-in |
- `height_fog_dynamic` | партия-05.md:113 | | height_fog_dynamic | динамический туман | Удобство в мире |
- `dynamic_weather_day_night` | партия-06.md:152 | | dynamic_weather_day_night | полный цикл день/ночь + погода | Доп. overhead |
- `ambient_weather_lighting` | партия-06.md:164 | | ambient_weather_lighting | молнии, туман, дождь, снег динамически | Доп. cost |
- `volumetric_lighting_volumetric_fog` | партия-08.md:29 | | volumetric_lighting_volumetric_fog | volumetric lighting + volumetric fog (пионер) | Удороажние cost |
- `dynamic_weather_volumetric` | партия-09.md:33 | | dynamic_weather_volumetric | объёмные облака и погода | Удороажние |
- `volumetrics_indoor_outdoor` | партия-09.md:42 | | volumetrics_indoor_outdoor | volumetric lighting (HDR volumetric) | Удороажние |
- `dynamic_weather_dust_storm` | партия-09.md:102 | | dynamic_weather_dust_storm | динамическая погода (песчаные бури на Sinai) | Дороже эффектов |
- `extreme_weather_tornado_sandstorm` | партия-09.md:230 | | extreme_weather_tornado_sandstorm | экстремальная погода (торнадо, песчаные бури) | Дороже physics |
- `weather_affects_gameplay` | партия-09.md:241 | | weather_affects_gameplay | погода влияет на геймплей (торнадо поднимает технику) | Дороже physics |
- `weather_time_dynamic_weather` | партия-10.md:32 | | weather_time_dynamic_weather | цикл день/ночь + динамическая погода | Дороже physics |
- `realistic_dynamic_weather_storms` | партия-10.md:44 | | realistic_dynamic_weather_storms | песчаные бури, дождь, снег | Дороже physics |
- `city_xploration_day_night` | партия-10.md:117 | | city_xploration_day_night | NPC поведение меняется днём/ночью | Дороже AI |
- `night_cycle_full` | партия-10.md:200 | | night_cycle_full | полный цикл день/ночь (1:3) | Дороже AI |

## water_simulation — 3

- `houdini_water_flow_maps` | партия-02.md:313 | | houdini_water_flow_maps | созданы для Swamp Fever кампании, переиспользованы в Portal 2 | Pipeline cost |
- `underwater_exploration_first_time` | партия-04.md:93 | | underwater_exploration_first_time | первое подводное плавание в серии со времён Black Flag | Доп. cost |
- `water_surface_flow` | партия-05.md:32 | | water_surface_flow | течение воды через surface maps | Удороажние Houdini pipeline |
