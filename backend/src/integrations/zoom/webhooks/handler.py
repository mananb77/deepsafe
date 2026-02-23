"""
Zoom Webhook Handler

Processes webhook events from Zoom:
- Meeting events (started, ended, participant joined/left)
- Recording events
- User events
- App events

Webhook Documentation:
https://developers.zoom.us/docs/api/rest/webhook-reference/
"""

import hashlib
import hmac
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Union

from src.shared.config import get_settings


logger = logging.getLogger(__name__)


class ZoomWebhookEvent(str, Enum):
    """Zoom webhook event types."""

    # Meeting events
    MEETING_STARTED = "meeting.started"
    MEETING_ENDED = "meeting.ended"
    MEETING_PARTICIPANT_JOINED = "meeting.participant_joined"
    MEETING_PARTICIPANT_LEFT = "meeting.participant_left"
    MEETING_PARTICIPANT_WAITING = "meeting.participant_joined_waiting_room"
    MEETING_PARTICIPANT_ADMITTED = "meeting.participant_admitted"
    MEETING_HOST_CHANGED = "meeting.host_changed"
    MEETING_SHARING_STARTED = "meeting.sharing_started"
    MEETING_SHARING_ENDED = "meeting.sharing_ended"

    # Recording events
    RECORDING_STARTED = "recording.started"
    RECORDING_STOPPED = "recording.stopped"
    RECORDING_PAUSED = "recording.paused"
    RECORDING_RESUMED = "recording.resumed"
    RECORDING_COMPLETED = "recording.completed"
    RECORDING_TRANSCRIPT_COMPLETED = "recording.transcript_completed"

    # Webinar events (if applicable)
    WEBINAR_STARTED = "webinar.started"
    WEBINAR_ENDED = "webinar.ended"
    WEBINAR_PARTICIPANT_JOINED = "webinar.participant_joined"
    WEBINAR_PARTICIPANT_LEFT = "webinar.participant_left"

    # App events
    APP_DEAUTHORIZED = "app_deauthorized"

    # Endpoint validation
    ENDPOINT_URL_VALIDATION = "endpoint.url_validation"


@dataclass
class ZoomWebhookPayload:
    """
    Parsed Zoom webhook payload.

    Provides structured access to webhook data.
    """
    event: str
    event_ts: int  # Unix timestamp in milliseconds
    payload: Dict[str, Any]

    # Parsed fields
    account_id: str = ""
    object_type: str = ""  # "meeting", "recording", "user", etc.
    object_id: str = ""  # Meeting ID, user ID, etc.

    # Meeting-specific
    meeting_id: Optional[str] = None
    meeting_uuid: Optional[str] = None
    host_id: Optional[str] = None
    topic: Optional[str] = None

    # Participant-specific
    participant_user_id: Optional[str] = None
    participant_user_name: Optional[str] = None
    participant_id: Optional[str] = None
    participant_email: Optional[str] = None

    # Recording-specific
    recording_id: Optional[str] = None
    recording_file_type: Optional[str] = None
    recording_download_url: Optional[str] = None

    # Raw data
    raw_payload: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_request(cls, data: Dict[str, Any]) -> "ZoomWebhookPayload":
        """
        Create payload from webhook request body.

        Args:
            data: Raw webhook request JSON body.

        Returns:
            Parsed ZoomWebhookPayload.
        """
        event = data.get("event", "")
        event_ts = data.get("event_ts", 0)
        payload = data.get("payload", {})

        # Extract common fields
        account_id = payload.get("account_id", "")
        obj = payload.get("object", {})

        # Determine object type and ID
        object_type = ""
        object_id = ""

        if "meeting" in event:
            object_type = "meeting"
            object_id = str(obj.get("id", ""))
        elif "recording" in event:
            object_type = "recording"
            object_id = str(obj.get("meeting_id", ""))
        elif "webinar" in event:
            object_type = "webinar"
            object_id = str(obj.get("id", ""))
        elif "user" in event:
            object_type = "user"
            object_id = str(obj.get("id", ""))

        # Extract meeting info
        meeting_id = None
        meeting_uuid = None
        host_id = None
        topic = None

        if object_type in ("meeting", "recording", "webinar"):
            meeting_id = str(obj.get("id", ""))
            meeting_uuid = obj.get("uuid")
            host_id = obj.get("host_id")
            topic = obj.get("topic")

        # Extract participant info
        participant_user_id = None
        participant_user_name = None
        participant_id = None
        participant_email = None

        participant = obj.get("participant", {})
        if participant:
            participant_user_id = participant.get("user_id") or participant.get("id")
            participant_user_name = participant.get("user_name") or participant.get("name")
            participant_id = participant.get("participant_id")
            participant_email = participant.get("email")

        # Extract recording info
        recording_id = None
        recording_file_type = None
        recording_download_url = None

        if object_type == "recording":
            recording_files = obj.get("recording_files", [])
            if recording_files:
                recording_file = recording_files[0]
                recording_id = recording_file.get("id")
                recording_file_type = recording_file.get("file_type")
                recording_download_url = recording_file.get("download_url")

        return cls(
            event=event,
            event_ts=event_ts,
            payload=payload,
            account_id=account_id,
            object_type=object_type,
            object_id=object_id,
            meeting_id=meeting_id,
            meeting_uuid=meeting_uuid,
            host_id=host_id,
            topic=topic,
            participant_user_id=participant_user_id,
            participant_user_name=participant_user_name,
            participant_id=participant_id,
            participant_email=participant_email,
            recording_id=recording_id,
            recording_file_type=recording_file_type,
            recording_download_url=recording_download_url,
            raw_payload=data,
        )

    @property
    def event_datetime(self) -> datetime:
        """Get event timestamp as datetime."""
        return datetime.utcfromtimestamp(self.event_ts / 1000)

    @property
    def event_type(self) -> Optional[ZoomWebhookEvent]:
        """Get typed event enum."""
        try:
            return ZoomWebhookEvent(self.event)
        except ValueError:
            return None


