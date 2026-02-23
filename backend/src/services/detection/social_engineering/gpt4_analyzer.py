"""
GPT-4 Semantic Analyzer

Uses GPT-4 for deep semantic analysis of conversation content:
- Intent classification
- Manipulation tactic detection
- Context understanding
- Natural language reasoning
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional
import json

import httpx

from src.shared.config import get_settings


@dataclass
class GPT4AnalysisResult:
    """Result from GPT-4 analysis."""

    is_suspicious: bool
    confidence: float  # 0-100
    intent_classification: str
    manipulation_tactics: List[str]
    risk_assessment: str
    reasoning: str
    recommendations: List[str]
    details: Dict[str, Any]


class GPT4Analyzer:
    """
    Uses GPT-4 for semantic analysis of social engineering attempts.

    Analysis capabilities:
    1. Intent classification - Identify true intent behind requests
    2. Manipulation detection - Recognize psychological tactics
    3. Context analysis - Understand business context
    4. Anomaly detection - Identify unusual requests

    Weight: 20% of total social engineering score
    """

    SYSTEM_PROMPT = """You are a security analyst specializing in detecting social engineering attacks in business communications. Your role is to analyze conversation transcripts and identify potential threats.

Analyze the provided conversation for:
1. Social engineering tactics (urgency, authority, reciprocity, scarcity, social proof)
2. Business Email Compromise (BEC) indicators
3. Fraudulent intent (payment redirect, credential theft, data exfiltration)
4. Manipulation techniques (emotional manipulation, pressure tactics)
5. Impersonation attempts

Respond with a JSON object containing:
{
    "is_suspicious": boolean,
    "confidence": number (0-100),
    "intent_classification": string (legitimate|suspicious|malicious|unknown),
    "manipulation_tactics": [list of identified tactics],
    "risk_assessment": string (low|medium|high|critical),
    "reasoning": string (explanation of analysis),
    "recommendations": [list of recommended actions]
}

