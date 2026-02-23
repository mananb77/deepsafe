"""
Unit Tests for Pydantic Schemas

Tests schema validation, serialization, and data transformation.
"""

from datetime import datetime, timedelta

import pytest
from pydantic import ValidationError

from src.shared.schemas.base import (
    PaginatedResponse,
    PaginationParams,
    ErrorResponse,
    SuccessResponse,
)
from src.shared.schemas.auth import (
    LoginRequest,
    TokenResponse,
    TokenPayload,
    PasswordChangeRequest,
)
from src.shared.schemas.user import (
    UserCreate,
    UserUpdate,
    UserResponse,
    BlacklistRequest,
)
from src.shared.schemas.company import (
    CompanyCreate,
    CompanyUpdate,
    CompanyResponse,
)
from src.shared.schemas.meeting import (
    MeetingCreate,
    MeetingUpdate,
    MeetingResponse,
    MeetingRiskUpdate,
    WebhookMeetingEvent,
)
from src.shared.schemas.participant import (
    ParticipantCreate,
    ParticipantUpdate,
    ParticipantResponse,
    ParticipantRiskUpdate,
)
from src.shared.schemas.incident import (
    IncidentCreate,
    IncidentUpdate,
    IncidentResolveRequest,
    IncidentResponse,
)
from src.shared.schemas.verification import (
    VerificationCreate,
    VerificationCheck,
    VerificationResponse,
)
from src.shared.schemas.risk import (
    RiskIndicatorCreate,
    RiskScoreResponse,
    DeepfakeDetectionResult,
    SocialEngineeringResult,
)
from src.shared.models.user import UserRole
from src.shared.models.company import SubscriptionTier
from src.shared.models.meeting import MeetingPlatform, MeetingStatus, RiskLevel
from src.shared.models.participant import ParticipantRole, TrustLevel
from src.shared.models.incident import IncidentType, IncidentSeverity, IncidentStatus
from src.shared.models.verification import (
    VerificationChannel,
    VerificationStatus,
    VerificationType,
)
from src.shared.models.risk_indicator import IndicatorType, IndicatorSource


class TestBaseSchemas:
    """Tests for base schemas."""

    def test_pagination_params_defaults(self):
        """Test default pagination values."""
        params = PaginationParams()

        assert params.page == 1
        assert params.page_size == 20
        assert params.offset == 0
        assert params.limit == 20

    def test_pagination_params_offset_calculation(self):
        """Test offset calculation for different pages."""
        params = PaginationParams(page=3, page_size=10)

        assert params.offset == 20
        assert params.limit == 10

    def test_pagination_params_validation(self):
        """Test pagination parameter validation."""
        with pytest.raises(ValidationError):
            PaginationParams(page=0)  # Must be >= 1

        with pytest.raises(ValidationError):
            PaginationParams(page_size=200)  # Max is 100

    def test_paginated_response(self):
        """Test paginated response properties."""
        response = PaginatedResponse[str](
            items=["a", "b", "c"],
            total=50,
            page=2,
            page_size=10,
            pages=5,
        )

        assert response.has_next is True
        assert response.has_prev is True
        assert len(response.items) == 3

    def test_error_response(self):
        """Test error response schema."""
        error = ErrorResponse(
            error="VALIDATION_ERROR",
            message="Invalid input",
            details={"field": "email", "reason": "invalid format"},
        )

        assert error.error == "VALIDATION_ERROR"
        assert "email" in str(error.details)

    def test_success_response(self):
        """Test success response schema."""
        success = SuccessResponse(
            message="Operation completed",
            data={"user_id": "123"},
        )

        assert success.success is True
        assert success.data["user_id"] == "123"


