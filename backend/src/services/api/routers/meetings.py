"""
Meetings Router

Endpoints for meeting management and monitoring.
"""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Query, status
from sqlalchemy import select, func, or_
from sqlalchemy.orm import selectinload

from src.shared.models.meeting import Meeting, MeetingPlatform, MeetingStatus, RiskLevel
from src.shared.models.participant import Participant
from src.shared.models.incident import Incident
from src.shared.schemas.meeting import (
    MeetingCreate,
    MeetingUpdate,
    MeetingResponse,
    MeetingDetailResponse,
    MeetingListResponse,
    MeetingRiskUpdate,
    MeetingStatsResponse,
    ParticipantSummary,
)
from src.shared.schemas.base import SuccessResponse
from src.services.api.dependencies import (
    AsyncSessionDep,
    CurrentUserDep,
    PaginationDep,
    MongoDBDep,
)
from src.services.api.exceptions import NotFoundError, AuthorizationError

router = APIRouter()


@router.get("", response_model=MeetingListResponse)
async def list_meetings(
    session: AsyncSessionDep,
    user: CurrentUserDep,
    pagination: PaginationDep,
    platform: Optional[MeetingPlatform] = Query(default=None),
    status_filter: Optional[MeetingStatus] = Query(default=None, alias="status"),
    risk_level: Optional[RiskLevel] = Query(default=None),
    search: Optional[str] = Query(default=None, description="Search by title"),
):
    """
    List meetings for the current user's company.

    Args:
        platform: Filter by platform.
        status_filter: Filter by meeting status.
        risk_level: Filter by risk level.
        search: Search by title.

    Returns:
        Paginated list of meetings.
    """
    query = select(Meeting).where(
        Meeting.company_id == user.company_id
    )

    if platform:
        query = query.where(Meeting.platform == platform)

    if status_filter:
        query = query.where(Meeting.status == status_filter)

    if risk_level:
        query = query.where(Meeting.risk_level == risk_level)

    if search:
        query = query.where(Meeting.title.ilike(f"%{search}%"))

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total = await session.scalar(count_query)

    # Apply pagination and ordering
    query = query.offset(pagination.offset).limit(pagination.limit)
    query = query.order_by(Meeting.created_at.desc())

    result = await session.execute(query)
    meetings = result.scalars().all()

    return MeetingListResponse(
        items=[MeetingResponse.model_validate(m) for m in meetings],
        total=total,
        page=pagination.page,
        page_size=pagination.page_size,
        pages=(total + pagination.page_size - 1) // pagination.page_size,
    )


@router.get("/active", response_model=list[MeetingResponse])
async def list_active_meetings(
    session: AsyncSessionDep,
    user: CurrentUserDep,
):
    """
    List currently active meetings.

    Returns:
        List of active meetings.
    """
    result = await session.execute(
        select(Meeting).where(
            Meeting.company_id == user.company_id,
            Meeting.status == MeetingStatus.IN_PROGRESS,
        ).order_by(Meeting.actual_start_at.desc())
    )
    meetings = result.scalars().all()

    return [MeetingResponse.model_validate(m) for m in meetings]


@router.get("/stats", response_model=MeetingStatsResponse)
async def get_meeting_stats(
    session: AsyncSessionDep,
    user: CurrentUserDep,
):
    """
    Get meeting statistics for dashboard.

    Returns:
        Meeting statistics.
    """
    company_id = user.company_id

    total = await session.scalar(
        select(func.count(Meeting.id)).where(Meeting.company_id == company_id)
    )

    active = await session.scalar(
        select(func.count(Meeting.id)).where(
            Meeting.company_id == company_id,
            Meeting.status == MeetingStatus.IN_PROGRESS,
        )
    )

    completed = await session.scalar(
        select(func.count(Meeting.id)).where(
            Meeting.company_id == company_id,
            Meeting.status == MeetingStatus.COMPLETED,
        )
    )

    high_risk = await session.scalar(
        select(func.count(Meeting.id)).where(
            Meeting.company_id == company_id,
            Meeting.risk_level.in_([RiskLevel.HIGH, RiskLevel.CRITICAL]),
        )
    )

    avg_risk = await session.scalar(
        select(func.avg(Meeting.risk_score)).where(Meeting.company_id == company_id)
    )

    total_participants = await session.scalar(
        select(func.count(Participant.id)).where(
            Participant.meeting_id.in_(
                select(Meeting.id).where(Meeting.company_id == company_id)
            )
        )
    )

    deepfake_detections = await session.scalar(
        select(func.count(Meeting.id)).where(
            Meeting.company_id == company_id,
            Meeting.deepfake_detected == True,
        )
    )

    se_detections = await session.scalar(
        select(func.count(Meeting.id)).where(
            Meeting.company_id == company_id,
            Meeting.social_engineering_detected == True,
        )
    )

    verifications_triggered = await session.scalar(
        select(func.count(Meeting.id)).where(
            Meeting.company_id == company_id,
            Meeting.verification_triggered == True,
        )
    )

    return MeetingStatsResponse(
        total_meetings=total or 0,
        active_meetings=active or 0,
        completed_meetings=completed or 0,
        high_risk_meetings=high_risk or 0,
        average_risk_score=round(avg_risk or 0, 2),
        total_participants=total_participants or 0,
        deepfake_detections=deepfake_detections or 0,
        social_engineering_detections=se_detections or 0,
        verifications_triggered=verifications_triggered or 0,
    )


