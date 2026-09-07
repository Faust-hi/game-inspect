"""Оценка ориентировочного минимального класса оборудования.

Результат намеренно формулируется как ориентировочный класс, а не как гарантия
конкретного значения FPS: система не располагает данными профилирования
конкретного проекта и не должна создавать ложную точность.
"""
from __future__ import annotations

import re

from sqlalchemy.orm import Session

from .. import repositories
from ..models.entities import HardwareCPU, HardwareGPU
from ..models.enums import Scale
from ..schemas.catalog import HardwareEstimateOut, ProjectProfile
from . import rules, serializers

SCALE_FACTOR = {"small": 0.8, "medium": 1.0, "large": 1.25, "very_large": 1.5}
RESOLUTION_FACTOR = {
    "720p": 0.62, "768p": 0.68, "900p": 0.78, "1080p": 1.0,
    "1200p": 1.12, "1440p": 1.6, "1600p": 1.85, "2160p": 3.0, "4k": 3.0,
}
QUALITY_FACTOR = {"low": 0.7, "medium": 1.0, "high": 1.35, "ultra": 1.7}

# Вклад каждой игровой функции в нагрузку на GPU и CPU.
FEATURE_GPU_LOAD = {
    "open_world_streaming": 0.05, "large_scale_terrain": 0.10, "procedural_vegetation": 0.10,
    "dynamic_global_illumination": 0.28, "baked_lighting": 0.02, "dynamic_shadows": 0.14,
    "particle_systems": 0.08, "physics_simulation": 0.02, "character_animation": 0.03,
    "crowd_simulation": 0.10, "ai_pathfinding": 0.01, "water_simulation": 0.10,
    "volumetric_effects": 0.16, "post_processing": 0.08, "multiplayer_netcode": 0.01,
    "rendering_architecture": 0.10, "render_scalability": 0.04,
    "geometry_pipeline": 0.05, "upscaling_frame_generation": 0.04,
    "storage_streaming": 0.02, "audio_system": 0.01,
    "build_delivery": 0.0, "runtime_memory": 0.01,
    "destruction_simulation": 0.12, "project_architecture": 0.0,
    "art_pipeline": 0.0, "split_screen_rendering": 0.20,
}
FEATURE_CPU_LOAD = {
    "open_world_streaming": 0.16, "large_scale_terrain": 0.08, "procedural_vegetation": 0.10,
    "dynamic_global_illumination": 0.06, "baked_lighting": 0.04, "dynamic_shadows": 0.06,
    "particle_systems": 0.06, "physics_simulation": 0.18, "character_animation": 0.10,
    "crowd_simulation": 0.22, "ai_pathfinding": 0.18, "water_simulation": 0.03,
    "volumetric_effects": 0.03, "post_processing": 0.03, "multiplayer_netcode": 0.16,
    "rendering_architecture": 0.10, "render_scalability": 0.03,
    "geometry_pipeline": 0.05, "upscaling_frame_generation": 0.02,
    "storage_streaming": 0.10, "audio_system": 0.05,
    "build_delivery": 0.01, "runtime_memory": 0.08,
    "destruction_simulation": 0.16, "project_architecture": 0.02,
    "art_pipeline": 0.0, "split_screen_rendering": 0.12,
}

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
_AUDIO_CPU_LOAD = {"low": 0.00, "medium": 0.03, "high": 0.07}
_STREAMING_METHODS = {
    "world_partition_streaming", "async_loading_pipeline", "navmesh_tiling_streaming",
    "tilemap_chunk_streaming", "audio_streaming_compression",
}

# Калибровочные коэффициенты: приводят свёртку факторов к нормализованным
# индексам каталога (1.0 — самая производительная запись в базе).
#
# Значения проверены калибровочным прогоном (tests/test_calibration.py)
# по контрольным проектам:
#   * 2D-игра, небольшой мир, 1080p/низкое            → GPU ~0.10 (класс 1–2);
#   * линейная 3D-игра, средний мир, 1080p/высокое/60 → GPU ~0.24 (класс 2);
#     класс 3 здесь был бы завышением: GTX 1660 Super честно тянет такой
#     профиль, а индекс 0.30+ получается только с тяжёлыми функциями
#     (тени/персонажи/пост), которые в эталон не входят;
#   * открытый мир, 1440p/высокое/60, тяжёлые функции → GPU ~0.68 (класс 4–5);
#   * 4K/ультра/очень большой мир                     → индекс > 1.0, фиксируется
#     превышение каталога.
# GPU_CALIBRATION поднят с 0.18 до 0.20: внешний sanity-check по Technical
# City показывал, что тяжёлый 1080p/high/60 open-world профиль с выбранными
# оптимизациями иногда опускался ниже класса RTX 3060/аналогов, хотя такой
# класс уже является разумным нижним ориентиром для современных PC-сценариев.
# Это не превращает внешние требования в жёсткое правило: версия игры,
# пресет и режим теста могут отличаться.
#
# CPU_CALIBRATION снижен с 0.26 до 0.25: иначе крошечная 2D-игра требовала
# минимум i7-8700K (класс 3) при разрыве в 0.007 до Ryzen 5 2600 — пессимизм
# без оснований. Остальные эталоны класс не меняют (проверено прогоном).
GPU_CALIBRATION = 0.20
CPU_CALIBRATION = 0.25


