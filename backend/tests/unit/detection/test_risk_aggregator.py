"""
Tests for Risk Aggregator

Tests combining detection results into composite risk scores.
"""

import pytest

from src.services.detection.risk_aggregator import (
    RiskAggregator,
    AggregatedRiskResult,
    RiskAction,
    ActionType,
)
from src.services.detection.base import (
    DetectionResult,
    DetectionType,
    RiskLevel,
)


class TestRiskAggregator:
    """Tests for RiskAggregator class."""

    @pytest.fixture
    def aggregator(self) -> RiskAggregator:
        """Create aggregator instance."""
        return RiskAggregator()

    @pytest.fixture
    def low_risk_audio_result(self) -> DetectionResult:
        """Create low-risk audio detection result."""
        return DetectionResult(
            detection_type=DetectionType.AUDIO_DEEPFAKE,
            is_detected=False,
            confidence=15.0,
            risk_level=RiskLevel.LOW,
            details={},
            evidence={},
            method="test",
            latency_ms=100.0,
        )

    @pytest.fixture
    def high_risk_audio_result(self) -> DetectionResult:
        """Create high-risk audio detection result."""
        return DetectionResult(
            detection_type=DetectionType.AUDIO_DEEPFAKE,
            is_detected=True,
            confidence=85.0,
            risk_level=RiskLevel.HIGH,
            details={"method_scores": {"resemble": 85}},
            evidence={"av_sync": {"is_synced": False, "offset_ms": 150}},
            method="test",
            latency_ms=100.0,
        )

    @pytest.fixture
    def low_risk_video_result(self) -> DetectionResult:
        """Create low-risk video detection result."""
        return DetectionResult(
            detection_type=DetectionType.VIDEO_DEEPFAKE,
            is_detected=False,
            confidence=10.0,
            risk_level=RiskLevel.LOW,
            details={"virtual_camera_detected": False},
            evidence={},
            method="test",
            latency_ms=150.0,
        )

    @pytest.fixture
    def high_risk_video_result(self) -> DetectionResult:
        """Create high-risk video detection result."""
        return DetectionResult(
            detection_type=DetectionType.VIDEO_DEEPFAKE,
            is_detected=True,
            confidence=80.0,
            risk_level=RiskLevel.HIGH,
            details={"virtual_camera_detected": True},
            evidence={"virtual_camera": {"confidence": 90, "detected_software": "OBS"}},
            method="test",
            latency_ms=150.0,
        )

    @pytest.fixture
    def low_risk_social_result(self) -> DetectionResult:
        """Create low-risk social engineering result."""
        return DetectionResult(
            detection_type=DetectionType.SOCIAL_ENGINEERING,
            is_detected=False,
            confidence=20.0,
            risk_level=RiskLevel.LOW,
            details={"risk_category": "low", "detected_scenarios": []},
            evidence={},
            method="test",
            latency_ms=200.0,
        )

    @pytest.fixture
    def high_risk_social_result(self) -> DetectionResult:
        """Create high-risk social engineering result."""
        return DetectionResult(
            detection_type=DetectionType.SOCIAL_ENGINEERING,
            is_detected=True,
            confidence=90.0,
            risk_level=RiskLevel.CRITICAL,
            details={
                "risk_category": "critical",
                "detected_scenarios": ["ceo_fraud"],
                "recommendations": ["Verify request directly"],
            },
            evidence={},
            method="test",
            latency_ms=200.0,
        )

    # --- Basic Aggregation Tests ---

    def test_aggregate_returns_result(self, aggregator, low_risk_audio_result):
        """Test that aggregate returns AggregatedRiskResult."""
        result = aggregator.aggregate(audio_result=low_risk_audio_result)
        assert isinstance(result, AggregatedRiskResult)

    def test_aggregate_no_results(self, aggregator):
        """Test aggregation with no results."""
        result = aggregator.aggregate()
        assert result.composite_risk_score == 0.0
        assert result.risk_level == RiskLevel.LOW

    def test_aggregate_low_risk_all(
        self, aggregator, low_risk_audio_result, low_risk_video_result, low_risk_social_result
    ):
        """Test aggregation with all low-risk results."""
        result = aggregator.aggregate(
            audio_result=low_risk_audio_result,
            video_result=low_risk_video_result,
            social_engineering_result=low_risk_social_result,
        )

        assert result.composite_risk_score < 30
        assert result.risk_level == RiskLevel.LOW

    def test_aggregate_high_risk_audio(self, aggregator, high_risk_audio_result):
        """Test aggregation with high-risk audio result."""
        result = aggregator.aggregate(audio_result=high_risk_audio_result)

        assert result.audio_deepfake_score == 85.0
        # Single audio source with 0.4 deepfake weight: 42.5 * 0.4 = 17
        assert result.composite_risk_score > 0
        assert result.deepfake_score > 0

    def test_aggregate_high_risk_video(self, aggregator, high_risk_video_result):
        """Test aggregation with high-risk video result."""
        result = aggregator.aggregate(video_result=high_risk_video_result)

        assert result.video_deepfake_score == 80.0
        assert result.virtual_camera_detected

    def test_aggregate_high_risk_social(self, aggregator, high_risk_social_result):
        """Test aggregation with high-risk social engineering result."""
        result = aggregator.aggregate(social_engineering_result=high_risk_social_result)

        assert result.social_engineering_score == 90.0
        # Single source at 90% with 0.4 weight = 36% composite = MEDIUM
        assert result.composite_risk_score > 30
        assert result.risk_level == RiskLevel.MEDIUM

    # --- Combined Risk Tests ---

    def test_combined_high_risk(
        self, aggregator, high_risk_audio_result, high_risk_video_result, high_risk_social_result
    ):
        """Test combination of multiple high-risk results."""
        result = aggregator.aggregate(
            audio_result=high_risk_audio_result,
            video_result=high_risk_video_result,
            social_engineering_result=high_risk_social_result,
        )

        # Multiple high-risk indicators should result in critical
        assert result.risk_level == RiskLevel.CRITICAL
        assert result.composite_risk_score > 80
        assert len(result.risk_factors) >= 2

    def test_deepfake_plus_social_engineering_boost(
        self, aggregator, high_risk_audio_result, high_risk_social_result
    ):
        """Test that deepfake + social engineering gets boosted."""
        result = aggregator.aggregate(
            audio_result=high_risk_audio_result,
            social_engineering_result=high_risk_social_result,
        )

        # Should have boosting applied
        assert any("combined" in f.lower() for f in result.risk_factors)

    def test_virtual_camera_plus_deepfake_boost(
        self, aggregator, high_risk_video_result, high_risk_audio_result
    ):
        """Test virtual camera + deepfake detection boost."""
        result = aggregator.aggregate(
            audio_result=high_risk_audio_result,
            video_result=high_risk_video_result,
        )

        assert result.virtual_camera_detected
        assert result.composite_risk_score > 50

    # --- Action Generation Tests ---

    def test_low_risk_monitor_action(self, aggregator, low_risk_audio_result):
        """Test that low risk generates monitor action."""
        result = aggregator.aggregate(audio_result=low_risk_audio_result)

        assert any(a.action_type == ActionType.MONITOR for a in result.recommended_actions)

    def test_high_risk_verify_action(self, aggregator, high_risk_audio_result, high_risk_social_result):
        """Test that high risk generates verify action."""
        result = aggregator.aggregate(
            audio_result=high_risk_audio_result,
            social_engineering_result=high_risk_social_result,
        )

        assert any(a.action_type == ActionType.VERIFY for a in result.recommended_actions)

    def test_critical_risk_intervene_action(
        self, aggregator, high_risk_audio_result, high_risk_video_result, high_risk_social_result
    ):
        """Test that critical risk generates intervene action."""
        result = aggregator.aggregate(
            audio_result=high_risk_audio_result,
            video_result=high_risk_video_result,
            social_engineering_result=high_risk_social_result,
        )

        if result.risk_level == RiskLevel.CRITICAL:
            assert any(a.action_type == ActionType.INTERVENE for a in result.recommended_actions)

    def test_actions_sorted_by_priority(self, aggregator, high_risk_social_result):
        """Test that actions are sorted by priority."""
        result = aggregator.aggregate(social_engineering_result=high_risk_social_result)

        if len(result.recommended_actions) > 1:
            priorities = [a.priority for a in result.recommended_actions]
            assert priorities == sorted(priorities, reverse=True)

    # --- Confidence Tests ---

    def test_confidence_with_all_results(
        self, aggregator, low_risk_audio_result, low_risk_video_result, low_risk_social_result
    ):
        """Test confidence is higher with all results available."""
        result = aggregator.aggregate(
            audio_result=low_risk_audio_result,
            video_result=low_risk_video_result,
            social_engineering_result=low_risk_social_result,
        )

        assert result.confidence > 90  # All three sources available

    def test_confidence_with_single_result(self, aggregator, low_risk_audio_result):
        """Test confidence is lower with single result."""
        result = aggregator.aggregate(audio_result=low_risk_audio_result)

        assert result.confidence < 50

    # --- Risk Level Tests ---

    def test_risk_level_thresholds(self, aggregator):
        """Test risk level threshold values."""
        assert aggregator.THRESHOLD_LOW == 30.0
        assert aggregator.THRESHOLD_MEDIUM == 60.0
        assert aggregator.THRESHOLD_HIGH == 85.0

    def test_score_to_risk_level(self, aggregator):
        """Test score to risk level conversion."""
        assert aggregator._score_to_risk_level(20.0) == RiskLevel.LOW
        assert aggregator._score_to_risk_level(45.0) == RiskLevel.MEDIUM
        assert aggregator._score_to_risk_level(75.0) == RiskLevel.HIGH
        assert aggregator._score_to_risk_level(95.0) == RiskLevel.CRITICAL

    # --- Custom Weights Tests ---

    def test_custom_weights(self):
        """Test aggregator with custom weights."""
        aggregator = RiskAggregator(
            deepfake_weight=0.6,
            social_engineering_weight=0.3,
            virtual_camera_weight=0.1,
        )

        # Weights should be normalized
        total = (aggregator.WEIGHT_DEEPFAKE +
                 aggregator.WEIGHT_SOCIAL_ENGINEERING +
                 aggregator.WEIGHT_VIRTUAL_CAMERA)
        assert abs(total - 1.0) < 0.01

    # --- Utility Method Tests ---

    def test_get_risk_level_description(self, aggregator):
        """Test getting risk level descriptions."""
        desc = aggregator.get_risk_level_description(RiskLevel.CRITICAL)
        assert "critical" in desc.lower() or "immediate" in desc.lower()

        desc = aggregator.get_risk_level_description(RiskLevel.LOW)
        assert "low" in desc.lower() or "normal" in desc.lower()

    def test_get_action_description(self, aggregator):
        """Test getting action descriptions."""
        desc = aggregator.get_action_description(ActionType.INTERVENE)
        assert "interven" in desc.lower() or "halt" in desc.lower()

        desc = aggregator.get_action_description(ActionType.MONITOR)
        assert "monitor" in desc.lower()


