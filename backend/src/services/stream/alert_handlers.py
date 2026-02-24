"""
Alert Dispatch Handlers

Concrete handler implementations for the AlertGenerator dispatch system.
Wires alerts to:
1. WebSocket broadcast — real-time dashboard updates
2. Incident auto-creation — persist to database when thresholds exceeded
3. Verification trigger — initiate MFA when risk > 65%
"""

import asyncio
import logging
from datetime import datetime
from typing import Optional
from uuid import uuid4

from src.services.stream.alert_generator import (
    Alert,
    AlertLevel,
    AlertType,
    AlertDispatcher,
    DispatchChannel,
)

logger = logging.getLogger(__name__)


# ─── WebSocket Broadcast Handler ────────────────────────────────────────────


async def websocket_alert_handler(alert: Alert) -> None:
    """
    Broadcast alert to all WebSocket clients subscribed to the meeting.

    Sends both an 'alert' message (for the toast/notification UI) and
    a 'risk_update' message (for the dashboard risk score display).
    """
    from src.services.api.websocket import (
        manager,
        alert_message,
        risk_update_message,
        incident_detected_message,
        verification_required_message,
    )

    # Send alert notification
    ws_alert = alert_message(
        alert_type=alert.alert_type.value,
        title=alert.title,
        message=alert.message,
        severity=alert.level.value,
        meeting_id=alert.meeting_id,
        actions=alert.suggested_actions,
    )
    await manager.broadcast_to_meeting(alert.meeting_id, ws_alert)

    # Send risk score update
    ws_risk = risk_update_message(
        meeting_id=alert.meeting_id,
        risk_score=alert.risk_score,
        risk_level=alert.level.value,
        participant_id=alert.participant_id,
    )
    await manager.broadcast_to_meeting(alert.meeting_id, ws_risk)

    logger.info(
        f"WebSocket broadcast: {alert.alert_type.value} "
        f"(level={alert.level.value}) for meeting {alert.meeting_id}"
    )


# ─── Incident Auto-Creation Handler ────────────────────────────────────────


# Map alert types to incident types
_ALERT_TO_INCIDENT_TYPE = {
    AlertType.AUDIO_DEEPFAKE: "audio_deepfake",
    AlertType.VIDEO_DEEPFAKE: "video_deepfake",
    AlertType.SOCIAL_ENGINEERING: "social_engineering",
    AlertType.VOICE_MISMATCH: "impersonation",
    AlertType.HIGH_RISK_PARTICIPANT: "suspicious_behavior",
    AlertType.MEETING_RISK_ELEVATED: "suspicious_behavior",
    AlertType.AV_SYNC_ANOMALY: "suspicious_behavior",
    AlertType.DEEPFAKE_DETECTED: "audio_deepfake",
    AlertType.VERIFICATION_REQUIRED: "verification_failed",
}

_ALERT_LEVEL_TO_SEVERITY = {
    AlertLevel.INFO: "low",
    AlertLevel.WARNING: "medium",
    AlertLevel.HIGH: "high",
    AlertLevel.CRITICAL: "critical",
}


async def incident_creation_handler(alert: Alert) -> None:
    """
    Auto-create an Incident record when alert level is WARNING or above.

    Uses the database session from the application's async engine to
    persist the incident. This runs outside of a request context, so
    we create our own session.
    """
    # Only create incidents for WARNING and above
    if alert.level == AlertLevel.INFO:
        return

    try:
        from src.shared.database.postgres import get_session_context
        from src.shared.models.incident import (
            Incident,
            IncidentType,
            IncidentSeverity,
            IncidentStatus,
        )

        incident_type_str = _ALERT_TO_INCIDENT_TYPE.get(
            alert.alert_type, "suspicious_behavior"
        )
        severity_str = _ALERT_LEVEL_TO_SEVERITY.get(alert.level, "medium")

        async with get_session_context() as session:
            incident = Incident(
                id=str(uuid4()),
                meeting_id=alert.meeting_id,
                participant_id=alert.participant_id,
                incident_type=IncidentType(incident_type_str),
                severity=IncidentSeverity(severity_str),
                status=IncidentStatus.DETECTED,
                title=alert.title,
                description=alert.message,
                confidence_score=alert.risk_score,
                detected_at=alert.timestamp,
                evidence_summary=str(alert.details),
                detection_method=alert.alert_type.value,
                alert_sent=True,
                alert_sent_at=datetime.utcnow(),
                raw_analysis_data=alert.details,
            )

            session.add(incident)
            await session.commit()

            logger.info(
                f"Incident created: {incident.id} "
                f"(type={incident_type_str}, severity={severity_str}) "
                f"for meeting {alert.meeting_id}"
            )

            # Also broadcast incident via WebSocket
            try:
                from src.services.api.websocket import (
                    manager,
                    incident_detected_message,
                )

                ws_msg = incident_detected_message(
                    incident_id=incident.id,
                    incident_type=incident_type_str,
                    severity=severity_str,
                    confidence=alert.risk_score,
                    participant_id=alert.participant_id or "",
                    title=alert.title,
                    meeting_id=alert.meeting_id,
                )
                await manager.broadcast_to_meeting(alert.meeting_id, ws_msg)
            except Exception as e:
                logger.warning(f"Failed to broadcast incident via WebSocket: {e}")

    except ImportError as e:
        logger.warning(f"Incident creation skipped (missing dependency): {e}")
    except Exception as e:
        logger.error(f"Failed to create incident for alert {alert.alert_id}: {e}")


