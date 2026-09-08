"""Offline comparison in independent performance units. Never imported by runtime.

CLI: python validation/evaluate.py references.json baseline.json candidate.json report.json
Empty/ineligible coverage is a result, never a successful accuracy claim.
"""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from statistics import mean, median
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class Reference(BaseModel):
    model_config = ConfigDict(extra="forbid")
    case_id: str
    game_group: str
    split: Literal["train", "validation", "test"]
    kind: Literal["point", "interval", "sufficient", "ineligible"]
    scale_id: str | None = None
    source: str | None = None
    exclusion_reason: str | None = None
    cpu_lower: float | None = Field(default=None, gt=0, allow_inf_nan=False)
    cpu_upper: float | None = Field(default=None, gt=0, allow_inf_nan=False)
    gpu_lower: float | None = Field(default=None, gt=0, allow_inf_nan=False)
    gpu_upper: float | None = Field(default=None, gt=0, allow_inf_nan=False)

    @model_validator(mode="after")
    def reference_contract(self):
        if self.kind == "ineligible":
            if not self.exclusion_reason:
                raise ValueError("Excluded reference must explain why")
            return self
        if not self.scale_id or not self.source:
            raise ValueError("Independent performance scale and source required")
        for component in ("cpu", "gpu"):
            lower, upper = getattr(self, component + "_lower"), getattr(self, component + "_upper")
            if upper is None or (self.kind != "sufficient" and lower is None):
                raise ValueError("Missing reference bounds")
            if lower is not None and lower > upper:
                raise ValueError("Reversed reference bounds")
            if self.kind == "point" and lower != upper:
                raise ValueError("Point reference requires identical bounds")
            if self.kind == "sufficient" and lower is not None:
                raise ValueError("Sufficient hardware does not establish a lower bound")
        return self


class Prediction(BaseModel):
    model_config = ConfigDict(extra="forbid")
    case_id: str
    scale_id: str
    cpu: float = Field(gt=0, allow_inf_nan=False)
    gpu: float = Field(gt=0, allow_inf_nan=False)
    compatible: bool | None = None
    memory_sufficient: bool | None = None
    cpu_range: tuple[float, float] | None = None
    gpu_range: tuple[float, float] | None = None

    @model_validator(mode="after")
    def valid_ranges(self):
        import math
        for component in ("cpu", "gpu"):
            bounds = getattr(self, component + "_range")
            if bounds and (not all(math.isfinite(value) and value > 0 for value in bounds)
                           or not bounds[0] <= getattr(self, component) <= bounds[1]):
                raise ValueError("Prediction must lie inside finite positive range")
        return self


def _unique(rows):
    mapping = {row.case_id: row for row in rows}
    if len(mapping) != len(rows):
        raise ValueError("Duplicate scenario identifier")
    return mapping


def compare(references: list[Reference], baseline: list[Prediction], candidate: list[Prediction]) -> dict:
    refs, before, after = _unique(references), _unique(baseline), _unique(candidate)
    if (before.keys() | after.keys()) - refs.keys():
        raise ValueError("Prediction without reference scenario")
    splits = {}
    for reference in references:
        old = splits.setdefault(reference.game_group, reference.split)
        if old != reference.split:
            raise ValueError("Related scenarios leak across partitions")
    rows = []
    for reference in references:
        row = {"case_id": reference.case_id, "game_group": reference.game_group,
               "split": reference.split, "reference_kind": reference.kind}
        reason = reference.exclusion_reason if reference.kind == "ineligible" else None
        if not reason and (reference.case_id not in before or reference.case_id not in after):
            reason = "Missing baseline or candidate prediction; excluded from paired comparison"
        if not reason and any(pred.scale_id != reference.scale_id for pred in
                              (before[reference.case_id], after[reference.case_id])):
            reason = "Prediction and independent reference use different performance scales"
        if reason:
            row.update(status="unevaluated", reason=reason)
        else:
            row["status"] = "evaluated"
            for name, predictions in (("baseline", before), ("candidate", after)):
                prediction = predictions[reference.case_id]
                metrics = {"compatible": prediction.compatible, "memory_sufficient": prediction.memory_sufficient}
                for component in ("cpu", "gpu"):
                    value = getattr(prediction, component)
                    lower, upper = getattr(reference, component + "_lower"), getattr(reference, component + "_upper")
                    signed = ((value - lower) / lower if lower is not None and value < lower
                              else (value - upper) / upper if value > upper else 0.0)
                    metrics[component + "_relative_deviation"] = signed
                    bounds = getattr(prediction, component + "_range")
                    metrics[component + "_range_width"] = bounds[1] - bounds[0] if bounds else None
                metrics["joint_within_70"] = all(abs(metrics[c + "_relative_deviation"]) <= .7 for c in ("cpu", "gpu"))
                row[name] = metrics
        rows.append(row)
    summaries = {}
    for split in ("train", "validation", "test"):
        for kind in ("point", "interval", "sufficient"):
            selected = [row for row in rows if row["status"] == "evaluated" and row["split"] == split and row["reference_kind"] == kind]
            if not selected:
                continue
            summary = {}
            for version in ("baseline", "candidate"):
                per_game = defaultdict(list)
                for row in selected:
                    per_game[row["game_group"]].append(row[version])
                metrics = {"games": len(per_game), "scenarios": len(selected)}
                for component in ("cpu", "gpu"):
                    errors = sorted(mean(abs(row[component + "_relative_deviation"]) for row in game) for game in per_game.values())
                    # Linear empirical quantile, including one-game sets.
                    position = (len(errors) - 1) * .9
                    index = int(position)
                    metrics[component] = {"median": median(errors),
                        "p90": errors[index] + (errors[min(index + 1, len(errors) - 1)] - errors[index]) * (position - index),
                        "signed_mean": mean(mean(row[component + "_relative_deviation"] for row in game) for game in per_game.values())}
                metrics["joint_within_70"] = mean(mean(row["joint_within_70"] for row in game) for game in per_game.values())
                summary[version] = metrics
            summaries[f"{split}/{kind}"] = summary
    return {"protocol_version": 1, "tolerance": .7,
            "note": "Point error, interval deviation and one-sided sufficient-hardware violations are separate; none establishes FPS accuracy by itself.",
            "coverage": {"total": len(rows), "paired_evaluated": sum(row["status"] == "evaluated" for row in rows),
                         "unevaluated": sum(row["status"] != "evaluated" for row in rows)},
            "summaries": summaries, "cases": rows}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("references", "baseline", "candidate", "output"):
        parser.add_argument(name, type=Path)
    args = parser.parse_args()
    read = lambda path: json.loads(path.read_text(encoding="utf-8-sig"))
    report = compare([Reference.model_validate(row) for row in read(args.references)],
                     [Prediction.model_validate(row) for row in read(args.baseline)],
                     [Prediction.model_validate(row) for row in read(args.candidate)])
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
