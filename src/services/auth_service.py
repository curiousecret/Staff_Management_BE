from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
from jose import jwt

from src.schemas.auth_schema import UserRegister, UserLogin, Token
from src.schemas.user_schema import UserResponse
from src.repositories.user_repository import UserRepository
from src.repositories.token_blacklist_repository import TokenBlacklistRepository
from src.repositories.refresh_token_repository import RefreshTokenRepository
from src.core.auth import verify_password, get_password_hash, create_access_token, create_refresh_token
from src.core.config import get_settings
from src.core.exceptions import UnauthorizedException

settings = get_settings()


class AuthService:
    """
    Service layer for authentication business logic.

    Handles user registration, login, logout, and token management.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = UserRepository(session)
        self.token_blacklist_repository = TokenBlacklistRepository(session)
        self.refresh_token_repository = RefreshTokenRepository(session)

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
        Authenticate user and generate JWT tokens (access + refresh).

        Args:
            login_data: User login credentials

        Returns:
            JWT access token and refresh token

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

        # Create refresh token
        refresh_token_str = create_refresh_token()
        refresh_token_expires = datetime.utcnow() + timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS
        )

        # Store refresh token in database
        await self.refresh_token_repository.create(
            token=refresh_token_str,
            user_id=user.id,
            expires_at=refresh_token_expires
        )

        # Commit the transaction
        await self.session.commit()

        return Token(
            access_token=access_token,
            refresh_token=refresh_token_str,
            token_type="bearer"
        )

    async def logout(self, token: str, user_id: int) -> dict:
        """
        Logout user by blacklisting their access token and revoking all refresh tokens.

        Args:
            token: The JWT access token to invalidate
            user_id: The ID of the user logging out

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

            # Add access token to blacklist
            await self.token_blacklist_repository.add_token(token, expires_at)

            # Revoke all refresh tokens for this user
            await self.refresh_token_repository.revoke_all_user_tokens(user_id)

            # Cleanup expired tokens (opportunistic cleanup)
            await self.token_blacklist_repository.cleanup_expired_tokens()
            await self.refresh_token_repository.cleanup_expired_tokens()

            # Commit the transaction
            await self.session.commit()

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

    async def refresh_access_token(self, refresh_token_str: str) -> Token:
        """
        Generate a new access token using a refresh token.

        Args:
            refresh_token_str: The refresh token string

        Returns:
            New JWT access token and the same refresh token

        Raises:
            UnauthorizedException: If refresh token is invalid or expired
        """
        # Get refresh token from database
        refresh_token = await self.refresh_token_repository.get_by_token(refresh_token_str)

        if refresh_token is None:
            raise UnauthorizedException("Invalid refresh token")

        # Check if token is revoked
        if refresh_token.is_revoked:
            raise UnauthorizedException("Refresh token has been revoked")

        # Check if token is expired
        if refresh_token.expires_at < datetime.utcnow():
            raise UnauthorizedException("Refresh token has expired")

        # Get user from database
        user = await self.repository.get_by_id(refresh_token.user_id)

        if user is None:
            raise UnauthorizedException("User not found")

        # Update last used timestamp
        await self.refresh_token_repository.update_last_used(refresh_token_str)

        # Create new access token
        access_token = create_access_token(data={"sub": user.username})

        # Commit the transaction
        await self.session.commit()

        # Return new access token with the same refresh token
        return Token(
            access_token=access_token,
            refresh_token=refresh_token_str,
            token_type="bearer"
        )
