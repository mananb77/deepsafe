"""
Local Whisper Transcriber

Uses faster-whisper for local audio transcription.
Lazy-loads model (~460MB for "small").
"""

import logging
from typing import Any, Dict, Optional

import numpy as np

logger = logging.getLogger(__name__)

# Lazy-loaded singleton
_model = None


def _load_model(model_size: str, device: str):
    """Load faster-whisper model (singleton)."""
    global _model

    if _model is not None:
        return

    try:
        from faster_whisper import WhisperModel

        compute_type = "int8" if device == "cpu" else "float16"
        logger.info(f"Loading Whisper model: {model_size} on {device} ({compute_type})")
        _model = WhisperModel(
            model_size,
            device=device,
            compute_type=compute_type,
        )
        logger.info("Whisper model loaded successfully")

    except ImportError:
        logger.warning("faster-whisper not installed. Transcription unavailable.")
        _model = "unavailable"
    except Exception as e:
        logger.warning(f"Failed to load Whisper model: {e}")
        _model = "unavailable"


class WhisperTranscriber:
    """
    Local audio transcription using faster-whisper.

    Provides transcription for audio chunks to feed into
    social engineering detection.
    """

    def __init__(
        self,
        model_size: str = "small",
        device: str = "cpu",
    ):
        self.model_size = model_size
        self.device = device

    async def transcribe(
        self,
        audio_data: bytes,
        sample_rate: int = 16000,
        language: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Transcribe audio data to text.

        Args:
            audio_data: Raw audio bytes (PCM16).
            sample_rate: Audio sample rate.
            language: Optional language code (e.g., "en").

        Returns:
            {"transcript": str, "confidence": float, "language": str, ...}
        """
        try:
            _load_model(self.model_size, self.device)
        except Exception as e:
            return {
                "transcript": "",
                "confidence": 0.0,
                "error": f"Model load failed: {e}",
            }

        if _model == "unavailable":
            return {
                "transcript": "",
                "confidence": 0.0,
                "error": "Whisper model unavailable. Install faster-whisper.",
            }

        try:
            audio_array = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0

            if len(audio_array) < sample_rate * 0.5:
                return {
                    "transcript": "",
                    "confidence": 0.0,
                    "error": "Audio too short for transcription",
                }

            kwargs = {"beam_size": 5}
            if language:
                kwargs["language"] = language

            segments, info = _model.transcribe(audio_array, **kwargs)

            transcript_parts = []
            total_confidence = 0.0
            segment_count = 0

            for segment in segments:
                transcript_parts.append(segment.text)
                total_confidence += segment.avg_log_prob
                segment_count += 1

            transcript = " ".join(transcript_parts).strip()
            avg_confidence = (total_confidence / segment_count) if segment_count > 0 else 0.0
            # Convert log prob to 0-1 confidence
            confidence = min(1.0, max(0.0, 1.0 + avg_confidence))

            return {
                "transcript": transcript,
                "confidence": confidence,
                "language": info.language if info else (language or "unknown"),
                "language_probability": info.language_probability if info else 0.0,
                "duration": info.duration if info else 0.0,
                "segments": segment_count,
            }

        except Exception as e:
            logger.error(f"Whisper transcription error: {e}")
            return {
                "transcript": "",
                "confidence": 0.0,
                "error": str(e),
            }
