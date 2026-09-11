"""Generate the reproducible Russian study in Markdown and PDF.

The report deliberately has no dependency on the FastAPI application. This is
useful for a clean checkout and for CI: the local SQLite snapshot can be read
when it already has the evidence layer, while the report still documents the
catalog and its limitations before the first application start.

Usage from the repository root::

    python tools/generate_research_report.py

The PDF writer uses ReportLab and registers a Unicode font so Russian text is
not silently replaced by empty glyphs. The final PDF is written to
``output/pdf/game-development-dss-study.pdf`` and the source to
``research/game-development-dss-study.md``.
"""
from __future__ import annotations

import argparse
import ast
import html
import re
import sqlite3
import subprocess
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DB = ROOT / "backend" / "gamedev_dss.db"
DEFAULT_MARKDOWN = ROOT / "research" / "game-development-dss-study.md"
DEFAULT_PDF = ROOT / "output" / "pdf" / "game-development-dss-study.pdf"
DEFAULT_MATRIX = ROOT / "research" / "catalog-coverage-matrix.md"


SOURCES = [
    ("S01", "Unreal Engine: World Partition", "Epic Games", "official_documentation", "https://dev.epicgames.com/documentation/en-us/unreal-engine/world-partition-in-unreal-engine", "World Partition; streaming sources"),
    ("S02", "Unreal Engine: Nanite Virtualized Geometry", "Epic Games", "official_documentation", "https://dev.epicgames.com/documentation/en-us/unreal-engine/nanite-virtualized-geometry-in-unreal-engine", "Nanite overview and supported content"),
    ("S03", "Unreal Engine: Lumen Global Illumination and Reflections", "Epic Games", "official_documentation", "https://dev.epicgames.com/documentation/en-us/unreal-engine/lumen-global-illumination-and-reflections-in-unreal-engine", "Lumen overview and hardware/software paths"),
    ("S04", "Supported Features by Rendering Path for Desktop", "Epic Games", "official_documentation", "https://dev.epicgames.com/documentation/en-us/unreal-engine/supported-features-by-rendering-path-for-desktop-with-unreal-engine", "Supported Features table"),
    ("S05", "DirectX Variable Rate Shading specification", "Microsoft", "standard/specification", "https://microsoft.github.io/DirectX-Specs/d3d/VariableRateShading.html", "shading-rate and feature-tier sections"),
    ("S06", "DirectX Mesh Shader specification", "Microsoft", "standard/specification", "https://microsoft.github.io/DirectX-Specs/d3d/MeshShader.html", "device support requirements"),
    ("S07", "Unity Manual: Job System", "Unity Technologies", "official_documentation", "https://docs.unity3d.com/Manual/JobSystem.html", "Job System overview"),
    ("S08", "Unity Manual: Entities (DOTS)", "Unity Technologies", "official_documentation", "https://docs.unity3d.com/Packages/com.unity.entities@1.0/manual/index.html", "Entities package overview"),
    ("S09", "Unity Manual: Netcode for Entities", "Unity Technologies", "official_documentation", "https://docs.unity3d.com/Packages/com.unity.netcode@1.0/manual/index.html", "package documentation"),
    ("S10", "Godot: Optimizing 3D Performance", "Godot Foundation", "official_documentation", "https://docs.godotengine.org/en/stable/tutorials/performance/optimizing_3d_performance.html", "performance optimization"),
    ("S11", "The AI Systems of Left 4 Dead", "Mike Booth / Valve", "conference_talk", "https://steamcdn-a.akamaihd.net/apps/valve/2009/ai_systems_of_l4d_mike_booth.pdf", "Adaptive Dramatic Pacing"),
    ("S12", "Counter-Strike 2: Moving Beyond Tick Rate", "Valve", "official_game_material", "https://www.counter-strike.net/cs2", "Sub-tick updates"),
    ("S13", "Peeking into VALORANT's Netcode", "Riot Games", "studio_engineering", "https://technology.riotgames.com/news/peeking-valorants-netcode", "peeker's advantage and simulation divergence"),
    ("S14", "Valorant 128-tick servers", "Riot Games", "studio_engineering", "https://technology.riotgames.com/news/valorants-128-tick-servers", "128-tick server material"),
    ("S15", "It Takes Two tech analysis", "Digital Foundry", "video/technical_analysis", "https://www.digitalfoundry.net/articles/digitalfoundry-2021-it-takes-two-tech-analysis", "split-screen rendering discussion"),
    ("S16", "Rendering the Hellscape of DOOM Eternal", "id Software / SIGGRAPH", "conference_talk", "https://advances.realtimerendering.com/s2020/RenderingDoomEternal.pdf", "geometry caches, gore, material compositing"),
    ("S17", "Hunt: Showdown - Audio readability, realism and consistency", "Crytek", "studio_engineering", "https://www.huntshowdown.com/news/hunt-audio-readability-realism-and-consistency", "occlusion, readability and consistency"),
    ("S18", "Game Engine Architecture, Third Edition", "Jason Gregory; CRC Press", "book", "https://www.gameenginebook.com/", "chapters 3-4 and 16"),
    ("S19", "Real-Time Rendering, Fourth Edition", "Tomas Akenine-Moller; Eric Haines; Naty Hoffman", "book", "https://www.realtimerendering.com/", "chapters 2-3 and 8"),
    ("S20", "Game Programming Patterns", "Robert Nystrom", "book", "https://gameprogrammingpatterns.com/", "Data Locality, Object Pool, State"),
    ("S21", "GPU Gems 3", "NVIDIA contributors", "book", "https://developer.nvidia.com/gpugems/gpugems3/", "volumetric lighting, shadows, post-processing"),
    ("S22", "Vulkan 1.3 Extensions Specification", "Khronos Vulkan Working Group", "standard/specification", "https://registry.khronos.org/vulkan/specs/1.3-extensions/html/", "device features, queues, synchronization"),
    ("S23", "Unreal Engine: Packaging Your Project", "Epic Games", "official_documentation", "https://dev.epicgames.com/documentation/en-us/unreal-engine/packaging-your-project", "Build/Cook/Stage/Package; cooking and chunks"),
    ("S24", "Unreal Engine: World Partition HLOD", "Epic Games", "official_documentation", "https://dev.epicgames.com/documentation/en-us/unreal-engine/world-partition---hierarchical-level-of-detail-in-unreal-engine", "HLOD layers, proxy meshes and loading ranges"),
    ("S25", "Using PCG with World Partition", "Epic Games", "official_documentation", "https://dev.epicgames.com/documentation/en-us/unreal-engine/using-pcg-with-world-partition-in-unreal-engine?lang=en-US", "PCG Data Layers and HLOD Layers"),
    ("S26", "Unreal Engine: Replication Graph", "Epic Games", "official_documentation", "https://dev.epicgames.com/documentation/en-us/unreal-engine/replication-graph-in-unreal-engine", "per-connection replication lists and Fortnite example"),
    ("S27", "Unreal Engine: Actor Relevancy", "Epic Games", "official_documentation", "https://dev.epicgames.com/documentation/en-us/unreal-engine/actor-relevancy-in-unreal-engine", "per-connection relevancy and distance"),
    ("S28", "CRYENGINE: Streaming System", "Crytek", "official_documentation", "https://www.cryengine.com/docs/static/engines/cryengine-5/categories/23756813/pages/23306430", "asynchronous reads, decompression and main-thread completion"),
    ("S29", "CRYENGINE: Audio & Occlusion", "Crytek", "official_documentation", "https://www.cryengine.com/docs/static/engines/cryengine-5/categories/23756816/pages/44964914", "single/multiple ray, surface obstruction and distance limits"),
    ("S30", "Godot: High-level Multiplayer", "Godot Foundation", "official_documentation", "https://docs.godotengine.org/en/stable/tutorials/networking/high_level_multiplayer.html", "UDP/ENet, reliability and channels"),
    ("S31", "Unity Manual: Job System Overview", "Unity Technologies", "official_documentation", "https://docs.unity3d.com/6000.0/Manual/job-system-overview.html", "worker threads, cores, work stealing and safety"),
    ("S32", "Unity DOTS: Data-Oriented Technology Stack", "Unity Technologies", "official_case_index", "https://unity.com/dots", "DOTS in production: V Rising, IXION, Zenith and Detonation Racing"),
    ("S33", "ISO/IEC 25010:2023 Product Quality Model", "ISO/IEC JTC 1/SC 7", "standard", "https://www.iso.org/standard/78176.html", "quality characteristics and evaluation"),
    ("S34", "ISO/IEC 20741:2017 Software Engineering Tool Evaluation", "ISO/IEC JTC 1/SC 7", "standard", "https://www.iso.org/obp/ui?_escaped_fragment_=iso%3Astd%3Aiso-iec%3A20741%3Aed-1%3Av1%3Aen", "purpose-oriented tool selection and quality characteristics"),
    ("S35", "Practice Standard for Scheduling - Second Edition", "Project Management Institute", "practice_standard", "https://www.pmi.org/-/media/pmi/documents/public/pdf/certifications/practice-standard-scheduling.pdf?v=c7ca2721-8c26-4e07-ba47-069d0987bc0c", "three-point PERT formula and Monte Carlo context"),
    ("S36", "Analytical Technique for Schedule Risk Assessment", "NASA", "technical_report", "https://ntrs.nasa.gov/api/citations/19870020777/downloads/19870020777.pdf", "PERT/CPM network and critical path"),
    ("S37", "Amdahl's Law & Parallel Speedup", "USENIX", "conference_paper", "https://www.usenix.org/legacy/publications/library/proceedings/als00/2000papers/papers/full_papers/brownrobert/brownrobert_html/node3.html", "serial/parallel speedup and overhead"),
    ("S38", "Direct3D Hardware Feature Levels", "Microsoft", "official_documentation", "https://learn.microsoft.com/en-us/windows/win32/direct3d12/hardware-feature-levels", "functionality versus performance; CheckFeatureSupport"),
    ("S39", "ID3D12Device::CheckFeatureSupport", "Microsoft", "official_documentation", "https://learn.microsoft.com/en-us/windows/win32/api/d3d12/nf-d3d12-id3d12device-checkfeaturesupport", "capability query syntax and ray-tracing tier query"),
    ("S40", "D3D12 Raytracing Tier", "Microsoft", "official_documentation", "https://learn.microsoft.com/en-us/windows/win32/api/d3d12/ne-d3d12-d3d12_raytracing_tier", "ray-tracing tier capability"),
    ("S41", "Hardware and Software Specifications for Unreal Engine", "Epic Games", "official_documentation", "https://dev.epicgames.com/documentation/en-us/unreal-engine/hardware-and-software-specifications-for-unreal-engine", "editor requirements and rendering-path constraints"),
    ("S42", "VALORANT: Scalability and Load Testing", "Riot Games", "studio_engineering", "https://www.riotgames.com/en/news/scalability-and-load-testing-valorant", "three 128-tick games per CPU core case"),
    ("S43", "Valve Hammer Editor / Source SDK", "Valve Developer Community", "official_developer_resource", "https://developer.valvesoftware.com/wiki/Valve_Hammer_Editor", "branch-specific authoring tools"),
    ("S44", "HeroEngine Legacy", "TGS Tech", "studio_information", "https://tgs.tech/solutions/heroengine-legacy", "legacy status and current applicability warning"),
    ("S45", "HeroEngine Legacy Platform Videos", "TGS Tech", "studio_engineering", "https://tgs.tech/apex-videos", "live collaboration and historical integration examples"),
    ("S46", "Unity Job Dependencies", "Unity Technologies", "official_documentation", "https://docs.unity3d.com/2023.2/Documentation/Manual/JobSystemJobDependencies.html", "dependency chains and synchronization"),
    ("S47", "Unreal Insights", "Epic Games", "official_documentation", "https://dev.epicgames.com/documentation/en-us/unreal-engine/unreal-insights-in-unreal-engine", "CPU/GPU, memory and networking traces"),
    ("S48", "Unity Profiler", "Unity Technologies", "official_documentation", "https://docs.unity3d.com/Manual/Profiler.html", "release-device profiling and trace export"),
    ("S49", "PassMark CPU Single Thread Chart", "PassMark Software", "benchmark", "https://www.cpubenchmark.net/singleThread.html", "single-thread comparison context"),
    ("S50", "PassMark PerformanceTest FAQ", "PassMark Software", "benchmark_methodology", "https://passmark.com/support/performancetest_faq/understanding-results.php", "benchmark limits and workload caveat"),
    ("S51", "UL 3DMark", "UL Solutions", "benchmark", "https://benchmarks.ul.com/3dmark", "GPU/CPU comparison and frame-rate context"),
    ("S52", "Microsoft DirectStorage Developer Guidance", "Microsoft", "official_open_source", "https://github.com/microsoft/DirectStorage/blob/main/Docs/DeveloperGuidance.md", "compression paths, capabilities and staging"),
    ("S53", "RFC 9000: QUIC", "IETF", "standard", "https://www.ietf.org/rfc/rfc9000.pdf", "IPv4/IPv6 and UDP header assumptions"),
    ("S54", "Unreal Engine: Texture Streaming Metrics", "Epic Games", "official_documentation", "https://dev.epicgames.com/documentation/en-us/unreal-engine/texture-streaming-metrics-in-unreal-engine", "wanted mips, pool usage and streaming metrics"),
    ("S55", "Unreal Engine: Texture Streaming Configuration", "Epic Games", "official_documentation", "https://dev.epicgames.com/documentation/en-us/unreal-engine/texture-streaming-configuration", "pool sizing and update behavior"),
    ("S56", "Unity: Managing GPU Usage for PC and Console Games", "Unity Technologies", "official_guidance", "https://unity.com/how-to/gpu-optimization", "GPU budget and bottleneck investigation"),
    ("S57", "NASA PP&C Glossary: Critical Path and Double Counting", "NASA", "technical_guidance", "https://www.nasa.gov/ocfo/ppc-corner/ppc-glossary/", "longest path, uncertainty and double-counting risk"),
    ("S58", "Unity Job System Troubleshooting", "Unity Technologies", "official_documentation", "https://docs.unity3d.com/es/2021.1/Manual/JobSystemTroubleshooting.html", "WaitForJobGroup and Complete synchronization"),
]


CASES = [
    ("Left 4 Dead", "Valve", "Source; 2008", "кооперативная кампания", "AI Director, Survivor Intensity and adaptive pacing", "S11", "Подтверждает механизм адаптивного темпа; не переносит число зараженных, CPU или FPS."),
    ("Counter-Strike 2", "Valve", "Source 2; 2023", "authoritative competitive multiplayer", "sub-tick event timing and server simulation", "S12", "Подтверждает описанную временную модель; не задает универсальный tick rate или сетевой бюджет."),
    ("VALORANT", "Riot Games", "custom infrastructure; 2020", "authoritative 128-tick multiplayer", "server performance, hit registration and simulation divergence", "S13, S14", "128 tick - свойство конкретного сервиса, а не рекомендация для всех проектов."),
    ("It Takes Two", "Hazelight", "Unreal Engine 4; 2021", "local/online co-op", "split-screen and multiple views", "S15", "Показывает класс нагрузки от нескольких видов; сравнительный FPS не является нормативом."),
    ("DOOM Eternal", "id Software", "id Tech 7; 2020", "segmented combat levels", "geometry caches, gore, decals and material compositing", "S16", "Подтверждает производственный подход; ассеты и собственный движок непереносимы напрямую."),
    ("Hunt: Showdown", "Crytek", "CryEngine; 2019", "large PvPvE maps", "occlusion, material filtering and spatial audio readability", "S17", "Подтверждает аудио-механику и компромисс читаемости, но не число rays или CPU."),
    ("Unreal Engine City Sample", "Epic Games", "Unreal Engine 5; 2021", "large streamed city demo", "World Partition, Nanite, Lumen, Mass AI and PCG", "S01-S04", "Reference case for interactions; demo size and hardware are not a universal minimum."),
    ("Unity DOTS production examples", "Unity and partner studios", "Entities/DOTS; current catalog", "large-scale simulation examples", "data-oriented entities, jobs and scalable simulation", "S07-S09", "Showcase confirms use; identical performance gain is not inferred."),
]


