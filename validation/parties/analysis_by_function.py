"""Анализ рекомендаций DSS по функциям игры и взаимному влиянию методов.

Зачем модуль отдельный от ``report.py``: здесь считаются числа, там — только
верстка. Разделение позволяет проверять метрики без перегенерации HTML.

Методологические правила, заложенные в расчёт:

1. **Единица анализа — функция игры**, а не плоский топ-N рекомендаций.
   Метод привязан к функции через ``Method.function_code``; у рекомендации
   ``function_code`` может быть пуст (решение кросс-функциональное), тогда
   функция берётся из каталога, чтобы доля «без функции» не искажала картину.

2. **Никаких причинных выводов из наблюдений.** Всё, что получено сопоставлением
   корзин реальных игр с оценкой, называется *совместной вариацией* и
   помечается в отчёте как наблюдение, а не как доказанный вклад метода.
   Причинность можно утверждать только там, где её задаёт сама модель
   (объявленные связи ``relations.json`` и экспертные коэффициенты влияния).

3. **Исключённые решения видны.** Решения, не связанные с техникой
   (монетизация, дата выхода, сюжет и концовки), отфильтрованы ещё в
   ``build_profiles.py``; здесь они только учитываются в метриках фильтра.

Выход: ``analysis.json`` — consumable для ``report.py``.
"""

from __future__ import annotations

import itertools
import json
import pathlib
import sys
from collections import Counter, defaultdict

HERE = pathlib.Path(__file__).resolve().parent
sys.stdout.reconfigure(encoding="utf-8")

ROWS = json.loads((HERE / "compare.json").read_text(encoding="utf-8"))
RES = json.loads((HERE / "results.json").read_text(encoding="utf-8"))
CAT = json.loads((HERE / "catalog.json").read_text(encoding="utf-8"))
REL = json.loads((HERE / "relations.json").read_text(encoding="utf-8"))
OUT = HERE / "analysis.json"

RESOURCES = ("cpu", "gpu", "ram", "vram", "disk", "network")
#: Значимым считается влияние от 1 балла по шкале −3..+3.
IMPACT_FLOOR = 1

METHOD_FUNCTION = {m["code"]: m["function_code"] for m in CAT["methods"]}
METHOD_NAME = {m["code"]: m["name"] for m in CAT["methods"]}
METHOD_IMPACT = {
    m["code"]: {r: (m.get(f"impact_{r}") or 0) for r in RESOURCES} for m in CAT["methods"]
}
FUNCTIONS = {f["code"]: f for f in CAT["functions"]}

N_GAMES = len(RES)


def func_of_recommendation(rec: dict) -> str | None:
    """Функция рекомендации: из ответа модели или из каталога метода."""
    return rec.get("function_code") or METHOD_FUNCTION.get(rec["method_code"])


# ---------------------------------------------------------------- функции


