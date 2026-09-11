"""Декларации пробелов: законное отсутствие источника объявлено машинно.

Дефект этого класса: записи, у которых источника нет по существу, оставляли
поле пустым, и аудит считал их «незадекларированными дырами»:

* связка «метод-инструмент» с инструментом собственной реализации —
  публичного источника не существует; правильное состояние —
  `evidence_status='user_defined'`, а не пустой URL;
* конфликт, выведенный из структуры каталога («A требует B»), — URL не
  существует, это не факт из документа;
* ребро графа без источника — плановая зависимость пакетов работ;
* сырые значения бенчмарков железа не сохранялись, из-за чего нормализация
  была непроверяема.

Причина дефекта — порядок заполнения: проходы выполнялись до создания самих
сущностей. Эти тесты фиксируют, что декларации присутствуют уже на свежей базе,
а не появляются при повторном заполнении.
"""
from __future__ import annotations

from sqlalchemy import select

from app.models.entities import (
    Conflict, DependencyEdge, EvidenceClaim, HardwareCPU, HardwareGPU,
    MethodEngineLink,
)

#: Префикс, которым помечается плановая зависимость без внешнего источника.
EDGE_MARKER = "[expert_estimate"


def test_user_defined_links_are_declared(db_session):
    """Связка без URL обязана нести явную пометку user_defined."""
    links = db_session.scalars(select(MethodEngineLink)).all()
    assert links
    undeclared = [
        link.code if hasattr(link, "code") else link.id
        for link in links
        if not (link.source_url or "").strip()
        and (link.evidence_status or "") != "user_defined"
    ]
    assert undeclared == [], f"связки без URL и без пометки: {len(undeclared)}"


def test_conflicts_without_url_are_declared(db_session):
    """Конфликт без URL обязан нести декларацию, а не пустое поле."""
    conflicts = db_session.scalars(select(Conflict)).all()
    assert conflicts
    missing = [c.id for c in conflicts if not (c.source_url or "").strip()]
    assert missing == [], f"конфликты без источника и без декларации: {len(missing)}"


def test_dependency_edges_without_source_are_declared(db_session):
    """Ребро графа без источника обязано быть объявлено экспертной оценкой."""
    edges = db_session.scalars(select(DependencyEdge)).all()
    assert edges
    undeclared = [
        e.id for e in edges
        if not e.source_id and EDGE_MARKER not in (e.description or "")
    ]
    assert undeclared == [], f"рёбра без источника и без декларации: {len(undeclared)}"


def test_hardware_rows_carry_raw_benchmark_value(db_session):
    """Нормализованный индекс без исходной величины непроверяем."""
    for model in (HardwareCPU, HardwareGPU):
        rows = db_session.scalars(select(model)).all()
        assert rows, model.__tablename__
        empty = [r.model for r in rows if r.benchmark_raw_value in (None, "", 0)]
        assert empty == [], f"{model.__tablename__} без сырого значения: {len(empty)}"


def test_no_dangling_published_claim(db_session):
    """Публичное утверждение либо имеет источник, либо самообосновано.

    Спека (строка 412): запись валидна при `source` ЛИБО при
    `formula` + `input_parameters`. Собственный расчёт не «висячая ссылка».
    """
    claims = db_session.scalars(
        select(EvidenceClaim).where(EvidenceClaim.status == "published")
    ).all()
    assert claims
    dangling = []
    for c in claims:
        if c.source_id is not None:
            continue
        self_justified = (
            c.basis == "derived"
            and (c.formula or "").strip()
            and bool(c.input_parameters)
        )
        if not self_justified and c.field != "adoption_evidence_gap":
            dangling.append(c.code)
    assert dangling == [], f"висячие утверждения: {dangling[:10]}"
