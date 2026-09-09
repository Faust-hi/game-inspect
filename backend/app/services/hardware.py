"""Единая расчётная модель нагрузки и ориентировочного класса оборудования.

Результат намеренно формулируется как ориентировочный класс, а не как гарантия
конкретного значения FPS: система не располагает данными профилирования
конкретного проекта и не должна создавать ложную точность.

Принципы модели (исправленная расчётная модель)
----------------------------------------------
1. **Сумма затрат подсистем, а не перемножение несвязанных нагрузок.**
   Стоимость кадра складывается из стоимостей подсистем CPU и GPU. Множители
   из разных подсистем больше не перемножаются: экономия в одной подсистеме
   не компенсирует нагрузку в другой.

2. **CPU: последовательная и параллельная работа разделены.**
   `main_thread` и `render_prep` образуют критический путь одного потока
   (проверяется по `single_thread_score`). Остальные подсистемы считаются
   распределяемыми между потоками (проверяются по `multi_thread_score`
   с учётом коэффициента распараллеливания). Процессор подбирается по обеим
   характеристикам: недостаточная любая из них делает запись неподходящей.

3. **GPU: растеризация, трассировка и память считаются раздельно.**
   `raster`-составляющая сравнивается с `raster_score`, `rt`-составляющая —
   с `rt_score`. Требование видеопамяти проверяется отдельно и не заменяется
   более производительной картой меньшего объёма.

4. **Ограничение производительности — самый медленный участок кадра.**
   `bottleneck` указывает стадию с наибольшей долей использованного бюджета
   кадра: именно она определяет достижимый результат. Все пять стадий
   сравниваются в одной шкале — доля бюджета кадра. Память отдельно:
   сравнивать гигабайты с миллисекундами нельзя, поэтому в сравнении участвует
   не рабочий набор, а вызванный его дефицитом простой подкачки.

5. **Работа на кадр отделена от работы на такт симуляции.**
   Физика и AI имеют собственную частоту (`physics_tick_hz`, такт AI).
   Изменение целевого FPS не пересчитывает физику: её вклад в кадр равен
   «стоимость такта × частота тактов / частота кадров» (модель fixed update).
   Повышение FPS разгружает каждый кадр, но не сам такт симуляции.

6. **Апскейлинг отделён от генерации кадров.**
   Апскейлинг снижает стоимость тех стадий рендера, которые зависят от
   внутреннего разрешения, и добавляет стоимость собственного прохода.
   Генерация кадров не удешевляет отрисованные кадры: она добавляет стоимость
   синтеза промежуточных кадров и не даёт общей скидки на все ресурсы.

7. **Память считается составом ресурсов и буферов.**
   RAM и VRAM складываются из поименованных компонентов (текстуры, геометрия,
   целевые буферы, стриминг, аудио, зеркало ресурсов в оперативной памяти).
   Одна и та же экономия не проходит дважды через профиль, функцию и выбранный
   метод: метод меняет конкретный компонент. Ресурсы, загруженные в
   видеопамять, могут иметь CPU-копии или временные буферы загрузки. Их объём
   учитывается отдельно и не задаёт универсального неравенства RAM ≥ VRAM.

8. **Перекрытие эффектов.**
   Если несколько решений уменьшают одну и ту же подсистему, по умолчанию
   учитывается наибольшая экономия в группе, а не их сумма: добавление решений
   само по себе не является численным бонусом. Совместный эффект применяется
   только при обоснованной связи `complement`. Дополнительные затраты
   (положительные вклады) сохраняются всегда.

9. **Одна модель для нагрузки, подбора оборудования и объяснений.**
   `build_model` строит стоимость кадра; `estimate_hardware` подбирает
   оборудование по этой же модели; `build_contributions` объясняет результат
   через вклад параметров, вклад решений, принятые допущения и причины
   неучёта эффекта.

10. **Отсутствие подходящего оборудования сообщается явно.**
    Если в каталоге нет записи, одновременно удовлетворяющей производительности,
    памяти и обязательным возможностям, конфигурация не подставляется:
    результат содержит явное сообщение и признак `exceeds_catalog`.

Коэффициенты в этом модуле — экспертные оценки, а не измерения. Единственный
публикуемый показатель точности (±70%) является **целью модели**, а не
подтверждённым результатом: независимая калибровка не выполнялась.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

from sqlalchemy.orm import Session

from .. import repositories
from ..models.entities import HardwareCPU, HardwareGPU
from ..schemas.catalog import (
    ContributionItem, ContributionsOut, HardwareEstimateOut, MemoryComposition,
    NonClientMethodOut, PracticeCheckOut, ProjectProfile, SubsystemBreakdown,
    count_scale_bounds, level_unspecified,
)
from . import rules, serializers

SCALE_FACTOR = {"small": 0.8, "medium": 1.0, "large": 1.25, "very_large": 1.5, "unknown": 1.0}
RESOLUTION_FACTOR = {
    "720p": 0.62, "768p": 0.68, "900p": 0.78, "1080p": 1.0,
    "1200p": 1.12, "1440p": 1.6, "1600p": 1.85, "2160p": 3.0, "4k": 3.0,
}
QUALITY_FACTOR = {"low": 0.7, "medium": 1.0, "high": 1.35, "ultra": 1.7}

# --- Подсистемы -------------------------------------------------------------
# Подсистемы CPU.
CPU_SUBSYSTEMS: list[str] = [
    "main_thread",        # основной игровой цикл, управление кадрами
    "render_prep",        # подготовка команд рендера (draw calls, culling)
    "parallel_sim",       # параллельная симуляция (Job System, ECS)
    "physics",            # физическое моделирование (такт симуляции)
    "animation",          # анимация персонажей, скининг
    "ai",                 # AI, pathfinding, crowd (такт симуляции)
    "audio",              # аудио-декодирование, пространственный звук
    "network",            # сетевая репликация, сериализация
    "streaming",          # потоковая загрузка, декомпрессия
    "compute",            # CPU-side compute (подготовка compute шейдеров)
    "post_processing",    # CPU-side постобработка
]

# Подсистемы GPU.
GPU_SUBSYSTEMS: list[str] = [
    "geometry",           # вершинная обработка, геометрия
    "shading",            # затенение, материалы, текстурирование
    "lighting_shadows",   # освещение, тени
    "transparency",       # прозрачность, частицы, пост-FX прозрачных объектов
    "post_processing",    # постобработка, цветокоррекция, блум
    "compute",            # compute шейдеры (не связанные с растеризацией)
    "raster",             # растеризация (базовый проход, заливка)
    "rt",                 # трассировка лучей (RT)
]

#: Критический путь одного потока: эти подсистемы не распараллеливаются.
CPU_SEQUENTIAL_SUBSYSTEMS: frozenset[str] = frozenset({"main_thread", "render_prep"})

#: Подсистемы, работающие по собственному такту симуляции, а не по кадру.
CPU_TICK_SUBSYSTEMS: frozenset[str] = frozenset({"physics", "ai"})

#: Подсистемы GPU, стоимость которых зависит от разрешения (заливка, пиксели).
GPU_PIXEL_SUBSYSTEMS: frozenset[str] = frozenset({
    "shading", "lighting_shadows", "transparency", "post_processing", "raster", "rt",
})

#: Подсистемы GPU, стоимость которых зависит от уровня качества материалов/света.
GPU_QUALITY_SUBSYSTEMS: frozenset[str] = frozenset({
    "shading", "lighting_shadows", "transparency", "post_processing",
})

CPU_SUBSYSTEM_LABELS: dict[str, str] = {
    "main_thread": "Главный поток",
    "render_prep": "Подготовка рендера",
    "parallel_sim": "Параллельная симуляция",
    "physics": "Физика (такт симуляции)",
    "animation": "Анимация",
    "ai": "AI и поиск пути",
    "audio": "Аудио",
    "network": "Сеть",
    "streaming": "Потоковая загрузка",
    "compute": "Вычисления на CPU",
    "post_processing": "Постобработка на CPU",
}

GPU_SUBSYSTEM_LABELS: dict[str, str] = {
    "geometry": "Геометрия",
    "shading": "Затенение",
    "lighting_shadows": "Освещение и тени",
    "transparency": "Прозрачность и частицы",
    "post_processing": "Постобработка",
    "compute": "Вычисления на GPU",
    "raster": "Растеризация",
    "rt": "Трассировка лучей",
    "frame_generation": "Генерация кадров",
}

BOTTLENECK_LABELS: dict[str, str] = {
    "cpu_main_thread": "главный поток CPU",
    "cpu_parallel": "параллельная работа CPU",
    "gpu_raster": "обычный рендеринг GPU",
    "gpu_rt": "трассировка лучей GPU",
    "memory": "память (RAM/VRAM)",
}
BOTTLENECK_TITLES: dict[str, str] = {
    "cpu_main_thread": "CPU (главный поток)",
    "cpu_parallel": "CPU (многопоточная работа)",
    "gpu_raster": "GPU (растеризация)",
    "gpu_rt": "GPU (трассировка лучей)",
    "memory": "Память",
}

#: Коэффициент распараллеливания: во столько условных потоков распределяется
#: параллельная работа. Экспертная оценка: реальная степень параллелизма
#: ограничена зависимостями между задачами и не измерялась.
PARALLEL_SPEEDUP = 2.4

#: Калибровочные переводы «вес функции» -> миллисекунды работы на кадр.
#: Экспертные коэффициенты: измерений на реальных проектах не выполнялось.
#: Ориентиры калибровки — published-рейтинги technical.city/PassMark:
#: тяжёлый открытый мир 1080p/high/60 с разумной корзиной оптимизаций
#: сходится к классу RTX 3060 (raster_score 0.43), тот же мир без оптимизаций
#: на 1440p — к классу RTX 3070 и выше.
CPU_FEATURE_MS = 10.0
GPU_FEATURE_MS = 6.2

#: Базовая стоимость кадра (мс) на эталонной конфигурации при content = 1,
#: 1080p, высоком качестве, без выбранных функций.
CPU_BASE_COST: dict[str, float] = {
    "main_thread": 2.2,
    "render_prep": 1.8,
    "parallel_sim": 0.6,
    "physics": 0.0,
    "animation": 0.0,
    "ai": 0.0,
    "audio": 0.3,
    "network": 0.0,
    "streaming": 0.2,
    "compute": 0.1,
    "post_processing": 0.1,
}

GPU_BASE_COST: dict[str, float] = {
    "geometry": 0.38,
    "shading": 0.88,
    "lighting_shadows": 0.25,
    "transparency": 0.13,
    "post_processing": 0.19,
    "compute": 0.06,
    "raster": 0.38,
    "rt": 0.0,
}

# Вклад функций в подсистемы CPU (относительные веса, переводятся в мс
# умножением на CPU_FEATURE_MS). Сложение, а не перемножение: две функции,
# нагружающие физику, складывают свою стоимость.
FEATURE_CPU_SUBSYSTEM_LOAD: dict[str, dict[str, float]] = {
    "open_world_streaming":     {"streaming": 0.10, "main_thread": 0.06},
    "large_scale_terrain":      {"streaming": 0.05, "main_thread": 0.03},
    "procedural_vegetation":    {"parallel_sim": 0.07, "main_thread": 0.03},
    "dynamic_global_illumination": {"compute": 0.04, "main_thread": 0.02},
    "baked_lighting":           {"main_thread": 0.04},
    "dynamic_shadows":          {"render_prep": 0.04, "main_thread": 0.02},
    "particle_systems":         {"parallel_sim": 0.04, "main_thread": 0.02},
    "physics_simulation":       {"physics": 0.12, "parallel_sim": 0.06},
    "character_animation":      {"animation": 0.07, "parallel_sim": 0.03},
    "crowd_simulation":         {"ai": 0.14, "parallel_sim": 0.08},
    "ai_pathfinding":           {"ai": 0.12, "parallel_sim": 0.06},
    "water_simulation":         {"physics": 0.02, "parallel_sim": 0.01},
    "volumetric_effects":       {"compute": 0.02, "main_thread": 0.01},
    "post_processing":          {"post_processing": 0.02, "main_thread": 0.01},
    "multiplayer_netcode":      {"network": 0.10, "main_thread": 0.06},
    "rendering_architecture":   {"render_prep": 0.07, "main_thread": 0.03},
    "render_scalability":       {"main_thread": 0.03},
    "geometry_pipeline":        {"render_prep": 0.05, "main_thread": 0.02},
    "upscaling_frame_generation": {"post_processing": 0.01, "main_thread": 0.01},
    "storage_streaming":        {"streaming": 0.07, "main_thread": 0.03},
    "audio_system":             {"audio": 0.04, "main_thread": 0.01},
    "build_delivery":           {},
    "runtime_memory":           {"main_thread": 0.08},
    # Сохранения: запись идёт через ту же подсистему ввода-вывода, что и
    # потоковая загрузка, поэтому функция не остаётся без статьи бюджета.
    "save_system":              {"streaming": 0.04, "main_thread": 0.01},
    "destruction_simulation":   {"physics": 0.10, "parallel_sim": 0.06},
    "project_architecture":     {"main_thread": 0.02},
    "art_pipeline":             {},
    "split_screen_rendering":   {"render_prep": 0.08, "main_thread": 0.04},
    # --- Трассировка лучей -------------------------------------------------
    # Полная трассировка пути заменяет растровое освещение, поэтому её стоимость
    # лежит в отдельной подсистеме `rt`, а не размывается по стадиям растра.
    "path_tracing":             {"compute": 0.04, "main_thread": 0.02},
    "ray_traced_effects":       {"compute": 0.02, "main_thread": 0.01},
    "dynamic_lighting":         {"render_prep": 0.06, "main_thread": 0.03},
    "mesh_shaders":             {"render_prep": 0.02, "main_thread": 0.01},
    # --- Мир, геймплей и симуляция ----------------------------------------
    "procedural_terrain":       {"streaming": 0.06, "parallel_sim": 0.05, "main_thread": 0.04},
    "gameplay_ability_system":  {"main_thread": 0.05, "parallel_sim": 0.04},
    "vehicle_simulation":       {"physics": 0.10, "parallel_sim": 0.05},
    "advanced_npc_ai":          {"ai": 0.10, "parallel_sim": 0.05},
}

# Вклад функций в подсистемы GPU (относительные веса -> мс через GPU_FEATURE_MS).
FEATURE_GPU_SUBSYSTEM_LOAD: dict[str, dict[str, float]] = {
    "open_world_streaming":     {"shading": 0.03, "geometry": 0.02},
    "large_scale_terrain":      {"geometry": 0.05, "shading": 0.05},
    "procedural_vegetation":    {"geometry": 0.06, "shading": 0.04},
    # Динамическое ГО — одна из самых дорогих функций: вес заметно выше
    # остальных стадий освещения.
    "dynamic_global_illumination": {"lighting_shadows": 0.34, "compute": 0.14},
    "baked_lighting":           {"lighting_shadows": 0.02},
    "dynamic_shadows":          {"lighting_shadows": 0.10, "raster": 0.04},
    "particle_systems":         {"transparency": 0.06, "shading": 0.02},
    "physics_simulation":       {},
    "character_animation":      {},
    "crowd_simulation":         {"geometry": 0.05, "shading": 0.05},
    "ai_pathfinding":           {},
    "water_simulation":         {"shading": 0.06, "transparency": 0.04},
    "volumetric_effects":       {"compute": 0.10, "transparency": 0.06},
    "post_processing":          {"post_processing": 0.08},
    "multiplayer_netcode":      {},
    "rendering_architecture":   {"raster": 0.05, "geometry": 0.05},
    "render_scalability":       {"post_processing": 0.04},
    "geometry_pipeline":        {"geometry": 0.03, "raster": 0.02},
    "upscaling_frame_generation": {"post_processing": 0.04},
    "storage_streaming":        {"shading": 0.02},
    "audio_system":             {},
    "build_delivery":           {},
    "runtime_memory":           {},
    "destruction_simulation":   {"geometry": 0.07, "transparency": 0.05},
    "project_architecture":     {},
    "art_pipeline":             {},
    "split_screen_rendering":   {"raster": 0.15, "geometry": 0.05},
    # --- Трассировка лучей -------------------------------------------------
    # Вес `rt` — самый крупный в каталоге: полная трассировка пути на 1080p
    # обходится в единицы миллисекунд на кадр и растёт с разрешением, поэтому
    # она и определяет требование к RT-способности GPU.
    "path_tracing":             {"rt": 1.15},
    "ray_traced_effects":       {"rt": 0.70},
    # Множество динамических источников: стоимость уходит в затенение и
    # освещение, а не в отдельный проход трассировки.
    "dynamic_lighting":         {"lighting_shadows": 0.16, "shading": 0.05},
    # Меш-шейдеры переносят сборку и отсечение примитивов на GPU: геометрия
    # дорожает, зато число вызовов отрисовки перестаёт зависеть от CPU.
    "mesh_shaders":             {"geometry": 0.12, "raster": 0.05},
    # --- Мир, геймплей и симуляция ----------------------------------------
    "procedural_terrain":       {"geometry": 0.04, "shading": 0.02},
    "gameplay_ability_system":  {"compute": 0.02},
    "vehicle_simulation":       {"geometry": 0.02},
    "advanced_npc_ai":          {},
}

# --- Явное распределение эффектов решений по подсистемам --------------------
#
# Ключ — код решения. Значения:
#   "cpu" — {подсистема: доля} — доля, на которую решение **уменьшает**
#           стоимость подсистемы (0.30 = минус 30%). Отрицательное значение —
#           дополнительная стоимость.
#   "gpu" — то же для подсистем GPU.
#   "mem" — {компонент памяти: доля} — доля, на которую решение **изменяет**
#           размер компонента (0.20 = плюс 20%, -0.20 = минус 20%).
#   "rt_ms" — абсолютная добавка стоимости трассировки лучей (мс на кадр):
#             нужна для решений, которые вводят RT-проход там, где его не было.
#
# Распределение задано явно для каждого решения: расчёт не обращается к
# отсутствующему полю function_code и не выводит подсистему из названия.
METHOD_SUBSYSTEM_EFFECTS: dict[str, dict] = {
    # --- Мир и потоковая загрузка ---
    "world_partition_streaming": {"cpu": {"streaming": 0.30, "main_thread": 0.12}, "mem": {"streaming": 0.35}},
    "world_origin_shifting": {"cpu": {"main_thread": 0.06}},
    "hierarchical_lod": {"cpu": {"render_prep": 0.18}, "gpu": {"geometry": 0.30, "raster": 0.10}, "mem": {"meshes": 0.12}},
    "gpu_compute_culling": {"cpu": {"render_prep": 0.34, "main_thread": 0.10}, "gpu": {"compute": 0.20}},
    "baked_occlusion_culling": {"cpu": {"render_prep": 0.20}, "gpu": {"geometry": 0.12, "raster": 0.08}, "mem": {"scene": 0.10}},
    "async_loading_pipeline": {"cpu": {"streaming": 0.22, "main_thread": 0.16}},
    "tiled_clustered_light_culling": {"gpu": {"lighting_shadows": 0.22, "shading": 0.06}, "mem": {"render_targets": -0.05}},
    "tilemap_chunk_streaming": {"cpu": {"streaming": 0.26, "main_thread": 0.10}, "mem": {"streaming": 0.20}},
    "tilemap_layer_culling": {"cpu": {"render_prep": 0.16}, "gpu": {"geometry": 0.22, "raster": 0.12}},
    # --- Ландшафт ---
    "terrain_clipmap": {"cpu": {"main_thread": 0.10}, "gpu": {"geometry": 0.20, "shading": 0.08}, "mem": {"meshes": -0.20, "textures": -0.10}},
    "virtual_texturing": {"gpu": {"shading": -0.05}, "mem": {"textures": -0.45, "streaming": 0.25}},
    "heightmap_compression": {"cpu": {"streaming": -0.08}, "mem": {"textures": -0.22, "streaming": -0.15}},
    "virtual_geometry_clusters": {"cpu": {"render_prep": 0.30}, "gpu": {"geometry": 0.26, "raster": 0.06}, "mem": {"meshes": -0.10}},
    "neural_texture_compression": {"cpu": {"streaming": -0.06}, "gpu": {"shading": 0.04}, "mem": {"textures": -0.40}},
    # --- Растительность ---
    "gpu_instancing_vegetation": {"cpu": {"render_prep": 0.32, "main_thread": 0.08}, "gpu": {"geometry": 0.18, "raster": 0.06}, "mem": {"meshes": 0.06}},
    "gpu_procedural_placement": {"cpu": {"parallel_sim": 0.30, "main_thread": 0.10}, "mem": {"scene": -0.30, "streaming": -0.20}},
    "impostors_billboards": {"gpu": {"geometry": 0.34, "shading": 0.10, "raster": 0.08}, "mem": {"meshes": -0.25, "textures": 0.08}},
    "vegetation_atlas_lod": {"gpu": {"geometry": 0.16, "shading": 0.08}, "mem": {"textures": -0.12}},
    # --- Глобальное освещение ---
    "sdf_global_illumination": {"gpu": {"lighting_shadows": -0.12, "compute": -0.10}, "mem": {"scene": 0.20, "textures": 0.15}},
    "irradiance_volume_probes": {"cpu": {"main_thread": 0.10}, "gpu": {"lighting_shadows": 0.26, "compute": 0.10}, "mem": {"textures": 0.10}},
    "voxel_cone_tracing": {"gpu": {"lighting_shadows": -0.20, "compute": -0.24}, "mem": {"textures": 0.30, "render_targets": 0.15}},
    "screen_space_gi": {"gpu": {"lighting_shadows": -0.16, "post_processing": -0.10}},
    "temporal_radiance_cache": {"gpu": {"lighting_shadows": 0.24, "compute": 0.08}, "mem": {"render_targets": 0.08}},
    "hardware_raytraced_gi": {"gpu": {"lighting_shadows": 0.18, "compute": 0.10}, "mem": {"render_targets": 0.10}, "rt_ms": 3.4},
    # --- Запечённое освещение ---
    "lightmap_atlas_baking": {"cpu": {"render_prep": 0.28, "main_thread": 0.14}, "gpu": {"lighting_shadows": 0.34, "raster": 0.10}, "mem": {"textures": 0.20}},
    "gpu_lightmap_baking": {},
    "lightmap_compression_streaming": {"cpu": {"streaming": -0.10}, "mem": {"textures": -0.30}},
    "lightmap_2d_baking": {"cpu": {"render_prep": 0.22}, "gpu": {"lighting_shadows": 0.30, "raster": 0.08}, "mem": {"textures": 0.12}},
    # --- Тени ---
    "cascaded_shadow_maps": {"gpu": {"lighting_shadows": -0.10, "raster": -0.06}, "mem": {"render_targets": 0.12}},
    "virtual_shadow_maps": {"gpu": {"lighting_shadows": -0.22, "raster": -0.12}, "mem": {"render_targets": 0.25}},
    "distance_field_shadows": {"cpu": {"render_prep": 0.14}, "gpu": {"lighting_shadows": 0.22, "raster": 0.10}, "mem": {"scene": 0.18}},
    "screen_space_contact_shadows": {"gpu": {"lighting_shadows": -0.08, "post_processing": -0.06}},
    "static_shadow_caching": {"gpu": {"lighting_shadows": 0.30, "raster": 0.14}, "mem": {"render_targets": 0.08}},
    "shadow_caster_2d_limits": {"cpu": {"render_prep": 0.16}, "gpu": {"lighting_shadows": 0.20, "raster": 0.08}},
    # --- Частицы ---
    "gpu_particle_simulation": {"cpu": {"parallel_sim": 0.32, "main_thread": 0.08}, "gpu": {"compute": -0.12}, "mem": {"meshes": 0.08}},
    "particle_pooling": {"cpu": {"main_thread": 0.18}, "mem": {"scene": -0.10}},
    "flipbook_particles": {"cpu": {"parallel_sim": 0.30, "main_thread": 0.10}, "gpu": {"transparency": 0.18, "compute": 0.06}, "mem": {"textures": 0.10}},
    "sprite_particle_atlas": {"cpu": {"parallel_sim": 0.16}, "gpu": {"transparency": 0.14, "raster": 0.06}},
    # --- Физика ---
    "fixed_timestep_physics": {},
    "physics_lod_sleeping": {"cpu": {"physics": 0.30}},
    "multithreaded_physics_jobs": {"cpu": {"physics": 0.10}},
    "broadphase_spatial_partitioning": {"cpu": {"physics": 0.26}, "mem": {"scene": 0.10}},
    "collision_layer_matrix": {"cpu": {"physics": 0.28}},
    # --- Анимация ---
    "gpu_skinning_compute": {"cpu": {"animation": 0.34, "parallel_sim": 0.12}, "gpu": {"compute": -0.10}},
    "animation_compression": {"cpu": {"streaming": -0.10}, "mem": {"meshes": -0.25}},
    "animation_lod_budget": {"cpu": {"animation": 0.30}},
    "motion_matching": {"cpu": {"animation": -0.30, "main_thread": -0.10}, "mem": {"meshes": 0.30}},
    "sprite_atlas_batching": {"cpu": {"render_prep": 0.30, "animation": 0.14}, "gpu": {"raster": 0.10}, "mem": {"meshes": 0.10, "textures": 0.10}},
    "sprite_sheet_compression": {"mem": {"textures": -0.30}},
    "skeletal_2d_deform": {"cpu": {"animation": -0.12, "main_thread": -0.06}, "mem": {"meshes": -0.30, "textures": -0.15}},
    # --- Толпа и AI ---
    "ecs_data_oriented_crowd": {"cpu": {"ai": 0.34, "parallel_sim": 0.20}, "mem": {"scene": -0.10}},
    "crowd_instancing_impostors": {"cpu": {"render_prep": 0.16}, "gpu": {"geometry": 0.26, "shading": 0.10}, "mem": {"meshes": -0.15}},
    "crowd_2d_instancing": {"cpu": {"render_prep": 0.34}, "gpu": {"geometry": 0.18, "raster": 0.08}},
    "agent_update_budget": {"cpu": {"ai": 0.32}},
    "navmesh_tiling_streaming": {"cpu": {"main_thread": 0.12}, "mem": {"scene": -0.15, "streaming": 0.15}},
    "time_sliced_pathfinding": {"cpu": {"ai": 0.20, "main_thread": 0.10}},
    "flow_field_pathing": {"cpu": {"ai": 0.34}, "mem": {"scene": 0.12}},
    "rvo_local_avoidance": {"cpu": {"ai": -0.14}},
    # --- Вода и объёмы ---
    "gerstner_fft_water": {"cpu": {"physics": 0.20}, "gpu": {"shading": -0.08, "compute": -0.10}},
    "screen_space_water_simple": {"gpu": {"shading": 0.26, "transparency": 0.16}, "mem": {"render_targets": -0.08}},
    "froxel_volumetric_fog": {"gpu": {"compute": -0.20, "transparency": -0.12}, "mem": {"render_targets": 0.10}},
    "volumetric_half_resolution": {"gpu": {"compute": 0.34, "transparency": 0.20}},
    "planar_reflection_budget": {"cpu": {"render_prep": -0.14}, "gpu": {"raster": -0.24, "shading": -0.14}, "mem": {"render_targets": -0.05}},
    # --- Постобработка, апскейлинг, генерация кадров ---
    "temporal_upscaling": {"gpu": {"post_processing": 0.10}, "mem": {"render_targets": 0.10}},
    "dynamic_resolution_scaling": {"gpu": {"post_processing": 0.16}},
    "deferred_forward_plus_choice": {"gpu": {"lighting_shadows": 0.16, "shading": 0.06}, "mem": {"render_targets": -0.20}},
    "variable_rate_shading": {"gpu": {"shading": 0.30}},
    "post_effect_selective": {"gpu": {"post_processing": 0.32}},
    "depth_prepass_early_z": {"cpu": {"render_prep": -0.08}, "gpu": {"raster": 0.26, "shading": 0.10}, "mem": {"render_targets": 0.05}},
    "screenspace_light_shafts": {"gpu": {"post_processing": -0.10}},
    # --- Рендер-архитектура ---
    "hiz_software_occlusion": {"cpu": {"main_thread": -0.12}, "gpu": {"geometry": 0.28, "raster": 0.10}},
    "pso_precaching_warmup": {"cpu": {"main_thread": -0.10, "render_prep": 0.06}},
    "bindless_uber_shaders": {"cpu": {"render_prep": 0.34, "main_thread": 0.10}},
    "srp_batcher_discipline": {"cpu": {"render_prep": 0.32}},
    "mesh_index_optimization": {"gpu": {"geometry": 0.14, "raster": 0.08}},
    "splitscreen_render_budget": {"cpu": {"render_prep": -0.20}, "gpu": {"raster": -0.22, "geometry": -0.12}, "mem": {"render_targets": -0.05}},
    "quality_tier_scalability": {},
    # --- Сеть ---
    "network_relevancy_priority": {"cpu": {"network": 0.30}},
    "client_prediction_reconciliation": {"cpu": {"network": -0.16, "main_thread": -0.06}},
    "delta_compression_state": {"cpu": {"network": 0.26, "main_thread": -0.10}},
    "headless_dedicated_server": {},
    "deterministic_lockstep": {"cpu": {"network": 0.24, "main_thread": -0.14}},
    "tickrate_budgeting": {"cpu": {"network": -0.24, "main_thread": -0.08}},
    # --- Память ---
    "managed_gc_alloc_budget": {"cpu": {"main_thread": 0.30}, "mem": {"scene": -0.10}},
    # --- Аудио ---
    "audio_occlusion_propagation": {"cpu": {"audio": -0.20}},
    "audio_streaming_compression": {"cpu": {"streaming": -0.06}, "mem": {"audio": -0.30}},
    # --- Разрушения ---
    "destruction_geometry_cache": {"cpu": {"physics": 0.34}, "mem": {"meshes": 0.20}},
    # --- Прочее (эффект не на компьютере игрока или без количественной оценки) ---
    "normal_bake_retopology_pipeline": {"gpu": {"shading": 0.12}, "mem": {"meshes": -0.15, "textures": -0.10}},
    "build_size_startup_budgets": {"mem": {"streaming": -0.15}},
    "differential_patch_pipeline": {},
    "composition_bootstrap_architecture": {"cpu": {"main_thread": 0.14}},
    "art_direction_stylization": {"gpu": {"shading": 0.14}},
    "snapshot_slot_saves": {"cpu": {"main_thread": -0.10}, "mem": {"streaming": 0.10}},
    "async_incremental_saves": {"cpu": {"main_thread": 0.10, "streaming": -0.08}, "mem": {"streaming": 0.15}},
    "ml_frame_generation": {"gpu": {"post_processing": -0.10}, "mem": {"render_targets": 0.12}},
    # --- Трассировка лучей -------------------------------------------------
    # Полная трассировка пути забирает растровое освещение, но вводит свой
    # проход; экономия трассировочного бюджета задаётся по подсистеме `rt`.
    "full_path_tracing_pipeline": {
        "cpu": {"compute": -0.10},
        "gpu": {"lighting_shadows": 0.20},
        "mem": {"render_targets": 0.10},
        "rt_ms": 2.5,
    },
    "path_tracing_sample_denoiser_budget": {
        "cpu": {"post_processing": -0.10},
        "gpu": {"rt": 0.42},
    },
    "selective_ray_traced_effects": {
        "gpu": {"lighting_shadows": 0.10},
        "mem": {"render_targets": 0.08},
        "rt_ms": 1.6,
    },
    "rt_effect_resolution_budget": {"gpu": {"rt": 0.55}, "mem": {"render_targets": -0.10}},
    # --- Динамическое освещение --------------------------------------------
    "dynamic_light_priority_budget": {
        "cpu": {"render_prep": 0.22}, "gpu": {"lighting_shadows": 0.28},
    },
    "light_range_attenuation_lod": {"gpu": {"lighting_shadows": 0.18, "shading": 0.06}},
    # --- Меш-шейдеры --------------------------------------------------------
    "meshlet_pipeline_adoption": {
        "cpu": {"render_prep": 0.34, "main_thread": 0.10}, "gpu": {"geometry": 0.12},
    },
    "gpu_meshlet_culling_budget": {"gpu": {"geometry": 0.30, "raster": 0.12}},
    # --- Процедурный мир ----------------------------------------------------
    "chunked_procedural_terrain": {
        "cpu": {"streaming": 0.24, "main_thread": 0.12},
        "mem": {"meshes": 0.15, "scene": -0.20},
    },
    "terrain_generation_streaming_budget": {
        "cpu": {"main_thread": 0.20, "streaming": 0.10}, "mem": {"scene": 0.15},
    },
    # --- Геймплейные и симуляционные подсистемы -----------------------------
    "data_driven_ability_system": {"cpu": {"main_thread": 0.18, "parallel_sim": 0.16}},
    "ability_visual_effect_budget": {
        "cpu": {"parallel_sim": 0.20},
        "gpu": {"transparency": 0.24, "post_processing": 0.10},
    },
    "raycast_vehicle_physics": {"cpu": {"physics": 0.18, "parallel_sim": 0.10}},
    "vehicle_simulation_lod": {"cpu": {"physics": 0.34, "parallel_sim": 0.20}},
    "behaviour_tree_update_budget": {"cpu": {"ai": 0.30, "parallel_sim": 0.18}},
    "npc_perception_budget": {"cpu": {"ai": 0.26}},
}

#: Решения, которые включают отдельный проход трассировки лучей.
_RT_METHODS = frozenset(code for code, eff in METHOD_SUBSYSTEM_EFFECTS.items() if "rt_ms" in eff)

_API_FACTORS = {
    "auto": (1.00, 1.00),
    "dx9": (0.92, 1.15),
    "dx11": (0.98, 1.08),
    "dx12": (1.02, 0.94),
    "vulkan": (1.00, 0.95),
    "opengl": (0.96, 1.14),
    "metal": (0.98, 0.95),
}
_STORAGE_RANK = {"hdd": 0, "sata_ssd": 1, "nvme": 2}
_STORAGE_CPU_FACTOR = {"auto": 1.00, "hdd": 1.12, "sata_ssd": 1.04, "nvme": 0.98}

# Апскейлинг меняет стоимость стадий, зависящих от внутреннего разрешения,
# и добавляет стоимость собственного прохода. Это не общая скидка на все
# ресурсы: геометрия и CPU-подготовка не удешевляются.
_UPSCALER_PIXEL_FACTOR = {
    "auto": 1.00, "none": 1.00, "taa": 0.92,
    "fsr": 0.62, "dlss": 0.58, "xess": 0.66,
}
_UPSCALER_POST_MS = {"auto": 0.0, "none": 0.0, "taa": 0.2, "fsr": 0.45, "dlss": 0.5, "xess": 0.5}

#: Стоимость синтеза одного промежуточного кадра генератором кадров (мс).
FRAME_GENERATION_MS = 1.2

# Сложность аудио влияет только на CPU.
_AUDIO_CPU_LOAD = {"low": 0.00, "medium": 0.30, "high": 0.70}
_UNKNOWN_AUDIO_NOTE = (
    "Сложность аудио не указана: стоимость декодирования и пространственного "
    "звука не учтена в оценке."
)
_STORAGE_RANK_LABELS = {"hdd": "HDD", "sata_ssd": "SATA SSD", "nvme": "NVMe SSD"}

_STREAMING_METHODS = {
    "world_partition_streaming", "async_loading_pipeline", "navmesh_tiling_streaming",
    "tilemap_chunk_streaming", "audio_streaming_compression",
}

#: Такт AI по умолчанию (Гц). Используется только если частота не задана
#: пользователем; фиксируется как допущение.
DEFAULT_AI_TICK_HZ = 20.0
#: Такт физики по умолчанию (Гц) — значение по умолчанию Unity/Unreal.
DEFAULT_PHYSICS_TICK_HZ = 50.0
#: Такт сети по умолчанию (Гц).
DEFAULT_NETWORK_TICK_HZ = 30.0

#: Предельная суммарная экономия в одной подсистеме: полное обнуление работы
#: невозможно, иначе решение «убирает» саму функцию.
MAX_SUBSYSTEM_SAVING = 0.70


# --- Компоненты памяти ------------------------------------------------------
MEMORY_COMPONENT_LABELS: dict[str, str] = {
    "system": "Резерв системы и драйверов",
    "engine": "Движок и исполняемый код",
    "scene": "Данные сцены и сущности",
    "meshes": "Геометрия и вершинные буферы",
    "textures": "Текстуры и материалы",
    "render_targets": "Целевые буферы рендера",
    "audio": "Аудиоресурсы и декодирование",
    "streaming": "Стриминговые буферы и декомпрессия",
    "mirror": "Зеркало ресурсов в оперативной памяти",
}
_MEMORY_ORDER = [
    "system", "engine", "scene", "meshes", "textures", "render_targets",
    "audio", "streaming", "mirror",
]

#: Нормативы доступного объёма памяти, когда профиль не задаёт предела (ГБ).
MEMORY_NORM_VRAM_GB = 8.0
MEMORY_NORM_RAM_GB = 16.0

#: Доля норматива, до которой рабочий набор не вызывает простоев подкачки.
#: Ниже порога память не ограничивает кадр: резерв есть всегда.
MEMORY_PRESSURE_FREE_SHARE = 0.75

#: Стоимость простоя подкачки при стопроцентном превышении норматива (мс/кадр).
#: Экспертная оценка: измерений на реальных проектах не выполнялось.
MEMORY_DEFICIT_STALL_MS = 6.0

#: Доля ресурсов видеопамяти, которая одновременно присутствует в оперативной
#: памяти: исходник потоковой загрузки и CPU-копии геометрии и текстур.
VRAM_MIRROR_SHARE = 0.25

def _supports_ray_tracing(gpu: HardwareGPU) -> bool:
    """Проверяет наличие аппаратной трассировки лучей по признакам каталога."""
    features = [str(f).lower() for f in (gpu.hw_features or [])]
    return any("ray tracing" in f or "rt core" in f or "rtx" in f for f in features)


def _resolution_factor(value: str) -> float:
    if not value:
        return 1.0
    return RESOLUTION_FACTOR.get(value.strip().lower(), 1.0)


def _api_supports(gpu: HardwareGPU, api: str) -> bool:
    """Поддерживает ли карта заявленный графический API (по данным каталога)."""
    apis = [str(item).lower() for item in (gpu.api_support or [])]
    if api in {"dx9", "dx11", "dx12"}:
        required = int(api[2:])
        versions = [re.search(r"directx\s+(\d+)", item) for item in apis]
        return any(match and int(match.group(1)) >= required for match in versions)
    return any(item.startswith(api) for item in apis)


def _gpu_feature_support(gpu: HardwareGPU, required: str) -> bool | None:
    """Подтверждает ли каталог поддержку возможности картой (D05).

    True — каталог подтверждает, False — опровергает (карта заведомо без
    этой возможности), None — каталог не отвечает. Неизвестность не
    приравнивается ни к поддержке, ни к отказу: конфигурация с ней не
    может молча объявляться подходящей.
    """
    req = (required or "").strip().lower()
    if not req:
        return None
    if req.startswith("directx"):
        tail = req.split()[-1]
        return _api_supports(gpu, f"dx{tail}") if tail.isdigit() else None
    if req in {"vulkan", "opengl", "metal"}:
        return _api_supports(gpu, req)
    features = [str(f).lower() for f in (gpu.hw_features or [])]
    # «Variable Rate Shading» покрывает «… (Tier 1)», «Hardware Ray Tracing» —
    # «… (2nd gen RT cores)»: совпадение по началу названия возможности.
    if any(
        f == req or f.startswith(req + " ") or f.startswith(req + "(")
        for f in features
    ):
        return True
    if "ray tracing" in req or req in {"rt", "rtx", "rt cores", "ray accelerators"}:
        return _supports_ray_tracing(gpu)
    if req.startswith(("dlss", "fsr", "xess")):
        return any(f.startswith(req) for f in features)
    return None


def _supports_profile_gpu(gpu: HardwareGPU, profile: ProjectProfile) -> bool:
    if profile.render_api != "auto" and not _api_supports(gpu, profile.render_api):
        return False
    if profile.upscaling_method == "dlss" and _gpu_feature_support(gpu, "DLSS") is not True:
        return False
    return True


#: Платформы количественного прогноза. Остальные сохраняют инженерные
#: объяснения, но совместимый аппаратный прогноз для них не обещается (D06).
_PC_PLATFORMS = frozenset({"pc_windows", "pc_linux"})


def _platform_status(profile: ProjectProfile) -> tuple[bool, list[str]]:
    """Наличие PC-цели и список не-PC платформ профиля."""
    platforms = list(profile.platforms or [])
    non_pc = sorted(p for p in platforms if p not in _PC_PLATFORMS)
    return (any(p in _PC_PLATFORMS for p in platforms), non_pc)


def _platform_scope_note(non_pc: list[str]) -> str:
    targets = ", ".join(non_pc)
    return (
        f"Количественный прогноз доступен только для Windows/Linux ПК: "
        f"для платформ ({targets}) совместимый аппаратный прогноз не обещается."
    )


#: Единая память без универсальной скидки: количественных данных для неё
#: недостаточно, поэтому ограничение фиксируется явно (G05).
_UNIFIED_MEMORY_GAP = (
    "Модель памяти «unified»: общий пул RAM/VRAM оценён приблизительно; "
    "универсальная скидка видеопамяти не применяется."
)


def _largest_impact(profile: ProjectProfile) -> float:
    return SCALE_FACTOR.get(profile.scale, SCALE_FACTOR["unknown"])


def _recommended_storage(profile: ProjectProfile, method_codes: set[str]) -> str:
    """Определить минимальный разумный класс накопителя для профиля."""
    streaming = _streaming_required(profile, method_codes)
    if streaming and profile.scale in {"large", "very_large"}:
        return "nvme"
    if streaming or profile.format != "2D":
        return "sata_ssd"
    return "hdd"


def _streaming_required(profile: ProjectProfile, method_codes: set[str]) -> bool:
    return (
        profile.world_type in {"open_world", "procedural", "sandbox"}
        or bool(method_codes & _STREAMING_METHODS)
        or "storage_streaming" in profile.functions
    )


def _estimated_draw_calls(profile: ProjectProfile, content: float, method_codes: set[str]) -> int:
    """Грубый draw-call ориентир для контроля явно заданного бюджета.

    Это не профилирование: значение нужно только для выявления противоречия
    между анкетой и пользовательским лимитом, а не для выдачи FPS.
    """
    base = 500 + 24_000 * content
    if "crowd_simulation" in profile.functions:
        base += 4_000 * profile.npc_count_effective
    if "split_screen_rendering" in profile.functions:
        base *= max(2, profile.player_count)
    if method_codes & {"hierarchical_lod", "baked_occlusion_culling", "gpu_compute_culling", "hiz_software_occlusion"}:
        base *= 0.65
    return max(100, round(base))


def _modeling_gaps(profile: ProjectProfile, method_codes: set[str], recommended_storage: str) -> list[str]:
    """Перечень неизвестных параметров, которые ограничивают точность оценки."""
    gaps: list[str] = [
        "Численные коэффициенты являются экспертными гипотезами, независимая калибровка не выполнена.",
        "Стоимость подсистем складывается как сумма работ; внутриподсстемные эффекты решений не измерялись.",
        "Степень распараллеливания задана коэффициентом, а не профилем конкретного движка.",
        "Постоянные расходы памяти ОС и движка не измерены для выбранного проекта; "
        "оценка может завышать требования лёгких игр.",
        "Объём буферов рендера и доля CPU-копий ресурсов заданы экспертно; "
        "резидентная и пиковая память отдельно не измерены.",
    ]
    streaming = _streaming_required(profile, method_codes)
    if profile.render_api == "auto":
        gaps.append("Не указан графический API/RHI: стоимость render thread и совместимость не определены.")
    if profile.memory_model == "auto":
        gaps.append("Не указана модель памяти RAM/VRAM: unified memory и GC не учтены явно.")
    if profile.memory_model == "unified":
        gaps.append(_UNIFIED_MEMORY_GAP)
    if profile.scale == "unknown":
        gaps.append("Не указан масштаб мира: нагрузка контента взята по нейтральному уровню.")
    if profile.object_count is None and profile.object_count_level == "unknown":
        gaps.append("Не указано количество объектов: вклад сцены взят по нейтральному уровню.")
    if profile.npc_count is None and profile.npc_count_level == "unknown":
        gaps.append("Не указано количество NPC: вклад симуляции взят по нейтральному уровню.")
    if streaming and profile.storage_type == "auto":
        gaps.append(f"Не указан накопитель: для этого профиля минимальный ориентир — {recommended_storage}.")
    if streaming and profile.streaming_pool_gb is None:
        gaps.append("Не задан streaming pool: пики подкачки и вытеснение ресурсов оценены приблизительно.")
    if profile.draw_call_budget is None and (
        "rendering_architecture" in profile.functions or "geometry_pipeline" in profile.functions
    ):
        gaps.append("Не задан draw-call budget: стоимость render thread проверяется только косвенно.")
    if profile.simulation_radius_m is None and (
        {"ai_pathfinding", "crowd_simulation"} & set(profile.functions)
    ):
        gaps.append("Не задан радиус симуляции: количество активных агентов за пределами кадра неизвестно.")
    if profile.physics_tick_hz is None and (
        {"physics_simulation", "multiplayer_netcode"} & set(profile.functions)
    ):
        gaps.append("Не задан physics/network tickrate: стоимость такта симуляции взята по умолчанию.")
    if level_unspecified(profile.audio_complexity) and "audio_system" in profile.functions:
        gaps.append(_UNKNOWN_AUDIO_NOTE)
    if profile.multiplayer and profile.network_topology == "auto":
        gaps.append("Не указана сетевая схема: P2P, client-server, dedicated и lockstep имеют разную цену.")
    if profile.target_resolution in {"1440p", "1600p", "2160p", "4k"} and profile.upscaling_method == "auto":
        gaps.append("Не указан upscaler: итоговая GPU-нагрузка для высокого разрешения может отличаться.")
    if "split_screen_rendering" in profile.functions and profile.local_view_count is None:
        gaps.append(
            "Число локальных вьюпортов split-screen не задано: нагрузка рассчитана "
            "из сценарного предположения о 2 вьюпортах."
        )
    if profile.frame_generation:
        gaps.append("Генерация кадров повышает отображаемый FPS, но не заменяет базовый FPS и добавляет задержку.")
        if profile.base_render_fps is None:
            gaps.append("Не задан целевой базовый FPS: расчёт выполнен без снижения требований за счёт генерации кадров.")
        else:
            gaps.append("Рассчитана нагрузка базового рендера; стоимость генератора и достижение отображаемого FPS не подтверждены.")
        gaps.append("Не указаны технология и версия генерации кадров: совместимость оборудования требует отдельной проверки.")
    return gaps


#: Диапазон целевого FPS, внутри которого зависимость стоимости кадра
#: откалибрована. Вне диапазона используется линейная экстраполяция.
_FPS_CALIBRATED_RANGE = (30, 144)

#: Число игроков, после которого сетевой вклад перестаёт различаться.
_PLAYER_SATURATION = 32


def _fmt(value: float) -> str:
    """Целое число с пробельным разделителем разрядов: «10 000»."""
    return f"{int(value):,}".replace(",", " ")


def _applicability_limits(profile: ProjectProfile) -> list[str]:
    """Выход входных данных за область, в которой модель различает значения."""
    limits: list[str] = []
    for field_name, value, label in (
        ("object_count", profile.object_count, "объектов"),
        ("npc_count", profile.npc_count, "NPC"),
    ):
        if value is None:
            continue
        _, top = count_scale_bounds(field_name)
        if value > top:
            limits.append(
                f"Число {label} ({_fmt(value)}) выше верхней границы модели "
                f"({_fmt(top)}): оценка не различает значения внутри этой области, "
                "результат является нижней границей диапазона."
            )

    low_fps, high_fps = _FPS_CALIBRATED_RANGE
    for value, label in ((profile.target_fps, "Целевой FPS"),
                         (profile.base_render_fps, "Базовый FPS")):
        if value is None:
            continue
        if value > high_fps:
            limits.append(
                f"{label} {_fmt(value)} выше откалиброванного диапазона "
                f"({low_fps}–{high_fps}): стоимость кадра экстраполирована."
            )
        elif value < low_fps:
            limits.append(
                f"{label} {_fmt(value)} ниже откалиброванного диапазона "
                f"({low_fps}–{high_fps}): стоимость кадра экстраполирована."
            )

    if profile.player_count > _PLAYER_SATURATION:
        limits.append(
            f"Число игроков ({_fmt(profile.player_count)}) выше порога различения "
            f"({_PLAYER_SATURATION}): сетевой вклад оценён по насыщению."
        )
    if profile.local_view_count is not None and profile.local_view_count > 4:
        limits.append(
            f"Число локальных вьюпортов ({profile.local_view_count}) выше области калибровки (≤4): "
            "стоимость масштабирована линейно, без эмпирической проверки."
        )

    _, non_pc = _platform_status(profile)
    if non_pc:
        limits.append(_platform_scope_note(non_pc))
    return limits


def _non_client_out(methods: list) -> list[NonClientMethodOut]:
    """Представление решений, чей эффект не относится к компьютеру игрока."""
    out: list[NonClientMethodOut] = []
    for method in methods:
        scope = rules.effect_scope_of(method)
        out.append(NonClientMethodOut(
            code=method.code, name=method.name,
            effect_scope=scope.value if scope else str(getattr(method, "effect_scope", "") or ""),
            effect_scope_label=scope.label if scope else "не распознана",
            reason=rules.non_client_reason(method),
        ))
    return out


# ---------------------------------------------------------------------------
# Единая расчётная модель
# ---------------------------------------------------------------------------
@dataclass
class FrameModel:
    """Результат расчёта стоимости кадра.

    Все стоимости — миллисекунды работы на один отрисованный кадр.
    """

    cpu: dict[str, float] = field(default_factory=dict)
    gpu: dict[str, float] = field(default_factory=dict)
    memory: dict[str, dict[str, float]] = field(default_factory=dict)
    # Производные величины
    cpu_sequential_ms: float = 0.0
    cpu_parallel_ms: float = 0.0
    gpu_raster_ms: float = 0.0
    gpu_rt_ms: float = 0.0
    budget_ms: float = 16.67
    render_fps: float = 60.0
    physics_tick_hz: float = DEFAULT_PHYSICS_TICK_HZ
    ai_tick_hz: float = DEFAULT_AI_TICK_HZ
    # Объяснения
    assumptions: list[str] = field(default_factory=list)
    exclusions: list[str] = field(default_factory=list)
    parameter_contributions: list[ContributionItem] = field(default_factory=list)
    method_contributions: list[ContributionItem] = field(default_factory=list)
    content: float = 1.0


def _base_cpu_costs(profile: ProjectProfile, content: float) -> dict[str, float]:
    """Базовая стоимость CPU-подсистем с учётом функций профиля."""
    costs = {key: value for key, value in CPU_BASE_COST.items()}
    for fn in profile.functions:
        for subsystem, weight in FEATURE_CPU_SUBSYSTEM_LOAD.get(fn, {}).items():
            costs[subsystem] = costs.get(subsystem, 0.0) + weight * CPU_FEATURE_MS

    # Масштаб сцены распределяется по подсистемам по-разному.
    costs["main_thread"] *= 0.6 + 0.4 * content
    costs["render_prep"] *= content
    for key in ("parallel_sim", "physics", "animation", "ai", "streaming"):
        costs[key] *= content
    costs["network"] *= content

    # Мультиплеер: сетевая репликация — отдельная подсистема, а не общий множитель.
    if profile.multiplayer:
        player_factor = 1.0 + 0.10 * min(1.0, profile.player_count / _PLAYER_SATURATION)
        costs["network"] += 3.0 * player_factor * content
        if profile.network_topology == "lockstep":
            costs["network"] *= 1.08
        elif profile.network_topology == "p2p":
            costs["network"] *= 1.04
    else:
        # Явное отключение мультиплеера убирает сетевой вклад полностью.
        costs["network"] = 0.0

    # Аудио.
    if not level_unspecified(profile.audio_complexity):
        costs["audio"] += _AUDIO_CPU_LOAD.get(profile.audio_complexity, 0.0)

    # Радиус симуляции влияет только на AI и параллельную симуляцию.
    if profile.simulation_radius_m is not None and (
        {"ai_pathfinding", "crowd_simulation", "advanced_npc_ai"} & set(profile.functions)
    ):
        factor = 1.0 + min(0.35, profile.simulation_radius_m / 30_000)
        costs["ai"] *= factor
        costs["parallel_sim"] *= 1.0 + (factor - 1.0) * 0.5

    # API и накопитель влияют на подготовку рендера и потоковую загрузку.
    _, api_cpu = _API_FACTORS.get(profile.render_api, _API_FACTORS["auto"])
    costs["render_prep"] *= api_cpu
    storage_cpu = _STORAGE_CPU_FACTOR.get(profile.storage_type, 1.0)
    costs["streaming"] *= storage_cpu
    return costs


def _base_gpu_costs(profile: ProjectProfile, content: float) -> dict[str, float]:
    """Базовая стоимость GPU-подсистем с учётом функций профиля."""
    costs = {key: value for key, value in GPU_BASE_COST.items()}
    for fn in profile.functions:
        for subsystem, weight in FEATURE_GPU_SUBSYSTEM_LOAD.get(fn, {}).items():
            costs[subsystem] = costs.get(subsystem, 0.0) + weight * GPU_FEATURE_MS

    res = _resolution_factor(profile.target_resolution)
    quality = QUALITY_FACTOR.get(profile.target_quality, 1.0)

    # Разрешение масштабирует только зависящие от заливки стадии.
    for key in GPU_PIXEL_SUBSYSTEMS:
        costs[key] *= res
    # Качество — стоимость материалов, света и прозрачности.
    for key in GPU_QUALITY_SUBSYSTEMS:
        costs[key] *= 0.75 + 0.25 * quality
    # Объём контента: геометрия и растеризация растут быстрее затенения.
    costs["geometry"] *= 0.5 + 0.5 * content
    costs["raster"] *= 0.5 + 0.5 * content
    costs["shading"] *= 0.7 + 0.3 * content
    costs["lighting_shadows"] *= 0.7 + 0.3 * content
    costs["transparency"] *= content
    costs["compute"] *= 0.7 + 0.3 * content

    api_gpu, _ = _API_FACTORS.get(profile.render_api, _API_FACTORS["auto"])
    for key in costs:
        costs[key] *= api_gpu
    return costs


def _apply_upscaling(
    costs: dict[str, float], profile: ProjectProfile, method_codes: set[str]
) -> tuple[str, list[str]]:
    """Применить апскейлинг только к зависящим от разрешения стадиям."""
    notes: list[str] = []
    upscaler = profile.upscaling_method
    if upscaler == "auto" and "temporal_upscaling" in method_codes:
        upscaler = "taa"
        notes.append("Апскейлинг не указан: принят временной апскейлинг из выбранного решения.")
    factor = _UPSCALER_PIXEL_FACTOR.get(upscaler, 1.0)
    if factor != 1.0:
        for key in GPU_PIXEL_SUBSYSTEMS:
            costs[key] *= factor
        notes.append(
            "Апскейлинг снижает стоимость стадий, зависящих от внутреннего разрешения; "
            "геометрия и подготовка рендера на CPU не удешевляются."
        )
    extra = _UPSCALER_POST_MS.get(upscaler, 0.0)
    if extra:
        costs["post_processing"] += extra
    return upscaler, notes


def _complement_pairs(relations) -> set[frozenset[str]]:
    """Пары решений с обоснованным совместным эффектом (`complement`)."""
    pairs: set[frozenset[str]] = set()
    for row in relations or ():
        if row.conflict_type == "complement":
            pairs.add(frozenset((row.a_code, row.b_code)))
    return pairs


def _apply_method_effects(
    cpu: dict[str, float],
    gpu: dict[str, float],
    memory: dict[str, dict[str, float]],
    methods: list,
    relations,
) -> tuple[list[ContributionItem], list[str]]:
    """Распределить эффекты решений по подсистемам с учётом перекрытия.

    Экономия в одной подсистеме не суммируется: без обоснованного совместного
    эффекта учитывается наибольшая экономия, остальные перечисляются как
    перекрытые. Дополнительные затраты сохраняются всегда.
    """
    contributions: list[ContributionItem] = []
    exclusions: list[str] = []
    complements = _complement_pairs(relations)

    savings: dict[str, list[tuple[str, float]]] = {}
    extra_cost: dict[str, list[tuple[str, float]]] = {}
    mem_delta: dict[str, list[tuple[str, float]]] = {}
    rt_add: list[tuple[str, float]] = []
    # Решения с эффектом, но без распределения: эффект не растворяется
    # молча, а перечисляется как причина неучёта.
    unmapped: list[str] = []

    for method in methods:
        effect = METHOD_SUBSYSTEM_EFFECTS.get(method.code)
        if effect is None:
            unmapped.append(method.name)
            continue
        if not effect:
            # Распределение задано пустым: эффект проявляется не в стоимости
            # кадра (например, только на сервере или в процессе разработки).
            continue
        for subsystem, value in (effect.get("cpu") or {}).items():
            if value >= 0:
                savings.setdefault(f"cpu:{subsystem}", []).append((method.code, value))
            else:
                extra_cost.setdefault(f"cpu:{subsystem}", []).append((method.code, -value))
        for subsystem, value in (effect.get("gpu") or {}).items():
            if value >= 0:
                savings.setdefault(f"gpu:{subsystem}", []).append((method.code, value))
            else:
                extra_cost.setdefault(f"gpu:{subsystem}", []).append((method.code, -value))
        for component, value in (effect.get("mem") or {}).items():
            mem_delta.setdefault(component, []).append((method.code, value))
        if effect.get("rt_ms"):
            rt_add.append((method.code, float(effect["rt_ms"])))

    names = {method.code: method.name for method in methods}

    def apply_savings(scope: str, costs: dict[str, float]) -> None:
        for key, entries in list(savings.items()):
            if not key.startswith(scope + ":"):
                continue
            subsystem = key.split(":", 1)[1]
            base = costs.get(subsystem, 0.0)
            if base <= 0:
                continue
            # Наибольшая экономия применяется всегда.
            best_code, best_value = max(entries, key=lambda item: item[1])
            total_saving = min(MAX_SUBSYSTEM_SAVING, best_value)
            superseded: list[str] = []
            for code, value in entries:
                if code == best_code:
                    continue
                if frozenset((best_code, code)) in complements:
                    # Обоснованное совместное действие: эффекты перемножаются
                    # как независимые доли оставшейся работы.
                    total_saving = min(
                        MAX_SUBSYSTEM_SAVING,
                        1.0 - (1.0 - total_saving) * (1.0 - min(MAX_SUBSYSTEM_SAVING, value)),
                    )
                else:
                    superseded.append(code)
            costs[subsystem] = base * (1.0 - total_saving)
            contributions.append(ContributionItem(
                label=f"{names.get(best_code, best_code)}: {_subsystem_label(scope, subsystem)}",
                delta=-round(total_saving, 3),
                detail=f"Снижает стоимость подсистемы на {round(total_saving * 100)}%.",
            ))
            for code in superseded:
                exclusions.append(
                    f"«{names.get(code, code)}»: экономия в подсистеме "
                    f"«{_subsystem_label(scope, subsystem)}» перекрыта решением "
                    f"«{names.get(best_code, best_code)}» — совместный эффект не обоснован, "
                    "повторно не учитывается."
                )

    apply_savings("cpu", cpu)
    apply_savings("gpu", gpu)

    for key, entries in extra_cost.items():
        scope, subsystem = key.split(":", 1)
        costs = cpu if scope == "cpu" else gpu
        base = costs.get(subsystem, 0.0)
        added = sum(value for _, value in entries)
        costs[subsystem] = base * (1.0 + added)
        for code, value in entries:
            contributions.append(ContributionItem(
                label=f"{names.get(code, code)}: {_subsystem_label(scope, subsystem)}",
                delta=round(value, 3),
                detail=f"Добавляет работу в подсистеме: +{round(value * 100)}% к её стоимости.",
            ))

    for code, value in rt_add:
        gpu["rt"] = gpu.get("rt", 0.0) + value
        contributions.append(ContributionItem(
            label=f"{names.get(code, code)}: трассировка лучей",
            delta=round(value, 3),
            detail="Вводит отдельный проход трассировки лучей.",
        ))

    for component, entries in mem_delta.items():
        sizes = memory.get(component)
        if not sizes:
            continue
        # Та же защита от двойного учёта: экономия одного и того же ресурса
        # несколькими решениями берётся один раз — по наибольшему эффекту.
        best_code, best_value = min(entries, key=lambda item: item[1])
        total = best_value
        superseded: list[str] = []
        for code, value in entries:
            if code == best_code:
                continue
            if frozenset((best_code, code)) in complements:
                total = (1.0 + total) * (1.0 + value) - 1.0
            elif value < 0:
                superseded.append(code)
        total = max(-0.7, min(3.0, total))
        sizes["ram"] *= 1.0 + total
        sizes["vram"] *= 1.0 + total
        contributions.append(ContributionItem(
            label=f"{names.get(best_code, best_code)}: {MEMORY_COMPONENT_LABELS.get(component, component)}",
            delta=round(total, 3),
            detail=(
                f"{'Увеличивает' if total >= 0 else 'Уменьшает'} компонент памяти "
                f"на {abs(round(total * 100))}%."
            ),
        ))
        for code in superseded:
            exclusions.append(
                f"«{names.get(code, code)}»: экономия компонента "
                f"«{MEMORY_COMPONENT_LABELS.get(component, component)}» перекрыта решением "
                f"«{names.get(best_code, best_code)}» и повторно не учитывается."
            )

    if unmapped:
        listed = ", ".join(f"«{name}»" for name in unmapped[:6])
        exclusions.append(
            f"Распределение эффекта по подсистемам не задано: {listed}. "
            "Численный вклад этих решений в стоимость кадра не учтён."
        )
    return contributions, exclusions


def _subsystem_label(scope: str, subsystem: str) -> str:
    if scope == "cpu":
        return CPU_SUBSYSTEM_LABELS.get(subsystem, subsystem)
    return GPU_SUBSYSTEM_LABELS.get(subsystem, subsystem)


def _memory_components(profile: ProjectProfile, content: float, method_codes: set[str]) -> dict[str, dict[str, float]]:
    """Состав памяти: RAM и VRAM складываются из поименованных компонентов."""
    res = _resolution_factor(profile.target_resolution)
    quality = QUALITY_FACTOR.get(profile.target_quality, 1.0)
    tex_quality = 1.0 + (quality - 1.0) * 0.8
    tex_res = 1.0 + (res - 1.0) * 0.35
    streaming = _streaming_required(profile, method_codes)
    audio_ram = 0.35 + (_AUDIO_CPU_LOAD.get(profile.audio_complexity, 0.0) if not level_unspecified(profile.audio_complexity) else 0.0)

    if profile.streaming_pool_gb is not None:
        streaming_ram = profile.streaming_pool_gb
        streaming_vram = profile.streaming_pool_gb * 0.5
    else:
        streaming_ram = 0.9 if streaming else 0.25
        streaming_vram = 0.5 if streaming else 0.15

    components = {
        "system": {"ram": 2.5, "vram": 0.0},
        "engine": {"ram": 2.0, "vram": 0.15},
        "scene": {"ram": 1.9 * content, "vram": 0.2 * content},
        "meshes": {"ram": 0.8 * content, "vram": 0.8 * content},
        "textures": {"ram": 0.55 * content * tex_quality, "vram": 2.2 * content * tex_quality * tex_res},
        "render_targets": {"ram": 0.15 * res, "vram": 1.8 * res},
        "audio": {"ram": audio_ram, "vram": 0.0},
        "streaming": {"ram": streaming_ram, "vram": streaming_vram},
    }
    # Split-screen дублирует целевые буферы рендера для каждого вьюпорта.
    if "split_screen_rendering" in profile.functions:
        views = profile.local_view_count or 2
        components["render_targets"]["vram"] *= max(1, views)
    components["mirror"] = {"ram": 0.0, "vram": 0.0}
    return _mirror_memory(components)


def _mirror_memory(components: dict[str, dict[str, float]]) -> dict[str, dict[str, float]]:
    """Пересчитать зеркало ресурсов в оперативной памяти.

    Доля CPU-копий — экспертное допущение о геометрии и текстурах, а не
    требование API. Буферы загрузки могут переиспользоваться после завершения
    копирования на GPU. RAM и VRAM не обязаны совпадать по объёму.
    После применения эффектов решений копии пересчитываются по тому же
    допущению, чтобы не сохранять зеркало уже исключённых ресурсов.
    """
    components.setdefault("mirror", {"ram": 0.0, "vram": 0.0})
    components["mirror"]["ram"] = VRAM_MIRROR_SHARE * (
        components.get("meshes", {}).get("vram", 0.0)
        + components.get("textures", {}).get("vram", 0.0)
    )
    components["mirror"]["vram"] = 0.0
    return components


def _render_fps(profile: ProjectProfile) -> tuple[float, float]:
    """Частота реально отрисованных кадров и отображаемая частота."""
    if profile.frame_generation and profile.base_render_fps is not None:
        return float(profile.base_render_fps), float(profile.target_fps)
    return float(profile.target_fps), float(profile.target_fps)


def build_model(profile: ProjectProfile, methods: list, relations=()) -> FrameModel:
    """Построить единую модель стоимости кадра.

    Одна и та же модель используется для сводной нагрузки, подбора
    оборудования и объяснений: расхождение между экранами невозможно, потому
    что все они читают один результат.
    """
    client_methods, outside_client = rules.split_by_effect_scope(methods)
    method_codes = {m.code for m in client_methods}
    content = (
        _largest_impact(profile)
        * (0.85 + 0.35 * profile.object_count_effective)
        * (0.85 + 0.35 * profile.npc_count_effective)
    )

    render_fps, display_fps = _render_fps(profile)
    budget_ms = 1000.0 / max(1.0, render_fps)

    cpu = _base_cpu_costs(profile, content)
    gpu = _base_gpu_costs(profile, content)
    memory = _memory_components(profile, content, method_codes)

    assumptions: list[str] = []
    exclusions: list[str] = [f"«{m.name}»: {rules.non_client_reason(m)}." for m in outside_client]

    # --- Работа по такту симуляции отделена от работы на кадр ---
    physics_tick = profile.physics_tick_hz or DEFAULT_PHYSICS_TICK_HZ
    if profile.physics_tick_hz is None and "physics_simulation" in profile.functions:
        assumptions.append(
            f"Частота такта физики не задана: принято {DEFAULT_PHYSICS_TICK_HZ:g} Гц. "
            "Изменение целевого FPS не пересчитывает стоимость такта."
        )
    ai_tick = DEFAULT_AI_TICK_HZ
    if "ai_pathfinding" in profile.functions or "crowd_simulation" in profile.functions:
        assumptions.append(
            f"Частота такта AI не задаётся анкетой: принято {DEFAULT_AI_TICK_HZ:g} Гц "
            "(экспертное допущение)."
        )
    for subsystem, tick_hz in (("physics", physics_tick), ("ai", ai_tick)):
        if cpu.get(subsystem, 0.0) > 0:
            cpu[subsystem] = cpu[subsystem] * (tick_hz / render_fps)
    if profile.multiplayer and cpu.get("network", 0.0) > 0:
        cpu["network"] = cpu["network"] * (DEFAULT_NETWORK_TICK_HZ / render_fps)

    # --- Апскейлинг: только стадии, зависящие от внутреннего разрешения ---
    _, upscale_notes = _apply_upscaling(gpu, profile, method_codes)
    assumptions.extend(upscale_notes)

    # --- Генерация кадров: отдельная стоимость, без скидки на рендер ---
    if profile.frame_generation:
        # Синтез промежуточных кадров — отдельная работа GPU. Она не удешевляет
        # отрисованные кадры и не даёт скидки на остальные ресурсы: стоимость
        # генерации распределяется по отрисованным кадрам.
        generated = max(0.0, display_fps - render_fps)
        extra_ms = FRAME_GENERATION_MS * generated / max(1.0, render_fps)
        gpu["frame_generation"] = gpu.get("frame_generation", 0.0) + extra_ms
        assumptions.append(
            "Генерация кадров добавлена как отдельная стоимость синтеза "
            f"{generated:g} промежуточных кадров в секунду; она не снижает стоимость "
            "отрисованных кадров."
        )

    # --- Эффекты решений с учётом перекрытия ---
    method_contributions, effect_exclusions = _apply_method_effects(
        cpu, gpu, memory, client_methods, relations
    )
    exclusions.extend(effect_exclusions)
    # Зеркало считается по итоговым размерам геометрии и текстур: иначе
    # экономия решений не доходила бы до оперативной памяти.
    _mirror_memory(memory)

    for key in list(cpu):
        cpu[key] = max(0.0, cpu[key])
    for key in list(gpu):
        gpu[key] = max(0.0, gpu[key])

    cpu_sequential = sum(cpu.get(key, 0.0) for key in CPU_SEQUENTIAL_SUBSYSTEMS)
    cpu_parallel = sum(value for key, value in cpu.items() if key not in CPU_SEQUENTIAL_SUBSYSTEMS)
    gpu_rt = gpu.get("rt", 0.0)
    gpu_raster = sum(value for key, value in gpu.items() if key != "rt")

    parameter_contributions = _parameter_contributions(profile, content, render_fps, budget_ms)

    return FrameModel(
        cpu=cpu, gpu=gpu, memory=memory,
        cpu_sequential_ms=cpu_sequential,
        cpu_parallel_ms=cpu_parallel,
        gpu_raster_ms=gpu_raster,
        gpu_rt_ms=gpu_rt,
        budget_ms=budget_ms,
        render_fps=render_fps,
        physics_tick_hz=physics_tick,
        ai_tick_hz=ai_tick,
        assumptions=assumptions,
        exclusions=exclusions,
        parameter_contributions=parameter_contributions,
        method_contributions=method_contributions,
        content=content,
    )


def _parameter_contributions(
    profile: ProjectProfile, content: float, render_fps: float, budget_ms: float
) -> list[ContributionItem]:
    """Вклад параметров анкеты: во сколько раз параметр меняет стоимость кадра."""
    items: list[ContributionItem] = []
    res = _resolution_factor(profile.target_resolution)
    quality = QUALITY_FACTOR.get(profile.target_quality, 1.0)
    items.append(ContributionItem(
        label=f"Разрешение {profile.target_resolution}",
        delta=round(res - 1.0, 3),
        detail="Множитель стоимости стадий рендера, зависящих от заливки.",
    ))
    items.append(ContributionItem(
        label=f"Качество «{profile.target_quality}»",
        delta=round((0.75 + 0.25 * quality) - 1.0, 3),
        detail="Множитель стоимости затенения, света, прозрачности и постобработки.",
    ))
    items.append(ContributionItem(
        label=f"Отрисованных кадров в секунду: {render_fps:g}",
        delta=round(budget_ms, 3),
        detail="Бюджет кадра в миллисекундах: 1000 / частота отрисованных кадров.",
    ))
    items.append(ContributionItem(
        label=f"Масштаб «{profile.scale}», объекты и NPC",
        delta=round(content - 1.0, 3),
        detail="Сводный множитель объёма контента относительно нейтрального уровня.",
    ))
    if profile.multiplayer:
        items.append(ContributionItem(
            label=f"Мультиплеер, игроков: {profile.player_count}",
            delta=round(0.10 * min(1.0, profile.player_count / _PLAYER_SATURATION), 3),
            detail="Добавка к стоимости сетевой репликации.",
        ))
    else:
        items.append(ContributionItem(
            label="Мультиплеер отключён",
            delta=0.0,
            detail="Сетевой вклад полностью исключён из расчёта.",
        ))
    if "physics_simulation" in profile.functions:
        items.append(ContributionItem(
            label=f"Такт физики: {profile.physics_tick_hz or DEFAULT_PHYSICS_TICK_HZ:g} Гц",
            delta=round((profile.physics_tick_hz or DEFAULT_PHYSICS_TICK_HZ) / render_fps, 3),
            detail="Стоимость такта физики распределяется по отрисованным кадрам.",
        ))
    return items


def _load_indices(profile: ProjectProfile, methods: list, relations=()) -> dict:
    """Индексы нагрузки и памяти по единой модели стоимости кадра.

    Тонкий адаптер над `build_model`: индексы нужны там, где полная оценка
    оборудования не требуется (сравнение вариантов профиля, проверка области
    применимости). Формулы не дублируются — они читаются из модели.
    """
    model = build_model(profile, methods, relations)
    budget = model.budget_ms
    st_index = model.cpu_sequential_ms / budget
    mt_index = model.cpu_parallel_ms / budget / PARALLEL_SPEEDUP
    raster_index = model.gpu_raster_ms / budget
    rt_index = model.gpu_rt_ms / budget
    ram_gb, vram_gb, _ = _memory_totals(model)
    client_methods = rules.split_by_effect_scope(methods)[0]
    method_codes = {m.code for m in client_methods}
    recommended_storage = _recommended_storage(profile, method_codes)
    return {
        "gpu_index": max(raster_index, rt_index),
        "cpu_index": max(st_index, mt_index),
        "cpu_st_index": st_index,
        "cpu_mt_index": mt_index,
        "gpu_raster_index": raster_index,
        "gpu_rt_index": rt_index,
        "vram_gb": vram_gb,
        "ram_gb": ram_gb,
        "required_rt": any(
            "Hardware Ray Tracing" in (m.requires_hw_features or []) for m in client_methods
        ) or model.gpu_rt_ms > 0,
        "required_hw": sorted({
            feature for m in client_methods for feature in (m.requires_hw_features or [])
        }),
        "recommended_storage": recommended_storage,
        "estimated_draw_calls": _estimated_draw_calls(profile, model.content, method_codes),
        "modeling_gaps": _modeling_gaps(profile, method_codes, recommended_storage),
        "applicability_limits": _applicability_limits(profile),
        "non_client_methods": _non_client_out(rules.split_by_effect_scope(methods)[1]),
        "cpu_subsystem_load": dict(model.cpu),
        "gpu_subsystem_load": dict(model.gpu),
        "cpu_subsystem_total": model.cpu_sequential_ms + model.cpu_parallel_ms,
        "gpu_subsystem_total": model.gpu_raster_ms + model.gpu_rt_ms,
    }


def _subsystem_shares(costs: dict[str, float], labels: dict[str, str], total: float) -> list[SubsystemBreakdown]:
    """Доли подсистем в своей группе (сумма долей равна 1)."""
    if total <= 0:
        return []
    return [
        SubsystemBreakdown(label=labels.get(key, key), share=round(value / total, 4))
        for key, value in sorted(costs.items(), key=lambda item: item[1], reverse=True)
        if value > 0
    ]


# ---------------------------------------------------------------------------
# Подбор оборудования
# ---------------------------------------------------------------------------
def _pick_gpu(
    pool: list[HardwareGPU], *, raster_index: float, rt_index: float,
    required_rt: bool, vram_gb: float,
) -> tuple[HardwareGPU | None, bool]:
    """Выбрать видеокарту, одновременно покрывающую растровую и RT-составляющие."""
    if required_rt:
        pool = [g for g in pool if _supports_ray_tracing(g)]
        if not pool:
            return None, True
    pool = [g for g in pool if g.vram_gb >= vram_gb]
    candidates = [
        g for g in pool
        if g.raster_score >= raster_index and (rt_index <= 0 or g.rt_score >= rt_index)
    ]
    if not candidates:
        return None, False
    # Десктопные карты предпочтительнее мобильных и встроек.
    desktop = [g for g in candidates if not _is_mobile_gpu(g.model)]
    chosen = desktop or candidates
    return min(chosen, key=lambda g: (g.perf_class, g.raster_score)), False


def _pick_cpu(pool: list[HardwareCPU], *, st_index: float, mt_index: float) -> HardwareCPU | None:
    """Выбрать процессор, одновременно покрывающий однопоточный и многопоточный индексы."""
    candidates = [
        c for c in pool
        if c.single_thread_score >= st_index and c.multi_thread_score >= mt_index
    ]
    if not candidates:
        return None
    desktop = [c for c in candidates if not _is_mobile_cpu(c.model)]
    chosen = desktop or candidates
    return min(chosen, key=lambda c: (c.perf_class, c.multi_thread_score))


# Маркеры мобильных и встроенных решений в названиях моделей каталога.
_MOBILE_GPU_MARKERS = (
    "laptop", "mobile", "uhd", "hd graphics", "iris",
    "vega 3", "vega 8", "vega 11", "vega graphics",
    "radeon 780m", "radeon graphics",
)
_MOBILE_CPU_RE = r"h$|van gogh"


def _is_mobile_gpu(model: str) -> bool:
    name = (model or "").lower()
    return any(marker in name for marker in _MOBILE_GPU_MARKERS)


def _is_mobile_cpu(model: str) -> bool:
    return bool(re.search(_MOBILE_CPU_RE, (model or "").lower()))


def _memory_totals(model: FrameModel) -> tuple[float, float, list[MemoryComposition]]:
    ram = sum(float(size.get("ram", 0.0)) for size in model.memory.values())
    vram = sum(float(size.get("vram", 0.0)) for size in model.memory.values())
    composition = [
        MemoryComposition(
            label=MEMORY_COMPONENT_LABELS[key],
            ram_gb=round(float(model.memory[key]["ram"]), 2),
            vram_gb=round(float(model.memory[key]["vram"]), 2),
        )
        for key in _MEMORY_ORDER
        if key in model.memory
    ]
    # Единственный путь суммирования для профиля нагрузки и подбора железа.
    # ОС и движок уже включены в компоненты; дополнительного резерва поверх
    # VRAM здесь нет. Округление не превращает оценку в аппаратный номинал.
    return round(ram, 1), round(vram, 1), composition


def _consequences(profile: ProjectProfile, methods: list, model: FrameModel) -> list[str]:
    """Последствия выбора для качества, сети и внедрения."""
    items: list[str] = []
    for method in methods:
        if method.quality_impact < 0:
            items.append(
                f"«{method.name}»: ожидаемое снижение качества изображения или анимации "
                f"({method.quality_impact})."
            )
        if method.concept_impact < 0:
            items.append(
                f"«{method.name}»: может потребовать изменения концепции "
                f"({method.concept_impact})."
            )
    net_impact = sum(m.impact_network for m in methods)
    if profile.multiplayer and net_impact:
        direction = "снижает" if net_impact < 0 else "повышает"
        items.append(
            f"Выбранные решения {direction} сетевой трафик (суммарная оценка {net_impact})."
        )
    if profile.multiplayer and not any(
        (m.function.code if m.function is not None else "") == "multiplayer_netcode"
        for m in methods
    ):
        items.append(
            "Мультиплеер включён, но решения сетевого кода не выбраны: сетевой вклад "
            "учтён по базовому профилю."
        )
    if profile.frame_generation:
        items.append(
            "Генерация кадров повышает отображаемую плавность, но добавляет задержку ввода "
            "и не заменяет базовый FPS."
        )
    if model.gpu_rt_ms > 0:
        items.append(
            "В расчёте есть трассировка лучей: требуется видеокарта с аппаратной поддержкой RT, "
            "производительность проверяется по отдельной RT-шкале."
        )
    late = sorted(
        (m for m in methods if m.late_cost in {"high", "blocking"}),
        key=lambda m: m.name,
    )
    if late:
        names = ", ".join(f"«{m.name}»" for m in late[:4])
        items.append(f"Позднее внедрение затруднено: {names}.")
    return items


def _storage_requirement(profile: ProjectProfile, database_gb: float, recommended: str) -> str:
    label = _STORAGE_RANK_LABELS.get(recommended, recommended)
    text = f"Накопитель не ниже {label}; ориентировочный объём установки — {database_gb:.0f} ГБ."
    if profile.size_limit_gb is not None and database_gb > profile.size_limit_gb:
        text += (
            f" Заданный предел размера ({profile.size_limit_gb:g} ГБ) ниже оценочного: "
            "требуется пересмотр бюджета контента."
        )
    return text


def _estimate_install_size(profile: ProjectProfile, model: FrameModel) -> float:
    """Ориентировочный объём установки: сумма компонентов ресурсов."""
    textures = model.memory.get("textures", {}).get("vram", 0.0)
    meshes = model.memory.get("meshes", {}).get("vram", 0.0)
    audio = model.memory.get("audio", {}).get("ram", 0.0)
    scale = _largest_impact(profile)
    base = 12.0 * scale
    return max(2.0, base + (textures + meshes) * 2.5 + audio * 6.0)


def _memory_pressure(
    *,
    vram_gb: float, ram_gb: float, budget_ms: float,
    vram_norm_gb: float, ram_norm_gb: float, streaming: bool,
) -> tuple[float, str]:
    """Давление памяти в долях бюджета кадра.

    Рабочий набор измеряется в гигабайтах, а остальные стадии — в долях
    бюджета кадра. Раньше сравнивались гигабайты, делённые на норматив, и доли
    бюджета: величина порядка единицы всегда побеждала величину порядка 0.1,
    поэтому узким местом почти всегда объявлялась память и переставала быть
    диагностикой.

    Память ограничивает кадр не сама по себе, а дефицитом: пока рабочий набор
    укладывается в доступный объём, простоя нет. Дефицит переводится в простой
    подкачки — и он уже сравнивается с бюджетом в одной шкале с остальными
    стадиями.
    """
    load_vram = vram_gb / max(1.0, vram_norm_gb)
    load_ram = ram_gb / max(1.0, ram_norm_gb)
    over = max(0.0, max(load_vram, load_ram) - MEMORY_PRESSURE_FREE_SHARE)
    if over <= 0.0:
        return 0.0, ""
    # При потоковой подгрузке дефицит памяти оборачивается не только
    # вытеснением, но и ожиданием чтения: простой заметнее.
    stall_ms = MEMORY_DEFICIT_STALL_MS * over * (1.2 if streaming else 1.0)
    note = (
        f"Рабочий набор ({max(load_vram, load_ram) * 100:.0f}% доступного объёма) превышает "
        "запас памяти: оценка включает простой подкачки. Дефицит устраняется "
        "уменьшением бюджета ресурсов, а не более производительным процессором "
        "или видеокартой."
    )
    return stall_ms / max(1.0, budget_ms), note


def _bottleneck(model: FrameModel, *, st_index: float, mt_index: float,
                raster_index: float, rt_index: float, memory_pressure: float) -> tuple[str, str]:
    """Самая медленная стадия обработки кадра.

    Все величины — доли бюджета кадра, поэтому шкалы сопоставимы.
    """
    options = {
        "cpu_main_thread": st_index,
        "cpu_parallel": mt_index,
        "gpu_raster": raster_index,
        "gpu_rt": rt_index,
        "memory": memory_pressure,
    }
    key = max(options, key=lambda item: options[item])
    return key, BOTTLENECK_TITLES[key]


def estimate_hardware(db: Session, profile: ProjectProfile, methods: list) -> HardwareEstimateOut:
    """Рассчитать ориентировочную минимальную конфигурацию по единой модели."""
    relations = repositories.conflicts(db)
    methods, basket_notes = rules.assess_selected_methods(methods, profile, relations)
    model = build_model(profile, methods, relations)

    budget = model.budget_ms
    st_index = model.cpu_sequential_ms / budget
    mt_index = model.cpu_parallel_ms / budget / PARALLEL_SPEEDUP
    raster_index = model.gpu_raster_ms / budget
    rt_index = model.gpu_rt_ms / budget

    ram_gb, vram_gb, composition = _memory_totals(model)

    method_codes = {m.code for m in methods}
    memory_pressure, memory_note = _memory_pressure(
        vram_gb=vram_gb, ram_gb=ram_gb, budget_ms=budget,
        vram_norm_gb=max(1.0, profile.vram_limit_gb or MEMORY_NORM_VRAM_GB),
        ram_norm_gb=max(1.0, profile.ram_limit_gb or MEMORY_NORM_RAM_GB),
        streaming=_streaming_required(profile, method_codes),
    )
    recommended_storage = _recommended_storage(profile, method_codes)
    estimated_draw_calls = _estimated_draw_calls(profile, model.content, method_codes)
    modeling_gaps = _modeling_gaps(profile, method_codes, recommended_storage)
    applicability_limits = _applicability_limits(profile)

    client_methods = rules.split_by_effect_scope(methods)[0]
    required_hw = sorted({
        feature for m in client_methods for feature in (m.requires_hw_features or [])
    })
    if profile.upscaling_method == "dlss":
        required_hw = sorted(set(required_hw) | {"DLSS"})
    required_rt = any(
        "Hardware Ray Tracing" in (m.requires_hw_features or []) for m in client_methods
    ) or model.gpu_rt_ms > 0

    picked = _pick_references(
        db, profile, model,
        st_index=st_index, mt_index=mt_index,
        raster_index=raster_index, rt_index=rt_index,
        vram_gb=vram_gb, ram_gb=ram_gb,
        required_rt=required_rt, required_hw=required_hw,
        recommended_storage=recommended_storage,
        estimated_draw_calls=estimated_draw_calls,
    )

    bottleneck, bottleneck_label = _bottleneck(
        model, st_index=st_index, mt_index=mt_index,
        raster_index=raster_index, rt_index=rt_index, memory_pressure=memory_pressure,
    )

    confidence, label, confidence_caveats = _confidence(
        profile, methods,
        exceeds=picked["exceeds"], unmet=picked["unmet"],
        modeling_gaps=modeling_gaps + basket_notes,
    )
    caveats = picked["caveats"] + basket_notes + confidence_caveats
    if memory_note:
        caveats.append(memory_note)
    non_client_methods = _non_client_out(rules.split_by_effect_scope(methods)[1])
    if non_client_methods:
        names = ", ".join(f"«{item.name}»" for item in non_client_methods)
        caveats.append(
            f"В оценку не вошли решения {names}: их эффект не относится к компьютеру игрока."
        )
    reference_gpu = picked["reference_gpu"]
    reference_cpu = picked["reference_cpu"]
    install_gb = _estimate_install_size(profile, model)

    return HardwareEstimateOut(
        required_gpu_index=round(max(raster_index, rt_index), 4),
        required_cpu_index=round(max(st_index, mt_index), 4),
        estimated_vram_gb=float(vram_gb),
        estimated_ram_gb=float(ram_gb),
        gpu_class=reference_gpu.perf_class if reference_gpu else 5,
        cpu_class=reference_cpu.perf_class if reference_cpu else 5,
        reference_gpu=serializers.gpu_out(reference_gpu) if reference_gpu else None,
        reference_cpu=serializers.cpu_out(reference_cpu) if reference_cpu else None,
        alternative_gpus=[serializers.gpu_out(g) for g in picked["alt_gpus"]],
        alternative_cpus=[serializers.cpu_out(c) for c in picked["alt_cpus"]],
        confidence=confidence,
        confidence_label=label,
        caveats=caveats,
        required_hw_features=required_hw,
        exceeds_catalog=picked["exceeds"],
        recommended_storage=recommended_storage,
        estimated_draw_calls=estimated_draw_calls,
        modeling_gaps=modeling_gaps,
        unmet_limits=picked["unmet"],
        applicability_limits=applicability_limits,
        non_client_methods=non_client_methods,
        cpu_main_thread_cost=round(model.cpu_sequential_ms, 3),
        cpu_parallel_cost=round(model.cpu_parallel_ms, 3),
        cpu_subsystems=_subsystem_shares(model.cpu, CPU_SUBSYSTEM_LABELS, model.cpu_sequential_ms + model.cpu_parallel_ms),
        gpu_raster_cost=round(model.gpu_raster_ms, 3),
        gpu_rt_cost=round(model.gpu_rt_ms, 3),
        gpu_subsystems=_subsystem_shares(
            {**model.gpu, "rt": model.gpu.get("rt", 0.0)}, GPU_SUBSYSTEM_LABELS,
            model.gpu_raster_ms + model.gpu_rt_ms,
        ),
        bottleneck=bottleneck,
        bottleneck_label=bottleneck_label,
        memory_composition=composition,
        consequences=_consequences(profile, methods, model),
        storage_requirement=_storage_requirement(profile, install_gb, recommended_storage),
    )


def _pick_references(
    db: Session, profile: ProjectProfile, model: FrameModel, *,
    st_index: float, mt_index: float, raster_index: float, rt_index: float,
    vram_gb: float, ram_gb: float, required_rt: bool, required_hw: list[str],
    recommended_storage: str, estimated_draw_calls: int,
) -> dict:
    """Референсные CPU/GPU по опубликованному каталогу и обязательным требованиям."""
    gpus = sorted(repositories.hardware_gpu(db), key=lambda g: g.raster_score)
    cpus = sorted(repositories.hardware_cpu(db), key=lambda c: c.multi_thread_score)

    unmet: list[str] = []
    caveats: list[str] = []
    if any(g.vram_gb <= 0 for g in gpus):
        caveats.append(
            "GPU без известного объёма доступной памяти не могут пройти проверку вместимости. "
            "Для встроенной графики нужен бюджет общей памяти конкретной системы; "
            "найденная дискретная карта не доказывает, что встроенной графики недостаточно."
        )
    if profile.vram_limit_gb is not None and vram_gb > profile.vram_limit_gb:
        unmet.append(
            f"Требуется {vram_gb:.1f} ГБ видеопамяти при заданном пределе "
            f"{profile.vram_limit_gb:.1f} ГБ."
        )
    if profile.ram_limit_gb is not None and ram_gb > profile.ram_limit_gb:
        unmet.append(
            f"Требуется {ram_gb:.1f} ГБ оперативной памяти при заданном пределе "
            f"{profile.ram_limit_gb:.1f} ГБ."
        )
    if (
        profile.storage_type != "auto"
        and _STORAGE_RANK.get(profile.storage_type, 0) < _STORAGE_RANK[recommended_storage]
    ):
        caveats.append(
            f"Накопитель {profile.storage_type} ниже рекомендуемого класса "
            f"{recommended_storage}: возможны задержки подкачки. Без бюджета потоковых данных "
            "недостаточность накопителя не установлена."
        )
    if profile.draw_call_budget is not None and estimated_draw_calls > profile.draw_call_budget:
        caveats.append(
            f"Оценочно требуется около {estimated_draw_calls:,} draw calls при бюджете "
            f"{profile.draw_call_budget:,}. Это риск превышения бюджета, а не измеренное число вызовов.".replace(",", " ")
        )

    compatible_gpus = [g for g in gpus if _supports_profile_gpu(g, profile)]
    missing_features = [
        g for g in compatible_gpus
        if not all(_gpu_feature_support(g, feature) is True for feature in required_hw)
    ]
    compatible_gpus = [g for g in compatible_gpus if g not in missing_features]
    if not compatible_gpus and gpus:
        unmet.append("В каталоге нет GPU с подтверждённой поддержкой выбранного API и апскейлера.")

    reference_gpu, rt_missing = _pick_gpu(
        compatible_gpus, raster_index=raster_index, rt_index=rt_index,
        required_rt=required_rt, vram_gb=vram_gb,
    )
    exceeds = False
    if reference_gpu is None:
        exceeds = True
        if rt_missing:
            caveats.append(
                "Выбранные решения требуют аппаратной трассировки лучей, но в базе нет ни одной "
                "подходящей видеокарты: оценка выполнена по производительности без учёта этого "
                "требования и не является применимой."
            )
        elif not gpus:
            caveats.append("В базе нет опубликованных записей о видеокартах: оценка не выполнена.")
        elif required_rt and not any(_supports_ray_tracing(g) for g in compatible_gpus):
            caveats.append(
                "В каталоге нет видеокарты с подтверждённой аппаратной трассировкой лучей: "
                "подходящий ориентир не найден."
            )
        elif not any(g.vram_gb >= vram_gb for g in compatible_gpus):
            caveats.append(
                f"В каталоге нет видеокарты с {vram_gb:.1f} ГБ видеопамяти и выше: "
                "подходящий ориентир не найден."
            )
        else:
            caveats.append(
                "В каталоге нет GPU, одновременно покрывающего расчётную растровую "
                "производительность, RT-составляющую, видеопамять и обязательные возможности. "
                "Подходящий ориентир не найден."
            )
        reference_gpu = None
    if reference_gpu is not None and reference_gpu.vram_gb < vram_gb:
        unmet.append(
            f"Видеокарта {reference_gpu.model} имеет {reference_gpu.vram_gb:g} ГБ видеопамяти "
            f"при требуемых {vram_gb:.1f} ГБ: в базе нет карты, одновременно достаточно "
            "производительной и вместительной."
        )

    reference_cpu = _pick_cpu(cpus, st_index=st_index, mt_index=mt_index)
    if reference_cpu is None:
        exceeds = True
        if cpus:
            caveats.append(
                "Требуемая производительность CPU (однопоточная, многопоточная или обе) "
                "превышает самую производительную запись базы."
            )
        else:
            caveats.append("В базе нет опубликованных записей о процессорах: оценка не выполнена.")

    has_pc, non_pc = _platform_status(profile)
    if non_pc and not has_pc:
        scope_note = _platform_scope_note(non_pc)
        unmet.append(scope_note)
        caveats.append(
            scope_note + " Инженерные объяснения и индексы нагрузки приведены, "
            "но совместимая конфигурация не подбирается."
        )
        return {
            "gpus": gpus, "cpus": cpus, "reference_gpu": None,
            "reference_cpu": None, "alt_gpus": [], "alt_cpus": [],
            "exceeds": True, "unmet": unmet, "caveats": caveats,
        }
    if non_pc:
        caveats.append(
            _platform_scope_note(non_pc) + " Приведённый ориентир относится только к PC-цели."
        )

    return {
        "gpus": gpus, "cpus": cpus, "reference_gpu": reference_gpu,
        "reference_cpu": reference_cpu,
        "alt_gpus": _alternatives([
            g for g in compatible_gpus
            if g.raster_score >= raster_index and g.vram_gb >= vram_gb
            and (rt_index <= 0 or g.rt_score >= rt_index)
            and (not required_rt or _supports_ray_tracing(g))
        ], reference_gpu),
        "alt_cpus": _alternatives([
            c for c in cpus
            if c.single_thread_score >= st_index and c.multi_thread_score >= mt_index
        ], reference_cpu),
        "exceeds": exceeds, "unmet": unmet, "caveats": caveats,
    }


def _alternatives(rows, reference):
    """Альтернативы: тот же класс, но более современные записи."""
    if reference is None:
        return []
    same_class = [r for r in rows if r.perf_class == reference.perf_class and r.model != reference.model]
    return sorted(same_class, key=lambda r: r.release_year, reverse=True)[:4]


def _confidence(
    profile: ProjectProfile,
    methods: list,
    *,
    exceeds: bool,
    unmet: list[str],
    modeling_gaps: list[str],
) -> tuple[float, str, list[str]]:
    """Уверенность оценки и поясняющие оговорки."""
    caveats: list[str] = []
    confidence = 0.85
    if profile.object_count is None:
        confidence -= 0.06
        if profile.object_count_level == "unknown":
            caveats.append("Количество объектов не указано: вклад сцены взят по нейтральному уровню.")
        else:
            caveats.append("Количество объектов задано качественным уровнем, а не числом: оценка приблизительная.")
    if profile.npc_count is None:
        confidence -= 0.06
        if profile.npc_count_level == "unknown":
            caveats.append("Количество NPC не указано: вклад симуляции взят по нейтральному уровню.")
        else:
            caveats.append("Количество NPC задано качественным уровнем, а не числом: оценка приблизительная.")
    if exceeds:
        confidence -= 0.15
    _, non_pc_platforms = _platform_status(profile)
    if non_pc_platforms:
        confidence -= 0.15
        caveats.append(
            _platform_scope_note(non_pc_platforms) + " Оценка относится только к Windows/Linux ПК."
        )
    if not methods:
        confidence -= 0.1
        caveats.append("Корзина решений пуста: оценка выполнена по базовому профилю проекта.")
    confidence -= min(0.18, 0.02 * len(modeling_gaps))
    if unmet:
        confidence -= 0.12 * len(unmet)
        caveats.extend(unmet)
        caveats.append(
            "Заданные ограничения не выполнены: необходимо пересмотреть бюджет памяти, "
            "целевые показатели качества или набор решений."
        )
    confidence = round(max(0.15, min(0.95, confidence)), 2)

    if confidence >= 0.75:
        label = "повышенная"
    elif confidence >= 0.55:
        label = "средняя"
    else:
        label = "низкая"

    caveats.append(
        "Результат является ориентировочным минимальным классом оборудования, а не гарантией "
        "достижения целевого FPS: требуется проверка на прототипе."
    )
    return confidence, label, caveats


def build_contributions(
    profile: ProjectProfile, methods: list, estimate: HardwareEstimateOut | None = None,
    *, relations=(),
) -> ContributionsOut:
    """Вклад параметров и решений, допущения и причины неучёта.

    Строится по той же модели, что и расчёт: объяснение не может разойтись с
    числом, потому что читает один и тот же разбор стоимости кадра.
    """
    checked, basket_notes = rules.assess_selected_methods(methods, profile, relations)
    model = build_model(profile, checked, relations)
    exclusions = list(model.exclusions) + list(basket_notes)
    for method in methods:
        if method.code not in {m.code for m in checked}:
            exclusions.append(
                f"«{method.name}»: эффект не учтён — решение исключено проверкой применимости."
            )
    if estimate is not None and estimate.non_client_methods:
        for item in estimate.non_client_methods:
            exclusions.append(f"«{item.name}»: {item.reason}.")
    return ContributionsOut(
        parameters=model.parameter_contributions,
        methods=model.method_contributions,
        assumptions=model.assumptions,
        exclusions=exclusions,
    )


def practice_check() -> PracticeCheckOut:
    """Блок «Сверка с практикой».

    Сверка с реальными играми не выполняется: паспорта игр не загружаются,
    показатели точности не вычисляются. Заявленная погрешность ±70% является
    целью модели, а не подтверждённым результатом.
    """
    return PracticeCheckOut(
        status="in_development",
        title="Сверка с практикой — в разработке",
        message=(
            "Сверка расчёта с реальными играми не выполняется: паспорта игр "
            "не загружаются, показатели точности не вычисляются. Заявленная "
            "погрешность ±70% является целью модели, а не подтверждённым результатом."
        ),
        details=[
            "База паспортов игр не используется и не загружается.",
            "Показатели точности не рассчитываются: независимой калибровки нет.",
            "Проверка модели предполагается на прототипе конкретного проекта.",
        ],
    )
