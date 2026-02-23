"""
Real-Time Alert Generator

Generates alerts based on analysis results and risk thresholds.
Implements configurable thresholds, cooldown management, and
multi-channel alert dispatch.

Alert Levels:
- info: Low risk, informational only
- warning: Medium risk, requires attention
- high: High risk, immediate action needed
- critical: Critical risk, automatic intervention

Dispatch Channels:
- websocket: Real-time UI updates
- notification: Push notifications
- sms: SMS alerts for high/critical
- callback: Voice callback for critical
- email: Email notifications
"""

import asyncio
import logging
import threading
import time
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set

from src.services.stream.pipeline.orchestrator import AnalysisResult


logger = logging.getLogger(__name__)


class AlertLevel(str, Enum):
    """Alert severity levels."""
    INFO = "info"
    WARNING = "warning"
    HIGH = "high"
    CRITICAL = "critical"


class AlertType(str, Enum):
    """Types of alerts."""
    DEEPFAKE_DETECTED = "deepfake_detected"
    AUDIO_DEEPFAKE = "audio_deepfake"
    VIDEO_DEEPFAKE = "video_deepfake"
    SOCIAL_ENGINEERING = "social_engineering"
    VOICE_MISMATCH = "voice_mismatch"
    AV_SYNC_ANOMALY = "av_sync_anomaly"
    HIGH_RISK_PARTICIPANT = "high_risk_participant"
    MEETING_RISK_ELEVATED = "meeting_risk_elevated"
    VERIFICATION_REQUIRED = "verification_required"


class DispatchChannel(str, Enum):
    """Alert dispatch channels."""
    WEBSOCKET = "websocket"
    NOTIFICATION = "notification"
    SMS = "sms"
    CALLBACK = "callback"
    EMAIL = "email"
    SIEM = "siem"


@dataclass
class AlertThresholds:
    """Configurable alert thresholds."""

    # Risk score thresholds (0.0 - 1.0)
    info_threshold: float = 0.30  # >= 30% triggers info
    warning_threshold: float = 0.50  # >= 50% triggers warning
    high_threshold: float = 0.65  # >= 65% triggers high
    critical_threshold: float = 0.85  # >= 85% triggers critical

    # Component-specific thresholds
    audio_deepfake_threshold: float = 0.70
    video_deepfake_threshold: float = 0.70
    social_engineering_threshold: float = 0.60
    voice_mismatch_threshold: float = 0.75
    av_sync_threshold: float = 0.80

    # Cooldown settings (seconds)
    info_cooldown: int = 60  # 1 minute
    warning_cooldown: int = 30  # 30 seconds
    high_cooldown: int = 15  # 15 seconds
    critical_cooldown: int = 5  # 5 seconds (near real-time)

    # Escalation
    escalation_count: int = 3  # Alerts before escalation
    escalation_window: int = 120  # Window in seconds

    def get_level_from_score(self, score: float) -> AlertLevel:
        """Determine alert level from risk score."""
        if score >= self.critical_threshold:
            return AlertLevel.CRITICAL
        elif score >= self.high_threshold:
            return AlertLevel.HIGH
        elif score >= self.warning_threshold:
            return AlertLevel.WARNING
        elif score >= self.info_threshold:
            return AlertLevel.INFO
        return AlertLevel.INFO

    def get_cooldown(self, level: AlertLevel) -> int:
        """Get cooldown period for alert level."""
        cooldowns = {
            AlertLevel.INFO: self.info_cooldown,
            AlertLevel.WARNING: self.warning_cooldown,
            AlertLevel.HIGH: self.high_cooldown,
            AlertLevel.CRITICAL: self.critical_cooldown,
        }
        return cooldowns.get(level, self.warning_cooldown)


