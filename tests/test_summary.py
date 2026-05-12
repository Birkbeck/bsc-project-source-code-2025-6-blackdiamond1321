"""Tests for monthly summary"""


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
    """Register and login"""
    client.post("/api/users/register", json=user)
    response = client.post(
        "/api/users/login",
        data={"username": user["email"], "password": user["password"]},
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def add_transaction(client, headers, type, amount, category="food", date="2026-05-01"):
    """Create a transaction"""
    return client.post(
        "/api/transactions",
        json={
            "type": type,
            "description": "test",
            "amount": amount,
            "category": category,
            "method": "card",
            "date": date,
        },
        headers=headers,
    )


def test_when_no_transactions(client):
    """No transactions for a month"""
    headers = register_and_login(client)
    response = client.get("/api/summary/2026/05", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["income_total"] == 0
    assert data["expense_total"] == 0
    assert data["net"] == 0
    assert data["by_category"] == []


def test_summary_totals(client):
    """Income and expense totals"""
    headers = register_and_login(client)
    add_transaction(client, headers, "income", 3000.0, "salary")
    add_transaction(client, headers, "expense", 200.0, "food")
    add_transaction(client, headers, "expense", 100.0, "food")

    response = client.get("/api/summary/2026/05", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["income_total"] == 3000.0
    assert data["expense_total"] == 300.0
    assert data["net"] == 2700.0


def test_summary_excludes_other_months(client):
    """List transaction only for a certain month"""
    headers = register_and_login(client)
    add_transaction(client, headers, "income", 100.0, "salary", date="2026-04-30")
    add_transaction(client, headers, "income", 500.0, "salary", date="2026-05-15")
    add_transaction(client, headers, "income", 300.0, "salary", date="2026-06-01")

    response = client.get("/api/summary/2026/05", headers=headers)
    data = response.json()
    assert data["income_total"] == 500.0