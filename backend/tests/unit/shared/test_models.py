"""
Unit Tests for SQLAlchemy Models

Tests model creation, relationships, and business logic methods.
"""

from datetime import datetime, timedelta
from uuid import uuid4

import pytest
from sqlalchemy import select

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
from src.shared.models.policy import PolicyType, PolicyTrigger, PolicyAction
from src.shared.models.audit_log import AuditAction, AuditCategory


class TestCompanyModel:
    """Tests for Company model."""

    def test_create_company(self, company_factory):
        """Test basic company creation."""
        company = company_factory(name="Acme Corp", domain="acme.com")

        assert company.id is not None
        assert company.name == "Acme Corp"
        assert company.domain == "acme.com"
        assert company.subscription_tier == SubscriptionTier.PROFESSIONAL
        assert company.created_at is not None

    def test_company_default_values(self, company_factory):
        """Test company default values."""
        company = company_factory()

        assert company.deepfake_detection_enabled is True
        assert company.social_engineering_detection_enabled is True
        assert company.verification_enabled is True
        assert company.sso_enabled is False
        assert company.default_risk_threshold == 60
        assert company.auto_record_high_risk is True

    def test_is_enterprise(self, company_factory):
        """Test is_enterprise property."""
        free_company = company_factory(subscription_tier=SubscriptionTier.FREE)
        enterprise_company = company_factory(subscription_tier=SubscriptionTier.ENTERPRISE)

        assert free_company.is_enterprise is False
        assert enterprise_company.is_enterprise is True

    def test_is_subscription_active(self, company_factory):
        """Test subscription active check."""
        # Free tier is always active
        free_company = company_factory(subscription_tier=SubscriptionTier.FREE)
        assert free_company.is_subscription_active is True

        # Paid tier with future expiration
        active_company = company_factory(
            subscription_tier=SubscriptionTier.PROFESSIONAL,
            subscription_expires_at=datetime.utcnow() + timedelta(days=30),
        )
        assert active_company.is_subscription_active is True

        # Paid tier with past expiration
        expired_company = company_factory(
            subscription_tier=SubscriptionTier.PROFESSIONAL,
            subscription_expires_at=datetime.utcnow() - timedelta(days=1),
        )
        assert expired_company.is_subscription_active is False

    def test_company_soft_delete(self, company_factory):
        """Test soft delete functionality."""
        company = company_factory()

        assert company.is_deleted is False
        assert company.deleted_at is None

        company.soft_delete()

        assert company.is_deleted is True
        assert company.deleted_at is not None

    def test_company_restore(self, company_factory):
        """Test restore after soft delete."""
        company = company_factory()
        company.soft_delete()
        company.restore()

        assert company.is_deleted is False
        assert company.deleted_at is None

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.skip(reason="Requires PostgreSQL (JSONB not supported in SQLite)")
    async def test_company_persistence(self, async_session, company_factory):
        """Test company persistence to database."""
        company = company_factory(name="Persist Test")
        async_session.add(company)
        await async_session.commit()

        result = await async_session.execute(
            select(Company).where(Company.id == company.id)
        )
        persisted = result.scalar_one()

        assert persisted.name == "Persist Test"


