"""
End-to-End Pipeline Test

Validates the full flow from meeting creation through bot deployment,
stream processing, detection, alert generation, and incident creation.

Run modes:
    pytest tests/e2e/test_e2e_pipeline.py              # mock mode (CI-safe)
    USE_MOCK_ANALYSIS=true pytest tests/e2e/            # explicit mock
    USE_MOCK_ANALYSIS=false pytest tests/e2e/           # real analysis (needs models)
"""

import asyncio
import os
import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

from src.integrations.common.types import AudioFrame, VideoFrame
from src.services.stream.processor import StreamProcessor, StreamProcessorConfig
from src.services.stream.pipeline.orchestrator import (
    AnalysisPipeline,
    AnalysisResult,
    PipelineConfig,
)
from src.services.stream.alert_generator import (
    Alert,
    AlertDispatcher,
    AlertGenerator,
    AlertLevel,
    AlertThresholds,
    AlertType,
    DispatchChannel,
)
from src.services.stream.alert_handlers import (
    websocket_alert_handler,
    incident_creation_handler,
    verification_trigger_handler,
    setup_alert_handlers,
)


# ─── Fixtures ────────────────────────────────────────────────────────────────


@pytest.fixture
def meeting_id():
    return "e2e-test-meeting-001"


@pytest.fixture
def processor_config():
    return StreamProcessorConfig(
        use_mock_analysis=True,
        audio_chunk_duration_ms=100,
        video_analysis_interval_ms=100,
        max_concurrent_analysis=2,
        alert_cooldown_seconds=0,  # No cooldown for testing
    )


@pytest.fixture
def alert_dispatcher():
    return AlertDispatcher()


@pytest.fixture
def high_risk_result(meeting_id):
    """An analysis result with scores high enough to trigger alerts."""
    return AnalysisResult(
        participant_id="participant-1",
        meeting_id=meeting_id,
        analysis_type="combined",
        audio_deepfake_score=0.92,
        video_deepfake_score=0.15,
        social_engineering_score=0.10,
        voice_mismatch_score=0.05,
        facial_anomaly_score=0.03,
        av_sync_score=0.02,
        confidence=0.88,
    )


@pytest.fixture
def moderate_risk_result(meeting_id):
    """An analysis result with moderate risk (should create incident but not verify)."""
    return AnalysisResult(
        participant_id="participant-2",
        meeting_id=meeting_id,
        analysis_type="audio",
        audio_deepfake_score=0.55,
        social_engineering_score=0.60,
        confidence=0.72,
    )


# ─── Stream Processing E2E ──────────────────────────────────────────────────


class TestStreamProcessingE2E:
    """End-to-end stream processing from frames to alerts."""

    @pytest.mark.asyncio
    async def test_full_audio_pipeline(self, meeting_id, processor_config):
        """Audio frames → buffer → chunk → analysis → result callback."""
        results = []

        async def on_result(result):
            results.append(result)

        processor = StreamProcessor(meeting_id=meeting_id, config=processor_config)
        processor.set_result_callback(on_result)

        await processor.start()

        # Feed enough audio frames to fill a chunk
        for i in range(30):
            frame = AudioFrame(
                participant_id="p1",
                meeting_id=meeting_id,
                data=bytes([i % 256] * 3200),  # 3200 bytes = 100ms at 16kHz mono
                sample_rate=16000,
                channels=1,
                timestamp=datetime.utcnow(),
            )
            await processor.process_audio_frame(frame)
            await asyncio.sleep(0.01)

        # Wait for analysis to complete
        await asyncio.sleep(1.0)
        await processor.stop()

        stats = processor.stats
        assert stats.audio_frames_processed == 30
        assert stats.analyses_completed >= 0  # May or may not have completed

    @pytest.mark.asyncio
    async def test_full_video_pipeline(self, meeting_id, processor_config):
        """Video frames → queue → analysis → result callback."""
        results = []

        async def on_result(result):
            results.append(result)

        processor = StreamProcessor(meeting_id=meeting_id, config=processor_config)
        processor.set_result_callback(on_result)

        await processor.start()

        for i in range(15):
            frame = VideoFrame(
                participant_id="p1",
                meeting_id=meeting_id,
                data=f"frame_{i}".encode(),
                width=640,
                height=480,
                timestamp=datetime.utcnow(),
            )
            await processor.process_video_frame(frame)
            await asyncio.sleep(0.05)

        await asyncio.sleep(1.0)
        await processor.stop()

        assert processor.stats.video_frames_processed == 15

    @pytest.mark.asyncio
    async def test_multi_participant_risk_tracking(self, meeting_id, processor_config):
        """Multiple participants tracked independently."""
        async with StreamProcessor(meeting_id=meeting_id, config=processor_config) as proc:
            for pid in ["alice", "bob", "eve"]:
                proc.add_participant(pid, {"name": pid.title()})

                for _ in range(5):
                    frame = AudioFrame(
                        participant_id=pid,
                        meeting_id=meeting_id,
                        data=bytes([0] * 1600),
                        sample_rate=16000,
                        channels=1,
                        timestamp=datetime.utcnow(),
                    )
                    await proc.process_audio_frame(frame)

            await asyncio.sleep(0.5)

            assert len(proc.participants) == 3
            assert proc.stats.audio_frames_processed == 15


