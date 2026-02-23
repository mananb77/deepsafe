"""
Participants Router

Endpoints for meeting participant management.
"""

from typing import Optional

from fastapi import APIRouter, Query, status
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from src.shared.models.meeting import Meeting
from src.shared.models.participant import Participant, TrustLevel
from src.shared.schemas.participant import (
    ParticipantCreate,
    ParticipantUpdate,
    ParticipantResponse,
    ParticipantDetailResponse,
    ParticipantRiskUpdate,
)
from src.shared.schemas.base import SuccessResponse, PaginatedResponse
from src.services.api.dependencies import (
    AsyncSessionDep,
    CurrentUserDep,
    PaginationDep,
)
from src.services.api.exceptions import NotFoundError, AuthorizationError

router = APIRouter()


@router.get("", response_model=PaginatedResponse[ParticipantResponse])
async def list_participants(
    session: AsyncSessionDep,
    user: CurrentUserDep,
    pagination: PaginationDep,
    meeting_id: Optional[str] = Query(default=None),
    trust_level: Optional[TrustLevel] = Query(default=None),
    is_flagged: Optional[bool] = Query(default=None),
):
    """
    List participants across meetings.

    Args:
        meeting_id: Filter by meeting.
        trust_level: Filter by trust level.
        is_flagged: Filter by flagged status.

    Returns:
        Paginated list of participants.
    """
    # Base query - only participants from company's meetings
    query = select(Participant).join(Meeting).where(
        Meeting.company_id == user.company_id
    )

    if meeting_id:
        query = query.where(Participant.meeting_id == meeting_id)

    if trust_level:
        query = query.where(Participant.trust_level == trust_level)

    if is_flagged is not None:
        query = query.where(Participant.is_flagged == is_flagged)

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total = await session.scalar(count_query)

    # Apply pagination
    query = query.offset(pagination.offset).limit(pagination.limit)
    query = query.order_by(Participant.joined_at.desc())

    result = await session.execute(query)
    participants = result.scalars().all()

    return PaginatedResponse(
        items=[ParticipantResponse.model_validate(p) for p in participants],
        total=total,
        page=pagination.page,
        page_size=pagination.page_size,
        pages=(total + pagination.page_size - 1) // pagination.page_size,
    )


@router.get("/{participant_id}", response_model=ParticipantDetailResponse)
async def get_participant(
    participant_id: str,
    session: AsyncSessionDep,
    user: CurrentUserDep,
):
    """
    Get detailed participant information.

    Args:
        participant_id: Participant unique identifier.

    Returns:
        Participant details.
    """
    result = await session.execute(
        select(Participant)
        .options(selectinload(Participant.meeting))
        .where(Participant.id == participant_id)
    )
    participant = result.scalar_one_or_none()

    if not participant:
        raise NotFoundError("Participant", participant_id)

    # Check access
    if participant.meeting.company_id != user.company_id:
        raise AuthorizationError("Access denied to this participant")

    # Get counts
    from src.shared.models.incident import Incident
    from src.shared.models.verification import Verification
    from src.shared.models.risk_indicator import RiskIndicator

    incident_count = await session.scalar(
        select(func.count(Incident.id)).where(Incident.participant_id == participant_id)
    )

    verification_count = await session.scalar(
        select(func.count(Verification.id)).where(Verification.participant_id == participant_id)
    )

    risk_indicator_count = await session.scalar(
        select(func.count(RiskIndicator.id)).where(RiskIndicator.participant_id == participant_id)
    )

    # Build response
    response_data = ParticipantResponse.model_validate(participant).model_dump()
    response_data["meeting_title"] = participant.meeting.title
    response_data["meeting_platform"] = participant.meeting.platform.value
    response_data["company_id"] = participant.meeting.company_id
    response_data["incident_count"] = incident_count or 0
    response_data["verification_count"] = verification_count or 0
    response_data["risk_indicator_count"] = risk_indicator_count or 0

    return ParticipantDetailResponse(**response_data)


