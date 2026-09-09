"""Record research evidence without modifying existing files or opening the live DB.

Run: .venv/Scripts/python.exe -B validation/research/capture.py NEW_OUTPUT_DIRECTORY
All outputs use exclusive creation. Catalog reconstruction uses SQLite in memory.
Lexical inventories are discovery aids, explicitly not completed semantic reviews.
"""
from __future__ import annotations

import ast
import hashlib
import importlib.metadata
import importlib.util
import itertools
import json
import platform
import random
import re
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "backend"))


def write(directory, name, value):
    with (directory / name).open("x", encoding="utf-8") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2, default=str, allow_nan=False)


def source_files():
    roots = ["backend/app", "backend/tests", "backend/alembic", "frontend/src",
             "docs", "validation", "audit-2026-09-07"]
    files = {p for name in roots for p in (ROOT / name).rglob("*")
             if p.is_file() and p.suffix in {".py", ".ts", ".tsx", ".json", ".md", ".txt"}
             and "research" not in p.relative_to(ROOT).parts and "__pycache__" not in p.parts}
    files.update(ROOT.glob("партия-*.md"))
    for name in ["README.md", "DSS-анализ-железо.md", "backend/requirements.txt",
                 "backend/requirements.lock", "frontend/package.json", "frontend/package-lock.json"]:
        if (ROOT / name).is_file():
            files.add(ROOT / name)
    return sorted(files)


def hashes(files):
    return {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in files}


