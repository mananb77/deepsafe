"""
Verification Engine

Orchestrates multi-channel verification based on risk level and transaction value.

Verification Matrix:
| Amount     | Risk      | Channels                          |
|------------|-----------|-----------------------------------|
| <$5K       | Any       | SMS only                          |
| $5-25K     | <60%      | SMS + email                       |
| $5-25K     | 61-85%    | SMS + push                        |
| $5-25K     | >85%      | SMS + callback + dual approval    |
| $25-100K   | Any       | Callback + push + dual approval   |
| >$100K     | Any       | All channels + 24h hold           |
"""

import asyncio
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Set
from uuid import UUID, uuid4

from src.services.verification.base import (
    BaseVerifier,
    VerificationChannel,
    VerificationConfig,
    VerificationRequest,
    VerificationResult,
    VerificationStatus,
    VerificationType,
    RiskTier,
    ChannelVerification,
    MultiChannelVerification,
    generate_verification_code,
    get_verification_channels_for_risk,
)
from src.services.verification.sms_verifier import SMSVerifier
from src.services.verification.voice_verifier import VoiceVerifier
from src.services.verification.push_verifier import PushVerifier
from src.services.verification.email_verifier import EmailVerifier


@dataclass
class VerificationSession:
    """Active verification session."""

    session_id: UUID
    request: VerificationRequest
    code: str
    channels: Dict[VerificationChannel, ChannelVerification]
    required_channels: List[VerificationChannel]
    status: VerificationStatus
    created_at: datetime
    expires_at: datetime
    requires_hold: bool = False
    hold_until: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def is_complete(self) -> bool:
        """Check if all required channels are verified."""
        for channel in self.required_channels:
            if channel not in self.channels:
                return False
            if self.channels[channel].status != VerificationStatus.VERIFIED:
                return False
        return True

    @property
    def is_expired(self) -> bool:
        """Check if session has expired."""
        return datetime.utcnow() > self.expires_at

    @property
    def is_held(self) -> bool:
        """Check if session is in hold period."""
        if not self.requires_hold or not self.hold_until:
            return False
        return datetime.utcnow() < self.hold_until

    @property
    def verified_count(self) -> int:
        """Count of verified channels."""
        return sum(
            1 for cv in self.channels.values()
            if cv.status == VerificationStatus.VERIFIED
        )

    @property
    def required_count(self) -> int:
        """Count of required channels."""
        return len(self.required_channels)


