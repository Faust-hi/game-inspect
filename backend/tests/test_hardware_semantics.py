"""Проверки причинного смысла параметров без игровых эталонов в продукте."""
import pytest
from pydantic import ValidationError
from sqlalchemy import select

from app.models.entities import Conflict, GameFunction, HardwareGPU, Method
from app.schemas.catalog import ProjectProfile
from app.seed import seeder
from app.seed.functions_data import GAME_FUNCTIONS
from app.seed.seeder import sync_function_taxonomy
from app.seed.corrections import correct_shadow_relation
from app.services.recommender import _qualitative_level, aggregate_load
from app.services.rules import assess_selected_methods
from app.services import hardware
from app.services.hardware import _load_indices, _pick_gpu, estimate_hardware


def test_target_fps_distinguishes_supported_extremes():
    profile = ProjectProfile()
    estimates = [
        _load_indices(profile.model_copy(update={"target_fps": fps}), [])
        for fps in (15, 30, 60, 144, 240, 480)
    ]
    for low, high in zip(estimates, estimates[1:]):
        assert low["gpu_index"] < high["gpu_index"]
        assert low["cpu_index"] < high["cpu_index"]


def test_physics_tick_does_not_scale_unrelated_work():
    profile = ProjectProfile(functions=["baked_lighting"])
    base = _load_indices(profile, [])
    changed = _load_indices(profile.model_copy(update={"physics_tick_hz": 120}), [])
    assert changed["cpu_index"] == base["cpu_index"]


def test_fractional_physics_tick_is_accepted_by_public_calculation(client):
    response = client.post("/api/recommend", json={
        "profile": {"physics_tick_hz": 66.6, "functions": ["physics_simulation"]},
        "basket": ["fixed_timestep_physics"],
    })
    assert response.status_code == 200
    assert response.json()["profile"]["physics_tick_hz"] == 66.6


def test_unknown_scene_dimensions_are_explicitly_reported(client):
    response = client.post("/api/hardware-estimate", json={
        "profile": {
            "scale": "unknown",
            "object_count_level": "unknown",
            "npc_count_level": "unknown",
        },
        "basket": [],
    })

    assert response.status_code == 200
    gaps = " ".join(response.json()["modeling_gaps"])
    assert "масштаб мира" in gaps
    assert "количество объектов" in gaps
    assert "количество NPC" in gaps


def test_seed_hardware_tolerates_unknown_optional_values(db, monkeypatch):
    """NULL из внешнего hardware-источника не ломает повторный seed."""
    monkeypatch.setattr(
        seeder,
        "_load_json",
        lambda _name: {
            "cpu": [],
            "gpu": [{
                "model": "Calibration GPU with unknown bandwidth",
                "memory_bandwidth_gbs": None,
                "vram_gb": None,
            }],
        },
    )

    assert seeder.seed_hardware(db, seeder.SeedOutcome()) == 1
    row = db.scalar(select(HardwareGPU).where(
        HardwareGPU.model == "Calibration GPU with unknown bandwidth"
    ))
    assert row is not None
    assert row.memory_bandwidth_gbs == 0.0
    assert row.vram_gb == 0.0


def test_physics_tick_scales_only_physics_contribution():
    """Удвоение частоты такта физики удваивает только подсистему physics."""
    profile = ProjectProfile(functions=["physics_simulation"], physics_tick_hz=60)
    base = _load_indices(profile, [])
    changed = _load_indices(profile.model_copy(update={"physics_tick_hz": 120}), [])
    assert changed["cpu_subsystem_load"]["physics"] == pytest.approx(
        2 * base["cpu_subsystem_load"]["physics"]
    )
    # Последовательные подсистемы не затронуты.
    for key in ("main_thread", "render_prep"):
        assert changed["cpu_subsystem_load"].get(key, 0.0) == pytest.approx(
            base["cpu_subsystem_load"].get(key, 0.0)
        )


def test_larger_budget_does_not_make_same_scene_cheaper():
    profile = ProjectProfile(draw_call_budget=100)
    base = _load_indices(profile, [])
    changed = _load_indices(profile.model_copy(update={"draw_call_budget": 1_000_000}), [])
    assert changed["cpu_index"] == base["cpu_index"]
    assert changed["estimated_draw_calls"] == base["estimated_draw_calls"]


