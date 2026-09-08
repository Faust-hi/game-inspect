# -*- coding: utf-8 -*-
"""Углублённый разбор прогона партий: насколько модель различает игры."""
from __future__ import annotations

import json
import statistics as st
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
data = json.loads((ROOT / "audit-2026-09-07" / "batch-run-results.json").read_text(encoding="utf-8"))
ok = [r for r in data if "error" not in r]

print("=" * 78)
print("1. ГЛУБИНА ДИФФЕРЕНЦИАЦИИ РЕШЕНИЙ")
print("=" * 78)

lens = [len(r["all_recommendations"]) for r in ok]
print(f"Длина полного списка рекомендаций: мин {min(lens)} · медиана {st.median(lens):.0f} · макс {max(lens)}")

all_codes = Counter()
for r in ok:
    for rec in r["all_recommendations"]:
        all_codes[rec["name"]] += 1
print(f"Уникальных решений во ВСЕХ списках: {len(all_codes)}")
print(f"Решений, встречающихся во всех {len(ok)} играх: "
      f"{sum(1 for v in all_codes.values() if v == len(ok))}")

# Доля каталога, которая вообще участвует в расчёте
touched = set()
for r in ok:
    touched.update(rec["code"] for rec in r["all_recommendations"])
    touched.update(r["all_excluded"])
print(f"Методов каталога, попавших в расчёт (рекомендации + исключённые): {len(touched)}")

print("\n--- Разница баллов внутри топа (устойчивость ранжирования) ---")
gaps_top2, spans = [], []
for r in ok:
    sc = [x["score"] for x in r["all_recommendations"]]
    if len(sc) >= 2:
        gaps_top2.append(sc[0] - sc[1])
    if sc:
        spans.append(sc[0] - sc[-1])
print(f"Отрыв 1-го места от 2-го: медиана {st.median(gaps_top2):.4f} · "
      f"мин {min(gaps_top2):.4f} · макс {max(gaps_top2):.4f}")
print(f"Размах баллов внутри списка: медиана {st.median(spans):.4f} · макс {max(spans):.4f}")
print(f"Игр с отрывом 1-го места < 0.01: {sum(1 for g in gaps_top2 if g < 0.01)} из {len(gaps_top2)}")

print("\n--- Топ-1 по играм ---")
for name, cnt in Counter(r["all_recommendations"][0]["name"] for r in ok if r["all_recommendations"]).most_common():
    print(f"  {cnt:3d}× {name}")

print("\n" + "=" * 78)
print("2. ПРАВДОПОДОБНОСТЬ АППАРАТНОЙ ОЦЕНКИ")
print("=" * 78)

years = [r["game"]["year"] for r in ok]
gpu = [r["hardware"]["required_gpu_index"] for r in ok]
cpu = [r["hardware"]["required_cpu_index"] for r in ok]
vram = [r["hardware"]["vram_gb"] for r in ok]
ram = [r["hardware"]["ram_gb"] for r in ok]


def corr(a, b):
    ma, mb = st.mean(a), st.mean(b)
    num = sum((x - ma) * (y - mb) for x, y in zip(a, b))
    den = (sum((x - ma) ** 2 for x in a) * sum((y - mb) ** 2 for y in b)) ** 0.5
    return num / den if den else 0.0


print(f"Корреляция «год выпуска ↔ индекс GPU»: {corr(years, gpu):+.3f}")
print(f"Корреляция «год выпуска ↔ индекс CPU»: {corr(years, cpu):+.3f}")
print(f"Корреляция «год выпуска ↔ VRAM»:       {corr(years, vram):+.3f}")
print(f"Корреляция «год выпуска ↔ RAM»:        {corr(years, ram):+.3f}")

print(f"\nДинамический диапазон: GPU {min(gpu):.3f}–{max(gpu):.3f} "
      f"(×{max(gpu)/min(gpu):.1f}), CPU {min(cpu):.3f}–{max(cpu):.3f} (×{max(cpu)/min(cpu):.1f})")
print(f"                       VRAM ×{max(vram)/min(vram):.1f}, RAM ×{max(ram)/min(ram):.1f}")

print("\n--- Одинаковые аппараты профили (сколько игр делят один результат) ---")
sig = Counter((h["reference_gpu"], h["reference_cpu"], round(h["vram_gb"], 1), round(h["ram_gb"], 1))
              for h in (r["hardware"] for r in ok))
print(f"Уникальных «аппаратных ответов» на 58 игр: {len(sig)}")
for k, c in sig.most_common(6):
    print(f"  {c:2d}× {k[0]} + {k[1]}, VRAM {k[2]}, RAM {k[3]}")

print("\n--- Год против места в рейтинге тяжести (проверка на артефакты) ---")
order = sorted(ok, key=lambda r: r["hardware"]["required_gpu_index"])
print("Топ-5 самых лёгких:", ", ".join(f"{r['game']['name']} ({r['game']['year']})" for r in order[:5]))
print("Топ-5 самых тяжёлых:", ", ".join(f"{r['game']['name']} ({r['game']['year']})" for r in order[-5:]))

print("\n--- Уверенность модели и оговорки ---")
print("Метка уверенности:", dict(Counter(r["hardware"]["confidence_label"] for r in ok).most_common()))
print(f"Игр с невыполненными ограничениями: {sum(1 for r in ok if r['hardware']['unmet_limits'])}")
print(f"Игр с выходом за каталог: {sum(1 for r in ok if r['hardware']['exceeds'])}")
print("Накопитель:", dict(Counter(r["hardware"]["storage"] for r in ok).most_common()))
print("\nУзкое место:", dict(Counter(r["hardware"]["bottleneck"] for r in ok).most_common()))

print("\n" + "=" * 78)
print("3. СВЯЗКА «ЖЕЛЕЗО ↔ РЕШЕНИЯ»")
print("=" * 78)
print("Есть ли игра, где топ-1 отличается от доминирующего решения?")
dom = Counter(r["all_recommendations"][0]["name"] for r in ok if r["all_recommendations"]).most_common(1)[0][0]
others = [(r["game"]["name"], r["all_recommendations"][0]["name"],
           r["hardware"]["reference_gpu"], r["hardware"]["bottleneck"])
          for r in ok if r["all_recommendations"] and r["all_recommendations"][0]["name"] != dom]
print(f"Доминирующее решение: «{dom}» ({len(ok) - len(others)}/{len(ok)})")
for name, top, g, b in others:
    print(f"  {name}: топ-1 «{top}», GPU {g}, узкое место {b}")
