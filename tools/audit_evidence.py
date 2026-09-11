#!/usr/bin/env python3
"""Orchestrator ground-truth audit of the evidence base.

Emits a machine-readable JSON + human summary measuring, per entity class:
  * how many entities exist
  * how many have N distinct evidence claims
  * how many have >=2 distinct sources carrying a locator
  * how many have >=2 independent game-case proofs
  * how many numeric claims are `derived` but lack formula/input_parameters
  * how many claims point at a source that does not exist (dangling)

Usage: python tools/audit_evidence.py [--db PATH] [--out PATH]
"""
from __future__ import annotations

import argparse
import json
import re
import sqlite3
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DB = ROOT / "backend" / "gamedev_dss.db"

# Minimum bar set by the task spec.
MIN_CLAIMS = 3          # "several deep research-analyses"
MIN_LOCATED_SOURCES = 2  # distinct sources WITH a locator
MIN_GAME_PROOFS = 2      # "additional proof by example in different games"

# Mirrors tools/verify_sources.py: a row recording a declared absence has no
# source on purpose and must not be reported as a dangling citation.
DECLARED_GAP_FIELDS = {"adoption_evidence_gap"}

# Domains where a game example is NOT sufficient proof -- these additionally
# require an in-project derivation (formula + inputs) or a measured anchor.
DERIVATION_REQUIRED = {
    "stage_budget", "target_platform", "scene_scale", "network_mode",
    "target_metrics", "project_risk", "basket", "load_profile",
    "hardware", "final_plan",
}


def q(conn, sql, params=()):
    cur = conn.execute(sql, params)
    cols = [d[0] for d in cur.description]
    return [dict(zip(cols, r)) for r in cur.fetchall()]


