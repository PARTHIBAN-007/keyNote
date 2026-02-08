import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Text, DateTime, CheckConstraint, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID,VECTOR, JSONB
from src.db.interfaces.postgres import Base 
from sqlalchemy.orm import relationship
from typing import List

from pgvector.sqlalchemy import Vector
def get_utc_now():
    return datetime.now(timezone.utc)

class Event(Base):
    __tablename__ = "event"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_name: Mapped[str] = mapped_column(String, index=True)
    organizer: Mapped[str] = mapped_column(String)
    chief_guest_name: Mapped[str] = mapped_column(String)
    venue: Mapped[str | None] = mapped_column(String) 
    
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=get_utc_now)
    end_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=get_utc_now)
    
    transcription: Mapped[str | None] = mapped_column(Text)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=get_utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=get_utc_now,
        onupdate=get_utc_now
    )

    chunks: Mapped[List["EventChunk"]] = relationship(
        "EventChunk", 
        back_populates="event", 
        cascade="all, delete-orphan" # If you delete Event, delete chunks
    )

    __table_args__ = (
        CheckConstraint('end_time > start_time', name='check_end_after_start'),
    )

class EventChunk(Base):
    __tablename__ = "event_chunk"

    id = Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4)
    event_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        ForeignKey("event.id", ondelete="CASCADE"), 
        nullable=False,
        index=True
    )

    search_text = Mapped[str] = mapped_column(String, nullable=False)
    raw_text = Mapped[str] = mapped_column(String, nullable=False)

    embedding: Mapped[List[float]] = mapped_column(Vector(1536))
    chunk_metadata: Mapped[dict] = mapped_column(JSONB, nullable=False, default={})
    event: Mapped["Event"] = relationship("Event", back_populates="chunks")

    def __repr__(self):
        return f"<EventChunk(id={self.id}, event_id={self.event_id})>"