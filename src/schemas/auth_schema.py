from pydantic import BaseModel, Field, field_validator
from typing import Optional
import re


class UserRegister(BaseModel):
    """Schema for user registration."""

    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="Unique username (alphanumeric and underscores only)",
        examples=["john_doe"],
    )

    password: str = Field(
        ...,
        min_length=8,
        max_length=72,
        description="Password (8-72 characters, bcrypt limitation)",
        examples=["SecurePassword123"],
    )

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        """Validate username contains only alphanumeric characters and underscores."""
        v = v.strip().lower()
        if not re.match(r"^[a-z0-9_]+$", v):
            raise ValueError(
                "Username must contain only lowercase letters, numbers, and underscores"
            )
        return v

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate password strength and length."""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if len(v) > 72:
            raise ValueError("Password cannot be longer than 72 characters (bcrypt limitation)")
        return v


class UserLogin(BaseModel):
    """Schema for user login."""

    username: str = Field(
        ...,
        description="Username",
        examples=["john_doe"],
    )

    password: str = Field(
        ...,
        description="Password",
        examples=["SecurePassword123"],
    )


class Token(BaseModel):
    """Schema for JWT token response."""

    access_token: str = Field(
        ...,
        description="JWT access token",
    )

    token_type: str = Field(
        default="bearer",
        description="Token type",
    )


class TokenData(BaseModel):
    """Schema for token payload data."""

    username: Optional[str] = None
