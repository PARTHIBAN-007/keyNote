from typing import List
from loguru import logger
import httpx

from src.schemas.embeddings.jina import JinaEmbeddingRequest,JinaEmbeddingResponse

class JinaEmbeddingsClient:
    def __init__(self,api_key:str,base_url:str = "https://api.jina.ai/v1"):
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        self.client = httpx.AsyncClient(timeout=30.0)
        logger.info("Jina Embeddings Client is initialized")

    async def embed_passage(self,texts: List[str],batch_size: int = 600)->List[List[float]]:
        """
        Embed the passage using jina embeddings
        :params texts: List of text passage to embed
        :params batch_size: Number of texts to process for each API Call.
        :returns: List of Embedding vectors
        """

        embeddings = []

        for i in range(0,len(texts),batch_size):
            batch = texts[i:i+batch_size]

            request_data = JinaEmbeddingRequest(
                model = "jina-embeddings-v3",
                task="retrieval.passage",
                dimensions= 1024,
                input = batch
            )

            try:
                response = await self.client.post(
                    f"{self.base_url}/embeddings",
                    headers = self.headers,
                    json = request_data.model_dump()
                )

                response.raise_for_status()
                print(response)


                result = JinaEmbeddingResponse(**response.json())
                print(result)
                batch_embeddings = [item["embedding"] for item in result.data]
                embeddings.extend(batch_embeddings)

                logger.debug(f"Embedding batch of {len(batch)} passages")
            except httpx.HTTPError as e:
                logger.error(f"Error Embedding passages: {e}")
                raise
            except Exception as e:
                logger.error(f"Unexpected error in embed_passages: {e}")
                raise

        logger.info(f"Successfullt embedded {len(texts)} passages")
        return embeddings
    
    async def embed_query(self,query:str)-> List[float]:
        """
        Embed the User Query using Jina Embeddings
        
        :param query Query text to embed
        :returns Embedding vector of the query
        """

        request_data = JinaEmbeddingRequest(
            model = "jina-embeddings-v3",
            task = "retrieval.query",
            dimensions= 1024,
            input = [query]
        )

        try:
            response = await self.client.post(f"{self.base_url}/embeddings",headers = self.headers,json = request_data.model_dump())
            response.raise_for_status()

            result = JinaEmbeddingResponse(**response.json())
            embedding = result.data[0]["embedding"]

            logger.debug(f"Embedded query: {query[:50]}")
            return embedding
        
        except httpx.HTTPError as e:
            logger.error(f"Error Embedding query: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in embed_query: {e}")
            raise

    async def close(self):
        """Close the HTTP Client"""
        await self.client.sclose()

    async def __aenter__(self):
        """Async Context Manager entry"""
        return self
    
    async def __aexit__(self):
        """Async context manager exit"""
        await self.close()

