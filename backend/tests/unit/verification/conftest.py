"""
Shared test fixtures for verification service tests.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from src.services.verification.base import (
    VerificationChannel,
    VerificationConfig,
    VerificationRequest,
    VerificationResult,
    VerificationStatus,
    VerificationType,
    RiskTier,
)
from src.services.verification.sms_verifier import (
    SMSVerifier,
    SMSProvider,
    ConsoleSMSProvider,
)
from src.services.verification.voice_verifier import (
    VoiceVerifier,
    VoiceProvider,
    ConsoleVoiceProvider,
)
from src.services.verification.push_verifier import (
    PushVerifier,
    PushProvider,
    ConsolePushProvider,
)
from src.services.verification.email_verifier import (
    EmailVerifier,
    EmailProvider,
    ConsoleEmailProvider,
)


@pytest.fixture
def sample_phone_number():
    """Sample phone number in various formats."""
    return "+15551234567"


@pytest.fixture
def sample_email():
    """Sample email address."""
    return "user@example.com"


@pytest.fixture
def sample_device_token():
    """Sample FCM device token."""
    return "fcm_token_abc123def456_sample_device_token"


@pytest.fixture
def sample_verification_code():
    """Sample 6-digit verification code."""
    return "123456"


@pytest.fixture
def sample_user_id():
    """Sample user UUID."""
    return uuid4()


@pytest.fixture
def sample_transaction_id():
    """Sample transaction UUID."""
    return uuid4()


@pytest.fixture
def verification_config():
    """Standard verification configuration."""
    return VerificationConfig(
        code_length=6,
        code_numeric_only=True,
        expiry_minutes=10,
        max_attempts_per_code=3,
        max_codes_per_hour=5,
        sms_enabled=True,
        voice_enabled=True,
        push_enabled=True,
        email_enabled=True,
    )


@pytest.fixture
def low_risk_request(sample_user_id, sample_phone_number, sample_email):
    """Low risk verification request (<$5K, low risk score)."""
    return VerificationRequest(
        user_id=sample_user_id,
        phone_number=sample_phone_number,
        email=sample_email,
        verification_type=VerificationType.TRANSACTION,
        risk_score=25.0,
        transaction_amount=1000.0,
    )


@pytest.fixture
def medium_risk_request(sample_user_id, sample_phone_number, sample_email, sample_device_token):
    """Medium risk verification request ($5-25K, 60-85% risk)."""
    return VerificationRequest(
        user_id=sample_user_id,
        phone_number=sample_phone_number,
        email=sample_email,
        device_token=sample_device_token,
        verification_type=VerificationType.TRANSACTION,
        risk_score=70.0,
        transaction_amount=15000.0,
    )


@pytest.fixture
def high_risk_request(sample_user_id, sample_phone_number, sample_email, sample_device_token):
    """High risk verification request ($25-100K, high risk)."""
    return VerificationRequest(
        user_id=sample_user_id,
        phone_number=sample_phone_number,
        email=sample_email,
        device_token=sample_device_token,
        verification_type=VerificationType.TRANSACTION,
        risk_score=90.0,
        transaction_amount=50000.0,
    )


@pytest.fixture
def critical_risk_request(sample_user_id, sample_phone_number, sample_email, sample_device_token):
    """Critical risk verification request (>$100K)."""
    return VerificationRequest(
        user_id=sample_user_id,
        phone_number=sample_phone_number,
        email=sample_email,
        device_token=sample_device_token,
        verification_type=VerificationType.TRANSACTION,
        risk_score=95.0,
        transaction_amount=150000.0,
    )


@pytest.fixture
def console_sms_provider():
    """Console SMS provider for testing."""
    return ConsoleSMSProvider()


@pytest.fixture
def console_voice_provider():
    """Console voice provider for testing."""
    return ConsoleVoiceProvider()


@pytest.fixture
def console_push_provider():
    """Console push provider for testing."""
    return ConsolePushProvider()


@pytest.fixture
def console_email_provider():
    """Console email provider for testing."""
    return ConsoleEmailProvider()


@pytest.fixture
def mock_sms_provider():
    """Mock SMS provider for testing."""
    provider = MagicMock(spec=SMSProvider)
    provider.name = "mock_sms"
    provider.is_available = AsyncMock(return_value=True)
    provider.send_sms = AsyncMock(return_value={
        "success": True,
        "message_id": "msg_123",
        "status": "sent",
    })
    return provider


@pytest.fixture
def mock_voice_provider():
    """Mock voice provider for testing."""
    provider = MagicMock(spec=VoiceProvider)
    provider.name = "mock_voice"
    provider.is_available = AsyncMock(return_value=True)
    provider.make_call = AsyncMock(return_value={
        "success": True,
        "call_id": "call_123",
        "status": "completed",
    })
    return provider


@pytest.fixture
def mock_push_provider():
    """Mock push provider for testing."""
    provider = MagicMock(spec=PushProvider)
    provider.name = "mock_push"
    provider.is_available = AsyncMock(return_value=True)
    provider.send_notification = AsyncMock(return_value={
        "success": True,
        "message_id": "push_123",
        "status": "sent",
    })
    return provider


@pytest.fixture
def mock_email_provider():
    """Mock email provider for testing."""
    provider = MagicMock(spec=EmailProvider)
    provider.name = "mock_email"
    provider.is_available = AsyncMock(return_value=True)
    provider.send_email = AsyncMock(return_value={
        "success": True,
        "message_id": "email_123",
        "status": "sent",
    })
    return provider


@pytest.fixture
def sms_verifier(mock_sms_provider):
    """SMS verifier with mock provider."""
    return SMSVerifier(provider=mock_sms_provider)


@pytest.fixture
def voice_verifier(mock_voice_provider):
    """Voice verifier with mock provider."""
    return VoiceVerifier(provider=mock_voice_provider)


@pytest.fixture
def push_verifier(mock_push_provider):
    """Push verifier with mock provider."""
    return PushVerifier(provider=mock_push_provider)


@pytest.fixture
def email_verifier(mock_email_provider):
    """Email verifier with mock provider."""
    return EmailVerifier(provider=mock_email_provider)


@pytest.fixture
def failing_sms_provider():
    """SMS provider that fails to send."""
    provider = MagicMock(spec=SMSProvider)
    provider.name = "failing_sms"
    provider.is_available = AsyncMock(return_value=True)
    provider.send_sms = AsyncMock(return_value={
        "success": False,
        "error": "Network error",
    })
    return provider


@pytest.fixture
def unavailable_provider():
    """Provider that is not available."""
    provider = MagicMock(spec=SMSProvider)
    provider.name = "unavailable"
    provider.is_available = AsyncMock(return_value=False)
    return provider