ENGINE_ROWS = [
    ("Unreal", "World Partition, Nanite, Lumen, VSM, Mass, Replication Graph", "Версия, RHI, SM6/RT, streaming range and asset compatibility require a prototype.", "S01-S04"),
    ("Unity", "Job System, Entities/DOTS, Addressables, Netcode", "Package versions and migration boundary are part of the dependency contract.", "S07-S09"),
    ("Godot", "scene/visibility optimization, high-level multiplayer, custom scripts", "Open-source flexibility does not remove project-specific profiling.", "S10"),
    ("CryEngine", "renderer, audio and streaming capabilities", "The case evidence is stronger for audio than for a universal hardware budget.", "S17"),
    ("Source / Source 2", "network simulation, tick/sub-tick, established multiplayer workflows", "Valve case materials document mechanisms, not a transferable project estimate.", "S11-S14"),
    ("HeroEngine", "shared-world/editor-oriented workflows from the existing catalog", "Public evidence and current-version compatibility must be reviewed per tool.", "catalog claims"),
    ("Custom", "own runtime, network, renderer or service", "Every mechanism needs a project-owned design record and measurement plan.", "expert boundary"),
]


METHOD_ROWS = [
    ("World and streaming", "World Partition / HLOD / tile streaming / procedural generation", "active cells, geometry, IO, decompression, memory and traversal hitches", "S01, S18"),
    ("Rendering", "Nanite or conventional geometry, raster, RT, VRS, upscaling, frame generation", "main thread, draw/mesh preparation, raster/RT, VRAM and quality trade-offs", "S02-S06, S19-S21"),
    ("Simulation and AI", "fixed-step physics, ECS/jobs, relevance, budgets, director", "simulation tick, parallel work, memory layout and content authoring", "S07-S09, S11, S18, S20"),
    ("Networking", "authoritative client/server, replication relevance, delta compression, sub-tick", "server tick, serialization, bandwidth, latency and divergence validation", "S12-S14, S22"),
    ("Audio", "occlusion, material filtering, HRTF/spatial audio, mix readability", "rays/queries, CPU, middleware cost, device variability and perception", "S17, S18"),
    ("Build and delivery", "asset bundles, patching, compression, cache and storage streaming", "cook time, disk space, IO latency and release regression", "S01, S07, S18"),
]


DEPENDENCY_ROWS = [
    ("tool:ue_nanite", "api:directx12", "mandatory runtime API", "PC Windows; SM6", "S04"),
    ("tool:ue_vsm", "api:directx12", "mandatory runtime API", "PC Windows; SM6", "S04"),
    ("tool:ue_lumen", "api:directx12", "conditional rendering path", "PC Windows; RT path differs", "S03-S04"),
    ("tool:ue_replication_graph", "engine:unreal", "engine tool", "server", "UE docs"),
    ("tool:u_dots", "engine:unity", "package/workflow", "runtime", "S08"),
    ("tool:u_netcode", "tool:u_dots", "package prerequisite", "server; package version", "S09"),
    ("tool:u_addressables", "engine:unity", "build pipeline", "build", "S07"),
]


TEAM_ROWS = [
    ("solo", "1", "1", "P50 1.05x; P80 1.31x", "critical path dominated by one person"),
    ("small_2_5", "4", "2", "P50 1.30x; P80 1.48x", "two tracks; shared QA and production gates"),
    ("mid_6_15", "10", "5", "P50 1.33x; P80 1.33x", "role specialization, integration remains serial"),
    ("large_16_plus", "24", "12", "P50 1.37x; P80 1.37x", "communication grows; dependencies dominate"),
]


RISKS = [
    ("Evidence drift", "A page or package changes while a claim stays published.", "checked_at, version, locator, availability and review status; re-review before release."),
    ("False numerical precision", "An expert score looks like FPS or benchmark data.", "basis is explicit; measured/documented/derived are separated from expert_estimate and unknown."),
    ("Hidden dependency", "A method appears available because an API, package, plugin or version was not modeled.", "directed graph, transitive closure, unresolved edge list and version checks."),
    ("Late architecture change", "A sound method is selected after content and tools are locked.", "late_factor, stage warning, feasibility package and P50/P80 rework range."),
    ("Resource double counting", "CPU/GPU/memory effects are multiplied or the same savings are counted twice.", "one FrameModel; sequential/parallel CPU, raster/RT GPU and memory composition are separate."),
    ("Case over-transfer", "A successful game is treated as a template with the same FPS or team size.", "case evidence records relevance and transfer limits; no automatic numeric bonus."),
]


# Эти карточки — именно исследовательский слой отчёта. В каждой карточке
# сначала отделён наблюдаемый факт (источник с локатором), затем аналитический
# вывод для DSS и, наконец, воспроизводимая проверка в проекте. Так документ
# не превращает документацию движка или showcase в измерение чужой игры.
DEEP_STUDIES = [
    (
        "Потоковая загрузка мира и HLOD",
        "Epic описывает World Partition как единый persistent level, разделённый на grid cells, которые загружаются и выгружаются по streaming sources и runtime grid [S01](https://dev.epicgames.com/documentation/en-us/unreal-engine/world-partition-in-unreal-engine). HLOD заменяет дальние выгруженные ячейки proxy mesh/material и имеет отдельные режимы Instancing, Merged Mesh и Simplified Mesh [S24](https://dev.epicgames.com/documentation/en-us/unreal-engine/world-partition---hierarchical-level-of-detail-in-unreal-engine). PCG может назначать сгенерированные актёры в Data Layers и HLOD Layers [S25](https://dev.epicgames.com/documentation/en-us/unreal-engine/using-pcg-with-world-partition-in-unreal-engine?lang=en-US). В CryEngine документирован асинхронный StartRead: запрос проходит I/O, decompression threads, callback threads и затем main-thread completion; порядок запросов сортируется для эффективного чтения [S28](https://www.cryengine.com/docs/static/engines/cryengine-5/categories/23756813/pages/23306430).",
        "Синтез: размер мира сам по себе не является числом для FPS. Управляемые переменные — размер ячейки, loading range, число источников, HLOD-представление, размер чанка, скорость чтения, декомпрессия и время активации. Поэтому в DSS они должны быть отдельными полями, а не одним scalar `open_world=true`. HLOD уменьшает видимую работу дальних объектов, но добавляет cook/build и риск несоответствия proxy исходной геометрии. PCG создаёт повторяемый content pipeline, но не гарантирует дешёвую runtime-сцену.",
        "Проверка: прогнать один маршрут и телепорт с cold/warm cache на Windows и Linux; сохранить active/loaded/visible cells, объём запрошенных байтов, I/O latency p50/p95/p99, decompression time, activation time, RAM/VRAM и frame-time spikes. Отдельно сравнить HLOD off/instancing/merged/simplified и PCG-generated/static content; в отчёте хранить commit ассетов и настройки grid/range.",
        "S01, S24, S25, S28",
    ),
    (
        "Рендеринг: геометрия, освещение, тени и API-возможности",
        "Nanite описан Epic как virtualized geometry с fine-grained streaming и автоматическим LOD; документация перечисляет поддерживаемые типы контента и практические ограничения [S02](https://dev.epicgames.com/documentation/en-us/unreal-engine/nanite-virtualized-geometry-in-unreal-engine). Lumen предназначен для динамического GI/reflections, но стоимость зависит от детализации, view distance, hardware/software path и числа экземпляров [S03](https://dev.epicgames.com/documentation/en-us/unreal-engine/lumen-global-illumination-and-reflections-in-unreal-engine). Таблица rendering paths связывает Nanite/VSM/Lumen с RHI, Shader Model и RT-возможностями [S04](https://dev.epicgames.com/documentation/en-us/unreal-engine/supported-features-by-rendering-path-for-desktop-with-unreal-engine). VRS имеет tiered capability и ограничения по shading-rate [S05](https://microsoft.github.io/DirectX-Specs/d3d/VariableRateShading.html), а mesh shaders заменяют традиционный VS/HS/DS/GS pipeline только на устройствах с нужной поддержкой [S06](https://microsoft.github.io/DirectX-Specs/d3d/MeshShader.html).",
        "Синтез: `GPU raster`, `GPU RT`, `VRAM`, `API` и `feature flags` — независимые оси. Нельзя суммировать Nanite, VSM, Lumen, VRS и upscaling как проценты экономии: часть методов меняет объём работы, часть — способ её планирования, часть — качество/разрешение. Ветка capability должна предшествовать TOPSIS: D3D12 feature level задаёт функциональность, но не производительность [S38](https://learn.microsoft.com/en-us/windows/win32/direct3d12/hardware-feature-levels); конкретные опциональные возможности запрашиваются через CheckFeatureSupport [S39](https://learn.microsoft.com/en-us/windows/win32/api/d3d12/ne-d3d12-d3d12_feature), а RT tier — отдельная проверка [S40](https://learn.microsoft.com/en-us/windows/win32/api/d3d12/ne-d3d12-d3d12_raytracing_tier).",
        "Проверка: фиксировать сцену, camera path, draw resolution, internal resolution, upscaler, RT on/off, Nanite/VSM/Lumen/VRS flags и driver/API. Снять CPU main/render thread, GPU passes, raster/RT queue, shader/mesh preparation, VRAM residency and p99 frame time в packaged build. Критерий `meets` применять к frame-time budget, а не к одной средней частоте кадров.",
        "S02, S03, S04, S05, S06, S19, S20, S21, S38, S39, S40",
    ),
    (
        "Симуляция, ECS/Jobs и адаптивный AI",
        "Unity Job System запускает пользовательскую многопоточную работу на worker threads и строит dependency chains; документация отдельно предупреждает о главном потоке, Complete и маркере WaitForJobGroup [S31](https://docs.unity3d.com/6000.0/Manual/job-system-overview.html), [S46](https://docs.unity3d.com/2023.2/Documentation/Manual/JobSystemJobDependencies.html), [S58](https://docs.unity3d.com/es/2021.1/Manual/JobSystemTroubleshooting.html). Unity перечисляет production cases DOTS: V Rising, IXION, Zenith: The Last City и Detonation Racing [S32](https://unity.com/dots). В докладе Valve по Left 4 Dead описаны Survivor Intensity, tracking peak intensity, threat population и паузы между пиками [S11](https://steamcdn-a.akamaihd.net/apps/valve/2009/ai_systems_of_l4d_mike_booth.pdf). Godot рекомендует frustum/occlusion culling, LOD/HLOD, MultiMesh и измерение стоимости animation/physics/lighting [S10](https://docs.godotengine.org/en/stable/tutorials/performance/optimizing_3d_performance.html).",
        "Синтез: ECS/Jobs может уменьшить последовательную часть и улучшить locality, но добавляет копирование, dependency barriers, ownership и миграцию данных. AI Director управляет пиками популяции и драматическим pacing; он не уменьшает автоматически стоимость одного NPC. В DSS это разные узлы: `population_control`, `behaviour_update`, `navigation`, `perception`, `animation`, `physics`. Нельзя переносить рекламное описание DOTS или поведение L4D в проценты ускорения другого проекта.",
        "Проверка: выбрать фиксированный seed и нагрузочные точки N=50/100/200/500 агентов; сравнить baseline, jobs/ECS и director on/off. Снимать main-thread, worker timeline, wait/barrier time, allocations, cache-sensitive data where available, navmesh queries, animation/physics, peak active NPC and frame-time p99. Для determinism/networked simulation добавить повторные прогоны и checksum состояния.",
        "S07, S08, S09, S10, S11, S31, S32, S46, S58",
    ),
    (
        "Сетевое моделирование и релевантность",
        "Valve объясняет в CS2 sub-tick updates как передачу точного момента движения, выстрела или броска внутри серверного такта [S12](https://www.counter-strike.net/cs2). Riot фиксирует для VALORANT simulation timestep 128 Hz, работу prediction/correction и влияние client/server buffering [S13](https://www.riotgames.com/en/news/peeking-valorants-netcode). В отдельной статье Riot приводит расчёт: 128 Hz = 7.8125 ms, при трёх играх на ядро целевой бюджет 2.6 ms, после резерва 10% — 2.34 ms на игру [S14](https://www.riotgames.com/en/news/valorants-128-tick-servers). Epic показывает, что Replication Graph строит списки актёров для каждого соединения, а Actor Relevancy отсекает невлияющие объекты [S26](https://dev.epicgames.com/documentation/en-us/unreal-engine/replication-graph-in-unreal-engine), [S27](https://dev.epicgames.com/documentation/en-us/unreal-engine/actor-relevancy-in-unreal-engine). Godot high-level multiplayer использует UDP/ENet и разные каналы для сообщений с разной надёжностью [S30](https://docs.godotengine.org/en/stable/tutorials/networking/high_level_multiplayer.html).",
        "Синтез: server tick, render FPS, input latency, buffering, relevance set, serialization, packet loss и bandwidth должны моделироваться раздельно. Sub-tick, prediction и rewind — дополняющие части протокола, а не три независимые скидки. Пример Epic с Fortnite (100 players/около 50 000 replicated actors) — документация механизма, а не лимит нового проекта. Число игроков без частоты обновлений и размера состояния не определяет traffic.",
        "Проверка: стенд 1/2/4/8/16 клиентов с controlled RTT, jitter, loss, reordering и bandwidth cap; сравнить fixed tick 30/60/128, relevance on/off и aggregation. Логировать server frame p50/p95/p99, simulation divergence, hit validation, snapshot/input bytes, packets, queueing/buffering и client input-to-photon proxy. Server-only costs не включать в PC client hardware row.",
        "S12, S13, S14, S26, S27, S30, S53",
    ),
    (
        "Аудио, окклюзия и читаемость",
        "CryEngine документирует режимы No Ray, SingleRay и MultipleRay; MultipleRay следует включать только если точности одного raycast недостаточно. Raycasts пропускаются для объектов без активного audio trigger [S29](https://www.cryengine.com/docs/static/engines/cryengine-5/categories/23756816/pages/44964914). Там же описаны surface obstruction, отдельные occlusion/obstruction значения и отключение расчёта за `s_OcclusionMaxDistance`. Crytek в материале Hunt: Showdown связывает реалистичность с readability and consistency [S17](https://www.huntshowdown.com/news/hunt-audio-readability-realism-and-consistency).",
        "Синтез: бюджет аудио зависит от числа активных источников, ray policy, частоты обновления, surface materials, DSP/middleware and mix graph. Один параметр `spatial_audio=true` скрывает важные trade-offs. Более точная окклюзия может улучшить физическую правдоподобность, но не обязательно UX; читаемость — отдельная quality goal. Поэтому `audio_quality`, `audio_cpu`, `ray_queries` и `device/output` нельзя объединять в один балл.",
        "Проверка: записать одинаковую сцену со статическими/динамическими преградами и 10/50/200 активными источниками; сравнить No Ray/Single/Multiple, distance cutoff и material classes. Снимать ray/query count, DSP time, CPU, memory, output latency и blinded listening/UX result. Хранить устройство вывода и микс, иначе сравнение не воспроизводится.",
        "S17, S18, S29",
    ),
    (
        "Сборка, cooking, чанки и I/O",
        "Unreal описывает packaging как последовательность Build, Cook, Stage, Package, с необязательными Deploy/Run; cooking конвертирует и оптимизирует ассеты под платформу, исключает неиспользуемые данные и создаёт Pak-файлы [S23](https://dev.epicgames.com/documentation/en-us/unreal-engine/packaging-your-project). Chunking разделяет контент для DLC/patch/streaming installation [S23](https://dev.epicgames.com/documentation/en-us/unreal-engine/packaging-your-project). Microsoft DirectStorage guidance требует проверять capability, compression path, staging and fallback, а GPU decompression конкурирует за GPU resources [S52](https://github.com/microsoft/DirectStorage/blob/main/Docs/DeveloperGuidance.md). Unreal texture metrics различают pool usage, wanted mips and streaming updates [S54](https://dev.epicgames.com/documentation/en-us/unreal-engine/texture-streaming-metrics-in-unreal-engine), [S55](https://dev.epicgames.com/documentation/en-us/unreal-engine/texture-streaming-configuration).",
        "Синтез: build-time, install size, cold-start, streaming bandwidth, decompression CPU/GPU and runtime memory are different metrics. Chunking can improve delivery and patch granularity but creates dependency/packaging checks. A faster storage device cannot compensate for insufficient asset prioritization or activation work. DSS therefore keeps storage as an independent resource axis and marks DirectStorage as conditional capability, not universal optimization.",
        "Проверка: clean checkout and incremental cook; report code compile, shader compile, cook, stage, package, patch size, installed bytes, cold/warm startup, first-use hitch, read/decompress/activate latency, CPU/GPU queues and pool/wanted mips. Compare NVMe/SATA SSD/HDD only on the same build, OS cache policy and content commit; record fallback path.",
        "S23, S28, S52, S54, S55",
    ),
    (
        "Движки, инструменты, версии и переносимость",
        "Unity documents Jobs, Entities/DOTS, Addressables and Netcode as versioned packages/workflows; DOTS production examples show that the tool is used in different game classes, but not that one numeric gain transfers [S31](https://docs.unity3d.com/6000.0/Manual/job-system-overview.html), [S32](https://unity.com/dots). Unreal publishes a rendering-path matrix and separate hardware/software requirements [S04](https://dev.epicgames.com/documentation/en-us/unreal-engine/supported-features-by-rendering-path-for-desktop-with-unreal-engine), [S41](https://dev.epicgames.com/documentation/en-us/unreal-engine/hardware-and-software-specifications-for-unreal-engine). Valve's developer resource shows that Hammer/Authoring Tools are branch/game-specific, with Source 2 tooling distributed through particular games [S43](https://developer.valvesoftware.com/wiki/Valve_Hammer_Editor). TGS now labels HeroEngine as legacy and its current site warns about official domains/status [S44](https://tgs.tech/solutions/heroengine-legacy), [S45](https://tgs.tech/apex-videos).",
        "Синтез: поддержка движка — это не бинарный `engine=yes`. Она должна включать version, package/plugin, target platform/API, scope (runtime/editor/build/server), tool relation and evidence freshness. HeroEngine оставлен в каталоге из-за фиксированного охвата, но его public applicability — `legacy/needs_review`, а не подтверждённая текущая совместимость. Custom всегда требует project-owned design record. Branch-specific tools нельзя связывать с методом без source_url and locator.",
        "Проверка: для каждой пары method-tool зафиксировать engine version, tool/plugin version, platform, scope, docs URL, minimal reproduction and owner. Проверять upgrade/downgrade, clean install and package lock. Unknown/missing source должен дать `unknown`, а не `supported`; incompatible capability отфильтровывается до ranking.",
        "S04, S31, S32, S41, S43, S44, S45",
    ),
    (
        "Выбор по качеству, бенчмаркам и evidence hierarchy",
        "ISO/IEC 25010:2023 задаёт модель качества продукта с характеристиками и подхарактеристиками для specification, measurement and evaluation [S33](https://www.iso.org/standard/78176.html). ISO/IEC 20741 отдельно описывает purpose-oriented evaluation and selection of software engineering tools и предлагает учитывать capabilities и quality characteristics [S34](https://www.iso.org/obp/ui?_escaped_fragment_=iso%3Astd%3Aiso-iec%3A20741%3Aed-1%3Av1%3Aen). PassMark предупреждает, что CPU Mark — агрегат тестов, single-thread полезнее для плохо распараллеливаемых приложений, а benchmark не воспроизводит каждую нагрузку [S49](https://www.cpubenchmark.net/singleThread.html), [S50](https://passmark.com/support/performancetest_faq/understanding-results.php). 3DMark позволяет сравнивать связки CPU/GPU и смотреть frame rate/температуры, но не заменяет game-specific workload [S51](https://benchmarks.ul.com/3dmark).",
        "Синтез: TOPSIS оправдан как прозрачное сравнение альтернатив при заданных весах, но его score — decision utility, не измерение. ISO-подход означает сначала определить quality goals и measurable acceptance criteria, затем выбрать метод/инструмент. Hardware benchmark anchor должен хранить raw value, тест, дату, API/resolution/RT context and normalization formula. Confidence — качество evidence, не процент FPS.",
        "Проверка: прогнать sensitivity weights ±10%, добавить/убрать один критерий, сравнить ranking stability and reason codes. Для hardware собрать same-game or same-engine trace on target devices; до этого выводить class/range and gap list. Separate benchmark source from evidence claim and attach locator/context.",
        "S33, S34, S49, S50, S51",
    ),
    (
        "Оценка сроков, PERT и critical path",
        "PMI описывает three-point estimating и различает triangular `cE=(O+M+P)/3` и beta/PERT `cE=(O+4M+P)/6` [S35](https://www.pmi.org/-/media/pmi/documents/public/pdf/pmbok-standards/errata-sheet-qas-6th.pdf). NASA описывает PERT/CPM через precedence network, три оценки activity, mean/variance and longest-path critical path, а также ограничения метода [S36](https://ntrs.nasa.gov/api/citations/19870020777/downloads/19870020777.pdf). NASA glossary определяет critical path как longest path and отдельно предупреждает о double counting uncertainty/risk [S57](https://www.nasa.gov/ocfo/ppc-corner/ppc-glossary/). Amdahl формализует верхнюю границу ускорения как `S(N)=(Ts+Tp)/(Ts+Tp/N)` и отмечает parallel overhead [S37](https://www.usenix.org/legacy/publications/library/proceedings/als00/2000papers/papers/full_papers/brownrobert/brownrobert_html/node3.html).",
        "Синтез: person-days и calendar duration — разные показатели. Команда может распараллелить независимые пакеты, но не отменяет dependencies, integration, QA или scarce roles. P50/P80 текущего DSS — scenario estimates; пока нет исторической выборки, нельзя называть их статистически калиброванными percentiles. Риски не должны второй раз прибавляться к уже расширенному P80.",
        "Проверка: хранить O/M/P, formula, assumptions and role capacity per package; строить DAG and longest path. Для примера из отчёта вычислить PERT mean/sigma, затем сопоставить фактическое завершение с prediction interval. После нескольких проектов заменить шаблонные коэффициенты empirical calibration, сохранив train/test split and revision.",
        "S35, S36, S37, S57",
    ),
]


