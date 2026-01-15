from sqlmodel import SQLModel, Field
from sqlalchemy import Column, String, Index
from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from enum import Enum


class StaffStatus(str, Enum):
    """Enum for staff status values."""
    ACTIVE = "active"
    INACTIVE = "inactive"


class Staff(SQLModel, table=True):
    """
    Staff database model.
    
    Uses integer PK for optimal indexing performance.
    staff_id is the business identifier (editable, unique).
    """
    
    __tablename__ = "staff"
    
    # Primary key - auto increment integer for fast indexing
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Business identifier - unique, indexed for fast lookups
    staff_id: str = Field(
        sa_column=Column(String(20), unique=True, nullable=False, index=True)
    )
    
    # Staff details
    name: str = Field(
        sa_column=Column(String(100), nullable=False, index=True)
    )
    
    dob: date = Field(nullable=False)
    
    # Salary with 2 decimal precision (max 12 digits total)
    salary: Decimal = Field(
        default=Decimal("0.00"),
        max_digits=12,
        decimal_places=2,
    )
    
    status: StaffStatus = Field(
        default=StaffStatus.ACTIVE,
        sa_column=Column(String(10), nullable=False, index=True)
    )
    
    # Audit fields
    created_at: datetime = Field(
        default_factory=lambda: datetime.utcnow(),
        nullable=False,
    )
    
    updated_at: datetime = Field(
        default_factory=lambda: datetime.utcnow(),
        nullable=False,
        sa_column_kwargs={"onupdate": datetime.utcnow},
    )
    
    # Composite index for common query patterns
    __table_args__ = (
        Index("ix_staff_status_created", "status", "created_at"),
    )