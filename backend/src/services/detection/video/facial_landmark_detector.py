"""
Facial Landmark Detector

Analyzes facial landmarks for deepfake indicators.
"""

import math
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class LandmarkAnalysisResult:
    """Result from facial landmark analysis."""

    is_suspicious: bool
    confidence: float  # 0-100
    inconsistency_score: float
    landmark_jitter: float
    face_boundary_artifacts: bool
    details: Dict[str, Any]


@dataclass
class FacialLandmarks:
    """68-point facial landmarks."""

    points: List[Tuple[float, float]]  # 68 (x, y) coordinates
    frame_number: int = 0
    timestamp: float = 0.0

    @property
    def jaw(self) -> List[Tuple[float, float]]:
        """Jawline landmarks (points 0-16)."""
        return self.points[0:17] if len(self.points) >= 17 else []

    @property
    def right_eyebrow(self) -> List[Tuple[float, float]]:
        """Right eyebrow landmarks (points 17-21)."""
        return self.points[17:22] if len(self.points) >= 22 else []

    @property
    def left_eyebrow(self) -> List[Tuple[float, float]]:
        """Left eyebrow landmarks (points 22-26)."""
        return self.points[22:27] if len(self.points) >= 27 else []

    @property
    def nose(self) -> List[Tuple[float, float]]:
        """Nose landmarks (points 27-35)."""
        return self.points[27:36] if len(self.points) >= 36 else []

    @property
    def right_eye(self) -> List[Tuple[float, float]]:
        """Right eye landmarks (points 36-41)."""
        return self.points[36:42] if len(self.points) >= 42 else []

    @property
    def left_eye(self) -> List[Tuple[float, float]]:
        """Left eye landmarks (points 42-47)."""
        return self.points[42:48] if len(self.points) >= 48 else []

    @property
    def outer_mouth(self) -> List[Tuple[float, float]]:
        """Outer mouth landmarks (points 48-59)."""
        return self.points[48:60] if len(self.points) >= 60 else []

    @property
    def inner_mouth(self) -> List[Tuple[float, float]]:
        """Inner mouth landmarks (points 60-67)."""
        return self.points[60:68] if len(self.points) >= 68 else []


