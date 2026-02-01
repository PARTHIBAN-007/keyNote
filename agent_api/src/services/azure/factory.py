
from .client import AzureTranscriptionClient


def get_transcription_service() -> AzureTranscriptionClient:
    """Factory to create a configured instance of the transcription client."""
    return AzureTranscriptionClient(
        speech_key=AZURE_SPEECH_KEY,
        speech_region=AZURE_SPEECH_REGION,
        storage_conn_str=AZURE_STORAGE_CONNECTION_STRING,
        container_name="audio-blob"
    )