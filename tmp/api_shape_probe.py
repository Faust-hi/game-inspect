"""Сверка фактических ответов API с типами frontend.

Пишет в tmp/api_shape.json реальные ответы: по ним видно, какие поля
объявлены в types.ts, но никогда не приходят (мёртвая ветка интерфейса).
"""
import json
import os
import pathlib
import sys
import tempfile

BACKEND = pathlib.Path(r"C:\Users\user\Desktop\game-inspect\backend")
sys.path.insert(0, str(BACKEND))

tmp = tempfile.mkdtemp(prefix="shape_probe_")
os.environ["DATABASE_URL"] = f"sqlite:///{tmp.replace(chr(92), '/')}/probe.db"
os.environ["AUTO_SEED"] = "false"

from app.database import Base, SessionLocal, engine  # noqa: E402
from app.seed import seeder  # noqa: E402

Base.metadata.create_all(bind=engine)
session = SessionLocal()
if seeder.is_empty(session):
    seeder.seed_all(session, validate=True)
session.commit()
session.close()

from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402

client = TestClient(app)

profile = {
    "name": "Проба",
    "format": "3D",
    "world_type": "open_world",
    "scale": "large",
    "stage": "prototype",
    "engine": "unreal",
    "platforms": ["pc_windows"],
    "functions": ["open_world_streaming", "crowd_simulation", "large_scale_terrain"],
    "target_resolution": "1440p",
    "target_quality": "high",
    "target_fps": 60,
    "npc_count_level": "high",
    "multiplayer": True,
    "player_count": 32,
}

CALLS = {
    "recommend": ("POST", "/api/recommend", {"profile": profile, "basket": []}),
    "hardware": ("POST", "/api/hardware-estimate", {"profile": profile, "basket": []}),
    "load": ("POST", "/api/load-profile", {"profile": profile, "basket": []}),
    "method": ("GET", "/api/catalog/methods", None),
    "function": ("GET", "/api/catalog/functions", None),
    "enums": ("GET", "/api/meta/enums", None),
    "health": ("GET", "/api/health", None),
    "hardware_catalog": ("GET", "/api/catalog/hardware", None),
}

out = {}
for name, (method, path, body) in CALLS.items():
    response = client.request(method, path, json=body)
    print(f"{name}: {response.status_code}")
    if response.status_code != 200:
        print("   тело:", response.text[:200])
        continue
    payload = response.json()
    out[name] = payload[0] if name in ("method", "function") else (
        payload["gpu"][0] if name == "hardware_catalog" else payload
    )
    if name == "hardware_catalog":
        out["gpu"] = out.pop("hardware_catalog")

target = pathlib.Path(r"C:\Users\user\Desktop\game-inspect\tmp\api_shape.json")
target.write_text(json.dumps(out, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
print("записано:", target)
