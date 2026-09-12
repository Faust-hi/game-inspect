"""Seed-данные доказательного слоя.

Файл содержит небольшой, но разнородный набор зависимостей, а
реестр источников автоматически расширяется всеми ссылками, уже входящими в
каталог. Это позволяет не обещать полное исследование только по нескольким
демо: coverage в API показывает, какие claims ещё требуют ручной ревизии.
"""
from __future__ import annotations

import hashlib
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models.entities import (
    DependencyEdge, Engine, EngineTool, EvidenceClaim,
    EvidenceSource, GameFunction, HardwareCPU, HardwareGPU, Method, TechnologyNode,
)
from .sources import SOURCES

CHECKED_AT = "2026-09-10"

EXTRA_SOURCES: dict[str, dict[str, str]] = {
    "L4D_AI_DIRECTOR": {
        "title": "The AI Systems of Left 4 Dead",
        "url": "https://steamcdn-a.akamaihd.net/apps/valve/2009/ai_systems_of_l4d_mike_booth.pdf",
        "date": "2009-09-01", "publisher": "Valve", "source_type": "engineering_talk",
        "locator": "section: Adaptive Dramatic Pacing",
    },
    "CS2_SUBTICK": {
        "title": "Counter-Strike 2: Moving Beyond Tick Rate",
        "url": "https://www.counter-strike.net/cs2",
        "date": "2023-09-27", "publisher": "Valve", "source_type": "official_game_material",
        "locator": "section: Sub-tick updates",
    },
    "RIOT_NETCODE": {
        "title": "Peeking into VALORANT's Netcode",
        "url": "https://technology.riotgames.com/news/peeking-valorants-netcode",
        "date": "2020-04-16", "publisher": "Riot Games", "source_type": "engineering_article",
        "locator": "sections: peeker's advantage and simulation divergence",
    },
    "UNITY_DOTS_PRODUCTION": {
        "title": "Unity DOTS - Data-Oriented Technology Stack",
        "url": "https://unity.com/dots",
        "date": "2024", "publisher": "Unity Technologies", "source_type": "official_case_index",
        "locator": "section: DOTS in Production",
    },
    "UE_CITY_SAMPLE": {
        "title": "City Sample Project Unreal Engine Demonstration",
        "url": "https://dev.epicgames.com/documentation/en-us/unreal-engine/city-sample-project-unreal-engine-demonstration",
        "date": "n/a", "publisher": "Epic Games", "source_type": "official_case_study",
        "locator": "sections: World Partition, Nanite Virtualized Geometry, Mass AI",
    },
    "UE_CITY_SAMPLE_PCG": {
        "title": "City Sample PCG for Unreal Engine",
        "url": "https://dev.epicgames.com/documentation/en-us/unreal-engine/city-sample-pcg-for-unreal-engine?lang=en-US",
        # Обновляемая документация Epic даты публикации не объявляет; значение
        # приведено к `n/a`, как у соседней страницы City Sample. Прежняя дата
        # была датой проверки ссылки, а не публикации.
        "date": "n/a", "publisher": "Epic Games", "source_type": "official_documentation",
        "locator": "section: procedural city and PCG graph examples",
    },
    "HUNT_AUDIO_2025": {
        "title": "Dev Insight - A deep dive into 3D Audio in Hunt",
        "url": "https://www.huntshowdown.com/news/dev-insight-a-deep-dive-into-3d-audio-in-hunt",
        "date": "2025-05-09", "publisher": "Crytek", "source_type": "studio_engineering_article",
        "locator": "section: CrySpatial",
    },
    "UE_FEATURE_MATRIX": {
        "title": "Supported Features by Rendering Path for Desktop",
        "url": "https://dev.epicgames.com/documentation/en-us/unreal-engine/supported-features-by-rendering-path-for-desktop-with-unreal-engine",
        "date": "n/a", "publisher": "Epic Games", "source_type": "official_documentation",
        "locator": "table: Supported Features by Rendering Path",
    },
    # Книги и справочные издания. Сайт/каталог издателя является точкой
    # идентификации издания; claims должны дополнительно указывать главу или
    # раздел. Книга не превращает экспертный балл в измерение проекта.
    "BOOK_GAME_ENGINE_ARCHITECTURE": {
        "title": "Game Engine Architecture, Third Edition",
        "url": "https://www.gameenginebook.com/",
        "date": "2018-07-01", "version": "3rd edition",
        "authors": "Jason Gregory", "publisher": "CRC Press",
        "source_type": "book",
        "locator": "chapters 3-4, 16: engine architecture, runtime, resource systems",
    },
    "BOOK_REAL_TIME_RENDERING": {
        "title": "Real-Time Rendering, Fourth Edition",
        "url": "https://www.realtimerendering.com/",
        "date": "2018-08-01", "version": "4th edition",
        "authors": "Tomas Akenine-Moller; Eric Haines; Naty Hoffman",
        "publisher": "A K Peters/CRC Press", "source_type": "book",
        "locator": "chapters 2-3, 8: rendering pipeline, transformations, shadows",
    },
    "BOOK_GAME_PROGRAMMING_PATTERNS": {
        "title": "Game Programming Patterns",
        "url": "https://gameprogrammingpatterns.com/",
        "date": "2014-11-13", "version": "online edition",
        "authors": "Robert Nystrom", "publisher": "Genever Benning",
        "source_type": "book",
        "locator": "chapters: Data Locality, Object Pool, State",
    },
    "BOOK_GPU_GEMS_3": {
        "title": "GPU Gems 3: Programming Techniques for High-Performance Graphics",
        "url": "https://developer.nvidia.com/gpugems/gpugems3/",
        "date": "2007-08-01", "version": "GPU Gems 3",
        "authors": "NVIDIA contributors", "publisher": "NVIDIA",
        "source_type": "book",
        "locator": "chapters on volumetric lighting, shadows and post-processing",
    },
    "STANDARD_VULKAN_SPEC": {
        "title": "Vulkan 1.3 Extensions Specification",
        "url": "https://registry.khronos.org/vulkan/specs/1.3-extensions/html/",
        "date": "2022", "version": "1.3 extensions",
        "authors": "Khronos Vulkan Working Group", "publisher": "Khronos Group",
        "source_type": "standard",
        "locator": "chapters: device features, queues, synchronization",
    },
    # Исследовательские источники отчёта, которых нет в legacy-реестре
    # ссылок. Они заведены отдельными записями, чтобы каждый новый claim мог
    # ссылаться не только на URL в Markdown, но и на нормализованный источник
    # в API. Дата оставлена пустой там, где страница не фиксирует дату
    # публикации: отсутствие даты честнее, чем выдуманная точность.
    "RESEARCH_S23_PACKAGING": {
        "title": "Unreal Engine: Packaging Your Project",
        "url": "https://dev.epicgames.com/documentation/en-us/unreal-engine/packaging-your-project",
        "date": "n/a",
        "publisher": "Epic Games", "source_type": "official_documentation",
        "locator": "sections: Build, Cook, Stage, Package; Chunking",
        "platform": "Windows/Linux PC",
    },
    "RESEARCH_S24_HLOD": {
        "title": "Unreal Engine: World Partition HLOD",
        "url": "https://dev.epicgames.com/documentation/en-us/unreal-engine/world-partition---hierarchical-level-of-detail-in-unreal-engine",
        "date": "n/a",
        "publisher": "Epic Games", "source_type": "official_documentation",
        "locator": "sections: HLOD layers and proxy mesh methods",
        "platform": "Windows/Linux PC",
    },
    "RESEARCH_S25_PCG": {
        "title": "Using PCG with World Partition",
        "url": "https://dev.epicgames.com/documentation/en-us/unreal-engine/using-pcg-with-world-partition-in-unreal-engine?lang=en-US",
        "date": "n/a",
        "publisher": "Epic Games", "source_type": "official_documentation",
        "locator": "sections: PCG Data Layers and HLOD Layers",
        "platform": "Windows/Linux PC",
    },
    "RESEARCH_S27_RELEVANCY": {
        "title": "Unreal Engine: Actor Relevancy",
        "url": "https://dev.epicgames.com/documentation/en-us/unreal-engine/actor-relevancy-in-unreal-engine",
        "date": "n/a",
        "publisher": "Epic Games", "source_type": "official_documentation",
        "locator": "sections: actor relevancy and distance",
        "platform": "Windows/Linux PC",
    },
    "RESEARCH_S28_CRY_STREAMING": {
        "title": "CRYENGINE: Streaming System",
        "url": "https://www.cryengine.com/docs/static/engines/cryengine-5/categories/23756813/pages/23306430",
        "date": "n/a",
        "publisher": "Crytek", "source_type": "official_documentation",
        "locator": "sections: asynchronous reads, decompression and main-thread completion",
        "platform": "Windows PC",
    },
    "RESEARCH_S29_CRY_AUDIO": {
        "title": "CRYENGINE: Audio & Occlusion",
        "url": "https://www.cryengine.com/docs/static/engines/cryengine-5/categories/23756816/pages/44964914",
        "date": "n/a",
        "publisher": "Crytek", "source_type": "official_documentation",
        "locator": "sections: No Ray, SingleRay, MultipleRay and distance limits",
        "platform": "Windows PC",
    },
    "RESEARCH_S31_UNITY_JOB_OVERVIEW": {
        "title": "Unity Manual: Job System Overview",
        # Unity перенесла справочник 6000.x под /Documentation/Manual/; прежний
        # путь `6000.0/Manual/job-system-overview.html` отдаёт 404 (проверено
        # пробой), новый — 200. Замена адреса, а не источника.
        "url": "https://docs.unity3d.com/6000.0/Documentation/Manual/job-system-overview.html",
        "date": "n/a",
        "publisher": "Unity Technologies", "source_type": "official_documentation",
        "locator": "sections: worker threads, cores, work stealing and safety",
        "platform": "Windows/Linux PC",
    },
    "RESEARCH_S33_ISO_25010": {
        "title": "ISO/IEC 25010:2023 Product Quality Model",
        "url": "https://www.iso.org/standard/78176.html",
        "publisher": "ISO/IEC JTC 1/SC 7", "source_type": "standard",
        "date": "2023", "version": "2023",
        "locator": "product quality model and evaluation characteristics",
    },
    "RESEARCH_S34_ISO_20741": {
        "title": "ISO/IEC 20741:2017 Software Engineering Tool Evaluation",
        "url": "https://www.iso.org/obp/ui?_escaped_fragment_=iso%3Astd%3Aiso-iec%3A20741%3Aed-1%3Av1%3Aen",
        "publisher": "ISO/IEC JTC 1/SC 7", "source_type": "standard",
        "date": "2017", "version": "2017",
        "locator": "purpose-oriented tool selection and quality characteristics",
    },
    "RESEARCH_S35_PMI_PERT": {
        "title": "Practice Standard for Scheduling - Second Edition",
        "url": "https://www.pmi.org/-/media/pmi/documents/public/pdf/certifications/practice-standard-scheduling.pdf?v=c7ca2721-8c26-4e07-ba47-069d0987bc0c",
        "date": "2011",
        "publisher": "Project Management Institute", "source_type": "practice_standard",
        "locator": "three-point estimating: triangular and beta/PERT formulas",
    },
    "RESEARCH_S36_NASA_SCHEDULE": {
        "title": "Analytical Technique for Schedule Risk Assessment",
        "url": "https://ntrs.nasa.gov/api/citations/19870020777/downloads/19870020777.pdf",
        "publisher": "NASA", "source_type": "technical_report",
        "date": "1987",
        "locator": "PERT/CPM precedence network and critical path sections",
    },
    "RESEARCH_S37_AMDAHL": {
        "title": "Amdahl's Law & Parallel Speedup",
        "url": "https://www.usenix.org/legacy/publications/library/proceedings/als00/2000papers/papers/full_papers/brownrobert/brownrobert_html/node3.html",
        "publisher": "USENIX", "source_type": "conference_paper",
        "date": "2000",
        "locator": "serial/parallel speedup and overhead",
    },
    "RESEARCH_S38_D3D_FEATURE_LEVELS": {
        "title": "Direct3D Hardware Feature Levels",
        "url": "https://learn.microsoft.com/en-us/windows/win32/direct3d12/hardware-feature-levels",
        "date": "n/a",
        "publisher": "Microsoft", "source_type": "official_documentation",
        "locator": "feature-level functionality versus performance",
        "platform": "Windows PC",
    },
    "RESEARCH_S39_D3D_CHECK_FEATURE": {
        "title": "ID3D12Device::CheckFeatureSupport",
        "url": "https://learn.microsoft.com/en-us/windows/win32/api/d3d12/nf-d3d12-id3d12device-checkfeaturesupport",
        "date": "n/a",
        "publisher": "Microsoft", "source_type": "official_documentation",
        "locator": "syntax, remarks and ray-tracing capability query",
        "platform": "Windows PC",
    },
    "RESEARCH_S40_D3D_RT_TIER": {
        "title": "D3D12 Raytracing Tier",
        "url": "https://learn.microsoft.com/en-us/windows/win32/api/d3d12/ne-d3d12-d3d12_raytracing_tier",
        "date": "n/a",
        "publisher": "Microsoft", "source_type": "official_documentation",
        "locator": "ray-tracing tier capability",
        "platform": "Windows PC",
    },
    "RESEARCH_S41_UE_SPECS": {
        "title": "Hardware and Software Specifications for Unreal Engine",
        "url": "https://dev.epicgames.com/documentation/en-us/unreal-engine/hardware-and-software-specifications-for-unreal-engine",
        "date": "n/a",
        "publisher": "Epic Games", "source_type": "official_documentation",
        "locator": "editor requirements and rendering-path constraints",
        "platform": "Windows/Linux PC",
    },
    "RESEARCH_S42_RIOT_SCALABILITY": {
        "title": "VALORANT: Scalability and Load Testing",
        "url": "https://www.riotgames.com/en/news/scalability-and-load-testing-valorant",
        "date": "2020-12-15",
        "publisher": "Riot Games", "source_type": "studio_engineering",
        "locator": "sections: server scalability and 128-tick load test",
        "platform": "server",
    },
    "RESEARCH_S43_HAMMER": {
        "title": "Valve Hammer Editor / Source SDK",
        "url": "https://developer.valvesoftware.com/wiki/Valve_Hammer_Editor",
        "date": "n/a",
        "publisher": "Valve Developer Community", "source_type": "official_developer_resource",
        "locator": "branch-specific Hammer/Source SDK tooling",
    },
    "RESEARCH_S44_HEROENGINE_LEGACY": {
        "title": "HeroEngine Legacy",
        "url": "https://tgs.tech/solutions/heroengine-legacy",
        "date": "n/a",
        "publisher": "TGS Tech", "source_type": "studio_information",
        "locator": "legacy status and current applicability warning",
    },
    "RESEARCH_S45_HEROENGINE_VIDEOS": {
        "title": "HeroEngine Legacy Platform Videos",
        "url": "https://tgs.tech/apex-videos",
        "date": "n/a",
        "publisher": "TGS Tech", "source_type": "studio_engineering",
        "locator": "historical live collaboration and integration examples",
    },
    "RESEARCH_S46_UNITY_JOB_DEPENDENCIES": {
        "title": "Unity Job Dependencies",
        "url": "https://docs.unity3d.com/2023.2/Documentation/Manual/JobSystemJobDependencies.html",
        "date": "n/a",
        "publisher": "Unity Technologies", "source_type": "official_documentation",
        "locator": "job dependencies and synchronization",
        "platform": "Windows/Linux PC",
    },
    "RESEARCH_S49_PASSMARK_SINGLE": {
        "title": "PassMark CPU Single Thread Chart",
        "url": "https://www.cpubenchmark.net/singleThread.html",
        "date": "n/a",
        "publisher": "PassMark Software", "source_type": "benchmark",
        "locator": "single-thread comparison chart and notes",
        "platform": "Windows/Linux PC",
    },
    "RESEARCH_S50_PASSMARK_FAQ": {
        "title": "PassMark PerformanceTest FAQ",
        "url": "https://passmark.com/support/performancetest_faq/understanding-results.php",
        "date": "n/a",
        "publisher": "PassMark Software", "source_type": "benchmark_methodology",
        "locator": "benchmark limits and workload caveat",
        "platform": "Windows/Linux PC",
    },
    "RESEARCH_S51_3DMARK": {
        "title": "UL 3DMark",
        "url": "https://benchmarks.ul.com/3dmark",
        "date": "n/a",
        "publisher": "UL Solutions", "source_type": "benchmark",
        "locator": "GPU/CPU comparison and frame-rate context",
        "platform": "Windows PC",
    },
    "RESEARCH_S53_QUIC_RFC": {
        "title": "RFC 9000: QUIC",
        "url": "https://www.ietf.org/rfc/rfc9000.pdf",
        "publisher": "IETF", "source_type": "standard",
        "date": "2021-05-01", "version": "RFC 9000",
        "locator": "packet format and transport assumptions",
        "platform": "Windows/Linux PC",
    },
    "RESEARCH_S54_UE_TEXTURE_METRICS": {
        "title": "Unreal Engine: Texture Streaming Metrics",
        "url": "https://dev.epicgames.com/documentation/en-us/unreal-engine/texture-streaming-metrics-in-unreal-engine",
        "date": "n/a",
        "publisher": "Epic Games", "source_type": "official_documentation",
        "locator": "wanted mips, pool usage and streaming metrics",
        "platform": "Windows/Linux PC",
    },
    "RESEARCH_S55_UE_TEXTURE_CONFIG": {
        "title": "Unreal Engine: Texture Streaming Configuration",
        "url": "https://dev.epicgames.com/documentation/en-us/unreal-engine/texture-streaming-configuration",
        "date": "n/a",
        "publisher": "Epic Games", "source_type": "official_documentation",
        "locator": "pool sizing and update behavior",
        "platform": "Windows/Linux PC",
    },
    "RESEARCH_S57_NASA_GLOSSARY": {
        "title": "NASA PP&C Glossary: Critical Path and Double Counting",
        "url": "https://www.nasa.gov/ocfo/ppc-corner/ppc-glossary/",
        "date": "n/a",
        "publisher": "NASA", "source_type": "technical_guidance",
        "locator": "critical path, uncertainty and double-counting entries",
    },
    "RESEARCH_S58_UNITY_JOB_TROUBLESHOOTING": {
        "title": "Unity Job System Troubleshooting",
        "url": "https://docs.unity3d.com/es/2021.1/Manual/JobSystemTroubleshooting.html",
        "date": "n/a",
        "publisher": "Unity Technologies", "source_type": "official_documentation",
        "locator": "WaitForJobGroup and Complete synchronization",
        "platform": "Windows/Linux PC",
    },
}

