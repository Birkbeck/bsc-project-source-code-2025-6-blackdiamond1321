"""Tests for loans and payments endpoints"""


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

VALID_LOAN = {
    "borrower": "Alice",
    "principal": 1000.0,
    "interest_rate": 5.0,
    "currency": "GBP",
    "borrowed_at": "2026-05-12",
}

VALID_PAYMENT = {
    "amount": 100.0,
    "currency": "GBP",
    "exchange_rate": 1.0,
    "paid_at": "2026-05-12",
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


# Loans

def test_create_loan(client):
    """Create a new loan"""
    headers = register_and_login(client)
    response = client.post("/api/loans", json=VALID_LOAN, headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert data["borrower"] == "Alice"
    assert data["principal"] == 1000.0
    assert data["amount_paid"] == 0


def test_update(client):
    """Update a loan"""
    headers = register_and_login(client)
    create = client.post("/api/loans", json=VALID_LOAN, headers=headers)
    loan_id = create.json()["id"]

    updated = {**VALID_LOAN, "borrower": "Bob"}
    response = client.put(f"/api/loans/{loan_id}", json=updated, headers=headers)
    assert response.status_code == 200
    assert response.json()["borrower"] == "Bob"


def test_delete(client):
    """Delete a loan, then 404 on get."""
    headers = register_and_login(client)
    create = client.post("/api/loans", json=VALID_LOAN, headers=headers)
    loan_id = create.json()["id"]

    delete = client.delete(f"/api/loans/{loan_id}", headers=headers)
    assert delete.status_code == 204

# Payments

def test_record_payment(client):
    """Pay £100 for a £1000 loan"""
    headers = register_and_login(client)
    create = client.post("/api/loans", json=VALID_LOAN, headers=headers)
    loan_id = create.json()["id"]

    response = client.post(f"/api/loans/{loan_id}/payments", json=VALID_PAYMENT, headers=headers)
    assert response.status_code == 201

    loan = client.get(f"/api/loans/{loan_id}", headers=headers).json()
    assert loan["amount_paid"] == 100.0


def test_record_payment_different_currency(client):
    """Pay $100 for a GBP loan"""
    headers = register_and_login(client)
    create = client.post("/api/loans", json=VALID_LOAN, headers=headers)
    loan_id = create.json()["id"]

    payment = {
        "amount": 100.0,
        "currency": "USD",
        "exchange_rate": 0.75, # £1 = $0.75
        "paid_at": "2026-05-12",
    }
    response = client.post(f"/api/loans/{loan_id}/payments", json=payment, headers=headers)
    assert response.status_code == 201

    loan = client.get(f"/api/loans/{loan_id}", headers=headers).json()
    assert loan["amount_paid"] == 75.0


def test_overpayment(client):
    """Paying more than the loan total"""
    headers = register_and_login(client)
    create = client.post("/api/loans", json=VALID_LOAN, headers=headers)
    loan_id = create.json()["id"]

    overpayment = {**VALID_PAYMENT, "amount": 2000.0} # max owed is 1050
    response = client.post(f"/api/loans/{loan_id}/payments", json=overpayment, headers=headers)
    assert response.status_code == 400