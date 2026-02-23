"""
Risk Assessment Schemas

Request/response schemas for risk indicators and scoring.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import Field

from src.shared.models.risk_indicator import IndicatorSource, IndicatorType
from src.shared.schemas.base import BaseSchema, PaginatedResponse, TimestampSchema


class RiskIndicatorCreate(BaseSchema):
    """Schema for creating a risk indicator."""

    meeting_id: str
    participant_id: Optional[str] = None
    indicator_type: IndicatorType
    source: IndicatorSource
    confidence: float = Field(ge=0, le=1, description="Detection confidence")
    weight: float = Field(default=1.0, ge=0, le=1, description="Weight in scoring")
    title: str = Field(min_length=1, max_length=255)
    description: Optional[str] = None
    meeting_timestamp_seconds: Optional[float] = None
    raw_data: Optional[Dict[str, Any]] = None
    audio_segment_url: Optional[str] = Field(default=None, max_length=500)
    video_frame_url: Optional[str] = Field(default=None, max_length=500)
    transcript_segment: Optional[str] = None
    model_version: Optional[str] = Field(default=None, max_length=50)


class RiskIndicatorResponse(TimestampSchema):
    """Risk indicator response schema."""

    id: str
    meeting_id: str
    participant_id: Optional[str] = None
    indicator_type: IndicatorType
    source: IndicatorSource
    confidence: float
    weight: float
    weighted_score: float
    title: str
    description: Optional[str] = None
    detected_at: datetime
    meeting_timestamp_seconds: Optional[float] = None
    audio_segment_url: Optional[str] = None
    video_frame_url: Optional[str] = None
    transcript_segment: Optional[str] = None
    model_version: Optional[str] = None
    model_threshold: Optional[float] = None


class RiskIndicatorDetailResponse(RiskIndicatorResponse):
    """Detailed risk indicator with raw data."""

    raw_data: Optional[Dict[str, Any]] = None
    meeting_title: str
    participant_name: Optional[str] = None


class RiskIndicatorListResponse(PaginatedResponse[RiskIndicatorResponse]):
    """Paginated risk indicator list."""

    pass


class RiskScoreComponent(BaseSchema):
    """Component of composite risk score."""

    category: str = Field(description="deepfake, social_engineering, etc.")
    score: float = Field(ge=0, le=1)
    weight: float = Field(ge=0, le=1)
    weighted_score: float
    indicator_count: int
    top_indicators: List[str] = Field(description="Top contributing indicators")


class RiskScoreResponse(BaseSchema):
    """Composite risk score response."""

    meeting_id: str
    participant_id: Optional[str] = None
    composite_score: float = Field(ge=0, le=100)
    risk_level: str = Field(description="low, medium, high, critical")
    components: List[RiskScoreComponent]
    timestamp: datetime
    trend: str = Field(description="increasing, decreasing, stable")
    recommended_actions: List[str]


class RealTimeRiskUpdate(BaseSchema):
    """Real-time risk update for WebSocket."""

    meeting_id: str
    participant_id: Optional[str] = None
    composite_score: float
    risk_level: str
    delta: float = Field(description="Change from previous score")
    triggering_indicator: Optional[RiskIndicatorResponse] = None
    timestamp: datetime


class DeepfakeDetectionResult(BaseSchema):
    """Result from deepfake detection."""

    is_deepfake: bool
    confidence: float = Field(ge=0, le=1)
    detection_type: str = Field(description="audio, video, or both")
    indicators: List[Dict[str, Any]]
    model_used: str
    processing_time_ms: int
    audio_analysis: Optional[Dict[str, Any]] = None
    video_analysis: Optional[Dict[str, Any]] = None
    av_sync_offset_ms: Optional[int] = None


class SocialEngineeringResult(BaseSchema):
    """Result from social engineering detection."""

    risk_score: float = Field(ge=0, le=1)
    components: Dict[str, float] = Field(
        description="Score breakdown by component",
    )
    detected_patterns: List[str]
    suspicious_keywords: List[str]
    behavioral_flags: List[str]
    gpt4_analysis: Optional[str] = None
    transcript_highlights: List[Dict[str, Any]] = Field(
        description="Flagged transcript segments",
    )


class RiskThresholdConfig(BaseSchema):
    """Risk threshold configuration."""

    low_max: int = Field(default=30, ge=0, le=100)
    medium_max: int = Field(default=60, ge=0, le=100)
    high_max: int = Field(default=85, ge=0, le=100)
    # Anything above high_max is critical


class RiskWeightConfig(BaseSchema):
    """Risk scoring weight configuration."""

    # Deepfake weights
    audio_deepfake: float = Field(default=0.35, ge=0, le=1)
    video_deepfake: float = Field(default=0.35, ge=0, le=1)
    av_sync: float = Field(default=0.15, ge=0, le=1)
    virtual_camera: float = Field(default=0.15, ge=0, le=1)

    # Social engineering weights (from 6-metric system)
    scenario_match: float = Field(default=0.20, ge=0, le=1)
    keyword_detection: float = Field(default=0.20, ge=0, le=1)
    gpt4_analysis: float = Field(default=0.20, ge=0, le=1)
    participant_mismatch: float = Field(default=0.15, ge=0, le=1)
    metadata_anomaly: float = Field(default=0.10, ge=0, le=1)
    behavioral_indicator: float = Field(default=0.15, ge=0, le=1)


class RiskDashboardResponse(BaseSchema):
    """Risk dashboard data."""

    period: str = Field(description="day, week, month")
    total_meetings: int
    high_risk_meetings: int
    critical_risk_meetings: int
    average_risk_score: float
    risk_trend: List[Dict[str, Any]] = Field(
        description="Risk scores over time",
    )
    top_risk_categories: List[Dict[str, Any]]
    detection_breakdown: Dict[str, int]
    false_positive_rate: float


class AlertConfig(BaseSchema):
    """Alert configuration for risk thresholds."""

    alert_type: str = Field(description="popup, notification, email, sms")
    threshold: float = Field(ge=0, le=100)
    message: str
    recipients: List[str] = Field(default_factory=list)
    cooldown_minutes: int = Field(default=5, ge=0)
    include_evidence: bool = Field(default=True)


class AlertTriggerResponse(BaseSchema):
    """Response when alert is triggered."""

    alert_id: str
    meeting_id: str
    participant_id: Optional[str] = None
    risk_score: float
    risk_level: str
    alert_type: str
    message: str
    triggered_at: datetime
    recipients_notified: List[str]
