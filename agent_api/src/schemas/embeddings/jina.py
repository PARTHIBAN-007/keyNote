from typing import List, Dict

from pydantic import BaseModel


class JinaEmbeddingRequest(BaseModel):
    """Request model for jina Embeddings request"""

    model: str = "jina-embeddings-v3"
    task: str = "retrieval.passage"
    dimensions: int = 1024
    late_chunking: bool = False
    embedding_type: str = "float"
    input = List[str]

class JinaEmbeddingResponse(BaseModel):
    """Response Model from the Jina Embeddings API"""

    model: str 
    object: str = "List"
    usage: Dict[str,int]
    data: List[Dict]