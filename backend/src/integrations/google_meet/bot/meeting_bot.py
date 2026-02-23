"""
Google Meet Bot Implementation

Puppeteer-based bot for Google Meet integration:
- Headless browser automation for meeting access
- Audio/video stream capture via WebRTC
- Participant tracking via DOM observation
- In-meeting overlays via content injection

Since Google Meet doesn't provide an official SDK for bots,
this uses browser automation to join meetings as a participant.

Requirements:
- Node.js with puppeteer-core
- Chrome/Chromium browser
- Google account for authentication

Architecture:
- Python orchestrator manages bot lifecycle
- Node.js subprocess handles browser automation
- WebSocket communication between Python and Node.js
"""

import asyncio
import json
import logging
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set
import uuid

import httpx

from src.integrations.common.interface import BaseMeetingBot
from src.integrations.common.types import (
    AlertConfig,
    AudioCallback,
    AudioFrame,
    BotCredentials,
    BotStatus,
    MeetingInfo,
    MeetingPlatform,
    OverlayConfig,
    ParticipantInfo,
    StreamType,
    TrustBadge,
    VideoCallback,
    VideoFrame,
)
from src.integrations.google_meet.auth.oauth import GoogleOAuth, GoogleTokens
from src.shared.config import get_settings


logger = logging.getLogger(__name__)


class GoogleMeetBotMode(str, Enum):
    """Bot operation mode."""
    PUPPETEER = "puppeteer"  # Full browser automation
    MOCK = "mock"  # Development/testing mode


@dataclass
class BrowserConfig:
    """Configuration for Puppeteer browser."""
    executable_path: Optional[str] = None  # Chrome/Chromium path
    headless: bool = True
    user_data_dir: Optional[str] = None  # For persistent sessions
    proxy: Optional[str] = None
    viewport_width: int = 1920
    viewport_height: int = 1080

    # Audio/video capture settings
    capture_audio: bool = True
    capture_video: bool = True
    video_fps: int = 15
    audio_sample_rate: int = 48000


