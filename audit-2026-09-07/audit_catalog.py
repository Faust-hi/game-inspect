# -*- coding: utf-8 -*-
"""Аудит каталога: полнота и непротиворечивость карточек методов."""
from __future__ import annotations

import json
import sqlite3
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "backend" / "gamedev_dss.db"
conn = sqlite3.connect(DB)
conn.row_factory = sqlite3.Row

CARD_FIELDS = [
    "summary", "description", "problem", "pros", "cons", "limitations",
    "application_steps", "verification_method", "verification_tools",
]
IMPACT_FIELDS = ["impact_cpu", "impact_gpu", "impact_ram", "impact_vram",
                 "impact_disk", "impact_network", "quality_impact",
                 "concept_impact", "performance_gain", "implementation_cost",
                 "complexity", "confidence"]

methods = [dict(r) for r in conn.execute("select * from methods")]
functions = [r[0] for r in conn.execute("select code from game_functions order by code")]
conflicts = [dict(r) for r in conn.execute("select * from conflicts")]
links = [dict(r) for r in conn.execute("select * from method_engine_links")]

print("=" * 78)
print("СОСТАВ КАТАЛОГА")
print("=" * 78)
print(f"Методов: {len(methods)}, функций: {len(functions)}, конфликтов: {len(conflicts)}, "
      f"связей с движками: {len(links)}")
print("\nФункции в базе:")
print("  " + ", ".join(functions))

# Словарь парсера партий шире каталога — показываем расхождение.
sys_path = ROOT / "audit-2026-09-07"
import sys  # noqa: E402
sys.path.insert(0, str(sys_path))
import run_batches as rb  # noqa: E402

extra = sorted(set(rb.VALID_FUNCTIONS) - set(functions))
print(f"\nКодов в списке парсера, которых НЕТ в базе ({len(extra)}):")
print("  " + ", ".join(extra))

print("\n" + "=" * 78)
print("1. ЗАПОЛНЕННОСТЬ КАРТОЧЕК")
print("=" * 78)
for f in CARD_FIELDS:
    empty = [m["code"] for m in methods if not (m.get(f) or "").strip()]
    flag = "  <-- ПУСТО" if empty else ""
    print(f"{f:<22} незаполнено {len(empty):>3} из {len(methods)}{flag}")
    if empty and len(empty) <= 12:
        print(f"{'':<22} {', '.join(empty)}")

print("\n" + "=" * 78)
print("2. ЧИСЛОВЫЕ ПОКАЗАТЕЛИ")
print("=" * 78)
for f in IMPACT_FIELDS:
    vals = [(m.get(f) or 0) for m in methods]
    zeros = sum(1 for v in vals if v == 0)
    print(f"{f:<22} нулей {zeros:>3}/{len(vals)}  мин {min(vals):+.2f} макс {max(vals):+.2f}")
all_zero = [m["code"] for m in methods
            if not any((m.get(f) or 0) for f in ["impact_cpu", "impact_gpu", "impact_ram",
                                                 "impact_vram", "impact_disk", "impact_network"])]
print(f"\nМетодов вообще без воздействия на подсистемы: {len(all_zero)}")
if all_zero:
    print("  " + ", ".join(all_zero))

print("\n" + "=" * 78)
print("3. ПРИВЯЗКА К ФУНКЦИЯМ")
print("=" * 78)
no_fn = [m["code"] for m in methods if not m.get("function_id")]
print(f"Методов без функции: {len(no_fn)}")
if no_fn:
    print("  " + ", ".join(no_fn))
by_fn = Counter(m["function_id"] for m in methods)
fn_names = {r[0]: r[1] for r in conn.execute("select id, code from game_functions")}
print("\nМетодов на функцию:")
for fn, cnt in sorted(by_fn.items(), key=lambda kv: -kv[1]):
    print(f"  {fn_names.get(fn, fn)}: {cnt}")
empty_fn = [fn_names[i] for i in fn_names if i not in by_fn]
print(f"\nФункций без единого метода ({len(empty_fn)}): " + ", ".join(empty_fn))

print("\n" + "=" * 78)
print("4. СТАДИИ И СТОИМОСТЬ ВНЕДРЕНИЯ")
print("=" * 78)
print("Рекомендуемая стадия:", dict(Counter(m["recommended_stage"] for m in methods).most_common()))
print("Цена позднего внедрения:", dict(Counter(m["late_cost"] for m in methods).most_common()))
print("Уровень решения:", dict(Counter(m["level"] for m in methods).most_common()))
print("Область эффекта:", dict(Counter(m["effect_scope"] for m in methods).most_common()))
print("Статус публикации:", dict(Counter(m["status"] for m in methods).most_common()))

print("\n" + "=" * 78)
print("5. КОНФЛИКТЫ: НЕПРОТИВОРЕЧИВОСТЬ")
print("=" * 78)
codes = {m["code"] for m in methods}
print("Типы связей в базе:", dict(Counter(c["conflict_type"] for c in conflicts).most_common()))
print("Серьёзность (severity):", dict(Counter(c["severity"] for c in conflicts).most_common()))

import sys as _sys  # noqa: E402
_sys.path.insert(0, str(ROOT / "backend"))
from app.models.enums import ConflictType  # noqa: E402