def _supports_ray_tracing(gpu: HardwareGPU) -> bool:
    """Проверяет наличие аппаратной трассировки лучей по признакам каталога."""
    features = [str(f).lower() for f in (gpu.hw_features or [])]
    return any("ray tracing" in f or "rt core" in f or "rtx" in f for f in features)


def _resolution_factor(value: str) -> float:
    if not value:
        return 1.0
    return RESOLUTION_FACTOR.get(value.strip().lower(), 1.0)


def _supports_profile_gpu(gpu: HardwareGPU, profile: ProjectProfile) -> bool:
    """Проверка заявленных возможностей каталога, без догадок по имени GPU."""
    features = [str(item).lower() for item in (gpu.hw_features or [])]
    if profile.upscaling_method == "dlss" and not any(item.startswith("dlss") for item in features):
        return False
    apis = [str(item).lower() for item in (gpu.api_support or [])]
    api = profile.render_api
    if api == "auto":
        return True
    if api in {"dx9", "dx11", "dx12"}:
        required = int(api[2:])
        versions = [re.search(r"directx\s+(\d+)", item) for item in apis]
        return any(match and int(match.group(1)) >= required for match in versions)
    return any(item.startswith(api) for item in apis)


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


def _largest_impact(profile: ProjectProfile) -> float:
    return SCALE_FACTOR.get(
        Scale(profile.scale).value if profile.scale in {s.value for s in Scale} else "medium", 1.0
    )


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
    if profile.audio_complexity is None and "audio_system" in profile.functions:
        gaps.append("Не задана сложность аудио: стоимость декодирования и пространственного звука неизвестна.")
    if profile.multiplayer and profile.network_topology == "auto":
        gaps.append("Не указана сетевая схема: P2P, client-server, dedicated и lockstep имеют разную цену.")
    if profile.target_resolution in {"1440p", "1600p", "2160p", "4k"} and profile.upscaling_method == "auto":
        gaps.append("Не указан upscaler: итоговая GPU-нагрузка для высокого разрешения может отличаться.")
    if profile.frame_generation:
        gaps.append("Генерация кадров повышает отображаемый FPS, но не заменяет базовый FPS и добавляет задержку.")
        if profile.base_render_fps is None:
            gaps.append("Не задан целевой базовый FPS: расчёт выполнен без снижения требований за счёт генерации кадров.")
        else:
            gaps.append("Рассчитана нагрузка базового рендера; стоимость генератора и достижение отображаемого FPS не подтверждены.")
        gaps.append("Не указаны технология и версия генерации кадров: совместимость оборудования требует отдельной проверки.")
    return gaps


