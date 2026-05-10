"""HTTP endpoints for user account.

Commons codes:
400 Bad Request
401 Unauthorized
403 Forbidden
404 Not Found
"""

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.dependencies import get_user_service
from app.schemas import TokenResponse, UserCreate, UserLogin
from app.services import EmailExistsError, UserService, InvalidCredentialsError

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



@router.post("/login", response_model=TokenResponse)
def login(
    data: UserLogin,
    service: UserService = Depends(get_user_service),
) -> TokenResponse:
    """Log in with email and password and return a session token"""
    try:
        return service.login(data)
    except InvalidCredentialsError as e:
        raise HTTPException(status_code=401, detail=str(e))