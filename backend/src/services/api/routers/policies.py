"""
Policies Router

Endpoints for policy management.
"""

from typing import Optional

from fastapi import APIRouter, Query, status
from sqlalchemy import select, func

from src.shared.models.policy import Policy, PolicyType, PolicyTrigger
from src.shared.schemas.base import SuccessResponse, PaginatedResponse
from src.services.api.dependencies import (
    AsyncSessionDep,
    CurrentUserDep,
    AdminUserDep,
    PaginationDep,
)
from src.services.api.exceptions import NotFoundError, AuthorizationError
from pydantic import BaseModel, Field
from typing import List, Any, Dict
from datetime import datetime


# Policy schemas (inline for this router)
class PolicyBase(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: Optional[str] = None
    policy_type: PolicyType
    trigger: PolicyTrigger
    is_enabled: bool = True
    priority: int = Field(default=100, ge=1)
    conditions: Dict[str, Any] = Field(default_factory=dict)
    actions: List[Dict[str, Any]] = Field(default_factory=list)
    min_risk_score: Optional[float] = Field(default=None, ge=0, le=100)
    max_risk_score: Optional[float] = Field(default=None, ge=0, le=100)
    min_transaction_amount: Optional[float] = None
    max_transaction_amount: Optional[float] = None
    cooldown_minutes: int = Field(default=0, ge=0)


class PolicyCreate(PolicyBase):
    pass


class PolicyUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = None
    is_enabled: Optional[bool] = None
    priority: Optional[int] = Field(default=None, ge=1)
    conditions: Optional[Dict[str, Any]] = None
    actions: Optional[List[Dict[str, Any]]] = None
    min_risk_score: Optional[float] = Field(default=None, ge=0, le=100)
    max_risk_score: Optional[float] = Field(default=None, ge=0, le=100)
    min_transaction_amount: Optional[float] = None
    max_transaction_amount: Optional[float] = None
    cooldown_minutes: Optional[int] = Field(default=None, ge=0)


class PolicyResponse(PolicyBase):
    id: str
    company_id: str
    last_triggered_at: Optional[datetime] = None
    trigger_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


router = APIRouter()


@router.get("", response_model=PaginatedResponse[PolicyResponse])
async def list_policies(
    session: AsyncSessionDep,
    user: CurrentUserDep,
    pagination: PaginationDep,
    policy_type: Optional[PolicyType] = Query(default=None),
    trigger: Optional[PolicyTrigger] = Query(default=None),
    is_enabled: Optional[bool] = Query(default=None),
):
    """
    List policies for the current user's company.

    Args:
        policy_type: Filter by policy type.
        trigger: Filter by trigger event.
        is_enabled: Filter by enabled status.

    Returns:
        Paginated list of policies.
    """
    query = select(Policy).where(
        Policy.company_id == user.company_id,
        Policy.is_deleted == False,
    )

    if policy_type:
        query = query.where(Policy.policy_type == policy_type)

    if trigger:
        query = query.where(Policy.trigger == trigger)

    if is_enabled is not None:
        query = query.where(Policy.is_enabled == is_enabled)

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total = await session.scalar(count_query)

    # Apply pagination and ordering
    query = query.offset(pagination.offset).limit(pagination.limit)
    query = query.order_by(Policy.priority.asc(), Policy.created_at.desc())

    result = await session.execute(query)
    policies = result.scalars().all()

    return PaginatedResponse(
        items=[PolicyResponse.model_validate(p) for p in policies],
        total=total,
        page=pagination.page,
        page_size=pagination.page_size,
        pages=(total + pagination.page_size - 1) // pagination.page_size,
    )


@router.get("/{policy_id}", response_model=PolicyResponse)
async def get_policy(
    policy_id: str,
    session: AsyncSessionDep,
    user: CurrentUserDep,
):
    """
    Get a specific policy.

    Args:
        policy_id: Policy unique identifier.

    Returns:
        Policy details.
    """
    result = await session.execute(
        select(Policy).where(
            Policy.id == policy_id,
            Policy.is_deleted == False,
        )
    )
    policy = result.scalar_one_or_none()

    if not policy:
        raise NotFoundError("Policy", policy_id)

    if policy.company_id != user.company_id:
        raise AuthorizationError("Access denied to this policy")

    return PolicyResponse.model_validate(policy)


@router.post("", response_model=PolicyResponse, status_code=status.HTTP_201_CREATED)
async def create_policy(
    request: PolicyCreate,
    session: AsyncSessionDep,
    admin: AdminUserDep,
):
    """
    Create a new policy (admin only).

    Args:
        request: Policy creation data.

    Returns:
        Created policy.
    """
    policy = Policy(
        company_id=admin.company_id,
        name=request.name,
        description=request.description,
        policy_type=request.policy_type,
        trigger=request.trigger,
        is_enabled=request.is_enabled,
        priority=request.priority,
        conditions=request.conditions,
        actions=request.actions,
        min_risk_score=request.min_risk_score,
        max_risk_score=request.max_risk_score,
        min_transaction_amount=request.min_transaction_amount,
        max_transaction_amount=request.max_transaction_amount,
        cooldown_minutes=request.cooldown_minutes,
    )

    session.add(policy)
    await session.commit()
    await session.refresh(policy)

    return PolicyResponse.model_validate(policy)


@router.patch("/{policy_id}", response_model=PolicyResponse)
async def update_policy(
    policy_id: str,
    request: PolicyUpdate,
    session: AsyncSessionDep,
    admin: AdminUserDep,
):
    """
    Update a policy (admin only).

    Args:
        policy_id: Policy unique identifier.
        request: Update data.

    Returns:
        Updated policy.
    """
    result = await session.execute(
        select(Policy).where(
            Policy.id == policy_id,
            Policy.company_id == admin.company_id,
            Policy.is_deleted == False,
        )
    )
    policy = result.scalar_one_or_none()

    if not policy:
        raise NotFoundError("Policy", policy_id)

    # Apply updates
    update_data = request.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if hasattr(policy, field):
            setattr(policy, field, value)

    await session.commit()
    await session.refresh(policy)

    return PolicyResponse.model_validate(policy)


@router.delete("/{policy_id}", response_model=SuccessResponse)
async def delete_policy(
    policy_id: str,
    session: AsyncSessionDep,
    admin: AdminUserDep,
):
    """
    Delete a policy (admin only).

    Args:
        policy_id: Policy unique identifier.

    Returns:
        Success message.
    """
    result = await session.execute(
        select(Policy).where(
            Policy.id == policy_id,
            Policy.company_id == admin.company_id,
            Policy.is_deleted == False,
        )
    )
    policy = result.scalar_one_or_none()

    if not policy:
        raise NotFoundError("Policy", policy_id)

    policy.soft_delete()
    await session.commit()

    return SuccessResponse(message="Policy deleted successfully")


@router.post("/{policy_id}/enable", response_model=PolicyResponse)
async def enable_policy(
    policy_id: str,
    session: AsyncSessionDep,
    admin: AdminUserDep,
):
    """
    Enable a policy (admin only).

    Args:
        policy_id: Policy unique identifier.

    Returns:
        Updated policy.
    """
    result = await session.execute(
        select(Policy).where(
            Policy.id == policy_id,
            Policy.company_id == admin.company_id,
            Policy.is_deleted == False,
        )
    )
    policy = result.scalar_one_or_none()

    if not policy:
        raise NotFoundError("Policy", policy_id)

    policy.is_enabled = True
    await session.commit()
    await session.refresh(policy)

    return PolicyResponse.model_validate(policy)


@router.post("/{policy_id}/disable", response_model=PolicyResponse)
async def disable_policy(
    policy_id: str,
    session: AsyncSessionDep,
    admin: AdminUserDep,
):
    """
    Disable a policy (admin only).

    Args:
        policy_id: Policy unique identifier.

    Returns:
        Updated policy.
    """
    result = await session.execute(
        select(Policy).where(
            Policy.id == policy_id,
            Policy.company_id == admin.company_id,
            Policy.is_deleted == False,
        )
    )
    policy = result.scalar_one_or_none()

    if not policy:
        raise NotFoundError("Policy", policy_id)

    policy.is_enabled = False
    await session.commit()
    await session.refresh(policy)

    return PolicyResponse.model_validate(policy)


@router.post("/defaults", response_model=List[PolicyResponse])
async def create_default_policies(
    session: AsyncSessionDep,
    admin: AdminUserDep,
):
    """
    Create default policy set for company (admin only).

    Returns:
        List of created policies.
    """
    policies = Policy.create_default_policies(admin.company_id)

    for policy in policies:
        session.add(policy)

    await session.commit()

    # Refresh all
    for policy in policies:
        await session.refresh(policy)

    return [PolicyResponse.model_validate(p) for p in policies]
