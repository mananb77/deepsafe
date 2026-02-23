"""
Unit tests for voice callback verifier.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock

from src.services.verification.base import (
    VerificationChannel,
    VerificationStatus,
)
from src.services.verification.voice_verifier import (
    VoiceVerifier,
    VoiceProvider,
    TwilioVoiceProvider,
    PlivoVoiceProvider,
    ConsoleVoiceProvider,
)


class TestConsoleVoiceProvider:
    """Tests for console voice provider."""

    @pytest.mark.asyncio
    async def test_console_provider_always_available(self, console_voice_provider):
        """Console provider should always be available."""
        assert await console_voice_provider.is_available() is True

    @pytest.mark.asyncio
    async def test_console_provider_makes_call(
        self, console_voice_provider, sample_phone_number, capsys
    ):
        """Console provider should print to console and return success."""
        result = await console_voice_provider.make_call(
            to=sample_phone_number,
            message="Your verification code is 1, 2, 3, 4, 5, 6",
        )

        assert result["success"] is True
        assert "call_id" in result
        assert result["status"] == "completed"

        # Check console output
        captured = capsys.readouterr()
        assert "VOICE VERIFICATION CALL" in captured.out
        assert sample_phone_number in captured.out

    @pytest.mark.asyncio
    async def test_console_provider_stores_calls(
        self, console_voice_provider, sample_phone_number
    ):
        """Console provider should store calls."""
        await console_voice_provider.make_call(
            to=sample_phone_number,
            message="Call 1",
        )
        await console_voice_provider.make_call(
            to=sample_phone_number,
            message="Call 2",
        )

        assert len(console_voice_provider.calls) == 2
        assert console_voice_provider.calls[0]["message"] == "Call 1"
        assert console_voice_provider.calls[1]["message"] == "Call 2"


class TestVoiceVerifier:
    """Tests for voice verifier."""

    @pytest.mark.asyncio
    async def test_channel_is_voice(self, voice_verifier):
        """Voice verifier should report VOICE channel."""
        assert voice_verifier.channel == VerificationChannel.VOICE

    @pytest.mark.asyncio
    async def test_verifier_name(self, voice_verifier):
        """Voice verifier should have correct name."""
        assert voice_verifier.name == "voice_verifier"

    @pytest.mark.asyncio
    async def test_send_code_success(
        self, voice_verifier, sample_phone_number, sample_verification_code
    ):
        """Send code should return success result."""
        result = await voice_verifier.send_code(
            recipient=sample_phone_number,
            code=sample_verification_code,
            expiry_minutes=10,
        )

        assert result.status == VerificationStatus.SENT
        assert result.channel == VerificationChannel.VOICE
        assert result.verified is False
        assert result.sent_at is not None
        assert result.expires_at is not None
        assert result.provider == "mock_voice"
        assert result.provider_message_id == "call_123"

    @pytest.mark.asyncio
    async def test_verify_code_correct(self, voice_verifier, sample_phone_number):
        """Verify code should return verified for correct code."""
        result = await voice_verifier.verify_code(
            recipient=sample_phone_number,
            code="123456",
            expected_code="123456",
        )

        assert result.status == VerificationStatus.VERIFIED
        assert result.verified is True

    @pytest.mark.asyncio
    async def test_verify_code_incorrect(self, voice_verifier, sample_phone_number):
        """Verify code should return failed for incorrect code."""
        result = await voice_verifier.verify_code(
            recipient=sample_phone_number,
            code="000000",
            expected_code="123456",
        )

        assert result.status == VerificationStatus.FAILED
        assert result.verified is False


class TestCodeForSpeech:
    """Tests for code formatting for speech."""

    @pytest.fixture
    def verifier(self, mock_voice_provider):
        return VoiceVerifier(provider=mock_voice_provider)

    def test_format_numeric_code(self, verifier):
        """Numeric code should be spelled out with pauses."""
        result = verifier._format_code_for_speech("123456")
        assert result == "1, 2, 3, 4, 5, 6"

    def test_format_alphanumeric_code(self, verifier):
        """Alphanumeric code should be spelled out."""
        result = verifier._format_code_for_speech("ABC123")
        assert result == "A, B, C, 1, 2, 3"

    def test_format_short_code(self, verifier):
        """Short code should be formatted correctly."""
        result = verifier._format_code_for_speech("1234")
        assert result == "1, 2, 3, 4"


class TestPhoneNormalization:
    """Tests for phone number normalization in voice verifier."""

    @pytest.fixture
    def verifier(self, mock_voice_provider):
        return VoiceVerifier(provider=mock_voice_provider)

    def test_normalize_e164_format(self, verifier):
        """E.164 format should be preserved."""
        result = verifier._normalize_phone("+15551234567")
        assert result == "+15551234567"

    def test_normalize_10_digit_us(self, verifier):
        """10-digit US number should get +1 prefix."""
        result = verifier._normalize_phone("5551234567")
        assert result == "+15551234567"

    def test_normalize_with_formatting(self, verifier):
        """Formatted number should be cleaned."""
        result = verifier._normalize_phone("(555) 123-4567")
        assert result == "+15551234567"


class TestProviderFallback:
    """Tests for provider fallback behavior."""

    @pytest.mark.asyncio
    async def test_fallback_to_console(self):
        """Should fall back to console provider when no providers configured."""
        verifier = VoiceVerifier()
        provider = await verifier._get_provider()

        assert provider.name == "console"

    @pytest.mark.asyncio
    async def test_uses_specified_provider(self, mock_voice_provider):
        """Should use specified provider when provided."""
        verifier = VoiceVerifier(provider=mock_voice_provider)
        provider = await verifier._get_provider()

        assert provider.name == "mock_voice"

    @pytest.mark.asyncio
    async def test_custom_template(self, mock_voice_provider, sample_phone_number):
        """Should use custom call script template."""
        verifier = VoiceVerifier(provider=mock_voice_provider)
        verifier.set_template("Custom message: {code_spoken}")

        await verifier.send_code(
            recipient=sample_phone_number,
            code="123456",
            expiry_minutes=5,
        )

        # Check the message was formatted correctly
        call_args = mock_voice_provider.make_call.call_args
        assert "1, 2, 3, 4, 5, 6" in call_args.kwargs.get("message", "")


class TestVoiceProviderFailure:
    """Tests for handling provider failures."""

    @pytest.mark.asyncio
    async def test_send_code_failure(
        self, sample_phone_number, sample_verification_code
    ):
        """Send code should return failure result when provider fails."""
        provider = MagicMock(spec=VoiceProvider)
        provider.name = "failing_voice"
        provider.is_available = AsyncMock(return_value=True)
        provider.make_call = AsyncMock(return_value={
            "success": False,
            "error": "Call failed",
        })

        verifier = VoiceVerifier(provider=provider)

        result = await verifier.send_code(
            recipient=sample_phone_number,
            code=sample_verification_code,
            expiry_minutes=10,
        )

        assert result.status == VerificationStatus.FAILED
        assert result.error == "Call failed"


class TestTwilioVoiceProvider:
    """Tests for Twilio voice provider (configuration only)."""

    def test_twilio_provider_name(self):
        """Twilio voice provider should have correct name."""
        provider = TwilioVoiceProvider()
        assert provider.name == "twilio"


class TestPlivoVoiceProvider:
    """Tests for Plivo voice provider (configuration only)."""

    def test_plivo_provider_name(self):
        """Plivo voice provider should have correct name."""
        provider = PlivoVoiceProvider()
        assert provider.name == "plivo"
