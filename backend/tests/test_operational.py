"""Проверки локального сервиса: здоровье, ошибки, формат ответа."""
from __future__ import annotations


# ---------------------------------------------------------------------------
# Проверки состояния
# ---------------------------------------------------------------------------
def test_health_reports_ready(client):
    data = client.get("/api/health").json()
    assert data["status"] in {"ok", "degraded"}
    assert data["version"]
    assert "database" in data


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
    """Клиент получает код ошибки, но не текст исключения."""
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


def test_request_id_is_returned(client):
    # Значение заголовка должно быть ASCII — иначе httpx не сможет его передать.
    response = client.get("/api/health", headers={"x-request-id": "check-123"})
    assert response.headers["X-Request-ID"] == "check-123"
