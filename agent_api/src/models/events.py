import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Text, DateTime, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from src.db.interfaces.postgres import Base 

def get_utc_now():
    return datetime.now(timezone.utc)

class Event(Base):
    __tablename__ = "event"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_name: Mapped[str] = mapped_column(String, index=True)
    organizer: Mapped[str] = mapped_column(String)
    chief_guest_name: Mapped[str] = mapped_column(String)
    
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=get_utc_now)
    end_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=get_utc_now)
    
    transcription: Mapped[str | None] = mapped_column(Text)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=get_utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=get_utc_now,
        onupdate=get_utc_now
    )

    __table_args__ = (
        CheckConstraint('end_time > start_time', name='check_end_after_start'),
    )