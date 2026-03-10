"""
User Profile Service

Manages user profile data (delivery addresses, preferences)
linked to Keycloak user IDs. Authentication is handled by the
API Gateway — this service handles authorization via shared RBAC decorators.
"""

from fastapi import FastAPI

app = FastAPI(
    title="User Profile Service",
    description="Stores and manages user profile data for the DLS-2 food delivery platform",
    version="0.1.0",
)


@app.get("/")
def read_root():
    """Root endpoint — basic service info."""
    return {
        "service": "user-service",
        "version": "0.1.0",
        "status": "running",
    }


@app.get("/health")
def health_check():
    """Health check endpoint — used by Docker and orchestration tools
    to verify the service is alive and responding."""
    return {"status": "healthy"}
