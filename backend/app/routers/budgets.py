"""HTTP endpoints for budget operations"""

from fastapi import APIRouter, Depends, status

from app.core.dependencies import get_budget_service, get_current_user
from app.models import User
from app.schemas import BudgetCreate, BudgetResponse
from app.services import BudgetService

router = APIRouter(prefix="/api/budgets", tags=["budgets"])


@router.post("", response_model=BudgetResponse)
def upsert_budget(
    data: BudgetCreate,
    service: BudgetService = Depends(get_budget_service),
    user: User = Depends(get_current_user),
) -> BudgetResponse:
    """Set or update a budget"""
    return service.upsert(user, data)


@router.get("", response_model=list[BudgetResponse])
def list_budgets(
    service: BudgetService = Depends(get_budget_service),
    user: User = Depends(get_current_user),
) -> list[BudgetResponse]:
    """Get all budget limits"""
    return service.list_for_user(user)


@router.delete("/{category}", status_code=status.HTTP_204_NO_CONTENT)
def delete_budget(
    category: str,
    service: BudgetService = Depends(get_budget_service),
    user: User = Depends(get_current_user),
) -> None:
    """Delete a budget"""
    service.delete(user, category)