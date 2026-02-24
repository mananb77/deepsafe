"""
Risk Indicator Model

Represents individual detection results and risk signals.
"""

from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Optional

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


class IndicatorType(str, Enum):
    """Types of risk indicators."""

    # Deepfake Detection
    AUDIO_DEEPFAKE = "audio_deepfake"
    VIDEO_DEEPFAKE = "video_deepfake"
    AV_SYNC_ANOMALY = "av_sync_anomaly"
    SPECTRAL_ANOMALY = "spectral_anomaly"
    FACIAL_ANOMALY = "facial_anomaly"
    VIRTUAL_CAMERA = "virtual_camera"

    # Social Engineering Detection
    SCENARIO_MATCH = "scenario_match"
    KEYWORD_DETECTION = "keyword_detection"
    GPT4_ANALYSIS = "gpt4_analysis"
    BEHAVIORAL_INDICATOR = "behavioral_indicator"

    # Participant Validation
    PARTICIPANT_MISMATCH = "participant_mismatch"
    METADATA_ANOMALY = "metadata_anomaly"
    IDENTITY_MISMATCH = "identity_mismatch"

    # Other
    CUSTOM = "custom"


class IndicatorSource(str, Enum):
    """Source of the risk indicator."""

    # External APIs
    RESEMBLE_AI = "resemble_ai"
    SENSITY = "sensity"
    OPENAI_GPT4 = "openai_gpt4"

    # Internal Models
    WAV2VEC = "wav2vec"
    EFFICIENTNET = "efficientnet"
    OLLAMA_LLM = "ollama_llm"
    WHISPER = "whisper"
    CUSTOM_MODEL = "custom_model"

    # Rule-based
    KEYWORD_RULES = "keyword_rules"
    BEHAVIORAL_RULES = "behavioral_rules"
    METADATA_ANALYSIS = "metadata_analysis"

    # Manual
    ANALYST = "analyst"


