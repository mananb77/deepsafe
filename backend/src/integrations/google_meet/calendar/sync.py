"""
Google Calendar Sync

Syncs Google Calendar events with Google Meet links for:
- Automatic bot scheduling
- Meeting metadata extraction
- Real-time event updates via push notifications

Google Calendar API Documentation:
https://developers.google.com/calendar/api/v3/reference
"""

import asyncio
import logging
import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set
import uuid

import httpx

from src.integrations.google_meet.auth.oauth import GoogleOAuth, GoogleTokens
from src.shared.config import get_settings


logger = logging.getLogger(__name__)


class EventStatus(str, Enum):
    """Calendar event status."""
    CONFIRMED = "confirmed"
    TENTATIVE = "tentative"
    CANCELLED = "cancelled"


class ResponseStatus(str, Enum):
    """Attendee response status."""
    NEEDS_ACTION = "needsAction"
    DECLINED = "declined"
    TENTATIVE = "tentative"
    ACCEPTED = "accepted"


@dataclass
class EventAttendee:
    """Calendar event attendee."""
    email: str
    display_name: str = ""
    response_status: ResponseStatus = ResponseStatus.NEEDS_ACTION
    is_organizer: bool = False
    is_optional: bool = False
    is_self: bool = False

    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> "EventAttendee":
        """Create from API response."""
        return cls(
            email=data.get("email", ""),
            display_name=data.get("displayName", ""),
            response_status=ResponseStatus(data.get("responseStatus", "needsAction")),
            is_organizer=data.get("organizer", False),
            is_optional=data.get("optional", False),
            is_self=data.get("self", False),
        )


@dataclass
class ConferenceData:
    """Google Meet conference data."""
    conference_id: str
    conference_solution: str  # "hangoutsMeet", "addOn"
    entry_point_uri: str  # The meet.google.com URL
    entry_point_type: str = "video"  # "video", "phone", "more"
    meeting_code: str = ""
    passcode: str = ""
    pin: str = ""

    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> Optional["ConferenceData"]:
        """Create from API response."""
        if not data:
            return None

        entry_points = data.get("entryPoints", [])
        video_entry = next(
            (ep for ep in entry_points if ep.get("entryPointType") == "video"),
            None
        )

        if not video_entry:
            return None

        uri = video_entry.get("uri", "")

        # Extract meeting code from URI
        meeting_code = ""
        if "meet.google.com/" in uri:
            meeting_code = uri.split("meet.google.com/")[-1].split("?")[0]

        return cls(
            conference_id=data.get("conferenceId", ""),
            conference_solution=data.get("conferenceSolution", {}).get("key", {}).get("type", ""),
            entry_point_uri=uri,
            entry_point_type=video_entry.get("entryPointType", "video"),
            meeting_code=meeting_code,
            passcode=video_entry.get("passcode", ""),
            pin=video_entry.get("pin", ""),
        )


