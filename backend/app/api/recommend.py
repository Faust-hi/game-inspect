"""Расчёт рекомендаций, профиля нагрузки и аппаратной оценки."""
from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from .. import repositories
from ..database import get_db
from ..schemas.catalog import (
    BasketRequest, LoadProfileOut, RecommendationResult, RecommendationRequest,
    ProjectProfile, ReportDataOut, ScheduleOut, ScheduleRequest,
)
from ..services import evidence, engines as engine_catalog, hardware, planning, recommender

router = APIRouter(prefix="", tags=["Расчёт"])


@router.post("/recommend", response_model=RecommendationResult, summary="Рассчитать рекомендации по профилю проекта")
def recommend(payload: RecommendationRequest, db: Session = Depends(get_db)):
    engine_catalog.require_known(db, payload.profile.engine)
    return recommender.build_recommendations(db, payload.profile, payload.basket or [], payload.baseline)


@router.post("/load-profile", response_model=LoadProfileOut, summary="Пересчитать сводный профиль нагрузки корзины")
def load_profile(payload: BasketRequest, db: Session = Depends(get_db)):
    engine_catalog.require_known(db, payload.profile.engine)
    methods = repositories.methods_by_codes(db, payload.basket or [])
    estimate = hardware.estimate_hardware(db, payload.profile, methods)
    return recommender.aggregate_load(
        methods, payload.profile, relations=repositories.conflicts(db), estimate=estimate,
    )


@router.post("/hardware-estimate", summary="Оценка референсного минимального класса оборудования")
def hardware_estimate(payload: BasketRequest, db: Session = Depends(get_db)):
    engine_catalog.require_known(db, payload.profile.engine)
    methods = repositories.methods_by_codes(db, payload.basket or [])
    return hardware.estimate_hardware(db, payload.profile, methods)


@router.post("/schedule", response_model=ScheduleOut, summary="Сценарный план трудоёмкости и critical path")
def schedule(payload: ScheduleRequest, db: Session = Depends(get_db)):
    engine_catalog.require_known(db, payload.profile.engine)
    return planning.schedule(
        db, payload.profile, payload.basket or [], payload.team,
        payload.include_dependencies,
    )


def _report_data(db: Session, profile: ProjectProfile, basket: list[str], baseline=None):
    """Собрать единый снимок, используемый UI и Markdown/PDF экспортом."""
    engine_catalog.require_known(db, profile.engine)
    recommendation = recommender.build_recommendations(
        db, profile, basket, baseline,
    )
    method_codes = recommendation.accounted_method_codes or list(basket)
    return ReportDataOut(
        recommendation=recommendation,
        evidence_summary=evidence.summary(db),
        sources=[source for source in (
            evidence.source_to_out(item) for item in repositories.evidence_sources(db)
        ) if source is not None],
        cases=evidence.cases_for_methods(db, method_codes),
        dependencies=evidence.dependencies_to_out(db),
        schedule=planning.schedule(
            db, profile, basket, "small_2_5", True,
        ),
    )


@router.post("/report-data", response_model=ReportDataOut, summary="Снимок расчёта для отчёта")
def report_data(payload: RecommendationRequest, db: Session = Depends(get_db)):
    return _report_data(db, payload.profile, payload.basket or [], payload.baseline)


@router.get("/report-data", response_model=ReportDataOut,
            summary="Снимок расчёта для отчёта по query-профилю")
def report_data_get(
    profile: ProjectProfile = Depends(),
    basket: list[str] = Query(default=[], description="Коды методов; параметр можно повторять"),
    db: Session = Depends(get_db),
):
    """GET-форма для ссылок и простого экспорта без JSON body.

    Сложные сценарии и baseline используют POST; GET сохраняет валидные
    значения профиля по умолчанию и принимает коды корзины повторяемым query
    параметром.
    """
    return _report_data(db, profile, basket)
