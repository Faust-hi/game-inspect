"""Расчёт рекомендаций, профиля нагрузки, похожих игр и аппаратной оценки."""
from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..config import settings
from ..database import get_db
from ..models.entities import GameExample, Method
from ..schemas.catalog import (
    BasketRequest, LoadProfileOut, RecommendationResult, SimilarGameOut,
)
from ..services import gower, hardware, recommender, serializers
from ..services.security import enforce_rate_limit

router = APIRouter(prefix="", tags=["Расчёт"])


def _limit(request: Request) -> None:
    """Ограничение частоты расчётных запросов: они самые затратные по CPU."""
    enforce_rate_limit(request, settings.RATE_LIMIT_CALC_PER_MINUTE, "calc")


@router.post("/recommend", response_model=RecommendationResult, summary="Рассчитать рекомендации по профилю проекта")
def recommend(payload: BasketRequest, request: Request, db: Session = Depends(get_db)):
    _limit(request)
    return recommender.build_recommendations(db, payload.profile, payload.basket or [])


@router.post("/load-profile", response_model=LoadProfileOut, summary="Пересчитать сводный профиль нагрузки корзины")
def load_profile(payload: BasketRequest, request: Request, db: Session = Depends(get_db)):
    _limit(request)
    methods = list(db.scalars(select(Method).where(Method.code.in_(payload.basket or []))).all())
    return recommender.aggregate_load(methods, payload.profile)


@router.post("/similar-games", response_model=list[SimilarGameOut], summary="Поиск похожих игр (расстояние Гауэра)")
def similar_games(payload: BasketRequest, request: Request, db: Session = Depends(get_db)):
    _limit(request)
    examples = list(db.scalars(select(GameExample).where(GameExample.status == "published")).all())
    return [
        SimilarGameOut(
            example=serializers.example_out(ex),
            similarity=sim,
            matching_optimizations=match,
        )
        for ex, sim, match in gower.find_similar(payload.profile, examples, top_n=6)
    ]


@router.post("/hardware-estimate", summary="Оценка референсного минимального класса оборудования")
def hardware_estimate(payload: BasketRequest, request: Request, db: Session = Depends(get_db)):
    _limit(request)
    methods = list(db.scalars(select(Method).where(Method.code.in_(payload.basket or []))).all())
    examples = list(db.scalars(select(GameExample).where(GameExample.status == "published")).all())
    similar = gower.find_similar(payload.profile, examples, top_n=5)
    return hardware.estimate_hardware(db, payload.profile, methods, similar_examples=len(similar))
