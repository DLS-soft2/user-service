"""
User Profile Service — main application entry point.

Manages user profile data (delivery addresses, preferences)
linked to Keycloak user IDs. Authentication is handled by the
API Gateway — this service handles authorization via shared RBAC decorators.
"""

from fastapi import FastAPI

from app.database import engine, Base
from app.routers import users

# Create all database tables on startup. This reads all classes that
# inherit from Base (our User model) and creates the corresponding
# tables in PostgreSQL if they don't already exist.
#
# NOTE: In production, you would use a migration tool (Alembic??)
# instead, so you can evolve your schema over time without losing data.
# For now, this is fine for development.
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="User Profile Service",
    description="Stores and manages user profile data for the DLS-2 food delivery platform",
    version="0.2.0",
)

# Include the users router with a prefix. All endpoints defined in
# users.py will be available under /v1/users/
# The prefix implements our URI versioning strategy.
app.include_router(users.router, prefix="/v1/users", tags=["users"])


@app.get("/")
def read_root():
    """Root endpoint — basic service info."""
    return {
        "service": "user-service",
        "version": "0.2.0",
        "status": "running",
    }


@app.get("/health")
def health_check():
    """Health check endpoint — used by Docker and orchestration tools
    to verify the service is alive and responding."""
    return {"status": "healthy"}
