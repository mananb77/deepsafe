"""
Shared prompts for social engineering analysis.

Used by both GPT4Analyzer (OpenAI API) and OllamaAnalyzer (local LLM).
"""

from typing import Any, Dict, List, Optional

from src.services.detection.social_engineering.participant_validator import ParticipantProfile


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


def build_analysis_prompt(
    transcript: str,
    meeting_context: Optional[Dict[str, Any]] = None,
    participant_info: Optional[Dict[str, Any]] = None,
) -> str:
    """Build the analysis prompt with context."""
    parts = ["Analyze the following conversation for social engineering indicators:"]

    # Add context if available
    if meeting_context:
        parts.append("\n\nMeeting Context:")
        if meeting_context.get("title"):
            parts.append(f"- Title: {meeting_context['title']}")
        if meeting_context.get("scheduled"):
            parts.append(f"- Scheduled: {meeting_context['scheduled']}")
        if meeting_context.get("organizer"):
            parts.append(f"- Organizer: {meeting_context['organizer']}")

    if participant_info:
        parts.append("\n\nParticipant Information:")
        for name, info in participant_info.items():
            parts.append(f"- {name}: {info}")

    # Add transcript
    parts.append(f"\n\nConversation Transcript:\n```\n{transcript}\n```")

    parts.append("\n\nProvide your analysis in JSON format.")

    return "\n".join(parts)


def build_participant_info(
    participants: Optional[List[ParticipantProfile]],
) -> Optional[Dict[str, str]]:
    """Build participant info dict from ParticipantProfile list."""
    if not participants:
        return None
    return {
        p.name: f"{p.claimed_role or 'Unknown role'} ({p.email or 'No email'})"
        for p in participants
    }