SOURCE_LOCATORS = {
    "UE_WORLDPARTITION": "sections: World Partition, Streaming Sources",
    "UE_NANITE": "section: Nanite Virtualized Geometry overview",
    "UE_LUMEN": "section: Lumen Global Illumination and Reflections",
    "UE_VSM": "section: Virtual Shadow Maps",
    "UNITY_JOBS": "section: Job System overview",
    "UNITY_ADDRESSABLES": "section: Addressables overview",
    "UNITY_ENTITIES": "section: Entities overview",
    "UNITY_NETCODE": "section: Netcode for Entities overview",
    "GODOT_PERF": "section: Optimizing 3D Performance",
    "GODOT_MULTIPLAYER": "section: High-level multiplayer",
    "MS_VRS": "sections: Specifying Shading Rate, Feature Tiering",
    "MS_MESH_SHADER": "section: Required Support from the device",
    "DOOM_ETERNAL": "slides: geometry caches, gore, material compositing, target frame rate",
    "HUNT_AUDIO": "sections: Occlusion and Realism, Feedback and Readability",
    "RIOT_TICK": "section: 128-tick servers",
    "DF_ITTakesTWO": "section: split-screen rendering and performance analysis",
}


# Claims from the deep research cards and the worked examples in the report.
# The list deliberately contains both documented mechanisms and calculations
# derived from explicit inputs. A derived claim may have no external source:
# its formula and inputs are the reproducible provenance in that case.
RESEARCH_CLAIMS: list[dict[str, Any]] = [
    {
        "code": "research:world_partition_cells", "entity": "research", "entity_code": "world_streaming",
        "field": "mechanism", "claim": "World Partition divides a persistent level into grid cells that can be loaded and unloaded by streaming sources.",
        "source_code": "UE_WORLDPARTITION", "locator": "sections: World Partition, Streaming Sources",
        "basis": "documented", "verification_status": "verified", "evidence_level": "primary",
        "context": "Mechanism claim; the source does not provide a transferable FPS number.", "status": "published",
    },
    {
        "code": "research:world_partition_hlod", "entity": "research", "entity_code": "world_streaming",
        "field": "hlod", "claim": "World Partition HLOD can represent distant unloaded content with proxy meshes/materials and different proxy construction modes.",
        "source_code": "RESEARCH_S24_HLOD", "locator": "sections: HLOD layers and proxy mesh methods",
        "basis": "documented", "verification_status": "verified", "evidence_level": "primary",
        "context": "HLOD changes runtime representation and also adds cook/build and content-validation work.", "status": "published",
    },
    {
        "code": "research:rendering_feature_matrix", "entity": "research", "entity_code": "rendering_paths",
        "field": "capability", "claim": "Nanite, Virtual Shadow Maps and Lumen are constrained by the selected desktop rendering path, RHI and hardware/software capability.",
        "source_code": "UE_FEATURE_MATRIX", "locator": "table: Supported Features by Rendering Path",
        "basis": "documented", "verification_status": "verified", "evidence_level": "primary",
        "context": "Capability compatibility must be checked before a performance ranking.", "status": "published",
    },
    {
        "code": "research:d3d_feature_level_not_perf", "entity": "research", "entity_code": "hardware_capability",
        "field": "feature_level", "claim": "Direct3D feature levels describe supported functionality and are not a performance benchmark.",
        "source_code": "RESEARCH_S38_D3D_FEATURE_LEVELS", "locator": "feature-level functionality versus performance",
        "basis": "documented", "verification_status": "verified", "evidence_level": "primary",
        "context": "A compatible feature level does not imply a target FPS.", "status": "published",
    },
    {
        "code": "research:unity_job_dependencies", "entity": "research", "entity_code": "simulation_jobs",
        "field": "dependency_barrier", "claim": "Unity Job System work is connected through dependencies and synchronization points; a Complete or wait can return work to the main-thread critical path.",
        "source_code": "RESEARCH_S58_UNITY_JOB_TROUBLESHOOTING", "locator": "WaitForJobGroup and Complete synchronization",
        "basis": "documented", "verification_status": "verified", "evidence_level": "primary",
        "context": "Parallelization can reduce serial work but does not make synchronization free.", "status": "published",
    },
    {
        "code": "research:replication_relevancy", "entity": "research", "entity_code": "network_relevance",
        "field": "mechanism", "claim": "Replication Graph and actor relevancy can form per-connection sets so that not every actor is replicated to every client.",
        "source_code": "UE_REPGRAPH", "locator": "sections: per-connection replication lists and relevancy",
        "basis": "documented", "verification_status": "verified", "evidence_level": "primary",
        "context": "The mechanism reduces candidate work under its conditions; it does not define a universal bandwidth budget.", "status": "published",
    },
    {
        "code": "research:cry_audio_ray_policy", "entity": "research", "entity_code": "spatial_audio",
        "field": "occlusion_policy", "claim": "CryEngine documents No Ray, SingleRay and MultipleRay occlusion modes and a distance limit for skipping occlusion work.",
        "source_code": "RESEARCH_S29_CRY_AUDIO", "locator": "sections: No Ray, SingleRay, MultipleRay and distance limits",
        "basis": "documented", "verification_status": "verified", "evidence_level": "primary",
        "context": "Ray policy is a quality/CPU trade-off and must be measured with the project's source count and material classes.", "status": "published",
    },
    {
        "code": "research:packaging_pipeline", "entity": "research", "entity_code": "build_delivery",
        "field": "pipeline", "claim": "Unreal packaging exposes Build, Cook, Stage and Package steps, with chunking available for delivery and patch/content partitioning.",
        "source_code": "RESEARCH_S23_PACKAGING", "locator": "sections: Build, Cook, Stage, Package; Chunking",
        "basis": "documented", "verification_status": "verified", "evidence_level": "primary",
        "context": "Build-time and runtime streaming costs are separate resource axes.", "status": "published",
    },
    {
        "code": "research:texture_streaming_metrics", "entity": "research", "entity_code": "texture_streaming",
        "field": "metrics", "claim": "Texture streaming metrics distinguish pool usage, wanted mips and streaming updates, which are different from a single texture-memory total.",
        "source_code": "RESEARCH_S54_UE_TEXTURE_METRICS", "locator": "wanted mips, pool usage and streaming metrics",
        "basis": "documented", "verification_status": "verified", "evidence_level": "primary",
        "context": "The DSS keeps VRAM, streaming pool and activation/IO observations separate.", "status": "published",
    },
    {
        "code": "research:heroengine_legacy", "entity": "research", "entity_code": "heroengine",
        "field": "applicability", "claim": "HeroEngine is retained as a legacy catalog entry, so current version and public applicability require review before selection.",
        "source_code": "RESEARCH_S44_HEROENGINE_LEGACY", "locator": "legacy status and current applicability warning",
        "basis": "documented", "verification_status": "needs_review", "evidence_level": "secondary",
        "context": "Legacy presence in the catalog is not evidence of current compatibility.", "status": "published",
    },
    {
        "code": "research:benchmark_workload_caveat", "entity": "research", "entity_code": "hardware_anchors",
        "field": "benchmark_context", "claim": "A general CPU benchmark is an anchor for comparison, not a substitute for a game-specific workload and trace.",
        "source_code": "RESEARCH_S50_PASSMARK_FAQ", "locator": "benchmark limits and workload caveat",
        "basis": "documented", "verification_status": "verified", "evidence_level": "primary",
        "context": "Raw benchmark, test name, date and workload context must travel together.", "status": "published",
    },
    {
        "code": "research:profiler_trace_fields", "entity": "research", "entity_code": "runtime_validation",
        "field": "measurement_plan", "claim": "Unreal Insights exposes CPU/GPU, memory and networking trace data that can be used for project-specific validation.",
        "source_code": "UE_INSIGHTS", "locator": "sections: CPU/GPU, memory and networking traces",
        "basis": "documented", "verification_status": "verified", "evidence_level": "primary",
        "context": "The current DSS stores a measurement plan but does not import profiler traces automatically.", "status": "published",
    },
    {
        "code": "research:frame_budget_60", "entity": "research", "entity_code": "frame_budget",
        "field": "target_fps_60", "claim": "For a 60 FPS target, the frame budget is 16.6667 ms.",
        "unit": "ms", "value_num": 16.666667, "formula": "1000 / target_fps",
        "input_parameters": {"target_fps": 60}, "locator": "formula: 1000 / 60",
        "basis": "derived", "verification_status": "derived_from_input", "evidence_level": "computed",
        "context": "Own calculation; it is a budget, not a measured frame time.", "status": "published",
    },
    {
        "code": "research:resolution_ratio_4k", "entity": "research", "entity_code": "render_resolution",
        "field": "pixel_ratio_4k_to_1080p", "claim": "3840x2160 contains four times as many pixels as 1920x1080 before considering other pipeline effects.",
        "unit": "ratio", "value_num": 4.0, "formula": "(3840 * 2160) / (1920 * 1080)",
        "input_parameters": {"width": 3840, "height": 2160, "baseline_width": 1920, "baseline_height": 1080},
        "locator": "formula: pixel-count ratio", "basis": "derived", "verification_status": "derived_from_input", "evidence_level": "computed",
        "context": "Own pixel-count calculation; it is not a prediction of four times GPU frame time.", "status": "published",
    },
    {
        "code": "research:amdahl_s04_n8", "entity": "research", "entity_code": "parallel_speedup",
        "field": "speedup_n8", "claim": "With a serial fraction s=0.40 and idealized N=8 workers, Amdahl's formula gives speedup 2.1053.",
        "unit": "speedup", "value_num": 2.105263, "formula": "(Ts + Tp) / (Ts + Tp / N), with s=0.40 and N=8",
        "input_parameters": {"serial_fraction": 0.4, "workers": 8}, "source_code": "RESEARCH_S37_AMDAHL", "locator": "serial/parallel speedup and overhead",
        "basis": "derived", "verification_status": "derived_from_formula", "evidence_level": "primary",
        "context": "Illustrative ceiling without contention, scheduling or cache overhead; not a game measurement.", "status": "published",
    },
    {
        "code": "research:network_9_clients", "entity": "research", "entity_code": "network_budget",
        "field": "server_to_clients_bytes_per_second", "claim": "With 9 clients, 20 updates/s and 120-byte payload plus a 28-byte IPv4/UDP header, the one-way payload estimate is 26,640 B/s, about 213 kbps.",
        "unit": "B/s", "value_num": 26640.0, "formula": "clients * updates_per_second * (payload_bytes + ipv4_udp_header_bytes)",
        "input_parameters": {"clients": 9, "updates_per_second": 20, "payload_bytes": 120, "ipv4_udp_header_bytes": 28},
        "source_code": "RESEARCH_S53_QUIC_RFC", "locator": "formula: illustrative IPv4/UDP header accounting",
        "basis": "derived", "verification_status": "derived_from_input", "evidence_level": "primary",
        "context": "Own scenario calculation; excludes encryption, retransmission, acknowledgements, other traffic and protocol overhead.", "status": "published",
    },
    {
        "code": "research:riot_128_tick_period", "entity": "research", "entity_code": "server_tick",
        "field": "tick_period_128hz", "claim": "A 128 Hz server tick has a period of 7.8125 ms.",
        "unit": "ms", "value_num": 7.8125, "formula": "1000 / tick_hz", "input_parameters": {"tick_hz": 128},
        "source_code": "RIOT_TICK", "locator": "section: 128-tick servers",
        "basis": "derived", "verification_status": "derived_from_published_rate", "evidence_level": "primary",
        "context": "The rate is a property of the cited service; it is not a universal target.", "status": "published",
    },
    {
        "code": "research:memory_headroom", "entity": "research", "entity_code": "memory_budget",
        "field": "planning_headroom_gib", "claim": "A 5.1 GiB resource subtotal with a 20% planning allowance yields 6.12 GiB.",
        "unit": "GiB", "value_num": 6.12, "formula": "(3.5 + 1.4 + 0.2) * 1.20",
        "input_parameters": {"textures_geometry_gib": 3.5, "render_targets_transient_gib": 1.4, "audio_other_gib": 0.2, "headroom": 0.2},
        "locator": "formula: subtotal plus explicit headroom", "basis": "derived", "verification_status": "derived_from_input", "evidence_level": "computed",
        "context": "Scenario allowance, not a measured RAM/VRAM requirement; CPU copies and residency policy remain separate.", "status": "published",
    },
    {
        "code": "research:pert_expected_duration", "entity": "research", "entity_code": "schedule_estimation",
        "field": "pert_expected_days", "claim": "For O=2, M=4 and P=10 person-days, beta/PERT expected duration is 4.6667 person-days.",
        "unit": "person-days", "value_num": 4.666667, "formula": "(O + 4*M + P) / 6",
        "input_parameters": {"optimistic": 2, "most_likely": 4, "pessimistic": 10}, "source_code": "RESEARCH_S35_PMI_PERT", "locator": "three-point estimating: beta/PERT formula",
        "basis": "derived", "verification_status": "derived_from_formula", "evidence_level": "primary",
        "context": "Worked example; P50/P80 in the application remain scenario estimates until calibrated with project history.", "status": "published",
    },
    {
        "code": "research:critical_path_example", "entity": "research", "entity_code": "critical_path",
        "field": "longest_path_days", "claim": "In the worked DAG A-B-D-E versus A-C-D-E, durations 3/5/8/6/4 make A-C-D-E the longest path at 21 days.",
        "unit": "days", "value_num": 21.0, "formula": "max(3+5+6+4, 3+8+6+4)",
        "input_parameters": {"A": 3, "B": 5, "C": 8, "D": 6, "E": 4}, "source_code": "RESEARCH_S36_NASA_SCHEDULE", "locator": "formula: longest precedence path example",
        "basis": "derived", "verification_status": "derived_from_dag", "evidence_level": "primary",
        "context": "Worked DAG calculation; it is not a schedule commitment for a project.", "status": "published",
    },
]


