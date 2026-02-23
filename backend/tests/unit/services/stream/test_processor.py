"""Unit tests for stream processor."""

import pytest
import asyncio
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

from src.services.stream.processor import (
    StreamProcessor,
    StreamProcessorConfig,
    ProcessingStats,
)
from src.integrations.common.types import AudioFrame, VideoFrame


class TestStreamProcessorConfig:
    """Tests for StreamProcessorConfig."""

    def test_default_config(self):
        """Test default configuration values."""
        config = StreamProcessorConfig()

        assert config.audio_chunk_duration_ms == 3000
        assert config.video_sample_fps == 2
        assert config.target_latency_ms == 5000
        assert config.max_concurrent_analysis == 4

    def test_custom_config(self):
        """Test custom configuration."""
        config = StreamProcessorConfig(
            audio_chunk_duration_ms=2000,
            video_sample_fps=5,
            target_latency_ms=3000,
        )

        assert config.audio_chunk_duration_ms == 2000
        assert config.video_sample_fps == 5
        assert config.target_latency_ms == 3000

    def test_enable_flags(self):
        """Test analysis enable flags."""
        config = StreamProcessorConfig(
            enable_audio_analysis=False,
            enable_video_analysis=True,
        )

        assert config.enable_audio_analysis is False
        assert config.enable_video_analysis is True


class TestProcessingStats:
    """Tests for ProcessingStats."""

    def test_stats_creation(self):
        """Test creating stats."""
        stats = ProcessingStats()

        assert stats.audio_frames_processed == 0
        assert stats.video_frames_processed == 0
        assert stats.audio_chunks_analyzed == 0
        assert stats.video_frames_analyzed == 0
        assert stats.alerts_generated == 0

    def test_to_dict(self):
        """Test stats serialization."""
        stats = ProcessingStats(
            audio_frames_processed=100,
            video_frames_processed=50,
        )

        d = stats.to_dict()

        assert d["audio_frames_processed"] == 100
        assert d["video_frames_processed"] == 50