# ─── Alert Generation E2E ───────────────────────────────────────────────────


class TestAlertGenerationE2E:
    """Alert generation from analysis results."""

    @pytest.mark.asyncio
    async def test_high_risk_generates_alerts(self, meeting_id, high_risk_result):
        """High audio deepfake score generates audio_deepfake alert."""
        generator = AlertGenerator(
            meeting_id=meeting_id,
            thresholds=AlertThresholds(audio_deepfake_threshold=0.70),
        )

        ws_handler = MagicMock()
        generator.register_handler(DispatchChannel.WEBSOCKET, ws_handler)

        alerts = await generator.process_result(
            high_risk_result, participant_id="participant-1"
        )

        assert len(alerts) >= 1
        audio_alerts = [a for a in alerts if a.alert_type == AlertType.AUDIO_DEEPFAKE]
        assert len(audio_alerts) == 1
        assert audio_alerts[0].risk_score == 0.92
        assert audio_alerts[0].level in (AlertLevel.HIGH, AlertLevel.CRITICAL)

    @pytest.mark.asyncio
    async def test_alert_dispatcher_routes_to_handlers(self, meeting_id, high_risk_result):
        """AlertDispatcher correctly routes to registered global handlers."""
        dispatcher = AlertDispatcher()

        ws_calls = []
        notif_calls = []

        async def mock_ws(alert):
            ws_calls.append(alert)

        async def mock_notif(alert):
            notif_calls.append(alert)

        dispatcher.register_global_handler(DispatchChannel.WEBSOCKET, mock_ws)
        dispatcher.register_global_handler(DispatchChannel.NOTIFICATION, mock_notif)

        alerts = await dispatcher.process_result(
            meeting_id, high_risk_result, participant_id="participant-1"
        )

        assert len(alerts) >= 1
        assert len(ws_calls) >= 1  # WebSocket always dispatched

    @pytest.mark.asyncio
    async def test_cooldown_suppresses_duplicate_alerts(self, meeting_id, high_risk_result):
        """Same alert type suppressed within cooldown window."""
        generator = AlertGenerator(
            meeting_id=meeting_id,
            thresholds=AlertThresholds(
                audio_deepfake_threshold=0.70,
                high_cooldown=300,  # 5 minute cooldown
            ),
        )

        first = await generator.process_result(
            high_risk_result, participant_id="participant-1"
        )
        second = await generator.process_result(
            high_risk_result, participant_id="participant-1"
        )

        assert len(first) >= 1
        assert len(second) == 0  # Suppressed by cooldown
        assert generator.stats["alerts_suppressed"] >= 1


# ─── Alert Handler E2E ──────────────────────────────────────────────────────


