"""
Social Engineering Detector

Main detector combining 6-metric scoring system:
- Scenario detection (20%)
- Keyword analysis (20%)
- GPT-4 semantic analysis (20%)
- Participant validation (15%)
- Metadata analysis (10%)
- Behavioral analysis (15%)

Risk Categories:
- 0-30%: Low - Normal monitoring
- 31-60%: Medium - Monitor closely
- 61-85%: High - Trigger verification
- 86-100%: Critical - Automatic intervention
"""

import asyncio
import time
from typing import Any, Dict, List, Optional, TYPE_CHECKING

from src.services.detection.base import (
    BaseDetector,
    DetectionResult,
    DetectionType,
    RiskLevel,
)
from src.services.detection.social_engineering.scenario_detector import (
    ScenarioDetector,
    AttackScenario,
)
from src.services.detection.social_engineering.keyword_analyzer import KeywordAnalyzer
from src.services.detection.social_engineering.gpt4_analyzer import GPT4Analyzer

if TYPE_CHECKING:
    from src.services.detection.social_engineering.ollama_analyzer import OllamaAnalyzer
from src.services.detection.social_engineering.participant_validator import (
    ParticipantValidator,
    ParticipantProfile,
)
from src.services.detection.social_engineering.metadata_analyzer import (
    MetadataAnalyzer,
    MeetingMetadata,
    ParticipantMetadata,
)
from src.services.detection.social_engineering.behavioral_analyzer import (
    BehavioralAnalyzer,
    ConversationTurn,
)


