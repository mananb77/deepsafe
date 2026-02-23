"""
Meeting Model

Represents video conferencing meetings being monitored.
"""

from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, List, Optional

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

from src.shared.models.base import BaseModel

if TYPE_CHECKING:
    from src.shared.models.company import Company
    from src.shared.models.participant import Participant
    from src.shared.models.incident import Incident
    from src.shared.models.risk_indicator import RiskIndicator


class MeetingStatus(str, Enum):
    """Meeting lifecycle status."""

    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class MeetingPlatform(str, Enum):
    """Supported video conferencing platforms."""

    ZOOM = "zoom"
    GOOGLE_MEET = "google_meet"
    MICROSOFT_TEAMS = "microsoft_teams"


class RiskLevel(str, Enum):
    """Risk classification levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Meeting(BaseModel):
    """
    Meeting model representing a monitored video conference.

    Stores meeting metadata, risk scores, and links to participants.
    """

    __tablename__ = "meetings"

    # Platform Information
    platform: Mapped[MeetingPlatform] = mapped_column(
        SQLEnum(MeetingPlatform, name="meeting_platform"),
        nullable=False,
    )
    platform_meeting_id: Mapped[str] = mapped_column(String(255), nullable=False)
    platform_meeting_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Company Association
    company_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Meeting Details
    title: Mapped[str] = mapped_column(String(500), default="Untitled Meeting")
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    host_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Scheduling
    scheduled_start_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    scheduled_end_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    actual_start_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    actual_end_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Status
    status: Mapped[MeetingStatus] = mapped_column(
        SQLEnum(MeetingStatus, name="meeting_status"),
        default=MeetingStatus.SCHEDULED,
        nullable=False,
    )

    # Participant Counts
    participant_count: Mapped[int] = mapped_column(Integer, default=0)
    max_participants: Mapped[int] = mapped_column(Integer, default=0)

    # Risk Assessment
    risk_score: Mapped[float] = mapped_column(Float, default=0.0)
    risk_level: Mapped[RiskLevel] = mapped_column(
        SQLEnum(RiskLevel, name="risk_level"),
        default=RiskLevel.LOW,
        nullable=False,
    )
    peak_risk_score: Mapped[float] = mapped_column(Float, default=0.0)
    peak_risk_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Detection Flags
    deepfake_detected: Mapped[bool] = mapped_column(Boolean, default=False)
    social_engineering_detected: Mapped[bool] = mapped_column(Boolean, default=False)
    verification_triggered: Mapped[bool] = mapped_column(Boolean, default=False)

    # Recording
    is_recorded: Mapped[bool] = mapped_column(Boolean, default=False)
    recording_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    transcript_available: Mapped[bool] = mapped_column(Boolean, default=False)

    # Bot Information
    bot_joined: Mapped[bool] = mapped_column(Boolean, default=False)
    bot_joined_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    bot_left_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Extra data (platform-specific data)
    extra_data: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    # Relationships
    company: Mapped["Company"] = relationship("Company", back_populates="meetings")
    participants: Mapped[List["Participant"]] = relationship(
        "Participant",
        back_populates="meeting",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )
    incidents: Mapped[List["Incident"]] = relationship(
        "Incident",
        back_populates="meeting",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )
    risk_indicators: Mapped[List["RiskIndicator"]] = relationship(
        "RiskIndicator",
        back_populates="meeting",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )

    # Indexes
    __table_args__ = (
        Index("ix_meetings_company_status", "company_id", "status"),
        Index("ix_meetings_company_risk", "company_id", "risk_level"),
        Index("ix_meetings_platform", "platform", "platform_meeting_id"),
        Index("ix_meetings_scheduled", "scheduled_start_at"),
    )

    def __repr__(self) -> str:
        return f"<Meeting(id={self.id}, platform={self.platform}, risk={self.risk_level})>"

    def update_risk(self, score: float) -> None:
        """Update risk score and level."""
        self.risk_score = score

        # Update risk level based on thresholds
        if score < 30:
            self.risk_level = RiskLevel.LOW
        elif score < 60:
            self.risk_level = RiskLevel.MEDIUM
        elif score < 85:
            self.risk_level = RiskLevel.HIGH
        else:
            self.risk_level = RiskLevel.CRITICAL

        # Track peak risk
        if score > self.peak_risk_score:
            self.peak_risk_score = score
            self.peak_risk_at = datetime.utcnow()

    def start(self) -> None:
        """Mark meeting as started."""
        self.status = MeetingStatus.IN_PROGRESS
        self.actual_start_at = datetime.utcnow()

    def end(self) -> None:
        """Mark meeting as ended."""
        self.status = MeetingStatus.COMPLETED
        self.actual_end_at = datetime.utcnow()

    def cancel(self) -> None:
        """Mark meeting as cancelled."""
        self.status = MeetingStatus.CANCELLED

    @property
    def duration_minutes(self) -> Optional[int]:
        """Calculate meeting duration in minutes."""
        if self.actual_start_at and self.actual_end_at:
            delta = self.actual_end_at - self.actual_start_at
            return int(delta.total_seconds() / 60)
        return None

    @property
    def is_high_risk(self) -> bool:
        """Check if meeting is high or critical risk."""
        return self.risk_level in (RiskLevel.HIGH, RiskLevel.CRITICAL)
