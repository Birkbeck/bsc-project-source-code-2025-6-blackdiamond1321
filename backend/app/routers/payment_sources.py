"""HTTP endpoints for payment source operations"""

from fastapi import APIRouter, Depends, status

from app.core.dependencies import get_current_user, get_payment_source_service
from app.models import User
from app.schemas import PaymentSourceCreate, PaymentSourceResponse
from app.services import PaymentSourceService

router = APIRouter(prefix="/api/payment-sources", tags=["payment-sources"])


@router.post(
    "",
    response_model=PaymentSourceResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_source(
    data: PaymentSourceCreate,
    service: PaymentSourceService = Depends(get_payment_source_service),
    user: User = Depends(get_current_user),
) -> PaymentSourceResponse:
    """Create a new payment source"""
    return service.create(user, data)


@router.get("", response_model=list[PaymentSourceResponse])
def list_sources(
    service: PaymentSourceService = Depends(get_payment_source_service),
    user: User = Depends(get_current_user),
) -> list[PaymentSourceResponse]:
    """Get all payment sources"""
    return service.list_for_user(user)


@router.delete("/{source_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_source(
    source_id: int,
    service: PaymentSourceService = Depends(get_payment_source_service),
    user: User = Depends(get_current_user),
) -> None:
    """Delete a method"""
    service.delete(user, source_id)

@router.put("/{source_id}", response_model=PaymentSourceResponse)
def update_source(
    source_id: int,
    data: PaymentSourceCreate,
    service: PaymentSourceService = Depends(get_payment_source_service),
    user: User = Depends(get_current_user),
) -> PaymentSourceResponse:
    """Rename a method"""
    return service.update(user, source_id, data)