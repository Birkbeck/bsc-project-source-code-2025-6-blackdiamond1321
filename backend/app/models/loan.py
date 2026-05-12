"""Loan ORM model"""

from sqlalchemy import Boolean, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Loan(Base):
    """Money the user has lent to a third part or repaying loans to  third part"""

    __tablename__ = "loans"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    borrower: Mapped[str] = mapped_column(String(255), nullable=False)
    principal: Mapped[float] = mapped_column(Float, nullable=False) # amount lent to the third party
    interest_rate: Mapped[float] = mapped_column(Float, default=0) # percent
    currency: Mapped[str] = mapped_column(String(3), default="GBP")
    borrowed_at: Mapped[str] = mapped_column(String(10), nullable=False) # YYYY-MM-DD
    paid_at: Mapped[str] = mapped_column(String(10), default="") # blank until fully repaid
    is_paid: Mapped[bool] = mapped_column(Boolean, default=False)
    amount_paid: Mapped[float] = mapped_column(Float, default=0)  # in loan currency