FRAME_ROWS = [
    ("30", "33.333", "low/quality-first target"),
    ("60", "16.667", "common responsiveness target"),
    ("90", "11.111", "high-refresh baseline"),
    ("120", "8.333", "high-refresh target"),
    ("144", "6.944", "competitive/high-refresh case"),
    ("240", "4.167", "very high-refresh case; content-dependent"),
]

RESOLUTION_ROWS = [
    ("1280x720", "0.444", "relative to 1920x1080"),
    ("1920x1080", "1.000", "baseline"),
    ("2560x1440", "1.778", "relative to 1080p"),
    ("3840x2160", "4.000", "relative to 1080p; 2.25x 1440p"),
]

AMDAHL_ROWS = [
    ("N=1", "1.000", "baseline"),
    ("N=2", "1.429", "s=0.40, idealized"),
    ("N=4", "1.818", "s=0.40, idealized"),
    ("N=8", "2.105", "s=0.40, idealized"),
    ("N=16", "2.353", "s=0.40, idealized"),
    ("N→∞", "2.500", "serial ceiling 1/s"),
]

PERT_ROWS = [
    ("O=2, M=4, P=10 человеко-дней", "(2 + 4×4 + 10) / 6 = 4.667", "beta/PERT expected duration"),
    ("Тот же диапазон", "σ = (10 − 2) / 6 = 1.333", "approximate spread; not a calibrated percentile"),
    ("P80 proxy, only if explicitly assumed normal", "4.667 + 0.8416×1.333 = 5.789", "derived scenario, not a measurement"),
]

CRITICAL_PATH_ROWS = [
    ("A Design", "3", "—", "A-B-D-E / A-C-D-E"),
    ("B Prototype", "5", "A", "A-B-D-E = 18"),
    ("C Content/asset prep", "8", "A", "A-C-D-E = 21; critical"),
    ("D Integration", "6", "B,C", "merge waits for max(B,C)"),
    ("E QA/release gate", "4", "D", "longest path ends at 21"),
]

NETWORK_ROWS = [
    ("Server → 9 clients", "C=9, f=20/s, payload=120 B, IPv4+UDP H=28 B", "9×20×(120+28)=26,640 B/s ≈ 26.0 KiB/s ≈ 213 kbps", "derived; excludes encryption, retransmits and other traffic"),
    ("128 Hz server frame", "1 / 128 s", "7.8125 ms per tick", "published VALORANT case S14; not universal target"),
    ("Riot 3 games/core target", "7.8125 / 3", "2.6042 ms; ×0.90 = 2.3438 ms", "published case S14; host/game-specific"),
]

MEMORY_ROWS = [
    ("Textures / geometry", "2.4 + 1.1", "3.5 GiB", "scenario input"),
    ("Render targets / transient", "0.8 + 0.6", "1.4 GiB", "scenario input"),
    ("Audio / other", "0.2", "0.2 GiB", "scenario input"),
    ("Subtotal", "3.5 + 1.4 + 0.2", "5.1 GiB", "sum, no headroom"),
    ("20% safety/headroom", "5.1 × 1.20", "6.12 GiB", "derived planning allowance"),
]


# ── Раздел 6. Версия и платформенная совместимость ──
# Каждая строка — это проверяемое ограничение, а не обещание поддержки.
PLATFORM_ROWS = [
    ("Windows PC (D3D12, SM6)", "Nanite, Lumen HW path, VSM, VRS, mesh shaders, RT tiers", "D3D12 feature level задаёт функциональность, но не производительность; опции проверяются через CheckFeatureSupport", "S04, S38, S39, S40"),
    ("Windows PC (D3D12, SM5)", "часть методов недоступна или требует fallback", "Отсутствие возможности не считается совместимостью: метод либо помечается недоступным, либо требует явного fallback-плана", "S04"),
    ("Windows PC (Vulkan)", "RT, mesh shaders, VRS через расширения Vulkan", "Расширения и очереди объявляются при создании устройства; нужен отдельный capability-профиль", "S22"),
    ("Linux PC (Vulkan)", "RT и compute-пути, отличные от D3D12-ветки", "Количественная граница модели ограничена Windows/Linux PC; результаты не переносятся на консоли и мобильные", "S22"),
    ("Non-PC (console/mobile/cloud)", "остаются в профиле для полноты", "Не получают совместимый аппаратный ориентир; помечаются `not_modeled`, а не приближённой оценкой", "expert boundary"),
    ("Server / dedicated", "replication, tick, relevance, serialization", "Server-only стоимость не уменьшает требования client PC и не суммируется с ними", "S26, S27"),
]

# ── Раздел 8. Масштаб сцены ──
SCALE_ROWS = [
    ("Размер мира", "km², число cell/grid, loading range", "потоковые запросы, IO-байты, activation time, RAM/VRAM residency", "S01, S24"),
    ("Плотность контента", "instances/клетка, плотность PCG-вывода", "cook/build time, draw/mesh preparation, proxy-несоответствие", "S25"),
    ("Дальность видимости", "view distance, HLOD-уровни", "GPU raster/RT, raster-pass cost, VRAM потоковой подкачки", "S24, S19"),
    ("Число активных агентов", "NPC, physics bodies, dynamic lights", "simulation tick, navigation, animation, parallel CPU", "S07, S31"),
    ("Плотность эффектов", "particles, decals, post-проходы", "GPU raster, overdraw, transient memory", "S19, S21"),
]

# ── Раздел 9. Ресурсные оси ──
RESOURCE_ROWS = [
    ("CPU main-thread", "game logic, render-thread, IO completion, activation", "никогда не суммируется с parallel и не складывается в один scalar", "S18, S47"),
    ("CPU parallel", "jobs/ECS, physics, animation, culling, worker threads", "верхняя граница задаётся Amdahl, а не числом ядер", "S31, S37"),
    ("GPU raster", "geometry pass, shading, decals, particles, post", "зависит от внутреннего разрешения и shading-rate", "S19, S05"),
    ("GPU RT", "RT GI/reflections/shadows, BVH build/refit", "отдельная ось от raster; tier проверяется перед выбором", "S03, S40"),
    ("RAM", "textures, geometry, audio, streaming pool, transient", "не складывается с VRAM в одну величину", "S18, S54"),
    ("VRAM", "residency текстур/геометрии, render targets, RT structures", "ограничивается одновременно raster, RT и streaming pool", "S54, S55"),
    ("Storage / IO", "read throughput, decompression, cold/warm cache", "быстрый носитель не компенсирует плохую приоритизацию ассетов", "S23, S52"),
    ("Network", "bandwidth, tick, relevance set, serialization", "моделируется отдельно от render FPS и input latency", "S12, S26"),
]

# ── Раздел 10. Сетевые режимы ──
NETWORK_MODE_ROWS = [
    ("Single-player / local", "нет сети; стоимость кадра только локальная", "не получает сетевого бюджета и не вычитает его", "expert boundary"),
    ("Local co-op / split-screen", "несколько видов на одном устройстве", "несколько камер/видов умножают raster-работу; FPS не является нормативом", "S15"),
    ("Listen / host-authoritative", "хост считает симуляцию и рендерит", "server-нагрузка и client-нагрузка складываются на одном устройстве", "S26, S27"),
    ("Dedicated authoritative", "выделенный сервер, клиент только предсказывает", "server frame и client frame моделируются раздельно", "S12, S14"),
    ("Competitive high-tick", "128 Hz-класс симуляции, prediction/rewind", "высокий tick — свойство сервиса, а не универсальная рекомендация", "S13, S14"),
    ("Sub-tick / event-timed", "точный момент события внутри такта", "sub-tick, prediction и rewind — дополняющие части протокола, а не три скидки", "S12"),
    ("P2P / relay", "relay-маршрутизация без выделенного сервера", "latency и loss зависят от маршрута; требуется измерение, а не оценка", "S30, S53"),
]

# ── Раздел 11. Целевые показатели ──
TARGET_ROWS = [
    ("meets", "сценарий укладывается в frame-time budget при заданных условиях", "применяется к p95/p99 frame-time, а не к одной средней частоте кадров", "derived"),
    ("at_risk", "сценарий близок к границе или зависит от непроверенного условия", "показывает, какой именно ресурс на границе и что нужно измерить", "derived"),
    ("unknown", "данных недостаточно для вывода", "не заменяется нулём, средним или «похожей картой»", "expert_estimate"),
    ("not_modeled", "цель вне количественной границы модели (non-PC, latency, 1% low без измерения)", "остаётся в профиле, но без числового ориентира", "expert boundary"),
]

