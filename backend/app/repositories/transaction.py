"""Repository for transaction's operations"""

from app.models import Transaction
from app.repositories.base import BaseRepository


class TransactionRepository(BaseRepository[Transaction]):
    """Read and save transactions in the database"""

    # use Transaction model
    model = Transaction

    def get_for_user(self, transaction_id: int, user_id: int) -> Transaction | None:
        """Get a transaction if transaction belongs to user"""
        return (
            self._db.query(Transaction)
            .filter(Transaction.id == transaction_id, Transaction.user_id == user_id)
            .first()
        )

    def list_for_user(self, user_id: int) -> list[Transaction]:
        """Get all transactions for the user"""
        return (
            self._db.query(Transaction)
            .filter(Transaction.user_id == user_id)
            .all()
        )