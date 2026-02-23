"""
WebSocket Handler

Real-time updates for meeting monitoring dashboard.
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, Set, Optional, Any
from dataclasses import dataclass, field, asdict

from fastapi import WebSocket, WebSocketDisconnect, status
from pydantic import BaseModel

from src.shared.security.jwt import decode_token


class WebSocketMessage(BaseModel):
    """Base WebSocket message format."""

    type: str
    data: Dict[str, Any]
    timestamp: str = None

    def __init__(self, **data):
        if "timestamp" not in data or data["timestamp"] is None:
            data["timestamp"] = datetime.utcnow().isoformat() + "Z"
        super().__init__(**data)


@dataclass
class ConnectionInfo:
    """Information about a WebSocket connection."""

    websocket: WebSocket
    user_id: str
    company_id: str
    meeting_id: Optional[str] = None
    connected_at: datetime = field(default_factory=datetime.utcnow)


class ConnectionManager:
    """
    Manages WebSocket connections for real-time updates.

    Supports:
    - Per-meeting subscriptions
    - Company-wide broadcasts
    - User-specific messages
    """

    def __init__(self):
        # All active connections by connection ID
        self._connections: Dict[str, ConnectionInfo] = {}

        # Connections grouped by meeting ID
        self._meeting_connections: Dict[str, Set[str]] = {}

        # Connections grouped by company ID
        self._company_connections: Dict[str, Set[str]] = {}

        # Connection counter for generating IDs
        self._connection_counter = 0

        # Lock for thread-safe operations
        self._lock = asyncio.Lock()

    def _generate_connection_id(self) -> str:
        """Generate a unique connection ID."""
        self._connection_counter += 1
        return f"conn_{self._connection_counter}_{datetime.utcnow().timestamp()}"

    async def connect(
        self,
        websocket: WebSocket,
        user_id: str,
        company_id: str,
        meeting_id: Optional[str] = None,
    ) -> str:
        """
        Accept a WebSocket connection and register it.

        Args:
            websocket: The WebSocket connection.
            user_id: The authenticated user's ID.
            company_id: The user's company ID.
            meeting_id: Optional meeting ID to subscribe to.

        Returns:
            Connection ID for tracking.
        """
        await websocket.accept()

        async with self._lock:
            conn_id = self._generate_connection_id()

            # Store connection info
            self._connections[conn_id] = ConnectionInfo(
                websocket=websocket,
                user_id=user_id,
                company_id=company_id,
                meeting_id=meeting_id,
            )

            # Add to company connections
            if company_id not in self._company_connections:
                self._company_connections[company_id] = set()
            self._company_connections[company_id].add(conn_id)

            # Add to meeting connections if specified
            if meeting_id:
                if meeting_id not in self._meeting_connections:
                    self._meeting_connections[meeting_id] = set()
                self._meeting_connections[meeting_id].add(conn_id)

        return conn_id

    async def disconnect(self, conn_id: str) -> None:
        """
        Remove a WebSocket connection.

        Args:
            conn_id: The connection ID to remove.
        """
        async with self._lock:
            if conn_id not in self._connections:
                return

            conn_info = self._connections[conn_id]

            # Remove from company connections
            if conn_info.company_id in self._company_connections:
                self._company_connections[conn_info.company_id].discard(conn_id)
                if not self._company_connections[conn_info.company_id]:
                    del self._company_connections[conn_info.company_id]

            # Remove from meeting connections
            if conn_info.meeting_id and conn_info.meeting_id in self._meeting_connections:
                self._meeting_connections[conn_info.meeting_id].discard(conn_id)
                if not self._meeting_connections[conn_info.meeting_id]:
                    del self._meeting_connections[conn_info.meeting_id]

            # Remove connection
            del self._connections[conn_id]

    async def subscribe_to_meeting(self, conn_id: str, meeting_id: str) -> None:
        """
        Subscribe a connection to meeting updates.

        Args:
            conn_id: The connection ID.
            meeting_id: The meeting ID to subscribe to.
        """
        async with self._lock:
            if conn_id not in self._connections:
                return

            conn_info = self._connections[conn_id]

            # Unsubscribe from previous meeting if any
            if conn_info.meeting_id and conn_info.meeting_id in self._meeting_connections:
                self._meeting_connections[conn_info.meeting_id].discard(conn_id)

            # Subscribe to new meeting
            conn_info.meeting_id = meeting_id
            if meeting_id not in self._meeting_connections:
                self._meeting_connections[meeting_id] = set()
            self._meeting_connections[meeting_id].add(conn_id)

    async def unsubscribe_from_meeting(self, conn_id: str) -> None:
        """
        Unsubscribe a connection from meeting updates.

        Args:
            conn_id: The connection ID.
        """
        async with self._lock:
            if conn_id not in self._connections:
                return

            conn_info = self._connections[conn_id]

            if conn_info.meeting_id and conn_info.meeting_id in self._meeting_connections:
                self._meeting_connections[conn_info.meeting_id].discard(conn_id)
                if not self._meeting_connections[conn_info.meeting_id]:
                    del self._meeting_connections[conn_info.meeting_id]

            conn_info.meeting_id = None

    async def send_personal(self, conn_id: str, message: WebSocketMessage) -> bool:
        """
        Send a message to a specific connection.

        Args:
            conn_id: The connection ID.
            message: The message to send.

        Returns:
            True if sent successfully, False otherwise.
        """
        if conn_id not in self._connections:
            return False

        try:
            conn_info = self._connections[conn_id]
            await conn_info.websocket.send_json(message.model_dump())
            return True
        except Exception:
            await self.disconnect(conn_id)
            return False

    async def broadcast_to_meeting(
        self,
        meeting_id: str,
        message: WebSocketMessage,
        exclude_conn_id: Optional[str] = None,
    ) -> int:
        """
        Broadcast a message to all connections subscribed to a meeting.

        Args:
            meeting_id: The meeting ID.
            message: The message to broadcast.
            exclude_conn_id: Optional connection ID to exclude.

        Returns:
            Number of connections that received the message.
        """
        if meeting_id not in self._meeting_connections:
            return 0

        conn_ids = self._meeting_connections[meeting_id].copy()
        sent_count = 0

        for conn_id in conn_ids:
            if conn_id == exclude_conn_id:
                continue

            if await self.send_personal(conn_id, message):
                sent_count += 1

        return sent_count

    async def broadcast_to_company(
        self,
        company_id: str,
        message: WebSocketMessage,
        exclude_conn_id: Optional[str] = None,
    ) -> int:
        """
        Broadcast a message to all connections in a company.

        Args:
            company_id: The company ID.
            message: The message to broadcast.
            exclude_conn_id: Optional connection ID to exclude.

        Returns:
            Number of connections that received the message.
        """
        if company_id not in self._company_connections:
            return 0

        conn_ids = self._company_connections[company_id].copy()
        sent_count = 0

        for conn_id in conn_ids:
            if conn_id == exclude_conn_id:
                continue

            if await self.send_personal(conn_id, message):
                sent_count += 1

        return sent_count

    async def broadcast_all(
        self,
        message: WebSocketMessage,
        exclude_conn_id: Optional[str] = None,
    ) -> int:
        """
        Broadcast a message to all connections.

        Args:
            message: The message to broadcast.
            exclude_conn_id: Optional connection ID to exclude.

        Returns:
            Number of connections that received the message.
        """
        conn_ids = list(self._connections.keys())
        sent_count = 0

        for conn_id in conn_ids:
            if conn_id == exclude_conn_id:
                continue

            if await self.send_personal(conn_id, message):
                sent_count += 1

        return sent_count

    def get_meeting_connection_count(self, meeting_id: str) -> int:
        """Get the number of connections subscribed to a meeting."""
        return len(self._meeting_connections.get(meeting_id, set()))

    def get_company_connection_count(self, company_id: str) -> int:
        """Get the number of connections for a company."""
        return len(self._company_connections.get(company_id, set()))

    def get_total_connections(self) -> int:
        """Get the total number of active connections."""
        return len(self._connections)


# Global connection manager instance
manager = ConnectionManager()


# Message type factories for common events
def risk_update_message(
    meeting_id: str,
    risk_score: float,
    risk_level: str,
    participant_id: Optional[str] = None,
) -> WebSocketMessage:
    """Create a risk update message."""
    return WebSocketMessage(
        type="risk_update",
        data={
            "meeting_id": meeting_id,
            "risk_score": risk_score,
            "risk_level": risk_level,
            "participant_id": participant_id,
        },
    )


def incident_detected_message(
    incident_id: str,
    incident_type: str,
    severity: str,
    confidence: float,
    participant_id: str,
    title: str,
    meeting_id: str,
) -> WebSocketMessage:
    """Create an incident detected message."""
    return WebSocketMessage(
        type="incident_detected",
        data={
            "incident_id": incident_id,
            "incident_type": incident_type,
            "severity": severity,
            "confidence": confidence,
            "participant_id": participant_id,
            "title": title,
            "meeting_id": meeting_id,
        },
    )


def verification_required_message(
    verification_id: str,
    participant_id: str,
    channel: str,
    reason: str,
    meeting_id: str,
) -> WebSocketMessage:
    """Create a verification required message."""
    return WebSocketMessage(
        type="verification_required",
        data={
            "verification_id": verification_id,
            "participant_id": participant_id,
            "channel": channel,
            "reason": reason,
            "meeting_id": meeting_id,
        },
    )


def verification_result_message(
    verification_id: str,
    participant_id: str,
    status: str,
    meeting_id: str,
) -> WebSocketMessage:
    """Create a verification result message."""
    return WebSocketMessage(
        type="verification_result",
        data={
            "verification_id": verification_id,
            "participant_id": participant_id,
            "status": status,
            "meeting_id": meeting_id,
        },
    )


def participant_update_message(
    participant_id: str,
    meeting_id: str,
    trust_level: str,
    is_flagged: bool,
    flag_reason: Optional[str] = None,
) -> WebSocketMessage:
    """Create a participant update message."""
    return WebSocketMessage(
        type="participant_update",
        data={
            "participant_id": participant_id,
            "meeting_id": meeting_id,
            "trust_level": trust_level,
            "is_flagged": is_flagged,
            "flag_reason": flag_reason,
        },
    )


def meeting_status_message(
    meeting_id: str,
    status: str,
    participant_count: int,
) -> WebSocketMessage:
    """Create a meeting status message."""
    return WebSocketMessage(
        type="meeting_status",
        data={
            "meeting_id": meeting_id,
            "status": status,
            "participant_count": participant_count,
        },
    )


def alert_message(
    alert_type: str,
    title: str,
    message: str,
    severity: str,
    meeting_id: Optional[str] = None,
    actions: Optional[list] = None,
) -> WebSocketMessage:
    """Create an alert message."""
    return WebSocketMessage(
        type="alert",
        data={
            "alert_type": alert_type,
            "title": title,
            "message": message,
            "severity": severity,
            "meeting_id": meeting_id,
            "actions": actions or [],
        },
    )


async def authenticate_websocket(websocket: WebSocket) -> Optional[Dict[str, Any]]:
    """
    Authenticate a WebSocket connection using JWT token.

    The token can be passed via:
    1. Query parameter: ?token=xxx
    2. Sec-WebSocket-Protocol header

    Returns:
        Token payload if valid, None otherwise.
    """
    # Try query parameter first
    token = websocket.query_params.get("token")

    # Try protocol header if no query param
    if not token:
        protocols = websocket.headers.get("sec-websocket-protocol", "").split(",")
        for protocol in protocols:
            protocol = protocol.strip()
            if protocol.startswith("Bearer."):
                token = protocol[7:]  # Remove "Bearer." prefix
                break

    if not token:
        return None

    try:
        payload = decode_token(token)
        return payload
    except Exception:
        return None


async def handle_websocket_message(
    conn_id: str,
    message: dict,
    conn_info: ConnectionInfo,
) -> Optional[WebSocketMessage]:
    """
    Handle incoming WebSocket messages from clients.

    Supported message types:
    - subscribe: Subscribe to a meeting
    - unsubscribe: Unsubscribe from current meeting
    - ping: Keep-alive ping

    Args:
        conn_id: Connection ID.
        message: The received message.
        conn_info: Connection information.

    Returns:
        Response message if any.
    """
    msg_type = message.get("type")

    if msg_type == "subscribe":
        meeting_id = message.get("meeting_id")
        if meeting_id:
            await manager.subscribe_to_meeting(conn_id, meeting_id)
            return WebSocketMessage(
                type="subscribed",
                data={"meeting_id": meeting_id},
            )

    elif msg_type == "unsubscribe":
        await manager.unsubscribe_from_meeting(conn_id)
        return WebSocketMessage(
            type="unsubscribed",
            data={},
        )

    elif msg_type == "ping":
        return WebSocketMessage(
            type="pong",
            data={},
        )

    return None
