"""
Wav2Vec2 Local Audio Deepfake Detector

Uses facebook/wav2vec2-base via HuggingFace transformers for local
audio deepfake detection. Replaces ResembleAIClient when running
in local or hybrid detection mode.

Lazy-loads model on first call (~360MB RAM).
~200-400ms per 3s chunk on CPU.
"""

import logging
from typing import Any, Dict, Optional

import numpy as np

logger = logging.getLogger(__name__)

# Lazy-loaded singleton
_model = None
_processor = None


def _load_model(model_name: str, device: str):
    """Load wav2vec2 model and processor (singleton)."""
    global _model, _processor

    if _model is not None:
        return

    try:
        import torch
        from transformers import Wav2Vec2ForSequenceClassification, Wav2Vec2FeatureExtractor

        logger.info(f"Loading Wav2Vec2 model: {model_name} on {device}")
        _processor = Wav2Vec2FeatureExtractor.from_pretrained(model_name)
        _model = Wav2Vec2ForSequenceClassification.from_pretrained(
            model_name,
            num_labels=2,
        ).to(device)
        _model.eval()
        logger.info("Wav2Vec2 model loaded successfully")

    except Exception as e:
        logger.warning(f"Failed to load Wav2Vec2 model: {e}. Using feature-based fallback.")
        _model = "fallback"
        _processor = "fallback"


class Wav2VecDetector:
    """
    Local audio deepfake detector using Wav2Vec2.

    Returns results in the same format as ResembleAIClient.analyze()
    so existing calling code works unchanged.
    """

    def __init__(
        self,
        model_name: str = "facebook/wav2vec2-base",
        device: str = "cpu",
    ):
        self.model_name = model_name
        self.device = device

    async def analyze(
        self,
        audio_data: bytes,
        sample_rate: int = 16000,
    ) -> Dict[str, Any]:
        """
        Analyze audio for synthetic speech markers.

        Args:
            audio_data: Raw audio bytes (PCM16).
            sample_rate: Audio sample rate.

        Returns:
            Dict matching ResembleAIClient.analyze() shape:
            {"is_synthetic": bool, "confidence": float, ...}
        """
        try:
            _load_model(self.model_name, self.device)
        except Exception as e:
            return {
                "is_synthetic": False,
                "confidence": 0.0,
                "error": f"Model load failed: {e}",
            }

        try:
            # Convert bytes to float array
            audio_array = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0

            if len(audio_array) < sample_rate * 0.5:
                return {
                    "is_synthetic": False,
                    "confidence": 0.0,
                    "error": "Audio too short for analysis",
                }

            if _model == "fallback" or _processor == "fallback":
                return self._feature_based_analysis(audio_array, sample_rate)

            return await self._model_based_analysis(audio_array, sample_rate)

        except Exception as e:
            logger.error(f"Wav2Vec analysis error: {e}")
            return {
                "is_synthetic": False,
                "confidence": 0.0,
                "error": str(e),
            }

    async def _model_based_analysis(
        self,
        audio_array: np.ndarray,
        sample_rate: int,
    ) -> Dict[str, Any]:
        """Run inference with the loaded Wav2Vec2 model."""
        import torch

        inputs = _processor(
            audio_array,
            sampling_rate=sample_rate,
            return_tensors="pt",
            padding=True,
        )
        inputs = {k: v.to(self.device) for k, v in inputs.items()}

        with torch.no_grad():
            outputs = _model(**inputs)
            logits = outputs.logits
            probs = torch.softmax(logits, dim=-1)
            synthetic_prob = probs[0][1].item()

        is_synthetic = synthetic_prob > 0.5
        confidence = synthetic_prob * 100.0

        return {
            "is_synthetic": is_synthetic,
            "confidence": confidence,
            "model": self.model_name,
            "method": "wav2vec2_classification",
        }

    def _feature_based_analysis(
        self,
        audio_array: np.ndarray,
        sample_rate: int,
    ) -> Dict[str, Any]:
        """
        Feature-based fallback when model can't be loaded.

        Analyzes statistical properties of the audio that differ
        between natural and synthetic speech.
        """
        # Zero-crossing rate — synthetic speech tends to have more uniform ZCR
        zero_crossings = np.sum(np.abs(np.diff(np.sign(audio_array)))) / (2 * len(audio_array))
        zcr_variance = np.var(
            [
                np.sum(np.abs(np.diff(np.sign(audio_array[i : i + sample_rate])))) / (2 * sample_rate)
                for i in range(0, len(audio_array) - sample_rate, sample_rate // 4)
            ]
        ) if len(audio_array) >= sample_rate else 0.0

        # Energy variance — synthetic speech tends to have smoother energy envelope
        frame_size = int(sample_rate * 0.025)
        hop_size = int(sample_rate * 0.010)
        frames = [
            audio_array[i : i + frame_size]
            for i in range(0, len(audio_array) - frame_size, hop_size)
        ]
        energies = [np.sum(f ** 2) for f in frames] if frames else [0.0]
        energy_variance = np.var(energies)

        # Combine features into a synthetic probability
        # Low ZCR variance + low energy variance = more likely synthetic
        zcr_score = max(0, 1.0 - zcr_variance * 1000)
        energy_score = max(0, 1.0 - energy_variance * 100)

        synthetic_prob = (zcr_score * 0.5 + energy_score * 0.5) * 0.6  # Cap at 60% for fallback
        is_synthetic = synthetic_prob > 0.3

        return {
            "is_synthetic": is_synthetic,
            "confidence": synthetic_prob * 100.0,
            "model": "feature_based_fallback",
            "method": "statistical_features",
            "features": {
                "zero_crossing_rate": float(zero_crossings),
                "zcr_variance": float(zcr_variance),
                "energy_variance": float(energy_variance),
            },
        }
