"""Импорт анкеты из файлов проекта движка.

Локальный инструмент-консультант не читает код игры и сцены — это честно
зафиксировано в ограничениях. Но файлы настроек проекта (движок, версия,
название, разрешение) разбираются напрямую: это те же данные, что пользователь
вводит руками, только без опечаток.

Принцип: заполняется только то, что извлечено надёжно. Всё сомнительное идёт
в `detected` (показать человеку) или `warnings`, но не в профиль.
Платформы не угадываются: ни один из форматов не хранит их однозначно.
"""
from __future__ import annotations

import configparser
import json
import re

_VERSION_RE = re.compile(r"(\d+\.\d+(?:\.\d+)?)")


def height_to_resolution(height: int) -> str | None:
    """Высота экрана в ближайшее поддерживаемое разрешение (вниз)."""
    if height <= 0:
        return None
    if height <= 800:
        return "720p"
    if height <= 1080:
        return "1080p"
    if height <= 1600:
        return "1440p"
    return "4k"


def _short_version(raw: str) -> str | None:
    match = _VERSION_RE.search(raw or "")
    return match.group(1) if match else None


def parse_uproject(raw: bytes) -> dict:
    """Разбор .uproject (JSON): движок и его версия, плагины — в заметки."""
    try:
        data = json.loads(raw.decode("utf-8-sig"))
    except (ValueError, UnicodeDecodeError):
        return {"warnings": ["Файл .uproject не является корректным JSON."]}
    if not isinstance(data, dict):
        return {"warnings": ["Файл .uproject не содержит объект проекта."]}
    filled: dict = {"engine": "unreal"}
    detected: list[str] = []
    warnings: list[str] = []
    suggested: list[dict] = []
    version = _short_version(str(data.get("EngineAssociation", "")))
    if version:
        filled["engine_version"] = version
    else:
        warnings.append("Версия движка в .uproject не указана (EngineAssociation пуст).")
    plugins = data.get("Plugins") or []
    names = sorted({str(p.get("Name", "")) for p in plugins if isinstance(p, dict) and p.get("Name")})
    for name in names:
        detected.append(f"Плагин {name}: проверьте, не требует ли он отдельного метода.")
        if "dlss" in name.lower():
            suggested.append({
                "method_code": "temporal_upscaling",
                "reason": "DLSS-плагин в проекте — зафиксируйте это решением temporal_upscaling.",
            })
    return {"filled": filled, "detected": detected, "warnings": warnings, "suggested": suggested}


def _unity_pairs(text: str) -> dict[str, str]:
    """Плоский разбор `ключ: значение` без зависимости от YAML-парсера.

    ProjectSettings.asset — Unity-YAML, но нужные поля лежат на верхнем уровне
    секций в виде простых строк. Строгий парсер здесь избыточен: неизвестные
    строки игнорируются, а не ломают импорт.
    """
    out: dict[str, str] = {}
    for line in text.splitlines():
        if ":" not in line or line.startswith((" ", "\t", "#", "-", "%", "!")):
            continue
        key, _, value = line.partition(":")
        key, value = key.strip(), value.strip()
        if key and value and key not in out:
            out[key] = value
    return out


def parse_unity_settings(raw: bytes, filename: str) -> dict:
    """ProjectSettings.asset и ProjectVersion.txt: название, разрешение, версия."""
    text = raw.decode("utf-8-sig", errors="replace")
    filled: dict = {}
    detected: list[str] = []
    warnings: list[str] = []
    name = filename.lower()
    if "projectversion" in name:
        match = re.search(r"m_EditorVersion\s*:\s*([^\s]+)", text)
        if match:
            filled["engine"] = "unity"
            filled["engine_version"] = match.group(1).strip()
        else:
            warnings.append("В ProjectVersion.txt не найдена строка m_EditorVersion.")
        return {"filled": filled, "detected": detected, "warnings": warnings}
    pairs = _unity_pairs(text)
    if "productName" in pairs:
        filled["name"] = pairs["productName"][:200]
    try:
        width = int(pairs.get("defaultScreenWidth", "0"))
        height = int(pairs.get("defaultScreenHeight", "0"))
    except ValueError:
        width = height = 0
    if height > 0:
        resolution = height_to_resolution(height)
        if resolution:
            filled["target_resolution"] = resolution
        detected.append(f"Стартовое разрешение {width}x{height} → {resolution or 'не сопоставлено'}.")
    else:
        warnings.append("Стартовое разрешение в настройках не найдено.")
    if pairs.get("virtualRealitySupported") == "1":
        detected.append("Включён VR: учтите удвоенную стоимость кадра и лимиты платформ.")
    backend = pairs.get("scriptingBackend", "")
    if backend == "1":
        detected.append("Скриптовый бэкенд IL2CPP: ближе к нативной производительности.")
    return {"filled": filled, "detected": detected, "warnings": warnings}


