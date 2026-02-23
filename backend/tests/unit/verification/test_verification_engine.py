"""
Unit tests for verification engine (orchestration).
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from src.services.verification.base import (
    VerificationChannel,
    VerificationConfig,
    VerificationRequest,
    VerificationResult,
    VerificationStatus,
    VerificationType,
    RiskTier,
    get_verification_channels_for_risk,
    generate_verification_code,
)
from src.services.verification.verification_engine import (
    VerificationEngine,
    VerificationSession,
)
from src.services.verification.sms_verifier import SMSVerifier
from src.services.verification.voice_verifier import VoiceVerifier
from src.services.verification.push_verifier import PushVerifier
from src.services.verification.email_verifier import EmailVerifier


class TestVerificationCodeGeneration:
    """Tests for verification code generation."""

    def test_generate_numeric_code(self):
        """Should generate numeric-only code."""
        code = generate_verification_code(length=6, numeric_only=True)
        assert len(code) == 6
        assert code.isdigit()

    def test_generate_alphanumeric_code(self):
        """Should generate alphanumeric code."""
        code = generate_verification_code(length=6, numeric_only=False)
        assert len(code) == 6
        assert code.isalnum()

    def test_generate_different_lengths(self):
        """Should generate codes of specified length."""
        for length in [4, 6, 8]:
            code = generate_verification_code(length=length, numeric_only=True)
            assert len(code) == length

    def test_generate_unique_codes(self):
        """Should generate unique codes."""
        codes = [generate_verification_code() for _ in range(100)]
        # With 6-digit codes, collision is very unlikely
        assert len(set(codes)) > 95  # Allow for rare collisions


class TestVerificationChannelSelection:
    """Tests for risk-based channel selection."""

    def test_low_amount_low_risk(self):
        """<$5K should use SMS only."""
        channels, hold = get_verification_channels_for_risk(
            risk_score=25.0,
            transaction_amount=1000.0,
        )
        assert channels == [VerificationChannel.SMS]
        assert hold is False

    def test_medium_amount_low_risk(self):
        """$5-25K with <60% risk should use SMS + email."""
        channels, hold = get_verification_channels_for_risk(
            risk_score=50.0,
            transaction_amount=15000.0,
        )
        assert VerificationChannel.SMS in channels
        assert VerificationChannel.EMAIL in channels
        assert hold is False

    def test_medium_amount_medium_risk(self):
        """$5-25K with 60-85% risk should use SMS + push."""
        channels, hold = get_verification_channels_for_risk(
            risk_score=70.0,
            transaction_amount=15000.0,
        )
        assert VerificationChannel.SMS in channels
        assert VerificationChannel.PUSH in channels
        assert hold is False

    def test_medium_amount_high_risk(self):
        """$5-25K with >85% risk should use SMS + callback + dual approval."""
        channels, hold = get_verification_channels_for_risk(
            risk_score=90.0,
            transaction_amount=15000.0,
        )
        assert VerificationChannel.SMS in channels
        assert VerificationChannel.VOICE in channels
        assert hold is False

    def test_high_amount(self):
        """$25-100K should use callback + push + dual approval."""
        channels, hold = get_verification_channels_for_risk(
            risk_score=50.0,
            transaction_amount=50000.0,
        )
        assert VerificationChannel.VOICE in channels
        assert VerificationChannel.PUSH in channels
        assert hold is False

    def test_very_high_amount(self):
        """>$100K should use all channels + 24h hold."""
        channels, hold = get_verification_channels_for_risk(
            risk_score=50.0,
            transaction_amount=150000.0,
        )
        assert VerificationChannel.SMS in channels
        assert VerificationChannel.VOICE in channels
        assert VerificationChannel.PUSH in channels
        assert VerificationChannel.EMAIL in channels
        assert hold is True


class TestVerificationSession:
    """Tests for VerificationSession dataclass."""

    @pytest.fixture
    def sample_session(self, low_risk_request):
        """Create a sample verification session."""
        return VerificationSession(
            session_id=uuid4(),
            request=low_risk_request,
            code="123456",
            channels={},
            required_channels=[VerificationChannel.SMS],
            status=VerificationStatus.PENDING,
            created_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(minutes=10),
        )

    def test_is_complete_empty_channels(self, sample_session):
        """Session should not be complete with empty channels."""
        assert sample_session.is_complete is False

    def test_is_complete_pending_channel(self, sample_session):
        """Session should not be complete with pending channel."""
        from src.services.verification.base import ChannelVerification

        sample_session.channels[VerificationChannel.SMS] = ChannelVerification(
            channel=VerificationChannel.SMS,
            code="123456",
            status=VerificationStatus.SENT,
        )
        assert sample_session.is_complete is False

    def test_is_complete_verified_channel(self, sample_session):
        """Session should be complete when all required channels verified."""
        from src.services.verification.base import ChannelVerification

        sample_session.channels[VerificationChannel.SMS] = ChannelVerification(
            channel=VerificationChannel.SMS,
            code="123456",
            status=VerificationStatus.VERIFIED,
        )
        assert sample_session.is_complete is True

    def test_is_expired_future(self, sample_session):
        """Session should not be expired when expires_at is in future."""
        sample_session.expires_at = datetime.utcnow() + timedelta(minutes=10)
        assert sample_session.is_expired is False

    def test_is_expired_past(self, sample_session):
        """Session should be expired when expires_at is in past."""
        sample_session.expires_at = datetime.utcnow() - timedelta(minutes=1)
        assert sample_session.is_expired is True

    def test_is_held_no_hold(self, sample_session):
        """Session should not be held when requires_hold is False."""
        sample_session.requires_hold = False
        assert sample_session.is_held is False

    def test_is_held_active(self, sample_session):
        """Session should be held when hold_until is in future."""
        sample_session.requires_hold = True
        sample_session.hold_until = datetime.utcnow() + timedelta(hours=24)
        assert sample_session.is_held is True

    def test_is_held_expired(self, sample_session):
        """Session should not be held when hold_until is in past."""
        sample_session.requires_hold = True
        sample_session.hold_until = datetime.utcnow() - timedelta(hours=1)
        assert sample_session.is_held is False

    def test_verified_count(self, sample_session):
        """Should count verified channels."""
        from src.services.verification.base import ChannelVerification

        sample_session.required_channels = [
            VerificationChannel.SMS,
            VerificationChannel.EMAIL,
        ]
        sample_session.channels[VerificationChannel.SMS] = ChannelVerification(
            channel=VerificationChannel.SMS,
            code="123456",
            status=VerificationStatus.VERIFIED,
        )
        sample_session.channels[VerificationChannel.EMAIL] = ChannelVerification(
            channel=VerificationChannel.EMAIL,
            code="123456",
            status=VerificationStatus.SENT,
        )

        assert sample_session.verified_count == 1
        assert sample_session.required_count == 2


class TestVerificationEngine:
    """Tests for VerificationEngine."""

    @pytest.fixture
    def mock_verifiers(self, mock_sms_provider, mock_voice_provider, mock_push_provider, mock_email_provider):
        """Create mock verifiers for all channels."""
        sms = SMSVerifier(provider=mock_sms_provider)
        voice = VoiceVerifier(provider=mock_voice_provider)
        push = PushVerifier(provider=mock_push_provider)
        email = EmailVerifier(provider=mock_email_provider)
        return sms, voice, push, email

    @pytest.fixture
    def engine(self, mock_verifiers):
        """Create verification engine with mock verifiers."""
        sms, voice, push, email = mock_verifiers
        return VerificationEngine(
            sms_verifier=sms,
            voice_verifier=voice,
            push_verifier=push,
            email_verifier=email,
        )

    @pytest.mark.asyncio
    async def test_create_verification_low_risk(self, engine, low_risk_request):
        """Should create verification for low risk request."""
        session = await engine.create_verification(low_risk_request)

        assert session.status == VerificationStatus.SENT
        assert session.code is not None
        assert len(session.code) == 6
        assert VerificationChannel.SMS in session.required_channels

    @pytest.mark.asyncio
    async def test_create_verification_stores_session(self, engine, low_risk_request):
        """Should store session in engine."""
        session = await engine.create_verification(low_risk_request)

        stored = engine.get_session(session.session_id)
        assert stored is not None
        assert stored.session_id == session.session_id

    @pytest.mark.asyncio
    async def test_create_verification_custom_channels(self, engine, low_risk_request):
        """Should use custom channels when specified."""
        low_risk_request.required_channels = [
            VerificationChannel.SMS,
            VerificationChannel.EMAIL,
        ]

        session = await engine.create_verification(low_risk_request)

        assert VerificationChannel.SMS in session.required_channels
        assert VerificationChannel.EMAIL in session.required_channels

    @pytest.mark.asyncio
    async def test_verify_code_correct(self, engine, low_risk_request):
        """Should verify correct code."""
        session = await engine.create_verification(low_risk_request)
        code = session.code

        verified = await engine.verify_code(session.session_id, code)

        assert verified.status == VerificationStatus.VERIFIED
        assert verified.is_complete is True

    @pytest.mark.asyncio
    async def test_verify_code_incorrect(self, engine, low_risk_request):
        """Should reject incorrect code."""
        session = await engine.create_verification(low_risk_request)

        with pytest.raises(ValueError, match="Invalid verification code"):
            await engine.verify_code(session.session_id, "000000")

    @pytest.mark.asyncio
    async def test_verify_code_expired_session(self, engine, low_risk_request):
        """Should reject verification for expired session."""
        session = await engine.create_verification(low_risk_request)
        session.expires_at = datetime.utcnow() - timedelta(minutes=1)

        with pytest.raises(ValueError, match="expired"):
            await engine.verify_code(session.session_id, session.code)

    @pytest.mark.asyncio
    async def test_verify_code_not_found(self, engine):
        """Should raise error for non-existent session."""
        with pytest.raises(ValueError, match="not found"):
            await engine.verify_code(uuid4(), "123456")

    @pytest.mark.asyncio
    async def test_verify_code_max_attempts(self, engine, low_risk_request):
        """Should fail after max attempts exceeded."""
        # Use config with low max attempts
        engine.config.max_attempts_per_code = 2

        session = await engine.create_verification(low_risk_request)

        # First wrong attempt
        with pytest.raises(ValueError, match="Invalid"):
            await engine.verify_code(session.session_id, "000000")

        # Second wrong attempt
        with pytest.raises(ValueError, match="Invalid"):
            await engine.verify_code(session.session_id, "000001")

        # Third attempt should fail with max attempts error
        with pytest.raises(ValueError, match="Maximum verification attempts"):
            await engine.verify_code(session.session_id, "000002")

    @pytest.mark.asyncio
    async def test_resend_code(self, engine, low_risk_request):
        """Should resend verification code."""
        session = await engine.create_verification(low_risk_request)

        resent = await engine.resend_code(session.session_id)

        assert resent.session_id == session.session_id
        # Code should be the same
        assert resent.code == session.code

    @pytest.mark.asyncio
    async def test_resend_code_expired_session(self, engine, low_risk_request):
        """Should reject resend for expired session."""
        session = await engine.create_verification(low_risk_request)
        session.expires_at = datetime.utcnow() - timedelta(minutes=1)

        with pytest.raises(ValueError, match="expired"):
            await engine.resend_code(session.session_id)

    @pytest.mark.asyncio
    async def test_cancel_verification(self, engine, low_risk_request):
        """Should cancel verification session."""
        session = await engine.create_verification(low_risk_request)

        cancelled = await engine.cancel_verification(session.session_id)

        assert cancelled.status == VerificationStatus.CANCELLED

    @pytest.mark.asyncio
    async def test_get_session_status(self, engine, low_risk_request):
        """Should return session status summary."""
        session = await engine.create_verification(low_risk_request)

        status = engine.get_session_status(session.session_id)

        assert status["session_id"] == str(session.session_id)
        assert status["status"] == VerificationStatus.SENT.value
        assert "is_complete" in status
        assert "is_expired" in status
        assert "channels" in status

    def test_get_session_status_not_found(self, engine):
        """Should return error for non-existent session."""
        status = engine.get_session_status(uuid4())
        assert "error" in status

    @pytest.mark.asyncio
    async def test_get_available_channels(self, engine):
        """Should return list of available channels."""
        channels = await engine.get_available_channels()

        assert isinstance(channels, list)
        # All mock providers are available
        assert len(channels) > 0


class TestRateLimiting:
    """Tests for rate limiting."""

    @pytest.mark.asyncio
    async def test_rate_limit_enforcement(
        self,
        mock_sms_provider,
        mock_voice_provider,
        mock_push_provider,
        mock_email_provider,
        low_risk_request,
    ):
        """Should enforce rate limits."""
        sms = SMSVerifier(provider=mock_sms_provider)
        voice = VoiceVerifier(provider=mock_voice_provider)
        push = PushVerifier(provider=mock_push_provider)
        email = EmailVerifier(provider=mock_email_provider)

        config = VerificationConfig(max_codes_per_hour=2)
        engine = VerificationEngine(
            config=config,
            sms_verifier=sms,
            voice_verifier=voice,
            push_verifier=push,
            email_verifier=email,
        )

        # First request should succeed
        await engine.create_verification(low_risk_request)

        # Second request should succeed
        await engine.create_verification(low_risk_request)

        # Third request should be rate limited
        with pytest.raises(ValueError, match="Rate limit exceeded"):
            await engine.create_verification(low_risk_request)


class TestHighValueTransactions:
    """Tests for high-value transaction handling."""

    @pytest.mark.asyncio
    async def test_high_value_requires_hold(
        self,
        mock_sms_provider,
        mock_voice_provider,
        mock_push_provider,
        mock_email_provider,
        critical_risk_request,
    ):
        """High value transactions should require hold period."""
        sms = SMSVerifier(provider=mock_sms_provider)
        voice = VoiceVerifier(provider=mock_voice_provider)
        push = PushVerifier(provider=mock_push_provider)
        email = EmailVerifier(provider=mock_email_provider)

        engine = VerificationEngine(
            sms_verifier=sms,
            voice_verifier=voice,
            push_verifier=push,
            email_verifier=email,
        )

        session = await engine.create_verification(critical_risk_request)

        assert session.requires_hold is True
        assert session.hold_until is not None

    @pytest.mark.asyncio
    async def test_hold_period_blocks_completion(
        self,
        mock_sms_provider,
        mock_voice_provider,
        mock_push_provider,
        mock_email_provider,
        critical_risk_request,
    ):
        """Session should remain pending during hold period."""
        sms = SMSVerifier(provider=mock_sms_provider)
        voice = VoiceVerifier(provider=mock_voice_provider)
        push = PushVerifier(provider=mock_push_provider)
        email = EmailVerifier(provider=mock_email_provider)

        engine = VerificationEngine(
            sms_verifier=sms,
            voice_verifier=voice,
            push_verifier=push,
            email_verifier=email,
        )

        session = await engine.create_verification(critical_risk_request)
        code = session.code

        # Verify the code
        verified = await engine.verify_code(session.session_id, code)

        # Should be verified but still pending due to hold
        assert verified.is_held is True
        # Status should be PENDING, not VERIFIED
        assert verified.status == VerificationStatus.PENDING


class TestMultiChannelVerification:
    """Tests for multi-channel verification scenarios."""

    @pytest.mark.asyncio
    async def test_multi_channel_all_sent(
        self,
        mock_sms_provider,
        mock_voice_provider,
        mock_push_provider,
        mock_email_provider,
        high_risk_request,
    ):
        """Should send to multiple channels."""
        sms = SMSVerifier(provider=mock_sms_provider)
        voice = VoiceVerifier(provider=mock_voice_provider)
        push = PushVerifier(provider=mock_push_provider)
        email = EmailVerifier(provider=mock_email_provider)

        engine = VerificationEngine(
            sms_verifier=sms,
            voice_verifier=voice,
            push_verifier=push,
            email_verifier=email,
        )

        session = await engine.create_verification(high_risk_request)

        # Should have multiple channels
        assert len(session.required_channels) > 1
        # All channels should have been attempted
        assert len(session.channels) == len(session.required_channels)

    @pytest.mark.asyncio
    async def test_multi_channel_partial_failure(
        self, mock_sms_provider, mock_voice_provider, mock_push_provider, mock_email_provider, high_risk_request
    ):
        """Should handle partial channel failures."""
        # Make voice provider fail
        mock_voice_provider.make_call = AsyncMock(return_value={
            "success": False,
            "error": "Call failed",
        })

        sms = SMSVerifier(provider=mock_sms_provider)
        voice = VoiceVerifier(provider=mock_voice_provider)
        push = PushVerifier(provider=mock_push_provider)
        email = EmailVerifier(provider=mock_email_provider)

        engine = VerificationEngine(
            sms_verifier=sms,
            voice_verifier=voice,
            push_verifier=push,
            email_verifier=email,
        )

        session = await engine.create_verification(high_risk_request)

        # Session should still be sent (at least one channel succeeded)
        assert session.status == VerificationStatus.SENT

    @pytest.mark.asyncio
    async def test_verify_specific_channel(
        self,
        mock_sms_provider,
        mock_voice_provider,
        mock_push_provider,
        mock_email_provider,
        medium_risk_request,
    ):
        """Should verify specific channel only."""
        sms = SMSVerifier(provider=mock_sms_provider)
        voice = VoiceVerifier(provider=mock_voice_provider)
        push = PushVerifier(provider=mock_push_provider)
        email = EmailVerifier(provider=mock_email_provider)

        engine = VerificationEngine(
            sms_verifier=sms,
            voice_verifier=voice,
            push_verifier=push,
            email_verifier=email,
        )

        session = await engine.create_verification(medium_risk_request)
        code = session.code

        # Verify SMS channel specifically
        verified = await engine.verify_code(
            session.session_id,
            code,
            channel=VerificationChannel.SMS,
        )

        # SMS should be verified
        assert verified.channels[VerificationChannel.SMS].status == VerificationStatus.VERIFIED


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    @pytest.mark.asyncio
    async def test_missing_contact_info(
        self,
        mock_sms_provider,
        mock_voice_provider,
        mock_push_provider,
        mock_email_provider,
        sample_user_id,
    ):
        """Should handle missing contact information."""
        sms = SMSVerifier(provider=mock_sms_provider)
        voice = VoiceVerifier(provider=mock_voice_provider)
        push = PushVerifier(provider=mock_push_provider)
        email = EmailVerifier(provider=mock_email_provider)

        engine = VerificationEngine(
            sms_verifier=sms,
            voice_verifier=voice,
            push_verifier=push,
            email_verifier=email,
        )

        request = VerificationRequest(
            user_id=sample_user_id,
            phone_number=None,  # Missing phone
            email=None,  # Missing email
            verification_type=VerificationType.TRANSACTION,
            risk_score=25.0,
            transaction_amount=1000.0,
        )

        session = await engine.create_verification(request)

        # Channel should fail due to missing contact info
        sms_channel = session.channels.get(VerificationChannel.SMS)
        assert sms_channel is not None
        assert sms_channel.status == VerificationStatus.FAILED

    @pytest.mark.asyncio
    async def test_case_insensitive_code_verification(
        self,
        mock_sms_provider,
        mock_voice_provider,
        mock_push_provider,
        mock_email_provider,
        low_risk_request,
    ):
        """Should verify codes case-insensitively."""
        sms = SMSVerifier(provider=mock_sms_provider)
        voice = VoiceVerifier(provider=mock_voice_provider)
        push = PushVerifier(provider=mock_push_provider)
        email = EmailVerifier(provider=mock_email_provider)

        engine = VerificationEngine(
            sms_verifier=sms,
            voice_verifier=voice,
            push_verifier=push,
            email_verifier=email,
        )

        # Generate alphanumeric code
        session = await engine.create_verification(low_risk_request)

        # Verify with different case
        code_lower = session.code.lower()

        # Both should work
        verified = await engine.verify_code(session.session_id, code_lower)
        assert verified.is_complete

    @pytest.mark.asyncio
    async def test_whitespace_handling(
        self,
        mock_sms_provider,
        mock_voice_provider,
        mock_push_provider,
        mock_email_provider,
        low_risk_request,
    ):
        """Should handle whitespace in codes."""
        sms = SMSVerifier(provider=mock_sms_provider)
        voice = VoiceVerifier(provider=mock_voice_provider)
        push = PushVerifier(provider=mock_push_provider)
        email = EmailVerifier(provider=mock_email_provider)

        engine = VerificationEngine(
            sms_verifier=sms,
            voice_verifier=voice,
            push_verifier=push,
            email_verifier=email,
        )

        session = await engine.create_verification(low_risk_request)
        code_with_spaces = f"  {session.code}  "

        verified = await engine.verify_code(session.session_id, code_with_spaces)
        assert verified.is_complete
