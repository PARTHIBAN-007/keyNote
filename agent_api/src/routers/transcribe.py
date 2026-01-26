from fastapi import APIRouter, UploadFile, File, BackgroundTasks
from dotenv import load_dotenv
from loguru import logger

from src.services.azure.factory import get_transcription_service
router = APIRouter(tags = ["Transcription"])

@router.post("/transcribe")
async def transcribe(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    try:
        transcription_service = get_transcription_service()
        transcription_service.upload_file(file.file, file.filename)
        background_tasks.add_task(transcription_service.run_transcription, file.filename)
        
        return {
            "status": "Accepted", 
            "job_id": file.filename, 
            "message": "Upload successful. Transcription running in background."
        }

    except Exception as e:
        logger.error(f"API Endpoint Error: {str(e)}")
        return {"status": "Error", "message": str(e)}

