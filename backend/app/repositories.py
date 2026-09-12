"""Слой доступа к опубликованным данным.

Публичные маршруты обязаны работать только с опубликованным снимком базы
знаний. Раньше фильтр по статусу расставлялся в каждом маршруте вручную, из-за
чего часть сущностей отдавалась целиком, а карточка черновика была доступна
прямым запросом по коду.

Здесь собраны все публичные выборки. Каждая функция явно фильтрует статус, а
`PUBLISHED_ONLY` описывает, какие модели вообще участвуют в публичном снимке.
Административные маршруты используют ORM напрямую.
"""
from __future__ import annotations

from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

from .models.entities import (
    Conflict, Engine, EngineTool, GameFunction, HardwareCPU, HardwareGPU,
    Method, MethodEngineLink, EvidenceSource, EvidenceClaim,
    TechnologyNode, DependencyEdge,
)
from .models.enums import Status

PUBLISHED = Status.PUBLISHED.value


def _published(model, stmt: Select | None = None) -> Select:
    """Добавляет к выборке условие «только опубликованные записи»."""
    stmt = stmt if stmt is not None else select(model)
    return stmt.where(model.status == PUBLISHED)


def functions(db: Session) -> list[GameFunction]:
    return list(db.scalars(_published(GameFunction).order_by(GameFunction.sort_order)))


def function(db: Session, code: str) -> GameFunction | None:
    return db.scalar(_published(GameFunction).where(GameFunction.code == code))


def methods(db: Session) -> list[Method]:
    return list(db.scalars(_published(Method).order_by(Method.code)))


def method(db: Session, code: str) -> Method | None:
    """Публичная карточка метода: черновик и «проверено» недоступны."""
    return db.scalar(_published(Method).where(Method.code == code))


def methods_by_codes(db: Session, codes: list[str]) -> list[Method]:
    """Опубликованные методы для корзины. Неопубликованные коды игнорируются."""
    if not codes:
        return []
    return list(db.scalars(_published(Method).where(Method.code.in_(codes))))


def engines(db: Session) -> list[Engine]:
    return list(db.scalars(_published(Engine).order_by(Engine.code)))


def engine_tools(db: Session) -> list[EngineTool]:
    return list(db.scalars(_published(EngineTool).order_by(EngineTool.code)))


def conflicts(db: Session) -> list[Conflict]:
    return list(db.scalars(_published(Conflict).order_by(Conflict.a_code, Conflict.b_code)))


def hardware_cpu(db: Session) -> list[HardwareCPU]:
    return list(
        db.scalars(_published(HardwareCPU).order_by(HardwareCPU.multi_thread_score.desc()))
    )


def hardware_gpu(db: Session) -> list[HardwareGPU]:
    return list(db.scalars(_published(HardwareGPU).order_by(HardwareGPU.raster_score.desc())))


def method_links(db: Session, method_id: int) -> list[MethodEngineLink]:
    """Опубликованные связи метода с инструментами движков.

    Связь считается published, но ссылается на снятый с публикации инструмент —
    такая связь в публичный ответ не попадает, иначе пользователь увидит
    рекомендацию использовать удалённый инструмент.
    """
    published_tool_ids = select(EngineTool.id).where(
        EngineTool.status == PUBLISHED,
        EngineTool.engine_id.in_(select(Engine.id).where(Engine.status == PUBLISHED)),
    )
    stmt = (
        _published(MethodEngineLink)
        .where(MethodEngineLink.method_id == method_id)
        .where(MethodEngineLink.tool_id.in_(published_tool_ids))
    )
    return list(db.scalars(stmt))


def published_snapshot_counts(db: Session) -> dict[str, int]:
    """Число опубликованных записей по сущностям — для диагностики развёртывания."""
    def _count(model) -> int:
        return db.scalar(select(func.count(model.id)).where(model.status == PUBLISHED)) or 0

    return {
        "functions": _count(GameFunction),
        "methods": _count(Method),
        "engines": _count(Engine),
        "engine_tools": _count(EngineTool),
        "conflicts": _count(Conflict),
        "hardware_cpu": _count(HardwareCPU),
        "hardware_gpu": _count(HardwareGPU),
        "evidence_sources": _count(EvidenceSource),
        "evidence_claims": _count(EvidenceClaim),
        "technology_nodes": _count(TechnologyNode),
        "dependency_edges": _count(DependencyEdge),
    }


def evidence_sources(db: Session) -> list[EvidenceSource]:
    return list(db.scalars(_published(EvidenceSource).order_by(EvidenceSource.code)))


def evidence_source(db: Session, code: str) -> EvidenceSource | None:
    return db.scalar(_published(EvidenceSource).where(EvidenceSource.code == code))


def evidence_claims(
    db: Session, entity: str | None = None, entity_code: str | None = None,
) -> list[EvidenceClaim]:
    stmt = _published(EvidenceClaim).order_by(EvidenceClaim.entity, EvidenceClaim.entity_code, EvidenceClaim.field)
    if entity:
        stmt = stmt.where(EvidenceClaim.entity == entity)
    if entity_code:
        stmt = stmt.where(EvidenceClaim.entity_code == entity_code)
    return list(db.scalars(stmt))


def technology_nodes(db: Session) -> list[TechnologyNode]:
    return list(db.scalars(_published(TechnologyNode).order_by(TechnologyNode.node_type, TechnologyNode.code)))


def dependency_edges(db: Session) -> list[DependencyEdge]:
    return list(db.scalars(_published(DependencyEdge).order_by(DependencyEdge.id)))
