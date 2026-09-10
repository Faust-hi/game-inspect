"""Демонстрационная стабильность (офлайн).

Защищает показ: запуск с подготовленной БД, готовность данных,
основной сценарий из коробки, понятная ошибка вместо молчания,
отсутствие оборванных связей, влияющих на рекомендации.

Полный pytest и браузер при обычном запуске не требуются:
это проверки разработки и предпоказа, а не часть старта.
"""
from __future__ import annotations


def test_health_ready_on_seeded_database(client):
    """Готовое приложение: health ok, схема без ошибок, каталог не пуст."""
    body = client.get("/api/health").json()
    assert body["version"]
    assert body["ready"] is True
    assert body["schema_error"] is None
    assert body["catalog"]["methods"] > 0
    assert body["catalog"]["hardware_cpu"] > 0
    assert body["catalog"]["hardware_gpu"] > 0


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


def test_unknown_structure_is_refused_with_backup(tmp_path, monkeypatch):
    """Чужая структура: явный отказ + резервная копия, а не догадки."""
    import os

    from sqlalchemy import create_engine, text

    from app.config import reload_settings

    original = os.environ.get("DATABASE_URL")
    target = tmp_path / "foreign.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{target.as_posix()}")
    reload_settings()
    try:
        from app import db_migrate

        saved = dict(db_migrate.state)
        try:
            engine = create_engine(f"sqlite:///{target.as_posix()}", future=True)
            try:
                with engine.begin() as connection:
                    connection.execute(
                        text("CREATE TABLE foreign_data (id INTEGER PRIMARY KEY)")
                    )
            finally:
                engine.dispose()
            report = db_migrate.ensure_schema()
            assert report["migrated"] is False, report
            assert report["backup"] is not None
        finally:
            db_migrate.state.clear()
            db_migrate.state.update(saved)
    finally:
        if original is None:
            monkeypatch.delenv("DATABASE_URL", raising=False)
        else:
            monkeypatch.setenv("DATABASE_URL", original)
        reload_settings()


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
        assert link["a_code"] in codes or link["a_code"], link
        assert link["b_code"] in codes or link["b_code"], link

    hardware = client.get("/api/catalog/hardware").json()
    assert len(hardware["cpu"]) >= 30
    assert len(hardware["gpu"]) >= 30


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


def test_static_path_rejects_escape_and_serves_nested(tmp_path):
    """Раздача сборки: выход за пределы каталога закрыт, вложенный файл доступен."""
    from app.staticfiles_safe import safe_static_path

    root = tmp_path / "dist"
    (root / "assets").mkdir(parents=True)
    nested = root / "assets" / "app.js"
    nested.write_text("console.log(1)", encoding="utf-8")
    assert safe_static_path(root, "../gamedev_dss.db") is None
    assert safe_static_path(root, "..%2Fgamedev_dss.db") is None
    assert safe_static_path(root, "assets/app.js") == nested.resolve()


def test_foreign_origin_mutation_is_rejected(client):
    """Изменяющий запрос с чужого Origin — 403 с request_id, свой — проходит."""
    foreign = client.post(
        "/api/hardware-estimate",
        json={"profile": {}, "basket": []},
        headers={"Origin": "https://evil.example"},
    )
    assert foreign.status_code == 403
    assert foreign.json()["request_id"]
    own = client.post(
        "/api/hardware-estimate",
        json={"profile": {}, "basket": []},
        headers={"Origin": "http://localhost:5173"},
    )
    assert own.status_code == 200


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
