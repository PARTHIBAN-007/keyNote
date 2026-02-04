from typing import Optional

from src.config import Settings,get_settings

from src.services.embeddings.jina_client import JinaEmbeddingsClient

def make_embeddings_client(settings: Optional[Settings] = None)-> JinaEmbeddingsClient:
    """Factory function to create embedding service"""
    if settings is None:
        settings = get_settings()

    api_key = settings.jina_api_key

    return JinaEmbeddingsClient(api_key=api_key)