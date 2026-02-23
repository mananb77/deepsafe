"""
Companies Router

Endpoints for company management.
"""

from fastapi import APIRouter

from sqlalchemy import select

from src.shared.models.company import Company
from src.shared.models.user import User
from src.shared.models.meeting import Meeting, MeetingStatus
from src.shared.models.incident import Incident, IncidentStatus
from src.shared.schemas.company import (
    CompanyUpdate,
    CompanyResponse,
    CompanyStatsResponse,
)
from src.services.api.dependencies import (
    AsyncSessionDep,
    CurrentUserDep,
    AdminUserDep,
    RequestMetadataDep,
)
from src.services.api.exceptions import NotFoundError

router = APIRouter()


@router.get("/current", response_model=CompanyResponse)
async def get_current_company(
    session: AsyncSessionDep,
    user: CurrentUserDep,
):
    """
    Get the current user's company.

    Returns:
        Company details.
    """
    result = await session.execute(
        select(Company).where(Company.id == user.company_id)
    )
    company = result.scalar_one_or_none()

    if not company:
        raise NotFoundError("Company", user.company_id)

    return CompanyResponse.model_validate(company)


@router.patch("/current", response_model=CompanyResponse)
async def update_current_company(
    request: CompanyUpdate,
    session: AsyncSessionDep,
    admin: AdminUserDep,
    metadata: RequestMetadataDep,
):
    """
    Update the current user's company (admin only).

    Args:
        request: Update data.

    Returns:
        Updated company.
    """
    result = await session.execute(
        select(Company).where(Company.id == admin.company_id)
    )
    company = result.scalar_one_or_none()

    if not company:
        raise NotFoundError("Company", admin.company_id)

    # Apply updates
    update_data = request.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if hasattr(company, field):
            setattr(company, field, value)

    await session.commit()
    await session.refresh(company)

    return CompanyResponse.model_validate(company)


@router.get("/current/stats", response_model=CompanyStatsResponse)
async def get_company_stats(
    session: AsyncSessionDep,
    user: CurrentUserDep,
):
    """
    Get statistics for the current user's company.

    Returns:
        Company statistics.
    """
    from sqlalchemy import func
    from datetime import datetime

    company_id = user.company_id

    # User counts
    total_users = await session.scalar(
        select(func.count(User.id)).where(
            User.company_id == company_id,
            User.is_deleted == False,
        )
    )

    active_users = await session.scalar(
        select(func.count(User.id)).where(
            User.company_id == company_id,
            User.is_deleted == False,
            User.is_active == True,
        )
    )

    # Meeting counts
    total_meetings = await session.scalar(
        select(func.count(Meeting.id)).where(Meeting.company_id == company_id)
    )

    # This month's meetings
    start_of_month = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    meetings_this_month = await session.scalar(
        select(func.count(Meeting.id)).where(
            Meeting.company_id == company_id,
            Meeting.created_at >= start_of_month,
        )
    )

    active_meetings = await session.scalar(
        select(func.count(Meeting.id)).where(
            Meeting.company_id == company_id,
            Meeting.status == MeetingStatus.IN_PROGRESS,
        )
    )

    # Incident counts
    total_incidents = await session.scalar(
        select(func.count(Incident.id)).where(
            Incident.meeting_id.in_(
                select(Meeting.id).where(Meeting.company_id == company_id)
            )
        )
    )

    open_incidents = await session.scalar(
        select(func.count(Incident.id)).where(
            Incident.meeting_id.in_(
                select(Meeting.id).where(Meeting.company_id == company_id)
            ),
            Incident.status.in_([IncidentStatus.DETECTED, IncidentStatus.INVESTIGATING]),
        )
    )

    # High risk meetings
    from src.shared.models.meeting import RiskLevel
    high_risk_meetings = await session.scalar(
        select(func.count(Meeting.id)).where(
            Meeting.company_id == company_id,
            Meeting.risk_level.in_([RiskLevel.HIGH, RiskLevel.CRITICAL]),
        )
    )

    # Average risk score
    avg_risk = await session.scalar(
        select(func.avg(Meeting.risk_score)).where(Meeting.company_id == company_id)
    )

    # Verification stats
    from src.shared.models.verification import Verification, VerificationStatus
    from src.shared.models.participant import Participant

    verifications_triggered = await session.scalar(
        select(func.count(Verification.id)).where(
            Verification.participant_id.in_(
                select(Participant.id).where(
                    Participant.meeting_id.in_(
                        select(Meeting.id).where(Meeting.company_id == company_id)
                    )
                )
            )
        )
    )

    verifications_completed = await session.scalar(
        select(func.count(Verification.id)).where(
            Verification.participant_id.in_(
                select(Participant.id).where(
                    Participant.meeting_id.in_(
                        select(Meeting.id).where(Meeting.company_id == company_id)
                    )
                )
            ),
            Verification.status == VerificationStatus.VERIFIED,
        )
    )

    return CompanyStatsResponse(
        total_users=total_users or 0,
        active_users=active_users or 0,
        total_meetings=total_meetings or 0,
        meetings_this_month=meetings_this_month or 0,
        active_meetings=active_meetings or 0,
        total_incidents=total_incidents or 0,
        open_incidents=open_incidents or 0,
        high_risk_meetings=high_risk_meetings or 0,
        average_risk_score=round(avg_risk or 0, 2),
        verifications_triggered=verifications_triggered or 0,
        verifications_completed=verifications_completed or 0,
    )
