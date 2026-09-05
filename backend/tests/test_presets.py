"""Пресеты движков: детерминированы, каждая строка знает источник."""
from __future__ import annotations


def _presets(client, basket):
    response = client.post("/api/project-presets", json={
        "profile": {"name": "T", "functions": []}, "basket": basket,
    })
    assert response.status_code == 200, response.text
    files = {item["name"]: item["content"] for item in response.json()["files"]}
    assert set(files) == {"DefaultScalability.ini", "unity-quality-preset.json",
                          "godot-rendering-preset.json"}
    return files


def test_presets_are_deterministic(client):
    assert _presets(client, ["temporal_upscaling"]) == _presets(client, ["temporal_upscaling"])


def test_empty_basket_is_all_defaults(client):
    files = _presets(client, [])
    assert "from " not in files["DefaultScalability.ini"].split("; default")[0]
    assert "; default" in files["DefaultScalability.ini"]


def test_selected_method_marks_its_lines(client):
    files = _presets(client, ["cascaded_shadow_maps"])
    shadow_lines = [line for line in files["DefaultScalability.ini"].splitlines()
                    if line.startswith("sg.ShadowQuality")]
    assert len(shadow_lines) == 1
    assert "from cascaded_shadow_maps" in shadow_lines[0]


def test_unrelated_method_does_not_touch_shadows(client):
    """Чужое решение не должно менять несвязанные строки (изоляция)."""
    base = _presets(client, [])
    with_audio = _presets(client, ["audio_streaming_compression"])
    base_shadow = [line for line in base["DefaultScalability.ini"].splitlines()
                   if "Shadow" in line]
    audio_shadow = [line for line in with_audio["DefaultScalability.ini"].splitlines()
                    if "Shadow" in line]
    assert base_shadow == audio_shadow


def test_vram_limit_sets_pool_size(client):
    response = client.post("/api/project-presets", json={
        "profile": {"name": "T", "functions": [], "vram_limit_gb": 8.0}, "basket": [],
    })
    ini = next(item["content"] for item in response.json()["files"]
               if item["name"] == "DefaultScalability.ini")
    assert "r.Streaming.PoolSize=5734" in ini
