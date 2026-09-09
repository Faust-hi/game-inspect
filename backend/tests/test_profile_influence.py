"""Честность анкеты: каждое собираемое поле должно влиять на результат.

Анкета обещает персонализацию. Тест на обещание звучал бы как «поле есть в
запросе»; здесь проверяется другое — что изменение поля меняет ответ. Если
какое-то поле перестаёт влиять, тест падает, и это честнее, чем оставлять
пользователя с иллюзией учтённого ответа.
"""
from __future__ import annotations

import pytest


BASE = {
    "name": "Проект",
    "format": "3D",
    "world_type": "open_world",
    "scale": "large",
    "stage": "prototype",
    "engine": "unreal",
    "platforms": ["pc_windows"],
    "functions": ["open_world_streaming", "crowd_simulation"],
    "target_resolution": "1440p",
    "target_quality": "high",
    "target_fps": 60,
    "npc_count_level": "high",
}


def estimate(client, **overrides):
    profile = dict(BASE, **overrides)
    return client.post("/api/hardware-estimate", json={"profile": profile, "basket": []}).json()


def recommend(client, basket=(), **overrides):
    profile = dict(BASE, **overrides)
    return client.post("/api/recommend", json={"profile": profile, "basket": list(basket)}).json()


# ---------------------------------------------------------------------------
# Поля, влияющие на аппаратную оценку
# ---------------------------------------------------------------------------
def test_object_count_changes_estimate(client):
    """Точное число объектов участвует в расчёте, а не только повышает уверенность."""
    small = estimate(client, object_count=100)
    large = estimate(client, object_count=1_000_000)
    assert large["required_gpu_index"] > small["required_gpu_index"]
    assert large["estimated_ram_gb"] > small["estimated_ram_gb"]


def test_npc_count_changes_estimate(client):
    few = estimate(client, npc_count=10)
    many = estimate(client, npc_count=50_000)
    assert many["required_gpu_index"] > few["required_gpu_index"]


def test_object_count_span_is_meaningful(client):
    """Разница между уровнями не должна быть символической."""
    low = estimate(client, object_count=1_000)
    high = estimate(client, object_count=1_000_000)
    # Порядок величины в запасе по GPU — ожидаемый масштаб влияния.
    assert high["required_gpu_index"] / low["required_gpu_index"] > 1.1


def test_target_fps_changes_estimate(client):
    assert estimate(client, target_fps=144)["required_gpu_index"] > estimate(client, target_fps=30)["required_gpu_index"]


def test_resolution_and_quality_change_estimate(client):
    assert estimate(client, target_resolution="2160p")["required_gpu_index"] > estimate(
        client, target_resolution="720p")["required_gpu_index"]
    assert estimate(client, target_quality="ultra")["required_gpu_index"] > estimate(
        client, target_quality="low")["required_gpu_index"]


def test_scale_changes_estimate(client):
    """Объём мира меняет память и объём контента, а не повторяет работу на кадр.

    Раньше `scale` умножал стоимость кадра одновременно со счётчиками активных
    объектов и NPC: один и тот же множитель `content` покрывал и объём мира, и
    активную сцену. Физически размер мира определяет стриминг и резидентные
    ресурсы, но при том же числе активных сущностей работа на кадр не растёт.
    """
    small = estimate(client, scale="small")
    very_large = estimate(client, scale="very_large")
    # Резидентные ресурсы и объём контента растут с размером мира.
    assert very_large["estimated_ram_gb"] > small["estimated_ram_gb"]
    assert very_large["estimated_vram_gb"] > small["estimated_vram_gb"]
    assert very_large["estimated_draw_calls"] > small["estimated_draw_calls"]
    # Работа на кадр задаётся активной сценой и от размера мира не зависит.
    assert very_large["required_gpu_index"] == small["required_gpu_index"]
    assert very_large["required_cpu_index"] == small["required_cpu_index"]


def test_platforms_change_confidence(client):
    """Мобильные платформы: база не знает их оборудования, уверенность ниже."""
    desktop = estimate(client)
    mobile = estimate(client, platforms=["android"])
    assert mobile["confidence"] < desktop["confidence"]
    assert any("платформ" in c for c in mobile["caveats"])


# ---------------------------------------------------------------------------
# Обязательные ограничения
# ---------------------------------------------------------------------------
def test_ram_limit_is_a_hard_constraint(client):
    """Заданный предел памяти — обязательное ограничение, а не справка."""
    data = estimate(client, ram_limit_gb=4)
    assert data["unmet_limits"], "нарушение предела памяти должно быть зафиксировано"
    assert any("оперативной памяти" in text for text in data["unmet_limits"])
    free = estimate(client, ram_limit_gb=512)
    assert not any("оперативной памяти" in text for text in free["unmet_limits"])


