"""
Integration Test: Full Detection Pipeline

Tests the complete flow:
Audio frame → buffer → chunk → pipeline → detection → alert → policy → action

Uses mock analysis mode (no real ML models needed).
"""

import asyncio
import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

from src.integrations.common.types import AudioFrame, VideoFrame
from src.services.stream.processor import StreamProcessor, StreamProcessorConfig
from src.services.stream.pipeline.orchestrator import AnalysisPipeline, PipelineConfig
from src.services.stream.alert_generator import (
    AlertGenerator,
    AlertThresholds,
    AlertLevel,
    DispatchChannel,
)
from src.services.workflow.engine import PolicyEngine, PolicyDefinition
from src.services.workflow.action_dispatcher import ActionDispatcher, ActionStatus
from src.services.workflow.default_policies import get_default_policies


class TestFullDetectionPipeline:
    """End-to-end integration test for the detection pipeline."""

    @pytest.mark.asyncio
    async def test_audio_frame_to_alert(self):
        """Test: audio frames → buffer → chunk → analysis → alert."""
        config = StreamProcessorConfig(
            use_mock_analysis=True,
            audio_chunk_duration_ms=100,  # Short chunks for testing
            max_concurrent_analysis=2,
        )
        processor = StreamProcessor(meeting_id="test-meeting", config=config)

        alerts_received = []

        def alert_callback(alert):
            alerts_received.append(alert)

        processor.set_alert_callback(alert_callback)

        await processor.start()

        # Feed audio frames
        for i in range(20):
            frame = AudioFrame(
                participant_id="p1",
                meeting_id="test-meeting",
                data=bytes([0] * 5000),
                sample_rate=16000,
                channels=1,
                timestamp=datetime.utcnow(),
            )
            await processor.process_audio_frame(frame)
            await asyncio.sleep(0.01)

        # Wait for processing
        await asyncio.sleep(0.5)
        await processor.stop()

        # Verify frames were processed
        stats = processor.stats
        assert stats.audio_frames_processed == 20

    @pytest.mark.asyncio
    async def test_video_frame_processing(self):
        """Test: video frames → queue → analysis."""
        config = StreamProcessorConfig(
            use_mock_analysis=True,
            video_sample_fps=10,
        )
        processor = StreamProcessor(meeting_id="test-meeting", config=config)

        results_received = []

        async def result_callback(result):
            results_received.append(result)

        processor.set_result_callback(result_callback)

        await processor.start()

        for i in range(10):
            frame = VideoFrame(
                participant_id="p1",
                meeting_id="test-meeting",
                data=f"frame_{i}".encode(),
                width=640,
                height=480,
                timestamp=datetime.utcnow(),
            )
            await processor.process_video_frame(frame)
            await asyncio.sleep(0.05)

        await asyncio.sleep(0.5)
        await processor.stop()

        stats = processor.stats
        assert stats.video_frames_processed == 10

    @pytest.mark.asyncio
    async def test_multi_participant_processing(self):
        """Test processing with multiple participants."""
        config = StreamProcessorConfig(
            use_mock_analysis=True,
            audio_chunk_duration_ms=100,
        )

        async with StreamProcessor(meeting_id="test-meeting", config=config) as processor:
            for pid in ["p1", "p2", "p3"]:
                processor.add_participant(pid, {"name": f"User {pid}"})

                for _ in range(5):
                    frame = AudioFrame(
                        participant_id=pid,
                        meeting_id="test-meeting",
                        data=bytes([0] * 2000),
                        sample_rate=16000,
                        channels=1,
                        timestamp=datetime.utcnow(),
                    )
                    await processor.process_audio_frame(frame)

            await asyncio.sleep(0.3)

            assert len(processor.participants) == 3
            assert processor.stats.audio_frames_processed == 15

    @pytest.mark.asyncio
    async def test_pipeline_mock_analysis(self):
        """Test the analysis pipeline in mock mode."""
        from src.services.stream.buffers.audio_buffer import AudioChunk

        config = PipelineConfig(use_mock_analysis=True)
        pipeline = AnalysisPipeline(meeting_id="test-meeting", config=config)

        from datetime import datetime
        now = datetime.utcnow()
        chunk = AudioChunk(
            data=b"audio_data_here",
            participant_id="p1",
            meeting_id="test-meeting",
            sample_rate=16000,
            channels=1,
            bits_per_sample=16,
            duration_ms=3000,
            chunk_id="chunk-1",
            start_time=now,
            end_time=now,
            sequence_number=1,
        )

        result = await pipeline.analyze_audio(chunk)

        assert result.participant_id == "p1"
        assert result.meeting_id == "test-meeting"
        assert 0.0 <= result.audio_deepfake_score <= 1.0
        assert 0.0 <= result.combined_risk_score <= 1.0
        assert result.risk_level in ["low", "medium", "high", "critical"]

    @pytest.mark.asyncio
    async def test_alert_generation_from_result(self):
        """Test that high-risk analysis results generate alerts."""
        from src.services.stream.pipeline.orchestrator import AnalysisResult

        generator = AlertGenerator(
            meeting_id="test-meeting",
            thresholds=AlertThresholds(
                audio_deepfake_threshold=0.70,
            ),
        )

        handler = MagicMock()
        generator.register_handler(DispatchChannel.WEBSOCKET, handler)

        result = AnalysisResult(
            participant_id="p1",
            meeting_id="test-meeting",
            audio_deepfake_score=0.90,
        )

        alerts = await generator.process_result(result, participant_id="p1")

        assert len(alerts) > 0
        assert any(a.alert_type.value == "audio_deepfake" for a in alerts)

    @pytest.mark.asyncio
    async def test_policy_evaluation_from_detection(self):
        """Test: detection event → policy engine → matched actions."""
        engine = PolicyEngine()

        # Register default policies
        for policy in get_default_policies("test_company"):
            engine.register_policy(policy)

        # Simulate a high risk detection event
        matches = engine.evaluate(
            trigger="risk_score_change",
            context={"risk_score": 75},
            company_id="test_company",
        )

        # Should match high risk verification (61-85%)
        assert len(matches) >= 1
        action_types = []
        for match in matches:
            action_types.extend(match.get_action_types())

        assert "verify" in action_types or "alert" in action_types

    @pytest.mark.asyncio
    async def test_action_dispatch_from_policy(self):
        """Test: policy match → action dispatcher → handler called."""
        engine = PolicyEngine()
        dispatcher = ActionDispatcher()

        # Register a simple policy
        engine.register_policy(PolicyDefinition(
            policy_id="test_alert",
            name="Test Alert Policy",
            trigger="risk_score_change",
            min_risk_score=50,
            actions=[
                {"action": "alert", "channels": ["websocket"]},
                {"action": "log", "level": "warning"},
            ],
            company_id="test_company",
        ))

        # Register handlers
        alert_handler = MagicMock(return_value={"sent": True})
        log_handler = MagicMock(return_value={"logged": True})
        dispatcher.register_handler("alert", alert_handler)
        dispatcher.register_handler("log", log_handler)

        # Evaluate policies
        matches = engine.evaluate(
            trigger="risk_score_change",
            context={"risk_score": 75, "participant_id": "p1"},
            company_id="test_company",
        )

        # Dispatch actions
        for match in matches:
            results = await dispatcher.dispatch_actions(
                actions=match.actions,
                context=match.context,
            )

            assert all(r.status == ActionStatus.COMPLETED for r in results)

        alert_handler.assert_called_once()
        log_handler.assert_called_once()

    @pytest.mark.asyncio
    async def test_deepfake_detection_triggers_verification(self):
        """Test: deepfake event → policy → verify + record actions."""
        engine = PolicyEngine()

        for policy in get_default_policies("test_company"):
            engine.register_policy(policy)

        matches = engine.evaluate(
            trigger="deepfake_detected",
            context={
                "participant_id": "p1",
                "detection_type": "audio",
                "confidence": 0.92,
            },
            company_id="test_company",
        )

        assert len(matches) >= 1
        all_actions = []
        for match in matches:
            all_actions.extend(match.get_action_types())

        assert "verify" in all_actions
        assert "record" in all_actions

    @pytest.mark.asyncio
    async def test_high_value_transaction_triggers_hold(self):
        """Test: large transaction → policy → hold + approval actions."""
        engine = PolicyEngine()

        for policy in get_default_policies("test_company"):
            engine.register_policy(policy)

        matches = engine.evaluate(
            trigger="transaction_requested",
            context={
                "transaction_amount": 50000,
                "participant_id": "p1",
            },
            company_id="test_company",
        )

        assert len(matches) >= 1
        all_actions = []
        for match in matches:
            all_actions.extend(match.get_action_types())

        assert "hold" in all_actions
        assert "require_approval" in all_actions

    @pytest.mark.asyncio
    async def test_processor_context_manager(self):
        """Test StreamProcessor as async context manager."""
        config = StreamProcessorConfig(use_mock_analysis=True)

        async with StreamProcessor(meeting_id="ctx-test", config=config) as processor:
            assert processor.is_running is True

            frame = AudioFrame(
                participant_id="p1",
                meeting_id="ctx-test",
                data=bytes([0] * 1000),
                sample_rate=16000,
                channels=1,
                timestamp=datetime.utcnow(),
            )
            await processor.process_audio_frame(frame)

        assert processor.is_running is False
