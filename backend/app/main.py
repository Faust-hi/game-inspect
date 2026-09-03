"""Точка входа FastAPI-приложения.

При старте проверяется конфигурация, создаются таблицы и, если база пуста и
заполнение разрешено, выполняется первичное наполнение демонстрационными
данными. Собранный frontend отдаётся как статические файлы, поэтому в
эксплуатации достаточно одного процесса.
"""
from __future__ import annotations

import logging
import os
import time
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException

from .api import admin, catalog, recommend
from .config import FRONTEND_DIST, settings
from .database import SessionLocal, engine
from .logging_setup import configure_logging, log_event
from .models.entities import Base
from .seed import seeder
from .staticfiles_safe import safe_static_path

configure_logging()
logger = logging.getLogger("gamedev_dss")
access_logger = logging.getLogger("gamedev_dss.access")

#: Признак вынужденного запуска с небезопасной конфигурацией.
ALLOW_INSECURE_STARTUP = os.getenv("ALLOW_INSECURE_STARTUP", "").strip().lower() in {"1", "true", "yes", "on"}


def _check_configuration() -> None:
    """Проверяет конфигурацию. В эксплуатации небезопасный запуск блокируется."""
    problems = settings.production_problems()
    if not problems:
        return
    for problem in problems:
        logger.warning("Замечание конфигурации: %s", problem)
    if settings.is_production and not ALLOW_INSECURE_STARTUP:
        raise RuntimeError(
            "Запуск в эксплуатационном режиме с небезопасной конфигурацией отклонён. "
            "Устраните замечания выше либо задайте ALLOW_INSECURE_STARTUP=true "
            "для вынужденного запуска (не рекомендуется)."
        )


def _migration_state() -> str:
    """Состояние схемы относительно миграций Alembic.

    Возвращает «применены», «не применены» или «нет миграций». База, созданная
    `create_all` до появления миграций, содержит таблицы, но не содержит отметки
    ревизии: такая база не должна молча считаться мигрированной, иначе следующая
    миграция попытается создать уже существующие таблицы.
    """
    from sqlalchemy import inspect, text

    inspector = inspect(engine)
    tables = set(inspector.get_table_names())
    if not tables or "alembic_version" not in tables:
        return "не применены" if tables else "нет таблиц"
    try:
        with engine.connect() as connection:
            revision = connection.execute(text("SELECT version_num FROM alembic_version")).scalar()
    except Exception:  # noqa: BLE001 — такая база тоже считается немигрированной
        return "не применены"
    return f"применены (ревизия {revision})" if revision else "не применены"


def _bootstrap() -> None:
    _check_configuration()

    state = _migration_state()
    if settings.is_production:
        # В эксплуатации схемой управляют миграции Alembic (каталог backend/alembic).
        # create_all запускается и здесь, но он только создаёт отсутствующие
        # таблицы и не заменяет миграции: для существующей базы, созданной до
        # появления миграций, требуется `alembic stamp head`.
        logger.info("Эксплуатационный режим. Миграции: %s", state)
        if state == "не применены":
            logger.warning(
                "База содержит таблицы, но не имеет отметки ревизии Alembic. "
                "Выполните «alembic stamp head», если схема уже соответствует "
                "текущей ревизии, иначе следующая миграция не будет применена."
            )
    else:
        logger.info("Состояние миграций: %s", state)

    Base.metadata.create_all(bind=engine)
    if not settings.AUTO_SEED:
        return
    db = SessionLocal()
    try:
        if seeder.is_empty(db):
            logger.info("База пуста — выполняется первичное заполнение")
            result = seeder.seed_all(db, validate=True)
            log_event(logger, logging.INFO, "Первичное заполнение завершено", **result)
        else:
            logger.info("База уже содержит данные, заполнение пропущено")
    except Exception:  # noqa: BLE001 — сбой заполнения не должен ронять сервис
        logger.exception("Ошибка первичного заполнения базы")
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    _bootstrap()
    yield
    logger.info("Остановка приложения")


def _register_exception_handlers(app: FastAPI) -> None:
    """Единый формат ошибок. Подробности исключений клиенту не передаются."""

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        if exc.status_code >= 500:
            logger.error("Ошибка %s при обработке %s", exc.status_code, request.url.path)
        response = JSONResponse(
            status_code=exc.status_code,
            content={"error": exc.detail, "request_id": request.headers.get("x-request-id")},
        )
        for header, value in (exc.headers or {}).items():
            response.headers[header] = value
        return response

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        errors = [
            {"field": ".".join(str(p) for p in item.get("loc", ())), "message": item.get("msg", "")}
            for item in exc.errors()
        ]
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": "Некорректные данные запроса",
                "details": errors,
                "request_id": request.headers.get("x-request-id"),
            },
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        """Необработанное исключение: подробности в журнал, клиенту код для связи.

        Текст исключения в ответ не попадает никогда — даже вне промышленной
        среды. Раньше подробности добавлялись, когда `ENVIRONMENT` не был равен
        `production`; одной забытой переменной окружения достаточно, чтобы
        клиент увидел трассировку, пути к файлам и содержимое запроса.
        Разработчик тот же текст найдёт в журнале по `error_id`.
        """
        error_id = uuid.uuid4().hex[:12]
        logger.exception("Необработанное исключение %s при обработке %s", error_id, request.url.path)
        return JSONResponse(
            status_code=500,
            content={
                "error": "Внутренняя ошибка сервиса",
                "error_id": error_id,
                "request_id": request.headers.get("x-request-id"),
            },
        )