class TestUserModel:
    """Tests for User model."""

    def test_create_user(self, user_factory, company_factory):
        """Test basic user creation."""
        company = company_factory()
        user = user_factory(
            company=company,
            email="john@test.com",
            full_name="John Doe",
        )

        assert user.id is not None
        assert user.email == "john@test.com"
        assert user.full_name == "John Doe"
        assert user.company_id == company.id

    def test_user_default_role(self, user_factory, company_factory):
        """Test default user role."""
        company = company_factory()
        user = user_factory(company=company)

        assert user.role == UserRole.USER
        assert user.is_admin is False

    def test_is_admin(self, user_factory, company_factory):
        """Test is_admin property."""
        company = company_factory()
        admin = user_factory(company=company, role=UserRole.ADMIN)
        regular = user_factory(company=company, role=UserRole.USER)

        assert admin.is_admin is True
        assert regular.is_admin is False

    def test_is_security_analyst(self, user_factory, company_factory):
        """Test is_security_analyst property."""
        company = company_factory()
        admin = user_factory(company=company, role=UserRole.ADMIN)
        analyst = user_factory(company=company, role=UserRole.SECURITY_ANALYST)
        user = user_factory(company=company, role=UserRole.USER)

        assert admin.is_security_analyst is True
        assert analyst.is_security_analyst is True
        assert user.is_security_analyst is False

    def test_blacklist_user(self, user_factory, company_factory):
        """Test blacklisting a user."""
        company = company_factory()
        user = user_factory(company=company)

        user.blacklist("Suspicious activity")

        assert user.is_blacklisted is True
        assert user.blacklist_reason == "Suspicious activity"
        assert user.blacklisted_at is not None
        assert user.is_whitelisted is False

    def test_whitelist_user(self, user_factory, company_factory):
        """Test whitelisting a user."""
        company = company_factory()
        user = user_factory(company=company)
        user.blacklist("Test")

        user.whitelist()

        assert user.is_whitelisted is True
        assert user.is_blacklisted is False
        assert user.blacklist_reason is None

    def test_remove_from_lists(self, user_factory, company_factory):
        """Test removing user from all lists."""
        company = company_factory()
        user = user_factory(company=company)
        user.blacklist("Test")

        user.remove_from_lists()

        assert user.is_blacklisted is False
        assert user.is_whitelisted is False

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.skip(reason="Requires PostgreSQL (JSONB not supported in SQLite)")
    async def test_user_company_relationship(self, async_session, company_factory, user_factory):
        """Test user-company relationship."""
        company = company_factory()
        user = user_factory(company=company)

        async_session.add(company)
        async_session.add(user)
        await async_session.commit()

        result = await async_session.execute(
            select(User).where(User.id == user.id)
        )
        persisted = result.scalar_one()

        assert persisted.company_id == company.id


class TestMeetingModel:
    """Tests for Meeting model."""

    def test_create_meeting(self, meeting_factory, company_factory):
        """Test basic meeting creation."""
        company = company_factory()
        meeting = meeting_factory(
            company=company,
            platform=MeetingPlatform.GOOGLE_MEET,
            title="Board Meeting",
        )

        assert meeting.id is not None
        assert meeting.platform == MeetingPlatform.GOOGLE_MEET
        assert meeting.title == "Board Meeting"
        assert meeting.status == MeetingStatus.IN_PROGRESS

    def test_meeting_default_risk(self, meeting_factory):
        """Test default risk values."""
        meeting = meeting_factory()

        assert meeting.risk_score == 25.0
        assert meeting.risk_level == RiskLevel.LOW
        assert meeting.deepfake_detected is False
        assert meeting.social_engineering_detected is False

    def test_update_risk(self, meeting_factory):
        """Test risk score update logic."""
        meeting = meeting_factory()

        # Low risk
        meeting.update_risk(20)
        assert meeting.risk_level == RiskLevel.LOW

        # Medium risk
        meeting.update_risk(45)
        assert meeting.risk_level == RiskLevel.MEDIUM

        # High risk
        meeting.update_risk(70)
        assert meeting.risk_level == RiskLevel.HIGH

        # Critical risk
        meeting.update_risk(90)
        assert meeting.risk_level == RiskLevel.CRITICAL

    def test_peak_risk_tracking(self, meeting_factory):
        """Test peak risk score tracking."""
        meeting = meeting_factory()
        meeting.update_risk(50)

        assert meeting.peak_risk_score == 50
        assert meeting.peak_risk_at is not None

        meeting.update_risk(30)
        assert meeting.peak_risk_score == 50  # Peak unchanged

        meeting.update_risk(80)
        assert meeting.peak_risk_score == 80  # New peak

    def test_meeting_lifecycle(self, meeting_factory):
        """Test meeting start/end lifecycle."""
        meeting = meeting_factory(status=MeetingStatus.SCHEDULED)

        meeting.start()
        assert meeting.status == MeetingStatus.IN_PROGRESS
        assert meeting.actual_start_at is not None

        meeting.end()
        assert meeting.status == MeetingStatus.COMPLETED
        assert meeting.actual_end_at is not None

    def test_meeting_cancel(self, meeting_factory):
        """Test meeting cancellation."""
        meeting = meeting_factory(status=MeetingStatus.SCHEDULED)

        meeting.cancel()
        assert meeting.status == MeetingStatus.CANCELLED

    def test_is_high_risk(self, meeting_factory):
        """Test is_high_risk property."""
        low_risk = meeting_factory(risk_level=RiskLevel.LOW)
        medium_risk = meeting_factory(risk_level=RiskLevel.MEDIUM)
        high_risk = meeting_factory(risk_level=RiskLevel.HIGH)
        critical_risk = meeting_factory(risk_level=RiskLevel.CRITICAL)

        assert low_risk.is_high_risk is False
        assert medium_risk.is_high_risk is False
        assert high_risk.is_high_risk is True
        assert critical_risk.is_high_risk is True

    def test_duration_minutes(self, meeting_factory):
        """Test duration calculation."""
        meeting = meeting_factory()
        meeting.actual_start_at = datetime.utcnow() - timedelta(minutes=45)
        meeting.actual_end_at = datetime.utcnow()

        assert meeting.duration_minutes == 45

    def test_duration_minutes_no_end(self, meeting_factory):
        """Test duration when meeting hasn't ended."""
        meeting = meeting_factory()
        meeting.actual_start_at = datetime.utcnow()
        meeting.actual_end_at = None

        assert meeting.duration_minutes is None


