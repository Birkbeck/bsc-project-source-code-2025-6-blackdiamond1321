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

    @abstractmethod
    def create_challenge_token(self, user_id: int) -> str:
        """Token issued to check 2FA code"""

    @abstractmethod
    def decode_challenge_token(self, token: str) -> int | None:
        """Return user id only if the token is a valid 2FA challenge token"""