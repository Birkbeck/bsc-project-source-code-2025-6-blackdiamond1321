"""Tests for transactions endpoints"""


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

VALID_TRANSACTION = {
    "type": "expense",
    "description": "Tesco",
    "amount": 23.50,
    "category": "food",
    "method": "cash",
    "date": "2026-05-14",
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

def test_create_transaction(client):
    """Authorised user can create a transaction"""
    headers = register_and_login(client)
    response = client.post("/api/transactions", json=VALID_TRANSACTION, headers=headers)

    assert response.status_code == 201
    data = response.json()
    assert data["type"] == "expense"
    assert data["amount"] == 23.50
    assert data["description"] == "Tesco"
    assert "id" in data


def test_create_transaction_without_auth(client):
    """Without auth a token, returns 401"""
    response = client.post("/api/transactions", json=VALID_TRANSACTION)
    assert response.status_code == 401



def test_create_transaction_negative_amount(client):
    """Pydantic rejects negative or zero amounts."""
    headers = register_and_login(client)
    payload = {**VALID_TRANSACTION, "amount": -10.0}
    response = client.post("/api/transactions", json=payload, headers=headers)
    assert response.status_code == 422


# List


def test_list_transactions_returns_user_data(client):
    """List returns the user's created transactions"""
    headers = register_and_login(client)

    client.post("/api/transactions", json=VALID_TRANSACTION, headers=headers)
    client.post(
        "/api/transactions",
        json={**VALID_TRANSACTION, "description": "Tea", "amount": 2.0},
        headers=headers,
    )

    response = client.get("/api/transactions", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2

# Get one

def test_get_transaction(client):
    """Get the transaction by id"""
    headers = register_and_login(client)
    create = client.post("/api/transactions", json=VALID_TRANSACTION, headers=headers)
    tx_id = create.json()["id"]

    response = client.get(f"/api/transactions/{tx_id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["description"] == "Tesco"


# Update

def test_update_transaction(client):
    """Update a transaction's fields"""
    headers = register_and_login(client)
    create = client.post("/api/transactions", json=VALID_TRANSACTION, headers=headers)
    tx_id = create.json()["id"]

    updated = {**VALID_TRANSACTION, "description": "ALDI", "amount": 19.30}
    response = client.put(f"/api/transactions/{tx_id}", json=updated, headers=headers)
    assert response.status_code == 200
    assert response.json()["description"] == "ALDI"
    assert response.json()["amount"] == 19.30


# Delete


def test_delete_transaction(client):
    """Delete a transaction. Then try to get a transaction. Should return 404"""
    headers = register_and_login(client)
    create = client.post("/api/transactions", json=VALID_TRANSACTION, headers=headers)
    tx_id = create.json()["id"]

    delete = client.delete(f"/api/transactions/{tx_id}", headers=headers)
    assert delete.status_code == 204

    after = client.get(f"/api/transactions/{tx_id}", headers=headers)
    assert after.status_code == 404


# Test if a user can access another user's transactions


def test_user_cannot_access_other_users_transaction(client):
    """User cannot access other users transaction"""
    user_1 = register_and_login(client, VALID_USER)
    create = client.post("/api/transactions", json=VALID_TRANSACTION, headers=user_1)
    tx_id = create.json()["id"]

    user_2 = register_and_login(client, SECOND_USER)

    assert client.get(f"/api/transactions/{tx_id}", headers=user_2).status_code == 404
    assert client.put(f"/api/transactions/{tx_id}", json=VALID_TRANSACTION, headers=user_2).status_code == 404
    assert client.delete(f"/api/transactions/{tx_id}", headers=user_2).status_code == 404
