from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, update
from datetime import datetime
from typing import Optional

from src.models.refresh_token_model import RefreshToken
from src.core.exceptions import DatabaseException


class RefreshTokenRepository:
    """
    Repository for RefreshToken database operations.

    Handles creating, validating, and revoking refresh tokens.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, token: str, user_id: int, expires_at: datetime) -> RefreshToken:
        """
        Create a new refresh token.

        Args:
            token: The refresh token string
            user_id: The ID of the user this token belongs to
            expires_at: When the token expires

        Returns:
            Created RefreshToken object

        Raises:
            DatabaseException: If database operation fails
        """
        try:
            refresh_token = RefreshToken(
                token=token,
                user_id=user_id,
                expires_at=expires_at,
            )

            self.session.add(refresh_token)
            await self.session.flush()
            await self.session.refresh(refresh_token)

            return refresh_token

        except Exception as e:
            await self.session.rollback()
            raise DatabaseException(f"Failed to create refresh token: {str(e)}")

    async def get_by_token(self, token: str) -> Optional[RefreshToken]:
        """
        Get a refresh token by its token string.

        Args:
            token: The refresh token string to look up

        Returns:
            RefreshToken object if found, None otherwise
        """
        query = select(RefreshToken).where(RefreshToken.token == token)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def is_valid(self, token: str) -> bool:
        """
        Check if a refresh token is valid (exists, not revoked, not expired).

        Args:
            token: The refresh token string to validate

        Returns:
            True if token is valid, False otherwise
        """
        query = select(RefreshToken).where(
            RefreshToken.token == token,
            RefreshToken.is_revoked == False,
            RefreshToken.expires_at > datetime.utcnow()
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none() is not None

    async def revoke_token(self, token: str) -> bool:
        """
        Revoke a refresh token.

        Args:
            token: The refresh token string to revoke

        Returns:
            True if token was revoked, False if not found

        Raises:
            DatabaseException: If database operation fails
        """
        try:
            query = (
                update(RefreshToken)
                .where(RefreshToken.token == token)
                .values(is_revoked=True)
            )
            result = await self.session.execute(query)
            await self.session.flush()

            return result.rowcount > 0

        except Exception as e:
            await self.session.rollback()
            raise DatabaseException(f"Failed to revoke refresh token: {str(e)}")

    async def revoke_all_user_tokens(self, user_id: int) -> int:
        """
        Revoke all refresh tokens for a specific user.

        Useful for logout from all devices or account security actions.

        Args:
            user_id: The ID of the user whose tokens should be revoked

        Returns:
            Number of tokens revoked

        Raises:
            DatabaseException: If database operation fails
        """
        try:
            query = (
                update(RefreshToken)
                .where(
                    RefreshToken.user_id == user_id,
                    RefreshToken.is_revoked == False
                )
                .values(is_revoked=True)
            )
            result = await self.session.execute(query)
            await self.session.flush()

            return result.rowcount

        except Exception as e:
            await self.session.rollback()
            raise DatabaseException(f"Failed to revoke user tokens: {str(e)}")

    async def update_last_used(self, token: str) -> bool:
        """
        Update the last_used_at timestamp for a token.

        Args:
            token: The refresh token string

        Returns:
            True if updated, False if not found

        Raises:
            DatabaseException: If database operation fails
        """
        try:
            query = (
                update(RefreshToken)
                .where(RefreshToken.token == token)
                .values(last_used_at=datetime.utcnow())
            )
            result = await self.session.execute(query)
            await self.session.flush()

            return result.rowcount > 0

        except Exception as e:
            await self.session.rollback()
            raise DatabaseException(f"Failed to update token last used: {str(e)}")

    async def cleanup_expired_tokens(self) -> int:
        """
        Remove expired or revoked tokens from the database.

        Returns:
            Number of tokens removed

        Raises:
            DatabaseException: If database operation fails
        """
        try:
            query = delete(RefreshToken).where(
                (RefreshToken.expires_at < datetime.utcnow()) |
                (RefreshToken.is_revoked == True)
            )
            result = await self.session.execute(query)
            await self.session.flush()

            return result.rowcount

        except Exception as e:
            await self.session.rollback()
            raise DatabaseException(f"Failed to cleanup expired tokens: {str(e)}")
