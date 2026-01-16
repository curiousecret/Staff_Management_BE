from sqlmodel import SQLModel, Field
from sqlalchemy import Column, String, Index, ForeignKey
from datetime import datetime
from typing import Optional


class RefreshToken(SQLModel, table=True):
    """
    Refresh token model for storing long-lived refresh tokens.

    Refresh tokens are used to obtain new access tokens without requiring
    the user to re-authenticate. They are stored securely in the database
    and can be revoked individually.
    """

    __tablename__ = "refresh_tokens"

    # Primary key - auto increment integer
    id: Optional[int] = Field(default=None, primary_key=True)

    # The refresh token (should be unique and securely generated)
    token: str = Field(
        sa_column=Column(String(500), unique=True, nullable=False, index=True)
    )

    # User who owns this refresh token
    user_id: int = Field(
        sa_column=Column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    )

    # Whether the token has been revoked (e.g., on logout)
    is_revoked: bool = Field(default=False, nullable=False)

    # When the token was created
    created_at: datetime = Field(
        default_factory=lambda: datetime.utcnow(),
        nullable=False,
    )

    # Token expiration time
    expires_at: datetime = Field(nullable=False)

    # When the token was last used (optional, for tracking)
    last_used_at: Optional[datetime] = Field(default=None)

    __table_args__ = (
        Index('ix_refresh_tokens_user_id_expires_at', 'user_id', 'expires_at'),
        Index('ix_refresh_tokens_expires_at', 'expires_at'),
    )
