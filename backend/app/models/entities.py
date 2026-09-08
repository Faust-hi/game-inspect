"""ORM-модели базы инженерных знаний."""
from __future__ import annotations

import datetime as dt
from typing import Any

from sqlalchemy import (
    JSON, Boolean, CheckConstraint, DateTime, Float, ForeignKey, Integer, String, Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base
from ..models.enums import EffectScope, Status
from ..timeutil import utcnow

PUBLISHED = Status.PUBLISHED.value
DRAFT = Status.DRAFT.value

#: Ограничение статуса. Дублируется в БД, чтобы ни один запрос в обход
#: приложения не мог записать произвольное значение.
STATUS_CHECK = CheckConstraint(
    "status in ('draft', 'reviewed', 'published')", name="ck_status_values",
)


def _now() -> dt.datetime:
    """Текущий момент для колонок `created_at` / `updated_at`.

    Значение «наивное» и находится в UTC: колонка объявлена без сведений о
    часовом поясе, и при чтении база отдаёт время именно в таком виде.
    """
    return utcnow()


class GameFunction(Base):
    """Игровая функция — что именно должно работать в игре."""

    __tablename__ = "game_functions"
    __table_args__ = (
        UniqueConstraint("code", name="uq_game_functions_code"),
        STATUS_CHECK,
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="")
    category: Mapped[str] = mapped_column(String(80), default="общее")
    formats: Mapped[list[str]] = mapped_column(JSON, default=list)          # 2D / 2.5D / 3D
    typical_world_types: Mapped[list[str]] = mapped_column(JSON, default=list)
    sort_order: Mapped[int] = mapped_column(Integer, default=100)
    status: Mapped[str] = mapped_column(String(20), default=DRAFT, index=True)
    source_title: Mapped[str] = mapped_column(String(300), default="")
    source_url: Mapped[str] = mapped_column(String(600), default="")
    source_date: Mapped[str] = mapped_column(String(20), default="")
    updated_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=_now, onupdate=_now)

    methods: Mapped[list["Method"]] = relationship(back_populates="function", cascade="all, delete-orphan")