class SocialEngineeringDetector(BaseDetector):
    """
    Multi-metric social engineering detector.

    Combines 6 detection methods with weighted scoring:
    1. Scenario Detection (20%) - BEC, CEO fraud, vendor fraud patterns
    2. Keyword Analysis (20%) - Suspicious keywords and phrases
    3. GPT-4 Analysis (20%) - Semantic intent classification
    4. Participant Validation (15%) - Identity verification
    5. Metadata Analysis (10%) - Timing, location anomalies
    6. Behavioral Analysis (15%) - Manipulation tactics

    Risk thresholds:
    - Low (0-30%): Normal monitoring
    - Medium (31-60%): Monitor closely
    - High (61-85%): Trigger verification
    - Critical (86-100%): Automatic intervention
    """

    # Detection weights
    WEIGHT_SCENARIO = 0.20
    WEIGHT_KEYWORD = 0.20
    WEIGHT_GPT4 = 0.20
    WEIGHT_PARTICIPANT = 0.15
    WEIGHT_METADATA = 0.10
    WEIGHT_BEHAVIORAL = 0.15

    # Fallback weights (when GPT-4 unavailable)
    FALLBACK_WEIGHT_SCENARIO = 0.25
    FALLBACK_WEIGHT_KEYWORD = 0.25
    FALLBACK_WEIGHT_PARTICIPANT = 0.20
    FALLBACK_WEIGHT_METADATA = 0.12
    FALLBACK_WEIGHT_BEHAVIORAL = 0.18

    # Risk thresholds
    THRESHOLD_LOW = 30.0
    THRESHOLD_MEDIUM = 60.0
    THRESHOLD_HIGH = 85.0

    def __init__(
        self,
        gpt4_analyzer: Optional[GPT4Analyzer] = None,
        company_domain: Optional[str] = None,
        company_timezone: str = "America/New_York",
        enable_gpt4: bool = True,
        local_llm_analyzer: Optional["OllamaAnalyzer"] = None,
        enable_local_llm: bool = False,
    ):
        self.scenario_detector = ScenarioDetector()
        self.keyword_analyzer = KeywordAnalyzer()
        if gpt4_analyzer is not None:
            self.gpt4_analyzer = gpt4_analyzer
        elif enable_gpt4:
            self.gpt4_analyzer = GPT4Analyzer()
        else:
            self.gpt4_analyzer = None
        self.participant_validator = ParticipantValidator(company_domain=company_domain)
        self.metadata_analyzer = MetadataAnalyzer(company_timezone=company_timezone)
        self.behavioral_analyzer = BehavioralAnalyzer()
        self.enable_gpt4 = enable_gpt4
        self.local_llm_analyzer = local_llm_analyzer
        self.enable_local_llm = enable_local_llm

    @property
    def name(self) -> str:
        return "social_engineering_detector"

    async def is_available(self) -> bool:
        """Check if detector is available."""
        return True  # Local analyzers always available

    async def analyze(
        self,
        transcript: str,
        participants: Optional[List[ParticipantProfile]] = None,
        meeting_metadata: Optional[MeetingMetadata] = None,
        participant_metadata: Optional[List[ParticipantMetadata]] = None,
        conversation_turns: Optional[List[ConversationTurn]] = None,
        meeting_context: Optional[Dict[str, Any]] = None,
    ) -> DetectionResult:
        """
        Perform comprehensive social engineering detection.

        Args:
            transcript: Meeting transcript text.
            participants: List of participant profiles.
            meeting_metadata: Meeting metadata for timing/location analysis.
            participant_metadata: Per-participant metadata.
            conversation_turns: Structured conversation for behavioral analysis.
            meeting_context: Additional meeting context.

        Returns:
            DetectionResult with combined 6-metric analysis.
        """
        start_time = time.perf_counter()
        results: Dict[str, Any] = {}
        errors: List[str] = []

        # Run analyses in parallel where possible
        tasks = []

        # Scenario detection (always run)
        tasks.append(self._run_scenario_detection(transcript, meeting_context))

        # Keyword analysis (always run)
        tasks.append(self._run_keyword_analysis(transcript))

        # GPT-4 analysis (if enabled)
        if self.enable_gpt4:
            tasks.append(self._run_gpt4_analysis(transcript, meeting_context, participants))
        elif self.enable_local_llm and self.local_llm_analyzer:
            tasks.append(self._run_local_llm_analysis(transcript, meeting_context, participants))

        # Participant validation (if participants provided)
        if participants:
            tasks.append(self._run_participant_validation(participants, meeting_context))

        # Metadata analysis (if metadata provided)
        if meeting_metadata or participant_metadata:
            tasks.append(
                self._run_metadata_analysis(
                    meeting_metadata, participant_metadata or []
                )
            )

        # Behavioral analysis (if conversation turns provided)
        if conversation_turns:
            tasks.append(self._run_behavioral_analysis(conversation_turns))
        elif transcript:
            # Create simple conversation from transcript
            simple_turns = self._create_conversation_turns(transcript)
            if simple_turns:
                tasks.append(self._run_behavioral_analysis(simple_turns))

        # Execute all tasks
        task_results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results
        for result in task_results:
            if isinstance(result, Exception):
                errors.append(str(result))
            elif isinstance(result, dict):
                results.update(result)

        # Hybrid fallback: if GPT-4 was tried but failed, try local LLM
        if (
            self.enable_gpt4
            and self.enable_local_llm
            and self.local_llm_analyzer
            and not results.get("gpt4_used", False)
        ):
            try:
                local_result = await self._run_local_llm_analysis(
                    transcript, meeting_context, participants
                )
                results.update(local_result)
            except Exception:
                pass

        # Calculate combined score
        combined_score, method_scores, risk_category = self._calculate_combined_score(results)

        # Determine risk level
        risk_level = self._score_to_risk_level(combined_score)

        # Determine if attack detected
        is_detected = combined_score > self.THRESHOLD_LOW

        # Generate recommendations
        recommendations = self._generate_recommendations(
            combined_score, results, risk_category
        )

        latency_ms = (time.perf_counter() - start_time) * 1000

        return DetectionResult(
            detection_type=DetectionType.SOCIAL_ENGINEERING,
            is_detected=is_detected,
            confidence=combined_score,
            risk_level=risk_level,
            details={
                "method_scores": method_scores,
                "risk_category": risk_category,
                "gpt4_used": results.get("gpt4_used", False),
                "detected_scenarios": [
                    s.value for s in results.get("scenario", {}).get("detected", [])
                ],
                "recommendations": recommendations,
            },
            evidence={
                "scenario": results.get("scenario", {}),
                "keywords": results.get("keywords", {}),
                "gpt4": results.get("gpt4", {}),
                "participant": results.get("participant", {}),
                "metadata": results.get("metadata", {}),
                "behavioral": results.get("behavioral", {}),
            },
            method="6_metric_social_engineering",
            latency_ms=latency_ms,
            error="; ".join(errors) if errors else None,
        )

    async def _run_scenario_detection(
        self,
        transcript: str,
        context: Optional[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Run scenario detection."""
        try:
            result = self.scenario_detector.analyze(
                transcript,
                meeting_context=context,
            )

            return {
                "scenario": {
                    "detected": result.detected_scenarios,
                    "primary": result.primary_scenario,
                    "confidence": result.confidence,
                    "urgency_level": result.urgency_level,
                    "authority_exploitation": result.authority_exploitation,
                    "pattern_matches": result.pattern_matches[:10],
                }
            }
        except Exception as e:
            return {"scenario_error": str(e)}

    async def _run_keyword_analysis(
        self,
        transcript: str,
    ) -> Dict[str, Any]:
        """Run keyword analysis."""
        try:
            result = self.keyword_analyzer.analyze(transcript)

            return {
                "keywords": {
                    "is_suspicious": result.is_suspicious,
                    "confidence": result.confidence,
                    "total_risk_score": result.total_risk_score,
                    "category_scores": result.category_scores,
                    "high_risk_phrases": result.high_risk_phrases,
                    "top_matches": [
                        {"keyword": m.keyword, "category": m.category, "weight": m.risk_weight}
                        for m in result.keyword_matches[:10]
                    ],
                }
            }
        except Exception as e:
            return {"keywords_error": str(e)}

    async def _run_gpt4_analysis(
        self,
        transcript: str,
        context: Optional[Dict[str, Any]],
        participants: Optional[List[ParticipantProfile]],
    ) -> Dict[str, Any]:
        """Run GPT-4 analysis."""
        try:
            participant_info = None
            if participants:
                participant_info = {
                    p.name: f"{p.claimed_role or 'Unknown role'} ({p.email or 'No email'})"
                    for p in participants
                }

            result = await self.gpt4_analyzer.analyze(
                transcript,
                meeting_context=context,
                participant_info=participant_info,
            )

            if result.details.get("error"):
                return {
                    "gpt4_error": result.details["error"],
                    "gpt4_used": False,
                }

            return {
                "gpt4": {
                    "is_suspicious": result.is_suspicious,
                    "confidence": result.confidence,
                    "intent": result.intent_classification,
                    "manipulation_tactics": result.manipulation_tactics,
                    "risk_assessment": result.risk_assessment,
                    "reasoning": result.reasoning,
                    "recommendations": result.recommendations,
                },
                "gpt4_used": True,
            }
        except Exception as e:
            return {"gpt4_error": str(e), "gpt4_used": False}

    async def _run_local_llm_analysis(
        self,
        transcript: str,
        context: Optional[Dict[str, Any]],
        participants: Optional[List[ParticipantProfile]],
    ) -> Dict[str, Any]:
        """Run local LLM analysis via Ollama (same result keys as GPT-4)."""
        try:
            participant_info = None
            if participants:
                participant_info = {
                    p.name: f"{p.claimed_role or 'Unknown role'} ({p.email or 'No email'})"
                    for p in participants
                }

            result = await self.local_llm_analyzer.analyze(
                transcript,
                meeting_context=context,
                participant_info=participant_info,
            )

            if result.details.get("error"):
                return {
                    "gpt4_error": result.details["error"],
                    "gpt4_used": False,
                }

            return {
                "gpt4": {
                    "is_suspicious": result.is_suspicious,
                    "confidence": result.confidence,
                    "intent": result.intent_classification,
                    "manipulation_tactics": result.manipulation_tactics,
                    "risk_assessment": result.risk_assessment,
                    "reasoning": result.reasoning,
                    "recommendations": result.recommendations,
                },
                "gpt4_used": True,
            }
        except Exception as e:
            return {"gpt4_error": str(e), "gpt4_used": False}

    async def _run_participant_validation(
        self,
        participants: List[ParticipantProfile],
        context: Optional[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Run participant validation."""
        try:
            result = self.participant_validator.validate(
                participants,
                meeting_context=context,
            )

            return {
                "participant": {
                    "is_suspicious": result.is_suspicious,
                    "confidence": result.confidence,
                    "validation_status": result.validation_status.value,
                    "identity_mismatches": result.identity_mismatches,
                    "behavioral_flags": result.behavioral_flags,
                }
            }
        except Exception as e:
            return {"participant_error": str(e)}

    async def _run_metadata_analysis(
        self,
        meeting_metadata: Optional[MeetingMetadata],
        participant_metadata: List[ParticipantMetadata],
    ) -> Dict[str, Any]:
        """Run metadata analysis."""
        try:
            if not meeting_metadata:
                meeting_metadata = MeetingMetadata(meeting_id="unknown")

            result = self.metadata_analyzer.analyze(
                meeting_metadata,
                participant_metadata,
            )

            return {
                "metadata": {
                    "is_suspicious": result.is_suspicious,
                    "confidence": result.confidence,
                    "timing_anomalies": result.timing_anomalies,
                    "location_anomalies": result.location_anomalies,
                    "device_anomalies": result.device_anomalies,
                    "network_anomalies": result.network_anomalies,
                }
            }
        except Exception as e:
            return {"metadata_error": str(e)}

    async def _run_behavioral_analysis(
        self,
        conversation: List[ConversationTurn],
    ) -> Dict[str, Any]:
        """Run behavioral analysis."""
        try:
            result = self.behavioral_analyzer.analyze(conversation)

            return {
                "behavioral": {
                    "is_suspicious": result.is_suspicious,
                    "confidence": result.confidence,
                    "manipulation_indicators": result.manipulation_indicators,
                    "pressure_tactics": result.pressure_tactics_detected,
                    "evasion_behaviors": result.evasion_behaviors,
                    "flow_anomalies": result.conversation_flow_anomalies,
                    "speaker_dominance": result.speaker_dominance,
                }
            }
        except Exception as e:
            return {"behavioral_error": str(e)}

    def _create_conversation_turns(
        self,
        transcript: str,
    ) -> List[ConversationTurn]:
        """Create conversation turns from plain transcript."""
        turns = []

        # Simple parsing: split by speaker patterns like "John:" or "[John]"
        import re
        pattern = r'(?:^|\n)(?:\[([^\]]+)\]|([^:\n]+)):?\s*'

        parts = re.split(pattern, transcript)

        current_speaker = "Unknown"
        i = 0
        while i < len(parts):
            part = parts[i]
            if part and part.strip():
                # Check if this is a speaker name
                if i + 1 < len(parts) and not parts[i + 1]:
                    current_speaker = part.strip()
                else:
                    turns.append(ConversationTurn(
                        speaker=current_speaker,
                        text=part.strip(),
                    ))
            i += 1

        # If no speaker patterns found, treat whole transcript as one turn
        if not turns and transcript.strip():
            turns.append(ConversationTurn(
                speaker="Unknown",
                text=transcript.strip(),
            ))

        return turns

    def _calculate_combined_score(
        self,
        results: Dict[str, Any],
    ) -> tuple[float, Dict[str, float], str]:
        """
        Calculate combined 6-metric score.

        Returns (combined_score, method_scores, risk_category).
        """
        method_scores: Dict[str, float] = {}
        weighted_sum = 0.0
        total_weight = 0.0

        # Check if GPT-4 was used
        gpt4_used = results.get("gpt4_used", False)

        # Scenario score
        if "scenario" in results:
            scenario = results["scenario"]
            score = scenario.get("confidence", 0.0)

            # Boost if specific attack patterns detected
            if scenario.get("detected"):
                score = max(score, 50.0)

            method_scores["scenario"] = score

            weight = self.FALLBACK_WEIGHT_SCENARIO if not gpt4_used else self.WEIGHT_SCENARIO
            weighted_sum += score * weight
            total_weight += weight

        # Keyword score
        if "keywords" in results:
            keywords = results["keywords"]
            score = keywords.get("confidence", 0.0)
            method_scores["keywords"] = score

            weight = self.FALLBACK_WEIGHT_KEYWORD if not gpt4_used else self.WEIGHT_KEYWORD
            weighted_sum += score * weight
            total_weight += weight

        # GPT-4 score
        if gpt4_used and "gpt4" in results:
            gpt4 = results["gpt4"]
            score = gpt4.get("confidence", 0.0)

            # Map risk assessment to score boost
            risk_map = {"critical": 90, "high": 75, "medium": 50, "low": 25}
            if gpt4.get("risk_assessment") in risk_map:
                score = max(score, risk_map[gpt4["risk_assessment"]])

            method_scores["gpt4"] = score
            weighted_sum += score * self.WEIGHT_GPT4
            total_weight += self.WEIGHT_GPT4

        # Participant score
        if "participant" in results:
            participant = results["participant"]
            score = participant.get("confidence", 0.0)

            # Status-based boost
            status = participant.get("validation_status", "")
            if status == "impersonation_suspected":
                score = max(score, 80.0)
            elif status == "suspicious":
                score = max(score, 60.0)

            method_scores["participant"] = score

            weight = self.FALLBACK_WEIGHT_PARTICIPANT if not gpt4_used else self.WEIGHT_PARTICIPANT
            weighted_sum += score * weight
            total_weight += weight

        # Metadata score
        if "metadata" in results:
            metadata = results["metadata"]
            score = metadata.get("confidence", 0.0)
            method_scores["metadata"] = score

            weight = self.FALLBACK_WEIGHT_METADATA if not gpt4_used else self.WEIGHT_METADATA
            weighted_sum += score * weight
            total_weight += weight

        # Behavioral score
        if "behavioral" in results:
            behavioral = results["behavioral"]
            score = behavioral.get("confidence", 0.0)
            method_scores["behavioral"] = score

            weight = self.FALLBACK_WEIGHT_BEHAVIORAL if not gpt4_used else self.WEIGHT_BEHAVIORAL
            weighted_sum += score * weight
            total_weight += weight

        # Calculate combined score
        if total_weight > 0:
            combined = weighted_sum / total_weight
        else:
            combined = 0.0

        # Boost if multiple high-confidence methods agree
        high_confidence_count = sum(1 for s in method_scores.values() if s > 60)
        if high_confidence_count >= 3:
            combined = min(100, combined * 1.2)
        elif high_confidence_count >= 2:
            combined = min(100, combined * 1.1)

        # Determine risk category
        if combined >= self.THRESHOLD_HIGH:
            risk_category = "critical"
        elif combined >= self.THRESHOLD_MEDIUM:
            risk_category = "high"
        elif combined >= self.THRESHOLD_LOW:
            risk_category = "medium"
        else:
            risk_category = "low"

        return min(max(combined, 0.0), 100.0), method_scores, risk_category

    def _score_to_risk_level(self, score: float) -> RiskLevel:
        """Convert score to RiskLevel enum."""
        if score >= self.THRESHOLD_HIGH:
            return RiskLevel.CRITICAL
        elif score >= self.THRESHOLD_MEDIUM:
            return RiskLevel.HIGH
        elif score >= self.THRESHOLD_LOW:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW

    def _generate_recommendations(
        self,
        score: float,
        results: Dict[str, Any],
        risk_category: str,
    ) -> List[str]:
        """Generate recommendations based on analysis results."""
        recommendations = []

        if risk_category == "critical":
            recommendations.extend([
                "CRITICAL: Immediate intervention recommended",
                "Halt any financial transactions",
                "Trigger multi-channel verification",
                "Notify security team immediately",
            ])
        elif risk_category == "high":
            recommendations.extend([
                "HIGH RISK: Trigger identity verification",
                "Request callback verification for any financial requests",
                "Monitor conversation closely",
            ])
        elif risk_category == "medium":
            recommendations.extend([
                "MEDIUM RISK: Monitor conversation closely",
                "Verify participant identities through secondary channel",
            ])
        else:
            recommendations.append("LOW RISK: Continue normal monitoring")

        # Scenario-specific recommendations
        scenario = results.get("scenario", {})
        if scenario.get("primary"):
            primary = scenario["primary"]
            if primary == AttackScenario.CEO_FRAUD:
                recommendations.append(
                    "Verify request directly with claimed executive through known contact"
                )
            elif primary == AttackScenario.VENDOR_IMPERSONATION:
                recommendations.append(
                    "Verify bank account changes through established vendor contact"
                )
            elif primary == AttackScenario.IT_SUPPORT_SCAM:
                recommendations.append(
                    "Verify IT request through internal IT helpdesk"
                )

        # Participant-specific recommendations
        participant = results.get("participant", {})
        if participant.get("identity_mismatches"):
            recommendations.append(
                "Identity mismatches detected - verify participant through secondary channel"
            )

        return recommendations[:8]  # Limit recommendations

    async def close(self) -> None:
        """Clean up resources."""
        pass  # No persistent connections to close