enum_values = {t.value for t in ConflictType}
db_values = {c["conflict_type"] for c in conflicts}
off_enum = sorted(db_values - enum_values)
print(f"\nЗначений conflict_type, которых НЕТ в перечислении ConflictType: {len(off_enum)}")
print("  в базе:", sorted(db_values))
print("  в коде:", sorted(enum_values))
if off_enum:
    print("  НЕСОВМЕСТИМО: " + ", ".join(off_enum))

unknown = [c for c in conflicts if c["a_code"] not in codes or c["b_code"] not in codes]
print(f"\nСвязей с неизвестным кодом метода: {len(unknown)}")
for c in unknown[:10]:
    print(f"  {c['a_code']} <-> {c['b_code']} ({c['conflict_type']})")
self_c = [c for c in conflicts if c["a_code"] == c["b_code"]]
print(f"Связей метода с самим собой: {len(self_c)}")

pair_types = defaultdict(set)
for c in conflicts:
    pair_types[frozenset((c["a_code"], c["b_code"]))].add(c["conflict_type"])
dup_pairs = {p: sorted(t) for p, t in pair_types.items() if len(t) > 1}
print(f"\nПар с противоречивыми типами одновременно: {len(dup_pairs)}")
for p, t in list(dup_pairs.items())[:10]:
    print(f"  {' <-> '.join(sorted(p))}: {', '.join(t)}")

in_conf = set()
for c in conflicts:
    in_conf.add(c["a_code"])
    in_conf.add(c["b_code"])
print(f"\nМетодов, не участвующих ни в одной связи: {len(codes - in_conf)}")
print("  " + ", ".join(sorted(codes - in_conf)))

print("\n" + "=" * 78)
print("6. ОГРАНИЧЕНИЯ ПРИМЕНИМОСТИ")
print("=" * 78)
LIST_FIELDS = ["applicable_formats", "applicable_world_types", "applicable_engines",
               "applicable_platforms", "requires_features", "requires_hw_features"]


def as_list(raw):
    if raw is None:
        return []
    if isinstance(raw, list):
        return raw
    raw = raw.strip()
    if not raw:
        return []
    try:
        parsed = json.loads(raw)
        return parsed if isinstance(parsed, list) else [parsed]
    except ValueError:
        return [t.strip() for t in raw.replace(";", ",").split(",") if t.strip()]


print(f"{'поле':<24} пусто / всего   (пусто = ограничение не задано)")
for f in LIST_FIELDS + ["min_scale", "requires_conditions"]:
    empty = sum(1 for m in methods if not (as_list(m.get(f)) if f in LIST_FIELDS
                                           else (m.get(f) or "").strip()))
    print(f"{f:<24} {empty:>3} из {len(methods)}")

print("\n--- requires_features: ссылки на несуществующие функции ---")
bad_features = []
for m in methods:
    for tok in as_list(m.get("requires_features")):
        if tok not in functions:
            bad_features.append((m["code"], tok))
print(f"Таких ссылок: {len(bad_features)}")
for mc, tok in sorted(bad_features)[:20]:
    print(f"  {mc} -> {tok}")

print("\n--- requires_features: требуют функцию, которой нет в их же привязке ---")
fn_by_id = {r[0]: r[1] for r in conn.execute("select id, code from game_functions")}
mismatch = []
for m in methods:
    own = fn_by_id.get(m["function_id"])
    reqs = set(as_list(m.get("requires_features")))
    extra_req = reqs - {own}
    if extra_req:
        mismatch.append((m["code"], own, sorted(extra_req)))
print(f"Методов, требующих дополнительные функции: {len(mismatch)}")
for mc, own, reqs in mismatch[:20]:
    print(f"  {mc} (функция {own}) требует: {', '.join(reqs)}")

print("\n--- методы, требующие функцию, которой мало где есть методов ---")
for mc, own, reqs in mismatch:
    pass

print("\n" + "=" * 78)
print("7. ДУБЛИКАТЫ И ОДНООБРАЗИЕ")
print("=" * 78)
same_pros = defaultdict(list)
for m in methods:
    key = (m.get("pros") or "").strip().lower()
    if key:
        same_pros[key].append(m["code"])
dups = {k: v for k, v in same_pros.items() if len(v) > 1}
print(f"Групп методов с дословно одинаковыми «плюсами»: {len(dups)}")
for k, v in list(dups.items())[:6]:
    print(f"  ({len(v)} шт.) {', '.join(v[:6])}")
    print(f"     текст: {k[:110]}")

same_cons = defaultdict(list)
for m in methods:
    key = (m.get("cons") or "").strip().lower()
    if key:
        same_cons[key].append(m["code"])
dups_c = {k: v for k, v in same_cons.items() if len(v) > 1}
print(f"\nГрупп методов с дословно одинаковыми «минусами»: {len(dups_c)}")
for k, v in list(dups_c.items())[:6]:
    print(f"  ({len(v)} шт.) {', '.join(v[:6])}")
    print(f"     текст: {k[:110]}")

print("\n" + "=" * 78)
print("8. ИСТОЧНИКИ")
print("=" * 78)
no_url = [m["code"] for m in methods if not (m.get("source_url") or "").strip()]
print(f"Методов без source_url: {len(no_url)}")
if no_url:
    print("  " + ", ".join(no_url))
not_published = [m["code"] for m in methods if m.get("status") != "published"]
print(f"Методов со статусом, отличным от published: {len(not_published)}")
if not_published:
    print("  " + ", ".join(not_published))
