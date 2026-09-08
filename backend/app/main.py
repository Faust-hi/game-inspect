"""Точка входа локального FastAPI-приложения.

При старте создаются таблицы и, если база пуста и заполнение разрешено,
выполняется первичное наполнение демонстрационными данными.
Собранный frontend отдаётся как статические файлы, поэтому достаточно
одного процесса на 127.0.0.1.
"""
from __future__ import annotations

import logging
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text
from starlette.exceptions import HTTPException as StarletteHTTPException

from .api import admin, catalog, project_exchange, recommend
from .config import FRONTEND_DIST, settings
from .database import SessionLocal, engine
from .errors import ApiError, ErrorCode, code_for_status, error_payload
from .logging_setup import configure_logging
from .models.entities import Base
from .seed import seeder
from .staticfiles_safe import safe_static_path

configure_logging()
logger = logging.getLogger("gamedev_dss")


def request_id_of(request: Request) -> str:
    """Идентификатор запроса: тот же, что ушёл в заголовке и в журнал."""
    return getattr(request.state, "request_id", None) or request.headers.get("x-request-id") or ""


def _bootstrap() -> None:
    Base.metadata.create_all(bind=engine)
    if not settings.AUTO_SEED:
        return
    db = SessionLocal()
    try:
        if seeder.is_empty(db):
            logger.info("База пуста — выполняется первичное заполнение")
            result = seeder.seed_all(db, validate=True)
            logger.info("Первичное заполнение завершено: %s", result)
        else:
            result = seeder.sync_function_taxonomy(db)
            db.commit()
            logger.info("База уже содержит данные — синхронизирована классификация: %s", result)
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

    def _message_and_details(detail: object) -> tuple[str, list]:
        """Разбирает `detail` исключения: строка либо словарь с полями.

        Часть маршрутов передавала словарь `{"error": ..., "details": ...}`.
        Без разбора он попадал в тело как объект вместо строки, и клиент
        показывал безликое «Ошибка 422», теряя причину отказа.
        """
        if isinstance(detail, dict):
            message = detail.get("error") or detail.get("message") or "Ошибка запроса"
            details = detail.get("details") or []
            return str(message), details if isinstance(details, list) else [details]
        return str(detail), []

    @app.exception_handler(ApiError)
    async def api_error_handler(request: Request, exc: ApiError):
        request_id = request_id_of(request)
        logger.warning(
            "Ошибка %s [%s] при обработке %s: %s",
            exc.status, exc.code.value, request.url.path, exc.message,
        )
        return JSONResponse(
            status_code=exc.status,
            content=error_payload(
                exc.message, code=exc.code, request_id=request_id, details=exc.details,
            ),
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        request_id = request_id_of(request)
        message, details = _message_and_details(exc.detail)
        if exc.status_code >= 500:
            logger.error(
                "Ошибка %s при обработке %s [%s]: %s",
                exc.status_code, request.url.path, request_id, message,
            )
        return JSONResponse(
            status_code=exc.status_code,
            content=error_payload(
                message, code=code_for_status(exc.status_code),
                request_id=request_id, details=details,
            ),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        details = [
            {"field": ".".join(str(p) for p in item.get("loc", ())), "message": item.get("msg", "")}
            for item in exc.errors()
        ]
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=error_payload(
                "Некорректные данные запроса",
                code=ErrorCode.VALIDATION,
                request_id=request_id_of(request),
                details=details,
            ),
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        """Необработанное исключение: подробности в журнал, клиенту код для связи."""
        request_id = request_id_of(request)
        error_id = uuid.uuid4().hex[:12]
        logger.exception(
            "Необработанное исключение %s при обработке %s [%s]",
            error_id, request.url.path, request_id,
        )
        return JSONResponse(
            status_code=500,
            content=error_payload(
                "Внутренняя ошибка сервиса",
                code=ErrorCode.INTERNAL,
                request_id=request_id,
                details=[{"error_id": error_id}],
            ),
        )


def _register_middleware(app: FastAPI) -> None:
    """Сквозной идентификатор запроса.

    Идентификатор запоминается в состоянии запроса, а не только в заголовке:
    обработчики ошибок запускаются вне middleware и otherwise читали бы
    исходные заголовки, получая `request_id=null` в теле ответа.
    """

    @app.middleware("http")
    async def request_context(request: Request, call_next):
        request_id = request.headers.get("x-request-id") or uuid.uuid4().hex[:12]
        request.state.request_id = request_id
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response


def _register_health(app: FastAPI) -> None:
    """Проверка состояния локального сервиса."""

    @app.get("/api/health", tags=["Служебное"], summary="Состояние сервиса")
    def health():
        db = SessionLocal()
        try:
            try:
                db.execute(text("SELECT 1"))
            except Exception:  # noqa: BLE001 — проверка сообщает, а не падает
                logger.exception("Проверка базы данных не прошла")
                return JSONResponse(
                    status_code=503,
                    content={"status": "unavailable", "version": settings.APP_VERSION, "database": "error"},
                )
            filled = not seeder.is_empty(db)
        finally:
            db.close()
        return {
            "status": "ok" if filled else "degraded",
            "version": settings.APP_VERSION,
            "database": "ready" if filled else "empty",
        }


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_TITLE,
        version=settings.APP_VERSION,
        description=(
            "Информационная система поддержки принятия решений по оптимизации "
            "на этапе разработки игры. Локальный режим."
        ),
        lifespan=lifespan,
    )

    _register_middleware(app)
    _register_exception_handlers(app)

    prefix = settings.API_PREFIX
    app.include_router(catalog.router, prefix=prefix)
    app.include_router(catalog.enums_router, prefix=prefix)
    app.include_router(recommend.router, prefix=prefix)
    app.include_router(admin.router, prefix=prefix)
    app.include_router(admin.projects_router, prefix=prefix)
    app.include_router(project_exchange.router, prefix=prefix)
    _register_health(app)

    # Документация доступна по обоим адресам: /docs и /api/docs.
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
