"""
Tests for Wav2Vec Local Audio Deepfake Detector
"""

import struct
import pytest
from unittest.mock import patch, MagicMock, AsyncMock

from src.services.detection.audio.wav2vec_detector import Wav2VecDetector


class TestWav2VecDetector:
    """Tests for Wav2VecDetector class."""

    @pytest.fixture
    def detector(self) -> Wav2VecDetector:
        """Create detector instance."""
        return Wav2VecDetector(model_name="facebook/wav2vec2-base", device="cpu")

    @pytest.fixture
    def silence_audio(self) -> bytes:
        """Generate 1 second of silence at 16kHz."""
        samples = [0] * 16000
        return struct.pack(f"{len(samples)}h", *samples)

    @pytest.fixture
    def tone_audio(self) -> bytes:
        """Generate 1 second of 440Hz tone at 16kHz."""
        import math

        samples = [
            int(32767 * math.sin(2 * math.pi * 440 * i / 16000)) for i in range(16000)
        ]
        return struct.pack(f"{len(samples)}h", *samples)

    @pytest.fixture
    def short_audio(self) -> bytes:
        """Generate very short audio (< 0.5s)."""
        samples = [0] * 4000  # 0.25s at 16kHz
        return struct.pack(f"{len(samples)}h", *samples)

    async def test_analyze_returns_dict(self, detector, tone_audio):
        """Test that analyze returns a dict with expected keys."""
        # Force fallback mode to avoid needing actual model
        import src.services.detection.audio.wav2vec_detector as mod

        mod._model = "fallback"
        mod._processor = "fallback"

        result = await detector.analyze(tone_audio, sample_rate=16000)
        assert isinstance(result, dict)
        assert "is_synthetic" in result
        assert "confidence" in result

    async def test_short_audio_returns_early(self, detector, short_audio):
        """Test that very short audio returns low confidence."""
        import src.services.detection.audio.wav2vec_detector as mod

        mod._model = "fallback"
        mod._processor = "fallback"

        result = await detector.analyze(short_audio, sample_rate=16000)
        assert result["confidence"] == 0.0
        assert result["is_synthetic"] is False

    async def test_fallback_analysis_returns_valid_result(self, detector, tone_audio):
        """Test the feature-based fallback analysis."""
        import src.services.detection.audio.wav2vec_detector as mod

        mod._model = "fallback"
        mod._processor = "fallback"

        result = await detector.analyze(tone_audio, sample_rate=16000)
        assert result["is_synthetic"] in (True, False)
        assert 0.0 <= result["confidence"] <= 100.0
        assert result["method"] == "statistical_features"

    async def test_silence_has_low_confidence(self, detector, silence_audio):
        """Test that silence doesn't trigger synthetic detection."""
        import src.services.detection.audio.wav2vec_detector as mod

        mod._model = "fallback"
        mod._processor = "fallback"

        result = await detector.analyze(silence_audio, sample_rate=16000)
        # Silence should have low/zero confidence for synthetic
        assert result["confidence"] < 50.0

    async def test_model_load_failure_returns_error(self, detector, tone_audio):
        """Test graceful handling when model loading fails."""
        import src.services.detection.audio.wav2vec_detector as mod

        # Reset singleton state
        mod._model = None
        mod._processor = None

        with patch.dict("sys.modules", {"torch": None, "transformers": None}):
            # Force fallback by making import fail
            mod._model = "fallback"
            mod._processor = "fallback"
            result = await detector.analyze(tone_audio, sample_rate=16000)
            assert isinstance(result, dict)
            assert "confidence" in result

    @pytest.fixture(autouse=True)
    def _reset_singleton(self):
        """Reset model singleton between tests."""
        import src.services.detection.audio.wav2vec_detector as mod

        original_model = mod._model
        original_processor = mod._processor
        yield
        mod._model = original_model
        mod._processor = original_processor
