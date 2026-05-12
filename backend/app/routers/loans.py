"""HTTP endpoints for loan and payment operations"""

from fastapi import APIRouter, Depends, status

from app.core.dependencies import (
    get_current_user,
    get_loan_service,
    get_payment_service,
)
from app.models import User
from app.schemas import LoanCreate, LoanResponse, PaymentCreate, PaymentResponse
from app.services import LoanService, PaymentService

router = APIRouter(prefix="/api/loans", tags=["loans"])


# Loans

@router.post(
    "",
    response_model=LoanResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_loan(
    data: LoanCreate,
    service: LoanService = Depends(get_loan_service),
    user: User = Depends(get_current_user),
) -> LoanResponse:
    """Create a new loan"""
    return service.create(user, data)


@router.get("", response_model=list[LoanResponse])
def list_loans(
    service: LoanService = Depends(get_loan_service),
    user: User = Depends(get_current_user),
) -> list[LoanResponse]:
    """Get all loans"""
    return service.list_for_user(user)


@router.get("/{loan_id}", response_model=LoanResponse)
def get_loan(
    loan_id: int,
    service: LoanService = Depends(get_loan_service),
    user: User = Depends(get_current_user),
) -> LoanResponse:
    """Get a specific loan"""
    return service.get_for_user(user, loan_id)


@router.put("/{loan_id}", response_model=LoanResponse)
def update_loan(
    loan_id: int,
    data: LoanCreate,
    service: LoanService = Depends(get_loan_service),
    user: User = Depends(get_current_user),
) -> LoanResponse:
    """Update a loan"""
    return service.update(user, loan_id, data)


@router.delete("/{loan_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_loan(
    loan_id: int,
    service: LoanService = Depends(get_loan_service),
    user: User = Depends(get_current_user),
) -> None:
    """Delete a loan"""
    service.delete(user, loan_id)


# Payments

@router.post(
    "/{loan_id}/payments",
    response_model=PaymentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_payment(
    loan_id: int,
    data: PaymentCreate,
    service: PaymentService = Depends(get_payment_service),
    user: User = Depends(get_current_user),
) -> PaymentResponse:
    """Record a payment"""
    return service.record(user, loan_id, data)


@router.get("/{loan_id}/payments", response_model=list[PaymentResponse])
def list_payments(
    loan_id: int,
    service: PaymentService = Depends(get_payment_service),
    user: User = Depends(get_current_user),
) -> list[PaymentResponse]:
    """Get all payments made against a loan"""
    return service.list_for_loan(user, loan_id)