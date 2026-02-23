"""
Verification Service Base Types

Common types and interfaces for multi-channel verification.
"""

import secrets
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4


class VerificationChannel(Enum):
    """Verification channel types."""

    SMS = "sms"
    VOICE = "voice"
    PUSH = "push"
    EMAIL = "email"


class VerificationStatus(Enum):
    """Verification status states."""

    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    VERIFIED = "verified"
    FAILED = "failed"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class VerificationType(Enum):
    """Type of verification being performed."""

    IDENTITY = "identity"
    TRANSACTION = "transaction"
    ACTION = "action"
    LOGIN = "login"


class RiskTier(Enum):
    """Risk tier for verification requirements."""

    LOW = "low"  # 0-30%
    MEDIUM = "medium"  # 31-60%
    HIGH = "high"  # 61-85%
    CRITICAL = "critical"  # 86-100%


@dataclass
class VerificationRequest:
    """Request to initiate a verification."""

    # Required fields
    user_id: UUID
    verification_type: VerificationType

    # Contact info (at least one required)
    phone_number: Optional[str] = None
    email: Optional[str] = None
    device_token: Optional[str] = None  # For push notifications

    # Context
    meeting_id: Optional[UUID] = None
    participant_id: Optional[UUID] = None
    incident_id: Optional[UUID] = None

    # Transaction context (for financial verifications)
    transaction_amount: Optional[float] = None
    transaction_currency: str = "USD"
    transaction_description: Optional[str] = None

    # Risk context
    risk_score: float = 0.0
    risk_tier: RiskTier = RiskTier.LOW

    # Channel preferences
    preferred_channels: List[VerificationChannel] = field(default_factory=list)
    required_channels: List[VerificationChannel] = field(default_factory=list)

    # Configuration
    code_length: int = 6
    expiry_minutes: int = 10
    max_attempts: int = 3

    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    request_id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=datetime.utcnow)

    def get_required_channel_count(self) -> int:
        """Get number of channels that must succeed."""
        if self.required_channels:
            return len(self.required_channels)
        return 1  # Default: at least one channel must succeed


@dataclass
class VerificationResult:
    """Result from a verification attempt."""

    request_id: UUID
    channel: VerificationChannel
    status: VerificationStatus
    verified: bool

    # Timing
    sent_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    verified_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None

    # Attempt tracking
    attempts: int = 0
    max_attempts: int = 3

    # Provider info
    provider: Optional[str] = None
    provider_message_id: Optional[str] = None
    provider_status: Optional[str] = None

    # Error info
    error: Optional[str] = None
    error_code: Optional[str] = None

    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def is_expired(self) -> bool:
        """Check if verification has expired."""
        if not self.expires_at:
            return False
        return datetime.utcnow() > self.expires_at

    @property
    def can_retry(self) -> bool:
        """Check if verification can be retried."""
        return (
            self.attempts < self.max_attempts and
            not self.verified and
            not self.is_expired and
            self.status not in [VerificationStatus.CANCELLED, VerificationStatus.VERIFIED]
        )


@dataclass
class VerificationConfig:
    """Configuration for verification service."""

    # Code settings
    code_length: int = 6
    code_numeric_only: bool = True
    expiry_minutes: int = 10

    # Attempt limits
    max_attempts_per_code: int = 3
    max_codes_per_hour: int = 5
    cooldown_minutes: int = 1

    # Channel-specific settings
    sms_enabled: bool = True
    voice_enabled: bool = True
    push_enabled: bool = True
    email_enabled: bool = True

    # Provider settings
    twilio_account_sid: Optional[str] = None
    twilio_auth_token: Optional[str] = None
    twilio_phone_number: Optional[str] = None
    twilio_verify_service_sid: Optional[str] = None

    firebase_credentials_path: Optional[str] = None

    smtp_host: Optional[str] = None
    smtp_port: int = 587
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None
    smtp_from_email: Optional[str] = None

    # Message templates
    sms_template: str = "Your DeepSafe verification code is: {code}. Valid for {expiry} minutes."
    voice_template: str = "Your DeepSafe verification code is: {code}. I repeat: {code}."
    email_subject: str = "DeepSafe Verification Code"
    email_template: str = """
    Your DeepSafe verification code is: {code}

    This code is valid for {expiry} minutes.

    If you did not request this code, please ignore this message.
    """
    push_title: str = "DeepSafe Verification"
    push_body: str = "Tap to verify your identity. Code: {code}"


@dataclass
class ChannelVerification:
    """Tracking for a single channel verification."""

    channel: VerificationChannel
    code: str
    status: VerificationStatus
    sent_at: Optional[datetime] = None
    verified_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    attempts: int = 0
    provider_message_id: Optional[str] = None
    error: Optional[str] = None


