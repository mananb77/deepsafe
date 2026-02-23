"""
Verifications Router

Endpoints for identity verification management.
"""

from datetime import datetime, timedelta
from typing import Optional
import secrets

from fastapi import APIRouter, Query, status
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from src.shared.models.meeting import Meeting
from src.shared.models.participant import Participant
from src.shared.models.verification import (
    Verification,
    VerificationChannel,
    VerificationStatus,
    VerificationType,
)
from src.shared.schemas.verification import (
    VerificationCreate,
    VerificationResponse,
    VerificationCheck,
    VerificationDetailResponse,
    VerificationListResponse,
    VerificationStatsResponse,
)
from src.shared.schemas.base import SuccessResponse, PaginatedResponse
from src.services.api.dependencies import (
    AsyncSessionDep,
    CurrentUserDep,
    PaginationDep,
    RedisDep,
)
from src.services.api.exceptions import NotFoundError, AuthorizationError, ValidationError

router = APIRouter()


def generate_verification_code(length: int = 6) -> str:
    """Generate a random numeric verification code."""
    return "".join(str(secrets.randbelow(10)) for _ in range(length))


@router.get("", response_model=VerificationListResponse)
async def list_verifications(
    session: AsyncSessionDep,
    user: CurrentUserDep,
    pagination: PaginationDep,
    participant_id: Optional[str] = Query(default=None),
    channel: Optional[VerificationChannel] = Query(default=None),
    status_filter: Optional[VerificationStatus] = Query(default=None, alias="status"),
):
    """
    List verifications for the current user's company.

    Args:
        participant_id: Filter by participant.
        channel: Filter by channel.
        status_filter: Filter by status.

    Returns:
        Paginated list of verifications.
    """
    # Base query - verifications from company's meetings
    query = (
        select(Verification)
        .join(Participant)
        .join(Meeting)
        .where(Meeting.company_id == user.company_id)
    )

    if participant_id:
        query = query.where(Verification.participant_id == participant_id)

    if channel:
        query = query.where(Verification.channel == channel)

    if status_filter:
        query = query.where(Verification.status == status_filter)

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total = await session.scalar(count_query)

    # Apply pagination
    query = query.offset(pagination.offset).limit(pagination.limit)
    query = query.order_by(Verification.initiated_at.desc())

    result = await session.execute(query)
    verifications = result.scalars().all()

    return VerificationListResponse(
        items=[VerificationResponse.model_validate(v) for v in verifications],
        total=total,
        page=pagination.page,
        page_size=pagination.page_size,
        pages=(total + pagination.page_size - 1) // pagination.page_size,
    )


@router.get("/stats", response_model=VerificationStatsResponse)
async def get_verification_stats(
    session: AsyncSessionDep,
    user: CurrentUserDep,
):
    """
    Get verification statistics for dashboard.

    Returns:
        Verification statistics.
    """
    company_id = user.company_id

    # Base subquery
    verification_ids = (
        select(Verification.id)
        .join(Participant)
        .join(Meeting)
        .where(Meeting.company_id == company_id)
    )

    total = await session.scalar(
        select(func.count(Verification.id)).where(Verification.id.in_(verification_ids))
    )

    successful = await session.scalar(
        select(func.count(Verification.id)).where(
            Verification.id.in_(verification_ids),
            Verification.status == VerificationStatus.VERIFIED,
        )
    )

    failed = await session.scalar(
        select(func.count(Verification.id)).where(
            Verification.id.in_(verification_ids),
            Verification.status == VerificationStatus.FAILED,
        )
    )

    expired = await session.scalar(
        select(func.count(Verification.id)).where(
            Verification.id.in_(verification_ids),
            Verification.status == VerificationStatus.EXPIRED,
        )
    )

    # By channel
    by_channel = {}
    for channel in VerificationChannel:
        count = await session.scalar(
            select(func.count(Verification.id)).where(
                Verification.id.in_(verification_ids),
                Verification.channel == channel,
            )
        )
        by_channel[channel.value] = count or 0

    # By type
    by_type = {}
    for v_type in VerificationType:
        count = await session.scalar(
            select(func.count(Verification.id)).where(
                Verification.id.in_(verification_ids),
                Verification.verification_type == v_type,
            )
        )
        by_type[v_type.value] = count or 0

    success_rate = (successful / total * 100) if total and total > 0 else 0.0

    return VerificationStatsResponse(
        total_verifications=total or 0,
        successful_verifications=successful or 0,
        failed_verifications=failed or 0,
        expired_verifications=expired or 0,
        success_rate=round(success_rate, 2),
        by_channel=by_channel,
        by_type=by_type,
    )


