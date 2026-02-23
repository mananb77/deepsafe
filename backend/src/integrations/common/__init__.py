"""
Common types and interfaces for platform integrations.
"""

from src.integrations.common.types import (
    MeetingPlatform,
    BotStatus,
    StreamType,
    AlertSeverity,
    TrustLevel,
    BotCredentials,
    MeetingInfo,
    ParticipantInfo,
    AudioFrame,
    VideoFrame,
    TrustBadge,
    AlertConfig,
    OverlayConfig,
)
from src.integrations.common.interface import IMeetingBot

__all__ = [
    "MeetingPlatform",
    "BotStatus",
    "StreamType",
    "AlertSeverity",
    "TrustLevel",
    "BotCredentials",
    "MeetingInfo",
    "ParticipantInfo",
    "AudioFrame",
    "VideoFrame",
    "TrustBadge",
    "AlertConfig",
    "OverlayConfig",
    "IMeetingBot",
]
