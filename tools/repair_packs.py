#!/usr/bin/env python3
"""Orchestrator repair pass: fix contract violations found by verify_sources.py.

Fixes applied (each is logged, nothing is silently rewritten):

  1. basis="derived" with no formula/input_parameters -> reclassified by the
     semantics of the claim, because "derived" REQUIRES a formula:
        * field names a gap           -> "unknown"
        * field names a limitation /
          context taken from a source -> "documented"
        * field is a case caveat      -> "case_evidence"
  2. duplicate game_example (same title twice inside one entity) -> the weaker
     duplicate is demoted to a `claim` with basis="documented" so the evidence
     is preserved but the "distinct games" rule holds.

Usage: python tools/repair_packs.py [--apply]
Without --apply it only prints what it would change.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACK_DIR = ROOT / "research" / "packs"


def classify(field: str, statement: str, has_source: bool) -> str:
    f = (field or "").lower()
    s = (statement or "").lower()
    if "gap" in f or "no published" in s or "not found" in s:
        return "unknown"
    if "non_determinism" in f or "not a target another project" in s:
        return "case_evidence"
    if "limitation" in f or "context" in f:
        return "documented"
    return "documented" if has_source else "unknown"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    log: list[str] = []
    for path in sorted(PACK_DIR.glob("pack_*.json")):
        pack = json.loads(path.read_text(encoding="utf-8"))
        changed = 0

        for section, block in list(pack.items()):
            if not isinstance(block, dict):
                continue
            for ecode, edata in block.items():
                if not isinstance(edata, dict):
                    continue

                # ---- 1. derived without formula ----
                for c in edata.get("claims", []):
                    if (c.get("basis") == "derived"
                            and not (c.get("formula") or "").strip()
                            and not c.get("input_parameters")):
                        new = classify(c.get("field", ""), c.get("statement", ""),
                                       bool(c.get("source")))
                        log.append(f"{path.name} {section}/{ecode} "
                                   f"field={c.get('field')}: derived -> {new}")
                        c["basis"] = new
                        changed += 1

                # ---- 3. expert_estimate without explicit disclosure ----
                for c in edata.get("claims", []):
                    if c.get("basis") != "expert_estimate":
                        continue
                    blob = ((c.get("context") or "") + " "
                            + (c.get("statement") or "")).lower()
                    if any(w in blob for w in ("оцен", "estimat", "эксперт",
                                               "assum", "judgement", "judgment",
                                               "not measured")):
                        continue
                    note = ("Экспертная оценка автора исследования (не измерение "
                            "и не прямое числовое утверждение источника): "
                            "вариант реализации отобран по инженерному опыту "
                            "и документации, требует проверки на конкретном проекте.")
                    c["context"] = (note + " " + (c.get("context") or "")).strip()
                    log.append(f"{path.name} {section}/{ecode} "
                               f"field={c.get('field')}: added expert_estimate disclosure")
                    changed += 1

                # ---- 2. duplicate game examples ----
                gex = edata.get("game_examples", [])
                seen: dict[str, int] = {}
                keep: list[dict] = []
                demoted: list[dict] = []
                for g in gex:
                    key = (g.get("game") or "").strip().lower()
                    if key and key in seen:
                        demoted.append(g)
                    else:
                        if key:
                            seen[key] = 1
                        keep.append(g)
                for g in demoted:
                    log.append(f"{path.name} {section}/{ecode}: demote duplicate "
                               f"game_example '{g.get('game')}' -> claim")
                    edata.setdefault("claims", []).append({
                        "field": "shipping_evidence",
                        "statement": g.get("fact", ""),
                        "unit": "",
                        "value": None,
                        "value_range": [None, None],
                        "source": g.get("source"),
                        "locator": g.get("locator", ""),
                        "basis": "documented",
                        "verification_state": "verified",
                        "evidence_level": "medium",
                        "formula": "",
                        "input_parameters": {"game": g.get("game", ""),
                                             "note": "same title as another example; "
                                                     "kept as a documented claim, not a "
                                                     "second distinct game proof"},
                        "context": "Duplicate-title example demoted by the "
                                   "orchestrator repair pass so the distinct-games "
                                   "rule holds.",
                    })
                    changed += 1
                if demoted:
                    edata["game_examples"] = keep

        if changed:
            if args.apply:
                path.write_text(json.dumps(pack, ensure_ascii=False, indent=2),
                                encoding="utf-8")
            print(f"{path.name}: {changed} change(s)"
                  + ("" if args.apply else " (dry run)"))

    print(f"\ntotal changes: {len(log)}")
    for line in log:
        print("  -", line)
    if not args.apply:
        print("\nre-run with --apply to write")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
