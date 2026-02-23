"""
Company Schemas

Request/response schemas for company management.
"""

from datetime import datetime
from typing import Optional

from pydantic import EmailStr, Field, field_validator

from src.shared.models.company import SubscriptionTier
from src.shared.schemas.base import BaseSchema, TimestampSchema


class CompanyBase(BaseSchema):
    """Base company schema."""

    name: str = Field(min_length=1, max_length=255, description="Company name")
    domain: str = Field(min_length=3, max_length=255, description="Company domain")

    @field_validator("domain")
    @classmethod
    def validate_domain(cls, v: str) -> str:
        """Validate domain format."""
        import re

        # Basic domain validation
        pattern = r"^[a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?(\.[a-zA-Z]{2,})+$"
        if not re.match(pattern, v):
            raise ValueError("Invalid domain format")
        return v.lower()


class CompanyCreate(CompanyBase):
    """Schema for creating a new company."""

    logo_url: Optional[str] = Field(default=None, max_length=500)
    subscription_tier: SubscriptionTier = Field(default=SubscriptionTier.FREE)
    security_email: Optional[EmailStr] = Field(
        default=None,
        description="Email for security notifications",
    )


class CompanyUpdate(BaseSchema):
    """Schema for updating company information."""

    name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    logo_url: Optional[str] = Field(default=None, max_length=500)
    security_email: Optional[EmailStr] = None
    default_risk_threshold: Optional[int] = Field(default=None, ge=0, le=100)
    auto_record_high_risk: Optional[bool] = None
    notify_security_team: Optional[bool] = None
    deepfake_detection_enabled: Optional[bool] = None
    social_engineering_detection_enabled: Optional[bool] = None
    verification_enabled: Optional[bool] = None


class CompanyResponse(TimestampSchema):
    """Company response schema."""

    id: str
    name: str
    domain: str
    logo_url: Optional[str] = None
    subscription_tier: SubscriptionTier
    subscription_started_at: Optional[datetime] = None
    subscription_expires_at: Optional[datetime] = None
    max_users: int
    max_meetings_per_month: int
    max_concurrent_meetings: int
    deepfake_detection_enabled: bool
    social_engineering_detection_enabled: bool
    verification_enabled: bool
    sso_enabled: bool
    siem_integration_enabled: bool
    sso_provider: Optional[str] = None
    default_risk_threshold: int
    auto_record_high_risk: bool
    notify_security_team: bool
    security_email: Optional[str] = None


class CompanyStatsResponse(BaseSchema):
    """Company statistics response."""

    total_users: int
    active_users: int
    total_meetings: int
    meetings_this_month: int
    active_meetings: int
    total_incidents: int
    open_incidents: int
    high_risk_meetings: int
    average_risk_score: float
    verifications_triggered: int
    verifications_completed: int


class SubscriptionUpdateRequest(BaseSchema):
    """Request to update subscription."""

    tier: SubscriptionTier
    billing_period: str = Field(description="monthly or annual")


class SSOConfigRequest(BaseSchema):
    """SSO configuration request."""

    provider: str = Field(description="okta, azure_ad, or google")
    client_id: str
    client_secret: str
    issuer_url: Optional[str] = None
    tenant_id: Optional[str] = Field(
        default=None,
        description="Azure AD tenant ID",
    )
