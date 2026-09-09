"""Перечисления предметной области.

Хранятся в БД как строки, чтобы схема одинаково работала в SQLite и PostgreSQL.
"""
from __future__ import annotations

from enum import Enum


class Status(str, Enum):
    """Жизненный цикл записи базы знаний."""

    DRAFT = "draft"           # черновик
    REVIEWED = "reviewed"     # проверено
    PUBLISHED = "published"   # опубликовано

    @property
    def label(self) -> str:
        return {
            "draft": "черновик",
            "reviewed": "проверено",
            "published": "опубликовано",
        }[self.value]


class SolutionLevel(str, Enum):
    """Уровень решения."""

    ARCHITECTURE = "architecture"    # архитектура
    PRODUCTION = "production"        # производственный процесс
    ALGORITHM = "algorithm"          # алгоритм
    SETTING = "setting"              # настройка

    @property
    def label(self) -> str:
        return {
            "architecture": "архитектура",
            "production": "производственный процесс",
            "algorithm": "алгоритм",
            "setting": "настройка",
        }[self.value]


class DevStage(str, Enum):
    """Стадия разработки проекта."""

    CONCEPT = "concept"                  # концепт
    PREPRODUCTION = "preproduction"      # предпроизводство
    PROTOTYPE = "prototype"              # прототип
    PRODUCTION = "production"            # производство контента
    ALPHA = "alpha"
    BETA = "beta"
    RELEASE = "release"                  # релиз
    POST_RELEASE = "post_release"        # поддержка после релиза

    @property
    def label(self) -> str:
        return {
            "concept": "концепт",
            "preproduction": "предпроизводство",
            "prototype": "прототип",
            "production": "производство контента",
            "alpha": "альфа",
            "beta": "бета",
            "release": "релиз",
            "post_release": "поддержка после релиза",
        }[self.value]

    @property
    def order(self) -> int:
        """Порядковый номер стадии: чем больше, тем позже внедрять изменения дороже."""
        return {
            "concept": 0,
            "preproduction": 1,
            "prototype": 2,
            "production": 3,
            "alpha": 4,
            "beta": 5,
            "release": 6,
            "post_release": 7,
        }[self.value]


class LateCost(str, Enum):
    """Стоимость внедрения после рекомендованной стадии."""

    LOW = "low"          # низкая
    MEDIUM = "medium"    # средняя
    HIGH = "high"        # высокая
    CRITICAL = "critical"  # критическая

    @property
    def label(self) -> str:
        return {"low": "низкая", "medium": "средняя", "high": "высокая", "critical": "критическая"}[self.value]

    @property
    def weight(self) -> float:
        return {"low": 0.0, "medium": 0.35, "high": 0.7, "critical": 1.0}[self.value]


class CalcMode(str, Enum):
    """Способ расчёта."""

    REALTIME = "realtime"        # в реальном времени
    PRECOMPUTED = "precomputed"  # предварительный
    HYBRID = "hybrid"            # гибридный

    @property
    def label(self) -> str:
        return {"realtime": "real-time", "precomputed": "предварительный", "hybrid": "гибридный"}[self.value]


class EffectScope(str, Enum):
    """Где проявляется эффект метода.

    Оценка оборудования отвечает на вопрос о компьютере игрока, поэтому
    серверная экономия и ускорение разработки не могут уменьшать требования к
    нему: сервер без графики не облегчает рендер на клиенте, а быстрый пересчёт
    освещения на машине художника не делает игру быстрее. Пока область эффекта
    не была задана явно, влияние разработки и сервера складывалось в клиентскую
    нагрузку, и набор решений выглядел дешевле, чем он есть на самом деле.
    """

    CLIENT = "client"              # клиент реального времени
    SERVER = "server"              # серверная часть
    DEVELOPMENT = "development"    # процесс разработки и подготовка данных

    @property
    def label(self) -> str:
        return {
            "client": "клиент",
            "server": "сервер",
            "development": "разработка",
        }[self.value]

    @classmethod
    def of(cls, value: str | None) -> EffectScope | None:
        """Разобрать значение из базы. None — значение не распознано.

        Неизвестная область не приравнивается к клиентской: неизвестное
        происхождение эффекта нельзя молча превращать в экономию на компьютере
        игрока, поэтому вызывающая сторона обязана обработать None явно.
        """
        try:
            return cls(value)
        except ValueError:
            return None

    @property
    def affects_client(self) -> bool:
        """Меняет ли эффект требования к компьютеру игрока."""
        return self is EffectScope.CLIENT

    @property
    def hardware_note(self) -> str:
        """Пояснение, где проявляется эффект, отличный от клиентского."""
        return {
            "client": "",
            "server": "эффект относится к серверной части",
            "development": "эффект относится к процессу разработки",
        }[self.value]


