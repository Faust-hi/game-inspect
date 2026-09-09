"""Reproduce memory estimates; batch profiles are inputs, not accuracy references.

Run from the repository root: python validation/diagnose_memory.py OUTPUT.json
Uses an isolated in-memory database and never changes the application database.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.database import Base
from app.schemas.catalog import ProjectProfile
from app.seed import seeder
from app.services.hardware import _memory_components, build_model, estimate_hardware
from app.services.recommender import ALGORITHM_VERSION


def diagnose() -> dict:
    parser_path = ROOT / "audit-2026-09-07/run_batches.py"
    spec = importlib.util.spec_from_file_location("batch_parser", parser_path)
    parser = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(parser)
    engine = create_engine("sqlite://")
    try:
        Base.metadata.create_all(engine)
        rows = []
        with Session(engine) as db:
            seeder.seed_all(db, validate=False)
            db.flush()
            for path in sorted(ROOT.glob("партия-*.md")):
                for game in parser.parse_games(path.read_text(encoding="utf-8")):
                    profile = ProjectProfile.model_validate(parser.profile_of(game))
                    model = build_model(profile, [])
                    estimate = estimate_hardware(db, profile, [])
                    rows.append({
                        "batch": path.name,
                        "profile": profile.model_dump(mode="json"),
                        "content": model.content,
                        "components": model.memory,
                        "raw_ram_gb": sum(v["ram"] for v in model.memory.values()),
                        "estimated_ram_gb": estimate.estimated_ram_gb,
                        "estimated_vram_gb": estimate.estimated_vram_gb,
                        "cpu": estimate.reference_cpu.model if estimate.reference_cpu else None,
                        "gpu": estimate.reference_gpu.model if estimate.reference_gpu else None,
                    })
        tracked_inputs = [
            ROOT / "backend/app/services/hardware.py",
            ROOT / "backend/app/seed/data/hardware.json",
            parser_path,
            *sorted(ROOT.glob("партия-*.md")),
        ]
        return {
            "purpose": "diagnostic reproduction; no independent accuracy claim",
            "head": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
            "algorithm_version": ALGORITHM_VERSION,
            "sha256": {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                       for p in tracked_inputs},
            "zero_content_components_1080p": _memory_components(ProjectProfile(), 0, set()),
            "profiles": rows,
        }
    finally:
        engine.dispose()


if __name__ == "__main__":
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("output", type=Path)
    args = cli.parse_args()
    report = diagnose()
    with args.output.open("x", encoding="utf-8") as output:
        json.dump(report, output, ensure_ascii=False, indent=2, allow_nan=False)
    print(f"Wrote {len(report['profiles'])} diagnostic profiles to {args.output}")