@router.get("/{meeting_id}", response_model=MeetingDetailResponse)
async def get_meeting(
    meeting_id: str,
    session: AsyncSessionDep,
    user: CurrentUserDep,
):
    """
    Get detailed meeting information.

    Args:
        meeting_id: Meeting unique identifier.

    Returns:
        Meeting details with participants.
    """
    result = await session.execute(
        select(Meeting)
        .options(selectinload(Meeting.participants))
        .where(Meeting.id == meeting_id)
    )
    meeting = result.scalar_one_or_none()

    if not meeting:
        raise NotFoundError("Meeting", meeting_id)

    if meeting.company_id != user.company_id:
        raise AuthorizationError("Access denied to this meeting")

    # Get counts
    incident_count = await session.scalar(
        select(func.count(Incident.id)).where(Incident.meeting_id == meeting_id)
    )

    from src.shared.models.risk_indicator import RiskIndicator
    risk_indicator_count = await session.scalar(
        select(func.count(RiskIndicator.id)).where(RiskIndicator.meeting_id == meeting_id)
    )

    # Build response
    response_data = MeetingResponse.model_validate(meeting).model_dump()
    response_data["participants"] = [
        ParticipantSummary(
            id=p.id,
            display_name=p.display_name,
            email=p.email,
            trust_level=p.trust_level.value,
            is_flagged=p.is_flagged,
            composite_risk_score=p.composite_risk_score,
        )
        for p in meeting.participants
    ]
    response_data["incident_count"] = incident_count or 0
    response_data["risk_indicator_count"] = risk_indicator_count or 0

    return MeetingDetailResponse(**response_data)


@router.post("", response_model=MeetingResponse, status_code=status.HTTP_201_CREATED)
async def create_meeting(
    request: MeetingCreate,
    session: AsyncSessionDep,
    user: CurrentUserDep,
):
    """
    Register a new meeting for monitoring.

    Args:
        request: Meeting creation data.

    Returns:
        Created meeting.
    """
    meeting = Meeting(
        platform=request.platform,
        platform_meeting_id=request.platform_meeting_id,
        platform_meeting_url=request.platform_meeting_url,
        company_id=user.company_id,
        title=request.title,
        description=request.description,
        host_email=request.host_email,
        scheduled_start_at=request.scheduled_start_at,
        scheduled_end_at=request.scheduled_end_at,
        extra_data=request.extra_data,
    )

    session.add(meeting)
    await session.commit()
    await session.refresh(meeting)

    return MeetingResponse.model_validate(meeting)


@router.patch("/{meeting_id}", response_model=MeetingResponse)
async def update_meeting(
    meeting_id: str,
    request: MeetingUpdate,
    session: AsyncSessionDep,
    user: CurrentUserDep,
):
    """
    Update meeting information.

    Args:
        meeting_id: Meeting unique identifier.
        request: Update data.

    Returns:
        Updated meeting.
    """
    result = await session.execute(
        select(Meeting).where(Meeting.id == meeting_id)
    )
    meeting = result.scalar_one_or_none()

    if not meeting:
        raise NotFoundError("Meeting", meeting_id)

    if meeting.company_id != user.company_id:
        raise AuthorizationError("Access denied to this meeting")

    # Apply updates
    update_data = request.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if hasattr(meeting, field):
            setattr(meeting, field, value)

    await session.commit()
    await session.refresh(meeting)

    return MeetingResponse.model_validate(meeting)


@router.post("/{meeting_id}/risk", response_model=MeetingResponse)
async def update_meeting_risk(
    meeting_id: str,
    request: MeetingRiskUpdate,
    session: AsyncSessionDep,
    user: CurrentUserDep,
):
    """
    Update meeting risk score.

    Args:
        meeting_id: Meeting unique identifier.
        request: Risk update data.

    Returns:
        Updated meeting.
    """
    result = await session.execute(
        select(Meeting).where(Meeting.id == meeting_id)
    )
    meeting = result.scalar_one_or_none()

    if not meeting:
        raise NotFoundError("Meeting", meeting_id)

    if meeting.company_id != user.company_id:
        raise AuthorizationError("Access denied to this meeting")

    # Update risk score
    meeting.update_risk(request.risk_score)

    if request.deepfake_detected is not None:
        meeting.deepfake_detected = request.deepfake_detected

    if request.social_engineering_detected is not None:
        meeting.social_engineering_detected = request.social_engineering_detected

    if request.verification_triggered is not None:
        meeting.verification_triggered = request.verification_triggered

    await session.commit()
    await session.refresh(meeting)

    return MeetingResponse.model_validate(meeting)


