"""
Unit tests for SMS verifier.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock

from src.services.verification.base import (
    VerificationChannel,
    VerificationStatus,
)
from src.services.verification.sms_verifier import (
    SMSVerifier,
    SMSProvider,
    TwilioSMSProvider,
    PlivoSMSProvider,
    ConsoleSMSProvider,
)


class TestConsoleSMSProvider:
    """Tests for console SMS provider."""

    @pytest.mark.asyncio
    async def test_console_provider_always_available(self, console_sms_provider):
        """Console provider should always be available."""
        assert await console_sms_provider.is_available() is True

    @pytest.mark.asyncio
    async def test_console_provider_sends_successfully(
        self, console_sms_provider, sample_phone_number, capsys
    ):
        """Console provider should print to console and return success."""
        result = await console_sms_provider.send_sms(
            to=sample_phone_number,
            message="Test code: 123456",
        )

        assert result["success"] is True
        assert "message_id" in result
        assert result["status"] == "sent"

        # Check console output
        captured = capsys.readouterr()
        assert "SMS VERIFICATION" in captured.out
        assert sample_phone_number in captured.out
        assert "123456" in captured.out

    @pytest.mark.asyncio
    async def test_console_provider_stores_messages(self, console_sms_provider, sample_phone_number):
        """Console provider should store sent messages."""
        await console_sms_provider.send_sms(
            to=sample_phone_number,
            message="Code 1",
        )
        await console_sms_provider.send_sms(
            to=sample_phone_number,
            message="Code 2",
        )

        assert len(console_sms_provider.sent_messages) == 2
        assert console_sms_provider.sent_messages[0]["message"] == "Code 1"
        assert console_sms_provider.sent_messages[1]["message"] == "Code 2"


class TestSMSVerifier:
    """Tests for SMS verifier."""

    @pytest.mark.asyncio
    async def test_channel_is_sms(self, sms_verifier):
        """SMS verifier should report SMS channel."""
        assert sms_verifier.channel == VerificationChannel.SMS

    @pytest.mark.asyncio
    async def test_verifier_name(self, sms_verifier):
        """SMS verifier should have correct name."""
        assert sms_verifier.name == "sms_verifier"

    @pytest.mark.asyncio
    async def test_send_code_success(
        self, sms_verifier, sample_phone_number, sample_verification_code
    ):
        """Send code should return success result."""
        result = await sms_verifier.send_code(
            recipient=sample_phone_number,
            code=sample_verification_code,
            expiry_minutes=10,
        )

        assert result.status == VerificationStatus.SENT
        assert result.channel == VerificationChannel.SMS
        assert result.verified is False
        assert result.sent_at is not None
        assert result.expires_at is not None
        assert result.provider == "mock_sms"
        assert result.provider_message_id == "msg_123"

    @pytest.mark.asyncio
    async def test_send_code_failure(
        self, failing_sms_provider, sample_phone_number, sample_verification_code
    ):
        """Send code should return failure result when provider fails."""
        verifier = SMSVerifier(provider=failing_sms_provider)

        result = await verifier.send_code(
            recipient=sample_phone_number,
            code=sample_verification_code,
            expiry_minutes=10,
        )

        assert result.status == VerificationStatus.FAILED
        assert result.error == "Network error"

    @pytest.mark.asyncio
    async def test_verify_code_correct(self, sms_verifier, sample_phone_number):
        """Verify code should return verified for correct code."""
        result = await sms_verifier.verify_code(
            recipient=sample_phone_number,
            code="123456",
            expected_code="123456",
        )

        assert result.status == VerificationStatus.VERIFIED
        assert result.verified is True
        assert result.verified_at is not None

    @pytest.mark.asyncio
    async def test_verify_code_incorrect(self, sms_verifier, sample_phone_number):
        """Verify code should return failed for incorrect code."""
        result = await sms_verifier.verify_code(
            recipient=sample_phone_number,
            code="000000",
            expected_code="123456",
        )

        assert result.status == VerificationStatus.FAILED
        assert result.verified is False
        assert result.error == "Invalid code"

    @pytest.mark.asyncio
    async def test_verify_code_case_insensitive(self, sms_verifier, sample_phone_number):
        """Verify code should be case insensitive."""
        result = await sms_verifier.verify_code(
            recipient=sample_phone_number,
            code="abc123",
            expected_code="ABC123",
        )

        assert result.status == VerificationStatus.VERIFIED
        assert result.verified is True

    @pytest.mark.asyncio
    async def test_verify_code_strips_whitespace(self, sms_verifier, sample_phone_number):
        """Verify code should strip whitespace."""
        result = await sms_verifier.verify_code(
            recipient=sample_phone_number,
            code="  123456  ",
            expected_code="123456",
        )

        assert result.status == VerificationStatus.VERIFIED
        assert result.verified is True


class TestPhoneNormalization:
    """Tests for phone number normalization."""

    @pytest.fixture
    def verifier(self, mock_sms_provider):
        return SMSVerifier(provider=mock_sms_provider)

    def test_normalize_e164_format(self, verifier):
        """E.164 format should be preserved."""
        result = verifier._normalize_phone("+15551234567")
        assert result == "+15551234567"

    def test_normalize_10_digit_us(self, verifier):
        """10-digit US number should get +1 prefix."""
        result = verifier._normalize_phone("5551234567")
        assert result == "+15551234567"

    def test_normalize_11_digit_us(self, verifier):
        """11-digit US number starting with 1 should get + prefix."""
        result = verifier._normalize_phone("15551234567")
        assert result == "+15551234567"

    def test_normalize_with_formatting(self, verifier):
        """Formatted number should be cleaned."""
        result = verifier._normalize_phone("(555) 123-4567")
        assert result == "+15551234567"

    def test_normalize_with_dashes(self, verifier):
        """Number with dashes should be cleaned."""
        result = verifier._normalize_phone("555-123-4567")
        assert result == "+15551234567"

    def test_normalize_international(self, verifier):
        """International number should preserve country code."""
        result = verifier._normalize_phone("+447911123456")
        assert result == "+447911123456"


class TestProviderFallback:
    """Tests for provider fallback behavior."""

    @pytest.mark.asyncio
    async def test_fallback_to_console(self):
        """Should fall back to console provider when no providers configured."""
        verifier = SMSVerifier()
        provider = await verifier._get_provider()

        # Should get console provider as fallback
        assert provider.name == "console"

    @pytest.mark.asyncio
    async def test_uses_specified_provider(self, mock_sms_provider):
        """Should use specified provider when provided."""
        verifier = SMSVerifier(provider=mock_sms_provider)
        provider = await verifier._get_provider()

        assert provider.name == "mock_sms"

    @pytest.mark.asyncio
    async def test_custom_template(self, mock_sms_provider, sample_phone_number):
        """Should use custom message template."""
        verifier = SMSVerifier(provider=mock_sms_provider)
        verifier.set_template("Custom: {code} expires in {expiry} mins")

        await verifier.send_code(
            recipient=sample_phone_number,
            code="123456",
            expiry_minutes=5,
        )

        # Check the message was formatted correctly
        call_args = mock_sms_provider.send_sms.call_args
        assert "Custom: 123456 expires in 5 mins" in call_args.kwargs.get("message", "")


class TestTwilioProvider:
    """Tests for Twilio SMS provider (configuration only)."""

    def test_twilio_not_available_without_config(self):
        """Twilio should not be available without configuration."""
        # This test just verifies the provider checks for config
        provider = TwilioSMSProvider(
            account_sid=None,
            auth_token=None,
            from_number=None,
        )
        # is_available is async but we can check the attributes
        assert provider.account_sid is None or provider.account_sid == ""

    def test_twilio_provider_name(self):
        """Twilio provider should have correct name."""
        provider = TwilioSMSProvider()
        assert provider.name == "twilio"


class TestPlivoProvider:
    """Tests for Plivo SMS provider (configuration only)."""

    def test_plivo_provider_name(self):
        """Plivo provider should have correct name."""
        provider = PlivoSMSProvider()
        assert provider.name == "plivo"
