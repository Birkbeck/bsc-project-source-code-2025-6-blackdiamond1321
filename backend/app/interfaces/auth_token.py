"""Authorisation token"""

from abc import ABC, abstractmethod


class IAuthToken(ABC):
    """Interface for creating and verifying auth tokens"""

    @abstractmethod
    def create_token(self, user_id: int) -> str:
        """Create a session token for the user"""

    @abstractmethod
    def decode_token(self, token: str) -> int | None:
        """Return the user id if the token is valid or None if not valid"""