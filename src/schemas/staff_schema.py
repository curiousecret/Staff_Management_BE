from pydantic import BaseModel, Field, field_validator, ConfigDict
from datetime import date, datetime
from decimal import Decimal, ROUND_HALF_UP
from typing import Optional, List
import re

from src.models.staff_model import StaffStatus


# =============================================================================
# Request Schemas
# =============================================================================

class StaffCreate(BaseModel):
    """Schema for creating a new staff member."""
    
    staff_id: str = Field(
        ...,
        min_length=1,
        max_length=20,
        description="Unique staff identifier",
        examples=["STF001"],
    )
    
    name: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Staff full name (letters and spaces only)",
        examples=["John Doe"],
    )
    
    dob: date = Field(
        ...,
        description="Date of birth (must be 18+ years old)",
        examples=["1990-01-15"],
    )
    
    salary: Decimal = Field(
        ...,
        ge=Decimal("0"),
        description="Salary amount (2 decimal places)",
        examples=[5000.00],
    )
    
    status: StaffStatus = Field(
        default=StaffStatus.ACTIVE,
        description="Staff status",
        examples=["active"],
    )
    
    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate name contains only letters and spaces."""
        v = v.strip()
        if not re.match(r"^[a-zA-Z\s]+$", v):
            raise ValueError("Name must contain only letters and spaces")
        # Normalize multiple spaces to single space
        v = re.sub(r"\s+", " ", v)
        return v
    
    @field_validator("staff_id")
    @classmethod
    def validate_staff_id(cls, v: str) -> str:
        """Validate and normalize staff_id."""
        return v.strip()
    
    @field_validator("dob")
    @classmethod
    def validate_dob(cls, v: date) -> date:
        """Validate staff is at least 18 years old."""
        today = date.today()
        age = today.year - v.year - ((today.month, today.day) < (v.month, v.day))
        if age < 18:
            raise ValueError("Staff must be at least 18 years old")
        return v
    
    @field_validator("salary")
    @classmethod
    def validate_salary(cls, v: Decimal) -> Decimal:
        """Round salary to 2 decimal places."""
        return v.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


class StaffUpdate(BaseModel):
    """Schema for updating an existing staff member."""
    
    staff_id: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=20,
        description="Unique staff identifier",
    )
    
    name: Optional[str] = Field(
        default=None,
        min_length=2,
        max_length=100,
        description="Staff full name",
    )
    
    dob: Optional[date] = Field(
        default=None,
        description="Date of birth",
    )
    
    salary: Optional[Decimal] = Field(
        default=None,
        ge=Decimal("0"),
        description="Salary amount",
    )
    
    status: Optional[StaffStatus] = Field(
        default=None,
        description="Staff status",
    )
    
    @field_validator("name")
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        """Validate name contains only letters and spaces."""
        if v is None:
            return v
        v = v.strip()
        if not re.match(r"^[a-zA-Z\s]+$", v):
            raise ValueError("Name must contain only letters and spaces")
        v = re.sub(r"\s+", " ", v)
        return v
    
    @field_validator("staff_id")
    @classmethod
    def validate_staff_id(cls, v: Optional[str]) -> Optional[str]:
        """Validate and normalize staff_id."""
        if v is None:
            return v
        return v.strip()
    
    @field_validator("dob")
    @classmethod
    def validate_dob(cls, v: Optional[date]) -> Optional[date]:
        """Validate staff is at least 18 years old."""
        if v is None:
            return v
        today = date.today()
        age = today.year - v.year - ((today.month, today.day) < (v.month, v.day))
        if age < 18:
            raise ValueError("Staff must be at least 18 years old")
        return v
    
    @field_validator("salary")
    @classmethod
    def validate_salary(cls, v: Optional[Decimal]) -> Optional[Decimal]:
        """Round salary to 2 decimal places."""
        if v is None:
            return v
        return v.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


# =============================================================================
# Response Schemas
# =============================================================================

class StaffResponse(BaseModel):
    """Schema for staff response."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    staff_id: str
    name: str
    dob: date
    salary: Decimal
    status: StaffStatus
    created_at: datetime
    updated_at: datetime
    
    @field_validator("salary")
    @classmethod
    def format_salary(cls, v: Decimal) -> Decimal:
        """Ensure salary is displayed with 2 decimal places."""
        return v.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


class StaffListResponse(BaseModel):
    """Schema for paginated staff list response."""
    
    items: List[StaffResponse]
    total: int
    page: int
    limit: int
    total_pages: int


# =============================================================================
# Query Parameter Schemas
# =============================================================================

class StaffFilterParams(BaseModel):
    """Schema for staff list filter parameters."""
    
    page: int = Field(default=1, ge=1, description="Page number")
    limit: int = Field(default=10, ge=1, le=100, description="Items per page")
    status: Optional[StaffStatus] = Field(default=None, description="Filter by status")
    name: Optional[str] = Field(default=None, description="Search by name")
    salary_min: Optional[Decimal] = Field(default=None, ge=Decimal("0"), description="Minimum salary")
    salary_max: Optional[Decimal] = Field(default=None, ge=Decimal("0"), description="Maximum salary")
    sort_by: str = Field(default="created_at", description="Sort field")
    sort_order: str = Field(default="desc", pattern="^(asc|desc)$", description="Sort order")
    
    @field_validator("sort_by")
    @classmethod
    def validate_sort_by(cls, v: str) -> str:
        """Validate sort_by is an allowed field."""
        allowed_fields = {"staff_id", "name", "salary", "created_at", "status"}
        if v not in allowed_fields:
            raise ValueError(f"sort_by must be one of: {', '.join(allowed_fields)}")
        return v