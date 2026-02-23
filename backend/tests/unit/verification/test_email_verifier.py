"""
Unit tests for email verifier.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock

from src.services.verification.base import (
    VerificationChannel,
    VerificationStatus,
)
from src.services.verification.email_verifier import (
    EmailVerifier,
    EmailProvider,
    SMTPEmailProvider,
    SendGridEmailProvider,
    ConsoleEmailProvider,
)


class TestConsoleEmailProvider:
    """Tests for console email provider."""

    @pytest.mark.asyncio
    async def test_console_provider_always_available(self, console_email_provider):
        """Console provider should always be available."""
        assert await console_email_provider.is_available() is True

    @pytest.mark.asyncio
    async def test_console_provider_sends_email(
        self, console_email_provider, sample_email, capsys
    ):
        """Console provider should print to console and return success."""
        result = await console_email_provider.send_email(
            to=sample_email,
            subject="Verification Code",
            body_text="Your code is 123456",
            body_html="<p>Your code is 123456</p>",
        )

        assert result["success"] is True
        assert "message_id" in result
        assert result["status"] == "sent"

        # Check console output
        captured = capsys.readouterr()
        assert "EMAIL VERIFICATION" in captured.out
        assert sample_email in captured.out
        assert "Verification Code" in captured.out

    @pytest.mark.asyncio
    async def test_console_provider_stores_emails(
        self, console_email_provider, sample_email
    ):
        """Console provider should store sent emails."""
        await console_email_provider.send_email(
            to=sample_email,
            subject="Subject 1",
            body_text="Body 1",
        )
        await console_email_provider.send_email(
            to=sample_email,
            subject="Subject 2",
            body_text="Body 2",
        )

        assert len(console_email_provider.emails) == 2
        assert console_email_provider.emails[0]["subject"] == "Subject 1"
        assert console_email_provider.emails[1]["subject"] == "Subject 2"

    @pytest.mark.asyncio
    async def test_console_provider_stores_html(
        self, console_email_provider, sample_email
    ):
        """Console provider should store HTML body."""
        await console_email_provider.send_email(
            to=sample_email,
            subject="Test",
            body_text="Plain text",
            body_html="<p>HTML content</p>",
        )

        assert console_email_provider.emails[0]["body_html"] == "<p>HTML content</p>"


class TestEmailVerifier:
    """Tests for email verifier."""

    @pytest.mark.asyncio
    async def test_channel_is_email(self, email_verifier):
        """Email verifier should report EMAIL channel."""
        assert email_verifier.channel == VerificationChannel.EMAIL

    @pytest.mark.asyncio
    async def test_verifier_name(self, email_verifier):
        """Email verifier should have correct name."""
        assert email_verifier.name == "email_verifier"

    @pytest.mark.asyncio
    async def test_send_code_success(
        self, email_verifier, sample_email, sample_verification_code
    ):
        """Send code should return success result."""
        result = await email_verifier.send_code(
            recipient=sample_email,
            code=sample_verification_code,
            expiry_minutes=10,
        )

        assert result.status == VerificationStatus.SENT
        assert result.channel == VerificationChannel.EMAIL
        assert result.verified is False
        assert result.sent_at is not None
        assert result.expires_at is not None
        assert result.provider == "mock_email"
        assert result.provider_message_id == "email_123"

    @pytest.mark.asyncio
    async def test_send_code_formats_templates(
        self, mock_email_provider, sample_email, sample_verification_code
    ):
        """Send code should format code into templates."""
        verifier = EmailVerifier(provider=mock_email_provider)

        await verifier.send_code(
            recipient=sample_email,
            code=sample_verification_code,
            expiry_minutes=10,
        )

        call_args = mock_email_provider.send_email.call_args
        body_text = call_args.kwargs.get("body_text", "")
        body_html = call_args.kwargs.get("body_html", "")

        assert sample_verification_code in body_text
        assert sample_verification_code in body_html
        assert "10" in body_text  # expiry minutes

    @pytest.mark.asyncio
    async def test_verify_code_correct(self, email_verifier, sample_email):
        """Verify code should return verified for correct code."""
        result = await email_verifier.verify_code(
            recipient=sample_email,
            code="123456",
            expected_code="123456",
        )

        assert result.status == VerificationStatus.VERIFIED
        assert result.verified is True
        assert result.verified_at is not None

    @pytest.mark.asyncio
    async def test_verify_code_incorrect(self, email_verifier, sample_email):
        """Verify code should return failed for incorrect code."""
        result = await email_verifier.verify_code(
            recipient=sample_email,
            code="000000",
            expected_code="123456",
        )

        assert result.status == VerificationStatus.FAILED
        assert result.verified is False
        assert result.error == "Invalid code"

    @pytest.mark.asyncio
    async def test_verify_code_case_insensitive(self, email_verifier, sample_email):
        """Verify code should be case insensitive."""
        result = await email_verifier.verify_code(
            recipient=sample_email,
            code="abc123",
            expected_code="ABC123",
        )

        assert result.verified is True

    @pytest.mark.asyncio
    async def test_verify_code_strips_whitespace(self, email_verifier, sample_email):
        """Verify code should strip whitespace."""
        result = await email_verifier.verify_code(
            recipient=sample_email,
            code="  123456  ",
            expected_code="123456",
        )

        assert result.verified is True


class TestProviderFallback:
    """Tests for provider fallback behavior."""

    @pytest.mark.asyncio
    async def test_fallback_to_console(self):
        """Should fall back to console provider when no providers configured."""
        verifier = EmailVerifier()
        provider = await verifier._get_provider()

        assert provider.name == "console"

    @pytest.mark.asyncio
    async def test_uses_specified_provider(self, mock_email_provider):
        """Should use specified provider when provided."""
        verifier = EmailVerifier(provider=mock_email_provider)
        provider = await verifier._get_provider()

        assert provider.name == "mock_email"


class TestCustomization:
    """Tests for email customization."""

    @pytest.mark.asyncio
    async def test_custom_subject(self, mock_email_provider, sample_email):
        """Should use custom email subject."""
        verifier = EmailVerifier(provider=mock_email_provider)
        verifier.set_subject("Custom Subject")

        await verifier.send_code(
            recipient=sample_email,
            code="123456",
            expiry_minutes=5,
        )

        call_args = mock_email_provider.send_email.call_args
        assert call_args.kwargs.get("subject") == "Custom Subject"

    @pytest.mark.asyncio
    async def test_custom_templates(self, mock_email_provider, sample_email):
        """Should use custom email templates."""
        verifier = EmailVerifier(provider=mock_email_provider)
        verifier.set_templates(
            body_text="Custom text: {code}",
            body_html="<p>Custom HTML: {code}</p>",
        )

        await verifier.send_code(
            recipient=sample_email,
            code="123456",
            expiry_minutes=5,
        )

        call_args = mock_email_provider.send_email.call_args
        assert "Custom text: 123456" in call_args.kwargs.get("body_text", "")
        assert "<p>Custom HTML: 123456</p>" in call_args.kwargs.get("body_html", "")

    def test_add_custom_provider(self, mock_email_provider):
        """Should allow adding custom providers."""
        verifier = EmailVerifier()
        verifier.add_provider("custom", mock_email_provider)

        assert "custom" in verifier._providers


class TestEmailProviderFailure:
    """Tests for handling provider failures."""

    @pytest.mark.asyncio
    async def test_send_code_failure(
        self, sample_email, sample_verification_code
    ):
        """Send code should return failure result when provider fails."""
        provider = MagicMock(spec=EmailProvider)
        provider.name = "failing_email"
        provider.is_available = AsyncMock(return_value=True)
        provider.send_email = AsyncMock(return_value={
            "success": False,
            "error": "SMTP connection failed",
        })

        verifier = EmailVerifier(provider=provider)

        result = await verifier.send_code(
            recipient=sample_email,
            code=sample_verification_code,
            expiry_minutes=10,
        )

        assert result.status == VerificationStatus.FAILED
        assert result.error == "SMTP connection failed"


class TestSMTPEmailProvider:
    """Tests for SMTP email provider (configuration only)."""

    def test_smtp_provider_name(self):
        """SMTP provider should have correct name."""
        provider = SMTPEmailProvider()
        assert provider.name == "smtp"

    @pytest.mark.asyncio
    async def test_smtp_not_available_without_config(self):
        """SMTP should not be available without host configuration."""
        provider = SMTPEmailProvider(
            host=None,
            from_email=None,
        )
        available = await provider.is_available()
        assert available is False

    @pytest.mark.asyncio
    async def test_smtp_available_with_config(self):
        """SMTP should be available with host and from_email."""
        provider = SMTPEmailProvider(
            host="smtp.example.com",
            from_email="noreply@example.com",
        )
        available = await provider.is_available()
        assert available is True


class TestSendGridEmailProvider:
    """Tests for SendGrid email provider (configuration only)."""

    def test_sendgrid_provider_name(self):
        """SendGrid provider should have correct name."""
        provider = SendGridEmailProvider()
        assert provider.name == "sendgrid"

    @pytest.mark.asyncio
    async def test_sendgrid_not_available_without_config(self):
        """SendGrid should not be available without API key."""
        provider = SendGridEmailProvider(
            api_key=None,
            from_email=None,
        )
        available = await provider.is_available()
        assert available is False


class TestDefaultTemplates:
    """Tests for default email templates."""

    def test_default_subject(self):
        """Should have default subject."""
        verifier = EmailVerifier()
        assert "DeepSafe" in verifier._subject

    def test_default_body_text_has_placeholders(self):
        """Default body text should have code and expiry placeholders."""
        verifier = EmailVerifier()
        assert "{code}" in verifier._body_text_template
        assert "{expiry}" in verifier._body_text_template

    def test_default_body_html_has_placeholders(self):
        """Default body HTML should have code and expiry placeholders."""
        verifier = EmailVerifier()
        assert "{code}" in verifier._body_html_template
        assert "{expiry}" in verifier._body_html_template

    def test_default_body_html_is_valid_html(self):
        """Default body HTML should be valid HTML."""
        verifier = EmailVerifier()
        assert "<!DOCTYPE html>" in verifier._body_html_template
        assert "</html>" in verifier._body_html_template
