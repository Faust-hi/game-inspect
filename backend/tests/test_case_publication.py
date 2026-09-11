"""Публикация игровых кейсов: доказательство не должно ссылаться на невидимого родителя.

Дефект этого класса: `pack_loader._upsert_case` создавал кейс без явного
статуса, а `GameCase.status` по умолчанию — `draft`. Публичный слой
(`repositories.game_cases`) фильтрует по статусу, поэтому в API и отчёте были
видны только курируемые кейсы — 8 из 155. Следствие шире одного счётчика:
363 из 375 строк `case_evidence` ссылались на неопубликованного родителя, и
«Сверка с практикой» оставалась пустой в 12 сценариях из 25, хотя само
доказательство было опубликовано.

Тесты фиксируют три вещи:

* кейс получает статус вместе со своим подтверждением, а не задним числом;
* лечащий проход публикует подтверждённые кейсы, но не публикует «на всякий
  случай» кейс без доказательства, и идемпотентен;
* в согласованной базе нет опубликованного факта, чей родитель невидим.
"""
from __future__ import annotations

from sqlalchemy import func, select

from app import repositories
from app.models.entities import CaseEvidence, EvidenceSource, GameCase
from app.seed import corrections, pack_loader

DRAFT = "draft"
PUBLISHED = "published"


def _source(db, code: str) -> EvidenceSource:
    src = EvidenceSource(
        code=code,
        title="Источник для проверки публикации кейсов",
        url="https://example.org/case-publication",
        status=PUBLISHED,
    )
    db.add(src)
    db.flush()
    return src


# --- загрузчик пакетов ----------------------------------------------------


def test_upsert_case_publishes_when_source_resolves(db_session):
    """Кейс с разрешившимся источником создаётся опубликованным.

    Раньше статус не задавался вовсе, и тип оставлял запись черновиком.
    """
    src = _source(db_session, "src-test-case-pub")
    payload = {"code": "case-test-pub", "title": "Тестовый кейс", "source": src.code}

    case = pack_loader._upsert_case(db_session, payload, {src.code: src})

    assert case.status == PUBLISHED


def test_upsert_case_stays_draft_when_source_unknown(db_session):
    """Неизвестный источник не подменяется известным: кейс остаётся черновиком."""
    payload = {
        "code": "case-test-draft",
        "title": "Тестовый кейс",
        "source": "источник-которого-нет",
    }

    case = pack_loader._upsert_case(db_session, payload, {})

    assert case.status == DRAFT


def test_upsert_case_fills_world_type_without_overwriting(db_session):
    """Согласующий проход заполняет пустое поле и не затирает курируемое.

    Игровой пример несёт `world_type`/`network_mode`, но в секции методов они
    раньше не переносились — поля оставались пустыми. Повторная загрузка
    обязана быть идемпотентной: уже заполненное значение не переписывается.
    """
    case = GameCase(code="case-test-world", title="Кейс", status=DRAFT)
    db_session.add(case)
    db_session.flush()

    pack_loader._upsert_case(
        db_session, {"code": "case-test-world", "title": "Кейс", "world_type": "open_world"}, {}
    )
    assert case.world_type == "open_world"

    pack_loader._upsert_case(
        db_session, {"code": "case-test-world", "title": "Кейс", "world_type": "linear"}, {}
    )
    assert case.world_type == "open_world", "курируемое значение затёрто повторной загрузкой"


# --- лечащий проход -------------------------------------------------------


def test_correct_case_publication_publishes_backed_case(db_session):
    """Кейс с опубликованным фактом и источником публикуется."""
    src = _source(db_session, "src-test-backed")
    case = GameCase(code="case-test-backed", title="С доказательством", status=DRAFT)
    db_session.add(case)
    db_session.flush()
    db_session.add(
        CaseEvidence(
            code="ce-test-backed",
            case_id=case.id,
            fact="Подтверждённый факт",
            source_id=src.id,
            status=PUBLISHED,
        )
    )
    db_session.flush()

    assert corrections.correct_case_publication(db_session) >= 1
    assert case.status == PUBLISHED


