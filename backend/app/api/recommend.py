"""Расчёт рекомендаций, профиля нагрузки и аппаратной оценки."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import repositories
from ..database import get_db
from ..schemas.catalog import BasketRequest, LoadProfileOut, RecommendationResult, RecommendationRequest
from ..services import engines as engine_catalog, hardware, recommender

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
