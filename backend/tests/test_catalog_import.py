"""Импорт каталога: типизированные строки, массивы и составной ключ связи."""
from __future__ import annotations

import io
import json

import pytest
from sqlalchemy import select

from app.models.entities import Conflict, Method


def _csv(fieldnames: list[str], rows: list[list[str]]) -> bytes:
    buffer = io.StringIO()
    buffer.write(",".join(fieldnames) + "\n")
    for row in rows:
        buffer.write(",".join(row) + "\n")
    return buffer.getvalue().encode("utf-8")


def _stored_method(db, code: str) -> Method:
    """Импортированные записи — черновики, поэтому смотрим саму запись в базе."""
    method = db.scalar(select(Method).where(Method.code == code))
    assert method is not None, f"метод {code} не сохранён"
    return method


def test_json_arrays_are_preserved_as_lists(client, db):
    """Список из JSON не превращается в строку при сохранении."""
    payload = {"methods": [{
        "code": "tmp_list_method", "name": "Метод со списком",
        "pros": ["быстро", "дёшево"], "requires_hw_features": ["Compute Shaders"],
    }]}
    response = client.post(
        "/api/admin/import/methods",
        files={"file": ("m.json", json.dumps(payload).encode(), "application/json")},
    )
    assert response.status_code == 200, response.text

    method = _stored_method(db, "tmp_list_method")
    assert method.pros == ["быстро", "дёшево"], method.pros
    assert method.requires_hw_features == ["Compute Shaders"], method.requires_hw_features


def test_csv_semicolon_list_becomes_array(client, db):
    """«a;b» в CSV — это список, а не строка.

    Раньше JSON-колонка сообщала `python_type == dict`, проверка на список не
    срабатывала, и значение сохранялось строкой: публичная карточка и правила
    применимости ломались.
    """
    raw = _csv(["code", "name", "pros", "cons"], [
        ["tmp_csv_method", "Метод из CSV", "быстро;дёшево", "шумит"],
    ])
    response = client.post(
        "/api/admin/import/methods",
        files={"file": ("m.csv", raw, "text/csv")},
    )
    assert response.status_code == 200, response.text

    method = _stored_method(db, "tmp_csv_method")
    assert method.pros == ["быстро", "дёшево"], method.pros
    assert method.cons == ["шумит"], method.cons


def test_csv_hardware_gpu_features_are_lists(client):
    raw = _csv(["model", "vendor", "api_support", "hw_features", "raster_score"], [
        ["tmp GPU", "Test", "DirectX 12;Vulkan", "Hardware Ray Tracing", "0.5"],
    ])
    response = client.post(
        "/api/admin/import/hardware_gpu",
        files={"file": ("g.csv", raw, "text/csv")},
    )
    assert response.status_code == 200, response.text


def _ensure_methods(db, *codes: str) -> None:
    """Создать методы-заглушки для проверки ссылок связей.

    Связь обязана ссылаться на существующий каталог: висячая строка
    отклоняется до записи (D24/D25, N08). Поэтому тесты импорта связей
    сначала фиксируют концы в базе, а не полагаются на несуществующие коды.
    """
    for code in codes:
        if db.scalar(select(Method).where(Method.code == code)) is None:
            db.add(Method(code=code, name=f"Метод {code}"))
    db.commit()


