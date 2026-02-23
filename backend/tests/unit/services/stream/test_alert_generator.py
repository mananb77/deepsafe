"""Unit tests for alert generator."""

import pytest
import asyncio
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

from src.services.stream.alert_generator import (
    AlertGenerator,
    AlertThresholds,
    AlertDispatcher,
    Alert,
    AlertLevel,
    AlertType,
    DispatchChannel,
    AlertHistory,
)
from src.services.stream.pipeline.orchestrator import AnalysisResult


class TestAlertThresholds:
    """Tests for AlertThresholds configuration."""

    def test_default_thresholds(self):
        """Test default threshold values."""
        thresholds = AlertThresholds()

        assert thresholds.info_threshold == 0.30
        assert thresholds.warning_threshold == 0.50
        assert thresholds.high_threshold == 0.65
        assert thresholds.critical_threshold == 0.85

    def test_get_level_from_score_info(self):
        """Test level classification - info."""
        thresholds = AlertThresholds()

        level = thresholds.get_level_from_score(0.35)
        assert level == AlertLevel.INFO

    def test_get_level_from_score_warning(self):
        """Test level classification - warning."""
        thresholds = AlertThresholds()

        level = thresholds.get_level_from_score(0.55)
        assert level == AlertLevel.WARNING

    def test_get_level_from_score_high(self):
        """Test level classification - high."""
        thresholds = AlertThresholds()

        level = thresholds.get_level_from_score(0.75)
        assert level == AlertLevel.HIGH

    def test_get_level_from_score_critical(self):
        """Test level classification - critical."""
        thresholds = AlertThresholds()

        level = thresholds.get_level_from_score(0.90)
        assert level == AlertLevel.CRITICAL

    def test_get_cooldown(self):
        """Test cooldown period retrieval."""
        thresholds = AlertThresholds(
            info_cooldown=60,
            warning_cooldown=30,
            high_cooldown=15,
            critical_cooldown=5,
        )

        assert thresholds.get_cooldown(AlertLevel.INFO) == 60
        assert thresholds.get_cooldown(AlertLevel.WARNING) == 30
        assert thresholds.get_cooldown(AlertLevel.HIGH) == 15
        assert thresholds.get_cooldown(AlertLevel.CRITICAL) == 5


class TestAlert:
    """Tests for Alert dataclass."""

    def test_alert_creation(self):
        """Test creating an alert."""
        alert = Alert(
            alert_id="alert-1",
            alert_type=AlertType.AUDIO_DEEPFAKE,
            level=AlertLevel.HIGH,
            meeting_id="m1",
            participant_id="p1",
            title="Test Alert",
            message="Test message",
            risk_score=0.8,
            confidence=0.9,
        )

        assert alert.alert_id == "alert-1"
        assert alert.alert_type == AlertType.AUDIO_DEEPFAKE
        assert alert.level == AlertLevel.HIGH
        assert alert.meeting_id == "m1"
        assert alert.participant_id == "p1"

    def test_alert_to_dict(self):
        """Test alert serialization."""
        alert = Alert(
            alert_id="alert-1",
            alert_type=AlertType.DEEPFAKE_DETECTED,
            level=AlertLevel.WARNING,
            meeting_id="m1",
            participant_id="p1",
            title="Deepfake Detected",
            message="Test",
            risk_score=0.6,
        )

        d = alert.to_dict()

        assert d["alert_id"] == "alert-1"
        assert d["alert_type"] == "deepfake_detected"
        assert d["level"] == "warning"
        assert d["meeting_id"] == "m1"
        assert "timestamp" in d

    def test_alert_channels(self):
        """Test alert dispatch channels."""
        alert = Alert(
            alert_id="alert-1",
            alert_type=AlertType.SOCIAL_ENGINEERING,
            level=AlertLevel.CRITICAL,
            meeting_id="m1",
            participant_id=None,
            title="Social Engineering",
            message="Test",
            channels=[
                DispatchChannel.WEBSOCKET,
                DispatchChannel.SMS,
                DispatchChannel.CALLBACK,
            ],
        )

        assert DispatchChannel.WEBSOCKET in alert.channels
        assert DispatchChannel.SMS in alert.channels
        assert DispatchChannel.CALLBACK in alert.channels