@dataclass
class CalendarEvent:
    """
    Google Calendar event with Google Meet details.

    Contains all event metadata needed for bot scheduling.
    """
    event_id: str
    calendar_id: str
    summary: str  # Event title
    description: str = ""
    location: str = ""

    # Time
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    timezone: str = "UTC"
    is_all_day: bool = False

    # Status
    status: EventStatus = EventStatus.CONFIRMED
    visibility: str = "default"  # "default", "public", "private"

    # Organizer
    organizer_email: str = ""
    organizer_name: str = ""

    # Attendees
    attendees: List[EventAttendee] = field(default_factory=list)

    # Conference (Google Meet)
    conference_data: Optional[ConferenceData] = None

    # Recurrence
    recurring_event_id: Optional[str] = None
    recurrence: List[str] = field(default_factory=list)  # RRULE strings

    # Timestamps
    created: Optional[datetime] = None
    updated: Optional[datetime] = None

    # URLs
    html_link: str = ""

    @property
    def has_google_meet(self) -> bool:
        """Check if event has Google Meet attached."""
        return self.conference_data is not None

    @property
    def meet_link(self) -> Optional[str]:
        """Get Google Meet link if available."""
        if self.conference_data:
            return self.conference_data.entry_point_uri
        return None

    @property
    def meet_code(self) -> Optional[str]:
        """Get Google Meet code if available."""
        if self.conference_data:
            return self.conference_data.meeting_code
        return None

    @property
    def duration_minutes(self) -> int:
        """Get event duration in minutes."""
        if self.start_time and self.end_time:
            delta = self.end_time - self.start_time
            return int(delta.total_seconds() / 60)
        return 0

    @property
    def is_active(self) -> bool:
        """Check if event is currently happening."""
        if not self.start_time or not self.end_time:
            return False
        now = datetime.utcnow()
        return self.start_time <= now <= self.end_time

    @property
    def is_upcoming(self) -> bool:
        """Check if event is in the future."""
        if not self.start_time:
            return False
        return self.start_time > datetime.utcnow()

    @classmethod
    def from_api_response(
        cls,
        data: Dict[str, Any],
        calendar_id: str = "primary",
    ) -> "CalendarEvent":
        """Create from Google Calendar API response."""

        # Parse start/end times
        start_data = data.get("start", {})
        end_data = data.get("end", {})

        is_all_day = "date" in start_data

        if is_all_day:
            start_time = datetime.fromisoformat(start_data.get("date", ""))
            end_time = datetime.fromisoformat(end_data.get("date", ""))
        else:
            start_str = start_data.get("dateTime", "")
            end_str = end_data.get("dateTime", "")
            start_time = datetime.fromisoformat(start_str.replace("Z", "+00:00")) if start_str else None
            end_time = datetime.fromisoformat(end_str.replace("Z", "+00:00")) if end_str else None

        timezone = start_data.get("timeZone", "UTC")

        # Parse attendees
        attendees = [
            EventAttendee.from_api_response(a)
            for a in data.get("attendees", [])
        ]

        # Parse organizer
        organizer = data.get("organizer", {})

        # Parse timestamps
        created_str = data.get("created", "")
        updated_str = data.get("updated", "")

        created = datetime.fromisoformat(created_str.replace("Z", "+00:00")) if created_str else None
        updated = datetime.fromisoformat(updated_str.replace("Z", "+00:00")) if updated_str else None

        return cls(
            event_id=data.get("id", ""),
            calendar_id=calendar_id,
            summary=data.get("summary", ""),
            description=data.get("description", ""),
            location=data.get("location", ""),
            start_time=start_time,
            end_time=end_time,
            timezone=timezone,
            is_all_day=is_all_day,
            status=EventStatus(data.get("status", "confirmed")),
            visibility=data.get("visibility", "default"),
            organizer_email=organizer.get("email", ""),
            organizer_name=organizer.get("displayName", ""),
            attendees=attendees,
            conference_data=ConferenceData.from_api_response(
                data.get("conferenceData")
            ),
            recurring_event_id=data.get("recurringEventId"),
            recurrence=data.get("recurrence", []),
            created=created,
            updated=updated,
            html_link=data.get("htmlLink", ""),
        )


# Type for event callbacks
EventCallback = Callable[[CalendarEvent, str], None]  # event, change_type


