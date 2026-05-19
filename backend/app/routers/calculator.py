"""HTTP endpoint for calculator"""

from fastapi import APIRouter, Depends

from app.core.dependencies import get_calculator_service, get_current_user
from app.models import User
from app.schemas import CalculatorRequest, CalculatorResponse
from app.services import CalculatorService

router = APIRouter(prefix="/api/calculator", tags=["calculator"])


@router.post("", response_model=CalculatorResponse)
def project(
    data: CalculatorRequest,
    service: CalculatorService = Depends(get_calculator_service),
    user: User = Depends(get_current_user),
) -> CalculatorResponse:
    """Compound-interest projection"""
    return service.project(data)