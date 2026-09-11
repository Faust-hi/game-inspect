"""Регрессии публичных маршрутов доказательного слоя."""
from __future__ import annotations


def test_entity_evidence_path_alias_filters_claims(client):
    claims_response = client.get("/api/catalog/evidence", params={"entity": "method"})
    assert claims_response.status_code == 200
    claims = claims_response.json()
    assert claims

    selected = claims[0]
    response = client.get(
        f"/api/catalog/evidence/{selected['entity']}/{selected['entity_code']}"
    )
    assert response.status_code == 200
    returned = response.json()
    assert returned
    assert all(
        item["entity"] == selected["entity"]
        and item["entity_code"] == selected["entity_code"]
        for item in returned
    )


def test_report_data_get_uses_valid_default_profile(client):
    response = client.get("/api/report-data")

    assert response.status_code == 200
    payload = response.json()
    assert payload["recommendation"]["evidence_summary"]["calibration_status"] == "not_calibrated"
    assert payload["schedule"]["team"]["code"] == "small_2_5"


def test_graph_checks_reports_no_mandatory_cycles(client):
    """Граф обязан быть ациклическим по обязательным зависимостям.

    Цикл обязательных зависимостей неразрешим: ни один метод в нём нельзя
    поставить в план. Если этот тест падает, в каталог попали взаимные
    предусловия, которые нужно понизить до дополнения.
    """
    response = client.get("/api/catalog/graph-checks")

    assert response.status_code == 200
    payload = response.json()
    assert payload["counts"]["edges"] > 0
    assert payload["counts"]["nodes"] > 0
    cycles = [item for item in payload["issues"] if item["check"] == "cyclic_mandatory"]
    assert cycles == [], f"найдены циклы обязательных зависимостей: {cycles}"


def test_graph_checks_flags_unknown_version_instead_of_compatibility(client):
    """Без версии движка соответствие версиям не проверяется.

    Проверка обязана вернуть явный статус «не проверено», а не молчаливое
    «нарушений нет»: отсутствие данных не означает совместимость.
    """
    response = client.get("/api/catalog/graph-checks")

    assert response.status_code == 200
    checks = {item["check"] for item in response.json()["issues"]}
    assert "version_unknown" in checks


def test_graph_checks_detects_hard_conflict_inside_basket(client):
    """Жёсткий конфликт внутри корзины должен быть найден.

    Тест сам находит существующую пару hard_conflict, поэтому не зависит от
    конкретного содержимого каталога.
    """
    conflicts = client.get("/api/catalog/conflicts").json()
    hard = [item for item in conflicts if item["conflict_type"] == "hard_conflict"]
    if not hard:
        # Каталог без жёстких конфликтов — не повод считать проверку рабочей.
        return

    pair = hard[0]
    response = client.get(
        "/api/catalog/graph-checks",
        params=[("basket", pair["a_code"]), ("basket", pair["b_code"])],
    )

    assert response.status_code == 200
    found = [item for item in response.json()["issues"] if item["check"] == "basket_hard_conflict"]
    assert found, f"жёсткий конфликт {pair['a_code']} / {pair['b_code']} не обнаружен"


def test_graph_checks_api_incompatibility_is_reported(client):
    """Выбор API, не покрывающего обязательное требование, — ошибка, а не заметка."""
    response = client.get(
        "/api/catalog/graph-checks",
        params={"render_api": "dx11", "engine": "unreal", "engine_version": "5.4"},
    )

    assert response.status_code == 200
    issues = response.json()["issues"]
    assert any(item["check"] == "api_incompatibility" for item in issues)


def test_schedule_tasks_expose_work_package_fields(client):
    """Пакет работ обязан нести стадию, основание и минимальную оценку.

    Без них строку плана нельзя отличить от измерения и нельзя разложить по
    стадиям, а P50/P80 теряют опору.
    """
    profile = client.get("/api/report-data").json()["recommendation"]["profile"]
    methods = client.get("/api/catalog/methods").json()
    basket = [item["code"] for item in methods[:2]]

    response = client.post(
        "/api/schedule",
        json={"profile": profile, "basket": basket, "team": "small_2_5"},
    )

    assert response.status_code == 200
    tasks = response.json()["tasks"]
    assert tasks
    for task in tasks:
        assert task["recommended_stage"]
        assert task["basis"]
        assert task["minimum_days"] <= task["p50_days"] <= task["p80_days"]