class Method(Base):
    """Вариант реализации функции или общий метод оптимизации."""

    __tablename__ = "methods"
    __table_args__ = (
        UniqueConstraint("code", name="uq_methods_code"),
        STATUS_CHECK,
        # Оценки вне этих границ делают запись несравнимой с остальными
        # и искажают TOPSIS, поэтому диапазоны закреплены в схеме.
        CheckConstraint("performance_gain between 0.0 and 1.0", name="ck_methods_gain"),
        CheckConstraint("confidence between 0.0 and 1.0", name="ck_methods_confidence"),
        CheckConstraint("implementation_cost between 1 and 5", name="ck_methods_cost"),
        CheckConstraint("complexity between 1 and 5", name="ck_methods_complexity"),
        CheckConstraint("quality_impact between -2 and 2", name="ck_methods_quality"),
        CheckConstraint("concept_impact between -2 and 0", name="ck_methods_concept"),
        CheckConstraint("impact_cpu between -3 and 3", name="ck_methods_impact_cpu"),
        CheckConstraint("impact_gpu between -3 and 3", name="ck_methods_impact_gpu"),
        CheckConstraint("impact_ram between -3 and 3", name="ck_methods_impact_ram"),
        CheckConstraint("impact_vram between -3 and 3", name="ck_methods_impact_vram"),
        CheckConstraint("impact_disk between -3 and 3", name="ck_methods_impact_disk"),
        CheckConstraint("impact_network between -3 and 3", name="ck_methods_impact_network"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    kind: Mapped[str] = mapped_column(String(20), default="optimization")  # implementation | optimization
    function_id: Mapped[int | None] = mapped_column(ForeignKey("game_functions.id"), nullable=True)

    summary: Mapped[str] = mapped_column(Text, default="")
    description: Mapped[str] = mapped_column(Text, default="")
    problem: Mapped[str] = mapped_column(Text, default="")        # какую проблему решает
    pros: Mapped[list[str]] = mapped_column(JSON, default=list)
    cons: Mapped[list[str]] = mapped_column(JSON, default=list)
    limitations: Mapped[list[str]] = mapped_column(JSON, default=list)

    # Классификация решения
    level: Mapped[str] = mapped_column(String(20), default="algorithm")
    recommended_stage: Mapped[str] = mapped_column(String(20), default="prototype")
    late_cost: Mapped[str] = mapped_column(String(20), default="medium")
    calc_mode: Mapped[str] = mapped_column(String(20), default="realtime")
    # Область эффекта: только клиентская нагрузка участвует в оценке
    # оборудования игрока (см. `EffectScope`).
    effect_scope: Mapped[str] = mapped_column(String(20), default=EffectScope.CLIENT.value)

    # Влияние на подсистемы: -2..+2 (отрицательное = снижает нагрузку)
    impact_cpu: Mapped[int] = mapped_column(Integer, default=0)
    impact_gpu: Mapped[int] = mapped_column(Integer, default=0)
    impact_ram: Mapped[int] = mapped_column(Integer, default=0)
    impact_vram: Mapped[int] = mapped_column(Integer, default=0)
    impact_disk: Mapped[int] = mapped_column(Integer, default=0)
    impact_network: Mapped[int] = mapped_column(Integer, default=0)

    # -2..+2 : качество; -2..0 : концепция
    quality_impact: Mapped[int] = mapped_column(Integer, default=0)
    concept_impact: Mapped[int] = mapped_column(Integer, default=0)

    # Ожидаемый эффект и стоимость
    performance_gain: Mapped[float] = mapped_column(Float, default=0.5)  # 0..1
    implementation_cost: Mapped[int] = mapped_column(Integer, default=3)  # 1..5
    complexity: Mapped[int] = mapped_column(Integer, default=3)           # 1..5
    confidence: Mapped[float] = mapped_column(Float, default=0.7)         # 0..1 достоверность оценки
    requires_prototype: Mapped[bool] = mapped_column(Boolean, default=False)

    # Применимость
    applicable_formats: Mapped[list[str]] = mapped_column(JSON, default=list)
    applicable_world_types: Mapped[list[str]] = mapped_column(JSON, default=list)
    applicable_engines: Mapped[list[str]] = mapped_column(JSON, default=list)
    applicable_platforms: Mapped[list[str]] = mapped_column(JSON, default=list)
    requires_features: Mapped[list[str]] = mapped_column(JSON, default=list)   # коды функций
    requires_hw_features: Mapped[list[str]] = mapped_column(JSON, default=list)  # например ["Hardware Ray Tracing"]
    requires_conditions: Mapped[list[str]] = mapped_column(JSON, default=list)  # текстовые условия применимости
    min_scale: Mapped[str | None] = mapped_column(String(20), nullable=True)

    # Проверка решения
    verification_method: Mapped[str] = mapped_column(Text, default="")
    verification_tools: Mapped[list[str]] = mapped_column(JSON, default=list)

    # Алгоритм применения: упорядоченные шаги внедрения решения.
    # Отдельно от description, чтобы карточка метода отвечала на вопрос «как
    # внедрить», а не только «что это и зачем».
    application_steps: Mapped[list[str]] = mapped_column(JSON, default=list)

    status: Mapped[str] = mapped_column(String(20), default=DRAFT, index=True)
    source_title: Mapped[str] = mapped_column(String(300), default="")
    source_url: Mapped[str] = mapped_column(String(600), default="")
    source_date: Mapped[str] = mapped_column(String(20), default="")
    updated_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=_now, onupdate=_now)

    function: Mapped["GameFunction | None"] = relationship(back_populates="methods")
    engine_links: Mapped[list["MethodEngineLink"]] = relationship(back_populates="method", cascade="all, delete-orphan")


class Engine(Base):
    """Игровой движок."""

    __tablename__ = "engines"
    __table_args__ = (UniqueConstraint("code", name="uq_engines_code"), STATUS_CHECK)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    vendor: Mapped[str] = mapped_column(String(120), default="")
    versions: Mapped[list[str]] = mapped_column(JSON, default=list)
    supported_formats: Mapped[list[str]] = mapped_column(JSON, default=list)
    notes: Mapped[str] = mapped_column(Text, default="")
    docs_url: Mapped[str] = mapped_column(String(600), default="")
    status: Mapped[str] = mapped_column(String(20), default=DRAFT)
    updated_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=_now, onupdate=_now)

    tools: Mapped[list["EngineTool"]] = relationship(back_populates="engine", cascade="all, delete-orphan")


