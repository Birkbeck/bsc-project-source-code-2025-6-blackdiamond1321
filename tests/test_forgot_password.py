"""Tests for reset password"""

VALID_REGISTRATION = {
    "email": "john@example.com",
    "password": "Qwerty123!",
    "first_name": "John",
    "last_name": "Smith",
    "security_question": "Pet name?",
    "security_answer": "John",
}


def register_user(client):
    return client.post("/api/users/register", json=VALID_REGISTRATION)


def login_user(client, email="john@example.com", password="Qwerty123!"):
    return client.post(
        "/api/users/login",
        data={"username": email, "password": password},
    )

# reset-password

def test_reset_password_correct_answer(client):
    """Test reset password with correct answer"""
    register_user(client)
    response = client.post(
        "/api/users/reset-password",
        json={
            "email": "john@example.com",
            "answer": "John",
            "new_password": "John123!",
        },
    )
    assert response.status_code == 200

    # Confirm the new password actually works
    new_login = login_user(client, password="John123!")
    assert new_login.status_code == 200

def test_reset_password_answer_with_uppercase(client):
    """Answer comparison ignores case — 'JOHN' matches stored 'John'."""
    register_user(client)
    response = client.post(
        "/api/users/reset-password",
        json={
            "email": "john@example.com",
            "answer": "JOHN",
            "new_password": "NewPass456!",
        },
    )
    assert response.status_code == 200


def test_reset_password_wrong_answer(client):
    """Test reset password with wrong answer"""
    register_user(client)
    response = client.post(
        "/api/users/reset-password",
        json={
            "email": "john@example.com",
            "answer": "Smith",
            "new_password": "John123!",
        },
    )
    assert response.status_code == 400


def test_reset_password_different_email(client):
    """Test reset password with different email"""
    response = client.post(
        "/api/users/reset-password",
        json={
            "email": "smith@example.com",
            "answer": "Smith",
            "new_password": "John123!",
        },
    )
    assert response.status_code == 400