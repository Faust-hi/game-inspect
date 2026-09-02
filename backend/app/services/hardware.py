"""Оценка ориентировочного минимального класса оборудования.

Результат намеренно формулируется как ориентировочный класс, а не как гарантия
конкретного значения FPS: система не располагает данными профилирования
конкретного проекта и не должна создавать ложную точность.
"""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models.entities import HardwareCPU, HardwareGPU
from ..models.enums import Level3, Scale
from ..schemas.catalog import HardwareEstimateOut, ProjectProfile
from . import serializers

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
}
FEATURE_CPU_LOAD = {
    "open_world_streaming": 0.16, "large_scale_terrain": 0.08, "procedural_vegetation": 0.10,
    "dynamic_global_illumination": 0.06, "baked_lighting": 0.04, "dynamic_shadows": 0.06,
    "particle_systems": 0.06, "physics_simulation": 0.18, "character_animation": 0.10,
    "crowd_simulation": 0.22, "ai_pathfinding": 0.18, "water_simulation": 0.03,
    "volumetric_effects": 0.03, "post_processing": 0.03, "multiplayer_netcode": 0.16,
}

# Калибровочные коэффициенты: приводят свёртку факторов к нормализованным
# индексам каталога (1.0 — самая производительная запись в базе).
#
# Значения подобраны по контрольным проектам:
#   * 2D-игра, небольшой мир, 1080p/низкое            → индекс 0.10–0.20 (класс 1–2);
#   * линейная 3D-игра, средний мир, 1080p/высокое/60 → индекс 0.30–0.45 (класс 3);
#   * открытый мир, 1440p/высокое/60, тяжёлые функции → индекс 0.70–0.85 (класс 4–5);
#   * 4K/ультра/очень большой мир                     → индекс > 1.0, фиксируется
#     превышение каталога.
GPU_CALIBRATION = 0.18
CPU_CALIBRATION = 0.26


def _level(value: str | None, default: float = 0.55) -> float:
    try:
        return Level3(value).numeric if value else default
    except ValueError:
        return default


def _resolution_factor(value: str) -> float:
    if not value:
        return 1.0
    return RESOLUTION_FACTOR.get(value.strip().lower(), 1.0)


def _fps_factor(fps: int) -> float:
    """Относительная стоимость кадра: выше целевой FPS — дороже каждый кадр."""
    if fps <= 30:
        return 0.62
    if fps >= 144:
        return 1.7
    # Линейная интерполяция между 30 и 144 кадрами в секунду.
    return 0.62 + (fps - 30) * (1.7 - 0.62) / (144 - 30)


def _largest_impact(profile: ProjectProfile) -> float:
    return SCALE_FACTOR.get(
        Scale(profile.scale).value if profile.scale in {s.value for s in Scale} else "medium", 1.0
    )


