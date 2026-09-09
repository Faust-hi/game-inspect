"""Index current research gaps and migration graph without executing migrations."""
import ast
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
tables = json.loads((ROOT / "validation/research/run-2026-09-08-02/seed-catalog.json").read_text(encoding="utf-8"))["tables"]
methods = {r["id"]: r for r in tables["methods"]}
tools = {r["id"]: r for r in tables["engine_tools"]}
engines = {r["id"]: r for r in tables["engines"]}
links = []
for link in tables["method_engine_links"]:
    tool = tools[link["tool_id"]]
    engine = engines[tool["engine_id"]]
    links.append({"id": link["id"], "method": methods[link["method_id"]]["code"],
                  "engine": engine["code"], "tool": tool["code"],
                  "relation": link["relation_type"], "note": link["note"],
                  "source_url": link["source_url"], "tool_docs_url": tool["docs_url"],
                  "declared_engine_versions": engine["versions"],
                  "structured_tool_version_constraint": None,
                  "structured_link_version_constraint": None,
                  "semantic_primary_review": "pending_except_specific_cases_in_report",
                  "per_version_cases": [{"version": version, "status": "unknown_not_verified"}
                                        for version in engine["versions"]]})
graph = []
for path in sorted((ROOT / "backend/alembic/versions").glob("*.py")):
    fields = {}
    tree = ast.parse(path.read_text(encoding="utf-8-sig"))
    for node in tree.body:
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            if node.target.id in {"revision", "down_revision"}:
                fields[node.target.id] = ast.literal_eval(node.value)
    graph.append({"file": path.relative_to(ROOT).as_posix(), **fields})
heads = sorted({r["revision"] for r in graph} - {r["down_revision"] for r in graph})
value = {"kind": "structural_inventory_not_source_certification", "links": links,
         "counts": {"links": len(links), "by_engine": dict(Counter(r["engine"] for r in links)),
                    "per_version_cases": sum(len(r["per_version_cases"]) for r in links),
                    "link_source_differs_from_tool": sum(r["source_url"] != r["tool_docs_url"] for r in links)},
         "migration_graph": graph, "source_heads": heads, "migrations_executed": False,
         "live_database_inspected": False}
with (ROOT / "validation/research/continuation-index-2026-09-09.json").open("x", encoding="utf-8") as output:
    json.dump(value, output, ensure_ascii=False, indent=2)
print(json.dumps({"counts": value["counts"], "source_heads": heads}))
