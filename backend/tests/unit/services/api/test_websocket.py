"""
WebSocket Tests

Unit tests for WebSocket functionality.
"""

import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

from src.services.api.websocket import (
    ConnectionManager,
    WebSocketMessage,
    risk_update_message,
    incident_detected_message,
    verification_required_message,
    participant_update_message,
    meeting_status_message,
    alert_message,
)


class TestWebSocketMessage:
    """Tests for WebSocketMessage model."""

    def test_message_has_timestamp(self):
        """Message includes timestamp if not provided."""
        msg = WebSocketMessage(type="test", data={"key": "value"})

        assert msg.timestamp is not None
        assert "Z" in msg.timestamp  # ISO format with Z suffix

    def test_message_preserves_timestamp(self):
        """Message preserves provided timestamp."""
        timestamp = "2025-12-17T10:30:00.000Z"
        msg = WebSocketMessage(type="test", data={}, timestamp=timestamp)

        assert msg.timestamp == timestamp

    def test_message_serialization(self):
        """Message serializes to dict correctly."""
        msg = WebSocketMessage(
            type="risk_update",
            data={"meeting_id": "123", "score": 75.5},
        )

        result = msg.model_dump()

        assert result["type"] == "risk_update"
        assert result["data"]["meeting_id"] == "123"
        assert result["data"]["score"] == 75.5
        assert "timestamp" in result


class TestMessageFactories:
    """Tests for message factory functions."""

    def test_risk_update_message(self):
        """Risk update message has correct structure."""
        msg = risk_update_message(
            meeting_id="meeting-123",
            risk_score=75.5,
            risk_level="high",
            participant_id="participant-456",
        )

        assert msg.type == "risk_update"
        assert msg.data["meeting_id"] == "meeting-123"
        assert msg.data["risk_score"] == 75.5
        assert msg.data["risk_level"] == "high"
        assert msg.data["participant_id"] == "participant-456"

    def test_incident_detected_message(self):
        """Incident detected message has correct structure."""
        msg = incident_detected_message(
            incident_id="incident-123",
            incident_type="audio_deepfake",
            severity="high",
            confidence=92.5,
            participant_id="participant-456",
            title="Potential Audio Deepfake",
            meeting_id="meeting-789",
        )

        assert msg.type == "incident_detected"
        assert msg.data["incident_id"] == "incident-123"
        assert msg.data["incident_type"] == "audio_deepfake"
        assert msg.data["severity"] == "high"
        assert msg.data["confidence"] == 92.5

    def test_verification_required_message(self):
        """Verification required message has correct structure."""
        msg = verification_required_message(
            verification_id="verify-123",
            participant_id="participant-456",
            channel="sms",
            reason="High risk transaction",
            meeting_id="meeting-789",
        )

        assert msg.type == "verification_required"
        assert msg.data["verification_id"] == "verify-123"
        assert msg.data["channel"] == "sms"
        assert msg.data["reason"] == "High risk transaction"

    def test_participant_update_message(self):
        """Participant update message has correct structure."""
        msg = participant_update_message(
            participant_id="participant-456",
            meeting_id="meeting-789",
            trust_level="suspicious",
            is_flagged=True,
            flag_reason="Multiple detection triggers",
        )

        assert msg.type == "participant_update"
        assert msg.data["trust_level"] == "suspicious"
        assert msg.data["is_flagged"] is True
        assert msg.data["flag_reason"] == "Multiple detection triggers"

    def test_meeting_status_message(self):
        """Meeting status message has correct structure."""
        msg = meeting_status_message(
            meeting_id="meeting-789",
            status="in_progress",
            participant_count=5,
        )

        assert msg.type == "meeting_status"
        assert msg.data["status"] == "in_progress"
        assert msg.data["participant_count"] == 5

    def test_alert_message(self):
        """Alert message has correct structure."""
        msg = alert_message(
            alert_type="security",
            title="Security Alert",
            message="Potential threat detected",
            severity="high",
            meeting_id="meeting-789",
            actions=["verify", "remove"],
        )

        assert msg.type == "alert"
        assert msg.data["alert_type"] == "security"
        assert msg.data["title"] == "Security Alert"
        assert msg.data["severity"] == "high"
        assert msg.data["actions"] == ["verify", "remove"]


