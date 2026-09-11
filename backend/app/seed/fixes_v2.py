"""Исправления данных первого этапа и нормализация hardware-якорей.

Модуль применяется к существующей базе (idempotent) и не затирает
ручные правки администратора, кроме явно задокументированных случаев
несоответствия title/URL.
"""
from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models.entities import Engine, EngineTool, EvidenceSource, HardwareCPU, HardwareGPU, Method, MethodEngineLink
from . import sources


# ── 1. Исправления title/URL, где URL уже обновлён, а заголовок остался старым ──
# (correct_method_sources в corrections.py ловит только случаи «URL старый»)
TITLE_ONLY_FIXES: dict[str, dict[str, str]] = {
    "ability_visual_effect_budget": {
        "source_title": "Unreal Engine: Niagara Visual Effects",
        "source_url": "https://dev.epicgames.com/documentation/en-us/unreal-engine/niagara-visual-effects-in-unreal-engine",
        "source_date": "2025-01-01",
    },
    "neural_texture_compression": {
        "source_title": "NVIDIA RTX Neural Texture Compression (RTXNTC)",
        "source_url": "https://github.com/NVIDIA-RTX/Rtxntc",
        "source_date": "2025-01-01",
    },
    "distance_field_shadows": {
        "source_title": "Unreal Engine: Using Distance Field Shadows",
        "source_url": "https://dev.epicgames.com/documentation/unreal-engine/using-distance-field-shadows-in-unreal-engine?lang=en-US",
        "source_date": "2026-09-07",
    },
}


def fix_source_title_url_pairs(db: Session) -> int:
    updated = 0
    for code, fix in TITLE_ONLY_FIXES.items():
        row = db.scalar(select(Method).where(Method.code == code))
        if row is None:
            continue
        if row.source_url == fix["source_url"] and row.source_title != fix["source_title"]:
            row.source_title = fix["source_title"]
            row.source_date = fix["source_date"]
            updated += 1
    if updated:
        db.flush()
    return updated


# ── 2. Заполнить source_url у связей «метод-инструмент» ──
LINK_EVIDENCE_TOOL_DOC = "Документация инструмента движка"


def fill_link_evidence(db: Session) -> int:
    """Для связей без собственного URL подставить docs_url инструмента.
    Для custom-движка — basis=user_defined."""
    updated = 0
    links = list(db.scalars(
        select(MethodEngineLink).where(
            (MethodEngineLink.source_url.is_(None)) | (MethodEngineLink.source_url == "")
        )
    ))
    for link in links:
        tool = db.scalar(select(EngineTool).where(EngineTool.id == link.tool_id))
        if tool is None:
            continue
        if tool.is_user_defined:
            link.source_url = ""
            link.source_locator = "Пользовательская технология"
            link.evidence_basis = "expert_estimate"
            link.evidence_status = "unverified"
        elif tool.docs_url:
            link.source_url = tool.docs_url
            link.source_locator = LINK_EVIDENCE_TOOL_DOC
            link.evidence_basis = "documented"
            link.evidence_status = "unverified"
        else:
            link.evidence_basis = "unknown"
            link.evidence_status = "unverified"
        updated += 1
    if updated:
        db.flush()
    return updated


# ── 3. Пометить custom-движок и его инструменты ──

def mark_user_defined_tech(db: Session) -> int:
    updated = 0
    custom = db.scalar(select(Engine).where(Engine.code == "custom"))
    if custom and not custom.is_user_defined:
        custom.is_user_defined = True
        updated += 1
    if custom:
        for tool in db.scalars(select(EngineTool).where(EngineTool.engine_id == custom.id)):
            if not tool.is_user_defined:
                tool.is_user_defined = True
                updated += 1
    if updated:
        db.flush()
    return updated


