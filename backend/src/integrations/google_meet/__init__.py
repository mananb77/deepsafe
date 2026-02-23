"""Google Meet integration module."""

from src.integrations.google_meet.auth.oauth import (
    GoogleOAuth,
    GoogleTokens,
    GoogleUserInfo,
)
from src.integrations.google_meet.bot.meeting_bot import GoogleMeetBot
from src.integrations.google_meet.calendar.sync import (
    GoogleCalendarSync,
    CalendarEvent,
    CalendarWatcher,
)

__all__ = [
    # Auth
    "GoogleOAuth",
    "GoogleTokens",
    "GoogleUserInfo",
    # Bot
    "GoogleMeetBot",
    # Calendar
    "GoogleCalendarSync",
    "CalendarEvent",
    "CalendarWatcher",
]
