"""
Audit Log Model

Represents audit trail entries for compliance.
"""

from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Optional

from sqlalchemy import (
    String,
    DateTime,
    Enum as SQLEnum,
    ForeignKey,
    Index,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB, INET
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.shared.models.base import BaseModel

if TYPE_CHECKING:
    from src.shared.models.user import User


class AuditAction(str, Enum):
    """Types of auditable actions."""

    # Authentication
    LOGIN = "login"
    LOGOUT = "logout"
    LOGIN_FAILED = "login_failed"
    PASSWORD_CHANGED = "password_changed"
    PASSWORD_RESET = "password_reset"

    # User Management
    USER_CREATED = "user_created"
    USER_UPDATED = "user_updated"
    USER_DELETED = "user_deleted"
    USER_BLACKLISTED = "user_blacklisted"
    USER_WHITELISTED = "user_whitelisted"
    ROLE_CHANGED = "role_changed"

    # Meeting Actions
    MEETING_JOINED = "meeting_joined"
    MEETING_LEFT = "meeting_left"
    MEETING_MONITORED = "meeting_monitored"
    BOT_JOINED = "bot_joined"
    BOT_LEFT = "bot_left"

    # Detection & Incidents
    INCIDENT_CREATED = "incident_created"
    INCIDENT_UPDATED = "incident_updated"
    INCIDENT_RESOLVED = "incident_resolved"
    INCIDENT_FALSE_POSITIVE = "incident_false_positive"
    DEEPFAKE_DETECTED = "deepfake_detected"
    SOCIAL_ENGINEERING_DETECTED = "social_engineering_detected"

    # Verification
    VERIFICATION_INITIATED = "verification_initiated"
    VERIFICATION_COMPLETED = "verification_completed"
    VERIFICATION_FAILED = "verification_failed"

    # Policy
    POLICY_CREATED = "policy_created"
    POLICY_UPDATED = "policy_updated"
    POLICY_DELETED = "policy_deleted"
    POLICY_TRIGGERED = "policy_triggered"

    # Data Access
    DATA_EXPORTED = "data_exported"
    REPORT_GENERATED = "report_generated"
    TRANSCRIPT_ACCESSED = "transcript_accessed"
    RECORDING_ACCESSED = "recording_accessed"

    # Settings
    SETTINGS_UPDATED = "settings_updated"
    INTEGRATION_CONFIGURED = "integration_configured"

    # Other
    CUSTOM = "custom"


class AuditCategory(str, Enum):
    """Categories for grouping audit actions."""

    AUTHENTICATION = "authentication"
    USER_MANAGEMENT = "user_management"
    MEETING = "meeting"
    SECURITY = "security"
    VERIFICATION = "verification"
    POLICY = "policy"
    DATA_ACCESS = "data_access"
    SETTINGS = "settings"
    OTHER = "other"


class AuditLog(BaseModel):
    """
    Audit Log model for compliance tracking.

    Records all significant actions for security and compliance auditing.
    """

    __tablename__ = "audit_logs"

    # User Association
    user_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        comment="User who performed the action (null for system actions)",
    )

    # Action Details
    action: Mapped[AuditAction] = mapped_column(
        SQLEnum(AuditAction, name="audit_action"),
        nullable=False,
    )
    category: Mapped[AuditCategory] = mapped_column(
        SQLEnum(AuditCategory, name="audit_category"),
        nullable=False,
    )
    description: Mapped[str] = mapped_column(Text, nullable=False)

    # Target Information
    target_type: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="Type of entity affected (user, meeting, incident, etc.)",
    )
    target_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False),
        nullable=True,
        comment="ID of the affected entity",
    )

    # Context
    company_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False),
        nullable=True,
    )
    meeting_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False),
        nullable=True,
    )

    # Client Information
    ip_address: Mapped[Optional[str]] = mapped_column(INET, nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    session_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Timing
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
    )

    # Additional Data
    old_values: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True,
        comment="Previous values before change",
    )
    new_values: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True,
        comment="New values after change",
    )
    extra_data: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True,
        comment="Additional context data",
    )

    # Risk/Severity
    is_sensitive: Mapped[bool] = mapped_column(
        default=False,
        comment="Marks actions involving sensitive data",
    )
    risk_level: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
        comment="Risk level of the action (low, medium, high, critical)",
    )

    # Relationships
    user: Mapped[Optional["User"]] = relationship("User", back_populates="audit_logs")

    # Indexes
    __table_args__ = (
        Index("ix_audit_logs_user", "user_id"),
        Index("ix_audit_logs_action", "action"),
        Index("ix_audit_logs_category", "category"),
        Index("ix_audit_logs_occurred", "occurred_at"),
        Index("ix_audit_logs_company", "company_id"),
        Index("ix_audit_logs_meeting", "meeting_id"),
        Index("ix_audit_logs_target", "target_type", "target_id"),
        Index("ix_audit_logs_company_occurred", "company_id", "occurred_at"),
    )

    def __repr__(self) -> str:
        return f"<AuditLog(id={self.id}, action={self.action}, user={self.user_id})>"

    @classmethod
    def log_action(
        cls,
        action: AuditAction,
        description: str,
        user_id: Optional[str] = None,
        company_id: Optional[str] = None,
        meeting_id: Optional[str] = None,
        target_type: Optional[str] = None,
        target_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        session_id: Optional[str] = None,
        old_values: Optional[dict] = None,
        new_values: Optional[dict] = None,
        metadata: Optional[dict] = None,
        is_sensitive: bool = False,
        risk_level: Optional[str] = None,
    ) -> "AuditLog":
        """
        Factory method to create audit log entries.

        Automatically determines category based on action.
        """
        # Map actions to categories
        category_mapping = {
            AuditAction.LOGIN: AuditCategory.AUTHENTICATION,
            AuditAction.LOGOUT: AuditCategory.AUTHENTICATION,
            AuditAction.LOGIN_FAILED: AuditCategory.AUTHENTICATION,
            AuditAction.PASSWORD_CHANGED: AuditCategory.AUTHENTICATION,
            AuditAction.PASSWORD_RESET: AuditCategory.AUTHENTICATION,
            AuditAction.USER_CREATED: AuditCategory.USER_MANAGEMENT,
            AuditAction.USER_UPDATED: AuditCategory.USER_MANAGEMENT,
            AuditAction.USER_DELETED: AuditCategory.USER_MANAGEMENT,
            AuditAction.USER_BLACKLISTED: AuditCategory.USER_MANAGEMENT,
            AuditAction.USER_WHITELISTED: AuditCategory.USER_MANAGEMENT,
            AuditAction.ROLE_CHANGED: AuditCategory.USER_MANAGEMENT,
            AuditAction.MEETING_JOINED: AuditCategory.MEETING,
            AuditAction.MEETING_LEFT: AuditCategory.MEETING,
            AuditAction.MEETING_MONITORED: AuditCategory.MEETING,
            AuditAction.BOT_JOINED: AuditCategory.MEETING,
            AuditAction.BOT_LEFT: AuditCategory.MEETING,
            AuditAction.INCIDENT_CREATED: AuditCategory.SECURITY,
            AuditAction.INCIDENT_UPDATED: AuditCategory.SECURITY,
            AuditAction.INCIDENT_RESOLVED: AuditCategory.SECURITY,
            AuditAction.INCIDENT_FALSE_POSITIVE: AuditCategory.SECURITY,
            AuditAction.DEEPFAKE_DETECTED: AuditCategory.SECURITY,
            AuditAction.SOCIAL_ENGINEERING_DETECTED: AuditCategory.SECURITY,
            AuditAction.VERIFICATION_INITIATED: AuditCategory.VERIFICATION,
            AuditAction.VERIFICATION_COMPLETED: AuditCategory.VERIFICATION,
            AuditAction.VERIFICATION_FAILED: AuditCategory.VERIFICATION,
            AuditAction.POLICY_CREATED: AuditCategory.POLICY,
            AuditAction.POLICY_UPDATED: AuditCategory.POLICY,
            AuditAction.POLICY_DELETED: AuditCategory.POLICY,
            AuditAction.POLICY_TRIGGERED: AuditCategory.POLICY,
            AuditAction.DATA_EXPORTED: AuditCategory.DATA_ACCESS,
            AuditAction.REPORT_GENERATED: AuditCategory.DATA_ACCESS,
            AuditAction.TRANSCRIPT_ACCESSED: AuditCategory.DATA_ACCESS,
            AuditAction.RECORDING_ACCESSED: AuditCategory.DATA_ACCESS,
            AuditAction.SETTINGS_UPDATED: AuditCategory.SETTINGS,
            AuditAction.INTEGRATION_CONFIGURED: AuditCategory.SETTINGS,
        }

        category = category_mapping.get(action, AuditCategory.OTHER)

        return cls(
            action=action,
            category=category,
            description=description,
            user_id=user_id,
            company_id=company_id,
            meeting_id=meeting_id,
            target_type=target_type,
            target_id=target_id,
            ip_address=ip_address,
            user_agent=user_agent,
            session_id=session_id,
            old_values=old_values,
            new_values=new_values,
            metadata=metadata,
            is_sensitive=is_sensitive,
            risk_level=risk_level,
        )

    @classmethod
    def log_authentication(
        cls,
        action: AuditAction,
        user_id: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        success: bool = True,
        metadata: Optional[dict] = None,
    ) -> "AuditLog":
        """Convenience method for authentication events."""
        descriptions = {
            AuditAction.LOGIN: "User logged in successfully" if success else "User login attempt",
            AuditAction.LOGOUT: "User logged out",
            AuditAction.LOGIN_FAILED: "Failed login attempt",
            AuditAction.PASSWORD_CHANGED: "User changed password",
            AuditAction.PASSWORD_RESET: "Password reset requested",
        }

        return cls.log_action(
            action=action,
            description=descriptions.get(action, str(action)),
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
            metadata=metadata,
            is_sensitive=action in (AuditAction.PASSWORD_CHANGED, AuditAction.PASSWORD_RESET),
            risk_level="medium" if action == AuditAction.LOGIN_FAILED else "low",
        )

    @classmethod
    def log_security_event(
        cls,
        action: AuditAction,
        meeting_id: str,
        company_id: str,
        description: str,
        target_id: Optional[str] = None,
        metadata: Optional[dict] = None,
    ) -> "AuditLog":
        """Convenience method for security events."""
        risk_mapping = {
            AuditAction.DEEPFAKE_DETECTED: "critical",
            AuditAction.SOCIAL_ENGINEERING_DETECTED: "high",
            AuditAction.INCIDENT_CREATED: "high",
        }

        return cls.log_action(
            action=action,
            description=description,
            company_id=company_id,
            meeting_id=meeting_id,
            target_type="incident" if "INCIDENT" in action.name else "detection",
            target_id=target_id,
            metadata=metadata,
            risk_level=risk_mapping.get(action, "medium"),
        )
