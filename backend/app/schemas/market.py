"""Schemas for the market page"""

from pydantic import BaseModel


class Quote(BaseModel):
    """Create a base model of stock or crypto entity"""
    symbol: str
    name: str
    price: float
    change_pct: float
    currency: str = "USD"


class MarketResponse(BaseModel):
    """List of quotes"""
    quotes:     list[Quote]
    fetched_at: float
    stale:      bool = False