class FacialLandmarkDetector:
    """
    Analyzes facial landmarks across video frames for deepfake indicators.

    Detection methods:
    1. Temporal jitter - Unnatural movement between frames
    2. Landmark consistency - Relationship between facial features
    3. Face boundary artifacts - Edge anomalies at face swap boundaries
    4. Symmetry analysis - Unnatural facial symmetry

    Deepfakes often show:
    - Jitter at face boundaries (swap artifacts)
    - Inconsistent landmark relationships
    - Too-perfect or too-asymmetric facial features
    """

    # Thresholds
    JITTER_THRESHOLD = 2.0  # Pixels
    CONSISTENCY_THRESHOLD = 0.8
    SYMMETRY_VARIANCE_MIN = 0.02
    SYMMETRY_VARIANCE_MAX = 0.15

    def __init__(
        self,
        temporal_window: int = 5,
    ):
        self.temporal_window = temporal_window

    def analyze(
        self,
        landmarks_sequence: List[FacialLandmarks],
    ) -> LandmarkAnalysisResult:
        """
        Analyze sequence of facial landmarks for deepfake indicators.

        Args:
            landmarks_sequence: List of facial landmarks across frames.

        Returns:
            LandmarkAnalysisResult with detection findings.
        """
        if len(landmarks_sequence) < 2:
            return LandmarkAnalysisResult(
                is_suspicious=False,
                confidence=0.0,
                inconsistency_score=0.0,
                landmark_jitter=0.0,
                face_boundary_artifacts=False,
                details={"error": "Insufficient frames for analysis"},
            )

        # Analyze temporal jitter
        jitter = self._analyze_temporal_jitter(landmarks_sequence)

        # Analyze landmark consistency
        consistency_issues = self._analyze_consistency(landmarks_sequence)

        # Check face boundary artifacts
        boundary_artifacts = self._detect_boundary_artifacts(landmarks_sequence)

        # Analyze symmetry
        symmetry_score = self._analyze_symmetry(landmarks_sequence)

        # Calculate overall score
        score = self._calculate_score(jitter, consistency_issues, boundary_artifacts, symmetry_score)

        is_suspicious = score > 50.0

        return LandmarkAnalysisResult(
            is_suspicious=is_suspicious,
            confidence=score,
            inconsistency_score=consistency_issues,
            landmark_jitter=jitter,
            face_boundary_artifacts=boundary_artifacts > 0.5,
            details={
                "frames_analyzed": len(landmarks_sequence),
                "jitter": jitter,
                "consistency_issues": consistency_issues,
                "boundary_artifacts": boundary_artifacts,
                "symmetry_score": symmetry_score,
            },
        )

    def _analyze_temporal_jitter(
        self,
        landmarks_sequence: List[FacialLandmarks],
    ) -> float:
        """
        Analyze landmark jitter across frames.

        Returns average jitter in pixels.
        """
        if len(landmarks_sequence) < 2:
            return 0.0

        jitters = []

        for i in range(1, len(landmarks_sequence)):
            prev = landmarks_sequence[i - 1]
            curr = landmarks_sequence[i]

            if len(prev.points) != len(curr.points):
                continue

            # Calculate per-point displacement
            frame_jitter = []
            for j in range(len(prev.points)):
                px, py = prev.points[j]
                cx, cy = curr.points[j]
                displacement = math.sqrt((cx - px) ** 2 + (cy - py) ** 2)
                frame_jitter.append(displacement)

            if frame_jitter:
                # Use standard deviation of displacements
                mean = sum(frame_jitter) / len(frame_jitter)
                variance = sum((d - mean) ** 2 for d in frame_jitter) / len(frame_jitter)
                jitters.append(math.sqrt(variance))

        return sum(jitters) / len(jitters) if jitters else 0.0

    def _analyze_consistency(
        self,
        landmarks_sequence: List[FacialLandmarks],
    ) -> float:
        """
        Analyze consistency of landmark relationships.

        Returns inconsistency score (0-100).
        """
        if not landmarks_sequence:
            return 0.0

        issues = []

        for landmarks in landmarks_sequence:
            if len(landmarks.points) < 68:
                continue

            # Check eye-to-eye distance consistency
            if landmarks.right_eye and landmarks.left_eye:
                r_eye_center = self._centroid(landmarks.right_eye)
                l_eye_center = self._centroid(landmarks.left_eye)
                eye_distance = self._distance(r_eye_center, l_eye_center)

                # Check nose-to-eye ratio
                if landmarks.nose:
                    nose_tip = landmarks.nose[-1] if landmarks.nose else (0, 0)
                    nose_eye_dist = self._distance(nose_tip, r_eye_center)

                    ratio = nose_eye_dist / eye_distance if eye_distance > 0 else 0
                    # Normal ratio is around 0.8-1.2
                    if ratio < 0.5 or ratio > 1.5:
                        issues.append(1.0)
                    else:
                        issues.append(0.0)

            # Check mouth-to-nose ratio
            if landmarks.outer_mouth and landmarks.nose:
                mouth_center = self._centroid(landmarks.outer_mouth)
                nose_tip = landmarks.nose[-1]
                mouth_nose_dist = self._distance(mouth_center, nose_tip)

                # Check against face height
                if landmarks.jaw:
                    face_height = self._distance(landmarks.jaw[0], landmarks.jaw[-1])
                    ratio = mouth_nose_dist / face_height if face_height > 0 else 0

                    if ratio < 0.05 or ratio > 0.25:
                        issues.append(1.0)
                    else:
                        issues.append(0.0)

        if not issues:
            return 0.0

        return (sum(issues) / len(issues)) * 100

    def _detect_boundary_artifacts(
        self,
        landmarks_sequence: List[FacialLandmarks],
    ) -> float:
        """
        Detect artifacts at face boundaries.

        Returns artifact score (0-1).
        """
        if not landmarks_sequence:
            return 0.0

        artifact_scores = []

        for i in range(1, len(landmarks_sequence)):
            prev = landmarks_sequence[i - 1]
            curr = landmarks_sequence[i]

            if not prev.jaw or not curr.jaw:
                continue

            # Check jaw boundary movement
            jaw_movements = []
            for j in range(min(len(prev.jaw), len(curr.jaw))):
                movement = self._distance(prev.jaw[j], curr.jaw[j])
                jaw_movements.append(movement)

            if jaw_movements:
                # High variance in jaw movement indicates potential artifacts
                mean = sum(jaw_movements) / len(jaw_movements)
                variance = sum((m - mean) ** 2 for m in jaw_movements) / len(jaw_movements)

                # Normalize variance
                normalized = min(variance / 100, 1.0)
                artifact_scores.append(normalized)

        return sum(artifact_scores) / len(artifact_scores) if artifact_scores else 0.0

    def _analyze_symmetry(
        self,
        landmarks_sequence: List[FacialLandmarks],
    ) -> float:
        """
        Analyze facial symmetry.

        Returns symmetry abnormality score (0-100).
        """
        if not landmarks_sequence:
            return 0.0

        symmetry_scores = []

        for landmarks in landmarks_sequence:
            if not landmarks.right_eye or not landmarks.left_eye:
                continue

            # Compare eye symmetry
            r_eye_center = self._centroid(landmarks.right_eye)
            l_eye_center = self._centroid(landmarks.left_eye)

            # Check eyebrow symmetry
            if landmarks.right_eyebrow and landmarks.left_eyebrow:
                r_brow = self._centroid(landmarks.right_eyebrow)
                l_brow = self._centroid(landmarks.left_eyebrow)

                # Calculate asymmetry
                r_brow_eye = self._distance(r_brow, r_eye_center)
                l_brow_eye = self._distance(l_brow, l_eye_center)

                if max(r_brow_eye, l_brow_eye) > 0:
                    asymmetry = abs(r_brow_eye - l_brow_eye) / max(r_brow_eye, l_brow_eye)
                else:
                    asymmetry = 0

                # Too perfect (< 0.02) or too asymmetric (> 0.15) is suspicious
                if asymmetry < self.SYMMETRY_VARIANCE_MIN:
                    symmetry_scores.append(70)  # Too symmetric
                elif asymmetry > self.SYMMETRY_VARIANCE_MAX:
                    symmetry_scores.append(60)  # Too asymmetric
                else:
                    symmetry_scores.append(20)  # Normal

        return sum(symmetry_scores) / len(symmetry_scores) if symmetry_scores else 0.0

    def _calculate_score(
        self,
        jitter: float,
        consistency: float,
        boundary: float,
        symmetry: float,
    ) -> float:
        """
        Calculate overall detection score.

        Weights:
        - Jitter: 30%
        - Consistency: 25%
        - Boundary: 25%
        - Symmetry: 20%
        """
        # Convert jitter to score (higher jitter = higher score)
        jitter_score = min(jitter / self.JITTER_THRESHOLD * 50, 100)

        # Boundary artifact score
        boundary_score = boundary * 100

        # Weighted combination
        score = (
            jitter_score * 0.30 +
            consistency * 0.25 +
            boundary_score * 0.25 +
            symmetry * 0.20
        )

        return min(max(score, 0.0), 100.0)

    @staticmethod
    def _centroid(points: List[Tuple[float, float]]) -> Tuple[float, float]:
        """Calculate centroid of points."""
        if not points:
            return (0.0, 0.0)
        x = sum(p[0] for p in points) / len(points)
        y = sum(p[1] for p in points) / len(points)
        return (x, y)

    @staticmethod
    def _distance(p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
        """Calculate Euclidean distance between points."""
        return math.sqrt((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2)
