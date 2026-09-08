# -*- coding: utf-8 -*-
"""Прогон игр партий по всем стадиям проекта: что реально меняется."""
from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
sys.path.insert(0, str(BACKEND))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.database import SessionLocal  # noqa: E402
from app.models.enums import DevStage  # noqa: E402
from app.schemas.catalog import BasketRequest  # noqa: E402
from app.services import recommender  # noqa: E402

import run_batches as rb  # noqa: E402

STAGES = [s.value for s in DevStage]
db = SessionLocal()


def collect() -> list[dict]:
    rows = []
    for path in sorted(ROOT.glob("партия-*.md")):
        for game in rb.parse_games(path.read_text(encoding="utf-8")):
            game["batch"] = path.stem.replace("партия-", "")
            for stage in STAGES:
                profile = rb.profile_of(game)
                profile["stage"] = stage
                payload = BasketRequest(profile=profile, basket=[])
                data = recommender.build_recommendations(db, payload.profile, [])
                hw = data.hardware
                rows.append({
                    "game": game["name"],
                    "year": game["year"],
                    "stage": stage,
                    "top1": data.recommendations[0].method_code if data.recommendations else None,
                    "top1_name": data.recommendations[0].method_name if data.recommendations else None,
                    "top8": [r.method_code for r in data.recommendations[:8]],
                    "recs": len(data.recommendations),
                    "excluded": len(data.excluded),
                    "risks": [r.code for r in data.risks],
                    "gpu_index": hw.required_gpu_index if hw else None,
                    "vram": hw.estimated_vram_gb if hw else None,
                    "ram": hw.estimated_ram_gb if hw else None,
                    "gpu_model": hw.reference_gpu.model if hw and hw.reference_gpu else None,
                    "bottleneck": hw.bottleneck if hw else None,
                })
    return rows


def main() -> None:
    rows = collect()
    out = Path(__file__).resolve().parent / "stage-run-results.json"
    out.write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")

    by_stage = defaultdict(list)
    for r in rows:
        by_stage[r["stage"]].append(r)
    by_game = defaultdict(dict)
    for r in rows:
        by_game[r["game"]][r["stage"]] = r

    print("=" * 78)
    print("ВЛИЯНИЕ СТАДИИ НА РЕЗУЛЬТАТ (58 игр × 8 стадий)")
    print("=" * 78)
    print(f"{'Стадия':<16} {'уник. топ-1':<12} {'уник. наборов топ-8':<20} {'реков':<8} {'искл.'}")
    for stage in STAGES:
        rs = by_stage[stage]
        print(f"{stage:<16} {len(set(r['top1'] for r in rs)):<12} "
              f"{len(set(tuple(r['top8']) for r in rs)):<20} "
              f"{sum(r['recs'] for r in rs)/len(rs):<8.1f} "
              f"{sum(r['excluded'] for r in rs)/len(rs):.1f}")

    print("\n--- Меняется ли результат у конкретной игры при смене стадии ---")
    changed_top1 = [g for g, d in by_game.items() if len(set(v["top1"] for v in d.values())) > 1]
    changed_top8 = [g for g, d in by_game.items()
                    if len(set(tuple(v["top8"]) for v in d.values())) > 1]
    changed_hw = [g for g, d in by_game.items()
                  if len(set(v["gpu_index"] for v in d.values())) > 1]
    print(f"Игр, у которых топ-1 меняется хотя бы на одной стадии: {len(changed_top1)} из {len(by_game)}")
    print(f"Игр, у которых меняется состав топ-8:                 {len(changed_top8)} из {len(by_game)}")
    print(f"Игр, у которых меняется аппаратная оценка (индекс GPU): {len(changed_hw)} из {len(by_game)}")

    print("\n--- Предупреждения (риски) по стадиям ---")
    for stage in STAGES:
        rs = by_stage[stage]
        c = Counter(code for r in rs for code in r["risks"])
        print(f"\n{stage}:")
        for code, cnt in c.most_common():
            print(f"  {cnt:>4}× {code}")
        if not c:
            print("  (нет ни одного предупреждения)")

    print("\n--- Пример: одна игра по всем стадиям ---")
    sample = "Cyberpunk 2077"
    if sample in by_game:
        for stage in STAGES:
            r = by_game[sample][stage]
            print(f"  {stage:<14} топ-1 {r['top1']:<34} реков {r['recs']:>2} "
                  f"GPU {r['gpu_index']:.3f} VRAM {r['vram']:.1f} риски {','.join(r['risks']) or '—'}")

    print(f"\nДанные: {out}")


if __name__ == "__main__":
    main()
