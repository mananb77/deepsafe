"""
JWT Token Management

Handles creation, validation, and decoding of JWT tokens.
"""

from datetime import datetime, timedelta
from typing import Any, Dict, Optional
from uuid import uuid4

from jose import JWTError, jwt
from pydantic import BaseModel

from src.shared.config import get_settings


class TokenData(BaseModel):
    """JWT token payload data."""
    sub: str  # User ID
    email: str
    company_id: str
    role: str
    exp: datetime
    iat: datetime
    jti: str  # JWT ID for revocation
    type: str  # "access" or "refresh"


def create_access_token(
    user_id: str,
    email: str,
    company_id: str,
    role: str,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """
    Create a JWT access token.

    Args:
        user_id: The user's unique identifier.
        email: The user's email address.
        company_id: The user's company ID.
        role: The user's role.
        expires_delta: Optional custom expiration time.

    Returns:
        str: Encoded JWT access token.
    """
    settings = get_settings()

    if expires_delta is None:
        expires_delta = timedelta(minutes=settings.jwt.access_token_expire_minutes)

    now = datetime.utcnow()
    expire = now + expires_delta

    payload = {
        "sub": user_id,
        "email": email,
        "company_id": company_id,
        "role": role,
        "exp": expire,
        "iat": now,
        "jti": str(uuid4()),
        "type": "access",
    }

    return jwt.encode(
        payload,
        settings.jwt.secret_key,
        algorithm=settings.jwt.algorithm,
    )


def create_refresh_token(
    user_id: str,
    email: str,
    company_id: str,
    role: str,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """
    Create a JWT refresh token.

    Args:
        user_id: The user's unique identifier.
        email: The user's email address.
        company_id: The user's company ID.
        role: The user's role.
        expires_delta: Optional custom expiration time.

    Returns:
        str: Encoded JWT refresh token.
    """
    settings = get_settings()

    if expires_delta is None:
        expires_delta = timedelta(days=settings.jwt.refresh_token_expire_days)

    now = datetime.utcnow()
    expire = now + expires_delta

    payload = {
        "sub": user_id,
        "email": email,
        "company_id": company_id,
        "role": role,
        "exp": expire,
        "iat": now,
        "jti": str(uuid4()),
        "type": "refresh",
    }

    return jwt.encode(
        payload,
        settings.jwt.secret_key,
        algorithm=settings.jwt.algorithm,
    )


def decode_token(token: str) -> Dict[str, Any]:
    """
    Decode and validate a JWT token.

    Args:
        token: The JWT token string.

    Returns:
        Dict[str, Any]: The decoded token payload.

    Raises:
        JWTError: If the token is invalid or expired.
    """
    settings = get_settings()

    try:
        payload = jwt.decode(
            token,
            settings.jwt.secret_key,
            algorithms=[settings.jwt.algorithm],
        )
        return payload
    except JWTError as e:
        raise JWTError(f"Token validation failed: {str(e)}")


def verify_token_type(token: str, expected_type: str) -> Dict[str, Any]:
    """
    Decode token and verify its type.

    Args:
        token: The JWT token string.
        expected_type: Expected token type ("access" or "refresh").

    Returns:
        Dict[str, Any]: The decoded token payload.

    Raises:
        JWTError: If the token is invalid or wrong type.
    """
    payload = decode_token(token)

    if payload.get("type") != expected_type:
        raise JWTError(f"Expected {expected_type} token, got {payload.get('type')}")

    return payload


def get_token_expiry(token: str) -> datetime:
    """
    Get the expiration datetime of a token.

    Args:
        token: The JWT token string.

    Returns:
        datetime: Token expiration time.
    """
    payload = decode_token(token)
    return datetime.fromtimestamp(payload["exp"])


def is_token_expired(token: str) -> bool:
    """
    Check if a token is expired.

    Args:
        token: The JWT token string.

    Returns:
        bool: True if expired, False otherwise.
    """
    try:
        decode_token(token)
        return False
    except JWTError:
        return True