# Type for webhook event handlers
WebhookHandler = Callable[[ZoomWebhookPayload], None]


class ZoomWebhookHandler:
    """
    Zoom webhook event handler.

    Validates and processes incoming Zoom webhooks.

    Usage:
        handler = ZoomWebhookHandler()

        @handler.on(ZoomWebhookEvent.MEETING_STARTED)
        async def handle_meeting_started(payload):
            print(f"Meeting started: {payload.meeting_id}")

        # In FastAPI route:
        @app.post("/webhook/zoom")
        async def zoom_webhook(request: Request):
            body = await request.body()
            headers = dict(request.headers)
            result = await handler.handle_webhook(body, headers)
            return result
    """

    def __init__(
        self,
        webhook_secret_token: Optional[str] = None,
        verification_token: Optional[str] = None,
    ):
        """
        Initialize webhook handler.

        Args:
            webhook_secret_token: Secret for webhook signature verification.
            verification_token: Token for endpoint URL validation.
        """
        settings = get_settings()
        self.webhook_secret_token = webhook_secret_token or settings.zoom.webhook_secret_token
        self.verification_token = verification_token or settings.zoom.verification_token

        # Event handlers
        self._handlers: Dict[ZoomWebhookEvent, List[WebhookHandler]] = {}
        self._default_handlers: List[WebhookHandler] = []

    def on(
        self,
        event: Union[ZoomWebhookEvent, str],
    ) -> Callable[[WebhookHandler], WebhookHandler]:
        """
        Decorator to register event handler.

        Args:
            event: Event type to handle.

        Returns:
            Decorator function.

        Usage:
            @handler.on(ZoomWebhookEvent.MEETING_STARTED)
            async def handle_meeting_started(payload):
                pass
        """
        def decorator(func: WebhookHandler) -> WebhookHandler:
            if isinstance(event, str):
                try:
                    event_enum = ZoomWebhookEvent(event)
                except ValueError:
                    logger.warning(f"Unknown event type: {event}")
                    return func
            else:
                event_enum = event

            if event_enum not in self._handlers:
                self._handlers[event_enum] = []
            self._handlers[event_enum].append(func)
            return func

        return decorator

    def on_any(self) -> Callable[[WebhookHandler], WebhookHandler]:
        """
        Decorator to register handler for all events.

        Returns:
            Decorator function.
        """
        def decorator(func: WebhookHandler) -> WebhookHandler:
            self._default_handlers.append(func)
            return func
        return decorator

    def verify_signature(
        self,
        payload: bytes,
        timestamp: str,
        signature: str,
    ) -> bool:
        """
        Verify webhook signature.

        Args:
            payload: Raw request body.
            timestamp: x-zm-request-timestamp header.
            signature: x-zm-signature header.

        Returns:
            True if signature is valid.
        """
        if not self.webhook_secret_token:
            logger.warning("Webhook secret not configured, skipping signature verification")
            return True

        # Construct message
        message = f"v0:{timestamp}:{payload.decode('utf-8')}"

        # Calculate expected signature
        expected = "v0=" + hmac.new(
            self.webhook_secret_token.encode(),
            message.encode(),
            hashlib.sha256,
        ).hexdigest()

        return hmac.compare_digest(expected, signature)

    def _handle_url_validation(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle endpoint URL validation event.

        Zoom sends this when setting up webhook endpoint.

        Args:
            payload: Webhook payload.

        Returns:
            Response with encrypted token.
        """
        plain_token = payload.get("payload", {}).get("plainToken", "")

        if not plain_token:
            logger.error("No plainToken in validation request")
            return {"error": "Missing plainToken"}

        if not self.webhook_secret_token:
            logger.error("Webhook secret not configured")
            return {"error": "Webhook secret not configured"}

        # Create encrypted token
        encrypted_token = hmac.new(
            self.webhook_secret_token.encode(),
            plain_token.encode(),
            hashlib.sha256,
        ).hexdigest()

        return {
            "plainToken": plain_token,
            "encryptedToken": encrypted_token,
        }

    async def handle_webhook(
        self,
        body: bytes,
        headers: Dict[str, str],
    ) -> Dict[str, Any]:
        """
        Handle incoming webhook request.

        Args:
            body: Raw request body.
            headers: Request headers.

        Returns:
            Response dict (status and optional data).
        """
        # Parse payload
        try:
            data = json.loads(body)
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in webhook: {e}")
            return {"status": "error", "message": "Invalid JSON"}

        event = data.get("event", "")
        logger.info(f"Received Zoom webhook: {event}")

        # Handle URL validation
        if event == ZoomWebhookEvent.ENDPOINT_URL_VALIDATION.value:
            return self._handle_url_validation(data)

        # Verify signature (skip for URL validation)
        timestamp = headers.get("x-zm-request-timestamp", "")
        signature = headers.get("x-zm-signature", "")

        if signature and not self.verify_signature(body, timestamp, signature):
            logger.warning("Invalid webhook signature")
            return {"status": "error", "message": "Invalid signature"}

        # Parse payload
        payload = ZoomWebhookPayload.from_request(data)

        # Call handlers
        await self._dispatch_event(payload)

        return {"status": "success"}

    async def _dispatch_event(self, payload: ZoomWebhookPayload) -> None:
        """
        Dispatch event to registered handlers.

        Args:
            payload: Parsed webhook payload.
        """
        # Call default handlers first
        for handler in self._default_handlers:
            try:
                result = handler(payload)
                if hasattr(result, "__await__"):
                    await result
            except Exception as e:
                logger.error(f"Default handler error: {e}")

        # Call event-specific handlers
        event_type = payload.event_type
        if event_type and event_type in self._handlers:
            for handler in self._handlers[event_type]:
                try:
                    result = handler(payload)
                    if hasattr(result, "__await__"):
                        await result
                except Exception as e:
                    logger.error(f"Handler error for {event_type}: {e}")

    # ==================== Convenience Methods ====================

    def get_registered_events(self) -> List[ZoomWebhookEvent]:
        """Get list of events with registered handlers."""
        return list(self._handlers.keys())

    def clear_handlers(self) -> None:
        """Remove all registered handlers."""
        self._handlers.clear()
        self._default_handlers.clear()


# ==================== Event Handler Helpers ====================

def extract_meeting_info(payload: ZoomWebhookPayload) -> Dict[str, Any]:
    """
    Extract meeting information from webhook payload.

    Args:
        payload: Webhook payload.

    Returns:
        Dict with meeting details.
    """
    return {
        "meeting_id": payload.meeting_id,
        "meeting_uuid": payload.meeting_uuid,
        "host_id": payload.host_id,
        "topic": payload.topic,
        "account_id": payload.account_id,
    }


def extract_participant_info(payload: ZoomWebhookPayload) -> Dict[str, Any]:
    """
    Extract participant information from webhook payload.

    Args:
        payload: Webhook payload.

    Returns:
        Dict with participant details.
    """
    return {
        "user_id": payload.participant_user_id,
        "user_name": payload.participant_user_name,
        "participant_id": payload.participant_id,
        "email": payload.participant_email,
    }
