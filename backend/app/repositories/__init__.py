"""Store repositories for easy access"""

from app.repositories.user import UserRepository
from app.repositories.transaction import TransactionRepository
from app.repositories.budget import BudgetRepository
from app.repositories.loan import LoanRepository

__all__ = ["UserRepository", "TransactionRepository", "BudgetRepository", "LoanRepository"]