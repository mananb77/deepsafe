"""
Meeting Bot Interface

Defines the common interface (protocol) that all meeting platform bots must implement.
This ensures consistent behavior across Zoom, Google Meet, and Teams integrations.
"""

from abc import ABC, abstractmethod
from typing import Callable, List, Optional

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
    AudioCallback,
    VideoCallback,
    ParticipantCallback,
    MeetingCallback,
)


class IMeetingBot(ABC):
    """
    Abstract base class for meeting platform bots.

    All platform-specific bots (Zoom, Google Meet, Teams) must implement
    this interface to ensure consistent behavior.

    Lifecycle:
    1. Create bot instance
    2. Set credentials with set_credentials()
    3. Connect to meeting with connect()
    4. Subscribe to streams with subscribe_to_*()
    5. Interact with meeting (badges, alerts, etc.)
    6. Disconnect with disconnect()
    """

    @property
    @abstractmethod
    def platform(self) -> MeetingPlatform:
        """Get the platform this bot supports."""
        pass

    @property
    @abstractmethod
    def status(self) -> BotStatus:
        """Get current bot connection status."""
        pass

    @property
    @abstractmethod
    def meeting_info(self) -> Optional[MeetingInfo]:
        """Get current meeting information (if connected)."""
        pass

    @property
    @abstractmethod
    def bot_participant_id(self) -> Optional[str]:
        """Get the bot's participant ID in the meeting."""
        pass

    # ==================== Connection Management ====================

    @abstractmethod
    async def set_credentials(self, credentials: BotCredentials) -> None:
        """
        Set authentication credentials for the bot.

        Args:
            credentials: Platform-specific credentials.

        Raises:
            ValueError: If credentials are invalid for this platform.
        """
        pass

    @abstractmethod
    async def connect(
        self,
        meeting_id: str,
        password: Optional[str] = None,
        display_name: Optional[str] = None,
    ) -> bool:
        """
        Connect bot to a meeting.

        Args:
            meeting_id: Platform-specific meeting ID.
            password: Meeting password (if required).
            display_name: Bot display name in meeting.

        Returns:
            True if connection successful, False otherwise.

        Raises:
            ConnectionError: If connection fails.
            PermissionError: If bot is not authorized to join.
        """
        pass

    @abstractmethod
    async def disconnect(self) -> None:
        """
        Disconnect bot from meeting.

        Gracefully leaves the meeting and cleans up resources.
        """
        pass

    @abstractmethod
    async def reconnect(self) -> bool:
        """
        Attempt to reconnect to the current meeting.

        Returns:
            True if reconnection successful, False otherwise.
        """
        pass

    # ==================== Stream Subscription ====================

    @abstractmethod
    def subscribe_to_audio_stream(
        self,
        callback: AudioCallback,
        participant_id: Optional[str] = None,
    ) -> str:
        """
        Subscribe to audio stream from meeting.

        Args:
            callback: Function called with each audio frame.
            participant_id: Specific participant (None = all).

        Returns:
            Subscription ID for unsubscribing.
        """
        pass

    @abstractmethod
    def subscribe_to_video_stream(
        self,
        callback: VideoCallback,
        participant_id: Optional[str] = None,
        fps: int = 5,
    ) -> str:
        """
        Subscribe to video stream from meeting.

        Args:
            callback: Function called with each video frame.
            participant_id: Specific participant (None = active speaker).
            fps: Target frames per second.

        Returns:
            Subscription ID for unsubscribing.
        """
        pass

    @abstractmethod
    def unsubscribe(self, subscription_id: str) -> bool:
        """
        Unsubscribe from a stream.

        Args:
            subscription_id: ID returned from subscribe_to_*.

        Returns:
            True if unsubscribed, False if subscription not found.
        """
        pass

    # ==================== Participant Management ====================

    @abstractmethod
    async def get_participants(self) -> List[ParticipantInfo]:
        """
        Get list of all participants in the meeting.

        Returns:
            List of participant information.
        """
        pass

    @abstractmethod
    async def get_participant(self, participant_id: str) -> Optional[ParticipantInfo]:
        """
        Get information about a specific participant.

        Args:
            participant_id: Platform-specific participant ID.

        Returns:
            Participant information or None if not found.
        """
        pass

    @abstractmethod
    async def remove_participant(self, participant_id: str, reason: Optional[str] = None) -> bool:
        """
        Remove a participant from the meeting.

        Requires host/co-host privileges.

        Args:
            participant_id: Participant to remove.
            reason: Optional reason for removal (for audit).

        Returns:
            True if removed, False otherwise.

        Raises:
            PermissionError: If bot lacks required privileges.
        """
        pass

    @abstractmethod
    async def mute_participant(
        self,
        participant_id: str,
        mute_audio: bool = True,
        mute_video: bool = False,
    ) -> bool:
        """
        Mute a participant's audio/video.

        Requires host/co-host privileges.

        Args:
            participant_id: Participant to mute.
            mute_audio: Mute audio.
            mute_video: Mute video.

        Returns:
            True if muted, False otherwise.
        """
        pass

    @abstractmethod
    def subscribe_to_participant_events(
        self,
        callback: ParticipantCallback,
    ) -> str:
        """
        Subscribe to participant events (join, leave, mute, etc.).

        Args:
            callback: Function called with participant info and event type.
                      Event types: "joined", "left", "muted", "unmuted",
                      "video_on", "video_off", "renamed"

        Returns:
            Subscription ID for unsubscribing.
        """
        pass

    # ==================== Meeting Events ====================

    @abstractmethod
    def subscribe_to_meeting_events(
        self,
        callback: MeetingCallback,
    ) -> str:
        """
        Subscribe to meeting events.

        Args:
            callback: Function called with meeting info and event type.
                      Event types: "started", "ended", "recording_started",
                      "recording_stopped", "waiting_room_enabled", "host_changed"

        Returns:
            Subscription ID for unsubscribing.
        """
        pass

    # ==================== Overlay & UI ====================

    @abstractmethod
    async def show_trust_badge(
        self,
        participant_id: str,
        badge: TrustBadge,
    ) -> bool:
        """
        Show a trust badge for a participant.

        Args:
            participant_id: Participant to badge.
            badge: Badge configuration.

        Returns:
            True if badge shown, False otherwise.
        """
        pass

    @abstractmethod
    async def hide_trust_badge(self, participant_id: str) -> bool:
        """
        Hide trust badge for a participant.

        Args:
            participant_id: Participant to un-badge.

        Returns:
            True if badge hidden, False otherwise.
        """
        pass

    @abstractmethod
    async def show_alert(self, config: AlertConfig) -> bool:
        """
        Show an alert overlay in the meeting.

        Args:
            config: Alert configuration.

        Returns:
            True if alert shown, False otherwise.
        """
        pass

    @abstractmethod
    async def dismiss_alert(self, alert_id: str) -> bool:
        """
        Dismiss an active alert.

        Args:
            alert_id: ID of alert to dismiss.

        Returns:
            True if dismissed, False otherwise.
        """
        pass

    @abstractmethod
    async def update_overlay(self, config: OverlayConfig) -> bool:
        """
        Update the DeepSafe overlay configuration.

        Args:
            config: Overlay configuration.

        Returns:
            True if updated, False otherwise.
        """
        pass

    # ==================== Meeting Control ====================

    @abstractmethod
    async def send_chat_message(
        self,
        message: str,
        to_participant: Optional[str] = None,
    ) -> bool:
        """
        Send a chat message in the meeting.

        Args:
            message: Message text.
            to_participant: Specific recipient (None = everyone).

        Returns:
            True if sent, False otherwise.
        """
        pass

    @abstractmethod
    async def start_recording(self) -> bool:
        """
        Start meeting recording.

        Requires host privileges.

        Returns:
            True if recording started, False otherwise.
        """
        pass

    @abstractmethod
    async def stop_recording(self) -> bool:
        """
        Stop meeting recording.

        Returns:
            True if recording stopped, False otherwise.
        """
        pass

    @abstractmethod
    async def end_meeting(self, reason: Optional[str] = None) -> bool:
        """
        End the meeting for all participants.

        Requires host privileges.

        Args:
            reason: Optional reason for ending (for audit).

        Returns:
            True if meeting ended, False otherwise.
        """
        pass

    # ==================== Utility Methods ====================

    @abstractmethod
    async def get_meeting_info(self) -> Optional[MeetingInfo]:
        """
        Fetch current meeting information from platform.

        Returns:
            Meeting information or None if not connected.
        """
        pass

    @abstractmethod
    async def is_host(self) -> bool:
        """
        Check if bot has host privileges.

        Returns:
            True if bot is host/co-host, False otherwise.
        """
        pass

    @abstractmethod
    async def request_host(self, host_key: Optional[str] = None) -> bool:
        """
        Request host privileges.

        Args:
            host_key: Host key if required by platform.

        Returns:
            True if granted, False otherwise.
        """
        pass

    # ==================== Lifecycle Hooks ====================

    async def on_connected(self) -> None:
        """Called when bot successfully connects to meeting."""
        pass

    async def on_disconnected(self, reason: str) -> None:
        """Called when bot disconnects from meeting."""
        pass

    async def on_error(self, error: Exception) -> None:
        """Called when an error occurs."""
        pass

    async def on_participant_joined(self, participant: ParticipantInfo) -> None:
        """Called when a participant joins the meeting."""
        pass

    async def on_participant_left(self, participant: ParticipantInfo) -> None:
        """Called when a participant leaves the meeting."""
        pass


