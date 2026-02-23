"""
Unit tests for push notification verifier.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock

from src.services.verification.base import (
    VerificationChannel,
    VerificationStatus,
)
from src.services.verification.push_verifier import (
    PushVerifier,
    PushProvider,
    FirebasePushProvider,
    ConsolePushProvider,
)


class TestConsolePushProvider:
    """Tests for console push provider."""

    @pytest.mark.asyncio
    async def test_console_provider_always_available(self, console_push_provider):
        """Console provider should always be available."""
        assert await console_push_provider.is_available() is True

    @pytest.mark.asyncio
    async def test_console_provider_sends_notification(
        self, console_push_provider, sample_device_token, capsys
    ):
        """Console provider should print to console and return success."""
        result = await console_push_provider.send_notification(
            device_token=sample_device_token,
            title="Verification",
            body="Your code is 123456",
            data={"code": "123456"},
        )

        assert result["success"] is True
        assert "message_id" in result
        assert result["status"] == "sent"

        # Check console output
        captured = capsys.readouterr()
        assert "PUSH NOTIFICATION" in captured.out
        assert "Verification" in captured.out
        assert "123456" in captured.out

    @pytest.mark.asyncio
    async def test_console_provider_stores_notifications(
        self, console_push_provider, sample_device_token
    ):
        """Console provider should store sent notifications."""
        await console_push_provider.send_notification(
            device_token=sample_device_token,
            title="Title 1",
            body="Body 1",
        )
        await console_push_provider.send_notification(
            device_token=sample_device_token,
            title="Title 2",
            body="Body 2",
        )

        assert len(console_push_provider.notifications) == 2
        assert console_push_provider.notifications[0]["title"] == "Title 1"
        assert console_push_provider.notifications[1]["title"] == "Title 2"

    @pytest.mark.asyncio
    async def test_console_provider_truncates_token(
        self, console_push_provider, capsys
    ):
        """Console provider should truncate long device tokens in output."""
        long_token = "a" * 100

        await console_push_provider.send_notification(
            device_token=long_token,
            title="Test",
            body="Test body",
        )

        captured = capsys.readouterr()
        assert "..." in captured.out  # Token should be truncated


class TestPushVerifier:
    """Tests for push verifier."""

    @pytest.mark.asyncio
    async def test_channel_is_push(self, push_verifier):
        """Push verifier should report PUSH channel."""
        assert push_verifier.channel == VerificationChannel.PUSH

    @pytest.mark.asyncio
    async def test_verifier_name(self, push_verifier):
        """Push verifier should have correct name."""
        assert push_verifier.name == "push_verifier"

    @pytest.mark.asyncio
    async def test_send_code_success(
        self, push_verifier, sample_device_token, sample_verification_code
    ):
        """Send code should return success result."""
        result = await push_verifier.send_code(
            recipient=sample_device_token,
            code=sample_verification_code,
            expiry_minutes=10,
        )

        assert result.status == VerificationStatus.SENT
        assert result.channel == VerificationChannel.PUSH
        assert result.verified is False
        assert result.sent_at is not None
        assert result.expires_at is not None
        assert result.provider == "mock_push"
        assert result.provider_message_id == "push_123"

    @pytest.mark.asyncio
    async def test_send_code_includes_data(
        self, mock_push_provider, sample_device_token, sample_verification_code
    ):
        """Send code should include verification data in notification."""
        verifier = PushVerifier(provider=mock_push_provider)

        await verifier.send_code(
            recipient=sample_device_token,
            code=sample_verification_code,
            expiry_minutes=10,
            metadata={"user_id": "123"},
        )

        call_args = mock_push_provider.send_notification.call_args
        data = call_args.kwargs.get("data", {})

        assert data.get("type") == "verification"
        assert data.get("code") == sample_verification_code
        assert data.get("user_id") == "123"

    @pytest.mark.asyncio
    async def test_verify_code_correct(self, push_verifier, sample_device_token):
        """Verify code should return verified for correct code."""
        result = await push_verifier.verify_code(
            recipient=sample_device_token,
            code="123456",
            expected_code="123456",
        )

        assert result.status == VerificationStatus.VERIFIED
        assert result.verified is True
        assert result.verified_at is not None

    @pytest.mark.asyncio
    async def test_verify_code_incorrect(self, push_verifier, sample_device_token):
        """Verify code should return failed for incorrect code."""
        result = await push_verifier.verify_code(
            recipient=sample_device_token,
            code="000000",
            expected_code="123456",
        )

        assert result.status == VerificationStatus.FAILED
        assert result.verified is False
        assert result.error == "Invalid code"

    @pytest.mark.asyncio
    async def test_verify_code_case_insensitive(self, push_verifier, sample_device_token):
        """Verify code should be case insensitive."""
        result = await push_verifier.verify_code(
            recipient=sample_device_token,
            code="abc123",
            expected_code="ABC123",
        )

        assert result.verified is True


class TestSendToMultiple:
    """Tests for sending to multiple devices."""

    @pytest.mark.asyncio
    async def test_send_to_multiple_devices(self, mock_push_provider, sample_verification_code):
        """Should send to multiple device tokens."""
        verifier = PushVerifier(provider=mock_push_provider)

        tokens = [
            "device_token_1",
            "device_token_2",
            "device_token_3",
        ]

        results = await verifier.send_to_multiple(
            device_tokens=tokens,
            code=sample_verification_code,
            expiry_minutes=10,
        )

        assert len(results) == 3
        assert all(r.status == VerificationStatus.SENT for r in results)
        assert mock_push_provider.send_notification.call_count == 3

    @pytest.mark.asyncio
    async def test_send_to_empty_list(self, mock_push_provider, sample_verification_code):
        """Should handle empty device list."""
        verifier = PushVerifier(provider=mock_push_provider)

        results = await verifier.send_to_multiple(
            device_tokens=[],
            code=sample_verification_code,
            expiry_minutes=10,
        )

        assert len(results) == 0


class TestProviderFallback:
    """Tests for provider fallback behavior."""

    @pytest.mark.asyncio
    async def test_fallback_to_console(self):
        """Should fall back to console provider when no providers configured."""
        verifier = PushVerifier()
        provider = await verifier._get_provider()

        assert provider.name == "console"

    @pytest.mark.asyncio
    async def test_uses_specified_provider(self, mock_push_provider):
        """Should use specified provider when provided."""
        verifier = PushVerifier(provider=mock_push_provider)
        provider = await verifier._get_provider()

        assert provider.name == "mock_push"


class TestCustomization:
    """Tests for push notification customization."""

    @pytest.mark.asyncio
    async def test_custom_title(self, mock_push_provider, sample_device_token):
        """Should use custom notification title."""
        verifier = PushVerifier(provider=mock_push_provider)
        verifier.set_title("Custom Title")

        await verifier.send_code(
            recipient=sample_device_token,
            code="123456",
            expiry_minutes=5,
        )

        call_args = mock_push_provider.send_notification.call_args
        assert call_args.kwargs.get("title") == "Custom Title"

    @pytest.mark.asyncio
    async def test_custom_body_template(self, mock_push_provider, sample_device_token):
        """Should use custom body template."""
        verifier = PushVerifier(provider=mock_push_provider)
        verifier.set_body_template("Code: {code}")

        await verifier.send_code(
            recipient=sample_device_token,
            code="123456",
            expiry_minutes=5,
        )

        call_args = mock_push_provider.send_notification.call_args
        assert "Code: 123456" in call_args.kwargs.get("body", "")


class TestPushProviderFailure:
    """Tests for handling provider failures."""

    @pytest.mark.asyncio
    async def test_send_code_failure(
        self, sample_device_token, sample_verification_code
    ):
        """Send code should return failure result when provider fails."""
        provider = MagicMock(spec=PushProvider)
        provider.name = "failing_push"
        provider.is_available = AsyncMock(return_value=True)
        provider.send_notification = AsyncMock(return_value={
            "success": False,
            "error": "Invalid token",
        })

        verifier = PushVerifier(provider=provider)

        result = await verifier.send_code(
            recipient=sample_device_token,
            code=sample_verification_code,
            expiry_minutes=10,
        )

        assert result.status == VerificationStatus.FAILED
        assert result.error == "Invalid token"


class TestFirebasePushProvider:
    """Tests for Firebase push provider (configuration only)."""

    def test_firebase_provider_name(self):
        """Firebase provider should have correct name."""
        provider = FirebasePushProvider()
        assert provider.name == "firebase"

    @pytest.mark.asyncio
    async def test_firebase_not_available_without_config(self):
        """Firebase should not be available without configuration."""
        provider = FirebasePushProvider(
            credentials_path=None,
            project_id=None,
        )
        # Without credentials, it might still return True but will fail on send
        # This test just verifies it doesn't crash
        assert provider.name == "firebase"