@dataclass
class Alert:
    """An alert to be dispatched."""

    alert_id: str
    alert_type: AlertType
    level: AlertLevel
    meeting_id: str
    participant_id: Optional[str]

    # Content
    title: str
    message: str
    details: Dict[str, Any] = field(default_factory=dict)

    # Scores
    risk_score: float = 0.0
    confidence: float = 0.0

    # Metadata
    timestamp: datetime = field(default_factory=datetime.utcnow)
    channels: List[DispatchChannel] = field(default_factory=list)

    # Actions
    requires_verification: bool = False
    auto_intervention: bool = False
    suggested_actions: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "alert_id": self.alert_id,
            "alert_type": self.alert_type.value,
            "level": self.level.value,
            "meeting_id": self.meeting_id,
            "participant_id": self.participant_id,
            "title": self.title,
            "message": self.message,
            "details": self.details,
            "risk_score": self.risk_score,
            "confidence": self.confidence,
            "timestamp": self.timestamp.isoformat(),
            "channels": [c.value for c in self.channels],
            "requires_verification": self.requires_verification,
            "auto_intervention": self.auto_intervention,
            "suggested_actions": self.suggested_actions,
        }


@dataclass
class AlertHistory:
    """Track alert history for cooldown and escalation."""

    alerts: List[Alert] = field(default_factory=list)
    last_alert_time: Dict[str, float] = field(default_factory=dict)  # alert_type -> timestamp
    escalation_count: Dict[str, int] = field(default_factory=dict)  # alert_type -> count

    def add_alert(self, alert: Alert) -> None:
        """Record an alert."""
        self.alerts.append(alert)
        key = f"{alert.alert_type.value}:{alert.participant_id or 'meeting'}"
        self.last_alert_time[key] = time.time()
        self.escalation_count[key] = self.escalation_count.get(key, 0) + 1

    def get_last_alert_time(self, alert_type: AlertType, participant_id: Optional[str]) -> float:
        """Get timestamp of last alert of this type."""
        key = f"{alert_type.value}:{participant_id or 'meeting'}"
        return self.last_alert_time.get(key, 0)

    def get_escalation_count(
        self,
        alert_type: AlertType,
        participant_id: Optional[str],
        window_seconds: int,
    ) -> int:
        """Get count of alerts within escalation window."""
        key = f"{alert_type.value}:{participant_id or 'meeting'}"
        cutoff = time.time() - window_seconds

        count = 0
        for alert in self.alerts:
            if (
                alert.alert_type == alert_type
                and alert.participant_id == participant_id
                and alert.timestamp.timestamp() >= cutoff
            ):
                count += 1

        return count

    def cleanup(self, max_age_seconds: int = 3600) -> None:
        """Remove alerts older than max age."""
        cutoff = datetime.utcnow().timestamp() - max_age_seconds
        self.alerts = [
            a for a in self.alerts
            if a.timestamp.timestamp() >= cutoff
        ]


