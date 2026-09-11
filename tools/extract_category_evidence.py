"""Извлечение доказательной базы Категорий 1/2 в структурированный JSON.

Читает production-БД напрямую (SQLAlchemy) и выгружает для каждого параметра
чек-листа `CATEGORY_VERIFICATION_PLAN.md`:
  * published claims с источником (code/title/url/source_type), basis,
    formula, input_parameters, locator;
  * игровые примеры (game_cases + case_evidence) с ролью direct/cross_engine.

Запуск из backend/ через .dss-venv:
    ../.dss-venv/Scripts/python.exe ../tools/extract_category_evidence.py
"""
from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, ".")

from sqlalchemy import select  # noqa: E402

from app.database import SessionLocal  # noqa: E402
from app.models.entities import (  # noqa: E402
    CaseEvidence,
    EvidenceClaim,
    EvidenceSource,
    GameCase,
)

OUT = Path("../research/_verify_cache/category_evidence.json")
OUT.parent.mkdir(parents=True, exist_ok=True)


def main() -> None:
    db = SessionLocal()

    # --- источники: id -> dict
    srcs = {s.id: s for s in db.scalars(select(EvidenceSource)).all()}

    def src_out(sid):
        s = srcs.get(sid)
        if not s:
            return None
        return {
            "code": s.code,
            "title": s.title,
            "url": s.url,
            "source_type": s.source_type,
            "locator": s.locator,
        }

    # --- published claims, группируем по entity
    claims = db.scalars(
        select(EvidenceClaim).where(EvidenceClaim.status == "published")
    ).all()
    by_entity: dict[str, list] = defaultdict(list)
    for c in claims:
        by_entity[c.entity].append(c)

    # --- game cases
    cases = {g.id: g for g in db.scalars(select(GameCase)).all()}
    cev = db.scalars(
        select(CaseEvidence).where(CaseEvidence.status == "published")
    ).all()
    # группируем case_evidence по method_code и function_code
    cev_by_method: dict[str, list] = defaultdict(list)
    cev_by_function: dict[str, list] = defaultdict(list)
    for e in cev:
        if e.method_code:
            cev_by_method[e.method_code].append(e)
        if e.function_code:
            cev_by_function[e.function_code].append(e)

    def cev_out(e):
        g = cases.get(e.case_id)
        return {
            "case": g.code if g else None,
            "title": g.title if g else None,
            "studio": g.studio if g else "",
            "year": g.release_year if g else None,
            "engine": g.engine_code if g else "",
            "match_level": e.match_level,
            "role": "direct" if e.match_level == "direct" else "cross_engine",
            "fact": e.fact,
            "locator": e.locator,
            "source": src_out(e.source_id),
        }

    def claim_out(c):
        return {
            "code": c.code,
            "entity": c.entity,
            "entity_code": c.entity_code,
            "field": c.field,
            "claim": c.claim,
            "basis": c.basis,
            "formula": c.formula,
            "input_parameters": c.input_parameters,
            "value_num": c.value_num,
            "value_text": c.value_text,
            "unit": c.unit,
            "locator": c.locator,
            "source": src_out(c.source_id),
        }

    # --- per-entity_code агрегаты для всех entity
    entity_codes: dict[str, dict[str, dict]] = {}
    for ent, cl in by_entity.items():
        per_code: dict[str, list] = defaultdict(list)
        for c in cl:
            per_code[c.entity_code].append(c)
        entity_codes[ent] = {
            code: [claim_out(c) for c in lst] for code, lst in per_code.items()
        }

    # --- game examples по method/function
    method_examples = {
        code: [cev_out(e) for e in lst] for code, lst in cev_by_method.items()
    }
    function_examples = {
        code: [cev_out(e) for e in lst] for code, lst in cev_by_function.items()
    }

    # --- сводки
    summary = {
        "claims_total": len(claims),
        "sources_published": sum(1 for s in srcs.values() if s.status == "published"),
        "claims_per_entity": {k: len(v) for k, v in by_entity.items()},
        "basis_counter": dict(Counter(c.basis for c in claims)),
        "source_type_counter": dict(
            Counter(s.source_type for s in srcs.values() if s.status == "published")
        ),
        "game_cases": len(cases),
        "case_evidence": len(cev),
    }

    payload = {
        "summary": summary,
        "entity_codes": entity_codes,
        "method_examples": method_examples,
        "function_examples": function_examples,
    }
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")

    # --- консольная сводка
    print("== SUMMARY ==")
    print(json.dumps(summary, ensure_ascii=False, indent=1))
    print("\n== entities ==")
    for ent in sorted(entity_codes):
        n_codes = len(entity_codes[ent])
        n_claims = sum(len(v) for v in entity_codes[ent].values())
        print(f"  {ent:20s} codes={n_codes:4d} claims={n_claims}")
    print("\nwritten:", OUT.resolve())


if __name__ == "__main__":
    main()
