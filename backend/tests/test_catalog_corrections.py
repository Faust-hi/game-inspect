"""Исправления каталога обязаны доходить до уже существующей базы.

Полный сид сохраняет существующие записи, чтобы не стереть административные
правки. Оборотная сторона: правка каталога сама по себе в существующую базу не
попадает — сид честно сообщает расхождение и идёт дальше. Для курируемых
исправлений поэтому есть отдельные проходы. Эти тесты фиксируют, что проходы
существуют и работают: иначе база, собранная с нуля, и база, обновлённая
сидом, расходятся, и расхождение видно только в планировщике.
"""
from __future__ import annotations

import pytest

from sqlalchemy import select

from app.models.entities import Conflict, DependencyEdge, GameFunction, Method, TechnologyNode
from app.seed.corrections import CONTRADICTORY_RELATIONS, correct_contradictory_relations
from app.seed.fixes_v2 import PLATFORM_CORRECTIONS, correct_method_taxonomy


def _edge_count(db, source_code: str, target_code: str, kind: str) -> int:
    src = db.scalar(select(TechnologyNode).where(TechnologyNode.code == f"method:{source_code}"))
    dst = db.scalar(select(TechnologyNode).where(TechnologyNode.code == f"method:{target_code}"))
    if src is None or dst is None:
        return 0
    return db.scalar(
        select(DependencyEdge).where(
            DependencyEdge.source_node_id == src.id,
            DependencyEdge.target_node_id == dst.id,
            DependencyEdge.dependency_type == kind,
        )
    ) is not None


# --- противоречивые связи (N6) -------------------------------------------


@pytest.mark.critical
def test_contradictory_relation_is_withdrawn_with_its_edge(db_session):
    """Снятая связь исчезает вместе с ребром графа.

    `sync_dependency_graph` только добавляет рёбра, поэтому без явного удаления
    ребро пережило бы строку-основание и продолжало бы управлять порядком
    внедрения — связь «снята», а корзина всё ещё её слушается.
    """
    spec = CONTRADICTORY_RELATIONS[0]
    db_session.add(Conflict(
        a_code=spec["a_code"], b_code=spec["b_code"], conflict_type=spec["conflict_type"],
        severity=3, description=spec["description"], resolution="", status="published",
        source_url="", basis="expert_estimate",
    ))
    db_session.flush()
    source = db_session.scalar(
        select(TechnologyNode).where(TechnologyNode.code == f"method:{spec['a_code']}"))
    target = db_session.scalar(
        select(TechnologyNode).where(TechnologyNode.code == f"method:{spec['b_code']}"))
    db_session.add(DependencyEdge(
        source_node_id=source.id, target_node_id=target.id,
        dependency_type=spec["conflict_type"], mandatory=1, scope="runtime", severity=2,
        description="", workaround="", status="published", basis="expert_estimate",
    ))
    db_session.flush()

    assert correct_contradictory_relations(db_session) >= 1
    assert db_session.scalar(select(Conflict).where(
        Conflict.a_code == spec["a_code"],
        Conflict.b_code == spec["b_code"],
        Conflict.conflict_type == spec["conflict_type"],
    )) is None, "строка связи осталась в базе"
    assert not _edge_count(db_session, spec["a_code"], spec["b_code"], spec["conflict_type"]), (
        "ребро пережило строку-основание"
    )


@pytest.mark.extended
def test_contradictory_relation_correction_is_idempotent(db_session):
    """Повторный проход ничего не снимает: снятое уже снято."""
    assert correct_contradictory_relations(db_session) == 0


@pytest.mark.extended
def test_every_declared_removal_names_a_reason():
    """Снятие связи описано текстом, а не только парой кодов.

    Удаление по одной паре затронуло бы и осознанную правку администратора с
    другим текстом: описание — это и есть граница применения.
    """
    for spec in CONTRADICTORY_RELATIONS:
        assert spec["description"].strip(), f"снятие {spec['a_code']} без описания"
        assert spec["conflict_type"]


# --- таксономия методов (E5) ---------------------------------------------


@pytest.mark.critical
def test_platform_correction_reaches_an_existing_row(db_session):
    """Список платформ исправляется и в уже существующей записи.

    Без прохода правка каталога остаётся невидимой: метод не попадал в подбор
    для профиля с PS5, хотя профиль объявлял ту подсистему, которую метод
    должен закрывать.
    """
    code, (old, new) = next(iter(PLATFORM_CORRECTIONS.items()))
    row = db_session.scalar(select(Method).where(Method.code == code))
    row.applicable_platforms = list(old)
    db_session.flush()

    assert correct_method_taxonomy(db_session) >= 1
    assert sorted(row.applicable_platforms) == sorted(new)


@pytest.mark.critical
def test_platform_correction_leaves_a_foreign_value_alone(db_session):
    """Осознанно изменённый список платформ не затирается."""
    code, (_old, _new) = next(iter(PLATFORM_CORRECTIONS.items()))
    row = db_session.scalar(select(Method).where(Method.code == code))
    row.applicable_platforms = ["pc_windows"]
    db_session.flush()

    assert correct_method_taxonomy(db_session) >= 0
    assert list(row.applicable_platforms) == ["pc_windows"], "ручная правка затрётся проходом"


@pytest.mark.extended
def test_taxonomy_correction_is_idempotent(db_session):
    """Повторный проход ничего не меняет."""
    assert correct_method_taxonomy(db_session) == 0


@pytest.mark.extended
def test_virtualized_geometry_is_a_geometry_pipeline_method(db_session):
    """Метод числится в той подсистеме, которую закрывает.

    Под `large_scale_terrain` метод не попадал в корзину профилей, которые
    объявляли `geometry_pipeline` и использовали виртуализированную геометрию.
    """
    row = db_session.scalar(select(Method).where(Method.code == "virtual_geometry_clusters"))
    function = db_session.scalar(select(GameFunction).where(GameFunction.id == row.function_id))

    assert function.code == "geometry_pipeline"