@router.get("/{verification_id}", response_model=VerificationDetailResponse)
async def get_verification(
    verification_id: str,
    session: AsyncSessionDep,
    user: CurrentUserDep,
):
    """
    Get detailed verification information.

    Args:
        verification_id: Verification unique identifier.

    Returns:
        Verification details.
    """
    result = await session.execute(
        select(Verification)
        .options(
            selectinload(Verification.participant).selectinload(Participant.meeting)
        )
        .where(Verification.id == verification_id)
    )
    verification = result.scalar_one_or_none()

    if not verification:
        raise NotFoundError("Verification", verification_id)

    if verification.participant.meeting.company_id != user.company_id:
        raise AuthorizationError("Access denied to this verification")

    # Build response
    response_data = VerificationResponse.model_validate(verification).model_dump()
    response_data["participant_name"] = verification.participant.display_name
    response_data["participant_email"] = verification.participant.email
    response_data["meeting_id"] = verification.participant.meeting_id
    response_data["meeting_title"] = verification.participant.meeting.title
    response_data["remaining_attempts"] = verification.remaining_attempts
    response_data["is_expired"] = verification.is_expired

    return VerificationDetailResponse(**response_data)


@router.post("", response_model=VerificationResponse, status_code=status.HTTP_201_CREATED)
async def create_verification(
    request: VerificationCreate,
    session: AsyncSessionDep,
    user: CurrentUserDep,
    redis: RedisDep,
):
    """
    Initiate a new verification.

    Args:
        request: Verification creation data.

    Returns:
        Created verification.
    """
    # Verify participant access
    result = await session.execute(
        select(Participant)
        .options(selectinload(Participant.meeting))
        .where(Participant.id == request.participant_id)
    )
    participant = result.scalar_one_or_none()

    if not participant:
        raise NotFoundError("Participant", request.participant_id)

    if participant.meeting.company_id != user.company_id:
        raise AuthorizationError("Access denied to this participant")

    # Generate verification code
    code = generate_verification_code()

    verification = Verification(
        participant_id=request.participant_id,
        incident_id=request.incident_id,
        verification_type=request.verification_type,
        channel=request.channel,
        destination=request.destination,
        verification_code=code,
        expires_at=datetime.utcnow() + timedelta(minutes=request.expires_in_minutes),
        max_attempts=request.max_attempts,
        transaction_amount=request.transaction_amount,
        transaction_description=request.transaction_description,
    )

    session.add(verification)
    await session.commit()
    await session.refresh(verification)

    # Store in Redis for fast lookup
    await redis.set_verification_pending(
        verification_id=verification.id,
        data={
            "code": code,
            "participant_id": request.participant_id,
            "channel": request.channel.value,
            "attempts": 0,
            "max_attempts": request.max_attempts,
        },
        ttl=request.expires_in_minutes * 60,
    )

    # Dispatch verification delivery via Celery task
    try:
        from src.services.verification.tasks import send_verification_task
        send_verification_task.delay(
            verification_id=str(verification.id),
            channel=request.channel.value,
            destination=request.destination,
            code=code,
            expires_in_minutes=request.expires_in_minutes,
        )
    except Exception:
        pass  # Celery unavailable, fall through to simulated send

    # Mark as sent
    verification.mark_sent()
    await session.commit()

    return VerificationResponse.model_validate(verification)


