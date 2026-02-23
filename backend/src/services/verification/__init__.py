"""
Verification Service

Multi-channel identity verification for high-risk situations.

Channels:
- SMS via Twilio
- Voice callback via Twilio
- Push notification via Firebase
- Email fallback

Verification Matrix (by transaction value + risk):
| Amount     | Risk    | Channels                          |
|------------|---------|-----------------------------------|
| <$5K       | Any     | SMS only                          |
| $5-25K     | <60%    | SMS + email                       |
| $5-25K     | 61-85%  | SMS + push                        |
| $5-25K     | >85%    | SMS + callback + dual approval    |
| $25-100K   | Any     | Callback + push + dual approval   |
| >$100K     | Any     | All channels + 24h hold           |
"""

from src.services.verification.base import (
    BaseVerifier,
    VerificationChannel,
    VerificationStatus,
    VerificationType,
    RiskTier,
    VerificationRequest,
    VerificationResult,
    VerificationConfig,
    ChannelVerification,
    MultiChannelVerification,
    generate_verification_code,
    get_verification_channels_for_risk,
)
from src.services.verification.sms_verifier import SMSVerifier
from src.services.verification.voice_verifier import VoiceVerifier
from src.services.verification.push_verifier import PushVerifier
from src.services.verification.email_verifier import EmailVerifier
from src.services.verification.verification_engine import (
    VerificationEngine,
    VerificationSession,
)

__all__ = [
    # Base types
    "BaseVerifier",
    "VerificationChannel",
    "VerificationStatus",
    "VerificationType",
    "RiskTier",
    "VerificationRequest",
    "VerificationResult",
    "VerificationConfig",
    "ChannelVerification",
    "MultiChannelVerification",
    # Utility functions
    "generate_verification_code",
    "get_verification_channels_for_risk",
    # Verifiers
    "SMSVerifier",
    "VoiceVerifier",
    "PushVerifier",
    "EmailVerifier",
    # Engine
    "VerificationEngine",
    "VerificationSession",
]
