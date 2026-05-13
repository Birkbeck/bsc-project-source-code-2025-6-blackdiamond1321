"""Pydantic schemas use for user requests and responses"""

from pydantic import BaseModel, EmailStr, Field, field_validator

import re

def _validate_password_strength(value: str) -> str:
    """Backend gatekeeper for password rules. The register modal shows the
    same four checks as a live checklist — keep them in sync if you change
    the rules here."""
    if not re.search(r"[A-Z]", value):
        raise ValueError("Password must contain at least one capital letter")
    if not re.search(r"\d", value):
        raise ValueError("Password must contain at least one digit")
    if not re.search(r"[^a-zA-Z0-9]", value):
        raise ValueError("Password must contain at least one symbol (eg ?!£%)")
    return value

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

    @field_validator("password")
    @classmethod
    def check_password(cls, value: str) -> str:
        return _validate_password_strength(value)


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

class EmailRequest(BaseModel):
    """Take user email to look up the security question"""

    email: EmailStr


class ForgotPassword(BaseModel):
    """Change password via security question"""

    email: EmailStr
    answer: str
    new_password: str = Field(min_length=8)

    @field_validator("new_password")
    @classmethod
    def check_password(cls, value: str) -> str:
        return _validate_password_strength(value)