"""
Metadata Analyzer

Analyzes meeting metadata for anomalies:
- Meeting timing (off-hours, rushed scheduling)
- Location/timezone mismatches
- Device fingerprints
- Network characteristics
"""

from dataclasses import dataclass
from datetime import datetime, time, timedelta
from typing import Any, Dict, List, Optional, Set
from zoneinfo import ZoneInfo


@dataclass
class MeetingMetadata:
    """Metadata about a meeting."""

    meeting_id: str
    scheduled_time: Optional[datetime] = None
    actual_start_time: Optional[datetime] = None
    organizer_timezone: Optional[str] = None
    duration_minutes: Optional[int] = None
    scheduled_lead_time_hours: Optional[float] = None  # How far in advance scheduled
    is_recurring: bool = False
    platform: Optional[str] = None
    invite_method: Optional[str] = None  # calendar, link, direct


@dataclass
class ParticipantMetadata:
    """Metadata about a participant."""

    participant_id: str
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    timezone: Optional[str] = None
    device_type: Optional[str] = None  # desktop, mobile, phone
    join_time: Optional[datetime] = None
    location_country: Optional[str] = None
    vpn_detected: bool = False


@dataclass
class MetadataAnalysisResult:
    """Result from metadata analysis."""

    is_suspicious: bool
    confidence: float  # 0-100
    timing_anomalies: List[str]
    location_anomalies: List[str]
    device_anomalies: List[str]
    network_anomalies: List[str]
    details: Dict[str, Any]