class RelationType(str, Enum):
    """Тип связи общего метода с инструментом движка."""

    DIRECT = "direct"                # прямая реализация
    PARTIAL = "partial"              # частичный аналог
    ALTERNATIVE = "alternative"      # альтернативный подход
    COMPLEMENT = "complement"        # дополнение
    AUTOMATION = "automation"        # автоматизация
    DIAGNOSTIC = "diagnostic"        # диагностический инструмент
    LIMITED = "limited"              # ограниченное применение
    MISSING = "missing"              # отсутствие встроенного аналога

    @property
    def label(self) -> str:
        return {
            "direct": "прямая реализация",
            "partial": "частичный аналог",
            "alternative": "альтернативный подход",
            "complement": "дополнение",
            "automation": "автоматизация",
            "diagnostic": "диагностический инструмент",
            "limited": "ограниченное применение",
            "missing": "отсутствие встроенного аналога",
        }[self.value]


class ConflictType(str, Enum):
    """Тип связи между методами.

    План требует разделения: не все связи — полный запрет. Ошибка D12 —
    любой `conflict` удалял оба метода. Теперь:
    - HARD_CONFLICT: жёсткая несовместимость (оба исключаются из расчёта)
    - RISK: условный риск (оба остаются, добавляется предупреждение)
    - ALTERNATIVE: альтернативы (можно выбрать одно, оба не исключаются)
    - DEPENDENCY: обязательная зависимость (без B эффект A не учитывается)
    - COMPLEMENT: дополнение/синергия (вместе дают больше, но работают по отдельности)
    - OVERLAP: перекрывающиеся эффекты (частичная дублировка выигрыша)
    - UNKNOWN: непроверенное сочетание (отсутствие запрета ≠ доказанная совместимость)
    """

    HARD_CONFLICT = "hard_conflict"
    RISK = "risk"
    ALTERNATIVE = "alternative"
    DEPENDENCY = "dependency"
    COMPLEMENT = "complement"
    OVERLAP = "overlap"
    UNKNOWN = "unknown"

    @property
    def label(self) -> str:
        return {
            "hard_conflict": "жёсткая несовместимость",
            "risk": "условный риск",
            "alternative": "альтернатива",
            "dependency": "обязательная зависимость",
            "complement": "дополнение / синергия",
            "overlap": "перекрывающиеся эффекты",
            "unknown": "не проверено",
        }[self.value]


class MethodKind(str, Enum):
    IMPLEMENTATION = "implementation"  # вариант реализации функции
    OPTIMIZATION = "optimization"      # общий метод оптимизации

    @property
    def label(self) -> str:
        return {"implementation": "вариант реализации", "optimization": "метод оптимизации"}[self.value]


class GameFormat(str, Enum):
    FMT_2D = "2D"
    FMT_25D = "2.5D"
    FMT_3D = "3D"

    @property
    def label(self) -> str:
        return {"2D": "2D", "2.5D": "2.5D", "3D": "3D"}[self.value]


class WorldType(str, Enum):
    LINEAR = "linear"
    HUB = "hub"
    ARENA = "arena"
    OPEN_WORLD = "open_world"
    PROCEDURAL = "procedural"
    SANDBOX = "sandbox"

    @property
    def label(self) -> str:
        return {
            "linear": "линейные уровни",
            "hub": "хабы",
            "arena": "арена",
            "open_world": "открытый мир",
            "procedural": "процедурная генерация",
            "sandbox": "песочница",
        }[self.value]


class Scale(str, Enum):
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"
    VERY_LARGE = "very_large"
    UNKNOWN = "unknown"

    @property
    def label(self) -> str:
        return {
            "small": "небольшой",
            "medium": "средний",
            "large": "большой",
            "very_large": "очень большой",
            "unknown": "не указан",
        }[self.value]


class Resolution(str, Enum):
    """Целевое разрешение rendering."""

    R_720P = "720p"
    R_768P = "768p"
    R_900P = "900p"
    R_1080P = "1080p"
    R_1200P = "1200p"
    R_1440P = "1440p"
    R_1600P = "1600p"
    R_2160P = "2160p"
    R_4K = "4k"

    @property
    def label(self) -> str:
        return {
            "720p": "720p", "768p": "768p", "900p": "900p",
            "1080p": "1080p (Full HD)", "1200p": "1200p",
            "1440p": "1440p (2K)", "1600p": "1600p",
            "2160p": "2160p (4K)", "4k": "4K",
        }[self.value]


