#!/usr/bin/env python3
"""
Seed script for local development.

Creates a test company, admin user, sample policies, and a few meetings
so the frontend has data to display when running in live mode.

Usage:
    python scripts/seed.py                     # Use default DATABASE_URL
    DATABASE_URL=... python scripts/seed.py    # Override DB URL
"""

import asyncio
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from uuid import uuid4

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from src.shared.database.postgres import Base
from src.shared.models import (
    Company,
    User,
    Meeting,
    Participant,
    Policy,
)
from src.shared.models.company import SubscriptionTier
from src.shared.models.user import UserRole
from src.shared.models.meeting import MeetingPlatform, MeetingStatus, RiskLevel
from src.shared.models.participant import ParticipantRole, TrustLevel
from src.shared.models.policy import PolicyType, PolicyTrigger
from src.shared.security.password import hash_password


DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://deepsafe:deepsafe@localhost:5432/deepsafe",
)

# Stable IDs for idempotent seeding
COMPANY_ID = "00000000-0000-4000-8000-000000000001"
ADMIN_USER_ID = "00000000-0000-4000-8000-000000000002"
ANALYST_USER_ID = "00000000-0000-4000-8000-000000000003"


async def seed(session: AsyncSession) -> None:
    """Seed development data."""
    now = datetime.utcnow()

    # ── Company ──────────────────────────────────────────────
    company = Company(
        id=COMPANY_ID,
        name="DeepSafe Demo Corp",
        domain="deepsafe-demo.com",
        subscription_tier=SubscriptionTier.ENTERPRISE,
        max_users=100,
        max_meetings_per_month=10000,
        max_concurrent_meetings=50,
        deepfake_detection_enabled=True,
        social_engineering_detection_enabled=True,
        verification_enabled=True,
        sso_enabled=False,
        default_risk_threshold=65,
        auto_record_high_risk=True,
        is_deleted=False,
        created_at=now,
        updated_at=now,
    )
    session.add(company)

    # ── Users ────────────────────────────────────────────────
    admin = User(
        id=ADMIN_USER_ID,
        company_id=COMPANY_ID,
        email="admin@deepsafe-demo.com",
        full_name="Admin User",
        role=UserRole.ADMIN,
        hashed_password=hash_password("admin123"),
        is_active=True,
        is_verified=True,
        created_at=now,
        updated_at=now,
    )
    session.add(admin)

    analyst = User(
        id=ANALYST_USER_ID,
        company_id=COMPANY_ID,
        email="analyst@deepsafe-demo.com",
        full_name="Security Analyst",
        role=UserRole.ANALYST,
        hashed_password=hash_password("analyst123"),
        is_active=True,
        is_verified=True,
        created_at=now,
        updated_at=now,
    )
    session.add(analyst)

    # ── Meetings ─────────────────────────────────────────────
    meetings_data = [
        {
            "platform": MeetingPlatform.ZOOM,
            "title": "Q1 Board Review",
            "host_email": "cfo@deepsafe-demo.com",
            "status": MeetingStatus.COMPLETED,
            "risk_score": 12.0,
            "risk_level": RiskLevel.LOW,
            "participant_count": 8,
            "offset_hours": -48,
            "duration_hours": 1.5,
        },
        {
            "platform": MeetingPlatform.GOOGLE_MEET,
            "title": "Vendor Onboarding Call",
            "host_email": "procurement@deepsafe-demo.com",
            "status": MeetingStatus.COMPLETED,
            "risk_score": 45.0,
            "risk_level": RiskLevel.MEDIUM,
            "participant_count": 4,
            "deepfake_detected": False,
            "social_engineering_detected": True,
            "offset_hours": -24,
            "duration_hours": 0.75,
        },
        {
            "platform": MeetingPlatform.ZOOM,
            "title": "Wire Transfer Authorization",
            "host_email": "cfo@deepsafe-demo.com",
            "status": MeetingStatus.COMPLETED,
            "risk_score": 78.0,
            "risk_level": RiskLevel.HIGH,
            "participant_count": 3,
            "deepfake_detected": True,
            "verification_triggered": True,
            "offset_hours": -6,
            "duration_hours": 0.5,
        },
        {
            "platform": MeetingPlatform.GOOGLE_MEET,
            "title": "IT Support Session",
            "host_email": "it@deepsafe-demo.com",
            "status": MeetingStatus.IN_PROGRESS,
            "risk_score": 32.0,
            "risk_level": RiskLevel.MEDIUM,
            "participant_count": 2,
            "bot_joined": True,
            "offset_hours": 0,
            "duration_hours": None,
        },
        {
            "platform": MeetingPlatform.ZOOM,
            "title": "All Hands Standup",
            "host_email": "admin@deepsafe-demo.com",
            "status": MeetingStatus.SCHEDULED,
            "risk_score": 0.0,
            "risk_level": RiskLevel.LOW,
            "participant_count": 0,
            "offset_hours": 2,
            "duration_hours": 1,
        },
    ]

    meeting_ids = []
    for m in meetings_data:
        mid = str(uuid4())
        meeting_ids.append(mid)
        offset = timedelta(hours=m["offset_hours"])
        start = now + offset
        end = (
            start + timedelta(hours=m["duration_hours"])
            if m["duration_hours"]
            else None
        )

        meeting = Meeting(
            id=mid,
            company_id=COMPANY_ID,
            platform=m["platform"],
            platform_meeting_id=str(uuid4())[:12],
            title=m["title"],
            host_email=m["host_email"],
            status=m["status"],
            risk_score=m["risk_score"],
            risk_level=m["risk_level"],
            peak_risk_score=m["risk_score"],
            participant_count=m["participant_count"],
            max_participants=20,
            deepfake_detected=m.get("deepfake_detected", False),
            social_engineering_detected=m.get("social_engineering_detected", False),
            verification_triggered=m.get("verification_triggered", False),
            bot_joined=m.get("bot_joined", False),
            is_recorded=False,
            transcript_available=False,
            scheduled_start_at=start,
            scheduled_end_at=end,
            actual_start_at=start if m["status"] != MeetingStatus.SCHEDULED else None,
            actual_end_at=end if m["status"] == MeetingStatus.COMPLETED else None,
            created_at=now,
            updated_at=now,
        )
        session.add(meeting)

    # ── Sample Participants ──────────────────────────────────
    participant_names = [
        ("Alice Chen", "alice@deepsafe-demo.com", TrustLevel.TRUSTED),
        ("Bob Martinez", "bob@vendor.com", TrustLevel.UNKNOWN),
        ("Eve Black", "eve@unknown.com", TrustLevel.SUSPICIOUS),
    ]

    # Add participants to the completed high-risk meeting
    high_risk_meeting_id = meeting_ids[2]
    for name, email, trust in participant_names:
        session.add(Participant(
            id=str(uuid4()),
            meeting_id=high_risk_meeting_id,
            display_name=name,
            platform_participant_id=str(uuid4())[:12],
            email=email,
            role=ParticipantRole.ATTENDEE,
            trust_level=trust,
            trust_score=80.0 if trust == TrustLevel.TRUSTED else 30.0,
            deepfake_confidence=0.85 if trust == TrustLevel.SUSPICIOUS else 0.05,
            social_engineering_score=0.1,
            composite_risk_score=0.78 if trust == TrustLevel.SUSPICIOUS else 0.12,
            is_deepfake_suspect=trust == TrustLevel.SUSPICIOUS,
            is_flagged=trust == TrustLevel.SUSPICIOUS,
            flag_reason="Voice pattern anomaly detected" if trust == TrustLevel.SUSPICIOUS else None,
            is_verified=trust == TrustLevel.TRUSTED,
            has_video=True,
            has_audio=True,
            is_screen_sharing=False,
            joined_at=now - timedelta(hours=6),
            left_at=now - timedelta(hours=5, minutes=30),
            is_active=False,
            created_at=now,
            updated_at=now,
        ))

    # ── Policies ─────────────────────────────────────────────
    policies = [
        {
            "name": "High Risk Auto-Verify",
            "description": "Trigger identity verification when risk exceeds 65%",
            "policy_type": PolicyType.RISK_THRESHOLD,
            "trigger": PolicyTrigger.RISK_SCORE_CHANGE,
            "conditions": {"risk_threshold": 65},
            "actions": [
                {"action": "verify", "channels": ["sms", "push"]},
                {"action": "alert", "channels": ["websocket", "email"]},
            ],
            "min_risk_score": 65.0,
        },
        {
            "name": "Deepfake Detection Response",
            "description": "Immediate response when deepfake is detected",
            "policy_type": PolicyType.INCIDENT_RESPONSE,
            "trigger": PolicyTrigger.DEEPFAKE_DETECTED,
            "conditions": {"confidence_threshold": 70},
            "actions": [
                {"action": "verify", "channels": ["sms", "callback"]},
                {"action": "record", "target": "meeting"},
                {"action": "alert", "channels": ["websocket", "sms", "email"]},
            ],
            "min_risk_score": 0.0,
        },
        {
            "name": "Critical Risk Auto-Intervention",
            "description": "Automatic intervention for critical risk events",
            "policy_type": PolicyType.RISK_THRESHOLD,
            "trigger": PolicyTrigger.RISK_SCORE_CHANGE,
            "conditions": {"risk_threshold": 85},
            "actions": [
                {"action": "alert", "channels": ["websocket", "sms", "callback"]},
                {"action": "hold", "duration_hours": 24},
                {"action": "require_approval", "approvers": ["admin"]},
            ],
            "min_risk_score": 85.0,
        },
    ]

    for p in policies:
        session.add(Policy(
            id=str(uuid4()),
            company_id=COMPANY_ID,
            name=p["name"],
            description=p["description"],
            policy_type=p["policy_type"],
            trigger=p["trigger"],
            is_enabled=True,
            priority=100,
            conditions=p["conditions"],
            actions=p["actions"],
            min_risk_score=p["min_risk_score"],
            trigger_count=0,
            created_at=now,
            updated_at=now,
        ))

    await session.commit()
    print("Seed data created successfully!")
    print(f"  Company: DeepSafe Demo Corp ({COMPANY_ID})")
    print(f"  Admin:   admin@deepsafe-demo.com / admin123")
    print(f"  Analyst: analyst@deepsafe-demo.com / analyst123")
    print(f"  Meetings: {len(meetings_data)} seeded")
    print(f"  Policies: {len(policies)} seeded")


async def main():
    print(f"Connecting to: {DATABASE_URL}")
    engine = create_async_engine(DATABASE_URL, echo=False)

    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Tables ensured")

    session_factory = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with session_factory() as session:
        await seed(session)

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
