from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from decimal import Decimal

from src.core.database import get_async_session
from src.models.staff_model import StaffStatus
from src.schemas.staff_schema import (
    StaffCreate,
    StaffUpdate,
    StaffResponse,
    StaffListResponse,
    StaffFilterParams,
)
from src.services.staff_service import StaffService
from src.core.auth import get_current_user
from src.models.user_model import User

router = APIRouter(prefix="/staff", tags=["Staff"])


# =============================================================================
# Dependency Injection
# =============================================================================

async def get_staff_service(
    session: AsyncSession = Depends(get_async_session),
) -> StaffService:
    """Dependency to get StaffService instance."""
    return StaffService(session)


# =============================================================================
# API Endpoints
# =============================================================================

@router.post(
    "",
    response_model=StaffResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new staff member",
    description="Create a new staff member with the provided information.",
)
async def create_staff(
    staff_data: StaffCreate,
    service: StaffService = Depends(get_staff_service),
    current_user: User = Depends(get_current_user),
) -> StaffResponse:
    """
    Create a new staff member.
    
    - **staff_id**: Unique business identifier (required)
    - **name**: Full name, letters and spaces only (required)
    - **dob**: Date of birth, must be 18+ (required)
    - **salary**: Salary amount, 2 decimal places (required)
    - **status**: active or inactive (default: active)
    """
    return await service.create_staff(staff_data)


@router.get(
    "",
    response_model=StaffListResponse,
    summary="Get list of staff members",
    description="Get a paginated list of staff members with optional filters and sorting.",
)
async def get_staff_list(
    page: int = Query(default=1, ge=1, description="Page number"),
    limit: int = Query(default=10, ge=1, le=100, description="Items per page"),
    status: Optional[StaffStatus] = Query(default=None, description="Filter by status"),
    name: Optional[str] = Query(default=None, description="Search by name (partial match)"),
    salary_min: Optional[Decimal] = Query(default=None, ge=Decimal("0"), description="Minimum salary"),
    salary_max: Optional[Decimal] = Query(default=None, ge=Decimal("0"), description="Maximum salary"),
    sort_by: str = Query(
        default="created_at",
        description="Sort by field (staff_id, name, salary, created_at, status)",
    ),
    sort_order: str = Query(
        default="desc",
        pattern="^(asc|desc)$",
        description="Sort order (asc or desc)",
    ),
    service: StaffService = Depends(get_staff_service),
    current_user: User = Depends(get_current_user),
) -> StaffListResponse:
    """
    Get a paginated list of staff members.
    
    Supports filtering by:
    - **status**: Filter by active/inactive
    - **name**: Search by name (case-insensitive partial match)
    - **salary_min/salary_max**: Filter by salary range
    
    Supports sorting by:
    - staff_id, name, salary, created_at, status
    """
    filters = StaffFilterParams(
        page=page,
        limit=limit,
        status=status,
        name=name,
        salary_min=salary_min,
        salary_max=salary_max,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    return await service.get_staff_list(filters)


@router.get(
    "/{staff_id}",
    response_model=StaffResponse,
    summary="Get a staff member by staff_id",
    description="Get detailed information about a specific staff member.",
)
async def get_staff(
    staff_id: str,
    service: StaffService = Depends(get_staff_service),
    current_user: User = Depends(get_current_user),
) -> StaffResponse:
    """
    Get a staff member by their staff_id.
    
    - **staff_id**: The unique business identifier of the staff member
    """
    return await service.get_staff(staff_id)


@router.put(
    "/{staff_id}",
    response_model=StaffResponse,
    summary="Update a staff member",
    description="Update an existing staff member's information.",
)
async def update_staff(
    staff_id: str,
    update_data: StaffUpdate,
    service: StaffService = Depends(get_staff_service),
    current_user: User = Depends(get_current_user),
) -> StaffResponse:
    """
    Update an existing staff member.
    
    Only provided fields will be updated.
    
    - **staff_id**: Can be changed (must be unique)
    - **name**: Letters and spaces only
    - **dob**: Must be 18+
    - **salary**: 2 decimal places
    - **status**: active or inactive
    """
    return await service.update_staff(staff_id, update_data)


@router.delete(
    "/{staff_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a staff member",
    description="Permanently delete a staff member.",
)
async def delete_staff(
    staff_id: str,
    service: StaffService = Depends(get_staff_service),
    current_user: User = Depends(get_current_user),
) -> None:
    """
    Permanently delete a staff member.
    
    - **staff_id**: The unique business identifier of the staff member to delete
    
    This action cannot be undone.
    """
    await service.delete_staff(staff_id)