def test_startup_sync_preserves_admin_function_assignment(db):
    method = db.scalar(select(Method).where(Method.code == "ml_frame_generation"))
    function = db.scalar(select(GameFunction).where(GameFunction.code == "baked_lighting"))
    method.function_id = function.id
    db.flush()
    sync_function_taxonomy(db)
    assert method.function_id == function.id


def test_startup_sync_fills_missing_assignment(db):
    method = db.scalar(select(Method).where(Method.code == "ml_frame_generation"))
    method.function_id = None
    db.flush()
    sync_function_taxonomy(db)
    assert method.function_id is not None
    assert sync_function_taxonomy(db)["methods_linked"] == 0


def test_gpu_requires_enough_vram_without_user_limit():
    small = HardwareGPU(model="Small", perf_class=1, raster_score=0.5, vram_gb=2)
    enough = HardwareGPU(model="Enough", perf_class=2, raster_score=0.6, vram_gb=8)
    selected, _ = _pick_gpu(
        [small, enough], raster_index=0.4, rt_index=0.0, required_rt=False, vram_gb=6,
    )
    assert selected is enough
    selected, _ = _pick_gpu(
        [small], raster_index=0.4, rt_index=0.0, required_rt=False, vram_gb=6,
    )
    assert selected is None


def test_alternatives_meet_estimated_load_and_memory(db):
    result = estimate_hardware(db, ProjectProfile(), [])
    indices = _load_indices(ProjectProfile(), [])
    for gpu in result.alternative_gpus:
        assert gpu.raster_score >= result.required_gpu_index
        assert gpu.vram_gb >= result.estimated_vram_gb
    for cpu in result.alternative_cpus:
        assert cpu.single_thread_score >= indices["cpu_st_index"]
        assert cpu.multi_thread_score >= indices["cpu_mt_index"]


def test_dlss_requires_declared_support_in_reference_and_alternatives(db):
    profile = ProjectProfile(world_type="linear", scale="small", target_quality="low",
                             target_fps=30, upscaling_method="dlss")
    result = estimate_hardware(db, profile, [])
    assert "DLSS" in result.required_hw_features
    assert result.reference_gpu is not None
    for gpu in [result.reference_gpu, *result.alternative_gpus]:
        assert any(item.lower().startswith("dlss") for item in gpu.hw_features)


def test_linux_with_directx_has_no_native_path(db):
    """Linux + DirectX 12: цель без нативного пути не получает оборудования."""
    result = estimate_hardware(
        db, ProjectProfile(platforms=["pc_linux"], render_api="dx12"), []
    )
    assert result.reference_gpu is None
    assert result.reference_cpu is None
    assert result.alternative_gpus == []
    assert result.exceeds_catalog
    assert any("DirectX 12" in item and "Linux" in item for item in result.unmet_limits)
    # Численный результат сохраняется, но без привязки к API.
    assert result.required_gpu_index > 0
    target = next(t for t in result.targets if t.platform == "pc_linux")
    assert target.compatible is False
    assert target.api_source == "explicit"


def test_two_pc_targets_are_reported_separately(db):
    """Windows и Linux считаются отдельно и обе показаны в результате."""
    result = estimate_hardware(
        db, ProjectProfile(platforms=["pc_windows", "pc_linux"]), []
    )
    platforms = {t.platform for t in result.targets}
    assert platforms == {"pc_windows", "pc_linux"}
    windows = next(t for t in result.targets if t.platform == "pc_windows")
    linux = next(t for t in result.targets if t.platform == "pc_linux")
    assert windows.render_api == "dx12" and windows.api_source == "auto"
    assert linux.render_api == "vulkan" and linux.api_source == "auto"
    # Общий ориентир не ниже результата каждой цели.
    assert result.required_cpu_index >= max(windows.cpu_index, linux.cpu_index) - 1e-9
    assert result.required_gpu_index >= max(windows.gpu_index, linux.gpu_index) - 1e-9


@pytest.mark.parametrize("fps", [30, 60, 120])
def test_frame_generation_does_not_invent_base_fps(fps):
    profile = ProjectProfile(target_fps=fps)
    base = _load_indices(profile, [])
    enabled = _load_indices(profile.model_copy(update={"frame_generation": True}), [])
    assert enabled["gpu_index"] == base["gpu_index"]
    assert any("базовый FPS" in gap for gap in enabled["modeling_gaps"])


