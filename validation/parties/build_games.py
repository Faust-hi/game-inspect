"""Разбор партий 01-11: извлечение профилей игр для прогона через DSS.

На выходе: validation/parties/games_raw.json
  * название, год, движок (как в партии), платформы, таргеты, уровни объектов/NPC,
    мультиплеер, API, список фич, список инженерных решений (метод/реализация/цена),
    Min/Rec HW из инженерного паспорта, кадровый бюджет.
"""

from __future__ import annotations

import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT = pathlib.Path(__file__).resolve().parent / "games_raw.json"

sys.stdout.reconfigure(encoding="utf-8")

HEAD_RE = re.compile(r"^## (?P<num>\d+)\.\s+(?P<title>.+?)\s*$")
META_RE = {
    "engine": re.compile(r"^-\s+\*\*Engine:\*\*\s*(?P<v>.+)$"),
    "format": re.compile(r"^-\s+\*\*Format:\*\*\s*(?P<v>.+)$"),
    "targets": re.compile(r"^-\s+\*\*Targets:\*\*\s*(?P<v>.+)$"),
    "levels": re.compile(r"^-\s+\*\*Object/NPC level:\*\*\s*(?P<v>.+)$"),
    "api": re.compile(r"^-\s+\*\*API:\*\*\s*(?P<v>.+)$"),
    "platforms": re.compile(r"^-\s+\*\*Platforms:\*\*\s*(?P<v>.+)$"),
}
HW_RE = re.compile(r"^-\s+\*\*(?P<k>Min HW|Rec HW|Min HW \(PC|Rec HW \(PC|Frame budget)[^:]*:\*\*\s*(?P<v>.+)$")


def split_meta(v: str) -> dict:
    """Разбор строки '- **Format:** 3D | **World:** linear | **Scale:** small'."""
    out = {}
    for part in v.split("|"):
        m = re.match(r"\s*\*\*(?P<k>[^:*]+):\*\*\s*(?P<val>.+)", part)
        if m:
            out[m.group("k").strip().lower()] = m.group("val").strip()
    return out


def parse_file(path: pathlib.Path, party: int) -> list[dict]:
    lines = path.read_text(encoding="utf-8").splitlines()
    games: list[dict] = []
    cur: dict | None = None
    section: str | None = None
    for line in lines:
        hm = HEAD_RE.match(line)
        if hm:
            title = hm.group("title")
            year = None
            ym = re.search(r"\((?:переиздание\s+)?(\d{4})", title)
            if ym:
                year = int(ym.group(1))
            cur = {
                "party": party,
                "title": title.split("—")[0].strip(),
                "raw_title": title,
                "year": year,
                "engine_raw": None,
                "world_raw": None,
                "scale_raw": None,
                "targets_raw": None,
                "levels_raw": None,
                "api_raw": None,
                "platforms_raw": None,
                "features": [],
                "methods": [],
                "hw": [],
                "frame_budget_ms": None,
            }
            games.append(cur)
            section = None
            continue
        if cur is None:
            continue
        if line.startswith("### "):
            section = line[4:].strip()
            continue
        for key, rx in META_RE.items():
            m = rx.match(line)
            if m:
                cur[f"{key}_raw"] = m.group("v").strip()
                break
        else:
            m = HW_RE.match(line)
            if m:
                cur["hw"].append({m.group("k").strip(): m.group("v").strip()})
                fb = re.search(r"([\d.]+)\s*мс", m.group("v"))
                if "Frame budget" in m.group("k") and fb:
                    cur["frame_budget_ms"] = float(fb.group(1))
                continue
            if section == "Features" and line.startswith("- ") and "|" not in line:
                for token in re.split(r"[,\n]", line[2:]):
                    tok = token.strip()
                    if not tok:
                        continue
                    tok = re.sub(r"\s*\(.*?\)", "", tok).strip()
                    if tok:
                        cur["features"].append(tok)
                continue
            if section == "Инженерные решения" and line.startswith("|"):
                cells = [c.strip() for c in line.strip("|").split("|")]
                if len(cells) < 2:
                    continue
                code, impl = cells[0], cells[1]
                if code in ("Метод", "") or set(code) <= set("-: "):
                    continue
                cur["methods"].append(
                    {"code": code, "impl": impl, "price": cells[2] if len(cells) > 2 else ""}
                )
    return games


def main() -> None:
    games: list[dict] = []
    for i in range(1, 12):
        p = ROOT / f"партия-{i:02d}.md"
        if not p.exists():
            continue
        gs = parse_file(p, i)
        # отсекаем возможные неигровые секции: оставляем только с инженерными решениями
        gs = [g for g in gs if g["methods"]]
        games.extend(gs)
    # разбор составных строк Format/World/Scale и Object/NPC level + Multiplayer
    for g in games:
        fm = split_meta(g.get("format_raw") or "")
        g["world_raw"] = fm.get("world")
        g["scale_raw"] = fm.get("scale")
        g["format_raw"] = fm.get("format")
        lv = (g.get("levels_raw") or "").split("**Multiplayer:**")
        g["levels_raw"] = lv[0].strip().rstrip("|").strip()
        mp = lv[1].strip() if len(lv) > 1 else ""
        if mp:
            mp = mp.split("|")[0]
        g["multiplayer_raw"] = mp
    OUT.write_text(json.dumps(games, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"игр: {len(games)}")
    for g in games:
        print(f"  [{g['party']:02d}] {g['title'][:52]:54s} {len(g['methods']):3d} решений")


if __name__ == "__main__":
    main()
