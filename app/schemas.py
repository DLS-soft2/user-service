"""
Pydantic schemas (request/response models).

These define the SHAPE of data going in and out of the API.
They are separate from SQLAlchemy models (models.py) because:

- When CREATING a user, the client shouldn't send an ID or timestamps
  (the database generates those).
- When READING a user, we want to include the ID and timestamps.
- We might want to hide certain fields from the API response.

This separation is a common pattern in FastAPI applications and gives
us full control over what the API exposes.
"""

from datetime import datetime
from uuid import UUID
from typing import Optional

from pydantic import BaseModel, ConfigDict


class UserCreate(BaseModel):
    """Schema for creating a new user profile.

    This is what the client sends in the POST request body.
    Notice: no id, created_at, or updated_at — those are generated
    by the database automatically.
    """

    keycloak_id: str
    email: str
    full_name: str
    phone: Optional[str] = None
    default_address: Optional[str] = None


class UserUpdate(BaseModel):
    """Schema for updating an existing user profile.

    All fields are optional — the client only sends the fields
    they want to change. This is called a 'partial update' pattern.
    """

    email: Optional[str] = None
    full_name: Optional[str] = None
    phone: Optional[str] = None
    default_address: Optional[str] = None


class UserResponse(BaseModel):
    """Schema for returning a user profile in API responses.

    Includes all fields including the auto-generated ones (id, timestamps).
    model_config with from_attributes=True tells Pydantic to read data
    directly from SQLAlchemy model attributes (instead of expecting a dict).
    """

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    keycloak_id: str
    email: str
    full_name: str
    phone: Optional[str] = None
    default_address: Optional[str] = None
    created_at: datetime
    updated_at: datetime
