"""
Scenario Detector

Detects known social engineering attack patterns:
- Business Email Compromise (BEC) scenarios
- CEO fraud / executive impersonation
- Vendor/supplier fraud
- IT support scams
- HR/payroll fraud
- Account compromise schemes
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Set
import re


class AttackScenario(Enum):
    """Known social engineering attack scenarios."""

    # BEC Scenarios
    CEO_FRAUD = "ceo_fraud"
    CFO_FRAUD = "cfo_fraud"
    EXECUTIVE_IMPERSONATION = "executive_impersonation"

    # Vendor/Supplier Fraud
    VENDOR_IMPERSONATION = "vendor_impersonation"
    INVOICE_FRAUD = "invoice_fraud"
    PAYMENT_REDIRECT = "payment_redirect"

    # Internal Threats
    IT_SUPPORT_SCAM = "it_support_scam"
    HR_IMPERSONATION = "hr_impersonation"
    PAYROLL_DIVERSION = "payroll_diversion"

    # Account Compromise
    CREDENTIAL_HARVESTING = "credential_harvesting"
    MFA_BYPASS = "mfa_bypass"

    # Urgency/Pressure Tactics
    EMERGENCY_REQUEST = "emergency_request"
    TIME_PRESSURE = "time_pressure"

    # Unknown/Other
    UNKNOWN = "unknown"


@dataclass
class ScenarioResult:
    """Result from scenario detection."""

    detected_scenarios: List[AttackScenario]
    primary_scenario: Optional[AttackScenario]
    confidence: float  # 0-100
    pattern_matches: List[str]
    urgency_level: float  # 0-1
    authority_exploitation: float  # 0-1
    details: Dict[str, Any]


class ScenarioDetector:
    """
    Detects known social engineering attack scenarios from conversation content.

    Uses pattern matching on:
    1. Conversation flow patterns
    2. Request types
    3. Authority claims
    4. Urgency indicators
    5. Secrecy requests

    Weight: 20% of total social engineering score
    """

    # CEO/Executive fraud patterns
    CEO_FRAUD_PATTERNS = [
        r"(?i)\b(ceo|cfo|president|chairman|director)\s+(here|speaking|calling)",
        r"(?i)\bi\s+(need|require|want)\s+(you\s+to\s+)?(transfer|wire|send)",
        r"(?i)\b(urgent|confidential|sensitive)\s+(matter|request|transaction)",
        r"(?i)\bdon'?t\s+(tell|inform|notify)\s+(anyone|others)",
        r"(?i)\b(acquisition|merger|deal)\s+.{0,20}\b(confidential|secret)",
    ]

    # Vendor/Invoice fraud patterns
    VENDOR_FRAUD_PATTERNS = [
        r"(?i)\bbank\s+(account|details?)\s+(has\s+)?(changed|updated)",
        r"(?i)\b(new|updated)\s+(bank|account|payment)\s+(info|details|instructions)",
        r"(?i)\b(wire|transfer)\s+to\s+.{0,30}\b(new|different)\s+account",
        r"(?i)\binvoice\s+.{0,20}\b(urgent|overdue|past\s+due)",
        r"(?i)\b(vendor|supplier)\s+.{0,20}\bpayment\s+(redirect|change)",
    ]

    # IT support scam patterns
    IT_SUPPORT_PATTERNS = [
        r"(?i)\bi('?m|\s+am)\s+(from\s+)?(it|tech|support|helpdesk)",
        r"(?i)\b(security|virus|malware)\s+(issue|alert|detection)",
        r"(?i)\bneed\s+(your\s+)?(password|credentials|login)",
        r"(?i)\b(remote\s+access|teamviewer|anydesk|logmein)",
        r"(?i)\b(install|download|run)\s+this\s+(software|program|tool)",
    ]

    # HR/Payroll fraud patterns
    HR_FRAUD_PATTERNS = [
        r"(?i)\b(hr|human\s+resources|payroll)\s+(department|team|here)",
        r"(?i)\b(direct\s+deposit|bank\s+details?)\s+(change|update)",
        r"(?i)\b(w-?2|tax\s+form|salary)\s+(request|info)",
        r"(?i)\bemployee\s+.{0,20}\b(records?|information|data)",
    ]

    # Credential harvesting patterns
    CREDENTIAL_PATTERNS = [
        r"(?i)\b(verify|confirm)\s+(your\s+)?(identity|account|login)",
        r"(?i)\b(password|credentials?|login)\s+.{0,20}\b(expired|reset|verify)",
        r"(?i)\b(click|go\s+to|visit)\s+.{0,30}\b(link|url|portal)",
        r"(?i)\b(mfa|2fa|two-?factor|authenticator)\s+.{0,20}\b(code|token)",
    ]

    # Urgency/Pressure patterns
    URGENCY_PATTERNS = [
        r"(?i)\b(urgent|asap|immediately|right\s+now|today)",
        r"(?i)\b(deadline|time\s+sensitive|critical|emergency)",
        r"(?i)\b(before|by)\s+(end\s+of\s+)?(day|today|business\s+hours)",
        r"(?i)\b(must|have\s+to|need\s+to)\s+.{0,20}\b(now|today|immediately)",
        r"(?i)\b(can'?t|cannot)\s+wait",
    ]

    # Secrecy/Confidentiality patterns
    SECRECY_PATTERNS = [
        r"(?i)\bdon'?t\s+(tell|inform|notify|mention)",
        r"(?i)\b(keep\s+)?(this\s+)?(confidential|secret|between\s+us)",
        r"(?i)\b(private|sensitive)\s+(matter|request)",
        r"(?i)\bno\s+one\s+(else\s+)?(should\s+)?(know|be\s+aware)",
        r"(?i)\boff\s+the\s+record",
    ]

    # Authority exploitation patterns
    AUTHORITY_PATTERNS = [
        r"(?i)\bi('?m|\s+am)\s+(the\s+)?(ceo|cfo|president|director|manager|boss)",
        r"(?i)\b(john|name)\s+(smith|doe)?\s*(,\s*)?(ceo|cfo|president)",
        r"(?i)\b(board|executive|senior\s+management)\s+(approved|authorized)",
        r"(?i)\breporting\s+(directly\s+)?to\s+(ceo|board|executive)",
        r"(?i)\b(special|executive)\s+(authority|approval|override)",
    ]

    def __init__(self):
        # Compile all patterns for efficiency
        self._compiled_patterns: Dict[str, List[re.Pattern]] = {
            "ceo_fraud": [re.compile(p) for p in self.CEO_FRAUD_PATTERNS],
            "vendor_fraud": [re.compile(p) for p in self.VENDOR_FRAUD_PATTERNS],
            "it_support": [re.compile(p) for p in self.IT_SUPPORT_PATTERNS],
            "hr_fraud": [re.compile(p) for p in self.HR_FRAUD_PATTERNS],
            "credentials": [re.compile(p) for p in self.CREDENTIAL_PATTERNS],
            "urgency": [re.compile(p) for p in self.URGENCY_PATTERNS],
            "secrecy": [re.compile(p) for p in self.SECRECY_PATTERNS],
            "authority": [re.compile(p) for p in self.AUTHORITY_PATTERNS],
        }

    def analyze(
        self,
        transcript: str,
        participant_roles: Optional[Dict[str, str]] = None,
        meeting_context: Optional[Dict[str, Any]] = None,
    ) -> ScenarioResult:
        """
        Analyze transcript for social engineering attack scenarios.

        Args:
            transcript: Meeting transcript or conversation text.
            participant_roles: Map of participant names to claimed roles.
            meeting_context: Additional context about the meeting.

        Returns:
            ScenarioResult with detected scenarios and confidence.
        """
        if not transcript:
            return ScenarioResult(
                detected_scenarios=[],
                primary_scenario=None,
                confidence=0.0,
                pattern_matches=[],
                urgency_level=0.0,
                authority_exploitation=0.0,
                details={"error": "No transcript provided"},
            )

        pattern_matches: List[str] = []
        scenario_scores: Dict[AttackScenario, float] = {}

        # Check each pattern category
        ceo_matches = self._count_pattern_matches(transcript, "ceo_fraud")
        vendor_matches = self._count_pattern_matches(transcript, "vendor_fraud")
        it_matches = self._count_pattern_matches(transcript, "it_support")
        hr_matches = self._count_pattern_matches(transcript, "hr_fraud")
        cred_matches = self._count_pattern_matches(transcript, "credentials")

        # Calculate urgency and authority scores
        urgency_matches = self._count_pattern_matches(transcript, "urgency")
        secrecy_matches = self._count_pattern_matches(transcript, "secrecy")
        authority_matches = self._count_pattern_matches(transcript, "authority")

        # Build pattern match list
        all_matches = (
            ceo_matches + vendor_matches + it_matches + hr_matches +
            cred_matches + urgency_matches + secrecy_matches + authority_matches
        )
        pattern_matches = [m[1] for m in all_matches]

        # Score each scenario
        if ceo_matches or authority_matches:
            score = min(100, len(ceo_matches) * 25 + len(authority_matches) * 15)
            if score > 0:
                scenario_scores[AttackScenario.CEO_FRAUD] = score

        if vendor_matches:
            score = min(100, len(vendor_matches) * 30)
            if score > 0:
                scenario_scores[AttackScenario.VENDOR_IMPERSONATION] = score

        if it_matches:
            score = min(100, len(it_matches) * 25)
            if score > 0:
                scenario_scores[AttackScenario.IT_SUPPORT_SCAM] = score

        if hr_matches:
            score = min(100, len(hr_matches) * 30)
            if score > 0:
                scenario_scores[AttackScenario.HR_IMPERSONATION] = score

        if cred_matches:
            score = min(100, len(cred_matches) * 25)
            if score > 0:
                scenario_scores[AttackScenario.CREDENTIAL_HARVESTING] = score

        # Calculate urgency and authority levels
        urgency_level = min(1.0, len(urgency_matches) * 0.2 + len(secrecy_matches) * 0.15)
        authority_exploitation = min(1.0, len(authority_matches) * 0.25)

        # Boost scores based on urgency and authority
        for scenario in scenario_scores:
            boost = 1.0 + (urgency_level * 0.3) + (authority_exploitation * 0.2)
            scenario_scores[scenario] = min(100, scenario_scores[scenario] * boost)

        # Determine detected scenarios and primary
        detected_scenarios = [
            scenario for scenario, score in scenario_scores.items()
            if score > 30
        ]

        primary_scenario = None
        if scenario_scores:
            primary_scenario = max(scenario_scores.keys(), key=lambda s: scenario_scores[s])

        # Calculate overall confidence
        if scenario_scores:
            max_score = max(scenario_scores.values())
            # Boost confidence if multiple indicators present
            indicator_count = sum([
                1 if urgency_matches else 0,
                1 if secrecy_matches else 0,
                1 if authority_matches else 0,
            ])
            confidence = min(100, max_score + (indicator_count * 10))
        else:
            confidence = 0.0

        return ScenarioResult(
            detected_scenarios=detected_scenarios,
            primary_scenario=primary_scenario,
            confidence=confidence,
            pattern_matches=pattern_matches[:20],  # Limit to top 20
            urgency_level=urgency_level,
            authority_exploitation=authority_exploitation,
            details={
                "scenario_scores": {s.value: sc for s, sc in scenario_scores.items()},
                "pattern_categories": {
                    "ceo_fraud": len(ceo_matches),
                    "vendor_fraud": len(vendor_matches),
                    "it_support": len(it_matches),
                    "hr_fraud": len(hr_matches),
                    "credentials": len(cred_matches),
                    "urgency": len(urgency_matches),
                    "secrecy": len(secrecy_matches),
                    "authority": len(authority_matches),
                },
            },
        )

    def _count_pattern_matches(
        self,
        text: str,
        category: str,
    ) -> List[tuple]:
        """
        Count and return pattern matches for a category.

        Returns list of (pattern_index, matched_text) tuples.
        """
        matches = []
        patterns = self._compiled_patterns.get(category, [])

        for i, pattern in enumerate(patterns):
            for match in pattern.finditer(text):
                matches.append((i, match.group()))

        return matches

    def get_scenario_description(self, scenario: AttackScenario) -> str:
        """Get human-readable description of attack scenario."""
        descriptions = {
            AttackScenario.CEO_FRAUD: "CEO/Executive impersonation attempting to authorize fraudulent transactions",
            AttackScenario.CFO_FRAUD: "CFO impersonation targeting financial processes",
            AttackScenario.EXECUTIVE_IMPERSONATION: "General executive impersonation for unauthorized requests",
            AttackScenario.VENDOR_IMPERSONATION: "Vendor/supplier impersonation to redirect payments",
            AttackScenario.INVOICE_FRAUD: "Fraudulent invoice submission for payment",
            AttackScenario.PAYMENT_REDIRECT: "Attempt to redirect legitimate payments to attacker account",
            AttackScenario.IT_SUPPORT_SCAM: "Fake IT support attempting to gain system access",
            AttackScenario.HR_IMPERSONATION: "HR impersonation to steal employee data",
            AttackScenario.PAYROLL_DIVERSION: "Attempt to divert payroll to attacker accounts",
            AttackScenario.CREDENTIAL_HARVESTING: "Phishing attempt to steal login credentials",
            AttackScenario.MFA_BYPASS: "Attempt to bypass multi-factor authentication",
            AttackScenario.EMERGENCY_REQUEST: "Using fake emergency to bypass normal procedures",
            AttackScenario.TIME_PRESSURE: "Creating artificial time pressure to force hasty decisions",
            AttackScenario.UNKNOWN: "Unclassified suspicious behavior pattern",
        }
        return descriptions.get(scenario, "Unknown attack scenario")
