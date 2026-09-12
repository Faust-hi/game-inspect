"""Демонстрационная стабильность (офлайн).

Защищает показ: запуск с подготовленной БД, готовность данных,
основной сценарий из коробки, понятная ошибка вместо молчания,
отсутствие оборванных связей, влияющих на рекомендации.

Полный pytest и браузер при обычном запуске не требуются:
это проверки разработки и предпоказа, а не часть старта.

Широкие наборы инфраструктуры и безопасности сюда не входят — они не
обнаруживают дефекта, опасного для результата или показа. Из миграций
оставлена только минимальная проверка чистой SQLite: она непосредственно
защищает запуск демонстрации.
"""
from __future__ import annotations

import pytest


@pytest.mark.critical
def test_api_readiness_on_seeded_database(client):
    """Готовность API на заполненной базе: health ok и отчёт по умолчанию.

    Объединяет две повторявшиеся проверки готовности (слияние M1): состояние
    сервиса и то, что отчёт по умолчанию считается на валидном профиле.
    Второй запрос ловил дефект, при котором отчёт падал на профиле без
    обязательных полей и страница показа не открывалась вовсе.
    """
    body = client.get("/api/health").json()
    assert body["version"]
    assert body["ready"] is True
    assert body["schema_error"] is None
    assert body["catalog"]["methods"] > 0
    assert body["catalog"]["hardware_cpu"] > 0
    assert body["catalog"]["hardware_gpu"] > 0

    report = client.get("/api/report-data")
    assert report.status_code == 200, report.text
    payload = report.json()
    assert payload["recommendation"]["evidence_summary"]["calibration_status"] == "not_calibrated"


@pytest.mark.critical
def test_health_unavailable_on_schema_error(client, monkeypatch):
    """Сломанная схема: честный unavailable/503, а не «как готовое»."""
    from app import db_migrate

    monkeypatch.setitem(db_migrate.state, "schema_ok", False)
    monkeypatch.setitem(db_migrate.state, "schema_error", "boom")
    response = client.get("/api/health")
    assert response.status_code == 503
    body = response.json()
    assert body["status"] == "unavailable"
    assert body["ready"] is False


@pytest.mark.critical
def test_fresh_sqlite_bootstraps_through_migrations(tmp_path, monkeypatch):
    """Чистая SQLite поднимается только миграциями (защита демонстрации).

    Дефект: старая база молча оставалась без новых колонок (create_all
    их не добавляет), либо чужой схеме ставился слепой stamp head.
    """
    import os

    from app.config import reload_settings

    original = os.environ.get("DATABASE_URL")
    target = tmp_path / "demo.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{target.as_posix()}")
    reload_settings()
    try:
        from app import db_migrate

        saved = dict(db_migrate.state)
        try:
            report = db_migrate.ensure_schema()
            assert report["migrated"] is True, report
            assert "methods" in db_migrate._table_names(
                f"sqlite:///{target.as_posix()}"
            )
        finally:
            db_migrate.state.clear()
            db_migrate.state.update(saved)
    finally:
        if original is None:
            monkeypatch.delenv("DATABASE_URL", raising=False)
        else:
            monkeypatch.setenv("DATABASE_URL", original)
        reload_settings()


@pytest.mark.extended
def test_published_slice_has_sources_and_no_dangling_links(client):
    """Опубликованный срез целостен: источники есть, связи не оборваны.

    Общий инвариант вместо проверок каждого элемента и точных счётчиков:
    оборванная связь здесь — это рекомендация, ведущая в никуда.
    """
    methods = client.get("/api/catalog/methods").json()
    assert len(methods) >= 40
    for item in methods:
        assert item["source_url"], item["code"]
        assert item["function_code"], item["code"]

    codes = {item["code"] for item in methods}
    for link in client.get("/api/catalog/conflicts").json():
        # Строгое вхождение: запись `x in codes or x` истинна при любом
        # непустом коде и не обнаруживала бы оборванную связь.
        assert link["a_code"] in codes, link
        assert link["b_code"] in codes, link

    hardware = client.get("/api/catalog/hardware").json()
    assert len(hardware["cpu"]) >= 30
    assert len(hardware["gpu"]) >= 30


@pytest.mark.critical
def test_draft_does_not_leak_into_public_slice(client):
    """Черновик не виден в публичной выдаче (аналог утечки train→test).

    Дефект: непроверенная запись без источника попадает в рекомендации.
    """
    created = client.post("/api/admin/methods", json={
        "code": "tmp_draft_probe", "name": "Черновая проба",
        "summary": "Проверка", "status": "published",
    }).json()
    assert created["status"] == "draft"
    listed = {item["code"] for item in client.get("/api/catalog/methods").json()}
    assert "tmp_draft_probe" not in listed
    assert client.get("/api/catalog/methods/tmp_draft_probe").status_code == 404


