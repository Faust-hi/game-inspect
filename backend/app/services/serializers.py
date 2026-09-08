"""Преобразование ORM-объектов в выходные Pydantic-схемы.

Модуль выделен отдельно, чтобы исключить циклические импорты между
слоями API и сервисов: и маршруты каталогов, и алгоритмы расчёта
используют одни и те же функции преобразования.
"""
from __future__ import annotations

from sqlalchemy.orm import Session
from .. import repositories
from ..models.entities import Method
from ..models.enums import CalcMode, DevStage, EffectScope, LateCost, SolutionLevel
from ..schemas.catalog import MethodOut

from ..models.entities import Engine, EngineTool, GameExample, HardwareCPU, HardwareGPU, MethodEngineLink
from ..models.enums import RelationType
from ..schemas.catalog import GameExampleOut, HardwareCPUOut, HardwareGPUOut, MethodEngineLinkOut


def label_of(enum_cls, value: str, default: str = "") -> str:
    """Человекочитаемая метка значения перечисления."""
    try:
        return enum_cls(value).label
    except ValueError:
        return default


def link_out(db: Session, link: MethodEngineLink) -> MethodEngineLinkOut:
    """Связь метода с инструментом движка в публичном представлении."""
    tool: EngineTool | None = db.get(EngineTool, link.tool_id)
    engine: Engine | None = db.get(Engine, tool.engine_id) if tool else None
    try:
        label = RelationType(link.relation_type).label
    except ValueError:
        label = link.relation_type
    return MethodEngineLinkOut(
        engine_code=engine.code if engine else "",
        engine_name=engine.name if engine else "",
        tool_code=tool.code if tool else "",
        tool_name=tool.name if tool else "",
        relation_type=link.relation_type,
        relation_label=label,
        note=link.note,
        docs_url=tool.docs_url if tool else "",
    )


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


def method_to_out(
    db: Session, m: Method, with_links: bool = True, used_in: list[str] | None = None,
) -> MethodOut:
    # Для административного раздела связи берутся напрямую, для публичного —
    # только опубликованные: черновик связи не должен появляться в карточке.
    links = m.engine_links if with_links else []
    return MethodOut(
        code=m.code, name=m.name, kind=m.kind,
        function_code=m.function.code if m.function else None,
        summary=m.summary, description=m.description, problem=m.problem,
        pros=m.pros or [], cons=m.cons or [], limitations=m.limitations or [],
        level=m.level, level_label=label_of(SolutionLevel, m.level),
        recommended_stage=m.recommended_stage,
        recommended_stage_label=label_of(DevStage, m.recommended_stage),
        late_cost=m.late_cost, late_cost_label=label_of(LateCost, m.late_cost),
        calc_mode=m.calc_mode, calc_mode_label=label_of(CalcMode, m.calc_mode),
        effect_scope=m.effect_scope, effect_scope_label=label_of(EffectScope, m.effect_scope),
        impact_cpu=m.impact_cpu, impact_gpu=m.impact_gpu, impact_ram=m.impact_ram,
        impact_vram=m.impact_vram, impact_disk=m.impact_disk, impact_network=m.impact_network,
        quality_impact=m.quality_impact, concept_impact=m.concept_impact,
        performance_gain=m.performance_gain, implementation_cost=m.implementation_cost,
        complexity=m.complexity, confidence=m.confidence,
        requires_prototype=m.requires_prototype,
        applicable_formats=m.applicable_formats or [],
        applicable_world_types=m.applicable_world_types or [],
        applicable_engines=m.applicable_engines or [],
        applicable_platforms=m.applicable_platforms or [],
        requires_features=m.requires_features or [],
        requires_hw_features=m.requires_hw_features or [],
        requires_conditions=m.requires_conditions or [],
        verification_method=m.verification_method,
        verification_tools=m.verification_tools or [],
        application_steps=m.application_steps or [],
        used_in_projects=used_in if used_in is not None else [],
        status=m.status, source_title=m.source_title, source_url=m.source_url,
        engine_links=[link_out(db, link) for link in links],
    )


def method_to_out_public(
    db: Session, m: Method, with_links: bool = True, used_in: list[str] | None = None,
) -> MethodOut:
    """Публичное представление: только опубликованные связи с движками."""
    links = repositories.method_links(db, m.id) if with_links else []
    out = method_to_out(db, m, with_links=False)
    out.engine_links = [link_out(db, link) for link in links]
    if used_in is not None:
        out.used_in_projects = used_in
    else:
        out.used_in_projects = sorted(e.title for e in repositories.examples(db) if m.code in (e.optimizations_used or []))
    return out


