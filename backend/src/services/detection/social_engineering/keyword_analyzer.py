"""
Keyword Analyzer

Analyzes conversation keywords for social engineering indicators:
- Financial keywords (wire transfer, bank account, payment)
- Urgency keywords (urgent, immediately, deadline)
- Authority keywords (CEO, approved, authorized)
- Secrecy keywords (confidential, don't tell anyone)
- Action keywords (click, download, send)
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Set, Tuple
import re


@dataclass
class KeywordMatch:
    """A single keyword match with context."""

    keyword: str
    category: str
    risk_weight: float
    context: str  # Surrounding text
    position: int


@dataclass
class KeywordAnalysisResult:
    """Result from keyword analysis."""

    is_suspicious: bool
    confidence: float  # 0-100
    total_risk_score: float
    keyword_matches: List[KeywordMatch]
    category_scores: Dict[str, float]
    high_risk_phrases: List[str]
    details: Dict[str, Any]


class KeywordAnalyzer:
    """
    Analyzes conversation content for suspicious keywords and phrases.

    Keyword categories:
    1. Financial - Wire transfers, payments, bank changes
    2. Urgency - Time pressure, deadlines, immediate action
    3. Authority - Executive claims, approvals, overrides
    4. Secrecy - Confidentiality, hiding from others
    5. Action - Instructions to perform specific actions
    6. Sensitive Data - Personal info, credentials, access

    Weight: 20% of total social engineering score
    """

    # Financial keywords (highest risk)
    FINANCIAL_KEYWORDS = {
        # Wire/Transfer
        "wire transfer": 0.9,
        "wire money": 0.9,
        "bank transfer": 0.8,
        "transfer funds": 0.8,
        "send money": 0.7,
        "payment": 0.5,

        # Bank account
        "bank account": 0.7,
        "account number": 0.8,
        "routing number": 0.9,
        "iban": 0.8,
        "swift code": 0.8,

        # Changes
        "change bank": 0.9,
        "new account": 0.8,
        "updated account": 0.8,
        "different account": 0.9,
        "account change": 0.8,

        # Invoice
        "invoice": 0.4,
        "outstanding balance": 0.5,
        "payment due": 0.5,
        "overdue": 0.5,

        # Amounts
        "thousand": 0.3,
        "million": 0.6,
        "$": 0.2,
    }

    # Urgency keywords
    URGENCY_KEYWORDS = {
        "urgent": 0.7,
        "urgently": 0.7,
        "asap": 0.8,
        "immediately": 0.8,
        "right now": 0.7,
        "right away": 0.7,
        "today": 0.4,
        "by end of day": 0.6,
        "deadline": 0.5,
        "time sensitive": 0.7,
        "critical": 0.6,
        "emergency": 0.8,
        "can't wait": 0.7,
        "cannot wait": 0.7,
        "must be done": 0.6,
        "don't delay": 0.7,
    }

    # Authority keywords
    AUTHORITY_KEYWORDS = {
        "ceo": 0.6,
        "cfo": 0.6,
        "president": 0.5,
        "director": 0.4,
        "executive": 0.5,
        "board": 0.5,
        "chairman": 0.5,
        "approved": 0.4,
        "authorized": 0.5,
        "authority": 0.4,
        "override": 0.6,
        "special approval": 0.7,
        "executive order": 0.7,
        "direct order": 0.7,
        "my request": 0.3,
        "i'm asking": 0.3,
        "i need you to": 0.4,
    }

    # Secrecy keywords
    SECRECY_KEYWORDS = {
        "confidential": 0.5,
        "secret": 0.6,
        "private": 0.4,
        "don't tell": 0.8,
        "do not tell": 0.8,
        "don't mention": 0.7,
        "don't inform": 0.7,
        "keep this between": 0.8,
        "between us": 0.7,
        "off the record": 0.7,
        "sensitive matter": 0.6,
        "need to know": 0.5,
        "do not share": 0.6,
        "no one else": 0.6,
    }

    # Action keywords
    ACTION_KEYWORDS = {
        "click": 0.5,
        "click here": 0.6,
        "download": 0.5,
        "install": 0.6,
        "run": 0.4,
        "execute": 0.5,
        "open": 0.3,
        "verify": 0.4,
        "confirm": 0.3,
        "update": 0.3,
        "change": 0.3,
        "process": 0.3,
        "complete": 0.3,
        "send me": 0.4,
        "give me": 0.4,
        "provide": 0.3,
    }

    # Sensitive data keywords
    SENSITIVE_DATA_KEYWORDS = {
        "password": 0.8,
        "credentials": 0.8,
        "login": 0.5,
        "username": 0.5,
        "social security": 0.9,
        "ssn": 0.9,
        "tax id": 0.7,
        "employee id": 0.5,
        "date of birth": 0.6,
        "dob": 0.6,
        "credit card": 0.8,
        "cvv": 0.9,
        "pin": 0.7,
        "access code": 0.7,
        "verification code": 0.6,
        "mfa code": 0.8,
        "2fa": 0.6,
        "authenticator": 0.5,
    }

    # High-risk phrase combinations
    HIGH_RISK_PHRASES = [
        (r"(?i)wire\s+.{0,30}(urgent|immediately|today)", 0.95),
        (r"(?i)(ceo|cfo|president)\s+.{0,20}(urgent|need|request)", 0.85),
        (r"(?i)bank\s+account\s+.{0,20}(change|update|new)", 0.90),
        (r"(?i)don'?t\s+tell\s+.{0,20}(anyone|other)", 0.85),
        (r"(?i)(password|credentials)\s+.{0,20}(verify|confirm|need)", 0.90),
        (r"(?i)urgent\s+.{0,20}transfer", 0.90),
        (r"(?i)confidential\s+.{0,20}(wire|transfer|payment)", 0.90),
        (r"(?i)(click|go\s+to)\s+.{0,30}(link|url)", 0.70),
    ]

    def __init__(self):
        # Compile phrase patterns
        self._phrase_patterns = [
            (re.compile(pattern), weight)
            for pattern, weight in self.HIGH_RISK_PHRASES
        ]

    def analyze(
        self,
        text: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> KeywordAnalysisResult:
        """
        Analyze text for suspicious keywords.

        Args:
            text: Text to analyze.
            context: Additional context for analysis.

        Returns:
            KeywordAnalysisResult with findings.
        """
        if not text:
            return KeywordAnalysisResult(
                is_suspicious=False,
                confidence=0.0,
                total_risk_score=0.0,
                keyword_matches=[],
                category_scores={},
                high_risk_phrases=[],
                details={"error": "No text provided"},
            )

        text_lower = text.lower()
        keyword_matches: List[KeywordMatch] = []
        category_scores: Dict[str, float] = {
            "financial": 0.0,
            "urgency": 0.0,
            "authority": 0.0,
            "secrecy": 0.0,
            "action": 0.0,
            "sensitive_data": 0.0,
        }

        # Check each keyword category
        keyword_matches.extend(
            self._find_keywords(text, text_lower, self.FINANCIAL_KEYWORDS, "financial")
        )
        keyword_matches.extend(
            self._find_keywords(text, text_lower, self.URGENCY_KEYWORDS, "urgency")
        )
        keyword_matches.extend(
            self._find_keywords(text, text_lower, self.AUTHORITY_KEYWORDS, "authority")
        )
        keyword_matches.extend(
            self._find_keywords(text, text_lower, self.SECRECY_KEYWORDS, "secrecy")
        )
        keyword_matches.extend(
            self._find_keywords(text, text_lower, self.ACTION_KEYWORDS, "action")
        )
        keyword_matches.extend(
            self._find_keywords(text, text_lower, self.SENSITIVE_DATA_KEYWORDS, "sensitive_data")
        )

        # Calculate category scores
        for match in keyword_matches:
            category_scores[match.category] = max(
                category_scores[match.category],
                match.risk_weight * 100
            )

        # Check high-risk phrase combinations
        high_risk_phrases: List[str] = []
        phrase_score = 0.0

        for pattern, weight in self._phrase_patterns:
            matches = pattern.findall(text)
            if matches:
                for m in matches:
                    phrase_text = m if isinstance(m, str) else " ".join(m)
                    high_risk_phrases.append(phrase_text)
                phrase_score = max(phrase_score, weight * 100)

        # Calculate total risk score
        # Weighted combination of category scores
        total_risk_score = (
            category_scores["financial"] * 0.30 +
            category_scores["urgency"] * 0.15 +
            category_scores["authority"] * 0.15 +
            category_scores["secrecy"] * 0.20 +
            category_scores["action"] * 0.10 +
            category_scores["sensitive_data"] * 0.10
        )

        # Boost if high-risk phrases found
        if phrase_score > 0:
            total_risk_score = max(total_risk_score, phrase_score * 0.8)
            total_risk_score = min(100, total_risk_score * 1.2)

        # Calculate confidence based on number and severity of matches
        match_severity = sum(m.risk_weight for m in keyword_matches)
        confidence = min(100, total_risk_score + (match_severity * 5))

        # Determine if suspicious
        is_suspicious = confidence > 40.0 or len(high_risk_phrases) > 0

        return KeywordAnalysisResult(
            is_suspicious=is_suspicious,
            confidence=confidence,
            total_risk_score=total_risk_score,
            keyword_matches=keyword_matches[:30],  # Limit output
            category_scores=category_scores,
            high_risk_phrases=high_risk_phrases,
            details={
                "total_matches": len(keyword_matches),
                "categories_triggered": [
                    cat for cat, score in category_scores.items() if score > 0
                ],
                "phrase_patterns_matched": len(high_risk_phrases),
            },
        )

    def _find_keywords(
        self,
        text: str,
        text_lower: str,
        keywords: Dict[str, float],
        category: str,
    ) -> List[KeywordMatch]:
        """Find keyword matches in text."""
        matches = []

        for keyword, weight in keywords.items():
            keyword_lower = keyword.lower()

            # Find all occurrences
            start = 0
            while True:
                pos = text_lower.find(keyword_lower, start)
                if pos == -1:
                    break

                # Extract context (50 chars before and after)
                context_start = max(0, pos - 50)
                context_end = min(len(text), pos + len(keyword) + 50)
                context = text[context_start:context_end]

                matches.append(KeywordMatch(
                    keyword=keyword,
                    category=category,
                    risk_weight=weight,
                    context=context,
                    position=pos,
                ))

                start = pos + 1

        return matches

    def get_category_description(self, category: str) -> str:
        """Get description of keyword category."""
        descriptions = {
            "financial": "Financial terms related to money transfers and payments",
            "urgency": "Time pressure and urgency indicators",
            "authority": "Authority claims and executive references",
            "secrecy": "Requests for confidentiality and hiding information",
            "action": "Instructions to perform specific actions",
            "sensitive_data": "Requests for sensitive personal or access information",
        }
        return descriptions.get(category, "Unknown category")
