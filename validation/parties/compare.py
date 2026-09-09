"""Сравнение результатов прогона: железо + инженерные решения.

Дополнительно выполняется сверка с реальными «Rec HW» из инженерных паспортов
партий: модель GPU из паспорта ищется в каталоге оборудования DSS, её
raster_score сравнивается с требуемым индексом, который выдал расчёт.

Выход: validation/parties/compare.json (строки сводной таблицы)
"""

from __future__ import annotations

import json
import os
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
BACKEND = HERE.parents[1] / "backend"
sys.path.insert(0, str(BACKEND))
sys.stdout.reconfigure(encoding="utf-8")

os.environ.setdefault("AUTO_SEED", "false")
os.environ.setdefault("DATABASE_URL", f"sqlite:///{(BACKEND / 'gamedev_dss.db').as_posix()}")

from app.database import SessionLocal  # noqa: E402
from app.models.entities import HardwareGPU  # noqa: E402

RESULTS = json.loads((HERE / "results.json").read_text(encoding="utf-8"))
OUT = HERE / "compare.json"

GPU_RX = re.compile(
    r"(RTX\s*\d{4}\s*(?:Ti|Super)?|GTX\s*\d{3,4}\s*(?:Ti|Super)?|GT\s*\d{3,4}|"
    r"RX\s*\d{4}\s*(?:XT|GRE)?|Radeon\s+(?:HD\s+)?\d{4}\s*(?:XT)?|"
    r"Arc\s*A\d{3}|Vega\s*\d{2}|Radeon\s+R\d\s+\w+)",
    re.I,
)


def norm(model: str) -> str:
    m = model.lower()
    m = re.sub(r"\(.*?\)", "", m)
    m = m.replace("geforce", "").replace("nvidia", "").replace("amd", "")
    m = m.replace("radeon", "").replace("graphics", "")
    m = re.sub(r"\s+", " ", m).strip()
    m = re.sub(r"[^a-z0-9 ]", "", m)
    return m


def build_gpu_index(session) -> dict[str, dict]:
    idx = {}
    for g in session.query(HardwareGPU).all():
        idx[norm(g.model)] = {
            "model": g.model,
            "raster_score": g.raster_score,
            "rt_score": g.rt_score,
            "perf_class": g.perf_class,
            "vram_gb": g.vram_gb,
            "release_year": g.release_year,
        }
    return idx


def find_real_gpu(hw_rows: list[dict], gpu_idx: dict) -> dict | None:
    """Найти в паспорте строку Rec HW и сопоставить её GPU с каталогом."""
    fallback = None
    for row in hw_rows:
        for key, val in row.items():
            if not key.lower().startswith("rec hw"):
                continue
            for cand in GPU_RX.findall(val):
                n = norm(cand.strip())
                if n in gpu_idx:
                    return {"source": f"{key}: {val}"[:160], **gpu_idx[n]}
                for k, v in gpu_idx.items():
                    if k.startswith(n) or n.startswith(k):
                        return {"source": f"{key}: {val}"[:160], **v}
                if fallback is None:
                    fallback = {"source": f"{key}: {val}"[:160], "model": cand.strip()}
    return fallback


