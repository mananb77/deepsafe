"""
Audio Deepfake Detector

Main detector combining multiple analysis methods:
- Resemble AI API (primary, weight: 0.35)
- Spectral analysis (weight: 0.25)
- Prosody analysis (weight: 0.20)
- Audio-video sync (weight: 0.20)
- Wav2Vec fallback when API unavailable
"""

import asyncio
import time
from typing import Any, Dict, List, Optional

from src.services.detection.base import (
    AudioChunk,
    BaseDetector,
    DetectionResult,
    DetectionType,
    RiskLevel,
    VideoFrame,
)
from src.services.detection.audio.resemble_client import ResembleAIClient
from src.services.detection.audio.spectral_analyzer import SpectralAnalyzer
from src.services.detection.audio.prosody_analyzer import ProsodyAnalyzer
from src.services.detection.audio.av_sync_detector import AVSyncDetector


class AudioDeepfakeDetector(BaseDetector):
    """
    Multi-method audio deepfake detector.

    Combines multiple detection approaches for robust analysis:
    1. Resemble AI API - State-of-the-art synthetic voice detection
    2. Spectral Analysis - Frequency-domain artifact detection
    3. Prosody Analysis - Speech rhythm and intonation analysis
    4. A/V Sync Detection - Lip sync verification (42ms threshold)

    Score weights:
    - Resemble AI: 35%
    - Spectral: 25%
    - Prosody: 20%
    - A/V Sync: 20%

    Falls back to local analysis if API is unavailable.
    """

    # Detection weights
    WEIGHT_RESEMBLE = 0.35
    WEIGHT_SPECTRAL = 0.25
    WEIGHT_PROSODY = 0.20
    WEIGHT_AV_SYNC = 0.20

    # Fallback weights (when Resemble unavailable)
    FALLBACK_WEIGHT_SPECTRAL = 0.40
    FALLBACK_WEIGHT_PROSODY = 0.35
    FALLBACK_WEIGHT_AV_SYNC = 0.25

    def __init__(
        self,
        resemble_client: Optional[ResembleAIClient] = None,
        enable_api: bool = True,
    ):
        self.resemble_client = resemble_client or ResembleAIClient()
        self.spectral_analyzer = SpectralAnalyzer()
        self.prosody_analyzer = ProsodyAnalyzer()
        self.av_sync_detector = AVSyncDetector()
        self.enable_api = enable_api
        self._api_available: Optional[bool] = None

    @property
    def name(self) -> str:
        return "audio_deepfake_detector"

    async def is_available(self) -> bool:
        """Check if detector is available."""
        return True  # Local analyzers always available

    async def analyze(
        self,
        audio: AudioChunk,
        video_frames: Optional[List[VideoFrame]] = None,
        lip_positions: Optional[List[Dict[str, float]]] = None,
    ) -> DetectionResult:
        """
        Perform comprehensive audio deepfake detection.

        Args:
            audio: Audio chunk to analyze.
            video_frames: Optional video frames for A/V sync analysis.
            lip_positions: Optional lip position data for sync analysis.

        Returns:
            DetectionResult with combined analysis.
        """
        start_time = time.perf_counter()
        results: Dict[str, Any] = {}
        errors: List[str] = []

        # Run analyses in parallel where possible
        tasks = [
            self._run_spectral_analysis(audio),
            self._run_prosody_analysis(audio),
        ]

        # Add Resemble AI if enabled and potentially available
        if self.enable_api:
            tasks.append(self._run_resemble_analysis(audio))

        # Add A/V sync if video data available
        if video_frames or lip_positions:
            tasks.append(self._run_av_sync_analysis(audio, video_frames, lip_positions))

        # Execute all tasks
        task_results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results
        for result in task_results:
            if isinstance(result, Exception):
                errors.append(str(result))
            elif isinstance(result, dict):
                results.update(result)

        # Calculate combined score
        combined_score, method_scores = self._calculate_combined_score(results)

        # Determine if detected
        is_detected = combined_score > 50.0
        risk_level = RiskLevel.from_score(combined_score)

        latency_ms = (time.perf_counter() - start_time) * 1000

        return DetectionResult(
            detection_type=DetectionType.AUDIO_DEEPFAKE,
            is_detected=is_detected,
            confidence=combined_score,
            risk_level=risk_level,
            details={
                "method_scores": method_scores,
                "api_used": results.get("resemble_used", False),
                "av_sync_analyzed": "av_sync" in results,
            },
            evidence={
                "resemble": results.get("resemble", {}),
                "spectral": results.get("spectral", {}),
                "prosody": results.get("prosody", {}),
                "av_sync": results.get("av_sync", {}),
            },
            method="multi_method_audio",
            latency_ms=latency_ms,
            error="; ".join(errors) if errors else None,
        )

    async def _run_resemble_analysis(self, audio: AudioChunk) -> Dict[str, Any]:
        """Run Resemble AI analysis."""
        try:
            result = await self.resemble_client.analyze(
                audio.data,
                sample_rate=audio.sample_rate,
            )

            if result.get("error"):
                return {"resemble_error": result["error"], "resemble_used": False}

            return {
                "resemble": {
                    "is_synthetic": result.get("is_synthetic", False),
                    "confidence": result.get("confidence", 0.0),
                    "model_detected": result.get("model_detected"),
                },
                "resemble_used": True,
            }
        except Exception as e:
            return {"resemble_error": str(e), "resemble_used": False}

    async def _run_spectral_analysis(self, audio: AudioChunk) -> Dict[str, Any]:
        """Run spectral analysis."""
        try:
            result = self.spectral_analyzer.analyze(
                audio.data,
                sample_rate=audio.sample_rate,
            )
            return {
                "spectral": {
                    "is_synthetic": result.is_synthetic,
                    "confidence": result.confidence,
                    "synthetic_markers": result.synthetic_markers_detected,
                    "artifact_frequencies": result.artifact_frequencies,
                    "spectral_flatness": result.spectral_flatness,
                }
            }
        except Exception as e:
            return {"spectral_error": str(e)}

    async def _run_prosody_analysis(self, audio: AudioChunk) -> Dict[str, Any]:
        """Run prosody analysis."""
        try:
            result = self.prosody_analyzer.analyze(
                audio.data,
                sample_rate=audio.sample_rate,
            )
            return {
                "prosody": {
                    "is_synthetic": result.is_synthetic,
                    "confidence": result.confidence,
                    "pitch_variance": result.pitch_variance,
                    "energy_variance": result.energy_variance,
                    "speaking_rate": result.speaking_rate,
                    "pause_score": result.pause_pattern_score,
                }
            }
        except Exception as e:
            return {"prosody_error": str(e)}

    async def _run_av_sync_analysis(
        self,
        audio: AudioChunk,
        video_frames: Optional[List[VideoFrame]],
        lip_positions: Optional[List[Dict[str, float]]],
    ) -> Dict[str, Any]:
        """Run audio-video sync analysis."""
        try:
            frame_data = [f.data for f in video_frames] if video_frames else []
            result = self.av_sync_detector.analyze(
                audio.data,
                frame_data,
                lip_positions,
            )
            return {
                "av_sync": {
                    "is_synced": result.is_synced,
                    "offset_ms": result.sync_offset_ms,
                    "confidence": result.confidence,
                    "lip_sync_score": result.lip_sync_score,
                }
            }
        except Exception as e:
            return {"av_sync_error": str(e)}

    def _calculate_combined_score(
        self,
        results: Dict[str, Any],
    ) -> tuple[float, Dict[str, float]]:
        """
        Calculate combined detection score from all methods.

        Returns (combined_score, method_scores).
        """
        method_scores: Dict[str, float] = {}
        weighted_sum = 0.0
        total_weight = 0.0

        # Check if API was used successfully
        api_used = results.get("resemble_used", False)

        # Resemble AI score
        if api_used and "resemble" in results:
            resemble = results["resemble"]
            score = resemble.get("confidence", 0.0)
            if resemble.get("is_synthetic"):
                score = max(score, 60.0)  # Ensure high score if synthetic detected
            method_scores["resemble"] = score
            weighted_sum += score * self.WEIGHT_RESEMBLE
            total_weight += self.WEIGHT_RESEMBLE

        # Spectral analysis score
        if "spectral" in results:
            spectral = results["spectral"]
            score = spectral.get("confidence", 0.0)
            method_scores["spectral"] = score

            weight = (
                self.FALLBACK_WEIGHT_SPECTRAL if not api_used
                else self.WEIGHT_SPECTRAL
            )
            weighted_sum += score * weight
            total_weight += weight

        # Prosody analysis score
        if "prosody" in results:
            prosody = results["prosody"]
            score = prosody.get("confidence", 0.0)
            method_scores["prosody"] = score

            weight = (
                self.FALLBACK_WEIGHT_PROSODY if not api_used
                else self.WEIGHT_PROSODY
            )
            weighted_sum += score * weight
            total_weight += weight

        # A/V sync score
        if "av_sync" in results:
            av_sync = results["av_sync"]
            # Convert sync result to detection score
            # Low sync = high detection score
            if not av_sync.get("is_synced", True):
                score = 100 - av_sync.get("lip_sync_score", 0.5) * 100
            else:
                score = (1 - av_sync.get("lip_sync_score", 0.5)) * 50
            method_scores["av_sync"] = score

            weight = (
                self.FALLBACK_WEIGHT_AV_SYNC if not api_used
                else self.WEIGHT_AV_SYNC
            )
            weighted_sum += score * weight
            total_weight += weight

        # Calculate combined score
        if total_weight > 0:
            combined = weighted_sum / total_weight
        else:
            combined = 0.0

        # Apply detection boost if multiple methods agree
        high_confidence_count = sum(
            1 for s in method_scores.values() if s > 60
        )
        if high_confidence_count >= 2:
            combined = min(100, combined * 1.15)

        return min(max(combined, 0.0), 100.0), method_scores

    async def close(self) -> None:
        """Clean up resources."""
        if self.resemble_client:
            await self.resemble_client.close()
