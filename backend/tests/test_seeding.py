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

from app.models.entities import Engine, GameExample, Method
from app.seed import seeder


# ---------------------------------------------------------------------------
# N02: пропуски видны
# ---------------------------------------------------------------------------
def test_unreadable_example_file_is_reported(db, monkeypatch, tmp_path):
    """Непрочитанный файл примеров — потеря данных, а не деталь реализации."""
    broken = tmp_path / "broken.json"
    broken.write_text("{ не json", encoding="utf-8")
    monkeypatch.setattr(seeder, "_example_files", lambda: [(broken, "published")])

    outcome = seeder.SeedOutcome()
    seeder.seed_examples(db, outcome)

    assert outcome.skipped, "Файл не прочитан, но пропуск не попал в отчёт"
    assert "broken.json" in outcome.skipped[0]["key"]
    assert outcome.skipped[0]["reason"]


def test_example_row_without_source_is_reported(db, monkeypatch, tmp_path):
    """Пример без источника не импортируется, но и не пропадает бесследно."""
    path = tmp_path / "examples.json"
    path.write_text(
        json.dumps([{"title": "Без источника", "year": 2020}]), encoding="utf-8",
    )
    monkeypatch.setattr(seeder, "_example_files", lambda: [(path, "published")])

    outcome = seeder.SeedOutcome()
    seeder.seed_examples(db, outcome)

    assert outcome.skipped
    assert "Без источника" in outcome.skipped[0]["key"]
    assert db.scalar(select(GameExample).where(GameExample.title == "Без источника")) is None


def test_hardware_row_without_model_is_reported(db, monkeypatch):
    monkeypatch.setattr(
        seeder, "_load_json", lambda _name: {"cpu": [{"vendor": "Без модели"}], "gpu": []},
    )

    outcome = seeder.SeedOutcome()
    seeder.seed_hardware(db, outcome)

    assert [item["entity"] for item in outcome.skipped] == ["hardware_cpu"]


def test_seed_all_reports_skips(db, monkeypatch, tmp_path):
    """Отчёт заполнения содержит пропуски, а не только счётчики."""
    broken = tmp_path / "broken.json"
    broken.write_text("не json", encoding="utf-8")
    monkeypatch.setattr(seeder, "_example_files", lambda: [(broken, "published")])

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
