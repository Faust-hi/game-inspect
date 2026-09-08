"""Контракт входов анкеты: ноль, неизвестность, единица и границы.

Эти проверки существуют потому, что анкета — единственный источник данных для
численной модели. Любое значение, которое схема принимает, обязано давать
осмысленный результат: молчаливый переход «не указано» в измеренную величину
или падение расчёта на разрешённом значении делают оценку недостоверной.

Проверяется поведение и предметный смысл, а не конкретные коэффициенты: если
числа модели пересматриваются, эти тесты должны остаться зелёными.
"""
import pytest

from app.schemas.catalog import ProjectProfile, _effective_count, count_scale_bounds
from app.services.hardware import _applicability_limits, _load_indices

LEVELS = ("unknown", "low", "medium", "high")


# --- D07: неизвестность не ломает расчёт и не становится измерением ---------


@pytest.mark.parametrize("level", LEVELS)
def test_audio_complexity_every_level_is_accepted(client, level):
    """Все допустимые значения сложности аудио дают расчёт, а не ошибку 500."""
    response = client.post("/api/hardware-estimate", json={
        "profile": {"audio_complexity": level, "functions": ["audio_system"]},
        "basket": [],
    })

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["required_cpu_index"] > 0


def test_unknown_audio_is_reported_as_unknown_not_as_measured(client):
    """Неизвестная сложность аудио остаётся неизвестной.

    Отсутствие данных не должно превращаться в измеренную стоимость: расчёт
    обязан явно сообщить, что вклад аудио не учтён.
    """
    response = client.post("/api/hardware-estimate", json={
        "profile": {"audio_complexity": "unknown", "functions": ["audio_system"]},
        "basket": [],
    })

    assert response.status_code == 200
    gaps = " ".join(response.json()["modeling_gaps"])
    assert "сложность аудио не указана" in gaps.lower()


def test_unknown_audio_costs_nothing_and_is_still_distinguishable(client):
    """Неизвестность не занижает и не завышает нагрузку относительно уровней."""
    def cpu_index(level):
        response = client.post("/api/hardware-estimate", json={
            "profile": {"audio_complexity": level, "functions": ["audio_system"]},
            "basket": [],
        })
        assert response.status_code == 200
        return response.json()["required_cpu_index"]

    unknown = cpu_index("unknown")
    assert unknown <= cpu_index("medium") <= cpu_index("high")


# --- D08: ноль отличается от отсутствия значения ---------------------------


def test_zero_count_is_not_the_same_as_unspecified():
    """Ноль — осмысленное значение «сущностей нет», а не «данных нет»."""
    assert _effective_count(0, "medium", "npc_count") == 0.0
    assert _effective_count(None, "medium", "npc_count") > 0.0


def test_count_monotonicity_from_zero():
    """Рост числа сущностей не может снижать нагрузку.

    Раньше `value <= 0` подставлял качественный уровень, и профиль с нулём NPC
    получал нагрузку выше, чем профиль с одним NPC.
    """
    indices = [
        _load_indices(ProjectProfile(npc_count=count), [])["gpu_index"]
        for count in (0, 1, 10, 100, 1_000)
    ]
    assert indices == sorted(indices), indices
    assert indices[0] < indices[-1]


def test_zero_npc_is_cheaper_than_unspecified_npc():
    """Явный ноль дешевле нейтрального допущения об отсутствующих данных."""
    zero = _load_indices(ProjectProfile(npc_count=0), [])["cpu_index"]
    unknown = _load_indices(ProjectProfile(npc_count=None, npc_count_level="unknown"), [])["cpu_index"]
    assert zero < unknown


def test_object_count_zero_and_one_are_distinguishable():
    """Первый объект добавляет нагрузку, а не снимает её."""
    zero = _load_indices(ProjectProfile(object_count=0), [])["cpu_index"]
    one = _load_indices(ProjectProfile(object_count=1), [])["cpu_index"]
    assert zero < one


# --- D09: выход за область применимости виден ------------------------------


@pytest.mark.parametrize("field", ("object_count", "npc_count"))
def test_count_above_model_range_is_reported(field):
    """Насыщение шкалы сообщается, а не выдаётся за равную нагрузку."""
    _, top = count_scale_bounds(field)
    profile = ProjectProfile(**{field: int(top) * 100})

    limits = _applicability_limits(profile)

    assert limits, "выход за границу модели должен быть виден"
    assert any("выше верхней границы модели" in line for line in limits)


def test_saturated_counts_do_not_pretend_to_differ():
    """При выходе за границу результат одинаков, но это ограничение названо.

    Два разных числа дают один индекс — разница в том, что раньше это
    выглядело как измеренное равенство нагрузки, а теперь как предел модели.
    """
    _, top = count_scale_bounds("npc_count")
    near = _load_indices(ProjectProfile(npc_count=int(top)), [])["gpu_index"]
    far = _load_indices(ProjectProfile(npc_count=int(top) * 1000), [])["gpu_index"]

    assert near == far
    assert _applicability_limits(ProjectProfile(npc_count=int(top) * 1000))


def test_target_fps_outside_calibrated_range_is_reported():
    for fps, marker in ((240, "выше"), (20, "ниже")):
        limits = _applicability_limits(ProjectProfile(target_fps=fps))
        assert any(marker in line and "FPS" in line for line in limits), (fps, limits)


def test_player_count_saturation_is_reported():
    limits = _applicability_limits(ProjectProfile(player_count=64, multiplayer=True))
    assert any("игроков" in line for line in limits)


def test_in_range_profile_has_no_applicability_limits():
    """Обычный профиль не должен получать предупреждений о границах."""
    assert _applicability_limits(ProjectProfile()) == []


def test_applicability_limits_reach_the_api(client):
    response = client.post("/api/hardware-estimate", json={
        "profile": {"npc_count": 10_000_000, "target_fps": 240},
        "basket": [],
    })

    assert response.status_code == 200
    body = response.json()
    assert body["applicability_limits"], "ограничения применимости должны быть в ответе"


# --- Крайние и нечисловые значения -----------------------------------------


@pytest.mark.parametrize("payload", [
    {"object_count": -5},
    {"npc_count": -1},
    {"target_fps": 0},
    {"target_fps": "быстро"},
    {"audio_complexity": "огромная"},
    {"scale": "бесконечная"},
    {"player_count": 0},
])
def test_invalid_inputs_are_rejected_with_structured_error(client, payload):
    """Недопустимые значения отклоняются проверкой схемы, а не расчётом."""
    response = client.post("/api/hardware-estimate", json={"profile": payload, "basket": []})

    assert response.status_code == 422, response.text
    body = response.json()
    # Единый формат: строка сообщения, машинный код и непустой идентификатор,
    # совпадающий с заголовком. Раньше в теле был request_id=null.
    assert isinstance(body["error"], str)
    assert body["code"] == "validation_error"
    assert body["request_id"], "идентификатор запроса не может быть пустым"
    assert body["request_id"] == response.headers["x-request-id"]


def test_non_numeric_basket_entry_is_rejected(client):
    """Код решения — строка; словарь не превращается молча в неизвестный код."""
    response = client.post("/api/hardware-estimate", json={
        "profile": {},
        "basket": [{"код": 5}],
    })

    assert response.status_code == 422
    assert response.json()["details"]
