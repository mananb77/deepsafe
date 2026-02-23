"""
Verification Model

Represents multi-channel identity verifications.
"""

from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Optional

from sqlalchemy import (
    String,
    Integer,
    DateTime,
    Enum as SQLEnum,
    ForeignKey,
    Index,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.shared.models.base import BaseModel

if TYPE_CHECKING:
    from src.shared.models.participant import Participant
    from src.shared.models.incident import Incident


class VerificationStatus(str, Enum):
    """Verification lifecycle status."""

    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    VERIFIED = "verified"
    FAILED = "failed"
    EXPIRED = "expired"


class VerificationChannel(str, Enum):
    """Verification delivery channels."""

    SMS = "sms"
    VOICE = "voice"
    PUSH = "push"
    EMAIL = "email"


class VerificationType(str, Enum):
    """Types of verification."""

    IDENTITY = "identity"
    TRANSACTION = "transaction"
    HIGH_RISK = "high_risk"
    MANUAL = "manual"


class Verification(BaseModel):
    """
    Verification model for multi-channel identity verification.

    Tracks the full verification flow across SMS, voice, push, and email.
    """

    __tablename__ = "verifications"

    # Associations
    participant_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("participants.id", ondelete="CASCADE"),
        nullable=False,
    )
    incident_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("incidents.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Verification Type
    verification_type: Mapped[VerificationType] = mapped_column(
        SQLEnum(VerificationType, name="verification_type"),
        default=VerificationType.IDENTITY,
        nullable=False,
    )

    # Channel
    channel: Mapped[VerificationChannel] = mapped_column(
        SQLEnum(VerificationChannel, name="verification_channel"),
        nullable=False,
    )
    destination: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Phone number, email, or device token",
    )

    # Status
    status: Mapped[VerificationStatus] = mapped_column(
        SQLEnum(VerificationStatus, name="verification_status"),
        default=VerificationStatus.PENDING,
        nullable=False,
    )

    # Code/Token
    verification_code: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    verification_token: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Timing
    initiated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
    )
    sent_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    delivered_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    verified_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    # Attempts
    attempt_count: Mapped[int] = mapped_column(Integer, default=0)
    max_attempts: Mapped[int] = mapped_column(Integer, default=3)

    # Provider Information
    provider: Mapped[str] = mapped_column(
        String(50),
        default="twilio",
        nullable=False,
    )
    provider_message_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    provider_status: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # Failure Information
    failure_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    error_code: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # Transaction Context (for transaction verifications)
    transaction_amount: Mapped[Optional[float]] = mapped_column(nullable=True)
    transaction_description: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    transaction_metadata: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    # Extra data
    extra_data: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    # Relationships
    participant: Mapped["Participant"] = relationship(
        "Participant",
        back_populates="verifications",
    )
    incident: Mapped[Optional["Incident"]] = relationship(
        "Incident",
        back_populates="verifications",
    )

    # Indexes
    __table_args__ = (
        Index("ix_verifications_participant", "participant_id"),
        Index("ix_verifications_incident", "incident_id"),
        Index("ix_verifications_status", "status"),
        Index("ix_verifications_channel_status", "channel", "status"),
        Index("ix_verifications_token", "verification_token"),
    )

    def __repr__(self) -> str:
        return f"<Verification(id={self.id}, channel={self.channel}, status={self.status})>"

    def mark_sent(self, message_id: Optional[str] = None) -> None:
        """Mark verification as sent."""
        self.status = VerificationStatus.SENT
        self.sent_at = datetime.utcnow()
        if message_id:
            self.provider_message_id = message_id

    def mark_delivered(self) -> None:
        """Mark verification as delivered."""
        self.status = VerificationStatus.DELIVERED
        self.delivered_at = datetime.utcnow()

    def verify(self, code: str) -> bool:
        """
        Attempt to verify with provided code.

        Returns True if verification succeeded.
        """
        self.attempt_count += 1

        # Check if expired
        if datetime.utcnow() > self.expires_at:
            self.status = VerificationStatus.EXPIRED
            return False

        # Check attempts
        if self.attempt_count > self.max_attempts:
            self.status = VerificationStatus.FAILED
            self.failure_reason = "Maximum attempts exceeded"
            return False

        # Check code
        if self.verification_code and code == self.verification_code:
            self.status = VerificationStatus.VERIFIED
            self.verified_at = datetime.utcnow()
            return True

        return False

    def fail(self, reason: str, error_code: Optional[str] = None) -> None:
        """Mark verification as failed."""
        self.status = VerificationStatus.FAILED
        self.failure_reason = reason
        self.error_code = error_code

    def expire(self) -> None:
        """Mark verification as expired."""
        self.status = VerificationStatus.EXPIRED

    @property
    def is_pending(self) -> bool:
        """Check if verification is still pending."""
        return self.status in (
            VerificationStatus.PENDING,
            VerificationStatus.SENT,
            VerificationStatus.DELIVERED,
        )

    @property
    def is_successful(self) -> bool:
        """Check if verification was successful."""
        return self.status == VerificationStatus.VERIFIED

    @property
    def is_expired(self) -> bool:
        """Check if verification has expired."""
        if self.status == VerificationStatus.EXPIRED:
            return True
        return datetime.utcnow() > self.expires_at

    @property
    def remaining_attempts(self) -> int:
        """Get remaining verification attempts."""
        return max(0, self.max_attempts - self.attempt_count)
