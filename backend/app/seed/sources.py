"""Реестр подтверждённых источников.

Каждая запись проверена на доступность (HTTP 200). Методы и функции базы знаний
ссылаются на источники по ключу, что исключает дублирование URL и появление
непроверенных ссылок в опубликованных материалах.
"""

SOURCES: dict[str, dict[str, str]] = {
    # --- Unreal Engine -------------------------------------------------
    "UE_NANITE": {
        "title": "Unreal Engine: Nanite Virtualized Geometry",
        "url": "https://dev.epicgames.com/documentation/en-us/unreal-engine/nanite-virtualized-geometry-in-unreal-engine",
        "date": "2025-01-01",
    },
    "UE_LUMEN": {
        "title": "Unreal Engine: Lumen Global Illumination and Reflections",
        "url": "https://dev.epicgames.com/documentation/en-us/unreal-engine/lumen-global-illumination-and-reflections-in-unreal-engine",
        "date": "2025-01-01",
    },
    "UE_WORLDPARTITION": {
        "title": "Unreal Engine: World Partition",
        "url": "https://dev.epicgames.com/documentation/en-us/unreal-engine/world-partition-in-unreal-engine",
        "date": "2025-01-01",
    },
    "UE_VSM": {
        "title": "Unreal Engine: Virtual Shadow Maps",
        "url": "https://dev.epicgames.com/documentation/en-us/unreal-engine/virtual-shadow-maps-in-unreal-engine",
        "date": "2025-01-01",
    },
    "UE_NIAGARA": {
        "title": "Unreal Engine: Niagara Visual Effects",
        "url": "https://dev.epicgames.com/documentation/en-us/unreal-engine/niagara-visual-effects-in-unreal-engine",
        "date": "2025-01-01",
    },
    "UE_CHAOS": {
        "title": "Unreal Engine: Chaos Physics",
        "url": "https://dev.epicgames.com/documentation/en-us/unreal-engine/chaos-physics-in-unreal-engine",
        "date": "2025-01-01",
    },
    "UE_HLOD": {
        "title": "Unreal Engine: Hierarchical Level of Detail",
        "url": "https://dev.epicgames.com/documentation/en-us/unreal-engine/hierarchical-level-of-detail-in-unreal-engine",
        "date": "2025-01-01",
    },
    "UE_VIRTUALTEXTURING": {
        "title": "Unreal Engine: Virtual Texturing",
        "url": "https://dev.epicgames.com/documentation/en-us/unreal-engine/virtual-texturing-in-unreal-engine",
        "date": "2025-01-01",
    },
    "UE_INSIGHTS": {
        "title": "Unreal Engine: Unreal Insights",
        "url": "https://dev.epicgames.com/documentation/en-us/unreal-engine/unreal-insights-in-unreal-engine",
        "date": "2025-01-01",
    },
    "UE_NAVMESH": {
        "title": "Unreal Engine: Navigation Mesh",
        "url": "https://dev.epicgames.com/documentation/en-us/unreal-engine/navigation-mesh-in-unreal-engine",
        "date": "2025-01-01",
    },
    "UE_NETWORKING": {
        "title": "Unreal Engine: Networking and Multiplayer",
        "url": "https://dev.epicgames.com/documentation/en-us/unreal-engine/networking-and-multiplayer-in-unreal-engine",
        "date": "2025-01-01",
    },
    "UE_LWC": {
        "title": "Unreal Engine: Large World Coordinates",
        "url": "https://dev.epicgames.com/documentation/en-us/unreal-engine/large-world-coordinates-in-unreal-engine",
        "date": "2025-01-01",
    },
    "UE_SIGNIFICANCE": {
        "title": "Unreal Engine: Significance Manager",
        "url": "https://dev.epicgames.com/documentation/en-us/unreal-engine/significance-manager-in-unreal-engine",
        "date": "2025-01-01",
    },
    "UE_ANIMBUDGET": {
        "title": "Unreal Engine: Animation Budget Allocator",
        "url": "https://dev.epicgames.com/documentation/en-us/unreal-engine/animation-budget-allocator-in-unreal-engine",
        "date": "2025-01-01",
    },
    "UE_ISM": {
        "title": "Unreal Engine: Instanced Static Mesh",
        "url": "https://dev.epicgames.com/documentation/en-us/unreal-engine/instanced-static-mesh-in-unreal-engine",
        "date": "2025-01-01",
    },
    "UE_REPGRAPH": {
        "title": "Unreal Engine: Replication Graph",
        "url": "https://dev.epicgames.com/documentation/en-us/unreal-engine/replication-graph-in-unreal-engine",
        "date": "2025-01-01",
    },
    "UE_MASS": {
        "title": "Unreal Engine: Mass Entity",
        "url": "https://dev.epicgames.com/documentation/en-us/unreal-engine/mass-entity-in-unreal-engine",
        "date": "2025-01-01",
    },
    "UE_LOD": {
        "title": "Unreal Engine: Level of Detail",
        "url": "https://dev.epicgames.com/documentation/en-us/unreal-engine/level-of-detail-in-unreal-engine",
        "date": "2025-01-01",
    },
    "UE_SCALABILITY": {
        "title": "Unreal Engine: Scalability Reference",
        "url": "https://dev.epicgames.com/documentation/en-us/unreal-engine/scalability-in-unreal-engine",
        "date": "2025-01-01",
    },
    # --- Unity ---------------------------------------------------------
    "UNITY_OCCLUSION": {
        "title": "Unity Manual: Occlusion Culling",
        "url": "https://docs.unity3d.com/Manual/OcclusionCulling.html",
        "date": "2025-01-01",
    },
    "UNITY_INSTANCING": {
        "title": "Unity Manual: GPU Instancing",
        "url": "https://docs.unity3d.com/Manual/GPUInstancing.html",
        "date": "2025-01-01",
    },
    "UNITY_LIGHTPROBES": {
        "title": "Unity Manual: Light Probes",
        "url": "https://docs.unity3d.com/Manual/LightProbes.html",
        "date": "2025-01-01",
    },
    "UNITY_LIGHTMAPUV": {
        "title": "Unity Manual: Generating Lightmapping UVs",
        "url": "https://docs.unity3d.com/Manual/LightingGiUvs-GeneratingLightmappingUVs.html",
        "date": "2025-01-01",
    },
    "UNITY_JOBS": {
        "title": "Unity Manual: Job System",
        "url": "https://docs.unity3d.com/Manual/JobSystem.html",
        "date": "2025-01-01",
    },
    "UNITY_QUALITY": {
        "title": "Unity Manual: Quality Settings",
        "url": "https://docs.unity3d.com/Manual/class-QualitySettings.html",
        "date": "2025-01-01",
    },
    "UNITY_GFX_PERF": {
        "title": "Unity Manual: Optimizing Graphics Performance",
        "url": "https://docs.unity3d.com/Manual/OptimizingGraphicsPerformance.html",
        "date": "2025-01-01",
    },
    "UNITY_ADDRESSABLES": {
        "title": "Unity Manual: Addressables",
        "url": "https://docs.unity3d.com/Manual/com.unity.addressables.html",
        "date": "2025-01-01",
    },
    "UNITY_PROFILER": {
        "title": "Unity Manual: Profiler",
        "url": "https://docs.unity3d.com/Manual/Profiler.html",
        "date": "2025-01-01",
    },
    "UNITY_TEXTURE_STREAMING": {
        "title": "Unity Manual: Texture Streaming",
        "url": "https://docs.unity3d.com/Manual/TextureStreaming.html",
        "date": "2025-01-01",
    },
    "UNITY_SRP_BATCHER": {
        "title": "Unity Manual: SRP Batcher",
        "url": "https://docs.unity3d.com/Manual/SRPBatcher.html",
        "date": "2025-01-01",
    },
    "UNITY_ENTITIES": {
        "title": "Unity Manual: Entities (DOTS)",
        "url": "https://docs.unity3d.com/Packages/com.unity.entities@1.0/manual/index.html",
        "date": "2025-01-01",
    },
    "UNITY_NETCODE": {
        "title": "Unity Manual: Netcode",
        "url": "https://docs.unity3d.com/Packages/com.unity.netcode@1.0/manual/index.html",
        "date": "2025-01-01",
    },
    "UNITY_LIGHTMAPPER": {
        "title": "Unity Manual: Progressive Lightmapper",
        "url": "https://docs.unity3d.com/Manual/progressive-lightmapper.html",
        "date": "2025-01-01",
    },
    "UNITY_DRAW_CALLS": {
        "title": "Unity Manual: Choose a method for optimizing draw calls",
        "url": "https://docs.unity3d.com/Manual/optimizing-draw-calls-choose-method.html",
        "date": "2025-01-01",
    },
    # --- Godot ---------------------------------------------------------
    "GODOT_PERF": {
        "title": "Godot Docs: Optimizing 3D Performance",
        "url": "https://docs.godotengine.org/en/stable/tutorials/performance/optimizing_3d_performance.html",
        "date": "2025-01-01",
    },
    "GODOT_OCCLUSION": {
        "title": "Godot Docs: Occlusion Culling",
        "url": "https://docs.godotengine.org/en/stable/tutorials/3d/occlusion_culling.html",
        "date": "2025-01-01",
    },
    "GODOT_LIGHTS": {
        "title": "Godot Docs: Lights and Shadows",
        "url": "https://docs.godotengine.org/en/stable/tutorials/3d/lights_and_shadows.html",
        "date": "2025-01-01",
    },
    "GODOT_DECALS": {
        "title": "Godot Docs: Using Decals",
        "url": "https://docs.godotengine.org/en/stable/tutorials/3d/using_decals.html",
        "date": "2025-01-01",
    },
    "GODOT_THREADS": {
        "title": "Godot Docs: Using Multiple Threads",
        "url": "https://docs.godotengine.org/en/stable/tutorials/performance/using_multiple_threads.html",
        "date": "2025-01-01",
    },
    "GODOT_PHYSICS": {
        "title": "Godot Docs: Physics Introduction",
        "url": "https://docs.godotengine.org/en/stable/tutorials/physics/physics_introduction.html",
        "date": "2025-01-01",
    },
    "GODOT_MULTIPLAYER": {
        "title": "Godot Docs: High-level Multiplayer",
        "url": "https://docs.godotengine.org/en/stable/tutorials/networking/high_level_multiplayer.html",
        "date": "2025-01-01",
    },
    "GODOT_PARTICLES": {
        "title": "Godot Docs: 3D Particles",
        "url": "https://docs.godotengine.org/en/stable/tutorials/3d/particles/index.html",
        "date": "2025-01-01",
    },
    "GODOT_MULTIMESH": {
        "title": "Godot Docs: MultiMeshInstance3D",
        "url": "https://docs.godotengine.org/en/stable/classes/class_multimeshinstance3d.html",
        "date": "2025-01-01",
    },
    "GODOT_MESHLOD": {
        "title": "Godot Docs: Mesh Level of Detail",
        "url": "https://docs.godotengine.org/en/stable/tutorials/3d/mesh_lod.html",
        "date": "2025-01-01",
    },
    # --- Общие справочные материалы ------------------------------------
    "WIKI_LOD": {
        "title": "Level of detail (computer graphics)",
        "url": "https://en.wikipedia.org/wiki/Level_of_detail_(computer_graphics)",
        "date": "2025-01-01",
    },
    "WIKI_HSR": {
        "title": "Hidden-surface determination",
        "url": "https://en.wikipedia.org/wiki/Hidden-surface_determination",
        "date": "2025-01-01",
    },
    "WIKI_SHADOWMAP": {
        "title": "Shadow mapping",
        "url": "https://en.wikipedia.org/wiki/Shadow_mapping",
        "date": "2025-01-01",
    },
    "WIKI_BVH": {
        "title": "Bounding volume hierarchy",
        "url": "https://en.wikipedia.org/wiki/Bounding_volume_hierarchy",
        "date": "2025-01-01",
    },
    "WIKI_PARTICLES": {
        "title": "Particle system",
        "url": "https://en.wikipedia.org/wiki/Particle_system",
        "date": "2025-01-01",
    },
    "WIKI_MIPMAP": {
        "title": "Mipmap",
        "url": "https://en.wikipedia.org/wiki/Mipmap",
        "date": "2025-01-01",
    },
    "WIKI_ATLAS": {
        "title": "Texture atlas",
        "url": "https://en.wikipedia.org/wiki/Texture_atlas",
        "date": "2025-01-01",
    },
    "WIKI_NAVMESH": {
        "title": "Navigation mesh",
        "url": "https://en.wikipedia.org/wiki/Navigation_mesh",
        "date": "2025-01-01",
    },
    "WIKI_OBJECTPOOL": {
        "title": "Object pool pattern",
        "url": "https://en.wikipedia.org/wiki/Object_pool_pattern",
        "date": "2025-01-01",
    },
    "WIKI_SVO": {
        "title": "Sparse voxel octree",
        "url": "https://en.wikipedia.org/wiki/Sparse_voxel_octree",
        "date": "2025-01-01",
    },
    "WIKI_SDF": {
        "title": "Signed distance function",
        "url": "https://en.wikipedia.org/wiki/Signed_distance_function",
        "date": "2025-01-01",
    },
    "WIKI_DEFERRED": {
        "title": "Deferred shading",
        "url": "https://en.wikipedia.org/wiki/Deferred_shading",
        "date": "2025-01-01",
    },
    "CLUSTERED_SHADING": {
        "title": "Clustered Deferred and Forward Shading (Olsson, Billeter, Assarsson)",
        "url": "https://www.cse.chalmers.se/~uffe/clustered_shading_preprint.pdf",
        "date": "2012-01-01",
    },
    "WIKI_TAA": {
        "title": "Temporal anti-aliasing",
        "url": "https://en.wikipedia.org/wiki/Temporal_anti-aliasing",
        "date": "2025-01-01",
    },
    "WIKI_FFT": {
        "title": "Fast Fourier transform",
        "url": "https://en.wikipedia.org/wiki/Fast_Fourier_transform",
        "date": "2025-01-01",
    },
    "WIKI_GERSTNER": {
        "title": "Gerstner wave",
        "url": "https://en.wikipedia.org/wiki/Gerstner_wave",
        "date": "2025-01-01",
    },
    "WIKI_RAGDOLL": {
        "title": "Ragdoll physics",
        "url": "https://en.wikipedia.org/wiki/Ragdoll_physics",
        "date": "2025-01-01",
    },
    "WIKI_IK": {
        "title": "Inverse kinematics",
        "url": "https://en.wikipedia.org/wiki/Inverse_kinematics",
        "date": "2025-01-01",
    },
    "WIKI_SKINNING": {
        "title": "Skinning",
        "url": "https://en.wikipedia.org/wiki/Skinning",
        "date": "2025-01-01",
    },
    "WIKI_ECS": {
        "title": "Entity component system",
        "url": "https://en.wikipedia.org/wiki/Entity_component_system",
        "date": "2025-01-01",
    },
    "WIKI_DOD": {
        "title": "Data-oriented design",
        "url": "https://en.wikipedia.org/wiki/Data-oriented_design",
        "date": "2025-01-01",
    },
    # --- Проверенные практические источники (книги, библиотеки) -----------
    "GPP_OBJECTPOOL": {
        "title": "Game Programming Patterns: Object Pool",
        "url": "https://gameprogrammingpatterns.com/object-pool.html",
        "date": "2025-01-01",
    },
    "GPP_DATALOCALITY": {
        "title": "Game Programming Patterns: Data Locality",
        "url": "https://gameprogrammingpatterns.com/data-locality.html",
        "date": "2025-01-01",
    },
    "MESHOPT": {
        "title": "meshoptimizer: mesh optimization library",
        "url": "https://github.com/zeux/meshoptimizer",
        "date": "2025-01-01",
    },
    "WIKI_LIGHTMAP": {
        "title": "Lightmap",
        "url": "https://en.wikipedia.org/wiki/Lightmap",
        "date": "2025-01-01",
    },
    "WIKI_AO": {
        "title": "Ambient occlusion",
        "url": "https://en.wikipedia.org/wiki/Ambient_occlusion",
        "date": "2025-01-01",
    },
    "WIKI_DLSS": {
        "title": "Deep learning super sampling",
        "url": "https://en.wikipedia.org/wiki/Deep_learning_super_sampling",
        "date": "2025-01-01",
    },
    "WIKI_FSR": {
        "title": "FidelityFX Super Resolution",
        "url": "https://en.wikipedia.org/wiki/FidelityFX_Super_Resolution",
        "date": "2025-01-01",
    },
    "WIKI_IMPOSTOR": {
        "title": "Impostor (computer graphics)",
        "url": "https://en.wikipedia.org/wiki/Impostor_(computer_graphics)",
        "date": "2025-01-01",
    },
    "WIKI_PREDICTION": {
        "title": "Client-side prediction",
        "url": "https://en.wikipedia.org/wiki/Client-side_prediction",
        "date": "2025-01-01",
    },
    "WIKI_DELTA": {
        "title": "Delta encoding",
        "url": "https://en.wikipedia.org/wiki/Delta_encoding",
        "date": "2025-01-01",
    },
    "WIKI_VOLUMETRIC": {
        "title": "Volumetric rendering",
        "url": "https://en.wikipedia.org/wiki/Volumetric_rendering",
        "date": "2025-01-01",
    },
    # --- Альтернативные методы Треков 1–2 (ключи из исследований) -----------
    "UNITY_SHADERLOAD": {
        "title": "Unity Manual: Optimizing Shader Load Time",
        "url": "https://docs.unity3d.com/Manual/ShaderLoadTimeOptimization.html",
        "date": "2025-01-01",
    },
    "HUNT_AUDIO": {
        "title": "Hunt: Showdown — Audio readability, realism and consistency",
        "url": "https://www.huntshowdown.com/news/hunt-audio-readability-realism-and-consistency",
        "date": "2024-01-01",
    },
    "DOOM_ETERNAL": {
        "title": "Rendering the Hellscape of Doom Eternal (SIGGRAPH 2020)",
        "url": "https://advances.realtimerendering.com/s2020/RenderingDoomEternal.pdf",
        "date": "2020-08-25",
    },
    "GAFFER_TIMESTEP": {
        "title": "Fix Your Timestep! (Gaffer on Games)",
        "url": "https://gafferongames.com/post/fix_your_timestep/",
        "date": "2025-01-01",
    },
    "DF_ITTakesTWO": {
        "title": "It Takes Two tech analysis (Digital Foundry)",
        "url": "https://www.digitalfoundry.net/articles/digitalfoundry-2021-it-takes-two-tech-analysis",
        "date": "2021-03-27",
    },
    "COENEN_DOOM": {
        "title": "Doom Eternal graphics study (Simon Coenen)",
        "url": "https://www.simoncoenen.com/blog/programming/graphics/DoomEternalStudy",
        "date": "2024-01-01",
    },
    "RIOT_TICK": {
        "title": "Valorant 128-tick servers (Riot Engineering)",
        "url": "https://technology.riotgames.com/news/valorants-128-tick-servers",
        "date": "2020-04-16",
    },
}


def src(key: str | None) -> dict[str, str]:
    """Вернуть словарь источника по ключу (или пустой источник)."""
    if not key or key not in SOURCES:
        return {"title": "", "url": "", "date": ""}
    return SOURCES[key]
