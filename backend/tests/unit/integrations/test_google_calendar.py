"""Tests for Google Calendar sync."""

from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.integrations.google_meet.auth.oauth import GoogleTokens
from src.integrations.google_meet.calendar.sync import (
    EventStatus,
    ResponseStatus,
    EventAttendee,
    ConferenceData,
    CalendarEvent,
    GoogleCalendarSync,
    CalendarWatcher,
)


class TestEventStatusEnum:
    """Tests for EventStatus enum."""

    def test_values(self):
        """Test enum values."""
        assert EventStatus.CONFIRMED.value == "confirmed"
        assert EventStatus.TENTATIVE.value == "tentative"
        assert EventStatus.CANCELLED.value == "cancelled"


class TestResponseStatusEnum:
    """Tests for ResponseStatus enum."""

    def test_values(self):
        """Test enum values."""
        assert ResponseStatus.NEEDS_ACTION.value == "needsAction"
        assert ResponseStatus.DECLINED.value == "declined"
        assert ResponseStatus.TENTATIVE.value == "tentative"
        assert ResponseStatus.ACCEPTED.value == "accepted"


class TestEventAttendee:
    """Tests for EventAttendee dataclass."""

    def test_creation(self):
        """Test creating attendee."""
        attendee = EventAttendee(email="test@example.com")
        assert attendee.email == "test@example.com"
        assert attendee.response_status == ResponseStatus.NEEDS_ACTION

    def test_from_api_response(self):
        """Test creating from API response."""
        data = {
            "email": "test@example.com",
            "displayName": "Test User",
            "responseStatus": "accepted",
            "organizer": True,
            "optional": False,
            "self": True,
        }
        attendee = EventAttendee.from_api_response(data)
        assert attendee.email == "test@example.com"
        assert attendee.display_name == "Test User"
        assert attendee.response_status == ResponseStatus.ACCEPTED
        assert attendee.is_organizer is True
        assert attendee.is_self is True


class TestConferenceData:
    """Tests for ConferenceData dataclass."""

    def test_creation(self):
        """Test creating conference data."""
        conf = ConferenceData(
            conference_id="conf_123",
            conference_solution="hangoutsMeet",
            entry_point_uri="https://meet.google.com/abc-defg-hij",
            meeting_code="abc-defg-hij",
        )
        assert conf.conference_id == "conf_123"
        assert conf.meeting_code == "abc-defg-hij"

    def test_from_api_response(self):
        """Test creating from API response."""
        data = {
            "conferenceId": "conf_123",
            "conferenceSolution": {
                "key": {"type": "hangoutsMeet"},
            },
            "entryPoints": [
                {
                    "entryPointType": "video",
                    "uri": "https://meet.google.com/abc-defg-hij",
                    "passcode": "1234",
                },
                {
                    "entryPointType": "phone",
                    "uri": "tel:+1234567890",
                },
            ],
        }
        conf = ConferenceData.from_api_response(data)
        assert conf.conference_id == "conf_123"
        assert conf.entry_point_uri == "https://meet.google.com/abc-defg-hij"
        assert conf.meeting_code == "abc-defg-hij"
        assert conf.passcode == "1234"

    def test_from_api_response_no_video(self):
        """Test creating from API response without video entry."""
        data = {
            "conferenceId": "conf_123",
            "entryPoints": [
                {
                    "entryPointType": "phone",
                    "uri": "tel:+1234567890",
                },
            ],
        }
        conf = ConferenceData.from_api_response(data)
        assert conf is None

    def test_from_api_response_empty(self):
        """Test creating from empty data."""
        conf = ConferenceData.from_api_response(None)
        assert conf is None