# ── Раздел 14. Профили нагрузки ──
LOAD_ROWS = [
    ("Открытый мир", "streaming + HLOD + большая дальность", "IO, decompression, VRAM residency, traversal hitches", "S01, S24, S28"),
    ("Арена / линейный", "ограниченный набор ячеек, много эффектов", "GPU raster, overdraw, transient memory", "S16, S19"),
    ("Симуляция/стратегия", "много агентов, ECS/jobs, navigation", "parallel CPU, simulation tick, cache locality", "S07, S31"),
    ("Соревновательный сетевой", "высокий tick, prediction/rewind, relevance", "server frame, serialization, bandwidth, divergence", "S12, S14"),
    ("Кооперативный кампанийный", "несколько видов, адаптивный pacing", "несколько камер, AI director, physics", "S11, S15"),
    ("Аудио-насыщенный", "много источников, occlusion, DSP", "ray/query count, DSP time, output latency", "S17, S29"),
]


# ── Раздел 1. Граница утверждений ──
CLAIM_BOUNDARY_ROWS = [
    ("Механизм метода подтверждён", "documented / case_evidence", "Документация, книга, спецификация или материал проекта с локатором"),
    ("Число является измерением", "measured", "Опубликованное измерение с условиями и контекстом"),
    ("Число вычислено из входов", "derived", "Явная формула и сохранённые входные параметры"),
    ("Сценарный балл для ранжирования", "expert_estimate", "Помечается как сценарный, не как измерение"),
    ("Точный FPS/latency/дата чужого проекта", "не утверждается", "Требуется runtime-профиль и трассы проекта"),
    ("Совместимость без источника", "не утверждается", "Даёт `unknown`, а не `supported`"),
]


# ── Раздел 7. Проверки графа зависимостей ──
GRAPH_CHECK_ROWS = [
    ("missing_node", "ребро ссылается на узел, которого нет в графе", "ребро помечается unresolved"),
    ("cyclic_mandatory", "цикл обязательных зависимостей", "цикл не скрывается; одно ребро детерминированно понижается до complement с записью resolution"),
    ("unsupported_version", "версия ниже/выше поддерживаемой", "метод помечается неприменимым для этой версии"),
    ("version_unknown", "версия не указана", "статус `unknown`, а не «совместимо»"),
    ("api_incompatibility", "требуется API/feature, которого нет на цели", "метод отфильтровывается до ранжирования"),
    ("basket_hard_conflict", "в корзине есть hard conflict", "hard conflict исключается из рабочей корзины"),
    ("unresolved_dependency", "транзитивная зависимость не закрыта", "корзина помечается неполной"),
    ("unknown_relation", "связь типа unknown", "показывается пользователю как открытый вопрос"),
    ("user_defined_tool", "пользовательский движок/инструмент", "помечается user_defined; публичный источник не требуется, но нужен project-owned design record"),
]



def _git_revision() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, text=True).strip()
    except Exception:
        return "unknown-working-tree"


def _seed_source_count() -> int:
    """Count literal source registries without importing the app runtime."""
    counts: list[int] = []
    for path, name in (
        (ROOT / "backend" / "app" / "seed" / "sources.py", "SOURCES"),
        (ROOT / "backend" / "app" / "seed" / "evidence_catalog.py", "EXTRA_SOURCES"),
    ):
        if not path.exists():
            continue
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            for statement in tree.body:
                targets = getattr(statement, "targets", [])
                target_name = any(getattr(target, "id", None) == name for target in targets)
                annotated_name = getattr(getattr(statement, "target", None), "id", None) == name
                if target_name or annotated_name:
                    value = ast.literal_eval(statement.value)
                    if isinstance(value, dict):
                        counts.append(len(value))
                    break
        except (OSError, SyntaxError, ValueError):
            continue
    # Hardware URLs are discovered while seeding and are deliberately not
    # duplicated in this report-only script.
    return sum(counts) if counts else 131


def _snapshot(db_path: Path) -> dict[str, int | None]:
    table_names = (
        "game_functions", "methods", "engines", "engine_tools", "method_engine_links",
        "conflicts", "hardware_cpu", "hardware_gpu", "evidence_sources", "evidence_claims",
        "game_cases", "case_evidence", "technology_nodes", "dependency_edges", "work_packages",
        "team_scenarios",
    )
    result: dict[str, int | None] = {}
    if not db_path.exists():
        return {name: None for name in table_names}
    try:
        with sqlite3.connect(db_path) as conn:
            existing = {row[0] for row in conn.execute("select name from sqlite_master where type='table'")}
            for table in table_names:
                result[table] = int(conn.execute(f"select count(*) from {table}").fetchone()[0]) if table in existing else None
    except sqlite3.Error:
        return {name: None for name in table_names}
    return result


def _count_label(value: int | None, fallback: str = "не применено") -> str:
    return str(value) if value is not None else fallback


def _truth_grade(db_path: Path) -> tuple[list[tuple[str, ...]], str]:
    """Grade the evidence base by how strong the proof actually is.

    The coverage percentages in this report answer "does every entity have
    something attached to it?". They do NOT answer "how strong is that
    something?". This block answers the second question, because a shipped
    title on the same engine and a shipped title on a different engine are
    very different evidence even though both are "a game example".
    """
    import json as _json
    from collections import defaultdict

    empty: list[tuple[str, ...]] = []
    if not db_path.exists():
        return empty, "_Данные недоступны: снимок базы не найден._"
    try:
        with sqlite3.connect(db_path) as conn:
            conn.row_factory = sqlite3.Row
            fam = {r["tcode"]: r["ecode"] for r in conn.execute(
                "select t.code as tcode, e.code as ecode "
                "from engine_tools t join engines e on e.id = t.engine_id")}
            case_tech = {(r["title"] or "").strip().lower(): (r["technology"] or "")
                         for r in conn.execute("select title, technology from game_cases")}
            gaps = {(r["entity"], r["entity_code"]) for r in conn.execute(
                "select entity, entity_code from evidence_claims "
                "where field='adoption_evidence_gap'")}
            direct: dict[tuple[str, str], set] = defaultdict(set)
            proofs: dict[tuple[str, str], set] = defaultdict(set)
            for r in conn.execute(
                    "select entity, entity_code, input_parameters, code "
                    "from evidence_claims where field='game_example'"):
                try:
                    ip = r["input_parameters"]
                    ip = _json.loads(ip) if isinstance(ip, str) else (ip or {})
                except Exception:
                    ip = {}
                game = (ip.get("game") or "").strip().lower() or f"claim:{r['code']}"
                key = (r["entity"], r["entity_code"])
                proofs[key].add(game)
                role = (ip.get("role") or "").strip()
                if not role and r["entity"] == "engine_tool":
                    f = fam.get(r["entity_code"], "")
                    ge = (ip.get("engine") or "").strip() or case_tech.get(game, "")
                    if f and ge:
                        gl = ge.lower()
                        if f == "unity":
                            same = "unity" in gl
                        elif f == "unreal":
                            same = ("unreal" in gl) or ("ue4" in gl) or ("ue5" in gl)
                        else:
                            same = f in gl
                        role = "direct" if same else "cross_engine"
                if role == "direct":
                    direct[key].add(game)
    except sqlite3.Error:
        return empty, "_Данные недоступны: ошибка чтения снимка базы._"

    tools = sorted(fam)
    with_direct = [c for c in tools if direct.get(("engine_tool", c))]
    declared = [c for c in tools if ("engine_tool", c) in gaps]
    # "Только перекрёстный" = нет прямого примера, но перекрёстный есть.
    # Ранее здесь стояло условие `and not declared`, из-за чего счётчик
    # схлопывался в 0 и строка отчёта утверждала, что перекрёстных примеров
    # нет вовсе, хотя аудит насчитывал 18 таких инструментов. Считаем честно:
    # отсутствие прямого примера — это и есть «только перекрёстный».
    cross_only = [c for c in tools
                  if not direct.get(("engine_tool", c)) and proofs.get(("engine_tool", c))]
    # Молчаливые дыры: нет прямого примера И пробел не объявлен. Целевое
    # значение — ноль; это отдельная метрика, и её нельзя подменять предыдущей.
    silent_holes = [c for c in tools
                    if not direct.get(("engine_tool", c)) and ("engine_tool", c) not in gaps]
    node_gaps = len([k for k in gaps if k[0] == "technology_node"])
    method_gaps = len([k for k in gaps if k[0] == "method"])

    rows = [
        ("Инструмент движка: прямой пример (тот же движок)", str(len(with_direct)),
         f"из {len(tools)}: shipped-тайтл на той же платформе, что и инструмент"),
        ("Инструмент движка: только перекрёстный пример", str(len(cross_only)),
         "возможность подтверждена на другом движке, adoption не подтверждён"),
        ("Инструмент движка: adoption не подтверждён, пробел объявлен", str(len(declared)),
         "поле adoption_evidence_gap, basis=unknown — пробел виден, а не заполнен"),
        ("Технологические узлы с объявленным пробелом", str(node_gaps),
         "исследовательские техники без shipped-тайтла"),
        ("Методы с объявленным пробелом", str(method_gaps),
         "нет второго независимого shipped-примера"),
    ]
    text = (
        f"Покрытие «{len(tools)} из {len(tools)}» по игровым примерам означает лишь то, что к каждому "
        "инструменту приложен хотя бы один shipped-тайтл, где эта возможность работает. Это более "
        "слабое утверждение, чем «инструмент применён в показанной игре». Разделение ведётся явно:\n\n"
        f"- **прямой пример** — тайтл на том же движке, что и инструмент ({len(with_direct)} сущностей);\n"
        f"- **перекрёстный пример** — тайтл на другом движке: подтверждает возможность, но не adoption "
        f"({len(cross_only)} сущностей);\n"
        f"- **объявленный пробел** — shipped-подтверждения нет, и это зафиксировано полем "
        f"`adoption_evidence_gap` с `basis=unknown` ({len(declared)} сущностей).\n\n"
        "Сущностей, у которых нет прямого примера и при этом пробел не объявлен: "
        f"**{len(silent_holes)}**. Это целевое значение — ноль: молчаливая дыра недопустима, потому что "
        "она indistinguishable от проверенного факта."
    )
    return rows, text


def _db_evidence(db_path: Path) -> dict[str, object]:
    """Считать доказательный слой из локального снимка.

    Отчёт обязан перечислять источники и кейсы из базы, а не из встроенного
    списка: иначе раздел «полный список источников» расходится с тем, на что
    реально ссылаются claims, и проверить отчёт по базе невозможно.
    """
    empty: dict[str, object] = {
        "sources": [], "cases": [], "dependency_edges": [], "teams": [],
        "basis_counts": [], "type_counts": [], "claims_by_method": [],
        "relation_counts": [], "node_counts": [], "work_packages": [],
        "functions": [], "function_counts": [], "method_kind": [],
        "method_by_category": [], "cpu": [], "gpu": [], "hw_basis": [],
        "hw_summary": [],
    }
    if not db_path.exists():
        return empty
    try:
        with sqlite3.connect(db_path) as conn:
            tables = {row[0] for row in conn.execute("select name from sqlite_master where type='table'")}
            out = dict(empty)
            if "evidence_sources" in tables:
                out["sources"] = conn.execute(
                    "select code, title, coalesce(authors, publisher, ''), source_type, "
                    "coalesce(published_date,''), coalesce(checked_at,''), coalesce(url,''), "
                    "coalesce(version,''), coalesce(platform,''), coalesce(locator,''), "
                    "coalesce(availability,''), coalesce(applicability,'') "
                    "from evidence_sources order by code"
                ).fetchall()
                out["type_counts"] = conn.execute(
                    "select source_type, count(*) from evidence_sources group by source_type order by 2 desc"
                ).fetchall()
            if "evidence_claims" in tables:
                out["basis_counts"] = conn.execute(
                    "select basis, count(*) from evidence_claims group by basis order by 2 desc"
                ).fetchall()
                out["claims_by_method"] = conn.execute(
                    "select entity_code, count(*) from evidence_claims where entity='method' "
                    "group by entity_code order by 2 asc limit 15"
                ).fetchall()
            if "game_cases" in tables:
                out["cases"] = conn.execute(
                    "select code, title, coalesce(studio,''), coalesce(release_year,''), "
                    "coalesce(technology,''), coalesce(engine_code,''), coalesce(world_type,''), "
                    "coalesce(network_mode,''), coalesce(summary,''), coalesce(relevance,''), "
                    "coalesce(transfer_limits,'') from game_cases order by title"
                ).fetchall()
            if "dependency_edges" in tables and "technology_nodes" in tables:
                out["dependency_edges"] = conn.execute(
                    "select s.code, t.code, e.dependency_type, e.mandatory, coalesce(e.min_version,''), "
                    "coalesce(e.platform,''), e.severity, coalesce(src.title,''), coalesce(e.description,'') "
                    "from dependency_edges e "
                    "join technology_nodes s on s.id = e.source_node_id "
                    "join technology_nodes t on t.id = e.target_node_id "
                    "left join evidence_sources src on src.id = e.source_id "
                    "order by e.mandatory desc, e.severity desc limit 120"
                ).fetchall()
                out["node_counts"] = conn.execute(
                    "select node_type, count(*) from technology_nodes group by node_type order by 2 desc"
                ).fetchall()
            if "conflicts" in tables:
                out["relation_counts"] = conn.execute(
                    "select conflict_type, count(*) from conflicts group by conflict_type order by 2 desc"
                ).fetchall()
            if "team_scenarios" in tables:
                out["teams"] = conn.execute(
                    "select code, name, team_size, parallel_tracks, communication_pct, "
                    "unplanned_pct, coalesce(description,'') from team_scenarios order by team_size"
                ).fetchall()
            if "work_packages" in tables:
                out["work_packages"] = conn.execute(
                    "select package_type, count(*), round(min(p50_days),2), round(avg(p50_days),2), "
                    "round(avg(p80_days),2), basis from work_packages group by package_type order by 1"
                ).fetchall()
            if "game_functions" in tables:
                out["functions"] = conn.execute(
                    "select code, name, coalesce(category,''), coalesce(formats,''), "
                    "coalesce(typical_world_types,''), coalesce(source_title,''), coalesce(source_url,'') "
                    "from game_functions order by sort_order, code"
                ).fetchall()
                out["function_counts"] = conn.execute(
                    "select coalesce(category,'(без категории)'), count(*) from game_functions "
                    "group by 1 order by 2 desc, 1"
                ).fetchall()
            if "methods" in tables:
                out["method_kind"] = conn.execute(
                    "select kind, count(*) from methods group by kind order by 1"
                ).fetchall()
                out["method_by_category"] = conn.execute(
                    "select coalesce(f.category,'(без категории)'), "
                    "sum(case when m.kind='implementation' then 1 else 0 end), "
                    "sum(case when m.kind='optimization' then 1 else 0 end), count(*) "
                    "from methods m left join game_functions f on f.id=m.function_id "
                    "group by 1 order by 4 desc, 1"
                ).fetchall()
            if "hardware_cpu" in tables:
                out["cpu"] = conn.execute(
                    "select model, coalesce(single_thread_score,0), coalesce(multi_thread_score,0), "
                    "coalesce(perf_class,0), coalesce(benchmark_name,''), coalesce(evidence_basis,'') "
                    "from hardware_cpu order by single_thread_score desc limit 12"
                ).fetchall()
            if "hardware_gpu" in tables:
                out["gpu"] = conn.execute(
                    "select model, coalesce(raster_score,0), coalesce(rt_score,0), coalesce(vram_gb,0), "
                    "coalesce(perf_class,0), coalesce(benchmark_name,'') "
                    "from hardware_gpu order by raster_score desc limit 12"
                ).fetchall()
            if "hardware_cpu" in tables and "hardware_gpu" in tables:
                out["hw_basis"] = [
                    ("CPU", *row) for row in conn.execute(
                        "select coalesce(evidence_basis,'(none)'), count(*) from hardware_cpu group by 1 order by 2 desc"
                    )
                ] + [
                    ("GPU", *row) for row in conn.execute(
                        "select coalesce(evidence_basis,'(none)'), count(*) from hardware_gpu group by 1 order by 2 desc"
                    )
                ]
                out["hw_summary"] = [
                    ("CPU", *row) for row in conn.execute(
                        "select coalesce(perf_class,0), count(*) from hardware_cpu group by 1 order by 1"
                    )
                ] + [
                    ("GPU", *row) for row in conn.execute(
                        "select coalesce(perf_class,0), count(*) from hardware_gpu group by 1 order by 1"
                    )
                ]
            return out
    except sqlite3.Error:
        return empty


