"""Публичные каталоги базы знаний."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from ..database import get_db
from ..models.entities import (
    Conflict, Engine, EngineTool, GameExample, GameFunction, HardwareCPU, HardwareGPU, Method,
)
from ..models.enums import (
    CalcMode, ConflictType, DevStage, GameFormat, LateCost, Level3, MethodKind,
    Platform, Priority, RelationType, Scale, SolutionLevel, Status, WorldType,
)
from ..schemas.catalog import (
    ConflictOut, EngineOut, EngineToolOut, GameExampleOut, GameFunctionOut, HardwareCPUOut,
    HardwareGPUOut, MethodOut,
)
from ..services import serializers
from ..services.recommender import link_out, _label

router = APIRouter(prefix="/catalog", tags=["Каталоги"])


def method_to_out(db: Session, m: Method, with_links: bool = True) -> MethodOut:
    return MethodOut(
        code=m.code, name=m.name, kind=m.kind,
        function_code=m.function.code if m.function else None,
        summary=m.summary, description=m.description, problem=m.problem,
        pros=m.pros or [], cons=m.cons or [], limitations=m.limitations or [],
        level=m.level, level_label=_label(SolutionLevel, m.level),
        recommended_stage=m.recommended_stage,
        recommended_stage_label=_label(DevStage, m.recommended_stage),
        late_cost=m.late_cost, late_cost_label=_label(LateCost, m.late_cost),
        calc_mode=m.calc_mode, calc_mode_label=_label(CalcMode, m.calc_mode),
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
        status=m.status, source_title=m.source_title, source_url=m.source_url,
        engine_links=[link_out(db, l) for l in m.engine_links] if with_links else [],
    )


@router.get("/functions", response_model=list[GameFunctionOut], summary="Каталог игровых функций")
def list_functions(db: Session = Depends(get_db)):
    rows = db.scalars(
        select(GameFunction).where(GameFunction.status == "published").order_by(GameFunction.sort_order)
    ).all()
    return [
        GameFunctionOut(
            code=f.code, name=f.name, description=f.description, category=f.category,
            formats=f.formats or [], typical_world_types=f.typical_world_types or [],
            sort_order=f.sort_order, source_title=f.source_title, source_url=f.source_url,
        )
        for f in rows
    ]


@router.get("/methods", response_model=list[MethodOut], summary="Каталог методов и вариантов реализации")
def list_methods(
    function: str | None = Query(None, description="Код игровой функции"),
    kind: str | None = Query(None, description="implementation | optimization"),
    engine: str | None = Query(None, description="Код движка для фильтрации по наличию аналога"),
    db: Session = Depends(get_db),
):
    stmt = select(Method).options(selectinload(Method.engine_links)).where(Method.status == "published")
    rows = list(db.scalars(stmt).all())
    out = []
    for m in rows:
        if function and (not m.function or m.function.code != function):
            continue
        if kind and m.kind != kind:
            continue
        if engine:
            codes = {db.get(EngineTool, l.tool_id).engine.code for l in m.engine_links if db.get(EngineTool, l.tool_id)}
            if engine not in codes:
                continue
        out.append(method_to_out(db, m))
    out.sort(key=lambda x: x.name)
    return out


@router.get("/methods/{code}", response_model=MethodOut, summary="Карточка метода")
def get_method(code: str, db: Session = Depends(get_db)):
    m = db.scalar(select(Method).where(Method.code == code))
    if not m:
        raise HTTPException(404, "Метод не найден")
    return method_to_out(db, m)


@router.get("/engines", response_model=list[EngineOut], summary="Каталог игровых движков и их инструментов")
def list_engines(db: Session = Depends(get_db)):
    rows = db.scalars(select(Engine).options(selectinload(Engine.tools))).all()
    return [
        EngineOut(
            code=e.code, name=e.name, vendor=e.vendor, versions=e.versions or [],
            supported_formats=e.supported_formats or [], notes=e.notes, docs_url=e.docs_url,
            tools=[
                EngineToolOut(
                    code=t.code, name=t.name, subsystem=t.subsystem, description=t.description,
                    tool_type=t.tool_type, docs_url=t.docs_url,
                )
                for t in sorted(e.tools, key=lambda x: (x.subsystem, x.name))
            ],
        )
        for e in rows
    ]


@router.get("/conflicts", response_model=list[ConflictOut], summary="Конфликты, зависимости и усиления")
def list_conflicts(db: Session = Depends(get_db)):
    rows = db.scalars(select(Conflict)).all()
    return [
        ConflictOut(
            a_code=c.a_code, b_code=c.b_code, conflict_type=c.conflict_type,
            conflict_label=_label(ConflictType, c.conflict_type), severity=c.severity,
            description=c.description, resolution=c.resolution, source_url=c.source_url,
        )
        for c in rows
    ]


@router.get("/examples", response_model=list[GameExampleOut], summary="Подтверждённые примеры игр")
def list_examples(db: Session = Depends(get_db)):
    rows = db.scalars(select(GameExample).where(GameExample.status == "published").order_by(GameExample.title)).all()
    return [serializers.example_out(e) for e in rows]


@router.get("/hardware", summary="Каталог оборудования")
def list_hardware(db: Session = Depends(get_db)):
    cpus = db.scalars(select(HardwareCPU).order_by(HardwareCPU.multi_thread_score.desc())).all()
    gpus = db.scalars(select(HardwareGPU).order_by(HardwareGPU.raster_score.desc())).all()
    return {
        "cpu": [serializers.cpu_out(c) for c in cpus],
        "gpu": [serializers.gpu_out(g) for g in gpus],
    }


# ---------------------------------------------------------------------------
# Справочники для пользовательского интерфейса
# ---------------------------------------------------------------------------
enums_router = APIRouter(prefix="/meta", tags=["Справочники"])


def _enum_options(enum_cls) -> list[dict]:
    return [{"value": item.value, "label": item.label} for item in enum_cls]


@enums_router.get("/enums", summary="Все перечисления для построения анкеты")
def get_enums():
    return {
        "formats": _enum_options(GameFormat),
        "world_types": _enum_options(WorldType),
        "scales": _enum_options(Scale),
        "stages": _enum_options(DevStage),
        "platforms": _enum_options(Platform),
        "levels": _enum_options(Level3),
        "priorities": _enum_options(Priority),
        "solution_levels": _enum_options(SolutionLevel),
        "late_costs": _enum_options(LateCost),
        "calc_modes": _enum_options(CalcMode),
        "relation_types": _enum_options(RelationType),
        "conflict_types": _enum_options(ConflictType),
        "statuses": _enum_options(Status),
        "method_kinds": _enum_options(MethodKind),
    }