class MetadataAnalyzer:
    """
    Analyzes meeting metadata for social engineering indicators.

    Analysis areas:
    1. Timing - Off-hours meetings, rushed scheduling
    2. Location - Geographic anomalies, timezone mismatches
    3. Device - Unusual clients, fingerprint changes
    4. Network - VPN usage, IP reputation

    Weight: 10% of total social engineering score
    """

    # Business hours (default)
    BUSINESS_HOURS_START = time(8, 0)
    BUSINESS_HOURS_END = time(18, 0)

    # Suspicious scheduling patterns
    MIN_LEAD_TIME_HOURS = 1.0  # Meetings scheduled less than 1 hour ahead
    SUSPICIOUS_LEAD_TIME_HOURS = 0.5  # Very suspicious if under 30 minutes

    # High-risk countries (for context, not discrimination)
    HIGH_RISK_LOCATIONS: Set[str] = {
        # Countries commonly associated with scam operations
        # This should be configurable per organization
    }

    def __init__(
        self,
        company_timezone: str = "America/New_York",
        company_country: str = "US",
        business_hours_start: time = None,
        business_hours_end: time = None,
    ):
        self.company_timezone = company_timezone
        self.company_country = company_country
        self.business_hours_start = business_hours_start or self.BUSINESS_HOURS_START
        self.business_hours_end = business_hours_end or self.BUSINESS_HOURS_END

    def analyze(
        self,
        meeting_metadata: MeetingMetadata,
        participant_metadata: List[ParticipantMetadata],
        historical_context: Optional[Dict[str, Any]] = None,
    ) -> MetadataAnalysisResult:
        """
        Analyze meeting metadata for anomalies.

        Args:
            meeting_metadata: Metadata about the meeting.
            participant_metadata: Metadata for each participant.
            historical_context: Historical patterns for comparison.

        Returns:
            MetadataAnalysisResult with findings.
        """
        timing_anomalies: List[str] = []
        location_anomalies: List[str] = []
        device_anomalies: List[str] = []
        network_anomalies: List[str] = []

        suspicion_score = 0.0

        # Analyze timing
        timing_result = self._analyze_timing(meeting_metadata)
        timing_anomalies.extend(timing_result["anomalies"])
        suspicion_score = max(suspicion_score, timing_result["score"])

        # Analyze participant locations
        location_result = self._analyze_locations(participant_metadata)
        location_anomalies.extend(location_result["anomalies"])
        suspicion_score = max(suspicion_score, location_result["score"])

        # Analyze devices
        device_result = self._analyze_devices(participant_metadata)
        device_anomalies.extend(device_result["anomalies"])
        suspicion_score = max(suspicion_score, device_result["score"])

        # Analyze network characteristics
        network_result = self._analyze_network(participant_metadata)
        network_anomalies.extend(network_result["anomalies"])
        suspicion_score = max(suspicion_score, network_result["score"])

        # Historical comparison if available
        if historical_context:
            historical_result = self._compare_historical(
                meeting_metadata, participant_metadata, historical_context
            )
            timing_anomalies.extend(historical_result.get("timing", []))
            device_anomalies.extend(historical_result.get("device", []))
            suspicion_score = max(suspicion_score, historical_result.get("score", 0))

        confidence = suspicion_score
        is_suspicious = (
            suspicion_score > 40 or
            len(timing_anomalies) + len(location_anomalies) + len(network_anomalies) > 2
        )

        return MetadataAnalysisResult(
            is_suspicious=is_suspicious,
            confidence=confidence,
            timing_anomalies=timing_anomalies,
            location_anomalies=location_anomalies,
            device_anomalies=device_anomalies,
            network_anomalies=network_anomalies,
            details={
                "meeting_id": meeting_metadata.meeting_id,
                "participant_count": len(participant_metadata),
                "off_hours": any("off-hours" in a.lower() for a in timing_anomalies),
                "vpn_users": sum(1 for p in participant_metadata if p.vpn_detected),
            },
        )

    def _analyze_timing(
        self,
        metadata: MeetingMetadata,
    ) -> Dict[str, Any]:
        """Analyze meeting timing for anomalies."""
        anomalies = []
        score = 0.0

        # Check scheduled time
        if metadata.scheduled_time:
            try:
                tz = ZoneInfo(self.company_timezone)
                local_time = metadata.scheduled_time.astimezone(tz).time()

                # Off-hours meeting
                if local_time < self.business_hours_start or local_time > self.business_hours_end:
                    anomalies.append(
                        f"Meeting scheduled outside business hours ({local_time.strftime('%H:%M')})"
                    )
                    score = max(score, 30.0)

                # Weekend meeting
                if metadata.scheduled_time.weekday() >= 5:
                    anomalies.append("Meeting scheduled on weekend")
                    score = max(score, 25.0)
            except Exception:
                pass

        # Check lead time
        if metadata.scheduled_lead_time_hours is not None:
            if metadata.scheduled_lead_time_hours < self.SUSPICIOUS_LEAD_TIME_HOURS:
                anomalies.append(
                    f"Meeting scheduled with very short notice ({metadata.scheduled_lead_time_hours:.1f} hours)"
                )
                score = max(score, 50.0)
            elif metadata.scheduled_lead_time_hours < self.MIN_LEAD_TIME_HOURS:
                anomalies.append(
                    f"Meeting scheduled with short notice ({metadata.scheduled_lead_time_hours:.1f} hours)"
                )
                score = max(score, 35.0)

        # Check for unusual duration
        if metadata.duration_minutes:
            if metadata.duration_minutes > 240:  # 4+ hours
                anomalies.append(
                    f"Unusually long meeting duration ({metadata.duration_minutes} minutes)"
                )
                score = max(score, 20.0)

        return {"anomalies": anomalies, "score": score}

    def _analyze_locations(
        self,
        participants: List[ParticipantMetadata],
    ) -> Dict[str, Any]:
        """Analyze participant locations for anomalies."""
        anomalies = []
        score = 0.0

        countries = set()
        timezones = set()

        for p in participants:
            if p.location_country:
                countries.add(p.location_country)

                # Check against high-risk locations
                if p.location_country in self.HIGH_RISK_LOCATIONS:
                    anomalies.append(
                        f"Participant from high-risk location: {p.location_country}"
                    )
                    score = max(score, 40.0)

            if p.timezone:
                timezones.add(p.timezone)

        # Check for timezone mismatches
        if len(timezones) > 3:
            anomalies.append(f"Participants from {len(timezones)} different timezones")
            score = max(score, 25.0)

        # Check for unusual geographic spread
        if len(countries) > 4:
            anomalies.append(
                f"Participants from {len(countries)} different countries"
            )
            score = max(score, 20.0)

        return {"anomalies": anomalies, "score": score}

    def _analyze_devices(
        self,
        participants: List[ParticipantMetadata],
    ) -> Dict[str, Any]:
        """Analyze participant devices for anomalies."""
        anomalies = []
        score = 0.0

        for p in participants:
            # Check user agent for suspicious patterns
            if p.user_agent:
                ua_lower = p.user_agent.lower()

                # Very old browsers
                if any(old in ua_lower for old in ["msie 6", "msie 7", "chrome/4."]):
                    anomalies.append(
                        f"Participant using very old browser: {p.participant_id}"
                    )
                    score = max(score, 30.0)

                # Automation tools
                if any(bot in ua_lower for bot in ["selenium", "puppeteer", "headless"]):
                    anomalies.append(
                        f"Participant possibly using automation: {p.participant_id}"
                    )
                    score = max(score, 50.0)

            # Phone dial-in for sensitive meetings
            if p.device_type == "phone":
                anomalies.append(
                    f"Participant joined via phone dial-in: {p.participant_id}"
                )
                score = max(score, 20.0)

        return {"anomalies": anomalies, "score": score}

    def _analyze_network(
        self,
        participants: List[ParticipantMetadata],
    ) -> Dict[str, Any]:
        """Analyze network characteristics for anomalies."""
        anomalies = []
        score = 0.0

        vpn_count = 0

        for p in participants:
            if p.vpn_detected:
                vpn_count += 1

        # Multiple VPN users might indicate coordinated anonymization
        if vpn_count > 1:
            anomalies.append(f"{vpn_count} participants using VPN")
            score = max(score, 30.0)

        # If all external participants use VPN
        if vpn_count == len(participants) and len(participants) > 1:
            anomalies.append("All participants using VPN (possible anonymization)")
            score = max(score, 45.0)

        return {"anomalies": anomalies, "score": score}

    def _compare_historical(
        self,
        meeting_metadata: MeetingMetadata,
        participant_metadata: List[ParticipantMetadata],
        historical: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Compare against historical patterns."""
        result: Dict[str, List[str]] = {"timing": [], "device": []}
        score = 0.0

        # Check if meeting timing deviates from historical pattern
        typical_hours = historical.get("typical_meeting_hours")
        if typical_hours and meeting_metadata.scheduled_time:
            meeting_hour = meeting_metadata.scheduled_time.hour
            if meeting_hour < typical_hours.get("start", 0) or meeting_hour > typical_hours.get("end", 24):
                result["timing"].append(
                    "Meeting time deviates from historical pattern"
                )
                score = max(score, 25.0)

        # Check for new devices/locations for known participants
        known_participants = historical.get("known_participants", {})
        for p in participant_metadata:
            if p.participant_id in known_participants:
                known = known_participants[p.participant_id]

                # New device
                if p.user_agent and known.get("user_agents"):
                    if p.user_agent not in known["user_agents"]:
                        result["device"].append(
                            f"New device for known participant: {p.participant_id}"
                        )
                        score = max(score, 35.0)

                # New location
                if p.location_country and known.get("locations"):
                    if p.location_country not in known["locations"]:
                        result["device"].append(
                            f"New location for known participant: {p.participant_id}"
                        )
                        score = max(score, 40.0)

        result["score"] = score
        return result
