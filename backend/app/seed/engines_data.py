"""Каталог игровых движков и их инструментов.

Каталог расширяется через административный раздел без изменения кода:
достаточно добавить запись в ENGINES / ENGINE_TOOLS.
"""
from __future__ import annotations

from .sources import src

ENGINES: list[dict] = [
    {
        "code": "unreal",
        "name": "Unreal Engine",
        "vendor": "Epic Games",
        "versions": ["4.27", "5.0", "5.1", "5.2", "5.3", "5.4", "5.5"],
        "supported_formats": ["3D", "2.5D", "2D"],
        "notes": "Полный набор встроенных подсистем: виртуализированная геометрия, динамическое ГО, "
                 "мира большого масштаба, сетевая репликация. Высокие требования к железу при "
                 "использовании Lumen и Nanite.",
        "docs_url": "https://dev.epicgames.com/documentation/en-us/unreal-engine",
    },
    {
        "code": "unity",
        "name": "Unity",
        "vendor": "Unity Technologies",
        "versions": ["2021 LTS", "2022 LTS", "2023", "6 (6000.x)"],
        "supported_formats": ["3D", "2.5D", "2D"],
        "notes": "Гибкий набор рендер-конвейеров (URP/HDRP), развитая система ассетов Addressables, "
                 "DOTS для Data-Oriented разработки. Часть подсистем требует выбора пакета.",
        "docs_url": "https://docs.unity3d.com/Manual/index.html",
    },
    {
        "code": "godot",
        "name": "Godot",
        "vendor": "Godot Foundation",
        "versions": ["3.5", "3.6", "4.0", "4.1", "4.2", "4.3", "4.4"],
        "supported_formats": ["3D", "2.5D", "2D"],
        "notes": "Открытый движок. Встроенные средства оптимизации уступают коммерческим движкам, "
                 "часть решений реализуется вручную, но движок проще профилировать и модифицировать.",
        "docs_url": "https://docs.godotengine.org/en/stable/index.html",
    },
    {
        "code": "custom",
        "name": "Собственный движок",
        "vendor": "In-house",
        "versions": ["любая"],
        "supported_formats": ["3D", "2.5D", "2D"],
        "notes": "Собственная или сторонняя технология без готовых аналогов встроенных подсистем. "
                 "Все решения реализуются командой самостоятельно, стоимость внедрения максимальна, "
                 "но контроль над производительностью полный.",
        "docs_url": "",
    },
    {
        # Трек 1: CryEngine — рендер растительности/дальности, SVOGI/SVOTI, туман как
        # оптимизация. Встроенное не абсолют: KCD отказался от SVOGI в пользу запечённого.
        "code": "cryengine",
        "name": "CryEngine",
        "vendor": "Crytek",
        "versions": ["3.x", "V (5.x)"],
        "supported_formats": ["3D"],
        "notes": "Открытые пространства, вегетация с touch-bending, SVOGI/SVOTI, volumetric fog. "
                 "Сильная сторона — дальность и природа; цена — CPU-потоки и ручной LOD/стриминг.",
        "docs_url": "https://docs.cryengine.com",
    },
    {
        # Трек 1: Source / Source 2 — физика как геймплей, stencil-порталы,
        # competitive tick/interp/lagcomp, Vulkan/Rubikon в Source 2.
        "code": "source",
        "name": "Source / Source 2",
        "vendor": "Valve",
        "versions": ["Source 2004", "Source 2007 (OB)", "Source 2013", "Source 2"],
        "supported_formats": ["3D"],
        "notes": "Коридоры и арены, VPhysics/QPhysics со сном тел, BSP/порталы, тикрейт и "
                 "компенсация задержек. В Source 2 — Vulkan, Rubikon, Panorama, sub-tick.",
        "docs_url": "https://developer.valvesoftware.com/wiki/Main_Page",
    },
    {
        # Трек 1: HeroEngine — MMO-стриминг и live-коллаборация. Shipped-подтверждений
        # мало (SWTOR-форк, Faxion, Zosimos): кейсы честно помечены статусом.
        "code": "heroengine",
        "name": "HeroEngine",
        "vendor": "Idea Fabrik / Laniatus",
        "versions": ["1.x", "2.x"],
        "supported_formats": ["3D"],
        "notes": "MMO-платформа: HeroBlade live-edit, HeroCloud, инстансинг планет. Быстрый старт "
                 "малой командой ценой single-thread наследия, DX9 и вендор-зависимости.",
        "docs_url": "https://heroengine.com",
    },
]