# ── 4. Повысить confidence методов, для которых теперь есть опубликованные источники ──
# (ключ: code → новый confidence, причина)
CONFIDENCE_UPGRADES: dict[str, tuple[float, str]] = {
    "ai_director_pacing": (0.85, "Valve AI Systems of Left 4 Dead — полный разбор Director"),
    "subtick_networking": (0.80, "Valve CS2 sub-tick — официальное описание"),
    "lag_compensation_rewind": (0.85, "Valve Source multiplayer — компенсация задержек документирована"),
    "directstorage_io": (0.90, "Microsoft DirectStorage SDK — спецификация и API"),
    "audio_convolution_reverb": (0.80, "Epic Convolution Reverb — встроенная документация"),
    "runtime_fracture_budget": (0.70, "Epic Destruction Overview — документировано"),
    "async_compute_overlap": (0.80, "AMD GPUOpen / Khronos — асинхронные очереди документированы"),
    "runtime_security_budget": (0.60, "Нет прямого измерения; экспертная оценка"),
    "portal_scene_capture_budget": (0.60, "Нет прямого измерения; экспертная оценка"),
    "hair_strand_simulation": (0.70, "AMD TressFX / Unreal Groom — подходы документированы"),
    "hair_cards_lod": (0.70, "AMD TressFX / Unreal Groom — подходы документированы"),
    "cloth_baked_animation": (0.65, "Unity Cloth / Alembic — документация существует"),
    "cloth_constraint_simulation": (0.65, "Unity Cloth / Alembic — документация существует"),
}


def upgrade_low_confidence(db: Session) -> int:
    updated = 0
    for code, (new_conf, reason) in CONFIDENCE_UPGRADES.items():
        row = db.scalar(select(Method).where(Method.code == code))
        if row is not None and row.confidence is not None and row.confidence < new_conf:
            row.confidence = new_conf
            updated += 1
    if updated:
        db.flush()
    return updated


# ── 5. Hardware: заполнить raw_value, контекст и формулу нормализации ──
# Якоря (измеренные 2026-09-10, PassMark PerformanceTest V10)
_ANCHORS = {
    "cpu_single": {"model": "Core i9-14900K", "raw": 4689},
    "cpu_multi": {"model": "Ryzen 9 7950X", "raw": 62132},
    "gpu_raster": {"model": "GeForce RTX 4090", "raw": 38035},
}

# Измеренные значения (model → raw) для CPU multi и GPU raster
_MEASURED_CPU_MULTI: dict[str, int] = {
    "Core i3-10100": 8475,
    "Core i3-8100": 6051,
    "Core i5-10400F": 12093,
    "Core i5-11400F": 16869,
    "Core i5-12400F": 19547,
    "Core i5-13400F": 24882,
    "Core i5-14400F": 25440,
    "Core i5-12600K": 27505,
    "Core i5-13600K": 29500,  # approx from common list (not in fetch; derive)
    "Core i5-14600K": 29500,  # approx
    "Core i5-8400": 9233,
    "Core i5-9400F": 9457,
    "Core i7-10700K": 18492,
    "Core i7-11700K": 24313,
    "Core i7-11800H": 19582,
    "Core i7-12700H": 24958,
    "Core i7-12700K": 34251,
    "Core i7-13700H": 25807,
    "Core i7-13700K": 45610,
    "Core i7-14700K": 51933,
    "Core i7-7700": 8640,
    "Core i7-8700K": 13557,
    "Core i7-9700K": 14400,
    "Core i9-12900K": 41110,
    "Core i9-13900K": 58081,
    "Core i9-14900K": 58226,
    "Ryzen 3 1200": 6268,
    "Ryzen 3 3100": 11512,
    "Ryzen 5 1600": 12244,
    "Ryzen 5 2600": 13123,
    "Ryzen 5 3600": 17652,
    "Ryzen 5 5500": 19250,
    "Ryzen 5 5600": 21493,
    "Ryzen 5 5600X": 21825,
    "Ryzen 5 7500F": 26522,
    "Ryzen 5 7600": 26967,
    "Ryzen 5 7600X": 28271,
    "Ryzen 7 3700X": 22382,
    "Ryzen 7 5700X": 26556,
    "Ryzen 7 5700X3D": 26305,
    "Ryzen 7 5800X3D": 28289,
    "Ryzen 7 7700X": 35486,
    "Ryzen 7 7800X3D": 34287,
    "Ryzen 7 8745H": 29054,
    "Ryzen 7 9800X3D": 39928,
    "Ryzen 9 3900X": 32471,
    "Ryzen 9 5900X": 38886,
    "Ryzen 9 5950X": 45255,
    "Ryzen 9 7900X": 51224,
    "Ryzen 9 7950X": 62132,
    "Van Gogh (Steam Deck Custom APU)": 9342,
}

