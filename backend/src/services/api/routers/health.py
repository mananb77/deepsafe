"""
Health Check Router

Endpoints for service health monitoring.
"""

from fastapi import APIRouter, status
from pydantic import BaseModel

from src.shared.config import get_settings
from src.shared.database.postgres import get_engine
from src.shared.database.redis import get_redis
from src.shared.database.mongodb import get_mongodb

router = APIRouter()


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str
    environment: str
    database: str
    redis: str
    mongodb: str


class ReadinessResponse(BaseModel):
    """Readiness check response."""
    ready: bool
    checks: dict


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Basic health check endpoint.

    Returns service status and version information.
    """
    settings = get_settings()

    # Check database connections
    db_status = "healthy"
    redis_status = "healthy"
    mongo_status = "healthy"

    try:
        engine = get_engine()
        async with engine.connect() as conn:
            await conn.execute("SELECT 1")
    except Exception:
        db_status = "unhealthy"

    try:
        redis = await get_redis()
        await redis.client.ping()
    except Exception:
        redis_status = "unhealthy"

    try:
        mongo = await get_mongodb()
        await mongo.db.command("ping")
    except Exception:
        mongo_status = "unhealthy"

    overall_status = "healthy"
    if any(s == "unhealthy" for s in [db_status, redis_status, mongo_status]):
        overall_status = "degraded"

    return HealthResponse(
        status=overall_status,
        version=settings.app_version,
        environment=settings.environment,
        database=db_status,
        redis=redis_status,
        mongodb=mongo_status,
    )


@router.get("/health/live", status_code=status.HTTP_200_OK)
async def liveness_check():
    """
    Kubernetes liveness probe endpoint.

    Returns 200 if the service is running.
    """
    return {"status": "alive"}


@router.get("/health/ready", response_model=ReadinessResponse)
async def readiness_check():
    """
    Kubernetes readiness probe endpoint.

    Returns 200 if the service is ready to accept traffic.
    """
    checks = {
        "database": False,
        "redis": False,
        "mongodb": False,
    }

    try:
        engine = get_engine()
        async with engine.connect() as conn:
            await conn.execute("SELECT 1")
        checks["database"] = True
    except Exception:
        pass

    try:
        redis = await get_redis()
        await redis.client.ping()
        checks["redis"] = True
    except Exception:
        pass

    try:
        mongo = await get_mongodb()
        await mongo.db.command("ping")
        checks["mongodb"] = True
    except Exception:
        pass

    ready = all(checks.values())

    return ReadinessResponse(ready=ready, checks=checks)