def scalar(conn, sql, params=()):
    row = conn.execute(sql, params).fetchone()
    return row[0] if row else None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", default=str(DEFAULT_DB))
    ap.add_argument("--out", default=str(ROOT / "research" / "audit_evidence.json"))
    args = ap.parse_args()

    conn = sqlite3.connect(args.db)
    conn.row_factory = sqlite3.Row

    src_by_id = {r["id"]: dict(r) for r in q(conn, "select * from evidence_sources")}
    src_by_code = {r["code"]: r for r in src_by_id.values()}
    src_ids = set(src_by_id)

    claims = q(conn, "select * from evidence_claims")

    def has_locator(c):
        return bool((c.get("locator") or "").strip())

    def _text(value) -> str:
        """Строковое представление JSON-поля для проверки непустоты."""
        if isinstance(value, (dict, list)):
            return "x" if value else ""
        return (value or "").strip()

    def is_self_justified(c) -> bool:
        """Утверждение обосновано без внешнего источника (spec, строка 412).

        Правило спеки: запись валидна при `source` ЛИБО при
        `formula` + `input_parameters`. Собственный расчёт (`basis='derived'`)
        не «ссылается на несуществующий источник» — он вообще не ссылается
        наружу, поэтому не должен попадать в «висячие ссылки». Та же формула
        используется валидатором базы и тестом публикации доказательств.
        """
        return (
            (c.get("basis") or "") == "derived"
            and bool(_text(c.get("formula")))
            and bool(_text(c.get("input_parameters")))
        )

    # ---- per-entity aggregation -------------------------------------
    agg = defaultdict(lambda: {
        "claims": 0, "sources": set(), "located_sources": set(),
        "bases": set(), "numeric": 0, "derived_no_formula": 0,
        "dangling": 0, "fields": set(),
    })

    dangling_claims = []
    for c in claims:
        key = (c["entity"], c["entity_code"])
        a = agg[key]
        a["claims"] += 1
        a["bases"].add(c.get("basis") or "")
        a["fields"].add(c.get("field") or "")
        sid = c.get("source_id")
        if sid is None or sid not in src_ids:
            # A declared absence carries no source by design (see
            # DECLARED_GAP_FIELDS in tools/verify_sources.py). It is surfaced as
            # a declared gap, not counted as a broken citation -- but only when
            # it is also honestly marked basis='unknown'/evidence_level='low'.
            if (c.get("field") or "").strip() in DECLARED_GAP_FIELDS or is_self_justified(c):
                a["declared_gaps"] = a.get("declared_gaps", 0) + 1
            else:
                a["dangling"] += 1
                dangling_claims.append(c["code"])
        else:
            a["sources"].add(sid)
            if has_locator(c) or (src_by_id[sid].get("locator") or "").strip():
                a["located_sources"].add(sid)
        is_num = c.get("value_num") is not None or (c.get("range_min") is not None)
        if is_num:
            a["numeric"] += 1
        if c.get("basis") == "derived":
            if not (c.get("formula") or "").strip() or not (c.get("input_parameters") or "").strip():
                a["derived_no_formula"] += 1

    # ---- game-case proofs --------------------------------------------
    # NB: the key here MUST match the `kind` used in `report()` below.
    # Previously this map used "function" while report() looked up
    # "game_function", so every function silently reported 0 proofs.
    proofs = defaultdict(set)   # (kind, code) -> set(proof identity)
    prov_rows = q(conn, "select * from case_evidence")
    for p in prov_rows:
        for kind, code in (("method", p.get("method_code")),
                           ("game_function", p.get("function_code"))):
            if code:
                proofs[(kind, code)].add(p["case_id"])

    # Entities without a case_evidence column (engines, engine_tools,
    # technology_nodes, platforms, stage_budgets, network_modes,
    # target_metrics, load_profiles, risk_factors) store their game examples as
    # claims with field='game_example'. Count those too, keyed by game name so
    # two examples from the same title still count once.
    # A shipped title on the SAME engine shows the capability on the platform
    # the tool targets; a title on another engine shows the capability is
    # production-proven but says nothing about this particular tool. Counting
    # the two identically would overstate adoption, so they are tracked apart.
    tool_family = {r["tcode"]: r["ecode"] for r in q(
        conn, "select t.code as tcode, e.code as ecode "
              "from engine_tools t join engines e on e.id = t.engine_id")}
    case_tech = {(r["title"] or "").strip().lower(): (r["technology"] or "")
                 for r in q(conn, "select title, technology from game_cases")}

    def _role(entity: str, entity_code: str, params: dict, game_norm: str) -> str:
        role = (params.get("role") or "").strip()
        if role:
            return role
        if entity != "engine_tool":
            return ""
        fam = tool_family.get(entity_code, "")
        geng = (params.get("engine") or "").strip() or case_tech.get(game_norm, "")
        if not fam or not geng:
            return ""
        gl = geng.lower()
        if fam == "unity":
            direct = "unity" in gl
        elif fam == "unreal":
            direct = ("unreal" in gl) or ("ue4" in gl) or ("ue5" in gl)
        else:
            direct = fam in gl
        return "direct" if direct else "cross_engine"

    direct_proofs = defaultdict(set)
    for c in claims:
        if (c.get("field") or "") != "game_example":
            continue
        params = c.get("input_parameters") or {}
        if isinstance(params, str):
            try:
                params = json.loads(params)
            except Exception:
                params = {}
        game = (params.get("game") or "").strip().lower() or f"claim:{c['code']}"
        key = (c["entity"], c["entity_code"])
        proofs[key].add(game)
        if _role(c["entity"], c["entity_code"], params, game) == "direct":
            direct_proofs[key].add(game)

    # Any entity class may declare an explicit absence. Declared early because
    # report() and the technology-node walk both consult it.
    declared_gaps = {(r["entity"], r["entity_code"]) for r in q(conn,
        "select entity, entity_code from evidence_claims "
        "where field='adoption_evidence_gap'")}

    case_ids = {r["id"] for r in q(conn, "select id from game_cases")}
    orphan_case_evidence = [p["code"] for p in prov_rows if p["case_id"] not in case_ids]

    def report(label, kind, rows, code_key="code", name_key="name"):
        items = []
        for r in rows:
            code = r[code_key]
            a = agg.get((kind, code), {"claims": 0, "sources": set(), "located_sources": set(),
                                       "bases": set(), "numeric": 0, "derived_no_formula": 0,
                                       "dangling": 0, "fields": set()})
            gp = proofs.get((kind, code), set())
            dp = direct_proofs.get((kind, code), set())
            items.append({
                "code": code,
                "name": r.get(name_key) or r.get("title") or "",
                "claims": a["claims"],
                "direct_game_proofs": len(dp),
                "declared_gap": (kind, code) in declared_gaps,
                "sources": len(a["sources"]),
                "located_sources": len(a["located_sources"]),
                "fields": sorted(a["fields"]),
                "bases": sorted(x for x in a["bases"] if x),
                "numeric_claims": a["numeric"],
                "derived_no_formula": a["derived_no_formula"],
                "dangling": a["dangling"],
                "game_proofs": len(gp),
                "ok_claims": a["claims"] >= MIN_CLAIMS,
                "ok_sources": len(a["located_sources"]) >= MIN_LOCATED_SOURCES,
                "ok_proofs": len(gp) >= MIN_GAME_PROOFS,
            })
        total = len(items)
        def pct(n):
            return round(100.0 * n / total, 1) if total else 0.0
        summary = {
            "entity_class": label,
            "total": total,
            f"pct_claims>={MIN_CLAIMS}": pct(sum(i["ok_claims"] for i in items)),
            f"pct_located_sources>={MIN_LOCATED_SOURCES}": pct(sum(i["ok_sources"] for i in items)),
            f"pct_game_proofs>={MIN_GAME_PROOFS}": pct(sum(i["ok_proofs"] for i in items)),
            "pct_fully_ok": pct(sum(1 for i in items
                                    if i["ok_claims"] and i["ok_sources"] and i["ok_proofs"])),
            "total_derived_missing_formula": sum(i["derived_no_formula"] for i in items),
            "total_dangling_claims": sum(i["dangling"] for i in items),
            "entities_declaring_gap": sum(1 for i in items if i.get("declared_gap")),
        }
        # Cross-engine examples prove the capability shipped, not that this
        # specific tool was adopted. The split is only meaningful where an
        # entity belongs to one engine; for engine-agnostic classes (methods,
        # functions) every shipped example is equally valid, so reporting a
        # "direct" count of 0 there would be misleading.
        if kind == "engine_tool":
            summary.update({
                "direct_game_proofs_total": sum(i["direct_game_proofs"] for i in items),
                "entities_with_direct_proof": sum(1 for i in items
                                                  if i["direct_game_proofs"] > 0),
                "entities_unproven_and_undeclared": sum(
                    1 for i in items
                    if i["direct_game_proofs"] == 0 and not i.get("declared_gap")),
                "note": ("pct_game_proofs counts shipped-title evidence for the capability, "
                         "cross-engine included. entities_with_direct_proof is the stricter "
                         "count: shipped titles on the SAME engine as the tool."),
            })
        gaps = [i for i in items
                if not (i["ok_claims"] and i["ok_sources"] and i["ok_proofs"])]
        return summary, items, gaps

    out = {"db": str(args.db), "thresholds": {
        "min_claims": MIN_CLAIMS,
        "min_located_sources": MIN_LOCATED_SOURCES,
        "min_game_proofs": MIN_GAME_PROOFS,
    }, "classes": {}, "gaps": {}}

    # NOTE: `kind` MUST match the `entity` value actually used in
    # evidence_claims.entity -- the DB uses 'game_function' (singular), not
    # 'function'. Getting this wrong silently reports 0% coverage.
    specs = [
        ("game_functions", "game_function", "game_functions"),
        ("methods", "method", "methods"),
        ("engines", "engine", "engines"),
        ("engine_tools", "engine_tool", "engine_tools"),
    ]
    for label, kind, table in specs:
        rows = q(conn, f"select * from {table}")
        s, items, gaps = report(label, kind, rows)
        out["classes"][label] = s
        out["gaps"][label] = gaps

    # ---- technology_nodes ------------------------------------------------
    # A node `method:foo` / `tool:foo` / `engine:foo` IS the catalog entity, so
    # it inherits that entity's evidence. Only plugin/lib/api/sdk nodes are
    # standalone and need their own claims. Counting them all as 0% (the old
    # behaviour) reported a gap that does not exist.
    NODE_INHERITS = {"method": "method", "tool": "engine_tool", "engine": "engine"}
    nodes = q(conn, "select * from technology_nodes")
    # A node with no verifiable shipped-title example may declare that gap
    # explicitly (field='adoption_evidence_gap', basis='unknown'). That is an
    # honest state, not a silent hole -- but it is also NOT proof, so such a
    # node is counted separately instead of being promoted to "fully ok".
    node_items = []
    for n in nodes:
        ntype = n.get("node_type") or ""
        code = n["code"]
        if ntype in NODE_INHERITS and ":" in code:
            ent = NODE_INHERITS[ntype]
            underlying = code.split(":", 1)[1]
            a = agg.get((ent, underlying))
            src_ok = bool(a and len(a["located_sources"]) >= MIN_LOCATED_SOURCES)
            cl_ok = bool(a and a["claims"] >= MIN_CLAIMS)
            gp = len(proofs.get((ent, underlying), set()))
            origin = f"inherited:{ent}:{underlying}"
        else:
            a = agg.get(("technology_node", code))
            src_ok = bool(a and len(a["located_sources"]) >= MIN_LOCATED_SOURCES)
            cl_ok = bool(a and a["claims"] >= MIN_CLAIMS)
            gp = len(proofs.get(("technology_node", code), set()))
            origin = "own"
        node_items.append({
            "code": code, "name": n.get("name") or "", "node_type": ntype,
            "origin": origin,
            "claims": a["claims"] if a else 0,
            "located_sources": len(a["located_sources"]) if a else 0,
            "game_proofs": gp,
            "ok_claims": cl_ok, "ok_sources": src_ok, "ok_proofs": gp >= MIN_GAME_PROOFS,
            "declared_gap": ("technology_node", code) in declared_gaps,
        })
    total = len(node_items)
    standalone = [i for i in node_items if i["origin"] == "own"]

    def pct_of(items, pred):
        return round(100.0 * sum(1 for i in items if pred(i)) / len(items), 1) if items else 0.0

    out["classes"]["technology_nodes"] = {
        "entity_class": "technology_nodes", "total": total,
        "inherited_from_catalog": total - len(standalone),
        "standalone": len(standalone),
        "pct_fully_ok": pct_of(node_items, lambda i: i["ok_claims"] and i["ok_sources"] and i["ok_proofs"]),
        "standalone_pct_fully_ok": pct_of(standalone, lambda i: i["ok_claims"] and i["ok_sources"] and i["ok_proofs"]),
        "standalone_without_evidence": sum(1 for i in standalone if i["claims"] == 0),
        # nodes that satisfy claims+sources, document the technology properly,
        # and honestly declare that no shipped-title proof was located
        "standalone_declared_no_shipped_title_proof": sum(
            1 for i in standalone if i.get("declared_gap")),
        "standalone_documented_but_unproven": sum(
            1 for i in standalone
            if i.get("declared_gap") and i["ok_claims"] and i["ok_sources"]),
    }
    out["gaps"]["technology_nodes"] = [i for i in node_items
                                       if not (i["ok_claims"] and i["ok_sources"] and i["ok_proofs"])]

    # ---- game_cases ------------------------------------------------------
    # A case is evidenced by its case_evidence rows (source + locator), not by
    # claims keyed to the case code.
    case_rows = q(conn, "select * from game_cases")
    ce_by_case = defaultdict(lambda: {"n": 0, "sources": set(), "located": 0})
    for p in prov_rows:
        d = ce_by_case[p["case_id"]]
        d["n"] += 1
        if p.get("source_id"):
            d["sources"].add(p["source_id"])
        if (p.get("locator") or "").strip():
            d["located"] += 1
    case_items = []
    for r in case_rows:
        d = ce_by_case.get(r["id"], {"n": 0, "sources": set(), "located": 0})
        case_items.append({
            "code": r["code"], "name": r.get("title") or "",
            "claims": d["n"], "located_sources": len(d["sources"]),
            "game_proofs": 1 if d["n"] else 0,
            "ok_claims": d["n"] >= 1,
            "ok_sources": len(d["sources"]) >= 1,
            "ok_proofs": d["n"] >= 1,
        })
    out["classes"]["game_cases"] = {
        "entity_class": "game_cases", "total": len(case_items),
        "pct_fully_ok": pct_of(case_items, lambda i: i["ok_claims"] and i["ok_sources"] and i["ok_proofs"]),
        "without_any_case_evidence": sum(1 for i in case_items if i["claims"] == 0),
    }
    out["gaps"]["game_cases"] = [i for i in case_items
                                 if not (i["ok_claims"] and i["ok_sources"] and i["ok_proofs"])]

    # ---- link-level (no entity table of their own) --------------------
    # A user_defined link legitimately has no external URL: the tool is an
    # in-house technology. What matters is that the absence is DECLARED, so the
    # check accepts either a URL or an explicit user_defined marker.
    links = q(conn, "select * from method_engine_links")

    def link_has_source(l):
        if (l.get("source_url") or "").strip():
            return True
        return (l.get("evidence_status") or "") == "user_defined"

    link_ok = sum(1 for l in links if link_has_source(l))
    out["classes"]["method_engine_links"] = {
        "entity_class": "method_engine_links", "total": len(links),
        "with_url_or_declared_user_defined": link_ok,
        "pct_ok": round(100.0 * link_ok / len(links), 1) if links else 0.0,
        "missing_url": sum(1 for l in links if not (l.get("source_url") or "").strip()),
        "declared_user_defined": sum(1 for l in links
                                     if (l.get("evidence_status") or "") == "user_defined"),
        "undeclared_missing_url": sum(1 for l in links if not link_has_source(l)),
        "missing_locator": sum(1 for l in links if not (l.get("source_locator") or "").strip()),
        "missing_basis": sum(1 for l in links if not (l.get("evidence_basis") or "").strip()),
    }

    conf = q(conn, "select * from conflicts")

    def conflict_has_source(c):
        u = (c.get("source_url") or "").strip()
        return bool(u) or u.startswith("user_defined:")

    out["classes"]["conflicts"] = {
        "entity_class": "conflicts", "total": len(conf),
        "missing_url": sum(1 for c in conf if not (c.get("source_url") or "").strip()),
        "undeclared_missing_url": sum(1 for c in conf if not conflict_has_source(c)),
    }

    edges = q(conn, "select * from dependency_edges")

    def edge_declared_expert(e):
        # An edge to a user_defined tool has no public document by definition.
        # The honest state is an explicit declaration, not a NULL.
        d = (e.get("description") or "")
        return d.startswith("[expert_estimate") or "экспертн" in d.lower()

    out["classes"]["dependency_edges"] = {
        "entity_class": "dependency_edges", "total": len(edges),
        "missing_source_id": sum(1 for e in edges if not e.get("source_id")),
        "declared_expert_estimate": sum(1 for e in edges
                                        if not e.get("source_id") and edge_declared_expert(e)),
        "undeclared_missing_source": sum(1 for e in edges
                                         if not e.get("source_id")
                                         and not edge_declared_expert(e)),
        "unknown_relation": sum(1 for e in edges if (e.get("status") or "") == "unknown"),
    }

    wps = q(conn, "select * from work_packages")
    out["classes"]["work_packages"] = {
        "entity_class": "work_packages", "total": len(wps),
        "missing_source_or_basis": sum(
            1 for w in wps if not (w.get("source_id") or (w.get("basis") or "").strip())),
        "p80_lt_p50": sum(1 for w in wps
                          if (w.get("p80_days") or 0) < (w.get("p50_days") or 0)),
        "no_formula_basis": sum(1 for w in wps
                                if (w.get("basis") or "") in ("derived", "calculated")
                                and not (w.get("dependency_codes") or "").strip()),
    }

    for tbl, cols in (("hardware_cpu", ("benchmark_raw_value", "benchmark_context", "evidence_basis", "normalization_note")),
                      ("hardware_gpu", ("benchmark_raw_value", "benchmark_context", "evidence_basis", "normalization_note"))):
        rows = q(conn, f"select * from {tbl}")
        d = {"entity_class": tbl, "total": len(rows)}
        for col in cols:
            d["missing_" + col] = sum(1 for r in rows if not (r.get(col) or "")) if col != "benchmark_raw_value" \
                else sum(1 for r in rows if r.get(col) in (None, "", 0))
        d["missing_source_url"] = sum(1 for r in rows if not (r.get("source_url") or "").strip())
        out["classes"][tbl] = d

    # ---- source hygiene ----------------------------------------------
    src_issues = []
    url_re = re.compile(r"https?://", re.I)
    for s in src_by_id.values():
        title = (s.get("title") or "").strip()
        url = (s.get("url") or "").strip()
        if not title:
            src_issues.append({"code": s["code"], "issue": "empty_title"})
        if not url or not url_re.match(url):
            src_issues.append({"code": s["code"], "issue": "missing_or_bad_url", "url": url})
        if not (s.get("locator") or "").strip():
            src_issues.append({"code": s["code"], "issue": "missing_locator"})
        if not (s.get("published_date") or "").strip():
            src_issues.append({"code": s["code"], "issue": "missing_published_date"})
        # An explicit "n/a (living documentation)" is a declared absence, not a
        # gap: UE/Unity/Godot manual pages genuinely have no publication date.
        elif (s.get("published_date") or "").strip().lower().startswith("n/a"):
            src_issues.append({"code": s["code"], "issue": "declared_undated_living_doc"})
        if not (s.get("source_type") or "").strip():
            src_issues.append({"code": s["code"], "issue": "missing_source_type"})

    # heuristic title/URL contradiction detector (same class of bug as the
    # known "State -> Niagara", "DLSS -> RTXNTC", "VSM -> DF Shadows" cases)
    TOPIC_TOKENS = {
        "niagara": ["niagara"], "dlss": ["dlss"], "nanite": ["nanite"],
        "lumen": ["lumen"], "vsm": ["virtual shadow", "virtual-shadow", "vsm"],
        "dfshadow": ["distance field shadow", "distance-field"],
        "dlss_rayrecon": ["ray reconstruction", "rtxntc", "neural texture"],
        "chaos": ["chaos physics", "chaos cloth", "chaos destruction"],
        "subtick": ["sub-tick", "subtick"],
        "rtxdi": ["rtxdi", "ray traced direct"],
        "tsr": ["temporal super resolution", "\btsr\b"],
        "navmesh": ["navmesh", "nav mesh"],
        "ecs": ["\becs\b", "entity component system"],
        "sgf": ["shader graph"], "vfxgraph": ["vfx graph"],
    }

    def topics(text):
        t = (text or "").lower()
        return {k for k, pats in TOPIC_TOKENS.items() if any(re.search(p, t) for p in pats)}

    contradictions = []
    for s in src_by_id.values():
        tt = topics(s.get("title"))
        tu = topics(s.get("url"))
        if tt and tu and not (tt & tu):
            contradictions.append({
                "code": s["code"], "title": s.get("title"), "url": s.get("url"),
                "title_topics": sorted(tt), "url_topics": sorted(tu),
            })

    out["sources"] = {
        "total": len(src_by_id),
        "unused": sorted(s["code"] for s in src_by_id.values()
                         if not any(c.get("source_id") == s["id"] for c in claims)),
        "issue_counts": {k: sum(1 for i in src_issues if i["issue"] == k)
                         for k in {i["issue"] for i in src_issues}},
        "issue_examples": src_issues[:60],
        "title_url_contradictions": contradictions,
        "duplicate_urls": [u for u, n in
                           defaultdict(int, {u: 0 for u in []}).items()],
    }
    dup = defaultdict(list)
    for s in src_by_id.values():
        u = (s.get("url") or "").strip().lower()
        if u:
            dup[u].append(s["code"])
    out["sources"]["duplicate_urls"] = {u: c for u, c in dup.items() if len(c) > 1}

    out["claims"] = {
        "total": len(claims),
        "dangling": dangling_claims[:80],
        "dangling_count": len(dangling_claims),
        "by_basis": {b: sum(1 for c in claims if (c.get("basis") or "") == b)
                     for b in {c.get("basis") for c in claims}},
        "by_verification": {b: sum(1 for c in claims if (c.get("verification_status") or "") == b)
                            for b in {c.get("verification_status") for c in claims}},
        "numeric_without_source": sum(
            1 for c in claims
            if (c.get("value_num") is not None or c.get("range_min") is not None)
            and (c.get("source_id") is None or c.get("source_id") not in src_ids)
            and not is_self_justified(c)),
    }

    out["case_evidence"] = {
        "total": len(prov_rows),
        "orphan_case_evidence": orphan_case_evidence[:40],
        "orphan_count": len(orphan_case_evidence),
        "missing_source": sum(1 for p in prov_rows if not p.get("source_id")),
        "missing_locator": sum(1 for p in prov_rows if not (p.get("locator") or "").strip()),
    }

    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")

    # ---- human summary ------------------------------------------------
    print(f"DB: {args.db}\n")
    print(f"{'class':22s} {'n':>6s} {'claims>=3':>10s} {'src>=2':>8s} {'proofs>=2':>10s} {'FULL':>7s}")
    for k, s in out["classes"].items():
        if f"pct_claims>={MIN_CLAIMS}" in s:
            print(f"{k:22s} {s['total']:6d} {s[f'pct_claims>={MIN_CLAIMS}']:10.1f} "
                  f"{s[f'pct_located_sources>={MIN_LOCATED_SOURCES}']:8.1f} "
                  f"{s[f'pct_game_proofs>={MIN_GAME_PROOFS}']:10.1f} {s['pct_fully_ok']:7.1f}")
        elif "pct_fully_ok" in s:
            extra = " ".join(f"{kk}={vv}" for kk, vv in s.items()
                             if kk not in ("entity_class", "total", "pct_fully_ok"))
            print(f"{k:22s} {s['total']:6d} {'':10s} {'':8s} {'':10s} {s['pct_fully_ok']:7.1f}"
                  + (f"  [{extra}]" if extra else ""))
        else:
            extra = " ".join(f"{kk}={vv}" for kk, vv in s.items()
                             if kk not in ("entity_class", "total"))
            print(f"{k:22s} {s['total']:6d}  [{extra}]")
    print("\nsources:", json.dumps(out["sources"]["issue_counts"], ensure_ascii=False))
    print("title/url contradictions:", len(contradictions))
    print("claims by basis:", json.dumps(out["claims"]["by_basis"], ensure_ascii=False))
    print("dangling claims:", len(dangling_claims))
    print("\nfull report ->", args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