class GoogleMeetBot(BaseMeetingBot):
    """
    Google Meet bot using Puppeteer browser automation.

    Implements the IMeetingBot interface for Google Meet.

    Usage:
        bot = GoogleMeetBot(credentials)
        await bot.connect(meeting_code)

        @bot.on_audio
        def handle_audio(frame: AudioFrame):
            process_audio(frame)

        # Later...
        await bot.disconnect()
    """

    # Google Meet URL patterns
    MEET_BASE_URL = "https://meet.google.com"

    # CSS Selectors for Meet UI elements
    SELECTORS = {
        # Join flow
        "name_input": "input[aria-label='Your name']",
        "join_button": "button[data-idom-class*='join']",
        "ask_to_join_button": "button[jsname='Qx7uuf']",

        # Meeting controls
        "leave_button": "button[aria-label='Leave call']",
        "mute_button": "button[aria-label*='microphone']",
        "camera_button": "button[aria-label*='camera']",
        "participants_button": "button[aria-label*='participants']",

        # Participants
        "participant_list": "div[aria-label='Participants']",
        "participant_item": "div[data-participant-id]",

        # Chat
        "chat_button": "button[aria-label*='chat']",
        "chat_input": "textarea[aria-label*='message']",
        "chat_send": "button[aria-label='Send']",

        # Screen share detection
        "presenting_indicator": "div[data-is-presenting='true']",
    }

    def __init__(
        self,
        credentials: BotCredentials,
        mode: GoogleMeetBotMode = GoogleMeetBotMode.MOCK,
        browser_config: Optional[BrowserConfig] = None,
    ):
        """
        Initialize Google Meet bot.

        Args:
            credentials: Bot authentication credentials.
            mode: Operation mode (PUPPETEER or MOCK).
            browser_config: Browser configuration for Puppeteer mode.
        """
        super().__init__(credentials, MeetingPlatform.GOOGLE_MEET)

        self._mode = mode
        self._browser_config = browser_config or BrowserConfig()

        # OAuth client
        self._oauth = GoogleOAuth(
            client_id=credentials.google_client_id,
            client_secret=credentials.google_client_secret,
        )
        self._tokens: Optional[GoogleTokens] = None

        # Browser subprocess
        self._browser_process: Optional[subprocess.Popen] = None
        self._ws_connection: Optional[Any] = None  # WebSocket to browser

        # Meeting state
        self._meeting_code: Optional[str] = None
        self._meeting_title: Optional[str] = None
        self._participants: Dict[str, ParticipantInfo] = {}
        self._is_muted = True
        self._is_camera_off = True

        # Stream subscriptions
        self._audio_callbacks: Dict[str, AudioCallback] = {}
        self._video_callbacks: Dict[str, VideoCallback] = {}

        # Overlay state
        self._active_overlays: Dict[str, OverlayConfig] = {}
        self._trust_badges: Dict[str, TrustBadge] = {}

        # Mock mode streaming
        self._mock_stream_task: Optional[asyncio.Task] = None

        # HTTP client
        self._http_client: Optional[httpx.AsyncClient] = None

    async def _get_http_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._http_client is None or self._http_client.is_closed:
            self._http_client = httpx.AsyncClient(timeout=30.0)
        return self._http_client

    # ==================== Connection Methods ====================

    async def connect(
        self,
        meeting_id: str,
        password: Optional[str] = None,
        display_name: Optional[str] = None,
    ) -> bool:
        """
        Connect to a Google Meet meeting.

        Args:
            meeting_id: Meeting code (e.g., "abc-defg-hij").
            password: Not used for Google Meet.
            display_name: Name to display in the meeting.

        Returns:
            True if connected successfully.
        """
        if self._status != BotStatus.DISCONNECTED:
            logger.warning("Bot is already connected or connecting")
            return False

        self._status = BotStatus.CONNECTING
        self._meeting_code = self._normalize_meeting_code(meeting_id)
        display_name = display_name or self._credentials.bot_display_name or "DeepSafe Bot"

        try:
            if self._mode == GoogleMeetBotMode.MOCK:
                return await self._mock_connect(display_name)
            else:
                return await self._puppeteer_connect(display_name)

        except Exception as e:
            logger.error(f"Failed to connect to Google Meet: {e}")
            self._status = BotStatus.ERROR
            self._error = str(e)
            return False

    def _normalize_meeting_code(self, meeting_id: str) -> str:
        """Normalize meeting code format."""
        # Remove URL prefix if present
        if "meet.google.com/" in meeting_id:
            meeting_id = meeting_id.split("meet.google.com/")[-1]

        # Remove query parameters
        if "?" in meeting_id:
            meeting_id = meeting_id.split("?")[0]

        return meeting_id.strip("/")

    async def _mock_connect(self, display_name: str) -> bool:
        """Mock connection for development."""
        logger.info(f"[MOCK] Connecting to Google Meet: {self._meeting_code}")

        # Simulate connection delay
        await asyncio.sleep(1.0)

        # Set up mock meeting info
        self._meeting_info = MeetingInfo(
            meeting_id=self._meeting_code or "",
            platform=MeetingPlatform.GOOGLE_MEET,
            title=f"Mock Meeting {self._meeting_code}",
            start_time=datetime.utcnow(),
            host_id="mock_host",
            host_name="Mock Host",
            join_url=f"{self.MEET_BASE_URL}/{self._meeting_code}",
        )

        # Add mock participants
        self._participants = {
            "mock_host": ParticipantInfo(
                participant_id="mock_host",
                user_id="host_user_123",
                display_name="Mock Host",
                email="host@example.com",
                is_host=True,
            ),
            "mock_participant": ParticipantInfo(
                participant_id="mock_participant",
                user_id="participant_456",
                display_name="Mock Participant",
            ),
        }

        self._status = BotStatus.CONNECTED
        self._connected_at = datetime.utcnow()

        # Start mock stream generation
        self._mock_stream_task = asyncio.create_task(self._mock_stream_loop())

        logger.info(f"[MOCK] Connected to Google Meet: {self._meeting_code}")
        return True

    async def _puppeteer_connect(self, display_name: str) -> bool:
        """Connect using Puppeteer browser automation."""
        logger.info(f"Connecting to Google Meet via Puppeteer: {self._meeting_code}")

        # Ensure we have valid tokens
        if not await self._ensure_authenticated():
            raise RuntimeError("Failed to authenticate with Google")

        # Start browser subprocess
        await self._start_browser_process()

        # Navigate to meeting and join
        meeting_url = f"{self.MEET_BASE_URL}/{self._meeting_code}"

        await self._send_browser_command("navigate", {"url": meeting_url})
        await asyncio.sleep(2.0)  # Wait for page load

        # Set display name
        await self._send_browser_command("set_text", {
            "selector": self.SELECTORS["name_input"],
            "value": display_name,
        })

        # Click join button
        await self._send_browser_command("click", {
            "selector": self.SELECTORS["join_button"],
        })

        # Wait for join to complete (may need to click "Ask to join")
        await asyncio.sleep(3.0)

        # Check if we need to ask to join
        ask_button_exists = await self._send_browser_command("exists", {
            "selector": self.SELECTORS["ask_to_join_button"],
        })

        if ask_button_exists:
            await self._send_browser_command("click", {
                "selector": self.SELECTORS["ask_to_join_button"],
            })
            # Wait for host to admit
            logger.info("Waiting to be admitted to the meeting...")

        # Wait for meeting to load
        await asyncio.sleep(5.0)

        # Verify we're in the meeting
        in_meeting = await self._verify_in_meeting()
        if not in_meeting:
            raise RuntimeError("Failed to join meeting")

        # Set up meeting info
        self._meeting_info = MeetingInfo(
            meeting_id=self._meeting_code or "",
            platform=MeetingPlatform.GOOGLE_MEET,
            title=await self._get_meeting_title() or f"Meeting {self._meeting_code}",
            start_time=datetime.utcnow(),
            join_url=meeting_url,
        )

        # Start capturing streams
        await self._start_stream_capture()

        # Start participant observer
        await self._start_participant_observer()

        self._status = BotStatus.CONNECTED
        self._connected_at = datetime.utcnow()

        logger.info(f"Connected to Google Meet: {self._meeting_code}")
        return True

    async def _ensure_authenticated(self) -> bool:
        """Ensure we have valid Google authentication."""
        if self._tokens and not self._tokens.is_expired:
            return True

        # Try to use refresh token
        if self._credentials.refresh_token:
            try:
                self._tokens = await self._oauth.refresh_tokens(
                    self._credentials.refresh_token
                )
                return True
            except Exception as e:
                logger.warning(f"Failed to refresh token: {e}")

        # Try to use existing access token
        if self._credentials.access_token:
            self._tokens = GoogleTokens(
                access_token=self._credentials.access_token,
                refresh_token=self._credentials.refresh_token,
            )
            return True

        logger.error("No valid Google credentials available")
        return False

    async def _start_browser_process(self) -> None:
        """Start Puppeteer browser subprocess."""
        # Path to our Node.js browser controller script
        script_path = Path(__file__).parent / "browser_controller.js"

        if not script_path.exists():
            # Create a placeholder - in production this would be a full implementation
            logger.warning("Browser controller script not found, using mock mode")
            self._mode = GoogleMeetBotMode.MOCK
            return

        # Build command
        cmd = [
            "node",
            str(script_path),
            "--headless" if self._browser_config.headless else "",
        ]

        if self._browser_config.executable_path:
            cmd.extend(["--executable", self._browser_config.executable_path])

        # Start process
        self._browser_process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        # Wait for ready signal
        await asyncio.sleep(2.0)

    async def _send_browser_command(
        self,
        command: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """Send command to browser subprocess."""
        if self._mode == GoogleMeetBotMode.MOCK:
            # Return mock responses
            if command == "exists":
                return False
            return None

        if not self._browser_process:
            raise RuntimeError("Browser process not running")

        message = json.dumps({
            "command": command,
            "params": params or {},
        }) + "\n"

        self._browser_process.stdin.write(message.encode())
        self._browser_process.stdin.flush()

        # Read response
        response_line = self._browser_process.stdout.readline()
        if response_line:
            return json.loads(response_line.decode())
        return None

    async def _verify_in_meeting(self) -> bool:
        """Verify bot is in the meeting."""
        # Check for leave button as indicator
        return await self._send_browser_command("exists", {
            "selector": self.SELECTORS["leave_button"],
        })

    async def _get_meeting_title(self) -> Optional[str]:
        """Get meeting title from page."""
        return await self._send_browser_command("get_text", {
            "selector": "title",
        })

    async def _start_stream_capture(self) -> None:
        """Start capturing audio/video streams."""
        if not self._browser_config.capture_audio and not self._browser_config.capture_video:
            return

        await self._send_browser_command("start_capture", {
            "audio": self._browser_config.capture_audio,
            "video": self._browser_config.capture_video,
            "video_fps": self._browser_config.video_fps,
            "audio_sample_rate": self._browser_config.audio_sample_rate,
        })

    async def _start_participant_observer(self) -> None:
        """Start observing participant changes."""
        await self._send_browser_command("observe_participants", {
            "selector": self.SELECTORS["participant_list"],
        })

    async def disconnect(self) -> bool:
        """
        Disconnect from the meeting.

        Returns:
            True if disconnected successfully.
        """
        if self._status == BotStatus.DISCONNECTED:
            return True

        self._status = BotStatus.DISCONNECTING

        try:
            if self._mode == GoogleMeetBotMode.MOCK:
                return await self._mock_disconnect()
            else:
                return await self._puppeteer_disconnect()

        except Exception as e:
            logger.error(f"Error during disconnect: {e}")
            self._status = BotStatus.ERROR
            return False

    async def _mock_disconnect(self) -> bool:
        """Mock disconnection."""
        logger.info(f"[MOCK] Disconnecting from Google Meet")

        # Cancel mock stream
        if self._mock_stream_task:
            self._mock_stream_task.cancel()
            try:
                await self._mock_stream_task
            except asyncio.CancelledError:
                pass
            self._mock_stream_task = None

        await asyncio.sleep(0.5)

        self._status = BotStatus.DISCONNECTED
        self._meeting_code = None
        self._meeting_info = None
        self._participants.clear()

        logger.info("[MOCK] Disconnected from Google Meet")
        return True

    async def _puppeteer_disconnect(self) -> bool:
        """Disconnect using Puppeteer."""
        logger.info("Disconnecting from Google Meet")

        # Click leave button
        await self._send_browser_command("click", {
            "selector": self.SELECTORS["leave_button"],
        })

        await asyncio.sleep(1.0)

        # Close browser
        if self._browser_process:
            self._browser_process.terminate()
            self._browser_process = None

        self._status = BotStatus.DISCONNECTED
        self._meeting_code = None
        self._meeting_info = None
        self._participants.clear()

        logger.info("Disconnected from Google Meet")
        return True

    # ==================== Audio Stream Methods ====================

    def subscribe_to_audio_stream(
        self,
        callback: AudioCallback,
        participant_id: Optional[str] = None,
    ) -> str:
        """
        Subscribe to audio stream.

        Args:
            callback: Function to receive audio frames.
            participant_id: Filter to specific participant (None for all).

        Returns:
            Subscription ID.
        """
        subscription_id = str(uuid.uuid4())
        self._audio_callbacks[subscription_id] = callback
        logger.debug(f"Audio subscription added: {subscription_id}")
        return subscription_id

    def unsubscribe_from_audio_stream(self, subscription_id: str) -> bool:
        """Unsubscribe from audio stream."""
        if subscription_id in self._audio_callbacks:
            del self._audio_callbacks[subscription_id]
            return True
        return False

    # ==================== Video Stream Methods ====================

    def subscribe_to_video_stream(
        self,
        callback: VideoCallback,
        participant_id: Optional[str] = None,
    ) -> str:
        """
        Subscribe to video stream.

        Args:
            callback: Function to receive video frames.
            participant_id: Filter to specific participant (None for all).

        Returns:
            Subscription ID.
        """
        subscription_id = str(uuid.uuid4())
        self._video_callbacks[subscription_id] = callback
        logger.debug(f"Video subscription added: {subscription_id}")
        return subscription_id

    def unsubscribe_from_video_stream(self, subscription_id: str) -> bool:
        """Unsubscribe from video stream."""
        if subscription_id in self._video_callbacks:
            del self._video_callbacks[subscription_id]
            return True
        return False

    # ==================== Mock Stream Generation ====================

    async def _mock_stream_loop(self) -> None:
        """Generate mock audio/video frames for development."""
        import random

        frame_count = 0

        while self._status == BotStatus.CONNECTED:
            # Generate mock audio frame (every 100ms)
            if self._audio_callbacks:
                audio_frame = AudioFrame(
                    data=bytes(1600),  # 100ms of 16kHz audio
                    sample_rate=16000,
                    channels=1,
                    timestamp=datetime.utcnow(),
                    participant_id="mock_participant",
                    is_speech=random.random() > 0.7,
                )

                for callback in self._audio_callbacks.values():
                    try:
                        callback(audio_frame)
                    except Exception as e:
                        logger.error(f"Audio callback error: {e}")

            # Generate mock video frame (every 66ms for ~15fps)
            if frame_count % 2 == 0 and self._video_callbacks:
                video_frame = VideoFrame(
                    data=bytes(1920 * 1080 * 3),  # RGB frame
                    width=1920,
                    height=1080,
                    format="RGB",
                    timestamp=datetime.utcnow(),
                    participant_id="mock_participant",
                    is_screen_share=False,
                )

                for callback in self._video_callbacks.values():
                    try:
                        callback(video_frame)
                    except Exception as e:
                        logger.error(f"Video callback error: {e}")

            frame_count += 1
            await asyncio.sleep(0.1)  # 10 FPS for audio, 5 FPS for video

    # ==================== Participant Methods ====================

    async def get_participants(self) -> List[ParticipantInfo]:
        """Get list of participants."""
        if self._mode == GoogleMeetBotMode.MOCK:
            return list(self._participants.values())

        # Refresh participant list from browser
        participants_data = await self._send_browser_command("get_participants", {})

        if participants_data:
            self._participants.clear()
            for p in participants_data:
                participant = ParticipantInfo(
                    participant_id=p.get("id", ""),
                    display_name=p.get("name", "Unknown"),
                    is_host=p.get("is_host", False),
                    is_muted=p.get("is_muted", False),
                    is_video_on=p.get("is_video_on", False),
                    is_screen_sharing=p.get("is_presenting", False),
                )
                self._participants[participant.participant_id] = participant

        return list(self._participants.values())

    async def get_participant(self, participant_id: str) -> Optional[ParticipantInfo]:
        """Get specific participant info."""
        return self._participants.get(participant_id)

    async def remove_participant(self, participant_id: str) -> bool:
        """
        Remove participant from meeting.

        Note: Only works if bot is host/moderator.
        """
        if self._mode == GoogleMeetBotMode.MOCK:
            if participant_id in self._participants:
                del self._participants[participant_id]
                return True
            return False

        result = await self._send_browser_command("remove_participant", {
            "participant_id": participant_id,
        })

        return bool(result)

    # ==================== Overlay Methods ====================

    async def show_trust_badge(
        self,
        participant_id: str,
        badge: TrustBadge,
    ) -> bool:
        """
        Show trust badge for a participant.

        In Google Meet, this injects a badge overlay near the participant's video.
        """
        if self._mode == GoogleMeetBotMode.MOCK:
            self._trust_badges[participant_id] = badge
            logger.info(f"[MOCK] Trust badge shown for {participant_id}: {badge.level}")
            return True

        result = await self._send_browser_command("inject_badge", {
            "participant_id": participant_id,
            "level": badge.level.value,
            "label": badge.label,
            "color": badge.color,
        })

        if result:
            self._trust_badges[participant_id] = badge

        return bool(result)

    async def hide_trust_badge(self, participant_id: str) -> bool:
        """Hide trust badge for a participant."""
        if self._mode == GoogleMeetBotMode.MOCK:
            if participant_id in self._trust_badges:
                del self._trust_badges[participant_id]
            return True

        result = await self._send_browser_command("remove_badge", {
            "participant_id": participant_id,
        })

        if result and participant_id in self._trust_badges:
            del self._trust_badges[participant_id]

        return bool(result)

    async def show_alert(self, config: AlertConfig) -> bool:
        """
        Show security alert in meeting.

        Injects an alert overlay into the Google Meet UI.
        """
        if self._mode == GoogleMeetBotMode.MOCK:
            logger.info(f"[MOCK] Alert shown: {config.severity} - {config.title}")
            return True

        result = await self._send_browser_command("show_alert", {
            "severity": config.severity.value,
            "title": config.title,
            "message": config.message,
            "duration": config.duration_seconds,
            "dismissible": config.dismissible,
        })

        return bool(result)

    async def hide_alert(self, alert_id: str) -> bool:
        """Hide an alert."""
        if self._mode == GoogleMeetBotMode.MOCK:
            return True

        return await self._send_browser_command("hide_alert", {
            "alert_id": alert_id,
        })

    async def show_overlay(self, config: OverlayConfig) -> bool:
        """Show custom overlay."""
        if self._mode == GoogleMeetBotMode.MOCK:
            self._active_overlays[config.overlay_id] = config
            logger.info(f"[MOCK] Overlay shown: {config.overlay_id}")
            return True

        result = await self._send_browser_command("show_overlay", {
            "id": config.overlay_id,
            "position": config.position,
            "html": config.html_content,
        })

        if result:
            self._active_overlays[config.overlay_id] = config

        return bool(result)

    async def hide_overlay(self, overlay_id: str) -> bool:
        """Hide custom overlay."""
        if self._mode == GoogleMeetBotMode.MOCK:
            if overlay_id in self._active_overlays:
                del self._active_overlays[overlay_id]
            return True

        result = await self._send_browser_command("hide_overlay", {
            "id": overlay_id,
        })

        if result and overlay_id in self._active_overlays:
            del self._active_overlays[overlay_id]

        return bool(result)

    # ==================== Meeting Control Methods ====================

    async def mute_self(self) -> bool:
        """Mute bot's microphone."""
        if self._mode == GoogleMeetBotMode.MOCK:
            self._is_muted = True
            return True

        if not self._is_muted:
            result = await self._send_browser_command("click", {
                "selector": self.SELECTORS["mute_button"],
            })
            if result:
                self._is_muted = True
            return bool(result)
        return True

    async def unmute_self(self) -> bool:
        """Unmute bot's microphone."""
        if self._mode == GoogleMeetBotMode.MOCK:
            self._is_muted = False
            return True

        if self._is_muted:
            result = await self._send_browser_command("click", {
                "selector": self.SELECTORS["mute_button"],
            })
            if result:
                self._is_muted = False
            return bool(result)
        return True

    async def turn_camera_on(self) -> bool:
        """Turn on bot's camera."""
        if self._mode == GoogleMeetBotMode.MOCK:
            self._is_camera_off = False
            return True

        if self._is_camera_off:
            result = await self._send_browser_command("click", {
                "selector": self.SELECTORS["camera_button"],
            })
            if result:
                self._is_camera_off = False
            return bool(result)
        return True

    async def turn_camera_off(self) -> bool:
        """Turn off bot's camera."""
        if self._mode == GoogleMeetBotMode.MOCK:
            self._is_camera_off = True
            return True

        if not self._is_camera_off:
            result = await self._send_browser_command("click", {
                "selector": self.SELECTORS["camera_button"],
            })
            if result:
                self._is_camera_off = True
            return bool(result)
        return True

    async def send_chat_message(self, message: str) -> bool:
        """Send a chat message in the meeting."""
        if self._mode == GoogleMeetBotMode.MOCK:
            logger.info(f"[MOCK] Chat message sent: {message}")
            return True

        # Open chat if not open
        await self._send_browser_command("click", {
            "selector": self.SELECTORS["chat_button"],
        })
        await asyncio.sleep(0.5)

        # Type message
        await self._send_browser_command("set_text", {
            "selector": self.SELECTORS["chat_input"],
            "value": message,
        })

        # Send
        result = await self._send_browser_command("click", {
            "selector": self.SELECTORS["chat_send"],
        })

        return bool(result)

    # ==================== Properties ====================

    @property
    def meeting_info(self) -> Optional[MeetingInfo]:
        """Get current meeting info."""
        return self._meeting_info

    @property
    def is_muted(self) -> bool:
        """Check if bot is muted."""
        return self._is_muted

    @property
    def is_camera_off(self) -> bool:
        """Check if bot camera is off."""
        return self._is_camera_off

    @property
    def mode(self) -> GoogleMeetBotMode:
        """Get bot operation mode."""
        return self._mode

    # ==================== Cleanup ====================

    async def close(self) -> None:
        """Clean up resources."""
        await self.disconnect()

        if self._http_client and not self._http_client.is_closed:
            await self._http_client.aclose()

        await self._oauth.close()
