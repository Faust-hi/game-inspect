"""Каталог игровых функций (MVP: 15 функций)."""
from __future__ import annotations

from .sources import src

# Форматы: 2D / 2.5D / 3D. Типы мира: linear / hub / arena / open_world / procedural / sandbox.
GAME_FUNCTIONS: list[dict] = [
    {
        "code": "open_world_streaming",
        "name": "Потоковая загрузка открытого мира",
        "description": "Непрерывная подгрузка и выгрузка частей мира при движении игрока без экранов загрузки.",
        "category": "Мир и загрузка",
        "formats": ["3D", "2.5D", "2D"],
        "typical_world_types": ["open_world", "procedural", "sandbox"],
        "sort_order": 10,
        "source_key": "UE_WORLDPARTITION",
    },
    {
        "code": "large_scale_terrain",
        "name": "Крупномасштабный ландшафт",
        "description": "Рендер обширных поверхностей с сохранением детализации вблизи и обобщением вдали.",
        "category": "Мир и загрузка",
        "formats": ["3D", "2.5D"],
        "typical_world_types": ["open_world", "procedural", "sandbox", "hub"],
        "sort_order": 20,
        "source_key": "UE_NANITE",
    },
    {
        "code": "procedural_vegetation",
        "name": "Растительность и объекты окружения",
        "description": "Массовое размещение деревьев, травы, камней и прочих повторяющихся объектов.",
        "category": "Мир и загрузка",
        "formats": ["3D", "2.5D", "2D"],
        "typical_world_types": ["open_world", "procedural", "sandbox", "linear"],
        "sort_order": 30,
        "source_key": "UE_ISM",
    },
    {
        "code": "dynamic_global_illumination",
        "name": "Динамическое глобальное освещение",
        "description": "Переотражённый свет, пересчитываемый при изменении освещения и геометрии в рантайме.",
        "category": "Освещение",
        "formats": ["3D", "2.5D"],
        "typical_world_types": ["open_world", "linear", "hub", "arena", "procedural", "sandbox"],
        "sort_order": 40,
        "source_key": "UE_LUMEN",
    },
    {
        "code": "baked_lighting",
        "name": "Запечённое освещение",
        "description": "Предварительный расчёт освещения статической геометрии в лайтмапы и зонды.",
        "category": "Освещение",
        "formats": ["3D", "2.5D", "2D"],
        "typical_world_types": ["linear", "hub", "arena"],
        "sort_order": 50,
        "source_key": "WIKI_LIGHTMAP",
    },
    {
        "code": "dynamic_shadows",
        "name": "Динамические тени",
        "description": "Тени от подвижных источников света и подвижных объектов, пересчитываемые каждый кадр.",
        "category": "Освещение",
        "formats": ["3D", "2.5D", "2D"],
        "typical_world_types": ["open_world", "linear", "hub", "arena", "procedural", "sandbox"],
        "sort_order": 60,
        "source_key": "WIKI_SHADOWMAP",
    },
    {
        "code": "particle_systems",
        "name": "Системы частиц",
        "description": "Визуальные эффекты из большого числа элементов: дым, огонь, искры, обломки.",
        "category": "Визуальные эффекты",
        "formats": ["3D", "2.5D", "2D"],
        "typical_world_types": ["open_world", "linear", "hub", "arena", "procedural", "sandbox"],
        "sort_order": 70,
        "source_key": "WIKI_PARTICLES",
    },
    {
        "code": "physics_simulation",
        "name": "Физическая симуляция",
        "description": "Твёрдые тела, сочленения, разрушения и взаимодействие объектов с учётом коллизий.",
        "category": "Симуляция",
        "formats": ["3D", "2.5D", "2D"],
        "typical_world_types": ["open_world", "linear", "hub", "arena", "procedural", "sandbox"],
        "sort_order": 80,
        "source_key": "UE_CHAOS",
    },
    {
        "code": "character_animation",
        "name": "Анимация персонажей",
        "description": "Скелетная анимация, скиннинг, смешивание и IK для персонажей и существ.",
        "category": "Персонажи",
        "formats": ["3D", "2.5D", "2D"],
        "typical_world_types": ["open_world", "linear", "hub", "arena", "procedural", "sandbox"],
        "sort_order": 90,
        "source_key": "WIKI_SKINNING",
    },
    {
        "code": "crowd_simulation",
        "name": "Толпы NPC",
        "description": "Одновременная симуляция и отрисовка десятков и сотен NPC в кадре.",
        "category": "Персонажи",
        "formats": ["3D", "2.5D", "2D"],
        "typical_world_types": ["open_world", "linear", "hub", "sandbox"],
        "sort_order": 100,
        "source_key": "UE_MASS",
    },
    {
        "code": "ai_pathfinding",
        "name": "ИИ и поиск пути",
        "description": "Навигация агентов по миру с обходом препятствий и динамикой окружения.",
        "category": "Симуляция",
        "formats": ["3D", "2.5D", "2D"],
        "typical_world_types": ["open_world", "linear", "hub", "arena", "procedural", "sandbox"],
        "sort_order": 110,
        "source_key": "WIKI_NAVMESH",
    },
    {
        "code": "water_simulation",
        "name": "Водные поверхности",
        "description": "Поверхность воды с волнами, отражениями, преломлением и взаимодействием.",
        "category": "Визуальные эффекты",
        "formats": ["3D", "2.5D", "2D"],
        "typical_world_types": ["open_world", "procedural", "sandbox", "linear"],
        "sort_order": 120,
        "source_key": "WIKI_GERSTNER",
    },
    {
        "code": "volumetric_effects",
        "name": "Объёмные эффекты (туман, облака, дымка)",
        "description": "Рассеивание света в объёме: туман, облака, световые лучи, атмосферная дымка.",
        "category": "Визуальные эффекты",
        "formats": ["3D", "2.5D", "2D"],
        "typical_world_types": ["open_world", "linear", "hub", "arena", "procedural", "sandbox"],
        "sort_order": 130,
        "source_key": "WIKI_VOLUMETRIC",
    },
    {
        "code": "post_processing",
        "name": "Постобработка изображения",
        "description": "Экранные эффекты после основного рендера: сглаживание, масштабирование, цветокоррекция, свечение.",
        "category": "Рендер",
        "formats": ["3D", "2.5D", "2D"],
        "typical_world_types": ["open_world", "linear", "hub", "arena", "procedural", "sandbox"],
        "sort_order": 140,
        "source_key": "WIKI_TAA",
    },
    {
        "code": "multiplayer_netcode",
        "name": "Сетевой код мультиплеера",
        "description": "Синхронизация состояния между клиентами и сервером, компенсация задержек, репликация.",
        "category": "Сеть",
        "formats": ["3D", "2.5D", "2D"],
        "typical_world_types": ["open_world", "arena", "hub", "sandbox", "procedural"],
        "sort_order": 150,
        "source_key": "WIKI_PREDICTION",
    },
]


def with_sources() -> list[dict]:
    """Добавить поля источника к каждой функции."""
    out = []
    for fn in GAME_FUNCTIONS:
        s = src(fn.pop("source_key", None))
        fn["source_title"] = s["title"]
        fn["source_url"] = s["url"]
        fn["source_date"] = s["date"]
        out.append(fn)
    return out