def test_explicit_base_fps_has_no_extra_gpu_discount():
    """Базовый 60 FPS + генерация до 120: рендер не снижается, генерация отдельна."""
    baseline = _load_indices(ProjectProfile(target_fps=60), [])
    generated = _load_indices(
        ProjectProfile(target_fps=120, frame_generation=True, base_render_fps=60), []
    )
    # Отрисованных кадров по-прежнему 60: стоимость рендеринга не изменилась.
    for key in ("geometry", "shading", "lighting_shadows", "transparency", "raster"):
        assert generated["gpu_subsystem_load"][key] == pytest.approx(
            baseline["gpu_subsystem_load"][key]
        )
    # Генерация учтена отдельной стоимостью, а не как скидка.
    assert generated["gpu_subsystem_load"]["frame_generation"] > 0
    assert generated["gpu_index"] > baseline["gpu_index"]
    assert any("стоимость генератора" in gap for gap in generated["modeling_gaps"])


def test_generated_fps_cannot_be_lower_than_base():
    with pytest.raises(ValidationError):
        ProjectProfile(target_fps=60, frame_generation=True, base_render_fps=120)


def test_storage_and_draw_call_estimates_are_risks_not_proven_failures(db):
    result = estimate_hardware(db, ProjectProfile(storage_type="sata_ssd", draw_call_budget=100), [])
    assert not any("Накопитель" in item or "draw calls" in item for item in result.unmet_limits)
    assert any("задержки подкачки" in item for item in result.caveats)
    assert any("риск превышения" in item for item in result.caveats)


def test_inapplicable_basket_does_not_reduce_hardware_or_load(db):
    method = db.scalar(select(Method).where(Method.code == "world_partition_streaming"))
    method.applicable_formats = ["3D"]
    method.impact_cpu = -3
    profile = ProjectProfile(format="2D")
    baseline = estimate_hardware(db, profile, [])
    selected = estimate_hardware(db, profile, [method])
    assert selected.required_cpu_index == baseline.required_cpu_index
    assert selected.required_gpu_index == baseline.required_gpu_index
    assert any("эффект не учтён" in note for note in selected.caveats)
    load = aggregate_load([method], profile)
    assert load.cpu == 50
    assert any("эффект не учтён" in note for note in load.notes)


def test_selected_method_respects_min_scale_in_hardware_estimate(db):
    """Аппаратная оценка не должна учитывать метод, исключённый масштабом."""
    method = db.scalar(select(Method).where(Method.code == "world_partition_streaming"))
    profile = ProjectProfile(world_type="open_world", scale="small")
    baseline = estimate_hardware(db, profile, [])
    selected = estimate_hardware(db, profile, [method])

    assert selected.required_cpu_index == baseline.required_cpu_index
    assert selected.required_gpu_index == baseline.required_gpu_index
    assert any("масштабе мира" in note for note in selected.caveats)


def test_memory_is_not_bottleneck_without_deficit(db):
    """Память не ограничивает кадр, пока рабочий набор укладывается в объём.

    Раньше `memory_pressure` считался как гигабайты, делённые на норматив, и
    сравнивался с долями бюджета кадра: величина порядка единицы всегда
    выигрывала у величины порядка 0.1, и узким местом объявлялась память у
    57 игр из 58. В сравнении участвует только дефицит.
    """
    profile = ProjectProfile(
        scale="medium", target_resolution="1080p", target_quality="high",
        functions=["character_animation", "ai_pathfinding"],
        vram_limit_gb=16, ram_limit_gb=32,
    )
    result = estimate_hardware(db, profile, [])
    assert result.estimated_vram_gb < 16 * hardware.MEMORY_PRESSURE_FREE_SHARE
    assert result.bottleneck != "memory"
    assert not any("простой подкачки" in item for item in result.caveats)


