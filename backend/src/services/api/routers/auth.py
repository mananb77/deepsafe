"""
Authentication Router

Endpoints for user authentication, token management, and password operations.
"""

from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.shared.config import get_settings
from src.shared.database.postgres import get_async_session
from src.shared.models.user import User
from src.shared.models.audit_log import AuditLog, AuditAction
from src.shared.schemas.auth import (
    LoginRequest,
    TokenResponse,
    RefreshTokenRequest,
    PasswordChangeRequest,
)
from src.shared.schemas.base import SuccessResponse
from src.shared.security.jwt import (
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_token_type,
)
from src.shared.security.password import verify_password, hash_password, needs_rehash
from src.services.api.dependencies import (
    AsyncSessionDep,
    CurrentUserDep,
    RequestMetadataDep,
)
from src.services.api.exceptions import AuthenticationError, ValidationError

router = APIRouter()


@router.post("/login", response_model=TokenResponse)
async def login(
    request: LoginRequest,
    session: AsyncSessionDep,
    metadata: RequestMetadataDep,
):
    """
    Authenticate user and return JWT tokens.

    Args:
        request: Login credentials (email, password).

    Returns:
        TokenResponse: Access and refresh tokens.

    Raises:
        AuthenticationError: If credentials are invalid.
    """
    settings = get_settings()

    # Find user by email
    result = await session.execute(
        select(User).where(
            User.email == request.email.lower(),
            User.is_deleted == False,
        )
    )
    user = result.scalar_one_or_none()

    if not user:
        # Log failed attempt
        audit_log = AuditLog.log_authentication(
            action=AuditAction.LOGIN_FAILED,
            user_id=None,
            ip_address=metadata.get("ip_address"),
            user_agent=metadata.get("user_agent"),
            success=False,
            metadata={"email": request.email},
        )
        session.add(audit_log)
        await session.commit()

        raise AuthenticationError("Invalid email or password")

    if not user.is_active:
        raise AuthenticationError("Account is disabled")

    if user.is_sso_user:
        raise AuthenticationError("Please use SSO login for this account")

    # Verify password
    if not user.hashed_password or not verify_password(request.password, user.hashed_password):
        # Log failed attempt
        audit_log = AuditLog.log_authentication(
            action=AuditAction.LOGIN_FAILED,
            user_id=user.id,
            ip_address=metadata.get("ip_address"),
            user_agent=metadata.get("user_agent"),
            success=False,
        )
        session.add(audit_log)
        await session.commit()

        raise AuthenticationError("Invalid email or password")

    # Check if password needs rehashing
    if needs_rehash(user.hashed_password):
        user.hashed_password = hash_password(request.password)

    # Update last login
    user.last_login_at = datetime.utcnow()
    user.last_active_at = datetime.utcnow()

    # Create tokens
    access_token = create_access_token(
        user_id=user.id,
        email=user.email,
        company_id=user.company_id,
        role=user.role.value,
    )
    refresh_token = create_refresh_token(
        user_id=user.id,
        email=user.email,
        company_id=user.company_id,
        role=user.role.value,
    )

    # Log successful login
    audit_log = AuditLog.log_authentication(
        action=AuditAction.LOGIN,
        user_id=user.id,
        ip_address=metadata.get("ip_address"),
        user_agent=metadata.get("user_agent"),
        success=True,
    )
    session.add(audit_log)
    await session.commit()

    expires_in = settings.jwt.access_token_expire_minutes * 60
    expires_at = datetime.utcnow() + timedelta(minutes=settings.jwt.access_token_expire_minutes)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=expires_in,
        expires_at=expires_at,
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    request: RefreshTokenRequest,
    session: AsyncSessionDep,
):
    """
    Refresh access token using refresh token.

    Args:
        request: Refresh token.

    Returns:
        TokenResponse: New access and refresh tokens.

    Raises:
        AuthenticationError: If refresh token is invalid.
    """
    settings = get_settings()

    try:
        payload = verify_token_type(request.refresh_token, "refresh")
    except Exception as e:
        raise AuthenticationError(f"Invalid refresh token: {str(e)}")

    user_id = payload.get("sub")

    # Verify user still exists and is active
    result = await session.execute(
        select(User).where(
            User.id == user_id,
            User.is_deleted == False,
        )
    )
    user = result.scalar_one_or_none()

    if not user:
        raise AuthenticationError("User not found")

    if not user.is_active:
        raise AuthenticationError("Account is disabled")

    # Create new tokens
    access_token = create_access_token(
        user_id=user.id,
        email=user.email,
        company_id=user.company_id,
        role=user.role.value,
    )
    new_refresh_token = create_refresh_token(
        user_id=user.id,
        email=user.email,
        company_id=user.company_id,
        role=user.role.value,
    )

    # Update last active
    user.last_active_at = datetime.utcnow()
    await session.commit()

    expires_in = settings.jwt.access_token_expire_minutes * 60
    expires_at = datetime.utcnow() + timedelta(minutes=settings.jwt.access_token_expire_minutes)

    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh_token,
        expires_in=expires_in,
        expires_at=expires_at,
    )


@router.post("/logout", response_model=SuccessResponse)
async def logout(
    user: CurrentUserDep,
    session: AsyncSessionDep,
    metadata: RequestMetadataDep,
):
    """
    Logout current user.

    Note: This endpoint doesn't invalidate the JWT token on the server side.
    Token invalidation should be handled client-side by removing the token.
    For full server-side invalidation, implement a token blacklist in Redis.
    """
    # Log logout
    audit_log = AuditLog.log_authentication(
        action=AuditAction.LOGOUT,
        user_id=user.id,
        ip_address=metadata.get("ip_address"),
        user_agent=metadata.get("user_agent"),
        success=True,
    )
    session.add(audit_log)
    await session.commit()

    return SuccessResponse(message="Logged out successfully")


@router.post("/change-password", response_model=SuccessResponse)
async def change_password(
    request: PasswordChangeRequest,
    user: CurrentUserDep,
    session: AsyncSessionDep,
    metadata: RequestMetadataDep,
):
    """
    Change the current user's password.

    Args:
        request: Current and new password.

    Returns:
        SuccessResponse: Success message.

    Raises:
        AuthenticationError: If current password is incorrect.
        ValidationError: If new password doesn't meet requirements.
    """
    if user.is_sso_user:
        raise ValidationError("SSO users cannot change password here")

    # Verify current password
    if not user.hashed_password or not verify_password(request.current_password, user.hashed_password):
        raise AuthenticationError("Current password is incorrect")

    # Ensure new password is different
    if request.current_password == request.new_password:
        raise ValidationError("New password must be different from current password")

    # Update password
    user.hashed_password = hash_password(request.new_password)

    # Log password change
    audit_log = AuditLog.log_authentication(
        action=AuditAction.PASSWORD_CHANGED,
        user_id=user.id,
        ip_address=metadata.get("ip_address"),
        user_agent=metadata.get("user_agent"),
        success=True,
    )
    session.add(audit_log)
    await session.commit()

    return SuccessResponse(message="Password changed successfully")


@router.get("/me")
async def get_current_user(user: CurrentUserDep):
    """
    Get current authenticated user's profile.

    Returns:
        User profile information.
    """
    return {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "role": user.role.value,
        "company_id": user.company_id,
        "is_verified": user.is_verified,
        "is_sso_user": user.is_sso_user,
        "last_login_at": user.last_login_at,
    }