def _load_indices(profile: ProjectProfile, methods: list) -> dict:
    """Нагрузочные индексы GPU/CPU и оценка памяти по профилю и решениям."""
    res = _resolution_factor(profile.target_resolution)
    fps = _fps_factor(profile.target_fps)
    render_fps = _render_fps_factor(profile)
    quality = QUALITY_FACTOR.get(profile.target_quality, 1.0)
    scale = _largest_impact(profile)
    # Точное число объектов и NPC участвует в расчёте напрямую, а не только
    # через качественный уровень: иначе изменение числа с 1 000 до 1 000 000
    # не влияло бы на результат, но повышало бы «уверенность» оценки.
    obj = 0.85 + 0.35 * profile.object_count_effective
    npc = 0.85 + 0.35 * profile.npc_count_effective
    content = scale * obj * npc

    method_codes = {m.code for m in methods}
    recommended_storage = _recommended_storage(profile, method_codes)
    estimated_draw_calls = _estimated_draw_calls(profile, content, method_codes)
    modeling_gaps = _modeling_gaps(profile, method_codes, recommended_storage)

    feature_gpu = 1.0 + sum(FEATURE_GPU_LOAD.get(f, 0.05) for f in profile.functions)
    feature_cpu = 1.0 + sum(FEATURE_CPU_LOAD.get(f, 0.05) for f in profile.functions)
    if profile.multiplayer:
        feature_cpu += 0.15 + 0.1 * min(1.0, profile.player_count / 32)
        if profile.network_topology == "lockstep":
            feature_cpu += 0.08
        elif profile.network_topology == "p2p":
            feature_cpu += 0.04

    if profile.audio_complexity:
        feature_cpu += _AUDIO_CPU_LOAD[profile.audio_complexity]
    if profile.simulation_radius_m is not None and {"ai_pathfinding", "crowd_simulation"} & set(profile.functions):
        feature_cpu *= 1.0 + min(0.25, profile.simulation_radius_m / 40_000)
    if profile.physics_tick_hz is not None and "physics_simulation" in profile.functions:
        # Частота физики меняет только вклад физической симуляции.
        feature_cpu += FEATURE_CPU_LOAD["physics_simulation"] * (profile.physics_tick_hz / 60 - 1.0)

    gpu_method = 1.0 + 0.06 * sum(m.impact_gpu for m in methods)
    cpu_method = 1.0 + 0.07 * sum(m.impact_cpu for m in methods)
    vram_method = 0.6 * sum(m.impact_vram for m in methods)
    ram_method = 0.5 * sum(m.impact_ram for m in methods)
    gpu_method = max(0.45, min(2.0, gpu_method))
    cpu_method = max(0.45, min(2.0, cpu_method))

    api_gpu, api_cpu = _API_FACTORS.get(profile.render_api, _API_FACTORS["auto"])
    storage_cpu = _STORAGE_CPU_FACTOR.get(profile.storage_type, 1.0)
    upscaler = profile.upscaling_method
    if upscaler == "auto" and "temporal_upscaling" in method_codes:
        upscaler = "taa"
    gpu_index = (
        GPU_CALIBRATION * res * render_fps * quality * content * feature_gpu * gpu_method
        * api_gpu * _UPSCALER_GPU_FACTOR.get(upscaler, 1.0)
    )
    cpu_index = (
        CPU_CALIBRATION * content * feature_cpu * cpu_method * (0.6 + 0.4 * fps)
        * api_cpu * storage_cpu
    )
    # Бюджет служит для сравнения с оценкой, а не изменяет объём работы.

    vram_gb = 1.4 + 2.0 * res + 2.4 * (quality - 0.7) + 1.2 * (content - 1.0) + vram_method
    if profile.memory_model == "unified":
        vram_gb *= 0.9
    vram_gb = max(1.5, round(vram_gb, 1))
    ram_gb = 4.0 + 4.0 * content + 2.0 * profile.object_count_effective + ram_method
    if profile.streaming_pool_gb is not None:
        ram_gb += min(8.0, profile.streaming_pool_gb * 0.15)
    if profile.memory_model == "managed":
        ram_gb += 1.0
    ram_gb = max(4.0, round(ram_gb, 1))

    required_hw = sorted({
        feature for m in methods for feature in (m.requires_hw_features or [])
    })
    if profile.upscaling_method == "dlss":
        required_hw = sorted(set(required_hw) | {"DLSS"})
    return {
        "gpu_index": gpu_index, "cpu_index": cpu_index,
        "vram_gb": vram_gb, "ram_gb": ram_gb,
        "required_rt": any("Hardware Ray Tracing" in (m.requires_hw_features or []) for m in methods),
        "required_hw": required_hw,
        "recommended_storage": recommended_storage,
        "estimated_draw_calls": estimated_draw_calls,
        "modeling_gaps": modeling_gaps,
    }


# Маркеры мобильных и встроенных решений в названиях моделей каталога.
# Референс для десктопного профиля обязан быть десктопным: мобильная карта
# в ответе вводит в заблуждение (её нельзя купить в десктоп). Анкета целевой
# форм-фактор не спрашивает, поэтому правило одно: сначала десктопный пул,
# при отсутствии подходящего — весь пул (лучше мобильный ориентир, чем никакого).
_MOBILE_GPU_MARKERS = (
    "laptop", "mobile", "uhd", "hd graphics", "iris", "vega",
    "radeon 780m", "radeon graphics", "(tm)",
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
        caveats.append("Количество объектов задано качественным уровнем, а не числом: оценка приблизительная.")
    if profile.npc_count is None:
        confidence -= 0.06
    if similar_examples == 0:
        confidence -= 0.12
        caveats.append("Не найдено похожих игр в базе: сверка с практикой невозможна.")
    if exceeds:
        confidence -= 0.15
    if any(p in ("android", "ios", "switch", "ps4", "xbox_one") for p in profile.platforms):
        confidence -= 0.15
        caveats.append(
            "Для части целевых платформ в базе нет данных об оборудовании: оценка относится "
            "только к персональным компьютерам."
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
    )
