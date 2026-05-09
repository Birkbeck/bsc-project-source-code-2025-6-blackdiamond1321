# FinTrack. Personal Expense Tracker

A personal expense tracker where users record income and expenses manually across multiple sources (cash, debit or 
credit cards) without linking real bank accounts. The system produces financial summaries and exports them as PDF 
reports.

## Tech stack

- **Backend** - Python 3.14, FastAPI, SQLAlchemy, MySQL, Pydantic
- **Frontend** - JavaScript, HTML, CSS
- **Auth** - argon2id password hashing, JWT sessions, 2FA
- **Tests** - pytest with in-memory SQLite for fast test runs

## Setup

1. Install and start MySQL:

 **MacOS:**

```zsh
   brew install mysql
   brew services start mysql
   mysql_secure_installation
   ```
 **Windows:** download and run the MySQL Installer from https://dev.mysql.com/downloads/installer/

2. Copy the environment template and fill in your MySQL password:

```zsh
cp .env.example .env
```

3. Apply the database schema:

```zsh
uv run python database/migrate.py
```
This runs database/schema.sql via pymysql.

## Run
```zsh
uv run uvicorn main:app --app-dir backend --reload
```

