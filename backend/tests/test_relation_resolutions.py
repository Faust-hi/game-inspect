"""Решение связей и метаданные карточки метода (офлайн).

Дефекты, которые здесь защищаются:

* связь без рекомендации «что делать» — спецификация (стр. 142) требует у
  каждой связи решение или workaround, а паки описывают только причину связи;
* решение без основания — выведенное из типа связи неотличимо от
  документированного, то есть выглядит подтверждённым без подтверждения;
* поля карточки метода, объявленные спецификацией («варианты реализации»,
  «условия применимости», «требуемые данные и инструменты»), которые есть в
  исследованиях, но не переносятся в базу;
* симметричная связь, записанная дважды в обе стороны: повторная загрузка
  пакетов добавляла обратную пару, которой нет при сборке с нуля, и в графе
  появлялось лишнее ребро.
"""
from __future__ import annotations

from sqlalchemy import or_, select

from app.models.entities import Conflict, DependencyEdge, Method

#: Допустимые основания. Значение вне списка означает, что основание
#: проставлено произвольно и не может быть проверено читателем карточки.
KNOWN_BASIS = frozenset({
    "documented", "measured", "derived", "case_evidence", "expert_estimate", "unknown",
})

#: Типы связей без направления: «A дополняет B» и «B дополняет A» — одно
#: отношение, а не два.
SYMMETRIC_TYPES = frozenset({"complement", "alternative", "hard_conflict", "risk"})


def test_every_conflict_has_resolution_and_basis(db):
    """У каждой связи есть решение и явное основание решения."""
    rows = list(db.scalars(select(Conflict)))
    assert rows
    missing = [c.a_code for c in rows if not (c.resolution or "").strip()]
    assert missing == [], f"связи без решения: {len(missing)}, например {missing[:5]}"
    bad = [c.a_code for c in rows if (c.basis or "").strip() not in KNOWN_BASIS]
    assert bad == [], f"решение без корректного основания: {len(bad)}, например {bad[:5]}"


def test_every_dependency_edge_has_workaround_and_basis(db):
    """У каждого ребра графа есть обходной путь и явное основание."""
    rows = list(db.scalars(select(DependencyEdge)))
    assert rows
    missing = [e.dependency_type for e in rows if not (e.workaround or "").strip()]
    assert missing == [], f"рёбра без обходного пути: {len(missing)}"
    bad = [e.dependency_type for e in rows if (e.basis or "").strip() not in KNOWN_BASIS]
    assert bad == [], f"обход без корректного основания: {len(bad)}"


def test_method_card_metadata_is_loaded(db):
    """Варианты реализации, условия применимости и требуемые данные перенесены.

    Данные есть в паках у каждого метода; пустое поле означало бы, что
    загрузчик их не читает, а не что данных нет.
    """
    rows = list(db.scalars(select(Method)))
    assert rows
    no_variants = [m.code for m in rows if not (m.implementation_variants or [])]
    no_conditions = [m.code for m in rows if not (m.requires_conditions or [])]
    no_required = [m.code for m in rows if not (m.required_data_and_tools or "").strip()]
    assert no_variants == [], f"методы без вариантов реализации: {len(no_variants)}"
    assert no_conditions == [], f"методы без условий применимости: {len(no_conditions)}"
    assert no_required == [], f"методы без требуемых данных: {len(no_required)}"

    for method in rows:
        for variant in method.implementation_variants:
            assert isinstance(variant, dict), f"{method.code}: вариант не объект"
            assert (variant.get("name") or "").strip(), f"{method.code}: вариант без имени"
            assert (variant.get("description") or "").strip(), f"{method.code}: вариант без описания"
            assert (variant.get("basis") or "").strip() in KNOWN_BASIS, (
                f"{method.code}: неизвестное основание варианта {variant.get('basis')!r}"
            )


def test_no_symmetric_relation_is_recorded_twice(db):
    """Симметричная связь не дублируется обратной парой.

    Дефект: сессия создаётся с `autoflush=False`, поэтому проверка
    существования не видела строку, добавленную в том же проходе. Повторная
    загрузка пакетов создавала «B дополняет A» рядом с «A дополняет B»,
    и в графе появлялось ребро, которого нет при сборке с нуля.
    """
    keys = {(c.a_code, c.b_code, c.conflict_type) for c in db.scalars(select(Conflict))}
    duplicated = sorted(
        key for key in keys
        if key[2] in SYMMETRIC_TYPES and (key[1], key[0], key[2]) in keys
    )
    assert duplicated == [], f"симметричная связь записана дважды: {duplicated[:5]}"


