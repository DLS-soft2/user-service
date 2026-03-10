"""
GraphQL resolvers (queries and mutations).

In GraphQL, you have:
- Queries  = reading data (like GET)
- Mutations = changing data (like POST, PUT, DELETE)

The resolvers are the functions that do the work — they
talk to the database and return results. Strawberry connects them
to the GraphQL schema automatically.
"""

from uuid import UUID
from typing import List, Optional

import strawberry
from sqlalchemy.orm import Session

from app.models import User
from app.graphql import UserType, UserCreateInput, UserUpdateInput

# 'input' is required by Strawberry's API convention
# pylint: disable=redefined-builtin

def _model_to_type(user: User) -> UserType:
    """Convert a SQLAlchemy User model to a GraphQL UserType.

    This is needed because Strawberry and SQLAlchemy use different
    object types. We manually map the fields from one to the other.
    """
    return UserType(
        id=user.id,
        keycloak_id=user.keycloak_id,
        email=user.email,
        full_name=user.full_name,
        phone=user.phone,
        default_address=user.default_address,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )


@strawberry.type
class Query:
    """GraphQL queries — all read operations.

    The frontend can call these to fetch user data. For example:

        query {
            users {
                fullName
                email
            }
        }

    This would return only the name and email for all users —
    no over-fetching of unnecessary fields.
    """

    @strawberry.field
    def users(self, info: strawberry.types.Info) -> List[UserType]:
        """Get all user profiles."""
        db: Session = info.context["db"]
        db_users = db.query(User).all()
        return [_model_to_type(user) for user in db_users]

    @strawberry.field
    def user(self, info: strawberry.types.Info, user_id: UUID) -> Optional[UserType]:
        """Get a single user by ID."""
        db: Session = info.context["db"]
        db_user = db.query(User).filter(User.id == user_id).first()
        if not db_user:
            return None
        return _model_to_type(db_user)

    @strawberry.field
    def user_by_keycloak_id(
        self, info: strawberry.types.Info, keycloak_id: str
    ) -> Optional[UserType]:
        """Get a user by their Keycloak ID.

        This is the most common lookup — the API Gateway extracts
        the Keycloak ID from the JWT and uses it to fetch the profile.
        """
        db: Session = info.context["db"]
        db_user = db.query(User).filter(User.keycloak_id == keycloak_id).first()
        if not db_user:
            return None
        return _model_to_type(db_user)


@strawberry.type
class Mutation:
    """GraphQL mutations — all write operations.

    Example of creating a user:

        mutation {
            createUser(input: {
                keycloakId: "kc-123",
                email: "user@example.com",
                fullName: "John Doe"
            }) {
                id
                fullName
                createdAt
            }
        }
    """

    @strawberry.mutation
    def create_user(
        self, info: strawberry.types.Info, input: UserCreateInput  # noqa: A002
    ) -> UserType:
        """Create a new user profile."""
        db: Session = info.context["db"]

        new_user = User(
            keycloak_id=input.keycloak_id,
            email=input.email,
            full_name=input.full_name,
            phone=input.phone,
            default_address=input.default_address,
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return _model_to_type(new_user)

    @strawberry.mutation
    def update_user(
        self,
        info: strawberry.types.Info,
        user_id: UUID,
        input: UserUpdateInput,  # noqa: A002
    ) -> Optional[UserType]:
        """Update an existing user profile."""
        db: Session = info.context["db"]
        db_user = db.query(User).filter(User.id == user_id).first()
        if not db_user:
            return None

        # Only update fields that were provided
        if input.email is not None:
            db_user.email = input.email
        if input.full_name is not None:
            db_user.full_name = input.full_name
        if input.phone is not None:
            db_user.phone = input.phone
        if input.default_address is not None:
            db_user.default_address = input.default_address

        db.commit()
        db.refresh(db_user)

        return _model_to_type(db_user)

    @strawberry.mutation
    def delete_user(self, info: strawberry.types.Info, user_id: UUID) -> bool:
        """Delete a user profile. Returns true if successful."""
        db: Session = info.context["db"]
        db_user = db.query(User).filter(User.id == user_id).first()
        if not db_user:
            return False

        db.delete(db_user)
        db.commit()
        return True
