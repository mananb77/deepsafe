"""
Push Notification Verifier

Push notification verification via:
- Firebase Cloud Messaging (FCM)
- Apple Push Notification Service (APNs) via FCM
- Console mock (development)
"""

from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from uuid import uuid4

from src.shared.config import get_settings
from src.services.verification.base import (
    BaseVerifier,
    VerificationChannel,
    VerificationResult,
    VerificationStatus,
)


class PushProvider(ABC):
    """Base class for push notification providers."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Provider name."""
        pass

    @abstractmethod
    async def send_notification(
        self,
        device_token: str,
        title: str,
        body: str,
        data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Send push notification.

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


class FirebasePushProvider(PushProvider):
    """Firebase Cloud Messaging (FCM) provider."""

    def __init__(
        self,
        credentials_path: Optional[str] = None,
        project_id: Optional[str] = None,
    ):
        settings = get_settings()
        self.credentials_path = credentials_path or getattr(settings, 'firebase_credentials_path', None)
        self.project_id = project_id or getattr(settings, 'firebase_project_id', None)
        self._initialized = False

    @property
    def name(self) -> str:
        return "firebase"

    async def is_available(self) -> bool:
        """Check if Firebase is configured."""
        return bool(self.credentials_path or self.project_id)

    def _initialize(self):
        """Initialize Firebase Admin SDK."""
        if self._initialized:
            return

        try:
            import firebase_admin
            from firebase_admin import credentials

            if not firebase_admin._apps:
                if self.credentials_path:
                    cred = credentials.Certificate(self.credentials_path)
                    firebase_admin.initialize_app(cred)
                else:
                    # Use default credentials (e.g., on GCP)
                    firebase_admin.initialize_app()

            self._initialized = True
        except Exception:
            pass

    async def send_notification(
        self,
        device_token: str,
        title: str,
        body: str,
        data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Send push notification via FCM."""
        if not await self.is_available():
            return {
                "success": False,
                "error": "Firebase not configured",
            }

        try:
            from firebase_admin import messaging

            self._initialize()

            # Build message
            message = messaging.Message(
                notification=messaging.Notification(
                    title=title,
                    body=body,
                ),
                data={k: str(v) for k, v in (data or {}).items()},
                token=device_token,
                android=messaging.AndroidConfig(
                    priority="high",
                    notification=messaging.AndroidNotification(
                        click_action="VERIFY_ACTION",
                        priority="high",
                    ),
                ),
                apns=messaging.APNSConfig(
                    payload=messaging.APNSPayload(
                        aps=messaging.Aps(
                            alert=messaging.ApsAlert(
                                title=title,
                                body=body,
                            ),
                            badge=1,
                            sound="default",
                            category="VERIFICATION",
                        ),
                    ),
                ),
            )

            # Send message
            response = messaging.send(message)

            return {
                "success": True,
                "message_id": response,
                "status": "sent",
            }

        except ImportError:
            return {
                "success": False,
                "error": "firebase-admin package not installed",
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }


class ConsolePushProvider(PushProvider):
    """
    Console push provider for development/testing.

    Prints notification to console instead of sending.
    """

    def __init__(self):
        self.notifications: list = []

    @property
    def name(self) -> str:
        return "console"

    async def is_available(self) -> bool:
        """Console provider is always available."""
        return True

    async def send_notification(
        self,
        device_token: str,
        title: str,
        body: str,
        data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Print notification to console."""
        message_id = str(uuid4())

        print(f"\n{'='*50}")
        print(f"PUSH NOTIFICATION (Console Mode)")
        print(f"{'='*50}")
        print(f"Device Token: {device_token[:20]}..." if len(device_token) > 20 else f"Device Token: {device_token}")
        print(f"Title: {title}")
        print(f"Body: {body}")
        if data:
            print(f"Data: {data}")
        print(f"Message ID: {message_id}")
        print(f"{'='*50}\n")

        self.notifications.append({
            "device_token": device_token,
            "title": title,
            "body": body,
            "data": data,
            "message_id": message_id,
            "timestamp": datetime.utcnow().isoformat(),
        })

        return {
            "success": True,
            "message_id": message_id,
            "status": "sent",
        }


class PushVerifier(BaseVerifier):
    """
    Push notification verification.

    Sends verification codes via push notifications.
    Supports action buttons for quick verification.

    Features:
    - Firebase Cloud Messaging (Android + iOS)
    - Rich notifications with action buttons
    - Background delivery for reliability
    - Deep linking to verification screen
    """

    DEFAULT_TITLE = "DeepSafe Verification"
    DEFAULT_BODY = "Your verification code is: {code}. Tap to verify."

    def __init__(
        self,
        provider: Optional[PushProvider] = None,
        title: Optional[str] = None,
        body_template: Optional[str] = None,
    ):
        self._provider = provider
        self._title = title or self.DEFAULT_TITLE
        self._body_template = body_template or self.DEFAULT_BODY
        self._providers: Dict[str, PushProvider] = {}

    @property
    def channel(self) -> VerificationChannel:
        return VerificationChannel.PUSH

    @property
    def name(self) -> str:
        return "push_verifier"

    async def _get_provider(self) -> PushProvider:
        """Get an available push provider."""
        if self._provider:
            return self._provider

        if not self._providers:
            self._providers = {
                "firebase": FirebasePushProvider(),
                "console": ConsolePushProvider(),
            }

        for name, provider in self._providers.items():
            if await provider.is_available():
                return provider

        return self._providers["console"]

    async def is_available(self) -> bool:
        """Check if any push provider is available."""
        provider = await self._get_provider()
        return await provider.is_available()

    async def send_code(
        self,
        recipient: str,  # Device token
        code: str,
        expiry_minutes: int,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> VerificationResult:
        """
        Send verification code via push notification.

        Args:
            recipient: Device token (FCM token).
            code: Verification code.
            expiry_minutes: Code expiration time.
            metadata: Additional metadata.

        Returns:
            VerificationResult with send status.
        """
        request_id = uuid4()
        now = datetime.utcnow()

        # Format body
        body = self._body_template.format(code=code, expiry=expiry_minutes)

        # Build notification data
        data = {
            "type": "verification",
            "code": code,
            "expiry_minutes": str(expiry_minutes),
            "request_id": str(request_id),
            **(metadata or {}),
        }

        # Get provider and send
        provider = await self._get_provider()
        result = await provider.send_notification(
            device_token=recipient,
            title=self._title,
            body=body,
            data=data,
        )

        if result.get("success"):
            return VerificationResult(
                request_id=request_id,
                channel=VerificationChannel.PUSH,
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
                channel=VerificationChannel.PUSH,
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
            recipient: Device token.
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
            channel=VerificationChannel.PUSH,
            status=VerificationStatus.VERIFIED if verified else VerificationStatus.FAILED,
            verified=verified,
            verified_at=now if verified else None,
            error=None if verified else "Invalid code",
        )

    async def send_to_multiple(
        self,
        device_tokens: List[str],
        code: str,
        expiry_minutes: int,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> List[VerificationResult]:
        """
        Send verification to multiple devices.

        Useful when user has multiple devices registered.

        Args:
            device_tokens: List of FCM device tokens.
            code: Verification code.
            expiry_minutes: Code expiration time.
            metadata: Additional metadata.

        Returns:
            List of VerificationResult for each device.
        """
        results = []
        for token in device_tokens:
            result = await self.send_code(
                recipient=token,
                code=code,
                expiry_minutes=expiry_minutes,
                metadata=metadata,
            )
            results.append(result)
        return results

    def set_title(self, title: str) -> None:
        """Set notification title."""
        self._title = title

    def set_body_template(self, template: str) -> None:
        """Set notification body template."""
        self._body_template = template

    def add_provider(self, name: str, provider: PushProvider) -> None:
        """Add a custom push provider."""
        self._providers[name] = provider
