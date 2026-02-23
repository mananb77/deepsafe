"""
Social Engineering Detection Module

6-metric scoring system:
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

from src.services.detection.social_engineering.detector import SocialEngineeringDetector
from src.services.detection.social_engineering.scenario_detector import (
    ScenarioDetector,
    ScenarioResult,
    AttackScenario,
)
from src.services.detection.social_engineering.keyword_analyzer import (
    KeywordAnalyzer,
    KeywordAnalysisResult,
)
from src.services.detection.social_engineering.gpt4_analyzer import (
    GPT4Analyzer,
    GPT4AnalysisResult,
)
from src.services.detection.social_engineering.participant_validator import (
    ParticipantValidator,
    ParticipantValidationResult,
)
from src.services.detection.social_engineering.metadata_analyzer import (
    MetadataAnalyzer,
    MetadataAnalysisResult,
)
from src.services.detection.social_engineering.behavioral_analyzer import (
    BehavioralAnalyzer,
    BehavioralAnalysisResult,
)

__all__ = [
    "SocialEngineeringDetector",
    "ScenarioDetector",
    "ScenarioResult",
    "AttackScenario",
    "KeywordAnalyzer",
    "KeywordAnalysisResult",
    "GPT4Analyzer",
    "GPT4AnalysisResult",
    "ParticipantValidator",
    "ParticipantValidationResult",
    "MetadataAnalyzer",
    "MetadataAnalysisResult",
    "BehavioralAnalyzer",
    "BehavioralAnalysisResult",
]