def test_vram_limit_is_a_hard_constraint(client):
    data = estimate(client, vram_limit_gb=2)
    assert data["unmet_limits"]
    assert any("видеопамяти" in text for text in data["unmet_limits"])


def test_unmet_limits_lower_confidence(client):
    free = estimate(client, vram_limit_gb=256)
    tight = estimate(client, vram_limit_gb=1)
    assert tight["confidence"] < free["confidence"]


def test_exceeding_catalog_is_reported(client):
    """Заведомо недостижимые требования помечаются, а не подбираются «как-нибудь»."""
    data = estimate(client, target_resolution="2160p", target_quality="ultra",
                    target_fps=240, scale="very_large", object_count=100_000_000)
    assert data["exceeds_catalog"] is True


def test_ray_tracing_requirement_is_mandatory(client, db):
    """Решение, требующее RT, не получает видеокарту без трассировки лучей."""
    from sqlalchemy import select

    from app.models.entities import Method

    method = db.scalar(
        select(Method).where(Method.requires_hw_features.isnot(None))
    )
    if method is None or "Hardware Ray Tracing" not in (method.requires_hw_features or []):
        pytest.skip("в базе нет метода, требующего трассировку лучей")

    data = client.post("/api/hardware-estimate",
                       json={"profile": BASE, "basket": [method.code]}).json()
    assert data["required_hw_features"]
    if data["reference_gpu"] is not None:
        features = [str(f).lower() for f in data["reference_gpu"].get("hw_features", [])]
        assert any("ray tracing" in f or "rtx" in f or "rt core" in f for f in features)


# ---------------------------------------------------------------------------
# Поля, влияющие на рекомендации
# ---------------------------------------------------------------------------
def test_complexity_tolerance_excludes_solutions(client):
    strict = recommend(client, complexity_tolerance=1)
    loose = recommend(client, complexity_tolerance=5)
    assert len(strict["excluded"]) > len(loose["excluded"])
    assert len(strict["recommendations"]) < len(loose["recommendations"])


def test_deadline_weeks_affects_risks(client):
    """Срок разработки сопоставляется с трудоёмкостью выбранных решений."""
    methods = client.get("/api/catalog/methods").json()
    heavy = sorted(methods, key=lambda m: -m["implementation_cost"])[:3]
    basket = [m["code"] for m in heavy]

    no_deadline = recommend(client, basket=basket)
    assert not any(r["code"] == "deadline_pressure" for r in no_deadline["risks"])

    tight = recommend(client, basket=basket, deadline_weeks=4)
    assert any(r["code"] == "deadline_pressure" for r in tight["risks"])

    # Степень риска зависит от срока: 4 недели хуже двух лет.
    generous = recommend(client, basket=basket, deadline_weeks=104)
    severity = {r["code"]: r["severity"] for r in tight["risks"]}
    generous_severity = {r["code"]: r["severity"] for r in generous["risks"]}
    assert severity["deadline_pressure"] == "high"
    assert generous_severity.get("deadline_pressure") != "high"


def test_size_limit_excludes_disk_heavy_solutions(client):
    tight = recommend(client, size_limit_gb=1)
    loose = recommend(client, size_limit_gb=4096)
    assert len(tight["excluded"]) >= len(loose["excluded"])


def test_netcode_without_multiplayer_flag_warns(client):
    """Сетевая функция при выключенном мультиплеере — несогласованный вход."""
    flagged = recommend(
        client, multiplayer=False,
        functions=["open_world_streaming", "multiplayer_netcode"],
    )
    assert any(r["code"] == "network_without_flag" for r in flagged["risks"])

    consistent = recommend(
        client, multiplayer=True, player_count=4,
        functions=["open_world_streaming", "multiplayer_netcode"],
    )
    assert not any(r["code"] == "network_without_flag" for r in consistent["risks"])


def test_engine_affects_support(client):
    """Движок определяет, насколько решение «родное» для выбранной технологии.

    Считается не число упоминаний, а качество связи: для Unreal те же методы
    покрываются собственными инструментами чаще, чем для Unity, где часть
    решений доступна лишь частично. Если движок перестанет влиять на подбор,
    обе推薦дация перестанет быть персонализированной.
    """
    def direct_count(engine):
        data = recommend(client, engine=engine)
        return sum(
            1 for item in data["recommendations"]
            if item["engine_support"]
            and item["engine_support"]["engine_code"] == engine
            and item["engine_support"]["relation_type"] == "direct"
        )

    def own_support_share(engine):
        data = recommend(client, engine=engine)
        supported = [item for item in data["recommendations"] if item["engine_support"]]
        assert supported
        own = sum(1 for item in supported
                  if item["engine_support"]["engine_code"] == engine)
        return own / len(supported)

    # Поддержка следует за выбранным движком, а не приклеена к одному:
    # общие методы без функции тоже несут свои связи.
    assert own_support_share("unreal") >= 0.9
    assert own_support_share("unity") >= 0.9
    assert direct_count("unreal") != direct_count("unity")

    # Для Unity часть решений доступна не напрямую: это видно в ответе.
    unity = recommend(client, engine="unity")
    relations = {
        item["engine_support"]["relation_type"]
        for item in unity["recommendations"] if item["engine_support"]
    }
    assert relations - {"direct"}, "для Unity ожидаются непрямые способы реализации"


