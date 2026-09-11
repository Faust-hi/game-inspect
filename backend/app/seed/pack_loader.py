"""Загрузчик исследовательских пакетов в доказательный слой.

Каждый пакет — JSON с полным набором sources, claims, game_examples и
work packages. Модуль нормализует source_type, upsert-ит источники,
claims, кейсы и пакеты работ, не затирая существующие записи
администратора.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from sqlalchemy import select, tuple_
from sqlalchemy.orm import Session

from ..models.entities import (
    CaseEvidence, Conflict, EvidenceClaim, EvidenceSource, GameCase, Method,
    TechnologyNode, WorkPackage,
)
from ..models.enums import Status

#: Публикуются только утверждения с источником: спека прямо запрещает
#: публикацию записи без обязательного источника. Утверждение без источника
#: остаётся черновиком — это объявленный пробел, а не тихая публикация.
DRAFT = Status.DRAFT.value
PUBLISHED = Status.PUBLISHED.value

PACK_DIR = Path(__file__).parent.parent.parent.parent / "research" / "packs"

# Нормализация свободных source_type → контролируемый реестр
_SOURCE_TYPE_MAP: dict[str, str] = {
    "official_engine_documentation": "official_documentation",
    "official_sdk_documentation": "official_documentation",
    "official_documentation": "official_documentation",
    "official_sample_documentation": "official_documentation",
    "official_studio_support_article": "official_documentation",
    "official_game_material": "official_documentation",
    "official_case_index": "case_study",
    "official_case_study": "case_study",
    "academic_paper": "academic_paper",
    "academic paper": "academic_paper",
    "book": "book",
    "book_chapter_primary": "book",
    "conference_talk": "conference_talk",
    "conference_session_primary": "conference_talk",
    "conference_slides_primary": "conference_talk",
    "conference presentation": "conference_talk",
    "conference talk": "conference_talk",
    "conference talk abstract / studio publication": "conference_talk",
    "engineering_blog": "engineering_blog",
    "studio_engineering_blog_primary": "engineering_blog",
    "studio_engineering_article": "engineering_blog",
    "engine engineering blog (first-party)": "engineering_blog",
    "first-party studio interview": "interview",
    "interview": "interview",
    "open_source": "open_source",
    "open_source_library": "open_source",
    "open_source_project": "open_source",
    "open_source_project_documentation": "open_source",
    "open_source_sdk": "open_source",
    "open_source_source_code": "open_source",
    "hardware_benchmark": "hardware_benchmark",
    "vendor_press_release": "vendor_press_release",
    "vendor_product_page": "vendor_press_release",
    "vendor_news / technical article": "engineering_blog",
    "vendor_engineering_blog": "engineering_blog",
    "vendor_engineering_article": "engineering_blog",
    "graphics api specification": "api_specification",
    "graphics API specification": "api_specification",
    "graphics API specification / guide": "api_specification",
    "graphics API specification / proposal": "api_specification",
    "standard": "standard",
    "postmortem": "postmortem",
    "studio_documentation_primary": "official_documentation",
    "secondary_encyclopedic": "secondary",
    "secondary": "secondary",
    "secondary technical analysis (secondary)": "secondary",
    "third-party technical analysis (secondary)": "secondary",
    "practitioner technical article with open-source reference implementation": "engineering_blog",
    "practitioner technical article with reference implementation": "engineering_blog",
    "locator-failure record": "secondary",
}


def _norm_source_type(raw: str) -> str:
    return _SOURCE_TYPE_MAP.get(raw.lower().strip(), "secondary")


#: Стадии проекта, допустимые в поле `recommended_stage`.
_VALID_STAGES = {
    "concept", "preproduction", "prototype", "production",
    "alpha", "beta", "release", "post_release",
}

#: Ключевые слова для разбора свободного текста о рекомендованной стадии.
#: Часть исследовательских пакетов хранит в `recommended_stage` не код стадии,
#: а развёрнутую рекомендацию на английском («vertical_slice, once lighting art
#: direction is locked…»). Это осмысленный текст, но он не является значением
#: перечисления: если подставить его в поле как есть, стадия перестаёт быть
#: сравнимой и фильтруемой. Слова разбираются по порядку — побеждает то, что
#: встретится первым в тексте, потому что именно оно названо основной стадией.
_STAGE_HINTS: tuple[tuple[str, str], ...] = (
    ("concept", "concept"),
    ("preproduction", "preproduction"),
    ("pre-production", "preproduction"),
    ("vertical_slice", "prototype"),
    ("vertical slice", "prototype"),
    ("prototype", "prototype"),
    ("production", "production"),
    ("alpha", "alpha"),
    ("beta", "beta"),
    ("post_launch", "post_release"),
    ("post-launch", "post_release"),
    ("post_release", "post_release"),
    ("release", "release"),
)


def normalize_stage(raw: Any) -> tuple[str, str | None]:
    """Привести рекомендованную стадию к коду перечисления.

    Возвращает пару «код стадии» и «исходный свободный текст, если он не был
    кодом». Второй элемент не пустой только тогда, когда значение пришлось
    разбирать: вызывающий код обязан сохранить его как примечание, а не
    потерять. Пустое или неизвестное значение даёт `prototype` — это самое
    раннее безопасное допущение: стадия не скрывает метод из выдачи.
    """
    text = str(raw or "").strip()
    if not text:
        return "prototype", None
    low = text.lower()
    if low in _VALID_STAGES:
        return low, None
    for needle, stage in _STAGE_HINTS:
        if needle in low:
            return stage, text
    # Текст не распознан: стадия не выдумывается, но и не теряется.
    return "prototype", text


def _load_packs() -> list[dict[str, Any]]:
    packs = []
    if not PACK_DIR.exists():
        return packs
    for p in sorted(PACK_DIR.glob("pack_*.json")):
        try:
            packs.append(json.loads(p.read_text(encoding="utf-8")))
        except Exception:
            continue
    return packs


def _upsert_source(db: Session, payload: dict[str, Any]) -> EvidenceSource:
    code = payload["code"]
    existing = db.scalar(select(EvidenceSource).where(EvidenceSource.code == code))
    if existing:
        return existing
    src = EvidenceSource(
        code=code,
        title=payload.get("title", "")[:300],
        authors=payload.get("author_or_publisher", "")[:300],
        publisher=payload.get("author_or_publisher", "")[:200],
        source_type=_norm_source_type(payload.get("source_type", "secondary")),
        published_date=payload.get("published_date", "")[:20],
        checked_at=payload.get("verified_date", "2026-09-10")[:30],
        url=payload.get("url", "")[:800],
        version=payload.get("engine_or_api_version", "")[:80],
        platform=payload.get("platform", "")[:120],
        locator=payload.get("locator", "overview")[:300],
        availability=payload.get("availability", "available")[:30],
        applicability=payload.get("applicability_note", "")[:2000],
        notes="",
        # Источник из курируемого пакета — это запись реестра, а не черновик:
        # у неё уже есть код, тип и локатор. Оставленный по умолчанию черновик
        # обнулял ссылку при выдаче: утверждение публиковалось, но его источник
        # отфильтровывался, и запись выглядела как «источника нет» — то есть
        # ровно как нарушение требования «запись без обязательного источника не
        # публикуется», хотя источник в базе был.
        status=PUBLISHED,
    )
    db.add(src)
    db.flush()
    return src


def _upsert_claim(db: Session, payload: dict[str, Any], sources_map: dict[str, EvidenceSource]) -> EvidenceClaim | None:
    code = payload["code"]
    existing = db.scalar(select(EvidenceClaim).where(EvidenceClaim.code == code))
    if existing:
        # Rows loaded before a metadata field existed keep the old shape. Fill
        # in only the keys that are genuinely missing (e.g. the engine/role
        # classification added later) so already-loaded evidence is enriched
        # instead of being silently left unclassified.
        new_ip = payload.get("input_parameters")
        if isinstance(new_ip, dict) and new_ip:
            cur = existing.input_parameters
            cur = cur if isinstance(cur, dict) else {}
            merged = dict(cur)
            changed = False
            for k, v in new_ip.items():
                # Never blank out a value that is already populated.
                if v in (None, "", {}):
                    continue
                if cur.get(k) in (None, "", {}) and merged.get(k) != v:
                    merged[k] = v
                    changed = True
            if changed:
                existing.input_parameters = merged
                db.flush()
        return existing
    src = sources_map.get(payload.get("source"))
    # `value_range` может быть явным null (в JSON это законно). Раньше это
    # приводило к TypeError и обрывало весь sync_packs, оставляя базу без
    # новых пакетов, — поэтому диапазон нормализуется здесь, в одной точке.
    vr = payload.get("value_range") or [None, None]
    if not isinstance(vr, (list, tuple)):
        vr = [None, None]
    range_min = vr[0] if len(vr) > 0 else None
    range_max = vr[1] if len(vr) > 1 else None
    claim = EvidenceClaim(
        code=code,
        entity=payload.get("entity", "method"),
        entity_code=payload.get("entity_code", ""),
        field=payload.get("field", ""),
        claim=payload.get("claim", "")[:4000],
        unit=payload.get("unit", "")[:40],
        value_text=str(payload.get("value", ""))[:4000],
        value_num=payload.get("value") if isinstance(payload.get("value"), (int, float)) else None,
        range_min=range_min,
        range_max=range_max,
        source_id=src.id if src else None,
        locator=payload.get("locator", "")[:300],
        basis=payload.get("basis", "unknown"),
        verification_status=payload.get("verification_state", "unverified"),
        evidence_level=payload.get("evidence_level", "low"),
        formula=payload.get("formula", "")[:2000],
        input_parameters=payload.get("input_parameters", {}),
        context=payload.get("context", "")[:2000],
        # Источник есть — утверждение публикуемо; источника нет — остаётся
        # черновиком и не попадает в выдачу. Раньше статус не задавался вовсе,
        # и ВСЕ утверждения из пакетов оставались черновиками навсегда:
        # целые семейства доказательств (инструменты, движки, стадии, риски)
        # были недостижимы через API и отчёт, хотя источник у них был.
        status=PUBLISHED if src is not None else DRAFT,
    )
    db.add(claim)
    db.flush()
    return claim


def _upsert_case(db: Session, payload: dict[str, Any], sources_map: dict[str, EvidenceSource]) -> GameCase | None:
    code = payload["code"]
    existing = db.scalar(select(GameCase).where(GameCase.code == code))
    if existing:
        return existing
    case = GameCase(
        code=code,
        title=payload.get("title", "")[:200],
        studio=payload.get("studio", "")[:200],
        release_year=payload.get("year"),
        technology=payload.get("engine", "")[:200],
        engine_code=payload.get("engine_code", "")[:64],
        world_type=payload.get("world_type", "")[:80],
        network_mode=payload.get("network_mode", "")[:120],
        summary=payload.get("summary", "")[:4000],
        relevance=payload.get("relevance", "")[:2000],
        transfer_limits=payload.get("transfer_limits", "")[:2000],
    )
    db.add(case)
    db.flush()
    return case


def _upsert_work_package(db: Session, payload: dict[str, Any]) -> WorkPackage | None:
    code = payload["code"]
    existing = db.scalar(select(WorkPackage).where(WorkPackage.code == code))
    if existing:
        return existing
    wp = WorkPackage(
        code=code,
        method_code=payload.get("method_code", "")[:64],
        name=payload.get("name", "")[:220],
        package_type=payload.get("package_type", "integration"),
        role=payload.get("role", "engineering"),
        min_days=payload.get("min_days", 0.0),
        p50_days=payload.get("p50_days", 1.0),
        p80_days=payload.get("p80_days", 1.5),
        parallelizable=payload.get("parallelizable", True),
        recommended_stage=normalize_stage(payload.get("recommended_stage"))[0],
        late_factor=payload.get("late_factor", 1.0),
        dependency_codes=payload.get("dependency_codes", []),
        basis=payload.get("basis", "expert_estimate"),
    )
    db.add(wp)
    db.flush()
    return wp


def _build_claim_code(source_code: str, entity: str, entity_code: str, field: str, idx: int) -> str:
    # A declared-absence row carries source=None on purpose (see gap_claim in
    # tools/gen_pack_tool_proofs.py). Formatting None would produce the literal
    # "None_" prefix, so it is normalised to an explicit NOSRC marker instead.
    src = (source_code or "NOSRC")
    return f"{src}_{entity}_{entity_code}_{field}_{idx}".replace("-", "_")[:160]


# ── Связи «метод-метод» ──
# Пакеты содержат relations (типизированная связь) и dependencies
# (обязательная зависимость). И то и другое — рёбра между методами, поэтому
# хранится в одной таблице с сохранением исходного типа связи.
_RELATION_SEVERITY: dict[str, int] = {
    "hard_conflict": 3,
    "risk": 2,
    "dependency": 3,
    "alternative": 1,
    "complement": 1,
    "overlap": 1,
    "unknown": 2,
}

#: Типы связей, у которых нет направления: «A дополняет B» и «B дополняет A» —
#: одно отношение, записанное дважды. Для них повторная запись в обратном
#: порядке считается дубликатом. «dependency» и «overlap» направленные:
#: порядок сторон задаёт смысл, поэтому обратная пара — другое отношение.
_SYMMETRIC_RELATIONS = frozenset({"complement", "alternative", "hard_conflict", "risk"})


def _upsert_relation(
    db: Session,
    a_code: str,
    b_code: str,
    relation_type: str,
    description: str,
    source_url: str,
    known_methods: set[str],
    seen: set[tuple[str, str, str]],
) -> bool:
    """Добавить ребро «метод-метод». Возвращает True, если запись создана.

    Связь с несуществующим методом не создаётся: ребро в никуда сделало бы
    проверку транзитивных зависимостей недостоверной.
    """
    if not a_code or not b_code or a_code == b_code:
        return False
    if a_code not in known_methods or b_code not in known_methods:
        return False
    if relation_type not in _RELATION_SEVERITY:
        relation_type = "unknown"
    key = (a_code, b_code, relation_type)
    # `seen` нужен потому, что незакоммиченные строки не видны запросу,
    # и один и тот же пакет может объявить связь дважды.
    if key in seen:
        return False
    # Дубликат проверяется по тройке в том виде, в каком она хранится в базе,
    # плюс по обратной паре для симметричных типов связи. Без второй проверки
    # «A дополняет B» из одного пакета и «B дополняет A» из другого создавали
    # две записи об одном и том же отношении, и автоматический разрыв циклов
    # понижал только одну из них — вторая продолжала требовать взаимности.
    # Проверка симметрична только для типов, у которых нет направления: у
    # «dependency» и «overlap» порядок значим, поэтому A→B и B→A остаются
    # разными отношениями.
    pairs = [(a_code, b_code)]
    if relation_type in _SYMMETRIC_RELATIONS:
        pairs.append((b_code, a_code))
    exists = db.scalar(
        select(Conflict.id).where(
            Conflict.conflict_type == relation_type,
            tuple_(Conflict.a_code, Conflict.b_code).in_(pairs),
        )
    )
    if exists:
        seen.add(key)
        return False
    db.add(
        Conflict(
            a_code=a_code,
            b_code=b_code,
            conflict_type=relation_type,
            severity=_RELATION_SEVERITY[relation_type],
            description=description[:4000],
            resolution="",
            source_url=source_url[:600],
            status="published",
        )
    )
    seen.add(key)
    return True


# Секции пакета, не являющиеся методами, но требующие доказательного слоя.
# section -> (entity в evidence_claims, колонка связи в case_evidence)
_ENTITY_SECTIONS: dict[str, tuple[str, str]] = {
    "functions": ("game_function", "function_code"),
    "engines": ("engine", "engine_code"),
    "engine_tools": ("engine_tool", "engine_tool_code"),
    "technology_nodes": ("technology_node", "node_code"),
    "cases": ("game_case", "case_code"),
    "platforms": ("target_platform", "platform_code"),
    "stage_budgets": ("stage_budget", "stage_code"),
    "network_modes": ("network_mode", "network_mode_code"),
    "target_metrics": ("target_metric", "metric_code"),
    "load_profiles": ("load_profile", "profile_code"),
    "risk_factors": ("risk_factor", "risk_code"),
}


def sync_packs(db: Session) -> dict[str, int]:
    packs = _load_packs()
    stats = {"sources": 0, "claims": 0, "cases": 0, "case_evidence": 0, "work_packages": 0, "relations": 0}
    sources_map: dict[str, EvidenceSource] = {}
    known_methods = {code for (code,) in db.execute(select(Method.code)).all()}
    seen_relations: set[tuple[str, str, str]] = set()

    # 1. Sources
    for pack in packs:
        for s in pack.get("sources", []):
            src = _upsert_source(db, s)
            sources_map[s["code"]] = src
            stats["sources"] += 1

    # 2. Claims + Cases + Work packages
    for pack in packs:
        for mcode, mdata in pack.get("methods", {}).items():
            # claims
            for i, c in enumerate(mdata.get("claims", [])):
                payload = {
                    "code": _build_claim_code(c.get("source", "UNKNOWN"), "method", mcode, c.get("field", ""), i),
                    "entity": "method",
                    "entity_code": mcode,
                    "field": c.get("field", ""),
                    "claim": c.get("statement", ""),
                    "unit": c.get("unit", ""),
                    "value": c.get("value"),
                    "value_range": c.get("value_range") or [None, None],
                    "source": c.get("source"),
                    "locator": c.get("locator", ""),
                    "basis": c.get("basis", "unknown"),
                    "verification_state": c.get("verification_state", "unverified"),
                    "evidence_level": c.get("evidence_level", "low"),
                    "formula": c.get("formula", ""),
                    "input_parameters": c.get("input_parameters", {}),
                    "context": c.get("context", ""),
                }
                _upsert_claim(db, payload, sources_map)
                stats["claims"] += 1

            # game examples → GameCase + CaseEvidence
            for i, ex in enumerate(mdata.get("game_examples", [])):
                case_code = f"CASE_{ex['game'].replace(' ', '_').replace(':', '')}_{i}"[:120]
                case = _upsert_case(db, {
                    "code": case_code,
                    "title": ex["game"],
                    "studio": ex.get("studio", ""),
                    "year": ex.get("year"),
                    "engine": ex.get("engine", ""),
                    "world_type": "",
                    "network_mode": "",
                    "summary": ex.get("fact", ""),
                    "relevance": ex.get("relevance", ""),
                    "transfer_limits": ex.get("non_transferable", ""),
                }, sources_map)
                if case:
                    # case evidence row
                    src = sources_map.get(ex.get("source"))
                    ce_code = f"CE_{case_code}_{mcode}_{i}"[:160]
                    existing_ce = db.scalar(select(CaseEvidence).where(CaseEvidence.code == ce_code))
                    if not existing_ce:
                        ce = CaseEvidence(
                            code=ce_code,
                            case_id=case.id,
                            method_code=mcode,
                            fact=ex.get("fact", "")[:4000],
                            match_level=ex.get("relevance", "partial"),
                            locator=ex.get("locator", "")[:300],
                            source_id=src.id if src else None,
                            basis="case_evidence",
                            transfer_limits=ex.get("non_transferable", "")[:2000],
                            status=PUBLISHED if src is not None else DRAFT,
                        )
                        db.add(ce)
                        stats["case_evidence"] += 1
                    stats["cases"] += 1

            # work packages
            effort = mdata.get("effort_person_days", {})
            if effort and effort.get("p50") is not None:
                for pkg_type, role_map in {
                    "design": "designer",
                    "feasibility": "engineer",
                    "integration": "engineer",
                    "content": "artist",
                    "optimization": "engineer",
                    "qa": "qa",
                    "release": "engineer",
                    "documentation": "writer",
                }.items():
                    # Simplified: one WP per method per type, P50/P80 split
                    p50 = float(effort["p50"]) / 8.0
                    p80 = float(effort["p80"]) / 8.0
                    _upsert_work_package(db, {
                        "code": f"WP_{mcode}_{pkg_type}"[:180],
                        "method_code": mcode,
                        "name": f"{pkg_type}: {mcode}",
                        "package_type": pkg_type,
                        "role": role_map,
                        "p50_days": p50,
                        "p80_days": p80,
                        "basis": effort.get("basis", "expert_estimate"),
                        "recommended_stage": normalize_stage(
                            mdata.get("recommended_stage")
                        )[0],
                    })
                    stats["work_packages"] += 1

            # relations → типизированные рёбра «метод-метод»
            for rel in mdata.get("relations", []):
                src = sources_map.get(rel.get("source"))
                if _upsert_relation(
                    db,
                    mcode,
                    rel.get("code", ""),
                    rel.get("type", "unknown"),
                    rel.get("note", ""),
                    src.url if src else "",
                    known_methods,
                    seen_relations,
                ):
                    stats["relations"] += 1

            # dependencies → обязательные рёбра «метод-метод»
            for dep in mdata.get("dependencies", []):
                if _upsert_relation(
                    db,
                    mcode,
                    dep,
                    "dependency",
                    f"Метод «{mcode}» требует предварительного метода «{dep}».",
                    "",
                    known_methods,
                    seen_relations,
                ):
                    stats["relations"] += 1

    # 3. Generic non-method sections: functions, engines, engine_tools,
    #    technology_nodes, cases and the derivation domains. Same
    #    claim/game_example shape as methods, different entity linkage.
    for section, (entity, link_field) in _ENTITY_SECTIONS.items():
        for pack in packs:
            for ecode, edata in (pack.get(section) or {}).items():
                if not isinstance(edata, dict):
                    continue
                for i, c in enumerate(edata.get("claims", [])):
                    _upsert_claim(db, {
                        "code": _build_claim_code(
                            c.get("source", "UNKNOWN"), entity, ecode, c.get("field", ""), i),
                        "entity": entity,
                        "entity_code": ecode,
                        "field": c.get("field", ""),
                        "claim": c.get("statement", ""),
                        "unit": c.get("unit", ""),
                        "value": c.get("value"),
                        "value_range": c.get("value_range", [None, None]) or [None, None],
                        "source": c.get("source"),
                        "locator": c.get("locator", ""),
                        "basis": c.get("basis", "unknown"),
                        "verification_state": c.get("verification_state", "unverified"),
                        "evidence_level": c.get("evidence_level", "low"),
                        "formula": c.get("formula", ""),
                        "input_parameters": c.get("input_parameters", {}),
                        "context": c.get("context", ""),
                    }, sources_map)
                    stats["claims"] += 1

                for i, ex in enumerate(edata.get("game_examples", [])):
                    if link_field in ("function_code", "method_code"):
                        case_code = f"CASE_{ex['game'].replace(' ', '_').replace(':', '')}_{i}"[:120]
                        case = _upsert_case(db, {
                            "code": case_code,
                            "title": ex["game"],
                            "studio": ex.get("studio", ""),
                            "year": ex.get("year"),
                            "engine": ex.get("engine", ""),
                            "world_type": ex.get("world_type", ""),
                            "network_mode": ex.get("network_mode", ""),
                            "summary": ex.get("fact", ""),
                            "relevance": ex.get("relevance", ""),
                            "transfer_limits": ex.get("non_transferable", ""),
                        }, sources_map)
                        if case:
                            ce_code = f"CE_{case_code}_{ecode}_{i}"[:160]
                            exists = db.scalar(
                                select(CaseEvidence).where(CaseEvidence.code == ce_code))
                            if not exists:
                                src = sources_map.get(ex.get("source"))
                                db.add(CaseEvidence(
                                    code=ce_code,
                                    case_id=case.id,
                                    method_code=ecode if link_field == "method_code" else None,
                                    function_code=ecode if link_field == "function_code" else None,
                                    fact=ex.get("fact", "")[:4000],
                                    match_level=ex.get("relevance", "partial"),
                                    locator=ex.get("locator", "")[:300],
                                    source_id=src.id if src else None,
                                    basis="case_evidence",
                                    transfer_limits=ex.get("non_transferable", "")[:2000],
                                    status=PUBLISHED if src is not None else DRAFT,
                                ))
                                stats["case_evidence"] += 1
                            stats["cases"] += 1
                    else:
                        # У этих сущностей нет колонки связи в case_evidence —
                        # игровой пример сохраняем как claim с basis=case_evidence.
                        src_code = ex.get("source", "UNKNOWN")
                        _upsert_claim(db, {
                            "code": _build_claim_code(
                                src_code, entity, ecode, f"case:{ex.get('game','')}", i),
                            "entity": entity,
                            "entity_code": ecode,
                            "field": "game_example",
                            "claim": ex.get("fact", ""),
                            "unit": "",
                            "value": None,
                            "value_range": [None, None],
                            "source": ex.get("source"),
                            "locator": ex.get("locator", ""),
                            "basis": "case_evidence",
                            "verification_state": ex.get("verification_state", "unverified"),
                            "evidence_level": ex.get("evidence_level", "medium"),
                            "formula": "",
                            # `engine` and `role` are carried through so the
                            # audit can tell a same-engine example (the tool's
                            # own platform) from a cross-engine one (the
                            # capability proven elsewhere). Without them the
                            # two would be counted identically, which would
                            # overstate tool adoption.
                            "input_parameters": {"game": ex.get("game", ""),
                                                 "studio": ex.get("studio", ""),
                                                 "year": ex.get("year"),
                                                 "engine": ex.get("engine", ""),
                                                 "role": ex.get("role", ""),
                                                 "proves": ex.get("proves", "")},
                            "context": ex.get("relevance", ""),
                        }, sources_map)
                        stats["claims"] += 1

    db.flush()
    return stats
