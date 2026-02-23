"""Tests for Zoom webhook handlers."""

import hashlib
import hmac
import json
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.integrations.zoom.webhooks.handler import (
    ZoomWebhookEvent,
    ZoomWebhookPayload,
    ZoomWebhookHandler,
    extract_meeting_info,
    extract_participant_info,
)


class TestZoomWebhookEvent:
    """Tests for ZoomWebhookEvent enum."""

    def test_meeting_events(self):
        """Test meeting event values."""
        assert ZoomWebhookEvent.MEETING_STARTED.value == "meeting.started"
        assert ZoomWebhookEvent.MEETING_ENDED.value == "meeting.ended"
        assert ZoomWebhookEvent.MEETING_PARTICIPANT_JOINED.value == "meeting.participant_joined"
        assert ZoomWebhookEvent.MEETING_PARTICIPANT_LEFT.value == "meeting.participant_left"

    def test_recording_events(self):
        """Test recording event values."""
        assert ZoomWebhookEvent.RECORDING_STARTED.value == "recording.started"
        assert ZoomWebhookEvent.RECORDING_COMPLETED.value == "recording.completed"

    def test_webinar_events(self):
        """Test webinar event values."""
        assert ZoomWebhookEvent.WEBINAR_STARTED.value == "webinar.started"
        assert ZoomWebhookEvent.WEBINAR_ENDED.value == "webinar.ended"

    def test_app_events(self):
        """Test app event values."""
        assert ZoomWebhookEvent.APP_DEAUTHORIZED.value == "app_deauthorized"

    def test_url_validation_event(self):
        """Test URL validation event."""
        assert ZoomWebhookEvent.ENDPOINT_URL_VALIDATION.value == "endpoint.url_validation"


class TestZoomWebhookPayload:
    """Tests for ZoomWebhookPayload dataclass."""

    def test_from_meeting_started_request(self):
        """Test parsing meeting started webhook."""
        data = {
            "event": "meeting.started",
            "event_ts": 1609459200000,
            "payload": {
                "account_id": "account_123",
                "object": {
                    "id": "123456789",
                    "uuid": "abc123==",
                    "host_id": "host_123",
                    "topic": "Test Meeting",
                },
            },
        }

        payload = ZoomWebhookPayload.from_request(data)

        assert payload.event == "meeting.started"
        assert payload.event_ts == 1609459200000
        assert payload.account_id == "account_123"
        assert payload.object_type == "meeting"
        assert payload.meeting_id == "123456789"
        assert payload.meeting_uuid == "abc123=="
        assert payload.host_id == "host_123"
        assert payload.topic == "Test Meeting"

    def test_from_participant_joined_request(self):
        """Test parsing participant joined webhook."""
        data = {
            "event": "meeting.participant_joined",
            "event_ts": 1609459200000,
            "payload": {
                "account_id": "account_123",
                "object": {
                    "id": "123456789",
                    "uuid": "abc123==",
                    "participant": {
                        "user_id": "user_456",
                        "user_name": "John Doe",
                        "participant_id": "p_789",
                        "email": "john@example.com",
                    },
                },
            },
        }

        payload = ZoomWebhookPayload.from_request(data)

        assert payload.event == "meeting.participant_joined"
        assert payload.participant_user_id == "user_456"
        assert payload.participant_user_name == "John Doe"
        assert payload.participant_id == "p_789"
        assert payload.participant_email == "john@example.com"

    def test_from_recording_completed_request(self):
        """Test parsing recording completed webhook."""
        data = {
            "event": "recording.completed",
            "event_ts": 1609459200000,
            "payload": {
                "account_id": "account_123",
                "object": {
                    "meeting_id": "123456789",
                    "uuid": "abc123==",
                    "recording_files": [
                        {
                            "id": "rec_123",
                            "file_type": "MP4",
                            "download_url": "https://zoom.us/recording/123",
                        },
                    ],
                },
            },
        }

        payload = ZoomWebhookPayload.from_request(data)

        assert payload.event == "recording.completed"
        assert payload.object_type == "recording"
        assert payload.recording_id == "rec_123"
        assert payload.recording_file_type == "MP4"
        assert payload.recording_download_url == "https://zoom.us/recording/123"

    def test_event_datetime_property(self):
        """Test event_datetime conversion."""
        data = {
            "event": "meeting.started",
            "event_ts": 1609459200000,  # 2021-01-01 00:00:00 UTC
            "payload": {},
        }

        payload = ZoomWebhookPayload.from_request(data)
        dt = payload.event_datetime

        assert dt.year == 2021
        assert dt.month == 1
        assert dt.day == 1

    def test_event_type_property_valid(self):
        """Test event_type for valid event."""
        data = {
            "event": "meeting.started",
            "event_ts": 1609459200000,
            "payload": {},
        }

        payload = ZoomWebhookPayload.from_request(data)
        assert payload.event_type == ZoomWebhookEvent.MEETING_STARTED

    def test_event_type_property_unknown(self):
        """Test event_type for unknown event."""
        data = {
            "event": "unknown.event",
            "event_ts": 1609459200000,
            "payload": {},
        }

        payload = ZoomWebhookPayload.from_request(data)
        assert payload.event_type is None