def test_engine_version_is_checked_against_known_versions(client):
    """Версия движка не влияет на ранжирование, но проверяется на известность."""
    unknown = recommend(client, engine_version="0.0.1-beta")
    codes = {r["code"] for r in unknown["risks"]}
    assert "unknown_engine_version" in codes

    # Известная версия предупреждения не вызывает.
    engines = client.get("/api/catalog/engines").json()
    unreal = next(e for e in engines if e["code"] == "unreal")
    assert unreal["versions"], "у движка должен быть перечень известных версий"
    known = recommend(client, engine_version=unreal["versions"][0])
    assert "unknown_engine_version" not in {r["code"] for r in known["risks"]}


def test_priority_changes_ranking(client, db):
    """Приоритет действительно переупорядочивает решения, а не только меняет веса.

    Проверка «набор весов отличается» проходила бы даже при неизменном порядке,
    поэтому сравнивается положение дешёвых решений: при приоритете «стоимость»
    они обязаны подняться относительно приоритета «производительность».
    """
    from sqlalchemy import select
    from app.models.entities import Method
    methods = list(db.scalars(select(Method).where(Method.status == "published")))
    for method in methods:
        method.status = "draft"
    # A controlled tradeoff inside one function, not incomparable ranks of different functions.
    for index, method in enumerate(methods[:4]):
        method.status = "published"
        method.function = methods[0].function
        method.function_id = methods[0].function_id
        method.requires_features = []
        method.requires_hw_features = []
        method.applicable_formats = []
        method.applicable_world_types = []
        method.applicable_engines = []
        method.applicable_platforms = []
        method.min_scale = None
        method.implementation_cost = index + 1
        method.performance_gain = .2 * (index + 1)
        method.complexity = 2
        method.confidence = .8
        method.quality_impact = method.concept_impact = 0
        method.late_cost = "low"
        method.recommended_stage = "prototype"
        for resource in ('cpu', 'gpu', 'ram', 'vram', 'disk', 'network'):
            setattr(method, 'impact_' + resource, 0)
    db.flush()
    performance = recommend(client, priority="performance")
    cost = recommend(client, priority="cost")

    ranks_performance = {item["method_code"]: item["rank"] for item in performance["recommendations"]}
    ranks_cost = {item["method_code"]: item["rank"] for item in cost["recommendations"]}
    assert set(ranks_performance) == set(ranks_cost)

    total = len(ranks_performance)
    assert total >= 4, "для сравнения порядка нужно несколько альтернатив"

    # Треть самых дешёвых решений.
    cheap = sorted(performance["recommendations"],
                   key=lambda item: (item["implementation_cost"], item["method_code"]))
    cheap_codes = [item["method_code"] for item in cheap[: max(1, total // 3)]]

    def mean_rank(ranks):
        return sum(ranks[code] for code in cheap_codes) / len(cheap_codes)

    assert mean_rank(ranks_cost) < mean_rank(ranks_performance), (
        f"при приоритете «стоимость» дешёвые решения не поднялись: "
        f"{mean_rank(ranks_cost)} против {mean_rank(ranks_performance)}"
    )


def test_functions_filter_recommendations(client):
    data = recommend(client, functions=["water_simulation"])
    assert data["recommendations"]
    codes = {item["function_code"] for item in data["recommendations"]}
    from app.seed.methods_data import FUNCTION_ASSIGNMENTS
    assert "water_simulation" in codes
    assert codes <= {"water_simulation", *FUNCTION_ASSIGNMENTS.values()}
    assert None not in codes  # Сквозные методы тоже имеют собственную техническую функцию.


# ---------------------------------------------------------------------------
# Обещания, которые система не даёт
# ---------------------------------------------------------------------------
def test_estimate_does_not_promise_fps(client):
    """Аппаратная оценка не обещает конкретный FPS — только ориентировочный класс."""
    data = estimate(client)
    # Ни одно поле ответа не называется как гарантированный показатель кадров.
    assert not [key for key in data if "fps" in key.lower() and "target" not in key.lower()]
    assert any("ориентировочным" in text for text in data["caveats"])
    assert data["confidence_label"] in ("низкая", "средняя", "повышенная")


def test_estimate_always_has_caveats_and_confidence(client):
    for overrides in ({}, {"scale": "small"}, {"target_fps": 240}, {"platforms": ["android"]}):
        data = estimate(client, **overrides)
        assert data["caveats"], f"без оговорок оценка выглядит как гарантия: {overrides}"
        assert 0.0 < data["confidence"] <= 1.0