def test_memory_deficit_becomes_bottleneck(db):
    """Заданный предел памяти, который не выполняется, делает память узким местом."""
    profile = ProjectProfile(
        scale="very_large", object_count_level="high", npc_count_level="high",
        functions=["open_world_streaming", "large_scale_terrain", "procedural_vegetation"],
        vram_limit_gb=4,
    )
    result = estimate_hardware(db, profile, [])
    assert result.estimated_vram_gb > profile.vram_limit_gb
    assert result.bottleneck == "memory"
    assert any("простой подкачки" in item for item in result.caveats)


def test_bottleneck_distinguishes_contrasting_projects(db):
    """Узкое место — диагностика: на контрастных проектах оно различается."""
    variants = {
        "обычный проект 1080p": ProjectProfile(
            scale="medium", target_resolution="1080p", target_quality="high",
            functions=["character_animation", "ai_pathfinding"],
        ),
        "4K и ультра": ProjectProfile(
            scale="very_large", object_count_level="high",
            target_resolution="2160p", target_quality="ultra",
            functions=["open_world_streaming", "dynamic_shadows", "volumetric_effects"],
        ),
        "дефицит видеопамяти": ProjectProfile(
            scale="very_large", object_count_level="high", npc_count_level="high",
            functions=["open_world_streaming", "large_scale_terrain", "procedural_vegetation"],
            vram_limit_gb=4,
        ),
    }
    found = {name: estimate_hardware(db, profile, []).bottleneck
             for name, profile in variants.items()}
    assert len(set(found.values())) == len(found), found
    assert found["4K и ультра"] == "gpu_raster"
    assert found["дефицит видеопамяти"] == "memory"


def test_memory_totals_match_components_in_both_calculation_paths(db):
    """Итог равен составу; резерв ОС не начисляется повторно поверх VRAM."""
    for profile in (
        ProjectProfile(),
        ProjectProfile(scale="very_large", object_count_level="high",
                       npc_count_level="high", target_resolution="2160p",
                       target_quality="ultra"),
        ProjectProfile(scale="small", target_resolution="720p", target_quality="low"),
    ):
        result = estimate_hardware(db, profile, [])
        model = hardware.build_model(profile, [])
        indices = _load_indices(profile, [])
        expected_ram = round(sum(size["ram"] for size in model.memory.values()), 1)
        expected_vram = round(sum(size["vram"] for size in model.memory.values()), 1)
        assert result.estimated_ram_gb == indices["ram_gb"] == expected_ram
        assert result.estimated_vram_gb == indices["vram_gb"] == expected_vram


@pytest.mark.parametrize("ram,vram", [(5.0, 12.0), (2.0, 0.5)])
def test_independent_memory_working_sets_have_no_extra_floor(db, monkeypatch, ram, vram):
    """Заданный состав ресурсов не подменяется общим нижним пределом.

    Синтетический состав проверяет арифметику, а не требования конкретной игры.
    """
    profile = ProjectProfile()
    model = hardware.build_model(profile, [])
    for sizes in model.memory.values():
        sizes.update(ram=0.0, vram=0.0)
    model.memory["system"]["ram"] = ram
    model.memory["render_targets"]["vram"] = vram
    monkeypatch.setattr(hardware, "build_model", lambda *args, **kwargs: model)

    result = estimate_hardware(db, profile, [])
    assert result.estimated_ram_gb == ram
    assert result.estimated_vram_gb == vram
    assert _load_indices(profile, [])["ram_gb"] == ram
    assert _load_indices(profile, [])["vram_gb"] == vram


def test_unknown_gpu_memory_has_an_explicit_catalog_limitation(db):
    result = estimate_hardware(db, ProjectProfile(), [])
    assert any("бюджет общей памяти" in note for note in result.caveats)


def test_memory_composition_sums_match_estimates(db):
    """Состав памяти, показанный пользователю, сходится с итоговой оценкой."""
    result = estimate_hardware(db, ProjectProfile(scale="very_large", object_count_level="high"), [])
    assert result.memory_composition
    assert sum(item.ram_gb for item in result.memory_composition) == pytest.approx(
        result.estimated_ram_gb, abs=0.15
    )
    assert sum(item.vram_gb for item in result.memory_composition) == pytest.approx(
        result.estimated_vram_gb, abs=0.15
    )


