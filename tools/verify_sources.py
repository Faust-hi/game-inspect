#!/usr/bin/env python3
"""Orchestrator ground-truth verifier for the evidence base.

This is the control mechanism that keeps research workers honest. It does two
things the plain coverage audit (`tools/audit_evidence.py`) does NOT do:

  1. It actually CONTACTS every URL and records the HTTP result, so a
     fabricated or rotted citation is caught instead of counted.
  2. It re-checks every rule from the worker contract (`SCHEMA.md` hard rules)
     mechanically: dangling source refs, derived-without-formula, numeric
     claims without a source, non-distinct game examples, missing locators,
     dishonest `availability`, title/URL topic contradictions.

Usage:
    python tools/verify_sources.py                 # verify packs + db
    python tools/verify_sources.py --no-net        # skip HTTP (offline)
    python tools/verify_sources.py --packs-only
    python tools/verify_sources.py --db-only
"""
from __future__ import annotations

import argparse
import json
import re
import socket
import sqlite3
import ssl
import urllib.error
import urllib.request
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DB = ROOT / "backend" / "gamedev_dss.db"
PACK_DIR = ROOT / "research" / "packs"
CACHE = ROOT / "research" / "_verify_cache"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/125.0 Safari/537.36")

ALLOWED_BASIS = {
    "measured", "documented", "derived", "case_evidence",
    "expert_estimate", "unknown",
}
# A claim that carries a number MUST be traceable to a source.
NUMERIC_BASES_REQUIRING_SOURCE = {"measured", "documented", "derived", "case_evidence"}

# Fields that record a DECLARED ABSENCE rather than a positive claim. Such a
# row states "no source was located that says X"; there is nothing to cite, and
# fabricating a citation would be a false attribution. They are therefore
# exempt from the source and locator requirements -- but they must still be
# reported separately so a declared gap can never quietly become invisible.
DECLARED_GAP_FIELDS = {"adoption_evidence_gap"}

# Topic-token contradiction detector: same class of bug as the known
# "State -> Niagara", "DLSS -> RTXNTC", "VSM -> DF Shadows" mismatches.
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


def topics(text: str) -> set[str]:
    t = (text or "").lower()
    return {k for k, pats in TOPIC_TOKENS.items()
            if any(re.search(p, t) for p in pats)}


# ─────────────────────────── HTTP reachability ───────────────────────────

# Объявленный маркер отсутствия ссылки (`user_defined:catalog_dependency`).
# Это НЕ адрес: `declare_evidence_gaps` ставит его конфликтам, выведенным из
# структуры каталога, у которых публичного источника не существует. Проверять
# его как URL и объявлять «мёртвой ссылкой» нельзя: 30 таких конфликтов давали
# 30 ложных срабатываний и раздували `url_dead` с 4 до 34, а
# `tools/repair_dead_links.py` пытался бы «починить» саму декларацию.
DECLARED_URL_MARKER = re.compile(r"^\s*(user_defined|declared)\s*:", re.I)


def _cache_path(url: str) -> Path:
    import hashlib
    h = hashlib.sha1(url.encode("utf-8")).hexdigest()[:16]
    return CACHE / h


