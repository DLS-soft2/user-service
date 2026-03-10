"""
Application configuration.

Uses pydantic-settings to read values from environment variables.
This is the standard approach in microservices — you never hardcode
database passwords or connection strings in your code. Instead, each
environment (local dev, CI, production) sets its own env vars.
"""

from pydantic_settings import BaseSettings
from pydantic import ConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables.

    For local development, the defaults point to a local PostgreSQL
    instance (run via Docker Compose). In production, these
    are overridden by the deployment environment.
    """

    database_url: str = "postgresql://postgres:postgres@localhost:5432/userdb"
    app_name: str = "User Profile Service"
    debug: bool = True

    model_config = ConfigDict(env_file=".env")

# Single settings instance used across the application
settings = Settings()
