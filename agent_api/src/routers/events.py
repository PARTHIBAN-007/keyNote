from fastapi import APIRouter
from datetime import datetime
from src.database import get_db_session
from src.models.events import Event
router = APIRouter(
    tags=["events"]
)

import uuid

@router.get("/events/health")
async def health_check():
    return {"status": "events router is healthy"}

from pydantic import BaseModel
from pydantic import ConfigDict

class EventCreate(BaseModel):
    event_name: str
    organizer: str
    chief_guest_name: str
    start_time: datetime
    end_time: datetime
    transcription: str | None = None

class EventResponse(EventCreate):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
from fastapi import APIRouter, HTTPException
from typing import List
from sqlalchemy import select, desc
from src.database import get_db_session
from src.models.events import Event

# 1. GET ALL EVENTS
@router.get("/events/", response_model=List[EventResponse])
async def get_all_events():
    with get_db_session() as session:
        # select(Event) is the SQLAlchemy 2.0 style
        query = select(Event).order_by(Event.created_at.desc())
        result = session.execute(query)
        return result.scalars().all()

# 2. GET RECENT 5 EVENTS
@router.get("/events/recent", response_model=List[EventResponse])
async def get_recent_events():
    with get_db_session() as session:
        query = select(Event).order_by(desc(Event.created_at)).limit(5)
        result = session.execute(query)
        return result.scalars().all()

# 3. CREATE EVENT
@router.post("/events/", response_model=EventResponse)
async def create_event(event_data: EventCreate):
    with get_db_session() as session:
        # Create new Event instance
        new_event = Event(
            event_name=event_data.event_name,
            organizer=event_data.organizer,
            chief_guest_name=event_data.chief_guest_name,
            start_time=event_data.start_time,
            end_time=event_data.end_time,
            transcription=event_data.transcription
        )
        
        session.add(new_event)
        session.commit()
        session.refresh(new_event)
        return new_event

# 4. UPDATE EVENT
@router.put("/events/{event_id}", response_model=EventResponse)
async def update_event(event_id: uuid.UUID, update_data: EventCreate):
    with get_db_session() as session:
        # Find the event first
        event = session.get(Event, event_id)
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")
        
        # Update attributes dynamically
        for key, value in update_data.model_dump().items():
            setattr(event, key, value)
            
        session.commit()
        session.refresh(event)
        return event

# 5. DELETE EVENT
@router.delete("/events/{event_id}")
async def delete_event(event_id: uuid.UUID):
    with get_db_session() as session:
        event = session.get(Event, event_id)
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")
        
        session.delete(event)
        session.commit()
        return {"message": f"Event {event_id} deleted successfully"}

