"""Загрузчик пакетов не теряет сбойные файлы молча.

Дефект этого класса: исключение при чтении пака просто пропускало файл.
База заполнялась без него, и оператор не видел, что часть доказательной базы
не загружена, — молчаливая потеря данных. Тесты фиксируют, что сбой
возвращается вызывающему коду и попадает в статистику `sync_packs`, а не
исчезает бесследно.
"""
from __future__ import annotations

import json

from app.seed import pack_loader


def test_valid_pack_is_loaded_without_failures(tmp_path, monkeypatch):
    (tmp_path / "pack_ok.json").write_text(
        json.dumps({"sources": [], "methods": {}}), encoding="utf-8"
    )
    monkeypatch.setattr(pack_loader, "PACK_DIR", tmp_path)

    packs, failures = pack_loader._load_packs()

    assert len(packs) == 1
    assert failures == []


def test_malformed_pack_is_reported_not_skipped(tmp_path, monkeypatch):
    """Битый JSON не исчезает: файл назван в списке сбоев."""
    (tmp_path / "pack_ok.json").write_text(json.dumps({"methods": {}}), encoding="utf-8")
    (tmp_path / "pack_broken.json").write_text("{not valid json", encoding="utf-8")
    monkeypatch.setattr(pack_loader, "PACK_DIR", tmp_path)

    packs, failures = pack_loader._load_packs()

    assert len(packs) == 1
    assert [item["file"] for item in failures] == ["pack_broken.json"]
    assert failures[0]["error"]


def test_non_object_pack_is_reported(tmp_path, monkeypatch):
    """JSON неверного вида (не объект) тоже объявляется сбоем."""
    (tmp_path / "pack_list.json").write_text("[1, 2, 3]", encoding="utf-8")
    monkeypatch.setattr(pack_loader, "PACK_DIR", tmp_path)

    packs, failures = pack_loader._load_packs()

    assert packs == []
    assert [item["file"] for item in failures] == ["pack_list.json"]
    assert "объект JSON" in failures[0]["error"]
