"""Store interfaces for easy access"""

from app.interfaces.repository import IRepository
from app.interfaces.password_hasher import IPasswordHasher

__all__ = ["IRepository", "IPasswordHasher"]