#!/usr/bin/env python3
"""Consistency check: does the engine still reproduce the numbers documented in research?

The unit tests in `backend/tests/` pin the *invariants* of the calculation model
(scene scale changes load but not frame cost; server effects do not discount the
player PC; team size moves the calendar but not person-days). They deliberately
assert direction and equality, not exact values, so a legitimate model change
does not break them.

That leaves a second, quieter failure mode: the research documents record the
concrete numbers those runs produced, and nothing re-checks them. If the model
drifts, the tests stay green while `research/category_verification.md` silently
goes stale — exactly the defect that had to be reconciled by hand.

This tool closes that gap. It rebuilds a throwaway database, runs the same three
scenarios the research documents, and compares the results against the recorded
values. Exact matching is intentional here: a mismatch is a signal to update the
research document (or to explain the change), not a reason to relax the check.
It is therefore a maintenance tool, not a unit test — it is not part of pytest.

Usage:
    python tools/check_research_invariants.py [--json PATH]

Runs on a temporary database; the working `backend/gamedev_dss.db` is never
opened for writing. Exit code is non-zero when any recorded value no longer
reproduces.
"""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"

# The engine needs a database; point it at a fresh file before importing the app
# so no module picks up the working one. AUTO_SEED is disabled because this tool
# seeds the throwaway database itself.
_TMP = pathlib.Path(tempfile.mkdtemp(prefix="dss_invariants_"))
os.environ["DATABASE_URL"] = f"sqlite:///{(_TMP / 'invariants.db').as_posix()}"
os.environ["AUTO_SEED"] = "false"

sys.path.insert(0, str(BACKEND))

from fastapi.testclient import TestClient  # noqa: E402

from app.database import Base, SessionLocal, engine  # noqa: E402
from app.main import app  # noqa: E402
from app.seed import seeder  # noqa: E402

# Recorded results — see research/category_verification.md §2.3, §2.8, §2.10.
SCENE_PROFILE = {
    "name": "Инвариант масштаба сцены",
    "format": "3D",
    "world_type": "open_world",
    "scale": "large",
    "stage": "prototype",
    "engine": "unreal",
    "platforms": ["pc_windows"],
    "functions": ["open_world_streaming", "crowd_simulation"],
    "target_resolution": "1080p",
    "target_quality": "high",
    "target_fps": 60,
}
SCENE_EXPECTED = {
    "small": {"ram": 11.5, "vram": 6.4, "draw_calls": 23567, "storage": "sata_ssd"},
    "very_large": {"ram": 15.2, "vram": 9.4, "draw_calls": 41825, "storage": "nvme"},
}
SCENE_FRAME_INDEX = {"cpu": 0.2842, "gpu": 0.2131}

SERVER_EXPECTED = {"cpu": 0.2842, "gpu": 0.1515}

PLAN_BASKET = [
    "world_partition_streaming", "virtual_geometry_clusters", "hardware_raytraced_gi",
    "temporal_upscaling", "virtual_shadow_maps", "motion_matching",
    "client_prediction_reconciliation", "tickrate_budgeting", "directstorage_io",
    "gpu_compute_culling",
]
# Календарь и длина критического пути учитывают предусловия из `dependency_codes`
# у пакетов работ: первый пакет метода ждёт интеграционный пакет того метода,
# от которого он зависит. До 2026-09-11 это поле оставалось пустым, и путь
# укорачивался (7 задач, меньший календарь) — зависимость между
# `world_partition_streaming` и `async_loading_pipeline` в плане не проявлялась.
# Величина оценки — курируемая (`effort_person_days` из research/packs/pack_*.json),
# структура по фазам — формульная (доли `implementation_cost` и `complexity`).
# До 2026-09-11 величину задавала только формула: 12 различных итогов на 124
# метода и разброс 3,02×, из-за чего конвейер не отличался от точечной правки.
# Подробнее — research/n2-recommendation-2026-09-11.md.
PLAN_EXPECTED_CALENDAR = {
    "solo": 678.33, "small_2_5": 453.54, "mid_6_15": 222.69, "large_16_plus": 116.31,
}
PLAN_EXPECTED_EFFORT = 702.00
# Корзина разрастается обязательными предусловиями: 10 методов запроса дают 19
# с учётом зависимостей. До 2026-09-11 их было 21: `motion_matching` требовал
# `animation_lod_budget`, с которым у него объявлен `hard_conflict`, — снятая
# пара убрала из плана сам метод и его собственную зависимость.
PLAN_EXPECTED_METHODS = 19
PLAN_EXPECTED_TASKS = 126
PLAN_EXPECTED_CRITICAL = 9


