"""Repository for loans"""

from app.models import Loan
from app.repositories.base import BaseRepository


class LoanRepository(BaseRepository[Loan]):
    """Read and save loans in the database"""

    # use Loan model
    model = Loan

    def get_for_user(self, loan_id: int, user_id: int) -> Loan | None:
        """Get a loan"""
        return (
            self._db.query(Loan)
            .filter(Loan.id == loan_id, Loan.user_id == user_id)
            .first()
        )

    def list_for_user(self, user_id: int) -> list[Loan]:
        """Get all loans for current user"""
        return (
            self._db.query(Loan)
            .filter(Loan.user_id == user_id)
            .all()
        )