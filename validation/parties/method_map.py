"""Сопоставление инженерных решений из партий с методами каталога DSS.

Ключи — коды методов каталога (111 штук). Значения — список подстрок (в нижнем
регистре), которые ищутся в конкатенации «код решения + описание реализации».
Совпадение хотя бы одной подстроки считается реализацией метода в игре.
"""

from __future__ import annotations

# код метода каталога -> ключевые слова (англ. коды решений партий + русские описания)
KEYWORDS: dict[str, list[str]] = {
    # --- advanced_npc_ai ---
    "behaviour_tree_update_budget": [
        "behaviour_tree", "behavior_tree", "дерев", "ai_update_budget", "ai_budget",
        "ai_director", "ai_subsystem", "npc_ai", "ai_tick", "ai_lod", "ai_update",
    ],
    "npc_perception_budget": [
        "perception", "восприят", "зрени", "npc_dynamic_ai", "social_aug", "мимик",
        "npc_daily_routine", "расписание дня", "npc_responses", "sight",
    ],
    # --- ai_pathfinding ---
    "flow_field_pathing": ["flow_field", "flowfield", "поле потоков"],
    "navmesh_tiling_streaming": [
        "navmesh", "nav_mesh", "навигац", "navigation_mesh", "hex_grid_pathfinding",
    ],
    "rvo_local_avoidance": [
        "rvo", "local_avoidance", "avoidance", "уклонен", "расхожден", "crowd_avoid",
    ],
    "time_sliced_pathfinding": [
        "time_sliced", "time-sliced", "pathfinding", "поиск пути", "a_star", "astar",
        "path_find", " multithread.*path", "pathfinding_budget",
    ],
    # --- art_pipeline ---
    "art_direction_stylization": [
        "styliz", "стилизац", "art_direction", "cel_shading", "мультяш", "комикс",
        "trompe", "painterly",
    ],
    "normal_bake_retopology_pipeline": [
        "retopolog", "normal_bake", "bake_normal", "normal_map", "репотоп", "lod_генерац",
    ],
    # --- audio_system ---
    "audio_occlusion_propagation": [
        "audio_occlusion", "occlusion_audio", "звук.*преград", "окклюз.*звук",
        "geometric_occluder", "аудиооккл", " звук.*закрыт",
    ],
    "audio_streaming_compression": [
        "audio_stream", "audio_compression", "аудиопоток", "audio_overhaul",
        "звук.*сжат", "rain_masks", "footstep", "шаги",
    ],
    # --- baked_lighting ---
    "gpu_lightmap_baking": ["gpu_lightmap", "lightmap.*gpu", "gpu.*bake", "запеч.*gpu"],
    "lightmap_2d_baking": ["lightmap_2d", "2d_lightmap", "lightmap.*2d"],
    "lightmap_atlas_baking": [
        "lightmap_atlas", "atlas_lightmap", "lightmap", "запечённ", "запеч",
        "baked_lighting", "light_map", "световые карты", "precombine", "previs",
        "precomputed", "baked_gi", "static_lighting", "baked_shadow",
    ],
    "lightmap_compression_streaming": [
        "lightmap_compression", "lightmap_stream", "сжат.*карт", "stream.*lightmap",
    ],
    # --- build_delivery ---
    "build_size_startup_budgets": [
        "build_size", "startup_budget", "размер сборки", "day_one_patch", "day-one",
        "патч.*релиз", "size_limit",
    ],
    "differential_patch_pipeline": [
        "differential_patch", "delta_patch", "дифференц", "инкрементальн.*патч",
        "vpk_packed", "vpk", "differential",
    ],
    # --- character_animation ---
    "animation_compression": [
        "animation_compression", "anim_compression", "сжат.*анимац", "анимац.*сжат",
    ],
    "animation_lod_budget": [
        "animation_lod", "anim_lod", "lod.*анимац", "анимац.*лод", "animation_budget",
    ],
    "gpu_skinning_compute": [
        "gpu_skinning", "compute_skinning", "скиннинг.*gpu", "gpu.*скин", "skinning",
    ],
    "motion_matching": [
        "motion_matching", "моушн", "motion_match", "freeflow_combat", "parkour",
        "паркур", "euphoria", "процедурн.*анимац",
    ],
    "skeletal_2d_deform": ["skeletal_2d", "2d_skeletal", "2d_deform"],
    "sprite_atlas_batching": ["sprite_atlas", "atlas_batching", "спрайт.*атлас"],
    "sprite_sheet_compression": ["sprite_sheet", "spritesheet", "спрайт.*лист"],
    # --- crowd_simulation ---
    "agent_update_budget": [
        "agent_update", "agent_budget", "агент.*бюджет", "crowd", "толп",
        "crowd_30000", "npc_update", "update_budget",
    ],
    "crowd_2d_instancing": ["crowd_2d", "2d_crowd", "инстанс.*2d"],
    "crowd_instancing_impostors": [
        "crowd_instancing", "impostor", "импостор", "crowd_imp", "billboard.*crowd",
    ],
    "ecs_data_oriented_crowd": [
        "ecs", "data_oriented", "ecs_determinism", "entity_system", "entity-driven",
        "data-oriented", "компонентн",
    ],
    # --- destruction_simulation ---
    "destruction_geometry_cache": [
        "destruction", "разруш", "geometry_cache", "разрушаем", "destruct",
        "levelution", "levolution", "battlefield.*разруш",
    ],
    # --- dynamic_global_illumination ---
    "hardware_raytraced_gi": [
        "rt_gi", "ray_traced_gi", "ray_traced_global", "rt_global", "гибридн.*rt",
        "rtx.*gi", "ddgi", "gi.*rt", " hardware_gi",
    ],
    "irradiance_volume_probes": [
        "irradiance", "light_probe", "probe_volume", "проб", "irradiance_volume",
    ],
    "screen_space_gi": ["screen_space_gi", "ssgi", "screen-space.*gi"],
    "sdf_global_illumination": ["sdf_gi", "sdf_global", "distance_field.*gi", "sdf.*gi"],
    "temporal_radiance_cache": [
        "temporal_radiance", "radiance_cache", "temporal.*gi", "временн.*gi",
        "temporal_cache",
    ],
    "voxel_cone_tracing": ["voxel_cone", "cone_tracing", "воксел.*gi", "voxel_gi"],
    # --- dynamic_lighting ---
    "dynamic_light_priority_budget": [
        "dynamic_light", "light_priority", "light_budget", "динамич.*свет",
        "light_limit", "fp16_hdr", "hdr_rendering", "hdr",
    ],
    "light_range_attenuation_lod": [
        "attenuation", "light_range", "дальност.*свет", "light_lod", "light_attenuation",
    ],
    # --- dynamic_shadows ---
    "cascaded_shadow_maps": [
        "cascaded_shadow", "csm", "каскадн.*тен", "shadow_cascad", "shadow_map",
        "теневые буферы",
    ],
    "distance_field_shadows": ["distance_field_shadow", "sdf_shadow", "df_shadow"],
    "screen_space_contact_shadows": [
        "contact_shadow", "screen_space_shadow", "sscs", "контактн.*тен",
    ],
    "shadow_caster_2d_limits": ["shadow_caster_2d", "2d_shadow"],
    "static_shadow_caching": [
        "static_shadow", "shadow_cach", "кэш.*тен", "shadow_cache", "cached_shadow",
    ],
    "virtual_shadow_maps": ["virtual_shadow", "vsm", "виртуальн.*тен"],
    # --- gameplay_ability_system ---
    "ability_visual_effect_budget": [
        "ability_visual", "effect_budget", "visual_effect_budget", "эффект.*бюджет",
        "particle_budget",
    ],
    "data_driven_ability_system": [
        "data_driven_ability", "gameplay_ability", "ability_system", "augmentation",
        "аугментац", "skill_tree", "perk", "hero_abilit", "способност",
    ],
    # --- geometry_pipeline ---
    "mesh_index_optimization": [
        "mesh_index", "index_optimization", "индекс.*оптим", "geometry_optimization",
        "mesh_optim", "lod_генерац", "lod_system", "lod",
    ],
    # --- large_scale_terrain ---
    "heightmap_compression": [
        "heightmap", "height_map", "карта высот", "terr.*сжат", "terrain_compression",
    ],
    "neural_texture_compression": [
        "neural_texture", "нейронн.*текстур", "ntc", "megatexture", "id_tech_5",
        "virtual_texture", "виртуальн.*текстур", "vt_maxppf", "streaming_texture",
    ],
    "terrain_clipmap": [
        "clipmap", "geo_clipmap", "террейн.*чанк", "terrain_chunk", "large_terrain",
        "terrain_streaming", "world_partition",
    ],
    "virtual_geometry_clusters": [
        "virtual_geometry", "nanite", "meshlet", "cluster_renderer", "виртуальн.*геометр",
        "mesh_shader", "меш-шейдер", "mesh_shaders_first", "gpu_meshlet",
    ],
    "virtual_texturing": [
        "virtual_textur", "виртуальн.*текстур", "texture_streaming", "потоков.*текстур",
        "megatexture", "mipmap_stream",
    ],
    # --- mesh_shaders ---
    "gpu_meshlet_culling_budget": [
        "meshlet_culling", "gpu_culling", "gpu_compute_culling", "отсечени.*gpu",
        "gpu_meshlet", "meshlet",
    ],
    "meshlet_pipeline_adoption": [
        "meshlet_pipeline", "mesh_shader", "meshlet", "меш-шейдер", "mesh_shaders_first",
        "primitive_shader",
    ],
    # --- multiplayer_netcode ---
    "client_prediction_reconciliation": [
        "client_prediction", "prediction", "предсказ", "rollback", "favor_the_shooter",
        "lag_compensation", "перемот", "rewind", "interpolat", "интерполяц",
    ],
    "delta_compression_state": [
        "delta_compression", "дельт.*сжат", "state_compression", "сжат.*состоян",
        "network_compression", "bit_packing",
    ],
    "deterministic_lockstep": [
        "lockstep", "determinism", "детермини", "deterministic_lockstep", "ecs_determinism",
        "fixed_tick", "rollback_netcode",
    ],
    "headless_dedicated_server": [
        "dedicated_server", "headless", "выделенн.*сервер", "dedicated_server_linux",
        "listen_server", "dedicated",
    ],
    "network_relevancy_priority": [
        "relevancy", "network_relevancy", "релевантн", "priority.*сеть", "network_priority",
        "distance_culling.*network", "interest",
    ],
    "tickrate_budgeting": [
        "tickrate", "tick_rate", "tic_rate", "тикрейт", "64_tick", "128_tick", "128tick",
        "64tick", "tick_63hz", "sub_tick", "subtick", "snapshot", "20_tick",
        "network_tick", "hz_tick", "10/30 hz", "10_hz", "30_hz", "sub-tick",
    ],
    # --- open_world_streaming ---
    "async_loading_pipeline": [
        "async_loading", "async_load", "асинхронн.*загруз", "loading_pipeline",
        "streaming_pipeline", "async_stream", "async", "потоков.*загруз",
    ],
    "baked_occlusion_culling": [
        "baked_occlusion", "occlusion_culling", "окклюз", "pvs", "previs", "precombine",
        "potentially_visible", "visibility",
    ],
    "gpu_compute_culling": [
        "gpu_culling", "compute_culling", "gpu.*отсечен", "culling.*gpu", "frustum_cull",
        "отсечени",
    ],
    "hierarchical_lod": [
        "hierarchical_lod", "hierarchical", "hlo", "lod_system", "lod_level", "lod",
        "уровн.*детал",
    ],
    "tilemap_chunk_streaming": [
        "tilemap_chunk", "chunk_streaming", "чанк", "chunk", "world_partition",
        "district", "zone_streaming", "terrain_streaming", "streaming.*чанк",
    ],
    "world_origin_shifting": [
        "origin_shift", "origin_shifting", "сдвиг.*начал", "floating_origin",
        "large_world_coordinate", "lwc", "64-bit.*координат", "32-bit.*координат",
    ],
    "world_partition_streaming": [
        "world_partition", "partition", "streaming.*zone", "seamless", "без швов",
        "streaming_volume", "redengine4_streaming", "open_world_streaming",
    ],
    # --- particle_systems ---
    "flipbook_particles": ["flipbook", "флипбук"],
    "gpu_particle_simulation": [
        "gpu_particle", "particle.*gpu", "частиц.*gpu", "physx.*частиц", "physx",
        "gpu.*частиц",
    ],
    "particle_pooling": ["particle_pool", "пул.*частиц", "pooling"],
    "sprite_particle_atlas": ["particle_atlas", "атлас.*частиц"],
    # --- path_tracing ---
    "full_path_tracing_pipeline": [
        "path_tracing", "path_tracer", "трассировк.*путе", "full_pt", "rt_overdrive",
        "path-tracing", "pt_mode",
    ],
    "path_tracing_sample_denoiser_budget": [
        "denoiser", "деноиз", "sample_budget", "denoise", "ray_reconstruction",
        "шумоподавл",
    ],
    # --- physics_simulation ---
    "broadphase_spatial_partitioning": [
        "broadphase", "spatial_partition", "spatial_hash", "пространственн.*разбиен",
        "collision_layer", "collision_matrix", "слои.*столкнов", "havok", "physx.*физик",
    ],
    "collision_layer_matrix": [
        "collision_layer", "layer_matrix", "collision_matrix", "слои.*столкнов",
        "collision_filter",
    ],
    "fixed_timestep_physics": [
        "fixed_timestep", "fixed_tick", "pstep", "p-step", "havok_30fps", "60fps_lock",
        "30fps_lock", "fps_lock", "fps_cap", "физическ.*шаг", "timestep",
        "дельта-тайм", "delta_time", "fixed_delta",
    ],
    "multithreaded_physics_jobs": [
        "multithread", "multi_thread", "multi-core", "multicore", "многопоточ",
        "job_system", "job_graph", "parallel", "параллельн", "thread", "поток.*cpu",
        "hyperthread", "smt", "core_count", "cpu_count",
    ],
    "physics_lod_sleeping": [
        "physics_lod", "sleep", "спящ", "physics_sleep", "ragdoll_lod", "lod.*физик",
    ],
    # --- post_processing ---
    "deferred_forward_plus_choice": [
        "deferred", "forward_plus", "forward+", "отложенн", "deferred_render",
        "forward_render", "deferred_forward", "hdr_rendering",
    ],
    "depth_prepass_early_z": [
        "depth_prepass", "early_z", "z_prepass", "prepass", "early-z", "z-prepass",
        "depth_only",
    ],
    "dynamic_resolution_scaling": [
        "dynamic_resolution", "dynamic_texture_scaling", "resolution_scal",
        "динамич.*разреш", "drs", "resolution_scale",
    ],
    "post_effect_selective": [
        "post_effect", "post_processing", "postprocess", "постобработ", "post_eff",
        "bloom", "dof", "боке", "motion_blur", "chromatic",
    ],
    "screenspace_light_shafts": [
        "light_shaft", "god_ray", "godray", "луч.*свет", "volumetric_light",
        "light_reveal", "lighting_reveal",
    ],
    "temporal_upscaling": [
        "temporal_upscal", "temporal_upscaling", "taa", "temporal_aa", "fsr", "dlss",
        "xess", "upscal", "апскейл", "temporal", "temporal_aa_", "supersampling",
        "ubersampling", "ssaa", "checkerboard", "reconstruction",
    ],
    "variable_rate_shading": [
        "variable_rate_shading", "vrs", "переменн.*шейдинг", "variable_rate",
    ],
    # --- procedural_terrain ---
    "chunked_procedural_terrain": [
        "procedural_terrain", "chunked_procedural", "procedural_generation",
        "процедурн.*генерац", "procgen", "voxel_chunk", "процедурн.*мир",
        "procedural_generat",
    ],
    "terrain_generation_streaming_budget": [
        "terrain_generation", "generation_streaming", "генерац.*поток",
        "generation_budget", "terrain_streaming", "world_generation",
    ],
    # --- procedural_vegetation ---
    "gpu_instancing_vegetation": [
        "gpu_instancing", "instanc", "инстанс", "vegetation", "растительн", "foliage",
        "дерев", "grass", "трав",
    ],
    "gpu_procedural_placement": [
        "procedural_placement", "процедурн.*размещ", "scatter", "placement",
    ],
    "impostors_billboards": ["impostor", "billboard", "билборд", "импостор"],
    "tilemap_layer_culling": ["tilemap_layer", "layer_culling", "tilemap"],
    "vegetation_atlas_lod": ["vegetation_atlas", "vegetation_lod", "атлас.*растит"],
    # --- project_architecture ---
    "composition_bootstrap_architecture": [
        "composition", "bootstrap", "composition_bootstrap", "entity_system",
        "ecs_", "модульн", "modular", "архитектур", "scripting_extension", "lua_scripting",
        "mod_api", "modd", "мод-поддерж", "sdk", "workshop", "editor", "редактор",
        "eden_editor", "plugin", "api",
    ],
    # --- ray_traced_effects ---
    "rt_effect_resolution_budget": [
        "rt_effect", "rt_resolution", "ray_traced_reflection", "rt_reflection",
        "rt_shadow", "rt_ao", "rtx", "rt_", "dxr", "ray_tracing", "трассировк",
        "rt_overdrive",
    ],
    "selective_ray_traced_effects": [
        "selective_ray", "selective_rt", "rt_effect", "ray_traced_effects",
        "reflection.*rt", "rt_reflection", "ray_tracing", "dxr", "rtx",
    ],
    # --- render_scalability ---
    "quality_tier_scalability": [
        "quality_tier", "scalability", "масштабир", "preset", "пресет", "quality_preset",
        "graphic_option", "настройк.*график", "low_medium_high", "quality_level",
    ],
    # --- rendering_architecture ---
    "bindless_uber_shaders": [
        "bindless", "uber_shader", "uber_shaders", "убер-шейдер", "descriptor",
        "shader_permut", "пермутац.*шейд", "shader_compil", "компиляц.*шейд",
        "pso_precach", "pso",
    ],
    "hiz_software_occlusion": [
        "hiz", "software_occlusion", "software_culling", "программн.*отсечени",
        "occlusion_query", "hzb",
    ],
    "pso_precaching_warmup": [
        "pso_precaching", "pso", "shader_warmup", "прогрев.*шейд", "precach",
        "shader_compil", "компиляц.*шейд", "eac_blocks_async_shader",
    ],
    "srp_batcher_discipline": [
        "srp_batcher", "batcher", "batching", "батчинг", "draw_call", "drawcall",
        "mat_queue", "draw_call_budget", "instanc",
    ],
    "tiled_clustered_light_culling": [
        "tiled_light", "clustered_light", "clustered", "tiled_clustered",
        "кластерн.*свет", "forward_plus", "light_culling",
    ],
    # --- runtime_memory ---
    "managed_gc_alloc_budget": [
        "gc_", "garbage", "сборк.*мусор", "alloc", "аллокац", "memory_pool", "пул.*памят",
        "java_gc", "zgc", "32-bit", "32bit", "x64", "64-bit", "64bit",
        "memory_limit", "vram_limit", "2-3 gb", "адресн.*пространств", "nomemrestrict",
        "memory_budget", "memory", "памят",
    ],
    # --- save_system ---
    "async_incremental_saves": [
        "async_save", "incremental_save", "асинхронн.*сохран", "autosave", "автосохран",
        "save_system", "сохранени",
    ],
    "snapshot_slot_saves": [
        "snapshot_save", "slot_save", "слот.*сохран", "save_slot", "save_only_at",
        "сохранени.*кроват", "save_scum",
    ],
    # --- split_screen_rendering ---
    "splitscreen_render_budget": [
        "splitscreen", "split_screen", "split-screen", "локальн.*мультиплеер",
        "local_multiplayer",
    ],
    # --- upscaling_frame_generation ---
    "ml_frame_generation": [
        "frame_generation", "frame_gen", "dlss_3", "dlss3", "fg_", "генерац.*кадр",
        "dlss 3", "fsr_3", "frame_generation", "ml_frame",
    ],
    # --- vehicle_simulation ---
    "raycast_vehicle_physics": [
        "raycast_vehicle", "vehicle_physics", "vehicle_simulation", " vehicle",
        "машин", "автомобил", "транспорт", "vehicle_combat", "horse_ai", "лошад",
        "mounted", "mount",
    ],
    "vehicle_simulation_lod": [
        "vehicle_lod", "vehicle_simulation_lod", "vehicle.*lod", "трафик",
        "traffic_density", "crowd_traffic",
    ],
    # --- volumetric_effects ---
    "froxel_volumetric_fog": [
        "froxel", "volumetric_fog", "volumetric", "объёмн", "объемн.*туман",
        "volumetric_smoke", "дым", "fog", "туман", "volumetric_cloud",
    ],
    "volumetric_half_resolution": [
        "half_resolution", "half-res", "половинн.*разреш", "volumetric.*half",
        "quarter_res",
    ],
    # --- water_simulation ---
    "gerstner_fft_water": [
        "gerstner", "fft_water", "water_simulation", " water", "вод", "ocean",
        "океан", "волн",
    ],
    "planar_reflection_budget": [
        "planar_reflection", "planar", "плоск.*отраж", "reflection", "отражени",
        "mirror", "зеркал", "screen_space_reflection", "ssr",
    ],
    "screen_space_water_simple": [
        "screen_space_water", "screen-space.*water", "water.*screen",
    ],
}


def match_methods(code: str, impl: str) -> list[str]:
    """Вернуть коды методов каталога, соответствующие решению из партии."""
    hay = f"{code} {impl}".lower()
    hits = []
    for mcode, kws in KEYWORDS.items():
        for kw in kws:
            if kw in hay:
                hits.append(mcode)
                break
    return hits
