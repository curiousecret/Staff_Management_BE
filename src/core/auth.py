from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
import secrets

from src.core.config import get_settings
from src.core.database import get_async_session
from src.core.exceptions import UnauthorizedException
from src.models.user_model import User
from src.repositories.user_repository import UserRepository
from src.repositories.token_blacklist_repository import TokenBlacklistRepository
from src.schemas.auth_schema import TokenData


# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

# Get settings
settings = get_settings()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain text password against a hashed password.

    Args:
        plain_password: The plain text password to verify
        hashed_password: The hashed password to compare against

    Returns:
        True if password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hash a plain text password.

    Args:
        password: The plain text password to hash

    Returns:
        The hashed password
    """
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.

    Args:
        data: Dictionary containing the data to encode in the token
        expires_delta: Optional custom expiration time delta

    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    return encoded_jwt


def create_refresh_token() -> str:
    """
    Create a secure random refresh token.

    Generates a cryptographically secure random token using secrets module.
    This token is stored in the database and used to obtain new access tokens.

    Returns:
        A secure random token string (64 characters)
    """
    return secrets.token_urlsafe(48)  # 48 bytes = 64 characters when base64 encoded


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_async_session),
) -> User:
    """
    Dependency to get the current authenticated user from JWT token.

    Args:
        token: JWT token from the Authorization header
        session: Database session

    Returns:
        The authenticated User object

    Raises:
        UnauthorizedException: If token is invalid, blacklisted, or user not found
    """
    # Check if token is blacklisted first
    token_blacklist_repository = TokenBlacklistRepository(session)
    is_blacklisted = await token_blacklist_repository.is_blacklisted(token)

    if is_blacklisted:
        raise UnauthorizedException("Token has been revoked")

    try:
        # Decode the JWT token
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )

        username: str = payload.get("sub")
        if username is None:
            raise UnauthorizedException("Could not validate credentials")

        token_data = TokenData(username=username)

    except JWTError:
        raise UnauthorizedException("Could not validate credentials")

    # Get user from database
    user_repository = UserRepository(session)
    user = await user_repository.get_by_username(username=token_data.username)

    if user is None:
        raise UnauthorizedException("Could not validate credentials")

    return user
