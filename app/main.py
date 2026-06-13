from contextlib import asynccontextmanager

from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

from app.routers import users
from app.graphql.schema import graphql_router


@asynccontextmanager
async def lifespan(_application: FastAPI):
    """Startup and shutdown logic for the application."""
    yield


app = FastAPI(
    title="User Profile Service",
    description="Stores and manages user profile data for the DLS-2 food delivery platform",
    version="0.4.0",
    lifespan=lifespan,
)
Instrumentator().instrument(app).expose(app)

app.include_router(users.router, prefix="/api/v1/users", tags=["users"])

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
