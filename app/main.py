"""
User Profile Service — main application entry point.

Manages user profile data (delivery addresses, preferences)
linked to Keycloak user IDs. Authentication is handled by the
API Gateway — this service handles authorization via shared RBAC decorators.

This service exposes TWO API types:
- REST  (under /v1/users/)  — standard CRUD endpoints
- GraphQL (under /graphql)  — flexible queries for the frontend
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import engine, Base
from app.routers import users
from app.graphql.schema import graphql_router


@asynccontextmanager
async def lifespan(_application: FastAPI):
    """Startup and shutdown logic for the application."""
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="User Profile Service",
    description="Stores and manages user profile data for the DLS-2 food delivery platform",
    version="0.3.0",
    lifespan=lifespan,
)

# REST endpoints — standard CRUD under /v1/users/
app.include_router(users.router, prefix="/v1/users", tags=["users"])

# GraphQL endpoint — available at /graphql with interactive GraphiQL playground
app.include_router(graphql_router, prefix="/graphql", tags=["graphql"])


@app.get("/")
def read_root():
    """Root endpoint — basic service info."""
    return {
        "service": "user-service",
        "version": "0.3.0",
        "status": "running",
    }


@app.get("/health")
def health_check():
    """Health check endpoint — used by Docker and orchestration tools
    to verify the service is alive and responding."""
    return {"status": "healthy"}
