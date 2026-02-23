"""
API Test Fixtures

Shared fixtures for API unit tests.
"""

import asyncio
from datetime import datetime, timedelta
from typing import AsyncGenerator, Generator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from src.shared.models.base import Base
from src.shared.models.user import User, UserRole
from src.shared.models.company import Company, SubscriptionTier
from src.shared.models.meeting import Meeting, MeetingPlatform, MeetingStatus
from src.shared.models.participant import Participant, TrustLevel
from src.shared.models.incident import Incident, IncidentType, IncidentSeverity, IncidentStatus
from src.shared.security.jwt import create_access_token
from src.shared.security.password import hash_password


# Test database URL - kept for reference but tests use mocks
TEST_DATABASE_URL = "postgresql+asyncpg://deepsafe:deepsafe@localhost:5432/deepsafe_test"


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
def sync_engine():
    """Create sync database engine for TestClient (which uses synchronous calls).

    Uses seeded test data from scripts/seed_test_db.py.
    """
    from sqlalchemy import create_engine
    # Use sync driver for synchronous TestClient
    sync_url = TEST_DATABASE_URL.replace("+asyncpg", "")
    engine = create_engine(sync_url, echo=False)
    yield engine
    engine.dispose()


@pytest.fixture(scope="function")
async def async_engine():
    """Create async test database engine with PostgreSQL.

    Uses seeded test data from scripts/seed_test_db.py.
    Does not drop/recreate tables to preserve seeded data.
    """
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        pool_size=5,
        max_overflow=0,
    )

    yield engine

    await engine.dispose()


