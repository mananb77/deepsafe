"""
Meeting Schemas

Request/response schemas for meeting management.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import Field, HttpUrl

from src.shared.models.meeting import MeetingPlatform, MeetingStatus, RiskLevel
from src.shared.schemas.base import BaseSchema, PaginatedResponse, TimestampSchema


class MeetingBase(BaseSchema):
    """Base meeting schema."""

    platform: MeetingPlatform = Field(description="Video conferencing platform")
    platform_meeting_id: str = Field(
        min_length=1,
        max_length=255,
        description="Platform-specific meeting ID",
    )
    title: str = Field(
        default="Untitled Meeting",
        max_length=500,
        description="Meeting title",
    )


class MeetingCreate(MeetingBase):
    """Schema for creating/registering a meeting."""

    platform_meeting_url: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Meeting URL",
    )
    description: Optional[str] = Field(default=None, description="Meeting description")
    host_email: Optional[str] = Field(default=None, max_length=255)
    scheduled_start_at: Optional[datetime] = Field(
        default=None,
        description="Scheduled start time",
    )
    scheduled_end_at: Optional[datetime] = Field(
        default=None,
        description="Scheduled end time",
    )
    extra_data: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Platform-specific extra data",
    )


class MeetingUpdate(BaseSchema):
    """Schema for updating meeting information."""

    title: Optional[str] = Field(default=None, max_length=500)
    description: Optional[str] = None
    scheduled_start_at: Optional[datetime] = None
    scheduled_end_at: Optional[datetime] = None
    status: Optional[MeetingStatus] = None
    is_recorded: Optional[bool] = None
    recording_url: Optional[str] = Field(default=None, max_length=500)


class MeetingRiskUpdate(BaseSchema):
    """Schema for updating meeting risk score."""

    risk_score: float = Field(ge=0, le=100, description="New risk score (0-100)")
    deepfake_detected: Optional[bool] = None
    social_engineering_detected: Optional[bool] = None
    verification_triggered: Optional[bool] = None


class ParticipantSummary(BaseSchema):
    """Brief participant info for meeting responses."""

    id: str
    display_name: str
    email: Optional[str] = None
    trust_level: str
    is_flagged: bool
    composite_risk_score: float


class MeetingResponse(TimestampSchema):
    """Meeting response schema."""

    id: str
    platform: MeetingPlatform
    platform_meeting_id: str
    platform_meeting_url: Optional[str] = None
    company_id: str
    title: str
    description: Optional[str] = None
    host_email: Optional[str] = None
    scheduled_start_at: Optional[datetime] = None
    scheduled_end_at: Optional[datetime] = None
    actual_start_at: Optional[datetime] = None
    actual_end_at: Optional[datetime] = None
    status: MeetingStatus
    participant_count: int
    max_participants: int
    risk_score: float
    risk_level: RiskLevel
    peak_risk_score: float
    peak_risk_at: Optional[datetime] = None
    deepfake_detected: bool
    social_engineering_detected: bool
    verification_triggered: bool
    is_recorded: bool
    recording_url: Optional[str] = None
    transcript_available: bool
    bot_joined: bool
    bot_joined_at: Optional[datetime] = None
    bot_left_at: Optional[datetime] = None
    duration_minutes: Optional[int] = None


class MeetingDetailResponse(MeetingResponse):
    """Detailed meeting response with participants."""

    participants: List[ParticipantSummary] = Field(default_factory=list)
    incident_count: int = 0
    risk_indicator_count: int = 0


class MeetingListResponse(PaginatedResponse[MeetingResponse]):
    """Paginated meeting list response."""

    pass


class MeetingStatsResponse(BaseSchema):
    """Meeting statistics for dashboard."""

    total_meetings: int
    active_meetings: int
    completed_meetings: int
    high_risk_meetings: int
    average_risk_score: float
    total_participants: int
    deepfake_detections: int
    social_engineering_detections: int
    verifications_triggered: int


class WebhookMeetingEvent(BaseSchema):
    """Webhook event for meeting updates."""

    platform: MeetingPlatform
    platform_meeting_id: str
    event_type: str = Field(description="started, ended, participant_joined, etc.")
    timestamp: datetime
    payload: Dict[str, Any]


class MeetingTranscriptSegment(BaseSchema):
    """Transcript segment from MongoDB."""

    id: str
    participant_id: str
    participant_name: str
    text: str
    timestamp: float
    risk_indicators: Optional[Dict[str, Any]] = None


class MeetingTranscriptResponse(BaseSchema):
    """Meeting transcript response."""

    meeting_id: str
    segments: List[MeetingTranscriptSegment]
    total_segments: int
    has_more: bool


class BotJoinRequest(BaseSchema):
    """Request to join meeting with bot."""

    meeting_url: str = Field(description="Meeting URL to join")
    bot_name: str = Field(default="DeepSafe Monitor", max_length=100)
    enable_audio: bool = Field(default=True)
    enable_video: bool = Field(default=False)


class BotLeaveRequest(BaseSchema):
    """Request to remove bot from meeting."""

    reason: Optional[str] = Field(default=None, max_length=255)