class TestCalendarEvent:
    """Tests for CalendarEvent dataclass."""

    def test_creation(self):
        """Test creating event."""
        event = CalendarEvent(
            event_id="event_123",
            calendar_id="primary",
            summary="Test Meeting",
        )
        assert event.event_id == "event_123"
        assert event.summary == "Test Meeting"

    def test_has_google_meet_true(self):
        """Test has_google_meet when meet is attached."""
        event = CalendarEvent(
            event_id="event_123",
            calendar_id="primary",
            summary="Test Meeting",
            conference_data=ConferenceData(
                conference_id="conf_123",
                conference_solution="hangoutsMeet",
                entry_point_uri="https://meet.google.com/abc-defg-hij",
                meeting_code="abc-defg-hij",
            ),
        )
        assert event.has_google_meet is True

    def test_has_google_meet_false(self):
        """Test has_google_meet when no meet attached."""
        event = CalendarEvent(
            event_id="event_123",
            calendar_id="primary",
            summary="Test Meeting",
        )
        assert event.has_google_meet is False

    def test_meet_link(self):
        """Test meet_link property."""
        event = CalendarEvent(
            event_id="event_123",
            calendar_id="primary",
            summary="Test Meeting",
            conference_data=ConferenceData(
                conference_id="conf_123",
                conference_solution="hangoutsMeet",
                entry_point_uri="https://meet.google.com/abc-defg-hij",
                meeting_code="abc-defg-hij",
            ),
        )
        assert event.meet_link == "https://meet.google.com/abc-defg-hij"

    def test_meet_code(self):
        """Test meet_code property."""
        event = CalendarEvent(
            event_id="event_123",
            calendar_id="primary",
            summary="Test Meeting",
            conference_data=ConferenceData(
                conference_id="conf_123",
                conference_solution="hangoutsMeet",
                entry_point_uri="https://meet.google.com/abc-defg-hij",
                meeting_code="abc-defg-hij",
            ),
        )
        assert event.meet_code == "abc-defg-hij"

    def test_duration_minutes(self):
        """Test duration_minutes calculation."""
        now = datetime.utcnow()
        event = CalendarEvent(
            event_id="event_123",
            calendar_id="primary",
            summary="Test Meeting",
            start_time=now,
            end_time=now + timedelta(hours=1),
        )
        assert event.duration_minutes == 60

    def test_is_active_true(self):
        """Test is_active when event is happening."""
        now = datetime.utcnow()
        event = CalendarEvent(
            event_id="event_123",
            calendar_id="primary",
            summary="Test Meeting",
            start_time=now - timedelta(minutes=30),
            end_time=now + timedelta(minutes=30),
        )
        assert event.is_active is True

    def test_is_active_false(self):
        """Test is_active when event is not happening."""
        now = datetime.utcnow()
        event = CalendarEvent(
            event_id="event_123",
            calendar_id="primary",
            summary="Test Meeting",
            start_time=now + timedelta(hours=1),
            end_time=now + timedelta(hours=2),
        )
        assert event.is_active is False

    def test_is_upcoming_true(self):
        """Test is_upcoming for future event."""
        now = datetime.utcnow()
        event = CalendarEvent(
            event_id="event_123",
            calendar_id="primary",
            summary="Test Meeting",
            start_time=now + timedelta(hours=1),
        )
        assert event.is_upcoming is True

    def test_is_upcoming_false(self):
        """Test is_upcoming for past event."""
        now = datetime.utcnow()
        event = CalendarEvent(
            event_id="event_123",
            calendar_id="primary",
            summary="Test Meeting",
            start_time=now - timedelta(hours=1),
        )
        assert event.is_upcoming is False

    def test_from_api_response_full(self):
        """Test creating from full API response."""
        data = {
            "id": "event_123",
            "summary": "Team Meeting",
            "description": "Weekly sync",
            "location": "Conference Room A",
            "start": {
                "dateTime": "2025-01-15T10:00:00Z",
                "timeZone": "America/New_York",
            },
            "end": {
                "dateTime": "2025-01-15T11:00:00Z",
                "timeZone": "America/New_York",
            },
            "status": "confirmed",
            "visibility": "default",
            "organizer": {
                "email": "organizer@example.com",
                "displayName": "Organizer",
            },
            "attendees": [
                {"email": "attendee@example.com", "responseStatus": "accepted"},
            ],
            "conferenceData": {
                "conferenceId": "conf_123",
                "conferenceSolution": {"key": {"type": "hangoutsMeet"}},
                "entryPoints": [
                    {
                        "entryPointType": "video",
                        "uri": "https://meet.google.com/abc-defg-hij",
                    },
                ],
            },
            "created": "2025-01-10T10:00:00Z",
            "updated": "2025-01-10T10:00:00Z",
            "htmlLink": "https://calendar.google.com/event/123",
        }

        event = CalendarEvent.from_api_response(data, "primary")

        assert event.event_id == "event_123"
        assert event.summary == "Team Meeting"
        assert event.description == "Weekly sync"
        assert event.status == EventStatus.CONFIRMED
        assert event.organizer_email == "organizer@example.com"
        assert len(event.attendees) == 1
        assert event.has_google_meet is True
        assert event.meet_code == "abc-defg-hij"

    def test_from_api_response_all_day(self):
        """Test creating all-day event from API response."""
        data = {
            "id": "event_123",
            "summary": "Company Holiday",
            "start": {"date": "2025-01-15"},
            "end": {"date": "2025-01-16"},
        }

        event = CalendarEvent.from_api_response(data, "primary")

        assert event.is_all_day is True