def estimate_hardware(
    db: Session,
    profile: ProjectProfile,
    methods: list,
    similar_examples: int = 0,
) -> HardwareEstimateOut:
    """Рассчитать ориентировочную минимальную конфигурацию."""
    caveats: list[str] = []

    # --- Коэффициенты проекта --------------------------------------------
    res = _resolution_factor(profile.target_resolution)
    fps = _fps_factor(profile.target_fps)
    quality = QUALITY_FACTOR.get(profile.target_quality, 1.0)
    scale = _largest_impact(profile)
    obj = 0.85 + 0.35 * _level(profile.object_count_level)
    npc = 0.85 + 0.35 * _level(profile.npc_count_level)
    content = scale * obj * npc

    feature_gpu = 1.0 + sum(FEATURE_GPU_LOAD.get(f, 0.05) for f in profile.functions)
    feature_cpu = 1.0 + sum(FEATURE_CPU_LOAD.get(f, 0.05) for f in profile.functions)
    if profile.multiplayer:
        feature_cpu += 0.15 + 0.1 * min(1.0, profile.player_count / 32)

    # --- Учёт выбранных решений ------------------------------------------
    gpu_method = 1.0 + 0.06 * sum(m.impact_gpu for m in methods)
    cpu_method = 1.0 + 0.07 * sum(m.impact_cpu for m in methods)
    vram_method = 0.6 * sum(m.impact_vram for m in methods)
    ram_method = 0.5 * sum(m.impact_ram for m in methods)
    gpu_method = max(0.45, min(2.0, gpu_method))
    cpu_method = max(0.45, min(2.0, cpu_method))

    gpu_index = GPU_CALIBRATION * res * fps * quality * content * feature_gpu * gpu_method
    cpu_index = CPU_CALIBRATION * content * feature_cpu * cpu_method * (0.6 + 0.4 * fps)

    # --- Оценка памяти ----------------------------------------------------
    vram_gb = 1.4 + 2.0 * res + 2.4 * (quality - 0.7) + 1.2 * (content - 1.0) + vram_method
    vram_gb = max(1.5, round(vram_gb, 1))
    ram_gb = 4.0 + 4.0 * content + 2.0 * _level(profile.object_count_level) + ram_method
    ram_gb = max(4.0, round(ram_gb, 1))

    # --- Подбор референсной конфигурации ---------------------------------
    gpus = list(db.scalars(select(HardwareGPU).order_by(HardwareGPU.raster_score)))
    cpus = list(db.scalars(select(HardwareCPU).order_by(HardwareCPU.multi_thread_score)))

    required_rt = any(
        "Hardware Ray Tracing" in (m.requires_hw_features or []) for m in methods
    )
    required_hw = sorted({
        feature for m in methods for feature in (m.requires_hw_features or [])
    })

    def pick_gpu(pool: list[HardwareGPU], index: float) -> HardwareGPU | None:
        candidates = [g for g in pool if g.raster_score >= index]
        if required_rt:
            rt_pool = [
                g for g in candidates
                if any("ray tracing" in f.lower() or "rt cores" in f.lower() or "ray tracing" in f.lower()
                       for f in (g.hw_features or []))
            ]
            if not rt_pool:
                caveats.append(
                    "Выбранные решения требуют аппаратной трассировки лучей: видеокарта подбирается "
                    "с учётом этого требования, но стоимость RT-эффектов оценить заранее нельзя."
                )
            else:
                candidates = rt_pool
        if not candidates:
            return None
        # Из подходящих выбираем наиболее скромную по классу и производительности.
        return min(candidates, key=lambda g: (g.perf_class, g.raster_score))

    reference_gpu = pick_gpu(gpus, gpu_index)
    exceeds = False
    if reference_gpu is None:
        exceeds = True
        reference_gpu = max(gpus, key=lambda g: g.raster_score) if gpus else None
        caveats.append(
            "Требуемая производительность превышает возможности самого быстрого оборудования в базе: "
            "необходимо снизить целевые показатели или изменить набор решений."
        )

    def pick_cpu(pool: list[HardwareCPU], index: float) -> HardwareCPU | None:
        candidates = [c for c in pool if c.multi_thread_score >= index]
        if not candidates:
            return None
        return min(candidates, key=lambda c: (c.perf_class, c.multi_thread_score))

    reference_cpu = pick_cpu(cpus, cpu_index)
    if reference_cpu is None and cpus:
        reference_cpu = max(cpus, key=lambda c: c.multi_thread_score)
        caveats.append(
            "Требуемая производительность CPU превышает самую производительную запись базы."
        )

    # Альтернативы: ближайшие по производительности, но более современные.
    alt_gpus = sorted(
        [g for g in gpus if reference_gpu and g.perf_class == reference_gpu.perf_class and g.model != reference_gpu.model],
        key=lambda g: g.release_year, reverse=True,
    )[:4]
    alt_cpus = sorted(
        [c for c in cpus if reference_cpu and c.perf_class == reference_cpu.perf_class and c.model != reference_cpu.model],
        key=lambda c: c.release_year, reverse=True,
    )[:4]

    # --- Уверенность оценки ---------------------------------------------
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

    return HardwareEstimateOut(
        required_gpu_index=round(gpu_index, 4),
        required_cpu_index=round(cpu_index, 4),
        estimated_vram_gb=float(vram_gb),
        estimated_ram_gb=float(ram_gb),
        gpu_class=reference_gpu.perf_class if reference_gpu else 5,
        cpu_class=reference_cpu.perf_class if reference_cpu else 5,
        reference_gpu=serializers.gpu_out(reference_gpu) if reference_gpu else None,
        reference_cpu=serializers.cpu_out(reference_cpu) if reference_cpu else None,
        alternative_gpus=[serializers.gpu_out(g) for g in alt_gpus],
        alternative_cpus=[serializers.cpu_out(c) for c in alt_cpus],
        confidence=confidence,
        confidence_label=label,
        caveats=caveats,
        required_hw_features=required_hw,
        exceeds_catalog=exceeds,
    )
