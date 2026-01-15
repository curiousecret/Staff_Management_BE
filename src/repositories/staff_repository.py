from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from sqlalchemy.exc import IntegrityError
from typing import Optional, Tuple, List
from decimal import Decimal

from src.models.staff_model import Staff, StaffStatus
from src.schemas.staff_schema import StaffCreate, StaffUpdate, StaffFilterParams
from src.core.exceptions import NotFoundException, DuplicateException, DatabaseException


class StaffRepository:
    """
    Repository for Staff database operations.
    
    Handles all database interactions for Staff entity.
    Uses async operations for optimal performance.
    """
    
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
    
    async def create(self, staff_data: StaffCreate) -> Staff:
        """
        Create a new staff record.
        
        Args:
            staff_data: Validated staff creation data
            
        Returns:
            Created Staff object
            
        Raises:
            DuplicateException: If staff_id already exists
            DatabaseException: If database operation fails
        """
        try:
            staff = Staff(
                staff_id=staff_data.staff_id,
                name=staff_data.name,
                dob=staff_data.dob,
                salary=staff_data.salary,
                status=staff_data.status,
            )
            
            self.session.add(staff)
            await self.session.flush()
            await self.session.refresh(staff)
            
            return staff
            
        except IntegrityError as e:
            await self.session.rollback()
            if "unique" in str(e).lower() or "duplicate" in str(e).lower():
                raise DuplicateException("Staff", "staff_id", staff_data.staff_id)
            raise DatabaseException(f"Failed to create staff: {str(e)}")
    
    async def get_by_staff_id(self, staff_id: str) -> Optional[Staff]:
        """
        Get staff by staff_id.
        
        Args:
            staff_id: The business identifier
            
        Returns:
            Staff object if found, None otherwise
        """
        query = select(Staff).where(Staff.staff_id == staff_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def get_by_id(self, id: int) -> Optional[Staff]:
        """
        Get staff by internal ID.
        
        Args:
            id: The internal primary key
            
        Returns:
            Staff object if found, None otherwise
        """
        query = select(Staff).where(Staff.id == id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def get_list(
        self,
        filters: StaffFilterParams,
    ) -> Tuple[List[Staff], int]:
        """
        Get paginated list of staff with filters.
        
        Args:
            filters: Filter and pagination parameters
            
        Returns:
            Tuple of (list of Staff, total count)
        """
        # Build base query
        query = select(Staff)
        count_query = select(func.count(Staff.id))
        
        # Apply filters
        conditions = []
        
        if filters.status is not None:
            conditions.append(Staff.status == filters.status)
        
        if filters.name is not None:
            # Case-insensitive partial match
            conditions.append(Staff.name.ilike(f"%{filters.name}%"))
        
        if filters.salary_min is not None:
            conditions.append(Staff.salary >= filters.salary_min)
        
        if filters.salary_max is not None:
            conditions.append(Staff.salary <= filters.salary_max)
        
        # Apply conditions to both queries
        if conditions:
            query = query.where(and_(*conditions))
            count_query = count_query.where(and_(*conditions))
        
        # Get total count
        total_result = await self.session.execute(count_query)
        total = total_result.scalar_one()
        
        # Apply sorting
        sort_column = getattr(Staff, filters.sort_by)
        if filters.sort_order == "desc":
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())
        
        # Apply pagination
        offset = (filters.page - 1) * filters.limit
        query = query.offset(offset).limit(filters.limit)
        
        # Execute query
        result = await self.session.execute(query)
        items = list(result.scalars().all())
        
        return items, total
    
    async def update(
        self,
        staff_id: str,
        update_data: StaffUpdate,
    ) -> Staff:
        """
        Update an existing staff record.
        
        Args:
            staff_id: The business identifier of staff to update
            update_data: Validated update data
            
        Returns:
            Updated Staff object
            
        Raises:
            NotFoundException: If staff not found
            DuplicateException: If new staff_id already exists
        """
        # Get existing staff
        staff = await self.get_by_staff_id(staff_id)
        if staff is None:
            raise NotFoundException("Staff", staff_id)
        
        # Check for duplicate staff_id if being changed
        if update_data.staff_id is not None and update_data.staff_id != staff_id:
            existing = await self.get_by_staff_id(update_data.staff_id)
            if existing is not None:
                raise DuplicateException("Staff", "staff_id", update_data.staff_id)
        
        # Update fields
        update_dict = update_data.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(staff, field, value)
        
        try:
            await self.session.flush()
            await self.session.refresh(staff)
            return staff
            
        except IntegrityError as e:
            await self.session.rollback()
            raise DatabaseException(f"Failed to update staff: {str(e)}")
    
    async def delete(self, staff_id: str) -> bool:
        """
        Permanently delete a staff record.
        
        Args:
            staff_id: The business identifier of staff to delete
            
        Returns:
            True if deleted successfully
            
        Raises:
            NotFoundException: If staff not found
        """
        staff = await self.get_by_staff_id(staff_id)
        if staff is None:
            raise NotFoundException("Staff", staff_id)
        
        await self.session.delete(staff)
        await self.session.flush()
        
        return True
    
    async def exists_by_staff_id(self, staff_id: str) -> bool:
        """
        Check if staff exists by staff_id.
        
        Args:
            staff_id: The business identifier
            
        Returns:
            True if exists, False otherwise
        """
        query = select(func.count(Staff.id)).where(Staff.staff_id == staff_id)
        result = await self.session.execute(query)
        count = result.scalar_one()
        return count > 0