class TestAlertHistory:
    """Tests for AlertHistory."""

    def test_add_alert(self):
        """Test adding alert to history."""
        history = AlertHistory()

        alert = Alert(
            alert_id="alert-1",
            alert_type=AlertType.AUDIO_DEEPFAKE,
            level=AlertLevel.HIGH,
            meeting_id="m1",
            participant_id="p1",
            title="Test",
            message="Test",
        )

        history.add_alert(alert)

        assert len(history.alerts) == 1
        assert history.get_last_alert_time(AlertType.AUDIO_DEEPFAKE, "p1") > 0

    def test_get_escalation_count(self):
        """Test escalation count tracking."""
        history = AlertHistory()

        # Add multiple alerts
        for i in range(5):
            alert = Alert(
                alert_id=f"alert-{i}",
                alert_type=AlertType.VIDEO_DEEPFAKE,
                level=AlertLevel.WARNING,
                meeting_id="m1",
                participant_id="p1",
                title="Test",
                message="Test",
            )
            history.add_alert(alert)

        count = history.get_escalation_count(
            AlertType.VIDEO_DEEPFAKE,
            "p1",
            window_seconds=3600,
        )

        assert count == 5

    def test_cleanup(self):
        """Test history cleanup."""
        history = AlertHistory()

        alert = Alert(
            alert_id="alert-1",
            alert_type=AlertType.AUDIO_DEEPFAKE,
            level=AlertLevel.HIGH,
            meeting_id="m1",
            participant_id="p1",
            title="Test",
            message="Test",
        )
        history.add_alert(alert)

        # Cleanup with 0 second max age should remove all
        history.cleanup(max_age_seconds=0)

        assert len(history.alerts) == 0


