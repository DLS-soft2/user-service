"""
User profile endpoints.

Implements CRUD (Create, Read, Update, Delete) operations for user profiles.
Each endpoint uses FastAPI's dependency injection to get a database session
via the get_db dependency — we don't create sessions manually.

All endpoints are prefixed with /v1/users (set in main.py when including
the router). The /v1/ prefix is our API versioning strategy — if we ever
need breaking changes, we create /v2/ endpoints while keeping /v1/ alive.
"""

from uuid import UUID
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.schemas import UserCreate, UserUpdate, UserResponse

router = APIRouter()


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """Create a new user profile.

    In the real system, this would be called after a user registers
    via Keycloak. The frontend would send the Keycloak ID along with
    the profile data so we can link the two.
    """
    # Check if a user with this keycloak_id already exists
    existing_user = db.query(User).filter(
        User.keycloak_id == user_data.keycloak_id
    ).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"User with keycloak_id '{user_data.keycloak_id}' already exists",
        )

    # Check if email is already taken
    existing_email = db.query(User).filter(User.email == user_data.email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Email '{user_data.email}' is already in use",
        )

    # Create the user — SQLAlchemy converts this Python object into
    # an INSERT INTO statement automatically
    new_user = User(**user_data.model_dump())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)  # Reload from DB to get generated fields (id, timestamps)

    return new_user


@router.get("/", response_model=List[UserResponse])
def get_all_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all user profiles with pagination.

    skip and limit provide basic pagination:
    - GET /v1/users/?skip=0&limit=10  → first 10 users
    - GET /v1/users/?skip=10&limit=10 → next 10 users
    """
    users = db.query(User).offset(skip).limit(limit).all()
    return users


@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: UUID, db: Session = Depends(get_db)):
    """Get a single user profile by ID."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user


@router.get("/keycloak/{keycloak_id}", response_model=UserResponse)
def get_user_by_keycloak_id(keycloak_id: str, db: Session = Depends(get_db)):
    """Get a user profile by their Keycloak ID.

    This is the endpoint the API Gateway will call most often — when
    a user makes a request, the JWT contains their Keycloak ID, and
    this endpoint looks up their full profile.
    """
    user = db.query(User).filter(User.keycloak_id == keycloak_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user


@router.put("/{user_id}", response_model=UserResponse)
def update_user(user_id: UUID, user_data: UserUpdate, db: Session = Depends(get_db)):
    """Update an existing user profile.

    Only updates the fields that are provided (not None).
    This is the partial update pattern — the client sends only
    what they want to change.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Only update fields that were actually sent in the request
    update_data = user_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)

    db.commit()
    db.refresh(user)

    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: UUID, db: Session = Depends(get_db)):
    """Delete a user profile.

    Returns 204 No Content on success (standard for DELETE operations).
    In a production system, you might want soft deletes instead (the
    Tombstone pattern from your architecture), but for now hard delete
    is fine.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    db.delete(user)
    db.commit()
