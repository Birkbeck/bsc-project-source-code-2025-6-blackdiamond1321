"""Business logic for loan payments"""

from app.models import Payment, User
from app.repositories import LoanRepository, PaymentRepository
from app.schemas import PaymentCreate
from app.utils.exceptions import LoanNotFoundError, OverpaymentError


class PaymentService:
    """Records payments against loans"""

    def __init__(self, loans: LoanRepository, payments: PaymentRepository):
        self._loans = loans
        self._payments = payments

    def record(self, user: User, loan_id: int, data: PaymentCreate) -> Payment:
        """Record a payment against the user's loan"""
        # check the loan exists
        loan = self._loans.get_for_user(loan_id, user.id)
        if not loan:
            raise LoanNotFoundError()

        # payment in different currency. Convert payment currency to loan currency
        amount_in_loan_currency = data.amount * data.exchange_rate

        # total owed = principal + interest
        total_owed = loan.principal * (1 + loan.interest_rate / 100)
        new_total_paid = loan.amount_paid + amount_in_loan_currency

        # do not allow overpayment
        if new_total_paid > total_owed:
            raise OverpaymentError()

        # save the payment
        payment = Payment(
            loan_id=loan.id,
            amount=data.amount,
            currency=data.currency,
            loan_currency=loan.currency,
            exchange_rate=data.exchange_rate,
            paid_at=data.paid_at,
        )
        self._payments.add(payment)

        # update loan totals. If fully paid mark as paid
        loan.amount_paid = new_total_paid
        if new_total_paid >= total_owed:
            loan.is_paid = True
            loan.paid_at = data.paid_at
        self._loans.update(loan)

        return payment

    def list_for_loan(self, user: User, loan_id: int) -> list[Payment]:
        """Get all payments"""
        loan = self._loans.get_for_user(loan_id, user.id)
        if not loan:
            raise LoanNotFoundError()
        return self._payments.list_payments(loan_id)