from fastapi import APIRouter, HTTPException, UploadFile, File
from datetime import datetime
from src.database import get_db_session
from src.models.events import Event
from src.services.azure.factory import get_transcription_service
from loguru import logger
import uuid

router = APIRouter(
    tags=["events"]
)

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
    venue: str | None = None
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


# 6. TRANSCRIBE AUDIO AND STORE IN EVENT
@router.post("/events/{event_id}/transcribe")
async def transcribe_and_store_audio(event_id: uuid.UUID, audio_file: UploadFile = File(...)):
    """
    Upload an audio file, transcribe it using Azure Speech Service,
    and store the transcription in the event's transcription field.
    """
    try:
        # 1. Verify event exists
        with get_db_session() as session:
            event = session.get(Event, event_id)
            if not event:
                raise HTTPException(status_code=404, detail="Event not found")
        
        # 2. Validate audio file
        if not audio_file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        allowed_formats = {".mp3", ".wav", ".flac", ".ogg", ".m4a"}
        file_ext = f".{audio_file.filename.split('.')[-1].lower()}"
        if file_ext not in allowed_formats:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid audio format. Allowed: {', '.join(allowed_formats)}"
            )
        
        logger.info(f"Processing transcription for event {event_id}")
        
        # 3. Get Azure transcription service
        transcription_service = get_transcription_service()
        
        # 4. Upload file to Azure Blob Storage
        file_obj = await audio_file.read()
        blob_filename = f"{event_id}_{audio_file.filename}"
        
        # Create BytesIO object for upload
        from io import BytesIO
        file_bytes_io = BytesIO(file_obj)
        
        transcription_service.upload_file(file_bytes_io, blob_filename)
        
        logger.info(f"Audio file uploaded: {blob_filename}")
        
        # 5. Run transcription and get results
        # Note: run_transcription currently saves to file, we'll modify to return text
        transcription = await _get_transcription_result(
            transcription_service, 
            blob_filename
        )
        
        if not transcription:
            raise HTTPException(
                status_code=500, 
                detail="Transcription failed. No text extracted."
            )
        
        # 6. Update event with transcription
        with get_db_session() as session:
            event = session.get(Event, event_id)
            if event:
                event.transcription = transcription
                session.commit()
                session.refresh(event)
                logger.info(f"Event {event_id} transcription stored successfully")
                return {
                    "event_id": event_id,
                    "status": "success",
                    "message": "Audio transcribed and stored successfully",
                    "transcription_length": len(transcription),
                    "transcription_preview": transcription[:200] + "..." if len(transcription) > 200 else transcription
                }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Transcription error for event {event_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500, 
            detail=f"Transcription failed: {str(e)}"
        )


async def _get_transcription_result(transcription_service, blob_name: str) -> str:
    """
    Helper function to run transcription and extract the text result.
    """
    import time
    import requests
    from io import BytesIO
    
    try:
        # Generate SAS URL
        file_url = transcription_service._generate_sas_url(blob_name)
        
        # Submit transcription job
        job_data = {
            "contentUrls": [file_url],
            "displayName": f"Transcription_{blob_name}",
            "locale": "en-US",
            "properties": {
                "wordLevelTimestampsEnabled": True,
                "timeToLiveHours": 1,
                "candidateLocales": ["en-US", "ta-IN"],
            }
        }
        
        headers = {
            "Ocp-Apim-Subscription-Key": transcription_service.speech_key,
            "Content-Type": "application/json"
        }
        
        logger.info(f"Submitting transcription job for {blob_name}...")
        response = transcription_service.session.post(
            f"{transcription_service.base_url}/transcriptions", 
            headers=headers, 
            json=job_data
        )
        
        if response.status_code != 201:
            logger.error(f"Job submission failed: {response.text}")
            return None
        
        job_url = response.json()['self']
        job_id = job_url.split('/')[-1]
        logger.info(f"Job created: {job_id}")
        
        # Poll for completion
        max_polls = 120  # Max 20 minutes with 10s intervals
        polls = 0
        while polls < max_polls:
            time.sleep(10)
            polls += 1
            
            try:
                status_res = transcription_service.session.get(job_url, headers=headers)
                status_data = status_res.json()
                status = status_data['status']
                
                logger.info(f"Job {job_id} status: {status}")
                
                if status == "Succeeded":
                    # Extract transcription text
                    files_url = status_data['links']['files']
                    files_data = transcription_service.session.get(files_url, headers=headers).json()
                    
                    content_url = next(
                        v['links']['contentUrl'] 
                        for v in files_data['values'] 
                        if v['kind'] == 'Transcription'
                    )
                    result_data = transcription_service.session.get(content_url).json()
                    
                    # Extract text from result
                    full_text = ""
                    if 'combinedRecognizedPhrases' in result_data and result_data['combinedRecognizedPhrases']:
                        full_text = result_data['combinedRecognizedPhrases'][0]['display']
                    elif 'combinedPhrases' in result_data and result_data['combinedPhrases']:
                        full_text = result_data['combinedPhrases'][0]['text']
                    elif 'phrases' in result_data:
                        full_text = " ".join([p.get('display', p.get('text', '')) for p in result_data['phrases']])
                    
                    # Cleanup
                    transcription_service._delete_blob(blob_name)
                    
                    logger.info(f"Transcription complete for {blob_name}")
                    return full_text if full_text else None
                    
                elif status == "Failed":
                    err = status_data.get('properties', {}).get('error', 'Unknown error')
                    logger.error(f"Transcription job failed: {err}")
                    transcription_service._delete_blob(blob_name)
                    return None
                    
            except requests.exceptions.ConnectionError:
                logger.warning("Connection lost, retrying...")
                continue
        
        logger.error(f"Transcription job {job_id} timed out")
        return None
        
    except Exception as e:
        logger.error(f"Error in transcription process: {str(e)}", exc_info=True)
        return None

