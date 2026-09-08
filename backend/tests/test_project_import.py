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


# --- Реальные форматы файлов движков ---------------------------------------
# Фикстуры повторяют структуру настоящих файлов: отступы Unity-YAML и
# шапку `config_version` Godot, из-за которых импорт раньше давал пустой
# результат, хотя отдельные поля в файле присутствовали.

UNITY_PROJECT_SETTINGS = b"""%YAML 1.1
%TAG !u! tag:unity3d.com,2011:
--- !u!129 &1
PlayerSettings:
  m_ObjectHideFlags: 0
  serializedVersion: 26
  productGUID: 0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f
  AndroidProfiler: 0
  productName: Real Unity Game
  companyName: Studio
  defaultScreenWidth: 1920
  defaultScreenHeight: 1080
  defaultScreenWidthWeb: 960
  m_StereoRenderingPath: 0
  virtualRealitySupported: 0
  scriptingBackend: 1
"""

GODOT_PROJECT = b"""config_version=5

[application]

config/name="Real Godot Game"
config/features=PackedStringArray("4.2", "Forward Plus")
config/icon="res://icon.svg"

[display]

window/size/viewport_width=2560
window/size/viewport_height=1440

[rendering]

renderer/rendering_method="forward_plus"
"""


def test_real_unity_project_settings_fills_indented_fields(client):
    """Поля PlayerSettings имеют отступ — они обязаны читаться."""
    response = client.post("/api/project-import", files=[
        ("files", ("ProjectSettings.asset", UNITY_PROJECT_SETTINGS, "text/plain")),
    ])
    assert response.status_code == 200, response.text
    body = response.json()

    assert body["patch"]["name"] == "Real Unity Game"
    assert body["patch"]["target_resolution"] == "1080p"
    # Файл настроек Unity определяет и движок, а не только отдельные поля.
    assert body["patch"]["engine"] == "unity"


def test_real_godot_project_with_config_version_header(client):
    """`config_version=5` до первой секции не ломает разбор."""
    response = client.post("/api/project-import", files=[
        ("files", ("project.godot", GODOT_PROJECT, "text/plain")),
    ])
    assert response.status_code == 200, response.text
    body = response.json()

    assert body["patch"]["name"] == "Real Godot Game"
    assert body["patch"]["engine_version"] == "4.2"
    assert body["patch"]["target_resolution"] == "1440p"
    assert not body["warnings"], body["warnings"]


def test_godot_value_with_percent_does_not_break_parsing(client):
    """Символ `%` в значении не воспринимается как интерполяция."""
    raw = b'config_version=5\n\n[application]\n\nconfig/name="100% Game"\n'
    response = client.post("/api/project-import", files=[
        ("files", ("project.godot", raw, "text/plain")),
    ])
    assert response.status_code == 200, response.text
    assert response.json()["patch"]["name"] == "100% Game"


def test_supported_heights_are_not_replaced_by_neighbours(client):
    """Точное поддерживаемое разрешение сохраняется, а не округляется."""
    for height, expected in ((768, "768p"), (900, "900p"), (1200, "1200p"), (1600, "1600p")):
        raw = UNITY_PROJECT_SETTINGS.replace(b"defaultScreenHeight: 1080",
                                             f"defaultScreenHeight: {height}".encode())
        response = client.post("/api/project-import", files=[
            ("files", ("ProjectSettings.asset", raw, "text/plain")),
        ])
        assert response.status_code == 200, response.text
        assert response.json()["patch"]["target_resolution"] == expected, height


def test_unsupported_height_is_marked_as_approximation(client):
    """Округление видно пользователю, а не выдаётся за точный режим."""
    raw = UNITY_PROJECT_SETTINGS.replace(b"defaultScreenHeight: 1080",
                                         b"defaultScreenHeight: 1050")
    response = client.post("/api/project-import", files=[
        ("files", ("ProjectSettings.asset", raw, "text/plain")),
    ])
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["patch"]["target_resolution"] == "1080p"
    assert any("приближённо" in line for line in body["detected"]), body["detected"]