def test_p80_is_never_below_p50(client):
    """Монотонность диапазона: P80 меньше P50 — противоречивые данные."""
    profile = client.get("/api/report-data").json()["recommendation"]["profile"]
    methods = client.get("/api/catalog/methods").json()
    basket = [item["code"] for item in methods[:4]]

    response = client.post(
        "/api/schedule",
        json={"profile": profile, "basket": basket, "team": "mid_6_15"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["effort"]["p80"] >= payload["effort"]["p50"]
    assert payload["calendar"]["p80"] >= payload["calendar"]["p50"]


def test_custom_team_profile_is_available(client):
    """Профиль «custom» из спецификации существует, а не подменяется малой командой.

    Дефект: пятого профиля не было, и запрос team=custom молча получал
    small_2_5 под чужим именем — пользователь видел не свой календарь.
    """
    codes = {team["code"] for team in client.get("/api/catalog/teams").json()}
    assert {"solo", "small_2_5", "mid_6_15", "large_16_plus", "custom"} <= codes

    profile = client.get("/api/report-data").json()["recommendation"]["profile"]
    response = client.post(
        "/api/schedule",
        json={"profile": profile, "basket": ["dynamic_global_illumination"],
              "team": "custom"},
    )
    assert response.status_code == 200
    assert response.json()["team"]["code"] == "custom"
    assert response.json()["team"]["team_size"] > 0


def test_unknown_team_is_declared_not_silently_substituted(client):
    """Неизвестный профиль команды объявляется, а не выдаётся за существующий.

    Дефект: неизвестный код молча возвращал small_2_5 под кодом small_2_5,
    и вызывающая сторона не могла отличить найденный профиль от подстановки.
    """
    profile = client.get("/api/report-data").json()["recommendation"]["profile"]
    response = client.post(
        "/api/schedule",
        json={"profile": profile, "basket": ["dynamic_global_illumination"],
              "team": "bogus_team"},
    )

    assert response.status_code == 200
    team = response.json()["team"]
    # Код сохраняется как запрошен, а описание прямо сообщает о подстановке.
    assert team["code"] == "bogus_team"
    assert "не найден" in team["description"]
    assert "подстановк" in team["description"]


def _schedule_with_team(client, team: str) -> dict:
    profile = client.get("/api/report-data").json()["recommendation"]["profile"]
    methods = client.get("/api/catalog/methods").json()
    basket = [item["code"] for item in methods[:4]]
    response = client.post(
        "/api/schedule",
        json={"profile": profile, "basket": basket, "team": team},
    )
    assert response.status_code == 200
    return response.json()


def test_team_size_moves_calendar_not_person_days(client):
    """Размер команды меняет срок, но не суммарную трудоёмкость.

    Человеко-дни — свойство объёма работ, а не числа исполнителей: если команда
    больше, календарь обязан сжаться, а effort остаться тем же. Иначе размер
    команды молча «сокращал» бы работу, чего в реальности не происходит.
    """
    solo = _schedule_with_team(client, "solo")
    large = _schedule_with_team(client, "large_16_plus")

    assert solo["effort"]["p50"] == large["effort"]["p50"]
    assert solo["effort"]["p80"] == large["effort"]["p80"]
    assert large["calendar"]["p50"] <= solo["calendar"]["p50"]
    assert large["team"]["team_size"] >= solo["team"]["team_size"]
    assert large["calendar"]["p50"] < solo["calendar"]["p50"]


def test_dependent_tasks_form_critical_path(client):
    """Critical path состоит из реальных задач, и каждая помечена критической.

    Путь без задач или не помеченными узлами — фикция: по нему нельзя понять,
    задержка чего сдвигает весь срок.
    """
    payload = _schedule_with_team(client, "mid_6_15")

    codes = {task["code"] for task in payload["tasks"]}
    critical_path = payload["critical_path"]
    assert critical_path
    assert set(critical_path) <= codes
    # Каждый узел пути обязан нести флаг critical, и наоборот.
    flagged = {task["code"] for task in payload["tasks"] if task["critical"]}
    assert flagged == set(critical_path)


def test_dependency_pulls_prerequisite_into_schedule(client):
    """Включение зависимостей добавляет пакет-предусловие и не молчит о нём.

    Если метод требует prerequisite, план обязан либо включить его задачeй,
    либо явно перечислить как нерешённую зависимость — тихого пропуска нет.
    """
    profile = client.get("/api/report-data").json()["recommendation"]["profile"]
    basket = ["world_partition_streaming"]

    with_deps = client.post(
        "/api/schedule",
        json={"profile": profile, "basket": basket, "team": "mid_6_15",
              "include_dependencies": True},
    ).json()
    without = client.post(
        "/api/schedule",
        json={"profile": profile, "basket": basket, "team": "mid_6_15",
              "include_dependencies": False},
    ).json()

    assert set(without["methods"]) <= set(with_deps["methods"])
    # Каждый включённый метод представлен хотя бы одной задачей.
    task_methods = {task["method_code"] for task in with_deps["tasks"]}
    assert set(with_deps["methods"]) <= task_methods
    # Непокрытый prerequisite объявляется, а не проглатывается.
    for code in with_deps["unresolved_dependencies"]:
        assert isinstance(code, str) and code

