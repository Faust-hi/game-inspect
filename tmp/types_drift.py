"""Сверка объявленных типов frontend с фактическими ответами API."""
import json
import pathlib
import re

ROOT = pathlib.Path(r"C:\Users\user\Desktop\game-inspect")
shape = json.loads((ROOT / "tmp" / "api_shape.json").read_text(encoding="utf-8"))
types_src = (ROOT / "frontend" / "src" / "types.ts").read_text(encoding="utf-8")

# Имя интерфейса -> фактический объект из ответа.
PAIRS = {
    "RecommendationResult": shape["recommend"],
    "Recommendation": shape["recommend"]["recommendations"][0],
    "ExcludedMethod": shape["recommend"]["excluded"][0] if shape["recommend"]["excluded"] else {},
    "Risk": shape["recommend"]["risks"][0] if shape["recommend"]["risks"] else {},
    "HardwareEstimate": shape["hardware"],
    "LoadProfile": shape["load"],
    "Method": shape["method"],
    "GameFunction": shape["function"],
}


def interface_fields(name: str) -> list[str]:
    match = re.search(rf"export interface {name}\b[^{{]*\{{(.*?)\n\}}", types_src, re.S)
    if not match:
        return []
    body = match.group(1)
    fields = []
    for line in body.splitlines():
        line = line.strip()
        if not line or line.startswith("//") or line.startswith("/*") or line.startswith("*"):
            continue
        found = re.match(r"([A-Za-z_][A-Za-z0-9_]*)\s*(\?)?\s*:", line)
        if found:
            fields.append(found.group(1))
    return fields


for name, actual in PAIRS.items():
    declared = interface_fields(name)
    if not declared:
        print(f"[?] интерфейс {name} не найден в types.ts")
        continue
    missing = [f for f in declared if f not in actual]
    extra = [k for k in actual if k not in declared]
    print(f"\n=== {name} ===")
    print(f"  объявлено: {len(declared)}, пришло: {len(actual)}")
    if missing:
        print(f"  НЕ приходят: {missing}")
    if extra:
        print(f"  не описаны в типе: {extra}")
