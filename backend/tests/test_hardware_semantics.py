"""Проверки причинного смысла параметров без игровых эталонов в продукте."""
import pytest
from pydantic import ValidationError
from sqlalchemy import select

from app.models.entities import Conflict, GameFunction, HardwareGPU, Method
from app.schemas.catalog import ProjectProfile
from app.seed.seeder import sync_function_taxonomy
from app.seed.corrections import correct_shadow_relation
from app.services.recommender import aggregate_load
from app.services.rules import assess_selected_methods
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


def test_physics_tick_scales_only_physics_contribution():
    profile = ProjectProfile(functions=["physics_simulation"], physics_tick_hz=60)
    base = _load_indices(profile, [])
    changed = _load_indices(profile.model_copy(update={"physics_tick_hz": 120}), [])
    assert base["cpu_index"] < changed["cpu_index"] < 2 * base["cpu_index"]


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
        [small, enough], 0.4, required_rt=False, vram_limit_gb=None, vram_gb=6,
    )
    assert selected is enough
    selected, _ = _pick_gpu(
        [small], 0.4, required_rt=False, vram_limit_gb=None, vram_gb=6,
    )
    assert selected is None


def test_alternatives_meet_estimated_load_and_memory(db):
    result = estimate_hardware(db, ProjectProfile(), [])
    for gpu in result.alternative_gpus:
        assert gpu.raster_score >= result.required_gpu_index
        assert gpu.vram_gb >= result.estimated_vram_gb
    for cpu in result.alternative_cpus:
        assert cpu.multi_thread_score >= result.required_cpu_index


def test_dlss_requires_declared_support_in_reference_and_alternatives(db):
    profile = ProjectProfile(world_type="linear", scale="small", target_quality="low",
                             target_fps=30, upscaling_method="dlss")
    result = estimate_hardware(db, profile, [])
    assert "DLSS" in result.required_hw_features
    assert result.reference_gpu is not None
    for gpu in [result.reference_gpu, *result.alternative_gpus]:
        assert any(item.lower().startswith("dlss") for item in gpu.hw_features)


def test_missing_api_support_does_not_return_incompatible_reference(db):
    result = estimate_hardware(db, ProjectProfile(render_api="metal"), [])
    assert result.reference_gpu is None
    assert result.alternative_gpus == []
    assert result.exceeds_catalog
    assert result.unmet_limits


@pytest.mark.parametrize("fps", [30, 60, 120])
def test_frame_generation_does_not_invent_base_fps(fps):
    profile = ProjectProfile(target_fps=fps)
    base = _load_indices(profile, [])
    enabled = _load_indices(profile.model_copy(update={"frame_generation": True}), [])
    assert enabled["gpu_index"] == base["gpu_index"]
    assert any("базовый FPS" in gap for gap in enabled["modeling_gaps"])


def test_explicit_base_fps_has_no_extra_gpu_discount():
    baseline = _load_indices(ProjectProfile(target_fps=60), [])
    generated = _load_indices(ProjectProfile(target_fps=120, frame_generation=True, base_render_fps=60), [])
    assert generated["gpu_index"] == baseline["gpu_index"]
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
                        conflict_type="conflict", description="Альтернативные реализации")
    profile = ProjectProfile(functions=["open_world_streaming"])
    accepted, notes = assess_selected_methods(methods, profile, [relation])
    assert accepted == []
    assert any("конфликт" in note for note in notes)
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
    assert row.conflict_type == "synergy"
    row.conflict_type = "conflict"
    row.severity = 1
    row.description = "Два механизма теней для направленного света дублируют стоимость и дают непредсказуемое наложение результатов."
    row.resolution = "Ручное уточнение" if admin_edited else "Выбрать одну систему теней как основную."
    row.source_url = "https://en.wikipedia.org/wiki/Shadow_mapping"
    db.flush()
    assert correct_shadow_relation(db) == (0 if admin_edited else 1)
    assert row.conflict_type == ("conflict" if admin_edited else "synergy")
    assert correct_shadow_relation(db) == 0
