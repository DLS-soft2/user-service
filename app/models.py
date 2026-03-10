"""
Database models (SQLAlchemy).

Each class here represents a table in PostgreSQL. SQLAlchemy translates
the Python class into a CREATE TABLE statement automatically.

For example, the User class below becomes:

    CREATE TABLE users (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        keycloak_id VARCHAR UNIQUE NOT NULL,
        email VARCHAR UNIQUE NOT NULL,
        full_name VARCHAR NOT NULL,
        phone VARCHAR,
        default_address VARCHAR,
        created_at TIMESTAMP DEFAULT NOW(),
        updated_at TIMESTAMP DEFAULT NOW()
    );

We separate these from Pydantic schemas (schemas.py) because they
serve different purposes:
- Models = how data is stored in the database
- Schemas = how data is sent/received via the API
"""

import uuid

from sqlalchemy import Column, String, DateTime, func
from sqlalchemy.dialects.postgresql import UUID

from app.database import Base


class User(Base):
    """User profile table.

    Stores domain-specific user data linked to Keycloak user IDs.
    Authentication is handled by Keycloak — this service only stores
    profile data like delivery addresses and preferences.
    """

    __tablename__ = "users"

    # Primary key — UUID is better than auto-increment integers for
    # microservices because it avoids ID collisions between services
    # and doesn't reveal how many users you have.
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Links this profile to the Keycloak user. When a user logs in
    # via Keycloak, the JWT contains their Keycloak ID, which we use
    # to look up their profile here.
    keycloak_id = Column(String, unique=True, nullable=False, index=True)

    email = Column(String, unique=True, nullable=False)
    full_name = Column(String, nullable=False)
    phone = Column(String, nullable=True)
    default_address = Column(String, nullable=True)

    # Automatic timestamps — the database sets these, not our code
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
