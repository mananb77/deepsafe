"""
DeepSafe Pydantic Schemas

Request/response validation schemas for the API.
"""

from src.shared.schemas.base import BaseSchema, PaginatedResponse, TimestampSchema
from src.shared.schemas.auth import (
    TokenResponse,
    TokenPayload,
    LoginRequest,
    RefreshTokenRequest,
)
from src.shared.schemas.user import (
    UserBase,
    UserCreate,
    UserUpdate,
    UserResponse,
    UserListResponse,
)
from src.shared.schemas.company import (
    CompanyBase,
    CompanyCreate,
    CompanyUpdate,
    CompanyResponse,
)
from src.shared.schemas.meeting import (
    MeetingBase,
    MeetingCreate,
    MeetingUpdate,
    MeetingResponse,
    MeetingListResponse,
    MeetingRiskUpdate,
)
from src.shared.schemas.participant import (
    ParticipantBase,
    ParticipantCreate,
    ParticipantUpdate,
    ParticipantResponse,
)
from src.shared.schemas.incident import (
    IncidentBase,
    IncidentCreate,
    IncidentUpdate,
    IncidentResponse,
    IncidentListResponse,
)
from src.shared.schemas.verification import (
    VerificationCreate,
    VerificationResponse,
    VerificationCheck,
)
from src.shared.schemas.risk import (
    RiskIndicatorCreate,
    RiskIndicatorResponse,
    RiskScoreResponse,
)

__all__ = [
    # Base
    "BaseSchema",
    "PaginatedResponse",
    "TimestampSchema",
    # Auth
    "TokenResponse",
    "TokenPayload",
    "LoginRequest",
    "RefreshTokenRequest",
    # User
    "UserBase",
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "UserListResponse",
    # Company
    "CompanyBase",
    "CompanyCreate",
    "CompanyUpdate",
    "CompanyResponse",
    # Meeting
    "MeetingBase",
    "MeetingCreate",
    "MeetingUpdate",
    "MeetingResponse",
    "MeetingListResponse",
    "MeetingRiskUpdate",
    # Participant
    "ParticipantBase",
    "ParticipantCreate",
    "ParticipantUpdate",
    "ParticipantResponse",
    # Incident
    "IncidentBase",
    "IncidentCreate",
    "IncidentUpdate",
    "IncidentResponse",
    "IncidentListResponse",
    # Verification
    "VerificationCreate",
    "VerificationResponse",
    "VerificationCheck",
    # Risk
    "RiskIndicatorCreate",
    "RiskIndicatorResponse",
    "RiskScoreResponse",
]
