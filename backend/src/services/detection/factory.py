"""
Detector Factory

Creates detection service instances based on DETECTION_MODE.
Handles local model imports gracefully so missing ML deps don't crash the app.
"""

import logging
from typing import Tuple

from src.shared.config import get_settings
from src.shared.config.settings import DetectionMode
from src.services.detection.audio.detector import AudioDeepfakeDetector
from src.services.detection.video.detector import VideoDeepfakeDetector
from src.services.detection.social_engineering.detector import SocialEngineeringDetector

logger = logging.getLogger(__name__)


def create_detectors(
    mode: DetectionMode | None = None,
) -> Tuple[AudioDeepfakeDetector, VideoDeepfakeDetector, SocialEngineeringDetector]:
    """
    Create detector instances configured for the given detection mode.

    Args:
        mode: Detection mode. If None, reads from settings.

    Returns:
        Tuple of (audio_detector, video_detector, social_engineering_detector).
    """
    if mode is None:
        settings = get_settings()
        mode = settings.detection.mode

    logger.info(f"Creating detectors in '{mode.value}' mode")

    if mode == DetectionMode.LOCAL:
        return _create_local_detectors()
    elif mode == DetectionMode.API:
        return _create_api_detectors()
    elif mode == DetectionMode.HYBRID:
        return _create_hybrid_detectors()
    else:
        logger.warning(f"Unknown detection mode '{mode}', falling back to local")
        return _create_local_detectors()


def _create_local_detectors() -> Tuple[
    AudioDeepfakeDetector, VideoDeepfakeDetector, SocialEngineeringDetector
]:
    """Create detectors using only local models (no API keys needed)."""
    settings = get_settings()
    detection = settings.detection

    # Try to create local model wrappers
    wav2vec = _create_wav2vec_detector(detection.audio_model, detection.local_device)
    efficientnet = _create_efficientnet_detector(detection.video_model, detection.local_device)
    ollama = _create_ollama_analyzer(detection.ollama_model, detection.ollama_url)

    audio = AudioDeepfakeDetector(
        enable_api=False,
        local_audio_detector=wav2vec,
        enable_local=wav2vec is not None,
    )

    video = VideoDeepfakeDetector(
        enable_api=False,
        local_video_detector=efficientnet,
        enable_local=efficientnet is not None,
    )

    social = SocialEngineeringDetector(
        enable_gpt4=False,
        local_llm_analyzer=ollama,
        enable_local_llm=ollama is not None,
    )

    return audio, video, social


def _create_api_detectors() -> Tuple[
    AudioDeepfakeDetector, VideoDeepfakeDetector, SocialEngineeringDetector
]:
    """Create detectors using external APIs (current behavior)."""
    audio = AudioDeepfakeDetector(enable_api=True, enable_local=False)
    video = VideoDeepfakeDetector(enable_api=True, enable_local=False)
    social = SocialEngineeringDetector(enable_gpt4=True, enable_local_llm=False)

    return audio, video, social


def _create_hybrid_detectors() -> Tuple[
    AudioDeepfakeDetector, VideoDeepfakeDetector, SocialEngineeringDetector
]:
    """Create detectors that try API first, fall back to local models."""
    settings = get_settings()
    detection = settings.detection

    wav2vec = _create_wav2vec_detector(detection.audio_model, detection.local_device)
    efficientnet = _create_efficientnet_detector(detection.video_model, detection.local_device)
    ollama = _create_ollama_analyzer(detection.ollama_model, detection.ollama_url)

    audio = AudioDeepfakeDetector(
        enable_api=True,
        local_audio_detector=wav2vec,
        enable_local=wav2vec is not None,
    )

    video = VideoDeepfakeDetector(
        enable_api=True,
        local_video_detector=efficientnet,
        enable_local=efficientnet is not None,
    )

    social = SocialEngineeringDetector(
        enable_gpt4=True,
        local_llm_analyzer=ollama,
        enable_local_llm=ollama is not None,
    )

    return audio, video, social


def _create_wav2vec_detector(model_name: str, device: str):
    """Try to create Wav2Vec detector, return None if deps missing."""
    try:
        from src.services.detection.audio.wav2vec_detector import Wav2VecDetector

        return Wav2VecDetector(model_name=model_name, device=device)
    except ImportError as e:
        logger.warning(f"Wav2Vec detector unavailable: {e}")
        return None


def _create_efficientnet_detector(model_name: str, device: str):
    """Try to create EfficientNet detector, return None if deps missing."""
    try:
        from src.services.detection.video.efficientnet_detector import EfficientNetDetector

        return EfficientNetDetector(model_name=model_name, device=device)
    except ImportError as e:
        logger.warning(f"EfficientNet detector unavailable: {e}")
        return None


def _create_ollama_analyzer(model: str, ollama_url: str):
    """Try to create Ollama analyzer, return None if deps missing."""
    try:
        from src.services.detection.social_engineering.ollama_analyzer import OllamaAnalyzer

        return OllamaAnalyzer(model=model, ollama_url=ollama_url)
    except ImportError as e:
        logger.warning(f"Ollama analyzer unavailable: {e}")
        return None