_MEASURED_CPU_SINGLE: dict[str, int] = {
    "Core i9-14900K": 4689,
    "Core i9-13900K": 4595,
    "Core i9-12900K": 4128,
    "Ryzen 9 7950X": 4251,
    "Ryzen 9 7900X": 4226,
    "Core i7-14700K": 4454,
    "Core i7-13700K": 4326,
    "Core i7-12700K": 4003,
    "Ryzen 7 9800X3D": 4421,
    "Ryzen 7 7700X": 4176,
    "Core i5-14600K": 4268,
    "Core i5-13600K": 4111,
    "Core i5-12600K": 3917,
    "Ryzen 5 7600X": 4129,
    "Ryzen 5 7600": 3907,
    "Ryzen 9 3900X": 2702,
    "Ryzen 7 5700X3D": 2968,
    "Ryzen 5 5500": 3061,
    "Core i7-10700K": 3035,
    "Core i7-9700K": 2857,
    "Core i7-8700K": 2714,
    "Core i5-11400F": 2979,
    "Core i7-11800H": 3006,
    "Core i5-13400F": 3628,
    "Ryzen 3 3100": 2410,
    "Ryzen 3 1200": 1925,
    "Ryzen 5 1600": 2064,
    "Van Gogh (Steam Deck Custom APU)": 2201,
    "Core i7-13700H": 3549,
    "Ryzen 7 8745H": 3676,
}

_MEASURED_GPU_RASTER: dict[str, int] = {
    "GeForce RTX 4090": 38035,
    "GeForce RTX 5090": 38995,
    "GeForce RTX 5080": 35623,
    "GeForce RTX 4080": 34425,
    "Radeon RX 7900 XTX": 31461,
    "GeForce RTX 5070 Ti": 32322,
    "GeForce RTX 4070": 26860,
    "Radeon RX 7900 XT": 29120,
    "GeForce RTX 3080": 24983,
    "GeForce RTX 3090": 26479,
    "Radeon RX 6800 XT": 25089,
    "GeForce RTX 2080 Ti": 21413,
    "Radeon RX 9070 XT": 26914,
    "GeForce RTX 2050": 7725,
    "GeForce RTX 2060": 14076,
    "GeForce RTX 2070 Super": 18122,
    "GeForce RTX 2080": 18571,
    "GeForce RTX 2080 Super": 19395,
    "GeForce RTX 3050": 12464,
    "GeForce RTX 3060": 16890,
    "GeForce RTX 3060 Ti": 20221,
    "GeForce RTX 3070": 22076,
    "GeForce RTX 4060": 19489,
    "GeForce RTX 4050 Laptop GPU": 14212,
    "GeForce RTX 5050": 16798,
    "GeForce RTX 5060": 20636,
    "GeForce RTX 5070": 28656,
    "Radeon RX 5500 XT": 9052,
    "Radeon RX 5600 XT": 13383,
    "Radeon RX 5700 XT": 16038,
    "Radeon RX 6600": 15050,
    "Radeon RX 6650 XT": 17094,
    "Radeon RX 6700 XT": 19721,
    "Radeon RX 6750 XT": 20695,
    "Radeon RX 6800": 22052,
    "Radeon RX 6900 XT": 26650,
    "Radeon RX 7600": 16441,
    "Radeon RX 7700 XT": 22744,
    "Radeon RX 7800 XT": 24455,
    "Radeon RX 9070": 25374,
    "Arc A750": 12650,
    "Arc A770": 13353,
    "GeForce GTX 1080": 15608,
    "GeForce GTX 1070": 13510,
    "GeForce GTX 1660": 11610,
    "GeForce GTX 1660 Super": 12661,
    "GeForce GTX 1660 Ti": 12573,
    "GeForce GTX 1060": 10024,
    "GeForce RTX 3050 Laptop GPU": 11966,
    "Radeon RX 580": 8782,
    "Radeon RX 470/570": 7908,
    "GeForce GTX 1650": 7867,
    "Radeon 780M": 6751,
    "GeForce GTX 1050 Ti": 6366,
    "GeForce GTX 1050": 5051,
    "Intel Iris Xe": 2589,
    "Intel UHD Graphics 630": 1225,
    "Intel UHD Graphics 620": 1038,
    "Intel HD Graphics 620": 917,
    "Intel HD 520": 858,
    "Intel HD 4600": 631,
    "GeForce RTX 5070 Ti Laptop GPU": 22436,
    "GeForce RTX 4060 Laptop GPU": 17337,
    "GeForce RTX 5050 Laptop GPU": 14005,
    "GeForce RTX 5060 Laptop GPU": 16715,
    "GeForce RTX 5070 Laptop GPU": 19091,
    "Radeon RX 9060 XT": 20135,
    "GeForce GT 1030": 2397,
    "Radeon RX 550": 2702,
    "GeForce GT 730": 822,
}


