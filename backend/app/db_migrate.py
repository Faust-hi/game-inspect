"""Штатные миграции схемы: резервная копия и Alembic как единственный путь.

`Base.metadata.create_all` не добавляет колонки в существующие таблицы,
поэтому обновление старой базы через него молча оставляет схему устаревшей
(D37). Здесь схема создаётся и обновляется только миграциями; перед любым
изменением существующего файла делается проверяемая резервная копия.

Для базы без таблицы версий, но с таблицами (создана до миграций), слепой
`stamp head` запрещён: сначала сверяется структура с поддерживаемой схемой —
маркером служат колонки, добавленные миграциями. Штампуется newest-присутствующая
точка (начальная, `application_steps` либо `head` при полном соответствии),
затем выполняется обычный `upgrade head`. Неизвестная структура — отказ
с явной ошибкой, а не догадка.
"""
from __future__ import annotations

import datetime as dt
import logging
import sqlite3
from pathlib import Path
from urllib.parse import urlparse

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import make_url

from .config import BACKEND_DIR, get_settings

logger = logging.getLogger("gamedev_dss.migrate")

#: Начальная ревизия цепочки.
INITIAL_REVISION = "cdf89f70b108"

#: Ревизия, схема которой уже содержит `methods.application_steps`.
#: База с этой колонкой, но без `effect_scope`, штампуется сюда.
APPLICATION_STEPS_REVISION = "f225calib01"

#: Голова цепочки. Ставится только после сверки: либо база создана
#: миграциями, либо её структура уже соответствует голове (см. ниже).
#: Значение обязано совпадать с головой Alembic: устаревший штамп заставил бы
#: применить уже существующую колонку поверх той же схемы.
HEAD_REVISION = "b2indep01"

#: Колонки, добавленные миграциями, в порядке цепочки:
#: `(таблица, колонка, ревизия, добавившая колонку)`.
#: Отсутствие такой колонки — не чужая структура, а признак более старой
#: схемы. Перечень общий для всех таблиц: раньше учитывались только колонки
#: `methods`, и новая колонка в другой таблице делала унаследованную базу
#: «неизвестной».
LEGACY_MARKER_CHAIN: tuple[tuple[str, str, str], ...] = (
    ("methods", "application_steps", APPLICATION_STEPS_REVISION),
    ("methods", "effect_scope", "9547c3d766db"),
    ("engine_tools", "min_version", "7a1toolvers"),
    ("methods", "engine_tool_independent", HEAD_REVISION),
)

#: Те же маркеры словарём для сверки структуры.
LEGACY_MARKER_COLUMNS: dict[tuple[str, str], str] = {
    (table, column): revision for table, column, revision in LEGACY_MARKER_CHAIN
}

#: Таблицы исходной схемы. Их наличие отличает базу, созданную приложением до
#: миграций, от чужого файла: штамповать чужую структуру запрещено.
EXPECTED_INITIAL_TABLES = frozenset({
    "game_functions", "methods", "engines", "engine_tools",
    "method_engine_links", "conflicts",
    "hardware_cpu", "hardware_gpu",
})

#: Состояние последнего запуска миграций для health-check. Процесс отвечает
#: даже при неуспешном обновлении, но готовым себя не объявляет.
state: dict[str, object] = {"schema_ok": True, "schema_error": None, "backup": None}


class UnsupportedDatabaseError(RuntimeError):
    """URL СУБД вне поддерживаемого списка (только SQLite)."""


def assert_supported_database(database_url: str) -> None:
    """Только SQLite. Остальное — явная ошибка вместо полурабочего запуска."""
    scheme = urlparse(database_url).scheme
    if scheme != "sqlite":
        raise UnsupportedDatabaseError(
            f"Поддерживается только SQLite, получен URL со схемой {scheme!r}. "
            "PostgreSQL не поддерживается: уберите DATABASE_URL или укажите "
            "sqlite:///путь/к/файлу.db."
        )


def sqlite_path_of(database_url: str) -> Path | None:
    """Файл SQLite из URL либо None для памяти/не-SQLite."""
    parsed = make_url(database_url)
    if parsed.drivername != "sqlite":
        return None
    path = parsed.database or ""
    if path in ("", ":memory:"):
        return None
    candidate = Path(path)
    if not candidate.is_absolute():
        candidate = Path.cwd() / candidate
    return candidate