def test_local_views_scale_frame_work_not_full_buffers(db):
    """Число локальных видов меняет кадровую работу, а не только память.

    Раньше 1→4 вида не меняли CPU/GPU вообще, а память целевых буферов
    умножалась на число камер, как если бы каждый вид занимал весь экран.
    Правильная модель другая: подготовка рендера и геометрия повторяются для
    каждого вида, пиксельные стадии не умножаются (итоговое разрешение
    относится ко всему экрану), а буферы в сумме равны одному полноэкранному
    набору плюс неразделяемые вспомогательные.
    """
    base = ProjectProfile(functions=["split_screen_rendering"])
    rows = []
    for views in (1, 2, 4):
        result = _load_indices(base.model_copy(update={"local_view_count": views}), [])
        rows.append(result)
    one, two, four = rows

    # Кадровая работа растёт с числом видов.
    assert one["cpu_index"] < two["cpu_index"] < four["cpu_index"]
    assert one["gpu_index"] < two["gpu_index"] < four["gpu_index"]
    # Память растёт, но не в число видов: буферы не умножаются как полноэкранные.
    assert one["vram_gb"] < four["vram_gb"]
    assert four["vram_gb"] / one["vram_gb"] < 4.0
    # Ресурсы сцены разделяются: RAM от числа видов не зависит.
    assert one["ram_gb"] == four["ram_gb"]


def test_local_view_count_without_function_still_counts(db):
    """Явно заданное число видов учитывается и без выбранной функции split-screen."""
    single = _load_indices(ProjectProfile(local_view_count=1), [])
    four = _load_indices(ProjectProfile(local_view_count=4), [])
    assert four["cpu_index"] > single["cpu_index"]
    assert four["gpu_index"] > single["gpu_index"]


def test_ram_estimate_reacts_to_scale(db):
    """Коридор оценки памяти обязан повторять разницу масштаба проектов.

    Раньше весь коридор укладывался в ×1.6 на выборке от Portal 2007 до
    Alan Wake 2: постоянная часть (система, движок, аудио) составляла больше
    половины оценки и съедала различия проектов.
    """
    small = estimate_hardware(
        db, ProjectProfile(format="2D", scale="small", object_count_level="low",
                           npc_count_level="low", target_resolution="720p",
                           target_quality="low"), []
    )
    large = estimate_hardware(
        db, ProjectProfile(scale="very_large", object_count_level="high",
                           npc_count_level="high", target_resolution="2160p",
                           target_quality="ultra"), []
    )
    # Коридор проверяется по ресурсам самого проекта: резерв ОС и фона добавлен
    # как явная постоянная величина и не должен ни сжимать, ни раздувать
    # чувствительность модели к масштабу проекта.
    reserve_components = {
        hardware.MEMORY_COMPONENT_LABELS["system"],
        hardware.MEMORY_COMPONENT_LABELS["background"],
    }

    def project_ram(result) -> float:
        return sum(
            item.ram_gb for item in result.memory_composition
            if item.label not in reserve_components
        )

    assert project_ram(large) / project_ram(small) >= 2.0
    # Полная потребность системы включает резерв один раз и не обнуляется.
    # Допуск учитывает округление показа: итог округляется до 0.1 ГБ, а каждый
    # компонент — до 0.01 ГБ, поэтому сумма компонентов может отличаться от
    # итога на долю округления, помноженную на число компонентов.
    tolerance = 0.05 + 0.01 * len(large.memory_composition)
    assert large.estimated_ram_gb - project_ram(large) == pytest.approx(
        hardware.OS_RAM_RESERVE_GB + hardware.BACKGROUND_RAM_RESERVE_GB, abs=tolerance
    )


def test_every_catalog_function_has_a_measurable_model_effect(db):
    """Ни одна функция каталога не должна молча не влиять на модель.

    Функция без вклада в подсистемы — это флажок, который пользователь
    отмечает, а расчёт не замечает. Проверка ловит именно такие записи.
    """
    # Функции производства: их эффект лежит вне кадра (размер сборки, время
    # сборки, процесс), поэтому статью бюджета они не меняют.
    no_frame_cost = {"art_pipeline", "build_delivery", "runtime_security"}
    # Unknown SDK overhead is visible, rather than made up to change a number.
    security = ProjectProfile(functions=['runtime_security'])
    assert any('не измерены' in gap for gap in hardware._modeling_gaps(security, set(), 'sata_ssd'))
    base = ProjectProfile(scale="large", object_count_level="high")
    for code in {fn["code"] for fn in GAME_FUNCTIONS} - no_frame_cost:
        without = hardware.build_model(base, [], None)
        with_fn = hardware.build_model(
            base.model_copy(update={"functions": [code]}), [], None
        )
        assert (without.cpu != with_fn.cpu) or (without.gpu != with_fn.gpu) or (
            without.memory != with_fn.memory
        ), f"Функция {code} не влияет ни на одну подсистему"


