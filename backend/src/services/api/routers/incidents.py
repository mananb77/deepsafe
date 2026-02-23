"""
Incidents Router

Endpoints for security incident management.
"""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Query, status
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from src.shared.models.meeting import Meeting
from src.shared.models.incident import Incident, IncidentType, IncidentSeverity, IncidentStatus
from src.shared.models.audit_log import AuditLog, AuditAction
from src.shared.schemas.incident import (
    IncidentCreate,
    IncidentUpdate,
    IncidentResponse,
    IncidentDetailResponse,
    IncidentListResponse,
    IncidentResolveRequest,
    IncidentEscalateRequest,
    IncidentStatsResponse,
)
from src.shared.schemas.base import SuccessResponse
from src.services.api.dependencies import (
    AsyncSessionDep,
    CurrentUserDep,
    SecurityAnalystDep,
    PaginationDep,
    RequestMetadataDep,
)
from src.services.api.exceptions import NotFoundError, AuthorizationError

router = APIRouter()


@router.get("", response_model=IncidentListResponse)
async def list_incidents(
    session: AsyncSessionDep,
    user: CurrentUserDep,
    pagination: PaginationDep,
    meeting_id: Optional[str] = Query(default=None),
    incident_type: Optional[IncidentType] = Query(default=None),
    severity: Optional[IncidentSeverity] = Query(default=None),
    status_filter: Optional[IncidentStatus] = Query(default=None, alias="status"),
):
    """
    List incidents for the current user's company.

    Args:
        meeting_id: Filter by meeting.
        incident_type: Filter by incident type.
        severity: Filter by severity.
        status_filter: Filter by status.

    Returns:
        Paginated list of incidents.
    """
    # Base query - incidents from company's meetings
    query = select(Incident).join(Meeting).where(
        Meeting.company_id == user.company_id
    )

    if meeting_id:
        query = query.where(Incident.meeting_id == meeting_id)

    if incident_type:
        query = query.where(Incident.incident_type == incident_type)

    if severity:
        query = query.where(Incident.severity == severity)

    if status_filter:
        query = query.where(Incident.status == status_filter)

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total = await session.scalar(count_query)

    # Apply pagination
    query = query.offset(pagination.offset).limit(pagination.limit)
    query = query.order_by(Incident.detected_at.desc())

    result = await session.execute(query)
    incidents = result.scalars().all()

    return IncidentListResponse(
        items=[IncidentResponse.model_validate(i) for i in incidents],
        total=total,
        page=pagination.page,
        page_size=pagination.page_size,
        pages=(total + pagination.page_size - 1) // pagination.page_size,
    )


@router.get("/stats", response_model=IncidentStatsResponse)
async def get_incident_stats(
    session: AsyncSessionDep,
    user: CurrentUserDep,
):
    """
    Get incident statistics for dashboard.

    Returns:
        Incident statistics.
    """
    company_id = user.company_id

    # Base subquery for company's incidents
    incident_ids = select(Incident.id).join(Meeting).where(
        Meeting.company_id == company_id
    )

    total = await session.scalar(
        select(func.count(Incident.id)).where(Incident.id.in_(incident_ids))
    )

    open_incidents = await session.scalar(
        select(func.count(Incident.id)).where(
            Incident.id.in_(incident_ids),
            Incident.status.in_([IncidentStatus.DETECTED, IncidentStatus.INVESTIGATING]),
        )
    )

    resolved = await session.scalar(
        select(func.count(Incident.id)).where(
            Incident.id.in_(incident_ids),
            Incident.status == IncidentStatus.RESOLVED,
        )
    )

    false_positives = await session.scalar(
        select(func.count(Incident.id)).where(
            Incident.id.in_(incident_ids),
            Incident.status == IncidentStatus.FALSE_POSITIVE,
        )
    )

    # By type
    by_type = {}
    for incident_type in IncidentType:
        count = await session.scalar(
            select(func.count(Incident.id)).where(
                Incident.id.in_(incident_ids),
                Incident.incident_type == incident_type,
            )
        )
        by_type[incident_type.value] = count or 0

    # By severity
    by_severity = {}
    for severity in IncidentSeverity:
        count = await session.scalar(
            select(func.count(Incident.id)).where(
                Incident.id.in_(incident_ids),
                Incident.severity == severity,
            )
        )
        by_severity[severity.value] = count or 0

    # Detection accuracy
    total_resolved = (resolved or 0) + (false_positives or 0)
    detection_accuracy = (resolved / total_resolved * 100) if total_resolved > 0 else 100.0

    return IncidentStatsResponse(
        total_incidents=total or 0,
        open_incidents=open_incidents or 0,
        resolved_incidents=resolved or 0,
        false_positives=false_positives or 0,
        by_type=by_type,
        by_severity=by_severity,
        detection_accuracy=round(detection_accuracy, 2),
    )


