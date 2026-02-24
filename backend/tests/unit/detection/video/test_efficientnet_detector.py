"""
Tests for EfficientNet Local Video Deepfake Detector
"""

import pytest
import numpy as np
from unittest.mock import patch, MagicMock

from src.services.detection.video.efficientnet_detector import EfficientNetDetector


class TestEfficientNetDetector:
    """Tests for EfficientNetDetector class."""

    @pytest.fixture
    def detector(self) -> EfficientNetDetector:
        """Create detector instance."""
        return EfficientNetDetector(model_name="google/efficientnet-b4", device="cpu")

    @pytest.fixture
    def fake_image_bytes(self) -> bytes:
        """Generate a minimal valid JPEG-like image bytes."""
        # Create a small 8x8 RGB image and encode as raw bytes
        # For testing pixel_based_analysis, we need it decodable
        try:
            from PIL import Image
            import io

            img = Image.new("RGB", (64, 64), color=(128, 128, 128))
            buf = io.BytesIO()
            img.save(buf, format="JPEG")
            return buf.getvalue()
        except ImportError:
            # If PIL not available, return raw bytes that will hit the error path
            return b"\xff\xd8\xff\xe0" + b"\x00" * 100

    @pytest.fixture
    def blank_image_bytes(self) -> bytes:
        """Generate blank (all-zero) image bytes."""
        try:
            from PIL import Image
            import io

            img = Image.new("RGB", (64, 64), color=(0, 0, 0))
            buf = io.BytesIO()
            img.save(buf, format="JPEG")
            return buf.getvalue()
        except ImportError:
            return b"\x00" * 100

    async def test_analyze_returns_dict(self, detector, fake_image_bytes):
        """Test that analyze returns a dict with expected keys."""
        import src.services.detection.video.efficientnet_detector as mod

        mod._model = "fallback"
        mod._processor = "fallback"

        result = await detector.analyze(fake_image_bytes)
        assert isinstance(result, dict)
        assert "is_deepfake" in result
        assert "confidence" in result

    async def test_analyze_video_returns_aggregate(self, detector, fake_image_bytes):
        """Test that analyze_video aggregates multiple frames."""
        import src.services.detection.video.efficientnet_detector as mod

        mod._model = "fallback"
        mod._processor = "fallback"

        frames = [fake_image_bytes] * 5
        result = await detector.analyze_video(frames, sample_rate=1)
        assert isinstance(result, dict)
        assert "frames_analyzed" in result
        assert result["frames_analyzed"] == 5
        assert "frames_with_deepfake" in result

    async def test_analyze_video_empty_frames(self, detector):
        """Test analyze_video with no frames."""
        result = await detector.analyze_video([])
        assert result["frames_analyzed"] == 0
        assert result["confidence"] == 0.0

    async def test_analyze_video_sampling(self, detector, fake_image_bytes):
        """Test that analyze_video respects sample_rate."""
        import src.services.detection.video.efficientnet_detector as mod

        mod._model = "fallback"
        mod._processor = "fallback"

        frames = [fake_image_bytes] * 10
        result = await detector.analyze_video(frames, sample_rate=5)
        assert result["frames_analyzed"] == 2  # 10 / 5

    async def test_pixel_fallback_returns_valid_result(self, detector, fake_image_bytes):
        """Test the pixel-based fallback analysis."""
        import src.services.detection.video.efficientnet_detector as mod

        mod._model = "fallback"
        mod._processor = "fallback"

        result = await detector.analyze(fake_image_bytes)
        assert isinstance(result.get("is_deepfake"), bool)
        assert 0.0 <= result.get("confidence", 0) <= 100.0

    async def test_invalid_image_returns_error(self, detector):
        """Test handling of invalid image data."""
        import src.services.detection.video.efficientnet_detector as mod

        mod._model = "fallback"
        mod._processor = "fallback"

        result = await detector.analyze(b"not-an-image")
        # Should either return error or handle gracefully
        assert isinstance(result, dict)

    @pytest.fixture(autouse=True)
    def _reset_singleton(self):
        """Reset model singleton between tests."""
        import src.services.detection.video.efficientnet_detector as mod

        original_model = mod._model
        original_processor = mod._processor
        yield
        mod._model = original_model
        mod._processor = original_processor
