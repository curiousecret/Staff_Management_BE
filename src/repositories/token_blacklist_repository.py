from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from datetime import datetime
from typing import Optional

from src.models.token_blacklist_model import TokenBlacklist
from src.core.exceptions import DatabaseException


class TokenBlacklistRepository:
    """
    Repository for TokenBlacklist database operations.

    Handles blacklisting tokens and checking if tokens are blacklisted.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add_token(self, token: str, expires_at: datetime) -> TokenBlacklist:
        """
        Add a token to the blacklist.

        Args:
            token: The JWT token to blacklist
            expires_at: When the token expires

        Returns:
            Created TokenBlacklist object

        Raises:
            DatabaseException: If database operation fails
        """
        try:
            blacklisted_token = TokenBlacklist(
                token=token,
                expires_at=expires_at,
            )

            self.session.add(blacklisted_token)
            await self.session.flush()
            await self.session.refresh(blacklisted_token)

            return blacklisted_token

        except Exception as e:
            await self.session.rollback()
            raise DatabaseException(f"Failed to blacklist token: {str(e)}")

    async def is_blacklisted(self, token: str) -> bool:
        """
        Check if a token is blacklisted.

        Args:
            token: The JWT token to check

        Returns:
            True if token is blacklisted, False otherwise
        """
        query = select(TokenBlacklist).where(TokenBlacklist.token == token)
        result = await self.session.execute(query)
        return result.scalar_one_or_none() is not None

    async def cleanup_expired_tokens(self) -> int:
        """
        Remove expired tokens from the blacklist.

        Tokens that have passed their expiration time are no longer valid anyway,
        so there's no need to keep them in the blacklist.

        Returns:
            Number of tokens removed
        """
        try:
            query = delete(TokenBlacklist).where(
                TokenBlacklist.expires_at < datetime.utcnow()
            )
            result = await self.session.execute(query)
            await self.session.flush()

            return result.rowcount

        except Exception as e:
            await self.session.rollback()
            raise DatabaseException(f"Failed to cleanup expired tokens: {str(e)}")