class TestParticipantModel:
    """Tests for Participant model."""

    def test_create_participant(self, participant_factory, meeting_factory):
        """Test basic participant creation."""
        meeting = meeting_factory()
        participant = participant_factory(
            meeting=meeting,
            display_name="Alice Smith",
            email="alice@test.com",
        )

        assert participant.id is not None
        assert participant.display_name == "Alice Smith"
        assert participant.meeting_id == meeting.id

    def test_participant_default_trust(self, participant_factory):
        """Test default trust values."""
        participant = participant_factory()

        assert participant.trust_level == TrustLevel.UNKNOWN
        assert participant.trust_score == 50.0
        assert participant.is_flagged is False

    def test_update_risk_scores(self, participant_factory):
        """Test risk score updates."""
        participant = participant_factory()

        participant.update_risk_scores(deepfake=0.8, social_engineering=0.5)

        assert participant.deepfake_confidence == 0.8
        assert participant.social_engineering_score == 0.5
        assert participant.composite_risk_score == 0.8 * 0.6 + 0.5 * 0.4
        assert participant.is_deepfake_suspect is True
        assert participant.is_flagged is True

    def test_trust_level_update(self, participant_factory):
        """Test trust level updates based on scores."""
        participant = participant_factory()

        # High risk -> blacklisted
        participant.update_risk_scores(deepfake=0.9, social_engineering=0.9)
        assert participant.trust_level == TrustLevel.BLACKLISTED

        # Medium risk -> suspicious
        participant.update_risk_scores(deepfake=0.5, social_engineering=0.6)
        assert participant.trust_level == TrustLevel.SUSPICIOUS

    def test_verify_participant(self, participant_factory):
        """Test participant verification."""
        participant = participant_factory()
        participant.update_risk_scores(deepfake=0.8)

        participant.verify("sms")

        assert participant.is_verified is True
        assert participant.verification_method == "sms"
        assert participant.trust_level == TrustLevel.VERIFIED
        assert participant.is_flagged is False

    def test_participant_leave(self, participant_factory):
        """Test participant leaving meeting."""
        participant = participant_factory()

        participant.leave()

        assert participant.is_active is False
        assert participant.left_at is not None


