"""Расчёт рекомендаций, профиля нагрузки, похожих игр и аппаратной оценки."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import repositories
from ..database import get_db
from ..schemas.catalog import (
    BasketRequest, LoadProfileOut, RecommendationResult, SimilarGameOut,
)
from ..services import engines as engine_catalog, gower, hardware, recommender, serializers

router = APIRouter(prefix="", tags=["Расчёт"])


@router.post("/recommend", response_model=RecommendationResult, summary="Рассчитать рекомендации по профилю проекта")
def recommend(payload: BasketRequest, db: Session = Depends(get_db)):
    engine_catalog.require_known(db, payload.profile.engine)
    return recommender.build_recommendations(db, payload.profile, payload.basket or [])


@router.post("/load-profile", response_model=LoadProfileOut, summary="Пересчитать сводный профиль нагрузки корзины")
def load_profile(payload: BasketRequest, db: Session = Depends(get_db)):
    engine_catalog.require_known(db, payload.profile.engine)
    methods = repositories.methods_by_codes(db, payload.basket or [])
    return recommender.aggregate_load(methods, payload.profile, relations=repositories.conflicts(db))


@router.post("/similar-games", response_model=list[SimilarGameOut], summary="Поиск похожих игр (расстояние Гауэра)")
def similar_games(payload: BasketRequest, db: Session = Depends(get_db)):
    engine_catalog.require_known(db, payload.profile.engine)
    examples = repositories.examples(db)
    return [
        SimilarGameOut(
            example=serializers.example_out(ex),
            similarity=sim,
            matching_optimizations=match,
        )
        # Корзина передаётся в поиск: совпадения ищутся по выбранным решениям,
        # а не по функциям профиля — это разные множества кодов.
        for ex, sim, match in gower.find_similar(
            payload.profile, examples, top_n=6, basket=payload.basket or []
        )
    ]


@router.post("/hardware-estimate", summary="Оценка референсного минимального класса оборудования")
def hardware_estimate(payload: BasketRequest, db: Session = Depends(get_db)):
    engine_catalog.require_known(db, payload.profile.engine)
    methods = repositories.methods_by_codes(db, payload.basket or [])
    examples = repositories.examples(db)
    similar = gower.find_similar(payload.profile, examples, top_n=5, basket=payload.basket or [])
    return hardware.estimate_hardware(db, payload.profile, methods, similar_examples=len(similar))
