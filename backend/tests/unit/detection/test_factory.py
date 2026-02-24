"""
Tests for Detector Factory
"""

import pytest
from unittest.mock import patch, MagicMock

from src.shared.config.settings import DetectionMode
from src.services.detection.factory import create_detectors
from src.services.detection.audio.detector import AudioDeepfakeDetector
from src.services.detection.video.detector import VideoDeepfakeDetector
from src.services.detection.social_engineering.detector import SocialEngineeringDetector


class TestDetectorFactory:
    """Tests for create_detectors factory function."""

    def test_api_mode_returns_correct_config(self):
        """Test API mode creates detectors with API enabled."""
        with patch(
            "src.services.detection.audio.detector.ResembleAIClient"
        ), patch(
            "src.services.detection.video.detector.SensityClient"
        ), patch(
            "src.services.detection.social_engineering.detector.GPT4Analyzer"
        ):
            audio, video, social = create_detectors(DetectionMode.API)

        assert isinstance(audio, AudioDeepfakeDetector)
        assert isinstance(video, VideoDeepfakeDetector)
        assert isinstance(social, SocialEngineeringDetector)

        assert audio.enable_api is True
        assert audio.enable_local is False
        assert video.enable_api is True
        assert video.enable_local is False
        assert social.enable_gpt4 is True
        assert social.enable_local_llm is False

    def test_local_mode_returns_correct_config(self):
        """Test local mode creates detectors with local enabled."""
        with patch(
            "src.services.detection.factory.get_settings"
        ) as mock_settings:
            mock_detection = MagicMock()
            mock_detection.audio_model = "facebook/wav2vec2-base"
            mock_detection.video_model = "google/efficientnet-b4"
            mock_detection.ollama_model = "phi3:mini"
            mock_detection.ollama_url = "http://localhost:11434"
            mock_detection.local_device = "cpu"
            mock_settings.return_value.detection = mock_detection

            audio, video, social = create_detectors(DetectionMode.LOCAL)

        assert isinstance(audio, AudioDeepfakeDetector)
        assert isinstance(video, VideoDeepfakeDetector)
        assert isinstance(social, SocialEngineeringDetector)

        assert audio.enable_api is False
        assert video.enable_api is False
        assert social.enable_gpt4 is False

    def test_hybrid_mode_enables_both(self):
        """Test hybrid mode enables both API and local."""
        with patch(
            "src.services.detection.factory.get_settings"
        ) as mock_settings, patch(
            "src.services.detection.audio.detector.ResembleAIClient"
        ), patch(
            "src.services.detection.video.detector.SensityClient"
        ), patch(
            "src.services.detection.social_engineering.detector.GPT4Analyzer"
        ):
            mock_detection = MagicMock()
            mock_detection.audio_model = "facebook/wav2vec2-base"
            mock_detection.video_model = "google/efficientnet-b4"
            mock_detection.ollama_model = "phi3:mini"
            mock_detection.ollama_url = "http://localhost:11434"
            mock_detection.local_device = "cpu"
            mock_settings.return_value.detection = mock_detection

            audio, video, social = create_detectors(DetectionMode.HYBRID)

        assert audio.enable_api is True
        assert video.enable_api is True
        assert social.enable_gpt4 is True

    def test_local_mode_has_local_detectors(self):
        """Test local mode attaches local detector instances."""
        with patch(
            "src.services.detection.factory.get_settings"
        ) as mock_settings:
            mock_detection = MagicMock()
            mock_detection.audio_model = "facebook/wav2vec2-base"
            mock_detection.video_model = "google/efficientnet-b4"
            mock_detection.ollama_model = "phi3:mini"
            mock_detection.ollama_url = "http://localhost:11434"
            mock_detection.local_device = "cpu"
            mock_settings.return_value.detection = mock_detection

            audio, video, social = create_detectors(DetectionMode.LOCAL)

        # Local detectors should be set (they use lazy imports, so always succeed)
        assert audio.local_audio_detector is not None
        assert video.local_video_detector is not None
        assert social.local_llm_analyzer is not None

    def test_api_mode_has_no_local_detectors(self):
        """Test API mode does not attach local detector instances."""
        with patch(
            "src.services.detection.audio.detector.ResembleAIClient"
        ), patch(
            "src.services.detection.video.detector.SensityClient"
        ), patch(
            "src.services.detection.social_engineering.detector.GPT4Analyzer"
        ):
            audio, video, social = create_detectors(DetectionMode.API)

        assert audio.local_audio_detector is None
        assert video.local_video_detector is None
        assert social.local_llm_analyzer is None

    def test_factory_reads_from_settings_when_no_mode(self):
        """Test factory reads detection mode from settings when none given."""
        with patch(
            "src.services.detection.factory.get_settings"
        ) as mock_settings, patch(
            "src.services.detection.audio.detector.ResembleAIClient"
        ), patch(
            "src.services.detection.video.detector.SensityClient"
        ), patch(
            "src.services.detection.social_engineering.detector.GPT4Analyzer"
        ):
            mock_detection = MagicMock()
            mock_detection.mode = DetectionMode.API
            mock_detection.audio_model = "facebook/wav2vec2-base"
            mock_detection.video_model = "google/efficientnet-b4"
            mock_detection.ollama_model = "phi3:mini"
            mock_detection.ollama_url = "http://localhost:11434"
            mock_detection.local_device = "cpu"
            mock_settings.return_value.detection = mock_detection

            audio, video, social = create_detectors()

        assert audio.enable_api is True
        assert audio.enable_local is False