@router.post("/{meeting_id}/start", response_model=MeetingResponse)
async def start_meeting(
    meeting_id: str,
    session: AsyncSessionDep,
    user: CurrentUserDep,
):
    """
    Mark meeting as started.

    Args:
        meeting_id: Meeting unique identifier.

    Returns:
        Updated meeting.
    """
    result = await session.execute(
        select(Meeting).where(Meeting.id == meeting_id)
    )
    meeting = result.scalar_one_or_none()

    if not meeting:
        raise NotFoundError("Meeting", meeting_id)

    if meeting.company_id != user.company_id:
        raise AuthorizationError("Access denied to this meeting")

    meeting.start()
    await session.commit()
    await session.refresh(meeting)

    return MeetingResponse.model_validate(meeting)


@router.post("/{meeting_id}/end", response_model=MeetingResponse)
async def end_meeting(
    meeting_id: str,
    session: AsyncSessionDep,
    user: CurrentUserDep,
):
    """
    Mark meeting as ended.

    Args:
        meeting_id: Meeting unique identifier.

    Returns:
        Updated meeting.
    """
    result = await session.execute(
        select(Meeting).where(Meeting.id == meeting_id)
    )
    meeting = result.scalar_one_or_none()

    if not meeting:
        raise NotFoundError("Meeting", meeting_id)

    if meeting.company_id != user.company_id:
        raise AuthorizationError("Access denied to this meeting")

    meeting.end()
    await session.commit()
    await session.refresh(meeting)

    return MeetingResponse.model_validate(meeting)


@router.post("/{meeting_id}/join-bot", response_model=SuccessResponse)
async def join_bot(
    meeting_id: str,
    session: AsyncSessionDep,
    user: CurrentUserDep,
):
    """
    Deploy a bot to join the meeting and start monitoring.

    Launches the appropriate platform bot (Zoom/Google Meet)
    based on the meeting's platform.
    """
    result = await session.execute(
        select(Meeting).where(Meeting.id == meeting_id)
    )
    meeting = result.scalar_one_or_none()

    if not meeting:
        raise NotFoundError("Meeting", meeting_id)

    if meeting.company_id != user.company_id:
        raise AuthorizationError("Access denied to this meeting")

    if meeting.bot_joined:
        return SuccessResponse(message="Bot already in meeting")

    # Mark bot as joining
    meeting.bot_joined = True
    meeting.bot_joined_at = datetime.utcnow()

    # Start the meeting if not already
    if meeting.status == MeetingStatus.SCHEDULED:
        meeting.start()

    await session.commit()
    await session.refresh(meeting)

    # TODO: Dispatch Celery task to actually start the bot
    # from src.shared.messaging.tasks import start_meeting_bot
    # start_meeting_bot.delay(str(meeting.id), meeting.platform.value, meeting.platform_meeting_url)

    return SuccessResponse(
        message=f"Bot deployment initiated for {meeting.platform.value} meeting"
    )


@router.post("/{meeting_id}/leave-bot", response_model=SuccessResponse)
async def leave_bot(
    meeting_id: str,
    session: AsyncSessionDep,
    user: CurrentUserDep,
):
    """
    Remove the bot from the meeting.
    """
    result = await session.execute(
        select(Meeting).where(Meeting.id == meeting_id)
    )
    meeting = result.scalar_one_or_none()

    if not meeting:
        raise NotFoundError("Meeting", meeting_id)

    if meeting.company_id != user.company_id:
        raise AuthorizationError("Access denied to this meeting")

    if not meeting.bot_joined:
        return SuccessResponse(message="Bot is not in this meeting")

    meeting.bot_joined = False
    meeting.bot_left_at = datetime.utcnow()

    await session.commit()
    await session.refresh(meeting)

    # TODO: Dispatch Celery task to stop the bot
    # from src.shared.messaging.tasks import stop_meeting_bot
    # stop_meeting_bot.delay(str(meeting.id))

    return SuccessResponse(message="Bot removal initiated")


@router.get("/{meeting_id}/transcript")
async def get_meeting_transcript(
    meeting_id: str,
    session: AsyncSessionDep,
    user: CurrentUserDep,
    mongodb: MongoDBDep,
    limit: int = Query(default=100, le=1000),
    skip: int = Query(default=0, ge=0),
):
    """
    Get meeting transcript from MongoDB.

    Args:
        meeting_id: Meeting unique identifier.
        limit: Maximum segments to return.
        skip: Segments to skip.

    Returns:
        Transcript segments.
    """
    # Verify access
    result = await session.execute(
        select(Meeting).where(Meeting.id == meeting_id)
    )
    meeting = result.scalar_one_or_none()

    if not meeting:
        raise NotFoundError("Meeting", meeting_id)

    if meeting.company_id != user.company_id:
        raise AuthorizationError("Access denied to this meeting")

    # Fetch from MongoDB
    segments = await mongodb.get_meeting_transcript(
        meeting_id=meeting_id,
        limit=limit,
        skip=skip,
    )

    return {
        "meeting_id": meeting_id,
        "segments": segments,
        "total_segments": len(segments),
        "has_more": len(segments) == limit,
    }
