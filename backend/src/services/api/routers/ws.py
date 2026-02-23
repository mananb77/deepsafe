"""
WebSocket Router

WebSocket endpoints for real-time meeting updates.
"""

import asyncio
from typing import Optional

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, status

from src.services.api.websocket import (
    manager,
    authenticate_websocket,
    handle_websocket_message,
    WebSocketMessage,
)

router = APIRouter()


@router.websocket("")
async def websocket_endpoint(
    websocket: WebSocket,
    meeting_id: Optional[str] = Query(default=None),
):
    """
    Main WebSocket endpoint for real-time updates.

    Authentication:
        Pass JWT token via query parameter: ?token=xxx

    Optional Parameters:
        meeting_id: Subscribe to a specific meeting on connect.

    Message Format (incoming):
        {
            "type": "subscribe" | "unsubscribe" | "ping",
            "meeting_id": "uuid" (for subscribe)
        }

    Message Format (outgoing):
        {
            "type": "risk_update" | "incident_detected" | "verification_required" | ...,
            "data": { ... },
            "timestamp": "2025-12-17T10:30:00.000Z"
        }
    """
    # Authenticate
    payload = await authenticate_websocket(websocket)
    if not payload:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    user_id = payload.get("sub")
    company_id = payload.get("company_id")

    if not user_id or not company_id:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    # Connect and register
    conn_id = await manager.connect(
        websocket=websocket,
        user_id=user_id,
        company_id=company_id,
        meeting_id=meeting_id,
    )

    # Send connection confirmation
    await manager.send_personal(
        conn_id,
        WebSocketMessage(
            type="connected",
            data={
                "connection_id": conn_id,
                "user_id": user_id,
                "company_id": company_id,
                "meeting_id": meeting_id,
            },
        ),
    )

    try:
        while True:
            # Receive and process messages
            try:
                data = await asyncio.wait_for(
                    websocket.receive_json(),
                    timeout=60.0,  # 1 minute timeout
                )
            except asyncio.TimeoutError:
                # Send ping to keep connection alive
                await manager.send_personal(
                    conn_id,
                    WebSocketMessage(type="ping", data={}),
                )
                continue

            # Get current connection info
            if conn_id not in manager._connections:
                break

            conn_info = manager._connections[conn_id]

            # Handle the message
            response = await handle_websocket_message(conn_id, data, conn_info)
            if response:
                await manager.send_personal(conn_id, response)

    except WebSocketDisconnect:
        pass
    except Exception:
        pass
    finally:
        await manager.disconnect(conn_id)


@router.websocket("/meetings/{meeting_id}")
async def meeting_websocket(
    websocket: WebSocket,
    meeting_id: str,
):
    """
    WebSocket endpoint for a specific meeting.

    Convenience endpoint that automatically subscribes to the specified meeting.
    """
    # Authenticate
    payload = await authenticate_websocket(websocket)
    if not payload:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    user_id = payload.get("sub")
    company_id = payload.get("company_id")

    if not user_id or not company_id:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    # Connect and register with meeting subscription
    conn_id = await manager.connect(
        websocket=websocket,
        user_id=user_id,
        company_id=company_id,
        meeting_id=meeting_id,
    )

    # Send connection confirmation
    await manager.send_personal(
        conn_id,
        WebSocketMessage(
            type="connected",
            data={
                "connection_id": conn_id,
                "user_id": user_id,
                "company_id": company_id,
                "meeting_id": meeting_id,
            },
        ),
    )

    try:
        while True:
            try:
                data = await asyncio.wait_for(
                    websocket.receive_json(),
                    timeout=60.0,
                )
            except asyncio.TimeoutError:
                await manager.send_personal(
                    conn_id,
                    WebSocketMessage(type="ping", data={}),
                )
                continue

            if conn_id not in manager._connections:
                break

            conn_info = manager._connections[conn_id]
            response = await handle_websocket_message(conn_id, data, conn_info)
            if response:
                await manager.send_personal(conn_id, response)

    except WebSocketDisconnect:
        pass
    except Exception:
        pass
    finally:
        await manager.disconnect(conn_id)
