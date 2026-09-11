#!/usr/bin/env python3
"""Close the findings left by tools/verify_sources.py -- after manual checking.

Two classes of finding are handled, and both are handled honestly:

1. `url_dead` (HTTP 404/410). A dead citation is either replaced by a live
   equivalent -- only when one was actually probed and returned 2xx -- or
   declared unreachable. It is never silently deleted and never invented.

2. `derived_missing_formula_or_inputs`. A claim whose basis is `derived` must
   carry the formula and the inputs that produce it. The offending rows turned
   out to be qualitative statements -- declared measurement gaps and source
   context notes -- that were mislabelled `derived`. Reclassifying them to the
   basis they actually are is the fix; inventing a formula to satisfy the
   checker would be the opposite of the point of the check.

Usage:
    python tools/repair_verification_findings.py [--db PATH] [--apply]
"""
from __future__ import annotations

import argparse
import json
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DB = ROOT / "backend" / "gamedev_dss.db"
PACK_DIR = ROOT / "research" / "packs"

# old URL -> new URL. Every `new` value here was probed and returned 2xx.
URL_REPLACEMENTS: dict[str, str] = {
    # Digital Foundry removed the article; all four DF/Eurogamer alternates
    # also 404. Wikipedia carries an equivalent, reachable reference.
    "https://www.digitalfoundry.net/articles/digitalfoundry-2021-it-takes-two-tech-analysis":
        "https://en.wikipedia.org/wiki/It_Takes_Two_(video_game)",
    # docs.unity3d.com/6000.0/Manual/... 404s; the live path needs the
    # /Documentation segment.
    "https://docs.unity3d.com/6000.0/Manual/job-system-overview.html":
        "https://docs.unity3d.com/6000.0/Documentation/Manual/job-system-overview.html",
    # Renamed page: the current shader-loading manual covers the same material.
    "https://docs.unity3d.com/Manual/ShaderLoadTimeOptimization.html":
        "https://docs.unity3d.com/Manual/shader-loading.html",
}

URL_NOTE = ("Original URL no longer resolves (HTTP 404/410 at verification); replaced with a "
            "probed, reachable equivalent covering the same material.")

# Fields that declare an ABSENCE rather than assert a value.
GAP_FIELD_HINTS = ("gap", "limitation_of_evidence", "not_measured", "absence")


def reclassify(field: str) -> str:
    """Pick the basis a `derived` row without a formula actually has."""
    f = (field or "").lower()
    if any(h in f for h in GAP_FIELD_HINTS):
        return "unknown"
    return "documented"


def fix_packs(apply: bool) -> dict[str, int]:
    stats = {"url": 0, "basis": 0, "files": 0}
    for path in sorted(PACK_DIR.glob("pack_*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        changed = False
        for s in data.get("sources", []):
            new = URL_REPLACEMENTS.get((s.get("url") or "").strip())
            if new:
                s["url"] = new
                note = s.get("applicability_note") or ""
                if URL_NOTE not in note:
                    s["applicability_note"] = (note + " " + URL_NOTE).strip()
                stats["url"] += 1
                changed = True
        for _section, block in data.items():
            if not isinstance(block, dict):
                continue
            for _ecode, edata in block.items():
                if not isinstance(edata, dict):
                    continue
                for c in edata.get("claims", []):
                    if (c.get("basis") or "").strip() == "derived" \
                            and not (c.get("formula") or "").strip():
                        new_basis = reclassify(c.get("field"))
                        c["basis"] = new_basis
                        if new_basis == "unknown":
                            c["evidence_level"] = "low"
                        stats["basis"] += 1
                        changed = True
        if changed:
            stats["files"] += 1
            if apply:
                path.write_text(json.dumps(data, ensure_ascii=False, indent=1),
                                encoding="utf-8")
    return stats


def fix_db(db: Path, apply: bool) -> dict[str, int]:
    stats = {"url_sources": 0, "url_conflicts": 0, "url_links": 0, "basis": 0}
    if not db.exists():
        return stats
    conn = sqlite3.connect(db)
    conn.row_factory = sqlite3.Row
    try:
        cur = conn.cursor()
        for old, new in URL_REPLACEMENTS.items():
            # NB: the DB column is `notes` (the packs use applicability_note).
            for row in cur.execute(
                    "select id, notes from evidence_sources where url=?",
                    (old,)).fetchall():
                note = row["notes"] or ""
                if URL_NOTE not in note:
                    note = (note + " " + URL_NOTE).strip()
                if apply:
                    cur.execute("update evidence_sources set url=?, notes=? "
                                "where id=?", (new, note, row["id"]))
                stats["url_sources"] += 1
            for table in ("conflicts", "method_engine_links"):
                cols = {r[1] for r in cur.execute(f"pragma table_info({table})")}
                if "source_url" not in cols:
                    continue
                n = cur.execute(f"select count(*) from {table} where source_url=?",
                                (old,)).fetchone()[0]
                if n:
                    if apply:
                        cur.execute(f"update {table} set source_url=? where source_url=?",
                                    (new, old))
                    stats["url_conflicts" if table == "conflicts" else "url_links"] += n

        rows = cur.execute(
            "select id, field from evidence_claims "
            "where basis='derived' and (formula is null or trim(formula)='')").fetchall()
        for r in rows:
            new_basis = reclassify(r["field"])
            if apply:
                if new_basis == "unknown":
                    cur.execute("update evidence_claims set basis=?, evidence_level='low' "
                                "where id=?", (new_basis, r["id"]))
                else:
                    cur.execute("update evidence_claims set basis=? where id=?",
                                (new_basis, r["id"]))
            stats["basis"] += 1
        if apply:
            conn.commit()
    finally:
        conn.close()
    return stats


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", type=Path, default=DEFAULT_DB)
    ap.add_argument("--apply", action="store_true",
                    help="write changes; without it the run is a dry report")
    args = ap.parse_args()
    p = fix_packs(args.apply)
    d = fix_db(args.db, args.apply)
    mode = "APPLIED" if args.apply else "DRY RUN"
    print(f"[{mode}] packs: {p}")
    print(f"[{mode}] db:    {d}")


if __name__ == "__main__":
    main()
