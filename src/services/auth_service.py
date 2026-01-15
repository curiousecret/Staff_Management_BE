from sqlalchemy.ext.asyncio import AsyncSession

from src.schemas.auth_schema import UserRegister, UserLogin, Token
from src.schemas.user_schema import UserResponse
from src.repositories.user_repository import UserRepository
from src.core.auth import verify_password, get_password_hash, create_access_token
from src.core.exceptions import UnauthorizedException


class AuthService:
    """
    Service layer for authentication business logic.

    Handles user registration, login, and token generation.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.repository = UserRepository(session)

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
