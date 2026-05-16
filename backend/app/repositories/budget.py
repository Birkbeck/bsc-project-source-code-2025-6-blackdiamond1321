"""Repository for budgets"""

from app.models import Budget
from app.repositories.base import BaseRepository


class BudgetRepository(BaseRepository[Budget]):
    """Read and save budgets in the database"""

    # use Budget model
    model = Budget

    def find_by_category(self, user_id: int, category: str) -> Budget | None:
        """Find a budget for a specific category"""
        return (
            self._db.query(Budget)
            .filter(Budget.user_id == user_id, Budget.category == category)
            .first()
        )

    def list_for_user(self, user_id: int) -> list[Budget]:
        """Get all budgets for this user"""
        return (
            self._db.query(Budget)
            .filter(Budget.user_id == user_id)
            .order_by(Budget.id)
            .all()
        )