def analyse_functions() -> list[dict]:
    """Сводка по функциям: кого DSS советует, что реально реализовано.

    По каждой функции считается:
      * ``n_games_rec``   — в скольких играх функция попала в рекомендации;
      * ``n_games_impl``  — в скольких играх функция есть в реализованной корзине;
      * ``hit_rate``      — доля игр, где хотя бы один метод из тройки лучших
                            по функции реально реализован;
      * ``top1_share``    — доля игр, где лучшим по функции назван один и тот же
                            метод (показатель различительной способности:
                            1.0 означает, что ранг не зависит от проекта);
      * ``spread``        — разброс средних баллов между методами функции.
    """
    per_func: dict[str, dict] = defaultdict(
        lambda: {
            "rec_scores": defaultdict(list),
            "games_rec": set(),
            "games_impl": set(),
            "top1": Counter(),
            "hits": 0,
            "rec_pairs": [],
        }
    )

    for g in RES:
        recs = g["recommendations_base"]["recommendations"]
        by_func: dict[str, list[dict]] = defaultdict(list)
        for r in recs:
            f = func_of_recommendation(r)
            if f:
                by_func[f].append(r)
        impl_by_func: dict[str, set[str]] = defaultdict(set)
        for code in g["basket_resolved"]:
            f = METHOD_FUNCTION.get(code)
            if f:
                impl_by_func[f].add(code)

        for f, items in by_func.items():
            slot = per_func[f]
            slot["games_rec"].add(g["id"])
            items.sort(key=lambda r: -r["score"])
            top1_code = items[0]["method_code"]
            slot["top1"][top1_code] += 1
            for r in items:
                slot["rec_scores"][r["method_code"]].append(r["score"])
            top3 = {x["method_code"] for x in items[:3]}
            slot["rec_pairs"].append((g["id"], top3))
            if top3 & impl_by_func.get(f, set()):
                slot["hits"] += 1

        for f, codes in impl_by_func.items():
            per_func[f]["games_impl"].add(g["id"])

    out = []
    for code, slot in per_func.items():
        meta = FUNCTIONS.get(code, {})
        n_rec_games = len(slot["games_rec"])
        game_top1 = Counter()
        # считаем похожесть троек между играми внутри функции
        tops = [t for _, t in slot["rec_pairs"]]
        jac = [
            len(a & b) / len(a | b)
            for a, b in itertools.combinations(tops, 2)
            if a | b
        ]
        mean_scores = {
            m: sum(v) / len(v) for m, v in slot["rec_scores"].items()
        }
        ranked = sorted(mean_scores.items(), key=lambda kv: -kv[1])
        if ranked:
            best_code, best_score = ranked[0]
            worst_score = ranked[-1][1]
        else:
            best_code, best_score, worst_score = None, 0.0, 0.0
        # насколько часто один и тот же метод лучший
        top1_total = sum(slot["top1"].values())
        top1_share = (
            slot["top1"].most_common(1)[0][1] / top1_total if top1_total else 0.0
        )
        out.append(
            {
                "code": code,
                "name": meta.get("name", code),
                "category": meta.get("category", ""),
                "n_methods_catalog": sum(
                    1 for m in CAT["methods"] if m["function_code"] == code
                ),
                "n_games_rec": n_rec_games,
                "n_games_impl": len(slot["games_impl"]),
                "n_distinct_recommended": len(slot["rec_scores"]),
                "hit_rate": round(100.0 * slot["hits"] / n_rec_games, 1) if n_rec_games else 0.0,
                "top1_code": best_code,
                "top1_name": METHOD_NAME.get(best_code or "", ""),
                "top1_share": round(top1_share, 3),
                "jaccard": round(sum(jac) / len(jac), 3) if jac else None,
                "spread": round(best_score - worst_score, 4),
                "best_score": round(best_score, 4),
                "top3": [
                    {
                        "code": c,
                        "name": METHOD_NAME.get(c, c),
                        "score": round(s, 4),
                        "n_games": len(slot["rec_scores"][c]),
                    }
                    for c, s in ranked[:3]
                ],
            }
        )
    out.sort(key=lambda x: (-x["n_games_rec"], x["code"]))
    return out


# ------------------------------------------------------------ влияние методов


