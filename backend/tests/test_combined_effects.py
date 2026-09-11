"""Совместное действие методов (офлайн).

Дефекты: двойной учёт одного эффекта, наивное сложение улучшений,
применение эффекта вне его области (сервер/разработка удешевляют ПК
игрока, не-клиентская скидка, out-of-frame молча).
"""
from __future__ import annotations

import pytest

BASE = {
    "name": "Совместный учёт",
    "format": "3D",
    "world_type": "open_world",
    "scale": "large",
    "stage": "prototype",
    "engine": "unreal",
    "platforms": ["pc_windows"],
    "functions": ["open_world_streaming", "crowd_simulation"],
    "target_resolution": "1080p",
    "target_quality": "high",
    "target_fps": 60,
}


def estimate(client, basket=(), **overrides):
    profile = dict(BASE, **overrides)
    response = client.post(
        "/api/hardware-estimate", json={"profile": profile, "basket": list(basket)}
    )
    assert response.status_code == 200, response.text
    return response.json()


def recommend(client, basket=(), **overrides):
    profile = dict(BASE, **overrides)
    response = client.post(
        "/api/recommend", json={"profile": profile, "basket": list(basket)}
    )
    assert response.status_code == 200, response.text
    return response.json()


#: Обязательные предусловия решений, которые тесты берут в корзину по одному.
#:
#: Каталог объявляет обязательные зависимости («чтобы включить A, сначала
#: нужен B»), и правило проекта требует явного исключения зависимого решения,
#: когда его предусловие отсутствует. Поэтому корзина из одного решения
#: проверяла бы не эффект решения, а срабатывание этого правила.
#:
#: Предусловия здесь **не перечисляются руками**. Раньше в этом месте лежала
#: рукописная копия карты предусловий, и она разошлась с графом: `static_shadow_caching`
#: → `virtual_shadow_maps` в копию не попал, из-за чего пара «два расхода
#: складываются» проверяла один и тот же набор дважды. Достройку выполняет сам
#: расчёт (`services.method_dependencies`), и тест обязан проверять именно её.


def with_prerequisites(*codes: str) -> list[str]:
    """Корзина из указанных решений.

    Обязательные предусловия достраивает расчёт — тем же замыканием, что и в
    `/recommend` и `/schedule`. Дублировать их в тесте нельзя: копия правила
    неизбежно расходится с графом и перестаёт что-либо проверять.
    """
    return list(codes)


def test_streaming_pool_counts_only_transient_part(client):
    """Пул 8 ГБ не даёт +8 RAM / +4 VRAM поверх текстур (двойной учёт объёма)."""
    base = estimate(client)
    with_pool = estimate(client, streaming_pool_gb=8)
    delta_ram = with_pool["estimated_ram_gb"] - base["estimated_ram_gb"]
    delta_vram = with_pool["estimated_vram_gb"] - base["estimated_vram_gb"]
    assert 0.3 <= delta_ram <= 0.8
    assert 0.0 < delta_vram <= 0.3


def test_upscaling_field_and_card_act_once(client):
    """Поле и карточка апскейлинга — одно действие, а не две скидки."""
    field_only = estimate(client, upscaling_method="fsr")
    both = estimate(client, upscaling_method="fsr", basket=["temporal_upscaling"])
    assert both["gpu_raster_cost"] == pytest.approx(field_only["gpu_raster_cost"])
    assert both["estimated_vram_gb"] > field_only["estimated_vram_gb"]


def test_frame_generation_field_and_card_act_once(client):
    """Поле и карточка генерации кадров — один синтез, а не две скидки."""
    overrides = {"frame_generation": True, "base_render_fps": 60, "target_fps": 120}
    field_only = estimate(client, **overrides)
    both = estimate(
        client, basket=with_prerequisites("ml_frame_generation"), **overrides
    )
    # Карточка ML-генерации требует temporal_upscaling, который законно
    # удешевляет растр, поэтому равенство растра не гарантируется. Проверяем
    # то, что заявлено в названии: синтез промежуточных кадров начисляется
    # один раз, а не дважды — поле и карточка вместе не дают второй цифры.
    fg_field = next(
        s["share"] for s in field_only["gpu_subsystems"]
        if s["label"] == "Генерация кадров"
    )
    fg_both = next(
        s["share"] for s in both["gpu_subsystems"]
        if s["label"] == "Генерация кадров"
    )
    assert fg_both == pytest.approx(fg_field, abs=0.01)
    # Карточка добавляет буферы генератора — объём видеопамяти растёт.
    assert both["estimated_vram_gb"] > field_only["estimated_vram_gb"]


def test_rt_cost_scales_with_resolution(client):
    """RT-проход дорожает с разрешением (1080p → 4K более чем вдвое)."""
    # Предусловия RT-метода требуют функций «ray_traced_effects» и
    # «dynamic_lighting»: без них решение исключается по правилу зависимостей,
    # и RT-проход не вводился бы вовсе.
    functions = BASE["functions"] + ["ray_traced_effects", "dynamic_lighting"]
    basket = with_prerequisites("hardware_raytraced_gi")
    low = estimate(client, basket=basket, functions=functions, target_resolution="1080p")
    high = estimate(client, basket=basket, functions=functions, target_resolution="2160p")
    assert low["gpu_rt_cost"] > 0
    assert high["gpu_rt_cost"] > low["gpu_rt_cost"] * 2.0