class TestIncidentModel:
    """Tests for Incident model."""

    def test_create_incident(self, incident_factory, meeting_factory, participant_factory):
        """Test basic incident creation."""
        meeting = meeting_factory()
        participant = participant_factory(meeting=meeting)
        incident = incident_factory(
            meeting=meeting,
            participant=participant,
            incident_type=IncidentType.VIDEO_DEEPFAKE,
            title="Deepfake Detected",
        )

        assert incident.id is not None
        assert incident.incident_type == IncidentType.VIDEO_DEEPFAKE
        assert incident.status == IncidentStatus.DETECTED

    def test_incident_escalation(self, incident_factory):
        """Test incident severity escalation."""
        incident = incident_factory(severity=IncidentSeverity.LOW)

        incident.escalate(IncidentSeverity.HIGH)
        assert incident.severity == IncidentSeverity.HIGH

        # Can't de-escalate
        incident.escalate(IncidentSeverity.MEDIUM)
        assert incident.severity == IncidentSeverity.HIGH

    def test_incident_workflow(self, incident_factory):
        """Test incident status workflow."""
        incident = incident_factory()

        assert incident.status == IncidentStatus.DETECTED
        assert incident.is_active is True

        incident.investigate()
        assert incident.status == IncidentStatus.INVESTIGATING

        incident.verify_incident()
        assert incident.status == IncidentStatus.VERIFIED

        incident.resolve("Issue addressed", "user-123")
        assert incident.status == IncidentStatus.RESOLVED
        assert incident.is_resolved is True
        assert incident.resolution_notes == "Issue addressed"

    def test_mark_false_positive(self, incident_factory):
        """Test marking incident as false positive."""
        incident = incident_factory()

        incident.mark_false_positive("False alarm", "user-123")

        assert incident.status == IncidentStatus.FALSE_POSITIVE
        assert incident.is_resolved is True

    def test_add_action(self, incident_factory):
        """Test adding actions to incident."""
        incident = incident_factory()

        incident.add_action("Notified security team", {"emails": ["security@test.com"]})
        incident.add_action("Started recording")

        assert len(incident.actions_taken) == 2
        assert incident.actions_taken[0]["action"] == "Notified security team"

    def test_requires_immediate_action(self, incident_factory):
        """Test requires_immediate_action property."""
        critical_active = incident_factory(
            severity=IncidentSeverity.CRITICAL,
            status=IncidentStatus.DETECTED,
        )
        critical_resolved = incident_factory(
            severity=IncidentSeverity.CRITICAL,
            status=IncidentStatus.RESOLVED,
        )
        low_active = incident_factory(
            severity=IncidentSeverity.LOW,
            status=IncidentStatus.DETECTED,
        )

        assert critical_active.requires_immediate_action is True
        assert critical_resolved.requires_immediate_action is False
        assert low_active.requires_immediate_action is False


class TestVerificationModel:
    """Tests for Verification model."""

    def test_create_verification(self, verification_factory, participant_factory):
        """Test basic verification creation."""
        participant = participant_factory()
        verification = verification_factory(
            participant=participant,
            channel=VerificationChannel.SMS,
            destination="+15551234567",
        )

        assert verification.id is not None
        assert verification.channel == VerificationChannel.SMS
        assert verification.status == VerificationStatus.PENDING

    def test_verification_lifecycle(self, verification_factory):
        """Test verification status transitions."""
        verification = verification_factory(verification_code="123456")

        verification.mark_sent("msg-123")
        assert verification.status == VerificationStatus.SENT
        assert verification.provider_message_id == "msg-123"

        verification.mark_delivered()
        assert verification.status == VerificationStatus.DELIVERED

    def test_verify_correct_code(self, verification_factory):
        """Test successful verification."""
        verification = verification_factory(verification_code="123456")

        result = verification.verify("123456")

        assert result is True
        assert verification.status == VerificationStatus.VERIFIED
        assert verification.attempt_count == 1

    def test_verify_wrong_code(self, verification_factory):
        """Test failed verification with wrong code."""
        verification = verification_factory(verification_code="123456")

        result = verification.verify("wrong")

        assert result is False
        assert verification.status != VerificationStatus.VERIFIED
        assert verification.attempt_count == 1

    def test_verify_max_attempts(self, verification_factory):
        """Test verification fails after max attempts."""
        verification = verification_factory(
            verification_code="123456",
            max_attempts=3,
        )

        verification.verify("wrong")
        verification.verify("wrong")
        verification.verify("wrong")
        result = verification.verify("123456")

        assert result is False
        assert verification.status == VerificationStatus.FAILED

    def test_verify_expired(self, verification_factory):
        """Test verification fails when expired."""
        verification = verification_factory(
            verification_code="123456",
            expires_at=datetime.utcnow() - timedelta(minutes=1),
        )

        result = verification.verify("123456")

        assert result is False
        assert verification.status == VerificationStatus.EXPIRED

    def test_remaining_attempts(self, verification_factory):
        """Test remaining attempts calculation."""
        verification = verification_factory(max_attempts=3)

        assert verification.remaining_attempts == 3

        verification.verify("wrong")
        assert verification.remaining_attempts == 2


