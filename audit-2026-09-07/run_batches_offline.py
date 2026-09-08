# -*- coding: utf-8 -*-
"""Прогон игр из партий 1-11 напрямую через код backend (без HTTP).

Зачем отдельный скрипт: запущенный uvicorn может быть собран из более старой
версии исходников (тогда /api/recommend отвечает 500, а маршруты каталога —
404). Расчёт идёт в том же процессе, что и актуальный код, поэтому результат
всегда соответствует текущей модели.

Выход совместим с `analyze_batches.py` и `run_batches.py`.
"""
from __future__ import annotations

import json
import os
import sys
import tempfile
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
sys.path.insert(0, str(BACKEND))
sys.path.insert(0, str(Path(__file__).resolve().parent))

# Свежая база во временном каталоге: рабочая база проекта могла быть заполнена
# до расширения каталога, и тогда новые функции и решения в расчёт не попадут.
# Аудит обязан проверять текущий код, а не состояние чьей-то базы.
_DB_DIR = Path(tempfile.mkdtemp(prefix="audit_offline_db_"))
os.environ["DATABASE_URL"] = f"sqlite:///{(_DB_DIR / 'audit.db').as_posix()}"
os.environ["AUTO_SEED"] = "false"

from app.database import Base, SessionLocal, engine  # noqa: E402
from app.schemas.catalog import BasketRequest  # noqa: E402
from app.seed import seeder  # noqa: E402
from app.services import recommender  # noqa: E402

import run_batches as rb  # noqa: E402

Base.metadata.create_all(bind=engine)
_DB = SessionLocal()
if seeder.is_empty(_DB):
    _REPORT = seeder.seed_all(_DB, validate=False)
    _DB.commit()
    _SKIPPED = [item for item in _REPORT["skipped"] if item["entity"] != "method_engine_links"]
    if _SKIPPED:
        print("ВНИМАНИЕ, пропуски при заполнении:", _SKIPPED[:5])


def build(profile: dict) -> dict:
    payload = BasketRequest(profile=profile, basket=[])
    return recommender.build_recommendations(_DB, payload.profile, payload.basket)


def run_all() -> list[dict]:
    results = []
    for path in sorted(ROOT.glob("партия-*.md")):
        batch_id = path.stem.replace("партия-", "")
        text = path.read_text(encoding="utf-8")
        for game in rb.parse_games(text):
            game["batch"] = batch_id
            profile = rb.profile_of(game)
            try:
                data = build(profile)
            except Exception as exc:  # noqa: BLE001
                results.append({
                    "game": game,
                    "error": f"{type(exc).__name__}: {exc}",
                    "traceback": traceback.format_exc(limit=4),
                })
                continue
            hw = data.hardware
            results.append({
                "game": game,
                "hardware": {
                    "reference_gpu": hw.reference_gpu.model if hw and hw.reference_gpu else None,
                    "gpu_class": hw.gpu_class if hw else None,
                    "reference_cpu": hw.reference_cpu.model if hw and hw.reference_cpu else None,
                    "cpu_class": hw.cpu_class if hw else None,
                    "vram_gb": hw.estimated_vram_gb if hw else None,
                    "ram_gb": hw.estimated_ram_gb if hw else None,
                    "required_gpu_index": hw.required_gpu_index if hw else None,
                    "required_cpu_index": hw.required_cpu_index if hw else None,
                    "bottleneck": hw.bottleneck if hw else None,
                    "bottleneck_label": hw.bottleneck_label if hw else None,
                    "storage": hw.storage_requirement if hw else None,
                    "exceeds": hw.exceeds_catalog if hw else None,
                    "confidence": hw.confidence if hw else None,
                    "confidence_label": hw.confidence_label if hw else None,
                    "unmet_limits": hw.unmet_limits if hw else [],
                    "caveats_count": len(hw.caveats) if hw else 0,
                },
                "recommendations": [
                    {"code": r.method_code, "name": r.method_name, "score": r.score}
                    for r in (data.recommendations or [])[:8]
                ],
                # Полный список: нужен, чтобы оценить реальную глубину
                # дифференциации, а не только видимую на экране восьмёрку.
                "all_recommendations": [
                    {"code": r.method_code, "name": r.method_name, "score": r.score}
                    for r in (data.recommendations or [])
                ],
                "all_excluded": [r.method_code for r in (data.excluded or [])],
                "excluded_count": len(data.excluded or []),
                "risks_count": len(data.risks or []),
                "load": json.loads(data.load_profile.model_dump_json()) if data.load_profile else {},
            })
    return results


def main() -> None:
    results = run_all()
    out = Path(__file__).resolve().parent / "batch-run-results.json"
    out.write_text(json.dumps(results, ensure_ascii=False, indent=1), encoding="utf-8")
    ok = [r for r in results if "error" not in r]
    failed = [r for r in results if "error" in r]
    print(f"Прогнано игр: {len(results)} (успешно {len(ok)}, ошибок {len(failed)})")
    print(f"Результаты: {out}")
    for r in failed:
        print("  ОШИБКА:", r["game"]["name"], "->", r["error"])


if __name__ == "__main__":
    sys.exit(main())
