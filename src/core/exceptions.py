from fastapi import HTTPException, status


class BaseAPIException(HTTPException):
    """Base exception class for API errors."""
    
    def __init__(
        self,
        status_code: int,
        detail: str,
    ) -> None:
        super().__init__(status_code=status_code, detail=detail)


class NotFoundException(BaseAPIException):
    """Raised when a resource is not found."""
    
    def __init__(self, resource: str, identifier: str) -> None:
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{resource} with identifier '{identifier}' not found",
        )


class DuplicateException(BaseAPIException):
    """Raised when attempting to create a duplicate resource."""
    
    def __init__(self, resource: str, field: str, value: str) -> None:
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"{resource} with {field} '{value}' already exists",
        )


class ValidationException(BaseAPIException):
    """Raised when validation fails."""
    
    def __init__(self, detail: str) -> None:
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
        )


class DatabaseException(BaseAPIException):
    """Raised when a database operation fails."""

    def __init__(self, detail: str = "Database operation failed") -> None:
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
        )


class UnauthorizedException(BaseAPIException):
    """Raised when authentication fails or token is invalid."""

    def __init__(self, detail: str = "Could not validate credentials") -> None:
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
        )
        self.headers = {"WWW-Authenticate": "Bearer"}