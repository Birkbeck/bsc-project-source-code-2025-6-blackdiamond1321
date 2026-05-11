"""Tests for /login and /me"""


VALID_REGISTRATION = {
    "email": "john@example.com",
    "password": "Qwerty123!",
    "first_name": "John",
    "last_name": "Smith",
    "security_question": "Pet name?",
    "security_answer": "John",
}


def register_user(client):
    """Create a user via the API"""
    return client.post("/api/users/register", json=VALID_REGISTRATION)


def login_user(client, email="john@example.com", password="Qwerty123!"):
    """Log in via /login """
    return client.post(
        "/api/users/login",
        data={"username": email, "password": password},
    )


# Tests for login

def test_login_success(client):
    """Test if login successfully"""
    register_user(client)
    response = login_user(client)

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == "john@example.com"


def test_login_wrong_password(client):
    """Test login with wrong password"""
    register_user(client)
    response = login_user(client, password="qwerty")
    assert response.status_code == 401


def test_login_wrong_email(client):
    """Test login with wrong email"""
    register_user(client)
    response = login_user(client, email="nobody@example.com")
    assert response.status_code == 401


# Tests for me

def test_me_returns_current_user(client):
    """Test authorized request to /me"""
    register_user(client)
    token = login_user(client).json()["access_token"]

    response = client.get(
        "/api/users/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "john@example.com"
    assert "password_hash" not in data  # sanity: secret never leaked


def test_me_no_token(client):
    """Test request without token"""
    response = client.get("/api/users/me")
    assert response.status_code == 401


def test_me_invalid_token(client):
    """Test request with invalid token"""
    response = client.get(
        "/api/users/me",
        headers={"Authorization": "Bearer invalid-token-value"},
    )
    assert response.status_code == 401