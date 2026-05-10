"""Build services for FastAPI routes"""

from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import Argon2PasswordHasher, JWTAuthToken
from app.database import get_db
from app.repositories import UserRepository
from app.services import UserService


def get_user_service(db: Session = Depends(get_db)) -> UserService:
    """Build a UserService with its dependencies for a request"""
    return UserService(
        users=UserRepository(db),
        hasher=Argon2PasswordHasher(pepper=settings.PEPPER),
        tokens=JWTAuthToken(secret_key=settings.SECRET_KEY),
    )