def test_ray_tracing_functions_are_visible_in_the_model(db):
    """Трассировка пути и выборочные RT-эффекты — разные статьи бюджета."""
    plain = hardware.build_model(ProjectProfile(), [], None)
    assert plain.gpu["rt"] == 0.0

    effects = hardware.build_model(
        ProjectProfile(functions=["ray_traced_effects"]), [], None
    )
    full = hardware.build_model(
        ProjectProfile(functions=["path_tracing"]), [], None
    )
    assert 0.0 < effects.gpu["rt"] < full.gpu["rt"]


def test_path_tracing_defines_the_ray_tracing_bottleneck(db):
    """Проект с трассировкой пути упирается в RT, а не в главный поток."""
    profile = ProjectProfile(
        scale="large", object_count_level="high",
        target_resolution="1440p", target_quality="high",
        functions=["character_animation", "ai_pathfinding", "path_tracing"],
    )
    assert estimate_hardware(db, profile, []).bottleneck == "gpu_rt"


def test_gameplay_and_simulation_functions_load_their_own_subsystems(db):
    """Геймплейные подсистемы нагружают свои статьи, а не размываются в общий множитель."""
    cases = {
        "advanced_npc_ai": ("cpu", "ai"),
        "vehicle_simulation": ("cpu", "physics"),
        "gameplay_ability_system": ("cpu", "main_thread"),
        "procedural_terrain": ("cpu", "streaming"),
        "mesh_shaders": ("gpu", "geometry"),
        "dynamic_lighting": ("gpu", "lighting_shadows"),
    }
    plain = hardware.build_model(ProjectProfile(), [], None)
    for code, (scope, subsystem) in cases.items():
        with_fn = hardware.build_model(ProjectProfile(functions=[code]), [], None)
        costs = with_fn.cpu if scope == "cpu" else with_fn.gpu
        assert costs[subsystem] > (plain.cpu if scope == "cpu" else plain.gpu)[subsystem], code


def test_selected_method_conditions_are_visible_in_both_estimates(db):
    method = db.scalar(select(Method).where(Method.code == "world_partition_streaming"))
    method.requires_conditions = ["Проверить скорость подкачки при быстром перемещении"]
    profile = ProjectProfile()
    assert any(method.requires_conditions[0] in note for note in estimate_hardware(db, profile, [method]).caveats)
    assert any(method.requires_conditions[0] in note for note in aggregate_load([method], profile).notes)


def test_conflicting_methods_do_not_stack_effects(db):
    methods = list(db.scalars(select(Method).where(Method.code.in_([
        "world_partition_streaming", "hierarchical_lod",
    ]))))
    relation = Conflict(a_code=methods[0].code, b_code=methods[1].code,
                        conflict_type="hard_conflict", description="Альтернативные реализации")
    profile = ProjectProfile(functions=["open_world_streaming"])
    accepted, notes = assess_selected_methods(methods, profile, [relation])
    assert accepted == []
    assert any("жёсткая несовместимость" in note for note in notes)
    load = aggregate_load(methods, profile, relations=[relation])
    assert load.cpu == load.gpu == 50


def test_unmet_dependencies_propagate_independently_of_order(db):
    codes = ["world_partition_streaming", "hierarchical_lod", "async_loading_pipeline"]
    methods = list(db.scalars(select(Method).where(Method.code.in_(codes))))
    relations = [
        Conflict(a_code=codes[0], b_code=codes[1], conflict_type="dependency"),
        Conflict(a_code=codes[1], b_code=codes[2], conflict_type="dependency"),
        Conflict(a_code=codes[2], b_code="missing_requirement", conflict_type="dependency"),
    ]
    profile = ProjectProfile(functions=["open_world_streaming"])
    for ordered in (relations, list(reversed(relations))):
        accepted, notes = assess_selected_methods(methods, profile, ordered)
        assert accepted == []
        assert sum("обязательная зависимость" in note for note in notes) == 3


