"""
Zoom Integration

DeepSafe integration with Zoom using:
- Zoom OAuth 2.0 for authentication
- Zoom Meeting SDK for bot participation
- Zoom Webhooks for event handling
- Zoom Apps SDK for in-meeting overlays

Components:
- ZoomOAuth: OAuth 2.0 authentication flow
- ZoomMeetingBot: Meeting SDK bot implementation
- ZoomWebhookHandler: Webhook event processing
"""

from src.integrations.zoom.auth.oauth import (
    ZoomOAuth,
    ZoomTokens,
    ZoomUserInfo,
)
from src.integrations.zoom.bot.meeting_bot import ZoomMeetingBot
from src.integrations.zoom.webhooks.handler import (
    ZoomWebhookHandler,
    ZoomWebhookEvent,
    ZoomWebhookPayload,
)

__all__ = [
    # Auth
    "ZoomOAuth",
    "ZoomTokens",
    "ZoomUserInfo",
    # Bot
    "ZoomMeetingBot",
    # Webhooks
    "ZoomWebhookHandler",
    "ZoomWebhookEvent",
    "ZoomWebhookPayload",
]
