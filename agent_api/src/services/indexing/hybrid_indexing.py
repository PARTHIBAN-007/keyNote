from loguru import logger
from typing import Dict,List


from src.services.embeddings.jina_client import JinaEmbeddingsClient
from src.services.indexing.chunking import TextChunker

class HybridIndexingService:
    """Service for indexing event details with chuning and embeddings for hybrid search"""

    def __init__(self,chunker: TextChunker,embeddings_client: JinaEmbeddingsClient):
        """Initialize Hybrid Indexing Service
        
        :param chunker: Text Chunking Service
        :param embeddings_client: Embeddings Client for embedding the event
        """
        self.chunker = chunker
        self.embedding_service = embeddings_client

    async def index_events(self,event_data:Dict)->Dict[str,int]:
        """Index a single events with indexing and embeddings"""
        pass 
    