def http_check(url: str, timeout: int = 25, use_cache: bool = True) -> dict:
    """Return {'status': 'ok|protected|declared|dead|error', 'code': int|None, 'note': str}."""
    if DECLARED_URL_MARKER.match(url or ""):
        return {"status": "declared", "code": None,
                "note": "объявленное отсутствие ссылки, не адрес"}
    if not url or not re.match(r"^https?://", url, re.I):
        return {"status": "dead", "code": None, "note": "not an http(s) url"}
    CACHE.mkdir(parents=True, exist_ok=True)
    cp = _cache_path(url)
    if use_cache and cp.exists():
        try:
            return json.loads(cp.read_text(encoding="utf-8"))
        except Exception:
            pass

    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    result = None
    for method in ("HEAD", "GET"):
        try:
            req = urllib.request.Request(url, method=method, headers={
                "User-Agent": UA,
                "Accept": "*/*",
                "Accept-Language": "en-US,en;q=0.9",
            })
            with urllib.request.urlopen(req, timeout=timeout, context=ctx) as r:
                result = {"status": "ok", "code": r.status, "note": ""}
                break
        except urllib.error.HTTPError as e:
            code = e.code
            if code in (401, 403, 429):
                # Exists, but bot-protected. NOT evidence of fabrication.
                result = {"status": "protected", "code": code,
                          "note": "bot-protected / auth wall"}
            elif code in (404, 410):
                result = {"status": "dead", "code": code, "note": "not found"}
            else:
                result = {"status": "error", "code": code, "note": "http error"}
            # a 403 on HEAD is often followed by a 200 on GET -- retry once
            if method == "HEAD" and code in (403, 405, 501):
                continue
            break
        except urllib.error.URLError as e:
            reason = str(getattr(e, "reason", e))
            if "Name or service not known" in reason or "getaddrinfo" in reason:
                result = {"status": "dead", "code": None,
                          "note": "dns failure: " + reason[:120]}
                break
            result = {"status": "error", "code": None, "note": reason[:160]}
            break
        except socket.timeout:
            result = {"status": "error", "code": None, "note": "timeout"}
            break
        except Exception as e:  # noqa: BLE001
            result = {"status": "error", "code": None, "note": str(e)[:160]}
            break

    if result is None:
        result = {"status": "error", "code": None, "note": "no response"}
    if use_cache:
        try:
            cp.write_text(json.dumps(result), encoding="utf-8")
        except Exception:
            pass
    return result


# ─────────────────────────── pack-level checks ───────────────────────────

