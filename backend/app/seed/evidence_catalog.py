"""Seed-данные доказательного слоя.

Файл содержит небольшой, но разнородный набор кейсов и зависимостей, а
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
    CaseEvidence, DependencyEdge, Engine, EngineTool, EvidenceClaim,
    EvidenceSource, GameCase, GameFunction, HardwareCPU, HardwareGPU, Method, TechnologyNode,
    TeamScenario, WorkPackage,
)
from . import methods_data
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


CASE_RECORDS: list[dict[str, Any]] = [
    {
        "code": "left4dead_ai_director", "title": "Left 4 Dead", "studio": "Valve",
        "release_year": 2008, "technology": "Source", "engine_code": "source",
        "world_type": "линейные кооперативные кампании", "network_mode": "4-player co-op",
        "summary": "AI Director модулирует драматический темп по оценке интенсивности команды.",
        "relevance": "Прямой кейс адаптивного темпа и процедурного управления населением угроз.",
        "transfer_limits": "Не переносит количество заражённых, FPS или сложность кампании в другой проект.",
        "evidence": [{
            "code": "left4dead_ai_director.pacing", "method_code": "",
            "function_code": "advanced_npc_ai", "fact": "Система оценивает Survivor Intensity, повышает её событиями и постепенно снижает; Director регулирует pacing, а не обязательно амплитуду сложности.",
            "match_level": "direct", "source_code": "L4D_AI_DIRECTOR",
            "locator": "section: Adaptive Dramatic Pacing",
            "transfer_limits": "Публичный материал описывает механизм и компромисс, но не даёт универсальной оценки CPU/FPS.",
        }],
    },
    {
        "code": "counterstrike2_subtick", "title": "Counter-Strike 2", "studio": "Valve",
        "release_year": 2023, "technology": "Source 2", "engine_code": "source",
        "world_type": "соревновательные арены", "network_mode": "authoritative multiplayer",
        "summary": "Sub-tick architecture records the instant of relevant input events independently of the old tick-only framing.",
        "relevance": "Кейс серверной временной модели, сетевой отзывчивости и требований к валидации.",
        "transfer_limits": "Официальное описание не задаёт переносимый бюджет трафика или задержки для другой игры.",
        "evidence": [{
            "code": "counterstrike2_subtick.netcode", "method_code": "tickrate_budgeting",
            "function_code": "multiplayer_netcode", "fact": "Valve описывает sub-tick updates как механизм, при котором сервер знает момент движения, выстрела или броска.",
            "match_level": "direct", "source_code": "CS2_SUBTICK", "locator": "section: Sub-tick updates",
            "transfer_limits": "Нельзя выводить из этого факта универсальный tick rate, latency или hardware requirement.",
        }],
    },
    {
        "code": "valorant_128_tick", "title": "VALORANT", "studio": "Riot Games",
        "release_year": 2020, "technology": "собственная серверная инфраструктура", "engine_code": "custom",
        "world_type": "соревновательные арены", "network_mode": "authoritative 128-tick server",
        "summary": "Инженерный материал Riot разбирает серверную производительность и сетевую модель VALORANT.",
        "relevance": "Кейс серверного тика, влияния latency и проверки simulation divergence.",
        "transfer_limits": "128 tick - свойство описанного сервиса, а не универсальная рекомендация для каждой игры.",
        "evidence": [{
            "code": "valorant_128_tick.server", "method_code": "tickrate_budgeting",
            "function_code": "multiplayer_netcode", "fact": "Riot связывает серверную производительность с задачами hit registration, peeker's advantage и simulation divergence.",
            "match_level": "direct", "source_code": "RIOT_NETCODE", "locator": "sections: peeker's advantage and simulation divergence",
            "transfer_limits": "Состав железа, сетевой маршрут и тик должны измеряться отдельно для проекта.",
        }, {
            "code": "valorant_128_tick.server_rate", "method_code": "tickrate_budgeting",
            "function_code": "multiplayer_netcode", "fact": "Публичный материал Riot описывает 128-tick server performance как инженерную цель сервиса VALORANT.",
            "match_level": "direct", "source_code": "RIOT_TICK", "locator": "section: 128-tick servers",
            "transfer_limits": "Цель нельзя выдавать за доказанный минимум для другого числа игроков или другой симуляции.",
        }],
    },
    {
        "code": "it_takes_two_splitscreen", "title": "It Takes Two", "studio": "Hazelight",
        "release_year": 2021, "technology": "Unreal Engine 4", "engine_code": "unreal",
        "world_type": "линейные кооперативные сцены", "network_mode": "local/online co-op",
        "summary": "Технический анализ Digital Foundry рассматривает split-screen и две точки зрения как часть рендер-пайплайна.",
        "relevance": "Пример того, что локальные вьюпорты увеличивают клиентскую работу, но не равны сетевым игрокам.",
        "transfer_limits": "Результат зависит от сцены, разрешения, качества и конкретной реализации; FPS не переносится.",
        "evidence": [{
            "code": "it_takes_two_splitscreen.render", "method_code": "splitscreen_render_budget",
            "function_code": "split_screen_rendering", "fact": "Публичный технический разбор связывает кооперативный split-screen с отдельными видами и стоимостью рендеринга.",
            "match_level": "direct", "source_code": "DF_ITTakesTWO", "locator": "section: split-screen rendering and performance analysis",
            "transfer_limits": "Нельзя использовать сравнительный FPS анализа как норматив для другой сцены.",
        }],
    },
    {
        "code": "doom_eternal_rendering", "title": "DOOM Eternal", "studio": "id Software",
        "release_year": 2020, "technology": "id Tech 7", "engine_code": "custom",
        "world_type": "сегментированные боевые уровни", "network_mode": "single-player with online modes",
        "summary": "Доклад SIGGRAPH 2020 описывает geometry caches, gore, decals, material compositing и workflow вокруг целевого frame rate.",
        "relevance": "Кейс оптимизированного производственного графического пайплайна с явной целевой частотой.",
        "transfer_limits": "Собственный движок, ассеты и платформенный порт делают детали непереносимыми без повторного измерения.",
        "evidence": [{
            "code": "doom_eternal_rendering.pipeline", "method_code": "",
            "function_code": "rendering_architecture", "fact": "Команда id Software описывает несколько специализированных подсистем рендера и workflow, позволивших удерживать целевую частоту кадров на платформах проекта.",
            "match_level": "direct", "source_code": "DOOM_ETERNAL", "locator": "slides: geometry caches, gore, material compositing, target frame rate",
            "transfer_limits": "Доклад подтверждает инженерный подход, но не даёт универсального отношения ассеты -> FPS.",
        }],
    },
    {
        "code": "hunt_showdown_audio", "title": "Hunt: Showdown", "studio": "Crytek",
        "release_year": 2019, "technology": "CryEngine", "engine_code": "cryengine",
        "world_type": "большие PvPvE-карты", "network_mode": "competitive multiplayer",
        "summary": "Команда Hunt описывает occlusion rays, material-dependent filtering, HRTF/CrySpatial и аудио как источник игровой читаемости.",
        "relevance": "Кейс пространственного звука, где реализм ограничен читаемостью и измерительными правилами микса.",
        "transfer_limits": "Число emitters, лучей и стоимость CPU/аудио-потока зависят от карты и middleware.",
        "evidence": [{
            "code": "hunt_showdown_audio.occlusion", "method_code": "audio_occlusion_propagation",
            "function_code": "audio_system", "fact": "Для occlusion команда описывает проверку препятствия между emitter и listener и фильтрацию по типу поверхности.",
            "match_level": "direct", "source_code": "HUNT_AUDIO", "locator": "sections: Occlusion and Realism, Feedback and Readability",
            "transfer_limits": "Это подтверждение механизма, а не числовая модель трафика или FPS.",
        }, {
            "code": "hunt_showdown_audio.cryspatial", "method_code": "audio_occlusion_propagation",
            "function_code": "audio_system", "fact": "Crytek описывает CrySpatial как HRTF-based 3D audio, помогающий различать направление источника.",
            "match_level": "direct", "source_code": "HUNT_AUDIO_2025", "locator": "section: CrySpatial",
            "transfer_limits": "Восприятие звука зависит от устройства вывода и настройки микса; результат не переносится автоматически.",
        }],
    },
    {
        "code": "ue_city_sample_open_world", "title": "Unreal Engine City Sample", "studio": "Epic Games",
        "release_year": 2021, "technology": "Unreal Engine 5", "engine_code": "unreal",
        "world_type": "4 km x 4 km city sample", "network_mode": "technical demo",
        "summary": "Официальная документация City Sample связывает World Partition, Nanite, Lumen, VSM, Mass AI, Chaos и MetaSounds.",
        "relevance": "Связанный reference-case для большого мира, массовой симуляции, процедурных данных и memory/streaming trade-offs.",
        "transfer_limits": "Это демонстрационный проект; его polygon/asset counts и требования не являются минимальными требованиями для любой игры.",
        "evidence": [{
            "code": "ue_city_sample_open_world.world", "method_code": "world_partition_streaming",
            "function_code": "open_world_streaming", "fact": "City Sample использует World Partition и on-demand loading cells для большого города.",
            "match_level": "direct", "source_code": "UE_CITY_SAMPLE", "locator": "sections: World Partition and Big City",
            "transfer_limits": "Размер ячейки, loading range и активная сцена требуют калибровки на своем мире.",
        }, {
            "code": "ue_city_sample_open_world.geometry", "method_code": "virtual_geometry_clusters",
            "function_code": "geometry_pipeline", "fact": "Документация описывает Nanite на static meshes, высокополигональные исходники и динамическое изменение представления по видимости/детализации.",
            "match_level": "direct", "source_code": "UE_CITY_SAMPLE", "locator": "section: Nanite Virtualized Geometry",
            "transfer_limits": "Неподдерживаемые материалы, WPO, foliage и fallback meshes требуют отдельных проверок.",
        }, {
            "code": "ue_city_sample_open_world.procedural", "method_code": "",
            "function_code": "procedural_terrain", "fact": "City Sample PCG documentation содержит процедурную конфигурацию города, PCG graphs и shape grammar assets.",
            "match_level": "direct", "source_code": "UE_CITY_SAMPLE_PCG", "locator": "section: procedural city and PCG graph examples",
            "transfer_limits": "Наличие PCG graph не говорит о времени генерации, cook или runtime memory другого проекта.",
        }],
    },
    {
        "code": "unity_dots_production", "title": "Unity DOTS production examples", "studio": "Unity and partner studios",
        "release_year": 2024, "technology": "Unity DOTS / Entities", "engine_code": "unity",
        "world_type": "large-scale multiplayer and simulation examples", "network_mode": "varies by project",
        "summary": "Unity's official DOTS page lists production examples including V Rising, Megacity Metro and IXION.",
        "relevance": "Кейс data-oriented подхода, parallel jobs и масштабирования симуляции на отдельных проектах.",
        "transfer_limits": "Список showcase подтверждает применение, но не доказывает одинаковый выигрыш производительности для всех проектов.",
        "evidence": [{
            "code": "unity_dots_production.ecs", "method_code": "ecs_data_oriented_crowd",
            "function_code": "crowd_simulation", "fact": "Unity описывает DOTS/Entities как стек для более масштабной обработки и приводит production examples с ECS.",
            "match_level": "direct", "source_code": "UNITY_DOTS_PRODUCTION", "locator": "section: DOTS in Production",
            "transfer_limits": "Переход с GameObjects на ECS имеет migration cost и зависит от контракта данных и job safety.",
        }],
    },
]


DEPENDENCY_RECORDS: list[dict[str, Any]] = [
    {"source": "tool:ue_nanite", "target": "api:directx12", "dependency_type": "runtime_api", "mandatory": True, "min_version": "SM6", "platform": "pc_windows", "scope": "runtime", "severity": 1, "source_code": "UE_FEATURE_MATRIX", "description": "Nanite requires an appropriate desktop rendering path and Shader Model 6 support in the documented path.", "workaround": "Использовать поддерживаемый rendering path или отказаться от Nanite для этой цели."},
    {"source": "tool:ue_vsm", "target": "api:directx12", "dependency_type": "runtime_api", "mandatory": True, "min_version": "SM6", "platform": "pc_windows", "scope": "runtime", "severity": 2, "source_code": "UE_FEATURE_MATRIX", "description": "Virtual Shadow Maps have rendering-path and SM6 requirements in the engine feature matrix.", "workaround": "Выбрать совместимый путь теней и отдельно проверить качество."},
    {"source": "tool:ue_lumen", "target": "api:directx12", "dependency_type": "runtime_api", "mandatory": False, "min_version": "SM6", "platform": "pc_windows", "scope": "runtime", "severity": 2, "source_code": "UE_FEATURE_MATRIX", "description": "Hardware ray tracing path for Lumen requires a supported OS/RHI/GPU combination; software path differs.", "workaround": "Рассмотреть software ray tracing или другой GI path после прототипа."},
    {"source": "tool:ue_replication_graph", "target": "engine:unreal", "dependency_type": "engine_tool", "mandatory": True, "min_version": "", "platform": "", "scope": "server", "severity": 2, "source_code": "UE_REPGRAPH", "description": "Replication Graph is an Unreal-specific networking tool.", "workaround": "Для другого движка использовать его сетевой слой или собственную репликацию."},
    {"source": "tool:u_dots", "target": "engine:unity", "dependency_type": "engine_tool", "mandatory": True, "min_version": "", "platform": "", "scope": "runtime", "severity": 2, "source_code": "UNITY_ENTITIES", "description": "Entities/DOTS is a Unity package and workflow, not a generic engine-independent switch.", "workaround": "Оставить GameObjects или выбрать аналогичный data-oriented слой движка."},
    {"source": "tool:u_netcode", "target": "tool:u_dots", "dependency_type": "package", "mandatory": True, "min_version": "1.0", "platform": "pc_windows,pc_linux", "scope": "server", "severity": 2, "source_code": "UNITY_NETCODE", "description": "The selected Netcode for Entities path depends on the Entities package family.", "workaround": "Проверить совместимые версии пакетов и lockfile перед интеграцией."},
    {"source": "tool:u_addressables", "target": "engine:unity", "dependency_type": "engine_tool", "mandatory": True, "min_version": "", "platform": "", "scope": "build", "severity": 1, "source_code": "UNITY_ADDRESSABLES", "description": "Addressables is a Unity asset management package and build pipeline.", "workaround": "Использовать штатный streaming/build pipeline выбранного движка."},
]


TEAM_RECORDS = [
    {"code": "solo", "name": "Solo", "description": "Один специалист; узкие роли выполняются последовательно.", "team_size": 1, "role_capacity": {"design": 1, "engineering": 1, "technical_art": 1, "qa": 1, "production": 1}, "parallel_tracks": 1, "communication_pct": 0.05, "unplanned_pct": 0.25, "specialist_capacity": {}},
    {"code": "small_2_5", "name": "Малая команда (2-5)", "description": "Два параллельных потока и общая QA/production ёмкость.", "team_size": 4, "role_capacity": {"design": 1, "engineering": 2, "technical_art": 1, "qa": 1, "production": 1}, "parallel_tracks": 2, "communication_pct": 0.12, "unplanned_pct": 0.18, "specialist_capacity": {}},
    {"code": "mid_6_15", "name": "Средняя команда (6-15)", "description": "Специализированные роли и несколько независимых потоков.", "team_size": 10, "role_capacity": {"design": 2, "engineering": 5, "technical_art": 2, "qa": 2, "production": 1}, "parallel_tracks": 5, "communication_pct": 0.18, "unplanned_pct": 0.15, "specialist_capacity": {}},
    {"code": "large_16_plus", "name": "Большая команда (16+)", "description": "Срок ограничивается зависимостями, интеграцией и quality gates.", "team_size": 24, "role_capacity": {"design": 3, "engineering": 10, "technical_art": 5, "qa": 4, "production": 2}, "parallel_tracks": 12, "communication_pct": 0.25, "unplanned_pct": 0.12, "specialist_capacity": {}},
    # Шаблон «собственный состав» с явными нейтральными значениями. Это не
    # скрытая подмена: значения помечены как экспертные допущения, а не как
    # измеренная ёмкость конкретной студии, и переопределяются заказчиком.
    {"code": "custom", "name": "Собственный состав", "description": "Промежуточная ёмкость под нетиповую команду; численность и роли переопределяются пользователем.", "team_size": 6, "role_capacity": {"design": 1, "engineering": 3, "technical_art": 1, "qa": 1, "production": 1}, "parallel_tracks": 3, "communication_pct": 0.15, "unplanned_pct": 0.16, "specialist_capacity": {}},
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


def sync_cases(db: Session, sources: dict[str, EvidenceSource]) -> int:
    created = 0
    # CaseEvidence is intentionally allowed to point at a function without a
    # method (method_code="").  A non-empty method reference, however, must be
    # an actual catalog method.  Earlier seed data used function codes here,
    # which looked plausible in the UI but made cases_for_methods return no
    # cases for any real Method.
    method_codes = {
        item["code"] for item in methods_data.METHODS + methods_data.EXTRA_METHODS
    }
    for payload in CASE_RECORDS:
        case_payload = {key: value for key, value in payload.items() if key != "evidence"}
        case_payload["status"] = "published"
        case = _upsert_by_code(db, GameCase, case_payload)
        if case.id is None:
            db.flush()
        for item in payload.get("evidence", []):
            method_code = item.get("method_code", "")
            if method_code and method_code not in method_codes:
                raise ValueError(
                    f"Case evidence {item['code']} references unknown method "
                    f"{method_code!r}; use an exact method code or an empty "
                    "method_code for function-only evidence."
                )
            existing = db.scalar(
                select(CaseEvidence).where(CaseEvidence.code == item["code"])
            )
            if existing is not None:
                # Repair the old seed's function-as-method mismatch without
                # overwriting a deliberate administrator edit.  The legacy
                # value is recognizable because it equals function_code.
                if (
                    method_code != existing.method_code
                    and existing.method_code == item.get("function_code", "")
                ):
                    existing.method_code = method_code
                continue
            source = sources.get(item.get("source_code", ""))
            db.add(CaseEvidence(
                code=item["code"], case_id=case.id,
                function_code=item.get("function_code", ""), method_code=method_code,
                fact=item["fact"], match_level=item.get("match_level", "direct"),
                locator=item.get("locator", "overview"), source_id=source.id if source else None,
                basis="case_evidence", transfer_limits=item.get("transfer_limits", ""), status="published",
            ))
            created += 1
    db.flush()
    return created


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


def sync_work_packages(db: Session) -> int:
    """Создать пакеты работ, задать их величину и обновить предусловия.

    **Величину** оценки задаёт курируемая трудоёмкость пакета
    (`pack_loader.curated_effort`): только она различает конвейер
    виртуализированной геометрии (260 чел.-дней) и правку куллинга тайлмапа
    (3 чел.-дня) — 28 различных значений в размахе 86,7×. **Распределение**
    итога по фазам задаёт формула из `implementation_cost` и `complexity`: её
    собственный размах — 3,02×, и как итог она не различает почти ничего, но как
    профиль фаз она содержательна (29,3 % работы в интеграции против 12,5 % при
    делении поровну).

    Раньше публиковались обе семьи: формульная `{method}.{kind}` (802 строки) и
    пакетная `WP_{method}_{kind}` (992 строки, итог / 8 на фазу). Они давали
    1081,82 против 2435 чел.-дней, коррелировали всего на 0,45, а пакетная не
    несла полей, которые читает планировщик (`min_days`, `late_factor`,
    `parallelizable`, `dependency_codes`). Теперь семья одна: структура
    формульной, величина курируемая.

    `dependency_codes` пересчитываются и у уже существующих пакетов. Раньше
    проход только вставлял новые строки и пропускал существующие, а связи
    «метод требует метод» появляются позже — при загрузке пакетов. В итоге все
    802 опубликованных пакета оставались с пустым списком предусловий, хотя 64
    метода имеют опубликованную зависимость: планировщик не ставил первый пакет
    метода после интеграционного пакета его предусловия.
    """
    created = 0
    refreshed = 0
    relation_dependencies: dict[str, list[str]] = {}
    from ..models.entities import Conflict
    from .pack_loader import curated_effort
    curated = curated_effort()
    for relation in db.scalars(select(Conflict).where(
        Conflict.conflict_type == "dependency", Conflict.status == "published"
    )):
        relation_dependencies.setdefault(relation.a_code, []).append(relation.b_code)
    for method in db.scalars(select(Method).where(Method.status == "published")):
        factor = {"low": 1.08, "medium": 1.2, "high": 1.45, "critical": 1.8}.get(method.late_cost, 1.2)
        c = max(1.0, float(method.implementation_cost or 3)); x = max(1.0, float(method.complexity or 3))
        dependencies = list(relation_dependencies.get(method.code, []))
        packages = [
            ("design", "Проектирование и контракт", "design", 0.45 + c * 0.22, True),
            ("feasibility", "Проверка реализуемости", "engineering", (0.6 + x * 0.35) if method.requires_prototype or x >= 4 else 0.0, True),
            ("integration", "Интеграция в проект", "engineering", 0.9 + c * 0.55, False),
            ("content", "Подготовка контента и ассетов", "technical_art", 0.35 + x * 0.3, True),
            ("optimization", "Оптимизация и измерительный стенд", "engineering", 0.4 + x * 0.25, True),
            ("qa", "QA и регрессия", "qa", 0.45 + x * 0.22, False),
            ("release", "Стабилизация и документация", "production", 0.25 + c * 0.12, False),
        ]
        estimate = curated.get(method.code)
        # Сумма весов формулы — знаменатель долей: курируемый итог
        # раскладывается по фазам без остатка.
        shape_total = sum(item[3] for item in packages if item[3] > 0) or 1.0
        for kind, name, role, shape, parallelizable in packages:
            if shape <= 0:
                continue
            share = shape / shape_total
            if estimate is not None:
                p50 = estimate["p50"] * share
                p80 = estimate["p80"] * share
                basis = estimate.get("basis", "expert_estimate")
                stage = estimate.get("recommended_stage") or method.recommended_stage
                stage_note = estimate.get("stage_note") or ""
            else:
                # Метод без курируемой оценки: формульный итог остаётся
                # fallback, иначе работа метода пропала бы из календаря вовсе.
                p50 = shape
                p80 = shape * 1.5
                basis = "expert_estimate"
                stage = method.recommended_stage
                stage_note = ""
            p50 = round(p50, 4)
            p80 = round(p80, 4)
            min_days = round(p50 * 0.65, 4)
            code = f"{method.code}.{kind}"
            existing = db.scalar(select(WorkPackage).where(WorkPackage.code == code))
            if existing is not None:
                # Согласующий проход: величина оценки приходит из пакета, а
                # строка уже существует в собранной базе. Без него смена семьи не
                # доходила бы до базы — как раньше не доходил словарь ролей.
                changed = False
                for field, value in (
                    ("p50_days", p50), ("p80_days", p80), ("min_days", min_days),
                    ("role", role), ("parallelizable", parallelizable),
                    ("late_factor", factor), ("basis", basis),
                ):
                    if getattr(existing, field) != value:
                        setattr(existing, field, value)
                        changed = True
                if list(existing.dependency_codes or []) != dependencies:
                    existing.dependency_codes = dependencies
                    changed = True
                # Курируемая стадия перекрывает каталожную только когда она
                # есть; обоснование (`stage_note`) не затирается.
                if estimate is not None and stage and existing.recommended_stage != stage:
                    existing.recommended_stage = stage
                    changed = True
                if stage_note and not (existing.stage_note or "").strip():
                    existing.stage_note = stage_note
                    changed = True
                if changed:
                    refreshed += 1
                continue
            db.add(WorkPackage(
                code=code, method_code=method.code, name=f"{method.name}: {name}",
                package_type=kind, role=role, min_days=min_days,
                p50_days=p50, p80_days=p80,
                parallelizable=parallelizable, recommended_stage=stage,
                stage_note=stage_note, late_factor=factor, dependency_codes=dependencies,
                basis=basis, status="published",
            )); created += 1
    for payload in TEAM_RECORDS:
        if not db.scalar(select(TeamScenario.id).where(TeamScenario.code == payload["code"])):
            db.add(TeamScenario(**payload, status="published")); created += 1
    db.flush()
    return created + refreshed


def sync_all(db: Session) -> dict[str, int]:
    sources = sync_sources(db)
    cases = sync_cases(db, sources)
    claims = sync_claims(db, sources)
    graph = sync_nodes_and_edges(db, sources)
    work = sync_work_packages(db)
    # Ключ называет действие, а не только вставку: `sync_work_packages`
    # пересчитывает предусловия у существующих пакетов и возвращает сумму
    # созданных и обновлённых записей.
    return {"evidence_sources": len(sources), "evidence_claims_created": claims, "case_evidence_created": cases, **graph, "planning_records_synced": work}