def test_rt_budget_reduces_introduced_pass(client):
    """Бюджет трассировки сокращает введённый проход, а не теряется."""
    functions = BASE["functions"] + ["ray_traced_effects"]
    plain = estimate(
        client, basket=with_prerequisites("hardware_raytraced_gi"), functions=functions
    )
    budgeted = estimate(
        client,
        basket=with_prerequisites("hardware_raytraced_gi", "rt_effect_resolution_budget"),
        functions=functions,
    )
    assert plain["gpu_rt_cost"] > 0
    assert budgeted["gpu_rt_cost"] < plain["gpu_rt_cost"]


def test_raster_and_rt_share_one_frame_budget(client):
    """Растр и трассировка укладываются в один бюджет кадра: работа складывается.

    Границы заданы независимо от формулы реализации, из правила «все проходы
    делят один бюджет»: индекс обязан быть больше доли любого отдельного
    прохода (иначе учтён только самый тяжёлый) и не больше суммы долей
    (иначе часть работы учтена дважды). На этой корзине трассировка дороже
    растра, поэтому «только самый тяжёлый проход» дал бы примерно половину.
    """
    functions = BASE["functions"] + ["ray_traced_effects"]
    data = estimate(client, basket=["hardware_raytraced_gi"], functions=functions)
    budget_ms = 1000.0 / BASE["target_fps"]
    raster = data["gpu_raster_cost"] / budget_ms
    rt = data["gpu_rt_cost"] / budget_ms
    assert raster > 0 and rt > 0
    assert data["required_gpu_index"] > max(raster, rt) + 0.05
    assert data["required_gpu_index"] <= raster + rt + 0.02


def test_two_increments_sum_but_two_savings_count_once(client):
    """Два расхода складываются; две экономии одного объёма — по максимуму.

    Пара для «расходов» выбрана без обязательной связи между методами. Прежняя
    пара (`static_shadow_caching` + `virtual_shadow_maps`) для этого не годится:
    кэш теней требует виртуальных карт теней, поэтому его корзина уже содержит
    оба метода, и как два независимых расхода они не проверяют ничего (см.
    `test_mandatory_dependency_is_pulled_into_the_basket`).
    """
    first = estimate(client, basket=["cascaded_shadow_maps"])
    second = estimate(client, basket=["distance_field_shadows"])
    both_up = estimate(
        client, basket=["cascaded_shadow_maps", "distance_field_shadows"]
    )
    assert both_up["estimated_vram_gb"] > first["estimated_vram_gb"]
    assert both_up["estimated_vram_gb"] > second["estimated_vram_gb"]

    functions = BASE["functions"] + ["large_scale_terrain", "procedural_terrain"]
    base = estimate(client, functions=functions)["estimated_vram_gb"]
    first = estimate(
        client, basket=with_prerequisites("heightmap_compression"), functions=functions
    )
    second = estimate(
        client, basket=with_prerequisites("neural_texture_compression"), functions=functions
    )
    both_down = estimate(
        client,
        basket=with_prerequisites("heightmap_compression", "neural_texture_compression"),
        functions=functions,
    )
    saving = lambda result: base - result["estimated_vram_gb"]
    assert saving(first) > 0 and saving(second) > 0
    assert saving(both_down) == pytest.approx(
        max(saving(first), saving(second)), abs=0.2
    )
    assert saving(both_down) < saving(first) + saving(second)


def test_mandatory_dependency_is_pulled_into_the_basket(client):
    """Обязательная зависимость достраивается, а не выбрасывает метод из расчёта.

    `static_shadow_caching` без `virtual_shadow_maps` не реализуется. Раньше
    такой метод молча выпадал из расчёта: профиль нагрузки показывал нейтральные
    50/50 при непустой корзине. Теперь корзина с зависимостью и без неё
    считается одинаково — потому что это один и тот же набор методов.
    """
    alone = estimate(client, basket=["static_shadow_caching"])
    explicit = estimate(
        client, basket=["static_shadow_caching", "virtual_shadow_maps"]
    )
    neutral = estimate(client, basket=[])

    assert alone["estimated_vram_gb"] == pytest.approx(explicit["estimated_vram_gb"])
    assert alone["estimated_vram_gb"] > neutral["estimated_vram_gb"], "корзина схлопнулась"


def test_closure_additions_are_reported_and_counted(client):
    """Достроенные зависимости видны отдельной группой и входят в расчёт."""
    data = recommend(client, basket=["static_shadow_caching"])
    neutral = recommend(client, basket=[])

    assert data["basket_codes"] == ["static_shadow_caching"], "корзина пользователя переписана"
    assert "virtual_shadow_maps" in {item["code"] for item in data["required_additionally"]}
    assert data["required_additionally_notes"]
    # Объявленная, но не посчитанная зависимость — та же потеря, только скрытая.
    assert "virtual_shadow_maps" in data["accounted_method_codes"]
    assert data["load_profile"]["vram"] != neutral["load_profile"]["vram"]


def test_server_effect_does_not_discount_player_pc(client):
    """Сервер без графики не облегчает рендер у игрока (область эффекта)."""
    base = estimate(
        client, functions=["multiplayer_netcode"], multiplayer=True,
    )
    selected = estimate(
        client,
        basket=["headless_dedicated_server"],
        functions=["multiplayer_netcode"],
        multiplayer=True,
    )
    assert selected["required_gpu_index"] == base["required_gpu_index"]
    assert selected["required_cpu_index"] == base["required_cpu_index"]


def test_out_of_frame_effect_is_named_not_silent(client):
    """Эффект вне стоимости кадра назван в exclusions, а не пропущен молча."""
    notes = recommend(client, basket=["pso_precaching_warmup"])["contributions"][
        "exclusions"
    ]
    assert any("кадра" in note for note in notes)