class GoogleCalendarSync:
    """
    Google Calendar synchronization client.

    Fetches events and watches for changes.

    Usage:
        sync = GoogleCalendarSync(tokens)

        # Get events with Google Meet
        events = await sync.get_events_with_meet(
            time_min=datetime.utcnow(),
            time_max=datetime.utcnow() + timedelta(days=7),
        )

        # Watch for changes
        await sync.start_watching(calendar_id="primary")
    """

    CALENDAR_API_BASE = "https://www.googleapis.com/calendar/v3"

    def __init__(
        self,
        tokens: GoogleTokens,
        oauth: Optional[GoogleOAuth] = None,
    ):
        """
        Initialize calendar sync.

        Args:
            tokens: Google OAuth tokens.
            oauth: GoogleOAuth client for token refresh.
        """
        self._tokens = tokens
        self._oauth = oauth or GoogleOAuth()

        self._http_client: Optional[httpx.AsyncClient] = None

        # Sync state
        self._sync_tokens: Dict[str, str] = {}  # calendar_id -> sync_token
        self._watched_calendars: Set[str] = set()

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._http_client is None or self._http_client.is_closed:
            self._http_client = httpx.AsyncClient(timeout=30.0)
        return self._http_client

    async def _get_headers(self) -> Dict[str, str]:
        """Get auth headers, refreshing token if needed."""
        if self._tokens.is_expired and self._tokens.refresh_token:
            self._tokens = await self._oauth.refresh_tokens(
                self._tokens.refresh_token
            )

        return {
            "Authorization": f"Bearer {self._tokens.access_token}",
            "Content-Type": "application/json",
        }

    async def close(self) -> None:
        """Close HTTP client."""
        if self._http_client and not self._http_client.is_closed:
            await self._http_client.aclose()

    # ==================== Calendar List ====================

    async def get_calendars(self) -> List[Dict[str, Any]]:
        """
        Get list of user's calendars.

        Returns:
            List of calendar metadata.
        """
        client = await self._get_client()
        headers = await self._get_headers()

        response = await client.get(
            f"{self.CALENDAR_API_BASE}/users/me/calendarList",
            headers=headers,
        )
        response.raise_for_status()

        data = response.json()
        return data.get("items", [])

    async def get_primary_calendar(self) -> Dict[str, Any]:
        """Get primary calendar metadata."""
        client = await self._get_client()
        headers = await self._get_headers()

        response = await client.get(
            f"{self.CALENDAR_API_BASE}/calendars/primary",
            headers=headers,
        )
        response.raise_for_status()

        return response.json()

    # ==================== Events ====================

    async def get_events(
        self,
        calendar_id: str = "primary",
        time_min: Optional[datetime] = None,
        time_max: Optional[datetime] = None,
        max_results: int = 100,
        single_events: bool = True,
        order_by: str = "startTime",
        q: Optional[str] = None,
    ) -> List[CalendarEvent]:
        """
        Get calendar events.

        Args:
            calendar_id: Calendar ID (default "primary").
            time_min: Minimum start time.
            time_max: Maximum end time.
            max_results: Maximum number of results.
            single_events: Expand recurring events.
            order_by: Sort order ("startTime" or "updated").
            q: Search query.

        Returns:
            List of CalendarEvent objects.
        """
        client = await self._get_client()
        headers = await self._get_headers()

        params: Dict[str, Any] = {
            "maxResults": max_results,
            "singleEvents": str(single_events).lower(),
        }

        if single_events:
            params["orderBy"] = order_by

        if time_min:
            params["timeMin"] = time_min.isoformat() + "Z"
        if time_max:
            params["timeMax"] = time_max.isoformat() + "Z"
        if q:
            params["q"] = q

        events = []
        page_token = None

        while True:
            if page_token:
                params["pageToken"] = page_token

            response = await client.get(
                f"{self.CALENDAR_API_BASE}/calendars/{calendar_id}/events",
                headers=headers,
                params=params,
            )
            response.raise_for_status()

            data = response.json()

            for item in data.get("items", []):
                events.append(
                    CalendarEvent.from_api_response(item, calendar_id)
                )

            # Store sync token for incremental sync
            if "nextSyncToken" in data:
                self._sync_tokens[calendar_id] = data["nextSyncToken"]

            page_token = data.get("nextPageToken")
            if not page_token:
                break

        return events

    async def get_events_with_meet(
        self,
        calendar_id: str = "primary",
        time_min: Optional[datetime] = None,
        time_max: Optional[datetime] = None,
        max_results: int = 100,
    ) -> List[CalendarEvent]:
        """
        Get calendar events that have Google Meet attached.

        Args:
            calendar_id: Calendar ID.
            time_min: Minimum start time.
            time_max: Maximum end time.
            max_results: Maximum number of results.

        Returns:
            List of CalendarEvent objects with Google Meet.
        """
        events = await self.get_events(
            calendar_id=calendar_id,
            time_min=time_min,
            time_max=time_max,
            max_results=max_results,
        )

        return [e for e in events if e.has_google_meet]

    async def get_event(
        self,
        event_id: str,
        calendar_id: str = "primary",
    ) -> CalendarEvent:
        """
        Get a specific event by ID.

        Args:
            event_id: Event ID.
            calendar_id: Calendar ID.

        Returns:
            CalendarEvent object.
        """
        client = await self._get_client()
        headers = await self._get_headers()

        response = await client.get(
            f"{self.CALENDAR_API_BASE}/calendars/{calendar_id}/events/{event_id}",
            headers=headers,
        )
        response.raise_for_status()

        return CalendarEvent.from_api_response(response.json(), calendar_id)

    async def get_upcoming_meet_events(
        self,
        calendar_ids: Optional[List[str]] = None,
        hours_ahead: int = 24,
    ) -> List[CalendarEvent]:
        """
        Get upcoming events with Google Meet in the next N hours.

        Useful for scheduling bot joins.

        Args:
            calendar_ids: List of calendar IDs (default ["primary"]).
            hours_ahead: Hours to look ahead.

        Returns:
            List of upcoming CalendarEvent objects with Google Meet.
        """
        calendar_ids = calendar_ids or ["primary"]
        now = datetime.utcnow()
        time_max = now + timedelta(hours=hours_ahead)

        all_events = []

        for calendar_id in calendar_ids:
            events = await self.get_events_with_meet(
                calendar_id=calendar_id,
                time_min=now,
                time_max=time_max,
            )
            all_events.extend(events)

        # Sort by start time
        all_events.sort(key=lambda e: e.start_time or datetime.max)

        return all_events

    # ==================== Incremental Sync ====================

    async def sync_events(
        self,
        calendar_id: str = "primary",
    ) -> List[tuple[CalendarEvent, str]]:
        """
        Perform incremental sync to get changed events.

        Returns:
            List of (event, change_type) tuples.
            change_type is "created", "updated", or "deleted".
        """
        client = await self._get_client()
        headers = await self._get_headers()

        sync_token = self._sync_tokens.get(calendar_id)

        if not sync_token:
            # Full sync first
            events = await self.get_events(calendar_id=calendar_id)
            return [(e, "created") for e in events]

        params = {"syncToken": sync_token}
        changes = []

        while True:
            response = await client.get(
                f"{self.CALENDAR_API_BASE}/calendars/{calendar_id}/events",
                headers=headers,
                params=params,
            )

            if response.status_code == 410:
                # Sync token invalid, need full sync
                del self._sync_tokens[calendar_id]
                events = await self.get_events(calendar_id=calendar_id)
                return [(e, "created") for e in events]

            response.raise_for_status()
            data = response.json()

            for item in data.get("items", []):
                event = CalendarEvent.from_api_response(item, calendar_id)

                if item.get("status") == "cancelled":
                    change_type = "deleted"
                elif self._is_new_event(event):
                    change_type = "created"
                else:
                    change_type = "updated"

                changes.append((event, change_type))

            if "nextSyncToken" in data:
                self._sync_tokens[calendar_id] = data["nextSyncToken"]

            page_token = data.get("nextPageToken")
            if not page_token:
                break
            params["pageToken"] = page_token

        return changes

    def _is_new_event(self, event: CalendarEvent) -> bool:
        """Check if event is newly created (created == updated)."""
        if not event.created or not event.updated:
            return False
        # Allow 1 second tolerance
        delta = abs((event.updated - event.created).total_seconds())
        return delta < 1

    # ==================== Push Notifications ====================

    async def watch_calendar(
        self,
        calendar_id: str = "primary",
        webhook_url: str = "",
        expiration_hours: int = 24,
    ) -> Dict[str, Any]:
        """
        Set up push notifications for calendar changes.

        Requires a publicly accessible webhook URL.

        Args:
            calendar_id: Calendar to watch.
            webhook_url: URL to receive notifications.
            expiration_hours: Watch expiration time.

        Returns:
            Watch channel info.
        """
        if not webhook_url:
            settings = get_settings()
            webhook_url = settings.google.calendar_webhook_url

        if not webhook_url:
            raise ValueError("Webhook URL required for calendar watching")

        client = await self._get_client()
        headers = await self._get_headers()

        channel_id = str(uuid.uuid4())
        expiration_ms = int(
            (datetime.utcnow() + timedelta(hours=expiration_hours)).timestamp() * 1000
        )

        body = {
            "id": channel_id,
            "type": "web_hook",
            "address": webhook_url,
            "expiration": expiration_ms,
        }

        response = await client.post(
            f"{self.CALENDAR_API_BASE}/calendars/{calendar_id}/events/watch",
            headers=headers,
            json=body,
        )
        response.raise_for_status()

        self._watched_calendars.add(calendar_id)

        return response.json()

    async def stop_watching(
        self,
        channel_id: str,
        resource_id: str,
    ) -> bool:
        """
        Stop receiving push notifications.

        Args:
            channel_id: Channel ID from watch response.
            resource_id: Resource ID from watch response.

        Returns:
            True if stopped successfully.
        """
        client = await self._get_client()
        headers = await self._get_headers()

        try:
            response = await client.post(
                f"{self.CALENDAR_API_BASE}/channels/stop",
                headers=headers,
                json={
                    "id": channel_id,
                    "resourceId": resource_id,
                },
            )
            return response.status_code == 204
        except httpx.HTTPError:
            return False


