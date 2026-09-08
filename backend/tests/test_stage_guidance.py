"""Содержательная работа стадии разработки.

Проверки существуют потому, что стадия долгое время была декоративной:
переключение стадии не меняло ни состав рекомендаций, ни предупреждения, и
экран выглядел как переключатель без последствий.

Здесь проверяется три вещи: у каждой стадии есть собственные предупреждения и
предложения; стадия закрывает уровни решений, которые физически нельзя
внедрить; расчёт действительно исключает закрытые решения.
"""
from __future__ import annotations

from types import SimpleNamespace

import pytest

from app.models.enums import DevStage, LateCost, SolutionLevel
from app.services import stage_guidance

ALL_STAGES = [stage.value for stage in DevStage]

#: Поздние стадии: архитектура уже зафиксирована контентом.
LATE_STAGES = ["alpha", "beta", "release", "post_release"]
#: Ранние стадии: архитектурные решения ещё внедримы.
EARLY_STAGES = ["concept", "preproduction", "prototype", "production"]


# --- Маршрут: подсказка доступна без расчёта --------------------------------


@pytest.mark.parametrize("stage", ALL_STAGES)
def test_route_returns_guidance_for_every_stage(client, stage):
    """Для каждой стадии маршрут отдаёт сводку, предупреждения и предложения.

    Пустые предупреждения или предложения означали бы, что у стадии нет
    содержания — именно это и делало раздел декоративным.
    """
    response = client.get("/api/catalog/stage-guidance", params={"stage": stage})

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["stage"] == stage
    assert body["stage_label"]
    assert body["summary"]
    assert body["warnings"], f"у стадии {stage} нет предупреждений"
    assert body["suggestions"], f"у стадии {stage} нет предложений"
    for note in body["warnings"] + body["suggestions"]:
        assert note["title"] and note["text"]


def test_unknown_stage_falls_back_to_prototype(client):
    """Неизвестный код стадии сводится к прототипу, а не даёт ошибку 500."""
    response = client.get("/api/catalog/stage-guidance", params={"stage": "нет_такой_стадии"})

    assert response.status_code == 200, response.text
    assert response.json()["stage"] == DevStage.PROTOTYPE.value


# --- Содержание стадий различается ------------------------------------------


def test_every_stage_has_its_own_content(client):
    """Предупреждения и предложения у стадий не повторяются.

    Совпадающий набор у всех стадий означал бы, что содержание выведено из
    порядкового номера, а не задано для каждой стадии отдельно: у беты и релиза
    ограничения разные, хотя обе стадии поздние.
    """
    payloads = {
        stage: client.get("/api/catalog/stage-guidance", params={"stage": stage}).json()
        for stage in ALL_STAGES
    }

    assert len({payload["summary"] for payload in payloads.values()}) == len(ALL_STAGES)
    warnings = {stage: {note["code"] for note in payload["warnings"]} for stage, payload in payloads.items()}
    assert len({frozenset(codes) for codes in warnings.values()}) == len(ALL_STAGES)
    suggestions = {
        stage: {note["code"] for note in payload["suggestions"]} for stage, payload in payloads.items()
    }
    assert len({frozenset(codes) for codes in suggestions.values()}) == len(ALL_STAGES)


# --- Закрытые уровни решений ------------------------------------------------


@pytest.mark.parametrize("stage", LATE_STAGES)
def test_late_stages_block_architecture(client, stage):
    """На поздних стадиях архитектурные решения закрыты."""
    body = client.get("/api/catalog/stage-guidance", params={"stage": stage}).json()

    assert "architecture" in body["blocked_levels"]
    assert body["blocked_level_labels"]
    assert "architecture" not in body["available_levels"]


@pytest.mark.parametrize("stage", EARLY_STAGES)
def test_early_stages_keep_every_level_available(client, stage):
    """На ранних стадиях все уровни решений остаются доступными."""
    body = client.get("/api/catalog/stage-guidance", params={"stage": stage}).json()

    assert body["blocked_levels"] == []
    assert sorted(body["available_levels"]) == sorted(level.value for level in SolutionLevel)


