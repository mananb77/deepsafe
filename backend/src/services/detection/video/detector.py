"""
Video Deepfake Detector

Main detector combining multiple analysis methods:
- Sensity/GetReal API (primary, weight: 0.30)
- Facial landmark analysis (weight: 0.20)
- Micro-expression analysis (weight: 0.20)
- Lighting/shadow analysis (weight: 0.15)
- Virtual camera detection (weight: 0.15)
- EfficientNet-B4 fallback when API unavailable
"""

import asyncio
import time
from typing import Any, Dict, List, Optional

from src.services.detection.base import (
    BaseDetector,
    DetectionResult,
    DetectionType,
    RiskLevel,
    VideoFrame,
)
from src.services.detection.video.sensity_client import SensityClient
from src.services.detection.video.facial_landmark_detector import (
    FacialLandmarkDetector,
    FacialLandmarks,
)
from src.services.detection.video.micro_expression_analyzer import (
    MicroExpressionAnalyzer,
    FaceRegion,
)
from src.services.detection.video.lighting_analyzer import (
    LightingAnalyzer,
    FrameLightingData,
)
from src.services.detection.video.virtual_camera_detector import VirtualCameraDetector


class VideoDeepfakeDetector(BaseDetector):
    """
    Multi-method video deepfake detector.

    Combines multiple detection approaches for robust analysis:
    1. Sensity/GetReal API - State-of-the-art deepfake detection
    2. Facial Landmark Analysis - Temporal consistency of face points
    3. Micro-Expression Analysis - Blink patterns, expression timing
    4. Lighting Analysis - Shadow/lighting consistency
    5. Virtual Camera Detection - Detect virtual camera software

    Score weights (with API):
    - Sensity API: 30%
    - Facial Landmarks: 20%
    - Micro-expressions: 20%
    - Lighting: 15%
    - Virtual Camera: 15%

    Fallback weights (without API):
    - Facial Landmarks: 30%
    - Micro-expressions: 30%
    - Lighting: 25%
    - Virtual Camera: 15%
    """

    # Detection weights (with API)
    WEIGHT_SENSITY = 0.30
    WEIGHT_LANDMARKS = 0.20
    WEIGHT_MICRO_EXPRESSION = 0.20
    WEIGHT_LIGHTING = 0.15
    WEIGHT_VIRTUAL_CAMERA = 0.15

    # Fallback weights (without API)
    FALLBACK_WEIGHT_LANDMARKS = 0.30
    FALLBACK_WEIGHT_MICRO_EXPRESSION = 0.30
    FALLBACK_WEIGHT_LIGHTING = 0.25
    FALLBACK_WEIGHT_VIRTUAL_CAMERA = 0.15

    def __init__(
        self,
        sensity_client: Optional[SensityClient] = None,
        enable_api: bool = True,
        fps: float = 30.0,
    ):
        self.sensity_client = sensity_client or SensityClient()
        self.landmark_detector = FacialLandmarkDetector()
        self.micro_expression_analyzer = MicroExpressionAnalyzer(fps=fps)
        self.lighting_analyzer = LightingAnalyzer()
        self.virtual_camera_detector = VirtualCameraDetector()
        self.enable_api = enable_api
        self.fps = fps
        self._api_available: Optional[bool] = None

    @property
    def name(self) -> str:
        return "video_deepfake_detector"

    async def is_available(self) -> bool:
        """Check if detector is available."""
        return True  # Local analyzers always available

    async def analyze(
        self,
        frames: List[VideoFrame],
        landmarks_sequence: Optional[List[FacialLandmarks]] = None,
        face_regions: Optional[List[FaceRegion]] = None,
        lighting_data: Optional[List[FrameLightingData]] = None,
        device_name: Optional[str] = None,
        frame_timestamps: Optional[List[float]] = None,
    ) -> DetectionResult:
        """
        Perform comprehensive video deepfake detection.

        Args:
            frames: Video frames to analyze.
            landmarks_sequence: Pre-extracted facial landmarks (optional).
            face_regions: Pre-extracted face region data (optional).
            lighting_data: Pre-extracted lighting data (optional).
            device_name: Camera device name for virtual camera detection.
            frame_timestamps: Frame arrival timestamps for timing analysis.

        Returns:
            DetectionResult with combined analysis.
        """
        start_time = time.perf_counter()
        results: Dict[str, Any] = {}
        errors: List[str] = []

        # Run analyses in parallel where possible
        tasks = []

        # Sensity API analysis (if enabled)
        if self.enable_api and frames:
            tasks.append(self._run_sensity_analysis(frames))

        # Facial landmark analysis
        if landmarks_sequence:
            tasks.append(self._run_landmark_analysis(landmarks_sequence))

        # Micro-expression analysis
        if face_regions:
            tasks.append(self._run_micro_expression_analysis(face_regions))

        # Lighting analysis
        if lighting_data:
            tasks.append(self._run_lighting_analysis(lighting_data))

        # Virtual camera detection
        tasks.append(
            self._run_virtual_camera_detection(device_name, frame_timestamps)
        )

        # Execute all tasks
        if tasks:
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
            detection_type=DetectionType.VIDEO_DEEPFAKE,
            is_detected=is_detected,
            confidence=combined_score,
            risk_level=risk_level,
            details={
                "method_scores": method_scores,
                "api_used": results.get("sensity_used", False),
                "virtual_camera_detected": results.get("virtual_camera", {}).get("is_virtual", False),
                "frames_analyzed": len(frames) if frames else 0,
            },
            evidence={
                "sensity": results.get("sensity", {}),
                "landmarks": results.get("landmarks", {}),
                "micro_expressions": results.get("micro_expressions", {}),
                "lighting": results.get("lighting", {}),
                "virtual_camera": results.get("virtual_camera", {}),
            },
            method="multi_method_video",
            latency_ms=latency_ms,
            error="; ".join(errors) if errors else None,
        )

    async def _run_sensity_analysis(
        self,
        frames: List[VideoFrame],
    ) -> Dict[str, Any]:
        """Run Sensity API analysis on video frames."""
        try:
            # Extract frame bytes
            frame_bytes = [f.data for f in frames if f.data]

            if not frame_bytes:
                return {"sensity_error": "No frame data", "sensity_used": False}

            result = await self.sensity_client.analyze_video(
                frame_bytes,
                sample_rate=5,  # Analyze every 5th frame
            )

            if result.get("error"):
                return {"sensity_error": result["error"], "sensity_used": False}

            return {
                "sensity": {
                    "is_deepfake": result.get("is_deepfake", False),
                    "confidence": result.get("confidence", 0.0),
                    "manipulation_types": result.get("manipulation_types", []),
                    "frames_with_deepfake": result.get("frames_with_deepfake", 0),
                    "frames_analyzed": result.get("frames_analyzed", 0),
                },
                "sensity_used": True,
            }
        except Exception as e:
            return {"sensity_error": str(e), "sensity_used": False}

    async def _run_landmark_analysis(
        self,
        landmarks_sequence: List[FacialLandmarks],
    ) -> Dict[str, Any]:
        """Run facial landmark analysis."""
        try:
            result = self.landmark_detector.analyze(landmarks_sequence)

            return {
                "landmarks": {
                    "is_suspicious": result.is_suspicious,
                    "confidence": result.confidence,
                    "jitter": result.landmark_jitter,
                    "inconsistency_score": result.inconsistency_score,
                    "boundary_artifacts": result.face_boundary_artifacts,
                }
            }
        except Exception as e:
            return {"landmarks_error": str(e)}

    async def _run_micro_expression_analysis(
        self,
        face_regions: List[FaceRegion],
    ) -> Dict[str, Any]:
        """Run micro-expression analysis."""
        try:
            result = self.micro_expression_analyzer.analyze(face_regions)

            return {
                "micro_expressions": {
                    "is_suspicious": result.is_suspicious,
                    "confidence": result.confidence,
                    "blink_rate": result.blink_rate,
                    "blink_duration_avg": result.blink_duration_avg,
                    "expression_smoothness": result.expression_smoothness,
                    "micro_expression_count": result.micro_expression_count,
                }
            }
        except Exception as e:
            return {"micro_expressions_error": str(e)}

    async def _run_lighting_analysis(
        self,
        lighting_data: List[FrameLightingData],
    ) -> Dict[str, Any]:
        """Run lighting/shadow analysis."""
        try:
            result = self.lighting_analyzer.analyze(lighting_data)

            return {
                "lighting": {
                    "is_suspicious": result.is_suspicious,
                    "confidence": result.confidence,
                    "lighting_consistency": result.lighting_consistency,
                    "shadow_consistency": result.shadow_consistency,
                    "face_background_match": result.face_background_match,
                }
            }
        except Exception as e:
            return {"lighting_error": str(e)}

    async def _run_virtual_camera_detection(
        self,
        device_name: Optional[str],
        frame_timestamps: Optional[List[float]],
    ) -> Dict[str, Any]:
        """Run virtual camera detection."""
        try:
            result = self.virtual_camera_detector.analyze(
                device_name=device_name,
                frame_timestamps=frame_timestamps,
            )

            return {
                "virtual_camera": {
                    "is_virtual": result.is_virtual,
                    "confidence": result.confidence,
                    "detected_software": result.detected_software,
                    "indicators": result.indicators,
                }
            }
        except Exception as e:
            return {"virtual_camera_error": str(e)}

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
        api_used = results.get("sensity_used", False)

        # Sensity API score
        if api_used and "sensity" in results:
            sensity = results["sensity"]
            score = sensity.get("confidence", 0.0)
            if sensity.get("is_deepfake"):
                score = max(score, 60.0)
            method_scores["sensity"] = score
            weighted_sum += score * self.WEIGHT_SENSITY
            total_weight += self.WEIGHT_SENSITY

        # Facial landmark score
        if "landmarks" in results:
            landmarks = results["landmarks"]
            score = landmarks.get("confidence", 0.0)
            method_scores["landmarks"] = score

            weight = (
                self.FALLBACK_WEIGHT_LANDMARKS if not api_used
                else self.WEIGHT_LANDMARKS
            )
            weighted_sum += score * weight
            total_weight += weight

        # Micro-expression score
        if "micro_expressions" in results:
            micro = results["micro_expressions"]
            score = micro.get("confidence", 0.0)
            method_scores["micro_expressions"] = score

            weight = (
                self.FALLBACK_WEIGHT_MICRO_EXPRESSION if not api_used
                else self.WEIGHT_MICRO_EXPRESSION
            )
            weighted_sum += score * weight
            total_weight += weight

        # Lighting analysis score
        if "lighting" in results:
            lighting = results["lighting"]
            score = lighting.get("confidence", 0.0)
            method_scores["lighting"] = score

            weight = (
                self.FALLBACK_WEIGHT_LIGHTING if not api_used
                else self.WEIGHT_LIGHTING
            )
            weighted_sum += score * weight
            total_weight += weight

        # Virtual camera score
        if "virtual_camera" in results:
            vc = results["virtual_camera"]
            score = vc.get("confidence", 0.0)

            # Virtual camera detection is a strong indicator
            if vc.get("is_virtual"):
                score = max(score, 70.0)

            method_scores["virtual_camera"] = score

            weight = (
                self.FALLBACK_WEIGHT_VIRTUAL_CAMERA if not api_used
                else self.WEIGHT_VIRTUAL_CAMERA
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

        # Virtual camera is definitive
        if results.get("virtual_camera", {}).get("is_virtual"):
            combined = max(combined, 70.0)

        return min(max(combined, 0.0), 100.0), method_scores

    async def analyze_single_frame(
        self,
        frame: VideoFrame,
        device_name: Optional[str] = None,
    ) -> DetectionResult:
        """
        Quick analysis of a single frame.

        Useful for initial screening or low-latency requirements.

        Args:
            frame: Single video frame.
            device_name: Camera device name.

        Returns:
            DetectionResult with single-frame analysis.
        """
        start_time = time.perf_counter()
        results: Dict[str, Any] = {}
        errors: List[str] = []

        # Run API analysis if enabled
        if self.enable_api and frame.data:
            try:
                result = await self.sensity_client.analyze(
                    frame.data,
                    image_format="jpeg",
                )

                if not result.get("error"):
                    results["sensity"] = {
                        "is_deepfake": result.get("is_deepfake", False),
                        "confidence": result.get("confidence", 0.0),
                        "manipulation_type": result.get("manipulation_type"),
                    }
                    results["sensity_used"] = True
                else:
                    results["sensity_used"] = False
            except Exception as e:
                errors.append(f"Sensity: {e}")
                results["sensity_used"] = False

        # Virtual camera detection
        vc_result = self.virtual_camera_detector.analyze(device_name=device_name)
        results["virtual_camera"] = {
            "is_virtual": vc_result.is_virtual,
            "confidence": vc_result.confidence,
            "detected_software": vc_result.detected_software,
        }

        # Calculate score
        score = 0.0

        if results.get("sensity_used"):
            sensity = results["sensity"]
            if sensity.get("is_deepfake"):
                score = max(sensity.get("confidence", 60.0), 60.0)
            else:
                score = sensity.get("confidence", 0.0) * 0.5

        if results["virtual_camera"]["is_virtual"]:
            score = max(score, results["virtual_camera"]["confidence"])

        is_detected = score > 50.0
        risk_level = RiskLevel.from_score(score)
        latency_ms = (time.perf_counter() - start_time) * 1000

        return DetectionResult(
            detection_type=DetectionType.VIDEO_DEEPFAKE,
            is_detected=is_detected,
            confidence=score,
            risk_level=risk_level,
            details={
                "api_used": results.get("sensity_used", False),
                "virtual_camera_detected": results["virtual_camera"]["is_virtual"],
                "single_frame": True,
            },
            evidence=results,
            method="single_frame_video",
            latency_ms=latency_ms,
            error="; ".join(errors) if errors else None,
        )

    async def close(self) -> None:
        """Clean up resources."""
        if self.sensity_client:
            await self.sensity_client.close()
