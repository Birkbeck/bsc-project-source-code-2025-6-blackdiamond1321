"""Repository for payment sources"""

from app.models import PaymentSource
from app.repositories.base import BaseRepository


class PaymentSourceRepository(BaseRepository[PaymentSource]):
    """Read and save payment sources in the database"""

    model = PaymentSource

    def get_for_user(self, source_id: int, user_id: int) -> PaymentSource | None:
        """Get a payment method"""
        return (
            self._db.query(PaymentSource)
            .filter(PaymentSource.id == source_id, PaymentSource.user_id == user_id)
            .first()
        )

    def list_for_user(self, user_id: int) -> list[PaymentSource]:
        """Get all payment methods"""
        return (
            self._db.query(PaymentSource)
            .filter(PaymentSource.user_id == user_id)
            .all()
        )