# -*- coding: utf-8 -*-
"""Сравнение оценок модели с реальными системными требованиями из партий.

Из каждой игры извлекаются Min HW / Rec HW (CPU, RAM, GPU/VRAM).
Оценки модели (reference_cpu, reference_gpu, ram_gb, vram_gb) сравниваются
с этими требованиями по годам выпуска железа и объёмам памяти.
"""
from __future__ import annotations

import json
import re
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "audit-2026-09-07"
HARDWARE_JSON = ROOT / "backend" / "app" / "seed" / "data" / "hardware.json"
RESULTS_JSON = AUDIT / "batch-run-results.json"


def load_hardware_catalog() -> tuple[dict[str, dict], dict[str, dict]]:
    data = json.loads(HARDWARE_JSON.read_text(encoding="utf-8"))
    cpus = {item["model"]: item for item in data.get("cpu", [])}
    gpus = {item["model"]: item for item in data.get("gpu", [])}
    return cpus, gpus


def parse_ram_gb(text: str) -> float | None:
    m = re.search(r"(\d+)\s*(GB|MB|gb|mb|Gb|Mb)\s+RAM", text, re.IGNORECASE)
    if not m:
        m = re.search(r"RAM[:\s]*(\d+)\s*(GB|MB)", text, re.IGNORECASE)
    if not m:
        return None
    val = int(m.group(1))
    unit = m.group(2).lower()
    return val / 1024 if unit == "mb" else float(val)


def parse_gpu_vram(text: str) -> float | None:
    m = re.search(r"GPU\s+(\d+)\s*(MB|GB)", text, re.IGNORECASE)
    if not m:
        m = re.search(r"(\d+)\s*(MB|GB)\s+(VRAM|Video|GPU)", text, re.IGNORECASE)
    if not m:
        return None
    val = int(m.group(1))
    unit = m.group(2).lower()
    return val / 1024 if unit == "mb" else float(val)


def extract_hw_sections(text: str) -> list[dict]:
    games = []
    blocks = re.split(r"(?m)^## ", text)
    for block in blocks[1:]:
        lines = block.splitlines()
        header = lines[0].strip()
        m = re.match(r"\d+\.\s*(.+?)\s*\((\d{4})", header)
        if not m:
            continue
        name = m.group(1).strip()
        year = int(m.group(2))
        body = "\n".join(lines)

        min_match = re.search(r"\*\*Min HW:\*\*\s*(.+?)(?:\n\n|\n###|\n- \*\*Rec)", body, re.DOTALL)
        rec_match = re.search(r"\*\*Rec HW:\*\*\s*(.+?)(?:\n\n|\n###|\n- \*\*Frame)", body, re.DOTALL)

        min_text = min_match.group(1).strip() if min_match else ""
        rec_text = rec_match.group(1).strip() if rec_match else ""

        games.append({
            "name": name,
            "year": year,
            "min_ram_gb": parse_ram_gb(min_text),
            "rec_ram_gb": parse_ram_gb(rec_text),
            "min_vram_gb": parse_gpu_vram(min_text),
            "rec_vram_gb": parse_gpu_vram(rec_text),
            "min_text": min_text,
            "rec_text": rec_text,
        })
    return games


def era(year: int) -> str:
    if year < 2010:
        return "до 2010"
    if year < 2015:
        return "2010–2014"
    if year < 2020:
        return "2015–2019"
    return "2020+"


def avg(lst: list[float]) -> float:
    return sum(lst) / len(lst) if lst else 0.0


def med(lst: list[float]) -> float:
    return statistics.median(lst) if lst else 0.0


def pct(n: int, total: int) -> str:
    return f"{n}/{total} ({n*100//total}%)" if total else "N/A"


