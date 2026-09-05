"""Публикация как инвариант: черновик не должен стать виден пользователю.

Проверки разбиты по трём уровням, потому что запись попадает в базу тремя
путями — административная модель, импорт и прямой доступ к ORM, — и отсутствие
проверки хотя бы в одном из них открывает черновик в публичных каталогах.
"""
from __future__ import annotations

import json

import pytest

from app.models.entities import (
    Engine, EngineTool, GameExample, GameFunction, HardwareCPU, HardwareGPU, Method,
)
from app.services import publication
from app.services.publication import Status

ADMIN: dict[str, str] = {}


# ---------------------------------------------------------------------------
# Уровень 1: сама политика публикации
# ---------------------------------------------------------------------------
def test_status_cycle_only_allows_declared_transitions():
    assert publication.can_transition("draft", "reviewed") is True
    assert publication.can_transition("reviewed", "published") is True
    assert publication.can_transition("reviewed", "draft") is True
    assert publication.can_transition("published", "reviewed") is True

    # Прямая публикация черновика и возврат из публикации в черновик запрещены.
    assert publication.can_transition("draft", "published") is False
    assert publication.can_transition("published", "draft") is False
    assert publication.transition_error("draft", "published") is not None


def test_setting_same_status_is_not_an_error():
    """Повторная установка текущего статуса — пустая операция, а не отказ."""
    assert publication.transition_error("draft", "draft") is None
    assert publication.transition_error("published", "published") is None


def test_unknown_status_is_rejected():
    assert publication.transition_error("draft", "архив") is not None


@pytest.mark.parametrize("url,valid", [
    ("https://example.org", True),
    ("http://example.org", True),
    ("HTTPS://EXAMPLE.ORG", True),
    ("ftp://example.org", False),
    ("javascript:alert(1)", False),
    ("file:///etc/passwd", False),
    ("example.org", False),
    ("", False),
])
def test_is_valid_url(url, valid):
    assert publication.is_valid_url(url) is valid


def test_numeric_ranges_are_enforced():
    problems = publication.record_problems(Method, {"confidence": 5.0, "complexity": 99})
    joined = " ".join(problems)
    assert "confidence" in joined
    assert "complexity" in joined


def test_record_cannot_be_created_published():
    """Импорт не вправе сразу публиковать запись."""
    problems = publication.record_problems(Method, {"status": "published"})
    assert problems


def test_publication_requires_source():
    """Без ссылки и названия источника запись опубликовать нельзя."""
    blank = Method(code="no_source", name="Метод без источника")
    problems = publication.publication_problems(blank, has_links=True)
    joined = " ".join(problems).lower()
    assert "источник" in joined
    assert "название источника" in joined

    filled = Method(code="with_source", name="Метод", source_title="Источник",
                    source_url="https://example.org")
    assert not publication.publication_problems(filled, has_links=True)


# ---------------------------------------------------------------------------
# Уровень 2: публичные маршруты отдают только опубликованный снимок
# ---------------------------------------------------------------------------
PUBLIC_ENDPOINTS = [
    ("/api/catalog/functions", "code"),
    ("/api/catalog/methods", "code"),
    ("/api/catalog/engines", "code"),
    ("/api/catalog/examples", "title"),
    ("/api/catalog/conflicts", "a_code"),
]


@pytest.mark.parametrize("endpoint,key", PUBLIC_ENDPOINTS)
def test_public_catalogs_expose_only_published(client, db, endpoint, key):
    """Снятые с публикации записи не должны попадать в публичные каталоги."""
    from sqlalchemy import select

    rows = client.get(endpoint).json()
    assert rows, f"каталог {endpoint} пуст — проверка лишена смысла"
    codes = {row[key] for row in rows}

    # Убираем публикацию у первой записи напрямую через ORM: публичный слой
    # обязан это заметить.
    model = {
        "/api/catalog/functions": GameFunction,
        "/api/catalog/methods": Method,
        "/api/catalog/engines": Engine,
        "/api/catalog/examples": GameExample,
        "/api/catalog/conflicts": None,
    }[endpoint]
    if model is not None:
        victim = db.scalar(select(model).where(model.status == "published"))
        assert getattr(victim, key) in codes

        victim.status = "reviewed"
        db.flush()

        remaining = {row[key] for row in client.get(endpoint).json()}
        assert getattr(victim, key) not in remaining


def test_draft_method_card_is_not_available_by_code(client, db):
    """Прямой запрос карточки по коду не открывает черновик."""
    from sqlalchemy import select

    method = db.scalar(select(Method).where(Method.status == "published"))
    assert client.get(f"/api/catalog/methods/{method.code}").status_code == 200

    method.status = "draft"
    db.flush()
    assert client.get(f"/api/catalog/methods/{method.code}").status_code == 404


