"""
SMS Verifier

Multi-provider SMS verification supporting:
- Twilio (primary commercial)
- Plivo (cost-effective alternative)
- Console/Mock (development)
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, Optional
from uuid import uuid4

from src.shared.config import get_settings
from src.services.verification.base import (
    BaseVerifier,
    VerificationChannel,
    VerificationResult,
    VerificationStatus,
)


class SMSProvider(ABC):
    """Base class for SMS providers."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Provider name."""
        pass

    @abstractmethod
    async def send_sms(
        self,
        to: str,
        message: str,
        from_number: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Send SMS message.

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


class TwilioSMSProvider(SMSProvider):
    """Twilio SMS provider."""

    def __init__(
        self,
        account_sid: Optional[str] = None,
        auth_token: Optional[str] = None,
        from_number: Optional[str] = None,
    ):
        settings = get_settings()
        self.account_sid = account_sid or settings.twilio.account_sid
        self.auth_token = auth_token or settings.twilio.auth_token
        self.from_number = from_number or settings.twilio.phone_number
        self._client = None

    @property
    def name(self) -> str:
        return "twilio"

    async def is_available(self) -> bool:
        """Check if Twilio is configured."""
        return bool(self.account_sid and self.auth_token and self.from_number)

    async def send_sms(
        self,
        to: str,
        message: str,
        from_number: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Send SMS via Twilio."""
        if not await self.is_available():
            return {
                "success": False,
                "error": "Twilio not configured",
            }

        try:
            # Lazy import to avoid dependency if not using Twilio
            from twilio.rest import Client

            if self._client is None:
                self._client = Client(self.account_sid, self.auth_token)

            msg = self._client.messages.create(
                body=message,
                from_=from_number or self.from_number,
                to=to,
            )

            return {
                "success": True,
                "message_id": msg.sid,
                "status": msg.status,
            }

        except ImportError:
            return {
                "success": False,
                "error": "twilio package not installed",
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }


class PlivoSMSProvider(SMSProvider):
    """Plivo SMS provider (cost-effective alternative)."""

    def __init__(
        self,
        auth_id: Optional[str] = None,
        auth_token: Optional[str] = None,
        from_number: Optional[str] = None,
    ):
        settings = get_settings()
        self.auth_id = auth_id or getattr(settings, 'plivo_auth_id', None)
        self.auth_token = auth_token or getattr(settings, 'plivo_auth_token', None)
        self.from_number = from_number or getattr(settings, 'plivo_phone_number', None)
        self._client = None

    @property
    def name(self) -> str:
        return "plivo"

    async def is_available(self) -> bool:
        """Check if Plivo is configured."""
        return bool(self.auth_id and self.auth_token and self.from_number)

    async def send_sms(
        self,
        to: str,
        message: str,
        from_number: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Send SMS via Plivo."""
        if not await self.is_available():
            return {
                "success": False,
                "error": "Plivo not configured",
            }

        try:
            import plivo

            if self._client is None:
                self._client = plivo.RestClient(self.auth_id, self.auth_token)

            response = self._client.messages.create(
                src=from_number or self.from_number,
                dst=to,
                text=message,
            )

            return {
                "success": True,
                "message_id": response.message_uuid[0] if response.message_uuid else None,
                "status": "sent",
            }

        except ImportError:
            return {
                "success": False,
                "error": "plivo package not installed",
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }


class ConsoleSMSProvider(SMSProvider):
    """
    Console SMS provider for development/testing.

    Prints SMS to console instead of sending.
    """

    def __init__(self):
        self.sent_messages: list = []

    @property
    def name(self) -> str:
        return "console"

    async def is_available(self) -> bool:
        """Console provider is always available."""
        return True

    async def send_sms(
        self,
        to: str,
        message: str,
        from_number: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Print SMS to console."""
        message_id = str(uuid4())

        print(f"\n{'='*50}")
        print(f"SMS VERIFICATION (Console Mode)")
        print(f"{'='*50}")
        print(f"To: {to}")
        print(f"From: {from_number or 'DeepSafe'}")
        print(f"Message: {message}")
        print(f"Message ID: {message_id}")
        print(f"{'='*50}\n")

        self.sent_messages.append({
            "to": to,
            "message": message,
            "message_id": message_id,
            "timestamp": datetime.utcnow().isoformat(),
        })

        return {
            "success": True,
            "message_id": message_id,
            "status": "sent",
        }


class SMSVerifier(BaseVerifier):
    """
    SMS verification with multi-provider support.

    Supports:
    - Twilio (commercial)
    - Plivo (cost-effective)
    - Console (development)

    Automatically falls back to available providers.
    """

    DEFAULT_TEMPLATE = "Your DeepSafe verification code is: {code}. Valid for {expiry} minutes. Do not share this code."

    def __init__(
        self,
        provider: Optional[SMSProvider] = None,
        template: Optional[str] = None,
    ):
        self._provider = provider
        self._template = template or self.DEFAULT_TEMPLATE
        self._providers: Dict[str, SMSProvider] = {}

    @property
    def channel(self) -> VerificationChannel:
        return VerificationChannel.SMS

    @property
    def name(self) -> str:
        return "sms_verifier"

    async def _get_provider(self) -> SMSProvider:
        """Get an available SMS provider."""
        if self._provider:
            return self._provider

        # Try providers in order of preference
        if not self._providers:
            self._providers = {
                "twilio": TwilioSMSProvider(),
                "plivo": PlivoSMSProvider(),
                "console": ConsoleSMSProvider(),
            }

        for name, provider in self._providers.items():
            if await provider.is_available():
                return provider

        # Fall back to console for development
        return self._providers["console"]

    async def is_available(self) -> bool:
        """Check if any SMS provider is available."""
        provider = await self._get_provider()
        return await provider.is_available()

    async def send_code(
        self,
        recipient: str,
        code: str,
        expiry_minutes: int,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> VerificationResult:
        """
        Send verification code via SMS.

        Args:
            recipient: Phone number (E.164 format preferred).
            code: Verification code.
            expiry_minutes: Code expiration time.
            metadata: Additional metadata.

        Returns:
            VerificationResult with send status.
        """
        request_id = uuid4()
        now = datetime.utcnow()

        # Normalize phone number
        phone = self._normalize_phone(recipient)

        # Format message
        message = self._template.format(code=code, expiry=expiry_minutes)

        # Get provider and send
        provider = await self._get_provider()
        result = await provider.send_sms(to=phone, message=message)

        if result.get("success"):
            return VerificationResult(
                request_id=request_id,
                channel=VerificationChannel.SMS,
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
                channel=VerificationChannel.SMS,
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
            recipient: Phone number.
            code: Code submitted by user.
            expected_code: Expected correct code.

        Returns:
            VerificationResult with verification status.
        """
        request_id = uuid4()
        now = datetime.utcnow()

        # Normalize and compare codes (case-insensitive)
        submitted = code.strip().upper()
        expected = expected_code.strip().upper()

        verified = submitted == expected

        return VerificationResult(
            request_id=request_id,
            channel=VerificationChannel.SMS,
            status=VerificationStatus.VERIFIED if verified else VerificationStatus.FAILED,
            verified=verified,
            verified_at=now if verified else None,
            error=None if verified else "Invalid code",
        )

    def _normalize_phone(self, phone: str) -> str:
        """
        Normalize phone number to E.164 format.

        Args:
            phone: Phone number in any format.

        Returns:
            Normalized phone number.
        """
        # Remove all non-digit characters except leading +
        if phone.startswith('+'):
            digits = '+' + ''.join(c for c in phone[1:] if c.isdigit())
        else:
            digits = ''.join(c for c in phone if c.isdigit())

        # Add US country code if no country code present
        if not digits.startswith('+'):
            if len(digits) == 10:
                digits = '+1' + digits
            elif len(digits) == 11 and digits.startswith('1'):
                digits = '+' + digits
            else:
                digits = '+' + digits

        return digits

    def set_template(self, template: str) -> None:
        """Set custom message template."""
        self._template = template

    def add_provider(self, name: str, provider: SMSProvider) -> None:
        """Add a custom SMS provider."""
        self._providers[name] = provider
