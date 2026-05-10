"""HTTP endpoints for user account"""

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.dependencies import get_user_service
from app.schemas import TokenResponse, UserCreate
from app.services import EmailExistsError, UserService

router = APIRouter(prefix="/api/users", tags=["users"])


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,

)

def register(
    data: UserCreate,
    service: UserService = Depends(get_user_service),
) -> TokenResponse:
    """Create a new user account and return a session token"""

    try:
        return service.register(data)
    except EmailExistsError as e:
        raise HTTPException(status_code=400, detail=str(e))