def test_release_restricts_production_level():
    """Релиз закрывает часть производственных решений, но не уровень целиком.

    Отдельно от закрытых уровней: сказать «уровень закрыт» про уровень, где
    доступна часть решений, значило бы скрыть рабочие варианты.
    """
    body = stage_guidance.guidance("release")

    assert "production" in body.restricted_levels
    assert "production" not in body.blocked_levels


def test_post_release_reopens_production_level():
    """После релиза пайплайн снова открыт: патчи перерабатывают контент."""
    body = stage_guidance.guidance("post_release")

    assert "production" not in body.restricted_levels
    assert "production" not in body.blocked_levels


# --- Исключение закрытых решений из расчёта ---------------------------------


def test_blocked_method_is_excluded_from_recommendations(client):
    """Закрытое стадией решение не попадает в рекомендации.

    Раньше такое решение оставалось в списке и только сопровождалось
    предупреждением, из-за чего смена стадии не меняла выдачу.
    """
    early = client.post("/api/recommend", json={
        "profile": {"stage": "concept", "functions": ["graphics_3d"]},
        "basket": [],
    }).json()
    late = client.post("/api/recommend", json={
        "profile": {"stage": "release", "functions": ["graphics_3d"]},
        "basket": [],
    }).json()

    assert early["recommendations"] or late["recommendations"]
    codes = {item["method_code"] for item in late["recommendations"]}
    blocked = [
        item["method_code"] for item in early["recommendations"]
        if _is_blocked_on_release(client, item["method_code"])
    ]
    assert blocked, "в выдаче концепта нет архитектурных решений — проверка ничего не проверяет"
    assert not (set(blocked) & codes), "архитектурное решение осталось в выдаче релиза"


def _is_blocked_on_release(client, code: str) -> bool:
    """Закрыто ли решение стадией «релиз»: уровень и цена из карточки метода."""
    card = client.get(f"/api/catalog/methods/{code}")
    if card.status_code != 200:
        return False
    body = card.json()
    method = SimpleNamespace(level=body["level"], late_cost=body["late_cost"])
    return stage_guidance.is_blocked(method, "release")


def test_excluded_closed_method_reports_stage_as_reason(client):
    """Исключённое решение объясняет причину: решение закрыто стадией."""
    late = client.post("/api/recommend", json={
        "profile": {"stage": "release", "functions": ["graphics_3d"]},
        "basket": [],
    }).json()

    reasons = " ".join(
        reason for item in late["excluded"] for reason in item["excluded_reasons"]
    )
    assert "закрыто стадией" in reasons.lower(), "в причинах исключения нет указания на стадию"


def test_stage_guidance_present_in_result(client):
    """Блок стадии входит в результат расчёта: экран берёт его без запроса."""
    body = client.post("/api/recommend", json={
        "profile": {"stage": "beta", "functions": ["graphics_3d"]},
        "basket": [],
    }).json()

    assert body["stage_guidance"]["stage"] == "beta"
    assert body["stage_guidance"]["blocked_levels"] == ["architecture"]


# --- Согласованность таблицы блокировок -------------------------------------


def test_blocked_pairs_use_known_enum_values():
    """Все коды в таблице блокировок существуют в перечислениях.

    Опечатка в коде уровня или цены молча отключала бы правило: пара просто
    никогда бы не совпала ни с одним решением.
    """
    levels = {level.value for level in SolutionLevel}
    costs = {cost.value for cost in LateCost}

    for stage, pairs in stage_guidance._BLOCKED_BY_STAGE.items():
        assert stage in ALL_STAGES, f"неизвестная стадия в таблице блокировок: {stage}"
        for level, cost in pairs:
            assert level in levels, f"неизвестный уровень: {level}"
            assert cost in costs, f"неизвестная цена внедрения: {cost}"


def test_blocked_levels_are_consistent_with_blocked_pairs():
    """Уровень, закрытый целиком, не должен быть закрыт только частично."""
    for stage in ALL_STAGES:
        body = stage_guidance.guidance(stage)
        assert not (set(body.blocked_levels) & set(body.restricted_levels)), stage
        assert set(body.blocked_levels) | set(body.restricted_levels) <= {
            level.value for level in SolutionLevel
        }
        assert set(body.available_levels) | set(body.blocked_levels) == {
            level.value for level in SolutionLevel
        }
