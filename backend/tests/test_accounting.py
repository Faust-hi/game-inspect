"""Повторный и потерянный учёт: одна и та же работа считается один раз.

Исследование упрощённого MVP (docs/research/CONTINUATION-2026-09-09.md,
пункт 3 плана исправлений) выделило четыре класса ошибок:

* бюджет подкачки целиком прибавлялся в RAM и половиной в VRAM поверх уже
  посчитанных текстур — один объём учитывался дважды;
* добавка трассировки лучей прибавлялась после масштабирования по разрешению
  и не менялась при переходе 1080p → 4K;
* экономия подсистемы ``rt`` применялась к нулевой базе и терялась молча:
  бюджетные решения не сокращали только что введённый проход;
* поле и карточка апскейлинга/генерации кадров действовали дважды по одной
  технологии, а противоречивый ввод не объяснялся.

Тесты фиксируют исправленное поведение.
"""
from __future__ import annotations

import pytest

BASE = {
    "name": "Учёт",
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
    return client.post(
        "/api/hardware-estimate", json={"profile": profile, "basket": list(basket)}
    ).json()


def recommend(client, basket=(), **overrides):
    profile = dict(BASE, **overrides)
    return client.post("/api/recommend", json={"profile": profile, "basket": list(basket)}).json()


def assumptions(result) -> list[str]:
    return result["contributions"]["assumptions"]


def method_contributions(result) -> list[dict]:
    return result["contributions"]["methods"]


# ---------------------------------------------------------------------------
# Бюджет подкачки: состав пула и исключение двойного счёта
# ---------------------------------------------------------------------------
def test_streaming_pool_adds_only_transient_part(client):
    """Пул не прибавляется целиком в RAM и половиной в VRAM поверх текстур.

    Раньше пул 8 ГБ давал +8 ГБ RAM и +4 ГБ VRAM сверх уже посчитанных
    резидентных текстур. Теперь сверх резидентных компонентов идёт только
    транзитная часть: буферы загрузки, распаковки и опережающей подкачки.
    """
    base = estimate(client)
    with_pool = estimate(client, streaming_pool_gb=8)

    delta_ram = with_pool["estimated_ram_gb"] - base["estimated_ram_gb"]
    delta_vram = with_pool["estimated_vram_gb"] - base["estimated_vram_gb"]
    # Транзитная часть пула 8 ГБ — 2 ГБ, из них 0.6 ГБ в VRAM; без пула модель
    # держала собственное допущение подкачки 0.9/0.5 ГБ.
    assert 0.3 <= delta_ram <= 0.8
    assert 0.0 < delta_vram <= 0.3
    # Прежний двойной учёт давал бы кратные значения.
    assert delta_ram < 2.0
    assert delta_vram < 1.0


def test_memory_increases_of_one_component_are_summed(client):
    """Два добавочных расхода одного компонента складываются, а не заменяются.

    Ветвь памяти выбирала наименьшее изменение компонента, поэтому из двух
    увеличивающих расходов выживал меньший, а бóльший пропадал молча:
    изолированная проба давала VSM 12.5 и статическое кэширование 10.8 по
    отдельности, но 10.8 вместе.
    """
    vsm = estimate(client, basket=["virtual_shadow_maps"])
    caching = estimate(client, basket=["static_shadow_caching"])
    both = estimate(client, basket=["virtual_shadow_maps", "static_shadow_caching"])

    # Каждое решение добавляет свой объём целевых буферов.
    assert both["estimated_vram_gb"] > vsm["estimated_vram_gb"]
    assert both["estimated_vram_gb"] > caching["estimated_vram_gb"]


def test_memory_saving_is_still_counted_once(client):
    """Экономия того же ресурса по-прежнему берётся один раз.

    Складывание добавочных расходов не означает сложение экономий: два решения
    не могут сэкономить один и тот же объём текстур дважды.
    """
    functions = BASE["functions"] + ["large_scale_terrain"]
    base = estimate(client, functions=functions)["estimated_vram_gb"]
    first = estimate(client, basket=["heightmap_compression"], functions=functions)
    second = estimate(client, basket=["neural_texture_compression"], functions=functions)
    both = estimate(
        client,
        basket=["heightmap_compression", "neural_texture_compression"],
        functions=functions,
    )

    saving_first = base - first["estimated_vram_gb"]
    saving_second = base - second["estimated_vram_gb"]
    saving_both = base - both["estimated_vram_gb"]
    assert saving_first > 0 and saving_second > 0
    assert saving_both == pytest.approx(max(saving_first, saving_second), abs=0.2)
    assert saving_both < saving_first + saving_second


def test_streaming_pool_composition_is_explained(client):
    """Состав пула объясняется: что прибавлено, а что уже учтено в текстурах."""
    notes = assumptions(recommend(client, streaming_pool_gb=8))

    assert any("Бюджет подкачки задан" in note for note in notes)
    assert any("повторно не учитывается" in note for note in notes)


def test_small_streaming_pool_reports_contradiction(client):
    """Пул меньше резидентного набора профиля — противоречие видно явно."""
    notes = assumptions(recommend(client, streaming_pool_gb=1))

    assert any("меньше резидентного набора" in note for note in notes)


# ---------------------------------------------------------------------------
# Трассировка лучей: масштаб по разрешению и применение бюджета к проходу
# ---------------------------------------------------------------------------
def test_rt_cost_scales_with_resolution(client):
    """RT-проход дорожает вместе с внутренним разрешением.

    Раньше добавка из эффекта решения прибавлялась после масштабирования:
    1080p → 4K оставляла стоимость трассировки неизменной, хотя число лучей
    растёт вместе с числом пикселей.
    """
    basket = ["hardware_raytraced_gi"]
    low = estimate(client, basket=basket, target_resolution="1080p")
    high = estimate(client, basket=basket, target_resolution="2160p")

    assert low["gpu_rt_cost"] > 0
    assert high["gpu_rt_cost"] > low["gpu_rt_cost"] * 2.0


def test_rt_budget_reduces_the_introduced_pass(client):
    """Бюджет трассировки сокращает введённый проход, а не теряется.

    Экономия подсистемы ``rt`` применялась к нулевой базе и пропадала молча:
    проход вводился позже применения экономии.
    """
    functions = BASE["functions"] + ["ray_traced_effects"]
    gi = estimate(client, basket=["hardware_raytraced_gi"], functions=functions)
    budgeted = estimate(
        client,
        basket=["hardware_raytraced_gi", "rt_effect_resolution_budget"],
        functions=functions,
    )

    assert gi["gpu_rt_cost"] > 0
    assert budgeted["gpu_rt_cost"] < gi["gpu_rt_cost"]


# ---------------------------------------------------------------------------
# Апскейлинг: один источник внутреннего разрешения, а не поле плюс карточка
# ---------------------------------------------------------------------------
def test_upscaling_field_and_card_do_not_double_act(client):
    """Карточка не добавляет вторую скидку поверх явно указанного апскейлера.

    Раньше поле «FSR» и карточка временного апскейлинга давали два разных
    действия по одной технологии без различения реализации и правки.
    """
    field_only = estimate(client, upscaling_method="fsr")
    both = estimate(client, upscaling_method="fsr", basket=["temporal_upscaling"])

    assert both["gpu_raster_cost"] == pytest.approx(field_only["gpu_raster_cost"])
    # Карточка по-прежнему видна в расчёте — буферами истории кадров.
    assert both["estimated_vram_gb"] > field_only["estimated_vram_gb"]


def test_upscaling_none_with_card_is_explained(client):
    """Противоречивый ввод (апскейлинг отключён + карточка) объясняется."""
    plain = estimate(client, upscaling_method="none")
    card = estimate(client, upscaling_method="none", basket=["temporal_upscaling"])
    notes = assumptions(recommend(client, upscaling_method="none", basket=["temporal_upscaling"]))

    # Поле анкеты имеет приоритет: скидки внутреннего разрешения нет.
    assert card["gpu_raster_cost"] == pytest.approx(plain["gpu_raster_cost"])
    assert any("отключён" in note and "Временной апскейлинг" in note for note in notes)


# ---------------------------------------------------------------------------
# Динамическое разрешение: меняет внутреннее разрешение, а не постобработку
# ---------------------------------------------------------------------------
def test_dynamic_resolution_changes_internal_resolution(client):
    """Динамическое разрешение удешевляет пиксельные стадии, а не только пост."""
    base = estimate(client)
    drs = estimate(client, basket=["dynamic_resolution_scaling"])
    notes = assumptions(recommend(client, basket=["dynamic_resolution_scaling"]))

    assert drs["gpu_raster_cost"] < base["gpu_raster_cost"]
    assert any("снижает внутреннее разрешение" in note for note in notes)


def test_dynamic_resolution_scales_rt_pass(client):
    """Тот же множитель внутреннего разрешения действует и на трассировку."""
    gi = estimate(client, basket=["hardware_raytraced_gi"])
    both = estimate(
        client, basket=["hardware_raytraced_gi", "dynamic_resolution_scaling"]
    )

    assert both["gpu_rt_cost"] < gi["gpu_rt_cost"]


# ---------------------------------------------------------------------------
# Генерация кадров: стоимость синтеза считается один раз
# ---------------------------------------------------------------------------
def test_frame_generation_field_and_card_counted_once(client):
    """Поле и карточка не начисляют две стоимости одного ML-прохода."""
    overrides = {"frame_generation": True, "base_render_fps": 60, "target_fps": 120}
    field_only = estimate(client, **overrides)
    both = estimate(client, basket=["ml_frame_generation"], **overrides)

    assert both["gpu_raster_cost"] == pytest.approx(field_only["gpu_raster_cost"])
    # Карточка остаётся в расчёте буферами генератора.
    assert both["estimated_vram_gb"] > field_only["estimated_vram_gb"]


def test_frame_generation_card_without_flag_is_explained(client):
    """Карточка без включённого поля не считает синтез молча — объясняет."""
    notes = assumptions(recommend(client, basket=["ml_frame_generation"]))

    assert any(
        "ML-генерация кадров" in note and "не включена" in note for note in notes
    )


# ---------------------------------------------------------------------------
# Базовая функция и её реализация: один проход, а не два
# ---------------------------------------------------------------------------
def test_full_path_tracing_does_not_add_a_second_base_pass(client):
    """Реализация не вводит второй базовый проход поверх функции.

    Функция `path_tracing` уже вносит стоимость трассировки: реализация
    описывает способ её выполнения и забирает растровое освещение, но не
    добавляет ещё одну фиксированную стоимость того же прохода.
    """
    functions = BASE["functions"] + ["path_tracing"]
    function_only = estimate(client, functions=functions)
    implemented = estimate(
        client, basket=["full_path_tracing_pipeline"], functions=functions
    )

    assert function_only["gpu_rt_cost"] > 0
    assert implemented["gpu_rt_cost"] == pytest.approx(function_only["gpu_rt_cost"])
    # Зато реализация забирает растровое освещение — это видно отдельно.
    assert implemented["gpu_raster_cost"] < function_only["gpu_raster_cost"]


def test_selective_rt_effects_limit_the_existing_pass(client):
    """Выборочная трассировка ограничивает проход, а не создаёт новый."""
    functions = BASE["functions"] + ["ray_traced_effects"]
    base = estimate(client, functions=functions)
    selective = estimate(client, basket=["selective_ray_traced_effects"], functions=functions)

    assert base["gpu_rt_cost"] > 0
    assert selective["gpu_rt_cost"] < base["gpu_rt_cost"]


def test_gpu_raster_and_rt_share_one_frame_budget(client):
    """Растровый и RT-проходы не получают каждый полный бюджет кадра.

    Раньше требование к GPU бралось по более тяжёлой из двух частей:
    растеризация на 60% бюджета и трассировка на 60% выглядели
    укладывающимися в кадр, хотя последовательные проходы занимают 120%.
    """
    functions = BASE["functions"] + ["ray_traced_effects"]
    result = estimate(client, basket=["hardware_raytraced_gi"], functions=functions)
    budget_ms = 1000.0 / BASE["target_fps"]

    assert result["gpu_rt_cost"] > 0
    assert result["gpu_raster_cost"] > 0
    # Требование — сумма долей проходов, а не максимум.
    assert result["required_gpu_index"] == pytest.approx(
        (result["gpu_raster_cost"] + result["gpu_rt_cost"]) / budget_ms, abs=0.02
    )
    assert result["required_gpu_index"] > result["gpu_rt_cost"] / budget_ms


# ---------------------------------------------------------------------------
# Собственная стоимость решения не выдаётся за экономию
# ---------------------------------------------------------------------------
def test_gpu_compute_culling_pays_for_its_pass(client):
    """Отсечение на GPU добавляет вычисления и экономит невидимую геометрию.

    Прежде карта показывала только экономию вычислений, то есть выдавала
    собственную стоимость прохода за выигрыш.
    """
    items = method_contributions(recommend(client, basket=["gpu_compute_culling"]))

    compute = [item for item in items if item["label"].endswith("Вычисления на GPU")]
    geometry = [item for item in items if item["label"].endswith("Геометрия")]
    assert compute and compute[0]["delta"] > 0
    assert geometry and geometry[0]["delta"] < 0


def test_particle_pooling_holds_memory_instead_of_releasing_it(client):
    """Пул удерживает объекты: уменьшение памяти сцены не обещается."""
    base = estimate(client)
    pooling = estimate(client, basket=["particle_pooling"])

    assert pooling["estimated_ram_gb"] >= base["estimated_ram_gb"]
    assert pooling["estimated_vram_gb"] >= base["estimated_vram_gb"]


def test_animation_data_is_a_separate_memory_component(client):
    """Анимационные данные не записываются в геометрию."""
    labels = [item["label"] for item in estimate(client)["memory_composition"]]

    assert any("Анимационные данные" in label for label in labels)


def test_effect_outside_the_frame_is_explained(client):
    """Эффект вне стоимости кадра назван, а не пропущен молча."""
    notes = recommend(client, basket=["pso_precaching_warmup"])["contributions"]["exclusions"]

    assert any("прогрев" in note.lower() for note in notes)
    assert any("кадра" in note for note in notes)
