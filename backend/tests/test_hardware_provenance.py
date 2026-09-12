"""Провенанс бенчмарков железа и дата публикации источника.

Шесть полей провенанса описывают одно число: `benchmark_raw_value` и то, что
его объясняет — метку основания, ссылку на источник, контекст и примечание.
Если заполнять их по частям, получается строка, где основание заявляет замер,
а число выведено обратно из нормализованного индекса. Тесты фиксируют, что
блок движется целиком: либо курирован, либо пересчитан.

Второй предмет — дата публикации: прежняя версия загрузчика пакетов срезала её
до 20 знаков, теряя оговорку куратора.
"""
from __future__ import annotations

import pytest

from sqlalchemy import select

from app.models.entities import EvidenceSource, HardwareCPU, HardwareGPU
from app.seed import fixes_v2, pack_loader

PROVENANCE_FIELDS = (
    "benchmark_raw_value",
    "benchmark_name",
    "benchmark_context",
    "normalization_note",
    "evidence_basis",
    "evidence_source_id",
)


@pytest.mark.critical
def test_curated_provenance_survives_startup_pass(db_session):
    """Правка администратора не уничтожается стартовыми проходами."""
    row = db_session.scalars(select(HardwareCPU)).first()
    row.benchmark_raw_value = 31000.0
    row.benchmark_name = "Курированный замер"
    row.benchmark_context = "Сверено вручную 2026-09-12"
    row.normalization_note = "Курировано вручную: сверено с PassMark."
    row.evidence_basis = "measured"
    row.evidence_source_id = 936
    db_session.flush()

    filled = fixes_v2.apply_hardware_raw_values(db_session)
    refreshed = fixes_v2.refresh_hardware_raw_values(db_session)

    assert filled == 0, "заполнять было нечего: сырое значение у строки уже есть"
    assert refreshed == 0
    assert row.benchmark_raw_value == 31000.0
    assert row.evidence_basis == "measured"
    assert row.normalization_note == "Курировано вручную: сверено с PassMark."


@pytest.mark.extended
def test_empty_provenance_block_is_filled_whole(db_session):
    """Пробел закрывается всем блоком, а не одним числом."""
    row = db_session.scalars(select(HardwareGPU)).first()
    # Пустое состояние блока: сырого значения нет, метка не определена.
    # Текстовые поля объявлены NOT NULL, поэтому пустота — пустая строка.
    row.benchmark_raw_value = None
    row.benchmark_name = ""
    row.benchmark_context = ""
    row.normalization_note = ""
    row.evidence_basis = "unknown"
    row.evidence_source_id = None
    db_session.flush()

    filled = fixes_v2.apply_hardware_raw_values(db_session)

    assert filled >= 1
    for field in PROVENANCE_FIELDS:
        assert getattr(row, field) not in (None, "", 0), field
    assert row.evidence_basis in {"measured", "derived"}
    assert row.benchmark_name == "PassMark G3D Mark (raster)"
    assert row.benchmark_context


@pytest.mark.extended
def test_measured_basis_matches_a_measured_value(db_session):
    """«Измерено» означает число из словаря замеров, а не вывод из индекса."""
    measured_cpu = set(fixes_v2._MEASURED_CPU_MULTI.values())
    measured_gpu = set(fixes_v2._MEASURED_GPU_RASTER.values())
    for row in db_session.scalars(select(HardwareCPU)):
        if row.evidence_basis == "measured":
            assert float(row.benchmark_raw_value) in measured_cpu, row.model
    for row in db_session.scalars(select(HardwareGPU)):
        if row.evidence_basis == "measured":
            assert float(row.benchmark_raw_value) in measured_gpu, row.model


@pytest.mark.extended
def test_refresh_pass_skips_rows_that_differ_from_previous_value(db_session, monkeypatch):
    """Точечный проход срабатывает только на прежнем значении."""
    row = db_session.scalars(select(HardwareCPU)).first()
    row.benchmark_raw_value = 31000.0
    db_session.flush()
    monkeypatch.setitem(fixes_v2.BENCHMARK_REFRESH, row.model, 29500.0)

    assert fixes_v2.refresh_hardware_raw_values(db_session) == 0
    assert row.benchmark_raw_value == 31000.0

    row.benchmark_raw_value = 29500.0
    db_session.flush()
    assert fixes_v2.refresh_hardware_raw_values(db_session) == 1


@pytest.mark.extended
def test_refresh_pass_is_noop_with_empty_registry(db_session):
    """Пустой реестр — законное состояние: обновлять нечего."""
    assert not fixes_v2.BENCHMARK_REFRESH
    assert fixes_v2.refresh_hardware_raw_values(db_session) == 0


@pytest.mark.extended
def test_truncated_source_date_is_restored(db_session):
    """Обрубок прежнего лимита восстанавливается целиком."""
    src = db_session.scalars(select(EvidenceSource)).first()
    full = "2019-09-17 (последний акт обновления)"
    src.published_date = full[:20]
    db_session.flush()

    assert pack_loader._restore_full_date(src, full) is True
    assert src.published_date == full


@pytest.mark.extended
def test_curated_source_date_is_not_touched(db_session):
    """Иное значение — в том числе курированное — не трогается."""
    src = db_session.scalars(select(EvidenceSource)).first()
    src.published_date = "Проверено вручную 2026-09-12"
    db_session.flush()

    assert pack_loader._restore_full_date(
        src, "2019-09-17 (последний акт обновления)") is False
    assert src.published_date == "Проверено вручную 2026-09-12"