def test_symmetric_relation_declared_from_both_sides_is_one_record(db):
    """Прямая проверка загрузчика: связь с двух сторон — одна запись."""
    from app.seed.pack_loader import _upsert_relation

    a_code, b_code = "sprite_atlas_batching", "hair_strand_simulation"
    # Возможная связь пары из каталога убирается в транзакции теста, чтобы
    # результат не зависел от текущего содержимого базы.
    for row in db.scalars(select(Conflict).where(
        Conflict.conflict_type == "complement",
        or_(Conflict.a_code.in_([a_code, b_code]), Conflict.b_code.in_([a_code, b_code])),
    )):
        db.delete(row)
    db.flush()

    known = {code for (code,) in db.execute(select(Method.code)).all()}
    assert {a_code, b_code} <= known, "методы проверки должны быть в каталоге"

    seen: set[tuple[str, str, str]] = set()
    first = _upsert_relation(db, a_code, b_code, "complement", "проверка", "", known, seen)
    second = _upsert_relation(db, b_code, a_code, "complement", "проверка", "", known, seen)
    assert first is True
    assert second is False, "обратная пара симметричной связи не должна создаваться"


def test_startup_sync_does_not_change_seeded_relations(db_session):
    """Стартовая синхронизация не расходится с полным заполнением.

    Дефект: коррекции связей выполнялись после загрузки пакетов и удаляли
    связь, объявленную пакетом, а разрыв циклов после этого не повторялся.
    При каждом старте приложения возвращались обязательные циклы и связи без
    решения — то есть заполнение отменялось самим запуском сервиса.
    """
    from app.seed import seeder

    before = {(c.a_code, c.b_code, c.conflict_type) for c in db_session.scalars(select(Conflict))}
    seeder.sync_function_taxonomy(db_session)
    after = {(c.a_code, c.b_code, c.conflict_type) for c in db_session.scalars(select(Conflict))}
    assert after == before, (
        f"стартовая синхронизация изменила связи: "
        f"потеряно {sorted(before - after)[:5]}, добавлено {sorted(after - before)[:5]}"
    )


def test_startup_sync_leaves_no_unresolved_relations(db_session):
    """После стартовой синхронизации у каждой связи есть решение и основание."""
    from app.seed import seeder

    seeder.sync_function_taxonomy(db_session)
    rows = list(db_session.scalars(select(Conflict)))
    assert rows
    assert all((c.resolution or "").strip() for c in rows)
    assert all((c.basis or "").strip() in KNOWN_BASIS for c in rows)


def test_resolution_pass_does_not_overwrite_curated_text(db):
    """Повторный проход заполняет только пустое: правка администратора цела."""
    from app.seed.relation_resolutions import apply_relation_resolutions

    row = db.scalar(select(Conflict).where(Conflict.conflict_type == "risk"))
    assert row is not None
    row.resolution = "Курируемый текст администратора."
    row.basis = "documented"
    db.flush()

    apply_relation_resolutions(db)

    assert row.resolution == "Курируемый текст администратора."
    assert row.basis == "documented"


def test_method_card_api_exposes_research_metadata(client):
    """Карточка метода отдаёт варианты реализации и требуемые данные."""
    methods = client.get("/api/catalog/methods").json()
    assert methods
    item = next(m for m in methods if m["implementation_variants"])
    variant = item["implementation_variants"][0]
    assert variant["name"].strip()
    assert variant["description"].strip()
    assert variant["basis"] in KNOWN_BASIS
    assert isinstance(variant["evidence"], list)
    assert item["required_data_and_tools"].strip()


def test_conflicts_api_exposes_resolution_and_basis(client):
    """Экран связей получает решение и его основание, а не только причину."""
    conflicts = client.get("/api/catalog/conflicts").json()
    assert conflicts
    assert all(c["resolution"].strip() for c in conflicts)
    assert all(c["basis"] in KNOWN_BASIS for c in conflicts)


def test_dependencies_api_exposes_workaround_and_basis(client):
    """Граф зависимостей отдаёт обходной путь и его основание."""
    graph = client.get("/api/catalog/dependencies").json()
    edges = graph["edges"] if isinstance(graph, dict) else graph
    assert edges
    assert all(e["workaround"].strip() for e in edges)
    assert all(e["basis"] in KNOWN_BASIS for e in edges)


