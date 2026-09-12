"""Расчёт рекомендаций, профиля нагрузки и аппаратной оценки."""
from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from .. import repositories
from ..database import get_db
from ..schemas.catalog import (
    BasketRequest, LoadProfileOut, RecommendationResult, RecommendationRequest,
    ProjectProfile, ReportDataOut,
)
from ..services import evidence, engines as engine_catalog, hardware, method_dependencies, recommender

router = APIRouter(prefix="", tags=["Расчёт"])


def _basket_methods(db: Session, codes: list[str]):
    """Методы корзины вместе с достроенными обязательными зависимостями.

    Возвращает `(методы, пояснения)`. Достройка нужна и на этих маршрутах:
    иначе «Профиль нагрузки» и «Оценка железа» для той же корзины считали бы
    другой набор, чем `/recommend`, — ровно то расхождение, из-за
    которого нагрузка и рекомендации расходились.
    """
    closure = method_dependencies.mandatory_closure(db, codes)
    return repositories.methods_by_codes(db, closure.codes), closure.notes


@router.post("/recommend", response_model=RecommendationResult, summary="Рассчитать рекомендации по профилю проекта")
def recommend(payload: RecommendationRequest, db: Session = Depends(get_db)):
    engine_catalog.require_known(db, payload.profile.engine)
    return recommender.build_recommendations(db, payload.profile, payload.basket or [], payload.baseline)


@router.post("/load-profile", response_model=LoadProfileOut, summary="Пересчитать сводный профиль нагрузки корзины")
def load_profile(payload: BasketRequest, db: Session = Depends(get_db)):
    engine_catalog.require_known(db, payload.profile.engine)
    methods, closure_notes = _basket_methods(db, payload.basket or [])
    estimate = hardware.estimate_hardware(db, payload.profile, methods)
    load = recommender.aggregate_load(
        methods, payload.profile, relations=repositories.conflicts(db), estimate=estimate,
    )
    load.notes = list(closure_notes) + list(load.notes)
    return load


@router.post("/hardware-estimate", summary="Оценка референсного минимального класса оборудования")
def hardware_estimate(payload: BasketRequest, db: Session = Depends(get_db)):
    engine_catalog.require_known(db, payload.profile.engine)
    methods, _closure_notes = _basket_methods(db, payload.basket or [])
    return hardware.estimate_hardware(db, payload.profile, methods)


def _report_data(
    db: Session,
    profile: ProjectProfile,
    basket: list[str],
    baseline=None,
):
    """Собрать единый снимок, используемый UI и Markdown/PDF экспортом."""
    engine_catalog.require_known(db, profile.engine)
    recommendation = recommender.build_recommendations(
        db, profile, basket, baseline,
    )
    return ReportDataOut(
        recommendation=recommendation,
        evidence_summary=evidence.summary(db),
        sources=[source for source in (
            evidence.source_to_out(item) for item in repositories.evidence_sources(db)
        ) if source is not None],
        dependencies=evidence.dependencies_to_out(db),
    )


@router.post("/report-data", response_model=ReportDataOut, summary="Снимок расчёта для отчёта")
def report_data(payload: RecommendationRequest, db: Session = Depends(get_db)):
    return _report_data(
        db, payload.profile, payload.basket or [], payload.baseline,
    )


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
