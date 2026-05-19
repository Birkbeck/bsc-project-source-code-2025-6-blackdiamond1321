"""Tests for the investment calculator endpoint"""


VALID_USER = {
    "email": "john@example.com",
    "password": "Qwerty123!",
    "first_name": "John",
    "last_name": "Smith",
    "security_question": "Pet name?",
    "security_answer": "John",
}


def register_and_login(client):
    """Register and login  user"""
    client.post("/api/users/register", json=VALID_USER)
    response = client.post(
        "/api/users/login",
        data={"username": VALID_USER["email"], "password": VALID_USER["password"]},
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def project(client, headers, **overrides):
    """Default values"""
    body = {
        "principal": 1000,
        "monthly_contribution": 100,
        "annual_rate_pct": 7,
        "years": 10,
    }
    body.update(overrides)
    return client.post("/api/calculator", json=body, headers=headers)


def test_invested_equals_principal_plus_contributions(client):
    """total_invested = principal + (monthly * months)"""
    headers = register_and_login(client)
    response = project(client, headers, principal=1000, monthly_contribution=100, years=10)
    data = response.json()
    # 1000 + (100 * 120) = 13000
    assert data["total_invested"] == 13000


def test_zero_principal(client):
    """Only monthly contributions"""
    headers = register_and_login(client)
    response = project(client, headers, principal=0)
    assert response.status_code == 200
    data = response.json()
    # 100 * 120 = 12000 contributed
    assert data["total_invested"] == 12000
    assert data["total_balance"] > 12000


def test_zero_monthly_contribution(client):
    """Just compound the initial principal"""
    headers = register_and_login(client)
    response = project(client, headers, monthly_contribution=0)
    assert response.status_code == 200
    data = response.json()
    assert data["total_invested"] == 1000
    assert data["total_balance"] > 1000

def test_zero_interest_rate(client):
    """Balance equals contributions exactly if interest 0"""
    headers = register_and_login(client)
    response = project(client, headers, annual_rate_pct=0)
    data = response.json()
    assert data["total_balance"] == data["total_invested"]
    assert data["total_interest"] == 0

def test_max_years(client):
    """Upper bound: 30 years * 12 months = 360 entities"""
    headers = register_and_login(client)
    response = project(client, headers, years=30)
    assert response.status_code == 200
    assert len(response.json()["months"]) == 360


def test_rejects_zero_years(client):
    """Years must be at least 1"""
    headers = register_and_login(client)
    response = project(client, headers, years=0)
    assert response.status_code == 422


def test_rejects_years_over_max(client):
    """Years cannot exceed 30"""
    headers = register_and_login(client)
    response = project(client, headers, years=100)
    assert response.status_code == 422


def test_rejects_negative_principal(client):
    """Principal must be more than 0"""
    headers = register_and_login(client)
    response = project(client, headers, principal=-1)
    assert response.status_code == 422


def test_rejects_rate_over_100(client):
    """100% is max"""
    headers = register_and_login(client)
    response = project(client, headers, annual_rate_pct=150)
    assert response.status_code == 422
