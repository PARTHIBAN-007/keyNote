from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional

class EventBase(BaseModel):
    event_name: str
    organizer: str
    chief_guest_name: str
    start_time: datetime
    end_time: datetime
    transcription: Optional[str] = None

    @field_validator('end_time')
    def check_end_time(cls, v, values):
        if 'start_time' in values.data and v <= values.data['start_time']:
            raise ValueError('end_time must be after start_time')
        return v

class EventCreate(EventBase):
    pass

class EventRead(EventBase):
    id: int

    class Config:
        from_attributes = True

class DashboardSummary(BaseModel):
    upcoming: list[EventRead]
    recent: list[EventRead]
