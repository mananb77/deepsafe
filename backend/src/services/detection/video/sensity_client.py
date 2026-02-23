"""
Sensity/GetReal AI Client

Client wrapper for video deepfake detection API.
"""

import asyncio
import base64
from typing import Any, Dict, List, Optional

import httpx

from src.shared.config import get_settings
from src.services.detection.base import BaseAPIClient


class SensityClient(BaseAPIClient):
    """
    Client for Sensity (or similar) video deepfake detection API.

    Provides detection of:
    - Face swaps
    - Lip sync manipulations
    - Full face generation
    - GAN-generated faces
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: float = 60.0,  # Video analysis takes longer
    ):
        settings = get_settings()
        self.api_key = api_key or settings.sensity_api_key
        self.base_url = base_url or "https://api.sensity.ai/v1"
        self.timeout = timeout
        self._client: Optional[httpx.AsyncClient] = None

    @property
    def name(self) -> str:
        return "sensity_ai"

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                timeout=self.timeout,
            )
        return self._client

    async def close(self) -> None:
        """Close HTTP client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._client = None

    async def health_check(self) -> bool:
        """Check if Sensity API is available."""
        if not self.api_key:
            return False

        try:
            client = await self._get_client()
            response = await client.get("/status")
            return response.status_code == 200
        except Exception:
            return False

    async def analyze(
        self,
        image_data: bytes,
        image_format: str = "jpeg",
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Analyze single image/frame for deepfake detection.

        Args:
            image_data: Image bytes (JPEG, PNG, etc.).
            image_format: Image format (jpeg, png).
            **kwargs: Additional parameters.

        Returns:
            Analysis results from Sensity.
        """
        if not self.api_key:
            return {
                "error": "API key not configured",
                "is_deepfake": None,
                "confidence": 0.0,
            }

        try:
            client = await self._get_client()

            # Encode image as base64
            image_b64 = base64.b64encode(image_data).decode("utf-8")

            payload = {
                "image": image_b64,
                "format": image_format,
                "detect_types": kwargs.get("detect_types", [
                    "face_swap",
                    "lip_sync",
                    "full_face",
                    "gan_generated",
                ]),
            }

            response = await client.post("/detect/deepfake", json=payload)

            if response.status_code == 200:
                result = response.json()
                return {
                    "is_deepfake": result.get("is_deepfake", False),
                    "confidence": result.get("confidence", 0.0) * 100,
                    "manipulation_type": result.get("manipulation_type"),
                    "model_detected": result.get("model_detected"),
                    "face_regions": result.get("face_regions", []),
                    "raw_response": result,
                }
            else:
                return {
                    "error": f"API error: {response.status_code}",
                    "is_deepfake": None,
                    "confidence": 0.0,
                }

        except httpx.TimeoutException:
            return {
                "error": "API timeout",
                "is_deepfake": None,
                "confidence": 0.0,
            }
        except Exception as e:
            return {
                "error": str(e),
                "is_deepfake": None,
                "confidence": 0.0,
            }

    async def analyze_video(
        self,
        frames: List[bytes],
        sample_rate: int = 5,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Analyze multiple video frames.

        Args:
            frames: List of frame image bytes.
            sample_rate: Analyze every Nth frame.
            **kwargs: Additional parameters.

        Returns:
            Aggregated analysis results.
        """
        if not self.api_key:
            return {
                "error": "API key not configured",
                "is_deepfake": None,
                "confidence": 0.0,
            }

        # Sample frames
        sampled_frames = frames[::sample_rate]

        if not sampled_frames:
            return {
                "error": "No frames to analyze",
                "is_deepfake": None,
                "confidence": 0.0,
            }

        # Analyze frames in parallel (with concurrency limit)
        semaphore = asyncio.Semaphore(3)

        async def analyze_with_limit(frame: bytes) -> Dict[str, Any]:
            async with semaphore:
                return await self.analyze(frame, **kwargs)

        results = await asyncio.gather(
            *[analyze_with_limit(frame) for frame in sampled_frames],
            return_exceptions=True,
        )

        # Aggregate results
        valid_results = [r for r in results if isinstance(r, dict) and "error" not in r]

        if not valid_results:
            return {
                "error": "All frame analyses failed",
                "is_deepfake": None,
                "confidence": 0.0,
            }

        # Calculate aggregate scores
        deepfake_detections = sum(1 for r in valid_results if r.get("is_deepfake"))
        avg_confidence = sum(r.get("confidence", 0) for r in valid_results) / len(valid_results)

        # If majority of frames detected as deepfake, classify as deepfake
        is_deepfake = deepfake_detections > len(valid_results) / 2

        # Collect manipulation types
        manipulation_types = list(set(
            r.get("manipulation_type")
            for r in valid_results
            if r.get("manipulation_type")
        ))

        return {
            "is_deepfake": is_deepfake,
            "confidence": avg_confidence,
            "manipulation_types": manipulation_types,
            "frames_analyzed": len(valid_results),
            "frames_with_deepfake": deepfake_detections,
            "frame_results": valid_results,
        }