class TestGoogleCalendarSync:
    """Tests for GoogleCalendarSync class."""

    @pytest.fixture
    def sync(self):
        """Create sync client for testing."""
        tokens = GoogleTokens(
            access_token="test_access_token",
            refresh_token="test_refresh_token",
            expires_in=3600,
        )
        with patch("src.integrations.google_meet.auth.oauth.get_settings") as mock:
            mock.return_value.google.client_id = "test_id"
            mock.return_value.google.client_secret = "test_secret"
            return GoogleCalendarSync(tokens)

    @pytest.mark.asyncio
    async def test_get_calendars(self, sync):
        """Test getting calendar list."""
        with patch.object(sync, "_get_client") as mock_get_client:
            mock_response = MagicMock()
            mock_response.json.return_value = {
                "items": [
                    {"id": "primary", "summary": "My Calendar"},
                    {"id": "work@example.com", "summary": "Work"},
                ],
            }
            mock_response.raise_for_status = MagicMock()

            mock_client = AsyncMock()
            mock_client.get.return_value = mock_response
            mock_get_client.return_value = mock_client

            calendars = await sync.get_calendars()

            assert len(calendars) == 2
            assert calendars[0]["id"] == "primary"

    @pytest.mark.asyncio
    async def test_get_events(self, sync):
        """Test getting events."""
        with patch.object(sync, "_get_client") as mock_get_client:
            mock_response = MagicMock()
            mock_response.json.return_value = {
                "items": [
                    {
                        "id": "event_1",
                        "summary": "Meeting 1",
                        "start": {"dateTime": "2025-01-15T10:00:00Z"},
                        "end": {"dateTime": "2025-01-15T11:00:00Z"},
                    },
                    {
                        "id": "event_2",
                        "summary": "Meeting 2",
                        "start": {"dateTime": "2025-01-15T14:00:00Z"},
                        "end": {"dateTime": "2025-01-15T15:00:00Z"},
                    },
                ],
                "nextSyncToken": "sync_token_123",
            }
            mock_response.raise_for_status = MagicMock()

            mock_client = AsyncMock()
            mock_client.get.return_value = mock_response
            mock_get_client.return_value = mock_client

            events = await sync.get_events(calendar_id="primary")

            assert len(events) == 2
            assert events[0].event_id == "event_1"
            assert events[0].summary == "Meeting 1"

    @pytest.mark.asyncio
    async def test_get_events_with_meet(self, sync):
        """Test getting events with Google Meet."""
        with patch.object(sync, "_get_client") as mock_get_client:
            mock_response = MagicMock()
            mock_response.json.return_value = {
                "items": [
                    {
                        "id": "event_1",
                        "summary": "In-person Meeting",
                        "start": {"dateTime": "2025-01-15T10:00:00Z"},
                        "end": {"dateTime": "2025-01-15T11:00:00Z"},
                    },
                    {
                        "id": "event_2",
                        "summary": "Video Meeting",
                        "start": {"dateTime": "2025-01-15T14:00:00Z"},
                        "end": {"dateTime": "2025-01-15T15:00:00Z"},
                        "conferenceData": {
                            "conferenceId": "conf_123",
                            "conferenceSolution": {"key": {"type": "hangoutsMeet"}},
                            "entryPoints": [
                                {
                                    "entryPointType": "video",
                                    "uri": "https://meet.google.com/abc-defg-hij",
                                },
                            ],
                        },
                    },
                ],
            }
            mock_response.raise_for_status = MagicMock()

            mock_client = AsyncMock()
            mock_client.get.return_value = mock_response
            mock_get_client.return_value = mock_client

            events = await sync.get_events_with_meet(calendar_id="primary")

            assert len(events) == 1
            assert events[0].event_id == "event_2"
            assert events[0].has_google_meet is True

    @pytest.mark.asyncio
    async def test_get_event(self, sync):
        """Test getting a specific event."""
        with patch.object(sync, "_get_client") as mock_get_client:
            mock_response = MagicMock()
            mock_response.json.return_value = {
                "id": "event_123",
                "summary": "Test Meeting",
                "start": {"dateTime": "2025-01-15T10:00:00Z"},
                "end": {"dateTime": "2025-01-15T11:00:00Z"},
            }
            mock_response.raise_for_status = MagicMock()

            mock_client = AsyncMock()
            mock_client.get.return_value = mock_response
            mock_get_client.return_value = mock_client

            event = await sync.get_event(event_id="event_123")

            assert event.event_id == "event_123"
            assert event.summary == "Test Meeting"

    @pytest.mark.asyncio
    async def test_watch_calendar(self, sync):
        """Test setting up calendar watch."""
        with patch.object(sync, "_get_client") as mock_get_client:
            mock_response = MagicMock()
            mock_response.json.return_value = {
                "id": "channel_123",
                "resourceId": "resource_456",
                "expiration": "1609459200000",
            }
            mock_response.raise_for_status = MagicMock()

            mock_client = AsyncMock()
            mock_client.post.return_value = mock_response
            mock_get_client.return_value = mock_client

            with patch("src.integrations.google_meet.calendar.sync.get_settings") as mock_settings:
                mock_settings.return_value.google.calendar_webhook_url = ""

                watch_info = await sync.watch_calendar(
                    calendar_id="primary",
                    webhook_url="https://example.com/webhook",
                )

            assert watch_info["id"] == "channel_123"
            assert "primary" in sync._watched_calendars

    @pytest.mark.asyncio
    async def test_stop_watching(self, sync):
        """Test stopping calendar watch."""
        with patch.object(sync, "_get_client") as mock_get_client:
            mock_response = MagicMock()
            mock_response.status_code = 204

            mock_client = AsyncMock()
            mock_client.post.return_value = mock_response
            mock_get_client.return_value = mock_client

            result = await sync.stop_watching(
                channel_id="channel_123",
                resource_id="resource_456",
            )

            assert result is True


