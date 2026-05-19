"""Pydantic schemas use for user requests and responses"""

from pydantic import BaseModel, EmailStr, Field, field_validator

import re

def _validate_password_strength(value: str) -> str:
    """Password rules validator"""
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
    totp_enabled: bool = False

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

class UserUpdate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr

class PasswordChange(BaseModel):
    """Change password from the settings page"""

    current_password: str
    new_password: str = Field(min_length=8)

    @field_validator("new_password")
    @classmethod
    def check_password(cls, value: str) -> str:
        return _validate_password_strength(value)

class AccountDelete(BaseModel):
    """Confirm account deletion by asking email and password"""
    email: EmailStr
    password: str

class TFASetupResponse(BaseModel):
    """Returned when the user starts 2FA setup"""
    secret: str
    qr_data_url: str

class TFAEnableRequest(BaseModel):
    """Confirm the 6-digit code from the auth app"""
    code: str = Field(min_length=6, max_length=6)

class TFAEnableResponse(BaseModel):
    """After enabling 2FA, return the one-time recovery codes"""
    recovery_codes: list[str]

class TFADisableRequest(BaseModel):
    """Disable 2FA"""
    password: str
    code: str = Field(min_length=6, max_length=6)

class TFAChallengeResponse(BaseModel):
    """Sent by login when 2FA is on"""
    requires_2fa: bool = True
    challenge_token: str


class TFALoginRequest(BaseModel):
    """2nd login step with challenge token and 6-digit code"""
    challenge_token: str
    code: str