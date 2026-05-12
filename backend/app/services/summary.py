"""Business logic for monthly summary"""

from app.models import User
from app.repositories import TransactionRepository
from app.schemas import CategoryBreakdown, MonthlySummary


class SummaryService:
    """Calculate monthly income/expense totals and category breakdowns"""

    def __init__(self, transactions: TransactionRepository):
        self._transactions = transactions

    def monthly_summary(self, user: User, year: int, month: int) -> dict:
        """Get income total, expense total, net saving, and expense breakdown"""
        rows = self._transactions.list_for_user_in_month(user.id, year, month)

        income_total = sum(t.amount for t in rows if t.type == "income")
        expense_total = sum(t.amount for t in rows if t.type == "expense")

        # break down expenses by category
        by_category: dict[str, float] = {}
        for t in rows:
            if t.type == "expense":
                by_category[t.category] = by_category.get(t.category, 0.0) + t.amount

        return MonthlySummary(
            income_total=income_total,
            expense_total=expense_total,
            net=income_total - expense_total,
            by_category=[
                CategoryBreakdown(category=cat, total=total)
                for cat, total in by_category.items()
            ],
        )
