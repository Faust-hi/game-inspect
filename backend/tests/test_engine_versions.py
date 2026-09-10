"""Движок и версии (офлайн).

Дефекты: выдача несовместимого метода как подходящего,
признание неизвестной версии совместимой, молчаливый отказ
нового движка из каталога.
"""
from __future__ import annotations


def _post(client, path, **overrides):
    profile = {
        "name": "Движок",
        "format": "3D",
        "world_type": "open_world",
        "scale": "large",
        "stage": "prototype",
        "engine": "unreal",
        "platforms": ["pc_windows"],
        "functions": ["large_scale_terrain"],
        "target_resolution": "1080p",
        "target_quality": "high",
        "target_fps": 60,
    }
    profile.update(overrides)
    return client.post(path, json={"profile": profile, "basket": []})


def test_unknown_engine_rejected_with_hint(client):
    """Неизвестный движок: понятный отказ со списком допустимых, а не пустой расчёт."""
    response = _post(client, "/api/recommend", engine="no_such_engine")
    assert response.status_code == 422, response.text
    body = response.json()
    assert "no_such_engine" in body["error"]
    assert any("unreal" in item for item in body["details"])


def test_catalog_engine_accepted_without_code_change(client):
    """Движок из каталога принимается расчётом (расширение без изменения кода)."""
    for path in ("/api/recommend", "/api/load-profile", "/api/hardware-estimate"):
        profile = {
            "engine": "custom", "functions": [],
            "platforms": ["pc_windows"],
        }
        response = client.post(path, json={"profile": profile, "basket": []})
        assert response.status_code == 200, (path, response.text)


def test_version_cuts_builtin_tool_and_warns_in_basket(client):
    """Nanite недоступен в UE 4.27: карточка не выдаёт его за готовый, корзина — риск.

    Дефект: метод с отсутствующим в версии инструментом советуют как готовый.
    """
    response = _post(client, "/api/recommend", engine_version="4.27")
    assert response.status_code == 200, response.text
    cards = [
        row for row in response.json()["recommendations"]
        if row["method_code"] == "virtual_geometry_clusters"
    ]
    assert cards, "ожидался метод с привязкой к Nanite"
    support = cards[0]["engine_support"]
    assert support is not None and support["tool_code"] == "ue_nanite"
    assert support["available"] is False

    basket_profile = {
        "engine": "unreal", "engine_version": "4.27",
        "functions": ["large_scale_terrain"],
        "platforms": ["pc_windows"],
    }
    basket = client.post(
        "/api/recommend",
        json={"profile": basket_profile, "basket": ["virtual_geometry_clusters"]},
    ).json()
    assert "engine_tool_version" in {risk["code"] for risk in basket["risks"]}


def test_linux_with_directx_gets_no_hardware(client):
    """Linux + DirectX 12: цели без нативного пути — без референса, с явной причиной."""
    response = client.post("/api/hardware-estimate", json={
        "profile": {"platforms": ["pc_linux"], "render_api": "dx12", "functions": []},
        "basket": [],
    })
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["reference_gpu"] is None
    assert body["reference_cpu"] is None
    assert body["exceeds_catalog"] is True
    assert any("DirectX 12" in item and "Linux" in item for item in body["unmet_limits"])


def test_directstorage_needs_windows_and_modern_api(client):
    """DirectStorage учитывается на Windows/DX12 и исключается на Linux/Vulkan.

    Дефект: платформенное условие игнорируется — советуют неработающее решение.
    """
    def accounted(**changes):
        profile = {
            "functions": ["audio_system", "open_world_streaming"],
            "multiplayer": True, "player_count": 8,
            "render_api": "dx12", "world_type": "open_world",
        }
        profile.update(changes)
        data = client.post(
            "/api/recommend",
            json={"profile": profile, "basket": ["directstorage_io"]},
        ).json()
        return data["accounted_method_codes"]

    assert "directstorage_io" in accounted(
        platforms=["pc_windows"], render_api="dx12", storage_type="hdd",
    )
    assert "directstorage_io" not in accounted(
        platforms=["pc_linux"], render_api="vulkan",
    )
