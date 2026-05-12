"""Business logic for loans"""

from app.models import Loan, User
from app.repositories import LoanRepository
from app.schemas import LoanCreate
from app.utils.exceptions import LoanNotFoundError


class LoanService:
    """Business logic loans: create, list, get, update, delete"""

    def __init__(self, loans: LoanRepository):
        self._loans = loans

    def create(self, user: User, data: LoanCreate) -> Loan:
        """Create a new loan"""
        loan = Loan(
            user_id=user.id,
            borrower=data.borrower,
            principal=data.principal,
            interest_rate=data.interest_rate,
            currency=data.currency,
            borrowed_at=data.borrowed_at,
        )
        return self._loans.add(loan)

    def list_for_user(self, user: User) -> list[Loan]:
        """Get all loans for the user"""
        return self._loans.list_for_user(user.id)

    def get_for_user(self, user: User, loan_id: int) -> Loan:
        """Get a loan for the user"""
        loan = self._loans.get_for_user(loan_id, user.id)
        if not loan:
            raise LoanNotFoundError()
        return loan

    def update(self, user: User, loan_id: int, data: LoanCreate) -> Loan:
        """Update a loan"""
        loan = self.get_for_user(user, loan_id)
        loan.borrower = data.borrower
        loan.principal = data.principal
        loan.interest_rate = data.interest_rate
        loan.currency = data.currency
        loan.borrowed_at = data.borrowed_at
        return self._loans.update(loan)

    def delete(self, user: User, loan_id: int) -> None:
        """Delete a loan"""
        loan = self.get_for_user(user, loan_id)
        self._loans.delete(loan)