"""Store schemas for easy access"""

from app.schemas.user import TokenResponse, UserCreate, UserResponse, UserLogin, EmailRequest, ForgotPassword
from app.schemas.transaction import TransactionCreate, TransactionResponse
from app.schemas.budget import BudgetCreate, BudgetResponse
from app.schemas.loan import LoanCreate, LoanResponse

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
    "LoanResponse"
]