def main() -> None:
    session = SessionLocal()
    gpu_idx = build_gpu_index(session)
    session.close()

    rows = []
    for r in RESULTS:
        eb = r["estimate_base"]
        ek = r["estimate_basket"]
        load = r["load"] or {}
        rec_base = r["recommendations_base"]
        rec_basket = r["recommendations_basket"]
        recs = rec_base.get("recommendations") or []
        top10 = [x["method_code"] for x in recs[:10]]
        basket = set(r["basket_resolved"])
        hit10 = [c for c in top10 if c in basket]
        real = find_real_gpu(r["hw_passport"], gpu_idx)
        dev = None
        if real and real.get("raster_score") is not None:
            dev = round(eb["required_gpu_index"] - float(real["raster_score"]), 3)
        n_dm = r.get("n_decisions_matched", r["n_matched"])
        rows.append(
            {
                "id": r["id"],
                "party": r["party"],
                "title": r["title"],
                "year": r["year"],
                "engine": r["engine_dss"],
                "engine_raw": r["engine_raw"],
                "world": r["profile"]["world_type"],
                "scale": r["profile"]["scale"],
                "target": f"{r['profile']['target_resolution']}/{r['profile']['target_fps']}",
                "api": r["profile"]["render_api"],
                # --- железо: базовая оценка ---
                "cpu_ref": (eb.get("reference_cpu") or {}).get("model"),
                "cpu_class": eb.get("cpu_class"),
                "gpu_ref": (eb.get("reference_gpu") or {}).get("model"),
                "gpu_class": eb.get("gpu_class"),
                "cpu_index": eb.get("required_cpu_index"),
                "gpu_index": eb.get("required_gpu_index"),
                "ram_gb": eb.get("estimated_ram_gb"),
                "vram_gb": eb.get("estimated_vram_gb"),
                "bottleneck": eb.get("bottleneck_label") or eb.get("bottleneck"),
                "confidence": eb.get("confidence_label"),
                # --- эффект реализованных решений ---
                "d_cpu_index": round(
                    ek["required_cpu_index"] - eb["required_cpu_index"], 4
                ),
                "d_gpu_index": round(
                    ek["required_gpu_index"] - eb["required_gpu_index"], 4
                ),
                "d_ram_gb": round((ek.get("estimated_ram_gb") or 0) - (eb.get("estimated_ram_gb") or 0), 1),
                "d_vram_gb": round((ek.get("estimated_vram_gb") or 0) - (eb.get("estimated_vram_gb") or 0), 1),
                "load_cpu": (load or {}).get("cpu"),
                "load_gpu": (load or {}).get("gpu"),
                "load_ram": (load or {}).get("ram"),
                "load_vram": (load or {}).get("vram"),
                "non_client": len(eb.get("non_client_methods") or []) if eb.get("non_client_methods") else 0,
                # --- инженерные решения ---
                # Покрытие считается по техническим решениям: монетизация,
                # дата выхода, сюжетные развилки и концовки в знаменателе
                # означали бы «пробел каталога» там, где его нет.
                "n_decisions": r["n_decisions"],
                "n_technical": r.get("n_technical", r["n_decisions"]),
                "n_excluded": r.get("n_excluded", 0),
                "n_review": r.get("n_review", 0),
                "n_matched": r["n_matched"],
                "n_decisions_matched": n_dm,
                "coverage": (
                    round(100.0 * n_dm / r["n_technical"], 1)
                    if r.get("n_technical") else 0.0
                ),
                "basket_size": len(basket),
                "n_recs": len(recs),
                "top10": top10,
                "top10_hit": len(hit10),
                "hit_codes": hit10,
                "risks": [
                    {"code": x.get("code"), "title": x.get("title"), "severity": x.get("severity")}
                    for x in (rec_base.get("risks") or [])
                ],
                "recs_after": len(rec_basket.get("recommendations") or []),
                "caveats": eb.get("caveats") or [],
                # --- сверка с реальным Rec HW ---
                "real_gpu": real.get("model") if real else None,
                "real_gpu_score": real.get("raster_score") if real else None,
                "real_gpu_src": real.get("source") if real else None,
                "gpu_deviation": dev,
            }
        )
    OUT.write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")

    print(f"{'игра':44s} {'CPU':16s} {'GPU':22s} {'iGPU':>6s} {'RAM':>5s} {'VRAM':>5s} "
          f"{'узк.':16s} {'реш':>4s} {'покр%':>6s} {'топ10':>5s} {'реал.GPU':16s} {'откл':>6s}")
    for r in sorted(rows, key=lambda x: -(x["gpu_index"] or 0)):
        print(
            f"{r['title'][:43]:44s} {str(r['cpu_ref'])[:15]:16s} {str(r['gpu_ref'])[:21]:22s} "
            f"{r['gpu_index']:6.3f} {r['ram_gb']:5.1f} {r['vram_gb']:5.1f} "
            f"{str(r['bottleneck'])[:15]:16s} {r['n_matched']:4d} {r['coverage']:6.1f} "
            f"{r['top10_hit']:5d} {str(r['real_gpu'])[:15]:16s} "
            f"{'' if r['gpu_deviation'] is None else r['gpu_deviation']:>6}"
        )


if __name__ == "__main__":
    main()
