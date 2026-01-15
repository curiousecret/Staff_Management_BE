from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_async_session
from src.schemas.auth_schema import UserRegister, UserLogin, Token
from src.schemas.user_schema import UserResponse
from src.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


# =============================================================================
# Dependency Injection
# =============================================================================

async def get_auth_service(
    session: AsyncSession = Depends(get_async_session),
) -> AuthService:
    """Dependency to get AuthService instance."""
    return AuthService(session)


# =============================================================================
# API Endpoints
# =============================================================================

@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Create a new user account with username and password.",
)
async def register(
    user_data: UserRegister,
    service: AuthService = Depends(get_auth_service),
) -> UserResponse:
    """
    Register a new user.

    - **username**: Unique username (3-50 characters, alphanumeric and underscores only)
    - **password**: Password (minimum 8 characters)
    """
    return await service.register(user_data)


@router.post(
    "/login",
    response_model=Token,
    summary="Login and get access token",
    description="Authenticate with username and password to receive a JWT access token.",
)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    service: AuthService = Depends(get_auth_service),
) -> Token:
    """
    Login with username and password.

    Returns a JWT access token to be used for authenticating subsequent requests.

    Use the token in the Authorization header: `Bearer <token>`

    - **username**: Your username
    - **password**: Your password
    """
    # OAuth2PasswordRequestForm uses 'username' and 'password' fields
    login_data = UserLogin(username=form_data.username, password=form_data.password)
    return await service.login(login_data)
