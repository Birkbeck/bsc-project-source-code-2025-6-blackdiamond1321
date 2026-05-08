"""SQLAlchemy engine, session factory and declarative Base class"""

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import settings

# 1 engine for the whole process. It manages a connection pool
engine = create_engine(settings.database_url)


# Session factory bound to the engine. Calling SessionLocal() returns a fresh Session
# Each request gets its own via get_db()
SessionLocal = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    """Parent class for every ORM model"""
    pass


def get_db():
    """FastAPI dependency that yields a session and closes it once it finishes"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """Create every table that has a model class"""

    # Base.metadata contains all the models that subclassed Base
    Base.metadata.create_all(bind=engine)