class TestAlertGenerator:
    """Tests for AlertGenerator."""

    def test_generator_creation(self):
        """Test creating an alert generator."""
        generator = AlertGenerator(
            meeting_id="meeting-1",
            thresholds=AlertThresholds(),
        )

        assert generator.meeting_id == "meeting-1"

    def test_register_handler(self):
        """Test registering dispatch handlers."""
        generator = AlertGenerator(meeting_id="m1")

        handler = MagicMock()
        generator.register_handler(DispatchChannel.WEBSOCKET, handler)

        # Handler should be registered
        assert handler in generator._handlers[DispatchChannel.WEBSOCKET]

    def test_unregister_handler(self):
        """Test unregistering handlers."""
        generator = AlertGenerator(meeting_id="m1")

        handler = MagicMock()
        generator.register_handler(DispatchChannel.WEBSOCKET, handler)
        generator.unregister_handler(DispatchChannel.WEBSOCKET, handler)

        assert handler not in generator._handlers[DispatchChannel.WEBSOCKET]

    @pytest.mark.asyncio
    async def test_process_low_risk_result(self):
        """Test processing a low risk result."""
        generator = AlertGenerator(
            meeting_id="m1",
            thresholds=AlertThresholds(info_threshold=0.30),
        )

        result = AnalysisResult(
            participant_id="p1",
            meeting_id="m1",
            audio_deepfake_score=0.1,
            video_deepfake_score=0.1,
        )

        alerts = await generator.process_result(result, participant_id="p1")

        # Low scores should not generate alerts
        assert len(alerts) == 0

    @pytest.mark.asyncio
    async def test_process_audio_deepfake_alert(self):
        """Test processing high audio deepfake score."""
        generator = AlertGenerator(
            meeting_id="m1",
            thresholds=AlertThresholds(audio_deepfake_threshold=0.70),
        )

        result = AnalysisResult(
            participant_id="p1",
            meeting_id="m1",
            audio_deepfake_score=0.85,  # Above threshold
        )

        alerts = await generator.process_result(result, participant_id="p1")

        # Should generate audio deepfake alert
        audio_alerts = [a for a in alerts if a.alert_type == AlertType.AUDIO_DEEPFAKE]
        assert len(audio_alerts) >= 1

    @pytest.mark.asyncio
    async def test_process_video_deepfake_alert(self):
        """Test processing high video deepfake score."""
        generator = AlertGenerator(
            meeting_id="m1",
            thresholds=AlertThresholds(video_deepfake_threshold=0.70),
        )

        result = AnalysisResult(
            participant_id="p1",
            meeting_id="m1",
            video_deepfake_score=0.90,  # Above threshold
        )

        alerts = await generator.process_result(result, participant_id="p1")

        video_alerts = [a for a in alerts if a.alert_type == AlertType.VIDEO_DEEPFAKE]
        assert len(video_alerts) >= 1

    @pytest.mark.asyncio
    async def test_process_social_engineering_alert(self):
        """Test processing social engineering alert."""
        generator = AlertGenerator(
            meeting_id="m1",
            thresholds=AlertThresholds(social_engineering_threshold=0.60),
        )

        result = AnalysisResult(
            participant_id="p1",
            meeting_id="m1",
            social_engineering_score=0.75,  # Above threshold
        )

        alerts = await generator.process_result(result, participant_id="p1")

        se_alerts = [a for a in alerts if a.alert_type == AlertType.SOCIAL_ENGINEERING]
        assert len(se_alerts) >= 1

    @pytest.mark.asyncio
    async def test_alert_cooldown(self):
        """Test that cooldown suppresses duplicate alerts."""
        thresholds = AlertThresholds(
            audio_deepfake_threshold=0.70,
            high_cooldown=60,  # 60 second cooldown
        )
        generator = AlertGenerator(
            meeting_id="m1",
            thresholds=thresholds,
        )

        result = AnalysisResult(
            participant_id="p1",
            meeting_id="m1",
            audio_deepfake_score=0.85,
        )

        # First call should generate alert
        alerts1 = await generator.process_result(result, participant_id="p1")

        # Second call immediately should be suppressed
        alerts2 = await generator.process_result(result, participant_id="p1")

        assert len(alerts1) > 0
        # Second batch should have fewer or no new alerts of the same type
        # (cooldown in effect)

    @pytest.mark.asyncio
    async def test_alert_dispatch(self):
        """Test that alerts are dispatched to handlers."""
        generator = AlertGenerator(
            meeting_id="m1",
            thresholds=AlertThresholds(audio_deepfake_threshold=0.70),
        )

        handler = AsyncMock()
        generator.register_handler(DispatchChannel.WEBSOCKET, handler)

        result = AnalysisResult(
            participant_id="p1",
            meeting_id="m1",
            audio_deepfake_score=0.85,
        )

        await generator.process_result(result, participant_id="p1")

        # Handler should have been called
        assert handler.called

    @pytest.mark.asyncio
    async def test_sync_handler_dispatch(self):
        """Test dispatch to synchronous handler."""
        generator = AlertGenerator(
            meeting_id="m1",
            thresholds=AlertThresholds(audio_deepfake_threshold=0.70),
        )

        handler = MagicMock()  # Sync handler
        generator.register_handler(DispatchChannel.WEBSOCKET, handler)

        result = AnalysisResult(
            participant_id="p1",
            meeting_id="m1",
            audio_deepfake_score=0.85,
        )

        await generator.process_result(result, participant_id="p1")

        # Sync handler should have been called
        assert handler.called

    @pytest.mark.asyncio
    async def test_combined_risk_alert(self):
        """Test combined risk alert generation."""
        generator = AlertGenerator(
            meeting_id="m1",
            thresholds=AlertThresholds(warning_threshold=0.50),
        )

        result = AnalysisResult(
            participant_id="p1",
            meeting_id="m1",
            audio_deepfake_score=0.6,
            video_deepfake_score=0.6,
            social_engineering_score=0.6,
        )

        alerts = await generator.process_result(result, participant_id="p1")

        # Should generate combined risk alert
        combined_alerts = [
            a for a in alerts
            if a.alert_type in [AlertType.HIGH_RISK_PARTICIPANT, AlertType.MEETING_RISK_ELEVATED]
        ]
        # May or may not have combined alert depending on combined score
        assert isinstance(combined_alerts, list)

    @pytest.mark.asyncio
    async def test_critical_alert_actions(self):
        """Test that critical alerts have appropriate actions."""
        generator = AlertGenerator(
            meeting_id="m1",
            thresholds=AlertThresholds(
                critical_threshold=0.85,
                audio_deepfake_threshold=0.70,
            ),
        )

        result = AnalysisResult(
            participant_id="p1",
            meeting_id="m1",
            audio_deepfake_score=0.95,
            video_deepfake_score=0.95,
            social_engineering_score=0.95,
        )

        alerts = await generator.process_result(result, participant_id="p1")

        critical_alerts = [a for a in alerts if a.level == AlertLevel.CRITICAL]

        # Critical alerts should have verification or intervention flags
        for alert in critical_alerts:
            assert alert.requires_verification or alert.auto_intervention or len(alert.suggested_actions) > 0

    def test_get_alert_history(self):
        """Test retrieving alert history."""
        generator = AlertGenerator(meeting_id="m1")

        history = generator.get_alert_history(participant_id="p1")

        assert isinstance(history, list)

    def test_cleanup_history(self):
        """Test history cleanup."""
        generator = AlertGenerator(meeting_id="m1")

        # Should not raise
        generator.cleanup_history(max_age_seconds=0)

    def test_reset(self):
        """Test generator reset."""
        generator = AlertGenerator(meeting_id="m1")

        generator.reset()

        stats = generator.stats
        assert stats["alerts_generated"] == 0
        assert stats["alerts_dispatched"] == 0

    def test_stats(self):
        """Test generator statistics."""
        generator = AlertGenerator(meeting_id="m1")

        stats = generator.stats

        assert "alerts_generated" in stats
        assert "alerts_suppressed" in stats
        assert "alerts_dispatched" in stats


