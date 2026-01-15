from sqlmodel import SQLModel, Field
from sqlalchemy import Column, String
from datetime import datetime
from typing import Optional


class User(SQLModel, table=True):
    """
    User database model for authentication.

    Uses integer PK for optimal indexing performance.
    username is the business identifier (unique, indexed).
    """

    __tablename__ = "users"

    # Primary key - auto increment integer for fast indexing
    id: Optional[int] = Field(default=None, primary_key=True)

    # Business identifier - unique, indexed for fast lookups
    username: str = Field(
        sa_column=Column(String(50), unique=True, nullable=False, index=True)
    )

    # Hashed password - never store plain text passwords
    hashed_password: str = Field(
        sa_column=Column(String(255), nullable=False)
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
