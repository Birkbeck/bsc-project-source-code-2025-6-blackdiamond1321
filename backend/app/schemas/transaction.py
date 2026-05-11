"""Schemas for transactions"""

from typing import Literal

from pydantic import BaseModel, Field


class TransactionCreate(BaseModel):
    """Create transaction class"""

    # Chose income or expense
    type: Literal["income", "expense"]

    description: str = Field(min_length=1, max_length=255)

    # Amount should not be less than 0
    amount: float = Field(gt=0)

    category: str = Field(min_length=1, max_length=50)
    method: str = Field(min_length=1, max_length=50)

    # Data format: YYYY-MM-DD
    date: str = Field(min_length=10, max_length=10)


class TransactionResponse(BaseModel):
    """Transaction data sent to client"""

    id: int
    type: str
    description: str
    amount: float
    category: str
    method: str
    date: str

    model_config = {"from_attributes": True}