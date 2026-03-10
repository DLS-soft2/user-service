"""
Database connection setup.

This module creates three things:
1. engine    — the actual connection to PostgreSQL
2. SessionLocal — a factory that creates database sessions (one per request)
3. Base      — a base class that all our database models inherit from

Think of it like this:
- The engine is the "pipe" to the database
- A session is a "conversation" with the database (open it, do stuff, close it)
- Base is the "template" for defining tables as Python classes
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from app.config import settings

# Create the database engine — this is the connection to PostgreSQL.
# pool_pre_ping=True makes SQLAlchemy check if the connection is still
# alive before using it, which prevents errors after database restarts.
engine = create_engine(settings.database_url, pool_pre_ping=True)

# SessionLocal is a factory — every time we call SessionLocal(), we get
# a new database session. We use one session per API request.
# autocommit=False means we control when changes are saved (explicit commits).
# autoflush=False means we control when SQLAlchemy syncs with the database.

# pylint: disable=invalid-name
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all database models. Every table we define will
# inherit from this, and SQLAlchemy uses it to keep track of all tables.
Base = declarative_base()


def get_db():
    """Dependency that provides a database session per request.

    FastAPI calls this automatically for every endpoint that needs
    a database connection. The 'yield' keyword means:
    1. Create a session
    2. Give it to the endpoint
    3. After the endpoint is done, close the session

    This pattern ensures we never leave database connections hanging open.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
