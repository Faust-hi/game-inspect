"""Преобразование ORM-объектов в выходные Pydantic-схемы.

Модуль выделен отдельно, чтобы исключить циклические импорты между
слоями API и сервисов: и маршруты каталогов, и алгоритмы расчёта
используют одни и те же функции преобразования.
"""
from __future__ import annotations

from ..models.entities import GameExample, HardwareCPU, HardwareGPU
from ..schemas.catalog import GameExampleOut, HardwareCPUOut, HardwareGPUOut


def example_out(example: GameExample) -> GameExampleOut:
    return GameExampleOut(
        title=example.title,
        year=example.year,
        developer=example.developer,
        engine=example.engine,
        format=example.format,
        world_type=example.world_type,
        scale=example.scale,
        platforms=example.platforms or [],
        target_resolution=example.target_resolution,
        target_fps=example.target_fps,
        object_count_level=example.object_count_level,
        npc_count_level=example.npc_count_level,
        multiplayer=bool(example.multiplayer),
        player_count=example.player_count,
        features=example.features or [],
        optimizations_used=example.optimizations_used or [],
        summary=example.summary,
        performance_outcome=example.performance_outcome,
        source_title=example.source_title,
        source_url=example.source_url,
        verified_by=example.verified_by,
    )


def cpu_out(cpu: HardwareCPU) -> HardwareCPUOut:
    return HardwareCPUOut(
        model=cpu.model,
        vendor=cpu.vendor,
        generation=cpu.generation,
        architecture=cpu.architecture,
        release_year=cpu.release_year,
        cores=cpu.cores,
        threads=cpu.threads,
        single_thread_score=cpu.single_thread_score,
        multi_thread_score=cpu.multi_thread_score,
        perf_class=cpu.perf_class,
        memory_support=cpu.memory_support,
        tdp_w=cpu.tdp_w,
        notes=cpu.notes,
        source_title=cpu.source_title,
        source_url=cpu.source_url,
    )


def gpu_out(gpu: HardwareGPU) -> HardwareGPUOut:
    return HardwareGPUOut(
        model=gpu.model,
        vendor=gpu.vendor,
        generation=gpu.generation,
        architecture=gpu.architecture,
        release_year=gpu.release_year,
        vram_gb=gpu.vram_gb,
        vram_type=gpu.vram_type,
        memory_bandwidth_gbs=gpu.memory_bandwidth_gbs,
        api_support=gpu.api_support or [],
        hw_features=gpu.hw_features or [],
        raster_score=gpu.raster_score,
        rt_score=gpu.rt_score,
        perf_class=gpu.perf_class,
        tdp_w=gpu.tdp_w,
        notes=gpu.notes,
        source_title=gpu.source_title,
        source_url=gpu.source_url,
    )
