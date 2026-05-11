"""Schemas for budgets"""

from pydantic import BaseModel, Field


class BudgetCreate(BaseModel):
    """Create budget class"""

    category: str = Field(min_length=1, max_length=50)

    # Monthly limit should not be less than 0
    monthly_limit: float = Field(gt=0)


class BudgetResponse(BaseModel):
    """Budget data sent to the client"""

    id: int
    category: str
    monthly_limit: float

    model_config = {"from_attributes": True}