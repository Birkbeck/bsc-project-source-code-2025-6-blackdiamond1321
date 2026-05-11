"""HTTP endpoints for user account.

Commons codes:
400 Bad Request
401 Unauthorized
403 Forbidden
404 Not Found
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.core.dependencies import get_user_service, get_current_user
from app.schemas import TokenResponse, UserCreate, UserLogin, UserResponse
from app.services import EmailExistsError, UserService, InvalidCredentialsError
from app.models import User

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
    form_data: OAuth2PasswordRequestForm = Depends(),
    service: UserService = Depends(get_user_service),
) -> TokenResponse:
    """Log in with email and password and return a token"""
    try:
        return service.login(UserLogin(
            # In OAuth2 the field is username
            email=form_data.username,
            password=form_data.password,
        ))
    except InvalidCredentialsError as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.get("/me", response_model=UserResponse)
def me(current_user: User = Depends(get_current_user)) -> User:
    """Return the logged-in user's info"""
    return current_user