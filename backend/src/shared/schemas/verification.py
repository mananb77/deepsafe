"""
Verification Schemas

Request/response schemas for identity verification.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import Field

from src.shared.models.verification import (
    VerificationChannel,
    VerificationStatus,
    VerificationType,
)
from src.shared.schemas.base import BaseSchema, PaginatedResponse, TimestampSchema


class VerificationCreate(BaseSchema):
    """Schema for initiating a verification."""

    participant_id: str = Field(description="Participant to verify")
    incident_id: Optional[str] = Field(
        default=None,
        description="Related incident (if applicable)",
    )
    verification_type: VerificationType = Field(default=VerificationType.IDENTITY)
    channel: VerificationChannel = Field(description="Verification channel")
    destination: str = Field(
        min_length=1,
        max_length=255,
        description="Phone number, email, or device token",
    )
    expires_in_minutes: int = Field(
        default=5,
        ge=1,
        le=60,
        description="Code expiration time",
    )
    max_attempts: int = Field(
        default=3,
        ge=1,
        le=10,
        description="Maximum verification attempts",
    )
    # Transaction context (for transaction verifications)
    transaction_amount: Optional[float] = Field(default=None, ge=0)
    transaction_description: Optional[str] = Field(default=None, max_length=500)


class VerificationCheck(BaseSchema):
    """Schema for checking/completing verification."""

    code: str = Field(
        min_length=4,
        max_length=10,
        description="Verification code",
    )


class VerificationResponse(TimestampSchema):
    """Verification response schema."""

    id: str
    participant_id: str
    incident_id: Optional[str] = None
    verification_type: VerificationType
    channel: VerificationChannel
    destination: str
    status: VerificationStatus
    initiated_at: datetime
    sent_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    verified_at: Optional[datetime] = None
    expires_at: datetime
    attempt_count: int
    max_attempts: int
    provider: str
    provider_status: Optional[str] = None
    failure_reason: Optional[str] = None
    transaction_amount: Optional[float] = None
    transaction_description: Optional[str] = None


class VerificationDetailResponse(VerificationResponse):
    """Detailed verification response."""

    participant_name: str
    participant_email: Optional[str] = None
    meeting_id: str
    meeting_title: str
    remaining_attempts: int
    is_expired: bool


class VerificationListResponse(PaginatedResponse[VerificationResponse]):
    """Paginated verification list response."""

    pass


class VerificationStatusUpdate(BaseSchema):
    """Webhook update for verification status."""

    verification_id: str
    provider_message_id: str
    status: str = Field(description="Provider-specific status")
    timestamp: datetime
    error_code: Optional[str] = None
    error_message: Optional[str] = None


class MultiChannelVerificationRequest(BaseSchema):
    """Request for multi-channel verification based on risk."""

    participant_id: str
    incident_id: Optional[str] = None
    risk_score: float = Field(ge=0, le=100)
    transaction_amount: Optional[float] = None
    channels: Optional[List[VerificationChannel]] = Field(
        default=None,
        description="Override automatic channel selection",
    )


class VerificationMatrixResponse(BaseSchema):
    """Response with verification requirements based on risk/amount."""

    risk_score: float
    transaction_amount: Optional[float]
    required_channels: List[VerificationChannel]
    requires_dual_approval: bool
    hold_period_hours: int = Field(
        default=0,
        description="Required hold period before proceeding",
    )
    explanation: str


class VerificationStatsResponse(BaseSchema):
    """Verification statistics."""

    total_verifications: int
    successful_verifications: int
    failed_verifications: int
    expired_verifications: int
    success_rate: float
    by_channel: Dict[str, int]
    by_type: Dict[str, int]
    average_verification_time_seconds: Optional[float] = None


class ResendVerificationRequest(BaseSchema):
    """Request to resend verification."""

    verification_id: str
    channel: Optional[VerificationChannel] = Field(
        default=None,
        description="Use different channel for resend",
    )
    new_destination: Optional[str] = Field(
        default=None,
        description="Use different destination (e.g., backup phone)",
    )


class VoiceVerificationConfig(BaseSchema):
    """Configuration for voice verification call."""

    language: str = Field(default="en-US")
    voice: str = Field(default="alice", description="Twilio voice")
    repeat_count: int = Field(default=2, ge=1, le=5)
    digit_pause_ms: int = Field(default=500, ge=100, le=2000)


class PushVerificationPayload(BaseSchema):
    """Push notification payload for verification."""

    title: str = Field(default="Identity Verification Required")
    body: str
    meeting_id: str
    meeting_title: str
    participant_name: str
    risk_level: str
    action_url: str
    require_biometric: bool = Field(
        default=False,
        description="Require biometric confirmation",
    )
