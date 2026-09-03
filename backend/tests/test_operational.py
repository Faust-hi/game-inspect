"""Проверки эксплуатационной готовности: безопасность, ошибки, здоровье сервиса."""
from __future__ import annotations

import pytest

from app.config import Settings
from app.services.security import SlidingWindowLimiter, limiter, token_matches


# ---------------------------------------------------------------------------
# Проверки состояния
# ---------------------------------------------------------------------------
def test_health_reports_ready(client):
    data = client.get("/api/health").json()
    assert data["status"] in {"ok", "degraded"}
    assert data["version"]
    assert "database" in data


def test_liveness_does_not_touch_database(client):
    """Проверка «живости» должна отвечать даже при недоступной базе."""
    response = client.get("/api/health/live")
    assert response.status_code == 200
    assert response.json()["status"] == "alive"


def test_readiness_reports_database(client):
    data = client.get("/api/health/ready").json()
    assert data["status"] in {"ready", "not_ready"}


# ---------------------------------------------------------------------------
# Обработка ошибок
# ---------------------------------------------------------------------------
def test_validation_error_has_structured_details(client):
    # basket должен быть списком: строка вызывает ошибку проверки типа.
    response = client.post("/api/recommend", json={"profile": {}, "basket": "не список"})
    assert response.status_code == 422
    body = response.json()
    assert body["error"]
    assert isinstance(body["details"], list)
    assert body["details"], "нужен перечень полей с ошибками, а не только общий текст"


def test_error_response_contains_request_id(client):
    response = client.get("/api/catalog/methods/__нет_такого__")
    assert response.status_code == 404
    assert "request_id" in response.json()


def test_internal_error_does_not_leak_details(client, monkeypatch, caplog):
    """Клиент получает код ошибки, но не текст исключения.

    Подробности не передаются ни при какой конфигурации: предыдущая версия
    добавляла их в ответ, когда `ENVIRONMENT` отличался от `production`.
    """
    from fastapi.testclient import TestClient

    from app.api import recommend as recommend_api
    from app.main import app

    def broken(*args, **kwargs):
        raise RuntimeError("секретные подробности внутреннего сбоя")

    monkeypatch.setattr(recommend_api.recommender, "build_recommendations", broken)
    # raise_server_exceptions=False — иначе тестовый клиент выбросит исключение
    # сам и обработчик приложения не будет задействован.
    with TestClient(app, raise_server_exceptions=False) as failing_client:
        with caplog.at_level("ERROR"):
            response = failing_client.post("/api/recommend", json={"profile": {}, "basket": []})
    assert response.status_code == 500
    body = response.json()
    assert body["error_id"]
    assert "секретные подробности" not in str(body)
    assert "detail" not in body
    # Зато подробности сохранены в журнале: по error_id их найдёт разработчик.
    assert "секретные подробности" in caplog.text
    assert body["error_id"] in caplog.text


# ---------------------------------------------------------------------------
# Защитные заголовки
# ---------------------------------------------------------------------------
def test_security_headers_are_set(client):
    response = client.get("/api/health")
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"
    assert response.headers["Referrer-Policy"] == "no-referrer"


def test_api_responses_are_not_cached(client):
    response = client.get("/api/health")
    assert "no-store" in response.headers.get("Cache-Control", "")


def test_request_id_is_returned(client):
    # Значение заголовка должно быть ASCII — иначе httpx не сможет его передать.
    response = client.get("/api/health", headers={"x-request-id": "check-123"})
    assert response.headers["X-Request-ID"] == "check-123"


# ---------------------------------------------------------------------------
# Токен администратора
# ---------------------------------------------------------------------------
def test_token_comparison_rejects_wrong_values():
    assert token_matches("admin") is True  # совпадает с настроенным в тестах
    assert token_matches("Admin") is False
    assert token_matches("") is False
    assert token_matches(None) is False


def test_token_comparison_rejects_prefix():
    """Совпадение только начала строки не должно допускаться."""
    assert token_matches("adm") is False
    assert token_matches("adminadmin") is False


def test_standard_token_is_flagged_as_insecure():
    settings = Settings(ADMIN_TOKEN="admin", CORS_ORIGINS="*")
    problems = settings.production_problems()
    assert any("ADMIN_TOKEN" in p for p in problems)
    assert any("CORS_ORIGINS" in p for p in problems)


def test_secure_configuration_has_no_problems():
    settings = Settings(
        ENVIRONMENT="production",
        ADMIN_TOKEN="очень-длинный-случайный-токен",
        CORS_ORIGINS="https://dss.example.ru",
        DATABASE_URL="postgresql+psycopg2://user:pw@localhost:5432/dss",
        AUTO_SEED=False,
        DB_ECHO=False,
    )
    assert settings.production_problems() == []


def test_production_on_sqlite_is_flagged():
    settings = Settings(
        ENVIRONMENT="production",
        ADMIN_TOKEN="токен",
        CORS_ORIGINS="https://dss.example.ru",
        DATABASE_URL="sqlite:///./local.db",
    )
    assert any("SQLite" in p for p in settings.production_problems())


# ---------------------------------------------------------------------------
# Ограничение частоты запросов
# ---------------------------------------------------------------------------
def test_rate_limiter_allows_up_to_limit():
    local = SlidingWindowLimiter()
    for _ in range(3):
        allowed, _ = local.check("ключ", limit=3)
        assert allowed is True
    allowed, remaining = local.check("ключ", limit=3)
    assert allowed is False
    assert remaining == 0


def test_rate_limiter_separates_keys():
    local = SlidingWindowLimiter()
    local.check("первый", limit=1)
    assert local.check("первый", limit=1)[0] is False
    assert local.check("второй", limit=1)[0] is True


def test_rate_limit_returns_429(client, profile, monkeypatch):
    from app.config import settings as app_settings

    limiter.reset()
    monkeypatch.setattr(app_settings, "RATE_LIMIT_ENABLED", True)
    monkeypatch.setattr(app_settings, "RATE_LIMIT_CALC_PER_MINUTE", 2)
    try:
        codes = [
            client.post("/api/recommend", json={"profile": profile, "basket": []}).status_code
            for _ in range(4)
        ]
    finally:
        monkeypatch.setattr(app_settings, "RATE_LIMIT_ENABLED", False)
        limiter.reset()

    assert codes[:2] == [200, 200]
    assert 429 in codes, f"ожидался отказ при превышении лимита, получено {codes}"


def test_rate_limit_disabled_by_default_in_tests(client, profile):
    """В тестах счётчики отключены, иначе прогон станет нестабильным."""
    from app.config import settings as app_settings

    assert app_settings.RATE_LIMIT_ENABLED is False
    for _ in range(5):
        assert client.post("/api/recommend", json={"profile": profile, "basket": []}).status_code == 200