def test_conflict_import_uses_composite_key(client, db):
    """Связь импортируется по тройке a_code/b_code/conflict_type.

    У связи нет полей `code`, `model` или `title`, поэтому раньше ключ
    скатывался в несуществующий `title`: строка отклонялась, а при добавлении
    поля импорт отвечал 500.
    """
    _ensure_methods(db, "tmp_alpha", "tmp_beta")
    raw = _csv(["a_code", "b_code", "conflict_type", "severity", "description"], [
        ["tmp_alpha", "tmp_beta", "hard_conflict", "1", "тестовая связь"],
    ])
    response = client.post(
        "/api/admin/import/conflicts",
        files={"file": ("c.csv", raw, "text/csv")},
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["created"] == 1, body


def test_conflict_import_second_time_updates_not_duplicates(client, db):
    """Повторный импорт той же тройки обновляет запись, а не создаёт вторую."""
    _ensure_methods(db, "tmp_gamma", "tmp_delta")
    raw = _csv(["a_code", "b_code", "conflict_type", "severity", "description"], [
        ["tmp_gamma", "tmp_delta", "hard_conflict", "2", "обновлённая связь"],
    ])
    first = client.post(
        "/api/admin/import/conflicts", files={"file": ("c.csv", raw, "text/csv")},
    )
    assert first.json()["created"] == 1, first.text

    second = client.post(
        "/api/admin/import/conflicts", files={"file": ("c.csv", raw, "text/csv")},
    )
    assert second.status_code == 200, second.text
    assert second.json()["updated"] == 1, second.text

    stored = db.scalars(
        select(Conflict).where(Conflict.a_code == "tmp_gamma", Conflict.b_code == "tmp_delta")
    ).all()
    assert len(stored) == 1, "составной ключ не должен создавать дубликаты"


def test_conflict_row_without_composite_key_is_rejected(client):
    raw = _csv(["a_code", "b_code", "conflict_type"], [["tmp_alpha", "tmp_beta", ""]])
    response = client.post(
        "/api/admin/import/conflicts", files={"file": ("c.csv", raw, "text/csv")},
    )

    assert response.status_code == 422
    body = response.json()
    assert isinstance(body["error"], str)
    assert any("ключ" in str(item) for item in body["details"]), body["details"]


def test_bad_list_value_is_reported_before_writing(client):
    """Непроверенная структура отклоняется до записи, а не ломает каталог."""
    payload = {"methods": [{"code": "tmp_bad_list", "name": "Плохая строка", "pros": 5}]}
    response = client.post(
        "/api/admin/import/methods",
        files={"file": ("m.json", json.dumps(payload).encode(), "application/json")},
    )

    assert response.status_code == 422, response.text
    assert response.json()["details"]


@pytest.mark.parametrize("entity,fieldnames,row", [
    ("methods", ["code", "name"], ["tmp_x", "X"]),
    ("hardware_cpu", ["model", "vendor"], ["tmp CPU", "Test"]),
    ("hardware_gpu", ["model", "vendor"], ["tmp GPU 2", "Test"]),
])
def test_missing_key_is_reported_per_row(client, entity, fieldnames, row):
    raw = _csv(fieldnames, [row, ["", "без ключа"]])
    response = client.post(
        f"/api/admin/import/{entity}", files={"file": ("f.csv", raw, "text/csv")},
    )

    assert response.status_code == 422, response.text
    assert any("ключ" in str(item) for item in response.json()["details"])


def test_dict_inside_list_is_rejected_before_writing(client, db):
    """Словарь в массиве не превращается в строку через str().

    Регрессия аудита этапа 1: pros=[{"bad": "structure"}] раньше сохранялся
    как "{'bad': 'structure'}", теперь файл отклоняется целиком и ничего
    не записывает.
    """
    payload = {"methods": [{
        "code": "tmp_dict_in_list", "name": "Словарь в списке",
        "pros": [{"bad": "structure"}],
    }]}
    response = client.post(
        "/api/admin/import/methods",
        files={"file": ("m.json", json.dumps(payload).encode(), "application/json")},
    )
    assert response.status_code == 422, response.text
    assert response.json()["details"]
    assert db.scalar(select(Method).where(Method.code == "tmp_dict_in_list")) is None


def test_int_inside_list_is_rejected_before_writing(client, db):
    """Число в массиве строк отклоняется, а не приводится молча."""
    payload = {"methods": [{
        "code": "tmp_int_in_list", "name": "Число в списке",
        "pros": ["быстро", 5],
    }]}
    response = client.post(
        "/api/admin/import/methods",
        files={"file": ("m.json", json.dumps(payload).encode(), "application/json")},
    )
    assert response.status_code == 422, response.text
    assert db.scalar(select(Method).where(Method.code == "tmp_int_in_list")) is None


def test_conflict_with_missing_methods_is_rejected(client, db):
    """Связь на несуществующие методы не сохраняется висячей строкой.

    Регрессия аудита этапа 1: импорт audit_missing_a/audit_missing_b раньше
    отвечал 200 и сохранял строку, теперь — 422 без записи.
    """
    raw = _csv(["a_code", "b_code", "conflict_type", "description"], [
        ["audit_missing_a", "audit_missing_b", "conflict", "висячая связь"],
    ])
    response = client.post(
        "/api/admin/import/conflicts", files={"file": ("c.csv", raw, "text/csv")},
    )
    assert response.status_code == 422, response.text
    details = " ".join(str(item) for item in response.json()["details"])
    assert "не найден" in details, details
    assert db.scalars(
        select(Conflict).where(Conflict.a_code == "audit_missing_a")
    ).all() == []


def test_conflict_with_one_missing_end_is_rejected(client, db):
    """Отсутствует хотя бы один конец — отклоняется весь файл."""
    _ensure_methods(db, "tmp_existing_side")
    raw = _csv(["a_code", "b_code", "conflict_type"], [
        ["tmp_existing_side", "tmp_no_such_method", "conflict"],
    ])
    response = client.post(
        "/api/admin/import/conflicts", files={"file": ("c.csv", raw, "text/csv")},
    )
    assert response.status_code == 422, response.text
    assert db.scalars(
        select(Conflict).where(Conflict.a_code == "tmp_existing_side")
    ).all() == []


def test_conflict_self_reference_is_rejected(client, db):
    """Связь метода с самим собой запрещена ограничением базы и проверкой."""
    _ensure_methods(db, "tmp_self_ref")
    raw = _csv(["a_code", "b_code", "conflict_type"], [
        ["tmp_self_ref", "tmp_self_ref", "conflict"],
    ])
    response = client.post(
        "/api/admin/import/conflicts", files={"file": ("c.csv", raw, "text/csv")},
    )
    assert response.status_code == 422, response.text
