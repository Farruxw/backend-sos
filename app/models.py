"""Bazadagi jadvallar: Call, Unit, ChatMessage."""
import enum
from datetime import datetime, timezone

from sqlalchemy import DateTime, Enum, Float, String, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


def now() -> datetime:
    return datetime.now(timezone.utc)


class Status(str, enum.Enum):
    NEW = "NEW"
    ENROUTE = "ENROUTE"
    ARRIVED = "ARRIVED"
    DONE = "DONE"
    CANCELLED = "CANCELLED"


class Call(Base):
    """Chaqiruv (SOS)."""
    __tablename__ = "calls"

    id: Mapped[int] = mapped_column(primary_key=True)
    full_name: Mapped[str | None] = mapped_column(String(200))
    phone: Mapped[str | None] = mapped_column(String(30))
    address: Mapped[str | None] = mapped_column(String(300))
    lat: Mapped[float] = mapped_column(Float)
    lng: Mapped[float] = mapped_column(Float)
    accuracy: Mapped[float | None] = mapped_column(Float)
    text: Mapped[str] = mapped_column(Text)
    services: Mapped[str | None] = mapped_column(String(50))      # "103,101"
    severity: Mapped[str | None] = mapped_column(String(10))      # HIGH | MEDIUM | LOW
    ai_summary: Mapped[str | None] = mapped_column(Text)
    status: Mapped[Status] = mapped_column(Enum(Status), default=Status.NEW)
    unit_id: Mapped[int | None] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    arrived_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class Unit(Base):
    """Brigada."""
    __tablename__ = "units"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    service: Mapped[str] = mapped_column(String(3))               # 101..104
    lat: Mapped[float] = mapped_column(Float)
    lng: Mapped[float] = mapped_column(Float)
    busy: Mapped[bool] = mapped_column(Boolean, default=False)
    crew: Mapped[str | None] = mapped_column(String(500))
    plate: Mapped[str | None] = mapped_column(String(20))


class ChatMessage(Base):
    """Mutaxassis chatidagi xabar."""
    __tablename__ = "chat_messages"

    id: Mapped[int] = mapped_column(primary_key=True)
    specialty: Mapped[str] = mapped_column(String(50), index=True)
    sender: Mapped[str] = mapped_column(String(10))               # PATIENT | DOCTOR | AI
    text: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
