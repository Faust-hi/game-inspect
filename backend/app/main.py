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
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException

from .api import admin, catalog, recommend
from .config import FRONTEND_DIST, settings
from .database import SessionLocal, engine
from .logging_setup import configure_logging, log_event
from .models.entities import Base
from .seed import seeder

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


def _bootstrap() -> None:
    _check_configuration()

    if settings.is_production:
        # В эксплуатации схемой управляют миграции Alembic; create_all страхует
        # только свежие развёртывания и не затрагивает существующие таблицы.
        logger.info("Эксплуатационный режим: схемой управляют миграции Alembic")

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
        """Необработанное исключение: подробности в журнал, клиенту код для связи."""
        error_id = uuid.uuid4().hex[:12]
        logger.exception("Необработанное исключение %s при обработке %s", error_id, request.url.path)
        content = {
            "error": "Внутренняя ошибка сервиса",
            "error_id": error_id,
            "request_id": request.headers.get("x-request-id"),
        }
        if not settings.is_production:
            content["detail"] = f"{type(exc).__name__}: {exc}"
        return JSONResponse(status_code=500, content=content)


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

    # Статическая раздача собранного frontend (если сборка выполнена).
    if FRONTEND_DIST.exists():
        assets = FRONTEND_DIST / "assets"
        if assets.exists():
            app.mount("/assets", StaticFiles(directory=str(assets)), name="assets")

        @app.get("/", include_in_schema=False)
        def index():
            return FileResponse(FRONTEND_DIST / "index.html")

        @app.get("/{full_path:path}", include_in_schema=False)
        def spa(full_path: str):
            candidate = FRONTEND_DIST / full_path
            if candidate.is_file():
                return FileResponse(candidate)
            return FileResponse(FRONTEND_DIST / "index.html")
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
