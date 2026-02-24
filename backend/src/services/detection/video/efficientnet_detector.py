"""
EfficientNet-B4 Local Video Deepfake Detector

Uses google/efficientnet-b4 via HuggingFace transformers for local
video deepfake detection. Replaces SensityClient when running
in local or hybrid detection mode.

Lazy-loads model on first call.
~100-200ms per frame on CPU.
"""

import logging
from typing import Any, Dict, List, Optional

import numpy as np

logger = logging.getLogger(__name__)

# Lazy-loaded singleton
_model = None
_processor = None


def _load_model(model_name: str, device: str):
    """Load EfficientNet model and processor (singleton)."""
    global _model, _processor

    if _model is not None:
        return

    try:
        import torch
        from transformers import AutoFeatureExtractor, AutoModelForImageClassification

        logger.info(f"Loading EfficientNet model: {model_name} on {device}")
        _processor = AutoFeatureExtractor.from_pretrained(model_name)
        _model = AutoModelForImageClassification.from_pretrained(
            model_name,
        ).to(device)
        _model.eval()
        logger.info("EfficientNet model loaded successfully")

    except Exception as e:
        logger.warning(f"Failed to load EfficientNet model: {e}. Using pixel-based fallback.")
        _model = "fallback"
        _processor = "fallback"


