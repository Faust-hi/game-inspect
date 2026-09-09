"""Research only: all fields/methods/relations on actual ORM data in memory."""
from __future__ import annotations
import dataclasses
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "backend"))
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from app.database import Base
from app.models.entities import Method, GameFunction, Conflict
from app.schemas.catalog import ProjectProfile
from app.seed.seeder import seed_all
from app.services import hardware, rules

OUT = ROOT / "validation/research/simplified-2026-09-09"

def dump(name, value):
    with (OUT / name).open("x", encoding="utf-8") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2,
                  default=lambda o: o.model_dump() if hasattr(o, "model_dump") else str(o), allow_nan=False)

def frame(profile, methods, relations):
    counted, notes = rules.assess_selected_methods(methods, profile, relations)
    model = hardware.build_model(profile, counted, relations)
    return {"counted": [m.code for m in counted], "notes": notes,
            "model": dataclasses.asdict(model)}

def quantities(record):
    model = record["model"]
    return {k: v for k, v in model.items() if k in
            {"cpu", "gpu", "memory", "cpu_sequential_ms", "cpu_parallel_ms",
             "gpu_raster_ms", "gpu_rt_ms", "budget_ms", "render_fps", "content"}}

def difference(a, b):
    return [key for key in a if a[key] != b.get(key)]

def compatible_profile(base, methods):
    values = base.model_dump()
    for field, attr in (("format", "applicable_formats"), ("world_type", "applicable_world_types"),
                        ("engine", "applicable_engines")):
        restrictions = [set(getattr(m, attr)) for m in methods if getattr(m, attr)]
        if restrictions:
            allowed = set.intersection(*restrictions)
            if not allowed:
                return None
            if values[field] not in allowed:
                values[field] = sorted(allowed)[0]
    allowed_platforms = {"pc_windows", "pc_linux"}
    for method in methods:
        if method.applicable_platforms:
            allowed_platforms &= set(method.applicable_platforms)
    if not allowed_platforms:
        return None
    values["platforms"] = ["pc_windows" if "pc_windows" in allowed_platforms else "pc_linux"]
    return ProjectProfile.model_validate(values)

