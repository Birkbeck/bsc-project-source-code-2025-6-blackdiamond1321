# FinTrack — Personal Expense Tracker

A privacy-focused personal-finance web application where users record income and expenses manually across multiple sources (cash, debit and credit cards) without linking real bank accounts. The system produces monthly category budgets, tracks informal loans, generates financial summaries and exports them as PDF reports.

> Final-year project for the BSc Computing degree at Birkbeck, University of London.

---


## Features

- **Transactions** — record income and expenses with description, amount, category, payment method and date. Edit, delete and filter by date range, category or payment method.
- **Custom payment methods** — define your own list (e.g. "HSBC Current", "Cash", "Crypto") instead of choosing from a fixed dropdown.
- **Monthly budgets** — set per-category spending limits with a colour-coded progress bar that shifts from green to amber to red as the limit is approached and exceeded.
- **Loans** — record money lent to or borrowed from third parties, with partial repayments and multi-currency support.
- **Overview dashboard** — at-a-glance stat cards, six-month income vs expense chart, cumulative savings line and a recent-activity list.
- **Summary reports** — totals, per-category donut, per-payment-method breakdown and daily-spending line for any date range, downloadable as a PDF that mirrors the on-screen layout.
- **Investment calculator** — projects compound growth for a regular savings plan.
- **Live market data** — selected stock and cryptocurrency prices from Yahoo Finance, cached in memory.
- **Two-factor authentication** — TOTP via Google Authenticator (or any compatible app), with one-time recovery codes.
- **Password recovery** — answer a personal security question set at registration.

---

## Tech stack

| Layer | Technology |
|---|---|
| Backend language | Python 3.14 |
| Backend framework | FastAPI with Pydantic v2 for validation |
| ORM | SQLAlchemy 2.0 with typed `Mapped` / `mapped_column` |
| Database | MySQL 8.0 via PyMySQL |
| Password hashing | Argon2-CFFI (Argon2id) with a server-side pepper |
| Session tokens | PyJWT (HS256-signed JWTs) |
| Two-factor authentication | pyotp (TOTP) + qrcode / PIL for the QR code |
| PDF reports | ReportLab |
| Market data | yfinance (Yahoo Finance) |
| Frontend | Vanilla JavaScript (ES modules), HTML, CSS — no build step |
| Charts | Chart.js (loaded from CDN as an ES module) |
| Tests | pytest, in-memory SQLite for fast runs |
| Package manager | uv (lockfile-based reproducible installs) |
| Version control | Git with Conventional Commits style |

---

## Project structure

```
fintrack/
├── backend/
│   ├── main.py
│   └── app/
│       ├── core/
│       ├── interfaces/
│       ├── models/
│       ├── repositories/
│       ├── routers/
│       ├── schemas/
│       ├── services/
│       ├── utils/
│       └── database.py
├── frontend/
│   ├── static/
│   │   ├── js/
│   │   └── styles/
│   └── templates/
│       ├── modals/
│       ├── private/
│       ├── public/
│       └── views/
├── database/
│   ├── schema.sql
│   ├── 2fa.sql
│   └── migrate.py
├── tests/                      
├── images/                     
├── pyproject.toml              
├── uv.lock                     
└── README.md
```

---

## rRequisites

- **Python 3.14**
- **MySQL 8.0**
- **uv** package manager — install with:

---

## Setup

### 1. Install and start MySQL

**macOS:**
```zsh
brew install mysql
brew services start mysql
mysql_secure_installation
```

**Windows:** download and run the MySQL Installer from https://dev.mysql.com/downloads/installer/

### 2. Configure environment

Copy the environment template and fill in your MySQL password, a random `SECRET_KEY` for JWT signing, and a random `PEPPER` for password hashing:

```zsh
cp .env.example .env
```

Open `.env` and set the values:

```
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=fintrack
SECRET_KEY=a_long_random_string
PEPPER=another_long_random_string
```

`SECRET_KEY` is used to sign session and challenge JWTs. `PEPPER` is mixed in before Argon2id hashing so a compromised database alone is not enough to mount an offline attack. Both should be long, random and kept secret.

### 3. Install Python dependencies

```zsh
uv sync
```

### 4. Apply the database schema

```zsh
uv run python database/migrate.py
```

This runs `database/schema.sql` (initial schema) followed by `database/2fa.sql` (2FA columns) via PyMySQL.

---

## Running the application

```zsh
uv run uvicorn main:app --app-dir backend --reload
```

The application is then available at **http://localhost:8000**. The landing page is served at `/` and the REST API is mounted under `/api`.

---

## Running the tests

The test suite uses an in-memory SQLite database so it runs in seconds without touching MySQL:

```zsh
uv run pytest
```

For a single module:

```zsh
uv run pytest tests/test_users.py -v
```

---

## API documentation

FastAPI generates an OpenAPI specification and a Swagger UI automatically:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **Raw OpenAPI schema:** http://localhost:8000/openapi.json

Swagger UI was used heavily during development for manual testing — authenticate once and then exercise any endpoint interactively.

---

## Database schema

Six tables, all using the InnoDB engine:

| Table | Purpose |
|---|---|
| `users` | Account credentials, profile, security question, 2FA state |
| `transactions` | Every income or expense entry |
| `budgets` | Per-category monthly spending limits |
| `loans` | Money lent to or borrowed from third parties |
| `payments` | Repayments against a loan (supports multi-currency) |
| `payment_sources` | User-defined payment methods (cash, card names, etc.) |

All child tables carry a `user_id` foreign key so each user's data is fully isolated. Cascade-delete is enabled at the ORM layer, so deleting a user removes all of their data.

---

## Security notes

- **Passwords** are hashed with Argon2id, with the parameters recommended by the OWASP Password Storage Cheat Sheet. A server-side pepper from the `PEPPER` environment variable is applied before hashing, so a compromised database alone is not enough for an offline attack.
- **Session tokens** are HS256-signed JWTs with a one-hour expiry (reduced from 24 hours after the midpoint review).
- **Two-factor authentication** uses TOTP (RFC 6238) with a 30-second window and a single-step clock-drift tolerance.
- **Challenge tokens** issued during the first step of a 2FA login carry a `purpose: 2fa_pending` claim so they cannot be mistaken for full session tokens.
- **Recovery codes** are generated as part of 2FA enrolment and stored as a JSON list; each is single-use.
- **User-data isolation** is enforced at the service layer: every protected endpoint resolves the current user from the JWT and queries only against that user's records.

---
