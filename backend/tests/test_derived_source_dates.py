"""Производные копии даты источника и оговорка в описании ребра графа.

Дата источника живёт в трёх местах: запись реестра (`evidence_sources`) и две
производные копии (`methods.source_date`, `game_functions.source_date`). Проход
`correct_placeholder_source_dates` долго правил только первую, поэтому 155 строк
держали заглушку «1 января» при объявленном `n/a`. Тесты фиксируют, что правило
теперь доходит до копий и при этом не трогает настоящую дату.

Второй предмет — оговорка «и помечен как пользовательская технология» в описании
ребра «инструмент → движок»: каталог добавил её позже самих рёбер.
"""
from __future__ import annotations

from sqlalchemy import select

from app.models.entities import (
    DependencyEdge, Engine, EngineTool, EvidenceSource, GameFunction, Method,
    TechnologyNode,
)
from app.seed import corrections, sources
from app.seed.dependency_graph import tool_engine_description
from app.seed.evidence_catalog import EXTRA_SOURCES

MARKER = "[expert_estimate:no_external_source]"

#: Адрес, который делят две записи реестра с разными датами. По нему замена не
#: делается: выбрать одну из двух дат значило бы выдумать.
AMBIGUOUS_URL = "https://www.counter-strike.net/cs2"


def _registry_by_url() -> dict[str, set[str]]:
    out: dict[str, set[str]] = {}
    for record in {**sources.SOURCES, **EXTRA_SOURCES}.values():
        url = (record.get("url") or "").strip()
        date = (record.get("date") or "").strip()
        if url and date:
            out.setdefault(url, set()).add(date)
    return out


def _method_with_unambiguous_source(db_session, *, dated: bool = False):
    """Метод, источник которого разрешается в реестре однозначно.

    `dated=True` требует источника с объявленной **настоящей** датой: только на
    нём проверяется, что курированное значение переживает проход. У источников
    с объявленным `n/a` конкретная дата заменяется по правилу (см.
    `test_concrete_date_yields_to_declared_absence`).
    """
    by_url = _registry_by_url()
    for row in db_session.scalars(select(Method)):
        dates = by_url.get((row.source_url or "").strip())
        if not dates or len(dates) != 1:
            continue
        value = dates.pop()
        if dated and value == "n/a":
            continue
        return row, value
    raise AssertionError("в каталоге нет метода с подходящим источником")


def test_placeholder_date_on_method_is_replaced(db_session):
    """Заглушка «1 января» заменяется объявленным значением реестра."""
    row, expected = _method_with_unambiguous_source(db_session)
    row.source_date = "2025-01-01"
    db_session.flush()

    assert corrections.correct_placeholder_source_dates(db_session) >= 1
    assert row.source_date == expected


def test_verification_date_on_method_is_replaced(db_session):
    """Дата проверки ссылки, выданная за публикацию, тоже заменяется."""
    row, expected = _method_with_unambiguous_source(db_session)
    row.source_date = "2026-09-09"
    db_session.flush()

    corrections.correct_placeholder_source_dates(db_session)
    assert row.source_date == expected


def test_curated_date_on_method_survives(db_session):
    """Настоящая дата у источника с объявленной датой не трогается."""
    row, _ = _method_with_unambiguous_source(db_session, dated=True)
    row.source_date = "2019-09-17"
    db_session.flush()

    corrections.correct_placeholder_source_dates(db_session)
    assert row.source_date == "2019-09-17"


def test_concrete_date_yields_to_declared_absence(db_session):
    """Конкретная дата у источника с объявленным `n/a` заменяется.

    Это не потеря правки, а смысл правила: реестр объявил, что даты публикации
    у источника не существует, поэтому любое число здесь — заглушка либо дата
    проверки ссылки. Так же ведёт себя проход и для самих записей реестра.
    """
    by_url = _registry_by_url()
    row = next(
        (m for m in db_session.scalars(select(Method))
         if by_url.get((m.source_url or "").strip()) == {"n/a"}),
        None,
    )
    assert row is not None, "нет метода с объявленным отсутствием даты"
    row.source_date = "2023-03-22"
    db_session.flush()

    corrections.correct_placeholder_source_dates(db_session)
    assert row.source_date == "n/a"


def test_empty_date_on_method_is_filled(db_session):
    """Пустое поле заполняется: реестр значение объявляет.

    Пустое поле проект относит к другой категории — «дата неизвестна», тогда
    как у этих источников дата объявлена как отсутствующая (`n/a`). У методов
    прохода «заполнить пустое» нет вовсе, поэтому закрывает его этот проход.
    """
    row, expected = _method_with_unambiguous_source(db_session)
    row.source_date = ""
    db_session.flush()

    corrections.correct_placeholder_source_dates(db_session)
    assert row.source_date == expected


def test_placeholder_date_on_function_is_replaced(db_session):
    """Копия даты у игровой функции правится тем же правилом."""
    by_url = _registry_by_url()
    row = next(
        (f for f in db_session.scalars(select(GameFunction))
         if by_url.get((f.source_url or "").strip())),
        None,
    )
    assert row is not None, "в каталоге нет функции с источником из реестра"
    expected = by_url[(row.source_url or "").strip()].pop()
    row.source_date = "2025-01-01"
    db_session.flush()

    corrections.correct_placeholder_source_dates(db_session)
    assert row.source_date == expected


