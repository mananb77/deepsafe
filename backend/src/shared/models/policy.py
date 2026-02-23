"""
Policy Model

Represents workflow and automation policies.
"""

from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Optional

from sqlalchemy import (
    String,
    Integer,
    Float,
    Boolean,
    DateTime,
    Enum as SQLEnum,
    ForeignKey,
    Index,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.shared.models.base import BaseModel, SoftDeleteMixin

if TYPE_CHECKING:
    from src.shared.models.company import Company


class PolicyType(str, Enum):
    """Types of policies."""

    RISK_THRESHOLD = "risk_threshold"
    VERIFICATION = "verification"
    NOTIFICATION = "notification"
    APPROVAL = "approval"
    RECORDING = "recording"
    BLOCKING = "blocking"


class PolicyTrigger(str, Enum):
    """Events that trigger policy evaluation."""

    MEETING_START = "meeting_start"
    PARTICIPANT_JOIN = "participant_join"
    RISK_SCORE_CHANGE = "risk_score_change"
    DEEPFAKE_DETECTED = "deepfake_detected"
    SOCIAL_ENGINEERING_DETECTED = "social_engineering_detected"
    TRANSACTION_MENTIONED = "transaction_mentioned"
    VERIFICATION_REQUESTED = "verification_requested"
    VERIFICATION_FAILED = "verification_failed"


class PolicyAction(str, Enum):
    """Actions that policies can take."""

    ALERT_POPUP = "alert_popup"
    SEND_NOTIFICATION = "send_notification"
    TRIGGER_VERIFICATION = "trigger_verification"
    START_RECORDING = "start_recording"
    FLAG_PARTICIPANT = "flag_participant"
    BLOCK_SCREEN_SHARE = "block_screen_share"
    REQUIRE_APPROVAL = "require_approval"
    ALERT_SECURITY_TEAM = "alert_security_team"
    LOG_INCIDENT = "log_incident"


class Policy(BaseModel, SoftDeleteMixin):
    """
    Policy model for workflow automation.

    Defines rules for automated responses to detected threats.
    """

    __tablename__ = "policies"

    # Company Association
    company_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Policy Identity
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    policy_type: Mapped[PolicyType] = mapped_column(
        SQLEnum(PolicyType, name="policy_type"),
        nullable=False,
    )

    # Status
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    priority: Mapped[int] = mapped_column(
        Integer,
        default=100,
        comment="Lower number = higher priority",
    )

    # Trigger Configuration
    trigger: Mapped[PolicyTrigger] = mapped_column(
        SQLEnum(PolicyTrigger, name="policy_trigger"),
        nullable=False,
    )

    # Conditions (evaluated as AND)
    conditions: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
        comment="Conditions that must be met for policy to activate",
    )

    # Actions
    actions: Mapped[list] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
        comment="List of actions to take when policy triggers",
    )

    # Risk Thresholds
    min_risk_score: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
        comment="Minimum risk score to trigger (0-100)",
    )
    max_risk_score: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
        comment="Maximum risk score to trigger (0-100)",
    )

    # Transaction Thresholds
    min_transaction_amount: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
        comment="Minimum transaction amount to trigger",
    )
    max_transaction_amount: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
        comment="Maximum transaction amount to trigger",
    )

    # Time Restrictions
    active_days: Mapped[Optional[list]] = mapped_column(
        JSONB,
        nullable=True,
        comment="Days of week policy is active (0=Monday, 6=Sunday)",
    )
    active_hours_start: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="Hour of day policy starts (0-23)",
    )
    active_hours_end: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="Hour of day policy ends (0-23)",
    )

    # Cooldown
    cooldown_minutes: Mapped[int] = mapped_column(
        Integer,
        default=0,
        comment="Minutes before policy can trigger again",
    )
    last_triggered_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Statistics
    trigger_count: Mapped[int] = mapped_column(Integer, default=0)

    # Extra data
    extra_data: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    # Relationships
    company: Mapped["Company"] = relationship("Company", back_populates="policies")

    # Indexes
    __table_args__ = (
        Index("ix_policies_company", "company_id"),
        Index("ix_policies_company_enabled", "company_id", "is_enabled"),
        Index("ix_policies_type_trigger", "policy_type", "trigger"),
        Index("ix_policies_priority", "priority"),
    )

    def __repr__(self) -> str:
        return f"<Policy(id={self.id}, name={self.name}, type={self.policy_type})>"

    def can_trigger(self) -> bool:
        """Check if policy can be triggered (not in cooldown)."""
        if not self.is_enabled:
            return False

        if self.cooldown_minutes == 0:
            return True

        if self.last_triggered_at is None:
            return True

        elapsed = (datetime.utcnow() - self.last_triggered_at).total_seconds() / 60
        return elapsed >= self.cooldown_minutes

    def record_trigger(self) -> None:
        """Record that policy was triggered."""
        self.last_triggered_at = datetime.utcnow()
        self.trigger_count += 1

    def evaluate_conditions(self, context: dict) -> bool:
        """
        Evaluate if conditions are met.

        Args:
            context: Dictionary with evaluation context (risk_score, transaction_amount, etc.)

        Returns:
            True if all conditions are met.
        """
        # Check risk score thresholds
        if "risk_score" in context:
            risk_score = context["risk_score"]
            if self.min_risk_score is not None and risk_score < self.min_risk_score:
                return False
            if self.max_risk_score is not None and risk_score > self.max_risk_score:
                return False

        # Check transaction amount thresholds
        if "transaction_amount" in context and context["transaction_amount"] is not None:
            amount = context["transaction_amount"]
            if self.min_transaction_amount is not None and amount < self.min_transaction_amount:
                return False
            if self.max_transaction_amount is not None and amount > self.max_transaction_amount:
                return False

        # Check time restrictions
        if self.active_days is not None or self.active_hours_start is not None:
            now = datetime.utcnow()

            if self.active_days is not None and now.weekday() not in self.active_days:
                return False

            if self.active_hours_start is not None:
                hour = now.hour
                if self.active_hours_end is not None:
                    if self.active_hours_start <= self.active_hours_end:
                        if not (self.active_hours_start <= hour <= self.active_hours_end):
                            return False
                    else:  # Spans midnight
                        if not (hour >= self.active_hours_start or hour <= self.active_hours_end):
                            return False

        # Evaluate custom conditions
        for condition_key, condition_value in self.conditions.items():
            if condition_key in context:
                if context[condition_key] != condition_value:
                    return False

        return True

    @classmethod
    def create_default_policies(cls, company_id: str) -> list["Policy"]:
        """Create default policy set for a company."""
        return [
            # High risk alert policy
            cls(
                company_id=company_id,
                name="High Risk Alert",
                description="Alert security team when risk score exceeds 75%",
                policy_type=PolicyType.NOTIFICATION,
                trigger=PolicyTrigger.RISK_SCORE_CHANGE,
                min_risk_score=75,
                conditions={},
                actions=[
                    {"action": PolicyAction.ALERT_POPUP.value},
                    {"action": PolicyAction.ALERT_SECURITY_TEAM.value},
                    {"action": PolicyAction.LOG_INCIDENT.value},
                ],
                priority=10,
            ),
            # Deepfake verification policy
            cls(
                company_id=company_id,
                name="Deepfake Verification Required",
                description="Trigger verification when deepfake is detected",
                policy_type=PolicyType.VERIFICATION,
                trigger=PolicyTrigger.DEEPFAKE_DETECTED,
                conditions={},
                actions=[
                    {"action": PolicyAction.TRIGGER_VERIFICATION.value},
                    {"action": PolicyAction.FLAG_PARTICIPANT.value},
                    {"action": PolicyAction.START_RECORDING.value},
                ],
                priority=5,
            ),
            # Large transaction approval policy
            cls(
                company_id=company_id,
                name="Large Transaction Approval",
                description="Require dual approval for transactions over $25,000",
                policy_type=PolicyType.APPROVAL,
                trigger=PolicyTrigger.TRANSACTION_MENTIONED,
                min_transaction_amount=25000,
                conditions={},
                actions=[
                    {"action": PolicyAction.REQUIRE_APPROVAL.value},
                    {"action": PolicyAction.SEND_NOTIFICATION.value},
                ],
                priority=20,
            ),
        ]
