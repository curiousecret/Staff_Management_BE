from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_async_session
from src.core.auth import get_current_user
from src.models.user_model import User
from src.schemas.auth_schema import UserRegister, UserLogin, Token
from src.schemas.user_schema import UserResponse
from src.services.auth_service import AuthService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

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


@router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
    summary="Logout user",
    description="Logout the current authenticated user by blacklisting their token.",
)
async def logout(
    token: str = Depends(oauth2_scheme),
    current_user: User = Depends(get_current_user),
    service: AuthService = Depends(get_auth_service),
) -> dict:
    """
    Logout the authenticated user by blacklisting their token.

    This endpoint invalidates the JWT token on the server side.
    The token will no longer be accepted for authentication, even if it hasn't expired yet.
    Expired tokens are automatically cleaned up from the blacklist.

    Requires a valid JWT token in the Authorization header: `Bearer <token>`
    """
    return await service.logout(token)
