"""Аппаратный слой: причина отказа и узкое место согласованы с расчётом (N8).

Проверяется три вещи:

* узкое место сравнивается с суммарным индексом GPU (растеризация + RT), а не
  с половинами одной стадии — иначе диагноз расходится с подбором видеокарты;
* ``_pick_gpu`` называет причину отказа (RT / видеопамять / производительность),
  поэтому сообщение описывает настоящую причину, а не первую подходящую;
* отсев пула по API не выдаётся за отсутствие обязательных возможностей и
  наоборот.
"""
from __future__ import annotations

import pytest

BASE = {
    "name": "Сообщения железа",
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


class _GPU:
    """Минимальная карта для проверки подбора: те же поля, что у каталога."""

    def __init__(self, model, raster, rt, vram, features=(), api=("DirectX 12",), perf_class=1):
        self.model = model
        self.raster_score = raster
        self.rt_score = rt
        self.vram_gb = vram
        self.hw_features = list(features)
        self.api_support = list(api)
        self.perf_class = perf_class


# --- Узкое место -----------------------------------------------------------

@pytest.mark.critical
def test_bottleneck_sums_raster_and_rt():
    """Узкое место — суммарный GPU, а не его половины.

    Дефект: индекс GPU и стоимость кадра складывают растеризацию и трассировку,
    а `_bottleneck` сравнивал их порознь. При raster = RT = 0.4 и CPU = 0.5
    узким местом назывался CPU, хотя ограничитель — GPU (0.8).
    """
    from app.services import hardware as hardware_service

    key, title = hardware_service._bottleneck(
        st_index=0.5, mt_index=0.4, raster_index=0.4, rt_index=0.4, memory_pressure=0.0,
    )
    assert key == "gpu"
    assert "GPU" in title


@pytest.mark.critical
def test_bottleneck_still_names_cpu_when_cpu_dominates():
    """Суммирование GPU не отменяет диагноз CPU там, где он действительно узкий."""
    from app.services import hardware as hardware_service

    key, _ = hardware_service._bottleneck(
        st_index=0.9, mt_index=0.3, raster_index=0.2, rt_index=0.2, memory_pressure=0.0,
    )
    assert key == "cpu_main_thread"


@pytest.mark.extended
def test_bottleneck_has_no_separate_raster_and_rt_stages():
    """Раздельных ключей растровой и RT-стадии больше нет.

    Они описывали половины одной стадии кадра: наличие такого ключа означало бы,
    что диагноз снова расходится с подбором железа.
    """
    from app.services import hardware as hardware_service

    assert set(hardware_service.BOTTLENECK_TITLES) == {
        "cpu_main_thread", "cpu_parallel", "gpu", "memory",
    }


@pytest.mark.critical
def test_reported_bottleneck_matches_model_stages(client):
    """Ответ API называет стадию из модели, а не строку, которой в модели нет."""
    from app.services import hardware as hardware_service

    data = estimate(client)
    assert data["bottleneck"] in hardware_service.BOTTLENECK_TITLES
    assert data["bottleneck_label"] == hardware_service.BOTTLENECK_TITLES[data["bottleneck"]]


# --- Причина отказа в подборе видеокарты -----------------------------------

@pytest.mark.critical
def test_pick_gpu_names_rt_reason():
    """Нет карты с трассировкой лучей — названа именно эта причина."""
    from app.services import hardware as hardware_service

    pool = [_GPU("GeForce GTX 1660 Super", 0.4, 0.0, 8.0)]
    gpu, reason = hardware_service._pick_gpu(
        pool, raster_index=0.1, rt_index=0.1, required_rt=True, vram_gb=4.0,
    )
    assert gpu is None
    assert reason == "rt"


@pytest.mark.critical
def test_pick_gpu_names_vram_reason():
    """Карта нужного класса есть, но объёма не хватает — названа память."""
    from app.services import hardware as hardware_service

    pool = [_GPU("GeForce RTX 4090", 1.0, 1.0, 8.0, features=["Ray Tracing"])]
    gpu, reason = hardware_service._pick_gpu(
        pool, raster_index=0.1, rt_index=0.0, required_rt=True, vram_gb=16.0,
    )
    assert gpu is None
    assert reason == "vram"


@pytest.mark.critical
def test_pick_gpu_names_perf_reason():
    """Памяти хватает, класса не хватает — названа производительность."""
    from app.services import hardware as hardware_service

    pool = [_GPU("GeForce RTX 3060", 0.43, 0.4, 12.0, features=["Ray Tracing"])]
    gpu, reason = hardware_service._pick_gpu(
        pool, raster_index=0.95, rt_index=0.9, required_rt=True, vram_gb=8.0,
    )
    assert gpu is None
    assert reason == "perf"


@pytest.mark.extended
def test_pick_gpu_has_no_reason_on_success():
    """Успешный подбор причины отказа не имеет."""
    from app.services import hardware as hardware_service

    pool = [_GPU("GeForce RTX 4090", 1.0, 1.0, 24.0, features=["Ray Tracing"])]
    gpu, reason = hardware_service._pick_gpu(
        pool, raster_index=0.1, rt_index=0.1, required_rt=True, vram_gb=8.0,
    )
    assert gpu is not None
    assert reason is None


# --- Сообщение и причина совпадают -----------------------------------------

@pytest.mark.extended
def test_api_filtered_pool_is_blamed_on_api(client, monkeypatch):
    """Пул отсеян по API — сообщение говорит про API.

    Дефект: при пустом `api_compatible` список неподтверждённых возможностей
    вычислялся по пустому множеству карт, поэтому сообщение объявляло отсутствие
    ВСЕХ обязательных возможностей сразу, хотя настоящая причина — API.
    """
    from app.services import hardware as hardware_service

    monkeypatch.setattr(
        hardware_service, "_supports_profile_gpu", lambda gpu, profile: False,
    )
    data = estimate(client, basket=["gpu_particle_simulation"])
    joined = " ".join(data["unmet_limits"])
    assert "не подтверждает выбранный API" in joined
    assert "обязательных возможностей" not in joined


@pytest.mark.extended
def test_capability_filtered_pool_names_the_capability(client, monkeypatch):
    """Пул отсеян по обязательной возможности — названа возможность, не API."""
    from app.services import hardware as hardware_service

    real = hardware_service._gpu_feature_support

    def fake(gpu, required):
        if (required or "").strip().lower() == "compute shaders":
            return False
        return real(gpu, required)

    monkeypatch.setattr(hardware_service, "_gpu_feature_support", fake)
    data = estimate(client, basket=["gpu_particle_simulation"])
    joined = " ".join(data["unmet_limits"])
    assert "Compute Shaders" in joined
    assert "не подтверждает выбранный API" not in joined


@pytest.mark.extended
def test_no_single_gpu_covers_all_capabilities_is_said_as_such(client, monkeypatch):
    """Каждая возможность по отдельности подтверждена, вместе — ни одной картой.

    Это отдельный случай: сообщение «нет GPU с поддержкой возможностей» было бы
    неверным (карты есть), а «нет карты под API» — тоже (API подходит).
    """
    from app.services import hardware as hardware_service

    real = hardware_service._gpu_feature_support

    def fake(gpu, required):
        req = (required or "").strip().lower()
        name = (gpu.model or "").lower()
        if req == "bindless textures":
            return "rtx" in name
        if req == "compute shaders":
            return "gtx" in name
        return real(gpu, required)

    monkeypatch.setattr(hardware_service, "_gpu_feature_support", fake)
    data = estimate(client, basket=["bindless_uber_shaders", "gpu_particle_simulation"])
    joined = " ".join(data["unmet_limits"])
    assert "одновременно подтверждает все" in joined
    assert "нет GPU с подтверждённой поддержкой обязательных возможностей" not in joined


@pytest.mark.critical
def test_violated_limit_is_a_structural_verdict_not_only_text(client):
    """Нарушенный предел виден машинно, а не только строкой в списке.

    `exceeds_catalog` отвечает на вопрос «покрывает ли каталог требование» и
    при нарушенных пределах профиля остаётся `False`: карта в каталоге есть.
    Поэтому потребитель, читавший этот флаг как «конфигурация подходит»,
    получал утвердительный ответ там, где заданный бюджет не соблюдён.
    Вердикт по пределам вынесен в отдельное поле и не подменяет собой
    покрытие каталога. Числа при этом не клампятся: требуемую память нельзя
    уменьшить указом, меняется только вердикт.
    """
    ok = estimate(client)
    assert ok["constraints_satisfied"] is True
    assert ok["unmet_limits"] == []

    violated = estimate(client, ram_limit_gb=4, vram_limit_gb=2)
    assert violated["constraints_satisfied"] is False
    assert violated["unmet_limits"], "пределы нарушены, но список пуст"
    # Покрытие каталога — другой вопрос, и он не должен меняться от пределов.
    assert violated["exceeds_catalog"] is False
    # Числа не клампятся: меняется вердикт, а не требуемая память.
    assert violated["estimated_ram_gb"] == ok["estimated_ram_gb"]
    assert violated["estimated_vram_gb"] == ok["estimated_vram_gb"]
    assert violated["required_gpu_index"] == ok["required_gpu_index"]


@pytest.mark.critical
def test_target_fps_is_applied_and_no_unmodelled_goals_remain(client):
    """Единственная цель сборки участвует в расчёте; необеспеченных целей нет.

    `target_fps` задаёт бюджет кадра (1000/FPS) и через него влияет на требуемую
    производительность, поэтому статус `not_modeled` рядом с числом, посчитанным
    из этой же цели, был неправдой — теперь `applied`.

    Цели, для которых модели нет (1% low, время запуска и сохранения, задержка
    стриминга, сетевая задержка и трафик, серверный tick), из профиля убраны:
    объявлять пробел для данных, которых система не собирает и не считает,
    значит создавать вид функции, которой нет. Тест держит это решение —
    возврат поля в схему уронит проверку.
    """
    from app.schemas.catalog import ProjectProfile

    data = estimate(client, target_fps=60)
    statuses = {item["metric"]: item["status"] for item in data["target_assessments"]}
    assert statuses == {"target_fps": "applied"}

    # Предпосылка: цель действительно меняет расчёт, иначе статус `applied` лжив.
    slower = estimate(client, target_fps=120)
    assert slower["required_gpu_index"] > data["required_gpu_index"]

    for gone in (
        "target_1_percent_low_fps", "max_startup_seconds", "max_streaming_latency_ms",
        "max_save_seconds", "target_network_latency_ms", "target_server_tick_hz",
        "max_network_kbps", "deadline_weeks",
    ):
        assert gone not in ProjectProfile.model_fields, (
            f"поле {gone} вернулось в профиль: для него нет ни анкеты, ни модели"
        )
