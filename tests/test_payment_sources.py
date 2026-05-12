"""Tests for payment sources endpoints"""


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


def register_and_login(client, user=VALID_USER):
    """Register and login, return auth headers."""
    client.post("/api/users/register", json=user)
    response = client.post(
        "/api/users/login",
        data={"username": user["email"], "password": user["password"]},
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_create_payment_source(client):
    """Create a payment method"""
    headers = register_and_login(client)
    response = client.post(
        "/api/payment-sources",
        json={"name": "NatWest Debit"},
        headers=headers,
    )
    assert response.status_code == 201
    assert response.json()["name"] == "NatWest Debit"


def test_list_payment_sources(client):
    """List the user's payment sources"""
    headers = register_and_login(client)
    client.post("/api/payment-sources", json={"name": "NatWest"}, headers=headers)
    client.post("/api/payment-sources", json={"name": "Cash"}, headers=headers)

    response = client.get("/api/payment-sources", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    names = {s["name"] for s in data}
    assert names == {"NatWest", "Cash"}


def test_delete_payment_source(client):
    """Delete a payment method"""
    headers = register_and_login(client)
    create = client.post("/api/payment-sources", json={"name": "NatWest"}, headers=headers)
    source_id = create.json()["id"]

    delete = client.delete(f"/api/payment-sources/{source_id}", headers=headers)
    assert delete.status_code == 204

    list_after = client.get("/api/payment-sources", headers=headers)
    assert list_after.json() == []

