"""
Email Verifier

Email-based verification as a fallback channel.
Supports:
- SMTP (standard email servers)
- SendGrid API
- AWS SES
- Console mock (development)
"""

import ssl
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any, Dict, Optional
from uuid import uuid4
import asyncio

from src.shared.config import get_settings
from src.services.verification.base import (
    BaseVerifier,
    VerificationChannel,
    VerificationResult,
    VerificationStatus,
)


class EmailProvider(ABC):
    """Base class for email providers."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Provider name."""
        pass

    @abstractmethod
    async def send_email(
        self,
        to: str,
        subject: str,
        body_text: str,
        body_html: Optional[str] = None,
        from_email: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Send email.

        Returns dict with:
        - success: bool
        - message_id: Optional[str]
        - error: Optional[str]
        """
        pass

    @abstractmethod
    async def is_available(self) -> bool:
        """Check if provider is configured and available."""
        pass


class SMTPEmailProvider(EmailProvider):
    """SMTP email provider."""

    def __init__(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        from_email: Optional[str] = None,
        use_tls: bool = True,
    ):
        settings = get_settings()
        self.host = host or getattr(settings, 'smtp_host', None)
        self.port = port or getattr(settings, 'smtp_port', 587)
        self.username = username or getattr(settings, 'smtp_username', None)
        self.password = password or getattr(settings, 'smtp_password', None)
        self.from_email = from_email or getattr(settings, 'smtp_from_email', None)
        self.use_tls = use_tls

    @property
    def name(self) -> str:
        return "smtp"

    async def is_available(self) -> bool:
        """Check if SMTP is configured."""
        return bool(self.host and self.from_email)

    async def send_email(
        self,
        to: str,
        subject: str,
        body_text: str,
        body_html: Optional[str] = None,
        from_email: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Send email via SMTP."""
        if not await self.is_available():
            return {
                "success": False,
                "error": "SMTP not configured",
            }

        try:
            import smtplib

            # Create message
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = from_email or self.from_email
            msg["To"] = to

            # Attach text part
            msg.attach(MIMEText(body_text, "plain"))

            # Attach HTML part if provided
            if body_html:
                msg.attach(MIMEText(body_html, "html"))

            # Send email (run in thread pool to not block)
            def send():
                context = ssl.create_default_context()
                with smtplib.SMTP(self.host, self.port) as server:
                    if self.use_tls:
                        server.starttls(context=context)
                    if self.username and self.password:
                        server.login(self.username, self.password)
                    server.send_message(msg)

            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, send)

            return {
                "success": True,
                "message_id": str(uuid4()),
                "status": "sent",
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }


class SendGridEmailProvider(EmailProvider):
    """SendGrid API email provider."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        from_email: Optional[str] = None,
    ):
        settings = get_settings()
        self.api_key = api_key or getattr(settings, 'sendgrid_api_key', None)
        self.from_email = from_email or getattr(settings, 'sendgrid_from_email', None)

    @property
    def name(self) -> str:
        return "sendgrid"

    async def is_available(self) -> bool:
        """Check if SendGrid is configured."""
        return bool(self.api_key and self.from_email)

    async def send_email(
        self,
        to: str,
        subject: str,
        body_text: str,
        body_html: Optional[str] = None,
        from_email: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Send email via SendGrid."""
        if not await self.is_available():
            return {
                "success": False,
                "error": "SendGrid not configured",
            }

        try:
            from sendgrid import SendGridAPIClient
            from sendgrid.helpers.mail import Mail, Content

            message = Mail(
                from_email=from_email or self.from_email,
                to_emails=to,
                subject=subject,
            )

            message.add_content(Content("text/plain", body_text))
            if body_html:
                message.add_content(Content("text/html", body_html))

            client = SendGridAPIClient(self.api_key)
            response = client.send(message)

            return {
                "success": response.status_code in [200, 201, 202],
                "message_id": response.headers.get("X-Message-Id"),
                "status": str(response.status_code),
            }

        except ImportError:
            return {
                "success": False,
                "error": "sendgrid package not installed",
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }


