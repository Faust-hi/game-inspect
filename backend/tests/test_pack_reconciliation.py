"""Пакеты работ: правка пакета должна доходить до уже собранной базы.

Дефект: `_upsert_work_package` для существующей строки сверял только
`stage_note`, поэтому исправление словаря ролей (`designer` → `design`) до
прод-базы не дошло: 868 пакетов сохранили имена, которых нет в ёмкости команды,
и планировщик молча брал для них ёмкость 1 — размер команды переставал влиять
на план. Согласующий проход закрывает расхождение источника и результата.
"""
from __future__ import annotations

from sqlalchemy import select


def _package(code: str, **overrides):
    from app.models.entities import WorkPackage

    fields = {
        "method_code": "test_reconcile",
        "name": "старое имя",
        "package_type": "design",
        "role": "designer",
        "min_days": 0.0,
        "p50_days": 1.0,
        "p80_days": 1.5,
        "parallelizable": True,
        "recommended_stage": "production",
        "late_factor": 1.0,
        "dependency_codes": [],
        "basis": "expert_estimate",
    }
    fields.update(overrides)
    return WorkPackage(code=code, **fields)


def _payload(code: str, **overrides):
    fields = {
        "code": code,
        "method_code": "test_reconcile",
        "name": "новое имя",
        "package_type": "design",
        "role": "design",
        "p50_days": 1.5,
        "p80_days": 3.25,
        "basis": "expert_estimate",
        "recommended_stage": "prototype",
    }
    fields.update(overrides)
    return fields


def test_pack_change_reaches_an_existing_package(db_session):
    """Правка пакета обновляет уже созданную строку, а не только новую."""
    from app.models.entities import WorkPackage
    from app.seed import pack_loader

    code = "test_reconcile.role"
    db_session.add(_package(code))
    db_session.flush()

    pack_loader._upsert_work_package(db_session, _payload(code))
    row = db_session.scalar(select(WorkPackage).where(WorkPackage.code == code))

    assert row.role == "design"
    assert row.name == "новое имя"
    assert row.p50_days == 1.5
    assert row.p80_days == 3.25
    assert row.recommended_stage == "prototype"


def test_reconciliation_is_idempotent(db_session):
    """Повторная загрузка того же пакета ничего не меняет."""
    from app.models.entities import WorkPackage
    from app.seed import pack_loader

    code = "test_reconcile.idempotent"
    db_session.add(_package(code))
    db_session.flush()

    pack_loader._upsert_work_package(db_session, _payload(code))
    db_session.flush()
    row = db_session.scalar(select(WorkPackage).where(WorkPackage.code == code))
    snapshot = (row.role, row.name, row.p50_days, row.p80_days, row.recommended_stage,
                row.stage_note, row.min_days, row.parallelizable, row.late_factor,
                list(row.dependency_codes or []))

    pack_loader._upsert_work_package(db_session, _payload(code))
    db_session.flush()
    again = (row.role, row.name, row.p50_days, row.p80_days, row.recommended_stage,
             row.stage_note, row.min_days, row.parallelizable, row.late_factor,
             list(row.dependency_codes or []))

    assert again == snapshot


def test_reconciliation_keeps_fields_the_pack_does_not_own(db_session):
    """Поля вне пакета (плановая стадия, предусловия, примечание) не затираются.

    Пакет не описывает `min_days`, параллелизуемость, `late_factor` и
    предусловия — они принадлежат планировщику, и согласующий проход не должен
    подменять их значениями по умолчанию.
    """
    from app.models.entities import WorkPackage
    from app.seed import pack_loader

    code = "test_reconcile.foreign"
    db_session.add(_package(
        code, min_days=3.0, parallelizable=False, late_factor=2.0,
        dependency_codes=["other_method"], stage_note="курируемое примечание",
    ))
    db_session.flush()

    pack_loader._upsert_work_package(db_session, {
        "code": code, "method_code": "test_reconcile", "name": "новое имя",
        "package_type": "design", "role": "design", "p50_days": 1.5, "p80_days": 3.25,
    })
    row = db_session.scalar(select(WorkPackage).where(WorkPackage.code == code))

    assert row.min_days == 3.0
    assert row.parallelizable is False
    assert row.late_factor == 2.0
    assert list(row.dependency_codes or []) == ["other_method"]
    assert row.stage_note == "курируемое примечание"


def test_new_package_gets_pack_values(db_session):
    """Новая строка создаётся со значениями пакета."""
    from app.models.entities import WorkPackage
    from app.seed import pack_loader

    code = "test_reconcile.new"
    created = pack_loader._upsert_work_package(db_session, _payload(code))
    db_session.flush()
    row = db_session.scalar(select(WorkPackage).where(WorkPackage.code == code))

    assert created is not None
    assert row.role == "design"
    assert row.p50_days == 1.5


def test_every_package_role_is_a_team_capacity_key(db_session):
    """Роль пакета обязана быть ключом ёмкости команды.

    Иначе планировщик молча берёт ёмкость 1, и размер команды перестаёт влиять
    на план — это не заметно ни в ответе, ни в отчёте. Проверка по данным, а не
    по списку в тесте: новая роль без ёмкости не сможет остаться незамеченной.
    """
    from app.models.entities import TeamScenario, WorkPackage

    capacity_keys: set[str] = set()
    for team in db_session.scalars(select(TeamScenario)):
        capacity_keys |= set((team.role_capacity or {}).keys())
    assert capacity_keys, "у сценариев команды нет словаря ёмкости"

    roles = {row.role for row in db_session.scalars(select(WorkPackage))}
    assert roles <= capacity_keys, (
        "роли пакетов без ёмкости в команде: " + ", ".join(sorted(roles - capacity_keys))
    )


def test_duplicate_effort_is_declared_not_silent(db_session):
    """Оценка трудоёмкости, описанная дважды с разными значениями, объявляется.

    Победителя определяет порядок загрузки пакетов, поэтому расхождение должно
    быть видно в статистике загрузки, а не растворяться в ней. Ожидаемое число
    считается по самим пакетам, а не берётся из списка: если расхождение в
    данных исправят, счётчик обязан стать нулём.
    """
    from app.seed import pack_loader

    packs, _ = pack_loader._load_packs()
    seen: dict[str, tuple[float, float]] = {}
    expected = 0
    for pack in packs:
        methods = pack.get("methods")
        if not isinstance(methods, dict):
            continue
        for code, data in methods.items():
            effort = (data or {}).get("effort_person_days") or {}
            if effort.get("p50") is None:
                continue
            p50 = float(effort["p50"])
            p80 = float(effort["p80"]) if effort.get("p80") is not None else p50 * 1.5
            if code in seen and seen[code] != (p50, p80):
                expected += 1
            seen[code] = (p50, p80)

    stats = pack_loader.sync_packs(db_session)
    assert stats["pack_effort_conflicts"] == expected