def main() -> int:
    if not RESULTS_JSON.exists():
        print(f"Нет файла результатов: {RESULTS_JSON}")
        return 1

    cpus, gpus = load_hardware_catalog()
    results = json.loads(RESULTS_JSON.read_text(encoding="utf-8"))

    real_by_name: dict[str, dict] = {}
    for path in sorted(ROOT.glob("партия-*.md")):
        for g in extract_hw_sections(path.read_text(encoding="utf-8")):
            real_by_name[g["name"]] = g

    matched = []
    for r in results:
        if "error" in r:
            continue
        name = r["game"]["name"]
        real = real_by_name.get(name)
        if not real:
            continue
        hw = r.get("hardware") or {}
        model_ram = hw.get("ram_gb")
        model_vram = hw.get("vram_gb")
        ref_cpu = hw.get("reference_cpu")
        ref_gpu = hw.get("reference_gpu")

        cpu_year = cpus.get(ref_cpu, {}).get("release_year") if ref_cpu else None
        gpu_year = gpus.get(ref_gpu, {}).get("release_year") if ref_gpu else None

        matched.append({
            "name": name,
            "year": real["year"],
            "era": era(real["year"]),
            "model_ram": model_ram,
            "model_vram": model_vram,
            "min_ram": real["min_ram_gb"],
            "rec_ram": real["rec_ram_gb"],
            "min_vram": real["min_vram_gb"],
            "rec_vram": real["rec_vram_gb"],
            "cpu_year": cpu_year,
            "gpu_year": gpu_year,
            "ref_cpu": ref_cpu,
            "ref_gpu": ref_gpu,
            "bottleneck": hw.get("bottleneck"),
        })

    # --- Эпохальный анализ ---
    eras = ["до 2010", "2010–2014", "2015–2019", "2020+"]
    era_stats: dict[str, dict] = {e: {
        "count": 0,
        "ram_ratios_min": [], "ram_ratios_rec": [],
        "vram_ratios_min": [], "vram_ratios_rec": [],
        "cpu_leaps": [], "gpu_leaps": [],
        "under_min_ram": [], "under_rec_ram": [],
    } for e in eras}

    for m in matched:
        e = m["era"]
        st = era_stats[e]
        st["count"] += 1

        if m["model_ram"] is not None and m["min_ram"] is not None:
            st["ram_ratios_min"].append(m["model_ram"] / max(m["min_ram"], 0.5))
        if m["model_ram"] is not None and m["rec_ram"] is not None:
            st["ram_ratios_rec"].append(m["model_ram"] / max(m["rec_ram"], 0.5))
        if m["model_vram"] is not None and m["min_vram"] is not None:
            st["vram_ratios_min"].append(m["model_vram"] / max(m["min_vram"], 0.25))
        if m["model_vram"] is not None and m["rec_vram"] is not None:
            st["vram_ratios_rec"].append(m["model_vram"] / max(m["rec_vram"], 0.25))
        if m["cpu_year"] and m["year"]:
            st["cpu_leaps"].append(m["cpu_year"] - m["year"])
        if m["gpu_year"] and m["year"]:
            st["gpu_leaps"].append(m["gpu_year"] - m["year"])
        if m["model_ram"] is not None and m["min_ram"] is not None and m["model_ram"] < m["min_ram"]:
            st["under_min_ram"].append(m["name"])
        if m["model_ram"] is not None and m["rec_ram"] is not None and m["model_ram"] < m["rec_ram"]:
            st["under_rec_ram"].append(m["name"])

    print("=" * 80)
    print("СРАВНЕНИЕ МОДЕЛИ С РЕАЛЬНЫМИ ТРЕБОВАНИЯМИ (по эпохам)")
    print("=" * 80)
    print(f"Всего игр: {len(matched)}")
    print()

    for e in eras:
        st = era_stats[e]
        if st["count"] == 0:
            continue
        print(f"--- {e} ({st['count']} игр) ---")
        print(f"  RAM median к Min:   {med(st['ram_ratios_min']):.1f}x  (mean {avg(st['ram_ratios_min']):.1f}x)")
        print(f"  RAM median к Rec:   {med(st['ram_ratios_rec']):.1f}x  (mean {avg(st['ram_ratios_rec']):.1f}x)")
        print(f"  VRAM median к Min:  {med(st['vram_ratios_min']):.1f}x  (mean {avg(st['vram_ratios_min']):.1f}x)")
        print(f"  VRAM median к Rec:  {med(st['vram_ratios_rec']):.1f}x  (mean {avg(st['vram_ratios_rec']):.1f}x)")
        print(f"  CPU median перескок: {med(st['cpu_leaps']):+.0f} лет  (mean {avg(st['cpu_leaps']):+.1f})")
        print(f"  GPU median перескок: {med(st['gpu_leaps']):+.0f} лет  (mean {avg(st['gpu_leaps']):+.1f})")
        if st["under_min_ram"]:
            print(f"  RAM < Min: {', '.join(st['under_min_ram'])}")
        if st["under_rec_ram"]:
            print(f"  RAM < Rec: {', '.join(st['under_rec_ram'])}")
        print()

    # Глобальная сводка
    all_ram_min = [x for m in matched for x in ([m["model_ram"]/max(m["min_ram"],0.5)] if m["model_ram"] is not None and m["min_ram"] is not None else [])]
    all_ram_rec = [x for m in matched for x in ([m["model_ram"]/max(m["rec_ram"],0.5)] if m["model_ram"] is not None and m["rec_ram"] is not None else [])]
    all_vram_min = [x for m in matched for x in ([m["model_vram"]/max(m["min_vram"],0.25)] if m["model_vram"] is not None and m["min_vram"] is not None else [])]
    all_vram_rec = [x for m in matched for x in ([m["model_vram"]/max(m["rec_vram"],0.25)] if m["model_vram"] is not None and m["rec_vram"] is not None else [])]
    all_cpu_leaps = [m["cpu_year"] - m["year"] for m in matched if m["cpu_year"] and m["year"]]
    all_gpu_leaps = [m["gpu_year"] - m["year"] for m in matched if m["gpu_year"] and m["year"]]

    print("--- ГЛОБАЛЬНАЯ СВОДКА ---")
    print(f"RAM median к Min:  {med(all_ram_min):.1f}x")
    print(f"RAM median к Rec:  {med(all_ram_rec):.1f}x")
    print(f"VRAM median к Min: {med(all_vram_min):.1f}x")
    print(f"VRAM median к Rec: {med(all_vram_rec):.1f}x")
    print(f"CPU median перескок: {med(all_cpu_leaps):+.0f} лет")
    print(f"GPU median перескок: {med(all_gpu_leaps):+.0f} лет")
    print()

    # Аномалии (модель ниже минимума)
    print("--- АНОМАЛИИ: модель RAM < Min RAM ---")
    for m in matched:
        if m["model_ram"] is not None and m["min_ram"] is not None and m["model_ram"] < m["min_ram"]:
            print(f"  {m['name']} ({m['year']}): модель {m['model_ram']} GB < min {m['min_ram']} GB")
    print()
    print("--- АНОМАЛИИ: модель RAM < Rec RAM ---")
    for m in matched:
        if m["model_ram"] is not None and m["rec_ram"] is not None and m["model_ram"] < m["rec_ram"]:
            print(f"  {m['name']} ({m['year']}): модель {m['model_ram']} GB < rec {m['rec_ram']} GB")
    print()
    print("--- АНОМАЛИИ: модель VRAM < Min VRAM ---")
    for m in matched:
        if m["model_vram"] is not None and m["min_vram"] is not None and m["model_vram"] < m["min_vram"]:
            print(f"  {m['name']} ({m['year']}): модель {m['model_vram']} GB < min {m['min_vram']} GB")
    print()

    # Сохраняем расширенный отчёт
    out_path = AUDIT / "model-vs-real-report.md"
    lines = [
        "# Сравнение оценок модели с реальными требованиями",
        "",
        f"Игр проанализировано: {len(matched)} / {len(results)}",
        "",
        "## По эпохам",
        "",
        "| Эпоха | Игр | RAM med/min | RAM med/rec | VRAM med/min | VRAM med/rec | CPU med leap | GPU med leap |",
        "|-------|-----|-------------|-------------|--------------|--------------|--------------|--------------|",
    ]
    for e in eras:
        st = era_stats[e]
        if st["count"] == 0:
            continue
        lines.append(
            f"| {e} | {st['count']} | "
            f"{med(st['ram_ratios_min']):.1f}x | {med(st['ram_ratios_rec']):.1f}x | "
            f"{med(st['vram_ratios_min']):.1f}x | {med(st['vram_ratios_rec']):.1f}x | "
            f"{med(st['cpu_leaps']):+.0f} | {med(st['gpu_leaps']):+.0f} |"
        )
    lines.extend([
        "",
        "## Полная таблица",
        "",
        "| Игра | Год | RAM модель | RAM min | RAM rec | VRAM модель | VRAM min | VRAM rec | CPU модель | CPU год | GPU модель | GPU год | Bottleneck |",
        "|------|-----|------------|---------|---------|-------------|----------|----------|------------|---------|------------|---------|------------|",
    ])
    for m in matched:
        lines.append(
            f"| {m['name'][:40]} | {m['year']} | "
            f"{fmt(m['model_ram'])} | {fmt(m['min_ram'])} | {fmt(m['rec_ram'])} | "
            f"{fmt(m['model_vram'])} | {fmt(m['min_vram'])} | {fmt(m['rec_vram'])} | "
            f"{fmt_str(m['ref_cpu'])} | {fmt(m['cpu_year'])} | "
            f"{fmt_str(m['ref_gpu'])} | {fmt(m['gpu_year'])} | {fmt_str(m['bottleneck'])} |"
        )
    lines.extend([
        "",
        "## Сводка",
        "",
        f"- RAM median к Min: {med(all_ram_min):.1f}x",
        f"- RAM median к Rec: {med(all_ram_rec):.1f}x",
        f"- VRAM median к Min: {med(all_vram_min):.1f}x",
        f"- VRAM median к Rec: {med(all_vram_rec):.1f}x",
        f"- CPU median перескок: {med(all_cpu_leaps):+.0f} лет",
        f"- GPU median перескок: {med(all_gpu_leaps):+.0f} лет",
        "",
        "### Аномалии (модель ниже требований)",
    ])
    for m in matched:
        if m["model_ram"] is not None and m["min_ram"] is not None and m["model_ram"] < m["min_ram"]:
            lines.append(f"- **RAM < Min**: {m['name']} ({m['year']}): модель {m['model_ram']} GB < min {m['min_ram']} GB")
    for m in matched:
        if m["model_ram"] is not None and m["rec_ram"] is not None and m["model_ram"] < m["rec_ram"]:
            lines.append(f"- **RAM < Rec**: {m['name']} ({m['year']}): модель {m['model_ram']} GB < rec {m['rec_ram']} GB")
    for m in matched:
        if m["model_vram"] is not None and m["min_vram"] is not None and m["model_vram"] < m["min_vram"]:
            lines.append(f"- **VRAM < Min**: {m['name']} ({m['year']}): модель {m['model_vram']} GB < min {m['min_vram']} GB")

    out_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Детальный отчёт сохранён: {out_path}")
    return 0


def fmt(val: float | int | None) -> str:
    return str(val) if val is not None else "—"


def fmt_str(val: str | None) -> str:
    return val[:35] if val else "—"


if __name__ == "__main__":
    sys.exit(main())
