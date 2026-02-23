"""
Behavioral Analyzer

Analyzes conversation behavioral patterns for manipulation indicators:
- Communication style changes
- Pressure tactics
- Deflection behaviors
- Manipulation techniques
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple
import re


@dataclass
class ConversationTurn:
    """A single turn in a conversation."""

    speaker: str
    text: str
    timestamp: Optional[float] = None
    duration_seconds: Optional[float] = None


@dataclass
class BehavioralAnalysisResult:
    """Result from behavioral analysis."""

    is_suspicious: bool
    confidence: float  # 0-100
    manipulation_indicators: List[str]
    pressure_tactics_detected: List[str]
    evasion_behaviors: List[str]
    conversation_flow_anomalies: List[str]
    speaker_dominance: Dict[str, float]
    details: Dict[str, Any]


class BehavioralAnalyzer:
    """
    Analyzes behavioral patterns in conversations for manipulation indicators.

    Detection areas:
    1. Manipulation techniques (reciprocity, commitment, authority)
    2. Pressure tactics (urgency, scarcity, fear)
    3. Evasion behaviors (deflection, topic changes, vague answers)
    4. Conversation flow (dominance, interruptions, topic steering)

    Weight: 15% of total social engineering score
    """

    # Manipulation technique patterns
    RECIPROCITY_PATTERNS = [
        r"(?i)i('ve|\s+have)\s+done\s+.{0,30}\bfor\s+you",
        r"(?i)i('m|\s+am)\s+doing\s+you\s+a\s+favor",
        r"(?i)remember\s+when\s+i\s+.{0,30}helped",
        r"(?i)you\s+owe\s+me",
        r"(?i)after\s+all\s+i('ve|\s+have)\s+done",
    ]

    COMMITMENT_PATTERNS = [
        r"(?i)you\s+(said|agreed|promised|committed)",
        r"(?i)we\s+(already\s+)?(discussed|agreed|decided)",
        r"(?i)as\s+(we|you)\s+agreed",
        r"(?i)you\s+can'?t\s+back\s+out",
        r"(?i)you\s+gave\s+your\s+word",
    ]

    SOCIAL_PROOF_PATTERNS = [
        r"(?i)everyone\s+(else\s+)?(does|has|is)",
        r"(?i)all\s+(the\s+)?other\s+(companies|people|departments)",
        r"(?i)(john|mary|bob)\s+already\s+(approved|did|agreed)",
        r"(?i)this\s+is\s+(standard|normal|common)\s+practice",
        r"(?i)other\s+(ceos|executives|managers)\s+(always|usually)",
    ]

    AUTHORITY_PATTERNS = [
        r"(?i)i('m|\s+am)\s+(the|your)\s+(ceo|boss|manager|director)",
        r"(?i)this\s+comes\s+from\s+(the\s+)?(top|board|executive)",
        r"(?i)(direct|specific)\s+(order|instruction|request)",
        r"(?i)i\s+(have\s+)?(the\s+)?authority\s+to",
        r"(?i)don'?t\s+question\s+(me|this)",
    ]

    SCARCITY_PATTERNS = [
        r"(?i)limited\s+(time|offer|opportunity)",
        r"(?i)only\s+(one|last)\s+(chance|opportunity)",
        r"(?i)won'?t\s+(be\s+)?(available|possible)\s+(again|later)",
        r"(?i)now\s+or\s+never",
        r"(?i)expires?\s+(today|soon|shortly)",
    ]

    FEAR_PATTERNS = [
        r"(?i)you('ll|\s+will)\s+(lose|miss|fail)",
        r"(?i)(serious|severe)\s+consequences",
        r"(?i)your\s+(job|position|career)\s+(is|could\s+be)",
        r"(?i)i('ll|\s+will)\s+have\s+to\s+(report|escalate|tell)",
        r"(?i)(legal|regulatory)\s+(action|consequences|issues)",
    ]

    # Evasion behavior patterns
    DEFLECTION_PATTERNS = [
        r"(?i)let'?s\s+(not\s+)?talk\s+about\s+that",
        r"(?i)that'?s\s+not\s+(important|relevant)",
        r"(?i)we\s+can\s+discuss\s+that\s+later",
        r"(?i)don'?t\s+worry\s+about\s+(that|it)",
        r"(?i)that'?s\s+above\s+your\s+(pay\s+grade|level)",
    ]

    VAGUE_RESPONSE_PATTERNS = [
        r"(?i)i('ll|\s+will)\s+explain\s+later",
        r"(?i)it'?s\s+complicated",
        r"(?i)you\s+don'?t\s+need\s+to\s+know",
        r"(?i)trust\s+me\s+on\s+this",
        r"(?i)just\s+do\s+(it|this|what\s+i\s+say)",
    ]

    def __init__(self):
        # Compile patterns
        self._manipulation_patterns = {
            "reciprocity": [re.compile(p) for p in self.RECIPROCITY_PATTERNS],
            "commitment": [re.compile(p) for p in self.COMMITMENT_PATTERNS],
            "social_proof": [re.compile(p) for p in self.SOCIAL_PROOF_PATTERNS],
            "authority": [re.compile(p) for p in self.AUTHORITY_PATTERNS],
            "scarcity": [re.compile(p) for p in self.SCARCITY_PATTERNS],
            "fear": [re.compile(p) for p in self.FEAR_PATTERNS],
        }

        self._evasion_patterns = {
            "deflection": [re.compile(p) for p in self.DEFLECTION_PATTERNS],
            "vague": [re.compile(p) for p in self.VAGUE_RESPONSE_PATTERNS],
        }

    def analyze(
        self,
        conversation: List[ConversationTurn],
        target_speaker: Optional[str] = None,
    ) -> BehavioralAnalysisResult:
        """
        Analyze conversation for behavioral indicators.

        Args:
            conversation: List of conversation turns.
            target_speaker: Speaker suspected of manipulation (optional).

        Returns:
            BehavioralAnalysisResult with findings.
        """
        if not conversation:
            return BehavioralAnalysisResult(
                is_suspicious=False,
                confidence=0.0,
                manipulation_indicators=[],
                pressure_tactics_detected=[],
                evasion_behaviors=[],
                conversation_flow_anomalies=[],
                speaker_dominance={},
                details={"error": "No conversation provided"},
            )

        # Concatenate all text for pattern analysis
        full_text = " ".join(turn.text for turn in conversation)

        # Find manipulation indicators
        manipulation = self._find_manipulation_indicators(full_text)

        # Find pressure tactics
        pressure = self._find_pressure_tactics(full_text)

        # Find evasion behaviors
        evasion = self._find_evasion_behaviors(full_text)

        # Analyze conversation flow
        flow_anomalies, dominance = self._analyze_conversation_flow(conversation)

        # Per-speaker analysis if target specified
        speaker_scores: Dict[str, float] = {}
        if target_speaker:
            target_turns = [t for t in conversation if t.speaker == target_speaker]
            target_text = " ".join(t.text for t in target_turns)

            target_manipulation = self._find_manipulation_indicators(target_text)
            target_pressure = self._find_pressure_tactics(target_text)

            speaker_scores[target_speaker] = min(100, (
                len(target_manipulation) * 20 +
                len(target_pressure) * 25
            ))

        # Calculate overall score
        score = self._calculate_score(
            manipulation, pressure, evasion, flow_anomalies, dominance
        )

        is_suspicious = (
            score > 40 or
            len(manipulation) >= 2 or
            len(pressure) >= 2
        )

        return BehavioralAnalysisResult(
            is_suspicious=is_suspicious,
            confidence=score,
            manipulation_indicators=manipulation,
            pressure_tactics_detected=pressure,
            evasion_behaviors=evasion,
            conversation_flow_anomalies=flow_anomalies,
            speaker_dominance=dominance,
            details={
                "turns_analyzed": len(conversation),
                "speakers": list(set(t.speaker for t in conversation)),
                "speaker_scores": speaker_scores,
                "manipulation_categories": self._categorize_indicators(manipulation),
            },
        )

    def _find_manipulation_indicators(self, text: str) -> List[str]:
        """Find manipulation technique indicators."""
        indicators = []

        for category, patterns in self._manipulation_patterns.items():
            for pattern in patterns:
                matches = pattern.findall(text)
                if matches:
                    for match in matches:
                        indicators.append(f"{category}: {match}")

        return indicators[:15]  # Limit output

    def _find_pressure_tactics(self, text: str) -> List[str]:
        """Find pressure tactic indicators."""
        tactics = []

        # Check urgency patterns (from manipulation patterns)
        urgency_patterns = [
            r"(?i)(urgent|immediately|asap|right\s+now|today)",
            r"(?i)(deadline|time\s+sensitive|critical|emergency)",
            r"(?i)(can'?t|cannot)\s+wait",
            r"(?i)must\s+(be\s+)?(done|completed|sent)\s+(now|today)",
        ]

        for pattern in urgency_patterns:
            matches = re.findall(pattern, text)
            if matches:
                for match in matches:
                    match_str = match if isinstance(match, str) else " ".join(match)
                    tactics.append(f"urgency: {match_str}")

        # Add scarcity and fear from manipulation patterns
        for category in ["scarcity", "fear"]:
            patterns = self._manipulation_patterns.get(category, [])
            for pattern in patterns:
                matches = pattern.findall(text)
                if matches:
                    for match in matches:
                        tactics.append(f"{category}: {match}")

        return tactics[:10]

    def _find_evasion_behaviors(self, text: str) -> List[str]:
        """Find evasion behavior indicators."""
        behaviors = []

        for category, patterns in self._evasion_patterns.items():
            for pattern in patterns:
                matches = pattern.findall(text)
                if matches:
                    for match in matches:
                        behaviors.append(f"{category}: {match}")

        return behaviors[:10]

    def _analyze_conversation_flow(
        self,
        conversation: List[ConversationTurn],
    ) -> Tuple[List[str], Dict[str, float]]:
        """
        Analyze conversation flow patterns.

        Returns (anomalies, speaker_dominance).
        """
        anomalies = []
        dominance: Dict[str, float] = {}

        if not conversation:
            return anomalies, dominance

        # Calculate speaker dominance
        speaker_words: Dict[str, int] = {}
        total_words = 0

        for turn in conversation:
            word_count = len(turn.text.split())
            speaker_words[turn.speaker] = speaker_words.get(turn.speaker, 0) + word_count
            total_words += word_count

        if total_words > 0:
            for speaker, words in speaker_words.items():
                dominance[speaker] = (words / total_words) * 100

        # Check for extreme dominance
        for speaker, pct in dominance.items():
            if pct > 80:
                anomalies.append(f"Speaker {speaker} dominates conversation ({pct:.0f}%)")
            elif pct > 70:
                anomalies.append(f"Speaker {speaker} is highly dominant ({pct:.0f}%)")

        # Check for rapid-fire responses (potential scripted behavior)
        if len(conversation) > 3:
            short_gaps = 0
            for i in range(1, len(conversation)):
                if (conversation[i].timestamp and conversation[i-1].timestamp and
                    conversation[i].timestamp - conversation[i-1].timestamp < 1.0):
                    short_gaps += 1

            if short_gaps > len(conversation) * 0.5:
                anomalies.append("Unusually rapid conversation exchanges")

        # Check for topic steering (frequent introduction of new topics)
        topic_shifts = self._detect_topic_shifts(conversation)
        if topic_shifts > len(conversation) * 0.3:
            anomalies.append(f"Frequent topic shifts ({topic_shifts} detected)")

        return anomalies, dominance

    def _detect_topic_shifts(self, conversation: List[ConversationTurn]) -> int:
        """Detect number of abrupt topic shifts."""
        # Simple heuristic: topic shift indicators
        shift_patterns = [
            r"(?i)^(anyway|by\s+the\s+way|speaking\s+of|also|one\s+more\s+thing)",
            r"(?i)let'?s\s+(talk|discuss)\s+about",
            r"(?i)changing\s+the\s+(subject|topic)",
        ]

        shifts = 0
        for turn in conversation:
            for pattern in shift_patterns:
                if re.search(pattern, turn.text):
                    shifts += 1
                    break

        return shifts

    def _calculate_score(
        self,
        manipulation: List[str],
        pressure: List[str],
        evasion: List[str],
        flow_anomalies: List[str],
        dominance: Dict[str, float],
    ) -> float:
        """Calculate overall behavioral score."""
        score = 0.0

        # Manipulation indicators (35%)
        manipulation_score = min(100, len(manipulation) * 20)
        score += manipulation_score * 0.35

        # Pressure tactics (30%)
        pressure_score = min(100, len(pressure) * 25)
        score += pressure_score * 0.30

        # Evasion behaviors (20%)
        evasion_score = min(100, len(evasion) * 25)
        score += evasion_score * 0.20

        # Flow anomalies (15%)
        flow_score = min(100, len(flow_anomalies) * 30)
        score += flow_score * 0.15

        # Boost if extreme dominance
        max_dominance = max(dominance.values()) if dominance else 0
        if max_dominance > 80:
            score = min(100, score * 1.1)

        return min(max(score, 0.0), 100.0)

    def _categorize_indicators(self, indicators: List[str]) -> Dict[str, int]:
        """Categorize manipulation indicators by type."""
        categories: Dict[str, int] = {}

        for indicator in indicators:
            category = indicator.split(":")[0] if ":" in indicator else "other"
            categories[category] = categories.get(category, 0) + 1

        return categories
