# user-service

User Profile Service for the DLS-2 food delivery platform. Stores and manages user profile data (delivery addresses, food preferences) linked to Keycloak user IDs.

## Tech Stack

- **Framework:** FastAPI (Python 3.12)
- **Database:** PostgreSQL (SQLAlchemy ORM)
- **Auth:** Keycloak (JWT via API Gateway) + shared RBAC library

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Service info |
| GET | `/health` | Health check |
| POST | `/v1/users/` | Create user profile |
| GET | `/v1/users/` | List all users |
| GET | `/v1/users/{id}` | Get user by ID |
| GET | `/v1/users/keycloak/{keycloak_id}` | Get user by Keycloak ID |
| PUT | `/v1/users/{id}` | Update user profile |
| DELETE | `/v1/users/{id}` | Delete user profile |

## Development

```bash
poetry install
poetry run uvicorn app.main:app --port 8001 --reload
```

## Run with Docker Compose

```bash
docker compose up --build
```

## Run Tests

```bash
poetry run pytest
```