class TestZoomWebhookHandler:
    """Tests for ZoomWebhookHandler class."""

    @pytest.fixture
    def handler(self):
        """Create handler for testing."""
        with patch("src.integrations.zoom.webhooks.handler.get_settings") as mock:
            mock.return_value.zoom.webhook_secret_token = "test_secret"
            mock.return_value.zoom.verification_token = "test_verification"
            return ZoomWebhookHandler()

    def test_initialization(self, handler):
        """Test handler initialization."""
        assert handler.webhook_secret_token == "test_secret"
        assert handler.verification_token == "test_verification"

    def test_initialization_with_params(self):
        """Test handler initialization with explicit params."""
        handler = ZoomWebhookHandler(
            webhook_secret_token="explicit_secret",
            verification_token="explicit_verification",
        )
        assert handler.webhook_secret_token == "explicit_secret"
        assert handler.verification_token == "explicit_verification"

    def test_verify_signature_valid(self, handler):
        """Test signature verification with valid signature."""
        payload = b'{"event": "meeting.started"}'
        timestamp = "1609459200"

        # Generate valid signature
        message = f"v0:{timestamp}:{payload.decode('utf-8')}"
        expected = "v0=" + hmac.new(
            b"test_secret",
            message.encode(),
            hashlib.sha256,
        ).hexdigest()

        result = handler.verify_signature(payload, timestamp, expected)
        assert result is True

    def test_verify_signature_invalid(self, handler):
        """Test signature verification with invalid signature."""
        payload = b'{"event": "meeting.started"}'
        timestamp = "1609459200"

        result = handler.verify_signature(payload, timestamp, "v0=invalid_signature")
        assert result is False

    def test_verify_signature_no_secret(self):
        """Test signature verification without secret configured."""
        handler = ZoomWebhookHandler(webhook_secret_token=None)
        result = handler.verify_signature(b"payload", "timestamp", "signature")
        assert result is True  # Skips verification

    def test_on_decorator(self, handler):
        """Test event handler registration with decorator."""
        @handler.on(ZoomWebhookEvent.MEETING_STARTED)
        def handle_meeting_started(payload):
            pass

        assert ZoomWebhookEvent.MEETING_STARTED in handler._handlers
        assert len(handler._handlers[ZoomWebhookEvent.MEETING_STARTED]) == 1

    def test_on_decorator_string_event(self, handler):
        """Test event handler registration with string event."""
        @handler.on("meeting.started")
        def handle_meeting_started(payload):
            pass

        assert ZoomWebhookEvent.MEETING_STARTED in handler._handlers

    def test_on_any_decorator(self, handler):
        """Test default handler registration."""
        @handler.on_any()
        def handle_any(payload):
            pass

        assert len(handler._default_handlers) == 1

    def test_get_registered_events(self, handler):
        """Test getting registered events."""
        @handler.on(ZoomWebhookEvent.MEETING_STARTED)
        def handle1(payload):
            pass

        @handler.on(ZoomWebhookEvent.MEETING_ENDED)
        def handle2(payload):
            pass

        events = handler.get_registered_events()
        assert ZoomWebhookEvent.MEETING_STARTED in events
        assert ZoomWebhookEvent.MEETING_ENDED in events

    def test_clear_handlers(self, handler):
        """Test clearing handlers."""
        @handler.on(ZoomWebhookEvent.MEETING_STARTED)
        def handle(payload):
            pass

        @handler.on_any()
        def handle_any(payload):
            pass

        handler.clear_handlers()

        assert len(handler._handlers) == 0
        assert len(handler._default_handlers) == 0

    @pytest.mark.asyncio
    async def test_handle_webhook_url_validation(self, handler):
        """Test handling URL validation webhook."""
        body = json.dumps({
            "event": "endpoint.url_validation",
            "payload": {
                "plainToken": "test_plain_token",
            },
        }).encode()

        result = await handler.handle_webhook(body, {})

        assert "plainToken" in result
        assert "encryptedToken" in result
        assert result["plainToken"] == "test_plain_token"

    @pytest.mark.asyncio
    async def test_handle_webhook_invalid_json(self, handler):
        """Test handling invalid JSON."""
        body = b"not valid json"

        result = await handler.handle_webhook(body, {})

        assert result["status"] == "error"
        assert "Invalid JSON" in result["message"]

    @pytest.mark.asyncio
    async def test_handle_webhook_invalid_signature(self, handler):
        """Test handling webhook with invalid signature."""
        body = json.dumps({
            "event": "meeting.started",
            "event_ts": 1609459200000,
            "payload": {},
        }).encode()

        headers = {
            "x-zm-request-timestamp": "1609459200",
            "x-zm-signature": "v0=invalid",
        }

        result = await handler.handle_webhook(body, headers)

        assert result["status"] == "error"
        assert "Invalid signature" in result["message"]

    @pytest.mark.asyncio
    async def test_handle_webhook_dispatches_event(self, handler):
        """Test that webhook dispatches to registered handlers."""
        handled_payloads = []

        @handler.on(ZoomWebhookEvent.MEETING_STARTED)
        async def handle_meeting_started(payload):
            handled_payloads.append(payload)

        body = json.dumps({
            "event": "meeting.started",
            "event_ts": 1609459200000,
            "payload": {
                "account_id": "account_123",
                "object": {"id": "123456789"},
            },
        }).encode()

        # Generate valid signature
        timestamp = "1609459200"
        message = f"v0:{timestamp}:{body.decode('utf-8')}"
        signature = "v0=" + hmac.new(
            b"test_secret",
            message.encode(),
            hashlib.sha256,
        ).hexdigest()

        headers = {
            "x-zm-request-timestamp": timestamp,
            "x-zm-signature": signature,
        }

        result = await handler.handle_webhook(body, headers)

        assert result["status"] == "success"
        assert len(handled_payloads) == 1
        assert handled_payloads[0].event == "meeting.started"

    @pytest.mark.asyncio
    async def test_handle_webhook_calls_default_handlers(self, handler):
        """Test that webhook calls default handlers."""
        default_called = []

        @handler.on_any()
        async def handle_any(payload):
            default_called.append(payload)

        body = json.dumps({
            "event": "meeting.started",
            "event_ts": 1609459200000,
            "payload": {},
        }).encode()

        # Skip signature verification by not providing signature header
        result = await handler.handle_webhook(body, {})

        assert len(default_called) == 1