class TestAuthSchemas:
    """Tests for authentication schemas."""

    def test_login_request_valid(self):
        """Test valid login request."""
        request = LoginRequest(
            email="user@example.com",
            password="securepassword123",
        )

        assert request.email == "user@example.com"
        assert request.password == "securepassword123"

    def test_login_request_invalid_email(self):
        """Test login with invalid email."""
        with pytest.raises(ValidationError) as exc_info:
            LoginRequest(email="invalid-email", password="password123")

        assert "email" in str(exc_info.value).lower()

    def test_login_request_short_password(self):
        """Test login with too short password."""
        with pytest.raises(ValidationError):
            LoginRequest(email="user@example.com", password="short")

    def test_token_response(self):
        """Test token response schema."""
        response = TokenResponse(
            access_token="access.token.here",
            refresh_token="refresh.token.here",
            expires_in=1800,
            expires_at=datetime.utcnow() + timedelta(minutes=30),
        )

        assert response.token_type == "bearer"
        assert response.access_token == "access.token.here"

    def test_token_payload(self):
        """Test JWT token payload schema."""
        payload = TokenPayload(
            sub="user-123",
            email="user@test.com",
            company_id="company-456",
            role="admin",
            exp=datetime.utcnow() + timedelta(hours=1),
            iat=datetime.utcnow(),
        )

        assert payload.sub == "user-123"
        assert payload.role == "admin"

    def test_password_change_request(self):
        """Test password change request validation."""
        request = PasswordChangeRequest(
            current_password="oldpassword123",
            new_password="newpassword456",
        )

        assert request.current_password == "oldpassword123"


class TestUserSchemas:
    """Tests for user schemas."""

    def test_user_create_valid(self):
        """Test valid user creation."""
        user = UserCreate(
            email="newuser@example.com",
            full_name="New User",
            password="SecurePass123",
            role=UserRole.USER,
            company_id="company-123",
        )

        assert user.email == "newuser@example.com"
        assert user.role == UserRole.USER

    def test_user_create_password_validation(self):
        """Test password strength validation."""
        # Missing uppercase
        with pytest.raises(ValidationError):
            UserCreate(
                email="user@test.com",
                full_name="Test User",
                password="alllowercase123",
            )

        # Missing digit
        with pytest.raises(ValidationError):
            UserCreate(
                email="user@test.com",
                full_name="Test User",
                password="NoDigitsHere",
            )

    def test_user_create_sso_no_password(self):
        """Test SSO user without password is valid."""
        user = UserCreate(
            email="sso@example.com",
            full_name="SSO User",
            password=None,
            company_id="company-123",
        )

        assert user.password is None

    def test_user_update_partial(self):
        """Test partial user update."""
        update = UserUpdate(full_name="Updated Name")

        assert update.full_name == "Updated Name"
        assert update.phone_number is None
        assert update.role is None

    def test_user_response_from_attributes(self):
        """Test user response can be created from ORM model attributes."""
        data = {
            "id": "user-123",
            "email": "user@test.com",
            "full_name": "Test User",
            "phone_number": None,
            "avatar_url": None,
            "role": UserRole.USER,
            "company_id": "company-456",
            "is_active": True,
            "is_verified": True,
            "is_sso_user": False,
            "sso_provider": None,
            "is_blacklisted": False,
            "is_whitelisted": False,
            "last_login_at": None,
            "notify_email": True,
            "notify_push": True,
            "notify_sms": False,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }

        response = UserResponse(**data)
        assert response.id == "user-123"
        assert response.email == "user@test.com"

    def test_blacklist_request(self):
        """Test blacklist request validation."""
        request = BlacklistRequest(reason="Suspicious activity detected")

        assert request.reason == "Suspicious activity detected"

        with pytest.raises(ValidationError):
            BlacklistRequest(reason="")  # Empty reason


class TestCompanySchemas:
    """Tests for company schemas."""

    def test_company_create_valid(self):
        """Test valid company creation."""
        company = CompanyCreate(
            name="Acme Corp",
            domain="acme.com",
            subscription_tier=SubscriptionTier.PROFESSIONAL,
        )

        assert company.name == "Acme Corp"
        assert company.domain == "acme.com"

    def test_company_domain_validation(self):
        """Test domain format validation."""
        # Valid domains
        CompanyCreate(name="Test", domain="example.com")
        CompanyCreate(name="Test", domain="sub.example.co.uk")

        # Invalid domains
        with pytest.raises(ValidationError):
            CompanyCreate(name="Test", domain="invalid")

        with pytest.raises(ValidationError):
            CompanyCreate(name="Test", domain="no-tld")

    def test_company_domain_lowercase(self):
        """Test domain is normalized to lowercase."""
        company = CompanyCreate(
            name="Test",
            domain="EXAMPLE.COM",
        )

        assert company.domain == "example.com"

    def test_company_update_partial(self):
        """Test partial company update."""
        update = CompanyUpdate(
            default_risk_threshold=75,
            auto_record_high_risk=True,
        )

        assert update.default_risk_threshold == 75
        assert update.name is None


