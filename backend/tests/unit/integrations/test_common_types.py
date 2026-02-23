"""Tests for common integration types."""

from datetime import datetime, timedelta

import pytest

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


class TestMeetingPlatformEnum:
    """Tests for MeetingPlatform enum."""

    def test_platform_values(self):
        """Test enum values."""
        assert MeetingPlatform.ZOOM.value == "zoom"
        assert MeetingPlatform.GOOGLE_MEET.value == "google_meet"
        assert MeetingPlatform.TEAMS.value == "teams"

    def test_platform_from_string(self):
        """Test creating enum from string."""
        assert MeetingPlatform("zoom") == MeetingPlatform.ZOOM
        assert MeetingPlatform("google_meet") == MeetingPlatform.GOOGLE_MEET


class TestBotStatusEnum:
    """Tests for BotStatus enum."""

    def test_status_values(self):
        """Test all status values exist."""
        assert BotStatus.DISCONNECTED
        assert BotStatus.CONNECTING
        assert BotStatus.CONNECTED
        assert BotStatus.IN_WAITING_ROOM
        assert BotStatus.IN_MEETING
        assert BotStatus.LEAVING
        assert BotStatus.ERROR


class TestAlertSeverityEnum:
    """Tests for AlertSeverity enum."""

    def test_severity_values(self):
        """Test severity values."""
        assert AlertSeverity.INFO.value == "info"
        assert AlertSeverity.WARNING.value == "warning"
        assert AlertSeverity.DANGER.value == "danger"
        assert AlertSeverity.CRITICAL.value == "critical"


class TestTrustLevelEnum:
    """Tests for TrustLevel enum."""

    def test_trust_level_values(self):
        """Test trust level values."""
        assert TrustLevel.UNKNOWN.value == "unknown"
        assert TrustLevel.TRUSTED.value == "trusted"
        assert TrustLevel.VERIFIED.value == "verified"
        assert TrustLevel.SUSPICIOUS.value == "suspicious"
        assert TrustLevel.BLOCKED.value == "blocked"


class TestBotCredentials:
    """Tests for BotCredentials dataclass."""

    def test_creation_with_required_field(self):
        """Test creating credentials with required field."""
        creds = BotCredentials(platform=MeetingPlatform.ZOOM)
        assert creds.platform == MeetingPlatform.ZOOM
        assert creds.access_token is None
        assert creds.refresh_token is None

    def test_creation_with_zoom_fields(self):
        """Test creating Zoom credentials."""
        creds = BotCredentials(
            platform=MeetingPlatform.ZOOM,
            access_token="access_123",
            refresh_token="refresh_456",
            zoom_sdk_key="sdk_key",
            zoom_sdk_secret="sdk_secret",
        )
        assert creds.zoom_sdk_key == "sdk_key"
        assert creds.zoom_sdk_secret == "sdk_secret"

    def test_creation_with_google_fields(self):
        """Test creating Google credentials."""
        creds = BotCredentials(
            platform=MeetingPlatform.GOOGLE_MEET,
            access_token="access_123",
            google_client_id="client_id",
            google_client_secret="client_secret",
        )
        assert creds.google_client_id == "client_id"
        assert creds.google_client_secret == "client_secret"

    def test_bot_display_name(self):
        """Test bot display name."""
        creds = BotCredentials(
            platform=MeetingPlatform.ZOOM,
            bot_display_name="DeepSafe Bot",
        )
        assert creds.bot_display_name == "DeepSafe Bot"

    def test_is_token_expired_no_expiry(self):
        """Test is_token_expired when no expiry set."""
        creds = BotCredentials(platform=MeetingPlatform.ZOOM)
        assert creds.is_token_expired() is True

    def test_is_token_expired_future(self):
        """Test is_token_expired when expiry is in future."""
        creds = BotCredentials(
            platform=MeetingPlatform.ZOOM,
            token_expires_at=datetime.utcnow() + timedelta(hours=1),
        )
        assert creds.is_token_expired() is False

    def test_is_token_expired_past(self):
        """Test is_token_expired when expiry is in past."""
        creds = BotCredentials(
            platform=MeetingPlatform.ZOOM,
            token_expires_at=datetime.utcnow() - timedelta(hours=1),
        )
        assert creds.is_token_expired() is True


