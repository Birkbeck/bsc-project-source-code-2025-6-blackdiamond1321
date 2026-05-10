"""Pydantic schemas use for user requests and responses"""

from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    """Create user class"""

    # Validate email format automatically
    email: EmailStr

    # Password must contain at least 8 characters
    password: str = Field(min_length=8)

    first_name: str = Field(min_length=1, max_length=50)

    last_name: str = Field(min_length=1, max_length=50)

    # Security question for account recovery
    security_question: str = Field(min_length=1, max_length=255)

    # Answer to the security question
    security_answer: str = Field(min_length=1, max_length=255)


class UserResponse(BaseModel):
    """Public user data returned by the API"""

    id: int
    email: EmailStr
    first_name: str
    last_name: str

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    """Response returned after login or registration"""

    # JWT access token
    access_token: str

    # Authentication type
    token_type: str = "bearer"

    user: UserResponse

class UserLogin(BaseModel):
    """Login form"""

    email: EmailStr
    password: str