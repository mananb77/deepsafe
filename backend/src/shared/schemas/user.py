"""
User Schemas

Request/response schemas for user management.
"""

from datetime import datetime
from typing import List, Optional

from pydantic import EmailStr, Field, field_validator

from src.shared.models.user import UserRole
from src.shared.schemas.base import BaseSchema, PaginatedResponse, TimestampSchema


class UserBase(BaseSchema):
    """Base user schema with common fields."""

    email: EmailStr = Field(description="User email address")
    full_name: str = Field(min_length=1, max_length=255, description="Full name")
    phone_number: Optional[str] = Field(
        default=None,
        max_length=20,
        description="Phone number for verification",
    )


class UserCreate(UserBase):
    """Schema for creating a new user."""

    password: Optional[str] = Field(
        default=None,
        min_length=8,
        max_length=128,
        description="Password (not required for SSO users)",
    )
    role: UserRole = Field(default=UserRole.USER, description="User role")
    company_id: Optional[str] = Field(
        default=None,
        description="Company ID (required for non-SSO)",
    )

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: Optional[str]) -> Optional[str]:
        """Validate password meets security requirements."""
        if v is None:
            return v

        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")

        has_upper = any(c.isupper() for c in v)
        has_lower = any(c.islower() for c in v)
        has_digit = any(c.isdigit() for c in v)

        if not (has_upper and has_lower and has_digit):
            raise ValueError(
                "Password must contain uppercase, lowercase, and numeric characters"
            )

        return v


class UserUpdate(BaseSchema):
    """Schema for updating user information."""

    full_name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    phone_number: Optional[str] = Field(default=None, max_length=20)
    avatar_url: Optional[str] = Field(default=None, max_length=500)
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None
    notify_email: Optional[bool] = None
    notify_push: Optional[bool] = None
    notify_sms: Optional[bool] = None


class UserResponse(TimestampSchema):
    """User response schema."""

    id: str = Field(description="User ID")
    email: EmailStr
    full_name: str
    phone_number: Optional[str] = None
    avatar_url: Optional[str] = None
    role: UserRole
    company_id: str
    is_active: bool
    is_verified: bool
    is_sso_user: bool
    sso_provider: Optional[str] = None
    is_blacklisted: bool
    is_whitelisted: bool
    last_login_at: Optional[datetime] = None
    notify_email: bool
    notify_push: bool
    notify_sms: bool


class UserListResponse(PaginatedResponse[UserResponse]):
    """Paginated user list response."""

    pass


class UserProfileResponse(UserResponse):
    """Extended user profile with additional details."""

    company_name: str
    company_subscription_tier: str
    email_verified_at: Optional[datetime] = None
    phone_verified_at: Optional[datetime] = None


class BlacklistRequest(BaseSchema):
    """Request to blacklist a user."""

    reason: str = Field(min_length=1, max_length=500, description="Reason for blacklisting")


class UserStatsResponse(BaseSchema):
    """User statistics response."""

    total_meetings: int
    meetings_as_host: int
    incidents_involved: int
    verifications_completed: int
    average_trust_score: float
    last_meeting_at: Optional[datetime] = None
