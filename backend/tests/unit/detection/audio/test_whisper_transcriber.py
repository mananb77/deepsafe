"""
Tests for Local Whisper Transcriber
"""

import struct
import pytest
from unittest.mock import patch, MagicMock

from src.services.detection.audio.whisper_transcriber import WhisperTranscriber


class TestWhisperTranscriber:
    """Tests for WhisperTranscriber class."""

    @pytest.fixture
    def transcriber(self) -> WhisperTranscriber:
        """Create transcriber instance."""
        return WhisperTranscriber(model_size="small", device="cpu")

    @pytest.fixture
    def silence_audio(self) -> bytes:
        """Generate 1 second of silence at 16kHz."""
        samples = [0] * 16000
        return struct.pack(f"{len(samples)}h", *samples)

    @pytest.fixture
    def short_audio(self) -> bytes:
        """Generate very short audio (< 0.5s)."""
        samples = [0] * 4000
        return struct.pack(f"{len(samples)}h", *samples)

    async def test_transcribe_returns_dict(self, transcriber, silence_audio):
        """Test that transcribe returns expected dict shape."""
        import src.services.detection.audio.whisper_transcriber as mod

        mod._model = "unavailable"

        result = await transcriber.transcribe(silence_audio, sample_rate=16000)
        assert isinstance(result, dict)
        assert "transcript" in result
        assert "confidence" in result

    async def test_short_audio_returns_error(self, transcriber, short_audio):
        """Test that very short audio returns error."""
        import src.services.detection.audio.whisper_transcriber as mod

        # Set model to a mock that would work, to get past the load check
        mock_model = MagicMock()
        mod._model = mock_model

        result = await transcriber.transcribe(short_audio, sample_rate=16000)
        assert result["transcript"] == ""
        assert "too short" in result.get("error", "")

    async def test_unavailable_model_returns_error(self, transcriber, silence_audio):
        """Test handling when faster-whisper is not installed."""
        import src.services.detection.audio.whisper_transcriber as mod

        mod._model = "unavailable"

        result = await transcriber.transcribe(silence_audio, sample_rate=16000)
        assert result["transcript"] == ""
        assert "unavailable" in result.get("error", "").lower()

    async def test_transcribe_with_mock_model(self, transcriber, silence_audio):
        """Test transcription with a mocked Whisper model."""
        import src.services.detection.audio.whisper_transcriber as mod

        mock_segment = MagicMock()
        mock_segment.text = "Hello, this is a test."
        mock_segment.avg_log_prob = -0.3

        mock_info = MagicMock()
        mock_info.language = "en"
        mock_info.language_probability = 0.95
        mock_info.duration = 1.0

        mock_model = MagicMock()
        mock_model.transcribe.return_value = ([mock_segment], mock_info)
        mod._model = mock_model

        result = await transcriber.transcribe(silence_audio, sample_rate=16000)
        assert result["transcript"] == "Hello, this is a test."
        assert result["language"] == "en"
        assert result["confidence"] > 0.0

    async def test_transcribe_with_language_hint(self, transcriber, silence_audio):
        """Test transcription with a language hint."""
        import src.services.detection.audio.whisper_transcriber as mod

        mock_segment = MagicMock()
        mock_segment.text = "Bonjour"
        mock_segment.avg_log_prob = -0.2

        mock_info = MagicMock()
        mock_info.language = "fr"
        mock_info.language_probability = 0.99
        mock_info.duration = 1.0

        mock_model = MagicMock()
        mock_model.transcribe.return_value = ([mock_segment], mock_info)
        mod._model = mock_model

        result = await transcriber.transcribe(silence_audio, sample_rate=16000, language="fr")
        assert result["language"] == "fr"
        mock_model.transcribe.assert_called_once()
        call_kwargs = mock_model.transcribe.call_args
        assert call_kwargs[1].get("language") == "fr"

    @pytest.fixture(autouse=True)
    def _reset_singleton(self):
        """Reset model singleton between tests."""
        import src.services.detection.audio.whisper_transcriber as mod

        original_model = mod._model
        yield
        mod._model = original_model
