"""
Participant Model

Represents participants in monitored meetings.
"""

from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import (
    String,
    Float,
    Boolean,
    DateTime,
    Enum as SQLEnum,
    ForeignKey,
    Index,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.shared.models.base import BaseModel

if TYPE_CHECKING:
    from src.shared.models.user import User
    from src.shared.models.meeting import Meeting
    from src.shared.models.incident import Incident
    from src.shared.models.verification import Verification
    from src.shared.models.risk_indicator import RiskIndicator


class TrustLevel(str, Enum):
    """Participant trust classification."""

    UNKNOWN = "unknown"
    TRUSTED = "trusted"
    SUSPICIOUS = "suspicious"
    VERIFIED = "verified"
    BLACKLISTED = "blacklisted"


class ParticipantRole(str, Enum):
    """Role in the meeting."""

    HOST = "host"
    CO_HOST = "co_host"
    PRESENTER = "presenter"
    ATTENDEE = "attendee"


class Participant(BaseModel):
    """
    Participant model representing a person in a meeting.

    Stores participant identity, trust scores, and detection flags.
    """

    __tablename__ = "participants"

    # Meeting Association
    meeting_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("meetings.id", ondelete="CASCADE"),
        nullable=False,
    )

    # User Association (if known DeepSafe user)
    user_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Identity
    display_name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    phone_number: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    avatar_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Platform Identity
    platform_participant_id: Mapped[str] = mapped_column(String(255), nullable=False)
    platform_user_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Meeting Role
    role: Mapped[ParticipantRole] = mapped_column(
        SQLEnum(ParticipantRole, name="participant_role"),
        default=ParticipantRole.ATTENDEE,
        nullable=False,
    )

    # Participation Timing
    joined_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    left_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Trust Assessment
    trust_level: Mapped[TrustLevel] = mapped_column(
        SQLEnum(TrustLevel, name="trust_level"),
        default=TrustLevel.UNKNOWN,
        nullable=False,
    )
    trust_score: Mapped[float] = mapped_column(Float, default=50.0)

    # Risk Scores
    deepfake_confidence: Mapped[float] = mapped_column(Float, default=0.0)
    social_engineering_score: Mapped[float] = mapped_column(Float, default=0.0)
    composite_risk_score: Mapped[float] = mapped_column(Float, default=0.0)

    # Detection Flags
    is_deepfake_suspect: Mapped[bool] = mapped_column(Boolean, default=False)
    is_social_engineering_suspect: Mapped[bool] = mapped_column(Boolean, default=False)
    is_flagged: Mapped[bool] = mapped_column(Boolean, default=False)
    flag_reason: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Verification Status
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    verified_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    verification_method: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # Media Status
    has_video: Mapped[bool] = mapped_column(Boolean, default=False)
    has_audio: Mapped[bool] = mapped_column(Boolean, default=False)
    is_screen_sharing: Mapped[bool] = mapped_column(Boolean, default=False)

    # Extra data (platform-specific data)
    extra_data: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    # Device Information
    device_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    connection_quality: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # Relationships
    meeting: Mapped["Meeting"] = relationship("Meeting", back_populates="participants")
    user: Mapped[Optional["User"]] = relationship("User", back_populates="participants")
    incidents: Mapped[List["Incident"]] = relationship(
        "Incident",
        back_populates="participant",
        lazy="dynamic",
    )
    verifications: Mapped[List["Verification"]] = relationship(
        "Verification",
        back_populates="participant",
        lazy="dynamic",
    )
    risk_indicators: Mapped[List["RiskIndicator"]] = relationship(
        "RiskIndicator",
        back_populates="participant",
        lazy="dynamic",
    )

    # Indexes
    __table_args__ = (
        Index("ix_participants_meeting", "meeting_id"),
        Index("ix_participants_user", "user_id"),
        Index("ix_participants_trust", "meeting_id", "trust_level"),
        Index("ix_participants_risk", "meeting_id", "composite_risk_score"),
        Index("ix_participants_platform", "platform_participant_id"),
    )

    def __repr__(self) -> str:
        return f"<Participant(id={self.id}, name={self.display_name}, trust={self.trust_level})>"

    def update_risk_scores(
        self,
        deepfake: Optional[float] = None,
        social_engineering: Optional[float] = None,
    ) -> None:
        """Update risk scores and calculate composite."""
        if deepfake is not None:
            self.deepfake_confidence = deepfake
            self.is_deepfake_suspect = deepfake > 0.6

        if social_engineering is not None:
            self.social_engineering_score = social_engineering
            self.is_social_engineering_suspect = social_engineering > 0.6

        # Calculate composite risk score
        # Higher weight on deepfake as it's more definitive
        self.composite_risk_score = (
            self.deepfake_confidence * 0.6 + self.social_engineering_score * 0.4
        )

        # Update flags
        self.is_flagged = self.composite_risk_score > 0.6
        if self.is_flagged and not self.flag_reason:
            reasons = []
            if self.is_deepfake_suspect:
                reasons.append("potential deepfake")
            if self.is_social_engineering_suspect:
                reasons.append("social engineering indicators")
            self.flag_reason = ", ".join(reasons)

        # Update trust level
        self._update_trust_level()

    def _update_trust_level(self) -> None:
        """Update trust level based on scores and verification."""
        if self.is_verified:
            self.trust_level = TrustLevel.VERIFIED
        elif self.composite_risk_score > 0.7:
            self.trust_level = TrustLevel.BLACKLISTED
        elif self.composite_risk_score > 0.5:
            self.trust_level = TrustLevel.SUSPICIOUS
        elif self.user_id is not None:
            self.trust_level = TrustLevel.TRUSTED
        else:
            self.trust_level = TrustLevel.UNKNOWN

    def verify(self, method: str) -> None:
        """Mark participant as verified."""
        self.is_verified = True
        self.verified_at = datetime.utcnow()
        self.verification_method = method
        self.trust_level = TrustLevel.VERIFIED
        self.is_flagged = False
        self.flag_reason = None

    def leave(self) -> None:
        """Mark participant as having left the meeting."""
        self.is_active = False
        self.left_at = datetime.utcnow()

    @property
    def duration_minutes(self) -> Optional[int]:
        """Calculate participation duration in minutes."""
        if self.joined_at:
            end_time = self.left_at or datetime.utcnow()
            delta = end_time - self.joined_at
            return int(delta.total_seconds() / 60)
        return None
