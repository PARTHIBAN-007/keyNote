from loguru import logger
from typing import Dict,List


from src.services.embeddings.jina_client import JinaEmbeddingsClient
from src.services.indexing.chunking import EventTextChunker

class HybridIndexingService:
    """Service for indexing event details with chuning and embeddings for hybrid search"""

    def __init__(self,chunker: EventTextChunker,embeddings_client: JinaEmbeddingsClient):
        """Initialize Hybrid Indexing Service
        
        :param chunker: Text Chunking Service
        :param embeddings_client: Embeddings Client for embedding the event
        """
        self.chunker = chunker
        self.embedding_service = embeddings_client
        logger.info("Indexing service is initialized")

    async def index_events(self,event_data:Dict)->Dict[str,int]:
        """Index a single events with indexing and embeddings"""
        event_id = event_data.get("event_id")
        if not event_id:
            logger.error("Missing Event ID")
            return {
                "chunks_created":0,
                "chunks_indexed":0,
                "embeddings_generated": 0,
                "errors":1
            }

        try:
            chunks = self.chunker.chunk_event(
                event_name = event_data.get("event_name",""),
                event_id = event_data.get("event_id",""),
                event_organizer = event_data.get("event_organizer",""),
                event_chief_guest = event_data.get("chief_guest"),
                event_venue = event_data.get("venue",""),
                transcription = event_data.get("transcription","")
            )

            if not chunks:
                logger.warning(f"No chunks created for event :{event_data.get("event_name")}")
                return {
                    "chunks_created": 0,
                    "chunks_indexed": 0,
                    "embeddings_generated": 0,
                    "errors":0
                }
            
            logger.info(f"Created {len(chunks)} chunks for event {event_data.get("event_name")}")

            chunk_texts = [chunk.text for chunk in chunks]
            embeddings = await self.embedding_service.embed_passage(
                texts = chunk_texts,
                batch_size= 50
            )

            if len(embeddings)!=len(chunks):
                logger.error(f"Embeddings Count Mismatch : {len(embeddings)} != {len(chunks)}")
                return {
                    "chunks_created": len(chunks),
                    "chunks_indexed": 0,
                    "embeddings_generated": len(embeddings),
                    "errors": 1
                }
            
            chunks_with_embeddings = []

            for chunk, embedding in zip(chunks,embeddings):
                chunk_data = {
                    "event_id": chunk.event_id,
                    "event_name": chunk.metadata.event_name,

                }

        except Exception as e:
            logger.error(f"Error Indexing event {event_data.get("event_name","")} event_id: {event_id}")
            return {
                "chunks_created": 0,
                "chunks_indexed": 0,
                "embeddings_generated": 0,
                "errors":0
            }
                
    
