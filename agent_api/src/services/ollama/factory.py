from functools import lru_cache

from src.config import get_settings
from src.services.ollama.client import OllamClient

@lru_cache(maxsize=1)
def get_ollama_client():
    """Get ollam Client"""

    settings = get_settings()
    return OllamClient(settings)