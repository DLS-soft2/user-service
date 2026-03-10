# user-service

User Profile Service for the food delivery platform. Stores and manages user profile data (delivery addresses, food preferences) linked to Keycloak user IDs.

## Tech Stack

- **Framework:** FastAPI (Python 3.12)
- **Database:** PostgreSQL (SQLAlchemy ORM)
- **GraphQL:** Strawberry
- **Auth:** Keycloak (JWT via API Gateway) + shared RBAC library
- **CI/CD:** GitHub Actions with shared workflows → GHCR

## API

The service exposes both REST and GraphQL endpoints. REST is used for standard CRUD operations, while GraphQL allows the frontend to request exactly the fields it needs — reducing over-fetching.

### REST Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Service info |
| GET | `/health` | Health check |
| POST | `/v1/users/` | Create user profile |
| GET | `/v1/users/` | List all users (with pagination) |
| GET | `/v1/users/{id}` | Get user by UUID |
| GET | `/v1/users/keycloak/{keycloak_id}` | Get user by Keycloak ID |
| PUT | `/v1/users/{id}` | Update user profile (partial) |
| DELETE | `/v1/users/{id}` | Delete user profile |

### GraphQL

Available at `/graphql` (includes interactive GraphiQL playground).

**Queries:** `users`, `user(userId)`, `userByKeycloakId(keycloakId)`

**Mutations:** `createUser(input)`, `updateUser(userId, input)`, `deleteUser(userId)`

Example query:
```graphql
query {
  users {
    fullName
    defaultAddress
  }
}
```

## Project Structure

```
user-service/
├── app/
│   ├── graphql/
│   │   ├── __init__.py      # GraphQL type definitions
│   │   ├── resolvers.py     # Query and mutation logic
│   │   └── schema.py        # Schema setup + FastAPI integration
│   ├── routers/
│   │   └── users.py         # REST CRUD endpoints
│   ├── config.py            # Settings from environment variables
│   ├── database.py          # SQLAlchemy engine and session setup
│   ├── main.py              # FastAPI app entry point
│   ├── models.py            # Database table definitions
│   └── schemas.py           # Pydantic request/response models
├── tests/
│   ├── conftest.py          # Test fixtures (SQLite test database)
│   ├── test_users.py        # REST endpoint tests
│   └── test_graphql.py      # GraphQL query/mutation tests
├── docker-compose.yaml      # Local dev: PostgreSQL + service
├── Dockerfile               # Multi-stage production build
└── pyproject.toml           # Dependencies and versioning
```

## Development

```bash
poetry install
poetry run uvicorn app.main:app --port 8001 --reload
```

Note: requires a running PostgreSQL instance. See Docker Compose below for an easier setup.

## Run with Docker Compose

Starts PostgreSQL and the service together:

```bash
docker compose up --build
```

- REST + Swagger UI: http://localhost:8001/docs
- GraphQL playground: http://localhost:8001/graphql

## Run Tests

Tests use SQLite in-memory — no database setup needed:

```bash
poetry run pytest -v
```

## CI/CD

Automated via GitHub Actions using shared workflows from `DLS-soft2/shared-workflows`:

- **On PR to main:** Pylint linting, pytest, version bump check
- **On merge to main:** Docker image built and pushed to `ghcr.io/dls-soft2/user-service:<version>`