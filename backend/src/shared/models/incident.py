"""
Incident Model

Represents security incidents detected during meetings.
"""

from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import (
    String,
    Float,
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
    from src.shared.models.meeting import Meeting
    from src.shared.models.participant import Participant
    from src.shared.models.verification import Verification


class IncidentStatus(str, Enum):
    """Incident lifecycle status."""

    DETECTED = "detected"
    INVESTIGATING = "investigating"
    VERIFIED = "verified"
    FALSE_POSITIVE = "false_positive"
    RESOLVED = "resolved"


class IncidentSeverity(str, Enum):
    """Incident severity levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class IncidentType(str, Enum):
    """Types of security incidents."""

    AUDIO_DEEPFAKE = "audio_deepfake"
    VIDEO_DEEPFAKE = "video_deepfake"
    SOCIAL_ENGINEERING = "social_engineering"
    IMPERSONATION = "impersonation"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    SUSPICIOUS_BEHAVIOR = "suspicious_behavior"
    VERIFICATION_FAILED = "verification_failed"
    POLICY_VIOLATION = "policy_violation"


class Incident(BaseModel):
    """
    Incident model representing a security event.

    Tracks the full lifecycle of detected security incidents.
    """

    __tablename__ = "incidents"

    # Associations
    meeting_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("meetings.id", ondelete="CASCADE"),
        nullable=False,
    )
    participant_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("participants.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Incident Classification
    incident_type: Mapped[IncidentType] = mapped_column(
        SQLEnum(IncidentType, name="incident_type"),
        nullable=False,
    )
    severity: Mapped[IncidentSeverity] = mapped_column(
        SQLEnum(IncidentSeverity, name="incident_severity"),
        default=IncidentSeverity.MEDIUM,
        nullable=False,
    )
    status: Mapped[IncidentStatus] = mapped_column(
        SQLEnum(IncidentStatus, name="incident_status"),
        default=IncidentStatus.DETECTED,
        nullable=False,
    )

    # Details
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    confidence_score: Mapped[float] = mapped_column(Float, default=0.0)

    # Detection Context
    detected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
    )
    meeting_timestamp_seconds: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
        comment="Timestamp within the meeting when incident was detected",
    )

    # Evidence
    evidence_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    evidence_references: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True,
        comment="References to MongoDB forensic evidence documents",
    )
    screenshot_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    audio_clip_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Resolution
    resolved_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    resolved_by_user_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False),
        nullable=True,
    )
    resolution_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Actions Taken
    actions_taken: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True,
        comment="List of automated and manual actions taken",
    )
    verification_triggered: Mapped[bool] = mapped_column(default=False)
    alert_sent: Mapped[bool] = mapped_column(default=False)
    alert_sent_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Analysis Details
    detection_method: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    detection_model: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    raw_analysis_data: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    # Relationships
    meeting: Mapped["Meeting"] = relationship("Meeting", back_populates="incidents")
    participant: Mapped[Optional["Participant"]] = relationship(
        "Participant",
        back_populates="incidents",
    )
    verifications: Mapped[List["Verification"]] = relationship(
        "Verification",
        back_populates="incident",
        lazy="dynamic",
    )

    # Indexes
    __table_args__ = (
        Index("ix_incidents_meeting", "meeting_id"),
        Index("ix_incidents_meeting_type", "meeting_id", "incident_type"),
        Index("ix_incidents_status_severity", "status", "severity"),
        Index("ix_incidents_detected_at", "detected_at"),
    )

    def __repr__(self) -> str:
        return f"<Incident(id={self.id}, type={self.incident_type}, status={self.status})>"

    def escalate(self, new_severity: IncidentSeverity) -> None:
        """Escalate incident to higher severity."""
        severity_order = [
            IncidentSeverity.LOW,
            IncidentSeverity.MEDIUM,
            IncidentSeverity.HIGH,
            IncidentSeverity.CRITICAL,
        ]
        current_idx = severity_order.index(self.severity)
        new_idx = severity_order.index(new_severity)

        if new_idx > current_idx:
            self.severity = new_severity

    def investigate(self) -> None:
        """Mark incident as under investigation."""
        self.status = IncidentStatus.INVESTIGATING

    def verify_incident(self) -> None:
        """Mark incident as verified (confirmed real threat)."""
        self.status = IncidentStatus.VERIFIED

    def mark_false_positive(self, notes: str, user_id: str) -> None:
        """Mark incident as false positive."""
        self.status = IncidentStatus.FALSE_POSITIVE
        self.resolved_at = datetime.utcnow()
        self.resolved_by_user_id = user_id
        self.resolution_notes = notes

    def resolve(self, notes: str, user_id: str) -> None:
        """Mark incident as resolved."""
        self.status = IncidentStatus.RESOLVED
        self.resolved_at = datetime.utcnow()
        self.resolved_by_user_id = user_id
        self.resolution_notes = notes

    def add_action(self, action: str, details: Optional[dict] = None) -> None:
        """Record an action taken for this incident."""
        if self.actions_taken is None:
            self.actions_taken = []

        self.actions_taken.append(
            {
                "action": action,
                "details": details,
                "timestamp": datetime.utcnow().isoformat(),
            }
        )

    @property
    def is_resolved(self) -> bool:
        """Check if incident is resolved."""
        return self.status in (IncidentStatus.RESOLVED, IncidentStatus.FALSE_POSITIVE)

    @property
    def is_active(self) -> bool:
        """Check if incident is still active."""
        return self.status in (IncidentStatus.DETECTED, IncidentStatus.INVESTIGATING)

    @property
    def requires_immediate_action(self) -> bool:
        """Check if incident requires immediate attention."""
        return (
            self.severity in (IncidentSeverity.HIGH, IncidentSeverity.CRITICAL)
            and self.is_active
        )
