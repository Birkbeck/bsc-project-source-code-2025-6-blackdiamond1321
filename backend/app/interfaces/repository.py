"""Base repository interface.
Repositories do communication with the database and provide basic CRUD operations (create,
read, update, delete). Different databases can implement the same interface.
"""

# use abc to implement interface
from abc import ABC, abstractmethod


class IRepository[T](ABC):
    """Abstract class for all repositories"""

    @abstractmethod
    def get(self, entity_id: int) -> T | None:
        """Get one entity by its id"""

    @abstractmethod
    def get_all(self) -> list[T]:
        """Return all entities"""

    @abstractmethod
    def add(self, entity: T) -> T:
        """Add a new entity"""

    @abstractmethod
    def update(self, entity: T) -> T:
        """Update an entity"""

    @abstractmethod
    def delete(self, entity: T) -> None:
        """Delete an entity"""