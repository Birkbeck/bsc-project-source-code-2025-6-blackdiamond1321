"""Pydantic schemas for the investment calculator"""

from pydantic import BaseModel, Field


class CalculatorRequest(BaseModel):
    """Inputs for a compound-interest calculator"""
    principal: float = Field(ge=0, le=1_000_000_000)
    monthly_contribution: float = Field(ge=0, le=1_000_000)
    annual_rate_pct: float = Field(ge=0, le=100)
    years: int = Field(ge=1, le=30)


class CalculatorMonth(BaseModel):
    """One month of the projection"""
    month: int
    balance: float
    contributions: float
    interest: float


class CalculatorResponse(BaseModel):
    """Results of the compound-interest calculation"""
    months:  list[CalculatorMonth]
    total_balance:   float
    total_invested:  float
    total_interest:  float