class EngineTool(Base):
    """Инструмент / подсистема игрового движка."""

    __tablename__ = "engine_tools"
    __table_args__ = (UniqueConstraint("code", name="uq_engine_tools_code"), STATUS_CHECK)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    engine_id: Mapped[int] = mapped_column(ForeignKey("engines.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    subsystem: Mapped[str] = mapped_column(String(80), default="")
    description: Mapped[str] = mapped_column(Text, default="")
    tool_type: Mapped[str] = mapped_column(String(40), default="runtime")  # runtime | editor | profiler | build
    docs_url: Mapped[str] = mapped_column(String(600), default="")
    status: Mapped[str] = mapped_column(String(20), default=DRAFT)
    updated_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=_now, onupdate=_now)

    engine: Mapped["Engine"] = relationship(back_populates="tools")
    method_links: Mapped[list["MethodEngineLink"]] = relationship(back_populates="tool", cascade="all, delete-orphan")


class MethodEngineLink(Base):
    """Связь общего метода с конкретным инструментом движка."""

    __tablename__ = "method_engine_links"
    __table_args__ = (UniqueConstraint("method_id", "tool_id", name="uq_method_tool"), STATUS_CHECK)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    method_id: Mapped[int] = mapped_column(ForeignKey("methods.id"), nullable=False)
    tool_id: Mapped[int] = mapped_column(ForeignKey("engine_tools.id"), nullable=False)
    relation_type: Mapped[str] = mapped_column(String(20), default="direct")
    note: Mapped[str] = mapped_column(Text, default="")
    source_url: Mapped[str] = mapped_column(String(600), default="")
    status: Mapped[str] = mapped_column(String(20), default=DRAFT)
    updated_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=_now, onupdate=_now)

    method: Mapped["Method"] = relationship(back_populates="engine_links")
    tool: Mapped["EngineTool"] = relationship(back_populates="method_links")


class Conflict(Base):
    """Конфликт, зависимость или усиление между методами."""

    __tablename__ = "conflicts"
    __table_args__ = (
        UniqueConstraint("a_code", "b_code", "conflict_type", name="uq_conflict_pair"),
        STATUS_CHECK,
        CheckConstraint("severity between 1 and 3", name="ck_conflicts_severity"),
        CheckConstraint("a_code <> b_code", name="ck_conflicts_distinct"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    a_code: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    b_code: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    conflict_type: Mapped[str] = mapped_column(String(20), default="conflict")
    severity: Mapped[int] = mapped_column(Integer, default=2)  # 1..3
    description: Mapped[str] = mapped_column(Text, default="")
    resolution: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(20), default=DRAFT)
    source_url: Mapped[str] = mapped_column(String(600), default="")
    updated_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=_now, onupdate=_now)


