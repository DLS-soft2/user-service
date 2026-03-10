"""
Tests for user profile CRUD endpoints.

Each test function tests one specific behavior. The naming convention
is test_<what_it_does> — its easy to see what broke when
a test fails.

The 'client' and 'sample_user_data' fixtures come from conftest.py
and are injected automatically by pytest.
"""


def test_root_endpoint(client):
    """Test that the root endpoint returns service info."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "user-service"
    assert data["status"] == "running"


def test_health_endpoint(client):
    """Test that the health check endpoint responds."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_create_user(client, sample_user_data):
    """Test creating a new user profile."""
    response = client.post("/v1/users/", json=sample_user_data)
    assert response.status_code == 201

    data = response.json()
    assert data["email"] == sample_user_data["email"]
    assert data["full_name"] == sample_user_data["full_name"]
    assert data["keycloak_id"] == sample_user_data["keycloak_id"]
    # Check that the database generated an ID and timestamps
    assert "id" in data
    assert "created_at" in data


def test_create_duplicate_user(client, sample_user_data):
    """Test that creating a user with an existing keycloak_id fails."""
    # Create the user first
    client.post("/v1/users/", json=sample_user_data)

    # Try to create the same user again — should get 409 Conflict
    response = client.post("/v1/users/", json=sample_user_data)
    assert response.status_code == 409


def test_get_all_users(client, sample_user_data):
    """Test listing all users."""
    # Create two users
    client.post("/v1/users/", json=sample_user_data)
    second_user = sample_user_data.copy()
    second_user["keycloak_id"] = "kc-test-user-002"
    second_user["email"] = "test2@example.com"
    client.post("/v1/users/", json=second_user)

    response = client.get("/v1/users/")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_get_user_by_id(client, sample_user_data):
    """Test fetching a single user by their UUID."""
    create_response = client.post("/v1/users/", json=sample_user_data)
    user_id = create_response.json()["id"]

    response = client.get(f"/v1/users/{user_id}")
    assert response.status_code == 200
    assert response.json()["email"] == sample_user_data["email"]


def test_get_user_not_found(client):
    """Test that fetching a non-existent user returns 404."""
    fake_id = "00000000-0000-0000-0000-000000000000"
    response = client.get(f"/v1/users/{fake_id}")
    assert response.status_code == 404


def test_get_user_by_keycloak_id(client, sample_user_data):
    """Test fetching a user by their Keycloak ID (the most common lookup)."""
    client.post("/v1/users/", json=sample_user_data)

    response = client.get(f"/v1/users/keycloak/{sample_user_data['keycloak_id']}")
    assert response.status_code == 200
    assert response.json()["email"] == sample_user_data["email"]


def test_update_user(client, sample_user_data):
    """Test updating a user's profile (partial update)."""
    create_response = client.post("/v1/users/", json=sample_user_data)
    user_id = create_response.json()["id"]

    # Only update the phone number — other fields should stay the same
    update_data = {"phone": "+45 87654321"}
    response = client.put(f"/v1/users/{user_id}", json=update_data)

    assert response.status_code == 200
    assert response.json()["phone"] == "+45 87654321"
    # Verify other fields weren't changed
    assert response.json()["full_name"] == sample_user_data["full_name"]


def test_delete_user(client, sample_user_data):
    """Test deleting a user profile."""
    create_response = client.post("/v1/users/", json=sample_user_data)
    user_id = create_response.json()["id"]

    # Delete the user
    delete_response = client.delete(f"/v1/users/{user_id}")
    assert delete_response.status_code == 204

    # Verify the user is gone
    get_response = client.get(f"/v1/users/{user_id}")
    assert get_response.status_code == 404
