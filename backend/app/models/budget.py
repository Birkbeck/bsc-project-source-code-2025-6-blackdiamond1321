"""Budget limit ORM model FinTrack accounts"""

from sqlalchemy import String, Float, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Budget(Base):
    """Monthly spending limit for one category"""

    __tablename__ = "budgets"


    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    monthly_limit: Mapped[float] = mapped_column(Float, nullable=False)