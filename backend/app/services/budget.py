"""Business logic for budgets"""

from app.models import Budget, User
from app.repositories import BudgetRepository
from app.schemas import BudgetCreate
from app.utils.exceptions import BudgetNotFoundError


class BudgetService:
    """Business logic for budgets: set, list, delete"""

    def __init__(self, budgets: BudgetRepository):
        self._budgets = budgets

    def upsert(self, user: User, data: BudgetCreate) -> Budget:
        """Set a monthly limit for a category"""
        existing = self._budgets.find_by_category(user.id, data.category)

        if existing:
            existing.monthly_limit = data.monthly_limit
            return self._budgets.update(existing)

        budget = Budget(
            user_id=user.id,
            category=data.category,
            monthly_limit=data.monthly_limit,
        )
        return self._budgets.add(budget)

    def list_for_user(self, user: User) -> list[Budget]:
        """Get all budgets for this user."""
        return self._budgets.list_for_user(user.id)

    def delete(self, user: User, category: str) -> None:
        """Delete a budget"""
        budget = self._budgets.find_by_category(user.id, category)
        if not budget:
            raise BudgetNotFoundError()
        self._budgets.delete(budget)