class BaseMeetingBot(IMeetingBot):
    """
    Base implementation of IMeetingBot with common functionality.

    Platform-specific bots should extend this class.
    """

    def __init__(self):
        self._status: BotStatus = BotStatus.DISCONNECTED
        self._meeting_info: Optional[MeetingInfo] = None
        self._credentials: Optional[BotCredentials] = None
        self._participants: dict[str, ParticipantInfo] = {}
        self._subscriptions: dict[str, dict] = {}
        self._bot_participant_id: Optional[str] = None

    @property
    def status(self) -> BotStatus:
        return self._status

    @property
    def meeting_info(self) -> Optional[MeetingInfo]:
        return self._meeting_info

    @property
    def bot_participant_id(self) -> Optional[str]:
        return self._bot_participant_id

    def _generate_subscription_id(self) -> str:
        """Generate unique subscription ID."""
        import uuid
        return str(uuid.uuid4())

    def _set_status(self, status: BotStatus) -> None:
        """Update bot status."""
        self._status = status

    def _add_participant(self, participant: ParticipantInfo) -> None:
        """Add participant to local cache."""
        self._participants[participant.participant_id] = participant

    def _remove_participant(self, participant_id: str) -> Optional[ParticipantInfo]:
        """Remove participant from local cache."""
        return self._participants.pop(participant_id, None)

    def _get_cached_participants(self) -> List[ParticipantInfo]:
        """Get cached participants list."""
        return list(self._participants.values())

    def _clear_state(self) -> None:
        """Clear all state (on disconnect)."""
        self._meeting_info = None
        self._participants.clear()
        self._subscriptions.clear()
        self._bot_participant_id = None
        self._status = BotStatus.DISCONNECTED