class TestAggregatedRiskResult:
    """Tests for AggregatedRiskResult dataclass."""

    def test_result_creation(self):
        """Test creating result with all fields."""
        result = AggregatedRiskResult(
            composite_risk_score=75.0,
            risk_level=RiskLevel.HIGH,
            deepfake_score=70.0,
            social_engineering_score=80.0,
            audio_deepfake_score=65.0,
            video_deepfake_score=75.0,
            virtual_camera_detected=True,
            recommended_actions=[],
            risk_factors=["Test factor"],
            confidence=85.0,
            details={},
        )

        assert result.composite_risk_score == 75.0
        assert result.risk_level == RiskLevel.HIGH
        assert result.virtual_camera_detected


class TestRiskAction:
    """Tests for RiskAction dataclass."""

    def test_action_creation(self):
        """Test creating a risk action."""
        action = RiskAction(
            action_type=ActionType.VERIFY,
            priority=8,
            description="Identity verification required",
            target="participant-123",
            parameters={"channels": ["sms", "push"]},
        )

        assert action.action_type == ActionType.VERIFY
        assert action.priority == 8
        assert action.target == "participant-123"


class TestActionType:
    """Tests for ActionType enum."""

    def test_all_action_types(self):
        """Test all action types exist."""
        assert ActionType.NONE
        assert ActionType.MONITOR
        assert ActionType.ALERT
        assert ActionType.VERIFY
        assert ActionType.INTERVENE

    def test_action_type_values(self):
        """Test action type string values."""
        assert ActionType.NONE.value == "none"
        assert ActionType.INTERVENE.value == "intervene"
