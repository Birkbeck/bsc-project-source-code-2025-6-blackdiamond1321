"""Tests for the register endpoint"""


VALID_PAYLOAD = {
    "email": "john@example.com",
    "password": "Qwerty123!",
    "first_name": "John",
    "last_name": "Smith",
    "security_question": "Pet name?",
    "security_answer": "John",
}


def test_register_creates_user(client):
    """Check registration process"""
    response = client.post("/api/users/register", json=VALID_PAYLOAD)
    assert response.status_code == 201

    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == "john@example.com"
    assert data["user"]["first_name"] == "John"


def test_register_rejects_duplicate_email(client):
    """Registering the same email twice"""
    client.post("/api/users/register", json=VALID_PAYLOAD)
    response = client.post("/api/users/register", json=VALID_PAYLOAD)
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]


def test_register_email_format(client):
    """Pydantic rejects invalid email format"""
    payload = {**VALID_PAYLOAD, "email": "test@test"}
    response = client.post("/api/users/register", json=payload)
    assert response.status_code == 422


def test_register_password_length(client):
    """Pydantic rejects password shorter than 8 chars"""
    payload = {**VALID_PAYLOAD, "password": "123"}
    response = client.post("/api/users/register", json=payload)
    assert response.status_code == 422