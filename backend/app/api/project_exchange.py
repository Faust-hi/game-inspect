"""Обмен с проектом движка: импорт анкеты из файлов и экспорт пресетов.

Оба направления честные по построению. Импорт заполняет только надёжно
извлечённые поля и показывает всё остальное как заметки. Экспорт помечает
каждую строку источником: выбранный метод либо значение по умолчанию.
"""
from __future__ import annotations

from fastapi import APIRouter, File, HTTPException, UploadFile

from ..config import settings
from ..schemas.catalog import (
    BasketRequest, ProjectImportOut, ProjectPresetsOut, ProjectProfile,
)
from ..services import presets, project_import

router = APIRouter(prefix="", tags=["Обмен с проектом"])

#: Те же ограничения, что у административного импорта: файлы настроек маленькие.
MAX_FILES = 10


async def _read_limited(file: UploadFile) -> bytes:
    """Прочитать файл с ограничением размера (защита от исчерпания памяти)."""
    limit = settings.IMPORT_MAX_BYTES
    chunks: list[bytes] = []
    total = 0
    while True:
        chunk = await file.read(64 * 1024)
        if not chunk:
            break
        total += len(chunk)
        if total > limit:
            raise HTTPException(
                413,
                f"Файл больше допустимого размера {limit // (1024 * 1024)} МБ.",
            )
        chunks.append(chunk)
    return b"".join(chunks)


@router.post("/project-import", response_model=ProjectImportOut, summary="Собрать анкету из файлов проекта движка")
async def project_import_endpoint(files: list[UploadFile] = File(...)):
    """Принимает .uproject, ProjectSettings.asset, ProjectVersion.txt, URP-ассеты,
    project.godot и Default*.ini. Возвращает частичный профиль и прозрачность."""
    if not files:
        raise HTTPException(400, "Не загружено ни одного файла")
    if len(files) > MAX_FILES:
        raise HTTPException(413, f"Не больше {MAX_FILES} файлов за раз.")
    parsed = project_import.import_project(
        [(file.filename or "", await _read_limited(file)) for file in files]
    )
    try:
        profile = ProjectProfile(**parsed["filled"])
    except Exception:  # noqa: BLE001 — кривой профиль не должен ронять эндпоинт
        raise HTTPException(422, "Из файлов не удалось собрать корректную анкету")
    return {
        "profile": profile,
        "filled": sorted(parsed["filled"]),
        "suggested": parsed["suggested"],
        "detected": parsed["detected"],
        "warnings": parsed["warnings"],
    }


@router.post("/project-presets", response_model=ProjectPresetsOut, summary="Сгенерировать пресеты движков из корзины")
def project_presets(payload: BasketRequest):
    """Три файла: DefaultScalability.ini, пресет качества Unity и пресет
    рендеринга Godot. Каждая строка знает свой источник."""
    return {"files": presets.build_preset_files(payload.profile, payload.basket or [])}