class RiskIndicator(BaseModel):
    """
    Risk Indicator model for detection results.

    Stores individual detection signals that contribute to overall risk scores.
    """

    __tablename__ = "risk_indicators"

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

    # Indicator Classification
    indicator_type: Mapped[IndicatorType] = mapped_column(
        SQLEnum(IndicatorType, name="indicator_type"),
        nullable=False,
    )
    source: Mapped[IndicatorSource] = mapped_column(
        SQLEnum(IndicatorSource, name="indicator_source"),
        nullable=False,
    )

    # Scores
    confidence: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        comment="Detection confidence score (0-1)",
    )
    weight: Mapped[float] = mapped_column(
        Float,
        default=1.0,
        comment="Weight in composite score calculation",
    )
    weighted_score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        comment="confidence * weight",
    )

    # Details
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Timing
    detected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
    )
    meeting_timestamp_seconds: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
        comment="Timestamp within the meeting",
    )

    # Raw Analysis Data
    raw_data: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True,
        comment="Raw output from detection model/API",
    )

    # Evidence References
    audio_segment_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    video_frame_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    transcript_segment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Model Information
    model_version: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    model_threshold: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Extra data
    extra_data: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    # Relationships
    meeting: Mapped["Meeting"] = relationship("Meeting", back_populates="risk_indicators")
    participant: Mapped[Optional["Participant"]] = relationship(
        "Participant",
        back_populates="risk_indicators",
    )

    # Indexes
    __table_args__ = (
        Index("ix_risk_indicators_meeting", "meeting_id"),
        Index("ix_risk_indicators_participant", "participant_id"),
        Index("ix_risk_indicators_type", "indicator_type"),
        Index("ix_risk_indicators_meeting_type", "meeting_id", "indicator_type"),
        Index("ix_risk_indicators_confidence", "confidence"),
        Index("ix_risk_indicators_detected", "detected_at"),
    )

    def __repr__(self) -> str:
        return f"<RiskIndicator(id={self.id}, type={self.indicator_type}, confidence={self.confidence})>"

    def __init__(self, **kwargs):
        """Initialize with automatic weighted_score calculation."""
        super().__init__(**kwargs)
        if "weighted_score" not in kwargs:
            self.weighted_score = self.confidence * self.weight

    def update_confidence(self, new_confidence: float) -> None:
        """Update confidence and recalculate weighted score."""
        self.confidence = new_confidence
        self.weighted_score = self.confidence * self.weight

    @property
    def is_high_confidence(self) -> bool:
        """Check if this is a high-confidence indicator."""
        return self.confidence >= 0.8

    @property
    def is_significant(self) -> bool:
        """Check if this indicator is significant (weighted score > 0.5)."""
        return self.weighted_score >= 0.5

    @classmethod
    def create_deepfake_indicator(
        cls,
        meeting_id: str,
        participant_id: str,
        indicator_type: IndicatorType,
        source: IndicatorSource,
        confidence: float,
        raw_data: dict,
        meeting_timestamp: Optional[float] = None,
    ) -> "RiskIndicator":
        """Factory method for creating deepfake indicators."""
        titles = {
            IndicatorType.AUDIO_DEEPFAKE: "Audio Deepfake Detected",
            IndicatorType.VIDEO_DEEPFAKE: "Video Deepfake Detected",
            IndicatorType.AV_SYNC_ANOMALY: "Audio-Video Sync Anomaly",
            IndicatorType.SPECTRAL_ANOMALY: "Audio Spectral Anomaly",
            IndicatorType.FACIAL_ANOMALY: "Facial Inconsistency Detected",
            IndicatorType.VIRTUAL_CAMERA: "Virtual Camera Detected",
        }

        return cls(
            meeting_id=meeting_id,
            participant_id=participant_id,
            indicator_type=indicator_type,
            source=source,
            confidence=confidence,
            weight=0.8,  # Higher weight for deepfake indicators
            title=titles.get(indicator_type, "Deepfake Indicator"),
            raw_data=raw_data,
            meeting_timestamp_seconds=meeting_timestamp,
        )

    @classmethod
    def create_social_engineering_indicator(
        cls,
        meeting_id: str,
        participant_id: Optional[str],
        indicator_type: IndicatorType,
        source: IndicatorSource,
        confidence: float,
        description: str,
        transcript_segment: Optional[str] = None,
        meeting_timestamp: Optional[float] = None,
    ) -> "RiskIndicator":
        """Factory method for creating social engineering indicators."""
        weights = {
            IndicatorType.SCENARIO_MATCH: 0.20,
            IndicatorType.KEYWORD_DETECTION: 0.20,
            IndicatorType.GPT4_ANALYSIS: 0.20,
            IndicatorType.BEHAVIORAL_INDICATOR: 0.15,
            IndicatorType.PARTICIPANT_MISMATCH: 0.15,
            IndicatorType.METADATA_ANOMALY: 0.10,
        }

        titles = {
            IndicatorType.SCENARIO_MATCH: "Social Engineering Pattern Match",
            IndicatorType.KEYWORD_DETECTION: "Suspicious Keywords Detected",
            IndicatorType.GPT4_ANALYSIS: "AI Analysis Alert",
            IndicatorType.BEHAVIORAL_INDICATOR: "Suspicious Behavior Pattern",
            IndicatorType.PARTICIPANT_MISMATCH: "Participant Identity Mismatch",
            IndicatorType.METADATA_ANOMALY: "Metadata Anomaly Detected",
        }

        return cls(
            meeting_id=meeting_id,
            participant_id=participant_id,
            indicator_type=indicator_type,
            source=source,
            confidence=confidence,
            weight=weights.get(indicator_type, 0.15),
            title=titles.get(indicator_type, "Social Engineering Indicator"),
            description=description,
            transcript_segment=transcript_segment,
            meeting_timestamp_seconds=meeting_timestamp,
        )