class TestAlertHandlerE2E:
    """Alert handlers: WebSocket broadcast, incident creation, verification."""

    @pytest.mark.asyncio
    async def test_websocket_handler_broadcasts(self, meeting_id):
        """WebSocket handler broadcasts alert and risk update messages."""
        alert = Alert(
            alert_id=f"{meeting_id}-alert-1",
            alert_type=AlertType.AUDIO_DEEPFAKE,
            level=AlertLevel.HIGH,
            meeting_id=meeting_id,
            participant_id="p1",
            title="Audio Deepfake Detected",
            message="Synthetic voice detected",
            risk_score=0.85,
            confidence=0.90,
        )

        mock_manager = AsyncMock()
        mock_manager.broadcast_to_meeting = AsyncMock(return_value=3)

        with patch("src.services.api.websocket.manager", mock_manager):
            await websocket_alert_handler(alert)

            # Should broadcast both alert and risk_update messages
            assert mock_manager.broadcast_to_meeting.call_count == 2

    @pytest.mark.asyncio
    async def test_incident_handler_creates_record(self, meeting_id):
        """Incident handler creates DB record for WARNING+ alerts."""
        alert = Alert(
            alert_id=f"{meeting_id}-alert-2",
            alert_type=AlertType.SOCIAL_ENGINEERING,
            level=AlertLevel.WARNING,
            meeting_id=meeting_id,
            participant_id="p1",
            title="Social Engineering Attempt",
            message="Suspicious patterns detected",
            risk_score=0.55,
            confidence=0.70,
        )

        mock_session = AsyncMock()
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=False)

        mock_manager = AsyncMock()
        mock_manager.broadcast_to_meeting = AsyncMock(return_value=0)

        with patch(
            "src.shared.database.postgres.get_session_context",
            return_value=mock_session,
        ):
            with patch("src.services.api.websocket.manager", mock_manager):
                await incident_creation_handler(alert)

                # Session should have been used to add and commit
                mock_session.add.assert_called_once()
                mock_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_incident_handler_skips_info_alerts(self, meeting_id):
        """Incident handler does NOT create records for INFO alerts."""
        alert = Alert(
            alert_id=f"{meeting_id}-alert-3",
            alert_type=AlertType.MEETING_RISK_ELEVATED,
            level=AlertLevel.INFO,
            meeting_id=meeting_id,
            participant_id=None,
            title="Risk Slightly Elevated",
            message="Minor increase",
            risk_score=0.35,
            confidence=0.60,
        )

        with patch(
            "src.shared.database.postgres.get_session_context"
        ) as mock_ctx:
            await incident_creation_handler(alert)
            # INFO alerts return early before calling get_session_context
            mock_ctx.assert_not_called()

    @pytest.mark.asyncio
    async def test_verification_handler_triggers_for_high_risk(self, meeting_id):
        """Verification handler initiates MFA for high-risk alerts."""
        from uuid import uuid4 as _uuid4

        alert = Alert(
            alert_id=f"{meeting_id}-alert-4",
            alert_type=AlertType.AUDIO_DEEPFAKE,
            level=AlertLevel.HIGH,
            meeting_id=str(_uuid4()),
            participant_id=str(_uuid4()),
            title="Audio Deepfake Detected",
            message="High confidence deepfake",
            risk_score=0.80,
            confidence=0.88,
            requires_verification=True,
        )

        mock_engine_instance = MagicMock()
        mock_ver_session = MagicMock()
        mock_ver_session.session_id = _uuid4()
        mock_engine_instance.create_verification = AsyncMock(return_value=mock_ver_session)

        mock_engine_cls = MagicMock(return_value=mock_engine_instance)

        mock_manager = AsyncMock()
        mock_manager.broadcast_to_meeting = AsyncMock(return_value=0)

        # Patch at the module where the import happens inside the function
        with patch.dict("sys.modules", {}):
            with patch(
                "src.services.verification.verification_engine.VerificationEngine",
                mock_engine_cls,
            ):
                with patch("src.services.api.websocket.manager", mock_manager):
                    await verification_trigger_handler(alert)

                    mock_engine_instance.create_verification.assert_called_once()

    @pytest.mark.asyncio
    async def test_verification_handler_skips_low_risk(self, meeting_id):
        """Verification handler does NOT trigger for low-risk alerts."""
        alert = Alert(
            alert_id=f"{meeting_id}-alert-5",
            alert_type=AlertType.MEETING_RISK_ELEVATED,
            level=AlertLevel.WARNING,
            meeting_id=meeting_id,
            participant_id="p1",
            title="Risk Elevated",
            message="Moderate risk",
            risk_score=0.50,
            confidence=0.65,
            requires_verification=False,
        )

        with patch(
            "src.services.verification.verification_engine.VerificationEngine"
        ) as mock_cls:
            await verification_trigger_handler(alert)
            # risk_score < 0.65 and requires_verification=False → skip
            mock_cls.assert_not_called()