def backup_sqlite(path: Path) -> Path:
    """Копия файла базы рядом с оригиналом. Возвращает путь копии.

    Имя содержит метку времени, чтобы последовательные запуски не затирали
    друг друга. Проверяемость: копия обязана существовать и быть непустой.
    """
    stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    target = path.with_name(f"{path.stem}.bak-{stamp}{path.suffix or '.db'}")
    from contextlib import closing
    with closing(sqlite3.connect(path.resolve().as_uri() + '?mode=ro', uri=True)) as source:
        with closing(sqlite3.connect(target)) as copy:
            source.backup(copy)
            if copy.execute('PRAGMA integrity_check').fetchone()[0] != 'ok':
                raise RuntimeError(f"Резервная копия не прошла проверку целостности: {target}")
    return target


def _table_names(database_url: str) -> set[str]:
    engine = create_engine(database_url, future=True)
    try:
        with engine.connect() as connection:
            return set(inspect(connection).get_table_names())
    finally:
        engine.dispose()


def _table_columns(database_url: str, table: str) -> set[str]:
    """Имена колонок указанной таблицы для определения достигнутой ревизии."""
    engine = create_engine(database_url, future=True)
    try:
        with engine.connect() as connection:
            return {
                row[1] for row in
                connection.execute(text(f"PRAGMA table_info({table})")).all()
            }
    finally:
        engine.dispose()


def _legacy_stamp_revision(database_url: str, tables: set[str]) -> str | None:
    """Ревизия для штампа унаследованной базы без таблицы версий.

    Возвращает None для чужой структуры (штамп запрещён). Маркером служат
    колонки, добавленные миграциями: штампуется newest-присутствующая точка,
    а остаток применяется обычным `upgrade head`. Штамп на `head` ставится
    только когда структура голове уже соответствует — это сверка, а не
    слепой штамп.
    """
    from .database import Base
    from .models import entities  # registers every supported table

    _LEGACY_REMOVED_TABLES = frozenset({"game_examples", "projects"})
    expected_tables = set(Base.metadata.tables) | _LEGACY_REMOVED_TABLES
    if not tables.issubset(expected_tables):
        return None
    # Колонки-маркеры, которых в унаследованной базе нет. Они исключаются из
    # сверки: их отсутствие — признак старой ревизии, а не чужой структуры.
    present_columns = {
        table: _table_columns(database_url, table) for table in {pair[0] for pair in LEGACY_MARKER_COLUMNS}
    }
    missing = {
        (table, column)
        for (table, column) in LEGACY_MARKER_COLUMNS
        if column not in present_columns.get(table, set())
    }
    # A familiar table name or marker column alone cannot establish provenance.
    engine = create_engine(database_url)
    try:
        inspector = inspect(engine)
        for name, table in Base.metadata.tables.items():
            actual = {column['name']: column for column in inspector.get_columns(name)}
            skipped = {column for (tbl, column) in missing if tbl == name}
            expected = {column.name: column for column in table.columns
                        if column.name not in skipped}
            if actual.keys() != expected.keys():
                return None
            for key, column in expected.items():
                observed = actual[key]
                if str(observed['type']).upper() != str(column.type.compile(dialect=engine.dialect)).upper():
                    return None
                if observed['nullable'] != column.nullable:
                    return None
            if set(inspector.get_pk_constraint(name)['constrained_columns']) != {column.name for column in table.primary_key}:
                return None
            foreign_keys = {(tuple(key['constrained_columns']), key['referred_table'], tuple(key['referred_columns']))
                            for key in inspector.get_foreign_keys(name)}
            expected_keys = {(tuple(element.parent.name for element in key.elements),
                              key.referred_table.name, tuple(element.column.name for element in key.elements))
                             for key in table.foreign_key_constraints}
            if foreign_keys != expected_keys:
                return None
    finally:
        engine.dispose()
    # Штампуется ревизия самого свежего присутствующего маркера: остаток
    # цепочки от неё применит недостающие колонки обычным upgrade head.
    # Раньше различались только три состояния (голова / application_steps /
    # начальная): при четвёртой миграционной колонке база предыдущей ревизии
    # штамповалась бы слишком рано, и upgrade падал бы на повторном
    # добавлении уже существующей колонки.
    stamp = INITIAL_REVISION
    for table, column, revision in LEGACY_MARKER_CHAIN:
        if column in present_columns.get(table, set()):
            stamp = revision
    return stamp


