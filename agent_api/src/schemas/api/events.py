from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class EventBase(BaseModel):
    event_name: str
    organizer: str
    chief_guest_name: Optional[str] = None
    start_time: datetime
    end_time: datetime
    transcription: Optional[str] = None

class EventCreate(EventBase):
    pass

class EventResponse(EventBase):
    id: int

    class Config:
        from_attributes = True 