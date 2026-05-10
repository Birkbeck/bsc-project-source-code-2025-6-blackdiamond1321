"""Store interfaces for easy access"""

from app.interfaces.repository import IRepository
from app.interfaces.password_hasher import IPasswordHasher
from app.interfaces.auth_token import IAuthToken

__all__ = ["IRepository", "IPasswordHasher", "IAuthToken"]