def _seed_scratch_database() -> None:
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    try:
        if seeder.is_empty(session):
            seeder.seed_all(session, validate=True)
        session.commit()
    finally:
        session.close()


class Checker:
    """Collects mismatches instead of aborting on the first one."""

    def __init__(self) -> None:
        self.issues: list[dict] = []

    def expect(self, label: str, actual, expected, tol: float = 0.0) -> None:
        if isinstance(expected, float) and isinstance(actual, (int, float)):
            ok = abs(float(actual) - expected) <= tol
        else:
            ok = actual == expected
        if not ok:
            self.issues.append({"check": label, "actual": actual, "expected": expected})


def _hw(client: TestClient, profile: dict, basket: list[str] | None = None) -> dict:
    response = client.post(
        "/api/hardware-estimate", json={"profile": profile, "basket": basket or []}
    )
    assert response.status_code == 200, response.text
    return response.json()


def _schedule(client: TestClient, profile: dict, basket: list[str], team: str) -> dict:
    response = client.post(
        "/api/schedule", json={"profile": profile, "basket": basket, "team": team}
    )
    assert response.status_code == 200, response.text
    return response.json()


def run(client: TestClient, checker: Checker) -> None:
    # §2.3 — scene scale moves load/streaming, not the cost of a frame.
    small = _hw(client, {**SCENE_PROFILE, "scale": "small"})
    very_large = _hw(client, {**SCENE_PROFILE, "scale": "very_large"})
    for scale, data in (("small", small), ("very_large", very_large)):
        want = SCENE_EXPECTED[scale]
        checker.expect(f"§2.3 {scale} RAM", data["estimated_ram_gb"], want["ram"], 0.05)
        checker.expect(f"§2.3 {scale} VRAM", data["estimated_vram_gb"], want["vram"], 0.05)
        checker.expect(f"§2.3 {scale} draw calls", data["estimated_draw_calls"], want["draw_calls"])
        checker.expect(f"§2.3 {scale} storage", data["recommended_storage"], want["storage"])
        checker.expect(f"§2.3 {scale} cpu index", data["required_cpu_index"], SCENE_FRAME_INDEX["cpu"], 0.001)
        checker.expect(f"§2.3 {scale} gpu index", data["required_gpu_index"], SCENE_FRAME_INDEX["gpu"], 0.001)

    # §2.8 — a headless server effect must not discount the player's PC.
    net_profile = {**SCENE_PROFILE, "functions": ["multiplayer_netcode"], "multiplayer": True}
    for basket, tag in (([], "base"), (["headless_dedicated_server"], "+headless")):
        data = _hw(client, net_profile, basket)
        checker.expect(f"§2.8 {tag} cpu index", data["required_cpu_index"], SERVER_EXPECTED["cpu"], 0.001)
        checker.expect(f"§2.8 {tag} gpu index", data["required_gpu_index"], SERVER_EXPECTED["gpu"], 0.001)

    # §2.10 — team size moves the calendar, never the person-days.
    plan_profile = {**SCENE_PROFILE, "functions": ["open_world_streaming", "crowd_simulation", "multiplayer_netcode"]}
    for team, calendar in PLAN_EXPECTED_CALENDAR.items():
        data = _schedule(client, plan_profile, PLAN_BASKET, team)
        checker.expect(f"§2.10 {team} effort.p50", data["effort"]["p50"], PLAN_EXPECTED_EFFORT, 0.02)
        checker.expect(f"§2.10 {team} calendar.p50", data["calendar"]["p50"], calendar, 0.02)
        checker.expect(f"§2.10 {team} methods", len(data["methods"]), PLAN_EXPECTED_METHODS)
        checker.expect(f"§2.10 {team} tasks", len(data["tasks"]), PLAN_EXPECTED_TASKS)
        checker.expect(f"§2.10 {team} critical", sum(1 for t in data["tasks"] if t["critical"]), PLAN_EXPECTED_CRITICAL)
        checker.expect(f"§2.10 {team} unresolved", len(data["unresolved_dependencies"]), 0)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--json", default=None, help="also write the result as JSON to this path")
    args = parser.parse_args()

    _seed_scratch_database()
    checker = Checker()
    with TestClient(app) as client:
        run(client, checker)

    if args.json:
        pathlib.Path(args.json).write_text(
            json.dumps({"ok": not checker.issues, "issues": checker.issues}, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    if checker.issues:
        print(f"РАСХОЖДЕНИЙ: {len(checker.issues)} — research/category_verification.md устарел")
        for issue in checker.issues:
            print(f"  - {issue['check']}: получено {issue['actual']!r}, записано {issue['expected']!r}")
        return 1
    print("OK: движок воспроизводит числа из research/category_verification.md (§2.3, §2.8, §2.10)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
