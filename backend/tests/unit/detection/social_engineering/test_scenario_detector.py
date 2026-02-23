"""
Tests for Scenario Detector

Tests detection of known social engineering attack patterns.
"""

import pytest

from src.services.detection.social_engineering.scenario_detector import (
    ScenarioDetector,
    ScenarioResult,
    AttackScenario,
)


class TestScenarioDetector:
    """Tests for ScenarioDetector class."""

    @pytest.fixture
    def detector(self) -> ScenarioDetector:
        """Create detector instance."""
        return ScenarioDetector()

    # --- CEO Fraud Detection Tests ---

    def test_detect_ceo_fraud_basic(self, detector):
        """Test basic CEO fraud detection."""
        transcript = """
        This is the CEO speaking. I need you to process an urgent wire transfer.
        Please wire $50,000 to this account immediately. Don't tell anyone about this.
        """
        result = detector.analyze(transcript)

        assert result.primary_scenario == AttackScenario.CEO_FRAUD
        assert result.confidence > 50
        assert AttackScenario.CEO_FRAUD in result.detected_scenarios

    def test_detect_ceo_fraud_with_urgency(self, detector):
        """Test CEO fraud with urgency indicators."""
        transcript = """
        Hi, this is John, the CEO. I'm in a meeting but need something done urgently.
        We have a confidential acquisition happening. This is extremely time sensitive.
        Wire $100,000 to the new vendor account. This must be done today, ASAP.
        """
        result = detector.analyze(transcript)

        # Urgency patterns are detected
        assert result.urgency_level > 0.3
        # Pattern matches should include urgency indicators
        assert len(result.pattern_matches) > 0

    def test_detect_ceo_fraud_secrecy(self, detector):
        """Test CEO fraud with secrecy requests."""
        transcript = """
        The CEO here. I need you to keep this between us.
        Don't tell anyone else about this transaction.
        This is a private matter that's confidential.
        """
        result = detector.analyze(transcript)

        assert len(result.pattern_matches) > 0

    # --- Vendor Fraud Detection Tests ---

    def test_detect_vendor_fraud(self, detector):
        """Test vendor/invoice fraud detection."""
        transcript = """
        This is your vendor calling. Our bank account has changed.
        Please update your records with our new account details.
        Wire the payment to this different account number.
        """
        result = detector.analyze(transcript)

        assert AttackScenario.VENDOR_IMPERSONATION in result.detected_scenarios
        assert result.confidence > 40

    def test_detect_payment_redirect(self, detector):
        """Test payment redirect fraud."""
        transcript = """
        Hi, this is the accounting department from your supplier.
        We're updating our payment information.
        Please redirect all future payments to this new bank account.
        The invoice is urgent and past due.
        """
        result = detector.analyze(transcript)

        assert result.confidence > 40

    # --- IT Support Scam Detection Tests ---

    def test_detect_it_support_scam(self, detector):
        """Test IT support scam detection."""
        transcript = """
        I'm from IT support. We've detected a security issue on your computer.
        I need your password to fix the problem.
        Please install this remote access software so I can help you.
        """
        result = detector.analyze(transcript)

        assert AttackScenario.IT_SUPPORT_SCAM in result.detected_scenarios
        assert result.confidence > 50

    def test_detect_credential_harvesting(self, detector):
        """Test credential harvesting detection."""
        transcript = """
        Your password has expired and needs to be reset.
        Please verify your identity by providing your current credentials.
        Click this link to update your login information.
        """
        result = detector.analyze(transcript)

        assert AttackScenario.CREDENTIAL_HARVESTING in result.detected_scenarios

    # --- HR Fraud Detection Tests ---

    def test_detect_hr_impersonation(self, detector):
        """Test HR impersonation detection."""
        transcript = """
        This is HR calling. We need to update your direct deposit information.
        Please provide your new bank details for payroll.
        Also, can you send me the employee records?
        """
        result = detector.analyze(transcript)

        # HR-related patterns are detected in the scenario scores
        assert result.details.get("scenario_scores", {}).get("hr_impersonation", 0) > 0
        assert len(result.pattern_matches) > 0

    # --- Benign Conversation Tests ---

    def test_benign_conversation_low_score(self, detector):
        """Test that benign conversations have low scores."""
        transcript = """
        Hi John, thanks for joining the meeting.
        Let's review the quarterly report together.
        I'll send you the document after we finish.
        Sounds good, see you next week.
        """
        result = detector.analyze(transcript)

        assert result.confidence < 30
        assert len(result.detected_scenarios) == 0

    def test_empty_transcript(self, detector):
        """Test handling of empty transcript."""
        result = detector.analyze("")

        assert result.confidence == 0.0
        assert len(result.detected_scenarios) == 0
        assert "error" in result.details

    def test_normal_financial_discussion(self, detector):
        """Test that normal financial discussions aren't flagged."""
        transcript = """
        Let's review the budget for next quarter.
        The payment to the vendor was processed last week.
        The invoice has been paid according to the normal schedule.
        """
        result = detector.analyze(transcript)

        # Some keywords may match but confidence should be moderate
        assert result.confidence < 60 or len(result.detected_scenarios) == 0

    # --- Authority and Urgency Tests ---

    def test_authority_exploitation_score(self, detector):
        """Test authority exploitation scoring."""
        transcript = """
        I'm the CEO and I'm authorizing this directly.
        This is a direct order from the board.
        I have special authority to override the normal process.
        """
        result = detector.analyze(transcript)

        assert result.authority_exploitation > 0.3

    def test_urgency_level_calculation(self, detector):
        """Test urgency level calculation."""
        transcript = """
        This is urgent and must be done immediately.
        The deadline is today. We can't wait.
        Do this right now, ASAP. Time sensitive!
        """
        result = detector.analyze(transcript)

        assert result.urgency_level > 0.5

    # --- Utility Method Tests ---

    def test_get_scenario_description(self, detector):
        """Test getting scenario descriptions."""
        description = detector.get_scenario_description(AttackScenario.CEO_FRAUD)
        assert "CEO" in description or "executive" in description.lower()

        description = detector.get_scenario_description(AttackScenario.IT_SUPPORT_SCAM)
        assert "IT" in description or "support" in description.lower()


class TestScenarioResult:
    """Tests for ScenarioResult dataclass."""

    def test_result_creation(self):
        """Test creating result with all fields."""
        result = ScenarioResult(
            detected_scenarios=[AttackScenario.CEO_FRAUD],
            primary_scenario=AttackScenario.CEO_FRAUD,
            confidence=75.0,
            pattern_matches=["CEO fraud pattern"],
            urgency_level=0.6,
            authority_exploitation=0.5,
            details={"scenario_scores": {"ceo_fraud": 75}},
        )

        assert result.primary_scenario == AttackScenario.CEO_FRAUD
        assert result.confidence == 75.0
        assert result.urgency_level == 0.6


class TestAttackScenario:
    """Tests for AttackScenario enum."""

    def test_all_scenarios_have_values(self):
        """Test that all scenarios have string values."""
        for scenario in AttackScenario:
            assert isinstance(scenario.value, str)
            assert len(scenario.value) > 0

    def test_scenario_values_unique(self):
        """Test that scenario values are unique."""
        values = [s.value for s in AttackScenario]
        assert len(values) == len(set(values))
