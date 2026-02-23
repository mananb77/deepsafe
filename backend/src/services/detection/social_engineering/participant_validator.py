"""
Participant Validator

Validates meeting participant identities and claims:
- Email domain verification
- Role/title verification against company directory
- Historical communication pattern matching
- Voice/video consistency checks
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Set
import re


class ValidationStatus(Enum):
    """Participant validation status."""

    VERIFIED = "verified"
    UNVERIFIED = "unverified"
    SUSPICIOUS = "suspicious"
    IMPERSONATION_SUSPECTED = "impersonation_suspected"
    UNKNOWN = "unknown"


@dataclass
class ParticipantProfile:
    """Profile information for a participant."""

    name: str
    email: Optional[str] = None
    claimed_role: Optional[str] = None
    claimed_company: Optional[str] = None
    phone: Optional[str] = None
    join_method: Optional[str] = None  # calendar, link, dial-in
    is_external: bool = False


@dataclass
class ParticipantValidationResult:
    """Result from participant validation."""

    is_suspicious: bool
    confidence: float  # 0-100
    validation_status: ValidationStatus
    identity_mismatches: List[str]
    domain_analysis: Dict[str, Any]
    behavioral_flags: List[str]
    details: Dict[str, Any]


class ParticipantValidator:
    """
    Validates meeting participant identities and claims.

    Validation checks:
    1. Email domain verification
    2. Name-email consistency
    3. Role claim verification
    4. External participant analysis
    5. Join method anomalies

    Weight: 15% of total social engineering score
    """

    # Common legitimate email providers (less suspicious for external)
    PUBLIC_EMAIL_PROVIDERS = {
        "gmail.com", "yahoo.com", "outlook.com", "hotmail.com",
        "live.com", "icloud.com", "aol.com", "protonmail.com",
        "mail.com", "zoho.com", "yandex.com",
    }

    # Suspicious patterns in email addresses
    SUSPICIOUS_EMAIL_PATTERNS = [
        r"ceo[._-]?.*@",  # ceo.name@
        r"chief[._-]?.*@",
        r"president[._-]?.*@",
        r"exec[._-]?.*@",
        r"support[._-]?.*@",
        r"helpdesk[._-]?.*@",
        r"it[._-]?.*@",
        r"admin[._-]?.*@",
        r"\d{4,}@",  # Many numbers in local part
    ]

    # Suspicious patterns in names
    SUSPICIOUS_NAME_PATTERNS = [
        r"^(CEO|CFO|CTO|COO|VP|Director|President)\s",  # Title prefix
        r"\s(CEO|CFO|CTO|COO)\s*$",  # Title suffix
    ]

    # Executive titles that require extra verification
    EXECUTIVE_TITLES = {
        "ceo", "cfo", "cto", "coo", "ciso", "cio",
        "president", "chairman", "director", "vp",
        "vice president", "chief", "executive",
    }

    def __init__(
        self,
        company_domain: Optional[str] = None,
        known_employees: Optional[Dict[str, Dict[str, Any]]] = None,
    ):
        """
        Initialize validator.

        Args:
            company_domain: Primary company email domain.
            known_employees: Dict of known employee emails to profile data.
        """
        self.company_domain = company_domain
        self.known_employees = known_employees or {}
        self._suspicious_patterns = [
            re.compile(p, re.IGNORECASE) for p in self.SUSPICIOUS_EMAIL_PATTERNS
        ]
        self._suspicious_name_patterns = [
            re.compile(p, re.IGNORECASE) for p in self.SUSPICIOUS_NAME_PATTERNS
        ]

    def validate(
        self,
        participants: List[ParticipantProfile],
        meeting_context: Optional[Dict[str, Any]] = None,
    ) -> ParticipantValidationResult:
        """
        Validate meeting participants.

        Args:
            participants: List of participant profiles.
            meeting_context: Context about the meeting.

        Returns:
            ParticipantValidationResult with findings.
        """
        if not participants:
            return ParticipantValidationResult(
                is_suspicious=False,
                confidence=0.0,
                validation_status=ValidationStatus.UNKNOWN,
                identity_mismatches=[],
                domain_analysis={},
                behavioral_flags=[],
                details={"error": "No participants provided"},
            )

        identity_mismatches: List[str] = []
        behavioral_flags: List[str] = []
        domain_info: Dict[str, Any] = {}
        suspicion_score = 0.0

        for participant in participants:
            # Validate each participant
            result = self._validate_participant(participant)

            identity_mismatches.extend(result["mismatches"])
            behavioral_flags.extend(result["flags"])

            if result["domain_info"]:
                domain_info[participant.email or participant.name] = result["domain_info"]

            suspicion_score = max(suspicion_score, result["score"])

        # Check for executive claims from external participants
        exec_external = self._check_external_executive_claims(participants)
        if exec_external:
            identity_mismatches.extend(exec_external)
            suspicion_score = max(suspicion_score, 70.0)

        # Check participant count anomalies
        if meeting_context:
            count_flags = self._check_participant_count(participants, meeting_context)
            behavioral_flags.extend(count_flags)

        # Determine overall status
        if suspicion_score > 70:
            status = ValidationStatus.IMPERSONATION_SUSPECTED
        elif suspicion_score > 40:
            status = ValidationStatus.SUSPICIOUS
        elif identity_mismatches:
            status = ValidationStatus.UNVERIFIED
        else:
            status = ValidationStatus.VERIFIED

        confidence = suspicion_score
        is_suspicious = suspicion_score > 30 or len(identity_mismatches) > 1

        return ParticipantValidationResult(
            is_suspicious=is_suspicious,
            confidence=confidence,
            validation_status=status,
            identity_mismatches=identity_mismatches,
            domain_analysis=domain_info,
            behavioral_flags=behavioral_flags,
            details={
                "participants_checked": len(participants),
                "external_count": sum(1 for p in participants if p.is_external),
                "executive_claims": sum(
                    1 for p in participants
                    if p.claimed_role and any(t in p.claimed_role.lower() for t in self.EXECUTIVE_TITLES)
                ),
            },
        )

    def _validate_participant(
        self,
        participant: ParticipantProfile,
    ) -> Dict[str, Any]:
        """Validate a single participant."""
        mismatches: List[str] = []
        flags: List[str] = []
        domain_info: Dict[str, Any] = {}
        score = 0.0

        email = participant.email
        name = participant.name

        # Email validation
        if email:
            domain = email.split("@")[1].lower() if "@" in email else None

            if domain:
                domain_info["domain"] = domain

                # Check if external
                if self.company_domain and domain != self.company_domain:
                    participant.is_external = True
                    domain_info["is_external"] = True

                    # External with public email claiming internal role
                    if domain in self.PUBLIC_EMAIL_PROVIDERS:
                        if participant.claimed_role:
                            role_lower = participant.claimed_role.lower()
                            if any(t in role_lower for t in self.EXECUTIVE_TITLES):
                                mismatches.append(
                                    f"Executive role claimed from public email: {email}"
                                )
                                score = max(score, 80.0)

                # Check for suspicious email patterns
                for pattern in self._suspicious_patterns:
                    if pattern.search(email):
                        flags.append(f"Suspicious email pattern: {email}")
                        score = max(score, 40.0)

            # Name-email consistency
            if name and email:
                name_parts = name.lower().split()
                local_part = email.split("@")[0].lower()

                # Check if any name part appears in email
                name_in_email = any(
                    part in local_part for part in name_parts if len(part) > 2
                )
                if not name_in_email and len(name_parts) >= 2:
                    flags.append(f"Name '{name}' doesn't match email local part")
                    score = max(score, 25.0)

        # Name validation
        if name:
            for pattern in self._suspicious_name_patterns:
                if pattern.search(name):
                    flags.append(f"Suspicious name format: {name}")
                    score = max(score, 35.0)

        # Known employee verification
        if email and email.lower() in self.known_employees:
            known = self.known_employees[email.lower()]

            # Verify name matches
            if known.get("name") and name:
                if known["name"].lower() != name.lower():
                    mismatches.append(
                        f"Name mismatch: claimed '{name}', expected '{known['name']}'"
                    )
                    score = max(score, 60.0)

            # Verify role matches
            if known.get("role") and participant.claimed_role:
                if known["role"].lower() != participant.claimed_role.lower():
                    mismatches.append(
                        f"Role mismatch: claimed '{participant.claimed_role}', expected '{known['role']}'"
                    )
                    score = max(score, 50.0)

        # Join method analysis
        if participant.join_method:
            if participant.join_method == "dial-in":
                # Dial-in from unknown numbers is higher risk
                flags.append("Joined via dial-in (identity less verifiable)")
                score = max(score, 20.0)

        return {
            "mismatches": mismatches,
            "flags": flags,
            "domain_info": domain_info,
            "score": score,
        }

    def _check_external_executive_claims(
        self,
        participants: List[ParticipantProfile],
    ) -> List[str]:
        """Check for external participants claiming executive roles."""
        issues = []

        for p in participants:
            if p.is_external and p.claimed_role:
                role_lower = p.claimed_role.lower()

                # Check for executive title claims
                for title in self.EXECUTIVE_TITLES:
                    if title in role_lower:
                        issues.append(
                            f"External participant '{p.name}' claims {p.claimed_role}"
                        )
                        break

        return issues

    def _check_participant_count(
        self,
        participants: List[ParticipantProfile],
        context: Dict[str, Any],
    ) -> List[str]:
        """Check for participant count anomalies."""
        flags = []

        expected_count = context.get("expected_participants")
        if expected_count and len(participants) != expected_count:
            if len(participants) > expected_count:
                flags.append(
                    f"More participants than expected ({len(participants)} vs {expected_count})"
                )

        # Check if meeting has unexpected external participants
        meeting_type = context.get("meeting_type", "")
        if "internal" in meeting_type.lower():
            external_count = sum(1 for p in participants if p.is_external)
            if external_count > 0:
                flags.append(
                    f"Internal meeting has {external_count} external participant(s)"
                )

        return flags

    def add_known_employee(
        self,
        email: str,
        profile: Dict[str, Any],
    ) -> None:
        """Add or update known employee profile."""
        self.known_employees[email.lower()] = profile
