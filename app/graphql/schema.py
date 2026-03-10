"""
GraphQL schema setup and FastAPI integration.

This module creates the Strawberry schema (combining queries and mutations)
and provides a custom GraphQL router that injects the database session
into the GraphQL context = resolvers can access the database.
"""

import strawberry
from strawberry.fastapi import GraphQLRouter
from fastapi import Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.graphql.resolvers import Query, Mutation

# Create the Strawberry schema — this combines all queries and mutations
# into a single GraphQL schema that clients can query against.
schema = strawberry.Schema(query=Query, mutation=Mutation)


async def get_context(db: Session = Depends(get_db)):
    """Provide database session to GraphQL resolvers via context.

    Uses FastAPI's Depends(get_db) — the same dependency our REST
    endpoints use. This ensures the session is properly created
    before the request and closed after it, just like in REST.
    """
    return {"db": db}


# GraphQLRouter is Strawberry's built-in FastAPI integration.
# It creates a /graphql endpoint with both the GraphQL API
# and an interactive GraphiQL playground (like Swagger but for GraphQL).
graphql_router = GraphQLRouter(schema, context_getter=get_context)