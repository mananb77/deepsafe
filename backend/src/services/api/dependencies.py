"""
API Dependencies

FastAPI dependency injection for database sessions, authentication, and authorization.
"""

from typing import Annotated, Optional

from fastapi import Depends, Header, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from src.shared.config import get_settings, Settings
from src.shared.database.postgres import get_async_session
from src.shared.database.redis import RedisClient, get_redis
from src.shared.database.mongodb import MongoDBClient, get_mongodb
from src.shared.models.user import User, UserRole
from src.shared.schemas.base import PaginationParams
from src.services.api.exceptions import AuthenticationError, AuthorizationError


# Security scheme
security = HTTPBearer(auto_error=False)


# Type aliases for dependency injection
AsyncSessionDep = Annotated[AsyncSession, Depends(get_async_session)]
SettingsDep = Annotated[Settings, Depends(get_settings)]


async def get_redis_client() -> RedisClient:
    """Get Redis client dependency."""
    return await get_redis()


async def get_mongodb_client() -> MongoDBClient:
    """Get MongoDB client dependency."""
    return await get_mongodb()


RedisDep = Annotated[RedisClient, Depends(get_redis_client)]
MongoDBDep = Annotated[MongoDBClient, Depends(get_mongodb_client)]


async def get_current_user(
    credentials: Annotated[Optional[HTTPAuthorizationCredentials], Depends(security)],
    session: AsyncSessionDep,
) -> User:
    """
    Get the current authenticated user from JWT token.

    Raises:
        AuthenticationError: If token is missing or invalid.
    """
    from src.shared.security.jwt import decode_token
    from sqlalchemy import select

    if credentials is None:
        raise AuthenticationError("Missing authentication token")

    token = credentials.credentials

    try:
        payload = decode_token(token)
    except Exception as e:
        raise AuthenticationError(f"Invalid token: {str(e)}")

    user_id = payload.get("sub")
    if not user_id:
        raise AuthenticationError("Invalid token payload")

    # Fetch user from database
    result = await session.execute(
        select(User).where(User.id == user_id, User.is_deleted == False)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise AuthenticationError("User not found")

    if not user.is_active:
        raise AuthenticationError("User account is disabled")

    return user


async def get_current_user_optional(
    credentials: Annotated[Optional[HTTPAuthorizationCredentials], Depends(security)],
    session: AsyncSessionDep,
) -> Optional[User]:
    """
    Get the current user if authenticated, otherwise None.

    Useful for endpoints that support both authenticated and anonymous access.
    """
    if credentials is None:
        return None

    try:
        return await get_current_user(credentials, session)
    except AuthenticationError:
        return None


CurrentUserDep = Annotated[User, Depends(get_current_user)]
OptionalUserDep = Annotated[Optional[User], Depends(get_current_user_optional)]


def require_role(*roles: UserRole):
    """
    Dependency factory for role-based authorization.

    Usage:
        @router.get("/admin")
        async def admin_only(user: User = Depends(require_role(UserRole.ADMIN))):
            ...
    """
    async def role_checker(user: CurrentUserDep) -> User:
        if user.role not in roles:
            raise AuthorizationError(
                f"Required role: {', '.join(r.value for r in roles)}",
                details={"user_role": user.role.value, "required_roles": [r.value for r in roles]},
            )
        return user

    return role_checker


def require_admin():
    """Require admin role."""
    return require_role(UserRole.ADMIN)


def require_security_analyst():
    """Require security analyst or admin role."""
    return require_role(UserRole.ADMIN, UserRole.SECURITY_ANALYST)


AdminUserDep = Annotated[User, Depends(require_admin())]
SecurityAnalystDep = Annotated[User, Depends(require_security_analyst())]


async def get_pagination(
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(default=20, ge=1, le=100, description="Items per page"),
) -> PaginationParams:
    """Get pagination parameters."""
    return PaginationParams(page=page, page_size=page_size)


PaginationDep = Annotated[PaginationParams, Depends(get_pagination)]


async def verify_company_access(
    company_id: str,
    user: CurrentUserDep,
) -> str:
    """
    Verify user has access to the specified company.

    Raises:
        AuthorizationError: If user doesn't belong to the company.
    """
    if user.company_id != company_id:
        raise AuthorizationError("Access denied to this company's resources")
    return company_id


async def get_request_metadata(
    x_request_id: Optional[str] = Header(default=None, alias="X-Request-ID"),
    x_forwarded_for: Optional[str] = Header(default=None, alias="X-Forwarded-For"),
    user_agent: Optional[str] = Header(default=None, alias="User-Agent"),
) -> dict:
    """Extract request metadata for logging and audit."""
    return {
        "request_id": x_request_id,
        "ip_address": x_forwarded_for.split(",")[0].strip() if x_forwarded_for else None,
        "user_agent": user_agent,
    }


RequestMetadataDep = Annotated[dict, Depends(get_request_metadata)]
