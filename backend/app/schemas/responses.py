"""Модели ответов, которые раньше отдавались «сырыми» словарями.

Пока ответ собран вручную из словарей, он не описан в схеме OpenAPI: документация
молчит, а клиент не может получить из неё типы. Описание ответа моделью стоит
недёшевого, но именно оно делает контракт проверяемым — расхождение между
backend и frontend становится ошибкой сборки, а не сообщением пользователя.
"""
from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from .catalog import HardwareCPUOut, HardwareGPUOut, ProjectProfile


class EnumOptionOut(BaseModel):
    """Вариант перечисления для выпадающего списка."""

    value: str
    label: str


class EnumsOut(BaseModel):
    """Все перечисления, нужные для построения анкеты."""

    formats: list[EnumOptionOut] = Field(default_factory=list)
    world_types: list[EnumOptionOut] = Field(default_factory=list)
    scales: list[EnumOptionOut] = Field(default_factory=list)
    stages: list[EnumOptionOut] = Field(default_factory=list)
    platforms: list[EnumOptionOut] = Field(default_factory=list)
    levels: list[EnumOptionOut] = Field(default_factory=list)
    priorities: list[EnumOptionOut] = Field(default_factory=list)
    solution_levels: list[EnumOptionOut] = Field(default_factory=list)
    late_costs: list[EnumOptionOut] = Field(default_factory=list)
    calc_modes: list[EnumOptionOut] = Field(default_factory=list)
    relation_types: list[EnumOptionOut] = Field(default_factory=list)
    conflict_types: list[EnumOptionOut] = Field(default_factory=list)
    statuses: list[EnumOptionOut] = Field(default_factory=list)
    method_kinds: list[EnumOptionOut] = Field(default_factory=list)


class HardwareCatalogOut(BaseModel):
    """Каталог оборудования: только опубликованные записи."""

    cpu: list[HardwareCPUOut] = Field(default_factory=list)
    gpu: list[HardwareGPUOut] = Field(default_factory=list)


class HealthOut(BaseModel):
    """Сводное состояние сервиса."""

    status: str
    version: str
    environment: str | None = None
    database: str


class HealthShortOut(BaseModel):
    """Короткий ответ проверок «жив» и «готов»: полей меньше, чем в сводном."""

    status: str
    version: str | None = None
    database: str | None = None


class ValidationIssueOut(BaseModel):
    """Замечание проверки целостности базы знаний."""

    entity: str
    entity_code: str
    severity: str
    message: str


class AdminOverviewOut(BaseModel):
    """Сводка наполнения базы и список замечаний."""

    counts: dict[str, Any] = Field(default_factory=dict)
    issues: list[ValidationIssueOut] = Field(default_factory=list)
    issues_by_severity: dict[str, int] = Field(default_factory=dict)


class ValidateOut(BaseModel):
    issues: list[ValidationIssueOut] = Field(default_factory=list)
    total: int = 0


class MethodSaveOut(BaseModel):
    """Результат сохранения метода: черновик при создании, прежний статус при правке."""

    created: bool
    code: str
    status: str


class StatusChangeOut(BaseModel):
    code: str
    status: str
    previous_status: str


class DeleteOut(BaseModel):
    deleted: str


class LinkOut(BaseModel):
    method: str
    tool: str
    relation: str


class ImportResultOut(BaseModel):
    entity: str
    created: int = 0
    updated: int = 0
    skipped: int = 0


class PublicationLogOut(BaseModel):
    entity: str
    entity_code: str
    from_status: str | None = None
    to_status: str
    actor: str = ""
    comment: str | None = None
    created_at: str = ""


class ProjectSavedOut(BaseModel):
    public_id: str
    ttl_days: int = 0


class ProjectLoadOut(BaseModel):
    public_id: str
    name: str
    profile: ProjectProfile
    basket: list[str] = Field(default_factory=list)
    updated_at: str = ""
