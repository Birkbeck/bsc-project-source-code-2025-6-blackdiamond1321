# FinTrack. Personal Expense Tracker

A personal expense tracker where users record income and expenses manually across multiple sources (cash, debit or 
credit cards) without linking real bank accounts. The system produces financial summaries and exports them as PDF 
reports.

## Tech stack

- **Backend** - Python 3.14, FastAPI, SQLAlchemy, MySQL, Pydantic
- **Frontend** - JavaScript, HTML, CSS
- **Auth** - argon2id password hashing, JWT sessions, 2FA
- **Tests** - pytest with in-memory SQLite for fast test runs


## Run

```zsh
uv run uvicorn main:app --app-dir backend --reload
```