@router.get("/{incident_id}", response_model=IncidentDetailResponse)
async def get_incident(
    incident_id: str,
    session: AsyncSessionDep,
    user: CurrentUserDep,
):
    """
    Get detailed incident information.

    Args:
        incident_id: Incident unique identifier.

    Returns:
        Incident details.
    """
    result = await session.execute(
        select(Incident)
        .options(
            selectinload(Incident.meeting),
            selectinload(Incident.participant),
        )
        .where(Incident.id == incident_id)
    )
    incident = result.scalar_one_or_none()

    if not incident:
        raise NotFoundError("Incident", incident_id)

    if incident.meeting.company_id != user.company_id:
        raise AuthorizationError("Access denied to this incident")

    # Build response
    response_data = IncidentResponse.model_validate(incident).model_dump()
    response_data["meeting_title"] = incident.meeting.title
    response_data["meeting_platform"] = incident.meeting.platform.value
    response_data["participant_name"] = incident.participant.display_name if incident.participant else None
    response_data["participant_email"] = incident.participant.email if incident.participant else None
    response_data["company_id"] = incident.meeting.company_id
    response_data["evidence_references"] = []
    response_data["verification_count"] = 0
    response_data["related_incidents"] = []

    return IncidentDetailResponse(**response_data)


@router.post("", response_model=IncidentResponse, status_code=status.HTTP_201_CREATED)
async def create_incident(
    request: IncidentCreate,
    session: AsyncSessionDep,
    user: CurrentUserDep,
    metadata: RequestMetadataDep,
):
    """
    Create a new security incident.

    Args:
        request: Incident creation data.

    Returns:
        Created incident.
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

    incident = Incident(
        meeting_id=request.meeting_id,
        participant_id=request.participant_id,
        incident_type=request.incident_type,
        severity=request.severity,
        title=request.title,
        description=request.description,
        confidence_score=request.confidence_score,
        meeting_timestamp_seconds=request.meeting_timestamp_seconds,
        evidence_summary=request.evidence_summary,
        detection_method=request.detection_method,
        detection_model=request.detection_model,
        raw_analysis_data=request.raw_analysis_data,
    )

    session.add(incident)

    # Update meeting flags
    if request.incident_type in [IncidentType.AUDIO_DEEPFAKE, IncidentType.VIDEO_DEEPFAKE]:
        meeting.deepfake_detected = True
    elif request.incident_type == IncidentType.SOCIAL_ENGINEERING:
        meeting.social_engineering_detected = True

    # Audit log
    audit_log = AuditLog.log_security_event(
        action=AuditAction.INCIDENT_CREATED,
        meeting_id=request.meeting_id,
        company_id=meeting.company_id,
        description=f"Incident created: {request.title}",
        target_id=incident.id,
        metadata={
            "incident_type": request.incident_type.value,
            "severity": request.severity.value,
        },
    )
    session.add(audit_log)

    await session.commit()
    await session.refresh(incident)

    return IncidentResponse.model_validate(incident)


@router.patch("/{incident_id}", response_model=IncidentResponse)
async def update_incident(
    incident_id: str,
    request: IncidentUpdate,
    session: AsyncSessionDep,
    analyst: SecurityAnalystDep,
):
    """
    Update incident information (security analyst only).

    Args:
        incident_id: Incident unique identifier.
        request: Update data.

    Returns:
        Updated incident.
    """
    result = await session.execute(
        select(Incident)
        .options(selectinload(Incident.meeting))
        .where(Incident.id == incident_id)
    )
    incident = result.scalar_one_or_none()

    if not incident:
        raise NotFoundError("Incident", incident_id)

    if incident.meeting.company_id != analyst.company_id:
        raise AuthorizationError("Access denied to this incident")

    # Apply updates
    update_data = request.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if hasattr(incident, field):
            setattr(incident, field, value)

    await session.commit()
    await session.refresh(incident)

    return IncidentResponse.model_validate(incident)


@router.post("/{incident_id}/resolve", response_model=IncidentResponse)
async def resolve_incident(
    incident_id: str,
    request: IncidentResolveRequest,
    session: AsyncSessionDep,
    analyst: SecurityAnalystDep,
    metadata: RequestMetadataDep,
):
    """
    Resolve an incident (security analyst only).

    Args:
        incident_id: Incident unique identifier.
        request: Resolution data.

    Returns:
        Resolved incident.
    """
    result = await session.execute(
        select(Incident)
        .options(selectinload(Incident.meeting))
        .where(Incident.id == incident_id)
    )
    incident = result.scalar_one_or_none()

    if not incident:
        raise NotFoundError("Incident", incident_id)

    if incident.meeting.company_id != analyst.company_id:
        raise AuthorizationError("Access denied to this incident")

    if request.is_false_positive:
        incident.mark_false_positive(request.resolution_notes, analyst.id)
    else:
        incident.resolve(request.resolution_notes, analyst.id)

    # Audit log
    audit_log = AuditLog.log_action(
        action=AuditAction.INCIDENT_RESOLVED if not request.is_false_positive else AuditAction.INCIDENT_FALSE_POSITIVE,
        description=f"Incident resolved: {incident.title}",
        user_id=analyst.id,
        company_id=analyst.company_id,
        meeting_id=incident.meeting_id,
        target_type="incident",
        target_id=incident.id,
        ip_address=metadata.get("ip_address"),
    )
    session.add(audit_log)

    await session.commit()
    await session.refresh(incident)

    return IncidentResponse.model_validate(incident)


@router.post("/{incident_id}/escalate", response_model=IncidentResponse)
async def escalate_incident(
    incident_id: str,
    request: IncidentEscalateRequest,
    session: AsyncSessionDep,
    analyst: SecurityAnalystDep,
):
    """
    Escalate incident severity (security analyst only).

    Args:
        incident_id: Incident unique identifier.
        request: Escalation data.

    Returns:
        Escalated incident.
    """
    result = await session.execute(
        select(Incident)
        .options(selectinload(Incident.meeting))
        .where(Incident.id == incident_id)
    )
    incident = result.scalar_one_or_none()

    if not incident:
        raise NotFoundError("Incident", incident_id)

    if incident.meeting.company_id != analyst.company_id:
        raise AuthorizationError("Access denied to this incident")

    incident.escalate(request.new_severity)
    incident.add_action(f"Escalated to {request.new_severity.value}", {"reason": request.reason})

    await session.commit()
    await session.refresh(incident)

    return IncidentResponse.model_validate(incident)


@router.post("/{incident_id}/investigate", response_model=IncidentResponse)
async def investigate_incident(
    incident_id: str,
    session: AsyncSessionDep,
    analyst: SecurityAnalystDep,
):
    """
    Mark incident as under investigation (security analyst only).

    Args:
        incident_id: Incident unique identifier.

    Returns:
        Updated incident.
    """
    result = await session.execute(
        select(Incident)
        .options(selectinload(Incident.meeting))
        .where(Incident.id == incident_id)
    )
    incident = result.scalar_one_or_none()

    if not incident:
        raise NotFoundError("Incident", incident_id)

    if incident.meeting.company_id != analyst.company_id:
        raise AuthorizationError("Access denied to this incident")

    incident.investigate()

    await session.commit()
    await session.refresh(incident)

    return IncidentResponse.model_validate(incident)