def _source_records() -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    merged = {**SOURCES, **EXTRA_SOURCES}
    for code, data in sorted(merged.items()):
        url = data.get("url", "")
        title = data.get("title", code)
        lower = f"{url} {title}".lower()
        if code in EXTRA_SOURCES:
            publisher = data.get("publisher", "")
            source_type = data.get("source_type", "secondary")
            locator = data.get("locator", SOURCE_LOCATORS.get(code, "overview"))
        else:
            publisher = (
                "Epic Games" if "epicgames.com" in lower or "unrealengine.com" in lower else
                "Unity Technologies" if "unity3d.com" in lower or "unity.com" in lower else
                "Godot Foundation" if "godotengine.org" in lower or "docs.godotengine.org" in lower else
                "Microsoft" if "microsoft.github.io" in lower else
                "NVIDIA" if "nvidia.com" in lower or "github.com/nvidia" in lower else
                "Valve" if "valvesoftware.com" in lower or "counter-strike.net" in lower else
                "Riot Games" if "riotgames.com" in lower else
                "Crytek" if "huntshowdown.com" in lower else ""
            )
            source_type = (
                "book" if "gameprogrammingpatterns.com" in lower else
                "official_documentation" if publisher in {"Epic Games", "Unity Technologies", "Godot Foundation", "Microsoft"} else
                "engineering_article" if publisher in {"Valve", "Riot Games", "Crytek", "NVIDIA"} else
                "research" if lower.endswith(".pdf") or "siggraph" in lower or "cse.chalmers" in lower else
                "open_source" if "github.com" in lower else "secondary"
            )
            locator = SOURCE_LOCATORS.get(code, "overview page")
        platform = data.get("platform", "") or (
            "Windows/Linux PC"
            if code not in EXTRA_SOURCES and ("windows" in title.lower() or "directx" in lower)
            else ""
        )
        records.append({
            "code": code, "title": title, "publisher": publisher,
            "authors": data.get("authors", ""),
            "source_type": source_type, "published_date": data.get("date", ""),
            "checked_at": CHECKED_AT, "url": url, "version": data.get("version", ""),
            "platform": platform,
            "locator": locator, "availability": "available",
            "applicability": data.get("applicability", ""),
            "notes": "Автоматически перенесено из реестра ссылок каталога; статус механизма и чисел хранится в claims.",
            "status": "published",
        })
    return records


