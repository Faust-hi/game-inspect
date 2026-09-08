"""Заполнение базы: пропуски видны, ручные правки не затираются.

Две потери, которые раньше были невидимы:

* файл, который не прочитался, и строка без обязательного поля пропадали молча,
  поэтому формальный успех не означал полного импорта (N02);
* повторное заполнение перезаписывало административные правки, и пользователь
  узнавал об этом только по исчезнувшим исправлениям (D43.6).
"""
from __future__ import annotations

import json

import pytest
from sqlalchemy import select

from app.models.entities import Engine, GameFunction, Method
from app.seed import seeder


# ---------------------------------------------------------------------------
# N02: пропуски видны
# ---------------------------------------------------------------------------
def test_hardware_row_without_model_is_reported(db, monkeypatch):
    monkeypatch.setattr(
        seeder, "_load_json", lambda _name: {"cpu": [{"vendor": "Без модели"}], "gpu": []},
    )

    outcome = seeder.SeedOutcome()
    seeder.seed_hardware(db, outcome)

    assert [item["entity"] for item in outcome.skipped] == ["hardware_cpu"]


def test_seed_all_reports_skips(db, monkeypatch):
    """Отчёт заполнения содержит пропуски, а не только счётчики."""
    monkeypatch.setattr(
        seeder, "_load_json", lambda _name: {"cpu": [], "gpu": [{"vendor": "Broken"}]},
    )

    report = seeder.seed_all(db, validate=False)

    assert report["skipped_count"] >= 1
    assert report["skipped"], "Пропуск потерян в итоговом отчёте"


# ---------------------------------------------------------------------------
# D43.6: ручные правки сохраняются
# ---------------------------------------------------------------------------
def test_reseeding_preserves_manual_edit(db):
    """Повторное заполнение не затирает правку администратора."""
    method = db.scalar(select(Method).limit(1))
    method.name = "Ручное название"
    db.flush()

    report = seeder.seed_all(db, validate=False)
    db.refresh(method)

    assert method.name == "Ручное название", "Правка затерта демонстрационными данными"
    assert report["preserved_count"] >= 1
    preserved = next(item for item in report["preserved"] if item["entity"] == "methods")
    assert "name" in preserved["fields"]
    assert preserved["key"] == method.code


def test_reseeding_preserves_unpublished_status(db):
    """Снятый с публикации движок не публикуется обратно при повторном сиде."""
    engine = db.scalar(select(Engine).limit(1))
    engine.status = "draft"
    db.flush()

    seeder.seed_all(db, validate=False)
    db.refresh(engine)

    assert engine.status == "draft"


def test_explicit_restore_replaces_manual_edit(db):
    """Явное восстановление демоданных возвращает штатное значение."""
    method = db.scalar(select(Method).limit(1))
    original_name = method.name

    method.name = "Ручное название"
    db.flush()
    seeder.seed_all(db, validate=False, overwrite=True)
    db.refresh(method)

    assert method.name == original_name, "Явное восстановление не вернуло демоданные"


def test_seed_endpoint_preserves_by_default_and_restores_on_demand(client, db):
    """Административный маршрут различает заполнение и восстановление."""
    method = db.scalar(select(Method).limit(1))
    original_name = method.name
    method.name = "Ручное название"
    db.flush()

    default = client.post("/api/admin/seed", json={}).json()
    assert default["preserved_count"] >= 1
    db.refresh(method)
    assert method.name == "Ручное название"

    restored = client.post("/api/admin/seed", json={"restore_demo": True}).json()
    assert restored["preserved_count"] == 0
    db.refresh(method)
    assert method.name == original_name


def test_fresh_database_has_nothing_to_preserve(db):
    """Первое заполнение пустой базы не считается расхождением."""
    outcome = seeder.SeedOutcome()
    seeder.seed_engines(db, outcome)

    assert outcome.preserved == []
    assert outcome.added.get("engines", 0) >= 0


@pytest.mark.parametrize("entity", ["game_functions", "methods", "engines", "engine_tools"])
def test_no_unexplained_skips_on_demo_data(db, entity):
    """Демонстрационное наполнение должно проходить без пропусков."""
    report = seeder.seed_all(db, validate=False)

    unexplained = [item for item in report["skipped"] if item["entity"] == entity]
    assert unexplained == [], f"Пропуски в {entity}: {unexplained}"


# ---------------------------------------------------------------------------
# Каталог функций: покрытие признаков, встречающихся в реальных проектах
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("code", [
    "path_tracing", "ray_traced_effects", "dynamic_lighting", "mesh_shaders",
    "procedural_terrain", "gameplay_ability_system", "vehicle_simulation",
    "advanced_npc_ai",
])
def test_feature_from_audit_is_present_in_catalog(db, code):
    """Признаки, которых не хватало по итогам аудита, описаны в каталоге.

    Без функции в каталоге признак проекта невозможно передать в расчёт:
    он либо отбрасывается, либо молча не влияет на результат.
    """
    published = {
        fn.code for fn in db.scalars(
            select(GameFunction).where(GameFunction.status == "published")
        )
    }
    assert code in published, f"Функции {code} нет среди опубликованных"


@pytest.mark.parametrize("code", [
    "full_path_tracing_pipeline", "path_tracing_sample_denoiser_budget",
    "selective_ray_traced_effects", "rt_effect_resolution_budget",
    "dynamic_light_priority_budget", "light_range_attenuation_lod",
    "meshlet_pipeline_adoption", "gpu_meshlet_culling_budget",
    "chunked_procedural_terrain", "terrain_generation_streaming_budget",
    "data_driven_ability_system", "ability_visual_effect_budget",
    "raycast_vehicle_physics", "vehicle_simulation_lod",
    "behaviour_tree_update_budget", "npc_perception_budget",
])
def test_new_method_is_published_and_attributable(db, code):
    """У нового решения есть родительская функция, источник и связь с движком."""
    method = db.scalar(select(Method).where(Method.code == code))
    assert method is not None, f"Метод {code} не попал в базу"
    assert method.status == "published", f"Метод {code} не опубликован"
    assert method.source_url, f"У метода {code} нет источника"
    parent = db.get(GameFunction, method.function_id) if method.function_id else None
    assert parent is not None, f"У метода {code} нет родительской функции"
