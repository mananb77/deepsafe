"""
Pytest Configuration and Fixtures

Shared fixtures for all test modules.
"""

import asyncio
from datetime import datetime, timedelta
from typing import AsyncGenerator, Generator
from uuid import uuid4

import pytest
import pytest_asyncio
from sqlalchemy import event
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.shared.config import Settings
from src.shared.database.postgres import Base
from src.shared.models import (
    Company,
    User,
    Meeting,
    Participant,
    Incident,
    Verification,
    RiskIndicator,
    Policy,
    AuditLog,
)
from src.shared.models.company import SubscriptionTier
from src.shared.models.user import UserRole
from src.shared.models.meeting import MeetingPlatform, MeetingStatus, RiskLevel
from src.shared.models.participant import ParticipantRole, TrustLevel
from src.shared.models.incident import IncidentType, IncidentSeverity, IncidentStatus
from src.shared.models.verification import (
    VerificationChannel,
    VerificationStatus,
    VerificationType,
)
from src.shared.models.risk_indicator import IndicatorType, IndicatorSource
from src.shared.models.policy import PolicyType, PolicyTrigger


# Test database URL (using SQLite for fast unit tests)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def test_settings() -> Settings:
    """Create test settings."""
    return Settings(
        environment="testing",
        debug=True,
        secret_key="test-secret-key",
    )


