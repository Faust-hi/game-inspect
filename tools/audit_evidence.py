#!/usr/bin/env python3
"""Orchestrator ground-truth audit of the evidence base.

Emits a machine-readable JSON + human summary measuring, per entity class:
  * how many entities exist
  * how many have N distinct evidence claims
  * how many have >=2 distinct sources carrying a locator
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

# Mirrors tools/verify_sources.py: a row recording a declared absence has no
# source on purpose and must not be reported as a dangling citation.
DECLARED_GAP_FIELDS = {"adoption_evidence_gap"}


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
    src_ids = set(src_by_id)

    claims = q(conn, "select * from evidence_claims")

    def has_locator(c):
        return bool((c.get("locator") or "").strip())

    def _text(value) -> str:
        """Строковое представление JSON-поля для проверки непустоты."""
        if isinstance(value, (dict, list)):
            return "x" if value else ""
        return (value or "").strip()

    def _json_len(value) -> int:
        """Длина JSON-списка, хранимого как TEXT; 0 для NULL, `[]` и битого JSON.

        Поля `implementation_variants` и `requires_conditions` лежат в SQLite
        строкой. Строка `'[]'` непустая, поэтому проверка «есть ли данные» по
        `_text` дала бы ложное «заполнено» — список разбирается явно.
        """
        if value is None:
            return 0
        if isinstance(value, list):
            return len(value)
        text = str(value).strip()
        if not text:
            return 0
        try:
            parsed = json.loads(text)
        except (TypeError, ValueError):
            return 0
        return len(parsed) if isinstance(parsed, list) else 0

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

    # Any entity class may declare an explicit absence. Declared early because
    # report() and the technology-node walk both consult it.
    declared_gaps = {(r["entity"], r["entity_code"]) for r in q(conn,
        "select entity, entity_code from evidence_claims "
        "where field='adoption_evidence_gap'")}

    def report(label, kind, rows, code_key="code", name_key="name"):
        items = []
        for r in rows:
            code = r[code_key]
            a = agg.get((kind, code), {"claims": 0, "sources": set(), "located_sources": set(),
                                       "bases": set(), "numeric": 0, "derived_no_formula": 0,
                                       "dangling": 0, "fields": set()})
            items.append({
                "code": code,
                "name": r.get(name_key) or r.get("title") or "",
                "claims": a["claims"],
                "declared_gap": (kind, code) in declared_gaps,
                "sources": len(a["sources"]),
                "located_sources": len(a["located_sources"]),
                "fields": sorted(a["fields"]),
                "bases": sorted(x for x in a["bases"] if x),
                "numeric_claims": a["numeric"],
                "derived_no_formula": a["derived_no_formula"],
                "dangling": a["dangling"],
                "ok_claims": a["claims"] >= MIN_CLAIMS,
                "ok_sources": len(a["located_sources"]) >= MIN_LOCATED_SOURCES,
            })
        total = len(items)
        def pct(n):
            return round(100.0 * n / total, 1) if total else 0.0
        summary = {
            "entity_class": label,
            "total": total,
            f"pct_claims>={MIN_CLAIMS}": pct(sum(i["ok_claims"] for i in items)),
            f"pct_located_sources>={MIN_LOCATED_SOURCES}": pct(sum(i["ok_sources"] for i in items)),
            "pct_fully_ok": pct(sum(1 for i in items
                                    if i["ok_claims"] and i["ok_sources"])),
            "total_derived_missing_formula": sum(i["derived_no_formula"] for i in items),
            "total_dangling_claims": sum(i["dangling"] for i in items),
            "entities_declaring_gap": sum(1 for i in items if i.get("declared_gap")),
        }
        gaps = [i for i in items
                if not (i["ok_claims"] and i["ok_sources"])]
        return summary, items, gaps

    out = {"db": str(args.db), "thresholds": {
        "min_claims": MIN_CLAIMS,
        "min_located_sources": MIN_LOCATED_SOURCES,
    }, "classes": {}, "gaps": {}}

    # ---- publication visibility -----------------------------------------
    # The class checks below read whole tables and measure CONTENT
    # completeness. They are blind to whether a row is published, while the
    # public API filters on status (`repositories._published`). A row that is
    # complete but draft is invisible and the audit stays green: 147 of 155
    # rows of one seeded class were drafts, so the practice cross-check came
    # back empty. Visibility is therefore measured as its own class.
    #
    # A draft is a DECLARED state for `evidence_claims`: a claim without a
    # source stays draft on purpose (declared gap), so it is not a gap here.
    DECLARED_DRAFT_TABLES = {"evidence_claims"}
    #
    # Row-level declarations: the invisibility of these rows is a DECISION with a
    # recorded reason, not an unexplained hole.
    #
    # This registry is empty as of 2026-09-11. It used to declare a second
    # family of derived rows (`WP_*`, 992 rows: curated effort split evenly
    # across eight phases). That family and the derived-effort subsystem were
    # removed in the 2026-09-12 backend cut, so there is nothing left to
    # declare.
    DECLARED_DRAFT_ROWS: dict[str, tuple[str, str]] = {}
    visibility: dict[str, dict] = {}
    for row in q(conn, "select name from sqlite_master where type='table' order by name"):
        name = row["name"]
        if name.startswith("sqlite_"):
            continue
        columns = {c["name"] for c in q(conn, f"pragma table_info({name})")}
        if "status" not in columns:
            continue
        total = scalar(conn, f"select count(*) from {name}") or 0
        published = scalar(conn, f"select count(*) from {name} where status='published'") or 0
        declared_draft = name in DECLARED_DRAFT_TABLES
        declared_rows = 0
        declaration = ""
        if declared_draft:
            # Table-level: every draft row of this table is a declared state.
            declared_rows = total - published
            declaration = ("a claim without a source stays draft on purpose "
                           "(declared gap), so draft is the declared state here")
        else:
            rule = DECLARED_DRAFT_ROWS.get(name)
            if rule:
                declared_rows = scalar(
                    conn,
                    f"select count(*) from {name} where status<>'published' and {rule[0]}",
                ) or 0
                declaration = rule[1]
        undeclared = total - published - declared_rows
        visibility[name] = {
            "total": total,
            "published": published,
            "invisible": total - published,
            "declared_invisible": declared_rows,
            "undeclared_invisible": undeclared,
            "declared_draft": declared_draft,
            "declaration": declaration,
            "ok": undeclared <= 0,
        }
    out["visibility"] = {
        "tables": visibility,
        "invisible_tables": sorted(k for k, v in visibility.items() if not v["ok"]),
        "invisible_rows": sum(v["invisible"] for v in visibility.values() if not v["ok"]),
        "declared_invisible_rows": sum(v["declared_invisible"] for v in visibility.values()),
    }

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
    # A node with no external evidence may declare that gap explicitly
    # (field='adoption_evidence_gap', basis='unknown'). That is an honest state,
    # not a silent hole.
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
            origin = f"inherited:{ent}:{underlying}"
        else:
            a = agg.get(("technology_node", code))
            src_ok = bool(a and len(a["located_sources"]) >= MIN_LOCATED_SOURCES)
            cl_ok = bool(a and a["claims"] >= MIN_CLAIMS)
            origin = "own"
        node_items.append({
            "code": code, "name": n.get("name") or "", "node_type": ntype,
            "origin": origin,
            "claims": a["claims"] if a else 0,
            "located_sources": len(a["located_sources"]) if a else 0,
            "ok_claims": cl_ok, "ok_sources": src_ok,
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
        "pct_fully_ok": pct_of(node_items, lambda i: i["ok_claims"] and i["ok_sources"]),
        "standalone_pct_fully_ok": pct_of(standalone, lambda i: i["ok_claims"] and i["ok_sources"]),
        "standalone_without_evidence": sum(1 for i in standalone if i["claims"] == 0),
        "standalone_declared_gap": sum(1 for i in standalone if i.get("declared_gap")),
    }
    out["gaps"]["technology_nodes"] = [i for i in node_items
                                       if not (i["ok_claims"] and i["ok_sources"])]

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

    #: Декларация «внешнего источника не существует»: проход
    #: `corrections.declare_evidence_gaps` пишет её в `source_url` префиксом
    #: `user_defined:`. Прежняя проверка `bool(u) or u.startswith(...)` была
    #: тождественна `bool(u)`: вторая ветка недостижима, потому что пустая
    #: строка не начинается с префикса. Различить «есть URL» и «есть
    #: декларация» она не могла, поэтому `undeclared_missing_url` совпадал с
    #: `missing_url` и молчаливая дыра не отличалась от объявленной.
    def conflict_is_declared(c) -> bool:
        return (c.get("source_url") or "").strip().startswith("user_defined:")

    def conflict_has_source(c) -> bool:
        u = (c.get("source_url") or "").strip()
        return bool(u) and not conflict_is_declared(c)

    out["classes"]["conflicts"] = {
        "entity_class": "conflicts", "total": len(conf),
        # Ссылка, которую можно открыть: декларация — не URL.
        "missing_url": sum(1 for c in conf if not conflict_has_source(c)),
        "declared_user_defined": sum(1 for c in conf if conflict_is_declared(c)),
        # Молчаливая дыра: нет ни URL, ни декларации. Обязана быть нулём.
        "undeclared_missing_url": sum(
            1 for c in conf if not conflict_has_source(c) and not conflict_is_declared(c)),
        # Спецификация (стр. 142) требует у каждой связи «решение или
        # workaround». Пустое решение — пробел, а не «нет рекомендации»:
        # решение выводится из типа связи детерминированно (basis='derived')
        # либо объявляется экспертным допущением.
        "missing_resolution": sum(1 for c in conf if not (c.get("resolution") or "").strip()),
        # Основание обязательно там, где решение есть: без него выведенное
        # решение неотличимо от документированного.
        "missing_resolution_basis": sum(
            1 for c in conf
            if (c.get("resolution") or "").strip() and not (c.get("basis") or "").strip()),
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
        # «Решение / workaround» (спецификация, стр. 142) у каждого ребра.
        "missing_workaround": sum(1 for e in edges if not (e.get("workaround") or "").strip()),
        "missing_workaround_basis": sum(
            1 for e in edges
            if (e.get("workaround") or "").strip() and not (e.get("basis") or "").strip()),
    }

    # Метаданные карточки метода из исследований (спецификация: «варианты
    # реализации», «условия применимости», «требуемые данные и инструменты»).
    # Пустое поле здесь — пробел переноса: данные есть в паках у 125 методов,
    # поэтому нулевое покрытие означало бы, что загрузчик их не читает.
    methods = q(conn, "select * from methods")
    out["classes"]["method_research_meta"] = {
        "entity_class": "methods", "total": len(methods),
        "missing_implementation_variants": sum(
            1 for m in methods if _json_len(m.get("implementation_variants")) == 0),
        "missing_applicability_conditions": sum(
            1 for m in methods if _json_len(m.get("requires_conditions")) == 0),
        "missing_required_data_and_tools": sum(
            1 for m in methods if not (m.get("required_data_and_tools") or "").strip()),
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
    # known "State -> Niagara", "DLSS -> RTXNTC", "VSM -> DF Shadows" cases).
    # Шаблоны со словесной границей записаны СЫРЫМИ строками: в обычном
    # литерале `"\btsr\b"` — это символ забоя (0x08), а не граница слова, и
    # шаблон не находил ничего. Набор и значения обязаны совпадать с
    # `tools/verify_sources.py`: расхождение двух копий уже приводило к тому,
    # что один инструмент видел противоречие, а другой — нет.
    TOPIC_TOKENS = {
        "niagara": ["niagara"],
        "dlss": [r"\bdlss\b"],
        "nanite": ["nanite"],
        "lumen": ["lumen"],
        "vsm": ["virtual shadow", "virtual-shadow", r"\bvsm\b"],
        "dfshadow": ["distance field shadow", "distance-field"],
        "ray_reconstruction": ["ray reconstruction", "rtxntc", "neural texture"],
        "chaos": ["chaos physics", "chaos cloth", "chaos destruction"],
        "subtick": ["sub-tick", "subtick"],
        "rtxdi": ["rtxdi", "ray traced direct"],
        "tsr": ["temporal super resolution", r"\btsr\b"],
        "navmesh": ["navmesh", "nav mesh"],
        "ecs": [r"\becs\b", "entity component system"],
        "shadergraph": ["shader graph"],
        "vfxgraph": ["vfx graph"],
        "hair": ["tressfx", "hairworks", "strand"],
        "audio": ["wwise", "fmod", "cryaudio"],
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
    }
    # Дубликаты URL считаются ниже и перезаписывают ключ. Прежняя заглушка
    # `defaultdict(int, {u: 0 for u in []})` давала пустой список и создавала
    # впечатление, что проверка выполнена.
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

    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")

    # ---- human summary ------------------------------------------------
    print(f"DB: {args.db}\n")
    print(f"{'class':22s} {'n':>6s} {'claims>=3':>10s} {'src>=2':>8s} {'FULL':>7s}")
    for k, s in out["classes"].items():
        if f"pct_claims>={MIN_CLAIMS}" in s:
            print(f"{k:22s} {s['total']:6d} {s[f'pct_claims>={MIN_CLAIMS}']:10.1f} "
                  f"{s[f'pct_located_sources>={MIN_LOCATED_SOURCES}']:8.1f} "
                  f"{s['pct_fully_ok']:7.1f}")
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
    vis = out["visibility"]
    if vis["invisible_tables"]:
        print("\nINVISIBLE rows (complete but not published):",
              ", ".join(f"{k} {v['published']}/{v['total']}"
                        for k, v in vis["tables"].items() if not v["ok"]))
    else:
        print("\nvisibility: no undeclared invisible rows")
    declared = [f"{k} {v['declared_invisible']}/{v['total']} — {v['declaration']}"
                for k, v in vis["tables"].items() if v["declared_invisible"]]
    if declared:
        print("\nDECLARED invisible rows (invisibility is a decision, not a finding):",
              "; ".join(declared))
    print("\nfull report ->", args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