class TestMeetingInfo:
    """Tests for MeetingInfo dataclass."""

    def test_creation(self):
        """Test creating meeting info."""
        info = MeetingInfo(
            meeting_id="123456789",
            platform=MeetingPlatform.ZOOM,
        )
        assert info.meeting_id == "123456789"
        assert info.platform == MeetingPlatform.ZOOM
        assert info.topic is None
        assert info.host_id is None

    def test_full_creation(self):
        """Test creating meeting info with all fields."""
        now = datetime.utcnow()
        info = MeetingInfo(
            meeting_id="123456789",
            platform=MeetingPlatform.ZOOM,
            topic="Test Meeting",
            start_time=now,
            host_id="host_123",
            host_email="host@example.com",
            join_url="https://zoom.us/j/123456789",
            password="abc123",
        )
        assert info.topic == "Test Meeting"
        assert info.start_time == now
        assert info.host_id == "host_123"
        assert info.host_email == "host@example.com"
        assert info.join_url == "https://zoom.us/j/123456789"


class TestParticipantInfo:
    """Tests for ParticipantInfo dataclass."""

    def test_creation(self):
        """Test creating participant info."""
        participant = ParticipantInfo(
            participant_id="p_123",
            platform=MeetingPlatform.ZOOM,
            meeting_id="m_456",
            display_name="Jane Doe",
        )
        assert participant.participant_id == "p_123"
        assert participant.display_name == "Jane Doe"
        assert participant.is_host is False

    def test_full_creation(self):
        """Test creating participant with all fields."""
        now = datetime.utcnow()
        participant = ParticipantInfo(
            participant_id="p_123",
            platform=MeetingPlatform.ZOOM,
            meeting_id="m_456",
            user_id="user_456",
            display_name="Jane Doe",
            email="jane@example.com",
            is_host=True,
            is_audio_on=True,
            is_video_on=False,
            is_screen_sharing=False,
            joined_at=now,
            trust_level=TrustLevel.VERIFIED,
        )
        assert participant.user_id == "user_456"
        assert participant.email == "jane@example.com"
        assert participant.is_host is True
        assert participant.is_audio_on is True
        assert participant.joined_at == now
        assert participant.trust_level == TrustLevel.VERIFIED


class TestAudioFrame:
    """Tests for AudioFrame dataclass."""

    def test_creation(self):
        """Test creating audio frame."""
        frame = AudioFrame(
            participant_id="p_123",
            meeting_id="m_456",
            data=b"\x00" * 1600,
            sample_rate=16000,
            channels=1,
        )
        assert len(frame.data) == 1600
        assert frame.sample_rate == 16000
        assert frame.channels == 1
        assert frame.participant_id == "p_123"

    def test_format_property(self):
        """Test audio format property."""
        frame = AudioFrame(
            participant_id="p_123",
            meeting_id="m_456",
            data=b"\x00" * 1600,
            sample_rate=16000,
            channels=1,
            bits_per_sample=16,
        )
        assert frame.format == "16000Hz/16bit/1ch"


class TestVideoFrame:
    """Tests for VideoFrame dataclass."""

    def test_creation(self):
        """Test creating video frame."""
        frame = VideoFrame(
            participant_id="p_123",
            meeting_id="m_456",
            data=b"\x00" * (640 * 480 * 3),
            width=640,
            height=480,
            format="RGB24",
        )
        assert frame.width == 640
        assert frame.height == 480
        assert frame.format == "RGB24"

    def test_resolution_property(self):
        """Test video resolution property."""
        frame = VideoFrame(
            participant_id="p_123",
            meeting_id="m_456",
            data=b"\x00" * (1920 * 1080 * 3),
            width=1920,
            height=1080,
        )
        assert frame.resolution == "1920x1080"

    def test_with_screen_share(self):
        """Test video frame with screen share flag."""
        frame = VideoFrame(
            participant_id="p_123",
            meeting_id="m_456",
            data=b"\x00" * (1280 * 720 * 3),
            width=1280,
            height=720,
            is_screen_share=True,
        )
        assert frame.is_screen_share is True


