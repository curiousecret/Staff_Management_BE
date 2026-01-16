from sqlmodel import SQLModel, Field
from sqlalchemy import Column, String, Index
from datetime import datetime
from typing import Optional


class TokenBlacklist(SQLModel, table=True):
    """
    Token blacklist model for storing invalidated JWT tokens.

    Tokens are added to this table when users logout.
    Expired tokens can be cleaned up periodically.
    """

    __tablename__ = "token_blacklist"

    # Primary key - auto increment integer
    id: Optional[int] = Field(default=None, primary_key=True)

    # The JWT token (hashed for security and storage efficiency)
    token: str = Field(
        sa_column=Column(String(500), unique=True, nullable=False, index=True)
    )

    # When the token was blacklisted
    blacklisted_at: datetime = Field(
        default_factory=lambda: datetime.utcnow(),
        nullable=False,
    )

    # Token expiration time (for cleanup purposes)
    expires_at: datetime = Field(nullable=False)

    __table_args__ = (
        Index('ix_token_blacklist_expires_at', 'expires_at'),
    )