DEPENDENCY_RECORDS: list[dict[str, Any]] = [
    {"source": "tool:ue_nanite", "target": "api:directx12", "dependency_type": "runtime_api", "mandatory": True, "min_version": "SM6", "platform": "pc_windows", "scope": "runtime", "severity": 1, "source_code": "UE_FEATURE_MATRIX", "description": "Nanite requires an appropriate desktop rendering path and Shader Model 6 support in the documented path.", "workaround": "Использовать поддерживаемый rendering path или отказаться от Nanite для этой цели."},
    {"source": "tool:ue_vsm", "target": "api:directx12", "dependency_type": "runtime_api", "mandatory": True, "min_version": "SM6", "platform": "pc_windows", "scope": "runtime", "severity": 2, "source_code": "UE_FEATURE_MATRIX", "description": "Virtual Shadow Maps have rendering-path and SM6 requirements in the engine feature matrix.", "workaround": "Выбрать совместимый путь теней и отдельно проверить качество."},
    {"source": "tool:ue_lumen", "target": "api:directx12", "dependency_type": "runtime_api", "mandatory": False, "min_version": "SM6", "platform": "pc_windows", "scope": "runtime", "severity": 2, "source_code": "UE_FEATURE_MATRIX", "description": "Hardware ray tracing path for Lumen requires a supported OS/RHI/GPU combination; software path differs.", "workaround": "Рассмотреть software ray tracing или другой GI path после прототипа."},
    {"source": "tool:ue_replication_graph", "target": "engine:unreal", "dependency_type": "engine_tool", "mandatory": True, "min_version": "", "platform": "", "scope": "server", "severity": 2, "source_code": "UE_REPGRAPH", "description": "Replication Graph is an Unreal-specific networking tool.", "workaround": "Для другого движка использовать его сетевой слой или собственную репликацию."},
    {"source": "tool:u_dots", "target": "engine:unity", "dependency_type": "engine_tool", "mandatory": True, "min_version": "", "platform": "", "scope": "runtime", "severity": 2, "source_code": "UNITY_ENTITIES", "description": "Entities/DOTS is a Unity package and workflow, not a generic engine-independent switch.", "workaround": "Оставить GameObjects или выбрать аналогичный data-oriented слой движка."},
    {"source": "tool:u_netcode", "target": "tool:u_dots", "dependency_type": "package", "mandatory": True, "min_version": "1.0", "platform": "pc_windows,pc_linux", "scope": "server", "severity": 2, "source_code": "UNITY_NETCODE", "description": "The selected Netcode for Entities path depends on the Entities package family.", "workaround": "Проверить совместимые версии пакетов и lockfile перед интеграцией."},
    {"source": "tool:u_addressables", "target": "engine:unity", "dependency_type": "engine_tool", "mandatory": True, "min_version": "", "platform": "", "scope": "build", "severity": 1, "source_code": "UNITY_ADDRESSABLES", "description": "Addressables is a Unity asset management package and build pipeline.", "workaround": "Использовать штатный streaming/build pipeline выбранного движка."},
]


