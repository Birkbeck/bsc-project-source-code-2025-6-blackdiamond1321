"""HTTP endpoints for the market page"""

from fastapi import APIRouter, Depends

from app.core.dependencies import get_current_user, get_market_service
from app.models import User
from app.schemas import MarketResponse
from app.services import MarketService

router = APIRouter(prefix="/api/market", tags=["market"])


@router.get("/stocks", response_model=MarketResponse)
def stocks(
    service: MarketService = Depends(get_market_service),
    user: User = Depends(get_current_user),
) -> MarketResponse:
    """Get latest price stock"""
    return service.get_stocks()


@router.get("/crypto", response_model=MarketResponse)
def crypto(
    service: MarketService = Depends(get_market_service),
    user: User = Depends(get_current_user),
) -> MarketResponse:
    """"get latest price crypto"""
    return service.get_crypto()