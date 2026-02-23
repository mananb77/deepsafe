"""
Detection Test Configuration

Shared fixtures and utilities for detection service tests.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch


# --- Audio Fixtures ---

@pytest.fixture
def sample_audio_data() -> bytes:
    """Sample audio data for testing."""
    # Generate 1 second of silence at 16kHz
    import struct
    samples = [0] * 16000
    return struct.pack(f'{len(samples)}h', *samples)


@pytest.fixture
def sample_audio_chunk():
    """Sample AudioChunk for testing."""
    from src.services.detection.base import AudioChunk
    import struct
    samples = [0] * 16000
    return AudioChunk(
        data=struct.pack(f'{len(samples)}h', *samples),
        sample_rate=16000,
        channels=1,
        timestamp=0.0,
        duration=1.0,
    )


# --- Video Fixtures ---

@pytest.fixture
def sample_frame_data() -> bytes:
    """Sample video frame data (JPEG-like bytes)."""
    # Minimal JPEG header for testing
    return b'\xff\xd8\xff\xe0' + b'\x00' * 100 + b'\xff\xd9'


@pytest.fixture
def sample_video_frame():
    """Sample VideoFrame for testing."""
    from src.services.detection.base import VideoFrame
    return VideoFrame(
        data=b'\xff\xd8\xff\xe0' + b'\x00' * 100 + b'\xff\xd9',
        width=640,
        height=480,
        timestamp=0.0,
        frame_number=0,
    )


@pytest.fixture
def sample_facial_landmarks():
    """Sample facial landmarks for testing."""
    from src.services.detection.video import FacialLandmarks
    # 68 random points representing facial landmarks
    points = [(100.0 + i * 2, 100.0 + i * 1.5) for i in range(68)]
    return FacialLandmarks(points=points, frame_number=0, timestamp=0.0)


@pytest.fixture
def sample_face_region():
    """Sample face region for testing."""
    from src.services.detection.video import FaceRegion
    return FaceRegion(
        frame_number=0,
        timestamp=0.0,
        eye_aspect_ratio_left=0.3,
        eye_aspect_ratio_right=0.3,
        mouth_aspect_ratio=0.5,
        eyebrow_position_left=0.2,
        eyebrow_position_right=0.2,
    )


@pytest.fixture
def sample_lighting_data():
    """Sample lighting data for testing."""
    from src.services.detection.video import FrameLightingData
    return FrameLightingData(
        frame_number=0,
        timestamp=0.0,
        face_brightness=128.0,
        face_contrast=30.0,
        face_color_temp=5500.0,
        background_brightness=120.0,
        background_contrast=25.0,
        background_color_temp=5400.0,
        shadow_direction=(0.5, -0.5),
        shadow_intensity=0.6,
        highlight_positions=[(0.3, 0.2)],
        specular_intensity=0.4,
    )


# --- Social Engineering Fixtures ---

@pytest.fixture
def sample_transcript_benign() -> str:
    """Sample benign meeting transcript."""
    return """
    John: Hi everyone, thanks for joining the weekly sync.
    Sarah: Happy to be here. Let's go over the project updates.
    John: Sure. We made good progress on the frontend this week.
    Sarah: Great. I'll send the report after the meeting.
    John: Thanks Sarah. Any questions before we wrap up?
    Sarah: No, all clear. Talk next week.
    """


@pytest.fixture
def sample_transcript_suspicious() -> str:
    """Sample suspicious meeting transcript."""
    return """
    CEO: This is the CEO speaking. I need you to process an urgent wire transfer.
    Employee: Oh, hello sir. What transfer?
    CEO: We have a confidential acquisition happening. Don't tell anyone about this.
    CEO: I need you to wire $250,000 to this new account immediately.
    CEO: The deadline is today. This is extremely urgent and must be done right now.
    Employee: Should I verify this with the CFO?
    CEO: No, this is between us. I'm authorizing this directly. Just do it now.
    """


@pytest.fixture
def sample_participant_profile():
    """Sample participant profile for testing."""
    from src.services.detection.social_engineering import ParticipantProfile
    return ParticipantProfile(
        name="John Smith",
        email="john.smith@company.com",
        claimed_role="Software Engineer",
        claimed_company="Company Inc",
        is_external=False,
    )


@pytest.fixture
def sample_participant_profile_suspicious():
    """Sample suspicious participant profile."""
    from src.services.detection.social_engineering import ParticipantProfile
    return ParticipantProfile(
        name="CEO John",
        email="ceo.john@gmail.com",
        claimed_role="CEO",
        claimed_company="Company Inc",
        is_external=True,
    )


@pytest.fixture
def sample_meeting_metadata():
    """Sample meeting metadata for testing."""
    from src.services.detection.social_engineering import MeetingMetadata
    from datetime import datetime
    return MeetingMetadata(
        meeting_id="test-meeting-123",
        scheduled_time=datetime.now(),
        scheduled_lead_time_hours=24.0,
        is_recurring=True,
        platform="zoom",
    )


@pytest.fixture
def sample_conversation_turns():
    """Sample conversation turns for testing."""
    from src.services.detection.social_engineering import ConversationTurn
    return [
        ConversationTurn(speaker="John", text="Let's discuss the project", timestamp=0.0),
        ConversationTurn(speaker="Sarah", text="Sure, I have some updates", timestamp=2.0),
        ConversationTurn(speaker="John", text="Go ahead", timestamp=4.0),
    ]


# --- Mock Fixtures ---

@pytest.fixture
def mock_resemble_client():
    """Mock Resemble AI client."""
    with patch('src.services.detection.audio.resemble_client.ResembleAIClient') as mock:
        client = mock.return_value
        client.analyze = AsyncMock(return_value={
            "is_synthetic": False,
            "confidence": 15.0,
            "model_detected": None,
        })
        client.health_check = AsyncMock(return_value=True)
        client.close = AsyncMock()
        yield client


@pytest.fixture
def mock_sensity_client():
    """Mock Sensity API client."""
    with patch('src.services.detection.video.sensity_client.SensityClient') as mock:
        client = mock.return_value
        client.analyze = AsyncMock(return_value={
            "is_deepfake": False,
            "confidence": 10.0,
            "manipulation_type": None,
        })
        client.analyze_video = AsyncMock(return_value={
            "is_deepfake": False,
            "confidence": 10.0,
            "frames_analyzed": 5,
            "frames_with_deepfake": 0,
        })
        client.health_check = AsyncMock(return_value=True)
        client.close = AsyncMock()
        yield client


@pytest.fixture
def mock_gpt4_client():
    """Mock GPT-4 analyzer."""
    with patch('src.services.detection.social_engineering.gpt4_analyzer.GPT4Analyzer') as mock:
        client = mock.return_value
        client.analyze = AsyncMock(return_value=MagicMock(
            is_suspicious=False,
            confidence=20.0,
            intent_classification="legitimate",
            manipulation_tactics=[],
            risk_assessment="low",
            reasoning="Normal conversation",
            recommendations=[],
            details={},
        ))
        yield client