class TestRiskIndicatorModel:
    """Tests for RiskIndicator model."""

    def test_create_risk_indicator(self, risk_indicator_factory):
        """Test basic risk indicator creation."""
        indicator = risk_indicator_factory(
            indicator_type=IndicatorType.AUDIO_DEEPFAKE,
            confidence=0.9,
        )

        assert indicator.id is not None
        assert indicator.indicator_type == IndicatorType.AUDIO_DEEPFAKE
        assert indicator.confidence == 0.9

    def test_weighted_score_calculation(self, risk_indicator_factory):
        """Test weighted score is calculated."""
        indicator = risk_indicator_factory(
            confidence=0.8,
            weight=0.5,
        )

        assert indicator.weighted_score == 0.4

    def test_update_confidence(self, risk_indicator_factory):
        """Test confidence update recalculates weighted score."""
        indicator = risk_indicator_factory(confidence=0.5, weight=1.0)
        indicator.update_confidence(0.9)

        assert indicator.confidence == 0.9
        assert indicator.weighted_score == 0.9

    def test_is_high_confidence(self, risk_indicator_factory):
        """Test high confidence property."""
        high = risk_indicator_factory(confidence=0.9)
        low = risk_indicator_factory(confidence=0.5)

        assert high.is_high_confidence is True
        assert low.is_high_confidence is False

    def test_create_deepfake_indicator(self, meeting_factory, participant_factory):
        """Test factory method for deepfake indicators."""
        meeting = meeting_factory()
        participant = participant_factory(meeting=meeting)

        indicator = RiskIndicator.create_deepfake_indicator(
            meeting_id=meeting.id,
            participant_id=participant.id,
            indicator_type=IndicatorType.AUDIO_DEEPFAKE,
            source=IndicatorSource.RESEMBLE_AI,
            confidence=0.85,
            raw_data={"analysis": "test"},
        )

        assert indicator.weight == 0.8
        assert indicator.title == "Audio Deepfake Detected"

    def test_create_social_engineering_indicator(self, meeting_factory):
        """Test factory method for social engineering indicators."""
        meeting = meeting_factory()

        indicator = RiskIndicator.create_social_engineering_indicator(
            meeting_id=meeting.id,
            participant_id=None,
            indicator_type=IndicatorType.KEYWORD_DETECTION,
            source=IndicatorSource.KEYWORD_RULES,
            confidence=0.7,
            description="Urgent financial keywords detected",
            transcript_segment="We need to wire $50,000 immediately",
        )

        assert indicator.weight == 0.20
        assert indicator.title == "Suspicious Keywords Detected"


