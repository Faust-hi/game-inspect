"""Импорт анкеты из файлов движка: заполняется только надёжное."""
from __future__ import annotations


def test_uproject_fills_engine_and_version(client):
    response = client.post("/api/project-import", files=[
        ("files", ("game.uproject", b'{"EngineAssociation": "5.3"}', "application/json")),
    ])
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["profile"]["engine"] == "unreal"
    assert body["profile"]["engine_version"] == "5.3"
    assert "engine" in body["filled"]


def test_dlss_plugin_suggests_upscaling(client):
    response = client.post("/api/project-import", files=[
        ("files", ("game.uproject",
                   b'{"EngineAssociation": "5.1", "Plugins": [{"Name": "DLSS"}]}',
                   "application/json")),
    ])
    codes = {item["method_code"] for item in response.json()["suggested"]}
    assert "temporal_upscaling" in codes


def test_godot_project_fills_name_and_resolution(client):
    response = client.post("/api/project-import", files=[
        ("files", ("project.godot",
                   b'[application]\nconfig/name="Test"\n'
                   b'config/features=PackedStringArray("4.2", "Forward Plus")\n'
                   b"[display]\nwindow/size/viewport_width=1920\n"
                   b"window/size/viewport_height=1080\n",
                   "text/plain")),
    ])
    body = response.json()
    assert body["profile"]["engine"] == "godot"
    assert body["profile"]["name"] == "Test"
    assert body["profile"]["target_resolution"] == "1080p"


def test_unity_version_fills_engine(client):
    response = client.post("/api/project-import", files=[
        ("files", ("ProjectVersion.txt", b"m_EditorVersion: 2022.3.10f1\n", "text/plain")),
    ])
    body = response.json()
    assert body["profile"]["engine"] == "unity"
    assert "2022" in body["profile"]["engine_version"]


def test_unknown_format_is_reported_not_failed(client):
    response = client.post("/api/project-import", files=[
        ("files", ("notes.txt", b"just some text", "text/plain")),
    ])
    assert response.status_code == 200
    body = response.json()
    assert body["filled"] == []
    assert body["warnings"]


def test_conflict_keeps_first_value(client):
    """Противоречащие файлы не перезаписывают друг друга молча."""
    response = client.post("/api/project-import", files=[
        ("files", ("a.uproject", b'{"EngineAssociation": "5.3"}', "application/json")),
        ("files", ("project.godot",
                   b'[application]\nconfig/features=PackedStringArray("4.2", "Forward Plus")\n',
                   "text/plain")),
    ])
    body = response.json()
    assert body["profile"]["engine"] == "unreal"
    assert any("unreal" in warning and "godot" in warning for warning in body["warnings"])


def test_patch_contains_only_extracted_fields(client):
    """Импорт отдаёт для применения только извлечённые поля.

    Полный `profile` применять нельзя: в нём все остальные поля заполнены
    значениями по умолчанию, и применение сбросило бы ответы пользователя.
    """
    response = client.post("/api/project-import", files=[
        ("files", ("game.uproject", b'{"EngineAssociation": "5.3"}', "application/json")),
    ])
    assert response.status_code == 200, response.text
    body = response.json()

    assert body["patch"] == {"engine": "unreal", "engine_version": "5.3"}
    # Предпросмотр полный, но применяется только patch.
    assert set(body["profile"]) > set(body["patch"])


def test_patch_does_not_reset_unrelated_answers(client):
    """Масштаб, функции и целевые показатели не входят в patch из .uproject."""
    response = client.post("/api/project-import", files=[
        ("files", ("game.uproject", b'{"EngineAssociation": "5.3"}', "application/json")),
    ])
    patch = response.json()["patch"]

    for field in ("scale", "functions", "target_fps", "target_resolution", "platforms"):
        assert field not in patch, f"поле {field} не извлекалось и не должно применяться"


def test_empty_import_produces_empty_patch(client):
    """Пустой результат импорта не должен ничего сбрасывать."""
    response = client.post("/api/project-import", files=[
        ("files", ("notes.txt", b"just some text", "text/plain")),
    ])
    assert response.status_code == 200, response.text
    assert response.json()["patch"] == {}


def test_invalid_extracted_value_reports_reason(client):
    """Причина отказа импорта понятна, а не сводится к «Ошибка 422»."""
    from app.services import project_import

    original = project_import.import_project
    project_import.import_project = lambda files: {
        "filled": {"target_fps": 9999},
        "suggested": [], "detected": [], "warnings": [],
    }
    try:
        response = client.post("/api/project-import", files=[
            ("files", ("game.uproject", b"{}", "application/json")),
        ])
    finally:
        project_import.import_project = original

    assert response.status_code == 422
    body = response.json()
    assert isinstance(body["error"], str)
    assert body["details"], "нужно сообщить, какое поле не подошло"