Be thorough but avoid false positives. Consider business context and normal communication patterns."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gpt-4-turbo-preview",
        timeout: float = 30.0,
    ):
        settings = get_settings()
        self.api_key = api_key or settings.openai_api_key
        self.model = model
        self.timeout = timeout
        self.base_url = "https://api.openai.com/v1"

    async def analyze(
        self,
        transcript: str,
        meeting_context: Optional[Dict[str, Any]] = None,
        participant_info: Optional[Dict[str, Any]] = None,
    ) -> GPT4AnalysisResult:
        """
        Analyze transcript using GPT-4.

        Args:
            transcript: Conversation transcript.
            meeting_context: Context about the meeting.
            participant_info: Information about participants.

        Returns:
            GPT4AnalysisResult with analysis findings.
        """
        if not self.api_key:
            return GPT4AnalysisResult(
                is_suspicious=False,
                confidence=0.0,
                intent_classification="unknown",
                manipulation_tactics=[],
                risk_assessment="unknown",
                reasoning="API key not configured - GPT-4 analysis skipped",
                recommendations=[],
                details={"error": "API key not configured"},
            )

        if not transcript or len(transcript.strip()) < 10:
            return GPT4AnalysisResult(
                is_suspicious=False,
                confidence=0.0,
                intent_classification="unknown",
                manipulation_tactics=[],
                risk_assessment="low",
                reasoning="Insufficient content for analysis",
                recommendations=[],
                details={"error": "Insufficient content"},
            )

        # Build analysis prompt
        user_prompt = self._build_prompt(transcript, meeting_context, participant_info)

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": self.model,
                        "messages": [
                            {"role": "system", "content": self.SYSTEM_PROMPT},
                            {"role": "user", "content": user_prompt},
                        ],
                        "temperature": 0.3,  # Lower temperature for more consistent analysis
                        "max_tokens": 1000,
                        "response_format": {"type": "json_object"},
                    },
                )

                if response.status_code != 200:
                    return self._create_error_result(f"API error: {response.status_code}")

                result = response.json()
                content = result["choices"][0]["message"]["content"]

                # Parse JSON response
                analysis = json.loads(content)

                return GPT4AnalysisResult(
                    is_suspicious=analysis.get("is_suspicious", False),
                    confidence=float(analysis.get("confidence", 0.0)),
                    intent_classification=analysis.get("intent_classification", "unknown"),
                    manipulation_tactics=analysis.get("manipulation_tactics", []),
                    risk_assessment=analysis.get("risk_assessment", "unknown"),
                    reasoning=analysis.get("reasoning", ""),
                    recommendations=analysis.get("recommendations", []),
                    details={
                        "model": self.model,
                        "tokens_used": result.get("usage", {}),
                    },
                )

        except httpx.TimeoutException:
            return self._create_error_result("API timeout")
        except json.JSONDecodeError as e:
            return self._create_error_result(f"JSON parse error: {e}")
        except Exception as e:
            return self._create_error_result(str(e))

    def _build_prompt(
        self,
        transcript: str,
        meeting_context: Optional[Dict[str, Any]],
        participant_info: Optional[Dict[str, Any]],
    ) -> str:
        """Build the analysis prompt with context."""
        parts = ["Analyze the following conversation for social engineering indicators:"]

        # Add context if available
        if meeting_context:
            parts.append(f"\n\nMeeting Context:")
            if meeting_context.get("title"):
                parts.append(f"- Title: {meeting_context['title']}")
            if meeting_context.get("scheduled"):
                parts.append(f"- Scheduled: {meeting_context['scheduled']}")
            if meeting_context.get("organizer"):
                parts.append(f"- Organizer: {meeting_context['organizer']}")

        if participant_info:
            parts.append(f"\n\nParticipant Information:")
            for name, info in participant_info.items():
                parts.append(f"- {name}: {info}")

        # Add transcript
        parts.append(f"\n\nConversation Transcript:\n```\n{transcript}\n```")

        parts.append("\n\nProvide your analysis in JSON format.")

        return "\n".join(parts)

    def _create_error_result(self, error: str) -> GPT4AnalysisResult:
        """Create an error result."""
        return GPT4AnalysisResult(
            is_suspicious=False,
            confidence=0.0,
            intent_classification="unknown",
            manipulation_tactics=[],
            risk_assessment="unknown",
            reasoning=f"Analysis error: {error}",
            recommendations=["Manual review recommended"],
            details={"error": error},
        )

    async def analyze_batch(
        self,
        transcripts: List[str],
        max_concurrent: int = 3,
    ) -> List[GPT4AnalysisResult]:
        """
        Analyze multiple transcripts with concurrency control.

        Args:
            transcripts: List of transcripts to analyze.
            max_concurrent: Maximum concurrent API calls.

        Returns:
            List of GPT4AnalysisResult.
        """
        import asyncio

        semaphore = asyncio.Semaphore(max_concurrent)

        async def analyze_with_limit(transcript: str) -> GPT4AnalysisResult:
            async with semaphore:
                return await self.analyze(transcript)

        return await asyncio.gather(
            *[analyze_with_limit(t) for t in transcripts]
        )

    def get_manipulation_tactic_description(self, tactic: str) -> str:
        """Get description of a manipulation tactic."""
        descriptions = {
            "urgency": "Creating artificial time pressure to force quick decisions",
            "authority": "Claiming or implying authority to compel compliance",
            "reciprocity": "Creating false sense of obligation",
            "scarcity": "Implying limited availability or time",
            "social_proof": "Claiming others have already complied",
            "liking": "Building false rapport or trust",
            "commitment": "Using prior commitments to manipulate",
            "fear": "Using fear or threats to compel action",
            "greed": "Appealing to desire for gain",
            "helpfulness": "Exploiting desire to be helpful",
        }
        return descriptions.get(tactic.lower(), f"Unknown tactic: {tactic}")