class TestPolicyModel:
    """Tests for Policy model."""

    def test_create_policy(self, policy_factory, company_factory):
        """Test basic policy creation."""
        company = company_factory()
        policy = policy_factory(
            company=company,
            name="High Risk Alert",
            policy_type=PolicyType.NOTIFICATION,
        )

        assert policy.id is not None
        assert policy.name == "High Risk Alert"
        assert policy.is_enabled is True

    def test_policy_can_trigger(self, policy_factory):
        """Test can_trigger check."""
        policy = policy_factory(cooldown_minutes=0)
        assert policy.can_trigger() is True

        disabled_policy = policy_factory(is_enabled=False)
        assert disabled_policy.can_trigger() is False

    def test_policy_cooldown(self, policy_factory):
        """Test cooldown enforcement."""
        policy = policy_factory(cooldown_minutes=5)

        assert policy.can_trigger() is True

        policy.record_trigger()

        assert policy.can_trigger() is False
        assert policy.trigger_count == 1

    def test_evaluate_conditions_risk_score(self, policy_factory):
        """Test condition evaluation with risk score."""
        policy = policy_factory(min_risk_score=60, max_risk_score=90)

        assert policy.evaluate_conditions({"risk_score": 70}) is True
        assert policy.evaluate_conditions({"risk_score": 50}) is False
        assert policy.evaluate_conditions({"risk_score": 95}) is False

    def test_evaluate_conditions_transaction(self, policy_factory):
        """Test condition evaluation with transaction amount."""
        policy = policy_factory(
            min_transaction_amount=1000,
            max_transaction_amount=10000,
        )

        assert policy.evaluate_conditions({"transaction_amount": 5000}) is True
        assert policy.evaluate_conditions({"transaction_amount": 500}) is False
        assert policy.evaluate_conditions({"transaction_amount": 15000}) is False

    def test_create_default_policies(self, company_factory):
        """Test default policy creation."""
        company = company_factory()

        policies = Policy.create_default_policies(company.id)

        assert len(policies) == 3
        policy_names = [p.name for p in policies]
        assert "High Risk Alert" in policy_names
        assert "Deepfake Verification Required" in policy_names
        assert "Large Transaction Approval" in policy_names


class TestAuditLogModel:
    """Tests for AuditLog model."""

    def test_create_audit_log(self, audit_log_factory, user_factory, company_factory):
        """Test basic audit log creation."""
        company = company_factory()
        user = user_factory(company=company)
        log = audit_log_factory(user=user)

        assert log.id is not None
        assert log.action == AuditAction.LOGIN
        assert log.category == AuditCategory.AUTHENTICATION

    def test_log_action_factory(self):
        """Test log_action factory method."""
        log = AuditLog.log_action(
            action=AuditAction.USER_CREATED,
            description="New user created",
            user_id="user-123",
            target_type="user",
            target_id="new-user-456",
        )

        assert log.action == AuditAction.USER_CREATED
        assert log.category == AuditCategory.USER_MANAGEMENT
        assert log.target_type == "user"

    def test_log_authentication(self):
        """Test authentication logging convenience method."""
        log = AuditLog.log_authentication(
            action=AuditAction.LOGIN,
            user_id="user-123",
            ip_address="192.168.1.1",
            success=True,
        )

        assert log.action == AuditAction.LOGIN
        assert log.category == AuditCategory.AUTHENTICATION
        assert log.ip_address == "192.168.1.1"
        assert log.risk_level == "low"

    def test_log_failed_authentication(self):
        """Test failed authentication logging."""
        log = AuditLog.log_authentication(
            action=AuditAction.LOGIN_FAILED,
            user_id="user-123",
            success=False,
        )

        assert log.risk_level == "medium"

    def test_log_security_event(self):
        """Test security event logging."""
        log = AuditLog.log_security_event(
            action=AuditAction.DEEPFAKE_DETECTED,
            meeting_id="meeting-123",
            company_id="company-456",
            description="Audio deepfake detected",
            target_id="incident-789",
        )

        assert log.action == AuditAction.DEEPFAKE_DETECTED
        assert log.category == AuditCategory.SECURITY
        assert log.risk_level == "critical"
        assert log.meeting_id == "meeting-123"
