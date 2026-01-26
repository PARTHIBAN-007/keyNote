import os
from .client import AzureTranscriptionClient

def get_transcription_service() -> AzureTranscriptionClient:
    """Factory to create a configured instance of the transcription client."""
    return AzureTranscriptionClient(
        speech_key=os.getenv("AZURE_SPEECH_KEY"),
        speech_region=os.getenv("AZURE_SPEECH_REGION"),
        storage_conn_str=os.getenv("AZURE_STORAGE_CONNECTION_STRING"),
        container_name="audio-blob"
    )