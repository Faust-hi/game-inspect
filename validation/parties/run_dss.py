"""Прогон всех игр партий 01-11 через расчётный движок DSS.

Для каждой игры считается:
  1) базовая аппаратная оценка профиля (пустая корзина);
  2) аппаратная оценка с учётом реализованных инженерных решений (корзина);
  3) сводный профиль нагрузки по корзине;
  4) рекомендации DSS до и после применения корзины.

Выход: validation/parties/results.json
"""

from __future__ import annotations

import json
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
BACKEND = HERE.parents[1] / "backend"
sys.path.insert(0, str(BACKEND))
sys.path.insert(0, str(HERE))
sys.stdout.reconfigure(encoding="utf-8")

os.environ.setdefault("AUTO_SEED", "false")
os.environ.setdefault("DATABASE_URL", f"sqlite:///{(BACKEND / 'gamedev_dss.db').as_posix()}")

from app.database import SessionLocal  # noqa: E402
from app.repositories import conflicts, methods_by_codes  # noqa: E402
from app.schemas.catalog import ProjectProfile  # noqa: E402
from app.services import hardware, recommender  # noqa: E402

PROFILES = json.loads((HERE / "profiles.json").read_text(encoding="utf-8"))
OUT = HERE / "results.json"


def dump(obj):
    if obj is None:
        return None
    if hasattr(obj, "model_dump"):
        return obj.model_dump(mode="json")
    return obj


def main() -> None:
    session = SessionLocal()
    results = []
    try:
        for p in PROFILES:
            profile = ProjectProfile(**p["profile"])
            basket = p["basket"]
            methods = methods_by_codes(session, basket)
            est_base = hardware.estimate_hardware(session, profile, [])
            est_basket = hardware.estimate_hardware(session, profile, methods)
            load = recommender.aggregate_load(
                methods, profile, relations=conflicts(session), estimate=est_basket
            )
            rec_base = recommender.build_recommendations(session, profile, [])
            rec_basket = recommender.build_recommendations(session, profile, basket)
            # второй срез: что DSS посоветовал бы, начнись проект с нуля
            arch_profile = profile.model_copy(update={"stage": "prototype"})
            rec_arch = recommender.build_recommendations(session, arch_profile, basket)
            results.append(
                {
                    "id": p["id"],
                    "party": p["party"],
                    "title": p["title"],
                    "year": p["year"],
                    "engine_dss": p["engine_dss"],
                    "engine_raw": p["engine_raw"],
                    "profile": p["profile"],
                    "basket": basket,
                    "basket_resolved": [m.code for m in methods],
                    "n_decisions": p["n_decisions"],
                    "n_technical": p.get("n_technical", p["n_decisions"]),
                    "n_excluded": p.get("n_excluded", 0),
                    "n_review": p.get("n_review", 0),
                    "n_matched": len(set(basket)),
                    "n_decisions_matched": p.get("n_decisions_matched", 0),
                    "unmatched": p["unmatched"],
                    "excluded": p.get("excluded", []),
                    "review": p.get("review", []),
                    "hw_passport": p["hw"],
                    "frame_budget_ms": p["frame_budget_ms"],
                    "estimate_base": dump(est_base),
                    "estimate_basket": dump(est_basket),
                    "load": dump(load),
                    "recommendations_base": dump(rec_base),
                    "recommendations_basket": dump(rec_basket),
                    "recommendations_arch": dump(rec_arch),
                }
            )
    finally:
        session.close()
    OUT.write_text(json.dumps(results, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"рассчитано игр: {len(results)}")
    e = results[0]["estimate_base"]
    print("поля оценки:", sorted(e.keys()))


if __name__ == "__main__":
    main()