@pytest.fixture(scope="function")
async def async_session(async_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create async test database session."""
    async_session_maker = async_sessionmaker(
        async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with async_session_maker() as session:
        yield session
        await session.rollback()


@pytest.fixture
def test_company_data() -> dict:
    """Test company data."""
    return {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "name": "Test Company",
        "domain": "testcompany.com",
        "subscription_tier": SubscriptionTier.PROFESSIONAL,
        "max_users": 50,
        "max_meetings_per_month": 500,
    }


@pytest.fixture
def test_user_data(test_company_data) -> dict:
    """Test user data."""
    return {
        "id": "550e8400-e29b-41d4-a716-446655440001",
        "company_id": test_company_data["id"],
        "email": "testuser@testcompany.com",
        "first_name": "Test",
        "last_name": "User",
        "role": UserRole.ADMIN,
        "password_hash": hash_password("testpassword123"),
        "is_active": True,
        "is_verified": True,
    }


@pytest.fixture
def test_meeting_data(test_company_data) -> dict:
    """Test meeting data."""
    return {
        "id": "550e8400-e29b-41d4-a716-446655440002",
        "company_id": test_company_data["id"],
        "platform": MeetingPlatform.ZOOM,
        "platform_meeting_id": "123456789",
        "title": "Test Meeting",
        "description": "A test meeting for unit tests",
        "host_email": "host@testcompany.com",
        "status": MeetingStatus.SCHEDULED,
        "scheduled_start_at": datetime.utcnow() + timedelta(hours=1),
        "scheduled_end_at": datetime.utcnow() + timedelta(hours=2),
    }


@pytest.fixture
def test_participant_data(test_meeting_data, test_user_data) -> dict:
    """Test participant data."""
    return {
        "id": "550e8400-e29b-41d4-a716-446655440003",
        "meeting_id": test_meeting_data["id"],
        "user_id": test_user_data["id"],
        "display_name": "Test Participant",
        "email": "participant@testcompany.com",
        "role": "attendee",
        "trust_level": TrustLevel.TRUSTED,
    }


@pytest.fixture
def test_incident_data(test_meeting_data, test_participant_data) -> dict:
    """Test incident data."""
    return {
        "id": "550e8400-e29b-41d4-a716-446655440004",
        "meeting_id": test_meeting_data["id"],
        "participant_id": test_participant_data["id"],
        "incident_type": IncidentType.AUDIO_DEEPFAKE,
        "severity": IncidentSeverity.HIGH,
        "title": "Potential Audio Deepfake Detected",
        "description": "Analysis indicates potential voice cloning",
        "confidence_score": 85.5,
    }


@pytest.fixture
async def test_company(async_session, test_company_data) -> Company:
    """Create test company in database."""
    company = Company(**test_company_data)
    async_session.add(company)
    await async_session.commit()
    await async_session.refresh(company)
    return company


@pytest.fixture
async def test_user(async_session, test_company, test_user_data) -> User:
    """Create test user in database."""
    user = User(**test_user_data)
    async_session.add(user)
    await async_session.commit()
    await async_session.refresh(user)
    return user


@pytest.fixture
async def test_meeting(async_session, test_company, test_meeting_data) -> Meeting:
    """Create test meeting in database."""
    meeting = Meeting(**test_meeting_data)
    async_session.add(meeting)
    await async_session.commit()
    await async_session.refresh(meeting)
    return meeting


@pytest.fixture
async def test_participant(async_session, test_meeting, test_participant_data) -> Participant:
    """Create test participant in database."""
    participant = Participant(**test_participant_data)
    async_session.add(participant)
    await async_session.commit()
    await async_session.refresh(participant)
    return participant


@pytest.fixture
async def test_incident(async_session, test_meeting, test_participant, test_incident_data) -> Incident:
    """Create test incident in database."""
    incident = Incident(**test_incident_data)
    async_session.add(incident)
    await async_session.commit()
    await async_session.refresh(incident)
    return incident


@pytest.fixture
def auth_token(test_user_data, test_company_data) -> str:
    """Generate auth token for test user."""
    return create_access_token(
        user_id=test_user_data["id"],
        email=test_user_data["email"],
        company_id=test_company_data["id"],
        role=test_user_data["role"].value,
    )


@pytest.fixture
def auth_headers(auth_token) -> dict:
    """Auth headers with bearer token."""
    return {"Authorization": f"Bearer {auth_token}"}


@pytest.fixture
def mock_redis():
    """Mock Redis client."""
    redis_mock = MagicMock()
    redis_mock.get = AsyncMock(return_value=None)
    redis_mock.set = AsyncMock(return_value=True)
    redis_mock.delete = AsyncMock(return_value=True)
    redis_mock.set_verification_pending = AsyncMock(return_value=True)
    return redis_mock


@pytest.fixture
def mock_mongodb():
    """Mock MongoDB client."""
    mongo_mock = MagicMock()
    mongo_mock.get_meeting_transcript = AsyncMock(return_value=[])
    return mongo_mock


@pytest.fixture
def mock_session(async_session):
    """Create a mock session that wraps the async session."""
    return async_session


@pytest.fixture
def mock_async_session(test_company_data, test_user_data, test_meeting_data, test_participant_data, test_incident_data):
    """Mock async database session with proper test data.

    Returns mock objects that match test fixtures for authorization checks.
    """
    from datetime import datetime, timedelta

    # Create mock meeting
    mock_meeting = MagicMock()
    mock_meeting.id = test_meeting_data["id"]
    mock_meeting.company_id = test_company_data["id"]
    mock_meeting.platform = test_meeting_data["platform"]
    mock_meeting.platform_meeting_id = test_meeting_data["platform_meeting_id"]
    mock_meeting.title = test_meeting_data["title"]
    mock_meeting.description = test_meeting_data.get("description", "")
    mock_meeting.host_email = test_meeting_data.get("host_email", "")
    mock_meeting.status = test_meeting_data["status"]
    mock_meeting.risk_score = 25.0
    mock_meeting.risk_level = MeetingStatus.SCHEDULED
    mock_meeting.participant_count = 2
    mock_meeting.deepfake_detected = False
    mock_meeting.social_engineering_detected = False
    mock_meeting.created_at = datetime.utcnow()
    mock_meeting.updated_at = datetime.utcnow()

    # Create mock participant
    mock_participant = MagicMock()
    mock_participant.id = test_participant_data["id"]
    mock_participant.meeting_id = test_meeting_data["id"]
    mock_participant.user_id = test_user_data["id"]
    mock_participant.display_name = test_participant_data["display_name"]
    mock_participant.email = test_participant_data.get("email", "")
    mock_participant.trust_level = TrustLevel.TRUSTED
    mock_participant.is_verified = True
    mock_participant.created_at = datetime.utcnow()

    # Create mock incident
    mock_incident = MagicMock()
    mock_incident.id = test_incident_data["id"]
    mock_incident.meeting_id = test_meeting_data["id"]
    mock_incident.participant_id = test_participant_data["id"]
    mock_incident.incident_type = test_incident_data["incident_type"]
    mock_incident.severity = test_incident_data["severity"]
    mock_incident.status = IncidentStatus.DETECTED
    mock_incident.title = test_incident_data["title"]
    mock_incident.description = test_incident_data["description"]
    mock_incident.confidence_score = test_incident_data["confidence_score"]
    mock_incident.created_at = datetime.utcnow()
    mock_incident.updated_at = datetime.utcnow()
    mock_incident.meeting = mock_meeting  # For relationship access

    # Create mock company
    mock_company = MagicMock()
    mock_company.id = test_company_data["id"]
    mock_company.name = test_company_data["name"]
    mock_company.domain = test_company_data["domain"]
    mock_company.subscription_tier = test_company_data["subscription_tier"]

    # Create mock user
    mock_user = MagicMock()
    mock_user.id = test_user_data["id"]
    mock_user.company_id = test_company_data["id"]
    mock_user.email = test_user_data["email"]
    mock_user.role = test_user_data["role"]
    mock_user.is_active = True
    mock_user.is_verified = True

    # Smart execute mock that returns appropriate data based on query
    def create_smart_execute():
        async def smart_execute(query, *args, **kwargs):
            result = MagicMock()
            query_str = str(query) if hasattr(query, '__str__') else ""

            # Default scalars mock
            def make_scalars_mock(items):
                scalars_mock = MagicMock()
                scalars_mock.all = MagicMock(return_value=items)
                scalars_mock.first = MagicMock(return_value=items[0] if items else None)
                scalars_mock.one_or_none = MagicMock(return_value=items[0] if items else None)
                scalars_mock.unique = MagicMock(return_value=scalars_mock)
                return scalars_mock

            # Check what type of query this is and return appropriate mock data
            if "meetings" in query_str.lower():
                result.scalars = MagicMock(return_value=make_scalars_mock([mock_meeting]))
                result.scalar_one_or_none = MagicMock(return_value=mock_meeting)
                result.fetchone = MagicMock(return_value=(1,))  # For count queries
            elif "incident" in query_str.lower():
                result.scalars = MagicMock(return_value=make_scalars_mock([mock_incident]))
                result.scalar_one_or_none = MagicMock(return_value=mock_incident)
                result.fetchone = MagicMock(return_value=(1,))
            elif "participant" in query_str.lower():
                result.scalars = MagicMock(return_value=make_scalars_mock([mock_participant]))
                result.scalar_one_or_none = MagicMock(return_value=mock_participant)
            elif "user" in query_str.lower():
                result.scalars = MagicMock(return_value=make_scalars_mock([mock_user]))
                result.scalar_one_or_none = MagicMock(return_value=mock_user)
            elif "compan" in query_str.lower():
                result.scalars = MagicMock(return_value=make_scalars_mock([mock_company]))
                result.scalar_one_or_none = MagicMock(return_value=mock_company)
            else:
                result.scalars = MagicMock(return_value=make_scalars_mock([]))
                result.scalar_one_or_none = MagicMock(return_value=None)
                result.fetchone = MagicMock(return_value=(0,))

            return result
        return smart_execute

    session = MagicMock()
    session.execute = AsyncMock(side_effect=create_smart_execute())
    session.scalar = AsyncMock(return_value=1)  # For count queries
    session.add = MagicMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    session.rollback = AsyncMock()
    session.close = AsyncMock()
    session.flush = AsyncMock()
    session.get = AsyncMock(return_value=mock_meeting)  # For get by ID

    return session


@pytest.fixture
def app(mock_redis, mock_mongodb, mock_async_session, test_user_data, test_company_data):
    """Create test FastAPI application with mocked dependencies.

    Uses smart mock that returns appropriate test data for authorization checks.
    """
    from fastapi import FastAPI, Depends, Request
    from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
    from typing import Optional, Annotated
    from src.services.api.routers import (
        auth_router,
        users_router,
        companies_router,
        meetings_router,
        participants_router,
        incidents_router,
        verifications_router,
        policies_router,
        health_router,
        ws_router,
    )
    from src.services.api.dependencies import get_redis_client, get_mongodb_client, get_current_user
    from src.shared.database.postgres import get_async_session
    from src.services.api.exceptions import (
        DeepSafeException,
        AuthenticationError,
        deepsafe_exception_handler,
        validation_exception_handler,
        generic_exception_handler,
    )
    from src.shared.security.jwt import decode_token
    from fastapi.exceptions import RequestValidationError

    # Create test app without lifespan (no real DB connections)
    test_app = FastAPI(
        title="DeepSafe API",
        version="1.0.0",
    )

    # Add exception handlers
    test_app.add_exception_handler(DeepSafeException, deepsafe_exception_handler)
    test_app.add_exception_handler(RequestValidationError, validation_exception_handler)
    test_app.add_exception_handler(Exception, generic_exception_handler)

    # Add routers
    test_app.include_router(health_router, tags=["health"])
    test_app.include_router(auth_router, prefix="/api/v1/auth", tags=["auth"])
    test_app.include_router(users_router, prefix="/api/v1/users", tags=["users"])
    test_app.include_router(companies_router, prefix="/api/v1/companies", tags=["companies"])
    test_app.include_router(meetings_router, prefix="/api/v1/meetings", tags=["meetings"])
    test_app.include_router(participants_router, prefix="/api/v1/participants", tags=["participants"])
    test_app.include_router(incidents_router, prefix="/api/v1/incidents", tags=["incidents"])
    test_app.include_router(verifications_router, prefix="/api/v1/verifications", tags=["verifications"])
    test_app.include_router(policies_router, prefix="/api/v1/policies", tags=["policies"])
    test_app.include_router(ws_router, prefix="/ws", tags=["websocket"])

    # Override dependencies with mocks
    async def override_redis():
        return mock_redis

    async def override_mongodb():
        return mock_mongodb

    async def override_session():
        yield mock_async_session

    security = HTTPBearer(auto_error=False)

    async def override_current_user(
        credentials: Annotated[Optional[HTTPAuthorizationCredentials], Depends(security)],
    ):
        """Mock current user that checks for auth header."""
        if credentials is None:
            raise AuthenticationError("Missing authentication token")

        try:
            payload = decode_token(credentials.credentials)
        except Exception:
            raise AuthenticationError("Invalid token")

        # Return a mock user based on the token payload
        mock_user = MagicMock()
        mock_user.id = payload.get("sub", test_user_data["id"])
        mock_user.company_id = payload.get("company_id", test_company_data["id"])
        mock_user.email = payload.get("email", test_user_data["email"])
        mock_user.role = UserRole(payload.get("role", "admin"))
        mock_user.is_active = True
        mock_user.is_verified = True
        return mock_user

    test_app.dependency_overrides[get_redis_client] = override_redis
    test_app.dependency_overrides[get_mongodb_client] = override_mongodb
    test_app.dependency_overrides[get_async_session] = override_session
    test_app.dependency_overrides[get_current_user] = override_current_user

    return test_app


@pytest.fixture
def client(app) -> TestClient:
    """Create synchronous test client."""
    return TestClient(app)


@pytest.fixture
async def async_client(app) -> AsyncGenerator[AsyncClient, None]:
    """Create async test client."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac
