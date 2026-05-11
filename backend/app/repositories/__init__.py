"""Store repositories for easy access"""

from app.repositories.user import UserRepository
from app.repositories.transaction import TransactionRepository

__all__ = ["UserRepository", "TransactionRepository"]