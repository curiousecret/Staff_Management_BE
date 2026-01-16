from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from jose import jwt

from src.schemas.auth_schema import UserRegister, UserLogin, Token
from src.schemas.user_schema import UserResponse
from src.repositories.user_repository import UserRepository
from src.repositories.token_blacklist_repository import TokenBlacklistRepository
from src.core.auth import verify_password, get_password_hash, create_access_token
from src.core.config import get_settings
from src.core.exceptions import UnauthorizedException

settings = get_settings()


class AuthService:
    """
    Service layer for authentication business logic.

    Handles user registration, login, logout, and token management.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.repository = UserRepository(session)
        self.token_blacklist_repository = TokenBlacklistRepository(session)

    async def register(self, user_data: UserRegister) -> UserResponse:
        """
        Register a new user.

        Args:
            user_data: Validated user registration data

        Returns:
            Created user as response schema (without password)

        Raises:
            DuplicateException: If username already exists (from repository)
        """
        # Hash the password
        hashed_password = get_password_hash(user_data.password)

        # Create user in database
        user = await self.repository.create(user_data, hashed_password)

        return UserResponse.model_validate(user)

    async def login(self, login_data: UserLogin) -> Token:
        """
        Authenticate user and generate JWT token.

        Args:
            login_data: User login credentials

        Returns:
            JWT access token

        Raises:
            UnauthorizedException: If credentials are invalid
        """
        # Get user from database
        user = await self.repository.get_by_username(login_data.username)

        if user is None:
            raise UnauthorizedException("Incorrect username or password")

        # Verify password
        if not verify_password(login_data.password, user.hashed_password):
            raise UnauthorizedException("Incorrect username or password")

        # Create access token
        access_token = create_access_token(data={"sub": user.username})

        return Token(access_token=access_token, token_type="bearer")

    async def logout(self, token: str) -> dict:
        """
        Logout user by blacklisting their token.

        Args:
            token: The JWT token to invalidate

        Returns:
            Success message

        Raises:
            UnauthorizedException: If token is invalid
        """
        try:
            # Decode token to get expiration time
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM]
            )

            # Get expiration timestamp
            exp_timestamp = payload.get("exp")
            if exp_timestamp is None:
                raise UnauthorizedException("Invalid token")

            expires_at = datetime.fromtimestamp(exp_timestamp)

            # Add token to blacklist
            await self.token_blacklist_repository.add_token(token, expires_at)

            # Cleanup expired tokens (opportunistic cleanup)
            await self.token_blacklist_repository.cleanup_expired_tokens()

            return {"message": "Successfully logged out"}

        except jwt.JWTError:
            raise UnauthorizedException("Invalid token")

    async def is_token_blacklisted(self, token: str) -> bool:
        """
        Check if a token is blacklisted.

        Args:
            token: The JWT token to check

        Returns:
            True if blacklisted, False otherwise
        """
        return await self.token_blacklist_repository.is_blacklisted(token)