def _register_middleware(app: FastAPI) -> None:
    """Идентификатор запроса, защитные заголовки и журнал обращений."""

    @app.middleware("http")
    async def request_context(request: Request, call_next):
        request_id = request.headers.get("x-request-id") or uuid.uuid4().hex[:12]
        started = time.perf_counter()
        try:
            response = await call_next(request)
        except Exception:  # noqa: BLE001 — ответ сформирует обработчик исключений
            duration_ms = (time.perf_counter() - started) * 1000
            log_event(
                access_logger,
                logging.ERROR,
                "request",
                method=request.method,
                path=request.url.path,
                status=500,
                duration_ms=round(duration_ms, 1),
                request_id=request_id,
            )
            raise
        duration_ms = (time.perf_counter() - started) * 1000

        response.headers["X-Request-ID"] = request_id
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "no-referrer")
        response.headers.setdefault("Cross-Origin-Opener-Policy", "same-origin")
        if request.url.path.startswith(settings.API_PREFIX):
            response.headers.setdefault("Cache-Control", "no-store")
        if settings.SECURITY_HSTS_ENABLED:
            response.headers.setdefault("Strict-Transport-Security", "max-age=31536000; includeSubDomains")

        log_event(
            access_logger,
            logging.INFO,
            "request",
            method=request.method,
            path=request.url.path,
            status=response.status_code,
            duration_ms=round(duration_ms, 1),
            request_id=request_id,
        )
        return response


def _register_health(app: FastAPI) -> None:
    """Проверки состояния: «жив ли процесс» и «готов ли обслуживать»."""

    def _ping() -> bool:
        from sqlalchemy import text

        db = SessionLocal()
        try:
            db.execute(text("SELECT 1"))
            return True
        except Exception:  # noqa: BLE001 — проверка сообщает, а не падает
            logger.exception("Проверка базы данных не прошла")
            return False
        finally:
            db.close()

    @app.get("/api/health", tags=["Служебное"], summary="Сводное состояние сервиса")
    def health():
        if not _ping():
            return JSONResponse(
                status_code=503,
                content={"status": "unavailable", "version": settings.APP_VERSION, "database": "error"},
            )
        db = SessionLocal()
        try:
            filled = not seeder.is_empty(db)
        finally:
            db.close()
        return {
            "status": "ok" if filled else "degraded",
            "version": settings.APP_VERSION,
            "environment": settings.ENVIRONMENT,
            "database": "ready" if filled else "empty",
        }

    @app.get("/api/health/live", tags=["Служебное"], summary="Процесс запущен")
    def health_live():
        """Не обращается к базе: ответ означает только то, что процесс жив."""
        return {"status": "alive", "version": settings.APP_VERSION}

    @app.get("/api/health/ready", tags=["Служебное"], summary="Готовность обслуживать запросы")
    def health_ready():
        if not _ping():
            return JSONResponse(status_code=503, content={"status": "not_ready", "database": "error"})
        db = SessionLocal()
        try:
            filled = not seeder.is_empty(db)
        finally:
            db.close()
        if not filled:
            return JSONResponse(status_code=503, content={"status": "not_ready", "database": "empty"})
        return {"status": "ready", "database": "ready"}


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_TITLE,
        version=settings.APP_VERSION,
        description=(
            "Информационная система поддержки принятия решений по оптимизации "
            "на этапе разработки игры."
        ),
        lifespan=lifespan,
        docs_url=None if settings.is_production else "/docs",
        redoc_url=None if settings.is_production else "/redoc",
        openapi_url=None if settings.is_production else "/openapi.json",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    _register_middleware(app)
    _register_exception_handlers(app)

    prefix = settings.API_PREFIX
    app.include_router(catalog.router, prefix=prefix)
    app.include_router(catalog.enums_router, prefix=prefix)
    app.include_router(recommend.router, prefix=prefix)
    app.include_router(admin.router, prefix=prefix)
    app.include_router(admin.projects_router, prefix=prefix)
    _register_health(app)

    if not settings.is_production:
        # Документация доступна по обоим адресам: /docs (адрес самого FastAPI)
        # и /api/docs (адрес, указанный в README и start.bat).
        @app.get("/api/docs", include_in_schema=False)
        def api_docs_redirect():
            return RedirectResponse(url="/docs", status_code=307)

        @app.get("/api/redoc", include_in_schema=False)
        def api_redoc_redirect():
            return RedirectResponse(url="/redoc", status_code=307)

    # Статическая раздача собранного frontend (если сборка выполнена).
    # Путь из URL никогда не склеивается с каталогом сборки напрямую: он
    # проходит через safe_static_path, которая отвергает выход за пределы
    # каталога, абсолютные пути и закодированные сегменты «..».
    if FRONTEND_DIST.exists():
        assets = FRONTEND_DIST / "assets"
        if assets.exists():
            app.mount("/assets", StaticFiles(directory=str(assets)), name="assets")

        spa_index = FRONTEND_DIST / "index.html"

        def _spa_response(full_path: str):
            candidate = safe_static_path(FRONTEND_DIST, full_path)
            return FileResponse(candidate if candidate is not None else spa_index)

        @app.get("/", include_in_schema=False)
        def index():
            return FileResponse(spa_index)

        @app.get("/{full_path:path}", include_in_schema=False)
        def spa(full_path: str):
            return _spa_response(full_path)
    else:

        @app.get("/", tags=["Служебное"])
        def root():
            return JSONResponse(
                {
                    "message": "Backend запущен. Frontend не собран: выполните сборку в каталоге frontend.",
                    "health": "/api/health",
                }
            )

    return app


app = create_app()