def test_derived_basis_requires_a_source(db):
    """«Выведено» означает «связь с источником»: без источника так помечать нельзя.

    Дефект: шаблонный обходной путь помечался `derived` независимо от наличия
    источника, поэтому одно и то же ребро получало разное основание в
    зависимости от того, был ли обходной путь уже заполнен. Пользовательская
    зависимость без публичного источника выглядела подтверждённой документом.
    """
    bad_conflicts = [
        c.a_code for c in db.scalars(select(Conflict))
        if (c.basis or "") == "derived"
        and (not (c.source_url or "").strip() or (c.source_url or "").startswith("user_defined:"))
    ]
    assert bad_conflicts == [], (
        f"конфликты помечены выведенными без источника: {len(bad_conflicts)}"
    )
    bad_edges = [
        e.dependency_type for e in db.scalars(select(DependencyEdge))
        if (e.basis or "") == "derived" and not e.source_id
    ]
    assert bad_edges == [], f"рёбра помечены выведенными без источника: {len(bad_edges)}"


def test_hardware_benchmark_claim_matches_its_row(db):
    """Производное утверждение об индексе железа не расходится со строкой.

    Дефект: утверждение создавалось до того, как строка железа получала точные
    значения бенчмарка, и оставалось с прежним контекстом — карточка показывала
    контекст, противоречащий строке, из которой индекс посчитан.
    """
    from app.models.entities import EvidenceClaim, HardwareCPU

    rows = list(db.scalars(select(HardwareCPU)))
    assert rows
    checked = 0
    for item in rows:
        claim = db.scalar(select(EvidenceClaim).where(
            EvidenceClaim.code == f"hardware_cpu:{item.model}:benchmark_index"
        ))
        if claim is None:
            continue
        checked += 1
        assert claim.context == (item.benchmark_context or ""), (
            f"{item.model}: контекст утверждения расходится со строкой железа"
        )
        assert claim.input_parameters.get("benchmark_name") == (item.benchmark_name or ""), (
            f"{item.model}: имя бенчмарка в утверждении расходится со строкой железа"
        )
    assert checked, "не найдено ни одного утверждения об индексе железа"


def test_seed_applies_researched_confidence(db):
    """Полное заполнение поднимает confidence методов с опубликованным источником.

    Дефект: пачка исправлений выполнялась только стартовой синхронизацией,
    поэтому свежая база оставляла 13 методов на значении по умолчанию 0.5 —
    метод с опубликованным источником выглядел менее подтверждённым, чем есть.
    """
    from app.seed.fixes_v2 import CONFIDENCE_UPGRADES

    for code, (expected, _reason) in CONFIDENCE_UPGRADES.items():
        row = db.scalar(select(Method).where(Method.code == code))
        if row is None or row.confidence is None:
            continue
        assert row.confidence >= expected, (
            f"{code}: confidence {row.confidence} ниже исследованного {expected}"
        )


def test_relation_pass_repairs_basis_without_source(db):
    """Согласующий проход чинит основание, противоречащее наличию источника."""
    from app.seed.relation_resolutions import apply_relation_resolutions

    edge = db.scalar(select(DependencyEdge).where(DependencyEdge.source_id.is_(None)))
    assert edge is not None, "нужно ребро без источника"
    edge.basis = "derived"
    db.flush()

    apply_relation_resolutions(db)

    assert edge.basis == "expert_estimate", (
        "ребро без источника не должно оставаться «выведенным»"
    )


def test_repeat_seed_repairs_stale_derived_claim(db_session):
    """Повторный проход возвращает расходящееся утверждение к строке-источнику."""
    from app.models.entities import EvidenceClaim, HardwareCPU
    from app.seed import seeder

    item = db_session.scalars(select(HardwareCPU)).first()
    claim = db_session.scalar(select(EvidenceClaim).where(
        EvidenceClaim.code == f"hardware_cpu:{item.model}:benchmark_index"
    ))
    assert claim is not None
    claim.context = "Устаревший контекст."
    db_session.flush()

    seeder.sync_function_taxonomy(db_session)

    assert claim.context == (item.benchmark_context or ""), (
        "повторный проход не согласовал утверждение со строкой железа"
    )