def _current_revisions(database_url: str) -> set[str] | None:
    """Ревизии из alembic_version либо None, если таблицы версий нет."""
    engine = create_engine(database_url, future=True)
    try:
        with engine.connect() as connection:
            names = set(inspect(connection).get_table_names())
            if "alembic_version" not in names:
                return None
            rows = connection.execute(text("SELECT version_num FROM alembic_version")).all()
            return {row[0] for row in rows}
    finally:
        engine.dispose()


def _alembic_config(database_url: str):
    """Конфиг для программного запуска миграций без перенастройки логов.

    Конструируется без alembic.ini намеренно: env.py вызывает fileConfig при
    наличии имени файла, а fileConfig снимает чужие хендлеры с корневого
    логгера (в тестах это убивало захват журнала pytest). CLI-путь через
    alembic.ini не меняется.
    """
    from alembic.config import Config

    cfg = Config()
    cfg.set_main_option("script_location", str(BACKEND_DIR / "alembic"))
    # env.py переопределяет URL из настроек приложения; дублируем и здесь,
    # чтобы в логах было видно единый источник.
    cfg.set_main_option("sqlalchemy.url", database_url.replace("%", "%%"))
    return cfg


def ensure_schema() -> dict[str, object]:
    """Привести схему к `head`: бэкап существующего файла, затем миграции.

    Возвращает отчёт для журнала и health-check. При неуспешном обновлении
    исключение не пробрасывается наружу молча: состояние фиксируется в
    :data:`state`, и приложение стартует неготовым, а не «как готовое».
    """
    from alembic import command

    # Настройки читаются свежими на каждый вызов: в тестах DATABASE_URL
    # переключается через reload_settings, а импортированный ранее объект
    # настроек остался бы привязан к прежнему URL.
    database_url = get_settings().DATABASE_URL
    report: dict[str, object] = {
        "database_url_scheme": urlparse(database_url).scheme,
        "backup": None, "stamped": None, "migrated": False, "error": None,
    }
    try:
        assert_supported_database(database_url)
        path = sqlite_path_of(database_url)
        # Факт существования фиксируется до первого подключения: сам коннект
        # к SQLite создаёт пустой файл, и поздняя проверка exists() приняла бы
        # только что созданный файл за унаследованную базу без версии.
        existed = path is not None and path.exists()
        if existed and path is not None:
            backup = backup_sqlite(path)
            report["backup"] = str(backup)
            state["backup"] = str(backup)
            logger.info("Резервная копия базы: %s", backup)
        else:
            logger.info("Файла базы нет — будет создана миграциями")

        revisions = _current_revisions(database_url)
        if revisions is None and existed:
            tables = _table_names(database_url)
            stamp = _legacy_stamp_revision(database_url, tables)
            if stamp is None:
                unknown = sorted(tables - EXPECTED_INITIAL_TABLES - {"alembic_version"})
                raise RuntimeError(
                    "База без таблицы версий и с неизвестной структурой: "
                    f"таблицы {sorted(tables)} (неожиданные: {unknown}). "
                    "Штамп запрещён — восстановите структуру из резервной копии."
                )
            logger.info(
                "База без таблицы версий, структура соответствует ревизии %s — "
                "штамп перед upgrade head",
                stamp,
            )
            command.stamp(_alembic_config(database_url), stamp)
            report["stamped"] = stamp
        command.upgrade(_alembic_config(database_url), "head")
        report["migrated"] = True
        state.update(schema_ok=True, schema_error=None)
        logger.info("Миграции применены: %s", report)
    except Exception as exc:  # noqa: BLE001 — отказ фиксируется, а не падает в UI
        report["error"] = str(exc)
        state.update(schema_ok=False, schema_error=str(exc))
        logger.exception("Миграции не применены, приложение не готово")
    return report