def declared_relations() -> dict:
    """Аудит объявленных в каталоге связей между методами."""
    by_type = Counter(r["type"] for r in REL)
    hubs = Counter()
    for r in REL:
        hubs[r["a"]] += 1
        hubs[r["b"]] += 1
    n_methods = len(CAT["methods"])
    n_pairs_possible = n_methods * (n_methods - 1) // 2
    observed = []
    for r in REL:
        both = sum(
            1
            for g in RES
            if r["a"] in g["basket_resolved"] and r["b"] in g["basket_resolved"]
        )
        either = sum(
            1
            for g in RES
            if r["a"] in g["basket_resolved"] or r["b"] in g["basket_resolved"]
        )
        observed.append(
            {
                "a": r["a"],
                "b": r["b"],
                "type": r["type"],
                "severity": r["severity"],
                "description": r["description"],
                "both": both,
                "either": either,
                "share_both_of_either": (round(both / either, 2) if either else None),
            }
        )
    return {
        "n_declared": len(REL),
        "n_pairs_possible": n_pairs_possible,
        "coverage_pct": round(100.0 * len(REL) / n_pairs_possible, 3),
        "by_type": dict(by_type),
        "hubs": [
            {"code": c, "name": METHOD_NAME.get(c, c), "n": n}
            for c, n in hubs.most_common(8)
        ],
        "observed": observed,
    }


def footprint_pairs(limit: int = 12) -> dict:
    """Пересечение ресурсных следов методов — кандидаты в связи каталога.

    Считается по экспертным коэффициентам влияния (шкала −3..+3):
      * ``contention`` — оба метода нагружают один ресурс (однонаправленно);
      * ``synergy``    — оба метод снижают нагрузку на один ресурс;
      * ``offset``     — влияние на один ресурс противоположно по знаку.
    Это свойства модели, а не измерения: пара с высоким ``contention`` —
    кандидат на проверку, а не доказанный конфликт.
    """
    declared = {frozenset((r["a"], r["b"])) for r in REL}
    rows = []
    for a, b in itertools.combinations(sorted(METHOD_IMPACT), 2):
        ia, ib = METHOD_IMPACT[a], METHOD_IMPACT[b]
        contention = synergy = offset = 0
        shared = []
        for r in RESOURCES:
            va, vb = ia[r], ib[r]
            if abs(va) < IMPACT_FLOOR or abs(vb) < IMPACT_FLOOR:
                continue
            shared.append(r)
            if va > 0 and vb > 0:
                contention += 1
            elif va < 0 and vb < 0:
                synergy += 1
            elif va * vb < 0:
                offset += 1
        if not shared:
            continue
        rows.append(
            {
                "a": a,
                "b": b,
                "a_name": METHOD_NAME[a],
                "b_name": METHOD_NAME[b],
                "shared": shared,
                "contention": contention,
                "synergy": synergy,
                "offset": offset,
                "declared": frozenset((a, b)) in declared,
            }
        )
    contention_top = sorted(
        (r for r in rows if r["contention"]), key=lambda r: (-r["contention"], r["a"])
    )[:limit]
    synergy_top = sorted(
        (r for r in rows if r["synergy"]), key=lambda r: (-r["synergy"], r["a"])
    )[:limit]
    return {
        "n_pairs_with_shared_resource": len(rows),
        "n_declared_overlap": sum(1 for r in rows if r["declared"]),
        "contention_top": contention_top,
        "synergy_top": synergy_top,
    }


def cooccurrence(limit: int = 15) -> dict:
    """Совместная встречаемость методов в корзинах 58 реальных игр.

    Это наблюдение:_pair встречается в корзинах чаще остального. Причину
    (общая предметная область, зависимость, мода эпохи) данные не устанавливают.
    """
    pair_counter = Counter()
    method_counter = Counter()
    for g in RES:
        codes = sorted(set(g["basket_resolved"]))
        method_counter.update(codes)
        for a, b in itertools.combinations(codes, 2):
            pair_counter[(a, b)] += 1
    declared = {frozenset((r["a"], r["b"])) for r in REL}
    top = [
        {
            "a": a,
            "b": b,
            "a_name": METHOD_NAME.get(a, a),
            "b_name": METHOD_NAME.get(b, b),
            "n": n,
            "declared": frozenset((a, b)) in declared,
        }
        for (a, b), n in pair_counter.most_common(limit)
    ]
    return {
        "n_methods_used": len(method_counter),
        "n_pairs_observed": len(pair_counter),
        "top": top,
        "most_used": [
            {"code": c, "name": METHOD_NAME.get(c, c), "n_games": n}
            for c, n in method_counter.most_common(15)
        ],
    }


