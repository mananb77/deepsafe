"""
Incident Schemas

Request/response schemas for security incidents.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import Field

from src.shared.models.incident import IncidentSeverity, IncidentStatus, IncidentType
from src.shared.schemas.base import BaseSchema, PaginatedResponse, TimestampSchema


class IncidentBase(BaseSchema):
    """Base incident schema."""

    incident_type: IncidentType = Field(description="Type of security incident")
    title: str = Field(min_length=1, max_length=255, description="Incident title")
    description: Optional[str] = Field(default=None, description="Detailed description")


class IncidentCreate(IncidentBase):
    """Schema for creating an incident."""

    meeting_id: str = Field(description="Meeting where incident occurred")
    participant_id: Optional[str] = Field(
        default=None,
        description="Participant involved (if applicable)",
    )
    severity: IncidentSeverity = Field(default=IncidentSeverity.MEDIUM)
    confidence_score: float = Field(ge=0, le=1, description="Detection confidence")
    meeting_timestamp_seconds: Optional[float] = Field(
        default=None,
        description="Timestamp within the meeting",
    )
    evidence_summary: Optional[str] = None
    detection_method: Optional[str] = Field(default=None, max_length=100)
    detection_model: Optional[str] = Field(default=None, max_length=100)
    raw_analysis_data: Optional[Dict[str, Any]] = None


class IncidentUpdate(BaseSchema):
    """Schema for updating an incident."""

    title: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = None
    severity: Optional[IncidentSeverity] = None
    status: Optional[IncidentStatus] = None
    evidence_summary: Optional[str] = None


class IncidentResolveRequest(BaseSchema):
    """Request to resolve an incident."""

    resolution_notes: str = Field(
        min_length=1,
        max_length=2000,
        description="Notes about the resolution",
    )
    is_false_positive: bool = Field(
        default=False,
        description="Mark as false positive",
    )


class IncidentEscalateRequest(BaseSchema):
    """Request to escalate an incident."""

    new_severity: IncidentSeverity
    reason: str = Field(min_length=1, max_length=500)
    notify_additional: List[str] = Field(
        default_factory=list,
        description="Additional email addresses to notify",
    )


class IncidentActionRequest(BaseSchema):
    """Request to add an action to an incident."""

    action: str = Field(min_length=1, max_length=255)
    details: Optional[Dict[str, Any]] = None


class EvidenceReference(BaseSchema):
    """Reference to forensic evidence."""

    evidence_id: str
    evidence_type: str
    description: str
    url: Optional[str] = None


class IncidentResponse(TimestampSchema):
    """Incident response schema."""

    id: str
    meeting_id: str
    participant_id: Optional[str] = None
    incident_type: IncidentType
    severity: IncidentSeverity
    status: IncidentStatus
    title: str
    description: Optional[str] = None
    confidence_score: float
    detected_at: datetime
    meeting_timestamp_seconds: Optional[float] = None
    evidence_summary: Optional[str] = None
    screenshot_url: Optional[str] = None
    audio_clip_url: Optional[str] = None
    resolved_at: Optional[datetime] = None
    resolved_by_user_id: Optional[str] = None
    resolution_notes: Optional[str] = None
    actions_taken: Optional[List[Dict[str, Any]]] = None
    verification_triggered: bool
    alert_sent: bool
    alert_sent_at: Optional[datetime] = None
    detection_method: Optional[str] = None
    detection_model: Optional[str] = None


class IncidentDetailResponse(IncidentResponse):
    """Detailed incident response with related data."""

    meeting_title: str
    meeting_platform: str
    participant_name: Optional[str] = None
    participant_email: Optional[str] = None
    company_id: str
    evidence_references: List[EvidenceReference] = Field(default_factory=list)
    verification_count: int = 0
    related_incidents: List["IncidentResponse"] = Field(default_factory=list)


class IncidentListResponse(PaginatedResponse[IncidentResponse]):
    """Paginated incident list response."""

    pass


class IncidentStatsResponse(BaseSchema):
    """Incident statistics for dashboard."""

    total_incidents: int
    open_incidents: int
    resolved_incidents: int
    false_positives: int
    by_type: Dict[str, int] = Field(
        description="Count by incident type",
    )
    by_severity: Dict[str, int] = Field(
        description="Count by severity",
    )
    average_resolution_time_hours: Optional[float] = None
    detection_accuracy: float = Field(
        description="Percentage of non-false-positive incidents",
    )


class IncidentTimelineEvent(BaseSchema):
    """Timeline event for incident history."""

    timestamp: datetime
    event_type: str
    description: str
    user_id: Optional[str] = None
    user_name: Optional[str] = None
    extra_data: Optional[Dict[str, Any]] = None


class IncidentTimelineResponse(BaseSchema):
    """Incident timeline response."""

    incident_id: str
    events: List[IncidentTimelineEvent]


class IncidentExportRequest(BaseSchema):
    """Request to export incidents."""

    format: str = Field(description="csv, json, or pdf")
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    incident_types: Optional[List[IncidentType]] = None
    severities: Optional[List[IncidentSeverity]] = None
    statuses: Optional[List[IncidentStatus]] = None
    include_evidence: bool = Field(default=False)
