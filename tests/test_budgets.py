"""Tests for budgets endpoints"""


VALID_USER = {
    "email": "john@example.com",
    "password": "Qwerty123!",
    "first_name": "John",
    "last_name": "Smith",
    "security_question": "Pet name?",
    "security_answer": "John",
}

SECOND_USER = {
    "email": "reborn@example.com",
    "password": "Reborn123!",
    "first_name": "Reborn",
    "last_name": "Smith",
    "security_question": "Pet name?",
    "security_answer": "Reborn",
}

VALID_BUDGET = {
    "category": "food",
    "monthly_limit": 200.0,
}


def register_and_login(client, user=VALID_USER):
    """Register a user and login"""
    client.post("/api/users/register", json=user)
    response = client.post(
        "/api/users/login",
        data={"username": user["email"], "password": user["password"]},
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


# Create

def test_create_budget(client):
    """Authorised user can set a budget"""
    headers = register_and_login(client)
    response = client.post("/api/budgets", json=VALID_BUDGET, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["category"] == "food"
    assert data["monthly_limit"] == 200.0

# Update

def test_update_existing_budget(client):
    """Update existing budgets"""
    headers = register_and_login(client)

    first = client.post("/api/budgets", json=VALID_BUDGET, headers=headers)
    first_id = first.json()["id"]

    second = client.post(
        "/api/budgets",
        json={**VALID_BUDGET, "monthly_limit": 300.0},
        headers=headers,
    )
    assert second.status_code == 200
    assert second.json()["id"] == first_id
    assert second.json()["monthly_limit"] == 300.0


# List

def test_list_budgets(client):
    """List returns the user's budgets"""
    headers = register_and_login(client)
    client.post("/api/budgets", json=VALID_BUDGET, headers=headers)
    client.post(
        "/api/budgets",
        json={"category": "rent", "monthly_limit": 800.0},
        headers=headers,
    )

    response = client.get("/api/budgets", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


    categories = {b["category"] for b in data}
    assert categories == {"food", "rent"}


# Delete

def test_delete_budget(client):
    """Delete a budget"""
    headers = register_and_login(client)
    client.post("/api/budgets", json=VALID_BUDGET, headers=headers)

    delete = client.delete("/api/budgets/food", headers=headers)
    assert delete.status_code == 204

    response = client.get("/api/budgets", headers=headers)
    assert response.json() == []


# Test if a user can delete another user's budget

def test_user_cannot_delete_other_users_budget(client):
    """User cannot access other users budget"""
    user_1 = register_and_login(client)
    client.post("/api/budgets", json=VALID_BUDGET, headers=user_1)

    user_2 = register_and_login(client, SECOND_USER)
    response = client.delete("/api/budgets/food", headers=user_2)
    assert response.status_code == 404

    # Check if
    list_user_1 = client.get("/api/budgets", headers=user_1)
    assert len(list_user_1.json()) == 1