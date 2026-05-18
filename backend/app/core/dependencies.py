"""Build services for FastAPI routes"""

from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer

from app.core.config import settings
from app.core.security import Argon2PasswordHasher, JWTAuthToken
from app.database import get_db
from app.repositories import (UserRepository, TransactionRepository, BudgetRepository,
                              LoanRepository, PaymentRepository, PaymentSourceRepository)
from app.services import (UserService, TransactionService, BudgetService, LoanService,
                          PaymentService, SummaryService, PaymentSourceService, PdfService)
from app.models.user import User
from app.interfaces import IAuthToken

# show the Swagger docs where to get a token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/users/login")


def get_auth_token() -> IAuthToken:
    return JWTAuthToken(secret_key=settings.SECRET_KEY)

def get_user_service(db: Session = Depends(get_db)) -> UserService:
    """Build a UserService with its dependencies for a request"""
    return UserService(
        users=UserRepository(db),
        hasher=Argon2PasswordHasher(pepper=settings.PEPPER),
        tokens=get_auth_token(),
    )

def get_transaction_service(db: Session = Depends(get_db)) -> TransactionService:
    """Build a TransactionService"""
    return TransactionService(transactions=TransactionRepository(db))

def get_budget_service(db: Session = Depends(get_db)) -> BudgetService:
    """Build a BudgetService"""
    return BudgetService(budgets=BudgetRepository(db))

def get_loan_service(db: Session = Depends(get_db)) -> LoanService:
    """Build a LoanService"""
    return LoanService(loans=LoanRepository(db))

def get_payment_service(db: Session = Depends(get_db)) -> PaymentService:
    """Build a PaymentService"""
    return PaymentService(
        loans=LoanRepository(db),
        payments=PaymentRepository(db),
    )

def get_summary_service(db: Session = Depends(get_db)) -> SummaryService:
    """Build a SummaryService"""
    return SummaryService(transactions=TransactionRepository(db))

def get_payment_source_service(db: Session = Depends(get_db)) -> PaymentSourceService:
    """Build a PaymentSourceService"""
    return PaymentSourceService(sources=PaymentSourceRepository(db))

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
    tokens: IAuthToken = Depends(get_auth_token),
) -> User:
    """Get the logged-in user from the JWT token"""
    user_id = tokens.decode_token(token)
    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user = UserRepository(db).get(user_id)
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")

    return user

def get_pdf_service() -> PdfService:
    """Build a PdfService"""
    return PdfService()