@pytest_asyncio.fixture(scope="function")
async def async_engine() -> AsyncGenerator[AsyncEngine, None]:
    """Create async database engine for tests."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        future=True,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def async_session(
    async_engine: AsyncEngine,
) -> AsyncGenerator[AsyncSession, None]:
    """Create async database session for tests."""
    session_factory = async_sessionmaker(
        async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )

    async with session_factory() as session:
        yield session
        await session.rollback()


# Factory Fixtures
@pytest.fixture
def company_factory():
    """Factory for creating Company instances."""

    def _create_company(**kwargs) -> Company:
        defaults = {
            "id": str(uuid4()),
            "name": f"Test Company {uuid4().hex[:6]}",
            "domain": f"test{uuid4().hex[:6]}.com",
            "subscription_tier": SubscriptionTier.PROFESSIONAL,
            "max_users": 50,
            "max_meetings_per_month": 1000,
            "max_concurrent_meetings": 10,
            "deepfake_detection_enabled": True,
            "social_engineering_detection_enabled": True,
            "verification_enabled": True,
            "sso_enabled": False,
            "default_risk_threshold": 60,
            "auto_record_high_risk": True,
            "is_deleted": False,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        defaults.update(kwargs)
        return Company(**defaults)

    return _create_company


@pytest.fixture
def user_factory(company_factory):
    """Factory for creating User instances."""

    def _create_user(company: Company = None, **kwargs) -> User:
        if company is None:
            company = company_factory()

        defaults = {
            "id": str(uuid4()),
            "email": f"user{uuid4().hex[:6]}@test.com",
            "full_name": "Test User",
            "company_id": company.id,
            "role": UserRole.USER,
            "is_active": True,
            "is_verified": True,
            "hashed_password": "hashed_password_placeholder",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        defaults.update(kwargs)
        return User(**defaults)

    return _create_user


@pytest.fixture
def meeting_factory(company_factory):
    """Factory for creating Meeting instances."""

    def _create_meeting(company: Company = None, **kwargs) -> Meeting:
        if company is None:
            company = company_factory()

        defaults = {
            "id": str(uuid4()),
            "platform": MeetingPlatform.ZOOM,
            "platform_meeting_id": f"meeting_{uuid4().hex[:8]}",
            "company_id": company.id,
            "title": "Test Meeting",
            "status": MeetingStatus.IN_PROGRESS,
            "risk_score": 25.0,
            "risk_level": RiskLevel.LOW,
            "peak_risk_score": 0.0,
            "participant_count": 0,
            "max_participants": 0,
            "deepfake_detected": False,
            "social_engineering_detected": False,
            "verification_triggered": False,
            "is_recorded": False,
            "transcript_available": False,
            "bot_joined": False,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        defaults.update(kwargs)
        return Meeting(**defaults)

    return _create_meeting


@pytest.fixture
def participant_factory(meeting_factory):
    """Factory for creating Participant instances."""

    def _create_participant(meeting: Meeting = None, **kwargs) -> Participant:
        if meeting is None:
            meeting = meeting_factory()

        defaults = {
            "id": str(uuid4()),
            "meeting_id": meeting.id,
            "display_name": f"Participant {uuid4().hex[:6]}",
            "platform_participant_id": f"part_{uuid4().hex[:8]}",
            "role": ParticipantRole.ATTENDEE,
            "trust_level": TrustLevel.UNKNOWN,
            "trust_score": 50.0,
            "deepfake_confidence": 0.0,
            "social_engineering_score": 0.0,
            "composite_risk_score": 0.0,
            "is_deepfake_suspect": False,
            "is_social_engineering_suspect": False,
            "is_verified": False,
            "is_flagged": False,
            "has_video": False,
            "has_audio": False,
            "is_screen_sharing": False,
            "joined_at": datetime.utcnow(),
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        defaults.update(kwargs)
        return Participant(**defaults)

    return _create_participant


@pytest.fixture
def incident_factory(meeting_factory, participant_factory):
    """Factory for creating Incident instances."""

    def _create_incident(
        meeting: Meeting = None,
        participant: Participant = None,
        **kwargs,
    ) -> Incident:
        if meeting is None:
            meeting = meeting_factory()
        if participant is None:
            participant = participant_factory(meeting=meeting)

        defaults = {
            "id": str(uuid4()),
            "meeting_id": meeting.id,
            "participant_id": participant.id,
            "incident_type": IncidentType.AUDIO_DEEPFAKE,
            "severity": IncidentSeverity.MEDIUM,
            "status": IncidentStatus.DETECTED,
            "title": "Test Incident",
            "description": "Test incident description",
            "confidence_score": 0.85,
            "detected_at": datetime.utcnow(),
            "verification_triggered": False,
            "alert_sent": False,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        defaults.update(kwargs)
        return Incident(**defaults)

    return _create_incident


@pytest.fixture
def verification_factory(participant_factory):
    """Factory for creating Verification instances."""

    def _create_verification(participant: Participant = None, **kwargs) -> Verification:
        if participant is None:
            participant = participant_factory()

        defaults = {
            "id": str(uuid4()),
            "participant_id": participant.id,
            "verification_type": VerificationType.IDENTITY,
            "channel": VerificationChannel.SMS,
            "destination": "+15551234567",
            "status": VerificationStatus.PENDING,
            "verification_code": "123456",
            "expires_at": datetime.utcnow() + timedelta(minutes=5),
            "max_attempts": 3,
            "attempt_count": 0,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        defaults.update(kwargs)
        return Verification(**defaults)

    return _create_verification


@pytest.fixture
def risk_indicator_factory(meeting_factory, participant_factory):
    """Factory for creating RiskIndicator instances."""

    def _create_risk_indicator(
        meeting: Meeting = None,
        participant: Participant = None,
        **kwargs,
    ) -> RiskIndicator:
        if meeting is None:
            meeting = meeting_factory()
        if participant is None:
            participant = participant_factory(meeting=meeting)

        defaults = {
            "id": str(uuid4()),
            "meeting_id": meeting.id,
            "participant_id": participant.id,
            "indicator_type": IndicatorType.AUDIO_DEEPFAKE,
            "source": IndicatorSource.RESEMBLE_AI,
            "confidence": 0.85,
            "weight": 0.8,
            "title": "Audio Deepfake Detected",
            "detected_at": datetime.utcnow(),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        defaults.update(kwargs)
        return RiskIndicator(**defaults)

    return _create_risk_indicator


@pytest.fixture
def policy_factory(company_factory):
    """Factory for creating Policy instances."""

    def _create_policy(company: Company = None, **kwargs) -> Policy:
        if company is None:
            company = company_factory()

        defaults = {
            "id": str(uuid4()),
            "company_id": company.id,
            "name": "Test Policy",
            "description": "Test policy description",
            "policy_type": PolicyType.RISK_THRESHOLD,
            "trigger": PolicyTrigger.RISK_SCORE_CHANGE,
            "is_enabled": True,
            "priority": 100,
            "conditions": {},
            "actions": [],
            "min_risk_score": 60.0,
            "trigger_count": 0,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        defaults.update(kwargs)
        return Policy(**defaults)

    return _create_policy


@pytest.fixture
def audit_log_factory(user_factory):
    """Factory for creating AuditLog instances."""

    def _create_audit_log(user: User = None, **kwargs) -> AuditLog:
        from src.shared.models.audit_log import AuditAction, AuditCategory

        defaults = {
            "id": str(uuid4()),
            "user_id": user.id if user else None,
            "action": AuditAction.LOGIN,
            "category": AuditCategory.AUTHENTICATION,
            "description": "User logged in",
            "is_sensitive": False,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        defaults.update(kwargs)
        return AuditLog(**defaults)

    return _create_audit_log