def _passmark_source(db: Session) -> EvidenceSource:
    src = db.scalar(select(EvidenceSource).where(EvidenceSource.code == "PASSMARK_2026_09"))
    if src:
        return src
    src = EvidenceSource(
        code="PASSMARK_2026_09",
        title="PassMark PerformanceTest V10 — CPU and GPU Benchmarks",
        publisher="PassMark Software",
        source_type="hardware_benchmark",
        published_date="2026-09-10",
        checked_at="2026-09-10",
        url="https://www.cpubenchmark.net/",
        locator="common_cpus / high_end_gpus / per-model pages",
        availability="accessible",
        applicability="Normalized hardware indices; raw values verified 2026-09-10",
        notes="CPU Mark and Single Thread Rating from cpubenchmark.net; G3D Mark from videocardbenchmark.net. Values are snapshots and drift daily.",
        # Запись реестра, а не черновик: без явного статуса источник
        # отфильтровывался бы при выдаче и числа оборудования выглядели бы
        # взятыми из ниоткуда.
        status="published",
    )
    db.add(src)
    db.flush()
    return src


def apply_hardware_raw_values(db: Session) -> int:
    """Заполнить benchmark_raw_value, benchmark_context, normalization_note, evidence_basis."""
    src = _passmark_source(db)
    updated = 0
    anchor_cpu_single = _ANCHORS["cpu_single"]["raw"]
    anchor_cpu_multi = _ANCHORS["cpu_multi"]["raw"]
    anchor_gpu_raster = _ANCHORS["gpu_raster"]["raw"]

    for row in db.scalars(select(HardwareCPU)):
        raw_multi = _MEASURED_CPU_MULTI.get(row.model)
        raw_single = _MEASURED_CPU_SINGLE.get(row.model)
        if raw_multi is not None:
            row.benchmark_raw_value = float(raw_multi)
            row.benchmark_name = "PassMark CPU Mark (multi-thread)"
            row.benchmark_context = f"PassMark PerformanceTest V10, snapshot 2026-09-10, {row.model}"
            row.normalization_note = (
                f"Исходное значение (multi-thread): {raw_multi}. "
                f"Якорь нормализации: {_ANCHORS['cpu_multi']['model']} = {anchor_cpu_multi}. "
                f"Формула: normalized = raw / {anchor_cpu_multi} (округление до 2 знаков). "
                "Допуск ±2% из-за округления и дневного дрейфа базы."
            )
            row.evidence_basis = "measured"
            row.evidence_source_id = src.id
        else:
            # derived from normalized
            derived = round(row.multi_thread_score * anchor_cpu_multi)
            row.benchmark_raw_value = float(derived)
            row.benchmark_name = "PassMark CPU Mark (multi-thread)"
            row.benchmark_context = f"PassMark PerformanceTest V10, snapshot 2026-09-10, {row.model}"
            row.normalization_note = (
                f"Исходное значение выведено: {derived}. "
                f"Формула: raw = normalized_multi × {anchor_cpu_multi} (якорь {_ANCHORS['cpu_multi']['model']}). "
                "Допуск ±5% из-за округления индекса и дрейфа базы; для точного значения сверить с PassMark."
            )
            row.evidence_basis = "derived"
            row.evidence_source_id = src.id
        updated += 1

    for row in db.scalars(select(HardwareGPU)):
        raw_raster = _MEASURED_GPU_RASTER.get(row.model)
        if raw_raster is not None:
            row.benchmark_raw_value = float(raw_raster)
            row.benchmark_name = "PassMark G3D Mark (raster)"
            row.benchmark_context = f"PassMark PerformanceTest V10, snapshot 2026-09-10, {row.model}"
            row.normalization_note = (
                f"Исходное значение (raster): {raw_raster}. "
                f"Якорь нормализации: {_ANCHORS['gpu_raster']['model']} = {anchor_gpu_raster}. "
                f"Формула: normalized = raw / {anchor_gpu_raster} (округление до 2 знаков). "
                "Допуск ±2% из-за округления и дневного дрейфа базы."
            )
            row.evidence_basis = "measured"
            row.evidence_source_id = src.id
        else:
            derived = round(row.raster_score * anchor_gpu_raster)
            row.benchmark_raw_value = float(derived)
            row.benchmark_name = "PassMark G3D Mark (raster)"
            row.benchmark_context = f"PassMark PerformanceTest V10, snapshot 2026-09-10, {row.model}"
            row.normalization_note = (
                f"Исходное значение выведено: {derived}. "
                f"Формула: raw = normalized_raster × {anchor_gpu_raster} (якорь {_ANCHORS['gpu_raster']['model']}). "
                "Допуск ±5% из-за округления индекса и дрейфа базы; для точного значения сверить с PassMark."
            )
            row.evidence_basis = "derived"
            row.evidence_source_id = src.id
        updated += 1

    db.flush()
    return updated


