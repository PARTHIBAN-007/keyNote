import uuid
from typing import Optional, List,Dict,Any,TypedDict
from sqlalchemy.orm import Session
from sqlalchemy import Select , func, text , desc

from loguru import logger
from src.models.events import EventChunk


class SearchResult(TypedDict):
    chunk_id: str
    event_id: str
    text: str
    score: float
    source: str  
    metadata: Dict[str, Any]


class PostgresVectorClient:
    def __init__(self,session:Session):
        self.session = session
        self.ts_config = "english"

    def search_bm25(
            self,
            query: str,
            size: int = 10,
            event_ids: Optional[List[uuid.UUID]] = None
    ):
        """Search the chunk using text search"""
        try:
            ts_query = func.websearch_to_tsquery(self.ts_config,query)

            match_vector = func.to_tsvector(self.ts_config,EventChunk.search_text)
            rank_score = func.ts_rank_cd(match_vector,ts_query).label("score")

            stmt = (
                Select(EventChunk,rank_score)
                .where(match_vector.op("@@")(ts_query))
                .order_by(desc(rank_score))
                .limit(size)
            )

            if event_ids:
                stmt = stmt.where(EventChunk.event_id.in_(event_ids))
            
            rows = self.session.execute(stmt).all()

            return [
                {
                    "chunk_id": str(row.EventChunk.id),
                    "event_id": str(row.EventChunk.event_id),
                    "text": row.EventChunk.raw_text,
                    "score": float(row.score),
                    "source": "bm25",
                    "metadata": row.EventChunk.chunk_metadata
                }
                for row in rows
            ]
        
        except Exception as e:
            logger.error(f"BM25 search failed: {e}")
            return []
        
    def search_vector(
            self,
            query_embedding: List[float],
            size: int = 10,
            event_ids: Optional[List[uuid.UUID]] = None
    ):
        try:
            distance = EventChunk.embedding.cosine_distance(query_embedding)
            similarity = (1-distance).label("score")

            stmt = (
                Select(EventChunk,similarity)
                .order_by(distance)
                .limit(size)
            )

            if event_ids:
                stmt = stmt.where(EventChunk.event_id.in_(event_ids))

            rows = self.session.execute(stmt).all()

            return [
                {
                    "chunk_id": str(row.EventChunk.id),
                    "event_id": str(row.EventChunk.event_id),
                    "text": row.EventChunk.raw_text,
                    "score": float(row.score),
                    "source": "vector",
                    "metadata": row.EventChunk.chunk_metadata
                }
                for row in rows
            ]
        except Exception as e:
            logger.error(f"Vector Search failed: {e}")
            return []

    def search_hybrid(
            self,
            query: str,
            query_embedding: List[float],
            size: int = 10,
            event_ids: Optional[List[uuid.UUID]] = None,
            k: int = 60,
            candidate_multiplier: int = 3
    ):
        candidate_limit = size*candidate_multiplier

        bm25_hits = self.search_bm25(query,size = candidate_limit,event_ids=event_ids)
        vector_hits = self.search_vector(query_embedding,size = candidate_limit,event_ids=event_ids)

        rrf_scores: Dict[str,float] = {}
        result_map: Dict[str,SearchResult] = {}

        def process_hits(hits: List[SearchResult]):
            for rank,hit in enumerate(hits):
                cid = hit["chunk_id"]

                if cid not in result_map:
                    result_map[cid] = hit
                
                rrf_scores[cid] = rrf_scores.get(cid,0.0) + (1.0/(k+rank+1))

        process_hits(bm25_hits)
        process_hits(vector_hits)


        sorted_ids = sorted(rrf_scores.items(), key = lambda item: item[1],reverse= True)

        final_results : List[SearchResult] = []

        for cid,score in sorted_ids[:size]:
            item = result_map[cid]
            final_results.append({
                "chunk_id": cid,
                "event_id": item["event_id"],
                "text": item["text"],
                "score": score,
                "source": "hybrid",
                "metadata":  item["metadata"],
            })

        return final_results
    
        




