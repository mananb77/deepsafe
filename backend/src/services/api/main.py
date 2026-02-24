"""
DeepSafe API Service

Main FastAPI application with middleware, exception handlers, and route configuration.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
import structlog

from src.shared.config import get_settings
from src.shared.database.postgres import init_db, close_db
from src.shared.database.redis import get_redis, close_redis
from src.shared.database.mongodb import get_mongodb, close_mongodb
from src.services.api.routers import (
    auth_router,
    users_router,
    companies_router,
    meetings_router,
    participants_router,
    incidents_router,
    verifications_router,
    policies_router,
    health_router,
    ws_router,
)
from src.services.api.exceptions import (
    DeepSafeException,
    deepsafe_exception_handler,
    validation_exception_handler,
    generic_exception_handler,
)

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application lifespan manager.

    Handles startup and shutdown events for database connections.
    """
    settings = get_settings()

    # Startup
    logger.info("Starting DeepSafe API", environment=settings.environment)

    try:
        # Initialize database connections
        logger.info("Initializing database connections")
        await init_db()
        await get_redis()
        await get_mongodb()
        logger.info("Database connections established")

        # Initialize alert dispatch pipeline
        try:
            from src.services.stream.alert_generator import AlertDispatcher
            from src.services.stream.alert_handlers import setup_alert_handlers

            alert_dispatcher = AlertDispatcher()
            setup_alert_handlers(alert_dispatcher)
            app.state.alert_dispatcher = alert_dispatcher
            logger.info("Alert dispatch pipeline initialized")
        except Exception as e:
            logger.warning("Alert dispatch pipeline initialization failed", error=str(e))

        yield

    finally:
        # Shutdown
        logger.info("Shutting down DeepSafe API")
        await close_db()
        await close_redis()
        await close_mongodb()
        logger.info("Database connections closed")


def create_application() -> FastAPI:
    """
    Application factory for creating the FastAPI instance.

    Returns:
        FastAPI: Configured application instance.
    """
    settings = get_settings()

    app = FastAPI(
        title="DeepSafe API",
        description="Social Engineering Defense Platform for Video Conferencing",
        version=settings.app_version,
        docs_url="/docs" if settings.is_development else None,
        redoc_url="/redoc" if settings.is_development else None,
        openapi_url="/openapi.json" if settings.is_development else None,
        lifespan=lifespan,
    )

    # Add middleware
    configure_middleware(app, settings)

    # Add exception handlers
    configure_exception_handlers(app)

    # Add routers
    configure_routers(app, settings)

    return app


def configure_middleware(app: FastAPI, settings) -> None:
    """Configure application middleware."""

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors.origins_list,
        allow_credentials=settings.cors.allow_credentials,
        allow_methods=settings.cors.allow_methods,
        allow_headers=settings.cors.allow_headers,
    )

    # GZip compression
    app.add_middleware(GZipMiddleware, minimum_size=1000)

    # Request logging middleware
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        """Log all HTTP requests."""
        request_id = request.headers.get("X-Request-ID", "")

        logger.info(
            "Request started",
            method=request.method,
            path=request.url.path,
            request_id=request_id,
        )

        response = await call_next(request)

        logger.info(
            "Request completed",
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            request_id=request_id,
        )

        return response

    # Request timing middleware
    @app.middleware("http")
    async def add_timing_header(request: Request, call_next):
        """Add server timing header."""
        import time
        start_time = time.perf_counter()
        response = await call_next(request)
        process_time = time.perf_counter() - start_time
        response.headers["X-Process-Time"] = f"{process_time:.4f}"
        return response


def configure_exception_handlers(app: FastAPI) -> None:
    """Configure exception handlers."""
    from fastapi.exceptions import RequestValidationError

    app.add_exception_handler(DeepSafeException, deepsafe_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)


def configure_routers(app: FastAPI, settings) -> None:
    """Configure API routers."""
    api_prefix = settings.api_prefix

    # Health check (no prefix)
    app.include_router(health_router, tags=["Health"])

    # API routes
    app.include_router(auth_router, prefix=f"{api_prefix}/auth", tags=["Authentication"])
    app.include_router(users_router, prefix=f"{api_prefix}/users", tags=["Users"])
    app.include_router(companies_router, prefix=f"{api_prefix}/companies", tags=["Companies"])
    app.include_router(meetings_router, prefix=f"{api_prefix}/meetings", tags=["Meetings"])
    app.include_router(participants_router, prefix=f"{api_prefix}/participants", tags=["Participants"])
    app.include_router(incidents_router, prefix=f"{api_prefix}/incidents", tags=["Incidents"])
    app.include_router(verifications_router, prefix=f"{api_prefix}/verifications", tags=["Verifications"])
    app.include_router(policies_router, prefix=f"{api_prefix}/policies", tags=["Policies"])

    # WebSocket routes
    app.include_router(ws_router, prefix=f"{api_prefix}/ws", tags=["WebSocket"])


# Create application instance
app = create_application()


@app.get("/")
async def root():
    """Root endpoint."""
    settings = get_settings()
    return {
        "service": "DeepSafe API",
        "version": settings.app_version,
        "status": "operational",
    }