def main():
    output = Path(sys.argv[1]).resolve()
    output.relative_to((ROOT / "validation/research").resolve())
    output.mkdir(parents=True, exist_ok=False)
    files = source_files()
    before = hashes(files)
    baseline = {"timestamp_utc": datetime.now(timezone.utc).isoformat(),
                "head": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
                "git_status": subprocess.check_output(["git", "status", "--short"], cwd=ROOT, text=True),
                "python": sys.version, "platform": platform.platform(), "sha256": before,
                "backend_installed": {d.metadata["Name"]: d.version for d in importlib.metadata.distributions()},
                "scope": "source/fixtures/locks; excludes dependencies, secrets, generated files, research outputs",
                "live_db": "not opened; source seed reconstruction only"}
    frontend = {}
    manifest = json.loads((ROOT / "frontend/package.json").read_text(encoding="utf-8"))
    for name in manifest.get("dependencies", {}) | manifest.get("devDependencies", {}):
        package = ROOT / "frontend/node_modules" / name / "package.json"
        frontend[name] = json.loads(package.read_text(encoding="utf-8"))["version"] if package.is_file() else None
    baseline["frontend_installed"] = frontend
    write(output, "baseline.json", baseline)

    code = {p.relative_to(ROOT).as_posix(): p.read_text(encoding="utf-8-sig")
            for p in files if p.suffix in {".py", ".ts", ".tsx"}}
    symbols, constants = [], []
    for path, text in code.items():
        if not path.endswith(".py"):
            continue
        tree = ast.parse(text)
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                symbols.append({"path": path, "line": node.lineno, "name": node.name,
                                "kind": type(node).__name__, "purpose_from_docstring": ast.get_docstring(node),
                                "status": "indexed_not_semantically_certified"})
        for node in tree.body:
            if isinstance(node, (ast.Assign, ast.AnnAssign)):
                targets = node.targets if isinstance(node, ast.Assign) else [node.target]
                for target in targets:
                    if isinstance(target, ast.Name) and target.id.isupper():
                        constants.append({"path": path, "line": node.lineno, "name": target.id,
                                          "expression": ast.get_source_segment(text, node),
                                          "evidence": "implementation_only_not_empirical_validation"})
    write(output, "symbols.json", symbols)
    write(output, "constants.json", constants)

    from sqlalchemy import create_engine
    from sqlalchemy.orm import Session
    from app.database import Base
    from app.models import entities
    from app.schemas.catalog import ProjectProfile, _effective_count
    from app.seed.seeder import seed_all
    from app.services import hardware
    from app.services.topsis import Criterion, topsis

    write(output, "profile-schema.json", ProjectProfile.model_json_schema())
    fields = []
    for name, field in ProjectProfile.model_fields.items():
        occurrences = [{"path": path, "line": i, "text": line.strip()}
                       for path, text in code.items() for i, line in enumerate(text.splitlines(), 1)
                       if re.search(r"\b" + re.escape(name) + r"\b", line)]
        fields.append({"name": name, "schema": ProjectProfile.model_json_schema()["properties"][name],
                       "occurrences": occurrences, "evidence": "lexical_usage_not_dataflow_proof",
                       "semantic_review": "pending_unless_explicitly_discussed_in_report"})
    write(output, "profile-usage.json", fields)
    write(output, "orm-schema.json", {table.name: [{"name": c.name, "type": str(c.type),
          "nullable": c.nullable, "default": str(c.default.arg) if c.default is not None else None,
          "foreign_keys": [str(f.target_fullname) for f in c.foreign_keys]} for c in table.columns]
          for table in Base.metadata.sorted_tables})

    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        seeded = seed_all(session, validate=False)
        session.flush()
        tables = {table.name: [dict(row) for row in session.execute(table.select()).mappings()]
                  for table in Base.metadata.sorted_tables}
        write(output, "seed-catalog.json", {"seed_outcome": seeded, "tables": tables})
        methods = sorted(tables["methods"], key=lambda x: x["code"])
        relations = tables["conflicts"]
        pairs = []
        for a, b in itertools.combinations(methods, 2):
            edges = [r for r in relations if {r["a_code"], r["b_code"]} == {a["code"], b["code"]}]
            aeff = hardware.METHOD_SUBSYSTEM_EFFECTS.get(a["code"], {})
            beff = hardware.METHOD_SUBSYSTEM_EFFECTS.get(b["code"], {})
            shared = [f"{kind}:{key}" for kind in ("cpu", "gpu", "mem")
                      for key in (aeff.get(kind) or {}) if key in (beff.get(kind) or {})]
            pairs.append({"a": a["code"], "b": b["code"], "relations": edges,
                          "same_function": a["function_id"] == b["function_id"], "shared_effect_targets": shared,
                          "review_status": "requires_source_review" if edges else "unknown",
                          "quantitative_joint_effect": "not_established"})
        write(output, "method-pairs.json", pairs)
        write(output, "method-passports.json", [{"catalog": m,
              "implemented_effect": hardware.METHOD_SUBSYSTEM_EFFECTS.get(m["code"]),
              "conditions_structured": False, "mechanism_evidence": "catalog_assertion_pending_source_review",
              "quantitative_evidence": "no_measurement_attached_to_coefficient",
              "required_verification": "same scene/hardware/build/settings; baseline and modified; overhead and quality"}
              for m in methods])
        summary = {"tables": {k: len(v) for k, v in tables.items()}, "pairs": len(pairs),
                   "pairs_with_edges": sum(bool(p["relations"]) for p in pairs),
                   "pairs_shared_targets": sum(bool(p["shared_effect_targets"]) for p in pairs)}
    engine.dispose()

    cases = json.loads((ROOT / "validation/review-queue.json").read_text(encoding="utf-8"))
    write(output, "external-rows.json", [{**r, "current_review": {
          "status": "pending_individual_primary_source_review",
          "decision": "exclude_from_numerical_calibration_until_verified",
          "reason": "existing row-level source text is not a matched measurement of required CPU/GPU performance",
          "automatic_record_only": True}} for r in cases])
    issues = []
    for path in ["docs/registry.md", "audit-2026-09-07/REPORT.md", "audit-2026-09-07/comparison/CONFIRMED.md"]:
        for line_no, line in enumerate((ROOT / path).read_text(encoding="utf-8").splitlines(), 1):
            if re.search(r"\b(?:D\d{2}(?:\.\d)?|G\d{2}|N\d{2})\b", line):
                issues.append({"path": path, "line": line_no, "historical_text": line,
                               "status": "historical_claim_not_current_verification"})
    write(output, "historical-issues.json", issues)

    probes = {"kind": "deterministic_function_probes_not_game_performance_measurements"}
    probes["count_boundary"] = {field: [{"count": n, "effective": _effective_count(n, "medium", field)}
        for n in values] for field, values in {"object_count": [0, 1, 499, 500, 501, 1000000, 1000001],
                                               "npc_count": [0, 1, 4, 5, 6, 10000, 100000]}.items()}
    probes["unknown_extra"] = {"ai_tick_hz_retained": "ai_tick_hz" in ProjectProfile.model_validate({"ai_tick_hz": 120}).model_dump()}
    probes["engine_memory"] = {e: hardware._memory_components(ProjectProfile(engine=e), 0.0, set())
                               for e in ["unreal", "unity", "godot", "custom"]}
    probes["method_memory"] = []
    for codes in [["hierarchical_lod"], ["animation_compression"], ["hierarchical_lod", "animation_compression"],
                  ["virtual_shadow_maps"], ["static_shadow_caching"], ["virtual_shadow_maps", "static_shadow_caching"]]:
        memory = {"meshes": {"ram": 10., "vram": 10.}, "render_targets": {"ram": 10., "vram": 10.}}
        contributions, exclusions = hardware._apply_method_effects({}, {}, memory,
            [SimpleNamespace(code=c, name=c) for c in codes], [])
        probes["method_memory"].append({"codes": codes, "memory": memory,
             "contributions": [x.model_dump() for x in contributions], "exclusions": exclusions})
    probes["physical_memory"] = {"rgba8_1080p_bytes": 1920 * 1080 * 4,
        "rgba8_4k_bytes": 3840 * 2160 * 4,
        "rgba8_4096_full_mips_bytes": sum(max(1, 4096 >> i)**2 * 4 for i in range(13)),
        "bc1_4096_full_mips_bytes": sum(((max(1, 4096 >> i)+3)//4)**2 * 8 for i in range(13)),
        "assumption": "payload only; no alignment/driver/aliasing/residency; not a game's total memory"}
    rng = random.Random(20260908)
    criteria = [Criterion("benefit", "benefit", "benefit"), Criterion("cost", "cost", "cost")]
    for _ in range(20000):
        a, b = [[rng.randint(1, 100) for _ in range(2)] for __ in range(2)]
        c = [min(a[0], b[0]), max(a[1], b[1]) + rng.randint(1, 100)]
        old, new = topsis([a, b], criteria).scores, topsis([a, b, c], criteria).scores
        if (old[0] - old[1]) * (new[0] - new[1]) < 0:
            probes["rank_reversal"] = {"before": [a, b], "after": [a, b, c], "old": old, "new": new,
                                       "qualification": "synthetic dominated added option; does not prove current catalog reversal"}
            break
    write(output, "probes.json", probes)
    # Seed helpers retain mutable module data: run the second reconstruction in
    # a fresh process. A repeated in-process seed failed in research run 01.
    subprocess.run([sys.executable, "-B", str(ROOT / "validation/diagnose_memory.py"),
                    str(output / "profiles.json")], cwd=ROOT, check=True)
    fresh_profiles = json.loads((output / "profiles.json").read_text(encoding="utf-8"))
    summary.update(profile_fields=len(fields), symbols=len(symbols), constants=len(constants),
                   external_rows=len(cases), profiles=len(fresh_profiles["profiles"]))
    write(output, "summary.json", summary)
    after = hashes(files)
    changed = [p for p, digest in before.items() if after.get(p) != digest]
    write(output, "preservation.json", {"checked_files": len(before), "changed": changed,
          "scope": baseline["scope"], "live_database_opened": False})
    print(json.dumps({"summary": summary, "changed_existing_inputs": changed,
                      "probe_results": probes}, ensure_ascii=False, default=str))


if __name__ == "__main__":
    main()
