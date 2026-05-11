"""Business logic for transactions"""

from app.models import Transaction, User
from app.repositories import TransactionRepository
from app.schemas import TransactionCreate
from app.utils.exceptions import TransactionNotFoundError


class TransactionService:
    """Business logic for transactions: create, list, update, delete..."""

    def __init__(self, transactions: TransactionRepository):
        self._transactions = transactions

    def create(self, user: User, data: TransactionCreate) -> Transaction:
        """Create a new transaction for this user"""
        transaction = Transaction(
            user_id=user.id,
            type=data.type,
            description=data.description,
            amount=data.amount,
            category=data.category,
            method=data.method,
            date=data.date,
        )
        return self._transactions.add(transaction)

    def list_for_user(self, user: User) -> list[Transaction]:
        """Get all transactions for this user"""
        return self._transactions.list_for_user(user.id)

    def get_for_user(self, user: User, transaction_id: int) -> Transaction:
        """Get one of the user's transactions"""
        transaction = self._transactions.get_for_user(transaction_id, user.id)
        if not transaction:
            raise TransactionNotFoundError()
        return transaction

    def update(self, user: User, transaction_id: int, data: TransactionCreate) -> Transaction:
        """Update chosen transaction"""
        transaction = self.get_for_user(user, transaction_id)

        transaction.type = data.type
        transaction.description = data.description
        transaction.amount = data.amount
        transaction.category = data.category
        transaction.method = data.method
        transaction.date = data.date
        return self._transactions.update(transaction)

    def delete(self, user: User, transaction_id: int) -> None:
        """Delete chosen transaction"""
        transaction = self.get_for_user(user, transaction_id)
        self._transactions.delete(transaction)