def _upsert_by_code(db: Session, model, payload: dict[str, Any]):
    code = payload["code"]
    obj = db.scalar(select(model).where(model.code == code))
    if obj is None:
        db.add(obj := model(**payload))
    return obj


def sync_sources(db: Session) -> dict[str, EvidenceSource]:
    out: dict[str, EvidenceSource] = {}
    for payload in _source_records():
        obj = _upsert_by_code(db, EvidenceSource, payload)
        # Existing administrator edits win; only fill fields still empty.
        for key, value in payload.items():
            if key in {"code", "status"}:
                continue
            if not getattr(obj, key, None):
                setattr(obj, key, value)
        out[obj.code] = obj
    db.flush()
    return out


def _source_by_url(sources: dict[str, EvidenceSource], url: str) -> EvidenceSource | None:
    return next((item for item in sources.values() if item.url == url and item.status == "published"), None)


def sync_claims(db: Session, sources: dict[str, EvidenceSource]) -> int:
    created = 0

    def add(payload: dict[str, Any], refresh: tuple[str, ...] = ()) -> None:
        nonlocal created
        existing = db.scalar(
            select(EvidenceClaim).where(EvidenceClaim.code == payload["code"])
        )
        if existing is not None:
            # Машинно-выведенное утверждение обязано следовать за исправленной
            # строкой-источником: индекс железа считается из строки бенчмарка, и
            # если строка позже получила точные значения, утверждение не должно
            # оставаться с прежним контекстом. Курируемые утверждения (basis не
            # `derived`) не трогаются: правки администратора сохраняются.
            if refresh and (existing.basis or "") == "derived":
                for key in refresh:
                    if getattr(existing, key, None) != payload.get(key):
                        setattr(existing, key, payload[key])
            return
        db.add(EvidenceClaim(**payload))
        created += 1

    for item in RESEARCH_CLAIMS:
        payload = dict(item)
        source_code = payload.pop("source_code", "")
        source = sources.get(source_code)
        if source is not None:
            payload["source_id"] = source.id
            payload.setdefault("locator", source.locator)
        payload.setdefault("status", "published")
        add(payload)

    for method in db.scalars(select(Method).where(Method.status == "published")):
        source = _source_by_url(sources, method.source_url)
        text = method.summary or method.description or method.problem or "Каталожное описание метода."
        add({
            "code": f"method:{method.code}:mechanism", "entity": "method", "entity_code": method.code,
            "field": "mechanism", "claim": f"{method.name}: {text}",
            "source_id": source.id if source else None,
            "locator": source.locator if source else "требуется первичный источник",
            "basis": "documented" if source else "unknown",
            "verification_status": "verified" if source else "needs_review",
            "evidence_level": "primary" if source and source.source_type in {"official_documentation", "engineering_article", "research", "engineering_talk", "studio_engineering_article", "official_case_study"} else "secondary",
            "context": "Подтверждает механизм/описание, не переносимый FPS.", "status": "published",
        })
        add({
            "code": f"method:{method.code}:performance_gain", "entity": "method", "entity_code": method.code,
            "field": "performance_gain", "claim": f"Сценарный балл эффекта метода {method.name}.",
            "unit": "0..1", "value_num": method.performance_gain,
            "source_id": source.id if source else None,
            "locator": source.locator if source else "числовая публикация отсутствует",
            "basis": "expert_estimate", "verification_status": "scenario_only",
            "evidence_level": "low", "context": "Экспертный балл для TOPSIS; не измерение FPS.", "status": "published",
        })
    for function in db.execute(select(GameFunction).where(GameFunction.status == "published")).scalars():
        source = _source_by_url(sources, function.source_url)
        add({
            "code": f"function:{function.code}:definition", "entity": "game_function", "entity_code": function.code,
            "field": "definition", "claim": f"{function.name}: {function.description}",
            "source_id": source.id if source else None, "locator": source.locator if source else "требуется источник",
            "basis": "documented" if source else "unknown", "verification_status": "verified" if source else "needs_review",
            "evidence_level": "primary" if source else "low", "context": "Определение функции, не измерение производительности.", "status": "published",
        })
    for model, entity in ((HardwareCPU, "hardware_cpu"), (HardwareGPU, "hardware_gpu")):
        for item in db.scalars(select(model).where(model.status == "published")):
            source = _source_by_url(sources, item.source_url)
            if source is None and item.source_url:
                digest = hashlib.sha1(item.source_url.encode("utf-8")).hexdigest()[:12]
                source = _upsert_by_code(db, EvidenceSource, {
                    "code": f"hardware:{digest}", "title": item.source_title or item.model,
                    "publisher": "Hardware benchmark publisher", "source_type": "hardware_benchmark",
                    "published_date": getattr(item, "source_date", ""), "checked_at": CHECKED_AT,
                    "url": item.source_url, "version": "", "platform": "PC",
                    "locator": "benchmark page", "availability": "available", "applicability": "",
                    "notes": "Исходное значение/методика нормализации требуют отдельной ревизии.", "status": "published",
                })
                # Claims and hardware rows store the integer FK, so a source
                # created from a hardware URL must be flushed before its id is
                # copied into either record.  The normal catalogue sources
                # were flushed by sync_sources; this branch is the only
                # late-created source path.
                db.flush()
                sources[source.code] = source
            if not getattr(item, "benchmark_name", ""):
                item.benchmark_name = item.source_title or "External benchmark"
                item.benchmark_context = "Нормализованный индекс каталога; не FPS и не универсальный игровой benchmark."
                item.normalization_note = "Индекс нормирован внутри набора каталога; сравнивать только в указанном контексте."
                item.evidence_basis = "derived"
                if source:
                    item.evidence_source_id = source.id
            value = getattr(item, "single_thread_score", None) if model is HardwareCPU else getattr(item, "raster_score", None)
            add({
                "code": f"{entity}:{item.model}:benchmark_index", "entity": entity, "entity_code": item.model,
                "field": "benchmark_index", "claim": f"{item.model}: индекс каталога получен из внешнего benchmark anchor и нормализации.",
                "unit": "normalized 0..1", "value_num": value, "source_id": source.id if source else None,
                "locator": source.locator if source else "benchmark source missing", "basis": "derived",
                "verification_status": "derived_with_context" if source else "needs_review", "evidence_level": "medium",
                "formula": "normalize(raw benchmark within catalog bounds)", "input_parameters": {"model": item.model, "benchmark_name": getattr(item, "benchmark_name", "")},
                "context": getattr(item, "benchmark_context", ""), "status": "published",
            }, refresh=("source_id", "value_num", "locator", "verification_status",
                        "input_parameters", "context"))
    db.flush()
    return created


