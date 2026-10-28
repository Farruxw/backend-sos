"""Baza ulanishi (SQLAlchemy). SQLite yoki PostgreSQL."""
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from .config import DATABASE_URL

_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


def get_db():
    """Har so'rov uchun alohida sessiya beradi va oxirida yopadi."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