class TestConnectionManager:
    """Tests for ConnectionManager."""

    @pytest.fixture
    def manager(self):
        """Create a fresh connection manager."""
        return ConnectionManager()

    @pytest.fixture
    def mock_websocket(self):
        """Create a mock WebSocket."""
        ws = AsyncMock()
        ws.send_json = AsyncMock()
        ws.accept = AsyncMock()
        return ws

    @pytest.mark.asyncio
    async def test_connect_registers_connection(self, manager, mock_websocket):
        """Connect registers the connection."""
        conn_id = await manager.connect(
            websocket=mock_websocket,
            user_id="user-123",
            company_id="company-456",
            meeting_id="meeting-789",
        )

        assert conn_id is not None
        assert conn_id in manager._connections
        mock_websocket.accept.assert_called_once()

    @pytest.mark.asyncio
    async def test_connect_adds_to_company_connections(self, manager, mock_websocket):
        """Connect adds to company connections."""
        conn_id = await manager.connect(
            websocket=mock_websocket,
            user_id="user-123",
            company_id="company-456",
        )

        assert "company-456" in manager._company_connections
        assert conn_id in manager._company_connections["company-456"]

    @pytest.mark.asyncio
    async def test_connect_adds_to_meeting_connections(self, manager, mock_websocket):
        """Connect adds to meeting connections when meeting_id provided."""
        conn_id = await manager.connect(
            websocket=mock_websocket,
            user_id="user-123",
            company_id="company-456",
            meeting_id="meeting-789",
        )

        assert "meeting-789" in manager._meeting_connections
        assert conn_id in manager._meeting_connections["meeting-789"]

    @pytest.mark.asyncio
    async def test_disconnect_removes_connection(self, manager, mock_websocket):
        """Disconnect removes the connection."""
        conn_id = await manager.connect(
            websocket=mock_websocket,
            user_id="user-123",
            company_id="company-456",
            meeting_id="meeting-789",
        )

        await manager.disconnect(conn_id)

        assert conn_id not in manager._connections
        assert manager.get_meeting_connection_count("meeting-789") == 0
        assert manager.get_company_connection_count("company-456") == 0

    @pytest.mark.asyncio
    async def test_subscribe_to_meeting(self, manager, mock_websocket):
        """Subscribe to meeting updates connection."""
        conn_id = await manager.connect(
            websocket=mock_websocket,
            user_id="user-123",
            company_id="company-456",
        )

        await manager.subscribe_to_meeting(conn_id, "meeting-789")

        assert "meeting-789" in manager._meeting_connections
        assert conn_id in manager._meeting_connections["meeting-789"]

    @pytest.mark.asyncio
    async def test_unsubscribe_from_meeting(self, manager, mock_websocket):
        """Unsubscribe removes from meeting connections."""
        conn_id = await manager.connect(
            websocket=mock_websocket,
            user_id="user-123",
            company_id="company-456",
            meeting_id="meeting-789",
        )

        await manager.unsubscribe_from_meeting(conn_id)

        assert manager.get_meeting_connection_count("meeting-789") == 0

    @pytest.mark.asyncio
    async def test_send_personal(self, manager, mock_websocket):
        """Send personal message to connection."""
        conn_id = await manager.connect(
            websocket=mock_websocket,
            user_id="user-123",
            company_id="company-456",
        )

        msg = WebSocketMessage(type="test", data={"key": "value"})
        result = await manager.send_personal(conn_id, msg)

        assert result is True
        mock_websocket.send_json.assert_called_once()

    @pytest.mark.asyncio
    async def test_broadcast_to_meeting(self, manager):
        """Broadcast to all meeting connections."""
        ws1 = AsyncMock()
        ws1.send_json = AsyncMock()
        ws1.accept = AsyncMock()

        ws2 = AsyncMock()
        ws2.send_json = AsyncMock()
        ws2.accept = AsyncMock()

        await manager.connect(ws1, "user-1", "company-1", "meeting-1")
        await manager.connect(ws2, "user-2", "company-1", "meeting-1")

        msg = WebSocketMessage(type="test", data={})
        count = await manager.broadcast_to_meeting("meeting-1", msg)

        assert count == 2
        ws1.send_json.assert_called_once()
        ws2.send_json.assert_called_once()

    @pytest.mark.asyncio
    async def test_broadcast_to_company(self, manager):
        """Broadcast to all company connections."""
        ws1 = AsyncMock()
        ws1.send_json = AsyncMock()
        ws1.accept = AsyncMock()

        ws2 = AsyncMock()
        ws2.send_json = AsyncMock()
        ws2.accept = AsyncMock()

        await manager.connect(ws1, "user-1", "company-1")
        await manager.connect(ws2, "user-2", "company-1")

        msg = WebSocketMessage(type="test", data={})
        count = await manager.broadcast_to_company("company-1", msg)

        assert count == 2

    @pytest.mark.asyncio
    async def test_broadcast_excludes_connection(self, manager):
        """Broadcast excludes specified connection."""
        ws1 = AsyncMock()
        ws1.send_json = AsyncMock()
        ws1.accept = AsyncMock()

        ws2 = AsyncMock()
        ws2.send_json = AsyncMock()
        ws2.accept = AsyncMock()

        conn1 = await manager.connect(ws1, "user-1", "company-1", "meeting-1")
        await manager.connect(ws2, "user-2", "company-1", "meeting-1")

        msg = WebSocketMessage(type="test", data={})
        count = await manager.broadcast_to_meeting("meeting-1", msg, exclude_conn_id=conn1)

        assert count == 1
        ws1.send_json.assert_not_called()
        ws2.send_json.assert_called_once()

    def test_get_connection_counts(self, manager):
        """Get connection counts returns correct values."""
        assert manager.get_total_connections() == 0
        assert manager.get_meeting_connection_count("meeting-1") == 0
        assert manager.get_company_connection_count("company-1") == 0
