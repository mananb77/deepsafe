"""
Risk Score Aggregator

Combines deepfake detection and social engineering scores into a composite risk score.

Risk Categories:
- 0-30%: Low - Normal monitoring
- 31-60%: Medium - Monitor closely
- 61-85%: High - Trigger verification
- 86-100%: Critical - Automatic intervention

Actions by risk level:
- Low: Passive monitoring, log activity
- Medium: Enhanced monitoring, alert user
- High: Trigger verification, flag for review
- Critical: Automatic intervention, multi-channel verification
"""

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

from src.services.detection.base import DetectionResult, DetectionType, RiskLevel


class ActionType(Enum):
    """Types of actions to take based on risk level."""

    NONE = "none"
    MONITOR = "monitor"
    ALERT = "alert"
    VERIFY = "verify"
    INTERVENE = "intervene"


@dataclass
class RiskAction:
    """An action to take based on risk assessment."""

    action_type: ActionType
    priority: int  # 1-10, higher = more urgent
    description: str
    target: Optional[str] = None  # e.g., participant ID
    parameters: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AggregatedRiskResult:
    """Result from risk aggregation."""

    composite_risk_score: float  # 0-100
    risk_level: RiskLevel
    deepfake_score: float
    social_engineering_score: float
    audio_deepfake_score: float
    video_deepfake_score: float
    virtual_camera_detected: bool
    recommended_actions: List[RiskAction]
    risk_factors: List[str]
    confidence: float
    details: Dict[str, Any]


