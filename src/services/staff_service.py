from sqlalchemy.ext.asyncio import AsyncSession
from typing import Tuple, List
import math

from src.models.staff_model import Staff
from src.schemas.staff_schema import (
    StaffCreate,
    StaffUpdate,
    StaffResponse,
    StaffListResponse,
    StaffFilterParams,
)
from src.repositories.staff_repository import StaffRepository
from src.core.exceptions import NotFoundException


class StaffService:
    """
    Service layer for Staff business logic.
    
    Handles business rules and orchestrates repository operations.
    """
    
    def __init__(self, session: AsyncSession) -> None:
        self.repository = StaffRepository(session)
    
    async def create_staff(self, staff_data: StaffCreate) -> StaffResponse:
        """
        Create a new staff member.
        
        Args:
            staff_data: Validated staff creation data
            
        Returns:
            Created staff as response schema
        """
        staff = await self.repository.create(staff_data)
        return StaffResponse.model_validate(staff)
    
    async def get_staff(self, staff_id: str) -> StaffResponse:
        """
        Get a staff member by staff_id.
        
        Args:
            staff_id: The business identifier
            
        Returns:
            Staff as response schema
            
        Raises:
            NotFoundException: If staff not found
        """
        staff = await self.repository.get_by_staff_id(staff_id)
        if staff is None:
            raise NotFoundException("Staff", staff_id)
        return StaffResponse.model_validate(staff)
    
    async def get_staff_list(
        self,
        filters: StaffFilterParams,
    ) -> StaffListResponse:
        """
        Get paginated list of staff with filters.
        
        Args:
            filters: Filter and pagination parameters
            
        Returns:
            Paginated staff list response
        """
        items, total = await self.repository.get_list(filters)
        
        # Calculate total pages
        total_pages = math.ceil(total / filters.limit) if total > 0 else 1
        
        return StaffListResponse(
            items=[StaffResponse.model_validate(item) for item in items],
            total=total,
            page=filters.page,
            limit=filters.limit,
            total_pages=total_pages,
        )
    
    async def update_staff(
        self,
        staff_id: str,
        update_data: StaffUpdate,
    ) -> StaffResponse:
        """
        Update an existing staff member.
        
        Args:
            staff_id: The business identifier of staff to update
            update_data: Validated update data
            
        Returns:
            Updated staff as response schema
        """
        staff = await self.repository.update(staff_id, update_data)
        return StaffResponse.model_validate(staff)
    
    async def delete_staff(self, staff_id: str) -> bool:
        """
        Delete a staff member permanently.
        
        Args:
            staff_id: The business identifier of staff to delete
            
        Returns:
            True if deleted successfully
        """
        return await self.repository.delete(staff_id)