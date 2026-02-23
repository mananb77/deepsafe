"""
Users Router

Endpoints for user management.
"""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Query, status
from sqlalchemy import select, func, or_
from sqlalchemy.orm import selectinload

from src.shared.models.user import User, UserRole
from src.shared.models.audit_log import AuditLog, AuditAction
from src.shared.schemas.user import (
    UserCreate,
    UserUpdate,
    UserResponse,
    UserListResponse,
    BlacklistRequest,
)
from src.shared.schemas.base import SuccessResponse
from src.shared.security.password import hash_password
from src.services.api.dependencies import (
    AsyncSessionDep,
    CurrentUserDep,
    AdminUserDep,
    PaginationDep,
    RequestMetadataDep,
)
from src.services.api.exceptions import NotFoundError, ConflictError, AuthorizationError

router = APIRouter()


@router.get("", response_model=UserListResponse)
async def list_users(
    session: AsyncSessionDep,
    user: CurrentUserDep,
    pagination: PaginationDep,
    role: Optional[UserRole] = Query(default=None, description="Filter by role"),
    is_active: Optional[bool] = Query(default=None, description="Filter by active status"),
    search: Optional[str] = Query(default=None, description="Search by name or email"),
):
    """
    List users in the current user's company.

    Args:
        role: Optional role filter.
        is_active: Optional active status filter.
        search: Optional search query.

    Returns:
        Paginated list of users.
    """
    # Base query - only users from same company
    query = select(User).where(
        User.company_id == user.company_id,
        User.is_deleted == False,
    )

    # Apply filters
    if role:
        query = query.where(User.role == role)

    if is_active is not None:
        query = query.where(User.is_active == is_active)

    if search:
        search_filter = or_(
            User.full_name.ilike(f"%{search}%"),
            User.email.ilike(f"%{search}%"),
        )
        query = query.where(search_filter)

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total = await session.scalar(count_query)

    # Apply pagination
    query = query.offset(pagination.offset).limit(pagination.limit)
    query = query.order_by(User.created_at.desc())

    result = await session.execute(query)
    users = result.scalars().all()

    return UserListResponse(
        items=[UserResponse.model_validate(u) for u in users],
        total=total,
        page=pagination.page,
        page_size=pagination.page_size,
        pages=(total + pagination.page_size - 1) // pagination.page_size,
    )


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    session: AsyncSessionDep,
    current_user: CurrentUserDep,
):
    """
    Get a specific user by ID.

    Args:
        user_id: The user's unique identifier.

    Returns:
        User details.

    Raises:
        NotFoundError: If user not found.
        AuthorizationError: If user is from different company.
    """
    result = await session.execute(
        select(User).where(User.id == user_id, User.is_deleted == False)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise NotFoundError("User", user_id)

    # Check company access
    if user.company_id != current_user.company_id:
        raise AuthorizationError("Access denied to this user")

    return UserResponse.model_validate(user)


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    request: UserCreate,
    session: AsyncSessionDep,
    admin: AdminUserDep,
    metadata: RequestMetadataDep,
):
    """
    Create a new user (admin only).

    Args:
        request: User creation data.

    Returns:
        Created user.

    Raises:
        ConflictError: If email already exists.
    """
    # Check email uniqueness
    existing = await session.execute(
        select(User).where(User.email == request.email.lower())
    )
    if existing.scalar_one_or_none():
        raise ConflictError(f"Email {request.email} is already registered")

    # Create user
    user = User(
        email=request.email.lower(),
        full_name=request.full_name,
        phone_number=request.phone_number,
        company_id=admin.company_id,  # Same company as admin
        role=request.role,
        hashed_password=hash_password(request.password) if request.password else None,
        is_active=True,
    )

    session.add(user)

    # Audit log
    audit_log = AuditLog.log_action(
        action=AuditAction.USER_CREATED,
        description=f"User {user.email} created",
        user_id=admin.id,
        company_id=admin.company_id,
        target_type="user",
        target_id=user.id,
        ip_address=metadata.get("ip_address"),
        new_values={"email": user.email, "role": user.role.value},
    )
    session.add(audit_log)

    await session.commit()
    await session.refresh(user)

    return UserResponse.model_validate(user)


