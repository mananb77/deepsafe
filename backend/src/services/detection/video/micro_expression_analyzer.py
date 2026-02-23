"""
Micro-Expression Analyzer

Detects unnatural facial micro-expressions that indicate deepfake manipulation.
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class MicroExpressionResult:
    """Result from micro-expression analysis."""

    is_suspicious: bool
    confidence: float  # 0-100
    blink_rate: float  # Blinks per minute
    blink_duration_avg: float  # Average blink duration in ms
    expression_smoothness: float  # 0-1, lower = more suspicious
    micro_expression_count: int
    details: Dict[str, Any]


@dataclass
class FaceRegion:
    """Face region data for a single frame."""

    frame_number: int
    timestamp: float
    eye_aspect_ratio_left: float  # EAR for left eye
    eye_aspect_ratio_right: float  # EAR for right eye
    mouth_aspect_ratio: float
    eyebrow_position_left: float
    eyebrow_position_right: float


class MicroExpressionAnalyzer:
    """
    Analyzes micro-expressions across video frames for deepfake indicators.

    Detection methods:
    1. Blink rate analysis - Deepfakes often have abnormal blink patterns
    2. Blink duration analysis - Synthetic blinks are often too fast/slow
    3. Expression smoothness - Unnatural transitions between expressions
    4. Micro-expression frequency - Real faces show brief involuntary expressions

    Normal human blink patterns:
    - Rate: 15-20 blinks per minute
    - Duration: 100-400ms
    - Deepfakes often show 0 blinks or very regular patterns
    """

    # Normal blink parameters
    NORMAL_BLINK_RATE_MIN = 10.0  # Blinks per minute
    NORMAL_BLINK_RATE_MAX = 25.0
    NORMAL_BLINK_DURATION_MIN = 100.0  # Milliseconds
    NORMAL_BLINK_DURATION_MAX = 400.0

    # Eye aspect ratio threshold for blink detection
    EAR_BLINK_THRESHOLD = 0.2

    # Minimum frames to consider a blink
    MIN_BLINK_FRAMES = 2

    def __init__(
        self,
        fps: float = 30.0,
    ):
        self.fps = fps
        self.frame_duration_ms = 1000.0 / fps

    def analyze(
        self,
        face_regions: List[FaceRegion],
        duration_seconds: Optional[float] = None,
    ) -> MicroExpressionResult:
        """
        Analyze micro-expressions across video frames.

        Args:
            face_regions: List of face region data across frames.
            duration_seconds: Video duration (calculated from frames if not provided).

        Returns:
            MicroExpressionResult with detection findings.
        """
        if len(face_regions) < 10:
            return MicroExpressionResult(
                is_suspicious=False,
                confidence=0.0,
                blink_rate=0.0,
                blink_duration_avg=0.0,
                expression_smoothness=1.0,
                micro_expression_count=0,
                details={"error": "Insufficient frames for analysis"},
            )

        # Calculate duration
        if duration_seconds is None:
            duration_seconds = len(face_regions) / self.fps

        # Analyze blinks
        blink_analysis = self._analyze_blinks(face_regions, duration_seconds)

        # Analyze expression smoothness
        smoothness = self._analyze_expression_smoothness(face_regions)

        # Count micro-expressions
        micro_expression_count = self._detect_micro_expressions(face_regions)

        # Calculate suspicion score
        score = self._calculate_score(
            blink_analysis, smoothness, micro_expression_count, duration_seconds
        )

        is_suspicious = score > 50.0

        return MicroExpressionResult(
            is_suspicious=is_suspicious,
            confidence=score,
            blink_rate=blink_analysis["rate"],
            blink_duration_avg=blink_analysis["avg_duration"],
            expression_smoothness=smoothness,
            micro_expression_count=micro_expression_count,
            details={
                "frames_analyzed": len(face_regions),
                "duration_seconds": duration_seconds,
                "blink_count": blink_analysis["count"],
                "blink_regularity": blink_analysis["regularity"],
                "smoothness_variance": blink_analysis.get("smoothness_variance", 0),
            },
        )

    def _analyze_blinks(
        self,
        face_regions: List[FaceRegion],
        duration_seconds: float,
    ) -> Dict[str, Any]:
        """
        Analyze blink patterns.

        Returns blink statistics.
        """
        # Detect blinks using eye aspect ratio
        blinks: List[Dict[str, Any]] = []
        in_blink = False
        blink_start = 0

        for i, region in enumerate(face_regions):
            # Average EAR of both eyes
            ear = (region.eye_aspect_ratio_left + region.eye_aspect_ratio_right) / 2

            if ear < self.EAR_BLINK_THRESHOLD:
                if not in_blink:
                    in_blink = True
                    blink_start = i
            else:
                if in_blink:
                    blink_end = i
                    blink_frames = blink_end - blink_start

                    if blink_frames >= self.MIN_BLINK_FRAMES:
                        blink_duration = blink_frames * self.frame_duration_ms
                        blinks.append({
                            "start_frame": blink_start,
                            "end_frame": blink_end,
                            "duration_ms": blink_duration,
                        })

                    in_blink = False

        # Calculate statistics
        blink_count = len(blinks)
        blink_rate = (blink_count / duration_seconds) * 60 if duration_seconds > 0 else 0

        # Average blink duration
        if blinks:
            avg_duration = sum(b["duration_ms"] for b in blinks) / len(blinks)
        else:
            avg_duration = 0.0

        # Calculate blink regularity (variance in inter-blink intervals)
        regularity = 0.0
        if len(blinks) >= 2:
            intervals = [
                blinks[i + 1]["start_frame"] - blinks[i]["end_frame"]
                for i in range(len(blinks) - 1)
            ]
            if intervals:
                mean_interval = sum(intervals) / len(intervals)
                if mean_interval > 0:
                    variance = sum((i - mean_interval) ** 2 for i in intervals) / len(intervals)
                    std_dev = variance ** 0.5
                    # Coefficient of variation
                    regularity = std_dev / mean_interval

        return {
            "count": blink_count,
            "rate": blink_rate,
            "avg_duration": avg_duration,
            "regularity": regularity,
            "blinks": blinks,
        }

    def _analyze_expression_smoothness(
        self,
        face_regions: List[FaceRegion],
    ) -> float:
        """
        Analyze smoothness of expression transitions.

        Returns smoothness score (0-1, lower = more suspicious).
        """
        if len(face_regions) < 2:
            return 1.0

        # Calculate frame-to-frame changes
        changes = []

        for i in range(1, len(face_regions)):
            prev = face_regions[i - 1]
            curr = face_regions[i]

            # Calculate change in mouth aspect ratio
            mouth_change = abs(curr.mouth_aspect_ratio - prev.mouth_aspect_ratio)

            # Calculate change in eyebrow positions
            brow_change = (
                abs(curr.eyebrow_position_left - prev.eyebrow_position_left) +
                abs(curr.eyebrow_position_right - prev.eyebrow_position_right)
            ) / 2

            # Calculate change in eye aspect ratios
            eye_change = (
                abs(curr.eye_aspect_ratio_left - prev.eye_aspect_ratio_left) +
                abs(curr.eye_aspect_ratio_right - prev.eye_aspect_ratio_right)
            ) / 2

            total_change = mouth_change + brow_change + eye_change
            changes.append(total_change)

        if not changes:
            return 1.0

        # Calculate variance of changes
        mean_change = sum(changes) / len(changes)
        variance = sum((c - mean_change) ** 2 for c in changes) / len(changes)

        # High variance in changes indicates jerky/unsmooth transitions
        # Normalize to 0-1 range (lower variance = higher smoothness)
        smoothness = 1.0 / (1.0 + variance * 10)

        return smoothness

    def _detect_micro_expressions(
        self,
        face_regions: List[FaceRegion],
    ) -> int:
        """
        Detect micro-expressions (brief involuntary facial movements).

        Micro-expressions last 1/25 to 1/5 of a second (40-200ms).
        Real faces show these; many deepfakes don't.

        Returns count of detected micro-expressions.
        """
        micro_expressions = 0
        min_frames = max(1, int(0.04 * self.fps))  # 40ms
        max_frames = int(0.2 * self.fps)  # 200ms

        i = 0
        while i < len(face_regions) - max_frames:
            # Look for rapid expression change and return
            baseline = face_regions[i]

            for j in range(i + 1, min(i + max_frames, len(face_regions))):
                curr = face_regions[j]

                # Calculate expression change from baseline
                change = (
                    abs(curr.mouth_aspect_ratio - baseline.mouth_aspect_ratio) +
                    abs(curr.eyebrow_position_left - baseline.eyebrow_position_left) +
                    abs(curr.eyebrow_position_right - baseline.eyebrow_position_right)
                )

                # Significant change detected
                if change > 0.1:
                    # Check if it returns to baseline within the window
                    for k in range(j + 1, min(i + max_frames, len(face_regions))):
                        return_region = face_regions[k]
                        return_change = (
                            abs(return_region.mouth_aspect_ratio - baseline.mouth_aspect_ratio) +
                            abs(return_region.eyebrow_position_left - baseline.eyebrow_position_left) +
                            abs(return_region.eyebrow_position_right - baseline.eyebrow_position_right)
                        )

                        if return_change < 0.05:
                            # Found a micro-expression
                            micro_expressions += 1
                            i = k
                            break
                    break
            i += 1

        return micro_expressions

    def _calculate_score(
        self,
        blink_analysis: Dict[str, Any],
        smoothness: float,
        micro_expression_count: int,
        duration_seconds: float,
    ) -> float:
        """
        Calculate overall suspicion score.

        Returns score 0-100.
        """
        score = 0.0

        # Blink rate analysis (35%)
        blink_rate = blink_analysis["rate"]
        if blink_rate < 1.0:
            # Almost no blinking - very suspicious
            score += 35.0
        elif blink_rate < self.NORMAL_BLINK_RATE_MIN:
            # Below normal
            score += 25.0
        elif blink_rate > self.NORMAL_BLINK_RATE_MAX:
            # Above normal
            score += 15.0
        else:
            # Normal range
            score += 5.0

        # Blink duration analysis (20%)
        avg_duration = blink_analysis["avg_duration"]
        if avg_duration > 0:
            if avg_duration < self.NORMAL_BLINK_DURATION_MIN:
                score += 15.0  # Too fast
            elif avg_duration > self.NORMAL_BLINK_DURATION_MAX:
                score += 15.0  # Too slow
            else:
                score += 3.0
        else:
            score += 20.0  # No blinks detected

        # Blink regularity (15%)
        # Very regular blinking (low variance) is suspicious
        regularity = blink_analysis["regularity"]
        if regularity < 0.1 and blink_analysis["count"] > 3:
            score += 15.0  # Too regular
        elif regularity < 0.3:
            score += 10.0
        else:
            score += 3.0

        # Expression smoothness (15%)
        # Low smoothness (jerky) is suspicious
        if smoothness < 0.3:
            score += 15.0
        elif smoothness < 0.5:
            score += 10.0
        else:
            score += 3.0

        # Micro-expression analysis (15%)
        # Real faces show micro-expressions; deepfakes often don't
        expected_micro = duration_seconds / 10  # Rough expectation
        if micro_expression_count == 0 and duration_seconds > 5:
            score += 15.0  # No micro-expressions in long video
        elif micro_expression_count < expected_micro * 0.3:
            score += 10.0
        else:
            score += 2.0

        return min(max(score, 0.0), 100.0)
