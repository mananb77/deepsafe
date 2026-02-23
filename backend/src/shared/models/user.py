"""
User Model

Represents users of the DeepSafe platform.
"""

from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import String, Boolean, DateTime, Enum as SQLEnum, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.shared.models.base import BaseModel, SoftDeleteMixin

if TYPE_CHECKING:
    from src.shared.models.company import Company
    from src.shared.models.participant import Participant
    from src.shared.models.audit_log import AuditLog


class UserRole(str, Enum):
    """User role levels."""

    ADMIN = "admin"
    SECURITY_ANALYST = "security_analyst"
    USER = "user"
    VIEWER = "viewer"


class User(BaseModel, SoftDeleteMixin):
    """
    User model representing platform users.

    Stores user identity, authentication info, and preferences.
    """

    __tablename__ = "users"

    # Identity
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    phone_number: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    avatar_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Authentication
    hashed_password: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    is_sso_user: Mapped[bool] = mapped_column(Boolean, default=False)
    sso_provider: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    sso_subject_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Company Association
    company_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
    )
    role: Mapped[UserRole] = mapped_column(
        SQLEnum(UserRole, name="user_role"),
        default=UserRole.USER,
        nullable=False,
    )

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    email_verified_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    phone_verified_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Trust Management
    is_blacklisted: Mapped[bool] = mapped_column(Boolean, default=False)
    blacklist_reason: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    blacklisted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    is_whitelisted: Mapped[bool] = mapped_column(Boolean, default=False)
    whitelisted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Session Management
    last_login_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    last_active_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Notification Preferences
    notify_email: Mapped[bool] = mapped_column(Boolean, default=True)
    notify_push: Mapped[bool] = mapped_column(Boolean, default=True)
    notify_sms: Mapped[bool] = mapped_column(Boolean, default=False)

    # Device Tokens for Push Notifications
    fcm_token: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    apns_token: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Relationships
    company: Mapped["Company"] = relationship("Company", back_populates="users")
    participants: Mapped[List["Participant"]] = relationship(
        "Participant",
        back_populates="user",
        lazy="dynamic",
    )
    audit_logs: Mapped[List["AuditLog"]] = relationship(
        "AuditLog",
        back_populates="user",
        lazy="dynamic",
    )

    # Indexes
    __table_args__ = (
        Index("ix_users_company_role", "company_id", "role"),
        Index("ix_users_sso", "sso_provider", "sso_subject_id"),
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email}, role={self.role})>"

    @property
    def is_admin(self) -> bool:
        """Check if user is an admin."""
        return self.role == UserRole.ADMIN

    @property
    def is_security_analyst(self) -> bool:
        """Check if user is a security analyst."""
        return self.role in (UserRole.ADMIN, UserRole.SECURITY_ANALYST)

    def blacklist(self, reason: str) -> None:
        """Add user to blacklist."""
        self.is_blacklisted = True
        self.blacklist_reason = reason
        self.blacklisted_at = datetime.utcnow()
        self.is_whitelisted = False
        self.whitelisted_at = None

    def whitelist(self) -> None:
        """Add user to whitelist."""
        self.is_whitelisted = True
        self.whitelisted_at = datetime.utcnow()
        self.is_blacklisted = False
        self.blacklist_reason = None
        self.blacklisted_at = None

    def remove_from_lists(self) -> None:
        """Remove user from both blacklist and whitelist."""
        self.is_blacklisted = False
        self.blacklist_reason = None
        self.blacklisted_at = None
        self.is_whitelisted = False
        self.whitelisted_at = None