@pytest.mark.critical
def test_critical_error_is_understandable(client):
    """Критическая ошибка: понятное сообщение + код + request_id, а не молчание."""
    response = client.post("/api/hardware-estimate", json={
        "profile": {"target_fps": 0}, "basket": [],
    })
    assert response.status_code == 422, response.text
    body = response.json()
    assert isinstance(body["error"], str) and body["error"]
    assert body["code"] == "validation_error"
    assert body["request_id"]
    assert body["request_id"] == response.headers["x-request-id"]


@pytest.mark.critical
def test_unknown_api_path_is_not_served_as_page(client):
    """Неизвестный путь API — 404 JSON, а не главная страница с кодом 200.

    Дефект: собранное приложение раздаёт маршрут `/{full_path}`, поэтому GET
    на неверный адрес API возвращал 200 text/html. Клиент получал «успешный»
    ответ, который нельзя разобрать, и ошибка в адресе запроса пропадала —
    вместо неё пользователь видел сбой без причины.
    """
    from app.main import FRONTEND_DIST

    if not FRONTEND_DIST.exists():
        pytest.skip("нужна собранная сборка: без dist маршрут не регистрируется")

    response = client.get("/api/catalog/nonexistent")
    assert response.status_code == 404, response.text
    assert response.headers["content-type"].startswith("application/json")
    body = response.json()
    assert body["code"] == "not_found"
    assert body["request_id"]

    # Пути самого приложения по-прежнему отдаются страницей.
    assert client.get("/profile").status_code == 200


@pytest.mark.critical
def test_private_file_outside_dist_is_not_served(client):
    """Приватный файл вне каталога сборки не выдаётся ни одним обходом пути.

    Свойство R6 «нет доступа к приватным файлам». Цель — рабочая база
    `backend/gamedev_dss.db`: она лежит рядом с каталогом сборки, и утечка
    видна по сигнатуре SQLite в теле ответа.

    Перебираются разные техники обхода (относительный подъём, процентное
    кодирование сегмента, двойное кодирование, свёртка `....//`, разделитель
    Windows, абсолютный путь). На вариант ровно один запрос: проверяются
    и код ответа, и отсутствие утечки в теле.
    """
    from app.main import FRONTEND_DIST

    if not FRONTEND_DIST.exists():
        pytest.skip("нужна собранная сборка: без dist маршрут не регистрируется")

    target = "backend/gamedev_dss.db"
    variants = {
        "относительный подъём": f"../{target}",
        "процентное кодирование": "..%2F" + target.replace("/", "%2F"),
        "закодированные точки": "%2e%2e%2f" + target.replace("/", "%2f"),
        "двойное кодирование": "..%252F" + target.replace("/", "%252F"),
        "свёртка точек": f"....//{target}",
        "разделитель Windows": "..\\" + target.replace("/", "\\"),
        "абсолютный путь": f"/{target}",
    }
    leaked: list[str] = []
    for name, path in variants.items():
        response = client.get(f"/{path}")
        # Обход либо отвергается, либо отдаёт главную страницу — но не файл.
        assert response.status_code in {200, 403, 404}, (name, response.status_code)
        if b"SQLite format 3" in response.content:
            leaked.append(name)
    assert not leaked, f"утечка приватного файла через обход пути: {leaked}"

    # Обычный статический файл сборки по-прежнему отдаётся: защита не должна
    # превращаться в отказ раздавать сам frontend.
    assert client.get("/").status_code == 200


@pytest.mark.critical
def test_foreign_origin_cannot_change_data(client, profile):
    """Изменяющий запрос из чужого origin браузера отклонён (R6).

    Локальное приложение обслуживает один сайт: запрос с заголовком `Origin`
    стороннего домена означает, что страницу открыли не мы (CSRF-сценарий),
    и изменение данных запрещено. Чтение при этом не блокируется — иначе
    внешние ссылки на отчёт перестали бы работать.

    Тест осмыслен только потому, что тот же запрос без заголовка `Origin`
    и с локальным origin проходит: при снятии защиты он начинает падать.
    """
    payload = {"profile": profile, "basket": []}

    local = client.post(
        "/api/recommend", json=payload, headers={"Origin": "http://localhost:5173"}
    )
    assert local.status_code == 200, local.text

    no_origin = client.post("/api/recommend", json=payload)
    assert no_origin.status_code == 200, no_origin.text

    foreign = client.post(
        "/api/recommend", json=payload, headers={"Origin": "https://evil.example"}
    )
    assert foreign.status_code == 403, foreign.text
    assert foreign.json()["code"] == "forbidden"

    # Чтение с чужим origin не блокируется: блокируется только изменение.
    assert client.get("/api/health", headers={"Origin": "https://evil.example"}).status_code == 200
