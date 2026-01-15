from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError
from typing import Optional

from src.models.user_model import User
from src.schemas.auth_schema import UserRegister
from src.core.exceptions import DuplicateException, DatabaseException


class UserRepository:
    """
    Repository for User database operations.

    Handles all database interactions for User entity.
    Uses async operations for optimal performance.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, user_data: UserRegister, hashed_password: str) -> User:
        """
        Create a new user record.

        Args:
            user_data: Validated user registration data
            hashed_password: Pre-hashed password

        Returns:
            Created User object

        Raises:
            DuplicateException: If username already exists
            DatabaseException: If database operation fails
        """
        try:
            user = User(
                username=user_data.username,
                hashed_password=hashed_password,
            )

            self.session.add(user)
            await self.session.flush()
            await self.session.refresh(user)

            return user

        except IntegrityError as e:
            await self.session.rollback()
            if "unique" in str(e).lower() or "duplicate" in str(e).lower():
                raise DuplicateException("User", "username", user_data.username)
            raise DatabaseException(f"Failed to create user: {str(e)}")

    async def get_by_username(self, username: str) -> Optional[User]:
        """
        Get user by username.

        Args:
            username: The username to search for

        Returns:
            User object if found, None otherwise
        """
        query = select(User).where(User.username == username)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_id(self, id: int) -> Optional[User]:
        """
        Get user by internal ID.

        Args:
            id: The internal primary key

        Returns:
            User object if found, None otherwise
        """
        query = select(User).where(User.id == id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def exists_by_username(self, username: str) -> bool:
        """
        Check if user exists by username.

        Args:
            username: The username to check

        Returns:
            True if exists, False otherwise
        """
        query = select(func.count(User.id)).where(User.username == username)
        result = await self.session.execute(query)
        count = result.scalar_one()
        return count > 0