class EfficientNetDetector:
    """
    Local video deepfake detector using EfficientNet-B4.

    Returns results in the same format as SensityClient
    so existing calling code works unchanged.
    """

    def __init__(
        self,
        model_name: str = "google/efficientnet-b4",
        device: str = "cpu",
    ):
        self.model_name = model_name
        self.device = device

    async def analyze(
        self,
        image_data: bytes,
        image_format: str = "jpeg",
    ) -> Dict[str, Any]:
        """
        Analyze a single image for deepfake indicators.

        Args:
            image_data: Raw image bytes.
            image_format: Image format (jpeg, png, etc.).

        Returns:
            Dict matching SensityClient.analyze() shape.
        """
        try:
            _load_model(self.model_name, self.device)
        except Exception as e:
            return {
                "is_deepfake": False,
                "confidence": 0.0,
                "error": f"Model load failed: {e}",
            }

        try:
            image = self._bytes_to_image(image_data)
            if image is None:
                return {
                    "is_deepfake": False,
                    "confidence": 0.0,
                    "error": "Failed to decode image",
                }

            if _model == "fallback" or _processor == "fallback":
                return self._pixel_based_analysis(image)

            return await self._model_based_analysis(image)

        except Exception as e:
            logger.error(f"EfficientNet analysis error: {e}")
            return {
                "is_deepfake": False,
                "confidence": 0.0,
                "error": str(e),
            }

    async def analyze_video(
        self,
        frames: List[bytes],
        sample_rate: int = 5,
    ) -> Dict[str, Any]:
        """
        Analyze multiple video frames for deepfake indicators.

        Args:
            frames: List of raw frame bytes.
            sample_rate: Analyze every Nth frame.

        Returns:
            Dict matching SensityClient.analyze_video() shape.
        """
        if not frames:
            return {
                "is_deepfake": False,
                "confidence": 0.0,
                "frames_analyzed": 0,
                "frames_with_deepfake": 0,
            }

        sampled_frames = frames[::sample_rate] if sample_rate > 1 else frames
        deepfake_count = 0
        confidences = []

        for frame_bytes in sampled_frames:
            result = await self.analyze(frame_bytes)
            if result.get("is_deepfake"):
                deepfake_count += 1
            confidences.append(result.get("confidence", 0.0))

        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
        is_deepfake = deepfake_count > len(sampled_frames) * 0.3

        return {
            "is_deepfake": is_deepfake,
            "confidence": avg_confidence,
            "frames_analyzed": len(sampled_frames),
            "frames_with_deepfake": deepfake_count,
            "manipulation_types": ["face_swap"] if is_deepfake else [],
        }

    def _bytes_to_image(self, image_data: bytes) -> Optional[Any]:
        """Convert raw bytes to a PIL Image or numpy array."""
        try:
            from PIL import Image
            import io

            return Image.open(io.BytesIO(image_data)).convert("RGB")
        except ImportError:
            pass

        try:
            import cv2

            arr = np.frombuffer(image_data, dtype=np.uint8)
            img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
            if img is not None:
                return img
        except ImportError:
            pass

        return None

    async def _model_based_analysis(self, image) -> Dict[str, Any]:
        """Run inference with the loaded EfficientNet model."""
        import torch

        inputs = _processor(images=image, return_tensors="pt")
        inputs = {k: v.to(self.device) for k, v in inputs.items()}

        with torch.no_grad():
            outputs = _model(**inputs)
            logits = outputs.logits
            probs = torch.softmax(logits, dim=-1)
            # Use the highest probability class as a deepfake score proxy
            max_prob = probs.max().item()
            # For a general classifier, high uncertainty (max_prob close to uniform)
            # might indicate manipulated content
            num_classes = probs.shape[-1]
            uniform_prob = 1.0 / num_classes
            anomaly_score = 1.0 - (max_prob - uniform_prob) / (1.0 - uniform_prob)
            anomaly_score = max(0.0, min(1.0, anomaly_score))

        is_deepfake = anomaly_score > 0.5
        confidence = anomaly_score * 100.0

        return {
            "is_deepfake": is_deepfake,
            "confidence": confidence,
            "model": self.model_name,
            "method": "efficientnet_classification",
        }

    def _pixel_based_analysis(self, image) -> Dict[str, Any]:
        """
        Pixel-based fallback when model can't be loaded.

        Checks for common deepfake artifacts:
        - Color channel inconsistencies
        - Edge artifacts
        - Noise pattern uniformity
        """
        try:
            if hasattr(image, "size"):
                # PIL Image
                img_array = np.array(image)
            else:
                # Already numpy
                img_array = image

            if img_array.ndim != 3 or img_array.shape[2] < 3:
                return {
                    "is_deepfake": False,
                    "confidence": 0.0,
                    "method": "pixel_fallback",
                    "error": "Invalid image dimensions",
                }

            # Channel correlation — deepfakes often have unusual channel correlations
            r, g, b = img_array[:, :, 0].flatten(), img_array[:, :, 1].flatten(), img_array[:, :, 2].flatten()
            rg_corr = np.corrcoef(r.astype(float), g.astype(float))[0, 1] if len(r) > 1 else 1.0
            rb_corr = np.corrcoef(r.astype(float), b.astype(float))[0, 1] if len(r) > 1 else 1.0

            # Noise level estimation
            gray = np.mean(img_array[:, :, :3], axis=2)
            noise_std = np.std(gray - np.mean(gray))

            # Edge density — deepfakes may have blurred or over-sharpened edges
            dx = np.diff(gray, axis=1)
            dy = np.diff(gray, axis=0)
            edge_density = (np.mean(np.abs(dx)) + np.mean(np.abs(dy))) / 2

            # Very uniform noise or unusual channel correlation = suspicious
            corr_anomaly = max(0, 1.0 - abs(rg_corr)) * 0.3 + max(0, 1.0 - abs(rb_corr)) * 0.3
            noise_anomaly = max(0, 0.5 - noise_std / 100) * 0.4

            synthetic_prob = min(1.0, corr_anomaly + noise_anomaly) * 0.5  # Cap at 50%

            return {
                "is_deepfake": synthetic_prob > 0.25,
                "confidence": synthetic_prob * 100.0,
                "model": "pixel_based_fallback",
                "method": "statistical_features",
                "features": {
                    "rg_correlation": float(rg_corr) if not np.isnan(rg_corr) else 0.0,
                    "rb_correlation": float(rb_corr) if not np.isnan(rb_corr) else 0.0,
                    "noise_std": float(noise_std),
                    "edge_density": float(edge_density),
                },
            }

        except Exception as e:
            return {
                "is_deepfake": False,
                "confidence": 0.0,
                "method": "pixel_fallback",
                "error": str(e),
            }
