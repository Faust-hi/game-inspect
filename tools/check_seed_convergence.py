"""Проверка сходимости заполнения: один вход — одно состояние базы.

Зачем. У базы два входа в заполнение: полный сидер (`seeder.seed_all`) и
стартовая синхронизация (`seeder.sync_function_taxonomy`, вызывается при старте
сервиса). Если они расходятся, состояние зависит от того, как база собрана и
сколько раз запускался сервис, — а «одинаковый вход даёт одинаковый результат»
это базовое требование проекта.

Почему не хватает счётчиков. Прежние проверки сравнивали число строк
(«456 конфликтов, 927 рёбер»). Два состояния с одинаковым числом строк могут
иметь разное содержание: так и были пропущены дефекты устаревших производных
данных — у 45 рёбер другое основание, у 130 утверждений другой контекст, у 13
методов другой `confidence`. Поэтому сверяется **всё**: каждая таблица по числу
строк и по отпечатку содержимого.

Что игнорируется и почему:
* `id`, `created_at`, `updated_at` — суррогатные и волатильные: зависят от
  порядка вставки и времени, а не от входных данных;
* порядок колонок — у базы, собранной миграциями, новые колонки дописаны в
  конец (ALTER TABLE), у собранной через `create_all` — в порядке модели.

Запуск:
    ./.dss-venv/Scripts/python.exe tools/check_seed_convergence.py

Код возврата 0 — состояния совпали, 1 — есть расхождения (печатаются таблицы).
Рабочая база не изменяется: всё строится на временных файлах.

Если инструмент показал расхождение, разбирать так:
1) сравнить таблицу построчно как мультимножество (без ключа: у `conflicts` нет
   естественного ключа — один метод участвует в нескольких связях);
2) свести строки по естественному ключу (`code`, `model`) и посмотреть, какие
   именно КОЛОНКИ разошлись — это отделяет содержательный дефект от сдвига
   суррогатных `id`.
"""
from __future__ import annotations

import hashlib
import json
import sqlite3
import subprocess
import sys
import tempfile
import shutil
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parents[1]
BACKEND_DIR = PROJECT_DIR / "backend"
VOLATILE = {"id", "created_at", "updated_at"}

#: Вспомогательный скрипт: выполняется в отдельном процессе, чтобы состояния
#: строились независимо и не делили между собой импортированные модули.
_WORKER = '''
import os, sys
db_path, mode, times = sys.argv[1], sys.argv[2], int(sys.argv[3])
sys.path.insert(0, sys.argv[4])
os.environ["DATABASE_URL"] = "sqlite:///" + db_path.replace("\\\\", "/")
from app.database import Base, SessionLocal, engine
from app.seed import seeder
if mode == "build":
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    seeder.seed_all(session, validate=False)
    session.commit()
    session.close()
else:
    action = seeder.seed_all if mode == "seed" else seeder.sync_function_taxonomy
    for _ in range(times):
        session = SessionLocal()
        if mode == "seed":
            action(session, validate=False)
        else:
            action(session)
        session.commit()
        session.close()
'''


def _run_worker(worker: Path, db: Path, mode: str, times: int = 1) -> None:
    result = subprocess.run(
        [sys.executable, str(worker), str(db), mode, str(times), str(BACKEND_DIR)],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"шаг {mode} не выполнен:\n{result.stderr[-2000:]}")


def _copy_db(src: Path, dst: Path) -> None:
    """Копия базы средствами SQLite.

    `shutil.copy` переносит только основной файл, а в режиме WAL свежие записи
    лежат в `-wal`: такая копия молча теряет часть данных, и проверка сравнивает
    не те состояния. Резервное копирование через API SQLite переносит
    согласованный снимок целиком.
    """
    if dst.exists():
        dst.unlink()
    source = sqlite3.connect(str(src))
    target = sqlite3.connect(str(dst))
    try:
        source.backup(target)
    finally:
        target.close()
        source.close()


def _snapshot(db_path: Path) -> dict[str, dict]:
    """Снимок всех таблиц: число строк и отпечаток содержимого."""
    conn = sqlite3.connect(str(db_path))
    tables = [
        r[0] for r in conn.execute(
            "select name from sqlite_master where type='table' "
            "and name not like 'sqlite_%' order by name"
        )
    ]
    out: dict[str, dict] = {}
    for table in tables:
        cols = [r[1] for r in conn.execute(f'pragma table_info("{table}")')]
        count = conn.execute(f'select count(*) from "{table}"').fetchone()[0]
        stable = sorted(c for c in cols if c not in VOLATILE)
        if stable and count:
            proj = ", ".join(f'ifnull("{c}", "")' for c in stable)
            rows = conn.execute(f'select {proj} from "{table}" order by {proj}').fetchall()
            blob = json.dumps(rows, ensure_ascii=False, default=str).encode("utf-8")
            digest = hashlib.sha256(blob).hexdigest()[:16]
        else:
            digest = "-"
        out[table] = {"rows": count, "hash": digest}
    conn.close()
    return out


def _report(label: str, base: dict, other: dict) -> bool:
    diffs = [
        (table, base.get(table), other.get(table))
        for table in sorted(set(base) | set(other))
        if base.get(table) != other.get(table)
    ]
    if not diffs:
        print(f"[OK] {label} — совпали все {len(base)} таблиц")
        return True
    print(f"[РАСХОЖДЕНИЕ] {label}")
    for table, ra, rb in diffs:
        print(f"    {table:26} A={ra}  B={rb}")
    return False


def main() -> int:
    tmpdir = Path(tempfile.mkdtemp(prefix="dss_convergence_"))
    try:
        worker = tmpdir / "_worker.py"
        worker.write_text(_WORKER, encoding="utf-8")

        fresh = tmpdir / "fresh.db"
        reseeded = tmpdir / "reseeded.db"
        restarted = tmpdir / "restarted.db"

        print("строю состояния: сборка с нуля, +3 полных сида, +3 старта...")
        _run_worker(worker, fresh, "build")
        _copy_db(fresh, reseeded)
        _copy_db(fresh, restarted)
        _run_worker(worker, reseeded, "seed", 3)
        _run_worker(worker, restarted, "startup", 3)

        base = _snapshot(fresh)
        mid = _snapshot(reseeded)
        late = _snapshot(restarted)

        print()
        ok = _report("сборка с нуля  vs  +3 полных сида", base, mid)
        ok &= _report("сборка с нуля  vs  +3 старта приложения", base, late)
        ok &= _report("+3 полных сида vs  +3 старта", mid, late)
        print()
        print("ИТОГ:", "СХОДИТСЯ" if ok else "ЕСТЬ РАСХОЖДЕНИЯ")
        return 0 if ok else 1
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(main())
