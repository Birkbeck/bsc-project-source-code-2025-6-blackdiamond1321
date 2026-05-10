"""Password hashing"""

from abc import ABC, abstractmethod


class IPasswordHasher(ABC):
    """Interface for password hashing """

    @abstractmethod
    def hash(self, plain: str) -> str:
        """Hash a plaintext password"""

    @abstractmethod
    def verify(self, plain: str, hashed: str) -> bool:
        """If the password matches the hash should return true"""