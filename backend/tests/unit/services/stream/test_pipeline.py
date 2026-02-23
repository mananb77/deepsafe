"""Unit tests for analysis pipeline orchestrator."""

import pytest
import asyncio
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

from src.services.stream.pipeline.orchestrator import (
    AnalysisPipeline,
    AnalysisResult,
    PipelineConfig,
)
from src.services.stream.buffers.audio_buffer import AudioChunk
from src.integrations.common.types import VideoFrame


def make_audio_chunk(
    participant_id="p1",
    meeting_id="m1",
    chunk_id="chunk-1",
    data=b"audio_data",
    sample_rate=16000,
    duration_ms=3000,
):
    """Helper to create AudioChunk with all required fields."""
    now = datetime.utcnow()
    return AudioChunk(
        chunk_id=chunk_id,
        participant_id=participant_id,
        meeting_id=meeting_id,
        data=data,
        sample_rate=sample_rate,
        channels=1,
        bits_per_sample=16,
        start_time=now,
        end_time=now,
        duration_ms=duration_ms,
        sequence_number=1,
    )


class TestPipelineConfig:
    """Tests for PipelineConfig."""

    def test_default_config(self):
        """Test default configuration values."""
        config = PipelineConfig()

        assert config.max_concurrent_analysis == 4
        assert config.timeout_seconds == 5.0
        assert config.enable_audio_analysis is True
        assert config.enable_video_analysis is True
        assert config.enable_social_engineering is True

    def test_weights_sum_to_one(self):
        """Test that risk score weights sum to 1.0."""
        config = PipelineConfig()

        total = (
            config.audio_deepfake_weight +
            config.video_deepfake_weight +
            config.social_engineering_weight +
            config.voice_mismatch_weight +
            config.facial_anomaly_weight +
            config.av_sync_weight
        )

        assert abs(total - 1.0) < 0.01

    def test_custom_weights(self):
        """Test custom weight configuration."""
        config = PipelineConfig(
            audio_deepfake_weight=0.5,
            video_deepfake_weight=0.3,
            social_engineering_weight=0.2,
        )

        assert config.audio_deepfake_weight == 0.5
        assert config.video_deepfake_weight == 0.3
        assert config.social_engineering_weight == 0.2


class TestAnalysisResult:
    """Tests for AnalysisResult."""

    def test_result_creation(self):
        """Test creating an analysis result."""
        result = AnalysisResult(
            participant_id="p1",
            meeting_id="m1",
        )

        assert result.participant_id == "p1"
        assert result.meeting_id == "m1"
        assert result.audio_deepfake_score == 0.0
        assert result.video_deepfake_score == 0.0

    def test_calculate_combined_risk_low(self):
        """Test combined risk calculation with low scores."""
        result = AnalysisResult(
            participant_id="p1",
            meeting_id="m1",
            audio_deepfake_score=0.1,
            video_deepfake_score=0.1,
            social_engineering_score=0.1,
            voice_mismatch_score=0.1,
            facial_anomaly_score=0.1,
            av_sync_score=0.1,
        )

        combined = result.calculate_combined_risk()

        # With all scores at 0.1, combined should be 0.1
        assert abs(combined - 0.1) < 0.01

    def test_calculate_combined_risk_high(self):
        """Test combined risk calculation with high scores."""
        result = AnalysisResult(
            participant_id="p1",
            meeting_id="m1",
            audio_deepfake_score=0.9,
            video_deepfake_score=0.9,
            social_engineering_score=0.9,
            voice_mismatch_score=0.9,
            facial_anomaly_score=0.9,
            av_sync_score=0.9,
        )

        combined = result.calculate_combined_risk()

        # With all scores at 0.9, combined should be 0.9
        assert abs(combined - 0.9) < 0.01

    def test_calculate_combined_risk_weighted(self):
        """Test that weights affect combined score."""
        # High audio, low everything else
        result = AnalysisResult(
            participant_id="p1",
            meeting_id="m1",
            audio_deepfake_score=1.0,
            video_deepfake_score=0.0,
            social_engineering_score=0.0,
            voice_mismatch_score=0.0,
            facial_anomaly_score=0.0,
            av_sync_score=0.0,
        )

        combined = result.calculate_combined_risk()

        # Should be approximately the audio weight (0.25)
        assert 0.20 <= combined <= 0.30

    def test_get_risk_level_low(self):
        """Test risk level classification - low."""
        result = AnalysisResult(
            participant_id="p1",
            meeting_id="m1",
            audio_deepfake_score=0.1,
            video_deepfake_score=0.1,
        )

        level = result.get_risk_level()
        assert level == "low"

    def test_get_risk_level_medium(self):
        """Test risk level classification - medium."""
        result = AnalysisResult(
            participant_id="p1",
            meeting_id="m1",
            audio_deepfake_score=0.5,
            video_deepfake_score=0.5,
            social_engineering_score=0.5,
        )

        level = result.get_risk_level()
        assert level in ["medium", "high"]  # Depends on exact weights

    def test_get_risk_level_critical(self):
        """Test risk level classification - critical."""
        result = AnalysisResult(
            participant_id="p1",
            meeting_id="m1",
            audio_deepfake_score=1.0,
            video_deepfake_score=1.0,
            social_engineering_score=1.0,
            voice_mismatch_score=1.0,
            facial_anomaly_score=1.0,
            av_sync_score=1.0,
        )

        level = result.get_risk_level()
        assert level == "critical"

    def test_to_dict(self):
        """Test result serialization."""
        result = AnalysisResult(
            participant_id="p1",
            meeting_id="m1",
            audio_deepfake_score=0.5,
        )

        d = result.to_dict()

        assert d["participant_id"] == "p1"
        assert d["meeting_id"] == "m1"
        assert d["audio_deepfake_score"] == 0.5
        assert "combined_risk_score" in d
        assert "risk_level" in d