@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    request: UserUpdate,
    session: AsyncSessionDep,
    current_user: CurrentUserDep,
    metadata: RequestMetadataDep,
):
    """
    Update a user.

    Regular users can only update their own profile.
    Admins can update any user in their company.

    Args:
        user_id: The user's unique identifier.
        request: Update data.

    Returns:
        Updated user.
    """
    result = await session.execute(
        select(User).where(User.id == user_id, User.is_deleted == False)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise NotFoundError("User", user_id)

    # Authorization check
    is_self = user_id == current_user.id
    is_admin = current_user.role == UserRole.ADMIN
    same_company = user.company_id == current_user.company_id

    if not (is_self or (is_admin and same_company)):
        raise AuthorizationError("Cannot update this user")

    # Non-admins can't change roles
    if request.role and not is_admin:
        raise AuthorizationError("Only admins can change user roles")

    # Track changes for audit
    old_values = {}
    new_values = {}

    # Apply updates
    update_data = request.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if hasattr(user, field):
            old_value = getattr(user, field)
            if old_value != value:
                old_values[field] = old_value.value if hasattr(old_value, 'value') else old_value
                new_values[field] = value.value if hasattr(value, 'value') else value
                setattr(user, field, value)

    if new_values:
        # Audit log
        audit_log = AuditLog.log_action(
            action=AuditAction.USER_UPDATED,
            description=f"User {user.email} updated",
            user_id=current_user.id,
            company_id=current_user.company_id,
            target_type="user",
            target_id=user.id,
            ip_address=metadata.get("ip_address"),
            old_values=old_values,
            new_values=new_values,
        )
        session.add(audit_log)

    await session.commit()
    await session.refresh(user)

    return UserResponse.model_validate(user)


@router.delete("/{user_id}", response_model=SuccessResponse)
async def delete_user(
    user_id: str,
    session: AsyncSessionDep,
    admin: AdminUserDep,
    metadata: RequestMetadataDep,
):
    """
    Soft delete a user (admin only).

    Args:
        user_id: The user's unique identifier.

    Returns:
        Success message.
    """
    result = await session.execute(
        select(User).where(
            User.id == user_id,
            User.company_id == admin.company_id,
            User.is_deleted == False,
        )
    )
    user = result.scalar_one_or_none()

    if not user:
        raise NotFoundError("User", user_id)

    # Can't delete yourself
    if user_id == admin.id:
        raise ConflictError("Cannot delete your own account")

    # Soft delete
    user.soft_delete()

    # Audit log
    audit_log = AuditLog.log_action(
        action=AuditAction.USER_DELETED,
        description=f"User {user.email} deleted",
        user_id=admin.id,
        company_id=admin.company_id,
        target_type="user",
        target_id=user.id,
        ip_address=metadata.get("ip_address"),
    )
    session.add(audit_log)

    await session.commit()

    return SuccessResponse(message="User deleted successfully")


@router.post("/{user_id}/blacklist", response_model=UserResponse)
async def blacklist_user(
    user_id: str,
    request: BlacklistRequest,
    session: AsyncSessionDep,
    admin: AdminUserDep,
    metadata: RequestMetadataDep,
):
    """
    Add a user to the blacklist (admin only).

    Args:
        user_id: The user's unique identifier.
        request: Blacklist reason.

    Returns:
        Updated user.
    """
    result = await session.execute(
        select(User).where(
            User.id == user_id,
            User.company_id == admin.company_id,
            User.is_deleted == False,
        )
    )
    user = result.scalar_one_or_none()

    if not user:
        raise NotFoundError("User", user_id)

    user.blacklist(request.reason)

    # Audit log
    audit_log = AuditLog.log_action(
        action=AuditAction.USER_BLACKLISTED,
        description=f"User {user.email} blacklisted: {request.reason}",
        user_id=admin.id,
        company_id=admin.company_id,
        target_type="user",
        target_id=user.id,
        ip_address=metadata.get("ip_address"),
        new_values={"reason": request.reason},
    )
    session.add(audit_log)

    await session.commit()
    await session.refresh(user)

    return UserResponse.model_validate(user)


@router.post("/{user_id}/whitelist", response_model=UserResponse)
async def whitelist_user(
    user_id: str,
    session: AsyncSessionDep,
    admin: AdminUserDep,
    metadata: RequestMetadataDep,
):
    """
    Add a user to the whitelist (admin only).

    Args:
        user_id: The user's unique identifier.

    Returns:
        Updated user.
    """
    result = await session.execute(
        select(User).where(
            User.id == user_id,
            User.company_id == admin.company_id,
            User.is_deleted == False,
        )
    )
    user = result.scalar_one_or_none()

    if not user:
        raise NotFoundError("User", user_id)

    user.whitelist()

    # Audit log
    audit_log = AuditLog.log_action(
        action=AuditAction.USER_WHITELISTED,
        description=f"User {user.email} whitelisted",
        user_id=admin.id,
        company_id=admin.company_id,
        target_type="user",
        target_id=user.id,
        ip_address=metadata.get("ip_address"),
    )
    session.add(audit_log)

    await session.commit()
    await session.refresh(user)

    return UserResponse.model_validate(user)