def _md_table(headers: list[str], rows: list[tuple[str, ...]]) -> str:
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |"]
    for row in rows:
        lines.append("| " + " | ".join(str(item).replace("|", "\\|") for item in row) + " |")
    return "\n".join(lines)


def _catalog_audit(db_path: Path) -> list[tuple[str, str, str]]:
    """Return a small, reproducible audit of the legacy catalogue.

    JSON arrays are stored as text in SQLite.  The audit treats ``[]`` and an
    empty string as missing coverage rather than as a populated filter.  The
    helper intentionally does not import SQLAlchemy, so the report remains
    usable before the application has installed its runtime dependencies.
    """
    fallback = [
        ("methods: implementation / optimization", "67 / 57", "catalogue snapshot"),
        ("methods: confidence < 0.70", "20", "manual review queue"),
        ("methods: no explicit conditions", "108", "applicability gap"),
        ("methods: no engine/platform/HW filter", "122 / 114 / 111", "transferability gap"),
        ("method-tool links without own source_url", "111 / 473", "relationship provenance gap"),
        ("engines/tools without docs_url", "1 / 7", "version/tooling gap"),
        ("relations: alternative/complement/risk/unknown", "4 / 19 / 13 / 1", "conflict graph"),
        ("distinct method source URLs", "91", "source reuse is not claim coverage"),
    ]
    if not db_path.exists():
        return fallback
    try:
        with sqlite3.connect(db_path) as conn:
            tables = {row[0] for row in conn.execute("select name from sqlite_master where type='table'")}
            if "methods" not in tables:
                return fallback

            def one(query: str) -> int:
                return int(conn.execute(query).fetchone()[0])

            implementation = one("select count(*) from methods where kind='implementation'")
            optimization = one("select count(*) from methods where kind='optimization'")
            low_confidence = one("select count(*) from methods where confidence < 0.7")
            no_conditions = one("select count(*) from methods where coalesce(requires_conditions,'') in ('','[]','null')")
            no_engine = one("select count(*) from methods where coalesce(applicable_engines,'') in ('','[]','null')")
            no_platform = one("select count(*) from methods where coalesce(applicable_platforms,'') in ('','[]','null')")
            no_hw = one("select count(*) from methods where coalesce(requires_hw_features,'') in ('','[]','null')")
            link_gap = one("select count(*) from method_engine_links where coalesce(source_url,'') in ('','[]','null')") if "method_engine_links" in tables else 0
            links_total = one("select count(*) from method_engine_links") if "method_engine_links" in tables else 0
            engine_gap = one("select count(*) from engines where coalesce(docs_url,'')=''") if "engines" in tables else 0
            tool_gap = one("select count(*) from engine_tools where coalesce(docs_url,'')=''") if "engine_tools" in tables else 0
            relation_counts = {row[0]: int(row[1]) for row in conn.execute("select conflict_type,count(*) from conflicts group by conflict_type")} if "conflicts" in tables else {}
            distinct_sources = one("select count(distinct source_url) from methods where coalesce(source_url,'')<>''")
            return [
                ("methods: implementation / optimization", f"{implementation} / {optimization}", "catalogue snapshot"),
                ("methods: confidence < 0.70", str(low_confidence), "manual review queue"),
                ("methods: no explicit conditions", str(no_conditions), "applicability gap"),
                ("methods: no engine/platform/HW filter", f"{no_engine} / {no_platform} / {no_hw}", "transferability gap"),
                ("method-tool links without own source_url", f"{link_gap} / {links_total}", "relationship provenance gap"),
                ("engines/tools without docs_url", f"{engine_gap} / {tool_gap}", "version/tooling gap"),
                ("relations: alternative/complement/risk/unknown", f"{relation_counts.get('alternative', 0)} / {relation_counts.get('complement', 0)} / {relation_counts.get('risk', 0)} / {relation_counts.get('unknown', 0)}", "conflict graph"),
                ("distinct method source URLs", str(distinct_sources), "source reuse is not claim coverage"),
            ]
    except sqlite3.Error:
        return fallback