class RiskAggregator:
    """
    Aggregates multiple detection results into a composite risk score.

    Combines:
    - Audio deepfake detection
    - Video deepfake detection
    - Social engineering detection

    Scoring weights:
    - Deepfake confidence: 40%
    - Social engineering score: 40%
    - Virtual camera detection: 20%

    The composite score determines the overall risk level and
    recommended actions for meeting security.
    """

    # Component weights
    WEIGHT_DEEPFAKE = 0.40
    WEIGHT_SOCIAL_ENGINEERING = 0.40
    WEIGHT_VIRTUAL_CAMERA = 0.20

    # Within deepfake, audio/video weights
    WEIGHT_AUDIO = 0.50
    WEIGHT_VIDEO = 0.50

    # Risk thresholds
    THRESHOLD_LOW = 30.0
    THRESHOLD_MEDIUM = 60.0
    THRESHOLD_HIGH = 85.0

    # Action thresholds
    ACTION_ALERT_THRESHOLD = 40.0
    ACTION_VERIFY_THRESHOLD = 65.0
    ACTION_INTERVENE_THRESHOLD = 85.0

    def __init__(
        self,
        deepfake_weight: float = None,
        social_engineering_weight: float = None,
        virtual_camera_weight: float = None,
    ):
        """
        Initialize aggregator with optional custom weights.

        Args:
            deepfake_weight: Weight for deepfake detection (default 0.40)
            social_engineering_weight: Weight for social engineering (default 0.40)
            virtual_camera_weight: Weight for virtual camera (default 0.20)
        """
        if deepfake_weight is not None:
            self.WEIGHT_DEEPFAKE = deepfake_weight
        if social_engineering_weight is not None:
            self.WEIGHT_SOCIAL_ENGINEERING = social_engineering_weight
        if virtual_camera_weight is not None:
            self.WEIGHT_VIRTUAL_CAMERA = virtual_camera_weight

        # Normalize weights
        total = self.WEIGHT_DEEPFAKE + self.WEIGHT_SOCIAL_ENGINEERING + self.WEIGHT_VIRTUAL_CAMERA
        self.WEIGHT_DEEPFAKE /= total
        self.WEIGHT_SOCIAL_ENGINEERING /= total
        self.WEIGHT_VIRTUAL_CAMERA /= total

    def aggregate(
        self,
        audio_result: Optional[DetectionResult] = None,
        video_result: Optional[DetectionResult] = None,
        social_engineering_result: Optional[DetectionResult] = None,
        meeting_context: Optional[Dict[str, Any]] = None,
    ) -> AggregatedRiskResult:
        """
        Aggregate detection results into composite risk score.

        Args:
            audio_result: Audio deepfake detection result.
            video_result: Video deepfake detection result.
            social_engineering_result: Social engineering detection result.
            meeting_context: Additional meeting context for risk assessment.

        Returns:
            AggregatedRiskResult with composite score and actions.
        """
        risk_factors: List[str] = []

        # Extract scores
        audio_score = 0.0
        video_score = 0.0
        social_score = 0.0
        virtual_camera_score = 0.0
        virtual_camera_detected = False

        # Process audio result
        if audio_result:
            audio_score = audio_result.confidence
            if audio_result.is_detected:
                risk_factors.append(f"Audio deepfake detected ({audio_score:.0f}% confidence)")

        # Process video result
        if video_result:
            video_score = video_result.confidence
            if video_result.is_detected:
                risk_factors.append(f"Video deepfake detected ({video_score:.0f}% confidence)")

            # Check for virtual camera
            if video_result.details.get("virtual_camera_detected"):
                virtual_camera_detected = True
                virtual_camera_score = video_result.evidence.get("virtual_camera", {}).get("confidence", 70.0)
                risk_factors.append(
                    f"Virtual camera detected: {video_result.evidence.get('virtual_camera', {}).get('detected_software', 'Unknown')}"
                )

        # Process social engineering result
        if social_engineering_result:
            social_score = social_engineering_result.confidence
            if social_engineering_result.is_detected:
                risk_category = social_engineering_result.details.get("risk_category", "unknown")
                risk_factors.append(
                    f"Social engineering risk: {risk_category} ({social_score:.0f}% confidence)"
                )

                # Add detected scenarios
                scenarios = social_engineering_result.details.get("detected_scenarios", [])
                for scenario in scenarios[:3]:
                    risk_factors.append(f"Attack pattern detected: {scenario}")

        # Calculate composite deepfake score
        deepfake_score = (audio_score * self.WEIGHT_AUDIO + video_score * self.WEIGHT_VIDEO)

        # Calculate composite risk score
        composite_score = (
            deepfake_score * self.WEIGHT_DEEPFAKE +
            social_score * self.WEIGHT_SOCIAL_ENGINEERING +
            virtual_camera_score * self.WEIGHT_VIRTUAL_CAMERA
        )

        # Apply boosting rules
        composite_score = self._apply_boosting(
            composite_score,
            audio_score,
            video_score,
            social_score,
            virtual_camera_detected,
            risk_factors,
        )

        # Determine risk level
        risk_level = self._score_to_risk_level(composite_score)

        # Generate recommended actions
        actions = self._generate_actions(
            composite_score,
            risk_level,
            audio_result,
            video_result,
            social_engineering_result,
            virtual_camera_detected,
            meeting_context,
        )

        # Calculate confidence (based on data availability)
        confidence = self._calculate_confidence(
            audio_result, video_result, social_engineering_result
        )

        return AggregatedRiskResult(
            composite_risk_score=min(max(composite_score, 0.0), 100.0),
            risk_level=risk_level,
            deepfake_score=deepfake_score,
            social_engineering_score=social_score,
            audio_deepfake_score=audio_score,
            video_deepfake_score=video_score,
            virtual_camera_detected=virtual_camera_detected,
            recommended_actions=actions,
            risk_factors=risk_factors,
            confidence=confidence,
            details={
                "weights": {
                    "deepfake": self.WEIGHT_DEEPFAKE,
                    "social_engineering": self.WEIGHT_SOCIAL_ENGINEERING,
                    "virtual_camera": self.WEIGHT_VIRTUAL_CAMERA,
                },
                "audio_details": audio_result.details if audio_result else {},
                "video_details": video_result.details if video_result else {},
                "social_engineering_details": social_engineering_result.details if social_engineering_result else {},
            },
        )

    def _apply_boosting(
        self,
        base_score: float,
        audio_score: float,
        video_score: float,
        social_score: float,
        virtual_camera: bool,
        risk_factors: List[str],
    ) -> float:
        """
        Apply boosting rules for combined indicators.

        Multiple high-confidence detections significantly increase risk.
        """
        score = base_score

        # Boost if multiple detection types agree
        high_confidence_count = sum([
            1 if audio_score > 60 else 0,
            1 if video_score > 60 else 0,
            1 if social_score > 60 else 0,
        ])

        if high_confidence_count >= 3:
            score = min(100, score * 1.3)
            risk_factors.append("Multiple high-confidence detections (significant boost)")
        elif high_confidence_count >= 2:
            score = min(100, score * 1.15)
            risk_factors.append("Multiple detection methods triggered")

        # Virtual camera with any deepfake detection is very suspicious
        if virtual_camera and (audio_score > 40 or video_score > 40):
            score = min(100, score * 1.2)
            risk_factors.append("Virtual camera combined with deepfake indicators")

        # Deepfake + social engineering is worst case
        if (audio_score > 50 or video_score > 50) and social_score > 50:
            score = min(100, score * 1.25)
            risk_factors.append("CRITICAL: Deepfake combined with social engineering attack")

        return score

    def _score_to_risk_level(self, score: float) -> RiskLevel:
        """Convert composite score to risk level."""
        if score >= self.THRESHOLD_HIGH:
            return RiskLevel.CRITICAL
        elif score >= self.THRESHOLD_MEDIUM:
            return RiskLevel.HIGH
        elif score >= self.THRESHOLD_LOW:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW

    def _generate_actions(
        self,
        score: float,
        risk_level: RiskLevel,
        audio_result: Optional[DetectionResult],
        video_result: Optional[DetectionResult],
        social_result: Optional[DetectionResult],
        virtual_camera: bool,
        context: Optional[Dict[str, Any]],
    ) -> List[RiskAction]:
        """Generate recommended actions based on risk assessment."""
        actions = []

        # Critical level actions
        if risk_level == RiskLevel.CRITICAL:
            actions.extend([
                RiskAction(
                    action_type=ActionType.INTERVENE,
                    priority=10,
                    description="Automatic intervention - halt sensitive operations",
                    parameters={"freeze_transactions": True, "notify_security": True},
                ),
                RiskAction(
                    action_type=ActionType.VERIFY,
                    priority=9,
                    description="Multi-channel verification required",
                    parameters={"channels": ["sms", "voice", "push"], "require_all": True},
                ),
                RiskAction(
                    action_type=ActionType.ALERT,
                    priority=9,
                    description="Alert security team immediately",
                    parameters={"team": "security", "priority": "critical"},
                ),
            ])

        # High level actions
        elif risk_level == RiskLevel.HIGH:
            actions.extend([
                RiskAction(
                    action_type=ActionType.VERIFY,
                    priority=8,
                    description="Identity verification required",
                    parameters={"channels": ["sms", "push"]},
                ),
                RiskAction(
                    action_type=ActionType.ALERT,
                    priority=7,
                    description="Alert meeting participants",
                    parameters={"show_warning": True},
                ),
                RiskAction(
                    action_type=ActionType.MONITOR,
                    priority=6,
                    description="Enhanced monitoring enabled",
                    parameters={"record": True, "flag_for_review": True},
                ),
            ])

        # Medium level actions
        elif risk_level == RiskLevel.MEDIUM:
            actions.extend([
                RiskAction(
                    action_type=ActionType.ALERT,
                    priority=5,
                    description="Display risk indicator to user",
                    parameters={"indicator_level": "warning"},
                ),
                RiskAction(
                    action_type=ActionType.MONITOR,
                    priority=4,
                    description="Increased monitoring frequency",
                    parameters={"sampling_rate": "high"},
                ),
            ])

        # Low level actions
        else:
            actions.append(RiskAction(
                action_type=ActionType.MONITOR,
                priority=1,
                description="Normal monitoring continues",
                parameters={"sampling_rate": "normal"},
            ))

        # Specific actions based on detection types
        if virtual_camera:
            actions.append(RiskAction(
                action_type=ActionType.ALERT,
                priority=6,
                description="Virtual camera detected - verify participant identity",
                parameters={"reason": "virtual_camera"},
            ))

        if audio_result and audio_result.is_detected:
            av_sync = audio_result.evidence.get("av_sync", {})
            if av_sync and not av_sync.get("is_synced", True):
                actions.append(RiskAction(
                    action_type=ActionType.ALERT,
                    priority=7,
                    description="Audio-video sync mismatch detected",
                    parameters={"offset_ms": av_sync.get("offset_ms", 0)},
                ))

        if social_result and social_result.details.get("risk_category") in ["high", "critical"]:
            recommendations = social_result.details.get("recommendations", [])
            for rec in recommendations[:2]:
                actions.append(RiskAction(
                    action_type=ActionType.ALERT,
                    priority=6,
                    description=rec,
                    parameters={"source": "social_engineering_analysis"},
                ))

        # Sort by priority
        actions.sort(key=lambda a: a.priority, reverse=True)

        return actions[:10]  # Limit to top 10 actions

    def _calculate_confidence(
        self,
        audio_result: Optional[DetectionResult],
        video_result: Optional[DetectionResult],
        social_result: Optional[DetectionResult],
    ) -> float:
        """
        Calculate confidence in the aggregated result.

        Higher confidence when more detection methods are available.
        """
        available = 0
        total_weight = 0.0

        if audio_result:
            available += 1
            total_weight += 0.33

        if video_result:
            available += 1
            total_weight += 0.33

        if social_result:
            available += 1
            total_weight += 0.34

        # Base confidence on data availability
        confidence = total_weight * 100

        # Boost if all methods agree
        if available == 3:
            results = [audio_result, video_result, social_result]
            all_detected = all(r.is_detected for r in results if r)
            none_detected = all(not r.is_detected for r in results if r)

            if all_detected or none_detected:
                confidence = min(100, confidence * 1.1)

        return confidence

    def get_risk_level_description(self, level: RiskLevel) -> str:
        """Get human-readable description of risk level."""
        descriptions = {
            RiskLevel.LOW: "Low risk - Normal monitoring. No immediate action required.",
            RiskLevel.MEDIUM: "Medium risk - Monitor closely. Potential indicators present.",
            RiskLevel.HIGH: "High risk - Verification required. Strong indicators detected.",
            RiskLevel.CRITICAL: "Critical risk - Immediate intervention. Multiple confirmed indicators.",
        }
        return descriptions.get(level, "Unknown risk level")

    def get_action_description(self, action_type: ActionType) -> str:
        """Get human-readable description of action type."""
        descriptions = {
            ActionType.NONE: "No action required",
            ActionType.MONITOR: "Continue or enhance monitoring",
            ActionType.ALERT: "Display alert or notification",
            ActionType.VERIFY: "Trigger identity verification",
            ActionType.INTERVENE: "Automatic intervention (halt operations)",
        }
        return descriptions.get(action_type, "Unknown action")
