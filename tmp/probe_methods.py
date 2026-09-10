"""Зонд: что отдаёт GET /api/methods в среде тестов."""
from __future__ import annotations

import json
import os
import pathlib
import sys
import tempfile

BACKEND = pathlib.Path(__file__).resolve().parents[1] / "backend"
sys.path.insert(0, str(BACKEND))
os.chdir(BACKEND)

tmp = tempfile.mkdtemp(prefix="probe_methods_")
os.environ["DATABASE_URL"] = f"sqlite:///{(pathlib.Path(tmp) / 'probe.db').as_posix()}"
os.environ["AUTO_SEED"] = "false"

from fastapi.testclient import TestClient  # noqa: E402

from app.database import Base, SessionLocal, engine  # noqa: E402
from app.main import app  # noqa: E402
from app.seed import seeder  # noqa: E402

Base.metadata.create_all(bind=engine)
session = SessionLocal()
try:
    if seeder.is_empty(session):
        seeder.seed_all(session, validate=True)
    session.commit()
finally:
    session.close()

with TestClient(app) as client:
    response = client.get("/api/catalog/methods")
    print("STATUS:", response.status_code)
    body = response.json()
    print("TYPE:", type(body).__name__)
    if isinstance(body, dict):
        print("KEYS:", list(body)[:10])
        print(json.dumps(body, ensure_ascii=False)[:600])
    else:
        print("LEN:", len(body))
        first = body[0]
        print("FIRST CODE:", first.get("code"))
        print("INDEPENDENT:", first.get("engine_tool_independent"))
        print("LINKS:", len(first.get("engine_links", [])))
        flagged = [m["code"] for m in body if m.get("engine_tool_independent")]
        print("FLAGGED COUNT:", len(flagged))
        print("FLAGGED:", flagged)

# Какая поддержка движка у методов в выдаче рекомендаций для разных профилей.
with TestClient(app) as client:
    for name, profile in {
        "multiplayer16": {
            "name": "П", "format": "3D", "world_type": "open_world", "scale": "large",
            "stage": "prototype", "engine": "unreal", "platforms": ["pc_windows"],
            "functions": ["large_scale_terrain"], "target_resolution": "1080p",
            "target_quality": "high", "target_fps": 60,
            "multiplayer": True, "player_count": 16,
        },
        "mp_full": {
            "name": "П", "format": "3D", "world_type": "open_world", "scale": "large",
            "stage": "prototype", "engine": "unreal", "platforms": ["pc_windows"],
            "functions": ["large_scale_terrain", "crowd_simulation", "audio_system", "open_world_streaming"],
            "target_resolution": "1080p", "target_quality": "high", "target_fps": 60,
            "multiplayer": True, "player_count": 32, "storage_type": "hdd", "render_api": "dx12",
        },
    }.items():
        data = client.post("/api/recommend", json={"profile": profile, "basket": []}).json()
        recs = data.get("recommendations", [])
        unsupported = [(i["method_code"], i.get("engine_tool_independent")) for i in recs if i["engine_support"] is None]
        print(f"[{name}] всего: {len(recs)}, без поддержки: {unsupported[:6]}")