class CalendarWatcher:
    """
    Calendar watcher for real-time event updates.

    Combines push notifications with incremental sync.

    Usage:
        watcher = CalendarWatcher(sync)

        @watcher.on_event
        async def handle_event(event: CalendarEvent, change_type: str):
            if event.has_google_meet:
                schedule_bot(event)

        await watcher.start()
    """

    def __init__(
        self,
        sync: GoogleCalendarSync,
        webhook_url: Optional[str] = None,
        poll_interval: int = 300,  # 5 minutes fallback
    ):
        """
        Initialize watcher.

        Args:
            sync: GoogleCalendarSync instance.
            webhook_url: URL for push notifications.
            poll_interval: Fallback polling interval in seconds.
        """
        self._sync = sync
        self._webhook_url = webhook_url
        self._poll_interval = poll_interval

        self._callbacks: List[EventCallback] = []
        self._is_running = False
        self._poll_task: Optional[asyncio.Task] = None
        self._watch_info: Dict[str, Dict[str, str]] = {}  # calendar_id -> watch info

    def on_event(self, callback: EventCallback) -> EventCallback:
        """Register event callback."""
        self._callbacks.append(callback)
        return callback

    async def start(
        self,
        calendar_ids: Optional[List[str]] = None,
        use_push: bool = True,
    ) -> None:
        """
        Start watching calendars.

        Args:
            calendar_ids: Calendars to watch.
            use_push: Use push notifications (requires webhook).
        """
        calendar_ids = calendar_ids or ["primary"]
        self._is_running = True

        # Set up push notifications if available
        if use_push and self._webhook_url:
            for calendar_id in calendar_ids:
                try:
                    watch_info = await self._sync.watch_calendar(
                        calendar_id=calendar_id,
                        webhook_url=self._webhook_url,
                    )
                    self._watch_info[calendar_id] = {
                        "channel_id": watch_info.get("id", ""),
                        "resource_id": watch_info.get("resourceId", ""),
                    }
                    logger.info(f"Started watching calendar: {calendar_id}")
                except Exception as e:
                    logger.warning(f"Failed to set up push for {calendar_id}: {e}")

        # Start fallback polling
        self._poll_task = asyncio.create_task(
            self._poll_loop(calendar_ids)
        )

    async def stop(self) -> None:
        """Stop watching calendars."""
        self._is_running = False

        # Stop push notifications
        for calendar_id, info in self._watch_info.items():
            try:
                await self._sync.stop_watching(
                    channel_id=info["channel_id"],
                    resource_id=info["resource_id"],
                )
            except Exception as e:
                logger.warning(f"Failed to stop watch for {calendar_id}: {e}")

        self._watch_info.clear()

        # Cancel polling
        if self._poll_task:
            self._poll_task.cancel()
            try:
                await self._poll_task
            except asyncio.CancelledError:
                pass
            self._poll_task = None

    async def handle_webhook(
        self,
        headers: Dict[str, str],
        body: bytes,
    ) -> None:
        """
        Handle incoming webhook notification.

        Call this from your webhook endpoint.

        Args:
            headers: Request headers.
            body: Request body.
        """
        channel_id = headers.get("x-goog-channel-id", "")
        resource_state = headers.get("x-goog-resource-state", "")

        if resource_state == "sync":
            # Initial sync confirmation
            logger.debug(f"Received sync notification for channel: {channel_id}")
            return

        if resource_state in ("exists", "update"):
            # Calendar changed, perform incremental sync
            # Find calendar ID for this channel
            calendar_id = None
            for cal_id, info in self._watch_info.items():
                if info.get("channel_id") == channel_id:
                    calendar_id = cal_id
                    break

            if calendar_id:
                await self._sync_and_notify(calendar_id)

    async def _poll_loop(self, calendar_ids: List[str]) -> None:
        """Fallback polling loop."""
        while self._is_running:
            try:
                for calendar_id in calendar_ids:
                    await self._sync_and_notify(calendar_id)

                await asyncio.sleep(self._poll_interval)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in poll loop: {e}")
                await asyncio.sleep(60)  # Back off on error

    async def _sync_and_notify(self, calendar_id: str) -> None:
        """Perform sync and notify callbacks."""
        try:
            changes = await self._sync.sync_events(calendar_id)

            for event, change_type in changes:
                for callback in self._callbacks:
                    try:
                        result = callback(event, change_type)
                        if asyncio.iscoroutine(result):
                            await result
                    except Exception as e:
                        logger.error(f"Callback error: {e}")

        except Exception as e:
            logger.error(f"Sync error for {calendar_id}: {e}")
