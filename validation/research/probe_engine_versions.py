"""Read-only application probe; fresh in-memory SQLite, exclusive research output."""
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "backend"))
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from app.database import Base
from app.models.entities import Method, MethodEngineLink
from app.schemas.catalog import ProjectProfile
from app.seed.seeder import seed_all
from app.services.recommender import build_recommendations
from app.services import rules, serializers

engine = create_engine("sqlite://")
Base.metadata.create_all(engine)
records = []
with Session(engine) as session:
    seed_all(session, validate=False)
    session.flush()
    method = session.scalar(select(Method).where(Method.code == "virtual_geometry_clusters"))
    for version in ("4.27", "5.5", "unknown-research-version"):
        profile = ProjectProfile(engine="unreal", engine_version=version,
                                 platforms=["pc_windows"], stage="preproduction",
                                 functions=["large_scale_terrain"], complexity_tolerance=5)
        result = build_recommendations(session, profile, [method.code])
        applicability = rules.evaluate(method, profile)
        records.append({"profile": profile.model_dump(), "applicability": vars(applicability),
                        "accounted_method_codes": result.accounted_method_codes,
                        "selected_methods": [m.model_dump() for m in result.selected_methods],
                        "risks": [r.model_dump() for r in result.risks],
                        "hardware": result.hardware.model_dump() if result.hardware else None})
    link = session.scalars(select(MethodEngineLink)).first()
    original = link.source_url
    # Transient synthetic input; do not flush or commit it, and restore immediately.
    link.source_url = "https://example.invalid/research-specific-evidence"
    with session.no_autoflush:
        public = serializers.link_out(session, link).model_dump()
    link.source_url = original
    evidence = {"input_source_url": "https://example.invalid/research-specific-evidence", "public": public}
engine.dispose()
value = {"kind": "deterministic_in_memory_probe_not_game_benchmark", "live_db_opened": False,
         "versions": records, "link_provenance_probe": evidence,
         "source_sha256": {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in
                           ("backend/app/services/rules.py", "backend/app/services/recommender.py",
                            "backend/app/services/serializers.py")}}
with (ROOT / "validation/research/engine-versions-2026-09-09.json").open("x", encoding="utf-8") as output:
    json.dump(value, output, ensure_ascii=False, indent=2, default=str)
print(json.dumps([{ "version": r["profile"]["engine_version"],
                    "applicable": r["applicability"]["applicable"],
                    "accounted": r["accounted_method_codes"],
                    "risk_codes": [v["code"] for v in r["risks"]]} for r in records], ensure_ascii=False))
