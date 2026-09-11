"""Согласованность плана и графа с обязательными проверками спеки.

Дефекты этого класса: значения перечислений подменяются свободным текстом,
стадия перестаёт быть сравнимой, а валидатор молчит, потому что проверки нет.
"""
from __future__ import annotations

from app.models.enums import DevStage
from app.seed.pack_loader import normalize_stage


STAGES = {stage.value for stage in DevStage}


def test_normalize_stage_keeps_valid_enum_untouched():
    """Код стадии остаётся собой и не помечается как свободный текст."""
    for code in STAGES:
        value, free_text = normalize_stage(code)
        assert value == code
        assert free_text is None


def test_normalize_stage_parses_research_prose():
    """Развёрнутая рекомендация превращается в код, а текст не теряется.

    Пакеты рендеринга и стриминга хранили в `recommended_stage` английское
    описание вида «vertical_slice_or_later, once lighting art direction is
    locked…». Подстановка такого текста в поле стадии делает её непригодной
    для сравнения и фильтрации, поэтому значение нормализуется, а исходная
    формулировка возвращается отдельно.
    """
    prose = (
        "vertical_slice_or_later, once lighting art direction is locked; "
        "earlier only as a tech spike"
    )
    value, free_text = normalize_stage(prose)
    assert value in STAGES
    assert value == "prototype"
    assert free_text == prose


def test_normalize_stage_never_silently_invents_a_late_stage():
    """Нераспознанный текст не превращается в позднюю стадию.

    Стадия не должна ни скрывать метод из выдачи, ни обещать зрелость:
    по умолчанию берётся ранняя безопасная стадия, а текст сохраняется.
    """
    value, free_text = normalize_stage("совершенно непонятная рекомендация")
    assert value == "prototype"
    assert free_text == "совершенно непонятная рекомендация"


def test_normalize_stage_handles_empty_and_none():
    """Пустое значение и None не дают исключения и не выдумывают текст."""
    assert normalize_stage(None) == ("prototype", None)
    assert normalize_stage("") == ("prototype", None)
    assert normalize_stage("   ") == ("prototype", None)


def test_published_work_packages_carry_enum_stage(client):
    """Все опубликованные пакеты работ имеют код стадии, а не прозу.

    Проверка закрывает обязательный инвариант плана: стадия берётся из
    перечисления, иначе фильтрация плана по этапу недостоверна.
    """
    response = client.post(
        "/api/schedule",
        json={
            "profile": {
                "name": "Стадии",
                "format": "3D",
                "world_type": "open_world",
                "scale": "large",
                "stage": "prototype",
                "engine": "unreal",
                "platforms": ["pc_windows"],
                "functions": ["open_world_streaming"],
                "target_resolution": "1080p",
                "target_quality": "high",
                "target_fps": 60,
            },
            "team": "small_2_5",
            "basket": ["virtual_shadow_maps"],
        },
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["tasks"], "план не должен быть пустым"
    for task in data["tasks"]:
        assert task["recommended_stage"] in STAGES, task
