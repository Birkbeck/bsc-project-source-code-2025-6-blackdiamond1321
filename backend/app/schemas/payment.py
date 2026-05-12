"""Schemas for loan payments"""

from pydantic import BaseModel, Field


class PaymentCreate(BaseModel):
    """Data needed to record a payment"""

    amount: float = Field(gt=0)
    currency: str = Field(min_length=3, max_length=3)
    exchange_rate: float = Field(gt=0, default=1.0)
    paid_at: str = Field(min_length=10, max_length=10)


class PaymentResponse(BaseModel):
    """Payment data sent to the client"""

    id: int
    loan_id: int
    amount: float
    currency: str
    loan_currency: str
    exchange_rate: float
    paid_at: str

    model_config = {"from_attributes": True}