def test_draft_tool_is_hidden_inside_published_engine(client, db):
    """Инструмент внутри опубликованного движка тоже фильтруется по статусу."""
    from sqlalchemy import select

    tool = db.scalar(select(EngineTool).where(EngineTool.status == "published"))
    engines = client.get("/api/catalog/engines").json()
    before = {t["code"] for e in engines for t in e["tools"]}
    assert tool.code in before

    tool.status = "draft"
    db.flush()
    after = {t["code"] for e in client.get("/api/catalog/engines").json() for t in e["tools"]}
    assert tool.code not in after


def test_hardware_catalogs_exclude_unpublished(client, db):
    from sqlalchemy import select

    cpu = db.scalar(select(HardwareCPU).where(HardwareCPU.status == "published"))
    gpu = db.scalar(select(HardwareGPU).where(HardwareGPU.status == "published"))
    cpu.status = "draft"
    gpu.status = "draft"
    db.flush()

    hardware = client.get("/api/catalog/hardware").json()
    assert cpu.model not in {c["model"] for c in hardware["cpu"]}
    assert gpu.model not in {g["model"] for g in hardware["gpu"]}


def test_unpublished_hardware_is_not_used_in_estimate(client, db, profile):
    """Оценка оборудования строится только по опубликованным записям."""
    from sqlalchemy import select

    gpus = list(db.scalars(select(HardwareGPU).where(HardwareGPU.status == "published")))
    assert len(gpus) >= 2
    best = max(gpus, key=lambda g: g.raster_score)
    before = client.post("/api/hardware-estimate",
                         json={"profile": profile, "basket": []}).json()
    assert before["reference_gpu"] is not None

    best.status = "draft"
    db.flush()
    after = client.post("/api/hardware-estimate",
                        json={"profile": profile, "basket": []}).json()
    if after["reference_gpu"] is not None:
        assert after["reference_gpu"]["model"] != best.model


def test_recommendations_ignore_unpublished_methods(client, db, profile):
    from sqlalchemy import select

    method = db.scalar(select(Method).where(Method.status == "published"))
    before = client.post("/api/recommend", json={"profile": profile, "basket": []}).json()
    codes_before = {r["method_code"] for r in before["recommendations"]}

    method.status = "draft"
    db.flush()
    after = client.post("/api/recommend", json={"profile": profile, "basket": []}).json()
    codes_after = {r["method_code"] for r in after["recommendations"]}
    assert method.code not in codes_after
    # Остальные рекомендации на месте: фильтр точечный, а не «всё или ничего».
    assert codes_after and codes_after <= codes_before | set()


# ---------------------------------------------------------------------------
# Уровень 3: импорт
# ---------------------------------------------------------------------------
def test_import_does_not_publish(client):
    rows = [{
        "code": "imp_pub", "name": "Импортированный", "status": "published",
        "source_url": "https://example.org/x", "source_title": "Источник",
    }]
    response = client.post("/api/admin/import/methods",
                           files={"file": ("m.json", json.dumps(rows), "application/json")},
                           headers=ADMIN)
    assert response.status_code == 422, response.text


def test_import_is_atomic(client):
    """Ошибка в одной строке отменяет весь импорт, а не часть."""
    rows = [
        {"code": "imp_ok", "name": "Корректный", "source_url": "https://example.org/ok",
         "source_title": "Источник"},
        {"code": "imp_bad", "name": "Сломанный", "source_url": "https://example.org/bad",
         "source_title": "Источник", "confidence": 42},
    ]
    response = client.post("/api/admin/import/methods",
                           files={"file": ("m.json", json.dumps(rows), "application/json")},
                           headers=ADMIN)
    assert response.status_code == 422, response.text

    codes = {m["code"] for m in client.get("/api/admin/methods", headers=ADMIN).json()}
    # Ни одна строка не записана: импорт либо выполняется целиком, либо нет.
    assert "imp_ok" not in codes
    assert "imp_bad" not in codes


def test_import_creates_drafts_only(client):
    rows = [{
        "code": "imp_draft", "name": "Импортированный черновик",
        "source_url": "https://example.org/d", "source_title": "Источник",
    }]
    response = client.post("/api/admin/import/methods",
                           files={"file": ("m.json", json.dumps(rows), "application/json")},
                           headers=ADMIN)
    assert response.status_code == 200, response.text
    assert response.json()["created"] == 1
    assert client.get("/api/catalog/methods/imp_draft").status_code == 404


def test_import_rejects_oversized_payload(client):
    rows = [{"code": f"m{i}", "name": f"Метод {i}"} for i in range(50)]
    huge = json.dumps(rows) * 4000
    response = client.post("/api/admin/import/methods",
                           files={"file": ("m.json", huge, "application/json")},
                           headers=ADMIN)
    assert response.status_code == 413, response.text


def test_status_values():
    """Значения статусов соответствуют ожидаемому жизненному циклу."""
    assert {s.value for s in Status} == {"draft", "reviewed", "published"}
