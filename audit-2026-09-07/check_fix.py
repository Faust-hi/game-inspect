# -*- coding: utf-8 -*-
"""Быстрая сверка после правок: разнообразие bottleneck и коридор памяти."""
from __future__ import annotations

import collections
import statistics
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT / "backend"))
sys.path.insert(0, str(HERE))

from app.database import SessionLocal  # noqa: E402
from app.schemas.catalog import BasketRequest  # noqa: E402
from app.services import hardware, recommender  # noqa: E402

import run_batches as rb  # noqa: E402


def profile(**over):
    base = rb.profile_of({
        "name": "проверка",
        "format": "3D", "world_type": "linear", "scale": "medium",
        "engine": "custom", "platforms": ["pc_windows"],
        "object_level": "medium", "npc_level": "medium",
        "multiplayer": False, "player_count": 1, "functions": [],
        "resolution": "1080p", "fps": 60,
    })
    base.update(over)
    return BasketRequest(profile=base, basket=[]).profile


CONTRAST = {
    "лёгкий 2D, 720p/low": dict(format="2D", scale="small", target_resolution="720p",
                                target_quality="low", functions=["particle_systems"]),
    "толпа NPC, 1080p/high": dict(scale="large", npc_count_level="high",
                                  functions=["crowd_simulation", "ai_pathfinding"]),
    "открытый мир, 4K/ultra": dict(scale="very_large", target_resolution="2160p",
                                   target_quality="ultra", object_count_level="high",
                                   functions=["open_world_streaming", "dynamic_shadows",
                                              "volumetric_effects"]),
    "шутер, 1080p/medium, 144 fps": dict(scale="small", target_quality="medium",
                                         target_fps=144, functions=[]),
    "физика 120 Гц": dict(physics_tick_hz=120,
                          functions=["physics_simulation", "destruction_simulation"]),
    "мир 8 ГБ VRAM предел": dict(scale="very_large", object_count_level="high",
                                 npc_count_level="high", vram_limit_gb=8,
                                 functions=["open_world_streaming", "large_scale_terrain",
                                            "procedural_vegetation"]),
    "мир 4 ГБ VRAM предел": dict(scale="very_large", object_count_level="high",
                                 npc_count_level="high", vram_limit_gb=4,
                                 functions=["open_world_streaming", "large_scale_terrain",
                                            "procedural_vegetation"]),
}


def main() -> None:
    db = SessionLocal()
    print("--- контрастные профили ---")
    seen = set()
    for name, over in CONTRAST.items():
        est = hardware.estimate_hardware(db, profile(**over), [])
        seen.add(est.bottleneck)
        print(f"{name:32s} {est.bottleneck:16s} cpu={est.required_cpu_index:.3f} "
              f"gpu={est.required_gpu_index:.3f} ram={est.estimated_ram_gb} "
              f"vram={est.estimated_vram_gb}")
    print("различных узких мест:", len(seen), sorted(seen))

    print("\n--- 58 игр из партий ---")
    rows = []
    tops = collections.Counter()
    for path in sorted(ROOT.glob("партия-*.md")):
        for game in rb.parse_games(path.read_text(encoding="utf-8")):
            payload = BasketRequest(profile=rb.profile_of(game), basket=[])
            data = recommender.build_recommendations(db, payload.profile, [])
            hw = data.hardware
            rows.append((game["name"], hw.bottleneck, hw.estimated_vram_gb,
                         hw.estimated_ram_gb))
            recs = sorted(data.recommendations, key=lambda r: (-r.score, r.method_code))
            if recs:
                tops[recs[0].method_name] += 1
    print("игр:", len(rows))
    print("bottleneck:", dict(collections.Counter(r[1] for r in rows)))
    rams = [r[3] for r in rows]
    vrams = [r[2] for r in rows]
    print(f"RAM  {min(rams)}–{max(rams)} ГБ, медиана {statistics.median(rams)}, "
          f"размах ×{max(rams) / min(rams):.2f}")
    print(f"VRAM {min(vrams)}–{max(vrams)} ГБ, медиана {statistics.median(vrams)}, "
          f"размах ×{max(vrams) / min(vrams):.2f}")
    print("RAM < VRAM:", sum(1 for r in rows if r[3] < r[2]))
    print("топ-1:", tops.most_common(5))


if __name__ == "__main__":
    sys.exit(main())
