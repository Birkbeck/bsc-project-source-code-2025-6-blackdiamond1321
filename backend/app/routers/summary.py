"""HTTP endpoints for monthly summary"""

from fastapi import APIRouter, Depends
from fastapi.responses import Response

from app.core.dependencies import get_current_user, get_summary_service, get_transaction_service, get_pdf_service
from app.models import User
from app.schemas import MonthlySummary
from app.services import SummaryService, TransactionService, PdfService

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

@router.get("/pdf")
def download_summary_pdf(
    date_from: str = "",
    date_to: str = "",
    transactions: TransactionService = Depends(get_transaction_service),
    pdf: PdfService = Depends(get_pdf_service),
    user: User = Depends(get_current_user),
):
    """Return a PDF summary of the user's transactions in the date range"""
    rows = transactions.list_for_user(user)
    if date_from:
        rows = [t for t in rows if t.date >= date_from]
    if date_to:
        rows = [t for t in rows if t.date <= date_to]

    body = pdf.build_summary(user, rows, date_from, date_to)
    return Response(
        content=body,
        media_type="application/pdf",
        headers={"Content-Disposition": 'attachment; filename="fintrack-summary.pdf"'},
    )