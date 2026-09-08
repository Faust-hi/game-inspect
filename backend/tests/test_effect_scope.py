"""Область эффекта решения: сервер и разработка не удешевляют компьютер игрока.

Оценка оборудования отвечает на вопрос о машине игрока. Пока область эффекта не
задавалась явно, головой сервер без графики снижал требования к GPU клиента, а
быстрый пересчёт лайтмапов на машине художника — к его процессору. Проверки
ниже фиксируют не только сам расчёт, но и то, что такие решения не исчезают
молча: они перечислены в ответе с указанием причины.
"""
from __future__ import annotations

import pytest
from sqlalchemy import select

from app.models.entities import Method
from app.schemas.catalog import ProjectProfile
from app.seed.corrections import correct_effect_scopes
from app.services.hardware import estimate_hardware
from app.services.recommender import aggregate_load

SERVER_METHOD = "headless_dedicated_server"
DEVELOPMENT_METHOD = "gpu_lightmap_baking"
CLIENT_METHOD = "world_partition_streaming"


def _method(db, code: str) -> Method:
    return db.scalar(select(Method).where(Method.code == code))


def test_seed_marks_known_non_client_scopes(db):
    """Каталог содержит явную область эффекта для записей, описывающих её прямо."""
    assert _method(db, SERVER_METHOD).effect_scope == "server"
    assert _method(db, DEVELOPMENT_METHOD).effect_scope == "development"
    assert _method(db, "tickrate_budgeting").effect_scope == "server"
    assert _method(db, CLIENT_METHOD).effect_scope == "client"


def test_server_effect_does_not_reduce_client_gpu(db):
    """Выделенный сервер без графики не облегчает рендер на клиенте."""
    method = _method(db, SERVER_METHOD)
    assert method.impact_gpu < 0, "запись должна описывать экономию GPU"
    profile = ProjectProfile(functions=["multiplayer_netcode"], multiplayer=True)

    baseline = estimate_hardware(db, profile, [])
    selected = estimate_hardware(db, profile, [method])

    assert selected.required_gpu_index == baseline.required_gpu_index
    assert selected.required_cpu_index == baseline.required_cpu_index
    assert [item.code for item in selected.non_client_methods] == [SERVER_METHOD]
    assert "серверной части" in selected.non_client_methods[0].reason
    assert any(SERVER_METHOD in caveat or "Выделенный сервер" in caveat
               for caveat in selected.caveats)


def test_development_effect_does_not_reduce_client_cpu(db):
    """Ускорение производственной итерации не ускоряет кадр у игрока."""
    method = _method(db, DEVELOPMENT_METHOD)
    profile = ProjectProfile(functions=["baked_lighting"])

    baseline = estimate_hardware(db, profile, [])
    selected = estimate_hardware(db, profile, [method])

    assert selected.required_cpu_index == baseline.required_cpu_index
    assert selected.required_gpu_index == baseline.required_gpu_index
    assert [item.code for item in selected.non_client_methods] == [DEVELOPMENT_METHOD]
    assert "процессу разработки" in selected.non_client_methods[0].reason


def test_client_effect_is_still_counted(db):
    """Разделение по области не должно отключать учёт клиентских решений."""
    method = _method(db, CLIENT_METHOD)
    profile = ProjectProfile(functions=["open_world_streaming"], world_type="open_world")

    baseline = estimate_hardware(db, profile, [])
    selected = estimate_hardware(db, profile, [method])

    assert selected.required_cpu_index != baseline.required_cpu_index
    assert selected.non_client_methods == []


def test_server_hardware_feature_does_not_constrain_client_gpu(db):
    method = _method(db, SERVER_METHOD)
    method.requires_hw_features = ["DirectX 12"]
    db.flush()
    profile = ProjectProfile(functions=["multiplayer_netcode"], multiplayer=True)

    assert "DirectX 12" not in estimate_hardware(db, profile, [method]).required_hw_features


def test_unknown_scope_is_not_treated_as_client(db):
    """Нераспознанная область не превращается в экономию на компьютере игрока."""
    method = _method(db, CLIENT_METHOD)
    method.effect_scope = "edge"
    method.impact_cpu = -3
    db.flush()
    profile = ProjectProfile(functions=["open_world_streaming"], world_type="open_world")

    baseline = estimate_hardware(db, profile, [])
    selected = estimate_hardware(db, profile, [method])

    assert selected.required_cpu_index == baseline.required_cpu_index
    item = selected.non_client_methods[0]
    assert item.effect_scope_label == "не распознана"
    assert "не распознана" in item.reason


def test_load_profile_counts_only_client_effects(db):
    method = _method(db, SERVER_METHOD)
    profile = ProjectProfile(functions=["multiplayer_netcode"], multiplayer=True)

    load = aggregate_load([method], profile)

    assert load.cpu == load.gpu == 50
    assert any("серверной части" in note for note in load.notes)


def test_recommendation_explains_non_client_scope(client):
    response = client.post("/api/recommend", json={
        "profile": {"functions": ["multiplayer_netcode"], "multiplayer": True},
        "basket": [],
    })
    assert response.status_code == 200, response.text
    reasons = [
        reason
        for item in response.json()["recommendations"]
        for reason in item["reasons"]
        if item["method_code"] == SERVER_METHOD
    ]
    assert any("Область эффекта — сервер" in reason for reason in reasons)


def test_catalog_returns_effect_scope(client):
    methods = {item["code"]: item for item in client.get("/api/catalog/methods").json()}
    assert methods[SERVER_METHOD]["effect_scope"] == "server"
    assert methods[SERVER_METHOD]["effect_scope_label"] == "сервер"
    assert methods[CLIENT_METHOD]["effect_scope_label"] == "клиент"

    scopes = client.get("/api/meta/enums").json()["effect_scopes"]
    assert {item["value"] for item in scopes} == {"client", "server", "development"}


def test_admin_rejects_unknown_effect_scope(client):
    response = client.post("/api/admin/methods", json={
        "code": "scope_probe", "name": "Проба области",
        "source_url": "https://example.org/scope", "source_title": "Источник",
        "effect_scope": "cloud",
    })
    assert response.status_code == 422, response.text
    assert "effect_scope" in response.text


@pytest.mark.parametrize("admin_edited", [False, True])
def test_scope_correction_preserves_manual_changes(db, admin_edited):
    """Существующие базы получают значение каталога, но не чужую правку."""
    method = _method(db, SERVER_METHOD)
    method.effect_scope = "development" if admin_edited else "client"
    db.flush()

    assert correct_effect_scopes(db) == (0 if admin_edited else 1)
    assert method.effect_scope == ("development" if admin_edited else "server")
    assert correct_effect_scopes(db) == 0