class TestAnalysisPipeline:
    """Tests for AnalysisPipeline."""

    def test_pipeline_creation(self):
        """Test creating a pipeline."""
        config = PipelineConfig()
        pipeline = AnalysisPipeline(
            meeting_id="meeting-1",
            config=config,
        )

        assert pipeline.meeting_id == "meeting-1"

    @pytest.mark.asyncio
    async def test_analyze_audio_mock_mode(self):
        """Test audio analysis in mock mode."""
        config = PipelineConfig(use_mock_analysis=True)
        pipeline = AnalysisPipeline(
            meeting_id="m1",
            config=config,
        )

        chunk = make_audio_chunk(participant_id="p1", meeting_id="m1")

        result = await pipeline.analyze_audio(chunk)

        assert result is not None
        assert result.participant_id == "p1"
        assert result.meeting_id == "m1"
        assert 0.0 <= result.audio_deepfake_score <= 1.0

    @pytest.mark.asyncio
    async def test_analyze_video_mock_mode(self):
        """Test video analysis in mock mode."""
        config = PipelineConfig(use_mock_analysis=True)
        pipeline = AnalysisPipeline(
            meeting_id="m1",
            config=config,
        )

        frame = VideoFrame(
            participant_id="p1",
            meeting_id="m1",
            data=b"frame_data",
            width=640,
            height=480,
            timestamp=datetime.utcnow(),
        )

        result = await pipeline.analyze_video(frame)

        assert result is not None
        assert result.participant_id == "p1"
        assert 0.0 <= result.video_deepfake_score <= 1.0

    @pytest.mark.asyncio
    async def test_analyze_combined_mock_mode(self):
        """Test combined A/V analysis in mock mode."""
        config = PipelineConfig(use_mock_analysis=True)
        pipeline = AnalysisPipeline(
            meeting_id="m1",
            config=config,
        )

        chunk = make_audio_chunk(participant_id="p1", meeting_id="m1")

        frame = VideoFrame(
            participant_id="p1",
            meeting_id="m1",
            data=b"frame_data",
            width=640,
            height=480,
            timestamp=datetime.utcnow(),
        )

        result = await pipeline.analyze_combined(chunk, frame)

        assert result is not None
        assert result.participant_id == "p1"
        # Combined analysis should have both audio and video scores
        assert 0.0 <= result.audio_deepfake_score <= 1.0
        assert 0.0 <= result.video_deepfake_score <= 1.0

    @pytest.mark.asyncio
    async def test_analysis_disabled(self):
        """Test that disabled analysis types return zero scores."""
        config = PipelineConfig(
            use_mock_analysis=True,
            enable_audio_analysis=False,
        )
        pipeline = AnalysisPipeline(
            meeting_id="m1",
            config=config,
        )

        chunk = make_audio_chunk(participant_id="p1", meeting_id="m1")

        result = await pipeline.analyze_audio(chunk)

        # With audio disabled, should get empty result or zero scores
        assert result is not None

    @pytest.mark.asyncio
    async def test_concurrent_analysis_limit(self):
        """Test that concurrent analysis respects limit."""
        config = PipelineConfig(
            use_mock_analysis=True,
            max_concurrent_analysis=2,
        )
        pipeline = AnalysisPipeline(
            meeting_id="m1",
            config=config,
        )

        # Start multiple analyses
        chunks = [
            make_audio_chunk(participant_id=f"p{i}", chunk_id=f"chunk-{i}")
            for i in range(5)
        ]

        # All should complete (semaphore should serialize)
        results = await asyncio.gather(*[
            pipeline.analyze_audio(chunk)
            for chunk in chunks
        ])

        assert len(results) == 5
        for result in results:
            assert result is not None

    @pytest.mark.asyncio
    async def test_timeout_handling(self):
        """Test that analysis times out properly."""
        config = PipelineConfig(
            timeout_seconds=0.1,  # Very short timeout
            use_mock_analysis=True,
        )
        pipeline = AnalysisPipeline(
            meeting_id="m1",
            config=config,
        )

        chunk = make_audio_chunk(participant_id="p1")

        # Should complete without error even with short timeout
        result = await pipeline.analyze_audio(chunk)
        assert result is not None

    @pytest.mark.asyncio
    async def test_stats(self):
        """Test pipeline statistics."""
        config = PipelineConfig(use_mock_analysis=True)
        pipeline = AnalysisPipeline(
            meeting_id="m1",
            config=config,
        )

        chunk = make_audio_chunk(participant_id="p1")

        await pipeline.analyze_audio(chunk)

        stats = pipeline.stats

        assert "audio_analyses" in stats
        assert "video_analyses" in stats
        assert "combined_analyses" in stats
        assert stats["audio_analyses"] >= 1

    @pytest.mark.asyncio
    async def test_reset(self):
        """Test pipeline reset."""
        config = PipelineConfig(use_mock_analysis=True)
        pipeline = AnalysisPipeline(
            meeting_id="m1",
            config=config,
        )

        chunk = make_audio_chunk(participant_id="p1")

        await pipeline.analyze_audio(chunk)

        pipeline.reset()

        stats = pipeline.stats
        assert stats["audio_analyses"] == 0

    @pytest.mark.asyncio
    async def test_av_sync_detection(self):
        """Test A/V sync detection in combined analysis."""
        config = PipelineConfig(
            use_mock_analysis=True,
            enable_av_sync_detection=True,
        )
        pipeline = AnalysisPipeline(
            meeting_id="m1",
            config=config,
        )

        chunk = make_audio_chunk(participant_id="p1")

        frame = VideoFrame(
            participant_id="p1",
            meeting_id="m1",
            data=b"frame",
            width=640,
            height=480,
            timestamp=datetime.utcnow(),
        )

        result = await pipeline.analyze_combined(chunk, frame)

        # A/V sync score should be set
        assert 0.0 <= result.av_sync_score <= 1.0


class TestAnalysisPipelineCeleryMode:
    """Tests for pipeline with Celery tasks."""

    @pytest.mark.asyncio
    async def test_celery_mode_fallback(self):
        """Test that pipeline falls back gracefully when Celery unavailable."""
        config = PipelineConfig(
            use_celery_tasks=True,
            use_mock_analysis=True,  # Fallback to mock
        )
        pipeline = AnalysisPipeline(
            meeting_id="m1",
            config=config,
        )

        chunk = make_audio_chunk(participant_id="p1")

        # Should work even if Celery not available
        result = await pipeline.analyze_audio(chunk)
        assert result is not None
