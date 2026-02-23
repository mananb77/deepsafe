"""
Voice Callback Verifier

Automated voice calls for high-value/high-risk verification.
Supports:
- Twilio Voice API
- Plivo Voice API
- Console mock (development)
"""

from abc import ABC, abstractmethod
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


class VoiceProvider(ABC):
    """Base class for voice call providers."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Provider name."""
        pass

    @abstractmethod
    async def make_call(
        self,
        to: str,
        message: str,
        from_number: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Make automated voice call.

        Returns dict with:
        - success: bool
        - call_id: Optional[str]
        - error: Optional[str]
        """
        pass

    @abstractmethod
    async def is_available(self) -> bool:
        """Check if provider is configured and available."""
        pass


class TwilioVoiceProvider(VoiceProvider):
    """Twilio Voice provider."""

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

    async def make_call(
        self,
        to: str,
        message: str,
        from_number: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Make voice call via Twilio."""
        if not await self.is_available():
            return {
                "success": False,
                "error": "Twilio not configured",
            }

        try:
            from twilio.rest import Client
            from twilio.twiml.voice_response import VoiceResponse

            if self._client is None:
                self._client = Client(self.account_sid, self.auth_token)

            # Create TwiML for the call
            response = VoiceResponse()
            response.say(message, voice='alice', language='en-US')
            response.pause(length=1)
            response.say(message, voice='alice', language='en-US')  # Repeat once

            # Make the call using TwiML bin or inline TwiML
            # For production, you'd use a webhook URL
            call = self._client.calls.create(
                twiml=str(response),
                from_=from_number or self.from_number,
                to=to,
            )

            return {
                "success": True,
                "call_id": call.sid,
                "status": call.status,
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


class PlivoVoiceProvider(VoiceProvider):
    """Plivo Voice provider."""

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

    async def make_call(
        self,
        to: str,
        message: str,
        from_number: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Make voice call via Plivo."""
        if not await self.is_available():
            return {
                "success": False,
                "error": "Plivo not configured",
            }

        try:
            import plivo

            if self._client is None:
                self._client = plivo.RestClient(self.auth_id, self.auth_token)

            # Plivo uses XML for call flow
            # For production, you'd host this XML at a URL
            # This is a simplified version using speak URL
            response = self._client.calls.create(
                from_=from_number or self.from_number,
                to_=to,
                answer_url=f"https://s3.amazonaws.com/plivosamplexml/speak.xml",
                answer_method="GET",
            )

            return {
                "success": True,
                "call_id": response.request_uuid,
                "status": "initiated",
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


class ConsoleVoiceProvider(VoiceProvider):
    """
    Console voice provider for development/testing.

    Prints call details to console instead of making actual call.
    """

    def __init__(self):
        self.calls: list = []

    @property
    def name(self) -> str:
        return "console"

    async def is_available(self) -> bool:
        """Console provider is always available."""
        return True

    async def make_call(
        self,
        to: str,
        message: str,
        from_number: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Print call details to console."""
        call_id = str(uuid4())

        print(f"\n{'='*50}")
        print(f"VOICE VERIFICATION CALL (Console Mode)")
        print(f"{'='*50}")
        print(f"To: {to}")
        print(f"From: {from_number or 'DeepSafe'}")
        print(f"Message: {message}")
        print(f"Call ID: {call_id}")
        print(f"{'='*50}\n")

        self.calls.append({
            "to": to,
            "message": message,
            "call_id": call_id,
            "timestamp": datetime.utcnow().isoformat(),
        })

        return {
            "success": True,
            "call_id": call_id,
            "status": "completed",
        }


class VoiceVerifier(BaseVerifier):
    """
    Voice callback verification.

    Makes automated phone calls to verify user identity.
    Used for high-value transactions and critical risk situations.

    Features:
    - Text-to-speech verification code
    - Code is repeated for clarity
    - DTMF input support for code entry (future)
    """

    DEFAULT_TEMPLATE = (
        "Hello, this is DeepSafe calling with a verification code. "
        "Your verification code is: {code_spoken}. "
        "I repeat, your verification code is: {code_spoken}. "
        "This code is valid for {expiry} minutes. "
        "Thank you."
    )

    def __init__(
        self,
        provider: Optional[VoiceProvider] = None,
        template: Optional[str] = None,
    ):
        self._provider = provider
        self._template = template or self.DEFAULT_TEMPLATE
        self._providers: Dict[str, VoiceProvider] = {}

    @property
    def channel(self) -> VerificationChannel:
        return VerificationChannel.VOICE

    @property
    def name(self) -> str:
        return "voice_verifier"

    async def _get_provider(self) -> VoiceProvider:
        """Get an available voice provider."""
        if self._provider:
            return self._provider

        if not self._providers:
            self._providers = {
                "twilio": TwilioVoiceProvider(),
                "plivo": PlivoVoiceProvider(),
                "console": ConsoleVoiceProvider(),
            }

        for name, provider in self._providers.items():
            if await provider.is_available():
                return provider

        return self._providers["console"]

    async def is_available(self) -> bool:
        """Check if any voice provider is available."""
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
        Make verification call with code.

        Args:
            recipient: Phone number.
            code: Verification code.
            expiry_minutes: Code expiration time.
            metadata: Additional metadata.

        Returns:
            VerificationResult with call status.
        """
        request_id = uuid4()
        now = datetime.utcnow()

        # Normalize phone number
        phone = self._normalize_phone(recipient)

        # Format code for speech (spell out each digit)
        code_spoken = self._format_code_for_speech(code)

        # Format message
        message = self._template.format(
            code_spoken=code_spoken,
            code=code,
            expiry=expiry_minutes,
        )

        # Get provider and make call
        provider = await self._get_provider()
        result = await provider.make_call(to=phone, message=message)

        if result.get("success"):
            return VerificationResult(
                request_id=request_id,
                channel=VerificationChannel.VOICE,
                status=VerificationStatus.SENT,
                verified=False,
                sent_at=now,
                expires_at=now + timedelta(minutes=expiry_minutes),
                provider=provider.name,
                provider_message_id=result.get("call_id"),
                provider_status=result.get("status"),
                metadata=metadata or {},
            )
        else:
            return VerificationResult(
                request_id=request_id,
                channel=VerificationChannel.VOICE,
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

        # Normalize and compare codes
        submitted = code.strip().upper()
        expected = expected_code.strip().upper()

        verified = submitted == expected

        return VerificationResult(
            request_id=request_id,
            channel=VerificationChannel.VOICE,
            status=VerificationStatus.VERIFIED if verified else VerificationStatus.FAILED,
            verified=verified,
            verified_at=now if verified else None,
            error=None if verified else "Invalid code",
        )

    def _normalize_phone(self, phone: str) -> str:
        """Normalize phone number to E.164 format."""
        if phone.startswith('+'):
            digits = '+' + ''.join(c for c in phone[1:] if c.isdigit())
        else:
            digits = ''.join(c for c in phone if c.isdigit())

        if not digits.startswith('+'):
            if len(digits) == 10:
                digits = '+1' + digits
            elif len(digits) == 11 and digits.startswith('1'):
                digits = '+' + digits
            else:
                digits = '+' + digits

        return digits

    def _format_code_for_speech(self, code: str) -> str:
        """
        Format verification code for text-to-speech.

        Spells out each character for clarity.
        Example: "123456" -> "1, 2, 3, 4, 5, 6"
        """
        # Spell out each character with pauses
        return ", ".join(list(code))

    def set_template(self, template: str) -> None:
        """Set custom call script template."""
        self._template = template

    def add_provider(self, name: str, provider: VoiceProvider) -> None:
        """Add a custom voice provider."""
        self._providers[name] = provider
