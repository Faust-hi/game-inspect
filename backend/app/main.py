"""Точка входа локального FastAPI-приложения.

При старте схема приводится к head штатным механизмом Alembic (с резервной
копией существующего файла); если база пуста и заполнение разрешено,
выполняется первичное наполнение демонстрационными данными.
Собранный frontend отдаётся как статические файлы, поэтому достаточно
одного процесса на 127.0.0.1.
"""
from __future__ import annotations

import logging
import uuid
from urllib.parse import urlsplit
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text
from starlette.exceptions import HTTPException as StarletteHTTPException

from .api import admin, catalog, recommend
from .config import FRONTEND_DIST, settings
from .database import SessionLocal
from .errors import ApiError, ErrorCode, code_for_status, error_payload
from .logging_setup import configure_logging
from . import db_migrate
from .seed import seeder
from .staticfiles_safe import safe_static_path

configure_logging()
logger = logging.getLogger("gamedev_dss")


def request_id_of(request: Request) -> str:
    """Идентификатор запроса: тот же, что ушёл в заголовке и в журнал."""
    return getattr(request.state, "request_id", None) or request.headers.get("x-request-id") or ""


def _bootstrap() -> None:
    """Штатный старт: схема — только миграциями, с резервной копией.

    `create_all` здесь не вызывается намеренно: он не добавляет колонки в
    существующие таблицы, и старая база молча оставалась бы устаревшей (D37).
    При неуспешной миграции заполнение пропускается: приложение стартует
    неготовым (см. /api/health), а не «как готовое».
    """
    try:
        db_migrate.assert_supported_database(settings.DATABASE_URL)
    except db_migrate.UnsupportedDatabaseError as exc:
        db_migrate.state.update(schema_ok=False, schema_error=str(exc))
        logger.error("Неподдерживаемая СУБД: %s", exc)
        return
    report = db_migrate.ensure_schema()
    if not report.get("migrated"):
        logger.error("Заполнение пропущено: схема не приведена к head")
        return
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
        origin = request.headers.get("origin")
        if request.method not in {"GET", "HEAD", "OPTIONS"} and origin:
            allowed = {str(request.base_url).rstrip('/'), 'http://localhost:5173', 'http://127.0.0.1:5173'}
            if origin not in allowed or urlsplit(origin).hostname not in {'localhost', '127.0.0.1', '::1'}:
                logger.warning("Rejected browser origin request_id=%s", request_id)
                return JSONResponse(status_code=403, headers={"X-Request-ID": request_id},
                    content=error_payload("Изменяющий запрос из стороннего сайта запрещён",
                                          code=ErrorCode.FORBIDDEN, request_id=request_id))
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response


def _register_health(app: FastAPI) -> None:
    """Проверка состояния локального сервиса.

    Разделяет живость процесса и готовность данных (D43.4): процесс отвечает
    всегда, а `ready=false` / `unavailable` означает, что схема не приведена
    к head либо опубликованный срез каталога неполон. Частично пустая база
    не выглядит готовой: требуются опубликованные методы и оборудование.
    """

    @app.get("/api/health", tags=["Служебное"], summary="Состояние сервиса")
    def health():
        from sqlalchemy import func, select

        from .models.entities import HardwareCPU, HardwareGPU, Method

        if not db_migrate.state.get("schema_ok", True):
            return JSONResponse(
                status_code=503,
                content={
                    "status": "unavailable", "version": settings.APP_VERSION,
                    "database": "error", "ready": False,
                    "schema_error": str(db_migrate.state.get("schema_error") or ""),
                    "catalog": {"methods": 0, "hardware_cpu": 0, "hardware_gpu": 0},
                },
            )
        db = SessionLocal()
        try:
            try:
                db.execute(text("SELECT 1"))
            except Exception:  # noqa: BLE001 — проверка сообщает, а не падает
                logger.exception("Проверка базы данных не прошла")
                return JSONResponse(
                    status_code=503,
                    content={"status": "unavailable", "version": settings.APP_VERSION,
                             "database": "error", "ready": False, "schema_error": None,
                             "catalog": {"methods": 0, "hardware_cpu": 0, "hardware_gpu": 0}},
                )
            published_methods = db.scalar(
                select(func.count(Method.id)).where(Method.status == "published")
            ) or 0
            published_cpu = db.scalar(
                select(func.count(HardwareCPU.id)).where(HardwareCPU.status == "published")
            ) or 0
            published_gpu = db.scalar(
                select(func.count(HardwareGPU.id)).where(HardwareGPU.status == "published")
            ) or 0
            catalog = {
                "methods": published_methods,
                "hardware_cpu": published_cpu, "hardware_gpu": published_gpu,
            }
            ready = published_methods > 0 and published_cpu > 0 and published_gpu > 0
            filled = not seeder.is_empty(db)
        finally:
            db.close()
        database = "ready" if filled else "empty"
        return {
            "status": "ok" if ready else "degraded",
            "version": settings.APP_VERSION,
            "database": database,
            "ready": ready,
            "schema_error": None,
            "catalog": catalog,
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