def parse_urp_asset(raw: bytes) -> dict:
    """URP-ассет: масштаб рендера меньше 1 означает уже используемый апскейл."""
    text = raw.decode("utf-8-sig", errors="replace")
    if "UniversalRenderPipelineAsset" not in text:
        return {"filled": {}, "detected": [], "warnings": ["Файл не похож на URP-ассет."]}
    detected: list[str] = []
    suggested: list[dict] = []
    match = re.search(r"m_RenderScale\s*:\s*([0-9.]+)", text)
    if match:
        try:
            scale = float(match.group(1))
        except ValueError:
            scale = 1.0
        if scale < 1.0:
            detected.append(
                f"Масштаб рендера {scale}: в проекте уже используется апскейл."
            )
            suggested.append({
                "method_code": "dynamic_resolution_scaling",
                "reason": "Масштаб рендера ниже 1 — зафиксируйте это решением dynamic_resolution_scaling.",
            })
        else:
            detected.append("Масштаб рендера 1.0: рендер в нативном разрешении.")
    else:
        detected.append("Масштаб рендера не найден: принято нативное разрешение.")
    return {"filled": {}, "detected": detected, "warnings": [], "suggested": suggested}


def parse_godot_project(raw: bytes) -> dict:
    """project.godot (INI): название, версия и метод рендеринга, разрешение."""
    filled: dict = {"engine": "godot"}
    detected: list[str] = []
    warnings: list[str] = []
    suggested: list[dict] = []
    parser = configparser.ConfigParser(strict=False)
    try:
        parser.read_string(raw.decode("utf-8-sig", errors="replace"))
    except configparser.Error:
        return {"filled": filled, "detected": detected,
                "warnings": ["Файл project.godot не разобран как INI."]}
    name = parser.get("application", "config/name", fallback="").strip().strip('"')
    if name:
        filled["name"] = name[:200]
    features = parser.get("application", "config/features", fallback="")
    version = _short_version(features)
    if version:
        filled["engine_version"] = version
    else:
        warnings.append("Версия Godot в config/features не найдена.")
    low_features = features.lower()
    if "forward plus" in low_features:
        detected.append("Метод рендеринга Forward Plus: самый требовательный конвейер Godot.")
    elif "mobile" in low_features:
        detected.append("Метод рендеринга Mobile: урезанные эффекты ради производительности.")
    elif "gl_compatibility" in low_features:
        detected.append("Метод рендеринга GL Compatibility: без части современных эффектов.")
    try:
        width = parser.getint("display", "window/size/viewport_width", fallback=0)
        height = parser.getint("display", "window/size/viewport_height", fallback=0)
    except ValueError:
        width = height = 0
    if height > 0:
        resolution = height_to_resolution(height)
        if resolution:
            filled["target_resolution"] = resolution
        detected.append(f"Вьюпорт {width}x{height} → {resolution or 'не сопоставлено'}.")
    if parser.has_option("rendering", "textures/vram_compression/import_etc2_astc"):
        detected.append("Включено сжатие текстур для мобильных (ETC2/ASTC).")
    return {"filled": filled, "detected": detected, "warnings": warnings, "suggested": suggested}


#: Известные ключи рендера UE: значение целиком идёт в заметки, без трактовки.
_UNREAL_RENDER_KEYS = (
    "r.DynamicGlobalIlluminationMethod",
    "r.ReflectionMethod",
    "r.Shadow.Virtual.Enable",
    "r.GenerateMeshDistanceFields",
    "r.AllowStaticLighting",
)


def parse_unreal_config(raw: bytes) -> dict:
    """DefaultEngine.ini и соседние: известные ключи рендера — в заметки."""
    text = raw.decode("utf-8-sig", errors="replace")
    detected: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith(("[", ";", "#", "+", "-", "!", ".")):
            continue
        for key in _UNREAL_RENDER_KEYS:
            if stripped.startswith(key):
                detected.append(f"Настройка движка: {stripped[:120]}")
                break
    if not detected:
        return {"filled": {}, "detected": [],
                "warnings": ["Знакомых ключей рендера в конфиге нет — заполните анкету вручную."]}
    return {"filled": {}, "detected": detected[:20], "warnings": []}


def import_project(files: list[tuple[str, bytes]]) -> dict:
    """Собрать частичную анкету из загруженных файлов.

    Первый успешно извлечённый источник побеждает для каждого поля:
    файлы не перезаписывают друг друга, противоречия видны в warnings.
    """
    filled: dict = {}
    detected: list[str] = []
    warnings: list[str] = []
    suggested: list[dict] = []
    seen_suggested: set[str] = set()
    handled = False
    for filename, raw in files:
        low = (filename or "").lower()
        if low.endswith(".uproject"):
            part = parse_uproject(raw)
        elif "projectversion" in low and low.endswith(".txt"):
            part = parse_unity_settings(raw, filename)
        elif low.endswith(".asset"):
            if b"UniversalRenderPipelineAsset" in raw[:4000] or "universalrenderpipeline" in low:
                part = parse_urp_asset(raw)
            else:
                part = parse_unity_settings(raw, filename)
        elif low == "project.godot":
            part = parse_godot_project(raw)
        elif low.endswith(".ini"):
            part = parse_unreal_config(raw)
        else:
            warnings.append(f"Файл {filename or 'без имени'}: формат не распознан, пропущен.")
            continue
        handled = True
        for key, value in part.get("filled", {}).items():
            if key not in filled:
                filled[key] = value
            elif filled[key] != value:
                warnings.append(
                    f"Поле {key}: {filled[key]!r} против {value!r} — оставлено первое."
                )
        detected.extend(part.get("detected", []))
        warnings.extend(part.get("warnings", []))
        for item in part.get("suggested", []):
            if item["method_code"] not in seen_suggested:
                seen_suggested.add(item["method_code"])
                suggested.append(item)
    if not handled:
        warnings.append("Ни один файл не распознан: анкета осталась по умолчанию.")
    return {"filled": filled, "detected": detected, "warnings": warnings, "suggested": suggested}
