"""Payment ORM model"""

from sqlalchemy import Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Payment(Base):
    """A repayment against a loan"""

    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    loan_id: Mapped[int] = mapped_column(Integer, ForeignKey("loans.id"), nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False) # in payment currency
    currency: Mapped[str] = mapped_column(String(3), nullable=False) # User can choose different currencies
    loan_currency: Mapped[str] = mapped_column(String(3), nullable=False) # loan currency
    exchange_rate: Mapped[float] = mapped_column(Float, default=1.0)
    paid_at: Mapped[str] = mapped_column(String(10), nullable=False) # YYYY-MM-DD