class VerificationEngine:
    """
    Multi-channel verification orchestration engine.

    Features:
    - Risk-based channel selection
    - Transaction value thresholds
    - Multi-channel verification
    - Hold periods for high-value transactions
    - Automatic fallback between providers
    - Rate limiting and attempt tracking
    """

    def __init__(
        self,
        config: Optional[VerificationConfig] = None,
        sms_verifier: Optional[SMSVerifier] = None,
        voice_verifier: Optional[VoiceVerifier] = None,
        push_verifier: Optional[PushVerifier] = None,
        email_verifier: Optional[EmailVerifier] = None,
    ):
        self.config = config or VerificationConfig()

        # Initialize verifiers
        self._verifiers: Dict[VerificationChannel, BaseVerifier] = {}

        if sms_verifier or self.config.sms_enabled:
            self._verifiers[VerificationChannel.SMS] = sms_verifier or SMSVerifier()

        if voice_verifier or self.config.voice_enabled:
            self._verifiers[VerificationChannel.VOICE] = voice_verifier or VoiceVerifier()

        if push_verifier or self.config.push_enabled:
            self._verifiers[VerificationChannel.PUSH] = push_verifier or PushVerifier()

        if email_verifier or self.config.email_enabled:
            self._verifiers[VerificationChannel.EMAIL] = email_verifier or EmailVerifier()

        # Active sessions (in production, use Redis)
        self._sessions: Dict[UUID, VerificationSession] = {}

        # Rate limiting (in production, use Redis)
        self._rate_limits: Dict[str, List[datetime]] = {}

    async def create_verification(
        self,
        request: VerificationRequest,
    ) -> VerificationSession:
        """
        Create and initiate a verification session.

        Args:
            request: Verification request with user and context info.

        Returns:
            VerificationSession with status and channel info.
        """
        # Check rate limits
        rate_key = f"{request.user_id}:{request.verification_type.value}"
        if not self._check_rate_limit(rate_key):
            raise ValueError("Rate limit exceeded. Please wait before requesting another code.")

        # Determine required channels
        if request.required_channels:
            channels = request.required_channels
            requires_hold = False
        else:
            channels, requires_hold = get_verification_channels_for_risk(
                request.risk_score,
                request.transaction_amount,
            )

        # Generate code
        code = generate_verification_code(
            length=request.code_length or self.config.code_length,
            numeric_only=self.config.code_numeric_only,
        )

        # Create session
        session_id = uuid4()
        now = datetime.utcnow()
        expiry_minutes = request.expiry_minutes or self.config.expiry_minutes

        session = VerificationSession(
            session_id=session_id,
            request=request,
            code=code,
            channels={},
            required_channels=channels,
            status=VerificationStatus.PENDING,
            created_at=now,
            expires_at=now + timedelta(minutes=expiry_minutes),
            requires_hold=requires_hold,
            hold_until=now + timedelta(hours=24) if requires_hold else None,
            metadata=request.metadata,
        )

        # Store session
        self._sessions[session_id] = session

        # Send verification to all required channels
        await self._send_to_channels(session)

        # Update rate limit
        self._record_rate_limit(rate_key)

        return session

    async def _send_to_channels(
        self,
        session: VerificationSession,
    ) -> None:
        """Send verification code to all required channels."""
        request = session.request
        expiry_minutes = request.expiry_minutes or self.config.expiry_minutes

        for channel in session.required_channels:
            if channel not in self._verifiers:
                # Skip unavailable channels
                session.channels[channel] = ChannelVerification(
                    channel=channel,
                    code=session.code,
                    status=VerificationStatus.FAILED,
                    error="Channel not available",
                )
                continue

            verifier = self._verifiers[channel]

            # Get recipient for this channel
            recipient = self._get_recipient(request, channel)
            if not recipient:
                session.channels[channel] = ChannelVerification(
                    channel=channel,
                    code=session.code,
                    status=VerificationStatus.FAILED,
                    error=f"No {channel.value} contact info provided",
                )
                continue

            # Send verification
            try:
                result = await verifier.send_code(
                    recipient=recipient,
                    code=session.code,
                    expiry_minutes=expiry_minutes,
                    metadata={
                        "session_id": str(session.session_id),
                        "user_id": str(request.user_id),
                        "verification_type": request.verification_type.value,
                    },
                )

                session.channels[channel] = ChannelVerification(
                    channel=channel,
                    code=session.code,
                    status=result.status,
                    sent_at=result.sent_at,
                    expires_at=result.expires_at,
                    provider_message_id=result.provider_message_id,
                    error=result.error,
                )

            except Exception as e:
                session.channels[channel] = ChannelVerification(
                    channel=channel,
                    code=session.code,
                    status=VerificationStatus.FAILED,
                    error=str(e),
                )

        # Update session status
        sent_count = sum(
            1 for cv in session.channels.values()
            if cv.status == VerificationStatus.SENT
        )

        if sent_count > 0:
            session.status = VerificationStatus.SENT
        else:
            session.status = VerificationStatus.FAILED

    def _get_recipient(
        self,
        request: VerificationRequest,
        channel: VerificationChannel,
    ) -> Optional[str]:
        """Get recipient address for a channel."""
        if channel == VerificationChannel.SMS:
            return request.phone_number
        elif channel == VerificationChannel.VOICE:
            return request.phone_number
        elif channel == VerificationChannel.PUSH:
            return request.device_token
        elif channel == VerificationChannel.EMAIL:
            return request.email
        return None

    async def verify_code(
        self,
        session_id: UUID,
        code: str,
        channel: Optional[VerificationChannel] = None,
    ) -> VerificationSession:
        """
        Verify a submitted code.

        Args:
            session_id: Verification session ID.
            code: Code submitted by user.
            channel: Specific channel being verified (optional).

        Returns:
            Updated VerificationSession.
        """
        session = self._sessions.get(session_id)
        if not session:
            raise ValueError("Verification session not found")

        if session.is_expired:
            session.status = VerificationStatus.EXPIRED
            raise ValueError("Verification session expired")

        # Normalize codes
        submitted = code.strip().upper()
        expected = session.code.strip().upper()

        # Check code
        if submitted != expected:
            # Track attempt
            for ch, cv in session.channels.items():
                if channel is None or ch == channel:
                    cv.attempts += 1

            # Check max attempts
            max_attempts = session.request.max_attempts or self.config.max_attempts_per_code
            total_attempts = sum(cv.attempts for cv in session.channels.values())

            if total_attempts >= max_attempts * len(session.channels):
                session.status = VerificationStatus.FAILED
                raise ValueError("Maximum verification attempts exceeded")

            raise ValueError("Invalid verification code")

        # Code is correct - mark channel(s) as verified
        now = datetime.utcnow()

        if channel:
            # Verify specific channel
            if channel in session.channels:
                session.channels[channel].status = VerificationStatus.VERIFIED
                session.channels[channel].verified_at = now
        else:
            # Verify all channels with the same code
            for ch, cv in session.channels.items():
                if cv.status == VerificationStatus.SENT:
                    cv.status = VerificationStatus.VERIFIED
                    cv.verified_at = now

        # Check if session is complete
        if session.is_complete:
            if session.is_held:
                session.status = VerificationStatus.PENDING  # Still in hold period
            else:
                session.status = VerificationStatus.VERIFIED

        return session

    async def resend_code(
        self,
        session_id: UUID,
        channel: Optional[VerificationChannel] = None,
    ) -> VerificationSession:
        """
        Resend verification code.

        Args:
            session_id: Verification session ID.
            channel: Specific channel to resend (optional, resends all if None).

        Returns:
            Updated VerificationSession.
        """
        session = self._sessions.get(session_id)
        if not session:
            raise ValueError("Verification session not found")

        if session.is_expired:
            raise ValueError("Verification session expired")

        # Check cooldown
        rate_key = f"resend:{session_id}"
        if not self._check_rate_limit(rate_key, max_per_hour=10):
            raise ValueError("Please wait before requesting another code")

        # Resend to specified channel or all channels
        channels_to_resend = [channel] if channel else session.required_channels

        for ch in channels_to_resend:
            if ch not in self._verifiers:
                continue

            if ch in session.channels:
                cv = session.channels[ch]
                if cv.status == VerificationStatus.VERIFIED:
                    continue  # Already verified, skip

            verifier = self._verifiers[ch]
            recipient = self._get_recipient(session.request, ch)

            if not recipient:
                continue

            try:
                result = await verifier.send_code(
                    recipient=recipient,
                    code=session.code,
                    expiry_minutes=self.config.expiry_minutes,
                )

                session.channels[ch] = ChannelVerification(
                    channel=ch,
                    code=session.code,
                    status=result.status,
                    sent_at=result.sent_at,
                    expires_at=result.expires_at,
                    provider_message_id=result.provider_message_id,
                    error=result.error,
                )

            except Exception as e:
                if ch in session.channels:
                    session.channels[ch].error = str(e)

        self._record_rate_limit(rate_key)

        return session

    async def cancel_verification(
        self,
        session_id: UUID,
    ) -> VerificationSession:
        """
        Cancel a verification session.

        Args:
            session_id: Verification session ID.

        Returns:
            Cancelled VerificationSession.
        """
        session = self._sessions.get(session_id)
        if not session:
            raise ValueError("Verification session not found")

        session.status = VerificationStatus.CANCELLED

        for cv in session.channels.values():
            if cv.status not in [VerificationStatus.VERIFIED, VerificationStatus.FAILED]:
                cv.status = VerificationStatus.CANCELLED

        return session

    def get_session(self, session_id: UUID) -> Optional[VerificationSession]:
        """Get verification session by ID."""
        return self._sessions.get(session_id)

    def get_session_status(self, session_id: UUID) -> Dict[str, Any]:
        """
        Get verification session status summary.

        Args:
            session_id: Verification session ID.

        Returns:
            Status summary dict.
        """
        session = self._sessions.get(session_id)
        if not session:
            return {"error": "Session not found"}

        return {
            "session_id": str(session.session_id),
            "status": session.status.value,
            "is_complete": session.is_complete,
            "is_expired": session.is_expired,
            "is_held": session.is_held,
            "verified_count": session.verified_count,
            "required_count": session.required_count,
            "channels": {
                ch.value: {
                    "status": cv.status.value,
                    "sent_at": cv.sent_at.isoformat() if cv.sent_at else None,
                    "verified_at": cv.verified_at.isoformat() if cv.verified_at else None,
                    "attempts": cv.attempts,
                }
                for ch, cv in session.channels.items()
            },
            "expires_at": session.expires_at.isoformat(),
            "hold_until": session.hold_until.isoformat() if session.hold_until else None,
        }

    def _check_rate_limit(
        self,
        key: str,
        max_per_hour: int = None,
    ) -> bool:
        """Check if action is within rate limits."""
        max_per_hour = max_per_hour or self.config.max_codes_per_hour
        now = datetime.utcnow()
        hour_ago = now - timedelta(hours=1)

        if key not in self._rate_limits:
            return True

        # Clean old entries
        self._rate_limits[key] = [
            ts for ts in self._rate_limits[key]
            if ts > hour_ago
        ]

        return len(self._rate_limits[key]) < max_per_hour

    def _record_rate_limit(self, key: str) -> None:
        """Record a rate limit event."""
        if key not in self._rate_limits:
            self._rate_limits[key] = []
        self._rate_limits[key].append(datetime.utcnow())

    async def get_available_channels(self) -> List[VerificationChannel]:
        """Get list of available verification channels."""
        available = []
        for channel, verifier in self._verifiers.items():
            if await verifier.is_available():
                available.append(channel)
        return available

    async def close(self) -> None:
        """Clean up resources."""
        for verifier in self._verifiers.values():
            await verifier.close()