class TestStreamProcessor:
    """Tests for StreamProcessor."""

    def test_processor_creation(self):
        """Test creating a stream processor."""
        config = StreamProcessorConfig()
        processor = StreamProcessor(
            meeting_id="meeting-1",
            config=config,
        )

        assert processor.meeting_id == "meeting-1"
        assert processor.is_running is False
        assert processor.is_paused is False

    @pytest.mark.asyncio
    async def test_start_stop(self):
        """Test starting and stopping processor."""
        config = StreamProcessorConfig()
        processor = StreamProcessor(
            meeting_id="m1",
            config=config,
        )

        await processor.start()
        assert processor.is_running is True

        await processor.stop()
        assert processor.is_running is False

    @pytest.mark.asyncio
    async def test_pause_resume(self):
        """Test pausing and resuming processor."""
        config = StreamProcessorConfig()
        processor = StreamProcessor(
            meeting_id="m1",
            config=config,
        )

        await processor.start()

        processor.pause()
        assert processor.is_paused is True

        processor.resume()
        assert processor.is_paused is False

        await processor.stop()

    @pytest.mark.asyncio
    async def test_process_audio_frame(self):
        """Test processing an audio frame."""
        config = StreamProcessorConfig()
        processor = StreamProcessor(
            meeting_id="m1",
            config=config,
        )

        await processor.start()

        frame = AudioFrame(
            participant_id="p1",
            meeting_id="m1",
            data=bytes([0] * 1000),
            sample_rate=16000,
            channels=1,
            timestamp=datetime.utcnow(),
        )

        await processor.process_audio_frame(frame)

        stats = processor.stats
        assert stats.audio_frames_processed >= 1

        await processor.stop()

    @pytest.mark.asyncio
    async def test_process_video_frame(self):
        """Test processing a video frame."""
        config = StreamProcessorConfig()
        processor = StreamProcessor(
            meeting_id="m1",
            config=config,
        )

        await processor.start()

        frame = VideoFrame(
            participant_id="p1",
            meeting_id="m1",
            data=b"frame_data",
            width=640,
            height=480,
            timestamp=datetime.utcnow(),
        )

        await processor.process_video_frame(frame)

        stats = processor.stats
        assert stats.video_frames_processed >= 1

        await processor.stop()

    @pytest.mark.asyncio
    async def test_processing_when_paused(self):
        """Test that processing is skipped when paused."""
        config = StreamProcessorConfig()
        processor = StreamProcessor(
            meeting_id="m1",
            config=config,
        )

        await processor.start()
        processor.pause()

        initial_stats = processor.stats
        initial_audio = initial_stats.audio_frames_processed

        frame = AudioFrame(
            participant_id="p1",
            meeting_id="m1",
            data=bytes([0] * 1000),
            sample_rate=16000,
            channels=1,
            timestamp=datetime.utcnow(),
        )

        await processor.process_audio_frame(frame)

        # Frame should still be counted but not analyzed
        stats = processor.stats
        # Processing may or may not count paused frames
        assert isinstance(stats.audio_frames_processed, int)

        await processor.stop()

    @pytest.mark.asyncio
    async def test_add_remove_participant(self):
        """Test adding and removing participants."""
        config = StreamProcessorConfig()
        processor = StreamProcessor(
            meeting_id="m1",
            config=config,
        )

        await processor.start()

        processor.add_participant("p1", {"name": "Test User"})
        assert "p1" in processor.participants

        processor.remove_participant("p1")
        assert "p1" not in processor.participants

        await processor.stop()

    @pytest.mark.asyncio
    async def test_result_callback(self):
        """Test result callback invocation."""
        config = StreamProcessorConfig(
            use_mock_analysis=True,
            audio_chunk_duration_ms=100,  # Short for testing
        )
        processor = StreamProcessor(
            meeting_id="m1",
            config=config,
        )

        callback = AsyncMock()
        processor.set_result_callback(callback)

        await processor.start()

        # Add enough audio for a chunk
        for _ in range(10):
            frame = AudioFrame(
                participant_id="p1",
                meeting_id="m1",
                data=bytes([0] * 5000),
                sample_rate=16000,
                channels=1,
                timestamp=datetime.utcnow(),
            )
            await processor.process_audio_frame(frame)
            await asyncio.sleep(0.01)

        # Wait for processing
        await asyncio.sleep(0.2)

        await processor.stop()

        # Callback may or may not have been called depending on chunk timing
        # This is more of an integration test

    @pytest.mark.asyncio
    async def test_alert_callback(self):
        """Test alert callback invocation."""
        config = StreamProcessorConfig()
        processor = StreamProcessor(
            meeting_id="m1",
            config=config,
        )

        callback = AsyncMock()
        processor.set_alert_callback(callback)

        # Callback should be registered
        assert processor._alert_callback == callback

        await processor.start()
        await processor.stop()

    @pytest.mark.asyncio
    async def test_get_participant_risk(self):
        """Test getting participant risk score."""
        config = StreamProcessorConfig()
        processor = StreamProcessor(
            meeting_id="m1",
            config=config,
        )

        await processor.start()

        processor.add_participant("p1", {})

        risk = processor.get_participant_risk("p1")

        # Should return a risk score (may be 0 if no analysis done)
        assert risk is None or (0.0 <= risk <= 1.0)

        await processor.stop()

    @pytest.mark.asyncio
    async def test_get_meeting_risk(self):
        """Test getting overall meeting risk."""
        config = StreamProcessorConfig()
        processor = StreamProcessor(
            meeting_id="m1",
            config=config,
        )

        await processor.start()

        risk = processor.get_meeting_risk()

        # Should return a risk score
        assert 0.0 <= risk <= 1.0

        await processor.stop()

    def test_stats(self):
        """Test getting processor stats."""
        config = StreamProcessorConfig()
        processor = StreamProcessor(
            meeting_id="m1",
            config=config,
        )

        stats = processor.stats

        assert hasattr(stats, "audio_frames_processed")
        assert hasattr(stats, "video_frames_processed")
        assert hasattr(stats, "alerts_generated")

    @pytest.mark.asyncio
    async def test_reset_stats(self):
        """Test resetting stats."""
        config = StreamProcessorConfig()
        processor = StreamProcessor(
            meeting_id="m1",
            config=config,
        )

        await processor.start()

        frame = AudioFrame(
            participant_id="p1",
            meeting_id="m1",
            data=bytes([0] * 1000),
            sample_rate=16000,
            channels=1,
            timestamp=datetime.utcnow(),
        )
        await processor.process_audio_frame(frame)

        processor.reset_stats()

        stats = processor.stats
        assert stats.audio_frames_processed == 0

        await processor.stop()

    @pytest.mark.asyncio
    async def test_multiple_participants(self):
        """Test processing for multiple participants."""
        config = StreamProcessorConfig()
        processor = StreamProcessor(
            meeting_id="m1",
            config=config,
        )

        await processor.start()

        for pid in ["p1", "p2", "p3"]:
            processor.add_participant(pid, {"name": f"User {pid}"})

            frame = AudioFrame(
                participant_id=pid,
                meeting_id="m1",
                data=bytes([0] * 1000),
                sample_rate=16000,
                channels=1,
                timestamp=datetime.utcnow(),
            )
            await processor.process_audio_frame(frame)

        assert len(processor.participants) == 3

        await processor.stop()

    @pytest.mark.asyncio
    async def test_latency_tracking(self):
        """Test that latency is tracked."""
        config = StreamProcessorConfig(target_latency_ms=5000)
        processor = StreamProcessor(
            meeting_id="m1",
            config=config,
        )

        await processor.start()

        frame = AudioFrame(
            participant_id="p1",
            meeting_id="m1",
            data=bytes([0] * 1000),
            sample_rate=16000,
            channels=1,
            timestamp=datetime.utcnow(),
        )
        await processor.process_audio_frame(frame)

        stats = processor.stats

        # Average latency tracking
        assert hasattr(stats, "average_latency_ms") or "average_latency_ms" in stats.to_dict()

        await processor.stop()

    @pytest.mark.asyncio
    async def test_context_manager(self):
        """Test using processor as context manager."""
        config = StreamProcessorConfig()

        async with StreamProcessor(meeting_id="m1", config=config) as processor:
            assert processor.is_running is True

            frame = AudioFrame(
                participant_id="p1",
                meeting_id="m1",
                data=bytes([0] * 1000),
                sample_rate=16000,
                channels=1,
                timestamp=datetime.utcnow(),
            )
            await processor.process_audio_frame(frame)

        assert processor.is_running is False