@pytest.mark.parametrize("admin_edited", [False, True])
def test_shadow_relation_correction_preserves_manual_changes(db, admin_edited):
    row = db.scalar(select(Conflict).where(
        Conflict.a_code == "cascaded_shadow_maps", Conflict.b_code == "distance_field_shadows",
    ))
    assert row.conflict_type == "complement"
    row.conflict_type = "hard_conflict"
    row.severity = 1
    row.description = "Два механизма теней для направленного света дублируют стоимость и дают непредсказуемое наложение результатов."
    row.resolution = "Ручное уточнение" if admin_edited else "Выбрать одну систему теней как основную."
    row.source_url = "https://en.wikipedia.org/wiki/Shadow_mapping"
    db.flush()
    assert correct_shadow_relation(db) == (0 if admin_edited else 1)
    assert row.conflict_type == ("hard_conflict" if admin_edited else "complement")
    assert correct_shadow_relation(db) == 0


# ---------------------------------------------------------------------------
# Качественные ресурсы в сводке нагрузки
# ---------------------------------------------------------------------------
QUALITATIVE_CASES = [
    ("disk", "lightmap_atlas_baking", "baked_lighting", 2, "повышает", {"world_type": "linear"}),
    ("network", "network_relevancy_priority", "multiplayer_netcode", -2, "снижает",
     {"multiplayer": True}),
]


@pytest.mark.parametrize("resource,code,function,score,direction,overrides", QUALITATIVE_CASES)
def test_disk_and_network_are_qualitative_not_percentages(
    db, resource, code, function, score, direction, overrides,
):
    """Накопитель и сеть не превращаются в проценты нагрузки.

    Раньше суммарный экспертный балл умножался на коэффициент и попадал на ту
    же шкалу 0..100, что и измеренная стоимость кадра: число выглядело
    результатом расчёта, хотя модель не считает ни объём данных, ни трафик и
    не может подтвердить его источниками.
    """
    method = db.scalar(select(Method).where(Method.code == code))
    profile = ProjectProfile(functions=[function], **overrides)

    load = aggregate_load([method], profile)
    detail = load.per_resource[resource]

    assert detail["quantitative"] is False
    assert detail["raw"] == pytest.approx(score)
    assert detail["direction"] == direction
    assert detail["level"] != "без значимого влияния"
    # Числовое поле остаётся нейтральным: шкалы у ресурса нет.
    assert detail["normalized"] == 50
    assert load.disk == load.network == 50
    assert "не оценивает" in detail["explanation"]
    # Измеренные ресурсы при этом остаются измеренными.
    for key in ("cpu", "gpu", "ram", "vram"):
        assert load.per_resource[key]["quantitative"] is True


@pytest.mark.parametrize("score,expected", [
    (0, "без значимого влияния"),
    (1, "небольшое"),
    (-2, "небольшое"),
    (3, "умеренное"),
    (-5, "умеренное"),
    (6, "существенное"),
    (-14, "существенное"),
])
def test_qualitative_level_follows_magnitude(score, expected):
    """Уровень влияния растёт с модулем суммарного балла, без единиц измерения."""
    assert _qualitative_level(score) == expected


def test_qualitative_resources_are_explained_only_when_affected(db):
    method = db.scalar(select(Method).where(Method.code == "network_relevancy_priority"))
    profile = ProjectProfile(functions=["multiplayer_netcode"], multiplayer=True)

    assert any("оценены качественно" in note for note in aggregate_load([method], profile).notes)
    assert not any("оценены качественно" in note for note in aggregate_load([], profile).notes)


def test_load_profile_endpoint_marks_qualitative_resources(client):
    response = client.post("/api/load-profile", json={
        "profile": {"functions": ["multiplayer_netcode"], "multiplayer": True},
        "basket": ["network_relevancy_priority"],
    })
    assert response.status_code == 200, response.text
    detail = response.json()["per_resource"]["network"]
    assert detail["quantitative"] is False
    assert detail["level"] == "небольшое"
    assert detail["normalized"] == 50
