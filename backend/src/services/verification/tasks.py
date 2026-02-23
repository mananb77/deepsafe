"""
Celery Tasks for Verification Delivery

Tasks for sending verification codes via SMS, voice, push, and email
using the existing verifier classes.
"""

import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

try:
    from src.shared.messaging.celery_app import celery_app
except ImportError:
    from unittest.mock import MagicMock
    celery_app = MagicMock()


@celery_app.task(
    name="verification.send_verification",
    queue="verification",
    bind=True,
    max_retries=3,
    soft_time_limit=30,
    time_limit=45,
)
def send_verification_task(
    self,
    verification_id: str,
    channel: str,
    destination: str,
    code: str,
    expires_in_minutes: int = 10,
) -> Dict[str, Any]:
    """
    Send a verification code via the specified channel.

    Routes to the appropriate channel-specific task.
    """
    logger.info(f"Sending verification {verification_id} via {channel} to {destination}")

    try:
        if channel == "sms":
            return _send_sms(destination, code, expires_in_minutes)
        elif channel == "voice":
            return _send_voice(destination, code, expires_in_minutes)
        elif channel == "push":
            return _send_push(destination, code, expires_in_minutes)
        elif channel == "email":
            return _send_email(destination, code, expires_in_minutes)
        else:
            logger.warning(f"Unknown verification channel: {channel}")
            return {"status": "failed", "error": f"Unknown channel: {channel}"}

    except Exception as e:
        logger.error(f"Verification send failed: {e}")
        raise self.retry(exc=e, countdown=2 ** self.request.retries)


@celery_app.task(
    name="verification.send_sms",
    queue="verification",
    bind=True,
    max_retries=3,
    soft_time_limit=15,
    time_limit=20,
)
def send_sms_verification(
    self,
    phone_number: str,
    code: str,
    expires_in_minutes: int = 10,
) -> Dict[str, Any]:
    """Send SMS verification code."""
    return _send_sms(phone_number, code, expires_in_minutes)


@celery_app.task(
    name="verification.send_voice",
    queue="verification",
    bind=True,
    max_retries=2,
    soft_time_limit=30,
    time_limit=45,
)
def send_voice_verification(
    self,
    phone_number: str,
    code: str,
    expires_in_minutes: int = 10,
) -> Dict[str, Any]:
    """Send voice verification call."""
    return _send_voice(phone_number, code, expires_in_minutes)


@celery_app.task(
    name="verification.send_push",
    queue="verification",
    bind=True,
    max_retries=3,
    soft_time_limit=10,
    time_limit=15,
)
def send_push_verification(
    self,
    device_token: str,
    code: str,
    expires_in_minutes: int = 10,
) -> Dict[str, Any]:
    """Send push notification verification."""
    return _send_push(device_token, code, expires_in_minutes)


@celery_app.task(
    name="verification.send_email",
    queue="verification",
    bind=True,
    max_retries=3,
    soft_time_limit=15,
    time_limit=20,
)
def send_email_verification(
    self,
    email_address: str,
    code: str,
    expires_in_minutes: int = 10,
) -> Dict[str, Any]:
    """Send email verification code."""
    return _send_email(email_address, code, expires_in_minutes)


# ==================== Internal Helpers ====================

def _send_sms(phone_number: str, code: str, expires_in_minutes: int) -> Dict[str, Any]:
    """Send SMS using SMSVerifier."""
    try:
        from src.services.verification.sms_verifier import SMSVerifier

        verifier = SMSVerifier()
        result = verifier.send_code_sync(
            recipient=phone_number,
            code=code,
            expiry_minutes=expires_in_minutes,
        )
        return {
            "status": "sent",
            "channel": "sms",
            "destination": phone_number,
            "provider_message_id": getattr(result, "provider_message_id", None),
        }
    except ImportError:
        logger.warning("SMSVerifier not available")
        return {"status": "failed", "channel": "sms", "error": "Service unavailable"}
    except Exception as e:
        logger.error(f"SMS send failed: {e}")
        return {"status": "failed", "channel": "sms", "error": str(e)}


def _send_voice(phone_number: str, code: str, expires_in_minutes: int) -> Dict[str, Any]:
    """Send voice call using VoiceVerifier."""
    try:
        from src.services.verification.voice_verifier import VoiceVerifier

        verifier = VoiceVerifier()
        result = verifier.send_code_sync(
            recipient=phone_number,
            code=code,
            expiry_minutes=expires_in_minutes,
        )
        return {
            "status": "sent",
            "channel": "voice",
            "destination": phone_number,
            "provider_message_id": getattr(result, "provider_message_id", None),
        }
    except ImportError:
        logger.warning("VoiceVerifier not available")
        return {"status": "failed", "channel": "voice", "error": "Service unavailable"}
    except Exception as e:
        logger.error(f"Voice send failed: {e}")
        return {"status": "failed", "channel": "voice", "error": str(e)}


def _send_push(device_token: str, code: str, expires_in_minutes: int) -> Dict[str, Any]:
    """Send push notification using PushVerifier."""
    try:
        from src.services.verification.push_verifier import PushVerifier

        verifier = PushVerifier()
        result = verifier.send_code_sync(
            recipient=device_token,
            code=code,
            expiry_minutes=expires_in_minutes,
        )
        return {
            "status": "sent",
            "channel": "push",
            "destination": device_token,
            "provider_message_id": getattr(result, "provider_message_id", None),
        }
    except ImportError:
        logger.warning("PushVerifier not available")
        return {"status": "failed", "channel": "push", "error": "Service unavailable"}
    except Exception as e:
        logger.error(f"Push send failed: {e}")
        return {"status": "failed", "channel": "push", "error": str(e)}


def _send_email(email_address: str, code: str, expires_in_minutes: int) -> Dict[str, Any]:
    """Send email using EmailVerifier."""
    try:
        from src.services.verification.email_verifier import EmailVerifier

        verifier = EmailVerifier()
        result = verifier.send_code_sync(
            recipient=email_address,
            code=code,
            expiry_minutes=expires_in_minutes,
        )
        return {
            "status": "sent",
            "channel": "email",
            "destination": email_address,
            "provider_message_id": getattr(result, "provider_message_id", None),
        }
    except ImportError:
        logger.warning("EmailVerifier not available")
        return {"status": "failed", "channel": "email", "error": "Service unavailable"}
    except Exception as e:
        logger.error(f"Email send failed: {e}")
        return {"status": "failed", "channel": "email", "error": str(e)}
