"""Store services for easy access"""

from app.services.user import EmailExistsError, UserService

__all__ = ["UserService", "EmailExistsError"]