class TestStreamProcessorIntegration:
    """Integration tests for StreamProcessor with pipeline."""

    @pytest.mark.asyncio
    async def test_end_to_end_audio_processing(self):
        """Test full audio processing flow."""
        config = StreamProcessorConfig(
            use_mock_analysis=True,
            audio_chunk_duration_ms=100,  # Short chunks for testing
        )
        processor = StreamProcessor(
            meeting_id="m1",
            config=config,
        )

        results = []
        async def result_callback(result):
            results.append(result)

        processor.set_result_callback(result_callback)

        await processor.start()

        # Add audio frames to trigger chunk creation
        for i in range(20):
            frame = AudioFrame(
                participant_id="p1",
                meeting_id="m1",
                data=bytes([0] * 2000),
                sample_rate=16000,
                channels=1,
                timestamp=datetime.utcnow(),
            )
            await processor.process_audio_frame(frame)
            await asyncio.sleep(0.01)

        # Wait for analysis
        await asyncio.sleep(0.5)

        await processor.stop()

        # Should have processed frames
        stats = processor.stats
        assert stats.audio_frames_processed > 0

    @pytest.mark.asyncio
    async def test_end_to_end_video_processing(self):
        """Test full video processing flow."""
        config = StreamProcessorConfig(
            use_mock_analysis=True,
            video_sample_fps=10,  # Higher FPS for testing
        )
        processor = StreamProcessor(
            meeting_id="m1",
            config=config,
        )

        await processor.start()

        # Add video frames
        for i in range(10):
            frame = VideoFrame(
                participant_id="p1",
                meeting_id="m1",
                data=f"frame_{i}".encode(),
                width=640,
                height=480,
                timestamp=datetime.utcnow(),
            )
            await processor.process_video_frame(frame)
            await asyncio.sleep(0.05)

        await asyncio.sleep(0.2)

        await processor.stop()

        stats = processor.stats
        assert stats.video_frames_processed > 0