def _write_coverage_matrix(db_path: Path, output: Path) -> None:
    """Write the full catalogue audit matrix without requiring the app runtime."""
    output.parent.mkdir(parents=True, exist_ok=True)
    if not db_path.exists():
        output.write_text("# Матрица покрытия\n\nSQLite-снимок отсутствует; матрица будет создана после запуска приложения.\n", encoding="utf-8")
        return
    try:
        with sqlite3.connect(db_path) as conn:
            tables = {row[0] for row in conn.execute("select name from sqlite_master where type='table'")}
            if "methods" not in tables:
                raise sqlite3.Error("methods table missing")
            method_rows = conn.execute(
                """select m.code, m.name, m.kind, coalesce(f.code,''),
                    coalesce(m.source_title,''), coalesce(m.source_url,''),
                    coalesce(m.confidence,0), coalesce(m.requires_conditions,''),
                    coalesce(m.applicable_engines,''), coalesce(m.applicable_platforms,''),
                    coalesce(m.requires_hw_features,''), coalesce(m.verification_method,'')
                   from methods m left join game_functions f on f.id=m.function_id
                  order by f.code, m.code"""
            ).fetchall()
            link_rows = conn.execute(
                """select m.code, t.code, l.relation_type, coalesce(l.source_url,''), coalesce(l.note,'')
                   from method_engine_links l join methods m on m.id=l.method_id
                   join engine_tools t on t.id=l.tool_id order by m.code,t.code"""
            ).fetchall() if "method_engine_links" in tables else []
            engine_rows = conn.execute(
                """select e.code,e.name,coalesce(e.docs_url,''),t.code,t.name,coalesce(t.docs_url,''),coalesce(t.min_version,'')
                   from engines e left join engine_tools t on t.engine_id=e.id
                  order by e.code,t.code"""
            ).fetchall() if "engines" in tables and "engine_tools" in tables else []
            conflict_rows = conn.execute(
                "select a_code,b_code,conflict_type,severity,coalesce(source_url,''),coalesce(description,'') from conflicts order by a_code,b_code"
            ).fetchall() if "conflicts" in tables else []
            hardware_rows = []
            for table, kind in (("hardware_cpu", "CPU"), ("hardware_gpu", "GPU")):
                if table in tables:
                    hardware_rows.extend((kind, *row) for row in conn.execute(f"select model,coalesce(source_title,''),coalesce(source_url,'') from {table} order by model"))
    except sqlite3.Error as exc:
        output.write_text(f"# Матрица покрытия\n\nНе удалось прочитать SQLite: `{exc}`.\n", encoding="utf-8")
        return

    def present(value: str) -> str:
        return "yes" if value not in ("", "[]", "null") else "gap"

    lines = [
        "# Матрица покрытия каталога и provenance",
        "",
        f"Снимок: `{db_path}`. Матрица создана генератором отчёта `{_git_revision()}`.",
        "",
        "Это аудит полноты полей, а не утверждение, что 124 метода уже прошли глубокую предметную рецензию. `yes` означает заполненное поле каталога; доказательность механизма/числа проверяется в EvidenceClaim.",
        "",
        "## Методы",
        "",
        "| Код | Функция | Вид | Источник | Confidence | Conditions | Engine filter | Platform filter | HW feature | Verification |",
        "| --- | --- | --- | --- | ---: | --- | --- | --- | --- | --- |",
    ]
    for code, name, kind, function, title, url, confidence, conditions, engines, platforms, hw, verification in method_rows:
        label = f"{code}: {name}".replace("|", "\\|")
        source = f"[{title}]({url})" if url else "gap"
        lines.append(f"| {label} | {function or '—'} | {kind} | {source} | {confidence:.2f} | {present(conditions)} | {present(engines)} | {present(platforms)} | {present(hw)} | {verification or 'gap'} |".replace("\n", " "))
    lines.extend(["", "## Связи метод-инструмент", "", "| Метод | Tool | Relation | Own source URL | Note |", "| --- | --- | --- | --- | --- |"])
    for method, tool, relation, url, note in link_rows:
        safe_note = (note or "—").replace("|", "\\|")
        lines.append(f"| {method} | {tool} | {relation} | {'yes' if url else 'gap'} | {safe_note} |")
    lines.extend(["", "## Движки и инструменты", "", "| Engine | Engine docs | Tool | Tool docs | Min version |", "| --- | --- | --- | --- | --- |"])
    for engine, engine_name, engine_url, tool, tool_name, tool_url, min_version in engine_rows:
        lines.append(f"| {engine}: {engine_name} | {'yes' if engine_url else 'gap'} | {tool_name or tool or '—'} | {'yes' if tool_url else 'gap'} | {min_version or '—'} |")
    lines.extend(["", "## Связи между решениями", "", "| A | B | Type | Severity | Source URL | Description |", "| --- | --- | --- | ---: | --- | --- |"])
    for a, b, relation, severity, url, description in conflict_rows:
        safe_description = (description or "—").replace("|", "\\|")
        lines.append(f"| {a} | {b} | {relation} | {severity} | {'yes' if url else 'gap'} | {safe_description} |")
    lines.extend(["", "## Оборудование", "", "| Type | Model | Source title | Source URL |", "| --- | --- | --- | --- |"])
    for kind, model, title, url in hardware_rows:
        source = f"[{title}]({url})" if url else "gap"
        lines.append(f"| {kind} | {model} | {source} | {'yes' if url else 'gap'} |")
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _report_rows(snapshot: dict[str, int | None], db_path: Path) -> dict[str, object]:
    """Собрать все строки отчёта один раз, чтобы Markdown и PDF совпадали."""
    revision = _git_revision()
    generated = date.today().isoformat()
    evidence_present = snapshot.get("evidence_sources") is not None
    status = "полный локальный снимок" if evidence_present else "legacy-снимок до первого запуска новой миграции"
    old_counts = [
        ("Игровые функции", _count_label(snapshot.get("game_functions"))),
        ("Методы", _count_label(snapshot.get("methods"))),
        ("Движки", _count_label(snapshot.get("engines"))),
        ("Инструменты движков", _count_label(snapshot.get("engine_tools"))),
        ("Связи метод-инструмент", _count_label(snapshot.get("method_engine_links"))),
        ("Связи между методами", _count_label(snapshot.get("conflicts"))),
        ("CPU / GPU", f"{_count_label(snapshot.get('hardware_cpu'))} / {_count_label(snapshot.get('hardware_gpu'))}"),
    ]
    new_counts = [
        ("EvidenceSource", _count_label(snapshot.get("evidence_sources"), f"seed catalog: {_seed_source_count()}")),
        ("EvidenceClaim", _count_label(snapshot.get("evidence_claims"), "будет создано при seed")),
        ("GameCase / CaseEvidence", f"{_count_label(snapshot.get('game_cases'), '8')} / {_count_label(snapshot.get('case_evidence'), 'seeded')}"),
        ("TechnologyNode / DependencyEdge", f"{_count_label(snapshot.get('technology_nodes'), 'derived from catalog')} / {_count_label(snapshot.get('dependency_edges'), '7 curated')}"),
        ("WorkPackage / TeamScenario", f"{_count_label(snapshot.get('work_packages'), 'derived per method')} / {_count_label(snapshot.get('team_scenarios'), '4')}"),
    ]
    source_rows = []
    for code, title, publisher, kind, url, locator in SOURCES:
        source_rows.append(f"- **{code}** {title}. {publisher}. Тип: `{kind}`. Локатор: {locator}. URL: {url}")

    # ── Полный реестр из базы ──
    ev = _db_evidence(db_path)

    def _row(value: object) -> str:
        text = str(value if value is not None else "").replace("\n", " ").strip()
        return text.replace("|", "\\|")

    full_source_rows = [
        "| Код | Название | Автор / издатель | Тип | Дата | Проверен | Версия | Платформа | Локатор | Доступность |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in ev["sources"]:
        code, title, author, stype, pub, checked, url, version, platform, locator, avail, _app = row
        full_source_rows.append(
            "| " + " | ".join(_row(x) for x in (
                code, title, author, stype, pub, checked, version, platform, locator, avail,
            )) + " |"
        )
    full_sources = "\n".join(full_source_rows)
    full_source_links = "\n".join(
        f"- `{_row(r[0])}` — {_row(r[1])} — {_row(r[6]) or 'URL не указан'}" for r in ev["sources"]
    )

    type_rows = [(str(t), str(c)) for t, c in ev["type_counts"]]
    basis_rows = [(str(t), str(c)) for t, c in ev["basis_counts"]]
    thin_rows = [(str(code), str(count)) for code, count in ev["claims_by_method"]]
    node_rows = [(str(t), str(c)) for t, c in ev["node_counts"]]
    relation_rows = [(str(t), str(c)) for t, c in ev["relation_counts"]]
    team_rows = [
        (str(code), str(name), str(size), str(tracks), f"{round(comm * 100)}%", f"{round(unpl * 100)}%")
        for code, name, size, tracks, comm, unpl, _d in ev["teams"]
    ]
    wp_rows = [
        (str(ptype), str(count), str(mn), str(avg50), str(avg80), str(basis))
        for ptype, count, mn, avg50, avg80, basis in ev["work_packages"]
    ]

    case_rows = [
        (
            _row(title), _row(studio), f"{_row(tech)} / {_row(year)}",
            f"{_row(world)} · {_row(network)}", _row(summary)[:260],
            _row(transfer)[:240],
        )
        for _c, title, studio, year, tech, _eng, world, network, summary, _rel, transfer in ev["cases"]
    ]

    dep_rows = [
        (
            _row(src), _row(dst), _row(dtype),
            "обязательная" if mandatory else "условная",
            _row(min_version) or "—", _row(platform) or "—", str(sev),
            _row(source_title) or "нет публичного источника",
        )
        for src, dst, dtype, mandatory, min_version, platform, sev, source_title, _desc in ev["dependency_edges"]
    ]

    # Разделение связей по обязательности и типу — это и есть проверка графа,
    # поэтому числа берутся из базы, а не из текста.
    mandatory_edges = sum(1 for r in ev["dependency_edges"] if r[3])
    curated_sources = sum(1 for r in ev["dependency_edges"] if r[7])
    evidence_edges = sum(1 for r in ev["dependency_edges"] if r[7])

    function_rows = [
        (_row(code), _row(name), _row(category), _row(formats)[:70], _row(worlds)[:90], _row(title) or "gap")
        for code, name, category, formats, worlds, title, _url in ev["functions"]
    ]
    function_count_rows = [(str(cat), str(cnt)) for cat, cnt in ev["function_counts"]]
    method_kind_rows = [(str(kind), str(cnt)) for kind, cnt in ev["method_kind"]]
    method_cat_rows = [
        (str(cat), str(impl), str(opt), str(total)) for cat, impl, opt, total in ev["method_by_category"]
    ]
    method_kind_text = " и ".join(f"{cnt} {kind}" for kind, cnt in method_kind_rows) or "124"
    fn_total = len(ev["functions"]) or 40
    method_total = sum(int(cnt) for _kind, cnt in method_kind_rows) or 124
    source_total = len(ev["sources"])

    cpu_rows = [
        (_row(model), f"{single:.2f}", f"{multi:.2f}", str(cls), _row(bench)[:44], _row(basis))
        for model, single, multi, cls, bench, basis in ev["cpu"]
    ]
    gpu_rows = [
        (_row(model), f"{raster:.2f}", f"{rt:.2f}", f"{vram:g}", str(cls), _row(bench)[:44])
        for model, raster, rt, vram, cls, bench in ev["gpu"]
    ]
    hw_basis_rows = [(str(kind), str(basis), str(cnt)) for kind, basis, cnt in ev["hw_basis"]]
    hw_class_rows = [(str(kind), str(cls), str(cnt)) for kind, cls, cnt in ev["hw_summary"]]
    cpu_total = sum(int(cnt) for kind, _cls, cnt in ev["hw_summary"] if kind == "CPU")
    gpu_total = sum(int(cnt) for kind, _cls, cnt in ev["hw_summary"] if kind == "GPU")
    hw_total = f"{cpu_total} CPU / {gpu_total} GPU"

    audit_rows = _catalog_audit(db_path)
    deep_sections = []
    for title, fact, synthesis, verification, source_codes in DEEP_STUDIES:
        deep_sections.append(
            f"### {title}\n\n**Факт и источник.** {fact}\n\n"
            f"**Синтез для DSS.** {synthesis}\n\n"
            f"**Проверка в проекте.** {verification}\n\n"
            f"Источники: `{source_codes}`."
        )
    deep_text = "\n\n".join(deep_sections)
    calculations_text = "\n\n".join([
        "### Бюджет кадра\n\n" + _md_table(["Target FPS", "Frame budget, ms", "Интерпретация"], FRAME_ROWS),
        "### Пиксельная нагрузка разрешения\n\n" + _md_table(["Разрешение", "Pixel ratio", "База"], RESOLUTION_ROWS),
        "### Предел параллелизации\n\n" + _md_table(["Workers", "Speedup", "Допущение"], AMDAHL_ROWS),
        "### Трёхточечная оценка\n\n" + _md_table(["Inputs", "Calculation", "Статус"], PERT_ROWS),
        "### Critical path\n\n" + _md_table(["Task", "Duration", "Predecessors", "Path result"], CRITICAL_PATH_ROWS),
        "### Сеть\n\n" + _md_table(["Scenario", "Inputs", "Derived result", "Limits"], NETWORK_ROWS),
        "### Память\n\n" + _md_table(["Component", "Inputs", "Result", "Basis"], MEMORY_ROWS),
    ])
    return {
        "revision": revision, "generated": generated, "status": status,
        "old_counts": old_counts, "new_counts": new_counts,
        "full_sources": full_sources, "full_source_links": full_source_links,
        "type_rows": type_rows, "basis_rows": basis_rows, "thin_rows": thin_rows,
        "node_rows": node_rows, "relation_rows": relation_rows,
        "team_rows": team_rows, "wp_rows": wp_rows,
        "case_rows": case_rows, "dep_rows": dep_rows,
        "mandatory_edges": mandatory_edges, "curated_sources": curated_sources,
        "evidence_edges": evidence_edges,
        "function_rows": function_rows, "function_count_rows": function_count_rows,
        "method_kind_rows": method_kind_rows, "method_cat_rows": method_cat_rows,
        "method_kind_text": method_kind_text, "fn_total": fn_total,
        "method_total": method_total, "source_total": source_total,
        "cpu_rows": cpu_rows, "gpu_rows": gpu_rows,
        "hw_basis_rows": hw_basis_rows, "hw_class_rows": hw_class_rows, "hw_total": hw_total,
        "audit_rows": audit_rows, "deep_text": deep_text,
        "calculations_text": calculations_text,
    }


def _markdown(snapshot: dict[str, int | None], db_path: Path) -> str:
    R = _report_rows(snapshot, db_path)
    (
        revision, generated, status, _, _,
        full_sources, full_source_links, type_rows, basis_rows, thin_rows,
        node_rows, relation_rows, team_rows, wp_rows, case_rows, dep_rows,
        mandatory_edges, curated_sources, _,
        function_rows, function_count_rows, _, method_cat_rows,
        method_kind_text, fn_total, method_total, source_total,
        cpu_rows, gpu_rows, hw_basis_rows, hw_class_rows, hw_total,
        audit_rows, deep_text, calculations_text,
    ) = (
        R["revision"], R["generated"], R["status"], R["old_counts"], R["new_counts"],
        R["full_sources"], R["full_source_links"], R["type_rows"], R["basis_rows"], R["thin_rows"],
        R["node_rows"], R["relation_rows"], R["team_rows"], R["wp_rows"], R["case_rows"], R["dep_rows"],
        R["mandatory_edges"], R["curated_sources"], R["evidence_edges"],
        R["function_rows"], R["function_count_rows"], R["method_kind_rows"], R["method_cat_rows"],
        R["method_kind_text"], R["fn_total"], R["method_total"], R["source_total"],
        R["cpu_rows"], R["gpu_rows"], R["hw_basis_rows"], R["hw_class_rows"], R["hw_total"],
        R["audit_rows"], R["deep_text"], R["calculations_text"],
    )
    return f"""# Доказательное исследование и DSS для проектирования игр

Дата генерации: {generated}  
Ревизия репозитория: `{revision}`  
Снимок базы: `{db_path}` — {status}

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

{_md_table(["Утверждение", "Статус", "Основание"], CLAIM_BOUNDARY_ROWS)}

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

{_md_table(["Тип источника", "Записей"], type_rows)}

### 2.3 Основание (basis) утверждений

{_md_table(["basis", "Claims"], basis_rows)}

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

{_md_table(["Метод", "Claims"], thin_rows)}

Все {method_total} метода каталога покрыты минимум шестью claims. Большее число
claims не означает автоматически более высокую достоверность: важны наличие
измерений, локаторов и условий применения, а не количество строк.

### 2.5 Сила доказательства: прямой пример, перекрёстный пример, объявленный пробел

{_md_table(["Класс доказательства", "Сущностей", "Комментарий"], _truth_grade(db_path)[0])}

{_truth_grade(db_path)[1]}

Правило для всех сущностей: **отсутствие источника не считается совместимостью**.
Если shipped-подтверждение найти не удалось, создаётся явная запись-пробел, а не
подбирается «похожий» пример. Пробел с `basis=unknown` и `evidence_level=low`
виден пользователю и в аудите; скрытая дыра — нет, поэтому она запрещена.

## 3. Классификация игровых функций

### 3.1 Категории и состав

{_md_table(["Категория", "Функций"], function_count_rows)}

### 3.2 Полный перечень функций

{_md_table(["Код", "Название", "Категория", "Форматы", "Типы мира", "Опорный источник"], function_rows)}

## 4. Варианты реализации по подсистемам

### 4.1 Подсистемы и что измерять

{_md_table(["Подсистема", "Варианты", "Что измерять/проверять", "Опорные источники"], METHOD_ROWS)}

### 4.2 Implementation и optimization по категориям

{_md_table(["Категория", "Implementation", "Optimization", "Всего"], method_cat_rows)}

В каталоге {method_kind_text} методов. Модель не выбирает один «лучший движок»
глобально. TOPSIS сравнивает сопоставимые альтернативы внутри функции, а
применимость проверяется до ранжирования по формату, миру, масштабу, платформе,
движку, железным возможностям, версии и условиям. Уверенность оценки — отдельный
критерий и не является процентом ускорения.

## 5. Сравнение движков и инструментов

{_md_table(["Движок/подход", "Инструменты и механизмы", "Проверка применимости", "Доказательства"], ENGINE_ROWS)}

Legacy-движок `custom` и его инструменты помечаются пользовательскими. Пустая
связь с инструментом не означает «поддерживается»: для engine-independent решения
хранится отдельный признак, а для неизвестной версии доступность получает статус
`unknown`.

## 6. Версия и платформенная совместимость

{_md_table(["Платформа / ветка", "Что доступно", "Ограничение проверки", "Источники"], PLATFORM_ROWS)}

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

{_md_table(["Тип связи", "Записей"], relation_rows)}

### 7.2 Состав узлов графа

{_md_table(["Тип узла", "Узлов"], node_rows)}

### 7.3 Обязательные и условные рёбра (выборка)

{_md_table(["Источник", "Цель", "Тип", "Обязательность", "Мин. версия", "Платформа", "Severity", "Источник"], dep_rows)}

В выборке обязательных рёбер: {mandatory_edges}; с публичным источником:
{curated_sources}. Рёбра без публичного источника несут явную пометку «нет
публичного источника», а не молчаливую совместимость.

### 7.4 Проверки графа

{_md_table(["Проверка", "Что обнаруживает", "Реакция системы"], GRAPH_CHECK_ROWS)}

При расчёте корзины система проверяет hard conflict, risk, alternative,
dependency, complement, overlap и unknown отдельно. Обязательные зависимости
расширяются транзитивно; неизвестный узел остаётся unresolved. Цикл обязательных
зависимостей не скрывается. Дополнение описывает совместное применение, но не
создаёт неподтверждённого прироста.

## 8. Масштаб сцены

{_md_table(["Параметр", "Единицы/входы", "Что определяет", "Источники"], SCALE_ROWS)}

Размер мира сам по себе не является числом для FPS. Управляемые переменные —
размер ячейки, loading range, число источников, HLOD-представление, размер чанка,
скорость чтения, декомпрессия и время активации. Поэтому в DSS они отдельные поля,
а не один scalar `open_world=true`.

## 9. CPU, GPU, RAM, VRAM и накопитель

{_md_table(["Ось", "Состав", "Правило моделирования", "Источники"], RESOURCE_ROWS)}

### 9.1 Пример композиции памяти

{_md_table(["Компонент", "Входы", "Результат", "Основание"], MEMORY_ROWS)}

RAM и VRAM не складываются в одну величину. Память состоит из текстур, геометрии,
render targets, streaming pool, audio, временных буферов и возможных CPU-копий.
GPU подбирается одновременно по raster, RT, VRAM, API и обязательным feature
flags; CPU — по single-thread и multi-thread. Physics и AI пересчитываются по
собственному fixed tick и не считаются как дополнительный FPS. Апскейлинг изменяет
внутреннее разрешение; frame generation добавляет собственный проход и не делает
уже отрисованный кадр бесплатным.

## 10. Сетевые режимы

{_md_table(["Режим", "Модель", "Ограничение", "Источники"], NETWORK_MODE_ROWS)}

### 10.1 Примеры воспроизводимых сетевых расчётов

{_md_table(["Scenario", "Inputs", "Derived result", "Limits"], NETWORK_ROWS)}

Server tick, render FPS, input latency, buffering, relevance set, serialization,
packet loss и bandwidth моделируются раздельно. Пример Epic с Fortnite —
документация механизма, а не лимит нового проекта. Число игроков без частоты
обновлений и размера состояния не определяет traffic.

## 11. Целевые показатели качества и производительности

### 11.1 Статусы оценки цели

{_md_table(["Статус", "Значение", "Правило", "Основание"], TARGET_ROWS)}

### 11.2 Бюджет кадра

{_md_table(["Target FPS", "Frame budget, ms", "Интерпретация"], FRAME_ROWS)}

### 11.3 Пиксельная нагрузка разрешения

{_md_table(["Разрешение", "Pixel ratio", "База"], RESOLUTION_ROWS)}

`frame_budget_ms = 1000 / target_fps`. Сценарные цели показываются как `meets`,
`at_risk`, `unknown` или `not_modeled`. Для 1% low FPS, startup, streaming
latency, save time, network latency, server tick и traffic не создаётся значение,
если оно не введено пользователем или не подтверждено измерением. Критерий `meets`
применяется к frame-time budget, а не к одной средней частоте кадров.

## 12. Стадии и work packages

{_md_table(["Тип пакета", "Пакетов", "Мин. P50", "Сред. P50", "Сред. P80", "Основание"], wp_rows)}

План строится из work packages: design, feasibility/prototype, integration,
content/assets, optimization, QA/regression, release stabilization,
documentation/maintenance. Каждый пакет имеет min, P50, P80, роль,
параллелизуемость, стадию, late factor, зависимости и основание. Legacy
`implementation_cost` сохранён для совместимости, но не является основой плана.

## 13. Трудоёмкость P50/P80 и календарь для разных команд

### 13.1 Профили команд

{_md_table(["Код", "Название", "Размер", "Параллельные потоки", "Коммуникации", "Непредвиденное"], team_rows)}

P50/P80 выражены в человеко-днях и не являются отраслевым нормативом. P50 —
наиболее вероятный сценарий при описанных допущениях; P80 — более осторожный
сценарий с неопределённостью. Команда влияет на календарную ёмкость, но не
уменьшает сумму person-days.

### 13.2 Трёхточечная оценка

{_md_table(["Inputs", "Calculation", "Статус"], PERT_ROWS)}

### 13.3 Предел параллелизации (Amdahl)

{_md_table(["Workers", "Speedup", "Допущение"], AMDAHL_ROWS)}

### 13.4 Critical path (пример)

{_md_table(["Task", "Duration", "Predecessors", "Path result"], CRITICAL_PATH_ROWS)}

Календарь вычисляется по dependency DAG и доступности роли. Независимые задачи
могут идти параллельно; integration, QA, release gates и узкие роли формируют
critical path. Поздняя стадия не убирает метод из выдачи, а добавляет
rework/late-risk note.

## 14. Профили нагрузки

{_md_table(["Профиль", "Состав", "Доминирующие оси", "Источники"], LOAD_ROWS)}

Стоимость кадра складывается из CPU main-thread, CPU parallel, GPU raster, GPU RT
и состава RAM/VRAM. Профиль нагрузки задаёт, какие оси доминируют и какие метрики
обязательны к измерению до того, как система выдаст сценарную оценку.

## 15. Оборудование

### 15.1 Покрытие и основание

{_md_table(["Тип", "basis", "Записей"], hw_basis_rows)}

{_md_table(["Тип", "Класс", "Записей"], hw_class_rows)}

Всего: {hw_total}. Индекс CPU/GPU — нормализованный anchor, а не FPS. В карточке
оборудования хранятся benchmark name, raw value, context, normalization note,
evidence basis и source link. Если каталог не содержит устройства, одновременно
покрывающего условия, результат сообщает `exceeds_catalog` и не подставляет
похожую карту молча.

### 15.2 CPU (верхняя часть по single-thread)

{_md_table(["Модель", "Single-thread", "Multi-thread", "Класс", "Benchmark", "Basis"], cpu_rows)}

### 15.3 GPU (верхняя часть по raster)

{_md_table(["Модель", "Raster", "RT", "VRAM, GB", "Класс", "Benchmark"], gpu_rows)}

## 16. Реальные игровые кейсы

{_md_table(["Кейс", "Студия", "Технология / год", "Сценарий", "Подтверждаемый факт / механизм", "Ограничение переноса"], case_rows)}

Кейс подтверждает факт применения, устройство или компромисс. Он не переносит
FPS, количество активных сущностей, tick rate, latency, размер команды или
требования к железу. Поэтому карточка хранит `relevance` и `transfer_limits`, а
`/recommend` показывает кейсы как практическую сверку со статусом
`not_calibrated`.

## 17. Риски

{_md_table(["Риск", "Почему важен", "Контроль"], RISKS)}

## 18. Итоговый план внедрения

1. Зафиксировать revision, входной профиль и опубликованный snapshot.
2. Прогнать Alembic и проверить резервную копию SQLite.
3. Выполнить seed доказательств; проверить claims без источника, локатора и версии.
4. Ревизовать {fn_total} функций, {method_total} методов, движки, инструменты, method-tool links, conflicts и hardware anchors.
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

{_md_table(["Проверка", "Значение", "Интерпретация"], audit_rows)}

### 19.4 Глубокие исследовательские карточки

{deep_text}

Каждая карточка разделяет наблюдаемый факт, аналитический синтез и план проверки.
Ссылка или showcase подтверждает только тот механизм и контекст, который указан в
локаторе; внешний проект не превращается в эталон производительности.

### 19.5 Воспроизводимые расчёты (сводка)

{calculations_text}

Таблицы выше — собственные вычисления DSS из явно указанных входов. Они
демонстрируют структуру бюджета и верхние/сценарные границы, но не являются
измерением конкретной игры. Для чисел, выведенных из документации (например,
128 Hz), сохранены и исходный источник, и формула.

### 19.6 Публичный API

- `GET /api/catalog/sources`, `/catalog/evidence`, `/catalog/evidence-summary`;
- `GET /api/catalog/cases`, `/catalog/cases/{{code}}`;
- `GET /api/catalog/dependencies`, `/catalog/teams`, `/catalog/graph-checks`;
- `POST /api/schedule`;
- `POST /api/report-data`, `GET /api/report-data`;
- расширенные `/recommend` и `/hardware-estimate` с evidence summary, cases, P50/P80, target assessments и unresolved items.

UI содержит экраны «Доказательства», «Кейсы игр», «Зависимости и конфликты»,
«Трудоёмкость и календарный план»; badges показывают documented, measured,
derived, case_evidence, expert_estimate и unknown. Все открываемые материалы
остаются ссылками на исходный источник.

## 20. Полный список источников

Всего в реестре {source_total} источников; ниже — полный перечень с типом, датой
проверки, версией, платформой, локатором и доступностью.

{full_sources}

### 20.1 Ссылки

{full_source_links}

Библиографические и иные носители могут добавляться без изменения схемы:
`source_type` — расширяемое поле, а обязательное требование к публикации задаётся
не видом носителя, а наличием проверяемого claim и локатора.
"""


def _font_paths() -> tuple[Path, Path]:
    candidates = [
        (Path("C:/Windows/Fonts/DejaVuSans.ttf"), Path("C:/Windows/Fonts/DejaVuSans-Bold.ttf")),
        (Path("C:/Windows/Fonts/arial.ttf"), Path("C:/Windows/Fonts/arialbd.ttf")),
        (Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"), Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")),
    ]
    for regular, bold in candidates:
        if regular.exists() and bold.exists():
            return regular, bold
    raise RuntimeError("Не найден Unicode-шрифт с кириллицей (ожидается DejaVu Sans или Arial).")


