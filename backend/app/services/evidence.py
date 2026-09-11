"""Сериализация и агрегаты доказательного слоя.

Сервис не делает вывод «источник есть => число измерено». Основание claims
(`basis`) и статус проверки передаются в API без скрытой переклассификации.
"""
from __future__ import annotations

from sqlalchemy.orm import Session

from .. import repositories
from ..models.entities import EvidenceClaim, EvidenceSource
from ..schemas.catalog import (
    CaseEvidenceOut, EvidenceClaimOut, EvidenceSourceOut, EvidenceSummaryOut,
    GameCaseOut, DependencyOut, PracticeCheckOut,
)


def source_to_out(source: EvidenceSource | None) -> EvidenceSourceOut | None:
    if source is None or source.status != "published":
        return None
    return EvidenceSourceOut(
        code=source.code, title=source.title, authors=source.authors,
        publisher=source.publisher,
        source_type=source.source_type, published_date=source.published_date,
        checked_at=source.checked_at, url=source.url, version=source.version,
        platform=source.platform, locator=source.locator,
        availability=source.availability, applicability=source.applicability,
        notes=source.notes,
    )


def claim_to_out(db: Session, claim: EvidenceClaim) -> EvidenceClaimOut:
    source = db.get(EvidenceSource, claim.source_id) if claim.source_id else None
    return EvidenceClaimOut(
        code=claim.code, entity=claim.entity, entity_code=claim.entity_code,
        field=claim.field, claim=claim.claim, unit=claim.unit,
        value_text=claim.value_text, value_num=claim.value_num,
        range_min=claim.range_min, range_max=claim.range_max,
        source=source_to_out(source), locator=claim.locator,
        basis=claim.basis, verification_status=claim.verification_status,
        evidence_level=claim.evidence_level, formula=claim.formula,
        input_parameters=claim.input_parameters or {}, context=claim.context,
    )


def cases_to_out(db: Session, cases) -> list[GameCaseOut]:
    result: list[GameCaseOut] = []
    for case in cases:
        evidence_rows = []
        for item in repositories.case_evidence(db, case.id):
            source = db.get(EvidenceSource, item.source_id) if item.source_id else None
            evidence_rows.append(CaseEvidenceOut(
                code=item.code, function_code=item.function_code,
                method_code=item.method_code, fact=item.fact,
                match_level=item.match_level, locator=item.locator,
                source=source_to_out(source), basis=item.basis,
                transfer_limits=item.transfer_limits,
            ))
        result.append(GameCaseOut(
            code=case.code, title=case.title, studio=case.studio,
            release_year=case.release_year, technology=case.technology,
            engine_code=case.engine_code, world_type=case.world_type,
            network_mode=case.network_mode, summary=case.summary,
            relevance=case.relevance, transfer_limits=case.transfer_limits,
            evidence=evidence_rows,
        ))
    return result


def cases_for_methods(db: Session, method_codes: list[str]) -> list[GameCaseOut]:
    if not method_codes:
        return []
    wanted = set(method_codes)
    cases = []
    for case in repositories.game_cases(db):
        if any(item.method_code in wanted for item in repositories.case_evidence(db, case.id)):
            cases.append(case)
    return cases_to_out(db, cases)


def dependencies_to_out(db: Session) -> list[DependencyOut]:
    """Вернуть опубликованный технологический граф с именами узлов."""
    nodes = {node.id: node for node in repositories.technology_nodes(db)}
    result: list[DependencyOut] = []
    for edge in repositories.dependency_edges(db):
        source = nodes.get(edge.source_node_id)
        target = nodes.get(edge.target_node_id)
        if source is None or target is None:
            # Неполный граф не должен превращаться в висячую строку в отчёте.
            continue
        evidence = db.get(EvidenceSource, edge.source_id) if edge.source_id else None
        result.append(DependencyOut(
            code=f"{source.code}->{target.code}:{edge.dependency_type}",
            source_code=source.code, source_name=source.name, source_type=source.node_type,
            target_code=target.code, target_name=target.name, target_type=target.node_type,
            dependency_type=edge.dependency_type, mandatory=bool(edge.mandatory),
            min_version=edge.min_version, max_version=edge.max_version,
            platform=edge.platform, scope=edge.scope, severity=edge.severity,
            source=source_to_out(evidence), description=edge.description,
            workaround=edge.workaround, status=edge.status,
        ))
    return result


def practice_check(cases: list[GameCaseOut]) -> PracticeCheckOut:
    """Показать реальные кейсы без превращения их в метрику точности."""
    codes = [case.code for case in cases]
    if not cases:
        return PracticeCheckOut(
            # Keep the existing API meaning for an empty basket: the practical
            # cross-check is still in development.  The explicit accuracy and
            # transferability fields below make the non-claim unambiguous.
            status="in_development",
            title="Сверка с практикой: подходящие кейсы не выбраны",
            message=(
                "В каталоге есть опубликованные кейсы, но для выбранной корзины "
                "нет прямой связи с ними. Это не означает отсутствия практики."
            ),
            details=[
                "Кейсы подтверждают механизм и инженерный компромисс, а не переносимый FPS.",
                "Независимая runtime-калибровка и метрики точности не выполняются.",
            ],
            case_count=0, case_codes=[], accuracy_status="not_calibrated",
            transferability="not_claimed",
        )
    details = [f"{case.title}: {case.summary}" for case in cases[:8]]
    return PracticeCheckOut(
        status="case_evidence", title="Сверка с практикой: механизмы подтверждены кейсами",
        message=(
            "Связанные кейсы показывают, что подобные механизмы применялись в "
            "реальных играх или инженерных демо. Их показатели и ограничения "
            "нельзя переносить в проект без собственного профилирования."
        ),
        details=details, case_count=len(cases), case_codes=codes,
        accuracy_status="not_calibrated", transferability="not_claimed",
    )


def summary(db: Session, *, method_codes: list[str] | None = None) -> EvidenceSummaryOut:
    sources = repositories.evidence_sources(db)
    claims = repositories.evidence_claims(db)
    if method_codes:
        wanted = set(method_codes)
        claims = [claim for claim in claims if claim.entity_code in wanted]
    cases = repositories.game_cases(db)
    claims_with_sources = sum(
        1 for claim in claims
        if claim.source_id is not None and claim.locator and claim.verification_status not in {"unverified", "rejected"}
    )
    numeric = [claim for claim in claims if claim.value_num is not None or claim.range_min is not None or claim.range_max is not None]
    published_numeric = sum(1 for claim in numeric if claim.basis in {"measured", "documented", "derived"} and claim.source_id is not None)
    unknown_numeric = len(numeric) - published_numeric
    coverage = (claims_with_sources / len(claims)) if claims else 0.0
    if not claims:
        label = "нет claims"
    elif coverage >= 0.85:
        label = "высокая по наличию источника"
    elif coverage >= 0.6:
        label = "средняя по наличию источника"
    else:
        label = "низкая по наличию источника"
    unconfirmed = sorted({
        f"{claim.entity}:{claim.entity_code}.{claim.field}"
        for claim in numeric
        if claim.source_id is None or claim.basis in {"expert_estimate", "unknown"}
    })
    return EvidenceSummaryOut(
        source_count=len(sources), claim_count=len(claims), case_count=len(cases),
        claims_with_sources=claims_with_sources,
        numeric_claims_published=published_numeric,
        numeric_claims_unknown=unknown_numeric,
        coverage_label=label, unconfirmed_numeric_factors=unconfirmed,
        calibration_status="not_calibrated",
    )