def test_ambiguous_url_is_not_resolved(db_session):
    """Адрес с двумя разными датами не разрешается вовсе."""
    row, _ = _method_with_unambiguous_source(db_session)
    row.source_url = AMBIGUOUS_URL
    row.source_date = "2025-01-01"
    db_session.flush()

    corrections.correct_placeholder_source_dates(db_session)
    assert row.source_date == "2025-01-01"


def test_derived_date_pass_is_idempotent(db_session):
    """Повторный прогон ничего не меняет."""
    row, expected = _method_with_unambiguous_source(db_session)
    row.source_date = "2025-01-01"
    db_session.flush()

    assert corrections.correct_placeholder_source_dates(db_session) >= 1
    assert row.source_date == expected
    assert corrections.correct_placeholder_source_dates(db_session) == 0


def test_technology_node_url_is_repaired(db_session):
    """Переезд страницы вендора доезжает и до узла технологии."""
    old_url, new_url = next(iter(corrections.SOURCE_URL_REPLACEMENTS.items()))
    node = db_session.scalars(select(TechnologyNode)).first()
    node.docs_url = old_url
    db_session.flush()

    assert corrections.repair_dead_source_urls(db_session) >= 1
    assert node.docs_url == new_url


def _engine_edge(db_session) -> tuple[DependencyEdge, EngineTool, Engine]:
    nodes = {node.id: node.code for node in db_session.scalars(select(TechnologyNode))}
    tools = {tool.code: tool for tool in db_session.scalars(select(EngineTool))}
    engines = {engine.code: engine for engine in db_session.scalars(select(Engine))}
    for edge in db_session.scalars(
        select(DependencyEdge).where(DependencyEdge.dependency_type == "engine")
    ):
        src = nodes.get(edge.source_node_id, "")
        dst = nodes.get(edge.target_node_id, "")
        tool = tools.get(src[len("tool:"):]) if src.startswith("tool:") else None
        engine = engines.get(dst[len("engine:"):]) if dst.startswith("engine:") else None
        if tool is not None and engine is not None and tool.is_user_defined:
            return edge, tool, engine
    raise AssertionError("в графе нет ребра «пользовательский инструмент → движок»")


def test_tool_engine_note_is_refreshed(db_session):
    """Прежний вид фразы заменяется видом с оговоркой."""
    edge, tool, engine = _engine_edge(db_session)
    old_text = tool_engine_description(tool.name, engine.name, is_user_defined=False)
    new_text = tool_engine_description(tool.name, engine.name, is_user_defined=True)

    edge.description = f"{MARKER} {old_text} Пояснение про источник."
    db_session.flush()

    assert corrections.refresh_tool_engine_notes(db_session) >= 1
    assert new_text in edge.description
    assert old_text not in edge.description
    # Пояснение о причине отсутствия источника сохраняется.
    assert "Пояснение про источник." in edge.description


def test_edited_edge_description_is_not_touched(db_session):
    """Описание, поправленное человеком, не переписывается."""
    edge, _, _ = _engine_edge(db_session)
    edge.description = f"{MARKER} Курированное описание ребра, сверено вручную."
    db_session.flush()

    assert corrections.refresh_tool_engine_notes(db_session) == 0
    assert edge.description == f"{MARKER} Курированное описание ребра, сверено вручную."


def test_tool_engine_note_pass_is_idempotent(db_session):
    """Повторный прогон не находит работы."""
    assert corrections.refresh_tool_engine_notes(db_session) == 0


def _legacy_record_row(db_session):
    code = next(iter(corrections.SOURCE_RECORD_LEGACY))
    row = db_session.scalars(select(EvidenceSource).where(EvidenceSource.code == code)).first()
    assert row is not None, f"нет записи {code}"
    for field, value in corrections.SOURCE_RECORD_LEGACY[code].items():
        setattr(row, field, value)
    db_session.flush()
    return code, row


def test_legacy_source_record_is_repaired(db_session):
    """Запись, починенная каталогом, доезжает до уже собранной базы.

    `_upsert_source` существующую строку не обновляет, поэтому без этого прохода
    свежая установка и рабочая база расходились бы: заголовок Digital Foundry
    остался бы стоять на URL Wikipedia, а локатор сообщал бы о 404.
    """
    code, row = _legacy_record_row(db_session)

    assert corrections.correct_source_records(db_session) >= 1
    assert row.title != corrections.SOURCE_RECORD_LEGACY[code]["title"]
    assert row.locator != corrections.SOURCE_RECORD_LEGACY[code]["locator"]
    # Запись перестаёт себе противоречить: заголовок соответствует адресу.
    assert "Wikipedia" in row.title
    assert "404" not in (row.locator or "")


def test_edited_source_record_is_not_touched(db_session):
    """Запись, поправленную человеком, проход не переписывает."""
    code, row = _legacy_record_row(db_session)
    row.title = "Курированный заголовок, сверено вручную"
    db_session.flush()

    assert corrections.correct_source_records(db_session) == 0
    assert row.title == "Курированный заголовок, сверено вручную"


def test_source_record_pass_is_idempotent(db_session):
    """Повторный прогон не находит работы."""
    _legacy_record_row(db_session)
    assert corrections.correct_source_records(db_session) >= 1
    assert corrections.correct_source_records(db_session) == 0


def test_source_record_pass_keeps_admin_fields(db_session):
    """`notes` и `status` — поля администратора, проход их не трогает."""
    _code, row = _legacy_record_row(db_session)
    row.notes = "Заметка администратора"
    row.status = "draft"
    db_session.flush()

    corrections.correct_source_records(db_session)
    assert row.notes == "Заметка администратора"
    assert row.status == "draft"