class TestCalendarWatcher:
    """Tests for CalendarWatcher class."""

    @pytest.fixture
    def watcher(self):
        """Create watcher for testing."""
        tokens = GoogleTokens(
            access_token="test_token",
            expires_in=3600,
        )
        with patch("src.integrations.google_meet.auth.oauth.get_settings") as mock:
            mock.return_value.google.client_id = "test_id"
            mock.return_value.google.client_secret = "test_secret"
            sync = GoogleCalendarSync(tokens)
            return CalendarWatcher(sync, poll_interval=60)

    def test_on_event_registration(self, watcher):
        """Test registering event callback."""
        @watcher.on_event
        def handle_event(event, change_type):
            pass

        assert len(watcher._callbacks) == 1

    @pytest.mark.asyncio
    async def test_handle_webhook_sync(self, watcher):
        """Test handling sync notification."""
        headers = {
            "x-goog-channel-id": "channel_123",
            "x-goog-resource-state": "sync",
        }

        # Should not raise any errors
        await watcher.handle_webhook(headers, b"")

    @pytest.mark.asyncio
    async def test_start_and_stop(self, watcher):
        """Test starting and stopping watcher."""
        with patch.object(watcher._sync, "watch_calendar") as mock_watch:
            mock_watch.return_value = {
                "id": "channel_123",
                "resourceId": "resource_456",
            }

            with patch.object(watcher._sync, "sync_events") as mock_sync:
                mock_sync.return_value = []

                await watcher.start(
                    calendar_ids=["primary"],
                    use_push=True,
                )

                # Wait a bit for task to start
                import asyncio
                await asyncio.sleep(0.1)

                assert watcher._is_running is True

                with patch.object(watcher._sync, "stop_watching") as mock_stop:
                    mock_stop.return_value = True
                    await watcher.stop()

                assert watcher._is_running is False
