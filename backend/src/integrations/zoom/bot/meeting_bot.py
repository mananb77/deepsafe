"""
Zoom Meeting Bot

Implementation of IMeetingBot for Zoom using the Zoom Meeting SDK.

This bot:
- Joins Zoom meetings as a participant
- Captures audio/video streams for analysis
- Displays trust badges and alerts via Zoom Apps
- Manages participants (remove, mute, etc.)

Note: The actual Zoom Meeting SDK is a native library (C++/Electron).
This implementation provides the Python wrapper and API integration.
For full functionality, this would need to interface with the native SDK.
"""

import asyncio
import logging
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional
from uuid import uuid4

import httpx

from src.integrations.common.interface import BaseMeetingBot
from src.integrations.common.types import (
    MeetingPlatform,
    BotStatus,
    BotCredentials,
    MeetingInfo,
    ParticipantInfo,
    AudioFrame,
    VideoFrame,
    TrustBadge,
    AlertConfig,
    OverlayConfig,
    TrustLevel,
    AudioCallback,
    VideoCallback,
    ParticipantCallback,
    MeetingCallback,
)
from src.integrations.zoom.auth.oauth import ZoomOAuth, ZoomTokens
from src.shared.config import get_settings


logger = logging.getLogger(__name__)


class ZoomMeetingBot(BaseMeetingBot):
    """
    Zoom Meeting Bot implementation.

    Uses Zoom REST API for meeting management and would interface
    with Zoom Meeting SDK for audio/video capture in production.

    For development/testing, this provides a mock implementation
    that simulates bot behavior.
    """

    # Zoom API base URL
    API_BASE_URL = "https://api.zoom.us/v2"

    def __init__(
        self,
        oauth: Optional[ZoomOAuth] = None,
        mock_mode: bool = False,
    ):
        """
        Initialize Zoom Meeting Bot.

        Args:
            oauth: ZoomOAuth instance for authentication.
            mock_mode: If True, simulate SDK behavior without actual connection.
        """
        super().__init__()
        self._oauth = oauth or ZoomOAuth()
        self._mock_mode = mock_mode
        self._tokens: Optional[ZoomTokens] = None
        self._http_client: Optional[httpx.AsyncClient] = None

        # Stream subscriptions
        self._audio_subscriptions: Dict[str, Dict] = {}
        self._video_subscriptions: Dict[str, Dict] = {}
        self._participant_subscriptions: Dict[str, ParticipantCallback] = {}
        self._meeting_subscriptions: Dict[str, MeetingCallback] = {}

        # Overlay state
        self._trust_badges: Dict[str, TrustBadge] = {}
        self._active_alerts: Dict[str, AlertConfig] = {}
        self._overlay_config: Optional[OverlayConfig] = None

        # Background tasks
        self._stream_task: Optional[asyncio.Task] = None
        self._heartbeat_task: Optional[asyncio.Task] = None

    @property
    def platform(self) -> MeetingPlatform:
        return MeetingPlatform.ZOOM

    async def _get_http_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._http_client is None or self._http_client.is_closed:
            self._http_client = httpx.AsyncClient(
                base_url=self.API_BASE_URL,
                timeout=30.0,
            )
        return self._http_client

    async def _get_auth_headers(self) -> Dict[str, str]:
        """Get authorization headers for API requests."""
        if not self._tokens:
            raise ValueError("Not authenticated - call set_credentials first")

        # Refresh token if expired
        if self._tokens.is_expired and self._tokens.refresh_token:
            self._tokens = await self._oauth.refresh_tokens(self._tokens.refresh_token)

        return {
            "Authorization": f"Bearer {self._tokens.access_token}",
            "Content-Type": "application/json",
        }

    async def _api_request(
        self,
        method: str,
        endpoint: str,
        **kwargs,
    ) -> Dict[str, Any]:
        """Make authenticated API request."""
        client = await self._get_http_client()
        headers = await self._get_auth_headers()

        response = await client.request(
            method,
            endpoint,
            headers=headers,
            **kwargs,
        )
        response.raise_for_status()

        if response.status_code == 204:
            return {}
        return response.json()

    # ==================== Connection Management ====================

    async def set_credentials(self, credentials: BotCredentials) -> None:
        """Set authentication credentials."""
        if credentials.platform != MeetingPlatform.ZOOM:
            raise ValueError(f"Invalid platform: {credentials.platform}")

        if credentials.access_token:
            # Use provided tokens
            self._tokens = ZoomTokens(
                access_token=credentials.access_token,
                refresh_token=credentials.refresh_token,
                expires_in=3600,
            )
        elif credentials.zoom_sdk_key and credentials.zoom_sdk_secret:
            # Generate JWT for SDK (in production, this would create SDK auth)
            logger.info("SDK credentials provided - would initialize SDK auth")
            # For mock mode, create a placeholder token
            if self._mock_mode:
                self._tokens = ZoomTokens(
                    access_token="mock_sdk_token",
                    expires_in=86400,
                )
        else:
            raise ValueError("No valid credentials provided")

        self._credentials = credentials
        logger.info("Zoom credentials configured")

    async def connect(
        self,
        meeting_id: str,
        password: Optional[str] = None,
        display_name: Optional[str] = None,
    ) -> bool:
        """Connect bot to a Zoom meeting."""
        if not self._tokens:
            raise ValueError("Not authenticated - call set_credentials first")

        self._set_status(BotStatus.CONNECTING)
        logger.info(f"Connecting to Zoom meeting: {meeting_id}")

        try:
            # Get meeting info first
            meeting_info = await self._fetch_meeting_info(meeting_id)
            if not meeting_info:
                logger.error(f"Meeting not found: {meeting_id}")
                self._set_status(BotStatus.ERROR)
                return False

            self._meeting_info = meeting_info

            if self._mock_mode:
                # Simulate joining the meeting
                await asyncio.sleep(0.5)  # Simulate connection delay
                self._bot_participant_id = f"bot_{uuid4().hex[:8]}"
                self._set_status(BotStatus.IN_MEETING)
                logger.info(f"[MOCK] Joined meeting as {self._bot_participant_id}")

                # Start mock stream simulation
                self._stream_task = asyncio.create_task(self._mock_stream_loop())

                await self.on_connected()
                return True
            else:
                # In production, this would:
                # 1. Initialize Zoom Meeting SDK
                # 2. Join meeting with SDK
                # 3. Set up audio/video callbacks
                logger.warning("Production SDK connection not implemented")
                self._set_status(BotStatus.ERROR)
                return False

        except Exception as e:
            logger.error(f"Failed to connect to meeting: {e}")
            self._set_status(BotStatus.ERROR)
            await self.on_error(e)
            return False

    async def disconnect(self) -> None:
        """Disconnect from meeting."""
        logger.info("Disconnecting from Zoom meeting")
        self._set_status(BotStatus.LEAVING)

        # Cancel background tasks
        if self._stream_task:
            self._stream_task.cancel()
            try:
                await self._stream_task
            except asyncio.CancelledError:
                pass
            self._stream_task = None

        if self._heartbeat_task:
            self._heartbeat_task.cancel()
            try:
                await self._heartbeat_task
            except asyncio.CancelledError:
                pass
            self._heartbeat_task = None

        # Clear state
        reason = "User requested disconnect"
        self._clear_state()

        await self.on_disconnected(reason)
        logger.info("Disconnected from Zoom meeting")

    async def reconnect(self) -> bool:
        """Attempt to reconnect to meeting."""
        if not self._meeting_info:
            return False

        meeting_id = self._meeting_info.meeting_id
        await self.disconnect()
        return await self.connect(meeting_id)

    # ==================== Stream Subscription ====================

    def subscribe_to_audio_stream(
        self,
        callback: AudioCallback,
        participant_id: Optional[str] = None,
    ) -> str:
        """Subscribe to audio stream."""
        subscription_id = self._generate_subscription_id()
        self._audio_subscriptions[subscription_id] = {
            "callback": callback,
            "participant_id": participant_id,
        }
        logger.debug(f"Audio subscription created: {subscription_id}")
        return subscription_id

    def subscribe_to_video_stream(
        self,
        callback: VideoCallback,
        participant_id: Optional[str] = None,
        fps: int = 5,
    ) -> str:
        """Subscribe to video stream."""
        subscription_id = self._generate_subscription_id()
        self._video_subscriptions[subscription_id] = {
            "callback": callback,
            "participant_id": participant_id,
            "fps": fps,
        }
        logger.debug(f"Video subscription created: {subscription_id}")
        return subscription_id

    def unsubscribe(self, subscription_id: str) -> bool:
        """Unsubscribe from a stream."""
        if subscription_id in self._audio_subscriptions:
            del self._audio_subscriptions[subscription_id]
            return True
        if subscription_id in self._video_subscriptions:
            del self._video_subscriptions[subscription_id]
            return True
        if subscription_id in self._participant_subscriptions:
            del self._participant_subscriptions[subscription_id]
            return True
        if subscription_id in self._meeting_subscriptions:
            del self._meeting_subscriptions[subscription_id]
            return True
        return False

    # ==================== Participant Management ====================

    async def get_participants(self) -> List[ParticipantInfo]:
        """Get list of meeting participants."""
        if self._mock_mode:
            return self._get_cached_participants()

        if not self._meeting_info:
            return []

        try:
            # Zoom API doesn't have real-time participant list for ongoing meetings
            # In production, this would come from SDK callbacks
            return self._get_cached_participants()
        except Exception as e:
            logger.error(f"Failed to get participants: {e}")
            return self._get_cached_participants()

    async def get_participant(self, participant_id: str) -> Optional[ParticipantInfo]:
        """Get specific participant info."""
        return self._participants.get(participant_id)

    async def remove_participant(
        self,
        participant_id: str,
        reason: Optional[str] = None,
    ) -> bool:
        """Remove participant from meeting."""
        if not await self.is_host():
            raise PermissionError("Bot must be host/co-host to remove participants")

        if self._mock_mode:
            participant = self._remove_participant(participant_id)
            if participant:
                logger.info(f"[MOCK] Removed participant: {participant_id}, reason: {reason}")
                await self._notify_participant_event(participant, "left")
                return True
            return False

        # Production: Use Zoom API to remove participant
        # Note: Zoom API doesn't support removing participants directly
        # This would need to be done via SDK
        logger.warning("Participant removal via API not supported")
        return False

    async def mute_participant(
        self,
        participant_id: str,
        mute_audio: bool = True,
        mute_video: bool = False,
    ) -> bool:
        """Mute participant's audio/video."""
        if not await self.is_host():
            raise PermissionError("Bot must be host/co-host to mute participants")

        if self._mock_mode:
            participant = self._participants.get(participant_id)
            if participant:
                if mute_audio:
                    participant.is_audio_on = False
                if mute_video:
                    participant.is_video_on = False
                logger.info(f"[MOCK] Muted participant: {participant_id}")
                await self._notify_participant_event(participant, "muted")
                return True
            return False

        # Production: Use SDK to mute
        logger.warning("Muting via API not supported")
        return False

    def subscribe_to_participant_events(
        self,
        callback: ParticipantCallback,
    ) -> str:
        """Subscribe to participant events."""
        subscription_id = self._generate_subscription_id()
        self._participant_subscriptions[subscription_id] = callback
        return subscription_id

    # ==================== Meeting Events ====================

    def subscribe_to_meeting_events(
        self,
        callback: MeetingCallback,
    ) -> str:
        """Subscribe to meeting events."""
        subscription_id = self._generate_subscription_id()
        self._meeting_subscriptions[subscription_id] = callback
        return subscription_id

    # ==================== Overlay & UI ====================

    async def show_trust_badge(
        self,
        participant_id: str,
        badge: TrustBadge,
    ) -> bool:
        """Show trust badge for participant."""
        self._trust_badges[participant_id] = badge
        logger.info(f"Trust badge set for {participant_id}: {badge.trust_level.value}")

        # In production, this would send badge to Zoom Apps overlay
        if not self._mock_mode:
            # Send to Zoom Apps SDK
            pass

        return True

    async def hide_trust_badge(self, participant_id: str) -> bool:
        """Hide trust badge for participant."""
        if participant_id in self._trust_badges:
            del self._trust_badges[participant_id]
            logger.info(f"Trust badge removed for {participant_id}")
            return True
        return False

    async def show_alert(self, config: AlertConfig) -> bool:
        """Show alert overlay."""
        self._active_alerts[config.alert_id] = config
        logger.info(f"Alert shown: {config.alert_id} - {config.title}")

        # In production, send to Zoom Apps overlay
        return True

    async def dismiss_alert(self, alert_id: str) -> bool:
        """Dismiss alert."""
        if alert_id in self._active_alerts:
            del self._active_alerts[alert_id]
            logger.info(f"Alert dismissed: {alert_id}")
            return True
        return False

    async def update_overlay(self, config: OverlayConfig) -> bool:
        """Update overlay configuration."""
        self._overlay_config = config
        logger.info(f"Overlay updated: enabled={config.enabled}")
        return True

    # ==================== Meeting Control ====================

    async def send_chat_message(
        self,
        message: str,
        to_participant: Optional[str] = None,
    ) -> bool:
        """Send chat message."""
        if self._mock_mode:
            target = to_participant or "everyone"
            logger.info(f"[MOCK] Chat message to {target}: {message}")
            return True

        # Production: Use SDK to send chat
        logger.warning("Chat messaging not implemented")
        return False

    async def start_recording(self) -> bool:
        """Start meeting recording."""
        if not await self.is_host():
            raise PermissionError("Bot must be host to start recording")

        if self._mock_mode:
            if self._meeting_info:
                self._meeting_info.is_recording = True
            logger.info("[MOCK] Recording started")
            return True

        # Production: Use API to start cloud recording
        if not self._meeting_info:
            return False

        try:
            await self._api_request(
                "PATCH",
                f"/meetings/{self._meeting_info.meeting_id}/recordings/status",
                json={"action": "start"},
            )
            self._meeting_info.is_recording = True
            return True
        except Exception as e:
            logger.error(f"Failed to start recording: {e}")
            return False

    async def stop_recording(self) -> bool:
        """Stop meeting recording."""
        if self._mock_mode:
            if self._meeting_info:
                self._meeting_info.is_recording = False
            logger.info("[MOCK] Recording stopped")
            return True

        if not self._meeting_info:
            return False

        try:
            await self._api_request(
                "PATCH",
                f"/meetings/{self._meeting_info.meeting_id}/recordings/status",
                json={"action": "stop"},
            )
            self._meeting_info.is_recording = False
            return True
        except Exception as e:
            logger.error(f"Failed to stop recording: {e}")
            return False

    async def end_meeting(self, reason: Optional[str] = None) -> bool:
        """End meeting for all participants."""
        if not await self.is_host():
            raise PermissionError("Bot must be host to end meeting")

        if self._mock_mode:
            logger.info(f"[MOCK] Meeting ended, reason: {reason}")
            await self.disconnect()
            return True

        if not self._meeting_info:
            return False

        try:
            await self._api_request(
                "PUT",
                f"/meetings/{self._meeting_info.meeting_id}/status",
                json={"action": "end"},
            )
            await self.disconnect()
            return True
        except Exception as e:
            logger.error(f"Failed to end meeting: {e}")
            return False

    # ==================== Utility Methods ====================

    async def get_meeting_info(self) -> Optional[MeetingInfo]:
        """Fetch current meeting info."""
        if not self._meeting_info:
            return None
        return await self._fetch_meeting_info(self._meeting_info.meeting_id)

    async def _fetch_meeting_info(self, meeting_id: str) -> Optional[MeetingInfo]:
        """Fetch meeting info from Zoom API."""
        if self._mock_mode:
            return MeetingInfo(
                meeting_id=meeting_id,
                platform=MeetingPlatform.ZOOM,
                topic="Mock Meeting",
                host_id="mock_host",
                is_waiting_room_enabled=False,
            )

        try:
            data = await self._api_request("GET", f"/meetings/{meeting_id}")
            return MeetingInfo(
                meeting_id=str(data.get("id", meeting_id)),
                platform=MeetingPlatform.ZOOM,
                topic=data.get("topic"),
                host_id=data.get("host_id"),
                host_email=data.get("host_email"),
                start_time=datetime.fromisoformat(data["start_time"].replace("Z", "+00:00"))
                if data.get("start_time") else None,
                scheduled_duration=data.get("duration"),
                join_url=data.get("join_url"),
                password=data.get("password"),
                is_waiting_room_enabled=data.get("settings", {}).get("waiting_room", False),
                platform_data=data,
            )
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return None
            raise

    async def is_host(self) -> bool:
        """Check if bot is host/co-host."""
        if self._mock_mode:
            return True  # Assume host in mock mode

        # Check from participant info
        if self._bot_participant_id:
            participant = self._participants.get(self._bot_participant_id)
            if participant:
                return participant.is_host or participant.is_co_host
        return False

    async def request_host(self, host_key: Optional[str] = None) -> bool:
        """Request host privileges."""
        logger.warning("Host request not implemented")
        return False

    # ==================== Internal Methods ====================

    async def _mock_stream_loop(self) -> None:
        """Mock stream simulation for development."""
        logger.info("Starting mock stream simulation")

        # Add mock participants
        for i in range(3):
            participant = ParticipantInfo(
                participant_id=f"participant_{i}",
                platform=MeetingPlatform.ZOOM,
                meeting_id=self._meeting_info.meeting_id if self._meeting_info else "",
                display_name=f"User {i+1}",
                email=f"user{i+1}@example.com",
                is_host=(i == 0),
                is_audio_on=True,
                is_video_on=True,
                joined_at=datetime.utcnow(),
            )
            self._add_participant(participant)
            await self._notify_participant_event(participant, "joined")

        frame_count = 0
        while True:
            try:
                await asyncio.sleep(0.2)  # 5 FPS equivalent

                # Generate mock audio frames
                for sub_id, sub in self._audio_subscriptions.items():
                    callback = sub["callback"]
                    target_participant = sub.get("participant_id")

                    for p_id, participant in self._participants.items():
                        if target_participant and p_id != target_participant:
                            continue
                        if not participant.is_audio_on:
                            continue

                        frame = AudioFrame(
                            participant_id=p_id,
                            meeting_id=self._meeting_info.meeting_id if self._meeting_info else "",
                            data=b"\x00" * 3200,  # Mock 100ms of audio at 16kHz
                            sample_rate=16000,
                            channels=1,
                            duration_ms=100,
                            sequence_number=frame_count,
                        )
                        try:
                            callback(frame)
                        except Exception as e:
                            logger.error(f"Audio callback error: {e}")

                # Generate mock video frames (less frequently)
                if frame_count % 5 == 0:
                    for sub_id, sub in self._video_subscriptions.items():
                        callback = sub["callback"]
                        target_participant = sub.get("participant_id")

                        for p_id, participant in self._participants.items():
                            if target_participant and p_id != target_participant:
                                continue
                            if not participant.is_video_on:
                                continue

                            frame = VideoFrame(
                                participant_id=p_id,
                                meeting_id=self._meeting_info.meeting_id if self._meeting_info else "",
                                data=b"\x00" * (640 * 480 * 3),  # Mock RGB frame
                                width=640,
                                height=480,
                                format="RGB24",
                                frame_number=frame_count // 5,
                                fps=5.0,
                            )
                            try:
                                callback(frame)
                            except Exception as e:
                                logger.error(f"Video callback error: {e}")

                frame_count += 1

            except asyncio.CancelledError:
                logger.info("Mock stream loop cancelled")
                break
            except Exception as e:
                logger.error(f"Mock stream error: {e}")

    async def _notify_participant_event(
        self,
        participant: ParticipantInfo,
        event_type: str,
    ) -> None:
        """Notify participant event subscribers."""
        for callback in self._participant_subscriptions.values():
            try:
                callback(participant, event_type)
            except Exception as e:
                logger.error(f"Participant callback error: {e}")

    async def _notify_meeting_event(
        self,
        meeting: MeetingInfo,
        event_type: str,
    ) -> None:
        """Notify meeting event subscribers."""
        for callback in self._meeting_subscriptions.values():
            try:
                callback(meeting, event_type)
            except Exception as e:
                logger.error(f"Meeting callback error: {e}")

    async def close(self) -> None:
        """Clean up resources."""
        await self.disconnect()
        if self._http_client and not self._http_client.is_closed:
            await self._http_client.aclose()
        await self._oauth.close()
