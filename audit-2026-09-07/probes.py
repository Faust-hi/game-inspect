"""Read-only audit probes: all database mutations target a disposable database.

Run from repository root with .venv/Scripts/python.exe audit-2026-09-07/probes.py.
Does not load the working database or change application sources.
"""
from __future__ import annotations

import collections
import hashlib
import json
import logging
import os
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
sys.dont_write_bytecode = True
temporary = tempfile.TemporaryDirectory(prefix="gameinspect_audit_")
os.environ["DATABASE_URL"] = "sqlite:///" + (Path(temporary.name) / "audit.db").as_posix()
os.environ["AUTO_SEED"] = "false"
os.environ["LOG_LEVEL"] = "CRITICAL"

from fastapi.testclient import TestClient
from sqlalchemy import select
from app.database import Base, SessionLocal, engine
from app.main import app
from app.models.entities import Method, GameExample, HardwareGPU, Project
from app import repositories
from app.seed import seeder
from app.schemas.catalog import ProjectProfile
from app.services import hardware, project_import, presets

logging.disable(logging.CRITICAL)
results = {}
Base.metadata.create_all(engine)
with SessionLocal() as db:
    results["seed"] = seeder.seed_all(db)
    results["published_counts"] = repositories.published_snapshot_counts(db)
    methods = repositories.methods(db)
    known = {m.code for m in methods}
    functions = {f.code for f in repositories.functions(db)}
    results["unknown_example_codes"] = [
        {"title": e.title, "features": sorted(set(e.features) - functions),
         "methods": sorted(set(e.optimizations_used) - known)}
        for e in repositories.examples(db)
        if set(e.features) - functions or set(e.optimizations_used) - known
    ]
    results["required_hardware"] = dict(collections.Counter(
        feature for m in methods for feature in m.requires_hw_features))
    results["empty_method_fields"] = {
        key: sum(not getattr(m, key) for m in methods)
        for key in ["pros", "cons", "limitations", "application_steps", "requires_conditions"]
    }

results["load_inputs"] = []
for fields in [
    {"audio_complexity": "unknown"}, {"npc_count": 0}, {"npc_count": 1},
    {"npc_count": 10_000}, {"npc_count": 10_000_000},
    {"format": "2D"}, {"format": "3D"},
    {"target_fps": 60}, {"target_fps": 120},
]:
    profile = ProjectProfile(**fields)
    try:
        value = hardware._load_indices(profile, [])
        results["load_inputs"].append({"input": fields, "output": {
            k: value[k] for k in ["cpu_index", "gpu_index", "ram_gb", "vram_gb"]}})
    except Exception as exc:
        results["load_inputs"].append({"input": fields, "error": repr(exc)})

results["unity_import"] = project_import.parse_unity_settings(
    b"PlayerSettings:\n  productName: Real Game\n  defaultScreenWidth: 1920\n  defaultScreenHeight: 1080\n",
    "ProjectSettings.asset")
results["godot_import"] = project_import.parse_godot_project(
    b'config_version=5\n\n[application]\nconfig/name="Real Game"\nconfig/features=PackedStringArray("4.3", "GL Compatibility")\n')
results["import_resolution"] = {str(n): project_import.height_to_resolution(n)
                                for n in [768, 900, 1200, 1600, 1800]}
results["godot_preset_keys"] = list(presets.godot_rendering_preset(ProjectProfile(), set()))

with TestClient(app, raise_server_exceptions=False) as client:
    results["hardware_api"] = []
    for fields in [{"audio_complexity": "unknown"}, {"platforms": ["macos"]},
                   {"platforms": ["macos"], "render_api": "metal"},
                   {"render_api": "dx9", "upscaling_method": "dlss"}]:
        response = client.post("/api/hardware-estimate", json={"profile": fields, "basket": []})
        results["hardware_api"].append({"input": fields, "status": response.status_code,
                                        "output": response.json()})
    response = client.post("/api/admin/import/conflicts", files={"file": (
        "conflicts.json", json.dumps([{"a_code": "a", "b_code": "b", "conflict_type": "conflict"}]),
        "application/json")})
    results["conflict_import"] = {"status": response.status_code, "body": response.json()}
    response = client.post("/api/admin/import/conflicts", files={"file": (
        "conflicts.json", json.dumps([{"title": "a-b", "a_code": "a", "b_code": "b"}]),
        "application/json")})
    results["conflict_import_with_title"] = {"status": response.status_code, "body": response.json()}
    response = client.get("/api/catalog/methods/not_in_catalog")
    results["request_id"] = {"header": response.headers.get("x-request-id"), "body": response.json()}
    imported = client.post("/api/project-import", files=[("files", (
        "ProjectVersion.txt", b"m_EditorVersion: 2022.3.10f1\n", "text/plain"))]).json()
    results["partial_import_full_defaults"] = imported
    saved = client.post("/api/projects", json={"profile": {}, "basket": []}).json()["public_id"]
    feedback = client.post(f"/api/projects/{saved}/feedback",
                           json={"method_code": "temporal_upscaling", "useful": True})
    results["feedback_outside_basket"] = {"status": feedback.status_code, "body": feedback.json()}
    with SessionLocal() as db:
        row = db.scalar(select(Project).where(Project.public_id == saved))
        results["saved_result_keys"] = list(row.result)
    response = client.post("/api/admin/methods", json={
        "code": "temporal_upscaling", "name": "Audit source erased"})
    public = client.get("/api/catalog/methods/temporal_upscaling").json()
    results["published_edit_without_source"] = {
        "write_status": response.status_code,
        "public": {k: public[k] for k in ["name", "status", "source_url"]}}

data = json.loads((ROOT / "backend/app/seed/data/hardware.json").read_text(encoding="utf-8"))
results["class_score_ranges"] = []
for kind, score in [("cpu", "multi_thread_score"), ("gpu", "raster_score")]:
    for level in range(1, 6):
        rows = [r for r in data[kind] if r["perf_class"] == level]
        low, high = min(rows, key=lambda r: r[score]), max(rows, key=lambda r: r[score])
        results["class_score_ranges"].append({
            "kind": kind, "class": level, "min": low[score], "max": high[score],
            "min_model": low["model"], "max_model": high["model"],
            "ratio": high[score] / low[score]})

results["source_sha256"] = {}
for folder in [ROOT / "backend/app", ROOT / "backend/tests", ROOT / "frontend/src"]:
    for path in sorted(folder.rglob("*")):
        if path.is_file() and "__pycache__" not in path.parts:
            results["source_sha256"][path.relative_to(ROOT).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
results["source_sha256"]["README.md"] = hashlib.sha256((ROOT / "README.md").read_bytes()).hexdigest()
engine.dispose()
temporary.cleanup()
print(json.dumps(results, ensure_ascii=False, indent=2))