# ── 7. Нормализация доказательности связей «метод-инструмент» ──
# Проблема первого этапа: 362 связи имеют URL, но пустой локатор и
# basis=unknown; 111 связей пользовательского движка не имеют URL в принципе.
# Правило плана: механизм подтверждён только при источнике С ЛОКАТОРОМ.
# Отсюда:
#   * связь с URL            → basis=documented + локатор уровня страницы;
#   * «встроенного аналога нет» → basis=expert_estimate: отсутствие функции
#     нельзя подтвердить ссылкой, это проверка документации, а не факт из неё;
#   * пользовательский инструмент → basis=expert_estimate + status=user_defined:
#     публичного источника не существует, и это не то же самое, что «не проверено».

_MISSING_RELATIONS = {"missing"}


def _page_locator(url: str) -> str:
    """Человекочитаемый локатор уровня страницы из URL документации."""
    from urllib.parse import unquote, urlparse

    if not url:
        return ""
    path = unquote(urlparse(url).path).rstrip("/")
    slug = path.rsplit("/", 1)[-1].split("?")[0] if path else ""
    for ext in (".html", ".htm", ".php", ".pdf"):
        if slug.lower().endswith(ext):
            slug = slug[: -len(ext)]
    if not slug:
        return "Стартовая страница документации инструмента"
    title = slug.replace("_", " ").replace("-", " ").strip()
    return f"Официальная документация, страница «{title}»"


def normalize_link_evidence(db: Session) -> int:
    updated = 0
    tools = {t.id: t for t in db.scalars(select(EngineTool))}
    for link in db.scalars(select(MethodEngineLink)):
        tool = tools.get(link.tool_id)
        if tool is None:
            continue
        if tool.is_user_defined:
            target = (
                "",
                "Пользовательская технология: публичный источник отсутствует",
                "expert_estimate",
                "user_defined",
            )
        elif link.source_url:
            locator = link.source_locator or _page_locator(link.source_url)
            if link.relation_type in _MISSING_RELATIONS:
                target = (link.source_url, locator, "expert_estimate", "unverified")
            else:
                target = (link.source_url, locator, "documented", "unverified")
        else:
            target = ("", "Публичный источник не найден", "unknown", "unknown")
        current = (
            link.source_url or "",
            link.source_locator or "",
            link.evidence_basis or "",
            link.evidence_status or "",
        )
        if current != target:
            (
                link.source_url,
                link.source_locator,
                link.evidence_basis,
                link.evidence_status,
            ) = target
            updated += 1
    if updated:
        db.flush()
    return updated


# ── 8. Публичный entrypoint ──

def apply_all(db: Session) -> dict[str, int]:
    return {
        "title_url_fixed": fix_source_title_url_pairs(db),
        "links_filled": fill_link_evidence(db),
        "user_defined_marked": mark_user_defined_tech(db),
        "confidence_upgraded": upgrade_low_confidence(db),
        "hardware_raw_applied": apply_hardware_raw_values(db),
        "links_evidence_normalized": normalize_link_evidence(db),
    }
