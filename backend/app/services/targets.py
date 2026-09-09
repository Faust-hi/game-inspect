"""Целевые платформы проекта: ОС, графический API, движок и версия.

Зачем отдельный модуль
----------------------
Профиль хранит одно поле `render_api` и список платформ. Раньше они почти не
взаимодействовали: сочетание «Linux + DirectX 12» доходило до расчёта и давало
численный результат, хотя нативного пути у такой цели нет, а «Metal» принимался
схемой как вариант для ПК. Совместимость подменялась молчаливым расчетом.

Здесь собирается явная проверка трёх вещей:

1. **ОС ↔ API.** DirectX — нативный графический API Windows; на Linux нативный
   путь — Vulkan/OpenGL. Перенос DirectX через слой совместимости (Proton/Wine)
   существует, но это *другая* цель с другим результатом: подменять её
   фиксированным коэффициентом или незаметной заменой API нельзя.
2. **auto разрешается отдельно по платформе.** Одно поле `auto` не может означать
   «DX12 для Windows и Vulkan для Linux» сразу: у двух целей разные нативные
   пути, поэтому значение выбирается для каждой цели отдельно.
3. **Движок ↔ API.** Набор API зависит от движка *и его версии*. Каталог
   заявляет лишь типичный набор; конкретная сборка может отличаться. Поэтому
   расхождение с объявленным набором выводится предупреждением и требованием
   проверить версию, а не выдаётся за измеренный факт.

Границы честности
-----------------
Нативность API для ОС — проверяемый факт, и несовместимая цель помечается
несовместимой. Поддержка конкретной версией движка — не проверяемый в MVP факт,
поэтому она не блокирует расчёт, а добавляет явную оговорку. Отсутствие записи
о движке означает «неизвестно», а не «поддерживается всё».
"""
from __future__ import annotations

from pydantic import BaseModel, Field

from ..schemas.catalog import ProjectProfile

#: Платформы, для которых обещается количественный прогноз.
PC_PLATFORMS: tuple[str, ...] = ("pc_windows", "pc_linux")

_OS_LABELS = {"pc_windows": "Windows", "pc_linux": "Linux"}

#: Графические API, нативные для ОС. DirectX вне Windows не является нативным.
OS_NATIVE_APIS: dict[str, frozenset[str]] = {
    "pc_windows": frozenset({"dx9", "dx11", "dx12", "vulkan", "opengl"}),
    "pc_linux": frozenset({"vulkan", "opengl"}),
}

#: Разрешение `auto` отдельно для каждой ОС: у целей разные нативные пути.
OS_DEFAULT_API: dict[str, str] = {"pc_windows": "dx12", "pc_linux": "vulkan"}

#: Порядок перечисления API в сообщениях: от современных к устаревшим.
_API_ORDER: tuple[str, ...] = ("dx12", "dx11", "dx9", "vulkan", "opengl")

API_LABELS: dict[str, str] = {
    "auto": "не указан",
    "dx9": "DirectX 9",
    "dx11": "DirectX 11",
    "dx12": "DirectX 12",
    "vulkan": "Vulkan",
    "opengl": "OpenGL",
}

#: Объявленные наборы API движка по ОС.
#: Пустое множество означает «каталог не заявляет набор» — проверка не
#: выполняется, выводится оговорка. Это не подтверждение поддержки.
ENGINE_APIS: dict[str, dict[str, frozenset[str]]] = {
    # Unreal: DirectX 11/12 и Vulkan на Windows; на Linux документация Epic
    # описывает Vulkan RHI как графический путь.
    "unreal": {
        "pc_windows": frozenset({"dx11", "dx12", "vulkan"}),
        "pc_linux": frozenset({"vulkan"}),
    },
    # Unity: набор графических API задаётся проектом (URP/HDRP, порядок API).
    "unity": {
        "pc_windows": frozenset({"dx11", "dx12", "vulkan", "opengl"}),
        "pc_linux": frozenset({"vulkan", "opengl"}),
    },
    # Godot 4: Vulkan и OpenGL (Compatibility), также присутствует D3D12.
    "godot": {
        "pc_windows": frozenset({"vulkan", "opengl", "dx12"}),
        "pc_linux": frozenset({"vulkan", "opengl"}),
    },
    # CryEngine: DirectX на Windows; состояние Linux-сборки зависит от версии,
    # поэтому набор для Linux не заявляется.
    "cryengine": {
        "pc_windows": frozenset({"dx11", "dx12", "vulkan"}),
        "pc_linux": frozenset(),
    },
    # Source: DX9/DX11 на Windows; Source 2 использует Vulkan (в т. ч. на Linux).
    "source": {
        "pc_windows": frozenset({"dx9", "dx11", "vulkan", "opengl"}),
        "pc_linux": frozenset({"vulkan", "opengl"}),
    },
    # Собственный движок: набор заведомо неизвестен.
    "custom": {"pc_windows": frozenset(), "pc_linux": frozenset()},
}