@dataclass
class MultiChannelVerification:
    """Tracking for multi-channel verification."""

    request_id: UUID
    user_id: UUID
    verification_type: VerificationType
    channels: Dict[VerificationChannel, ChannelVerification]
    required_channels: List[VerificationChannel]
    overall_status: VerificationStatus
    created_at: datetime
    expires_at: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def is_complete(self) -> bool:
        """Check if all required channels are verified."""
        for channel in self.required_channels:
            if channel in self.channels:
                if self.channels[channel].status != VerificationStatus.VERIFIED:
                    return False
            else:
                return False
        return True

    @property
    def is_expired(self) -> bool:
        """Check if verification has expired."""
        return datetime.utcnow() > self.expires_at

    @property
    def verified_channels(self) -> List[VerificationChannel]:
        """Get list of verified channels."""
        return [
            channel for channel, cv in self.channels.items()
            if cv.status == VerificationStatus.VERIFIED
        ]


class BaseVerifier(ABC):
    """Base class for verification channel implementations."""

    @property
    @abstractmethod
    def channel(self) -> VerificationChannel:
        """Return the channel type."""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Return verifier name."""
        pass

    @abstractmethod
    async def is_available(self) -> bool:
        """Check if this verifier is available."""
        pass

    @abstractmethod
    async def send_code(
        self,
        recipient: str,
        code: str,
        expiry_minutes: int,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> VerificationResult:
        """
        Send verification code to recipient.

        Args:
            recipient: Phone number, email, or device token.
            code: Verification code to send.
            expiry_minutes: Code expiration time.
            metadata: Additional metadata.

        Returns:
            VerificationResult with send status.
        """
        pass

    @abstractmethod
    async def verify_code(
        self,
        recipient: str,
        code: str,
        expected_code: str,
    ) -> VerificationResult:
        """
        Verify a code submitted by user.

        Args:
            recipient: Phone number, email, or device token.
            code: Code submitted by user.
            expected_code: Expected correct code.

        Returns:
            VerificationResult with verification status.
        """
        pass

    async def close(self) -> None:
        """Clean up resources."""
        pass


def generate_verification_code(length: int = 6, numeric_only: bool = True) -> str:
    """
    Generate a secure verification code.

    Args:
        length: Code length (default 6).
        numeric_only: If True, only digits (default True).

    Returns:
        Generated code string.
    """
    if numeric_only:
        # Generate numeric code
        return ''.join(secrets.choice('0123456789') for _ in range(length))
    else:
        # Alphanumeric (uppercase only for readability)
        return ''.join(secrets.choice('0123456789ABCDEFGHJKLMNPQRSTUVWXYZ') for _ in range(length))


def get_verification_channels_for_risk(
    risk_score: float,
    transaction_amount: Optional[float] = None,
) -> tuple[List[VerificationChannel], bool]:
    """
    Determine required verification channels based on risk and transaction amount.

    Args:
        risk_score: Risk score 0-100.
        transaction_amount: Optional transaction amount in USD.

    Returns:
        Tuple of (required_channels, requires_hold).
    """
    requires_hold = False

    # Determine risk tier
    if risk_score >= 86:
        risk_tier = RiskTier.CRITICAL
    elif risk_score >= 61:
        risk_tier = RiskTier.HIGH
    elif risk_score >= 31:
        risk_tier = RiskTier.MEDIUM
    else:
        risk_tier = RiskTier.LOW

    # Base channels by risk
    channels = []

    # Transaction amount thresholds
    if transaction_amount:
        if transaction_amount >= 100000:
            # >$100K: All channels + 24h hold
            channels = [
                VerificationChannel.SMS,
                VerificationChannel.VOICE,
                VerificationChannel.PUSH,
                VerificationChannel.EMAIL,
            ]
            requires_hold = True

        elif transaction_amount >= 25000:
            # $25-100K: Callback + push + dual approval
            channels = [
                VerificationChannel.VOICE,
                VerificationChannel.PUSH,
            ]

        elif transaction_amount >= 5000:
            # $5-25K: Depends on risk
            if risk_tier == RiskTier.CRITICAL:
                channels = [
                    VerificationChannel.SMS,
                    VerificationChannel.VOICE,
                ]
            elif risk_tier == RiskTier.HIGH:
                channels = [
                    VerificationChannel.SMS,
                    VerificationChannel.PUSH,
                ]
            else:
                channels = [
                    VerificationChannel.SMS,
                    VerificationChannel.EMAIL,
                ]

        else:
            # <$5K: SMS only
            channels = [VerificationChannel.SMS]

    else:
        # No transaction amount - base on risk only
        if risk_tier == RiskTier.CRITICAL:
            channels = [
                VerificationChannel.SMS,
                VerificationChannel.VOICE,
                VerificationChannel.PUSH,
            ]
        elif risk_tier == RiskTier.HIGH:
            channels = [
                VerificationChannel.SMS,
                VerificationChannel.PUSH,
            ]
        elif risk_tier == RiskTier.MEDIUM:
            channels = [VerificationChannel.SMS]
        else:
            channels = [VerificationChannel.SMS]

    return channels, requires_hold