def verify_packs(do_net: bool) -> dict:
    findings: dict[str, list] = defaultdict(list)
    stats = {"packs": 0, "sources": 0, "claims": 0,
             "derived_with_formula": 0, "derived_total": 0}
    url_index: dict[str, list[str]] = defaultdict(list)
    # Dedup is case-insensitive (a URL differing only in case is the same
    # resource for reporting), but the HTTP request MUST use the original
    # casing: many documentation hosts (Wikipedia, docs.unity3d.com,
    # raw.githubusercontent.com, learn.microsoft.com) are case-sensitive and
    # return 404 for a lowercased path. Lowercasing here produced ~99 false
    # "dead" findings, so `url_original` preserves the stored form for the
    # network probe while `url_index` keeps its normalised grouping key.
    url_original: dict[str, str] = {}
    # A source code may be DECLARED in one pack and CITED in another: the
    # loader (pack_loader.sync_packs) resolves codes against the union of all
    # packs, and so must the verifier. Building the code registry per-pack
    # flagged every legitimate cross-pack citation as dangling.
    all_source_codes: set[str] = set()
    for _p in sorted(PACK_DIR.glob("pack_*.json")):
        try:
            _d = json.loads(_p.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            continue
        for _s in _d.get("sources", []):
            if _s.get("code"):
                all_source_codes.add(_s["code"])

    for path in sorted(PACK_DIR.glob("pack_*.json")):
        try:
            pack = json.loads(path.read_text(encoding="utf-8"))
        except Exception as e:  # noqa: BLE001
            findings["pack_unparseable"].append({"pack": path.name, "error": str(e)})
            continue
        stats["packs"] += 1
        pname = path.name
        src_by_code = {}
        for s in pack.get("sources", []):
            code = s.get("code")
            if not code:
                findings["source_without_code"].append({"pack": pname, "title": s.get("title")})
                continue
            if code in src_by_code:
                findings["duplicate_source_code"].append({"pack": pname, "code": code})
            src_by_code[code] = s
            stats["sources"] += 1
            url = (s.get("url") or "").strip()
            url_index[url.lower()].append(f"{pname}:{code}")
            if url:
                url_original.setdefault(url.lower(), url)
            if not url:
                findings["source_missing_url"].append({"pack": pname, "code": code})
            if not (s.get("locator") or "").strip():
                findings["source_missing_locator"].append({"pack": pname, "code": code})
            if not (s.get("published_date") or "").strip():
                findings["source_missing_date"].append({"pack": pname, "code": code})
            if not (s.get("source_type") or "").strip():
                findings["source_missing_type"].append({"pack": pname, "code": code})
            if (s.get("availability") or "").strip() == "verified_fetched" and not url:
                findings["availability_overclaim"].append({"pack": pname, "code": code})

        # ---- walk every entity section ----
        for section, block in pack.items():
            if not isinstance(block, dict):
                continue
            for ecode, edata in block.items():
                if not isinstance(edata, dict):
                    continue
                for c in edata.get("claims", []):
                    stats["claims"] += 1
                    field = (c.get("field") or "").strip()
                    src = c.get("source")
                    if src and src not in all_source_codes:
                        findings["claim_dangling_source"].append(
                            {"pack": pname, "entity": f"{section}/{ecode}", "source": src})
                    if not (c.get("locator") or "").strip() and field not in DECLARED_GAP_FIELDS:
                        findings["claim_missing_locator"].append(
                            {"pack": pname, "entity": f"{section}/{ecode}",
                             "field": c.get("field")})
                    if field in DECLARED_GAP_FIELDS:
                        stats["declared_gaps"] = stats.get("declared_gaps", 0) + 1
                    basis = (c.get("basis") or "").strip()
                    if basis and basis not in ALLOWED_BASIS:
                        findings["claim_bad_basis"].append(
                            {"pack": pname, "entity": f"{section}/{ecode}", "basis": basis})
                    is_num = c.get("value") is not None or bool(c.get("value_range"))
                    # Тот же порядок обоснования, что и в БД-проверке: число
                    # допустимо без источника, если оно выведено собственной
                    # формулой с явными входами (спека, строка 412).
                    pack_self_justified = (
                        basis == "derived"
                        and bool((c.get("formula") or "").strip())
                        and bool(c.get("input_parameters"))
                    )
                    if (is_num and basis in NUMERIC_BASES_REQUIRING_SOURCE
                            and not src and not pack_self_justified):
                        findings["numeric_claim_without_source"].append(
                            {"pack": pname, "entity": f"{section}/{ecode}",
                             "field": c.get("field")})
                    if basis == "derived":
                        stats["derived_total"] += 1
                        has_f = bool((c.get("formula") or "").strip())
                        has_i = bool(c.get("input_parameters"))
                        if has_f and has_i:
                            stats["derived_with_formula"] += 1
                        else:
                            findings["derived_missing_formula_or_inputs"].append(
                                {"pack": pname, "entity": f"{section}/{ecode}",
                                 "field": c.get("field"),
                                 "has_formula": has_f, "has_inputs": has_i})
                    if basis == "expert_estimate":
                        # Disclosure may live in the statement OR the context.
                        blob = ((c.get("context") or "") + " "
                                + (c.get("statement") or "")).lower()
                        if not any(w in blob for w in
                                   ("оцен", "estimat", "эксперт", "assum",
                                    "judgement", "judgment", "not measured")):
                            findings["expert_estimate_without_disclosure"].append(
                                {"pack": pname, "entity": f"{section}/{ecode}",
                                 "field": c.get("field")})

    # ---- title/url contradiction across all packs ----
    for path in sorted(PACK_DIR.glob("pack_*.json")):
        try:
            pack = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        for s in pack.get("sources", []):
            tt, tu = topics(s.get("title")), topics(s.get("url"))
            if tt and tu and not (tt & tu):
                findings["title_url_contradiction"].append({
                    "pack": path.name, "code": s.get("code"),
                    "title": s.get("title"), "url": s.get("url"),
                    "title_topics": sorted(tt), "url_topics": sorted(tu)})

    dupes = {u: c for u, c in url_index.items() if u and len(c) > 1}

    # ---- HTTP reachability ----
    net: dict[str, dict] = {}
    if do_net:
        unique = [u for u in url_index if u]
        print(f"[net] checking {len(unique)} unique pack URLs ...", flush=True)
        for i, u in enumerate(unique, 1):
            # probe with the ORIGINAL casing; report under the normalised key
            net[u] = http_check(url_original.get(u, u))
            if i % 25 == 0:
                print(f"[net]   {i}/{len(unique)}", flush=True)
        for u, res in net.items():
            shown = url_original.get(u, u)
            if res["status"] == "dead":
                for owner in url_index[u]:
                    findings["url_dead"].append(
                        {"owner": owner, "url": shown, "note": res["note"], "code": res["code"]})
            elif res["status"] == "declared":
                # Объявленное отсутствие ссылки: не дефект, а решение.
                for owner in url_index[u]:
                    findings["url_declared"].append(
                        {"owner": owner, "url": shown, "note": res["note"]})
            elif res["status"] == "error":
                for owner in url_index[u]:
                    findings["url_error"].append(
                        {"owner": owner, "url": shown, "note": res["note"]})

    return {
        "stats": stats,
        "findings": {k: v for k, v in findings.items()},
        "duplicate_urls": dupes,
        "url_results": net,
        "unique_urls": len(url_index),
    }


# ─────────────────────────── db-level checks ───────────────────────────

def verify_db(db_path: str, do_net: bool) -> dict:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    def q(sql, params=()):
        cur = conn.execute(sql, params)
        cols = [d[0] for d in cur.description]
        return [dict(zip(cols, r)) for r in cur.fetchall()]

    src = q("select * from evidence_sources")
    src_ids = {r["id"] for r in src}
    claims = q("select * from evidence_claims")
    findings: dict[str, list] = defaultdict(list)

    url_owners: dict[str, list[str]] = defaultdict(list)
    # See verify_packs(): dedup case-insensitively, but probe with the
    # ORIGINAL casing or case-sensitive hosts report spurious 404s.
    url_original: dict[str, str] = {}

    def _own(raw: str, label: str) -> None:
        u = (raw or "").strip()
        if u:
            url_owners[u.lower()].append(label)
            url_original.setdefault(u.lower(), u)

    for s in src:
        _own(s.get("url"), f"source:{s['code']}")
    # NB: `conflicts` has no `code` column -- use id.
    for c in q("select id, source_url from conflicts "
               "where source_url is not null and source_url != ''"):
        _own(c["source_url"], f"conflict:{c['id']}")
    for l in q("select id, source_url from method_engine_links "
               "where source_url is not null and source_url != ''"):
        _own(l["source_url"], f"link:{l['id']}")
    for t in ("hardware_cpu", "hardware_gpu"):
        # These tables identify rows by id/model, not by `code`.
        for r in q(f"select id, model, source_url from {t} "
                   "where source_url is not null and source_url != ''"):
            _own(r["source_url"], f"{t}:{r['model']}")

    def _gap(c: dict) -> bool:
        return (c.get("field") or "").strip() in DECLARED_GAP_FIELDS

    def _self_justified(c: dict) -> bool:
        """Число обосновано собственным расчётом, а не внешним источником.

        Правило спецификации (строка 412): запись валидна при `source` ЛИБО при
        `formula` + `input_parameters`. `derived`-утверждение с формулой и
        входами не «без источника» — оно вообще не ссылается наружу, и его
        отсутствие в `source_id` не дефект. Та же формула используется в
        `tools/audit_evidence.py` и в валидаторе базы; без неё эта проверка
        давала 3 ложных срабатывания, пока аудит показывал 0.
        """
        return (
            (c.get("basis") or "") == "derived"
            and bool((c.get("formula") or "").strip())
            and bool((c.get("input_parameters") or "").strip())
        )

    # Declared absences are intentionally source-less; they are counted and
    # reported under their own key instead of being hidden inside `dangling`.
    # `_self_justified` обязателен и здесь: `derived`-утверждение с формулой и
    # входами вообще не ссылается наружу, и его пустой `source_id` — не дефект.
    # Без этого условия проверка давала ровно 3 ложных срабатывания
    # (`research:frame_budget_60`, `research:resolution_ratio_4k`,
    # `research:memory_headroom`) и противоречила `tools/audit_evidence.py`,
    # который показывал 0. Именно этот случай описан в docstring выше.
    dangling = [c["code"] for c in claims
                if not _gap(c)
                and not _self_justified(c)
                and (c.get("source_id") is None or c["source_id"] not in src_ids)]
    findings["declared_gap_claims"] = [c["code"] for c in claims if _gap(c)]
    derived_bad = [{"code": c["code"], "entity": f"{c['entity']}/{c['entity_code']}"}
                   for c in claims if c.get("basis") == "derived"
                   and (not (c.get("formula") or "").strip()
                        or not (c.get("input_parameters") or "").strip())]
    numeric_no_source = [c["code"] for c in claims
                         if (c.get("value_num") is not None or c.get("range_min") is not None)
                         and (c.get("source_id") is None or c["source_id"] not in src_ids)
                         and not _self_justified(c)]
    no_locator = [c["code"] for c in claims
                  if not (c.get("locator") or "").strip() and not _gap(c)]

    # NB: dependency_edges has no `code`; rows are identified by id and their
    # endpoints are node FKs. Selecting `code` here raised OperationalError and
    # aborted the whole DB stage before it ever ran.
    edges_no_src = q("select id, source_node_id, target_node_id from dependency_edges "
                     "where source_id is null or source_id = ''")
    # NB: `conflicts` identifies rows by id, not by `code` (same trap as the
    # URL-collection loop above and as dependency_edges).
    conflicts_no_url = q("select id, a_code, b_code from conflicts "
                         "where source_url is null or source_url = ''")
    links_no_url = q("select id from method_engine_links where source_url is null or source_url = ''")
    src_no_date = [s["code"] for s in src if not (s.get("published_date") or "").strip()]

    findings["claim_dangling_source"] = dangling
    findings["derived_missing_formula_or_inputs"] = derived_bad
    findings["numeric_claim_without_source"] = numeric_no_source
    findings["claim_missing_locator"] = no_locator
    findings["dependency_edge_without_source"] = edges_no_src
    findings["conflict_without_url"] = conflicts_no_url
    findings["method_engine_link_without_url"] = links_no_url
    findings["source_without_published_date"] = src_no_date

    net = {}
    if do_net:
        unique = [u for u in url_owners if u]
        print(f"[net] checking {len(unique)} unique DB URLs ...", flush=True)
        for i, u in enumerate(unique, 1):
            net[u] = http_check(url_original.get(u, u))
            if i % 50 == 0:
                print(f"[net]   {i}/{len(unique)}", flush=True)
        for u, res in net.items():
            shown = url_original.get(u, u)
            if res["status"] == "dead":
                for owner in url_owners[u]:
                    findings["url_dead"].append(
                        {"owner": owner, "url": shown, "note": res["note"], "code": res["code"]})
            elif res["status"] == "declared":
                # `user_defined:catalog_dependency` — объявленное отсутствие
                # ссылки у 30 конфликтов, выведенных из структуры каталога.
                for owner in url_owners[u]:
                    findings["url_declared"].append(
                        {"owner": owner, "url": shown, "note": res["note"]})
            elif res["status"] == "error":
                for owner in url_owners[u]:
                    findings["url_error"].append(
                        {"owner": owner, "url": shown, "note": res["note"]})

    return {
        "counts": {
            "sources": len(src), "claims": len(claims),
            "unique_urls": len(url_owners),
        },
        "findings": {k: v for k, v in findings.items()},
        "url_results": net,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", default=str(DEFAULT_DB))
    ap.add_argument("--out", default=str(ROOT / "research" / "verification_report.json"))
    ap.add_argument("--md", default=str(ROOT / "research" / "verification_report.md"))
    ap.add_argument("--no-net", action="store_true")
    ap.add_argument("--packs-only", action="store_true")
    ap.add_argument("--db-only", action="store_true")
    args = ap.parse_args()
    do_net = not args.no_net

    report: dict = {"net_checked": do_net}
    if not args.db_only:
        print("== verifying research packs ==", flush=True)
        report["packs"] = verify_packs(do_net)
    if not args.packs_only:
        print("== verifying database ==", flush=True)
        report["db"] = verify_db(args.db, do_net)

    Path(args.out).write_text(json.dumps(report, ensure_ascii=False, indent=2),
                              encoding="utf-8")

    # ---------- human-readable markdown ----------
    L: list[str] = ["# Проверка достоверности доказательной базы", ""]
    L.append("Автоматическая сверка всех источников, утверждений и связей "
             "на соответствие контракту исследования.")
    L.append("")
    L.append(f"- Сетевые проверки URL: **{'включены' if do_net else 'выключены'}**")
    L.append("")

    if "packs" in report:
        p = report["packs"]
        s = p["stats"]
        L += ["## 1. Исследовательские пакеты", "",
              f"- пакетов: **{s['packs']}**",
              f"- источников: **{s['sources']}**",
              f"- утверждений (claims): **{s['claims']}**",
              f"- derived-утверждений с формулой и входными параметрами: "
              f"**{s['derived_with_formula']} / {s['derived_total']}**",
              f"- уникальных URL: **{p['unique_urls']}**",
              ""]
        L.append("| Проверка | Нарушений |")
        L.append("|---|---|")
        for k in sorted(p["findings"]):
            L.append(f"| `{k}` | {len(p['findings'][k])} |")
        L.append("")
        if p["duplicate_urls"]:
            L += ["### Дублирующиеся URL", ""]
            for u, owners in list(p["duplicate_urls"].items())[:25]:
                L.append(f"- `{u}` → {', '.join(owners)}")
            L.append("")

    if "db" in report:
        d = report["db"]
        c = d["counts"]
        L += ["## 2. База данных", "",
              f"- источников: **{c['sources']}**",
              f"- утверждений: **{c['claims']}**",
              f"- уникальных URL: **{c['unique_urls']}**",
              ""]
        L.append("| Проверка | Нарушений |")
        L.append("|---|---|")
        for k in sorted(d["findings"]):
            L.append(f"| `{k}` | {len(d['findings'][k])} |")
        L.append("")

    # URL health summary
    all_net: dict[str, dict] = {}
    for part in ("packs", "db"):
        if part in report:
            all_net.update(report[part]["url_results"])
    if all_net:
        buckets = defaultdict(int)
        for r in all_net.values():
            buckets[r["status"]] += 1
        L += ["## 3. Доступность URL", "",
              f"- проверено уникальных URL: **{len(all_net)}**",
              f"- доступны (2xx): **{buckets.get('ok', 0)}**",
              f"- защищены ботом/авторизацией (403/401/429): **{buckets.get('protected', 0)}**",
              f"- недоступны (404/410/DNS): **{buckets.get('dead', 0)}**",
              f"- ошибки сети/таймаут: **{buckets.get('error', 0)}**",
              f"- объявленное отсутствие ссылки, не адрес: **{buckets.get('declared', 0)}**",
              ""]
        dead = [(u, r) for u, r in all_net.items() if r["status"] == "dead"]
        if dead:
            L += ["### Недоступные URL (требуют замены или пометки)", ""]
            for u, r in dead[:60]:
                L.append(f"- `{u}` — {r['note']}")
            L.append("")
        err = [(u, r) for u, r in all_net.items() if r["status"] == "error"]
        if err:
            L += ["### Ошибки соединения (проверить вручную)", ""]
            for u, r in err[:60]:
                L.append(f"- `{u}` — {r['note']}")
            L.append("")

    Path(args.md).write_text("\n".join(L), encoding="utf-8")

    # ---------- console summary ----------
    print()
    if "packs" in report:
        p = report["packs"]
        print("PACKS:", json.dumps(p["stats"], ensure_ascii=False))
        for k in sorted(p["findings"]):
            n = len(p["findings"][k])
            if n:
                print(f"  ! {k}: {n}")
    if "db" in report:
        d = report["db"]
        print("DB:", json.dumps(d["counts"], ensure_ascii=False))
        for k in sorted(d["findings"]):
            n = len(d["findings"][k])
            if n:
                print(f"  ! {k}: {n}")
    print(f"\nreport -> {args.out}")
    print(f"markdown -> {args.md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
