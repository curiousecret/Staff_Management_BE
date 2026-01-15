from pydantic import BaseModel, ConfigDict
from datetime import datetime


class UserResponse(BaseModel):
    """Schema for user response (without password)."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    created_at: datetime
    updated_at: datetime
