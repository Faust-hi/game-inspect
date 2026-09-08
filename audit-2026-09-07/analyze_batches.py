# -*- coding: utf-8 -*-
"""Анализ результатов прогона партий: разброс железа и итоги по решениям."""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
data = json.loads((ROOT / "audit-2026-09-07" / "batch-run-results.json").read_text(encoding="utf-8"))


def stats(values: list[float]) -> dict:
    vs = sorted(v for v in values if v is not None)
    if not vs:
        return {}
    n = len(vs)
    mid = n // 2
    median = vs[mid] if n % 2 else (vs[mid - 1] + vs[mid]) / 2
    return {
        "min": vs[0], "max": vs[-1],
        "median": median,
        "p25": vs[n // 4], "p75": vs[3 * n // 4],
    }


def fmt(v, nd=1):
    return f"{v:.{nd}f}" if isinstance(v, float) else str(v)


hw = [r["hardware"] for r in data]
games = [r["game"] for r in data]

print("=" * 78)
print("РАЗБРОС АППАРАТНЫХ ТРЕБОВАНИЙ (58 игр, пустая корзина, стадия release)")
print("=" * 78)

for key, label, nd in [
    ("gpu_class", "Класс GPU (1-5)", 0),
    ("cpu_class", "Класс CPU (1-5)", 0),
    ("vram_gb", "VRAM, ГБ", 1),
    ("ram_gb", "RAM, ГБ", 1),
    ("required_gpu_index", "Индекс GPU (доля от RTX 4090)", 3),
    ("required_cpu_index", "Индекс CPU", 3),
]:
    s = stats([h[key] for h in hw])
    if not s:
        continue
    print(f"\n{label}:")
    print(f"  мин {fmt(s['min'], nd)} · медиана {fmt(s['median'], nd)} · "
          f"макс {fmt(s['max'], nd)}  (p25 {fmt(s['p25'], nd)} / p75 {fmt(s['p75'], nd)})")

# Распределение классов
print("\nРаспределение классов GPU:", dict(sorted(Counter(h["gpu_class"] for h in hw).items())))
print("Распределение классов CPU:", dict(sorted(Counter(h["cpu_class"] for h in hw).items())))
print("Узкие места:", dict(Counter(h["bottleneck"] for h in hw if h["bottleneck"]).most_common()))
print("Выход за каталог:", sum(1 for h in hw if h["exceeds"]), "из", len(hw))

# Экстремумы
print("\n--- Экстремумы ---")
by_gpu = sorted(data, key=lambda r: (r["hardware"]["required_gpu_index"] or 0))
print("\nСамые лёгкие (индекс GPU):")
for r in by_gpu[:5]:
    h = r["hardware"]
    print(f"  {r['game']['name']} ({r['game']['year']}): GPU {h['reference_gpu'] or '—'}, "
          f"инд. {fmt(h['required_gpu_index'], 3)}, VRAM {fmt(h['vram_gb'])} ГБ")
print("\nСамые тяжёлые (индекс GPU):")
for r in by_gpu[-5:]:
    h = r["hardware"]
    print(f"  {r['game']['name']} ({r['game']['year']}): GPU {h['reference_gpu'] or '—'}, "
          f"инд. {fmt(h['required_gpu_index'], 3)}, VRAM {fmt(h['vram_gb'])} ГБ")

# Разброс reference GPU моделей
print("\n--- Подобранные референсные GPU (уникальные модели) ---")
gpu_models = Counter(h["reference_gpu"] for h in hw if h["reference_gpu"])
for model, cnt in gpu_models.most_common():
    print(f"  {model}: {cnt}")

print("\n--- Подобранные референсные CPU (уникальные модели) ---")
cpu_models = Counter(h["reference_cpu"] for h in hw if h["reference_cpu"])
for model, cnt in cpu_models.most_common():
    print(f"  {model}: {cnt}")

# Итоги по решениям
print("\n" + "=" * 78)
print("ИТОГИ ПО РЕШЕНИЯМ")
print("=" * 78)

all_recs = Counter()
for r in data:
    for rec in r["recommendations"]:
        all_recs[rec["name"]] += 1

print(f"\nВсего выдано рекомендаций (топ-8 на игру): {sum(all_recs.values())}")
print(f"Уникальных решений в топах: {len(all_recs)}")
print("\nЧаще всего в топ-8:")
for name, cnt in all_recs.most_common(15):
    print(f"  {cnt:3d}× {name}")

# Стабильность топ-1
top1 = Counter(r["recommendations"][0]["name"] for r in data if r["recommendations"])
print("\nКто занимает первое место:")
for name, cnt in top1.most_common(10):
    print(f"  {cnt:3d}× {name}")

# Средние показатели
print("\n--- Сводка ---")
avg_recs = sum(len(r["recommendations"]) for r in data) / len(data)
avg_excl = sum(r["excluded_count"] for r in data) / len(data)
avg_risks = sum(r["risks_count"] for r in data) / len(data)
print(f"Среднее число рекомендаций в топ-8: {avg_recs:.1f}")
print(f"Среднее число исключённых решений: {avg_excl:.1f}")
print(f"Среднее число рисков: {avg_risks:.1f}")

# Детальная таблица по играм
print("\n" + "=" * 78)
print("ДЕТАЛЬНАЯ ТАБЛИЦА")
print("=" * 78)
print(f"{'Игра':<38} {'Год':<5} {'GPU класс':<9} {'CPU кл.':<8} {'VRAM':<6} {'RAM':<6} {'Узкое место'}")
print("-" * 100)
for r in sorted(data, key=lambda r: (r["hardware"]["required_gpu_index"] or 0)):
    g, h = r["game"], r["hardware"]
    name = g["name"][:36]
    print(f"{name:<38} {g['year']:<5} {str(h['gpu_class']):<9} {str(h['cpu_class']):<8} "
          f"{fmt(h['vram_gb']):<6} {fmt(h['ram_gb']):<6} {h['bottleneck'] or '—'}")
