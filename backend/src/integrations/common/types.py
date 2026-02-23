"""
Common Types for Platform Integrations

Defines shared data types used across all meeting platform integrations.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional
from uuid import UUID


class MeetingPlatform(str, Enum):
    """Supported meeting platforms."""
    ZOOM = "zoom"
    GOOGLE_MEET = "google_meet"
    TEAMS = "teams"  # Post-MVP


class BotStatus(str, Enum):
    """Bot connection status."""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    IN_WAITING_ROOM = "in_waiting_room"
    IN_MEETING = "in_meeting"
    LEAVING = "leaving"
    ERROR = "error"


class StreamType(str, Enum):
    """Media stream types."""
    AUDIO = "audio"
    VIDEO = "video"
    SCREEN_SHARE = "screen_share"


class AlertSeverity(str, Enum):
    """Alert severity levels for overlays."""
    INFO = "info"
    WARNING = "warning"
    DANGER = "danger"
    CRITICAL = "critical"


class TrustLevel(str, Enum):
    """Participant trust levels for badges."""
    VERIFIED = "verified"
    TRUSTED = "trusted"
    UNKNOWN = "unknown"
    SUSPICIOUS = "suspicious"
    BLOCKED = "blocked"


@dataclass
class BotCredentials:
    """
    Credentials for bot authentication.

    Different platforms require different credentials:
    - Zoom: SDK key/secret or OAuth tokens
    - Google Meet: Service account or OAuth tokens
    - Teams: Azure AD app credentials
    """
    platform: MeetingPlatform

    # OAuth tokens (all platforms)
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    token_expires_at: Optional[datetime] = None

    # Zoom specific
    zoom_sdk_key: Optional[str] = None
    zoom_sdk_secret: Optional[str] = None
    zoom_zak_token: Optional[str] = None  # Zoom Access Key token

    # Google specific
    google_service_account_json: Optional[str] = None
    google_client_id: Optional[str] = None
    google_client_secret: Optional[str] = None

    # Teams specific (post-MVP)
    azure_app_id: Optional[str] = None
    azure_app_secret: Optional[str] = None
    azure_tenant_id: Optional[str] = None

    # Bot display name
    bot_display_name: str = "DeepSafe Security Bot"

    def is_token_expired(self) -> bool:
        """Check if OAuth token is expired."""
        if not self.token_expires_at:
            return True
        return datetime.utcnow() >= self.token_expires_at


@dataclass
class MeetingInfo:
    """
    Information about a meeting.

    Normalized structure across all platforms.
    """
    meeting_id: str  # Platform-specific meeting ID
    platform: MeetingPlatform

    # Meeting details
    topic: Optional[str] = None
    host_id: Optional[str] = None
    host_email: Optional[str] = None
    start_time: Optional[datetime] = None
    scheduled_duration: Optional[int] = None  # Minutes

    # Join information
    join_url: Optional[str] = None
    password: Optional[str] = None

    # Meeting state
    is_recording: bool = False
    is_waiting_room_enabled: bool = False
    participant_count: int = 0

    # Platform-specific data
    platform_data: Dict[str, Any] = field(default_factory=dict)

    # Internal tracking
    internal_id: Optional[UUID] = None  # DeepSafe meeting ID


@dataclass
class ParticipantInfo:
    """
    Information about a meeting participant.

    Normalized structure across all platforms.
    """
    participant_id: str  # Platform-specific participant ID
    platform: MeetingPlatform
    meeting_id: str

    # Identity
    display_name: str
    email: Optional[str] = None
    user_id: Optional[str] = None  # Platform user ID if authenticated

    # Status
    is_host: bool = False
    is_co_host: bool = False
    is_guest: bool = True
    is_authenticated: bool = False

    # Media state
    is_audio_on: bool = False
    is_video_on: bool = False
    is_screen_sharing: bool = False
    is_hand_raised: bool = False

    # DeepSafe tracking
    trust_level: TrustLevel = TrustLevel.UNKNOWN
    risk_score: float = 0.0
    is_verified: bool = False

    # Timing
    joined_at: Optional[datetime] = None
    left_at: Optional[datetime] = None

    # Platform-specific data
    platform_data: Dict[str, Any] = field(default_factory=dict)

    # Internal tracking
    internal_id: Optional[UUID] = None  # DeepSafe participant ID


@dataclass
class AudioFrame:
    """
    Audio frame from meeting stream.

    Contains raw audio data for analysis.
    """
    participant_id: str
    meeting_id: str

    # Audio data
    data: bytes
    sample_rate: int = 16000  # Hz
    channels: int = 1  # Mono
    bits_per_sample: int = 16

    # Timing
    timestamp: datetime = field(default_factory=datetime.utcnow)
    duration_ms: int = 0
    sequence_number: int = 0

    # Metadata
    is_silence: bool = False
    volume_level: float = 0.0  # 0.0 to 1.0

    @property
    def format(self) -> str:
        """Audio format string."""
        return f"{self.sample_rate}Hz/{self.bits_per_sample}bit/{self.channels}ch"


@dataclass
class VideoFrame:
    """
    Video frame from meeting stream.

    Contains raw video data for analysis.
    """
    participant_id: str
    meeting_id: str

    # Video data
    data: bytes
    width: int = 640
    height: int = 480
    format: str = "RGB24"  # RGB24, YUV420, etc.

    # Timing
    timestamp: datetime = field(default_factory=datetime.utcnow)
    frame_number: int = 0
    fps: float = 30.0

    # Metadata
    is_screen_share: bool = False
    has_face_detected: bool = False

    @property
    def resolution(self) -> str:
        """Video resolution string."""
        return f"{self.width}x{self.height}"


@dataclass
class TrustBadge:
    """
    Trust badge configuration for participant overlay.

    Displayed next to participant name in meeting UI.
    """
    participant_id: str
    trust_level: TrustLevel

    # Display
    label: Optional[str] = None  # Custom label text
    tooltip: Optional[str] = None  # Hover text
    icon: Optional[str] = None  # Icon name/URL

    # Styling
    color: Optional[str] = None  # Badge color
    background_color: Optional[str] = None

    # Animation
    is_animated: bool = False
    animation_type: Optional[str] = None  # "pulse", "glow", etc.

    # Visibility
    visible_to_host_only: bool = False
    visible_to_participant: bool = True

    @classmethod
    def verified(cls, participant_id: str) -> "TrustBadge":
        """Create a verified trust badge."""
        return cls(
            participant_id=participant_id,
            trust_level=TrustLevel.VERIFIED,
            label="Verified",
            tooltip="Identity verified by DeepSafe",
            color="#22c55e",  # Green
            icon="shield-check",
        )

    @classmethod
    def suspicious(cls, participant_id: str, reason: str = "") -> "TrustBadge":
        """Create a suspicious trust badge."""
        return cls(
            participant_id=participant_id,
            trust_level=TrustLevel.SUSPICIOUS,
            label="Suspicious",
            tooltip=f"Potential risk detected{': ' + reason if reason else ''}",
            color="#ef4444",  # Red
            icon="shield-alert",
            is_animated=True,
            animation_type="pulse",
        )

    @classmethod
    def unknown(cls, participant_id: str) -> "TrustBadge":
        """Create an unknown trust badge."""
        return cls(
            participant_id=participant_id,
            trust_level=TrustLevel.UNKNOWN,
            label="Unverified",
            tooltip="Identity not yet verified",
            color="#6b7280",  # Gray
            icon="shield-question",
        )


@dataclass
class AlertConfig:
    """
    Alert overlay configuration.

    Displayed to meeting participants when risk is detected.
    """
    alert_id: str
    severity: AlertSeverity

    # Content
    title: str
    message: str
    details: Optional[str] = None

    # Target
    meeting_id: str = ""
    participant_id: Optional[str] = None  # None = show to all
    show_to_host_only: bool = False

    # Timing
    duration_seconds: Optional[int] = None  # None = until dismissed
    auto_dismiss: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)

    # Actions
    actions: List[Dict[str, str]] = field(default_factory=list)
    # Each action: {"id": "verify", "label": "Verify Identity", "style": "primary"}

    # Styling
    icon: Optional[str] = None
    color: Optional[str] = None
    position: str = "top-right"  # "top-right", "top-center", "bottom-right", etc.

    # Sound
    play_sound: bool = True
    sound_type: str = "alert"  # "alert", "warning", "critical"

    @classmethod
    def deepfake_warning(
        cls,
        meeting_id: str,
        participant_id: str,
        confidence: float,
    ) -> "AlertConfig":
        """Create a deepfake detection alert."""
        return cls(
            alert_id=f"deepfake_{participant_id}_{datetime.utcnow().timestamp()}",
            severity=AlertSeverity.DANGER if confidence > 0.8 else AlertSeverity.WARNING,
            title="Potential Deepfake Detected",
            message=f"Suspicious audio/video detected from participant",
            details=f"Confidence: {confidence:.0%}",
            meeting_id=meeting_id,
            participant_id=participant_id,
            show_to_host_only=True,
            actions=[
                {"id": "verify", "label": "Verify Identity", "style": "primary"},
                {"id": "remove", "label": "Remove Participant", "style": "danger"},
                {"id": "dismiss", "label": "Dismiss", "style": "secondary"},
            ],
            icon="video-off",
            color="#ef4444",
        )

    @classmethod
    def social_engineering_warning(
        cls,
        meeting_id: str,
        risk_score: float,
        scenario: str,
    ) -> "AlertConfig":
        """Create a social engineering detection alert."""
        return cls(
            alert_id=f"social_eng_{meeting_id}_{datetime.utcnow().timestamp()}",
            severity=AlertSeverity.CRITICAL if risk_score > 0.85 else AlertSeverity.WARNING,
            title="Social Engineering Risk",
            message=f"Potential {scenario} attempt detected",
            details=f"Risk Score: {risk_score:.0%}",
            meeting_id=meeting_id,
            show_to_host_only=True,
            actions=[
                {"id": "verify_all", "label": "Verify All Participants", "style": "primary"},
                {"id": "end_meeting", "label": "End Meeting", "style": "danger"},
                {"id": "continue", "label": "Continue Monitoring", "style": "secondary"},
            ],
            icon="alert-triangle",
            color="#f59e0b",
        )


@dataclass
class OverlayConfig:
    """
    Meeting overlay configuration.

    Controls the DeepSafe overlay displayed in meetings.
    """
    meeting_id: str

    # Visibility
    enabled: bool = True
    visible_to_all: bool = False  # False = host only

    # Components
    show_trust_badges: bool = True
    show_risk_indicator: bool = True
    show_alert_banner: bool = True

    # Risk indicator
    current_risk_level: str = "low"  # "low", "medium", "high", "critical"
    risk_score: float = 0.0

    # Positioning
    position: str = "top-right"
    minimized: bool = False

    # Styling
    theme: str = "dark"  # "dark", "light", "auto"
    opacity: float = 0.95

    # Callbacks
    on_action: Optional[Callable[[str, Dict], None]] = None


# Type aliases for callbacks
AudioCallback = Callable[[AudioFrame], None]
VideoCallback = Callable[[VideoFrame], None]
ParticipantCallback = Callable[[ParticipantInfo, str], None]  # (participant, event_type)
MeetingCallback = Callable[[MeetingInfo, str], None]  # (meeting, event_type)
