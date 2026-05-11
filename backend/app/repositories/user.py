"""Repository for user's operations"""

from app.models import User
from app.repositories.base import BaseRepository

class UserRepository(BaseRepository[User]):
    """Database actions related to users"""

    # use User as model
    model = User

    def find_by_email(self, email: str) -> User | None:
        """Return a user with the given email if found or None"""

        return (
            self._db.query(User)
            .filter(User.email == email)
            .first()
        )

    def email_taken_by_other(self, email: str, user_id: int) -> bool:
        """Check if another user already uses this email"""
        #  When updating a profile the  user's own email should not count as duplicate
        existing_user = (
            self._db.query(User)
            .filter(
                User.email == email,
                User.id != user_id)
            .first()
        )
        return existing_user is not None