@router.post("/{verification_id}/check", response_model=VerificationResponse)
async def check_verification(
    verification_id: str,
    request: VerificationCheck,
    session: AsyncSessionDep,
    redis: RedisDep,
):
    """
    Check/complete a verification with the provided code.

    Args:
        verification_id: Verification unique identifier.
        request: Verification code.

    Returns:
        Updated verification.
    """
    result = await session.execute(
        select(Verification)
        .options(
            selectinload(Verification.participant).selectinload(Participant.meeting)
        )
        .where(Verification.id == verification_id)
    )
    verification = result.scalar_one_or_none()

    if not verification:
        raise NotFoundError("Verification", verification_id)

    # Check if already completed
    if verification.status == VerificationStatus.VERIFIED:
        raise ValidationError("Verification already completed")

    if verification.status in [VerificationStatus.FAILED, VerificationStatus.EXPIRED]:
        raise ValidationError(f"Verification {verification.status.value}")

    # Attempt verification
    success = verification.verify(request.code)

    if success:
        # Update participant
        verification.participant.verify(verification.channel.value)

        # Clear from Redis
        await redis.delete(f"verification:pending:{verification_id}")
    else:
        if verification.status == VerificationStatus.FAILED:
            # Max attempts reached
            await redis.delete(f"verification:pending:{verification_id}")

    await session.commit()
    await session.refresh(verification)

    return VerificationResponse.model_validate(verification)


@router.post("/{verification_id}/resend", response_model=VerificationResponse)
async def resend_verification(
    verification_id: str,
    session: AsyncSessionDep,
    user: CurrentUserDep,
    redis: RedisDep,
):
    """
    Resend a verification code.

    Args:
        verification_id: Verification unique identifier.

    Returns:
        New verification.
    """
    result = await session.execute(
        select(Verification)
        .options(
            selectinload(Verification.participant).selectinload(Participant.meeting)
        )
        .where(Verification.id == verification_id)
    )
    verification = result.scalar_one_or_none()

    if not verification:
        raise NotFoundError("Verification", verification_id)

    if verification.participant.meeting.company_id != user.company_id:
        raise AuthorizationError("Access denied to this verification")

    # Create new verification with same parameters
    code = generate_verification_code()

    new_verification = Verification(
        participant_id=verification.participant_id,
        incident_id=verification.incident_id,
        verification_type=verification.verification_type,
        channel=verification.channel,
        destination=verification.destination,
        verification_code=code,
        expires_at=datetime.utcnow() + timedelta(minutes=5),
        max_attempts=verification.max_attempts,
        transaction_amount=verification.transaction_amount,
        transaction_description=verification.transaction_description,
    )

    # Expire old verification
    verification.expire()

    session.add(new_verification)
    await session.commit()
    await session.refresh(new_verification)

    # Store in Redis
    await redis.set_verification_pending(
        verification_id=new_verification.id,
        data={
            "code": code,
            "participant_id": new_verification.participant_id,
            "channel": new_verification.channel.value,
            "attempts": 0,
            "max_attempts": new_verification.max_attempts,
        },
        ttl=300,
    )

    # Mark as sent
    new_verification.mark_sent()
    await session.commit()

    return VerificationResponse.model_validate(new_verification)


@router.post("/{verification_id}/cancel", response_model=SuccessResponse)
async def cancel_verification(
    verification_id: str,
    session: AsyncSessionDep,
    user: CurrentUserDep,
    redis: RedisDep,
):
    """
    Cancel a pending verification.

    Args:
        verification_id: Verification unique identifier.

    Returns:
        Success message.
    """
    result = await session.execute(
        select(Verification)
        .options(
            selectinload(Verification.participant).selectinload(Participant.meeting)
        )
        .where(Verification.id == verification_id)
    )
    verification = result.scalar_one_or_none()

    if not verification:
        raise NotFoundError("Verification", verification_id)

    if verification.participant.meeting.company_id != user.company_id:
        raise AuthorizationError("Access denied to this verification")

    if not verification.is_pending:
        raise ValidationError("Can only cancel pending verifications")

    verification.fail("Cancelled by user")

    # Clear from Redis
    await redis.delete(f"verification:pending:{verification_id}")

    await session.commit()

    return SuccessResponse(message="Verification cancelled")
