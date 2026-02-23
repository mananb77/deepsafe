"""
Tests for Keyword Analyzer

Tests keyword-based social engineering detection.
"""

import pytest

from src.services.detection.social_engineering.keyword_analyzer import (
    KeywordAnalyzer,
    KeywordAnalysisResult,
    KeywordMatch,
)


class TestKeywordAnalyzer:
    """Tests for KeywordAnalyzer class."""

    @pytest.fixture
    def analyzer(self) -> KeywordAnalyzer:
        """Create analyzer instance."""
        return KeywordAnalyzer()

    # --- Financial Keywords Tests ---

    def test_detect_wire_transfer(self, analyzer):
        """Test detection of wire transfer keywords."""
        text = "Please process this wire transfer immediately."
        result = analyzer.analyze(text)

        assert result.is_suspicious
        assert result.category_scores["financial"] > 0
        assert any(m.keyword == "wire transfer" for m in result.keyword_matches)

    def test_detect_bank_account_change(self, analyzer):
        """Test detection of bank account change keywords."""
        text = "Our bank account has changed. Please update to the new account."
        result = analyzer.analyze(text)

        assert result.category_scores["financial"] > 0

    def test_detect_routing_number(self, analyzer):
        """Test detection of sensitive financial details."""
        text = "Here's the routing number and account number for the transfer."
        result = analyzer.analyze(text)

        assert any("routing" in m.keyword.lower() for m in result.keyword_matches)

    # --- Urgency Keywords Tests ---

    def test_detect_urgency_keywords(self, analyzer):
        """Test detection of urgency keywords."""
        text = "This is urgent and must be done immediately. ASAP!"
        result = analyzer.analyze(text)

        assert result.category_scores["urgency"] > 0
        assert any(m.category == "urgency" for m in result.keyword_matches)

    def test_detect_deadline_pressure(self, analyzer):
        """Test detection of deadline pressure."""
        text = "The deadline is today. This is time sensitive and critical."
        result = analyzer.analyze(text)

        assert result.category_scores["urgency"] > 0

    # --- Authority Keywords Tests ---

    def test_detect_authority_claims(self, analyzer):
        """Test detection of authority claims."""
        text = "I'm the CEO and this has been approved by the board."
        result = analyzer.analyze(text)

        assert result.category_scores["authority"] > 0

    def test_detect_executive_titles(self, analyzer):
        """Test detection of executive titles."""
        text = "The CFO has authorized this. The president needs it done."
        result = analyzer.analyze(text)

        assert any("cfo" in m.keyword.lower() or "president" in m.keyword.lower()
                   for m in result.keyword_matches)

    # --- Secrecy Keywords Tests ---

    def test_detect_secrecy_requests(self, analyzer):
        """Test detection of secrecy requests."""
        text = "Don't tell anyone about this. Keep this confidential between us."
        result = analyzer.analyze(text)

        assert result.category_scores["secrecy"] > 0
        assert result.is_suspicious

    def test_detect_private_matter(self, analyzer):
        """Test detection of private matter indicators."""
        text = "This is a private matter. It's off the record."
        result = analyzer.analyze(text)

        assert result.category_scores["secrecy"] > 0

    # --- Sensitive Data Keywords Tests ---

    def test_detect_password_request(self, analyzer):
        """Test detection of password requests."""
        text = "Please provide your password and credentials for verification."
        result = analyzer.analyze(text)

        assert result.category_scores["sensitive_data"] > 0

    def test_detect_ssn_request(self, analyzer):
        """Test detection of SSN/personal info requests."""
        text = "I need your social security number and date of birth."
        result = analyzer.analyze(text)

        # SSN alone triggers sensitive_data category but not full suspicion
        # (would need urgency/secrecy indicators for full suspicion)
        assert result.category_scores.get("sensitive_data", 0) > 0
        assert len(result.keyword_matches) >= 2

    # --- High-Risk Phrase Tests ---

    def test_detect_high_risk_phrases(self, analyzer):
        """Test detection of high-risk phrase combinations."""
        text = "Wire transfer is urgent. The CEO needs this done today."
        result = analyzer.analyze(text)

        assert len(result.high_risk_phrases) > 0 or result.confidence > 60

    def test_detect_combined_threats(self, analyzer):
        """Test detection of combined threat patterns."""
        text = """
        Don't tell anyone about this confidential wire transfer.
        The CEO has approved this urgent payment.
        Please verify your credentials and process this immediately.
        """
        result = analyzer.analyze(text)

        # Multiple categories should be triggered
        active_categories = [cat for cat, score in result.category_scores.items() if score > 0]
        assert len(active_categories) >= 3
        assert result.confidence > 60

    # --- Benign Text Tests ---

    def test_benign_text_low_score(self, analyzer):
        """Test that benign text has low scores."""
        text = "Let's schedule a meeting to discuss the project timeline."
        result = analyzer.analyze(text)

        assert result.confidence < 30
        assert not result.is_suspicious

    def test_empty_text(self, analyzer):
        """Test handling of empty text."""
        result = analyzer.analyze("")

        assert result.confidence == 0.0
        assert not result.is_suspicious
        assert "error" in result.details

    def test_normal_business_communication(self, analyzer):
        """Test normal business communication."""
        text = """
        Thank you for the update on the project.
        I'll review the documents and get back to you tomorrow.
        Have a great day!
        """
        result = analyzer.analyze(text)

        assert result.confidence < 40

    # --- Context Tests ---

    def test_keyword_context_extraction(self, analyzer):
        """Test that context is extracted around keywords."""
        text = "Before this part, wire transfer some words, and after this part."
        result = analyzer.analyze(text)

        if result.keyword_matches:
            match = result.keyword_matches[0]
            assert len(match.context) > len(match.keyword)

    # --- Score Calculation Tests ---

    def test_score_range(self, analyzer):
        """Test that scores are in valid range."""
        text = "Urgent wire transfer confidential CEO approved password."
        result = analyzer.analyze(text)

        assert 0.0 <= result.confidence <= 100.0
        assert 0.0 <= result.total_risk_score <= 100.0
        for score in result.category_scores.values():
            assert 0.0 <= score <= 100.0


class TestKeywordMatch:
    """Tests for KeywordMatch dataclass."""

    def test_match_creation(self):
        """Test creating a keyword match."""
        match = KeywordMatch(
            keyword="wire transfer",
            category="financial",
            risk_weight=0.9,
            context="Please process this wire transfer today.",
            position=20,
        )

        assert match.keyword == "wire transfer"
        assert match.category == "financial"
        assert match.risk_weight == 0.9


class TestKeywordAnalysisResult:
    """Tests for KeywordAnalysisResult dataclass."""

    def test_result_creation(self):
        """Test creating result with all fields."""
        result = KeywordAnalysisResult(
            is_suspicious=True,
            confidence=75.0,
            total_risk_score=70.0,
            keyword_matches=[],
            category_scores={"financial": 80.0, "urgency": 60.0},
            high_risk_phrases=["urgent wire transfer"],
            details={"total_matches": 5},
        )

        assert result.is_suspicious
        assert result.confidence == 75.0
        assert result.category_scores["financial"] == 80.0