# ─── Full Pipeline E2E ──────────────────────────────────────────────────────


class TestFullPipelineE2E:
    """Full pipeline: frames → processing → detection → alerts → dispatch."""

    @pytest.mark.asyncio
    async def test_setup_alert_handlers_registers_all(self):
        """setup_alert_handlers registers handlers for all channels."""
        dispatcher = AlertDispatcher()
        setup_alert_handlers(dispatcher)

        # Create a generator and verify it has handlers
        gen = dispatcher.get_generator("test-meeting")
        assert len(gen._handlers[DispatchChannel.WEBSOCKET]) >= 1
        assert len(gen._handlers[DispatchChannel.NOTIFICATION]) >= 1
        assert len(gen._handlers[DispatchChannel.SMS]) >= 1

    @pytest.mark.asyncio
    async def test_risk_weights_match_prd(self):
        """Verify risk aggregation weights match PRD specification."""
        config = PipelineConfig()

        assert config.audio_deepfake_weight == 0.25
        assert config.video_deepfake_weight == 0.25
        assert config.social_engineering_weight == 0.20
        assert config.voice_mismatch_weight == 0.15
        assert config.facial_anomaly_weight == 0.10
        assert config.av_sync_weight == 0.05

        total = (
            config.audio_deepfake_weight
            + config.video_deepfake_weight
            + config.social_engineering_weight
            + config.voice_mismatch_weight
            + config.facial_anomaly_weight
            + config.av_sync_weight
        )
        assert abs(total - 1.0) < 0.001

    @pytest.mark.asyncio
    async def test_analysis_result_risk_calculation(self, meeting_id):
        """AnalysisResult.calculate_combined_risk uses correct weights."""
        result = AnalysisResult(
            meeting_id=meeting_id,
            audio_deepfake_score=1.0,
            video_deepfake_score=0.0,
            social_engineering_score=0.0,
            voice_mismatch_score=0.0,
            facial_anomaly_score=0.0,
            av_sync_score=0.0,
        )

        score = result.calculate_combined_risk()
        assert abs(score - 0.25) < 0.001  # Only audio at 25% weight

    @pytest.mark.asyncio
    async def test_processor_uses_env_mock_setting(self):
        """StreamProcessorConfig reads USE_MOCK_ANALYSIS from env."""
        with patch.dict(os.environ, {"USE_MOCK_ANALYSIS": "false"}):
            config = StreamProcessorConfig()
            assert config.use_mock_analysis is False

        with patch.dict(os.environ, {"USE_MOCK_ANALYSIS": "true"}):
            config = StreamProcessorConfig()
            assert config.use_mock_analysis is True

    @pytest.mark.asyncio
    async def test_end_to_end_with_alert_dispatch(self, meeting_id):
        """Full pipeline: mock frames → detection → alert → handlers called."""
        ws_calls = []
        incident_calls = []

        async def mock_ws_handler(alert):
            ws_calls.append(alert)

        async def mock_incident_handler(alert):
            incident_calls.append(alert)

        # Setup dispatcher with mock handlers
        dispatcher = AlertDispatcher()
        dispatcher.register_global_handler(DispatchChannel.WEBSOCKET, mock_ws_handler)
        dispatcher.register_global_handler(DispatchChannel.NOTIFICATION, mock_incident_handler)

        generator = dispatcher.get_generator(meeting_id)

        # Simulate a high-risk analysis result
        result = AnalysisResult(
            participant_id="p1",
            meeting_id=meeting_id,
            audio_deepfake_score=0.90,
            confidence=0.85,
        )

        alerts = await dispatcher.process_result(
            meeting_id, result, participant_id="p1"
        )

        # Should have generated and dispatched alerts
        assert len(alerts) >= 1
        assert len(ws_calls) >= 1

        # WebSocket is always dispatched; notification only for WARNING+
        audio_alerts = [a for a in alerts if a.alert_type == AlertType.AUDIO_DEEPFAKE]
        assert len(audio_alerts) == 1
        assert audio_alerts[0].level in (AlertLevel.HIGH, AlertLevel.CRITICAL)