def sync_nodes_and_edges(db: Session, sources: dict[str, EvidenceSource]) -> dict[str, int]:
    created_nodes = created_edges = 0
    node_cache: dict[str, TechnologyNode] = {}

    def node(code: str, node_type: str, name: str, *, version: str = "", platform: str = "", scope: str = "runtime", source: EvidenceSource | None = None):
        nonlocal created_nodes
        if code in node_cache:
            return node_cache[code]
        obj = db.scalar(select(TechnologyNode).where(TechnologyNode.code == code))
        if obj is None:
            obj = TechnologyNode(code=code, node_type=node_type, name=name, version=version, platform=platform, scope=scope, docs_url=source.url if source else "", source_id=source.id if source else None, status="published")
            db.add(obj); created_nodes += 1
        node_cache[code] = obj
        return obj

    methods = list(db.scalars(select(Method).where(Method.status == "published")))
    engines = list(db.scalars(select(Engine).where(Engine.status == "published")))
    tools = list(db.scalars(select(EngineTool).where(EngineTool.status == "published")))
    for item in methods:
        node(f"method:{item.code}", "method", item.name, source=_source_by_url(sources, item.source_url))
    for item in engines:
        node(f"engine:{item.code}", "engine", item.name, source=_source_by_url(sources, item.docs_url))
    for item in tools:
        engine = db.get(Engine, item.engine_id)
        node(f"tool:{item.code}", "tool", item.name, version=item.min_version or "", scope=item.tool_type, source=_source_by_url(sources, item.docs_url))
        if engine:
            node(f"engine:{engine.code}", "engine", engine.name, source=_source_by_url(sources, engine.docs_url))
    for code, name, version in (("api:directx12", "DirectX 12", "SM6"), ("api:vulkan", "Vulkan", ""), ("api:dx11", "DirectX 11", "")):
        node(code, "api", name, version=version, platform="pc_windows" if code != "api:vulkan" else "pc_windows,pc_linux", source=sources.get("UE_FEATURE_MATRIX"))
    db.flush()
    by_code = {item.code: item for item in db.scalars(select(TechnologyNode))}
    for item in DEPENDENCY_RECORDS:
        source_node = by_code.get(item["source"]); target_node = by_code.get(item["target"])
        if source_node is None or target_node is None:
            continue
        source = sources.get(item.get("source_code", ""))
        exists = db.scalar(select(DependencyEdge.id).where(
            DependencyEdge.source_node_id == source_node.id,
            DependencyEdge.target_node_id == target_node.id,
            DependencyEdge.dependency_type == item["dependency_type"],
        ))
        if exists:
            continue
        db.add(DependencyEdge(
            source_node_id=source_node.id, target_node_id=target_node.id,
            dependency_type=item["dependency_type"], mandatory=item["mandatory"],
            min_version=item.get("min_version", ""), max_version=item.get("max_version", ""),
            platform=item.get("platform", ""), scope=item.get("scope", "runtime"),
            severity=item.get("severity", 2), source_id=source.id if source else None,
            description=item.get("description", ""), workaround=item.get("workaround", ""), status="published",
        )); created_edges += 1
    db.flush()
    return {"technology_nodes_created": created_nodes, "dependency_edges_created": created_edges}


def sync_all(db: Session) -> dict[str, int]:
    sources = sync_sources(db)
    claims = sync_claims(db, sources)
    graph = sync_nodes_and_edges(db, sources)
    return {"evidence_sources": len(sources), "evidence_claims_created": claims, **graph}