# ─── Verification Trigger Handler ───────────────────────────────────────────


async def verification_trigger_handler(alert: Alert) -> None:
    """
    Trigger multi-factor verification when alert requires it.

    Per PRD FR-VER-004: risk-based channel selection.
    Triggered when:
    - alert.requires_verification is True (set by AlertGenerator for HIGH/CRITICAL)
    - OR risk_score >= 0.65 (65% threshold per PRD)
    """
    should_verify = alert.requires_verification or alert.risk_score >= 0.65

    if not should_verify:
        return

    if not alert.participant_id:
        logger.info(
            f"Verification skipped for meeting-level alert {alert.alert_id} "
            f"(no specific participant)"
        )
        return

    try:
        from src.services.verification.base import (
            VerificationRequest,
            VerificationType,
            VerificationChannel,
            get_verification_channels_for_risk,
        )
        from src.services.verification.verification_engine import VerificationEngine

        # Convert 0.0-1.0 score to 0-100 scale for channel selection
        risk_score_100 = alert.risk_score * 100

        # Get channels based on risk score (returns tuple of channels, requires_hold)
        channels, requires_hold = get_verification_channels_for_risk(risk_score_100)

        # Create verification request
        from uuid import UUID as _UUID
        try:
            participant_uuid = _UUID(alert.participant_id)
        except (ValueError, AttributeError):
            participant_uuid = uuid4()

        request = VerificationRequest(
            user_id=participant_uuid,
            verification_type=VerificationType.IDENTITY,
            meeting_id=_UUID(alert.meeting_id) if alert.meeting_id else None,
            participant_id=participant_uuid,
        )

        engine = VerificationEngine()
        session = await engine.create_verification(request)

        logger.info(
            f"Verification triggered: session={session.session_id} "
            f"channels={[c.value for c in channels]} "
            f"for participant {alert.participant_id} "
            f"in meeting {alert.meeting_id}"
        )

        # Broadcast verification_required via WebSocket
        try:
            from src.services.api.websocket import (
                manager,
                verification_required_message,
            )

            ws_msg = verification_required_message(
                verification_id=str(session.session_id),
                participant_id=alert.participant_id,
                channel=channels[0].value if channels else "sms",
                reason=alert.message,
                meeting_id=alert.meeting_id,
            )
            await manager.broadcast_to_meeting(alert.meeting_id, ws_msg)
        except Exception as e:
            logger.warning(f"Failed to broadcast verification via WebSocket: {e}")

    except ImportError as e:
        logger.warning(f"Verification trigger skipped (missing dependency): {e}")
    except Exception as e:
        logger.error(
            f"Failed to trigger verification for alert {alert.alert_id}: {e}"
        )


# ─── Setup Function ────────────────────────────────────────────────────────


def setup_alert_handlers(dispatcher: AlertDispatcher) -> None:
    """
    Register all default alert handlers with the dispatcher.

    Call this during application startup to wire the full
    alert → WebSocket + incident + verification pipeline.

    Args:
        dispatcher: The global AlertDispatcher instance.
    """
    dispatcher.register_global_handler(
        DispatchChannel.WEBSOCKET,
        websocket_alert_handler,
    )
    dispatcher.register_global_handler(
        DispatchChannel.NOTIFICATION,
        incident_creation_handler,
    )
    dispatcher.register_global_handler(
        DispatchChannel.SMS,
        verification_trigger_handler,
    )

    logger.info(
        "Alert handlers registered: WebSocket broadcast, "
        "incident auto-creation, verification trigger"
    )
