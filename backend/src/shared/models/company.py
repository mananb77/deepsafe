"""
Company Model

Represents organizations using the DeepSafe platform.
"""

from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import String, Integer, Boolean, DateTime, Enum as SQLEnum, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.shared.models.base import BaseModel, SoftDeleteMixin

if TYPE_CHECKING:
    from src.shared.models.user import User
    from src.shared.models.meeting import Meeting
    from src.shared.models.policy import Policy


class SubscriptionTier(str, Enum):
    """Subscription tier levels."""

    FREE = "free"
    STARTER = "starter"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"


class Company(BaseModel, SoftDeleteMixin):
    """
    Company model representing an organization.

    Stores company information, subscription details, and settings.
    """

    __tablename__ = "companies"

    # Basic Information
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    domain: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    logo_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Subscription
    subscription_tier: Mapped[SubscriptionTier] = mapped_column(
        SQLEnum(SubscriptionTier, name="subscription_tier"),
        default=SubscriptionTier.FREE,
        nullable=False,
    )
    subscription_started_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    subscription_expires_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Limits based on tier
    max_users: Mapped[int] = mapped_column(Integer, default=5, nullable=False)
    max_meetings_per_month: Mapped[int] = mapped_column(Integer, default=100, nullable=False)
    max_concurrent_meetings: Mapped[int] = mapped_column(Integer, default=3, nullable=False)

    # Feature Flags
    deepfake_detection_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    social_engineering_detection_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    verification_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    sso_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    siem_integration_enabled: Mapped[bool] = mapped_column(Boolean, default=False)

    # SSO Configuration
    sso_provider: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    sso_config: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Settings
    default_risk_threshold: Mapped[int] = mapped_column(Integer, default=60)
    auto_record_high_risk: Mapped[bool] = mapped_column(Boolean, default=True)
    notify_security_team: Mapped[bool] = mapped_column(Boolean, default=True)
    security_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Relationships
    users: Mapped[List["User"]] = relationship(
        "User",
        back_populates="company",
        lazy="dynamic",
    )
    meetings: Mapped[List["Meeting"]] = relationship(
        "Meeting",
        back_populates="company",
        lazy="dynamic",
    )
    policies: Mapped[List["Policy"]] = relationship(
        "Policy",
        back_populates="company",
        lazy="dynamic",
    )

    def __repr__(self) -> str:
        return f"<Company(id={self.id}, name={self.name}, tier={self.subscription_tier})>"

    @property
    def is_enterprise(self) -> bool:
        """Check if company has enterprise subscription."""
        return self.subscription_tier == SubscriptionTier.ENTERPRISE

    @property
    def is_subscription_active(self) -> bool:
        """Check if subscription is currently active."""
        if self.subscription_tier == SubscriptionTier.FREE:
            return True
        if self.subscription_expires_at is None:
            return False
        return self.subscription_expires_at > datetime.utcnow()
