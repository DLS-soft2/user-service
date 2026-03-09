# user-service

User Profile Service for the DLS-2 food delivery platform. Stores and manages user profile data (delivery addresses, food preferences) linked to Keycloak user IDs.

## Tech Stack

- **Framework:** FastAPI (Python 3.12)
- **Database:** PostgreSQL
- **Auth:** Keycloak (JWT via API Gateway) + shared RBAC library

## Development

```bash
poetry install
poetry run uvicorn app.main:app --port 8001 --reload
```

## Docker

```bash
docker build -t user-service .
docker run -p 8001:8000 user-service
```