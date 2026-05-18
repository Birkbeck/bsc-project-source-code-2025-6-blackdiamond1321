"""HTTP endpoints for user account.

Commons codes:
400 Bad Request
401 Unauthorized
403 Forbidden
404 Not Found
"""

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from app.core.dependencies import get_user_service, get_current_user
from app.schemas import (TokenResponse, UserCreate, UserLogin, UserResponse,
                         EmailRequest, ForgotPassword, UserUpdate, PasswordChange)
from app.services.user import UserService

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
    return service.register(data)

@router.post("/login", response_model=TokenResponse)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    service: UserService = Depends(get_user_service),
) -> TokenResponse:
    """Log in with email and password and return a token"""
    return service.login(UserLogin(
            # In OAuth2 the field is username
            email=form_data.username,
            password=form_data.password,
        ))


@router.get("/me", response_model=UserResponse)
def me(current_user: User = Depends(get_current_user)) -> User:
    """Return the logged-in user's info"""
    return current_user

@router.put("/me", response_model=UserResponse)
def update_profile(
    data: UserUpdate,
    service: UserService = Depends(get_user_service),
    user: User = Depends(get_current_user),
) -> User:
    """Update the user's profile"""
    return service.update_profile(user, data)

@router.post("/forgot-question")
def forgot_question(
    data: EmailRequest,
    service: UserService = Depends(get_user_service),
) -> dict:
    """Return the security question for the email"""
    question = service.get_security_question(data.email)
    return {"question": question}



@router.post("/reset-password")
def reset_password(
    data: ForgotPassword,
    service: UserService = Depends(get_user_service),
) -> dict:
    """Reset password by answering the question"""
    service.reset_password(data.email, data.answer, data.new_password)
    return {"message": "Password reset successfully"}

@router.post("/me/password", status_code=status.HTTP_204_NO_CONTENT)
def change_password(
    data: PasswordChange,
    service: UserService = Depends(get_user_service),
    user: User = Depends(get_current_user),
) -> None:
    """Change the logged-in user's password"""
    service.change_password(user, data.current_password, data.new_password)