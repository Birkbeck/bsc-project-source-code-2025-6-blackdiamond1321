"""HTTP endpoints for transaction operations"""

from fastapi import APIRouter, Depends, status

from app.core.dependencies import get_current_user, get_transaction_service
from app.models import User
from app.schemas import TransactionCreate, TransactionResponse
from app.services import TransactionService

router = APIRouter(prefix="/api/transactions", tags=["transactions"])


@router.post(
    "",
    response_model=TransactionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_transaction(
    data: TransactionCreate,
    service: TransactionService = Depends(get_transaction_service),
    user: User = Depends(get_current_user),
) -> TransactionResponse:
    """Create a new transaction for user"""
    return service.create(user, data)


@router.get("", response_model=list[TransactionResponse])
def list_transactions(
    service: TransactionService = Depends(get_transaction_service),
    user: User = Depends(get_current_user),
) -> list[TransactionResponse]:
    """Get all transactions for the user"""
    return service.list_for_user(user)


@router.get("/{transaction_id}", response_model=TransactionResponse)
def get_transaction(
    transaction_id: int,
    service: TransactionService = Depends(get_transaction_service),
    user: User = Depends(get_current_user),
) -> TransactionResponse:
    """Get the transaction"""
    return service.get_for_user(user, transaction_id)


@router.put("/{transaction_id}", response_model=TransactionResponse)
def update_transaction(
    transaction_id: int,
    data: TransactionCreate,
    service: TransactionService = Depends(get_transaction_service),
    user: User = Depends(get_current_user),
) -> TransactionResponse:
    """Update the transaction"""
    return service.update(user, transaction_id, data)


@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transaction(
    transaction_id: int,
    service: TransactionService = Depends(get_transaction_service),
    user: User = Depends(get_current_user),
) -> None:
    """Delete a transaction"""
    service.delete(user, transaction_id)