class TestHelperFunctions:
    """Tests for helper functions."""

    def test_extract_meeting_info(self):
        """Test extracting meeting info from payload."""
        data = {
            "event": "meeting.started",
            "event_ts": 1609459200000,
            "payload": {
                "account_id": "account_123",
                "object": {
                    "id": "123456789",
                    "uuid": "abc123==",
                    "host_id": "host_123",
                    "topic": "Test Meeting",
                },
            },
        }

        payload = ZoomWebhookPayload.from_request(data)
        info = extract_meeting_info(payload)

        assert info["meeting_id"] == "123456789"
        assert info["meeting_uuid"] == "abc123=="
        assert info["host_id"] == "host_123"
        assert info["topic"] == "Test Meeting"
        assert info["account_id"] == "account_123"

    def test_extract_participant_info(self):
        """Test extracting participant info from payload."""
        data = {
            "event": "meeting.participant_joined",
            "event_ts": 1609459200000,
            "payload": {
                "account_id": "account_123",
                "object": {
                    "id": "123456789",
                    "participant": {
                        "user_id": "user_456",
                        "user_name": "John Doe",
                        "participant_id": "p_789",
                        "email": "john@example.com",
                    },
                },
            },
        }

        payload = ZoomWebhookPayload.from_request(data)
        info = extract_participant_info(payload)

        assert info["user_id"] == "user_456"
        assert info["user_name"] == "John Doe"
        assert info["participant_id"] == "p_789"
        assert info["email"] == "john@example.com"
