"""Store repositories for easy access"""

from app.repositories.user import UserRepository
from app.repositories.transaction import TransactionRepository
from app.repositories.budget import BudgetRepository
from app.repositories.loan import LoanRepository
from app.repositories.payment import PaymentRepository

__all__ = ["UserRepository", "TransactionRepository", "BudgetRepository", "LoanRepository", "PaymentRepository"]