def test_correct_case_publication_leaves_unbacked_case_draft(db_session):
    """Кейс без подтверждённого доказательства не публикуется «на всякий случай».

    Кейс без источника — объявленный пробел, а не повод показать его в выдаче.
    """
    case = GameCase(code="case-test-unbacked", title="Без доказательства", status=DRAFT)
    db_session.add(case)
    db_session.flush()

    corrections.correct_case_publication(db_session)

    assert case.status == DRAFT


def test_correct_case_publication_ignores_unsourced_evidence(db_session):
    """Факт без источника не делает кейс публичным.

    Публикуется только подтверждение с источником: `derived`/собственный
    расчёт кейс как публичный пример не обосновывает.
    """
    case = GameCase(code="case-test-no-source", title="Факт без источника", status=DRAFT)
    db_session.add(case)
    db_session.flush()
    db_session.add(
        CaseEvidence(
            code="ce-test-no-source",
            case_id=case.id,
            fact="Факт без ссылки",
            source_id=None,
            status=PUBLISHED,
        )
    )
    db_session.flush()

    corrections.correct_case_publication(db_session)

    assert case.status == DRAFT


def test_correct_case_publication_is_idempotent(db_session):
    """Повторный проход ничего не меняет — лечащая функция идемпотентна."""
    corrections.correct_case_publication(db_session)

    assert corrections.correct_case_publication(db_session) == 0


def test_declare_evidence_gaps_reports_case_publication(db_session):
    """Публикация кейсов входит в отчёт прохода деклараций."""
    result = corrections.declare_evidence_gaps(db_session)

    assert "game_cases_published" in result
    assert isinstance(result["game_cases_published"], int)


# --- состояние согласованной базы ----------------------------------------


def test_no_published_evidence_points_to_draft_case(db_session):
    """Опубликованный факт не ссылается на невидимого родителя.

    Это и был видимый симптом: доказательство опубликовано, а кейс, через
    который оно попадает в «Сверку с практикой», — нет.
    """
    draft_ids = set(
        db_session.scalars(select(GameCase.id).where(GameCase.status != PUBLISHED))
    )
    dangling = (
        db_session.scalars(
            select(CaseEvidence.code).where(
                CaseEvidence.status == PUBLISHED,
                CaseEvidence.case_id.in_(draft_ids),
            )
        ).all()
        if draft_ids
        else []
    )

    assert dangling == [], f"опубликованных фактов на черновиках: {len(dangling)}"


def test_case_backed_by_published_evidence_is_published(db_session):
    """Кейс, подтверждённый опубликованным фактом с источником, не остаётся черновиком."""
    backed = set(
        db_session.scalars(
            select(CaseEvidence.case_id).where(
                CaseEvidence.status == PUBLISHED,
                CaseEvidence.source_id.is_not(None),
                CaseEvidence.case_id.is_not(None),
            )
        )
    )
    assert backed, "в согласованной базе нет подтверждённых фактов кейсов"

    still_draft = set(
        db_session.scalars(
            select(GameCase.id).where(
                GameCase.id.in_(backed),
                GameCase.status != PUBLISHED,
            )
        )
    )

    assert still_draft == set(), f"подтверждённых кейсов в черновиках: {len(still_draft)}"


def test_public_case_surface_has_no_orphan_evidence(db_session):
    """Публичный слой отдаёт все кейсы, на которые ссылается опубликованный факт.

    Проверка идёт через сам публичный слой (`repositories.game_cases`), а не
    через статус напрямую: дефект был именно в расхождении между фильтром
    публичного слоя и фактическим состоянием строк.
    """
    visible = {case.id for case in repositories.game_cases(db_session)}
    assert visible, "публичный слой не отдал ни одного кейса"

    orphans = db_session.scalars(
        select(CaseEvidence.code).where(
            CaseEvidence.status == PUBLISHED,
            CaseEvidence.case_id.not_in(visible),
        )
    ).all()

    assert orphans == [], f"фактов без видимого кейса: {len(orphans)}"


def test_seeded_cases_are_not_invisible(db_session):
    """На согласованной базе нет кейсов, невидимых без причины."""
    total = db_session.scalar(select(func.count()).select_from(GameCase))
    published = db_session.scalar(
        select(func.count()).select_from(GameCase).where(GameCase.status == PUBLISHED)
    )

    assert total
    assert published == total, f"невидимых кейсов: {total - published} из {total}"