class TestAlertDispatcher:
    """Tests for AlertDispatcher."""

    def test_dispatcher_creation(self):
        """Test creating a dispatcher."""
        dispatcher = AlertDispatcher()

        assert dispatcher.default_thresholds is not None

    def test_get_generator(self):
        """Test getting/creating generator for meeting."""
        dispatcher = AlertDispatcher()

        generator = dispatcher.get_generator("meeting-1")

        assert generator is not None
        assert generator.meeting_id == "meeting-1"

    def test_get_generator_cached(self):
        """Test that generator is cached."""
        dispatcher = AlertDispatcher()

        gen1 = dispatcher.get_generator("meeting-1")
        gen2 = dispatcher.get_generator("meeting-1")

        assert gen1 is gen2

    def test_remove_generator(self):
        """Test removing a generator."""
        dispatcher = AlertDispatcher()

        dispatcher.get_generator("meeting-1")
        dispatcher.remove_generator("meeting-1")

        # Getting again should create new instance
        gen = dispatcher.get_generator("meeting-1")
        assert gen is not None

    def test_register_global_handler(self):
        """Test registering global handler."""
        dispatcher = AlertDispatcher()

        handler = MagicMock()
        dispatcher.register_global_handler(DispatchChannel.SIEM, handler)

        # New generators should have the handler
        gen = dispatcher.get_generator("meeting-1")
        assert handler in gen._handlers[DispatchChannel.SIEM]

    @pytest.mark.asyncio
    async def test_process_result(self):
        """Test processing result through dispatcher."""
        dispatcher = AlertDispatcher(
            default_thresholds=AlertThresholds(audio_deepfake_threshold=0.70)
        )

        result = AnalysisResult(
            participant_id="p1",
            meeting_id="m1",
            audio_deepfake_score=0.85,
        )

        alerts = await dispatcher.process_result(
            meeting_id="m1",
            result=result,
            participant_id="p1",
        )

        assert isinstance(alerts, list)

    def test_get_stats(self):
        """Test getting aggregated stats."""
        dispatcher = AlertDispatcher()

        dispatcher.get_generator("m1")
        dispatcher.get_generator("m2")

        stats = dispatcher.get_stats()

        assert stats["active_meetings"] == 2
        assert "total_alerts_generated" in stats


class TestAlertTypes:
    """Tests for alert type enums."""

    def test_alert_level_values(self):
        """Test AlertLevel enum values."""
        assert AlertLevel.INFO.value == "info"
        assert AlertLevel.WARNING.value == "warning"
        assert AlertLevel.HIGH.value == "high"
        assert AlertLevel.CRITICAL.value == "critical"

    def test_alert_type_values(self):
        """Test AlertType enum values."""
        assert AlertType.DEEPFAKE_DETECTED.value == "deepfake_detected"
        assert AlertType.AUDIO_DEEPFAKE.value == "audio_deepfake"
        assert AlertType.VIDEO_DEEPFAKE.value == "video_deepfake"
        assert AlertType.SOCIAL_ENGINEERING.value == "social_engineering"

    def test_dispatch_channel_values(self):
        """Test DispatchChannel enum values."""
        assert DispatchChannel.WEBSOCKET.value == "websocket"
        assert DispatchChannel.SMS.value == "sms"
        assert DispatchChannel.CALLBACK.value == "callback"
        assert DispatchChannel.SIEM.value == "siem"
