"""Оценка ориентировочного минимального класса оборудования.

Результат намеренно формулируется как ориентировочный класс, а не как гарантия
конкретного значения FPS: система не располагает данными профилирования
конкретного проекта и не должна создавать ложную точность.

Подсистемная модель нагрузки (D03):
- CPU: main_thread, parallel_sim, render_prep, physics, animation, ai, audio, network, streaming
- GPU: geometry, shading, lighting_shadows, transparency, post_processing, compute, raster, rt
- Memory: resident_set, load_peaks, cpu_resources, gpu_resources, buffers, streaming, decompression

Каждый метод влияет только на свои подсистемы. Экономия в одной подсистеме
не компенсирует нагрузку в другой. Нет двойного учёта одной и той же работы.

Раздельные сценарные шкалы (G02): последовательная работа CPU ограничена
одним потоком (шкала single_thread_score), параллельная — ядрами
(multi_thread_score); растровая работа GPU и трассировка лучей — разные
сценарии (raster_score и rt_score). Карта или процессор обязаны успевать
каждую часть работы: сильная сторона не компенсирует слабую.

Обязательные возможности (D05) проверяются по каталогу до объявления
конфигурации подходящей: неподтверждённая поддержка — «неизвестно», а не
молчаливое «подходит».
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import ClassVar

from sqlalchemy.orm import Session

from .. import repositories
from ..models.entities import HardwareCPU, HardwareGPU
from ..schemas.catalog import (
    HardwareEstimateOut, NonClientMethodOut, ProjectProfile, count_scale_bounds,
    level_unspecified,
)
from . import rules, serializers

SCALE_FACTOR = {"small": 0.8, "medium": 1.0, "large": 1.25, "very_large": 1.5, "unknown": 1.0}
RESOLUTION_FACTOR = {
    "720p": 0.62, "768p": 0.68, "900p": 0.78, "1080p": 1.0,
    "1200p": 1.12, "1440p": 1.6, "1600p": 1.85, "2160p": 3.0, "4k": 3.0,
}
QUALITY_FACTOR = {"low": 0.7, "medium": 1.0, "high": 1.35, "ultra": 1.7}

# Подсистемы CPU (нормированные веса внутри 1.0).
CPU_SUBSYSTEMS: list[str] = [
    "main_thread",        # основной игровой цикл, управление кадрами
    "parallel_sim",       # параллельная симуляция (Job System, ECS)
    "render_prep",        # подготовка команд рендера (draw calls, culling)
    "physics",            # физическое моделирование
    "animation",          # анимация персонажей, скининг
    "ai",                 # AI, pathfinding, crowd
    "audio",              # аудио-декодирование, пространственный звук
    "network",            # сетевая репликация, сериализация
    "streaming",          # потоковая загрузка, декомпрессия
    "compute",            # CPU-side compute (подготовка compute шейдеров)
    "post_processing",    # CPU-side постобработка
]

# Подсистемы GPU (нормированные веса внутри 1.0).
GPU_SUBSYSTEMS: list[str] = [
    "geometry",           # вершинная обработка, геометрия
    "shading",            # затенение, материалы, текстурирование
    "lighting_shadows",   # освещение, тени
    "transparency",       # прозрачность, частицы, пост-FX прозрачных объектов
    "post_processing",    # постобработка, цветокоррекция, блум
    "compute",            # compute шейдеры (не связанные с растеризацией)
    "raster",             # растеризация (базовый проход)
    "rt",                 # трассировка лучей (RT)
]

# Подсистемы памяти
MEMORY_SUBSYSTEMS: list[str] = [
    "resident_set",       # resident-набор (VRAM + RAM)
    "load_peaks",         # пики загрузки/выгрузки
    "cpu_resources",      # CPU-side ресурсы (системная память под драйверы)
    "gpu_resources",      # GPU-side ресурсы (VRAM под текстуры, буферы)
    "buffers",            # постоянные буферы (command, uniform, vertex/index)
    "streaming",          # стриминговые буферы, декомпрессия
    "decompression",      # декомпрессия ассетов
]

# Базовые веса функций для каждой CPU-подсистемы (сумма по подсистемам ~ вклад функции).
# Значения подобраны так, чтобы суммарный вклад функции совпадал с прежним FEATURE_CPU_LOAD.
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
    "destruction_simulation":   {"physics": 0.10, "parallel_sim": 0.06},
    "project_architecture":     {"main_thread": 0.02},
    "art_pipeline":             {},
    "split_screen_rendering":   {"render_prep": 0.08, "main_thread": 0.04},
}

# Базовые веса функций для каждой GPU-подсистемы.
FEATURE_GPU_SUBSYSTEM_LOAD: dict[str, dict[str, float]] = {
    "open_world_streaming":     {"shading": 0.03, "geometry": 0.02},
    "large_scale_terrain":      {"geometry": 0.05, "shading": 0.05},
    "procedural_vegetation":    {"geometry": 0.06, "shading": 0.04},
    "dynamic_global_illumination": {"lighting_shadows": 0.20, "compute": 0.08},
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
}

# Влияние методов на подсистемы CPU (только для client-методов).
# Ключ: код метода -> {подсистема: дельта (-3..+3, отрицательное = экономия)}.
# Заполняется динамически из impact_cpu метода, распределяя по подсистемам.
METHOD_CPU_SUBSYSTEM_IMPACT: dict[str, dict[str, int]] = {}

# Влияние методов на подсистемы GPU.
METHOD_GPU_SUBSYSTEM_IMPACT: dict[str, dict[str, int]] = {}

# Влияние методов на память.
METHOD_MEMORY_SUBSYSTEM_IMPACT: dict[str, dict[str, int]] = {}

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
_UPSCALER_GPU_FACTOR = {
    "auto": 1.00, "none": 1.00, "taa": 0.96,
    "fsr": 0.84, "dlss": 0.80, "xess": 0.86,
}
# Сложность аудио влияет только на CPU.
_AUDIO_CPU_LOAD = {"low": 0.00, "medium": 0.03, "high": 0.07}
_UNKNOWN_AUDIO_NOTE = (
    "Сложность аудио не указана: стоимость декодирования и пространственного "
    "звука не учтена в оценке."
)
_STREAMING_METHODS = {
    "world_partition_streaming", "async_loading_pipeline", "navmesh_tiling_streaming",
    "tilemap_chunk_streaming", "audio_streaming_compression",
}

# Калибровочные коэффициенты.
# Подобраны под подсистемную модель D03.
GPU_CALIBRATION = 0.155
CPU_CALIBRATION = 0.20
#: RT-составляющая переводится в требование к отдельной сценарной шкале
#: rt_score (technical.city, якорь RTX 4090 = 1.0). Происхождение: RT-работа
#: сверх базовой единицы подсистемы rt при 1080p/high/60 и content≈1
#: должна требовать карту класса RTX 3050–3060 (rt_score 0.24–0.45).
GPU_RT_CALIBRATION = 1.0


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


def _fps_factor(fps: int) -> float:
    """Относительная стоимость кадра: выше целевой FPS — дороже каждый кадр."""
    if fps <= 30:
        return 0.62 * fps / 30
    if fps >= 144:
        return 1.7 * fps / 144
    # Линейная интерполяция между 30 и 144 кадрами в секунду.
    return 0.62 + (fps - 30) * (1.7 - 0.62) / (144 - 30)


def _render_fps_factor(profile: ProjectProfile) -> float:
    """Стоимость реально отрисованных кадров при включённой генерации кадров."""
    if profile.frame_generation and profile.base_render_fps is not None:
        return _fps_factor(profile.base_render_fps)
    return _fps_factor(profile.target_fps)


def _cpu_fps_factor(profile: ProjectProfile) -> float:
    """Частота, масштабирующая CPU-нагрузку.

    Сгенерированные кадры не выполняют симуляцию заново: при включённой
    генерации CPU следует за базовым рендером, а не за отображаемым FPS.
    Это частичное разделение G04/N04 — полный разбор render/sim/physics
    тиков требует подсистемных бюджетов (D03) и здесь не вводится.
    """
    if profile.frame_generation and profile.base_render_fps is not None:
        return _fps_factor(profile.base_render_fps)
    return _fps_factor(profile.target_fps)


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
    streaming = (
        profile.world_type in {"open_world", "procedural", "sandbox"}
        or bool(method_codes & _STREAMING_METHODS)
        or "storage_streaming" in profile.functions
    )
    if streaming and profile.scale in {"large", "very_large"}:
        return "nvme"
    if streaming or profile.format != "2D":
        return "sata_ssd"
    return "hdd"


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
    gaps: list[str] = []
    streaming = (
        profile.world_type in {"open_world", "procedural", "sandbox"}
        or bool(method_codes & _STREAMING_METHODS)
        or "storage_streaming" in profile.functions
    )
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
        gaps.append("Не задан physics/network tickrate: CPU-нагрузка симуляции взята по умолчанию.")
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
    """Выход входных данных за область, в которой модель различает значения.

    Модель насыщается: за верхней границей логарифмической шкалы разные числа
    объектов дают один и тот же индекс. Сообщать об этом обязан расчёт, а не
    пользователь: иначе одинаковый результат читается как доказанно равная
    реальная нагрузка.
    """
    limits: list[str] = []
    for field, value, label in (
        ("object_count", profile.object_count, "объектов"),
        ("npc_count", profile.npc_count, "NPC"),
    ):
        if value is None:
            continue
        _, top = count_scale_bounds(field)
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
    """Представление решений, чей эффект не относится к компьютеру игрока.

    Решения не удаляются из корзины и не считаются ошибочными: они просто не
    попадают в расчёт и перечисляются отдельно с указанием причины, иначе
    «не повлияло» не отличить от «забыто при расчёте».
    """
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


def _build_method_subsystem_impacts(methods: list) -> tuple[dict[str, dict[str, int]], dict[str, dict[str, int]], dict[str, dict[str, int]]]:
    """Построить карты влияния методов на подсистемы.

    Распределяет скалярные impact_* метода по подсистемам.
    Для методов без явного распределения использует эвристику по коду функции.
    """
    cpu_impacts: dict[str, dict[str, int]] = {}
    gpu_impacts: dict[str, dict[str, int]] = {}
    mem_impacts: dict[str, dict[str, int]] = {}

    for m in methods:
        code = m.code
        # CPU: распределяем impact_cpu по подсистемам в зависимости от функции метода
        cpu_total = m.impact_cpu
        if cpu_total != 0:
            # Эвристика: если метод связан с физикой/анимацией/ИИ — даём в соответствующие подсистемы
            fn_code = getattr(m, "function_code", None) or ""
            cpu_subs: dict[str, int] = {}
            if fn_code in {"physics_simulation", "destruction_simulation"}:
                cpu_subs = {"physics": cpu_total, "parallel_sim": max(0, cpu_total // 2)}
            elif fn_code in {"character_animation", "crowd_simulation"}:
                cpu_subs = {"animation": cpu_total, "parallel_sim": max(0, cpu_total // 2)}
            elif fn_code in {"ai_pathfinding", "crowd_simulation"}:
                cpu_subs = {"ai": cpu_total, "parallel_sim": max(0, cpu_total // 2)}
            elif fn_code in {"multiplayer_netcode"}:
                cpu_subs = {"network": cpu_total, "main_thread": max(0, cpu_total // 2)}
            elif fn_code in {"audio_system"}:
                cpu_subs = {"audio": cpu_total}
            elif fn_code in {"storage_streaming", "world_partition_streaming"}:
                cpu_subs = {"streaming": cpu_total, "main_thread": max(0, cpu_total // 2)}
            elif fn_code in {"rendering_architecture", "geometry_pipeline", "render_scalability"}:
                cpu_subs = {"render_prep": cpu_total, "main_thread": max(0, cpu_total // 2)}
            elif fn_code in {"dynamic_shadows", "dynamic_global_illumination", "baked_lighting"}:
                cpu_subs = {"render_prep": cpu_total, "main_thread": max(0, cpu_total // 2)}
            else:
                # Общий метод или неизвестная функция — даём в main_thread
                cpu_subs = {"main_thread": cpu_total}
            cpu_impacts[code] = cpu_subs

        # GPU: распределяем impact_gpu
        gpu_total = m.impact_gpu
        if gpu_total != 0:
            fn_code = getattr(m, "function_code", None) or ""
            gpu_subs: dict[str, int] = {}
            if fn_code in {"dynamic_shadows", "dynamic_global_illumination", "baked_lighting", "volumetric_effects"}:
                gpu_subs = {"lighting_shadows": gpu_total, "shading": max(0, gpu_total // 2)}
            elif fn_code in {"particle_systems", "water_simulation", "split_screen_rendering"}:
                gpu_subs = {"transparency": gpu_total, "shading": max(0, gpu_total // 2)}
            elif fn_code in {"rendering_architecture", "geometry_pipeline"}:
                gpu_subs = {"geometry": gpu_total, "raster": max(0, gpu_total // 2)}
            elif fn_code in {"post_processing", "upscaling_frame_generation"}:
                gpu_subs = {"post_processing": gpu_total}
            elif fn_code in {"procedural_vegetation", "large_scale_terrain", "crowd_simulation"}:
                gpu_subs = {"geometry": gpu_total, "shading": max(0, gpu_total // 2)}
            else:
                gpu_subs = {"shading": gpu_total, "raster": max(0, gpu_total // 2)}
            gpu_impacts[code] = gpu_subs

        # Memory: распределяем impact_vram/impact_ram
        mem_subs: dict[str, int] = {}
        if m.impact_vram != 0:
            mem_subs["gpu_resources"] = m.impact_vram
            mem_subs["buffers"] = max(0, m.impact_vram // 2)
        if m.impact_ram != 0:
            mem_subs["cpu_resources"] = m.impact_ram
            mem_subs["resident_set"] = max(0, m.impact_ram // 2)
        if mem_subs:
            mem_impacts[code] = mem_subs

    return cpu_impacts, gpu_impacts, mem_impacts


def _load_indices(profile: ProjectProfile, methods: list) -> dict:
    """Нагрузочные индексы GPU/CPU и оценка памяти по профилю и решениям (подсистемная модель D03)."""
    client_methods, outside_client = rules.split_by_effect_scope(methods)
    non_client_methods = _non_client_out(outside_client)
    res = _resolution_factor(profile.target_resolution)
    cpu_fps = _cpu_fps_factor(profile)
    render_fps = _render_fps_factor(profile)
    quality = QUALITY_FACTOR.get(profile.target_quality, 1.0)
    scale = _largest_impact(profile)
    obj = 0.85 + 0.35 * profile.object_count_effective
    npc = 0.85 + 0.35 * profile.npc_count_effective
    content = scale * obj * npc

    method_codes = {m.code for m in client_methods}
    recommended_storage = _recommended_storage(profile, method_codes)
    estimated_draw_calls = _estimated_draw_calls(profile, content, method_codes)
    modeling_gaps = _modeling_gaps(profile, method_codes, recommended_storage)
    applicability_limits = _applicability_limits(profile)

    # --- Подсистемная нагрузка CPU ---
    cpu_subsystem_load: dict[str, float] = {s: 1.0 for s in CPU_SUBSYSTEMS}
    # Базовая нагрузка от функций
    for fn in profile.functions:
        for subsys, weight in FEATURE_CPU_SUBSYSTEM_LOAD.get(fn, {}).items():
            cpu_subsystem_load[subsys] *= (1.0 + weight)
    # Мультиплеер
    if profile.multiplayer:
        cpu_subsystem_load["network"] *= (1.0 + 0.15 + 0.1 * min(1.0, profile.player_count / 32))
        if profile.network_topology == "lockstep":
            cpu_subsystem_load["network"] *= 1.08
        elif profile.network_topology == "p2p":
            cpu_subsystem_load["network"] *= 1.04
    # Аудио
    if not level_unspecified(profile.audio_complexity):
        cpu_subsystem_load["audio"] *= (1.0 + _AUDIO_CPU_LOAD[profile.audio_complexity])
    # Радиус симуляции
    if profile.simulation_radius_m is not None and {"ai_pathfinding", "crowd_simulation"} & set(profile.functions):
        factor = 1.0 + min(0.25, profile.simulation_radius_m / 40_000)
        cpu_subsystem_load["ai"] *= factor
        cpu_subsystem_load["parallel_sim"] *= factor
    # Физика tick rate
    if profile.physics_tick_hz is not None and "physics_simulation" in profile.functions:
        factor = 1.0 + (profile.physics_tick_hz / 60.0 - 1.0) * 0.5
        cpu_subsystem_load["physics"] *= factor
    # Методы: применяем влияния к подсистемам
    cpu_method_impacts, gpu_method_impacts, mem_method_impacts = _build_method_subsystem_impacts(client_methods)
    for code, impacts in cpu_method_impacts.items():
        for subsys, delta in impacts.items():
            if subsys in cpu_subsystem_load:
                cpu_subsystem_load[subsys] *= (1.0 + 0.07 * delta)

    # Считаем итоговый CPU индекс: сумма подсистем с учётом параллелизма
    # main_thread и render_prep — последовательны; остальные могут быть параллельны
    sequential_cpu = cpu_subsystem_load["main_thread"] * cpu_subsystem_load["render_prep"]
    parallel_cpu = 1.0
    for s in ["parallel_sim", "physics", "animation", "ai", "audio", "network", "streaming"]:
        parallel_cpu *= cpu_subsystem_load[s]
    # Упрощённая модель: последовательная часть + параллельная / 4 (4 ядра условно)
    cpu_subsystem_total = sequential_cpu + parallel_cpu / 4.0

    # --- Подсистемная нагрузка GPU ---
    gpu_subsystem_load: dict[str, float] = {s: 1.0 for s in GPU_SUBSYSTEMS}
    for fn in profile.functions:
        for subsys, weight in FEATURE_GPU_SUBSYSTEM_LOAD.get(fn, {}).items():
            gpu_subsystem_load[subsys] *= (1.0 + weight)
    # Методы GPU
    _, gpu_method_impacts, _ = _build_method_subsystem_impacts(client_methods)
    for code, impacts in gpu_method_impacts.items():
        for subsys, delta in impacts.items():
            if subsys in gpu_subsystem_load:
                gpu_subsystem_load[subsys] *= (1.0 + 0.06 * delta)

    # GPU последовательность: geometry -> shading -> lighting_shadows -> transparency -> post_processing
    # compute, raster, rt могут быть параллельны частично
    gpu_sequential = (gpu_subsystem_load["geometry"] * gpu_subsystem_load["shading"] *
                      gpu_subsystem_load["lighting_shadows"] * gpu_subsystem_load["transparency"] *
                      gpu_subsystem_load["post_processing"])
    gpu_parallel = 1.0
    for s in ["compute", "raster", "rt"]:
        gpu_parallel *= gpu_subsystem_load[s]
    gpu_subsystem_total = gpu_sequential + gpu_parallel / 4.0

    # Итоговые индексы с калибровкой
    gpu_index = GPU_CALIBRATION * res * render_fps * quality * content * gpu_subsystem_total
    cpu_index = CPU_CALIBRATION * content * cpu_subsystem_total * cpu_fps

    # АПИ и хранилище
    api_gpu, api_cpu = _API_FACTORS.get(profile.render_api, _API_FACTORS["auto"])
    storage_cpu = _STORAGE_CPU_FACTOR.get(profile.storage_type, 1.0)
    upscaler = profile.upscaling_method
    if upscaler == "auto" and "temporal_upscaling" in method_codes:
        upscaler = "taa"
    gpu_index *= api_gpu * _UPSCALER_GPU_FACTOR.get(upscaler, 1.0)
    cpu_index *= api_cpu * storage_cpu

    # Ограничения
    gpu_index = max(0.01, gpu_index)
    cpu_index = max(0.01, cpu_index)

    # --- Память ---
    vram_gb = 1.4 + 2.0 * res + 2.4 * (quality - 0.7) + 1.2 * (content - 1.0)
    ram_gb = 4.0 + 4.0 * content + 2.0 * profile.object_count_effective
    # Методы влияют на память
    for code, impacts in mem_method_impacts.items():
        for subsys, delta in impacts.items():
            if subsys in {"gpu_resources", "buffers"}:
                vram_gb += 0.3 * delta
            if subsys in {"cpu_resources", "resident_set"}:
                ram_gb += 0.25 * delta
    # Unified memory — без скидки, только gap
    vram_gb = max(1.5, round(vram_gb, 1))
    ram_gb = max(4.0, round(ram_gb, 1))

    # Аппаратные возможности
    required_hw = sorted({
        feature for m in client_methods for feature in (m.requires_hw_features or [])
    })
    if profile.upscaling_method == "dlss":
        required_hw = sorted(set(required_hw) | {"DLSS"})

    return {
        "gpu_index": gpu_index, "cpu_index": cpu_index,
        "vram_gb": vram_gb, "ram_gb": ram_gb,
        "required_rt": any(
            "Hardware Ray Tracing" in (m.requires_hw_features or []) for m in client_methods
        ),
        "required_hw": required_hw,
        "recommended_storage": recommended_storage,
        "estimated_draw_calls": estimated_draw_calls,
        "modeling_gaps": modeling_gaps,
        "applicability_limits": applicability_limits,
        "non_client_methods": non_client_methods,
        # Новые: подсистемные разборы для UI/экспорта
        "cpu_subsystem_load": cpu_subsystem_load,
        "gpu_subsystem_load": gpu_subsystem_load,
        "cpu_subsystem_total": cpu_subsystem_total,
        "gpu_subsystem_total": gpu_subsystem_total,
    }


# Маркеры мобильных и встроенных решений в названиях моделей каталога.
# Референс для десктопного профиля обязан быть десктопным: мобильная карта
# в ответе вводит в заблуждение (её нельзя купить в десктоп). Анкета целевой
# форм-фактор не спрашивает, поэтому правило одно: сначала десктопный пул,
# при отсутствии подходящего — весь пул (лучше мобильный ориентир, чем никакого).
#
# Намеренно узкие токены для Vega: в каталоге только встройки Vega 3/8,
# а широкое "vega" метило бы и дискретные RX Vega 56/64 как мобильные.
# Маркер "(tm)" удалён: в каталоге он ничего не находит, а любое упоминание
# товарного знака метило бы карту мобильной по ошибке.
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


def _pick_gpu(
    pool: list[HardwareGPU], index: float, *, required_rt: bool,
    vram_limit_gb: float | None, vram_gb: float,
) -> tuple[HardwareGPU | None, bool]:
    """Выбрать видеокарту. Второй элемент — признак «требование не выполнено».

    Аппаратная трассировка лучей — обязательная возможность, а не пожелание:
    если выбранные решения её требуют, видеокарта без RT не подходит ни при
    какой производительности.
    """
    if required_rt:
        pool = [g for g in pool if _supports_ray_tracing(g)]
        if not pool:
            return None, True
    # Потребность проекта обязательна даже без пользовательского бюджета.
    # Сам бюджет сравнивается с потребностью отдельно в _pick_references.
    pool = [g for g in pool if g.vram_gb >= vram_gb]
    candidates = [g for g in pool if g.raster_score >= index]
    if not candidates:
        return None, False
    # Из подходящих выбираем наиболее скромную по классу и производительности.
    # Десктопные карты предпочтительнее мобильных и встроек: мобильный референс
    # для десктопного профиля вводит в заблуждение. Если десктопа нет — честно
    # берём из всего пула (см. комментарий к _MOBILE_GPU_MARKERS).
    desktop = [g for g in candidates if not _is_mobile_gpu(g.model)]
    chosen = desktop or candidates
    return min(chosen, key=lambda g: (g.perf_class, g.raster_score)), False


def _pick_cpu(pool: list[HardwareCPU], index: float) -> HardwareCPU | None:
    candidates = [c for c in pool if c.multi_thread_score >= index]
    if not candidates:
        return None
    desktop = [c for c in candidates if not _is_mobile_cpu(c.model)]
    chosen = desktop or candidates
    return min(chosen, key=lambda c: (c.perf_class, c.multi_thread_score))


def _alternatives(rows, reference):
    """Альтернативы: тот же класс, но более современные записи."""
    if reference is None:
        return []
    same_class = [r for r in rows if r.perf_class == reference.perf_class and r.model != reference.model]
    return sorted(same_class, key=lambda r: r.release_year, reverse=True)[:4]


def _pick_references(db: Session, indices: dict, profile: ProjectProfile) -> dict:
    """Референсные CPU/GPU по опубликованному каталогу и обязательным требованиям."""
    # Только опубликованные записи: снятое с публикации оборудование не должно
    # попадать в оценку.
    gpus = sorted(repositories.hardware_gpu(db), key=lambda g: g.raster_score)
    cpus = sorted(repositories.hardware_cpu(db), key=lambda c: c.multi_thread_score)
    vram_gb = indices["vram_gb"]

    # Заданные пользователем пределы памяти — обязательные ограничения, а не
    # справочные числа. Нарушение фиксируется отдельно: молча вернуть
    # конфигурацию, не входящую в бюджет, значит ввести пользователя в заблуждение.
    unmet: list[str] = []
    caveats: list[str] = []
    if profile.vram_limit_gb is not None and vram_gb > profile.vram_limit_gb:
        unmet.append(
            f"Требуется {vram_gb:.1f} ГБ видеопамяти при заданном пределе "
            f"{profile.vram_limit_gb:.1f} ГБ."
        )
    ram_gb = indices["ram_gb"]
    if profile.ram_limit_gb is not None and ram_gb > profile.ram_limit_gb:
        unmet.append(
            f"Требуется {ram_gb:.1f} ГБ оперативной памяти при заданном пределе "
            f"{profile.ram_limit_gb:.1f} ГБ."
        )
    recommended_storage = indices["recommended_storage"]
    if (
        profile.storage_type != "auto"
        and _STORAGE_RANK.get(profile.storage_type, 0) < _STORAGE_RANK[recommended_storage]
    ):
        caveats.append(
            f"Накопитель {profile.storage_type} ниже рекомендуемого класса "
            f"{recommended_storage}: возможны задержки подкачки. Без бюджета потоковых данных "
            "недостаточность накопителя не установлена."
        )
    if profile.draw_call_budget is not None and indices["estimated_draw_calls"] > profile.draw_call_budget:
        caveats.append(
            f"Оценочно требуется около {indices['estimated_draw_calls']:,} draw calls при бюджете "
            f"{profile.draw_call_budget:,}. Это риск превышения бюджета, а не измеренное число вызовов.".replace(",", " ")
        )

    compatible_gpus = [g for g in gpus if _supports_profile_gpu(g, profile)]
    if not compatible_gpus and gpus:
        unmet.append("В каталоге нет GPU с подтверждённой поддержкой выбранного API и апскейлера.")
    reference_gpu, rt_missing = _pick_gpu(
        compatible_gpus, indices["gpu_index"], required_rt=indices["required_rt"],
        vram_limit_gb=profile.vram_limit_gb, vram_gb=vram_gb,
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
        else:
            caveats.append(
                "В каталоге нет GPU, одновременно покрывающего расчётную производительность, "
                "видеопамять и обязательные возможности. Показанная карта — только ориентир."
            )
        # Показываем максимально близкую запись как ориентир, но помечаем,
        # что конфигурация не покрывает требования.
        reference_gpu = max(compatible_gpus, key=lambda g: g.raster_score) if compatible_gpus else None
    if reference_gpu is not None and reference_gpu.vram_gb < vram_gb:
        unmet.append(
            f"Видеокарта {reference_gpu.model} имеет {reference_gpu.vram_gb:g} ГБ видеопамяти "
            f"при требуемых {vram_gb:.1f} ГБ: в базе нет карты, одновременно достаточно "
            "производительной и вместительной."
        )

    reference_cpu = _pick_cpu(cpus, indices["cpu_index"])
    if reference_cpu is None:
        exceeds = True
        if cpus:
            reference_cpu = max(cpus, key=lambda c: c.multi_thread_score)
            caveats.append(
                "Требуемая производительность CPU превышает самую производительную запись базы."
            )
        else:
            caveats.append("В базе нет опубликованных записей о процессорах: оценка не выполнена.")

    # Область применимости прогноза — только Windows/Linux ПК (D06). Смешанные
    # цели сохраняют PC-ориентир с предупреждением; чисто не-PC цели получают
    # явный отказ вместо PC-карты в поле подходящей рекомендации.
    has_pc, non_pc = _platform_status(profile)
    if non_pc and not has_pc:
        scope_note = _platform_scope_note(non_pc)
        unmet.append(scope_note)
        caveats.append(
            scope_note + " Инженерные объяснения и индексы нагрузки приведены, "
            "но совместимая конфигурация не подбирается."
        )
        reference_gpu = None
        reference_cpu = None
        exceeds = True
        return {
            "gpus": gpus, "cpus": cpus, "reference_gpu": None,
            "reference_cpu": None, "alt_gpus": [], "alt_cpus": [],
            "exceeds": exceeds, "unmet": unmet, "caveats": caveats,
        }
    if non_pc:
        mixed_note = (
            _platform_scope_note(non_pc) + " Приведённый ориентир относится "
            "только к PC-цели."
        )
        caveats.append(mixed_note)

    return {
        "gpus": gpus, "cpus": cpus, "reference_gpu": reference_gpu,
        "reference_cpu": reference_cpu,
        "alt_gpus": _alternatives([
            g for g in compatible_gpus
            if g.raster_score >= indices["gpu_index"] and g.vram_gb >= vram_gb
            and (not indices["required_rt"] or _supports_ray_tracing(g))
        ], reference_gpu),
        "alt_cpus": _alternatives([
            c for c in cpus if c.multi_thread_score >= indices["cpu_index"]
        ], reference_cpu),
        "exceeds": exceeds, "unmet": unmet, "caveats": caveats,
    }


def _confidence(
    profile: ProjectProfile,
    methods: list,
    *,
    similar_examples: int,
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
    if similar_examples == 0:
        confidence -= 0.12
        caveats.append("Не найдено похожих игр в базе: сверка с практикой невозможна.")
    if exceeds:
        confidence -= 0.15
    _, non_pc_platforms = _platform_status(profile)
    if non_pc_platforms:
        confidence -= 0.15
        caveats.append(
            _platform_scope_note(non_pc_platforms) + " Оценка относится "
            "только к Windows/Linux ПК."
        )
    if not methods:
        confidence -= 0.1
        caveats.append("Корзина решений пуста: оценка выполнена по базовому профилю проекта.")
    confidence -= min(0.18, 0.02 * len(modeling_gaps))
    if unmet:
        # Заданный бюджет памяти не выполняется: конфигурация приведена как
        # ориентир, но называть её подходящей нельзя.
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
    if profile.target_fps >= 120:
        caveats.append(
            "Целевые 120 FPS и выше обычно ограничиваются процессором: запас по CPU должен быть "
            "выше рассчитанного."
        )
    return confidence, label, caveats


def estimate_hardware(
    db: Session,
    profile: ProjectProfile,
    methods: list,
    similar_examples: int = 0,
) -> HardwareEstimateOut:
    """Рассчитать ориентировочную минимальную конфигурацию."""
    methods, basket_notes = rules.assess_selected_methods(methods, profile, repositories.conflicts(db))
    indices = _load_indices(profile, methods)
    picked = _pick_references(db, indices, profile)
    confidence, label, confidence_caveats = _confidence(
        profile, methods, similar_examples=similar_examples,
        exceeds=picked["exceeds"], unmet=picked["unmet"],
        modeling_gaps=indices["modeling_gaps"] + basket_notes,
    )
    caveats = picked["caveats"] + basket_notes + confidence_caveats
    non_client_methods = indices["non_client_methods"]
    if non_client_methods:
        # Предупреждение дублирует структурированный список: оговорки видны и
        # там, где интерфейс не выводит отдельные поля.
        names = ", ".join(f"«{item.name}»" for item in non_client_methods)
        caveats.append(
            f"В оценку не вошли решения {names}: их эффект не относится к компьютеру игрока."
        )
    reference_gpu = picked["reference_gpu"]
    reference_cpu = picked["reference_cpu"]

    return HardwareEstimateOut(
        required_gpu_index=round(indices["gpu_index"], 4),
        required_cpu_index=round(indices["cpu_index"], 4),
        estimated_vram_gb=float(indices["vram_gb"]),
        estimated_ram_gb=float(indices["ram_gb"]),
        gpu_class=reference_gpu.perf_class if reference_gpu else 5,
        cpu_class=reference_cpu.perf_class if reference_cpu else 5,
        reference_gpu=serializers.gpu_out(reference_gpu) if reference_gpu else None,
        reference_cpu=serializers.cpu_out(reference_cpu) if reference_cpu else None,
        alternative_gpus=[serializers.gpu_out(g) for g in picked["alt_gpus"]],
        alternative_cpus=[serializers.cpu_out(c) for c in picked["alt_cpus"]],
        confidence=confidence,
        confidence_label=label,
        caveats=caveats,
        required_hw_features=indices["required_hw"],
        exceeds_catalog=picked["exceeds"],
        recommended_storage=indices["recommended_storage"],
        estimated_draw_calls=indices["estimated_draw_calls"],
        modeling_gaps=indices["modeling_gaps"],
        unmet_limits=picked["unmet"],
        applicability_limits=indices["applicability_limits"],
        non_client_methods=non_client_methods,
    )
