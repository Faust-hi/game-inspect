"""Обмен с проектом движка: импорт анкеты из файлов и экспорт пресетов.

Оба направления честные по построению. Импорт заполняет только надёжно
извлечённые поля и показывает всё остальное как заметки. Экспорт помечает
каждую строку источником: выбранный метод либо значение по умолчанию.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session
from pydantic import ValidationError

from ..config import settings
from .. import repositories
from ..database import get_db
from ..errors import ApiError, ErrorCode
from ..schemas.catalog import (
    BasketRequest, ProjectImportOut, ProjectPresetsOut, ProjectProfile,
)
from ..services import engines, presets, project_import, rules
from ..schemas.project_file import ProjectFile

router = APIRouter(prefix="", tags=["Обмен с проектом"])

#: Те же ограничения, что у административного импорта: файлы настроек маленькие.
MAX_FILES = 10


@router.post("/project-file-import", response_model=ProjectFile,
             summary="Проверить и восстановить JSON-снимок проекта")
async def project_file_import(file: UploadFile = File(...)):
    content = await _read_limited(file)
    try:
        return ProjectFile.model_validate_json(content)
    except ValidationError as exc:
        raise ApiError("Некорректный файл проекта", code=ErrorCode.VALIDATION,
                       status=422, details=[{"field": ".".join(map(str, error["loc"])),
                                             "message": error["msg"]}
                                            for error in exc.errors()]) from exc


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
    except ValidationError as exc:
        # Причина отказа важна пользователю: он должен понимать, какое именно
        # извлечённое значение не подошло, а не видеть общую ошибку 422.
        raise ApiError(
            "Из файлов не удалось собрать корректную анкету",
            code=ErrorCode.VALIDATION,
            status=422,
            details=[
                {"field": ".".join(str(p) for p in item.get("loc", ())),
                 "message": item.get("msg", "")}
                for item in exc.errors()
            ],
        ) from exc

    extracted = set(parsed["filled"]) & set(ProjectProfile.model_fields)
    return {
        "profile": profile,
        "patch": profile.model_dump(include=extracted, mode="json"),
        "filled": sorted(extracted),
        "suggested": parsed["suggested"],
        "detected": parsed["detected"],
        "warnings": parsed["warnings"],
    }


@router.post("/project-presets", response_model=ProjectPresetsOut, summary="Сгенерировать пресеты движков из корзины")
def project_presets(payload: BasketRequest, db: Session = Depends(get_db)):
    """Три файла: DefaultScalability.ini, пресет качества Unity и пресет
    рендеринга Godot. Каждая строка знает свой источник."""
    engines.require_known(db, payload.profile.engine)
    methods = repositories.methods_by_codes(db, payload.basket or [])
    accepted, notes = rules.assess_selected_methods(methods, payload.profile, repositories.conflicts(db))
    files = presets.build_preset_files(payload.profile, [method.code for method in accepted])
    prefix = {"unreal": "Default", "unity": "unity-", "godot": "godot-"}.get(payload.profile.engine)
    selected_files = [file for file in files if prefix and file["name"].startswith(prefix)]
    return {"files": selected_files, "native_verified": False,
            "notes": ["Это пример настроек для ручной проверки: применение в минимальном проекте указанной версии не проверено.", *notes]}
