"""Значения стоимости проходов для переписывания теста про общий бюджет кадра."""
import json
import os
import pathlib
import sys
import tempfile

BACKEND = pathlib.Path(r"C:\Users\user\Desktop\game-inspect\backend")
sys.path.insert(0, str(BACKEND))

tmp = tempfile.mkdtemp(prefix="rt_")
os.environ["DATABASE_URL"] = f"sqlite:///{tmp.replace(chr(92), '/')}/probe.db"
os.environ["AUTO_SEED"] = "false"

from app.database import Base, SessionLocal, engine  # noqa: E402
from app.seed import seeder  # noqa: E402

Base.metadata.create_all(bind=engine)
s = SessionLocal()
if seeder.is_empty(s):
    seeder.seed_all(s, validate=True)
s.commit()
s.close()

from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402

client = TestClient(app)

BASE = {
    "format": "3D", "world_type": "open_world", "scale": "large",
    "stage": "prototype", "engine": "unreal", "platforms": ["pc_windows"],
    "functions": ["open_world_streaming", "crowd_simulation"],
    "target_resolution": "1080p", "target_quality": "high", "target_fps": 60,
}
functions = BASE["functions"] + ["ray_traced_effects"]


def estimate(basket=(), **overrides):
    profile = dict(BASE, **overrides)
    return client.post(
        "/api/hardware-estimate", json={"profile": profile, "basket": list(basket)}
    ).json()


cases = {
    "без RT-функции, без метода": estimate(),
    "с RT-функцией, без метода": estimate(functions=functions),
    "с RT-функцией и методом": estimate(basket=["hardware_raytraced_gi"], functions=functions),
    "с RT-функцией, метод + бюджет": estimate(
        basket=["hardware_raytraced_gi", "rt_effect_resolution_budget"], functions=functions
    ),
}
budget = 1000.0 / BASE["target_fps"]
for name, data in cases.items():
    print(f"{name}: raster={data['gpu_raster_cost']:.3f} rt={data['gpu_rt_cost']:.3f} "
          f"индекс={data['required_gpu_index']:.4f}")
    print(f"   (raster+rt)/бюджет = {(data['gpu_raster_cost'] + data['gpu_rt_cost']) / budget:.4f}")
print("бюджет кадра, мс:", round(budget, 3))
print(json.dumps({k: v["gpu_rt_cost"] for k, v in cases.items()}, ensure_ascii=False))