#: Оговорка о слое совместимости: не должна превращаться в коэффициент.
_TRANSLATION_NOTE = (
    "Перенос DirectX через слой совместимости (Proton/Wine) — отдельный сценарий "
    "с собственным результатом; в этой версии он не оценивается и фиксированным "
    "коэффициентом не заменяется."
)


def _api_names(codes) -> list[str]:
    """Названия API в порядке от современных к устаревшим."""
    ordered = [code for code in _API_ORDER if code in codes]
    ordered += sorted(code for code in codes if code not in _API_ORDER)
    return [API_LABELS.get(code, code) for code in ordered]


class PlatformTarget(BaseModel):
    """Одна цель сборки: ОС и разрешённый для неё графический API."""

    platform: str = Field(description="Код платформы: pc_windows или pc_linux")
    label: str = Field(default="", description="Название цели для интерфейса")
    render_api: str = Field(default="auto", description="Разрешённый графический API")
    api_label: str = Field(default="", description="Название API для интерфейса")
    #: Как получен API: задан пользователем или выбран по ОС.
    api_source: str = Field(default="auto", description="explicit или auto")
    compatible: bool = Field(default=True, description="Есть ли нативный путь для цели")
    engine_check: str = Field(
        default="unknown",
        description="confirmed, mismatch или unknown — результат сверки API с движком",
    )
    notes: list[str] = Field(default_factory=list)


def pc_platforms(profile: ProjectProfile) -> list[str]:
    """Целевые PC-платформы профиля в порядке объявления каталога."""
    selected = set(profile.platforms or [])
    return [code for code in PC_PLATFORMS if code in selected]


def resolve_targets(profile: ProjectProfile, *, engine_code: str | None = None) -> list[PlatformTarget]:
    """Развернуть профиль в список PC-целей со своим API и проверками.

    Возвращает только PC-цели: для остальных платформ количественный прогноз не
    обещается, и этим занимается аппаратный сервис.
    """
    code = (engine_code or profile.engine or "").strip().lower()
    explicit = profile.render_api if profile.render_api != "auto" else None
    targets: list[PlatformTarget] = []

    for platform in pc_platforms(profile):
        os_label = _OS_LABELS.get(platform, platform)
        native = OS_NATIVE_APIS.get(platform, frozenset())
        api = explicit or OS_DEFAULT_API.get(platform, "auto")
        notes: list[str] = []
        compatible = True

        if explicit and explicit not in native:
            compatible = False
            native_names = ", ".join(_api_names(native))
            notes.append(
                f"{API_LABELS.get(explicit, explicit)} не является нативным графическим "
                f"API для {os_label}: нативный путь — {native_names}. {_TRANSLATION_NOTE}"
            )

        declared = ENGINE_APIS.get(code, {}).get(platform, frozenset())
        if not declared:
            engine_check = "unknown"
            if code and code not in ENGINE_APIS:
                notes.append(
                    f"Для движка «{code}» каталог не заявляет набор графических API: "
                    "сверка API с движком не выполнена."
                )
            elif code:
                notes.append(
                    f"Для движка «{code}» набор графических API на {os_label} зависит от версии "
                    "и не заявлен каталогом: требуется проверка конкретной сборки."
                )
        elif api in declared:
            engine_check = "confirmed"
        else:
            engine_check = "mismatch"
            notes.append(
                f"Каталог не подтверждает {API_LABELS.get(api, api)} для движка «{code}» "
                f"на {os_label}: типичный набор — "
                + ", ".join(_api_names(declared))
                + ". Требуется проверка версии движка и настроек сборки."
            )

        targets.append(
            PlatformTarget(
                platform=platform,
                label=os_label,
                render_api=api,
                api_label=API_LABELS.get(api, api),
                api_source="explicit" if explicit else "auto",
                compatible=compatible,
                engine_check=engine_check,
                notes=notes,
            )
        )
    return targets


def incompatible_notes(targets: list[PlatformTarget]) -> list[str]:
    """Сообщения о целях без нативного пути, с указанием названия цели."""
    notes: list[str] = []
    for target in targets:
        if target.compatible:
            continue
        for note in target.notes:
            notes.append(f"Цель «{target.label}»: {note}")
    return notes


def any_compatible(targets: list[PlatformTarget]) -> bool:
    return any(target.compatible for target in targets)
