"""
Lighting and Shadow Analyzer

Detects inconsistent lighting and shadow patterns that indicate deepfake manipulation.
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple
import math


@dataclass
class LightingAnalysisResult:
    """Result from lighting analysis."""

    is_suspicious: bool
    confidence: float  # 0-100
    lighting_consistency: float  # 0-1, lower = more suspicious
    shadow_consistency: float  # 0-1, lower = more suspicious
    face_background_match: float  # 0-1, lower = more suspicious
    color_temperature_variance: float
    details: Dict[str, Any]


@dataclass
class FrameLightingData:
    """Lighting data for a single frame."""

    frame_number: int
    timestamp: float

    # Face region lighting
    face_brightness: float  # 0-255
    face_contrast: float  # Standard deviation
    face_color_temp: float  # Estimated color temperature (K)

    # Background lighting
    background_brightness: float
    background_contrast: float
    background_color_temp: float

    # Shadow analysis
    shadow_direction: Tuple[float, float]  # Normalized vector
    shadow_intensity: float  # 0-1

    # Highlight analysis
    highlight_positions: List[Tuple[float, float]]  # Normalized positions
    specular_intensity: float


class LightingAnalyzer:
    """
    Analyzes lighting consistency across video frames for deepfake indicators.

    Detection methods:
    1. Face-background lighting mismatch
    2. Shadow direction inconsistency
    3. Color temperature variance
    4. Specular highlight analysis
    5. Temporal lighting consistency

    Deepfakes often show:
    - Mismatched lighting between face and background
    - Inconsistent shadow directions
    - Unnatural color temperature on face
    - Missing or incorrect specular highlights
    """

    # Thresholds
    BRIGHTNESS_MISMATCH_THRESHOLD = 50.0  # Out of 255
    COLOR_TEMP_VARIANCE_THRESHOLD = 500.0  # Kelvin
    SHADOW_DIRECTION_VARIANCE_THRESHOLD = 0.3  # Radians

    def __init__(self):
        pass

    def analyze(
        self,
        lighting_data: List[FrameLightingData],
    ) -> LightingAnalysisResult:
        """
        Analyze lighting consistency across video frames.

        Args:
            lighting_data: List of lighting data across frames.

        Returns:
            LightingAnalysisResult with detection findings.
        """
        if len(lighting_data) < 2:
            return LightingAnalysisResult(
                is_suspicious=False,
                confidence=0.0,
                lighting_consistency=1.0,
                shadow_consistency=1.0,
                face_background_match=1.0,
                color_temperature_variance=0.0,
                details={"error": "Insufficient frames for analysis"},
            )

        # Analyze face-background lighting match
        face_bg_match = self._analyze_face_background_match(lighting_data)

        # Analyze shadow consistency
        shadow_consistency = self._analyze_shadow_consistency(lighting_data)

        # Analyze color temperature
        color_temp_analysis = self._analyze_color_temperature(lighting_data)

        # Analyze temporal lighting consistency
        temporal_consistency = self._analyze_temporal_consistency(lighting_data)

        # Analyze specular highlights
        specular_analysis = self._analyze_specular_highlights(lighting_data)

        # Calculate overall score
        score = self._calculate_score(
            face_bg_match,
            shadow_consistency,
            color_temp_analysis,
            temporal_consistency,
            specular_analysis,
        )

        is_suspicious = score > 50.0

        return LightingAnalysisResult(
            is_suspicious=is_suspicious,
            confidence=score,
            lighting_consistency=temporal_consistency,
            shadow_consistency=shadow_consistency,
            face_background_match=face_bg_match,
            color_temperature_variance=color_temp_analysis["variance"],
            details={
                "frames_analyzed": len(lighting_data),
                "avg_face_brightness": color_temp_analysis["avg_face_brightness"],
                "avg_bg_brightness": color_temp_analysis["avg_bg_brightness"],
                "shadow_direction_variance": color_temp_analysis.get("shadow_variance", 0),
                "specular_score": specular_analysis,
            },
        )

    def _analyze_face_background_match(
        self,
        lighting_data: List[FrameLightingData],
    ) -> float:
        """
        Analyze if face lighting matches background.

        Returns match score 0-1 (lower = more suspicious).
        """
        mismatches = []

        for frame in lighting_data:
            # Brightness mismatch
            brightness_diff = abs(frame.face_brightness - frame.background_brightness)
            brightness_mismatch = min(brightness_diff / self.BRIGHTNESS_MISMATCH_THRESHOLD, 1.0)

            # Color temperature mismatch
            temp_diff = abs(frame.face_color_temp - frame.background_color_temp)
            temp_mismatch = min(temp_diff / self.COLOR_TEMP_VARIANCE_THRESHOLD, 1.0)

            # Contrast mismatch (less important)
            contrast_diff = abs(frame.face_contrast - frame.background_contrast)
            contrast_mismatch = min(contrast_diff / 50.0, 1.0)

            # Combined mismatch
            total_mismatch = (
                brightness_mismatch * 0.4 +
                temp_mismatch * 0.4 +
                contrast_mismatch * 0.2
            )

            mismatches.append(total_mismatch)

        if not mismatches:
            return 1.0

        avg_mismatch = sum(mismatches) / len(mismatches)
        return 1.0 - avg_mismatch

    def _analyze_shadow_consistency(
        self,
        lighting_data: List[FrameLightingData],
    ) -> float:
        """
        Analyze if shadow directions are consistent across frames.

        Returns consistency score 0-1 (lower = more suspicious).
        """
        if len(lighting_data) < 2:
            return 1.0

        shadow_directions = [
            frame.shadow_direction for frame in lighting_data
            if frame.shadow_direction != (0.0, 0.0)
        ]

        if len(shadow_directions) < 2:
            return 1.0

        # Calculate angles
        angles = []
        for direction in shadow_directions:
            angle = math.atan2(direction[1], direction[0])
            angles.append(angle)

        # Calculate variance in angles
        mean_angle = sum(angles) / len(angles)
        variance = sum((a - mean_angle) ** 2 for a in angles) / len(angles)
        std_dev = math.sqrt(variance)

        # High variance means inconsistent shadows
        if std_dev > self.SHADOW_DIRECTION_VARIANCE_THRESHOLD:
            # Very inconsistent
            consistency = max(0.0, 1.0 - (std_dev / math.pi))
        else:
            # Consistent
            consistency = 1.0 - (std_dev / self.SHADOW_DIRECTION_VARIANCE_THRESHOLD) * 0.3

        return consistency

    def _analyze_color_temperature(
        self,
        lighting_data: List[FrameLightingData],
    ) -> Dict[str, Any]:
        """
        Analyze color temperature consistency.

        Returns analysis dict with variance and averages.
        """
        face_temps = [frame.face_color_temp for frame in lighting_data]
        bg_temps = [frame.background_color_temp for frame in lighting_data]
        face_brightness = [frame.face_brightness for frame in lighting_data]
        bg_brightness = [frame.background_brightness for frame in lighting_data]

        # Face temperature variance
        if face_temps:
            mean_face_temp = sum(face_temps) / len(face_temps)
            variance = sum((t - mean_face_temp) ** 2 for t in face_temps) / len(face_temps)
        else:
            mean_face_temp = 0
            variance = 0

        # Face-background temperature difference
        temp_diffs = [
            abs(face_temps[i] - bg_temps[i])
            for i in range(len(lighting_data))
        ]
        avg_temp_diff = sum(temp_diffs) / len(temp_diffs) if temp_diffs else 0

        return {
            "variance": math.sqrt(variance),
            "avg_face_temp": mean_face_temp,
            "avg_bg_temp": sum(bg_temps) / len(bg_temps) if bg_temps else 0,
            "avg_temp_diff": avg_temp_diff,
            "avg_face_brightness": sum(face_brightness) / len(face_brightness) if face_brightness else 0,
            "avg_bg_brightness": sum(bg_brightness) / len(bg_brightness) if bg_brightness else 0,
        }

    def _analyze_temporal_consistency(
        self,
        lighting_data: List[FrameLightingData],
    ) -> float:
        """
        Analyze lighting consistency over time.

        Returns consistency score 0-1 (lower = more suspicious).
        """
        if len(lighting_data) < 2:
            return 1.0

        # Calculate frame-to-frame brightness changes
        brightness_changes = []
        for i in range(1, len(lighting_data)):
            prev = lighting_data[i - 1]
            curr = lighting_data[i]

            face_change = abs(curr.face_brightness - prev.face_brightness)
            bg_change = abs(curr.background_brightness - prev.background_brightness)

            # Face changing without background change is suspicious
            if bg_change < 5 and face_change > 20:
                brightness_changes.append(1.0)  # Suspicious
            elif face_change > 50:
                brightness_changes.append(0.7)  # Somewhat suspicious
            else:
                brightness_changes.append(0.0)  # Normal

        if not brightness_changes:
            return 1.0

        # Higher average = more suspicious
        avg_suspicious = sum(brightness_changes) / len(brightness_changes)
        return 1.0 - avg_suspicious

    def _analyze_specular_highlights(
        self,
        lighting_data: List[FrameLightingData],
    ) -> float:
        """
        Analyze specular highlight patterns.

        Missing or inconsistent highlights can indicate deepfakes.

        Returns analysis score 0-1 (lower = more suspicious).
        """
        if not lighting_data:
            return 1.0

        # Check for presence of specular highlights
        frames_with_highlights = sum(
            1 for frame in lighting_data
            if len(frame.highlight_positions) > 0
        )

        presence_ratio = frames_with_highlights / len(lighting_data)

        # Check highlight position consistency
        if frames_with_highlights < 2:
            position_consistency = 0.5  # Can't determine
        else:
            # Compare highlight positions across frames
            all_positions = [
                frame.highlight_positions[0]
                for frame in lighting_data
                if frame.highlight_positions
            ]

            if len(all_positions) < 2:
                position_consistency = 0.5
            else:
                # Calculate variance in positions
                mean_x = sum(p[0] for p in all_positions) / len(all_positions)
                mean_y = sum(p[1] for p in all_positions) / len(all_positions)

                variance = sum(
                    (p[0] - mean_x) ** 2 + (p[1] - mean_y) ** 2
                    for p in all_positions
                ) / len(all_positions)

                # Some movement is natural; too much is suspicious
                if variance < 0.01:
                    position_consistency = 0.9  # Too stable (slightly suspicious)
                elif variance > 0.1:
                    position_consistency = 0.5  # Too variable
                else:
                    position_consistency = 1.0  # Natural

        # Combine scores
        # Low presence = suspicious (real faces usually have specular highlights)
        if presence_ratio < 0.3:
            return 0.3
        elif presence_ratio < 0.6:
            return 0.5 * position_consistency
        else:
            return 0.7 + 0.3 * position_consistency

    def _calculate_score(
        self,
        face_bg_match: float,
        shadow_consistency: float,
        color_temp_analysis: Dict[str, Any],
        temporal_consistency: float,
        specular_analysis: float,
    ) -> float:
        """
        Calculate overall suspicion score.

        Weights:
        - Face-background match: 30%
        - Shadow consistency: 25%
        - Color temperature: 20%
        - Temporal consistency: 15%
        - Specular highlights: 10%

        Returns score 0-100.
        """
        # Convert consistency scores to suspicion scores (lower consistency = higher suspicion)
        face_bg_score = (1.0 - face_bg_match) * 100
        shadow_score = (1.0 - shadow_consistency) * 100

        # Color temperature score based on variance
        temp_variance = color_temp_analysis["variance"]
        if temp_variance > self.COLOR_TEMP_VARIANCE_THRESHOLD:
            color_score = 80.0
        else:
            color_score = (temp_variance / self.COLOR_TEMP_VARIANCE_THRESHOLD) * 60

        # Also consider face-bg temperature difference
        temp_diff = color_temp_analysis["avg_temp_diff"]
        if temp_diff > 800:
            color_score = max(color_score, 70.0)

        temporal_score = (1.0 - temporal_consistency) * 100
        specular_score = (1.0 - specular_analysis) * 100

        # Weighted combination
        score = (
            face_bg_score * 0.30 +
            shadow_score * 0.25 +
            color_score * 0.20 +
            temporal_score * 0.15 +
            specular_score * 0.10
        )

        return min(max(score, 0.0), 100.0)
