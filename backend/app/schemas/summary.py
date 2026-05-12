"""Schemas for monthly summary"""

from pydantic import BaseModel


class CategoryBreakdown(BaseModel):
    """Data needed for category breakdown"""

    category: str
    total: float


class MonthlySummary(BaseModel):
    """Monthly income, expense, and category breakdown"""

    income_total: float
    expense_total: float
    net: float
    by_category: list[CategoryBreakdown]