"""Business logic for payment sources"""

from app.models import PaymentSource, User
from app.repositories import PaymentSourceRepository
from app.schemas import PaymentSourceCreate
from app.utils.exceptions import PaymentSourceNotFoundError


class PaymentSourceService:
    """Business logic for payment sources: create, list, delete"""

    def __init__(self, sources: PaymentSourceRepository):
        self._sources = sources

    def create(self, user: User, data: PaymentSourceCreate) -> PaymentSource:
        """Create a new payment method"""
        source = PaymentSource(user_id=user.id, name=data.name)
        return self._sources.add(source)

    def list_for_user(self, user: User) -> list[PaymentSource]:
        """Get all payment methods"""
        return self._sources.list_for_user(user.id)

    def delete(self, user: User, source_id: int) -> None:
        """Delete a payment method"""
        source = self._sources.get_for_user(source_id, user.id)
        if not source:
            raise PaymentSourceNotFoundError()
        self._sources.delete(source)