class HardwareCPU(Base):
    __tablename__ = "hardware_cpu"
    __table_args__ = (
        UniqueConstraint("model", name="uq_hw_cpu_model"),
        STATUS_CHECK,
        CheckConstraint("single_thread_score between 0.0 and 1.0", name="ck_cpu_single"),
        CheckConstraint("multi_thread_score between 0.0 and 1.0", name="ck_cpu_multi"),
        CheckConstraint("perf_class between 1 and 5", name="ck_cpu_class"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    vendor: Mapped[str] = mapped_column(String(40), default="")
    model: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    generation: Mapped[str] = mapped_column(String(80), default="")
    architecture: Mapped[str] = mapped_column(String(80), default="")
    release_year: Mapped[int] = mapped_column(Integer, default=0)
    cores: Mapped[int] = mapped_column(Integer, default=0)
    threads: Mapped[int] = mapped_column(Integer, default=0)
    base_clock_ghz: Mapped[float] = mapped_column(Float, default=0.0)
    boost_clock_ghz: Mapped[float] = mapped_column(Float, default=0.0)
    tdp_w: Mapped[int] = mapped_column(Integer, default=0)
    memory_support: Mapped[str] = mapped_column(String(60), default="")
    memory_channels: Mapped[int] = mapped_column(Integer, default=2)
    single_thread_score: Mapped[float] = mapped_column(Float, default=0.0)
    multi_thread_score: Mapped[float] = mapped_column(Float, default=0.0)
    perf_class: Mapped[int] = mapped_column(Integer, default=3, index=True)
    notes: Mapped[str] = mapped_column(Text, default="")
    source_title: Mapped[str] = mapped_column(String(300), default="")
    source_url: Mapped[str] = mapped_column(String(600), default="")
    source_date: Mapped[str] = mapped_column(String(20), default="")
    status: Mapped[str] = mapped_column(String(20), default=DRAFT)
    updated_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=_now, onupdate=_now)


class HardwareGPU(Base):
    __tablename__ = "hardware_gpu"
    __table_args__ = (
        UniqueConstraint("model", name="uq_hw_gpu_model"),
        STATUS_CHECK,
        CheckConstraint("raster_score between 0.0 and 1.0", name="ck_gpu_raster"),
        CheckConstraint("rt_score between 0.0 and 1.0", name="ck_gpu_rt"),
        CheckConstraint("perf_class between 1 and 5", name="ck_gpu_class"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    vendor: Mapped[str] = mapped_column(String(40), default="")
    model: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    generation: Mapped[str] = mapped_column(String(80), default="")
    architecture: Mapped[str] = mapped_column(String(80), default="")
    release_year: Mapped[int] = mapped_column(Integer, default=0)
    vram_gb: Mapped[float] = mapped_column(Float, default=0.0)
    vram_type: Mapped[str] = mapped_column(String(40), default="")
    memory_bandwidth_gbs: Mapped[float] = mapped_column(Float, default=0.0)
    bus_width_bit: Mapped[int] = mapped_column(Integer, default=0)
    tdp_w: Mapped[int] = mapped_column(Integer, default=0)
    api_support: Mapped[list[str]] = mapped_column(JSON, default=list)
    hw_features: Mapped[list[str]] = mapped_column(JSON, default=list)
    raster_score: Mapped[float] = mapped_column(Float, default=0.0)
    rt_score: Mapped[float] = mapped_column(Float, default=0.0)
    perf_class: Mapped[int] = mapped_column(Integer, default=3, index=True)
    notes: Mapped[str] = mapped_column(Text, default="")
    source_title: Mapped[str] = mapped_column(String(300), default="")
    source_url: Mapped[str] = mapped_column(String(600), default="")
    source_date: Mapped[str] = mapped_column(String(20), default="")
    status: Mapped[str] = mapped_column(String(20), default=DRAFT)
    updated_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=_now, onupdate=_now)


class PublicationLog(Base):
    """Журнал изменений статуса записей базы знаний.

    Публикация меняет то, что видят все пользователи. Без журнала невозможно
    ответить на вопрос, кто и когда вывел запись в публичный каталог.
    """

    __tablename__ = "publication_log"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    entity: Mapped[str] = mapped_column(String(60), default="", index=True)
    entity_code: Mapped[str] = mapped_column(String(120), default="", index=True)
    from_status: Mapped[str] = mapped_column(String(20), default="")
    to_status: Mapped[str] = mapped_column(String(20), default="")
    actor: Mapped[str] = mapped_column(String(80), default="")
    comment: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=_now)


class ValidationIssue(Base):
    """Замечание проверки целостности базы знаний (для административного раздела)."""

    __tablename__ = "validation_issues"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    entity: Mapped[str] = mapped_column(String(60), default="")
    entity_code: Mapped[str] = mapped_column(String(120), default="")
    severity: Mapped[str] = mapped_column(String(20), default="warning")  # error | warning | info
    message: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=_now)
