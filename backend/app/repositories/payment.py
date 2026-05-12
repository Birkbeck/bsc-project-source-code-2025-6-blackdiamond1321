"""Repository for loan payments"""

from app.models import Payment
from app.repositories.base import BaseRepository


class PaymentRepository(BaseRepository[Payment]):
    """Read and save loan payments in the database"""

    model = Payment

    def list_payments(self, loan_id: int) -> list[Payment]:
        """Get all payments made for the loan"""
        return (
            self._db.query(Payment)
            .filter(Payment.loan_id == loan_id)
            .all()
        )