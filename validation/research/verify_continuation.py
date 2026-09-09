"""Verify research coverage and preservation; never repair protected files."""
import hashlib
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
baseline = json.loads((ROOT / "validation/research/run-2026-09-08-02/baseline.json").read_text(encoding="utf-8"))
changed = []
for name, expected in baseline["sha256"].items():
    path = ROOT / name
    actual = hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None
    if actual != expected:
        changed.append({"path": name, "expected": expected, "actual": actual})
review = json.loads((ROOT / "validation/research/batch-01-review-2026-09-09.json").read_text(encoding="utf-8"))
rows = review["rows"]
assert len(rows) == len({r["row_id"] for r in rows}) == 92
assert sum(review["counts"].values()) == 92
assert all(not r["research_review_2026_09_09"]["numeric_calibration_eligible"] for r in rows)
index = json.loads((ROOT / "validation/research/continuation-index-2026-09-09.json").read_text(encoding="utf-8"))
assert len(index["links"]) == 473
assert sum(len(link["per_version_cases"]) for link in index["links"]) == 2162
assert index["source_heads"] == ["e103004d1fae"]
report = (ROOT / "docs/research/CONTINUATION-2026-09-09.md").read_text(encoding="utf-8")
definitions = set(re.findall(r"^\[\^(\d+)\]:", report, re.M))
references = set(re.findall(r"\[\^(\d+)\](?!:)", report))
assert references <= definitions
referenced_paths = set(re.findall(r"`((?:validation/research|docs/research)/[^`]+\.(?:json|py|cjs|md))`", report))
assert all((ROOT / name).is_file() for name in referenced_paths)
result = {"timestamp_utc": datetime.now(timezone.utc).isoformat(),
          "protected_files_checked": len(baseline["sha256"]), "protected_files_changed": changed,
          "head": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
          "git_status": subprocess.check_output(["git", "status", "--short"], cwd=ROOT, text=True),
          "research_checks": {"individual_semantic_reviews": len(rows), "numeric_eligible": 0,
                              "engine_links_indexed": 473, "potential_version_checks": 2162,
                              "referenced_artifacts_exist": True, "footnote_references_resolve": True},
          "live_database_opened": False, "application_tests_run": False,
          "application_fixes_made": False, "full_plan_complete": False}
with (ROOT / "validation/research/preservation-2026-09-09.json").open("x", encoding="utf-8") as output:
    json.dump(result, output, ensure_ascii=False, indent=2)
print(json.dumps(result, ensure_ascii=False))
assert not changed, "Protected files differ; record and investigate, do not overwrite"
