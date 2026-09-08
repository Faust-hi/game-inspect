"""Публичные каталоги базы знаний.

Все выборки идут через слой `repositories`, который возвращает только
опубликованный снимок. Ни один публичный маршрут не обращается к ORM напрямую:
иначе достаточно забыть условие по статусу в одном месте, и черновик станет
доступен всем пользователям.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from .. import repositories
from ..database import get_db
from ..models.entities import Method
from ..models.enums import (
    CalcMode, ConflictType, DevStage, EffectScope, GameFormat, LateCost, Level3,
    MemoryModel, MethodKind, NetworkTopology, Platform, Priority, RelationType,
    RenderAPI, Scale, SolutionLevel, Status, StorageType, UpscalingMethod, WorldType,
)
from ..schemas.catalog import (
    ConflictOut, EngineOut, EngineToolOut, GameExampleOut, GameFunctionOut,
    MethodOut,
)
from ..services import serializers
from ..services.serializers import label_of as _label
from ..services.serializers import link_out

router = APIRouter(prefix="/catalog", tags=["Каталоги"])


def _used_in_projects(db: Session, method_code: str) -> list[str]:
    """Проекты каталога, где решение применено.

    Производное поле без новой таблицы: связь «метод — проект» уже лежит в
    `GameExample.optimizations_used` кодами методов. Считается только по
    опубликованному срезу, чтобы черновики Трека 2 не попадали в карточку.
    """
    titles = []
    for example in repositories.examples(db):
        if method_code in (example.optimizations_used or []):
            titles.append(example.title)
    return sorted(titles)


def used_in_map(db: Session) -> dict[str, list[str]]:
    """Карта «код метода — проекты-применители» одним проходом по примерам."""
    mapping: dict[str, list[str]] = {}
    for example in repositories.examples(db):
        for code in example.optimizations_used or []:
            mapping.setdefault(code, []).append(example.title)
    for titles in mapping.values():
        titles.sort()
    return mapping


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
        level=m.level, level_label=_label(SolutionLevel, m.level),
        recommended_stage=m.recommended_stage,
        recommended_stage_label=_label(DevStage, m.recommended_stage),
        late_cost=m.late_cost, late_cost_label=_label(LateCost, m.late_cost),
        calc_mode=m.calc_mode, calc_mode_label=_label(CalcMode, m.calc_mode),
        effect_scope=m.effect_scope, effect_scope_label=_label(EffectScope, m.effect_scope),
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
        out.used_in_projects = _used_in_projects(db, m.code)
    return out


@router.get("/functions", response_model=list[GameFunctionOut], summary="Каталог игровых функций")
def list_functions(db: Session = Depends(get_db)):
    rows = repositories.functions(db)
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
    rows = repositories.methods(db)
    # Один проход по примерам на весь список вместо запроса на каждый метод.
    mapping = used_in_map(db)
    out = []
    for m in rows:
        if function and (not m.function or m.function.code != function):
            continue
        if kind and m.kind != kind:
            continue
        method = method_to_out_public(db, m, used_in=mapping.get(m.code, []))
        if engine and not any(link.engine_code == engine for link in method.engine_links):
            continue
        out.append(method)
    out.sort(key=lambda x: x.name)
    return out


@router.get("/methods/{code}", response_model=MethodOut, summary="Карточка метода")
def get_method(code: str, db: Session = Depends(get_db)):
    """Черновик и запись на проверке недоступны: для публичного каталога их нет."""
    m = repositories.method(db, code)
    if not m:
        raise HTTPException(404, "Метод не найден или не опубликован")
    return method_to_out_public(db, m)


@router.get("/engines", response_model=list[EngineOut], summary="Каталог игровых движков и их инструментов")
def list_engines(db: Session = Depends(get_db)):
    rows = repositories.engines(db)
    published_tools = {t.code for t in repositories.engine_tools(db)}
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
                if t.code in published_tools
            ],
        )
        for e in rows
    ]


@router.get("/conflicts", response_model=list[ConflictOut], summary="Конфликты, зависимости и усиления")
def list_conflicts(db: Session = Depends(get_db)):
    rows = repositories.conflicts(db)
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
    return [serializers.example_out(e) for e in repositories.examples(db)]


@router.get("/hardware", summary="Каталог оборудования")
def list_hardware(db: Session = Depends(get_db)):
    return {
        "cpu": [serializers.cpu_out(c) for c in repositories.hardware_cpu(db)],
        "gpu": [serializers.gpu_out(g) for g in repositories.hardware_gpu(db)],
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
        "render_apis": _enum_options(RenderAPI),
        "storage_types": _enum_options(StorageType),
        "memory_models": _enum_options(MemoryModel),
        "upscalers": _enum_options(UpscalingMethod),
        "network_topologies": _enum_options(NetworkTopology),
        "priorities": _enum_options(Priority),
        "solution_levels": _enum_options(SolutionLevel),
        "late_costs": _enum_options(LateCost),
        "calc_modes": _enum_options(CalcMode),
        "effect_scopes": _enum_options(EffectScope),
        "relation_types": _enum_options(RelationType),
        "conflict_types": _enum_options(ConflictType),
        "statuses": _enum_options(Status),
        "method_kinds": _enum_options(MethodKind),
    }