def _para(value: str, style, *, link: str | None = None):
    from reportlab.platypus import Paragraph

    content = html.escape(value).replace("\n", "<br/>")
    if link:
        content = f'<link href="{html.escape(link, quote=True)}" color="#1d5d85">{content}</link>'
    return Paragraph(content, style)


def _pdf(output: Path, snapshot: dict[str, int | None], db_path: Path) -> None:
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_LEFT
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import mm
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.platypus import (
        BaseDocTemplate, Frame, PageBreak, PageTemplate,
        Spacer, Table, TableStyle,
    )

    R = _report_rows(snapshot, db_path)

    regular, bold = _font_paths()
    pdfmetrics.registerFont(TTFont("DSSSans", str(regular)))
    pdfmetrics.registerFont(TTFont("DSSSans-Bold", str(bold)))
    styles = getSampleStyleSheet()
    body = ParagraphStyle("DSSBody", parent=styles["BodyText"], fontName="DSSSans", fontSize=8.7, leading=12, textColor=colors.HexColor("#23313b"), spaceAfter=5)
    small = ParagraphStyle("DSSSmall", parent=body, fontSize=7.1, leading=9.2, spaceAfter=0)
    tiny = ParagraphStyle("DSSTiny", parent=body, fontSize=6.2, leading=7.6, spaceAfter=0)
    table_header = ParagraphStyle("DSSTableHeader", parent=small, fontName="DSSSans-Bold", textColor=colors.white)
    title = ParagraphStyle("DSSTitle", parent=body, fontName="DSSSans-Bold", fontSize=23, leading=28, textColor=colors.HexColor("#102b3c"), alignment=TA_LEFT, spaceAfter=12)
    h1 = ParagraphStyle("DSSH1", parent=body, fontName="DSSSans-Bold", fontSize=15, leading=19, textColor=colors.HexColor("#0d4f6d"), spaceBefore=11, spaceAfter=8, keepWithNext=True)
    h2 = ParagraphStyle("DSSH2", parent=body, fontName="DSSSans-Bold", fontSize=10.5, leading=13, textColor=colors.HexColor("#245d74"), spaceBefore=7, spaceAfter=5, keepWithNext=True)
    note = ParagraphStyle("DSSNote", parent=body, fontSize=8, leading=11, textColor=colors.HexColor("#4c5962"), backColor=colors.HexColor("#edf5f7"), borderColor=colors.HexColor("#b6d4dd"), borderWidth=0.5, borderPadding=6, spaceBefore=4, spaceAfter=7)
    cover = ParagraphStyle("DSSCover", parent=body, fontSize=11, leading=15, textColor=colors.HexColor("#48606d"), spaceAfter=8)

    class NumberedCanvasMixin:
        def header_footer(self, canvas, doc):
            canvas.saveState()
            width, height = A4
            canvas.setStrokeColor(colors.HexColor("#d3e2e7"))
            canvas.line(18 * mm, height - 14 * mm, width - 18 * mm, height - 14 * mm)
            canvas.setFont("DSSSans", 7)
            canvas.setFillColor(colors.HexColor("#60727b"))
            canvas.drawString(18 * mm, height - 10 * mm, "Game Development DSS - evidence study")
            canvas.drawRightString(width - 18 * mm, 9 * mm, f"{doc.page}")
            canvas.restoreState()

    output.parent.mkdir(parents=True, exist_ok=True)
    doc = BaseDocTemplate(
        str(output), pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm,
        topMargin=21 * mm, bottomMargin=16 * mm, title="Доказательное исследование DSS",
        author="Game Development DSS",
    )
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="normal")
    doc.addPageTemplates([PageTemplate(id="main", frames=[frame], onPage=NumberedCanvasMixin().header_footer)])

    story = [
        Spacer(1, 26 * mm),
        _para("Доказательное исследование и DSS для проектирования игр", title),
        _para("Игровые функции, методы реализации, движки, зависимости, оборудование и календарный план", cover),
        Spacer(1, 4 * mm),
        _para(f"Выпуск: {R['generated']}. Ревизия: {R['revision']}. Формат: локальная PC-модель с прозрачными claims и сценарными диапазонами.", body),
        _para("Принцип: ни одно число не публикуется как измерение без опубликованного источника с локатором или явной формулы с входными параметрами. Отсутствие данных даёт статус unknown, а не ноль и не «совместимо».", note),
        PageBreak(),
    ]

    def add_heading(text: str, level: int = 1):
        story.append(_para(text, h1 if level == 1 else h2))

    def _strip_md(text: str) -> str:
        """Убрать markdown-разметку из абзаца для PDF.

        Отчёт пишется в markdown, и PDF-рендер обязан показывать текст, а не
        его разметку: иначе в готовом документе остаются литеральные `**`, `` ` ``
        и висячие `• **`. Ссылки сворачиваются в подпись, списки — в маркеры.
        """
        # Ссылки [подпись](url) -> подпись; bare-URL в скобках тоже сворачиваем.
        text = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", text)
        # Жирный/курсив: **x**, __x__, *x*, _x_ (только парные маркеры).
        text = re.sub(r"\*\*(.+?)\*\*", r"\1", text, flags=re.S)
        text = re.sub(r"__(.+?)__", r"\1", text, flags=re.S)
        # Инлайновый код: `x` -> x.
        text = re.sub(r"`([^`]+)`", r"\1", text)
        # Маркеры списка в начале строки -> внятный буллет.
        text = re.sub(r"(?m)^\s*[-*]\s+", "• ", text)
        # Схлопнуть пробелы перед пунктуацией, оставшиеся от свёртки.
        text = re.sub(r"\s+([,.;:])", r"\1", text)
        return text

    def add_text(text: str, style=body):
        for paragraph in [p.strip() for p in text.split("\n\n") if p.strip()]:
            story.append(_para(_strip_md(paragraph), style))

    def add_table(headers, rows, widths=None, *, compact: bool = False):
        cell_style = tiny if compact else small
        data = [[_para(str(item), table_header) for item in headers]]
        data.extend([[_para(str(item), cell_style) for item in row] for row in rows])
        table = Table(data, colWidths=widths, repeatRows=1, hAlign="LEFT")
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0d4f6d")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "DSSSans-Bold"),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#cbd9de")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f3f7f8")]),
            ("LEFTPADDING", (0, 0), (-1, -1), 4), ("RIGHTPADDING", (0, 0), (-1, -1), 4),
            ("TOPPADDING", (0, 0), (-1, -1), 2.5 if compact else 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5 if compact else 4),
        ]))
        story.append(table)
        story.append(Spacer(1, 5 * mm))

    def add_list(items):
        for item in items:
            story.append(_para(f"• {_strip_md(str(item))}", body))

    # ── 1 ──
    add_heading("1. Область применимости и ограничения")
    add_text("Система — локальное PC-ориентированное приложение поддержки инженерных решений. Оно связывает игровые функции, варианты реализации, движки и инструменты, конфликты, технологические зависимости, цели качества, нагрузочный профиль, референсный класс оборудования и план работ. Исследование универсальное: реальные игры используются как проверяемые кейсы механизма, но не как паспорта производительности для чужого проекта.")
    add_text("Количественная модель ограничена Windows PC и Linux PC. Целевой FPS, разрешение, quality, RAM/VRAM, streaming pool, draw-call budget, simulation radius, physics tick, сетевой latency/tick и storage задаются профилем. Если runtime-профиля проекта нет, система не обещает точный FPS, точную latency или календарную дату.")
    add_text("Вне текущего результата: прямое подключение к Unreal Insights/Unity Profiler, импорт runtime-метрик, денежный бюджет, multi-user авторизация и автоматическое изменение проекта движка.", note)
    add_heading("1.1 Что система утверждает и чего не утверждает", 2)
    add_table(["Утверждение", "Статус", "Основание"], CLAIM_BOUNDARY_ROWS, [52 * mm, 40 * mm, 82 * mm], compact=True)

    # ── 2 ──
    add_heading("2. Методология источников")
    add_text("Источник — любой проверяемый носитель, где можно установить механизм, ограничение, числовой результат или контекст. Реестр не ограничен статьями или интервью: книги, отдельные издания, стандарты, спецификации, академические статьи, материалы конференций и видео, инженерные postmortem, исходный код, открытые проекты, бенчмарки, учебники и технические анализы допустимы.")
    add_text("Книга хранится с автором, издателем, изданием и главой. Спецификация — с версией и разделом. Видео или доклад — с датой и timestamp/слайдами. Исходный код — с репозиторием, commit/tag и путём. Для любого типа URL сам по себе недостаточен: claim обязан иметь локатор.", note)
    add_heading("2.2 Типы источников в реестре", 2)
    add_table(["Тип источника", "Записей"], R["type_rows"], [120 * mm, 30 * mm], compact=True)
    add_heading("2.3 Основание (basis) утверждений", 2)
    add_table(["basis", "Claims"], R["basis_rows"], [120 * mm, 30 * mm], compact=True)
    add_list([
        "measured — опубликовано измерение с условиями;",
        "documented — механизм или ограничение прямо указаны в материале;",
        "derived — значение вычислено из явно сохранённых входов и формулы;",
        "case_evidence — подтверждено материалом реального проекта;",
        "expert_estimate — сценарный балл для ранжирования или планирования;",
        "unknown — данных недостаточно.",
    ])
    add_heading("2.4 Методы с наименьшим числом claims", 2)
    add_table(["Метод", "Claims"], R["thin_rows"], [120 * mm, 30 * mm], compact=True)

    add_heading("2.5 Сила доказательства: прямой пример, перекрёстный пример, объявленный пробел", 2)
    add_table(["Класс доказательства", "Сущностей", "Комментарий"],
              _truth_grade(db_path)[0], [72 * mm, 20 * mm, 68 * mm], compact=True)
    add_text(_truth_grade(db_path)[1].replace("\n\n", " ").replace("- ", "• "), note)

    # ── 3 ──
    add_heading("3. Классификация игровых функций")
    add_heading("3.1 Категории и состав", 2)
    add_table(["Категория", "Функций"], R["function_count_rows"], [120 * mm, 30 * mm], compact=True)
    add_heading("3.2 Полный перечень функций", 2)
    add_table(["Код", "Название", "Категория", "Форматы", "Типы мира", "Опорный источник"], R["function_rows"], [34 * mm, 40 * mm, 24 * mm, 24 * mm, 30 * mm, 22 * mm], compact=True)

    # ── 4 ──
    add_heading("4. Варианты реализации по подсистемам")
    add_heading("4.1 Подсистемы и что измерять", 2)
    add_table(["Подсистема", "Варианты", "Что измерять/проверять", "Опорные источники"], METHOD_ROWS, [30 * mm, 55 * mm, 62 * mm, 27 * mm])
    add_heading("4.2 Implementation и optimization по категориям", 2)
    add_table(["Категория", "Implementation", "Optimization", "Всего"], R["method_cat_rows"], [70 * mm, 34 * mm, 34 * mm, 30 * mm], compact=True)
    add_text(f"В каталоге {R['method_kind_text']} методов. Модель не выбирает один «лучший движок» глобально: TOPSIS сравнивает сопоставимые альтернативы внутри функции, а применимость проверяется до ранжирования. Уверенность оценки — отдельный критерий и не является процентом ускорения.", note)

    # ── 5 ──
    add_heading("5. Сравнение движков и инструментов")
    add_table(["Движок/подход", "Инструменты и механизмы", "Проверка применимости", "Доказательства"], ENGINE_ROWS, [30 * mm, 55 * mm, 62 * mm, 27 * mm])

    # ── 6 ──
    add_heading("6. Версия и платформенная совместимость")
    add_table(["Платформа / ветка", "Что доступно", "Ограничение проверки", "Источники"], PLATFORM_ROWS, [38 * mm, 48 * mm, 62 * mm, 26 * mm])
    add_text("Поддержка движка — не бинарный engine=yes. Она включает version, package/plugin, target platform/API, scope (runtime, editor, build, server, development), tool relation и свежесть доказательства. HeroEngine оставлен в каталоге из-за фиксированного охвата, но его public applicability — legacy/needs_review, а не подтверждённая совместимость.", note)

    # ── 7 ──
    add_heading("7. Зависимости, конфликты и альтернативы")
    add_text("Граф состоит из методов, движков, инструментов, API, SDK и библиотек. Ребро направлено и хранит mandatory, min/max version, platform, scope, severity, источник, описание и workaround.")
    add_heading("7.1 Типы связей между решениями", 2)
    add_table(["Тип связи", "Записей"], R["relation_rows"], [120 * mm, 30 * mm], compact=True)
    add_heading("7.2 Состав узлов графа", 2)
    add_table(["Тип узла", "Узлов"], R["node_rows"], [120 * mm, 30 * mm], compact=True)
    add_heading("7.3 Обязательные и условные рёбра (выборка)", 2)
    add_table(["Источник", "Цель", "Тип", "Обязательность", "Мин. версия", "Платформа", "Severity", "Источник"], R["dep_rows"], [26 * mm, 21 * mm, 21 * mm, 27 * mm, 16 * mm, 20 * mm, 15 * mm, 28 * mm], compact=True)
    add_text(f"В выборке обязательных рёбер: {R['mandatory_edges']}; с публичным источником: {R['curated_sources']}. Рёбра без публичного источника несут явную пометку «нет публичного источника», а не молчаливую совместимость.", note)
    add_heading("7.4 Проверки графа", 2)
    add_table(["Проверка", "Что обнаруживает", "Реакция системы"], GRAPH_CHECK_ROWS, [34 * mm, 62 * mm, 78 * mm], compact=True)

    # ── 8 ──
    add_heading("8. Масштаб сцены")
    add_table(["Параметр", "Единицы/входы", "Что определяет", "Источники"], SCALE_ROWS, [30 * mm, 48 * mm, 66 * mm, 30 * mm])
    add_text("Размер мира сам по себе не является числом для FPS. Управляемые переменные — размер ячейки, loading range, число источников, HLOD-представление, размер чанка, скорость чтения, декомпрессия и время активации. Поэтому в DSS они отдельные поля, а не один scalar open_world=true.", note)

    # ── 9 ──
    add_heading("9. CPU, GPU, RAM, VRAM и накопитель")
    add_table(["Ось", "Состав", "Правило моделирования", "Источники"], RESOURCE_ROWS, [26 * mm, 52 * mm, 66 * mm, 30 * mm])
    add_heading("9.1 Пример композиции памяти", 2)
    add_table(["Компонент", "Входы", "Результат", "Основание"], MEMORY_ROWS, [45 * mm, 40 * mm, 28 * mm, 61 * mm], compact=True)
    add_text("RAM и VRAM не складываются в одну величину. GPU подбирается одновременно по raster, RT, VRAM, API и feature flags; CPU — по single-thread и multi-thread. Physics и AI пересчитываются по собственному fixed tick и не считаются как дополнительный FPS. Апскейлинг изменяет внутреннее разрешение; frame generation добавляет собственный проход.", note)

    # ── 10 ──
    add_heading("10. Сетевые режимы")
    add_table(["Режим", "Модель", "Ограничение", "Источники"], NETWORK_MODE_ROWS, [34 * mm, 52 * mm, 60 * mm, 28 * mm])
    add_heading("10.1 Примеры воспроизводимых сетевых расчётов", 2)
    add_table(["Scenario", "Inputs", "Derived result", "Limits"], NETWORK_ROWS, [30 * mm, 50 * mm, 45 * mm, 49 * mm], compact=True)
    add_text("Server tick, render FPS, input latency, buffering, relevance set, serialization, packet loss и bandwidth моделируются раздельно. Пример Epic с Fortnite — документация механизма, а не лимит нового проекта.", note)

    # ── 11 ──
    add_heading("11. Целевые показатели качества и производительности")
    add_heading("11.1 Статусы оценки цели", 2)
    add_table(["Статус", "Значение", "Правило", "Основание"], TARGET_ROWS, [24 * mm, 50 * mm, 70 * mm, 30 * mm], compact=True)
    add_heading("11.2 Бюджет кадра", 2)
    add_table(["Target FPS", "Frame budget, ms", "Интерпретация"], FRAME_ROWS, [28 * mm, 35 * mm, 111 * mm], compact=True)
    add_heading("11.3 Пиксельная нагрузка разрешения", 2)
    add_table(["Разрешение", "Pixel ratio", "База"], RESOLUTION_ROWS, [37 * mm, 28 * mm, 109 * mm], compact=True)
    add_text("frame_budget_ms = 1000 / target_fps. Сценарные цели показываются как meets, at_risk, unknown или not_modeled. Для 1% low FPS, startup, streaming latency, save time, network latency, server tick и traffic не создаётся значение без входного значения или измерения. Критерий meets применяется к frame-time budget.", note)

    # ── 12 ──
    add_heading("12. Стадии и work packages")
    add_table(["Тип пакета", "Пакетов", "Мин. P50", "Сред. P50", "Сред. P80", "Основание"], R["wp_rows"], [34 * mm, 24 * mm, 26 * mm, 28 * mm, 28 * mm, 34 * mm], compact=True)
    add_text("План строится из work packages: design, feasibility/prototype, integration, content/assets, optimization, QA/regression, release stabilization, documentation/maintenance. Каждый пакет имеет min, P50, P80, роль, параллелизуемость, стадию, late factor, зависимости и основание. Legacy implementation_cost сохранён для совместимости, но не является основой плана.", note)

    # ── 13 ──
    add_heading("13. Трудоёмкость P50/P80 и календарь для разных команд")
    add_heading("13.1 Профили команд", 2)
    add_table(["Код", "Название", "Размер", "Потоки", "Коммуникации", "Непредвиденное"], R["team_rows"], [26 * mm, 40 * mm, 20 * mm, 22 * mm, 32 * mm, 34 * mm])
    add_text("P50/P80 выражены в человеко-днях и не являются отраслевым нормативом. Команда влияет на календарную ёмкость, но не уменьшает сумму person-days.", note)
    add_heading("13.2 Трёхточечная оценка", 2)
    add_table(["Inputs", "Calculation", "Статус"], PERT_ROWS, [52 * mm, 62 * mm, 60 * mm], compact=True)
    add_heading("13.3 Предел параллелизации (Amdahl)", 2)
    add_table(["Workers", "Speedup", "Допущение"], AMDAHL_ROWS, [26 * mm, 27 * mm, 121 * mm], compact=True)
    add_heading("13.4 Critical path (пример)", 2)
    add_table(["Task", "Duration", "Predecessors", "Path result"], CRITICAL_PATH_ROWS, [40 * mm, 22 * mm, 42 * mm, 70 * mm], compact=True)
    add_text("Календарь вычисляется по dependency DAG и доступности роли. Независимые задачи могут идти параллельно; integration, QA, release gates и узкие роли формируют critical path. Поздняя стадия добавляет rework/late-risk note, но не удаляет метод из выдачи.", note)

    # ── 14 ──
    add_heading("14. Профили нагрузки")
    add_table(["Профиль", "Состав", "Доминирующие оси", "Источники"], LOAD_ROWS, [32 * mm, 52 * mm, 60 * mm, 30 * mm])

    # ── 15 ──
    add_heading("15. Оборудование")
    add_heading("15.1 Покрытие и основание", 2)
    add_table(["Тип", "basis", "Записей"], R["hw_basis_rows"], [50 * mm, 70 * mm, 30 * mm], compact=True)
    add_table(["Тип", "Класс", "Записей"], R["hw_class_rows"], [50 * mm, 70 * mm, 30 * mm], compact=True)
    add_text(f"Всего: {R['hw_total']}. Индекс CPU/GPU — нормализованный anchor, а не FPS. В карточке оборудования хранятся benchmark name, raw value, context, normalization note, evidence basis и source link. Если каталог не содержит устройства, одновременно покрывающего условия, результат сообщает exceeds_catalog и не подставляет похожую карту молча.", note)
    add_heading("15.2 CPU (верхняя часть по single-thread)", 2)
    add_table(["Модель", "Single-thread", "Multi-thread", "Класс", "Benchmark", "Basis"], R["cpu_rows"], [42 * mm, 26 * mm, 26 * mm, 16 * mm, 42 * mm, 22 * mm], compact=True)
    add_heading("15.3 GPU (верхняя часть по raster)", 2)
    add_table(["Модель", "Raster", "RT", "VRAM, GB", "Класс", "Benchmark"], R["gpu_rows"], [46 * mm, 22 * mm, 20 * mm, 22 * mm, 16 * mm, 48 * mm], compact=True)

    # ── 16 ──
    add_heading("16. Реальные игровые кейсы")
    add_table(["Кейс", "Студия", "Технология / год", "Сценарий", "Подтверждаемый факт / механизм", "Ограничение переноса"], R["case_rows"], [26 * mm, 24 * mm, 26 * mm, 30 * mm, 38 * mm, 30 * mm], compact=True)
    add_text("Кейс подтверждает факт применения, устройство или компромисс. Он не переносит FPS, количество активных сущностей, tick rate, latency, размер команды или требования к железу. /recommend показывает кейсы как практическую сверку со статусом not_calibrated.", note)

    # ── 17 ──
    add_heading("17. Риски")
    add_table(["Риск", "Почему важен", "Контроль"], RISKS, [38 * mm, 59 * mm, 77 * mm])

    # ── 18 ──
    add_heading("18. Итоговый план внедрения")
    add_list([
        "Зафиксировать revision, входной профиль и опубликованный snapshot.",
        "Прогнать Alembic и проверить резервную копию SQLite.",
        "Выполнить seed доказательств; проверить claims без источника, локатора и версии.",
        f"Ревизовать {R['fn_total']} функций, {R['method_total']} методов, движки, инструменты, method-tool links, conflicts и hardware anchors.",
        "Для выбранной корзины закрыть prerequisites, version/API compatibility и hard conflicts.",
        "Запустить feasibility/prototype с трассами CPU/GPU/IO/network; сохранить условия измерения.",
        "Обновить raw benchmark anchors только вместе с контекстом и датой.",
        "Пересчитать P50/P80 и critical path по фактическим ролям команды.",
        "Проверить минимальную конфигурацию на Windows и Linux, затем пройти QA/regression/release gates.",
    ])

    # ── 19 ──
    add_heading("19. Ограничения модели, критерии приёмки и аудит")
    add_heading("19.1 Ограничения", 2)
    add_text("Без исходного кода, ассетов и runtime-профиля невозможно честно вывести точный FPS, универсальную latency, точный размер RAM/VRAM или календарную дату. Публичная документация и книги подтверждают устройство механизма, но не обещают его результат в другом проекте. Нормализованные hardware indices пригодны для ранжирования внутри каталога и сценарного сравнения; это не замена измерению.")
    add_text("Статус калибровки: not_calibrated. Процент точности не показывается. Чтобы изменить статус, нужна реальная выборка: одинаковый профиль, версия движка, commit ассетов, target platform/API, measured frame-time percentiles, memory, IO and network metrics, а также правило train/test split.", note)
    add_heading("19.2 Критерии приёмки", 2)
    add_list([
        "одинаковый вход, algorithm version и catalog revision дают одинаковый результат;",
        "увеличение объекта/NPC count, resolution или quality не уменьшает соответствующую нагрузку;",
        "CPU main/parallel, GPU raster/RT, RAM/VRAM и storage/network не смешиваются без подписи;",
        "неизвестная зависимость не считается закрытой;",
        "hard conflict не попадает в рабочую корзину;",
        "complement не даёт числовой бонус без измерения;",
        "удаление prerequisite делает метод явно неприменимым;",
        "team size меняет календарь, но не person-days;",
        "critical path строится по DAG, P80 >= P50;",
        "отсутствие числовых данных получает unknown/expert_estimate;",
        "non-PC цели не попадают в PC quantitative hardware estimate;",
        "source title, authors/publisher, type, version and locator видны пользователю;",
        "Markdown и PDF проходят текстовый и визуальный QA.",
    ])
    add_heading("19.3 Аудит покрытия каталога", 2)
    add_table(["Проверка", "Значение", "Интерпретация"], R["audit_rows"], [62 * mm, 52 * mm, 60 * mm], compact=True)
    add_heading("19.4 Глубокие исследовательские карточки", 2)
    for study_title, fact, synthesis, verification, source_codes in DEEP_STUDIES:
        add_heading(study_title, 2)
        add_text(f"Факт и источник: {fact}")
        add_text(f"Синтез для DSS: {synthesis}")
        add_text(f"Проверка в проекте: {verification}")
        add_text(f"Источники: {source_codes}.", small)
    add_heading("19.5 Воспроизводимые расчёты (сводка)", 2)
    add_table(["Target FPS", "Frame budget, ms", "Интерпретация"], FRAME_ROWS, [28 * mm, 35 * mm, 111 * mm], compact=True)
    add_table(["Разрешение", "Pixel ratio", "База"], RESOLUTION_ROWS, [37 * mm, 28 * mm, 109 * mm], compact=True)
    add_table(["Workers", "Speedup", "Допущение"], AMDAHL_ROWS, [26 * mm, 27 * mm, 121 * mm], compact=True)
    add_table(["Inputs", "Calculation", "Статус"], PERT_ROWS, [52 * mm, 62 * mm, 60 * mm], compact=True)
    add_table(["Task", "Duration", "Predecessors", "Path result"], CRITICAL_PATH_ROWS, [40 * mm, 22 * mm, 42 * mm, 70 * mm], compact=True)
    add_table(["Scenario", "Inputs", "Derived result", "Limits"], NETWORK_ROWS, [30 * mm, 50 * mm, 45 * mm, 49 * mm], compact=True)
    add_table(["Component", "Inputs", "Result", "Basis"], MEMORY_ROWS, [45 * mm, 40 * mm, 28 * mm, 61 * mm], compact=True)
    add_text("Расчёты выше получены из явно указанных входов и формул. Они показывают структуру бюджета и границы сценария, но не являются измерением конкретной игры.", note)
    add_heading("19.6 Публичный API", 2)
    add_list([
        "GET /api/catalog/sources, /catalog/evidence, /catalog/evidence-summary;",
        "GET /api/catalog/cases, /catalog/cases/{code};",
        "GET /api/catalog/dependencies, /catalog/teams, /catalog/graph-checks;",
        "POST /api/schedule; POST /api/report-data, GET /api/report-data;",
        "расширенные /recommend и /hardware-estimate с evidence summary, cases, P50/P80, target assessments и unresolved items.",
    ])
    add_text("UI содержит экраны «Доказательства», «Кейсы игр», «Зависимости и конфликты», «Трудоёмкость и календарный план»; badges показывают documented, measured, derived, case_evidence, expert_estimate и unknown.", note)

    # ── 20 ──
    add_heading("20. Полный список источников")
    add_text(f"Всего в реестре {R['source_total']} источников. Ниже — полный перечень с типом, датой проверки, локатором и доступностью, затем активные ссылки.")
    source_registry = _db_evidence(db_path)["sources"]
    add_table(
        ["Код", "Название", "Тип", "Проверен", "Локатор", "Доступность"],
        [
            (
                code, str(title)[:70], stype, str(checked), str(locator)[:60], avail,
            )
            for code, title, _author, stype, _pub, checked, _url, _version, _platform, locator, avail, _app in source_registry
        ],
        [32 * mm, 46 * mm, 26 * mm, 18 * mm, 30 * mm, 22 * mm],
        compact=True,
    )
    story.append(_para("Активные ссылки:", h2))
    for code, title_text, _author, _stype, _pub, _checked, url, _version, _platform, _locator, _avail, _app in source_registry:
        if url:
            story.append(_para(f"{code} - {str(title_text)[:70]}: {url}", tiny, link=url))
            story.append(Spacer(1, 1.0 * mm))
    story.append(Spacer(1, 4 * mm))
    story.append(_para("Полный URL каждого источника присутствует также в Markdown-версии отчёта и в EvidenceSource API.", note))
    doc.build(story)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate the evidence study Markdown and PDF")
    parser.add_argument("--db", type=Path, default=DEFAULT_DB)
    parser.add_argument("--markdown", type=Path, default=DEFAULT_MARKDOWN)
    parser.add_argument("--pdf", type=Path, default=DEFAULT_PDF)
    parser.add_argument("--matrix", type=Path, default=DEFAULT_MATRIX)
    args = parser.parse_args()
    snapshot = _snapshot(args.db)
    markdown = _markdown(snapshot, args.db)
    args.markdown.parent.mkdir(parents=True, exist_ok=True)
    args.markdown.write_text(markdown, encoding="utf-8")
    _pdf(args.pdf, snapshot, args.db)
    _write_coverage_matrix(args.db, args.matrix)
    print(f"Markdown: {args.markdown}")
    print(f"PDF: {args.pdf}")
    print(f"Matrix: {args.matrix}")
    print(f"Revision: {_git_revision()}")


if __name__ == "__main__":
    main()