class Quality(str, Enum):
    """Целевой уровень графического качества."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    ULTRA = "ultra"

    @property
    def label(self) -> str:
        return {"low": "низкое", "medium": "среднее", "high": "высокое", "ultra": "ультра"}[self.value]


class RenderAPI(str, Enum):
    """Графический API/RHI, влияющий на стоимость CPU и совместимость рендера.

    Metal исключён из перечисления: область количественной оценки — Windows и
    Linux, для которых Metal не является нативным графическим API. Прежде код
    Metal доходил до расчёта и мог определять стоимость render thread для
    PC-конфигурации, которой он не соответствует.
    """

    AUTO = "auto"
    DX9 = "dx9"
    DX11 = "dx11"
    DX12 = "dx12"
    VULKAN = "vulkan"
    OPENGL = "opengl"

    @property
    def label(self) -> str:
        return {
            "auto": "не указан",
            "dx9": "DirectX 9",
            "dx11": "DirectX 11",
            "dx12": "DirectX 12",
            "vulkan": "Vulkan",
            "opengl": "OpenGL",
        }[self.value]


class StorageType(str, Enum):
    """Тип накопителя, на который рассчитывается потоковая загрузка."""

    AUTO = "auto"
    HDD = "hdd"
    SATA_SSD = "sata_ssd"
    NVME = "nvme"

    @property
    def label(self) -> str:
        return {
            "auto": "не указан",
            "hdd": "HDD",
            "sata_ssd": "SATA SSD",
            "nvme": "NVMe SSD",
        }[self.value]


class NetworkTopology(str, Enum):
    """Сетевая схема, задающая стоимость синхронизации и тикрейта."""

    AUTO = "auto"
    CLIENT_SERVER = "client_server"
    P2P = "p2p"
    DEDICATED = "dedicated"
    LOCKSTEP = "lockstep"

    @property
    def label(self) -> str:
        return {
            "auto": "не указана",
            "client_server": "клиент-сервер",
            "p2p": "peer-to-peer",
            "dedicated": "выделенный сервер",
            "lockstep": "детерминированный lockstep",
        }[self.value]


class UpscalingMethod(str, Enum):
    """Метод масштабирования изображения до целевого разрешения."""

    AUTO = "auto"
    NONE = "none"
    TAA = "taa"
    FSR = "fsr"
    DLSS = "dlss"
    XESS = "xess"

    @property
    def label(self) -> str:
        return {
            "auto": "не указан",
            "none": "без масштабирования",
            "taa": "TAAU / temporal",
            "fsr": "AMD FSR",
            "dlss": "NVIDIA DLSS",
            "xess": "Intel XeSS",
        }[self.value]


class MemoryModel(str, Enum):
    """Модель памяти платформы."""

    AUTO = "auto"
    DEDICATED = "dedicated"
    UNIFIED = "unified"
    MANAGED = "managed"

    @property
    def label(self) -> str:
        return {
            "auto": "не указана",
            "dedicated": "раздельная RAM/VRAM",
            "unified": "единая память",
            "managed": "управляемая куча / GC",
        }[self.value]


class EngineCode(str, Enum):
    """Код игрового движка, поддерживаемый базой знаний."""

    UNREAL = "unreal"
    UNITY = "unity"
    GODOT = "godot"
    CRYENGINE = "cryengine"
    SOURCE = "source"
    HEROENGINE = "heroengine"
    CUSTOM = "custom"

    @property
    def label(self) -> str:
        return {
            "unreal": "Unreal Engine",
            "unity": "Unity",
            "godot": "Godot",
            "cryengine": "CryEngine",
            "source": "Source / Source 2",
            "heroengine": "HeroEngine",
            "custom": "Собственный движок",
        }[self.value]


class Level3(str, Enum):
    """Качественный уровень: низкий / средний / высокий."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    UNKNOWN = "unknown"

    @property
    def label(self) -> str:
        return {"low": "низкий", "medium": "средний", "high": "высокий", "unknown": "не указан"}[self.value]

    @property
    def numeric(self) -> float:
        return {"low": 0.25, "medium": 0.55, "high": 0.9, "unknown": 0.55}[self.value]


class Platform(str, Enum):
    PC_WINDOWS = "pc_windows"
    PC_LINUX = "pc_linux"
    ANDROID = "android"
    IOS = "ios"
    SWITCH = "switch"
    PS5 = "ps5"
    XBOX_SERIES = "xbox_series"
    PS4 = "ps4"
    XBOX_ONE = "xbox_one"
    WEB = "web"

    @property
    def label(self) -> str:
        return {
            "pc_windows": "PC (Windows)",
            "pc_linux": "PC (Linux)",
            "android": "Android",
            "ios": "iOS",
            "switch": "Nintendo Switch",
            "ps5": "PlayStation 5",
            "xbox_series": "Xbox Series X|S",
            "ps4": "PlayStation 4",
            "xbox_one": "Xbox One",
            "web": "Web",
        }[self.value]


class Priority(str, Enum):
    """Приоритет пользователя при ранжировании."""

    QUALITY = "quality"
    PERFORMANCE = "performance"
    COST = "cost"
    BALANCED = "balanced"

    @property
    def label(self) -> str:
        return {
            "quality": "качество",
            "performance": "производительность",
            "cost": "стоимость разработки",
            "balanced": "сбалансированный",
        }[self.value]
