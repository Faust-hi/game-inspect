"""Пакеты работ: величина из пакета обязана доходить до уже собранной базы.

История у этого класса дефектов одна и та же. Сначала `_upsert_work_package` для
существующей строки сверял только `stage_note`, поэтому исправление словаря
ролей (`designer` → `design`) до прод-базы не дошло: 868 пакетов сохранили
имена, которых нет в ёмкости команды, и планировщик молча брал для них ёмкость
1. Теперь величина оценки приходит из пакета в строки формульной семьи, и
согласующий проход обязан доводить её точно так же.

Проверки построены по данным, а не по списку: если расхождение в пакетах
исправят или появится новая роль без ёмкости, тест это заметит.
"""
from __future__ import annotations

from sqlalchemy import select


def _published_snapshot(db_session):
    from app.models.entities import WorkPackage

    rows = db_session.scalars(select(WorkPackage)).all()
    return {
        row.code: (
            row.role, round(float(row.p50_days), 4), round(float(row.p80_days), 4),
            round(float(row.min_days), 4), row.late_factor, row.parallelizable,
            row.recommended_stage, row.stage_note, list(row.dependency_codes or []),
            row.basis, row.status,
        )
        for row in rows
    }


def test_method_total_equals_curated_estimate(db_session):
    """Сумма фаз метода равна курируемой оценке пакета.

    Величину задаёт пакет, распределение по фазам — формула. Если сумма
    расходится с курируемой оценкой, значит в базе снова живёт вторая оценка
    (1081,82 против 2435 чел.-дней), а не одна.
    """
    from app.models.entities import WorkPackage
    from app.seed import pack_loader

    curated = pack_loader.curated_effort()
    assert curated, "курируемых оценок нет — нечего сверять"

    totals: dict[str, float] = {}
    for row in db_session.scalars(select(WorkPackage).where(WorkPackage.status == "published")):
        totals[row.method_code] = totals.get(row.method_code, 0.0) + float(row.p50_days)

    checked = 0
    for code, total in sorted(totals.items()):
        estimate = curated.get(code)
        if estimate is None:
            continue
        assert abs(total - estimate["p50"]) <= 0.05, (
            f"метод {code}: сумма фаз {round(total, 2)} чел.-дней не равна "
            f"курируемой оценке {estimate['p50']}"
        )
        checked += 1
    assert checked >= 100, f"сверено слишком мало методов: {checked}"


def test_curated_effort_reaches_an_existing_package(db_session):
    """Смена величины доходит до строки, которая уже есть в собранной базе.

    Именно этот случай и был сломан с ролями: проход обновлял только новые
    строки, а существующие оставались с прежними числами.
    """
    from app.models.entities import Method, WorkPackage
    from app.seed import evidence_catalog, pack_loader

    curated = pack_loader.curated_effort()
    method = db_session.scalar(
        select(Method).where(
            Method.status == "published", Method.code.in_(list(curated))
        ).order_by(Method.code)
    )
    assert method is not None, "нет опубликованного метода с курируемой оценкой"

    rows = db_session.scalars(
        select(WorkPackage).where(WorkPackage.method_code == method.code)
    ).all()
    assert rows, f"у метода {method.code} нет пакетов работ"

    # Испортить величины: как будто база собрана до смены семьи.
    for row in rows:
        row.p50_days = 1.0
        row.p80_days = 1.5
        row.min_days = 0.5
    db_session.flush()

    evidence_catalog.sync_work_packages(db_session)

    again = db_session.scalars(
        select(WorkPackage).where(WorkPackage.method_code == method.code)
    ).all()
    total = sum(float(row.p50_days) for row in again)
    assert abs(total - curated[method.code]["p50"]) <= 0.05, (
        f"метод {method.code}: после синхронизации {round(total, 2)} чел.-дней "
        f"вместо {curated[method.code]['p50']}"
    )


def test_reconciliation_is_idempotent(db_session):
    """Повторная синхронизация не меняет уже согласованные строки."""
    from app.seed import evidence_catalog

    evidence_catalog.sync_work_packages(db_session)
    db_session.flush()
    before = _published_snapshot(db_session)

    evidence_catalog.sync_work_packages(db_session)
    db_session.flush()

    assert _published_snapshot(db_session) == before


def test_planner_fields_survive_the_new_magnitude(db_session):
    """Поля, которые читает планировщик, не проседают до значений второй семьи.

    Прежняя пакетная семья не несла `min_days`, `late_factor` и
    `dependency_codes` и помечала гейтовые фазы параллелизуемыми. Публикация её
    «как есть» вернула бы все четыре дефекта: нижняя граница оценки обнулялась
    бы, надбавка за позднюю цену исчезала, а предусловия методов — терялись.
    """
    from app.models.entities import WorkPackage

    published = db_session.scalars(
        select(WorkPackage).where(WorkPackage.status == "published")
    ).all()
    assert published, "нет опубликованных пакетов работ"

    assert not [r.code for r in published if float(r.min_days or 0) <= 0], \
        "нижняя граница оценки обнулилась"
    assert not [r.code for r in published if float(r.late_factor or 0) <= 1.0], \
        "надбавка за позднюю цену исчезла"
    assert not [r.code for r in published
                if r.parallelizable and r.package_type in {"integration", "qa", "release"}], \
        "гейтовая фаза помечена параллелизуемой"


def test_no_second_family_remains(db_session):
    """Второй семьи нет: все строки пакетов работ опубликованы.

    992 строки `WP_*` жили в базе как черновики — невидимые для планировщика,
    но попадающие в счётчики и в аудит как объявленный пробел.
    """
    from app.models.entities import WorkPackage

    rows = db_session.scalars(select(WorkPackage)).all()
    assert rows, "ожидались пакеты работ"
    assert not [r.code for r in rows if r.code.startswith("WP_")], \
        "остались строки второй семьи"
    assert not [r.code for r in rows if r.status != "published"], \
        "остались невидимые пакеты работ"


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
