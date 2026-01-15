from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from src.core.database import init_db
from src.core.config import get_settings
from src.core.exceptions import BaseAPIException
from src.routers.staff_router import router as staff_router
from src.routers.auth_router import router as auth_router

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan handler.

    Handles startup and shutdown events.
    """
    # Startup
    print("Starting up...")
    await init_db()
    print("Database initialized")

    yield

    # Shutdown
    print("Shutting down...")


# =============================================================================
# Application Factory
# =============================================================================

def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.

    Returns:
        Configured FastAPI application instance
    """
    app = FastAPI(
        title="Staff Management API",
        description="API for managing staff information",
        version="1.0.0",
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure appropriately for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register exception handlers
    register_exception_handlers(app)

    # Register routers
    register_routers(app)

    return app


def register_exception_handlers(app: FastAPI) -> None:
    """Register global exception handlers."""

    @app.exception_handler(BaseAPIException)
    async def api_exception_handler(
        request: Request,
        exc: BaseAPIException,
    ) -> JSONResponse:
        """Handle custom API exceptions."""
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(
        request: Request,
        exc: Exception,
    ) -> JSONResponse:
        """Handle unexpected exceptions."""
        # Log the exception in production
        if settings.DEBUG:
            detail = str(exc)
        else:
            detail = "Internal server error"

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": detail},
        )


def register_routers(app: FastAPI) -> None:
    """Register API routers."""
    app.include_router(auth_router, prefix="/api/v1")
    app.include_router(staff_router, prefix="/api/v1")


# =============================================================================
# Application Instance
# =============================================================================

app = create_app()


# =============================================================================
# Health Check
# =============================================================================

@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}