def association(min_games: int = 5) -> list[dict]:
    """Совместная вариация «метод в корзине» ↔ «оценка оборудования».

    Сравниваются игры, у которых метод есть в корзине, с играми, у которых его
    нет. Разница средних по Δ (корзина минус базовый профиль) показывает не
    вклад метода, а *наблюдаемую связь*: корзины — множества, и метод приходит
    не один. Вывод формулируется только как гипотеза для проверки.
    """
    deltas = ("d_cpu_index", "d_gpu_index", "d_ram_gb", "d_vram_gb")
    presence: dict[str, list[dict]] = defaultdict(list)
    rows_by_id = {r["id"]: r for r in ROWS}
    for g in RES:
        row = rows_by_id.get(g["id"])
        if not row:
            continue
        for code in sorted(set(g["basket_resolved"])):
            presence[code].append(row)
    absent_universe = list(ROWS)
    out = []
    for code, rows_with in presence.items():
        n_with = len(rows_with)
        if n_with < min_games or n_with > N_GAMES - min_games:
            continue
        rec = {"code": code, "name": METHOD_NAME.get(code, code), "n_games": n_with}
        for d in deltas:
            w = [r[d] for r in rows_with if r.get(d) is not None]
            wo = [r[d] for r in absent_universe if r.get(d) is not None]
            if not w or not wo:
                continue
            mw = sum(w) / len(w)
            mo = sum(wo) / len(wo)
            rec[d] = {
                "with": round(mw, 4),
                "without": round(mo, 4),
                "diff": round(mw - mo, 4),
            }
        if any(k in rec for k in deltas):
            out.append(rec)
    # сортировка по модулю различия по GPU — самому показательному ресурсу
    out.sort(key=lambda r: -abs(r.get("d_gpu_index", {}).get("diff", 0)))
    return out


def main() -> None:
    functions = analyse_functions()
    rel = declared_relations()
    foot = footprint_pairs()
    cooc = cooccurrence()
    assoc = association()

    n_dec = sum(r["n_decisions"] for r in ROWS)
    n_tech = sum(r.get("n_technical", r["n_decisions"]) for r in ROWS)
    n_exc = sum(r.get("n_excluded", 0) for r in ROWS)
    n_rev = sum(r.get("n_review", 0) for r in ROWS)
    n_match = sum(r["n_decisions_matched"] for r in ROWS)

    excl_cat = Counter()
    for g in RES:
        for e in g.get("excluded", []):
            excl_cat[e.get("category", "прочее")] += 1

    payload = {
        "meta": {
            "n_games": N_GAMES,
            "n_decisions": n_dec,
            "n_technical": n_tech,
            "n_excluded": n_exc,
            "n_review": n_rev,
            "n_matched": n_match,
            "coverage_technical_pct": round(100.0 * n_match / n_tech, 1) if n_tech else 0.0,
            "coverage_all_pct": round(100.0 * n_match / n_dec, 1) if n_dec else 0.0,
            "excluded_by_category": dict(excl_cat.most_common()),
            "n_methods_catalog": len(CAT["methods"]),
            "n_functions_catalog": len(CAT["functions"]),
        },
        "functions": functions,
        "relations": rel,
        "footprint": foot,
        "cooccurrence": cooc,
        "association": assoc,
    }
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")

    print(f"функций в разборе: {len(functions)}")
    print(
        f"решений {n_dec}, технических {n_tech}, исключено {n_exc}, на разбор {n_rev}, "
        f"сопоставлено {n_match} ({payload['meta']['coverage_technical_pct']}%)"
    )
    print(f"связей в каталоге: {rel['n_declared']} из {rel['n_pairs_possible']} возможных пар")
    print(f"записано: {OUT}")


if __name__ == "__main__":
    main()