class TestMeetingSchemas:
    """Tests for meeting schemas."""

    def test_meeting_create_valid(self):
        """Test valid meeting creation."""
        meeting = MeetingCreate(
            platform=MeetingPlatform.ZOOM,
            platform_meeting_id="123-456-789",
            title="Team Sync",
            scheduled_start_at=datetime.utcnow() + timedelta(hours=1),
        )

        assert meeting.platform == MeetingPlatform.ZOOM
        assert meeting.title == "Team Sync"

    def test_meeting_risk_update_validation(self):
        """Test risk score bounds validation."""
        # Valid
        MeetingRiskUpdate(risk_score=50)
        MeetingRiskUpdate(risk_score=0)
        MeetingRiskUpdate(risk_score=100)

        # Invalid
        with pytest.raises(ValidationError):
            MeetingRiskUpdate(risk_score=-10)

        with pytest.raises(ValidationError):
            MeetingRiskUpdate(risk_score=150)

    def test_webhook_meeting_event(self):
        """Test webhook event schema."""
        event = WebhookMeetingEvent(
            platform=MeetingPlatform.GOOGLE_MEET,
            platform_meeting_id="abc-def-ghi",
            event_type="participant_joined",
            timestamp=datetime.utcnow(),
            payload={
                "participant_id": "part-123",
                "name": "John Doe",
            },
        )

        assert event.event_type == "participant_joined"
        assert event.payload["name"] == "John Doe"

    def test_meeting_response(self):
        """Test meeting response schema."""
        response = MeetingResponse(
            id="meeting-123",
            platform=MeetingPlatform.ZOOM,
            platform_meeting_id="123-456-789",
            company_id="company-456",
            title="Test Meeting",
            status=MeetingStatus.IN_PROGRESS,
            participant_count=5,
            max_participants=10,
            risk_score=45.5,
            risk_level=RiskLevel.MEDIUM,
            peak_risk_score=60.0,
            deepfake_detected=False,
            social_engineering_detected=True,
            verification_triggered=True,
            is_recorded=False,
            transcript_available=False,
            bot_joined=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        assert response.risk_level == RiskLevel.MEDIUM
        assert response.social_engineering_detected is True


class TestParticipantSchemas:
    """Tests for participant schemas."""

    def test_participant_create_valid(self):
        """Test valid participant creation."""
        participant = ParticipantCreate(
            meeting_id="meeting-123",
            display_name="Alice Smith",
            platform_participant_id="part-456",
            email="alice@example.com",
            role=ParticipantRole.HOST,
        )

        assert participant.display_name == "Alice Smith"
        assert participant.role == ParticipantRole.HOST

    def test_participant_risk_update(self):
        """Test participant risk score update."""
        update = ParticipantRiskUpdate(
            deepfake_confidence=0.85,
            social_engineering_score=0.45,
        )

        assert update.deepfake_confidence == 0.85
        assert update.social_engineering_score == 0.45

    def test_participant_risk_bounds(self):
        """Test risk score bounds validation."""
        with pytest.raises(ValidationError):
            ParticipantRiskUpdate(deepfake_confidence=1.5)

        with pytest.raises(ValidationError):
            ParticipantRiskUpdate(social_engineering_score=-0.1)


class TestIncidentSchemas:
    """Tests for incident schemas."""

    def test_incident_create_valid(self):
        """Test valid incident creation."""
        incident = IncidentCreate(
            meeting_id="meeting-123",
            participant_id="part-456",
            incident_type=IncidentType.AUDIO_DEEPFAKE,
            title="Deepfake Audio Detected",
            severity=IncidentSeverity.HIGH,
            confidence_score=0.92,
            detection_method="resemble_ai",
        )

        assert incident.incident_type == IncidentType.AUDIO_DEEPFAKE
        assert incident.confidence_score == 0.92

    def test_incident_confidence_bounds(self):
        """Test confidence score bounds."""
        with pytest.raises(ValidationError):
            IncidentCreate(
                meeting_id="m-1",
                incident_type=IncidentType.AUDIO_DEEPFAKE,
                title="Test",
                confidence_score=1.5,
            )

    def test_incident_resolve_request(self):
        """Test incident resolution request."""
        request = IncidentResolveRequest(
            resolution_notes="Verified as legitimate user after callback",
            is_false_positive=False,
        )

        assert request.resolution_notes.startswith("Verified")

    def test_incident_resolve_empty_notes(self):
        """Test resolution requires notes."""
        with pytest.raises(ValidationError):
            IncidentResolveRequest(resolution_notes="")


class TestVerificationSchemas:
    """Tests for verification schemas."""

    def test_verification_create_valid(self):
        """Test valid verification creation."""
        verification = VerificationCreate(
            participant_id="part-123",
            channel=VerificationChannel.SMS,
            destination="+15551234567",
            expires_in_minutes=5,
        )

        assert verification.channel == VerificationChannel.SMS
        assert verification.expires_in_minutes == 5

    def test_verification_create_with_transaction(self):
        """Test verification with transaction context."""
        verification = VerificationCreate(
            participant_id="part-123",
            verification_type=VerificationType.TRANSACTION,
            channel=VerificationChannel.VOICE,
            destination="+15551234567",
            transaction_amount=50000.00,
            transaction_description="Wire transfer to vendor",
        )

        assert verification.verification_type == VerificationType.TRANSACTION
        assert verification.transaction_amount == 50000.00

    def test_verification_check(self):
        """Test verification code check schema."""
        check = VerificationCheck(code="123456")
        assert check.code == "123456"

    def test_verification_code_length(self):
        """Test verification code length validation."""
        with pytest.raises(ValidationError):
            VerificationCheck(code="123")  # Too short

    def test_verification_expiry_bounds(self):
        """Test expiry time bounds."""
        with pytest.raises(ValidationError):
            VerificationCreate(
                participant_id="p-1",
                channel=VerificationChannel.SMS,
                destination="+15551234567",
                expires_in_minutes=0,  # Min is 1
            )


class TestRiskSchemas:
    """Tests for risk assessment schemas."""

    def test_risk_indicator_create(self):
        """Test risk indicator creation."""
        indicator = RiskIndicatorCreate(
            meeting_id="meeting-123",
            participant_id="part-456",
            indicator_type=IndicatorType.AUDIO_DEEPFAKE,
            source=IndicatorSource.RESEMBLE_AI,
            confidence=0.88,
            weight=0.8,
            title="Audio deepfake detected",
            model_version="v2.1.0",
        )

        assert indicator.confidence == 0.88
        assert indicator.source == IndicatorSource.RESEMBLE_AI

    def test_risk_indicator_bounds(self):
        """Test risk indicator score bounds."""
        with pytest.raises(ValidationError):
            RiskIndicatorCreate(
                meeting_id="m-1",
                indicator_type=IndicatorType.AUDIO_DEEPFAKE,
                source=IndicatorSource.RESEMBLE_AI,
                confidence=1.5,  # Max is 1
                title="Test",
            )

    def test_deepfake_detection_result(self):
        """Test deepfake detection result schema."""
        result = DeepfakeDetectionResult(
            is_deepfake=True,
            confidence=0.95,
            detection_type="audio",
            indicators=[
                {"type": "spectral_anomaly", "score": 0.92},
                {"type": "prosody_mismatch", "score": 0.88},
            ],
            model_used="resemble_ai_v3",
            processing_time_ms=245,
            av_sync_offset_ms=65,
        )

        assert result.is_deepfake is True
        assert len(result.indicators) == 2
        assert result.av_sync_offset_ms == 65

    def test_social_engineering_result(self):
        """Test social engineering detection result."""
        result = SocialEngineeringResult(
            risk_score=0.78,
            components={
                "scenario_match": 0.85,
                "keyword_detection": 0.90,
                "gpt4_analysis": 0.75,
                "behavioral_indicator": 0.60,
            },
            detected_patterns=["urgent_request", "authority_impersonation"],
            suspicious_keywords=["urgent", "wire transfer", "immediately"],
            behavioral_flags=["pressure_tactics", "isolation_attempt"],
            gpt4_analysis="High probability of BEC attack",
            transcript_highlights=[
                {"text": "We need this done today", "risk": 0.8},
            ],
        )

        assert result.risk_score == 0.78
        assert "urgent_request" in result.detected_patterns
        assert "wire transfer" in result.suspicious_keywords

    def test_risk_score_response(self):
        """Test composite risk score response."""
        response = RiskScoreResponse(
            meeting_id="meeting-123",
            participant_id="part-456",
            composite_score=75.5,
            risk_level="high",
            components=[
                {
                    "category": "deepfake",
                    "score": 0.85,
                    "weight": 0.6,
                    "weighted_score": 0.51,
                    "indicator_count": 3,
                    "top_indicators": ["audio_deepfake", "av_sync"],
                },
            ],
            timestamp=datetime.utcnow(),
            trend="increasing",
            recommended_actions=[
                "Trigger identity verification",
                "Alert security team",
            ],
        )

        assert response.composite_score == 75.5
        assert response.trend == "increasing"
        assert len(response.recommended_actions) == 2


class TestSchemaFromAttributes:
    """Tests for schema creation from ORM attributes."""

    def test_company_response_from_dict(self):
        """Test creating company response from dictionary."""
        data = {
            "id": "company-123",
            "name": "Test Corp",
            "domain": "test.com",
            "logo_url": None,
            "subscription_tier": SubscriptionTier.ENTERPRISE,
            "subscription_started_at": datetime.utcnow(),
            "subscription_expires_at": datetime.utcnow() + timedelta(days=365),
            "max_users": 100,
            "max_meetings_per_month": 10000,
            "max_concurrent_meetings": 50,
            "deepfake_detection_enabled": True,
            "social_engineering_detection_enabled": True,
            "verification_enabled": True,
            "sso_enabled": True,
            "siem_integration_enabled": True,
            "sso_provider": "okta",
            "default_risk_threshold": 70,
            "auto_record_high_risk": True,
            "notify_security_team": True,
            "security_email": "security@test.com",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }

        response = CompanyResponse(**data)
        assert response.subscription_tier == SubscriptionTier.ENTERPRISE
        assert response.sso_provider == "okta"

    def test_incident_response_serialization(self):
        """Test incident response JSON serialization."""
        response = IncidentResponse(
            id="incident-123",
            meeting_id="meeting-456",
            participant_id="part-789",
            incident_type=IncidentType.SOCIAL_ENGINEERING,
            severity=IncidentSeverity.HIGH,
            status=IncidentStatus.INVESTIGATING,
            title="BEC Attack Detected",
            description="Suspicious wire transfer request",
            confidence_score=0.88,
            detected_at=datetime.utcnow(),
            verification_triggered=True,
            alert_sent=True,
            alert_sent_at=datetime.utcnow(),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        # Test serialization
        json_data = response.model_dump_json()
        assert "BEC Attack" in json_data
        assert "social_engineering" in json_data

    def test_verification_response_from_attributes(self):
        """Test verification response from model attributes."""
        data = {
            "id": "ver-123",
            "participant_id": "part-456",
            "incident_id": None,
            "verification_type": VerificationType.IDENTITY,
            "channel": VerificationChannel.SMS,
            "destination": "+15551234567",
            "status": VerificationStatus.SENT,
            "initiated_at": datetime.utcnow(),
            "sent_at": datetime.utcnow(),
            "delivered_at": None,
            "verified_at": None,
            "expires_at": datetime.utcnow() + timedelta(minutes=5),
            "attempt_count": 0,
            "max_attempts": 3,
            "provider": "twilio",
            "provider_status": "delivered",
            "failure_reason": None,
            "transaction_amount": None,
            "transaction_description": None,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }

        response = VerificationResponse(**data)
        assert response.channel == VerificationChannel.SMS
        assert response.status == VerificationStatus.SENT
