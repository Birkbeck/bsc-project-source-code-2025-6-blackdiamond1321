"""Schemas for payment sources"""

from pydantic import BaseModel, Field


class PaymentSourceCreate(BaseModel):
    """Data needed to create a payment method"""

    name: str = Field(min_length=1, max_length=32)


class PaymentSourceResponse(BaseModel):
    """Payment source data sent to the client"""

    id: int
    name: str

    model_config = {"from_attributes": True}