"""HTTP endpoints for monthly summary"""

from fastapi import APIRouter, Depends

from app.core.dependencies import get_current_user, get_summary_service
from app.models import User
from app.schemas import MonthlySummary
from app.services import SummaryService

router = APIRouter(prefix="/api/summary", tags=["summary"])


@router.get("/{year}/{month}", response_model=MonthlySummary)
def get_monthly_summary(
    year: int,
    month: int,
    service: SummaryService = Depends(get_summary_service),
    user: User = Depends(get_current_user),
) -> MonthlySummary:
    """Get totals and category breakdown"""
    return service.monthly_summary(user, year, month)