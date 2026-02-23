"""
Participant Schemas

Request/response schemas for meeting participants.
"""

from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import Field

from src.shared.models.participant import ParticipantRole, TrustLevel
from src.shared.schemas.base import BaseSchema, TimestampSchema


class ParticipantBase(BaseSchema):
    """Base participant schema."""

    display_name: str = Field(min_length=1, max_length=255, description="Display name")
    email: Optional[str] = Field(default=None, max_length=255)
    phone_number: Optional[str] = Field(default=None, max_length=20)


class ParticipantCreate(ParticipantBase):
    """Schema for creating a participant record."""

    meeting_id: str = Field(description="Meeting ID")
    platform_participant_id: str = Field(
        min_length=1,
        max_length=255,
        description="Platform-specific participant ID",
    )
    platform_user_id: Optional[str] = Field(default=None, max_length=255)
    user_id: Optional[str] = Field(
        default=None,
        description="DeepSafe user ID if known",
    )
    role: ParticipantRole = Field(default=ParticipantRole.ATTENDEE)
    avatar_url: Optional[str] = Field(default=None, max_length=500)
    device_type: Optional[str] = Field(default=None, max_length=50)
    extra_data: Optional[Dict[str, Any]] = None


class ParticipantUpdate(BaseSchema):
    """Schema for updating participant information."""

    display_name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    role: Optional[ParticipantRole] = None
    trust_level: Optional[TrustLevel] = None
    is_flagged: Optional[bool] = None
    flag_reason: Optional[str] = Field(default=None, max_length=500)
    has_video: Optional[bool] = None
    has_audio: Optional[bool] = None
    is_screen_sharing: Optional[bool] = None
    connection_quality: Optional[str] = Field(default=None, max_length=50)


class ParticipantRiskUpdate(BaseSchema):
    """Schema for updating participant risk scores."""

    deepfake_confidence: Optional[float] = Field(default=None, ge=0, le=1)
    social_engineering_score: Optional[float] = Field(default=None, ge=0, le=1)


class ParticipantResponse(TimestampSchema):
    """Participant response schema."""

    id: str
    meeting_id: str
    user_id: Optional[str] = None
    display_name: str
    email: Optional[str] = None
    phone_number: Optional[str] = None
    avatar_url: Optional[str] = None
    platform_participant_id: str
    platform_user_id: Optional[str] = None
    role: ParticipantRole
    joined_at: Optional[datetime] = None
    left_at: Optional[datetime] = None
    is_active: bool
    trust_level: TrustLevel
    trust_score: float
    deepfake_confidence: float
    social_engineering_score: float
    composite_risk_score: float
    is_deepfake_suspect: bool
    is_social_engineering_suspect: bool
    is_flagged: bool
    flag_reason: Optional[str] = None
    is_verified: bool
    verified_at: Optional[datetime] = None
    verification_method: Optional[str] = None
    has_video: bool
    has_audio: bool
    is_screen_sharing: bool
    device_type: Optional[str] = None
    connection_quality: Optional[str] = None
    duration_minutes: Optional[int] = None


class ParticipantDetailResponse(ParticipantResponse):
    """Detailed participant response with history."""

    meeting_title: str
    meeting_platform: str
    company_id: str
    incident_count: int = 0
    verification_count: int = 0
    risk_indicator_count: int = 0


class ParticipantJoinEvent(BaseSchema):
    """Event when participant joins meeting."""

    platform_participant_id: str
    display_name: str
    email: Optional[str] = None
    role: ParticipantRole = ParticipantRole.ATTENDEE
    platform_user_id: Optional[str] = None
    avatar_url: Optional[str] = None
    device_type: Optional[str] = None
    joined_at: datetime


class ParticipantLeaveEvent(BaseSchema):
    """Event when participant leaves meeting."""

    platform_participant_id: str
    left_at: datetime
    reason: Optional[str] = Field(default=None, description="Leave reason if known")


class ParticipantMediaEvent(BaseSchema):
    """Event when participant's media status changes."""

    platform_participant_id: str
    has_video: bool
    has_audio: bool
    is_screen_sharing: bool
    timestamp: datetime


class TrustBadgeRequest(BaseSchema):
    """Request to display trust badge for participant."""

    participant_id: str
    badge_type: str = Field(
        description="verified, trusted, suspicious, unknown, flagged",
    )
    message: Optional[str] = Field(default=None, max_length=255)
    display_duration_seconds: int = Field(default=0, ge=0, description="0 = permanent")


class BlacklistParticipantRequest(BaseSchema):
    """Request to blacklist a participant."""

    reason: str = Field(min_length=1, max_length=500)
    block_email: bool = Field(
        default=True,
        description="Block this email across all meetings",
    )
    block_phone: bool = Field(
        default=False,
        description="Block this phone number across all meetings",
    )
