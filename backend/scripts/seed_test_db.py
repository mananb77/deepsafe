#!/usr/bin/env python3
"""
Seed script for test database.

Creates all tables and populates with test data matching test fixtures.
"""

import asyncio
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import text

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
from src.shared.models.verification import VerificationChannel, VerificationStatus, VerificationType
from src.shared.models.risk_indicator import IndicatorType, IndicatorSource
from src.shared.models.policy import PolicyType, PolicyTrigger
from src.shared.security.password import hash_password

# Test database URL - PostgreSQL
TEST_DATABASE_URL = "postgresql+asyncpg://deepsafe:deepsafe@localhost:5432/deepsafe_test"

# Test data IDs (matching conftest.py fixtures)
TEST_COMPANY_ID = "550e8400-e29b-41d4-a716-446655440000"
TEST_USER_ID = "550e8400-e29b-41d4-a716-446655440001"
TEST_MEETING_ID = "550e8400-e29b-41d4-a716-446655440002"
TEST_PARTICIPANT_ID = "550e8400-e29b-41d4-a716-446655440003"
TEST_INCIDENT_ID = "550e8400-e29b-41d4-a716-446655440004"
TEST_VERIFICATION_ID = "550e8400-e29b-41d4-a716-446655440005"
TEST_POLICY_ID = "550e8400-e29b-41d4-a716-446655440006"


async def create_tables(engine):
    """Create all tables."""
    async with engine.begin() as conn:
        # Drop all tables first for clean slate
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    print("Tables created successfully")


async def seed_data(session: AsyncSession):
    """Seed test data."""
    now = datetime.utcnow()

    # Create test company
    company = Company(
        id=TEST_COMPANY_ID,
        name="Test Company",
        domain="testcompany.com",
        subscription_tier=SubscriptionTier.PROFESSIONAL,
        max_users=50,
        max_meetings_per_month=500,
        max_concurrent_meetings=10,
        deepfake_detection_enabled=True,
        social_engineering_detection_enabled=True,
        verification_enabled=True,
        sso_enabled=False,
        default_risk_threshold=60,
        auto_record_high_risk=True,
        is_deleted=False,
        created_at=now,
        updated_at=now,
    )
    session.add(company)
    print(f"Created company: {company.name} ({company.id})")

    # Create test user
    user = User(
        id=TEST_USER_ID,
        company_id=TEST_COMPANY_ID,
        email="testuser@testcompany.com",
        full_name="Test User",
        role=UserRole.ADMIN,
        hashed_password=hash_password("testpassword123"),
        is_active=True,
        is_verified=True,
        created_at=now,
        updated_at=now,
    )
    session.add(user)
    print(f"Created user: {user.email} ({user.id})")

    # Create test meeting
    meeting = Meeting(
        id=TEST_MEETING_ID,
        company_id=TEST_COMPANY_ID,
        platform=MeetingPlatform.ZOOM,
        platform_meeting_id="123456789",
        title="Test Meeting",
        host_email="host@testcompany.com",
        status=MeetingStatus.SCHEDULED,
        risk_score=25.0,
        risk_level=RiskLevel.LOW,
        peak_risk_score=25.0,
        participant_count=2,
        max_participants=10,
        deepfake_detected=False,
        social_engineering_detected=False,
        verification_triggered=False,
        is_recorded=False,
        transcript_available=False,
        bot_joined=False,
        scheduled_start_at=now + timedelta(hours=1),
        scheduled_end_at=now + timedelta(hours=2),
        created_at=now,
        updated_at=now,
    )
    session.add(meeting)
    print(f"Created meeting: {meeting.title} ({meeting.id})")

    # Create test participant
    participant = Participant(
        id=TEST_PARTICIPANT_ID,
        meeting_id=TEST_MEETING_ID,
        user_id=TEST_USER_ID,
        display_name="Test Participant",
        platform_participant_id="part_test123",
        email="participant@testcompany.com",
        role=ParticipantRole.ATTENDEE,
        trust_level=TrustLevel.TRUSTED,
        trust_score=80.0,
        deepfake_confidence=0.0,
        social_engineering_score=0.0,
        composite_risk_score=10.0,
        is_deepfake_suspect=False,
        is_social_engineering_suspect=False,
        is_verified=True,
        is_flagged=False,
        has_video=True,
        has_audio=True,
        is_screen_sharing=False,
        joined_at=now,
        is_active=True,
        created_at=now,
        updated_at=now,
    )
    session.add(participant)
    print(f"Created participant: {participant.display_name} ({participant.id})")

    # Create test incident
    incident = Incident(
        id=TEST_INCIDENT_ID,
        meeting_id=TEST_MEETING_ID,
        participant_id=TEST_PARTICIPANT_ID,
        incident_type=IncidentType.AUDIO_DEEPFAKE,
        severity=IncidentSeverity.HIGH,
        status=IncidentStatus.DETECTED,
        title="Potential Audio Deepfake Detected",
        description="Analysis indicates potential voice cloning",
        confidence_score=85.5,
        detected_at=now,
        verification_triggered=False,
        alert_sent=False,
        created_at=now,
        updated_at=now,
    )
    session.add(incident)
    print(f"Created incident: {incident.title} ({incident.id})")

    # Create test verification
    verification = Verification(
        id=TEST_VERIFICATION_ID,
        participant_id=TEST_PARTICIPANT_ID,
        verification_type=VerificationType.IDENTITY,
        channel=VerificationChannel.SMS,
        destination="+15551234567",
        status=VerificationStatus.PENDING,
        verification_code="123456",
        expires_at=now + timedelta(minutes=5),
        max_attempts=3,
        attempt_count=0,
        created_at=now,
        updated_at=now,
    )
    session.add(verification)
    print(f"Created verification: {verification.id}")

    # Create test policy
    policy = Policy(
        id=TEST_POLICY_ID,
        company_id=TEST_COMPANY_ID,
        name="High Risk Alert Policy",
        description="Alert when risk score exceeds threshold",
        policy_type=PolicyType.RISK_THRESHOLD,
        trigger=PolicyTrigger.RISK_SCORE_CHANGE,
        is_enabled=True,
        priority=100,
        conditions={"risk_threshold": 80},
        actions=[{"action": "alert", "channels": ["email", "push"]}],
        min_risk_score=80.0,
        trigger_count=0,
        created_at=now,
        updated_at=now,
    )
    session.add(policy)
    print(f"Created policy: {policy.name} ({policy.id})")

    await session.commit()
    print("\nAll test data seeded successfully!")


async def main():
    """Main seed function."""
    print(f"Connecting to: {TEST_DATABASE_URL}")

    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
    )

    # Create tables
    await create_tables(engine)

    # Create session and seed data
    async_session_maker = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with async_session_maker() as session:
        await seed_data(session)

    await engine.dispose()
    print("\nDatabase seeded successfully!")


if __name__ == "__main__":
    asyncio.run(main())
