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
    CONFLICT = "conflict"      # конфликт
    DEPENDENCY = "dependency"  # зависимость
    SYNERGY = "synergy"        # усиление

    @property
    def label(self) -> str:
        return {"conflict": "конфликт", "dependency": "зависимость", "synergy": "усиление"}[self.value]


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

    @property
    def label(self) -> str:
        return {
            "small": "небольшой",
            "medium": "средний",
            "large": "большой",
            "very_large": "очень большой",
        }[self.value]


class Level3(str, Enum):
    """Качественный уровень: низкий / средний / высокий."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

    @property
    def label(self) -> str:
        return {"low": "низкий", "medium": "средний", "high": "высокий"}[self.value]

    @property
    def numeric(self) -> float:
        return {"low": 0.25, "medium": 0.55, "high": 0.9}[self.value]


class Platform(str, Enum):
    PC_WINDOWS = "pc_windows"
    PC_LINUX = "pc_linux"
    MACOS = "macos"
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
            "macos": "macOS",
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
