"""
Audio Deepfake Detection Module

Multi-method detection combining:
- Resemble AI API (primary)
- Spectral analysis
- Prosody analysis
- Audio-Video sync detection
- Wav2Vec 2.0 fallback model
"""

from src.services.detection.audio.detector import AudioDeepfakeDetector

__all__ = ["AudioDeepfakeDetector"]
