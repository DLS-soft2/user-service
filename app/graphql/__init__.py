"""
GraphQL type definitions.

These are similar to Pydantic schemas but for GraphQL. They define
what fields are available when the frontend queries for users.

Strawberry uses Python type annotations to generate the GraphQL schema
automatically — so a Python class becomes a GraphQL type.
"""

from datetime import datetime
from uuid import UUID
from typing import Optional

import strawberry

# Strawberry types are data containers, not behavioral classes
# pylint: disable=too-few-public-methods

@strawberry.type
class UserType:
    """GraphQL representation of a user profile.

    This is what the frontend receives when it queries for users.
    The @strawberry.type decorator converts this Python class into
    a GraphQL type definition automatically.
    """

    id: UUID
    keycloak_id: str
    email: str
    full_name: str
    phone: Optional[str] = None
    default_address: Optional[str] = None
    created_at: datetime
    updated_at: datetime


@strawberry.input
class UserCreateInput:
    """GraphQL input type for creating a user.

    @strawberry.input is like @strawberry.type but specifically for
    data coming FROM the frontend (mutation arguments).
    """

    keycloak_id: str
    email: str
    full_name: str
    phone: Optional[str] = None
    default_address: Optional[str] = None


@strawberry.input
class UserUpdateInput:
    """GraphQL input type for updating a user.

    All fields are optional — the frontend only sends what it
    wants to change (same partial update pattern as our REST API).
    """

    email: Optional[str] = None
    full_name: Optional[str] = None
    phone: Optional[str] = None
    default_address: Optional[str] = None
