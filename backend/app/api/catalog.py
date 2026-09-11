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
    ConflictOut, DependencyOut, EngineOut, EngineToolOut, EvidenceClaimOut,
    EvidenceSourceOut, EvidenceSummaryOut, GameCaseOut, GameFunctionOut,
    GraphChecksOut, MethodOut, StageGuidanceOut, TeamScenarioOut,
)
from ..services import evidence as evidence_service, serializers, stage_guidance
from ..services import graph as graph_service
from ..services.serializers import label_of as _label
from ..services.serializers import link_out

router = APIRouter(prefix="/catalog", tags=["Каталоги"])


# Shared serializers preserve these public aliases for administrative callers.
from ..services.serializers import method_to_out, method_to_out_public


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
    out = []
    for m in rows:
        if function and (not m.function or m.function.code != function):
            continue
        if kind and m.kind != kind:
            continue
        method = method_to_out_public(db, m)
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
                    tool_type=t.tool_type, docs_url=t.docs_url, min_version=t.min_version,
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


@router.get("/stage-guidance", response_model=StageGuidanceOut,
            summary="Предупреждения и предложения для стадии проекта")
def get_stage_guidance(
    stage: str = Query("prototype", description="Код стадии разработки"),
):
    """Что означает стадия: закрытые уровни решений, предупреждения, предложения.

    Маршрут не требует расчёта: экран стадии показывает ограничения сразу после
    выбора, а не после нажатия «рассчитать». Неизвестный код стадии сводится к
    прототипу — то же правило действует и в расчёте.
    """
    return stage_guidance.guidance_out(stage)


@router.get("/hardware", summary="Каталог оборудования")
def list_hardware(db: Session = Depends(get_db)):
    return {
        "cpu": [serializers.cpu_out(c) for c in repositories.hardware_cpu(db)],
        "gpu": [serializers.gpu_out(g) for g in repositories.hardware_gpu(db)],
    }


@router.get("/sources", response_model=list[EvidenceSourceOut], summary="Реестр опубликованных источников")
def list_sources(db: Session = Depends(get_db)):
    return [
        item for source in repositories.evidence_sources(db)
        if (item := evidence_service.source_to_out(source)) is not None
    ]


@router.get("/evidence", response_model=list[EvidenceClaimOut], summary="Атомарные утверждения и их provenance")
def list_evidence(
    entity: str | None = Query(None, description="Тип сущности, например method или hardware_gpu"),
    entity_code: str | None = Query(None, description="Код сущности"),
    db: Session = Depends(get_db),
):
    return [evidence_service.claim_to_out(db, claim)
            for claim in repositories.evidence_claims(db, entity=entity, entity_code=entity_code)]


@router.get("/evidence/{entity}/{code}", response_model=list[EvidenceClaimOut],
            summary="Доказательства сущности")
def list_entity_evidence(entity: str, code: str, db: Session = Depends(get_db)):
    """Вернуть claims ровно для одной сущности каталога.

    Алиас нужен для ссылок из карточек UI и отчёта. Фильтрация остаётся в
    репозитории, поэтому draft/review claims не становятся публичными.
    """
    return [evidence_service.claim_to_out(db, claim)
            for claim in repositories.evidence_claims(db, entity=entity, entity_code=code)]


@router.get("/evidence-summary", response_model=EvidenceSummaryOut, summary="Покрытие доказательной базы")
def evidence_summary(db: Session = Depends(get_db)):
    return evidence_service.summary(db)


@router.get("/cases", response_model=list[GameCaseOut], summary="Кейсы реальных игр и демо")
def list_cases(db: Session = Depends(get_db)):
    return evidence_service.cases_to_out(db, repositories.game_cases(db))


@router.get("/cases/{code}", response_model=GameCaseOut, summary="Кейс игры")
def get_case(code: str, db: Session = Depends(get_db)):
    case = repositories.game_case(db, code)
    if case is None:
        raise HTTPException(404, "Кейс не найден или не опубликован")
    return evidence_service.cases_to_out(db, [case])[0]


@router.get("/dependencies", response_model=list[DependencyOut], summary="Технологические зависимости")
def list_dependencies(db: Session = Depends(get_db)):
    return evidence_service.dependencies_to_out(db)


@router.get("/graph-checks", response_model=GraphChecksOut, summary="Проверки графа зависимостей")
def graph_checks(
    basket: list[str] = Query(default_factory=list, description="Коды методов в корзине решений"),
    engine: str | None = Query(default=None, description="Код выбранного движка"),
    engine_version: str | None = Query(default=None, description="Версия выбранного движка"),
    render_api: str | None = Query(default=None, description="Выбранный графический API"),
    db: Session = Depends(get_db),
):
    """Проверить граф зависимостей и вернуть находки вместе со счётчиками.

    Отсутствие находок не означает совместимость: непроверенные сочетания
    возвращаются отдельными записями со статусом `info`.
    """
    return graph_service.graph_checks(
        db,
        basket=basket,
        engine=engine,
        engine_version=engine_version,
        render_api=render_api,
    )


@router.get("/teams", response_model=list[TeamScenarioOut], summary="Сценарии состава команды")
def list_teams(db: Session = Depends(get_db)):
    return [
        TeamScenarioOut(
            code=item.code, name=item.name, description=item.description,
            team_size=item.team_size, role_capacity=item.role_capacity or {},
            parallel_tracks=item.parallel_tracks,
            communication_pct=item.communication_pct,
            unplanned_pct=item.unplanned_pct,
            specialist_capacity=item.specialist_capacity or {},
        )
        for item in repositories.team_scenarios(db)
    ]


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
