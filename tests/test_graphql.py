"""
Tests for GraphQL queries and mutations.

GraphQL requests are always POST to /graphql with a JSON body
containing the query string. The response always has a 'data'
field (and optionally an 'errors' field if something went wrong).
"""


GRAPHQL_URL = "/graphql"


def _create_test_user(client):
    """Helper — create a user via REST and return the response data."""
    user_data = {
        "keycloak_id": "kc-graphql-test-001",
        "email": "graphql@example.com",
        "full_name": "GraphQL Test User",
        "phone": "+45 11111111",
        "default_address": "GraphQL Street 1, 2100 Copenhagen",
    }
    response = client.post("/v1/users/", json=user_data)
    return response.json()


def test_query_all_users(client, sample_user_data):
    """Test querying all users via GraphQL."""
    # First create a user via REST
    client.post("/v1/users/", json=sample_user_data)

    # Then query via GraphQL
    query = """
        query {
            users {
                fullName
                email
            }
        }
    """
    response = client.post(GRAPHQL_URL, json={"query": query})
    assert response.status_code == 200

    data = response.json()
    assert "data" in data
    assert len(data["data"]["users"]) == 1
    assert data["data"]["users"][0]["fullName"] == sample_user_data["full_name"]


def test_query_user_by_id(client):
    """Test querying a single user by ID via GraphQL."""
    created = _create_test_user(client)

    query = """
        query($userId: UUID!) {
            user(userId: $userId) {
                fullName
                email
                phone
            }
        }
    """
    response = client.post(
        GRAPHQL_URL,
        json={"query": query, "variables": {"userId": created["id"]}},
    )
    assert response.status_code == 200

    data = response.json()
    assert data["data"]["user"]["fullName"] == "GraphQL Test User"
    assert data["data"]["user"]["phone"] == "+45 11111111"


def test_query_user_by_keycloak_id(client):
    """Test querying a user by Keycloak ID via GraphQL."""
    _create_test_user(client)

    query = """
        query($keycloakId: String!) {
            userByKeycloakId(keycloakId: $keycloakId) {
                fullName
                email
            }
        }
    """
    response = client.post(
        GRAPHQL_URL,
        json={"query": query, "variables": {"keycloakId": "kc-graphql-test-001"}},
    )
    assert response.status_code == 200

    data = response.json()
    assert data["data"]["userByKeycloakId"]["email"] == "graphql@example.com"


def test_query_nonexistent_user(client):
    """Test that querying a non-existent user returns null."""
    query = """
        query($userId: UUID!) {
            user(userId: $userId) {
                fullName
            }
        }
    """
    response = client.post(
        GRAPHQL_URL,
        json={
            "query": query,
            "variables": {"userId": "00000000-0000-0000-0000-000000000000"},
        },
    )
    assert response.status_code == 200
    assert response.json()["data"]["user"] is None


def test_query_specific_fields_only(client):
    """Test that GraphQL returns ONLY the requested fields.

    This is the key advantage over REST — no over-fetching.
    Here we only ask for the name, so we should NOT get email,
    phone, etc. in the response.
    """
    _create_test_user(client)

    query = """
        query {
            users {
                fullName
            }
        }
    """
    response = client.post(GRAPHQL_URL, json={"query": query})
    data = response.json()

    user = data["data"]["users"][0]
    assert "fullName" in user
    # These fields should NOT be in the response because we didn't ask for them
    assert "email" not in user
    assert "phone" not in user


def test_mutation_create_user(client):
    """Test creating a user via GraphQL mutation."""
    mutation = """
        mutation($input: UserCreateInput!) {
            createUser(input: $input) {
                id
                fullName
                email
                createdAt
            }
        }
    """
    variables = {
        "input": {
            "keycloakId": "kc-mutation-test-001",
            "email": "mutation@example.com",
            "fullName": "Mutation Test User",
        }
    }
    response = client.post(
        GRAPHQL_URL, json={"query": mutation, "variables": variables}
    )
    assert response.status_code == 200

    data = response.json()
    assert data["data"]["createUser"]["fullName"] == "Mutation Test User"
    assert data["data"]["createUser"]["id"] is not None


def test_mutation_update_user(client):
    """Test updating a user via GraphQL mutation."""
    created = _create_test_user(client)

    mutation = """
        mutation($userId: UUID!, $input: UserUpdateInput!) {
            updateUser(userId: $userId, input: $input) {
                fullName
                phone
            }
        }
    """
    variables = {
        "userId": created["id"],
        "input": {"phone": "+45 99999999"},
    }
    response = client.post(
        GRAPHQL_URL, json={"query": mutation, "variables": variables}
    )
    assert response.status_code == 200

    data = response.json()
    assert data["data"]["updateUser"]["phone"] == "+45 99999999"
    # Name should be unchanged
    assert data["data"]["updateUser"]["fullName"] == "GraphQL Test User"


def test_mutation_delete_user(client):
    """Test deleting a user via GraphQL mutation."""
    created = _create_test_user(client)

    mutation = """
        mutation($userId: UUID!) {
            deleteUser(userId: $userId)
        }
    """
    response = client.post(
        GRAPHQL_URL,
        json={"query": mutation, "variables": {"userId": created["id"]}},
    )
    assert response.status_code == 200
    assert response.json()["data"]["deleteUser"] is True

    # Verify user is gone
    query = """
        query($userId: UUID!) {
            user(userId: $userId) { fullName }
        }
    """
    verify = client.post(
        GRAPHQL_URL,
        json={"query": query, "variables": {"userId": created["id"]}},
    )
    assert verify.json()["data"]["user"] is None
