"""
Detection Service

Real-time detection of deepfakes and social engineering attacks.

Components:
- Audio deepfake detection (Resemble AI + local fallbacks)
- Video deepfake detection (Sensity/GetReal + local fallbacks)
- Social engineering detection (6-metric scoring)
- Risk score aggregation
"""

from src.services.detection.base import (
    DetectionResult,
    DetectionType,
    RiskLevel,
    AudioChunk,
    VideoFrame,
    BaseDetector,
    BaseAPIClient,
)
from src.services.detection.audio import AudioDeepfakeDetector
from src.services.detection.video import VideoDeepfakeDetector
from src.services.detection.social_engineering import SocialEngineeringDetector
from src.services.detection.risk_aggregator import (
    RiskAggregator,
    AggregatedRiskResult,
    RiskAction,
    ActionType,
)

__all__ = [
    # Base types
    "DetectionResult",
    "DetectionType",
    "RiskLevel",
    "AudioChunk",
    "VideoFrame",
    "BaseDetector",
    "BaseAPIClient",
    # Detectors
    "AudioDeepfakeDetector",
    "VideoDeepfakeDetector",
    "SocialEngineeringDetector",
    # Aggregation
    "RiskAggregator",
    "AggregatedRiskResult",
    "RiskAction",
    "ActionType",
]
