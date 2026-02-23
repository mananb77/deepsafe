"""
Platform Integrations

Meeting platform integrations for DeepSafe:
- Zoom (Meeting SDK bot)
- Google Meet (Puppeteer bot)
- Microsoft Teams (Bot Framework) - Post-MVP

Each integration implements the common IMeetingBot interface for:
- Audio/video stream capture
- Participant management
- Trust badge display
- Alert overlay system
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

# Zoom integration
from src.integrations.zoom import (
    ZoomOAuth,
    ZoomTokens,
    ZoomUserInfo,
    ZoomMeetingBot,
    ZoomWebhookHandler,
    ZoomWebhookEvent,
    ZoomWebhookPayload,
)

# Google Meet integration
from src.integrations.google_meet import (
    GoogleOAuth,
    GoogleTokens,
    GoogleUserInfo,
    GoogleMeetBot,
    GoogleCalendarSync,
    CalendarEvent,
    CalendarWatcher,
)

__all__ = [
    # Enums
    "MeetingPlatform",
    "BotStatus",
    "StreamType",
    "AlertSeverity",
    "TrustLevel",
    # Data types
    "BotCredentials",
    "MeetingInfo",
    "ParticipantInfo",
    "AudioFrame",
    "VideoFrame",
    "TrustBadge",
    "AlertConfig",
    "OverlayConfig",
    # Interface
    "IMeetingBot",
    # Zoom
    "ZoomOAuth",
    "ZoomTokens",
    "ZoomUserInfo",
    "ZoomMeetingBot",
    "ZoomWebhookHandler",
    "ZoomWebhookEvent",
    "ZoomWebhookPayload",
    # Google Meet
    "GoogleOAuth",
    "GoogleTokens",
    "GoogleUserInfo",
    "GoogleMeetBot",
    "GoogleCalendarSync",
    "CalendarEvent",
    "CalendarWatcher",
]
