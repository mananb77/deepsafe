"""
Base Pydantic Schemas

Common schema definitions and utilities.
"""

from datetime import datetime
from typing import Any, Generic, List, Optional, TypeVar

from pydantic import BaseModel, ConfigDict, Field


class BaseSchema(BaseModel):
    """Base schema with common configuration."""

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        use_enum_values=True,
        json_encoders={
            datetime: lambda v: v.isoformat() if v else None,
        },
    )


class TimestampSchema(BaseSchema):
    """Schema with timestamp fields."""

    created_at: datetime
    updated_at: datetime


T = TypeVar("T")


class PaginatedResponse(BaseSchema, Generic[T]):
    """Generic paginated response wrapper."""

    items: List[T]
    total: int = Field(description="Total number of items")
    page: int = Field(ge=1, description="Current page number")
    page_size: int = Field(ge=1, le=100, description="Items per page")
    pages: int = Field(description="Total number of pages")

    @property
    def has_next(self) -> bool:
        """Check if there's a next page."""
        return self.page < self.pages

    @property
    def has_prev(self) -> bool:
        """Check if there's a previous page."""
        return self.page > 1


class ErrorResponse(BaseSchema):
    """Standard error response."""

    error: str = Field(description="Error type/code")
    message: str = Field(description="Human-readable error message")
    details: Optional[dict] = Field(default=None, description="Additional error details")


class SuccessResponse(BaseSchema):
    """Standard success response."""

    success: bool = True
    message: str = Field(description="Success message")
    data: Optional[Any] = Field(default=None, description="Response data")


class HealthResponse(BaseSchema):
    """Health check response."""

    status: str = Field(description="Service status")
    version: str = Field(description="Application version")
    environment: str = Field(description="Environment name")
    database: str = Field(description="Database connection status")
    redis: str = Field(description="Redis connection status")
    mongodb: str = Field(description="MongoDB connection status")


class PaginationParams(BaseSchema):
    """Pagination parameters."""

    page: int = Field(default=1, ge=1, description="Page number")
    page_size: int = Field(default=20, ge=1, le=100, description="Items per page")

    @property
    def offset(self) -> int:
        """Calculate offset for database query."""
        return (self.page - 1) * self.page_size

    @property
    def limit(self) -> int:
        """Get limit for database query."""
        return self.page_size
