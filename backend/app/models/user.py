"""User ORM model for FinTrack accounts"""

from datetime import datetime, timezone

from sqlalchemy import DateTime, Integer, String

# use Mapped and mapped_column as it shows what type of data each field stores
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class User(Base):
    """User model for FinTrack accounts with fields for email, password, name, security question, answer,
    and creation date"""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    last_name: Mapped[str] = mapped_column(String(50), nullable=False)
    security_question: Mapped[str] = mapped_column(String(255),  nullable=False)
    security_answer: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    # When the user is deleted, delete all their dataa
    transactions = relationship("Transaction", cascade="all, delete-orphan")
    budgets = relationship("Budget", cascade="all, delete-orphan")
    loans = relationship("Loan", cascade="all, delete-orphan")
    payment_sources = relationship("PaymentSource", cascade="all, delete-orphan")