def _tool(code: str, engine: str, name: str, subsystem: str, description: str,
          tool_type: str = "runtime", docs_key: str | None = None,
          docs_url: str | None = None, source_title: str = "",
          min_version: str | None = None) -> dict:
    """Инструмент движка.

    `min_version` — минимальная версия движка, в которой встроенный инструмент
    существует. Граница задаётся только там, где она следует из документации
    вендора: пустое значение означает не «доступен всегда», а «граница не
    подтверждена». Показывать встроенный Nanite доступным для UE 4.27 нельзя —
    в этой версии его нет, и решение превращается в собственную реализацию.
    """
    # Прямая ссылка имеет приоритет: нужна движкам Трека 1 (CryEngine / Source /
    # HeroEngine), чьи доки не входят в реестр SOURCES. Старые вызовы с docs_key
    # работают как раньше — поведение для них не меняется.
    s = src(docs_key)
    return {
        "code": code,
        "engine_code": engine,
        "name": name,
        "subsystem": subsystem,
        "description": description,
        "tool_type": tool_type,
        "docs_url": docs_url if docs_url is not None else s["url"],
        "source_title": source_title or s["title"],
        "min_version": min_version,
    }


ENGINE_TOOLS: list[dict] = [
    # ---------------- Unreal Engine 5 ----------------
    # Nanite, Lumen, World Partition и виртуальные теневые карты появились
    # вместе с UE 5.0: для 4.27 встроенного аналога нет, и метод превращается в
    # собственную реализацию. Граница задана по документации Epic.
    _tool("ue_nanite", "unreal", "Nanite", "рендер",
          "Виртуализированная геометрия: автоматический LOD и кластеризованный растеризатор, "
          "снимающий ограничение на количество полигонов.", "runtime", "UE_NANITE",
          min_version="5.0"),
    _tool("ue_lumen", "unreal", "Lumen", "освещение",
          "Динамическое глобальное освещение и отражения на базе SDF, кэша освещённости и "
          "трассировки лучей.", "runtime", "UE_LUMEN", min_version="5.0"),
    _tool("ue_world_partition", "unreal", "World Partition", "мир",
          "Автоматическое разбиение мира на ячейки с потоковой загрузкой по дистанции, "
          "заменяет ручную сборку уровней-подровней.", "editor", "UE_WORLDPARTITION",
          min_version="5.0"),
    _tool("ue_vsm", "unreal", "Virtual Shadow Maps", "тени",
          "Виртуализированные карты теней высокого разрешения, заменяют каскадные карты теней.",
          "runtime", "UE_VSM", min_version="5.0"),
    _tool("ue_niagara", "unreal", "Niagara", "частицы",
          "Система частиц с поддержкой GPU-симуляции, вычислений на GPU и модульной структурой эмиттеров.",
          "runtime", "UE_NIAGARA"),
    _tool("ue_chaos", "unreal", "Chaos Physics", "физика",
          "Физический движок с многопоточной симуляцией, поддержкой разрушений и кэширования.",
          "runtime", "UE_CHAOS"),
    _tool("ue_hlod", "unreal", "HLOD", "мир",
          "Иерархические LOD: объединение групп удалённых объектов в упрощённые прокси-меши.",
          "editor", "UE_HLOD"),
    _tool("ue_virtual_texturing", "unreal", "Virtual Texturing", "текстуры",
          "Виртуальное текстурирование: подкачка тайлов текстур по demands, снимает ограничение "
          "на объём VRAM.", "runtime", "UE_VIRTUALTEXTURING"),
    _tool("ue_insights", "unreal", "Unreal Insights", "профилирование",
          "Встроенный профилировщик с трассировкой кадров, потоков, загрузки и памяти.",
          "profiler", "UE_INSIGHTS"),
    _tool("ue_navmesh", "unreal", "Navigation Mesh", "ИИ",
          "Навмеш и система поиска пути с поддержкой областей стоимости и динамического перестроения.",
          "runtime", "UE_NAVMESH"),
    _tool("ue_replication_graph", "unreal", "Replication Graph", "сеть",
          "Граф репликации для массовой сетевой репликации: приоритизация и релевантность акторов.",
          "runtime", "UE_REPGRAPH"),
    # Инструмент был пропущен: `methods_data.ALL_LINKS` ссылался на
    # `ue_networking`, источник `UE_NETWORKING` зарегистрирован, а записи
    # инструмента не существовало. Обе ссылки («предсказание и реконсиляция»,
    # «выделенный сервер») молча отбрасывались как ссылки на неизвестный
    # инструмент, и два метода оставались без связи с Unreal.
    _tool("ue_networking", "unreal", "Networking and Multiplayer", "сеть",
          "Сетевая подсистема UE: предсказание на клиенте и реконсиляция, "
          "репликация движения, сборка выделенного сервера.",
          "runtime", "UE_NETWORKING"),
    _tool("ue_significance", "unreal", "Significance Manager", "производительность",
          "Менеджер значимости: оценка важности объектов для распределения бюджета обновлений.",
          "runtime", "UE_SIGNIFICANCE"),
    _tool("ue_anim_budget", "unreal", "Animation Budget Allocator", "анимация",
          "Распределяет бюджет времени на анимацию между персонажами, автоматически снижая "
          "детализацию при перегрузке.", "runtime", "UE_ANIMBUDGET"),
    _tool("ue_ism", "unreal", "Instanced / Hierarchical Static Mesh", "рендер",
          "Компоненты инстансированного рендера большого количества одинаковых мешей.",
          "runtime", "UE_ISM"),
    _tool("ue_mass", "unreal", "Mass Entity", "ИИ",
          "ECS-фреймворк для симуляции большого количества агентов и толпы.", "runtime", "UE_MASS",
          min_version="5.0"),
    _tool("ue_lwc", "unreal", "Large World Coordinates", "мир",
          "Поддержка больших миров за счёт double-координат иorigin rebasing.", "runtime", "UE_LWC",
          min_version="5.0"),
    _tool("ue_lod", "unreal", "Static Mesh LOD", "рендер",
          "Автоматическая и ручная генерация уровней детализации мешей.", "editor", "UE_LOD"),
    _tool("ue_gas", "unreal", "Gameplay Ability System", "геймплей",
          "Плагин способностей: атрибуты, эффекты, теги, кулдауны и Machine состояний активации.",
          "runtime", docs_url="https://dev.epicgames.com/documentation/en-us/unreal-engine/gameplay-ability-system-for-unreal-engine",
          source_title="Unreal Engine: Gameplay Ability System"),
    _tool("ue_behavior_tree", "unreal", "Behavior Tree", "ИИ",
          "Деревья поведений с общей памятью (blackboard), декораторами и сервисами для индивидуального ИИ.",
          "runtime", docs_url="https://dev.epicgames.com/documentation/en-us/unreal-engine/behavior-trees-in-unreal-engine",
          source_title="Unreal Engine: Behavior Trees"),
    _tool("ue_vehicles", "unreal", "Chaos Vehicles", "физика",
          "Физика колёсного транспорта на Chaos: подвеска, сцепление, привод и повреждения.",
          "runtime", docs_url="https://dev.epicgames.com/documentation/en-us/unreal-engine/vehicles-in-unreal-engine",
          source_title="Unreal Engine: Vehicles"),

    # ---------------- Unity ----------------
    _tool("u_dots", "unity", "Entities / DOTS", "архитектура",
          "ECS-архитектура с Data-Oriented размещением данных и Burst-компиляцией задач.",
          "runtime", "UNITY_ENTITIES"),
    _tool("u_jobs", "unity", "C# Job System", "многопоточность",
          "Система параллельных задач с контролем зависимостей и Burst-компиляцией.",
          "runtime", "UNITY_JOBS"),
    _tool("u_addressables", "unity", "Addressables", "ассеты",
          "Адресуемая система ассетов с асинхронной загрузкой, бандлами и удалённым хостингом.",
          "editor", "UNITY_ADDRESSABLES"),
    _tool("u_srp", "unity", "URP / HDRP", "рендер",
          "Настраиваемые рендер-конвейеры: универсальный (URP) и высокодетализированный (HDRP).",
          "runtime", "UNITY_GFX_PERF"),
    _tool("u_instancing", "unity", "GPU Instancing", "рендер",
          "Инстансированный рендер одинаковых мешей с одним draw call.", "runtime", "UNITY_INSTANCING"),
    _tool("u_occlusion", "unity", "Occlusion Culling", "отсечение",
          "Запечённое отсечение по окклюзии с порталами для статических сцен.",
          "editor", "UNITY_OCCLUSION"),
    _tool("u_lightmapper", "unity", "Progressive Lightmapper", "освещение",
          "Прогрессивный лайтмаппер с CPU- и GPU-бэкендом, инкрементальным пересчётом.",
          "editor", "UNITY_LIGHTMAPPER"),
    _tool("u_light_probes", "unity", "Light Probes", "освещение",
          "Зонды освещённости для динамических объектов в сценах с запечённым освещением.",
          "runtime", "UNITY_LIGHTPROBES"),
    _tool("u_vfxgraph", "unity", "Visual Effect Graph", "частицы",
          "GPU-система частиц на графе с симуляцией миллионов частиц.", "runtime", "UNITY_GFX_PERF"),
    _tool("u_profiler", "unity", "Profiler", "профилирование",
          "Профилировщик CPU, GPU, памяти, рендера и аудио с покадровой трассировкой.",
          "profiler", "UNITY_PROFILER"),
    _tool("u_navmesh", "unity", "NavMesh", "ИИ",
          "Система навмешей с компонентами для рантайм-сборки и стриминга.", "runtime", "UNITY_QUALITY"),
    _tool("u_netcode", "unity", "Netcode for Entities", "сеть",
          "Сетевой код с предсказанием на клиенте, интерполяцией и сжатием состояния.",
          "runtime", "UNITY_NETCODE"),
    _tool("u_texture_streaming", "unity", "Mipmap Streaming", "текстуры",
          "Потоковая подкачка мип-уровней текстур по demands с контролом бюджета памяти.",
          "runtime", "UNITY_TEXTURE_STREAMING"),
    _tool("u_srp_batcher", "unity", "SRP Batcher", "рендер",
          "Батчер рендер-конвейера, снижающий накладные расходы на смену состояния шейдеров.",
          "runtime", "UNITY_SRP_BATCHER"),
    _tool("u_lod_group", "unity", "LOD Group", "рендер",
          "Компонент переключения уровней детализации по дистанции до камеры.",
          "editor", "UNITY_GFX_PERF"),
    _tool("u_quality", "unity", "Quality Settings", "настройки",
          "Профили качества: разрешение, дальность, качество теней, текстур, частиц, LOD-смещение.",
          "editor", "UNITY_QUALITY"),

    # ---------------- Godot ----------------
    _tool("g_multimesh", "godot", "MultiMeshInstance3D", "рендер",
          "Инстансированный рендер большого количества копий меша за один вызов отрисовки.",
          "runtime", "GODOT_MULTIMESH"),
    _tool("g_occluder", "godot", "OccluderInstance3D", "отсечение",
          "Окклюдеры и порталы для ручного отсечения невидимой геометрии.", "editor", "GODOT_OCCLUSION"),
    _tool("g_mesh_lod", "godot", "Automatic Mesh LOD", "рендер",
          "Автоматическая генерация и переключение уровней детализации мешей.",
          "editor", "GODOT_MESHLOD"),
    _tool("g_gi", "godot", "VoxelGI / LightmapGI / SDFGI", "освещение",
          "Три варианта глобального освещения: воксельное, запечённое в лайтмапы и на SDF.",
          "runtime", "GODOT_LIGHTS"),
    _tool("g_shadows", "godot", "DirectionalLight3D Shadows", "тени",
          "Настройки теней: PSSM-каскады, разрешение, смещения и фильтрация.", "runtime", "GODOT_LIGHTS"),
    _tool("g_gpu_particles", "godot", "GPUParticles3D", "частицы",
          "Частицы с симуляцией на GPU и поддержкой аттракторов и коллизий.", "runtime", "GODOT_PARTICLES"),
    _tool("g_physics_server", "godot", "PhysicsServer3D", "физика",
          "Сервер физики с контролем областей, слоёв и частоты обновления.", "runtime", "GODOT_PHYSICS"),
    _tool("g_navigation", "godot", "NavigationServer3D", "ИИ",
          "Навигационный сервер с навмешами, агентами и обходом препятствий.", "runtime", "GODOT_PERF"),
    _tool("g_bg_loading", "godot", "ResourceLoader (фоновое загрузка)", "мир",
          "Асинхронная загрузка ресурсов в отдельном потоке для организации стриминга.",
          "runtime", "GODOT_THREADS"),
    _tool("g_threads", "godot", "Thread / WorkerThreadPool", "многопоточность",
          "Низкоуровневые потоки и пул рабочих потоков для распараллеливания расчётов.",
          "runtime", "GODOT_THREADS"),
    _tool("g_multiplayer", "godot", "MultiplayerAPI", "сеть",
          "Высокоуровневый API мультиплеера с RPC, синхронизацией и репликацией.",
          "runtime", "GODOT_MULTIPLAYER"),
    _tool("g_profiler", "godot", "Профилировщик Godot", "профилирование",
          "Встроенные счётчики производительности и визуальные профилировщики.",
          "profiler", "GODOT_PERF"),
    _tool("g_visibility", "godot", "Ручное управление видимостью", "отсечение",
          "Управление видимостью и обновлением объектов через ноды сцены и слои.",
          "runtime", "GODOT_PERF"),

    # ---------------- Собственный движок ----------------
    _tool("c_job_system", "custom", "Система задач (job system)", "многопоточность",
          "Собственный планировщик задач с пулом потоков и учётом зависимостей.", "runtime"),
    _tool("c_ecs", "custom", "Собственный ECS", "архитектура",
          "Собственная Data-Oriented архитектура сущностей и компонентов.", "runtime"),
    _tool("c_render_graph", "custom", "Граф рендера", "рендер",
          "Собственный граф рендера с автоматическим управлением ресурсами и проходами.", "runtime"),
    _tool("c_memory", "custom", "Аллокатор и пулинг памяти", "память",
          "Собственные аренные аллокаторы и пулы объектов для исключения фрагментации.", "runtime"),
    _tool("c_streaming", "custom", "Подсистема стриминга", "мир",
          "Собственный стриминг плиток мира с приоритизацией и вытеснением.", "runtime"),
    _tool("c_profiler", "custom", "Встроенный профилировщик / Tracy", "профилирование",
          "Инструментированный профилировщик с покадровой трассировкой.", "profiler"),
    _tool("c_manual", "custom", "Реализация вручную", "общее",
          "Встроенного аналога нет: решение реализуется полностью силами команды.", "runtime"),

    # ---------------- CryEngine (Трек 1, минимум) ----------------
    _tool("ce_vegetation", "cryengine", "Vegetation + Touch Bending", "рендер",
          "Покраска вегетации по маскам, wind/detail bending на GPU, спрайты вдали.",
          docs_url="https://docs.cryengine.com", source_title="CryEngine Docs"),
    _tool("ce_svogi", "cryengine", "SVOGI / SVOTI", "освещение",
          "Воксельное глобальное освещение: конусная трассировка по разреженному октодереву.",
          docs_url="https://docs.cryengine.com", source_title="CryEngine Docs"),
    _tool("ce_fog", "cryengine", "Volumetric Fog / Clouds", "атмосфера",
          "Объёмный туман и облака; туман одновременно арт-приём и оптимизация дальности.",
          docs_url="https://docs.cryengine.com", source_title="CryEngine Docs"),
    _tool("ce_merged", "cryengine", "Merged Meshes / HLOD", "мир",
          "Слияние статики и LOD-цепочки для снижения draw calls открытого мира.",
          docs_url="https://docs.cryengine.com", source_title="CryEngine Docs"),
    _tool("ce_audio", "cryengine", "CryAudio + окклюзия", "аудио",
          "Трассировка слышимости по геометрии, HRTF, аттенюация по материалам.",
          docs_url="https://docs.cryengine.com", source_title="CryEngine Docs"),

    # ---------------- Source / Source 2 (Трек 1, минимум) ----------------
    _tool("s_vphysics", "source", "VPhysics / Rubikon", "физика",
          "Твёрдые тела со сном/пробуждением, substance-материалы, констрейнты; в Source 2 — Rubikon.",
          docs_url="https://developer.valvesoftware.com/wiki/Main_Page",
          source_title="Valve Developer Community"),
    _tool("s_portal", "source", "Stencil-порталы / BSP", "рендер",
          "Рекурсивный stencil-рендер порталов и BSP/PVS-отсечение коридорных сцен.",
          docs_url="https://developer.valvesoftware.com/wiki/Main_Page",
          source_title="Valve Developer Community"),
    _tool("s_netcode", "source", "Tick / Interp / Lagcomp", "сеть",
          "Тикрейт, интерполяция и компенсация задержек; в CS2 — sub-tick с меткой времени.",
          docs_url="https://developer.valvesoftware.com/wiki/Main_Page",
          source_title="Valve Developer Community"),
    _tool("s_vulkan", "source", "Source 2 Vulkan-рендер", "рендер",
          "Многопоточный Vulkan-рендер с батчингом submit и кэшем конвейеров (уроки Dota 2).",
          docs_url="https://developer.valvesoftware.com/wiki/Main_Page",
          source_title="Valve Developer Community"),
    _tool("s_vprof", "source", "VProf / net_graph", "профилирование",
          "Внутриигровой профайлер кадра и сетевой граф: тик, choke/loss, interp.",
          docs_url="https://developer.valvesoftware.com/wiki/Main_Page",
          source_title="Valve Developer Community"),

    # ---------------- HeroEngine (Трек 1, минимум) ----------------
    _tool("h_blade", "heroengine", "HeroBlade", "мир",
          "Live-редактирование мира всей командой на одном дев-сервере без nightly builds.",
          docs_url="https://heroengine.com", source_title="HeroEngine"),
    _tool("h_cloud", "heroengine", "HeroCloud", "сеть",
          "Хостинг, биллинг и симуляционные серверы MMO как сервис.",
          docs_url="https://heroengine.com", source_title="HeroEngine"),
    _tool("h_instancing", "heroengine", "Инстансинг планет / шардинг", "сеть",
          "Копии зон и фаззинг вместо бесшовности при тысячах игроков.",
          docs_url="https://heroengine.com", source_title="HeroEngine"),
    _tool("h_hsl", "heroengine", "HeroScript (HSL)", "скрипты",
          "Скриптовый язык геймплея поверх C++/C# ядра.",
          docs_url="https://heroengine.com", source_title="HeroEngine"),
]