def main():
    OUT.mkdir(exist_ok=False)
    old = json.loads((ROOT / "validation/research/run-2026-09-08-02/baseline.json").read_text(encoding="utf-8"))
    protected_before = {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in old["sha256"]}
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    with Session(engine) as db:
        seed_all(db, validate=False)
        db.flush()
        methods = list(db.scalars(select(Method).order_by(Method.code)))
        functions = list(db.scalars(select(GameFunction).order_by(GameFunction.code)))
        relations = list(db.scalars(select(Conflict).order_by(Conflict.id)))
        by_code = {m.code: m for m in methods}
        base = ProjectProfile(functions=[f.code for f in functions], stage="preproduction",
                              multiplayer=True, player_count=16, complexity_tolerance=5,
                              physics_tick_hz=60, object_count=5000, npc_count=100)
        reference = frame(base, [], relations)
        schema = ProjectProfile.model_json_schema()
        samples = {
            "name": ["Другое название"], "platforms": [["pc_windows"], ["pc_linux"], ["pc_windows", "pc_linux"]],
            "engine": ["unreal", "unity", "godot", "source"], "engine_version": [None, "4.27", "5.5"],
            "functions": [[], ["physics_simulation"], ["multiplayer_netcode"], base.functions],
            "object_count": [None, 0, 1, 499, 500, 501, 5000, 1000000],
            "npc_count": [None, 0, 1, 4, 5, 6, 100, 10000], "player_count": [1, 16, 128],
            "multiplayer": [False, True], "local_view_count": [None, 1, 2, 4],
            "target_fps": [30, 60, 120], "frame_generation": [False, True],
            "base_render_fps": [None, 30, 60], "streaming_pool_gb": [None, 1, 8],
            "draw_call_budget": [None, 100, 10000], "simulation_radius_m": [None, 0, 100, 10000],
            "physics_tick_hz": [None, 30, 60, 120], "ram_limit_gb": [None, 4, 64],
            "vram_limit_gb": [None, 2, 32], "size_limit_gb": [None, 1, 100],
            "deadline_weeks": [None, 0, 1, 52], "complexity_tolerance": [None, 1, 5],
        }
        field_cases = []
        for name, spec in schema["properties"].items():
            options = samples.get(name)
            if options is None:
                options = spec.get("enum")
                if options is None:
                    options = next((v["enum"] for v in spec.get("anyOf", []) if "enum" in v), None)
                assert options is not None, name
            cases = []
            for value in options:
                try:
                    profile = ProjectProfile.model_validate({**base.model_dump(), name: value})
                    result = frame(profile, [], relations)
                    cases.append({"input": value, "normalized": getattr(profile, name),
                                  "changed_quantities": difference(quantities(reference), quantities(result)), **result})
                except Exception as error:
                    cases.append({"input": value, "error": f"{type(error).__name__}: {error}"})
            field_cases.append({"field": name, "schema": spec, "cases": cases})
        dump("fields.json", {"scope": "single-field probes with empty basket; broad synthetic research profile, not a game benchmark",
                             "baseline_profile": base.model_dump(), "baseline": reference, "fields": field_cases})
        method_records = []
        for method in methods:
            profile = compatible_profile(base, [method])
            data = {c.name: getattr(method, c.name) for c in Method.__table__.columns}
            data["function_code_resolved_from_relationship"] = method.function.code if method.function else None
            data["implemented_effect"] = hardware.METHOD_SUBSYSTEM_EFFECTS.get(method.code)
            data["coefficient_status"] = "expert_not_independently_measured"
            if profile is None:
                data["probe"] = {"status": "no_pc_compatible_context"}
            else:
                before = frame(profile, [], relations)
                after = frame(profile, [method], relations)
                closure = {method.code}
                while True:
                    updated = closure | {r.b_code for r in relations if r.conflict_type == "dependency" and r.a_code in closure}
                    if updated == closure:
                        break
                    closure = updated
                basket = [by_code[c] for c in sorted(closure) if c in by_code]
                with_dependencies = frame(profile, basket, relations)
                data["probe"] = {"status": "executed", "profile": profile.model_dump(), "before": before,
                                 "single": after, "with_dependencies": with_dependencies,
                                 "changed_quantities": difference(quantities(before), quantities(after))}
            method_records.append(data)
        dump("methods.json", method_records)
        pairs = []
        for relation in relations:
            pair = [by_code[relation.a_code], by_code[relation.b_code]]
            profile = compatible_profile(base, pair)
            record = {c.name: getattr(relation, c.name) for c in Conflict.__table__.columns}
            if profile is not None:
                ab = frame(profile, pair, relations)
                ba = frame(profile, list(reversed(pair)), relations)
                record["probe"] = {"profile": profile.model_dump(), "a": frame(profile, pair[:1], relations),
                                   "b": frame(profile, pair[1:], relations), "ab": ab, "ba": ba,
                                   "order_invariant_quantities": quantities(ab) == quantities(ba)}
            else:
                record["probe"] = {"status": "no_common_pc_context"}
            pairs.append(record)
        dump("relations.json", pairs)
        selected = [by_code["hierarchical_lod"]]
        scenarios = {
            "windows": {"platforms": ["pc_windows"]}, "linux": {"platforms": ["pc_linux"]},
            "stage_prototype": {"stage": "prototype"}, "stage_production": {"stage": "production"},
            "priority_cost": {"priority": "cost"}, "priority_quality": {"priority": "quality"},
            "low_memory_limits": {"ram_limit_gb": 4, "vram_limit_gb": 2},
            "no_multiplayer": {"multiplayer": False}, "fps_120": {"target_fps": 120},
            "fg_120_base_60": {"target_fps": 120, "base_render_fps": 60, "frame_generation": True},
        }
        outputs = {"base": {"profile": base.model_dump(), "result": hardware.estimate_hardware(db, base, selected).model_dump()}}
        for name, patch in scenarios.items():
            profile = ProjectProfile.model_validate({**base.model_dump(), **patch})
            outputs[name] = {"profile": profile.model_dump(), "result": hardware.estimate_hardware(db, profile, selected).model_dump()}
        dump("hardware-scenarios.json", outputs)
        dump("functions.json", [{"code": f.code, "name": f.name,
                                 "cpu_targets": hardware.FEATURE_CPU_SUBSYSTEM_LOAD.get(f.code),
                                 "gpu_targets": hardware.FEATURE_GPU_SUBSYSTEM_LOAD.get(f.code),
                                 "methods": [m.code for m in methods if m.function_id == f.id]} for f in functions])
        rows = json.loads((ROOT / "validation/research/run-2026-09-08-02/external-rows.json").read_text(encoding="utf-8"))
        for row in rows:
            token = re.match(r"[a-z][a-z0-9_]*", row["code"])
            normalized = token.group() if token else row["code"]
            method = by_code.get(normalized)
            row["current_catalog_check"] = {"normalized_code": normalized,
                "exact_code_present": method is not None,
                "effect_mapping_present": normalized in hardware.METHOD_SUBSYSTEM_EFFECTS,
                "effect_mapping_nonempty": bool(hardware.METHOD_SUBSYSTEM_EFFECTS.get(normalized)),
                "semantic_equivalence": "requires_review_even_if_code_matches",
                "production_import": False}
        dump("batch-coverage.json", rows)
        unique_missing = sorted({r["current_catalog_check"]["normalized_code"] for r in rows if not r["current_catalog_check"]["exact_code_present"]})
        dump("missing-codes.json", unique_missing)
        summary = {"fields": len(field_cases), "field_probe_cases": sum(len(f["cases"]) for f in field_cases),
                   "field_probe_errors": sum("error" in c for f in field_cases for c in f["cases"]),
                   "methods": len(method_records), "method_probes_executed": sum(m["probe"]["status"] == "executed" for m in method_records),
                   "effect_mappings_missing": [m.code for m in methods if m.code not in hardware.METHOD_SUBSYSTEM_EFFECTS],
                   "effect_mappings_empty": [m.code for m in methods if hardware.METHOD_SUBSYSTEM_EFFECTS.get(m.code) == {}],
                   "relations": len(pairs), "relation_order_failures": [p["id"] for p in pairs if p["probe"].get("order_invariant_quantities") is False],
                   "batch_rows": len(rows), "batch_exact_match_rows": sum(r["current_catalog_check"]["exact_code_present"] for r in rows),
                   "batch_unique_codes": len({r["current_catalog_check"]["normalized_code"] for r in rows}),
                   "batch_unique_missing": len(unique_missing)}
        dump("summary.json", summary)
    engine.dispose()
    changed = [name for name, sha in protected_before.items() if hashlib.sha256((ROOT / name).read_bytes()).hexdigest() != sha]
    dump("preservation.json", {"protected": len(protected_before), "changed": changed, "live_database_opened": False})
    assert not changed
    print(json.dumps(summary, ensure_ascii=False))

if __name__ == "__main__":
    main()
