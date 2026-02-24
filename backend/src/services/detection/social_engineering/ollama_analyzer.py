"""
Ollama Local LLM Analyzer

Uses Ollama (localhost) for social engineering analysis.
Replaces GPT4Analyzer when running in local or hybrid detection mode.

Requires Ollama running separately: ollama pull phi3:mini && ollama serve
"""

import json
import logging
from typing import Any, Dict, List, Optional

import httpx

from src.services.detection.social_engineering.gpt4_analyzer import GPT4AnalysisResult
from src.services.detection.social_engineering.prompts import (
    SYSTEM_PROMPT,
    build_analysis_prompt,
)

logger = logging.getLogger(__name__)


class OllamaAnalyzer:
    """
    Local LLM analyzer using Ollama for social engineering detection.

    Returns GPT4AnalysisResult (same dataclass as GPT4Analyzer)
    so existing calling code works unchanged.
    """

    def __init__(
        self,
        model: str = "phi3:mini",
        ollama_url: str = "http://localhost:11434",
        timeout: float = 60.0,
    ):
        self.model = model
        self.ollama_url = ollama_url.rstrip("/")
        self.timeout = timeout

    async def analyze(
        self,
        transcript: str,
        meeting_context: Optional[Dict[str, Any]] = None,
        participant_info: Optional[Dict[str, Any]] = None,
    ) -> GPT4AnalysisResult:
        """
        Analyze transcript using local Ollama LLM.

        Args:
            transcript: Conversation transcript.
            meeting_context: Context about the meeting.
            participant_info: Information about participants.

        Returns:
            GPT4AnalysisResult with analysis findings.
        """
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

        user_prompt = build_analysis_prompt(transcript, meeting_context, participant_info)

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.ollama_url}/api/chat",
                    json={
                        "model": self.model,
                        "messages": [
                            {"role": "system", "content": SYSTEM_PROMPT},
                            {"role": "user", "content": user_prompt},
                        ],
                        "stream": False,
                        "format": "json",
                    },
                )

                if response.status_code != 200:
                    return self._create_error_result(
                        f"Ollama API error: {response.status_code}"
                    )

                result = response.json()
                content = result.get("message", {}).get("content", "")

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
                        "source": "ollama_local",
                    },
                )

        except httpx.ConnectError:
            return self._create_error_result(
                f"Cannot connect to Ollama at {self.ollama_url}. "
                "Ensure Ollama is running: ollama serve"
            )
        except httpx.TimeoutException:
            return self._create_error_result("Ollama request timeout")
        except json.JSONDecodeError as e:
            return self._create_error_result(f"JSON parse error: {e}")
        except Exception as e:
            return self._create_error_result(str(e))

    async def health_check(self) -> bool:
        """Check if Ollama is running and accessible."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.ollama_url}/api/tags")
                return response.status_code == 200
        except Exception:
            return False

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
