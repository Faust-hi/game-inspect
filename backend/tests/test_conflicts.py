"""Конфликты и зависимости (офлайн).

Дефекты: несовместимые решения без предупреждения, пропущенная
обязательная зависимость, исчезновение конфликта между backend
и интерфейсом (ответ обязан нести связи в явном виде).
"""
from __future__ import annotations


PROFILE = {
    "name": "Конфликты",
    "format": "3D",
    "world_type": "open_world",
    "scale": "large",
    "stage": "prototype",
    "engine": "unreal",
    "platforms": ["pc_windows"],
    "functions": ["open_world_streaming", "crowd_simulation"],
    "target_resolution": "1440p",
    "target_quality": "high",
    "target_fps": 60,
    "npc_count_level": "high",
}


def test_basket_conflict_is_visible(client, profile=None):
    """Пара из каталога конфликтов видна в корзине (не теряется по пути)."""
    data_profile = dict(PROFILE)
    conflicts = client.get("/api/catalog/conflicts").json()
    pair = next(
        item for item in conflicts
        if item["conflict_type"] in ("hard_conflict", "risk", "alternative")
    )
    data = client.post("/api/recommend", json={
        "profile": data_profile,
        "basket": [pair["a_code"], pair["b_code"]],
    }).json()
    codes = {(item["a_code"], item["b_code"]) for item in data["basket_conflicts"]}
    assert (
        (pair["a_code"], pair["b_code"]) in codes
        or (pair["b_code"], pair["a_code"]) in codes
    )


def test_unmet_dependency_is_reported(client, monkeypatch):
    """Незакрытая обязательная зависимость — явный конфликт корзины.

    Дефект: решение, которое не работает без второго, советуют в одиночку.
    В каталоге обязательных зависимостей нет, поэтому механизм проверяется
    на синтетической записи: молчаливая потеря типа связи недопустима.
    """
    from app import repositories
    from app.models.entities import Conflict
    from app.services import recommender

    real = repositories.conflicts
    synthetic = Conflict(
        a_code="skeletal_2d_deform",
        b_code="sprite_atlas_batching",
        conflict_type="dependency",
        severity=2,
        description="Проверочная обязательная зависимость.",
        resolution="Добавить второе решение в набор.",
    )
    monkeypatch.setattr(
        recommender.repositories, "conflicts",
        lambda db: list(real(db)) + [synthetic],
    )
    data = client.post("/api/recommend", json={
        "profile": PROFILE, "basket": ["skeletal_2d_deform"],
    }).json()
    assert any(
        item["conflict_type"] == "unmet_dependency"
        for item in data["basket_conflicts"]
    )


def test_complement_is_reported_as_synergy(client):
    """Дополняющая пара видна как синергия (усиление не теряется)."""
    conflicts = client.get("/api/catalog/conflicts").json()
    pair = next(item for item in conflicts if item["conflict_type"] == "complement")
    data = client.post("/api/recommend", json={
        "profile": PROFILE, "basket": [pair["a_code"], pair["b_code"]],
    }).json()
    assert data["basket_synergies"]


def test_hard_conflict_blocks_stacking(db):
    """Жёсткая несовместимость: эффекты не складываются, нагрузка нейтральна.

    Дефект: две взаимоисключающие реализации одновременно удешевляют расчёт.
    """
    from sqlalchemy import select

    from app.models.entities import Conflict, Method
    from app.schemas.catalog import ProjectProfile
    from app.services.recommender import aggregate_load
    from app.services.rules import assess_selected_methods

    methods = list(db.scalars(select(Method).where(Method.code.in_([
        "world_partition_streaming", "hierarchical_lod",
    ]))))
    assert len(methods) == 2
    relation = Conflict(
        a_code=methods[0].code, b_code=methods[1].code,
        conflict_type="hard_conflict", description="Альтернативные реализации",
    )
    profile = ProjectProfile(functions=["open_world_streaming"])
    accepted, _ = assess_selected_methods(methods, profile, [relation])
    assert accepted == []
    load = aggregate_load(methods, profile, relations=[relation])
    assert load.cpu == load.gpu == 50