class AlertGenerator:
    """
    Real-time alert generator for meeting analysis.

    Generates alerts based on analysis results, manages cooldowns,
    and dispatches to appropriate channels.

    Usage:
        generator = AlertGenerator(
            meeting_id="meeting-123",
            thresholds=AlertThresholds(),
        )

        # Register dispatch handlers
        generator.register_handler(DispatchChannel.WEBSOCKET, ws_handler)
        generator.register_handler(DispatchChannel.SMS, sms_handler)

        # Process analysis results
        alerts = await generator.process_result(analysis_result)
    """

    def __init__(
        self,
        meeting_id: str,
        thresholds: Optional[AlertThresholds] = None,
    ):
        """
        Initialize alert generator.

        Args:
            meeting_id: Meeting identifier.
            thresholds: Alert thresholds configuration.
        """
        self.meeting_id = meeting_id
        self.thresholds = thresholds or AlertThresholds()

        # Alert history per participant
        self._history: Dict[str, AlertHistory] = defaultdict(AlertHistory)
        self._meeting_history = AlertHistory()

        # Dispatch handlers
        self._handlers: Dict[DispatchChannel, List[Callable]] = defaultdict(list)

        # State
        self._alert_counter = 0
        self._lock = threading.Lock()

        # Statistics
        self._alerts_generated = 0
        self._alerts_suppressed = 0
        self._alerts_dispatched = 0

        # Channel configuration per alert level
        self._level_channels: Dict[AlertLevel, List[DispatchChannel]] = {
            AlertLevel.INFO: [DispatchChannel.WEBSOCKET],
            AlertLevel.WARNING: [DispatchChannel.WEBSOCKET, DispatchChannel.NOTIFICATION],
            AlertLevel.HIGH: [
                DispatchChannel.WEBSOCKET,
                DispatchChannel.NOTIFICATION,
                DispatchChannel.SMS,
                DispatchChannel.SIEM,
            ],
            AlertLevel.CRITICAL: [
                DispatchChannel.WEBSOCKET,
                DispatchChannel.NOTIFICATION,
                DispatchChannel.SMS,
                DispatchChannel.CALLBACK,
                DispatchChannel.SIEM,
            ],
        }

    @property
    def stats(self) -> Dict[str, Any]:
        """Get alert statistics."""
        return {
            "alerts_generated": self._alerts_generated,
            "alerts_suppressed": self._alerts_suppressed,
            "alerts_dispatched": self._alerts_dispatched,
        }

    def register_handler(
        self,
        channel: DispatchChannel,
        handler: Callable[[Alert], Any],
    ) -> None:
        """
        Register a dispatch handler for a channel.

        Args:
            channel: Dispatch channel.
            handler: Handler function (sync or async).
        """
        self._handlers[channel].append(handler)
        logger.info(f"Registered handler for channel {channel.value}")

    def unregister_handler(
        self,
        channel: DispatchChannel,
        handler: Callable[[Alert], Any],
    ) -> None:
        """Remove a handler from a channel."""
        if handler in self._handlers[channel]:
            self._handlers[channel].remove(handler)

    async def process_result(
        self,
        result: AnalysisResult,
        participant_id: Optional[str] = None,
    ) -> List[Alert]:
        """
        Process analysis result and generate alerts.

        Args:
            result: Analysis result to evaluate.
            participant_id: Participant ID (if participant-specific).

        Returns:
            List of generated alerts.
        """
        alerts = []

        # Calculate combined risk
        combined_score = result.calculate_combined_risk()
        level = self.thresholds.get_level_from_score(combined_score)

        # Always check for specific component threats (independent of combined score)
        alerts.extend(self._check_audio_deepfake(result, participant_id))
        alerts.extend(self._check_video_deepfake(result, participant_id))
        alerts.extend(self._check_social_engineering(result, participant_id))
        alerts.extend(self._check_voice_mismatch(result, participant_id))
        alerts.extend(self._check_av_sync(result, participant_id))

        # Generate combined risk alert if high enough
        if combined_score >= self.thresholds.warning_threshold:
            combined_alert = self._create_combined_alert(
                result, participant_id, combined_score, level
            )
            if combined_alert and self._should_generate_alert(combined_alert, participant_id):
                alerts.append(combined_alert)

        # Filter through cooldown
        filtered_alerts = []
        for alert in alerts:
            if self._should_generate_alert(alert, participant_id):
                filtered_alerts.append(alert)
                self._record_alert(alert, participant_id)
            else:
                self._alerts_suppressed += 1

        # Dispatch alerts
        for alert in filtered_alerts:
            await self._dispatch_alert(alert)

        self._alerts_generated += len(filtered_alerts)

        return filtered_alerts

    def _check_audio_deepfake(
        self,
        result: AnalysisResult,
        participant_id: Optional[str],
    ) -> List[Alert]:
        """Check for audio deepfake alerts."""
        alerts = []

        if result.audio_deepfake_score >= self.thresholds.audio_deepfake_threshold:
            level = self.thresholds.get_level_from_score(result.audio_deepfake_score)

            alert = self._create_alert(
                alert_type=AlertType.AUDIO_DEEPFAKE,
                level=level,
                participant_id=participant_id,
                title="Audio Deepfake Detected",
                message=f"Potential synthetic audio detected with {result.audio_deepfake_score:.0%} confidence",
                risk_score=result.audio_deepfake_score,
                confidence=result.confidence,
                details={
                    "detection_type": "audio_deepfake",
                    "score": result.audio_deepfake_score,
                    "analysis_details": result.details.get("audio", {}),
                },
                requires_verification=level in [AlertLevel.HIGH, AlertLevel.CRITICAL],
                auto_intervention=level == AlertLevel.CRITICAL,
                suggested_actions=(
                    ["Verify participant identity", "Review audio source"]
                    if level in [AlertLevel.HIGH, AlertLevel.CRITICAL]
                    else None
                ),
            )
            alerts.append(alert)

        return alerts

    def _check_video_deepfake(
        self,
        result: AnalysisResult,
        participant_id: Optional[str],
    ) -> List[Alert]:
        """Check for video deepfake alerts."""
        alerts = []

        if result.video_deepfake_score >= self.thresholds.video_deepfake_threshold:
            level = self.thresholds.get_level_from_score(result.video_deepfake_score)

            alert = self._create_alert(
                alert_type=AlertType.VIDEO_DEEPFAKE,
                level=level,
                participant_id=participant_id,
                title="Video Deepfake Detected",
                message=f"Potential deepfake video detected with {result.video_deepfake_score:.0%} confidence",
                risk_score=result.video_deepfake_score,
                confidence=result.confidence,
                details={
                    "detection_type": "video_deepfake",
                    "score": result.video_deepfake_score,
                    "analysis_details": result.details.get("video", {}),
                },
                requires_verification=level in [AlertLevel.HIGH, AlertLevel.CRITICAL],
                auto_intervention=level == AlertLevel.CRITICAL,
                suggested_actions=(
                    ["Verify participant identity", "Review video source"]
                    if level in [AlertLevel.HIGH, AlertLevel.CRITICAL]
                    else None
                ),
            )
            alerts.append(alert)

        return alerts

    def _check_social_engineering(
        self,
        result: AnalysisResult,
        participant_id: Optional[str],
    ) -> List[Alert]:
        """Check for social engineering alerts."""
        alerts = []

        if result.social_engineering_score >= self.thresholds.social_engineering_threshold:
            level = self.thresholds.get_level_from_score(result.social_engineering_score)

            alert = self._create_alert(
                alert_type=AlertType.SOCIAL_ENGINEERING,
                level=level,
                participant_id=participant_id,
                title="Social Engineering Attempt",
                message=f"Potential social engineering detected with {result.social_engineering_score:.0%} risk",
                risk_score=result.social_engineering_score,
                confidence=result.confidence,
                details={
                    "detection_type": "social_engineering",
                    "score": result.social_engineering_score,
                    "tactics": result.details.get("social_engineering", {}).get("tactics", []),
                },
                requires_verification=level in [AlertLevel.HIGH, AlertLevel.CRITICAL],
            )
            alerts.append(alert)

        return alerts

    def _check_voice_mismatch(
        self,
        result: AnalysisResult,
        participant_id: Optional[str],
    ) -> List[Alert]:
        """Check for voice mismatch alerts."""
        alerts = []

        if result.voice_mismatch_score >= self.thresholds.voice_mismatch_threshold:
            level = self.thresholds.get_level_from_score(result.voice_mismatch_score)

            alert = self._create_alert(
                alert_type=AlertType.VOICE_MISMATCH,
                level=level,
                participant_id=participant_id,
                title="Voice Verification Failed",
                message=f"Voice does not match registered voiceprint ({result.voice_mismatch_score:.0%} mismatch)",
                risk_score=result.voice_mismatch_score,
                confidence=result.confidence,
                details={
                    "detection_type": "voice_mismatch",
                    "score": result.voice_mismatch_score,
                },
                requires_verification=True,
            )
            alerts.append(alert)

        return alerts

    def _check_av_sync(
        self,
        result: AnalysisResult,
        participant_id: Optional[str],
    ) -> List[Alert]:
        """Check for A/V sync anomaly alerts."""
        alerts = []

        if result.av_sync_score >= self.thresholds.av_sync_threshold:
            level = self.thresholds.get_level_from_score(result.av_sync_score)

            alert = self._create_alert(
                alert_type=AlertType.AV_SYNC_ANOMALY,
                level=level,
                participant_id=participant_id,
                title="Audio-Video Sync Anomaly",
                message=f"Audio and video streams appear out of sync ({result.av_sync_score:.0%} anomaly)",
                risk_score=result.av_sync_score,
                confidence=result.confidence,
                details={
                    "detection_type": "av_sync",
                    "score": result.av_sync_score,
                    "sync_offset_ms": result.details.get("av_sync", {}).get("offset_ms"),
                },
            )
            alerts.append(alert)

        return alerts

    def _create_combined_alert(
        self,
        result: AnalysisResult,
        participant_id: Optional[str],
        combined_score: float,
        level: AlertLevel,
    ) -> Optional[Alert]:
        """Create a combined risk alert."""
        # Determine alert type based on context
        if participant_id:
            alert_type = AlertType.HIGH_RISK_PARTICIPANT
            title = "High Risk Participant"
            message = f"Participant shows elevated risk indicators ({combined_score:.0%})"
        else:
            alert_type = AlertType.MEETING_RISK_ELEVATED
            title = "Meeting Risk Elevated"
            message = f"Overall meeting risk has increased to {combined_score:.0%}"

        # Determine suggested actions
        suggested_actions = []
        if level == AlertLevel.WARNING:
            suggested_actions = ["Monitor participant closely", "Review recent activity"]
        elif level == AlertLevel.HIGH:
            suggested_actions = [
                "Verify participant identity",
                "Consider recording meeting",
                "Alert security team",
            ]
        elif level == AlertLevel.CRITICAL:
            suggested_actions = [
                "Initiate identity verification",
                "Notify security team immediately",
                "Consider removing participant",
                "Freeze sensitive operations",
            ]

        return self._create_alert(
            alert_type=alert_type,
            level=level,
            participant_id=participant_id,
            title=title,
            message=message,
            risk_score=combined_score,
            confidence=result.confidence,
            details={
                "audio_deepfake": result.audio_deepfake_score,
                "video_deepfake": result.video_deepfake_score,
                "social_engineering": result.social_engineering_score,
                "voice_mismatch": result.voice_mismatch_score,
                "av_sync": result.av_sync_score,
            },
            requires_verification=level in [AlertLevel.HIGH, AlertLevel.CRITICAL],
            auto_intervention=level == AlertLevel.CRITICAL,
            suggested_actions=suggested_actions,
        )

    def _create_alert(
        self,
        alert_type: AlertType,
        level: AlertLevel,
        participant_id: Optional[str],
        title: str,
        message: str,
        risk_score: float,
        confidence: float,
        details: Dict[str, Any],
        requires_verification: bool = False,
        auto_intervention: bool = False,
        suggested_actions: Optional[List[str]] = None,
    ) -> Alert:
        """Create an alert instance."""
        with self._lock:
            self._alert_counter += 1
            alert_id = f"{self.meeting_id}-alert-{self._alert_counter}"

        channels = self._level_channels.get(level, [DispatchChannel.WEBSOCKET])

        return Alert(
            alert_id=alert_id,
            alert_type=alert_type,
            level=level,
            meeting_id=self.meeting_id,
            participant_id=participant_id,
            title=title,
            message=message,
            details=details,
            risk_score=risk_score,
            confidence=confidence,
            channels=channels,
            requires_verification=requires_verification,
            auto_intervention=auto_intervention,
            suggested_actions=suggested_actions or [],
        )

    def _should_generate_alert(
        self,
        alert: Alert,
        participant_id: Optional[str],
    ) -> bool:
        """Check if alert should be generated based on cooldown."""
        history = (
            self._history[participant_id] if participant_id
            else self._meeting_history
        )

        last_time = history.get_last_alert_time(alert.alert_type, participant_id)
        cooldown = self.thresholds.get_cooldown(alert.level)

        if time.time() - last_time < cooldown:
            return False

        return True

    def _record_alert(self, alert: Alert, participant_id: Optional[str]) -> None:
        """Record alert in history."""
        history = (
            self._history[participant_id] if participant_id
            else self._meeting_history
        )
        history.add_alert(alert)

    async def _dispatch_alert(self, alert: Alert) -> None:
        """Dispatch alert to registered handlers."""
        for channel in alert.channels:
            handlers = self._handlers.get(channel, [])

            for handler in handlers:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        await handler(alert)
                    else:
                        handler(alert)
                    self._alerts_dispatched += 1
                except Exception as e:
                    logger.error(f"Alert dispatch error ({channel.value}): {e}")

    def get_alert_history(
        self,
        participant_id: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """
        Get alert history.

        Args:
            participant_id: Filter by participant (None for meeting-level).
            limit: Maximum alerts to return.

        Returns:
            List of alert dictionaries.
        """
        history = (
            self._history.get(participant_id, AlertHistory()) if participant_id
            else self._meeting_history
        )

        alerts = sorted(
            history.alerts,
            key=lambda a: a.timestamp,
            reverse=True,
        )[:limit]

        return [a.to_dict() for a in alerts]

    def cleanup_history(self, max_age_seconds: int = 3600) -> None:
        """Clean up old alert history."""
        self._meeting_history.cleanup(max_age_seconds)
        for history in self._history.values():
            history.cleanup(max_age_seconds)

    def reset(self) -> None:
        """Reset alert generator state."""
        self._history.clear()
        self._meeting_history = AlertHistory()
        self._alert_counter = 0
        self._alerts_generated = 0
        self._alerts_suppressed = 0
        self._alerts_dispatched = 0


class AlertDispatcher:
    """
    Centralized alert dispatcher for multiple meetings.

    Manages alert generators across meetings and provides
    global dispatch capabilities.
    """

    def __init__(self, default_thresholds: Optional[AlertThresholds] = None):
        """
        Initialize alert dispatcher.

        Args:
            default_thresholds: Default thresholds for new generators.
        """
        self.default_thresholds = default_thresholds or AlertThresholds()
        self._generators: Dict[str, AlertGenerator] = {}
        self._global_handlers: Dict[DispatchChannel, List[Callable]] = defaultdict(list)
        self._lock = threading.Lock()

    def get_generator(self, meeting_id: str) -> AlertGenerator:
        """
        Get or create alert generator for a meeting.

        Args:
            meeting_id: Meeting identifier.

        Returns:
            AlertGenerator for the meeting.
        """
        with self._lock:
            if meeting_id not in self._generators:
                generator = AlertGenerator(
                    meeting_id=meeting_id,
                    thresholds=self.default_thresholds,
                )

                # Register global handlers
                for channel, handlers in self._global_handlers.items():
                    for handler in handlers:
                        generator.register_handler(channel, handler)

                self._generators[meeting_id] = generator

            return self._generators[meeting_id]

    def remove_generator(self, meeting_id: str) -> None:
        """Remove alert generator for a meeting."""
        with self._lock:
            if meeting_id in self._generators:
                del self._generators[meeting_id]

    def register_global_handler(
        self,
        channel: DispatchChannel,
        handler: Callable[[Alert], Any],
    ) -> None:
        """
        Register a handler for all meetings.

        Args:
            channel: Dispatch channel.
            handler: Handler function.
        """
        self._global_handlers[channel].append(handler)

        # Register with existing generators
        for generator in self._generators.values():
            generator.register_handler(channel, handler)

    async def process_result(
        self,
        meeting_id: str,
        result: AnalysisResult,
        participant_id: Optional[str] = None,
    ) -> List[Alert]:
        """
        Process analysis result for a meeting.

        Args:
            meeting_id: Meeting identifier.
            result: Analysis result.
            participant_id: Participant ID if applicable.

        Returns:
            List of generated alerts.
        """
        generator = self.get_generator(meeting_id)
        return await generator.process_result(result, participant_id)

    def get_stats(self) -> Dict[str, Any]:
        """Get aggregated statistics."""
        total_generated = 0
        total_suppressed = 0
        total_dispatched = 0

        for generator in self._generators.values():
            stats = generator.stats
            total_generated += stats["alerts_generated"]
            total_suppressed += stats["alerts_suppressed"]
            total_dispatched += stats["alerts_dispatched"]

        return {
            "active_meetings": len(self._generators),
            "total_alerts_generated": total_generated,
            "total_alerts_suppressed": total_suppressed,
            "total_alerts_dispatched": total_dispatched,
        }
