"""Выгрузка справочников DSS: движки, функции, методы, инструменты.

Запуск (из каталога backend, чтобы работали относительные пути настроек):

    ../.venv/Scripts/python.exe ../validation/parties/dump_catalog.py

Результат: validation/parties/catalog.json — используется для сопоставления
игр из партий с профилем DSS.
"""
from __future__ import annotations

import json
import pathlib
import sys

BACKEND = pathlib.Path(__file__).resolve().parents[2] / "backend"
sys.path.insert(0, str(BACKEND))

os_env_db = BACKEND / "gamedev_dss.db"  # noqa: F841


def main() -> None:
    import os
    os.environ.setdefault("AUTO_SEED", "false")
    os.environ.setdefault(
        "DATABASE_URL", f"sqlite:///{(BACKEND / 'gamedev_dss.db').as_posix()}"
    )

    from app.database import SessionLocal
    from app.models.entities import Conflict, Engine, EngineTool, GameFunction, Method

    session = SessionLocal()
    try:
        engines = []
        for e in session.query(Engine).order_by(Engine.code).all():
            tools = [
                {"code": t.code, "name": t.name, "subsystem": t.subsystem,
                 "min_version": t.min_version}
                for t in session.query(EngineTool)
                .filter(EngineTool.engine_id == e.id).all()
            ]
            engines.append({
                "code": e.code, "name": e.name, "vendor": e.vendor,
                "versions": e.versions, "supported_formats": e.supported_formats,
                "tools": tools,
            })

        functions = [
            {"code": f.code, "name": f.name, "category": f.category,
             "formats": f.formats, "typical_world_types": f.typical_world_types}
            for f in session.query(GameFunction).order_by(GameFunction.code).all()
        ]

        func_code = {f.id: f.code for f in session.query(GameFunction).all()}

        methods = []
        for m in session.query(Method).order_by(Method.code).all():
            methods.append({
                "code": m.code, "name": m.name, "kind": m.kind,
                "function_code": func_code.get(m.function_id),
                "level": m.level,
                "applicable_formats": m.applicable_formats,
                "applicable_world_types": m.applicable_world_types,
                "applicable_engines": m.applicable_engines,
                "applicable_platforms": m.applicable_platforms,
                "requires_features": m.requires_features,
                "requires_hw_features": m.requires_hw_features,
                "effect_scope": m.effect_scope,
                "impact_cpu": m.impact_cpu, "impact_gpu": m.impact_gpu,
                "impact_ram": m.impact_ram, "impact_vram": m.impact_vram,
                "impact_disk": m.impact_disk, "impact_network": m.impact_network,
                "performance_gain": m.performance_gain,
                "implementation_cost": m.implementation_cost,
                "complexity": m.complexity,
                "status": m.status,
            })
    finally:
        session.close()

    out = pathlib.Path(__file__).resolve().parent / "catalog.json"
    out.write_text(
        json.dumps({"engines": engines, "functions": functions, "methods": methods},
                   ensure_ascii=False, indent=1),
        encoding="utf-8",
    )
    print(f"engines={len(engines)} functions={len(functions)} methods={len(methods)}")

    # Связи между методами выносятся отдельным файлом: они нужны для разбора
    # взаимного влияния решений и не требуются при сопоставлении игр.
    session = SessionLocal()
    try:
        relations = [
            {
                "a": c.a_code,
                "b": c.b_code,
                "type": c.conflict_type,
                "severity": c.severity,
                "description": c.description,
                "resolution": c.resolution,
                "source_url": c.source_url,
            }
            for c in session.query(Conflict)
            .order_by(Conflict.conflict_type, Conflict.a_code, Conflict.b_code)
            .all()
        ]
    finally:
        session.close()

    rel_out = pathlib.Path(__file__).resolve().parent / "relations.json"
    rel_out.write_text(
        json.dumps(relations, ensure_ascii=False, indent=1), encoding="utf-8"
    )
    print(f"relations={len(relations)}")
    print(f"written: {rel_out}")
    print(f"written: {out}")


if __name__ == "__main__":
    main()
