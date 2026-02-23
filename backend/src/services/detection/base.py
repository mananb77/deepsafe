"""
Detection Base Classes and Types

Common interfaces and types for all detection components.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class DetectionType(str, Enum):
    """Types of detection analysis."""

    AUDIO_DEEPFAKE = "audio_deepfake"
    VIDEO_DEEPFAKE = "video_deepfake"
    SOCIAL_ENGINEERING = "social_engineering"


class RiskLevel(str, Enum):
    """Risk level classifications."""

    LOW = "low"  # 0-30%
    MEDIUM = "medium"  # 31-60%
    HIGH = "high"  # 61-85%
    CRITICAL = "critical"  # 86-100%

    @classmethod
    def from_score(cls, score: float) -> "RiskLevel":
        """Get risk level from score (0-100)."""
        if score <= 30:
            return cls.LOW
        elif score <= 60:
            return cls.MEDIUM
        elif score <= 85:
            return cls.HIGH
        else:
            return cls.CRITICAL


@dataclass
class DetectionResult:
    """Result from a detection analysis."""

    detection_type: DetectionType
    is_detected: bool
    confidence: float  # 0-100
    risk_level: RiskLevel
    details: Dict[str, Any] = field(default_factory=dict)
    evidence: Dict[str, Any] = field(default_factory=dict)
    method: str = ""  # Which method/model produced this result
    latency_ms: float = 0.0
    timestamp: datetime = field(default_factory=datetime.utcnow)
    error: Optional[str] = None

    @property
    def is_high_risk(self) -> bool:
        """Check if result indicates high or critical risk."""
        return self.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "detection_type": self.detection_type.value,
            "is_detected": self.is_detected,
            "confidence": self.confidence,
            "risk_level": self.risk_level.value,
            "details": self.details,
            "evidence": self.evidence,
            "method": self.method,
            "latency_ms": self.latency_ms,
            "timestamp": self.timestamp.isoformat(),
            "error": self.error,
        }


@dataclass
class AudioChunk:
    """Audio data chunk for analysis."""

    data: bytes
    sample_rate: int = 16000
    channels: int = 1
    duration_ms: int = 3000
    participant_id: Optional[str] = None
    meeting_id: Optional[str] = None
    timestamp_seconds: float = 0.0
    format: str = "pcm"


@dataclass
class VideoFrame:
    """Video frame for analysis."""

    data: bytes
    width: int
    height: int
    format: str = "rgb24"  # rgb24, bgr24, jpeg, png
    participant_id: Optional[str] = None
    meeting_id: Optional[str] = None
    timestamp_seconds: float = 0.0
    frame_number: int = 0


@dataclass
class TranscriptSegment:
    """Transcript segment for analysis."""

    text: str
    speaker_id: Optional[str] = None
    speaker_name: Optional[str] = None
    start_time: float = 0.0
    end_time: float = 0.0
    confidence: float = 1.0
    language: str = "en"
    meeting_id: Optional[str] = None


@dataclass
class ParticipantContext:
    """Context about a participant for analysis."""

    participant_id: str
    display_name: str
    email: Optional[str] = None
    claimed_identity: Optional[str] = None
    is_verified: bool = False
    trust_level: str = "unverified"
    join_time: Optional[datetime] = None
    device_type: Optional[str] = None
    platform_user_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MeetingContext:
    """Context about a meeting for analysis."""

    meeting_id: str
    title: str
    platform: str
    company_id: str
    host_email: Optional[str] = None
    scheduled_start: Optional[datetime] = None
    actual_start: Optional[datetime] = None
    expected_participants: List[str] = field(default_factory=list)
    calendar_event_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AnalysisContext:
    """Full context for detection analysis."""

    meeting: MeetingContext
    participant: Optional[ParticipantContext] = None
    transcript_history: List[TranscriptSegment] = field(default_factory=list)
    previous_results: List[DetectionResult] = field(default_factory=list)


class BaseDetector(ABC):
    """Abstract base class for all detectors."""

    @abstractmethod
    async def analyze(self, *args, **kwargs) -> DetectionResult:
        """Perform detection analysis."""
        pass

    @abstractmethod
    async def is_available(self) -> bool:
        """Check if detector is available and configured."""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Get detector name."""
        pass


class BaseAPIClient(ABC):
    """Abstract base class for external API clients."""

    @abstractmethod
    async def analyze(self, data: bytes, **kwargs) -> Dict[str, Any]:
        """Send data for analysis."""
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """Check if API is available."""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Get API client name."""
        pass
