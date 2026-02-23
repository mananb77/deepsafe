"""
Authentication Schemas

Request/response schemas for authentication endpoints.
"""

from datetime import datetime
from typing import Optional

from pydantic import EmailStr, Field

from src.shared.schemas.base import BaseSchema


class LoginRequest(BaseSchema):
    """Login request schema."""

    email: EmailStr = Field(description="User email address")
    password: str = Field(min_length=8, max_length=128, description="User password")


class RefreshTokenRequest(BaseSchema):
    """Refresh token request schema."""

    refresh_token: str = Field(description="Refresh token")


class TokenResponse(BaseSchema):
    """Token response after successful authentication."""

    access_token: str = Field(description="JWT access token")
    refresh_token: str = Field(description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(description="Access token expiration in seconds")
    expires_at: datetime = Field(description="Access token expiration timestamp")


class TokenPayload(BaseSchema):
    """JWT token payload."""

    sub: str = Field(description="Subject (user ID)")
    email: str = Field(description="User email")
    company_id: str = Field(description="Company ID")
    role: str = Field(description="User role")
    exp: datetime = Field(description="Expiration timestamp")
    iat: datetime = Field(description="Issued at timestamp")
    jti: Optional[str] = Field(default=None, description="JWT ID for revocation")


class PasswordChangeRequest(BaseSchema):
    """Password change request schema."""

    current_password: str = Field(min_length=8, max_length=128)
    new_password: str = Field(min_length=8, max_length=128)


class PasswordResetRequest(BaseSchema):
    """Password reset request schema."""

    email: EmailStr = Field(description="Email address to send reset link")


class PasswordResetConfirm(BaseSchema):
    """Password reset confirmation schema."""

    token: str = Field(description="Password reset token")
    new_password: str = Field(min_length=8, max_length=128)


class SSOLoginRequest(BaseSchema):
    """SSO login request schema."""

    provider: str = Field(description="SSO provider (okta, azure_ad, google)")
    code: str = Field(description="OAuth authorization code")
    redirect_uri: str = Field(description="OAuth redirect URI")


class SSOCallbackResponse(BaseSchema):
    """SSO callback response."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user_id: str
    email: str
    full_name: str
    company_id: str
    is_new_user: bool = Field(description="True if user was just created")
