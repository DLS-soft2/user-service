"""
User Profile Service — main application entry point.

Manages user profile data (delivery addresses, preferences)
linked to Keycloak user IDs. Authentication is handled by the
API Gateway — this service handles authorization via shared RBAC decorators.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import engine, Base
from app.routers import users


@asynccontextmanager
async def lifespan(_application: FastAPI):
    """Startup and shutdown logic for the application.

    Code before 'yield' runs on startup, code after runs on shutdown.
    We create database tables here instead of at module level so that:
    1. Tests can override the database before tables are created
    2. The app doesn't crash on import if the database is unreachable
    """
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="User Profile Service",
    description="Stores and manages user profile data for the DLS-2 food delivery platform",
    version="0.2.0",
    lifespan=lifespan,
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
