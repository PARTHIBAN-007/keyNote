from fastapi import APIRouter, UploadFile, File, BackgroundTasks
from dotenv import load_dotenv
from loguru import logger

from src.services.azure.factory import get_transcription_service
router = APIRouter(tags = ["Transcription"])

@router.post("/transcribe")
async def transcribe(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    try:
        # 1. Get Service Instance
        transcription_service = get_transcription_service()

        # 2. Upload File
        # We pass the file stream directly to the service
        transcription_service.upload_file(file.file, file.filename)
        
        # 3. Add to Background Tasks
        # We pass the class method so it runs asynchronously after the response
        background_tasks.add_task(transcription_service.run_transcription, file.filename)
        
        return {
            "status": "Accepted", 
            "job_id": file.filename, 
            "message": "Upload successful. Transcription running in background."
        }

    except Exception as e:
        logger.error(f"API Endpoint Error: {str(e)}")
        return {"status": "Error", "message": str(e)}

