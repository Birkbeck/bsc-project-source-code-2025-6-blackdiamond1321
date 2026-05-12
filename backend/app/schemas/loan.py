"""Schemas for loans."""

from pydantic import BaseModel, Field


class LoanCreate(BaseModel):
    """Create a Loan class"""

    borrower: str = Field(min_length=1, max_length=255)
    principal: float = Field(gt=0)
    # interest_rate cannot should not be less than 0
    interest_rate: float = Field(ge=0, default=0)
    currency: str = Field(min_length=3, max_length=3, default="GBP")
    borrowed_at: str = Field(min_length=10, max_length=10)


class LoanResponse(BaseModel):
    """Loan data sent to the client"""

    id: int
    borrower: str
    principal: float
    interest_rate: float
    currency: str
    borrowed_at: str
    paid_at: str
    is_paid: bool
    amount_paid: float

    model_config = {"from_attributes": True}