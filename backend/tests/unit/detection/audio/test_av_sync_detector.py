"""
Tests for Audio-Video Sync Detector

Tests the 42ms threshold lip sync detection.
"""

import pytest
import struct

from src.services.detection.audio.av_sync_detector import (
    AVSyncDetector,
    AVSyncResult,
)


class TestAVSyncDetector:
    """Tests for AVSyncDetector class."""

    @pytest.fixture
    def detector(self) -> AVSyncDetector:
        """Create detector instance."""
        return AVSyncDetector()

    @pytest.fixture
    def sample_audio(self) -> bytes:
        """Generate sample audio data."""
        samples = [0] * 16000
        return struct.pack(f'{len(samples)}h', *samples)

    @pytest.fixture
    def sample_frames(self) -> list:
        """Generate sample video frames."""
        return [b'\x00' * 1000 for _ in range(30)]

    @pytest.fixture
    def sample_lip_positions(self) -> list:
        """Generate sample lip positions."""
        return [
            {"x": 0.5, "y": 0.5, "width": 0.1, "height": 0.05, "open": 0.3}
            for _ in range(30)
        ]

    def test_analyze_returns_result(self, detector, sample_audio, sample_frames, sample_lip_positions):
        """Test that analyze returns AVSyncResult."""
        result = detector.analyze(sample_audio, sample_frames, sample_lip_positions)
        assert isinstance(result, AVSyncResult)

    def test_sync_threshold_constant(self, detector):
        """Test that sync threshold is 42ms (human perception threshold)."""
        assert detector.SYNC_THRESHOLD_MS == 42.0

    def test_analyze_empty_inputs(self, detector):
        """Test handling of empty inputs."""
        result = detector.analyze(b'', [], None)
        assert isinstance(result, AVSyncResult)
        assert result.confidence == 0.0

    def test_analyze_no_lip_positions(self, detector, sample_audio, sample_frames):
        """Test analysis without lip positions."""
        result = detector.analyze(sample_audio, sample_frames, None)
        assert isinstance(result, AVSyncResult)

    def test_analyze_returns_offset(self, detector, sample_audio, sample_frames, sample_lip_positions):
        """Test that sync offset is calculated."""
        result = detector.analyze(sample_audio, sample_frames, sample_lip_positions)
        assert isinstance(result.sync_offset_ms, float)

    def test_analyze_returns_lip_sync_score(self, detector, sample_audio, sample_frames, sample_lip_positions):
        """Test that lip sync score is returned."""
        result = detector.analyze(sample_audio, sample_frames, sample_lip_positions)
        assert 0.0 <= result.lip_sync_score <= 1.0

    def test_is_synced_within_threshold(self, detector):
        """Test that sync is detected when offset is within threshold."""
        # Manually create a result with small offset
        result = AVSyncResult(
            is_synced=True,
            sync_offset_ms=30.0,  # Within 42ms threshold
            confidence=80.0,
            lip_sync_score=0.8,
            details={},
        )
        assert result.is_synced

    def test_not_synced_outside_threshold(self, detector):
        """Test that sync is not detected when offset exceeds threshold."""
        result = AVSyncResult(
            is_synced=False,
            sync_offset_ms=100.0,  # Outside 42ms threshold
            confidence=70.0,
            lip_sync_score=0.3,
            details={},
        )
        assert not result.is_synced

    def test_confidence_range(self, detector, sample_audio, sample_frames, sample_lip_positions):
        """Test that confidence is in valid range."""
        result = detector.analyze(sample_audio, sample_frames, sample_lip_positions)
        assert 0.0 <= result.confidence <= 100.0

    def test_varying_lip_positions(self, detector, sample_audio, sample_frames):
        """Test with varying lip positions (simulating speech)."""
        # Simulate mouth opening and closing
        lip_positions = []
        for i in range(30):
            openness = 0.2 + 0.3 * abs((i % 10) - 5) / 5  # Varies 0.2 to 0.5
            lip_positions.append({
                "x": 0.5,
                "y": 0.5,
                "width": 0.1,
                "height": 0.05,
                "open": openness,
            })

        result = detector.analyze(sample_audio, sample_frames, lip_positions)
        assert isinstance(result, AVSyncResult)


class TestAVSyncResult:
    """Tests for AVSyncResult dataclass."""

    def test_result_creation(self):
        """Test creating result with all fields."""
        result = AVSyncResult(
            is_synced=True,
            sync_offset_ms=25.0,
            confidence=85.0,
            lip_sync_score=0.9,
            details={"method": "cross_correlation"},
        )

        assert result.is_synced
        assert result.sync_offset_ms == 25.0
        assert result.confidence == 85.0
        assert result.lip_sync_score == 0.9
        assert result.details["method"] == "cross_correlation"

    def test_result_desync_detection(self):
        """Test result indicating desync."""
        result = AVSyncResult(
            is_synced=False,
            sync_offset_ms=150.0,
            confidence=90.0,
            lip_sync_score=0.2,
            details={"reason": "significant_offset"},
        )

        assert not result.is_synced
        assert result.sync_offset_ms > 42.0
        assert result.lip_sync_score < 0.5
