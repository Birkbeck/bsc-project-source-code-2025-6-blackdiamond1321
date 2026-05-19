"""Store schemas for easy access"""

from app.schemas.user import (TokenResponse, UserCreate, UserResponse, UserLogin, EmailRequest,
                              ForgotPassword, UserUpdate, PasswordChange, AccountDelete,
                              TFASetupResponse, TFAEnableResponse,TFAEnableRequest, TFADisableRequest,
                              TFALoginRequest, TFAChallengeResponse)
from app.schemas.transaction import TransactionCreate, TransactionResponse
from app.schemas.budget import BudgetCreate, BudgetResponse
from app.schemas.loan import LoanCreate, LoanResponse
from app.schemas.payment import PaymentCreate, PaymentResponse
from app.schemas.summary import MonthlySummary, CategoryBreakdown
from app.schemas.payment_source import PaymentSourceCreate, PaymentSourceResponse
from app.schemas.calculator import CalculatorRequest, CalculatorResponse, CalculatorMonth

__all__ = [
    "UserCreate",
    "UserResponse",
    "TokenResponse",
    "UserLogin",
    "EmailRequest",
    "ForgotPassword",
    "TransactionCreate",
    "TransactionResponse",
    "BudgetCreate",
    "BudgetResponse",
    "LoanCreate",
    "LoanResponse",
    "PaymentCreate",
    "PaymentResponse",
    "MonthlySummary",
    "CategoryBreakdown",
    "PaymentSourceCreate",
    "PaymentSourceResponse",
    "UserUpdate",
    "PasswordChange",
    "AccountDelete",
    "TFASetupResponse",
    "TFAEnableResponse",
    "TFAEnableRequest",
    "TFADisableRequest",
    "TFALoginRequest",
    "TFAChallengeResponse",
    "CalculatorRequest",
    "CalculatorResponse",
    "CalculatorMonth",
]