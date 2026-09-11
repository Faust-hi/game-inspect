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

    Профиль объявляет `geometry_pipeline`, а не `large_scale_terrain`:
    виртуализированная геометрия — приём конвейера геометрии, а не ландшафта.
    До исправления таксономии метод числился под `large_scale_terrain`, и проект
    с объявленным конвейером геометрии не получал его в рекомендациях вовсе.
    """
    response = _post(client, "/api/recommend", engine_version="4.27",
                     functions=["geometry_pipeline"])
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
        "functions": ["geometry_pipeline"],
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
            # `procedural_terrain` нужен предусловию DirectStorage — бюджету
            # генерации и кэша чанков: без выбранной функции метод исключается
            # как неприменимый, и до платформенного условия дело не доходит.
            "functions": ["audio_system", "open_world_streaming", "procedural_terrain"],
            "multiplayer": True, "player_count": 8,
            "render_api": "dx12", "world_type": "open_world",
        }
        profile.update(changes)
        # DirectStorage объявлен зависимым от слоя асинхронной загрузки: без
        # предусловия решение исключается целиком, и тест проверял бы правило
        # зависимостей, а не платформенное условие. Предусловия добавляются,
        # чтобы измерялось именно условие Windows/DX12.
        data = client.post(
            "/api/recommend",
            json={
                "profile": profile,
                "basket": [
                    "async_loading_pipeline",
                    "terrain_generation_streaming_budget",
                    "directstorage_io",
                ],
            },
        ).json()
        return data["accounted_method_codes"]

    assert "directstorage_io" in accounted(
        platforms=["pc_windows"], render_api="dx12", storage_type="hdd",
    )
    assert "directstorage_io" not in accounted(
        platforms=["pc_linux"], render_api="vulkan",
    )


def test_unlinked_methods_are_explicitly_engine_independent(client):
    """Несвязанные с инструментами методы помечены: «не нужен» ≠ «данных нет».

    Дефект: пустая привязка к версии движка читалась одинаково и для решений
    поверх движка (сетевой код, античит, DirectStorage), и для возможного
    пробела каталога — пользователь не мог их различить.
    """
    methods = client.get("/api/catalog/methods").json()
    unlinked = {m["code"] for m in methods if not m["engine_links"]}
    marked = {m["code"] for m in methods if m["engine_tool_independent"]}
    # Каждое отсутствие связей объяснено признаком (множества совпадают
    # и непусты — иначе проверка выродилась бы в сравнение двух пустот).
    assert unlinked and unlinked == marked
    # Признак не врёт о методах со связями: они опираются на инструмент.
    linked = [m for m in methods if m["engine_links"]]
    assert linked and not any(m["engine_tool_independent"] for m in linked)


def test_recommendation_names_independence_not_gap(client):
    """В выдаче рекомендаций пустая поддержка движка помечается признаком.

    Дефект: элемент рекомендации не отличал «методу не нужен встроенный
    инструмент» от «данных нет» — то же поле, что и в карточке каталога.
    """
    response = _post(
        client, "/api/recommend",
        functions=["large_scale_terrain", "audio_system", "open_world_streaming"],
        multiplayer=True, player_count=32, storage_type="hdd", render_api="dx12",
    )
    assert response.status_code == 200, response.text
    items = response.json()["recommendations"]
    unsupported = [i for i in items if i["engine_support"] is None]
    assert unsupported, "ожидался метод без встроенного аналога в выдаче"
    assert all(i["engine_tool_independent"] for i in unsupported)


def test_seed_validation_distinguishes_independence(db):
    """Правило целостности различает пробел и осознанное отсутствие связей.

    Дефект: предупреждение «нет связей» было ложным для решений поверх
    движка и настоящий пробел данных тонул в них; противоречие «признак
    есть и связи есть» не замечалось вовсе.
    """
    from sqlalchemy import select

    from app.models.entities import Method, MethodEngineLink
    from app.seed import seeder

    # Сид согласован: несвязанных методов без признака нет.
    base = seeder.validate_knowledge_base(db)
    assert not [e for e in base if "нет связей с инструментами" in e["message"]]

    # Пробел: у метода со связями связи удалены, признака нет — предупреждение.
    method = db.scalar(select(Method).where(Method.code == "virtual_geometry_clusters"))
    links = db.scalars(
        select(MethodEngineLink).where(MethodEngineLink.method_id == method.id)
    ).all()
    donor_tool_id = links[0].tool_id
    for link in links:
        db.delete(link)
    db.flush()
    entries = seeder.validate_knowledge_base(db)
    assert any(
        e["entity_code"] == "virtual_geometry_clusters" and e["severity"] == "warning"
        and "нет связей с инструментами" in e["message"]
        for e in entries
    )

    # Противоречие: независимому методу добавлена связь — ошибка.
    independent = db.scalar(select(Method).where(Method.code == "directstorage_io"))
    db.add(MethodEngineLink(
        method_id=independent.id, tool_id=donor_tool_id,
        relation_type="direct", note="противоречие для проверки", status="published",
    ))
    db.flush()
    entries = seeder.validate_knowledge_base(db)
    assert any(
        e["entity_code"] == "directstorage_io" and e["severity"] == "error"
        and "помечен не зависящим" in e["message"]
        for e in entries
    )


def test_independence_sync_repairs_existing_database(db):
    """Синхронизация доносит признак до существующих баз и не трогает чужое.

    Дефект: колонку добавляет миграция со значением по умолчанию «ложь» —
    у рабочей базы все несвязанные методы остались бы неотмеченными,
    и различие «не нужен» / «данных нет» действовало бы только на новых
    установках. Значение True вне списка каталога сохраняется: его мог
    поставить администратор осознанно.
    """
    from sqlalchemy import select

    from app.models.entities import Method
    from app.seed.corrections import correct_engine_tool_independence

    # Существующая база до синхронизации: колонку добавила миграция,
    # у всех записей значение по умолчанию «ложь».
    for row in db.scalars(select(Method)).all():
        row.engine_tool_independent = False
    db.flush()
    # Администраторская правка: признак у метода, которого нет в списке
    # каталога, — синхронизация обязана его сохранить.
    admin_row = db.scalar(select(Method).where(Method.code == "bindless_uber_shaders"))
    admin_row.engine_tool_independent = True
    db.flush()

    updated = correct_engine_tool_independence(db)

    codes = {
        m.code for m in db.scalars(
            select(Method).where(Method.engine_tool_independent.is_(True))
        ).all()
    }
    from app.seed.methods_data import ENGINE_TOOL_INDEPENDENT
    assert updated == len(ENGINE_TOOL_INDEPENDENT)
    assert codes == set(ENGINE_TOOL_INDEPENDENT) | {"bindless_uber_shaders"}
