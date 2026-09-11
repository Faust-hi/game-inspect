"""Дамп читаемого дайджеста доказательной базы по параметрам Категорий 1/2."""
from __future__ import annotations

import json
from pathlib import Path

d = json.load(open("../research/_verify_cache/category_evidence.json", encoding="utf-8"))
ec = d["entity_codes"]
mx = d["method_examples"]
fx = d["function_examples"]

out: list[str] = []


def claim_line(c):
    s = c["source"]
    sc = s["code"] if s else "—"
    extra = f" f={c['formula']}" if c["formula"] else ""
    return f"   [{c['basis']}] {c['field']}: {c['claim'][:150]}{extra}  <src {sc}>"


def dump(ent, codes=None, limit=None):
    codes = codes or list(ec[ent].keys())
    for code in codes:
        cl = ec[ent].get(code, [])
        out.append(f"\n### {ent}:{code}  (claims={len(cl)})")
        for c in cl[:limit]:
            out.append(claim_line(c))


out.append("======== CATEGORY 1 ========")
out.append("\n---- 1.1 game_function (all 40) ----")
for code in sorted(fx):
    n = len(ec["game_function"].get(code, []))
    ex = fx[code]
    direct = sum(1 for e in ex if e["role"] == "direct")
    games = "; ".join(sorted({e["title"] for e in ex if e["title"]}))[:180]
    out.append(f"  {code:32s} claims={n:3d} examples={len(ex)} direct={direct} | {games}")

out.append("\n---- 1.2 method coverage (all 124) ----")
for code in sorted(ec["method"]):
    n = len(ec["method"][code])
    ex = mx.get(code, [])
    direct = sum(1 for e in ex if e["role"] == "direct")
    games = "; ".join(sorted({e["title"] for e in ex if e["title"]}))[:140]
    out.append(f"  {code:36s} claims={n:3d} ex={len(ex)} direct={direct} | {games}")

out.append("\n---- 1.3 engine ----")
dump("engine")

out.append("\n---- 1.4 engine_tool (coverage summary) ----")
tool_codes = sorted(ec["engine_tool"])
for code in tool_codes:
    out.append(f"  {code:24s} claims={len(ec['engine_tool'][code])}")
out.append("\n  tool claims detail (first 8 tools):")
dump("engine_tool", tool_codes[:8])

out.append("\n---- 1.7 technology_node ----")
dump("technology_node", limit=6)

out.append("\n======== CATEGORY 2 ========")
for ent in ["stage_budget", "target_platform", "network_mode", "target_metric",
            "risk_factor", "load_profile", "hardware_cpu", "hardware_gpu", "research"]:
    out.append(f"\n---- {ent} ----")
    dump(ent, limit=6)

Path("../research/_verify_cache/digest.txt").write_text("\n".join(out), encoding="utf-8")
print("lines:", len(out))
print("written digest.txt")