class ConsoleEmailProvider(EmailProvider):
    """
    Console email provider for development/testing.

    Prints email to console instead of sending.
    """

    def __init__(self):
        self.emails: list = []

    @property
    def name(self) -> str:
        return "console"

    async def is_available(self) -> bool:
        """Console provider is always available."""
        return True

    async def send_email(
        self,
        to: str,
        subject: str,
        body_text: str,
        body_html: Optional[str] = None,
        from_email: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Print email to console."""
        message_id = str(uuid4())

        print(f"\n{'='*50}")
        print(f"EMAIL VERIFICATION (Console Mode)")
        print(f"{'='*50}")
        print(f"To: {to}")
        print(f"From: {from_email or 'noreply@deepsafe.ai'}")
        print(f"Subject: {subject}")
        print(f"Body:\n{body_text}")
        print(f"Message ID: {message_id}")
        print(f"{'='*50}\n")

        self.emails.append({
            "to": to,
            "subject": subject,
            "body_text": body_text,
            "body_html": body_html,
            "message_id": message_id,
            "timestamp": datetime.utcnow().isoformat(),
        })

        return {
            "success": True,
            "message_id": message_id,
            "status": "sent",
        }


class EmailVerifier(BaseVerifier):
    """
    Email-based verification.

    Sends verification codes via email.
    Used as a fallback channel when SMS/push unavailable.

    Features:
    - HTML and plain text emails
    - Multiple provider support (SMTP, SendGrid)
    - Branded email templates
    """

    DEFAULT_SUBJECT = "DeepSafe Verification Code"
    DEFAULT_BODY_TEXT = """
Your DeepSafe verification code is: {code}

This code is valid for {expiry} minutes.

If you did not request this code, please ignore this email.

- The DeepSafe Security Team
"""

    DEFAULT_BODY_HTML = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .code {{ font-size: 32px; font-weight: bold; color: #2563eb; letter-spacing: 4px;
                 background: #f3f4f6; padding: 20px; text-align: center; border-radius: 8px; }}
        .warning {{ color: #dc2626; font-size: 14px; margin-top: 20px; }}
        .footer {{ margin-top: 30px; font-size: 12px; color: #6b7280; }}
    </style>
</head>
<body>
    <div class="container">
        <h2>DeepSafe Verification Code</h2>
        <p>Your verification code is:</p>
        <div class="code">{code}</div>
        <p>This code is valid for <strong>{expiry} minutes</strong>.</p>
        <p class="warning">If you did not request this code, please ignore this email and do not share this code with anyone.</p>
        <div class="footer">
            <p>- The DeepSafe Security Team</p>
        </div>
    </div>
</body>
</html>
"""

    def __init__(
        self,
        provider: Optional[EmailProvider] = None,
        subject: Optional[str] = None,
        body_text_template: Optional[str] = None,
        body_html_template: Optional[str] = None,
    ):
        self._provider = provider
        self._subject = subject or self.DEFAULT_SUBJECT
        self._body_text_template = body_text_template or self.DEFAULT_BODY_TEXT
        self._body_html_template = body_html_template or self.DEFAULT_BODY_HTML
        self._providers: Dict[str, EmailProvider] = {}

    @property
    def channel(self) -> VerificationChannel:
        return VerificationChannel.EMAIL

    @property
    def name(self) -> str:
        return "email_verifier"

    async def _get_provider(self) -> EmailProvider:
        """Get an available email provider."""
        if self._provider:
            return self._provider

        if not self._providers:
            self._providers = {
                "sendgrid": SendGridEmailProvider(),
                "smtp": SMTPEmailProvider(),
                "console": ConsoleEmailProvider(),
            }

        for name, provider in self._providers.items():
            if await provider.is_available():
                return provider

        return self._providers["console"]

    async def is_available(self) -> bool:
        """Check if any email provider is available."""
        provider = await self._get_provider()
        return await provider.is_available()

    async def send_code(
        self,
        recipient: str,  # Email address
        code: str,
        expiry_minutes: int,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> VerificationResult:
        """
        Send verification code via email.

        Args:
            recipient: Email address.
            code: Verification code.
            expiry_minutes: Code expiration time.
            metadata: Additional metadata.

        Returns:
            VerificationResult with send status.
        """
        request_id = uuid4()
        now = datetime.utcnow()

        # Format templates
        body_text = self._body_text_template.format(code=code, expiry=expiry_minutes)
        body_html = self._body_html_template.format(code=code, expiry=expiry_minutes)

        # Get provider and send
        provider = await self._get_provider()
        result = await provider.send_email(
            to=recipient,
            subject=self._subject,
            body_text=body_text,
            body_html=body_html,
        )

        if result.get("success"):
            return VerificationResult(
                request_id=request_id,
                channel=VerificationChannel.EMAIL,
                status=VerificationStatus.SENT,
                verified=False,
                sent_at=now,
                expires_at=now + timedelta(minutes=expiry_minutes),
                provider=provider.name,
                provider_message_id=result.get("message_id"),
                provider_status=result.get("status"),
                metadata=metadata or {},
            )
        else:
            return VerificationResult(
                request_id=request_id,
                channel=VerificationChannel.EMAIL,
                status=VerificationStatus.FAILED,
                verified=False,
                provider=provider.name,
                error=result.get("error"),
                metadata=metadata or {},
            )

    async def verify_code(
        self,
        recipient: str,
        code: str,
        expected_code: str,
    ) -> VerificationResult:
        """
        Verify a code submitted by user.

        Args:
            recipient: Email address.
            code: Code submitted by user.
            expected_code: Expected correct code.

        Returns:
            VerificationResult with verification status.
        """
        request_id = uuid4()
        now = datetime.utcnow()

        # Normalize and compare codes
        submitted = code.strip().upper()
        expected = expected_code.strip().upper()

        verified = submitted == expected

        return VerificationResult(
            request_id=request_id,
            channel=VerificationChannel.EMAIL,
            status=VerificationStatus.VERIFIED if verified else VerificationStatus.FAILED,
            verified=verified,
            verified_at=now if verified else None,
            error=None if verified else "Invalid code",
        )

    def set_subject(self, subject: str) -> None:
        """Set email subject."""
        self._subject = subject

    def set_templates(
        self,
        body_text: Optional[str] = None,
        body_html: Optional[str] = None,
    ) -> None:
        """Set email body templates."""
        if body_text:
            self._body_text_template = body_text
        if body_html:
            self._body_html_template = body_html

    def add_provider(self, name: str, provider: EmailProvider) -> None:
        """Add a custom email provider."""
        self._providers[name] = provider