class TestTrustBadge:
    """Tests for TrustBadge dataclass."""

    def test_creation(self):
        """Test creating trust badge."""
        badge = TrustBadge(
            participant_id="p_123",
            trust_level=TrustLevel.VERIFIED,
            label="Verified Employee",
        )
        assert badge.trust_level == TrustLevel.VERIFIED
        assert badge.label == "Verified Employee"

    def test_with_styling(self):
        """Test trust badge with styling."""
        badge = TrustBadge(
            participant_id="p_123",
            trust_level=TrustLevel.TRUSTED,
            label="Trusted",
            color="#00FF00",
            icon="shield-check",
        )
        assert badge.color == "#00FF00"
        assert badge.icon == "shield-check"

    def test_verified_factory(self):
        """Test verified badge factory method."""
        badge = TrustBadge.verified("p_123")
        assert badge.trust_level == TrustLevel.VERIFIED
        assert badge.label == "Verified"

    def test_suspicious_factory(self):
        """Test suspicious badge factory method."""
        badge = TrustBadge.suspicious("p_123", "Voice mismatch")
        assert badge.trust_level == TrustLevel.SUSPICIOUS
        assert badge.is_animated is True

    def test_unknown_factory(self):
        """Test unknown badge factory method."""
        badge = TrustBadge.unknown("p_123")
        assert badge.trust_level == TrustLevel.UNKNOWN


class TestAlertConfig:
    """Tests for AlertConfig dataclass."""

    def test_creation(self):
        """Test creating alert config."""
        alert = AlertConfig(
            alert_id="alert_123",
            severity=AlertSeverity.WARNING,
            title="Security Alert",
            message="Suspicious activity detected",
        )
        assert alert.severity == AlertSeverity.WARNING
        assert alert.title == "Security Alert"
        assert alert.message == "Suspicious activity detected"

    def test_with_all_fields(self):
        """Test alert config with all fields."""
        alert = AlertConfig(
            alert_id="alert_123",
            severity=AlertSeverity.CRITICAL,
            title="Critical Alert",
            message="Deepfake detected",
            meeting_id="m_456",
            duration_seconds=30,
            auto_dismiss=False,
            actions=[{"id": "verify", "label": "Verify"}],
        )
        assert alert.duration_seconds == 30
        assert alert.auto_dismiss is False
        assert len(alert.actions) == 1

    def test_deepfake_warning_factory(self):
        """Test deepfake warning factory method."""
        alert = AlertConfig.deepfake_warning(
            meeting_id="m_123",
            participant_id="p_456",
            confidence=0.9,
        )
        assert alert.severity == AlertSeverity.DANGER
        assert "Deepfake" in alert.title
        assert alert.show_to_host_only is True

    def test_social_engineering_warning_factory(self):
        """Test social engineering warning factory method."""
        alert = AlertConfig.social_engineering_warning(
            meeting_id="m_123",
            risk_score=0.9,
            scenario="BEC",
        )
        assert alert.severity == AlertSeverity.CRITICAL
        assert "Social Engineering" in alert.title


class TestOverlayConfig:
    """Tests for OverlayConfig dataclass."""

    def test_creation(self):
        """Test creating overlay config."""
        overlay = OverlayConfig(
            meeting_id="m_123",
        )
        assert overlay.meeting_id == "m_123"
        assert overlay.enabled is True
        assert overlay.show_trust_badges is True

    def test_with_all_fields(self):
        """Test overlay config with all fields."""
        overlay = OverlayConfig(
            meeting_id="m_123",
            enabled=True,
            visible_to_all=True,
            show_trust_badges=True,
            show_risk_indicator=True,
            current_risk_level="high",
            risk_score=0.75,
            position="top-left",
            theme="light",
        )
        assert overlay.visible_to_all is True
        assert overlay.current_risk_level == "high"
        assert overlay.risk_score == 0.75
        assert overlay.position == "top-left"
        assert overlay.theme == "light"