@router.post("", response_model=ParticipantResponse, status_code=status.HTTP_201_CREATED)
async def create_participant(
    request: ParticipantCreate,
    session: AsyncSessionDep,
    user: CurrentUserDep,
):
    """
    Add a participant to a meeting.

    Args:
        request: Participant creation data.

    Returns:
        Created participant.
    """
    # Verify meeting access
    result = await session.execute(
        select(Meeting).where(Meeting.id == request.meeting_id)
    )
    meeting = result.scalar_one_or_none()

    if not meeting:
        raise NotFoundError("Meeting", request.meeting_id)

    if meeting.company_id != user.company_id:
        raise AuthorizationError("Access denied to this meeting")

    participant = Participant(
        meeting_id=request.meeting_id,
        user_id=request.user_id,
        display_name=request.display_name,
        email=request.email,
        phone_number=request.phone_number,
        platform_participant_id=request.platform_participant_id,
        platform_user_id=request.platform_user_id,
        role=request.role,
        avatar_url=request.avatar_url,
        device_type=request.device_type,
        extra_data=request.extra_data,
    )

    session.add(participant)

    # Update meeting participant count
    meeting.participant_count += 1
    if meeting.participant_count > meeting.max_participants:
        meeting.max_participants = meeting.participant_count

    await session.commit()
    await session.refresh(participant)

    return ParticipantResponse.model_validate(participant)


@router.patch("/{participant_id}", response_model=ParticipantResponse)
async def update_participant(
    participant_id: str,
    request: ParticipantUpdate,
    session: AsyncSessionDep,
    user: CurrentUserDep,
):
    """
    Update participant information.

    Args:
        participant_id: Participant unique identifier.
        request: Update data.

    Returns:
        Updated participant.
    """
    result = await session.execute(
        select(Participant)
        .options(selectinload(Participant.meeting))
        .where(Participant.id == participant_id)
    )
    participant = result.scalar_one_or_none()

    if not participant:
        raise NotFoundError("Participant", participant_id)

    if participant.meeting.company_id != user.company_id:
        raise AuthorizationError("Access denied to this participant")

    # Apply updates
    update_data = request.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if hasattr(participant, field):
            setattr(participant, field, value)

    await session.commit()
    await session.refresh(participant)

    return ParticipantResponse.model_validate(participant)


@router.post("/{participant_id}/risk", response_model=ParticipantResponse)
async def update_participant_risk(
    participant_id: str,
    request: ParticipantRiskUpdate,
    session: AsyncSessionDep,
    user: CurrentUserDep,
):
    """
    Update participant risk scores.

    Args:
        participant_id: Participant unique identifier.
        request: Risk update data.

    Returns:
        Updated participant.
    """
    result = await session.execute(
        select(Participant)
        .options(selectinload(Participant.meeting))
        .where(Participant.id == participant_id)
    )
    participant = result.scalar_one_or_none()

    if not participant:
        raise NotFoundError("Participant", participant_id)

    if participant.meeting.company_id != user.company_id:
        raise AuthorizationError("Access denied to this participant")

    # Update risk scores
    participant.update_risk_scores(
        deepfake=request.deepfake_confidence,
        social_engineering=request.social_engineering_score,
    )

    await session.commit()
    await session.refresh(participant)

    return ParticipantResponse.model_validate(participant)


@router.post("/{participant_id}/verify", response_model=ParticipantResponse)
async def verify_participant(
    participant_id: str,
    method: str = Query(description="Verification method (sms, voice, push)"),
    session: AsyncSessionDep = None,
    user: CurrentUserDep = None,
):
    """
    Mark participant as verified.

    Args:
        participant_id: Participant unique identifier.
        method: Verification method used.

    Returns:
        Updated participant.
    """
    result = await session.execute(
        select(Participant)
        .options(selectinload(Participant.meeting))
        .where(Participant.id == participant_id)
    )
    participant = result.scalar_one_or_none()

    if not participant:
        raise NotFoundError("Participant", participant_id)

    if participant.meeting.company_id != user.company_id:
        raise AuthorizationError("Access denied to this participant")

    participant.verify(method)

    await session.commit()
    await session.refresh(participant)

    return ParticipantResponse.model_validate(participant)


@router.post("/{participant_id}/leave", response_model=ParticipantResponse)
async def participant_leave(
    participant_id: str,
    session: AsyncSessionDep,
    user: CurrentUserDep,
):
    """
    Mark participant as having left the meeting.

    Args:
        participant_id: Participant unique identifier.

    Returns:
        Updated participant.
    """
    result = await session.execute(
        select(Participant)
        .options(selectinload(Participant.meeting))
        .where(Participant.id == participant_id)
    )
    participant = result.scalar_one_or_none()

    if not participant:
        raise NotFoundError("Participant", participant_id)

    if participant.meeting.company_id != user.company_id:
        raise AuthorizationError("Access denied to this participant")

    participant.leave()

    # Update meeting participant count
    participant.meeting.participant_count = max(0, participant.meeting.participant_count - 1)

    await session.commit()
    await session.refresh(participant)

    return ParticipantResponse.model_validate(participant)
