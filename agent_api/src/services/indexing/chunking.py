import re
from typing import List, Union
from uuid import UUID

from loguru import logger
from pydantic import BaseModel

class ChunkMetadata(BaseModel):
    chunk_index:int 
    word_count:int
    event_name:str
    chief_guest: str
    event_organizer:str
    event_venue:str
    overlap_prev:int
    overlap_next:int

class TextChunk(BaseModel):
    event_id: Union[str, UUID]
    text: str
    raw_content: str
    metadata: ChunkMetadata 


class EventTextChunker:
    """Service for chunking Event transcriptions into searchable segments."""

    def __init__(self, chunk_size: int = 500, overlap_size: int = 80, min_chunk_size: int = 50):
        self.chunk_size = chunk_size
        self.overlap_size = overlap_size
        self.min_chunk_size = min_chunk_size

        if overlap_size >= chunk_size:
            raise ValueError("Overlap size must be less than chunk size")

    def _split_into_words(self, text: str) -> List[str]:
        return re.findall(r"\S+", text)
    
    def _create_context_header(self,name: str, guest: str, venue:str)-> str:
        """Creates a string of metadata to prepend to the chunk"""
        return f"Event: {name}. Guest: {guest}. Venue: {venue}. Content: "

    def chunk_event(
            self,
            event_name:str,
            event_id:str,
            event_organizer:str,
            event_chief_guest: str,
            event_venue: str,
            transcription :str
        ) -> List[TextChunk]:
        """
        Processes an Event database record into a list of TextChunks.
        Injects event-specific context (Guest, Venue, Organizer) into every chunk.
        """
        text = transcription
        if not text or not text.strip():
            logger.warning(f"No transcription for event: {event_id}")
            return []


        words = self._split_into_words(text)
        context_header = self._create_context_header(event_name,event_chief_guest,event_venue)
        
        if len(words) < self.min_chunk_size:
            full_text =  " ".join(words)
            return [TextChunk(
                text=f"{context_header}{full_text}",
                event_id=event_id,
                raw_content = full_text,
                metadata=ChunkMetadata(
                    chunk_index=0,
                    word_count=len(words),
                    event_name=event_name,
                    chief_guest = event_chief_guest,
                    event_organizer = event_organizer,
                    event_venue = event_venue,
                    overlap_prev=0,
                    overlap_next=0
                )
            )]

        chunks = []
        chunk_index = 0
        current_pos = 0

        while current_pos < len(words):
            start = current_pos
            end = min(current_pos + self.chunk_size, len(words))
            
            segment_text = " ".join(words[start:end])

            chunk = TextChunk(
                event_id=event_id,
                text=f"{context_header} {segment_text}",
                raw_content= segment_text,
                metadata=ChunkMetadata(
                    chunk_index=chunk_index,
                    word_count=len(words[start:end]),
                    event_name=event_name,
                    chief_guest = event_chief_guest,
                    event_organizer = event_organizer,
                    event_venue = event_venue,
                    overlap_prev=self.overlap_size if start > 0 else 0,
                    overlap_next=self.overlap_size if end < len(words) else 0
                )
            )
            chunks.append(chunk)

            current_pos += (self.chunk_size - self.overlap_size)
            chunk_index += 1
            
            if end >= len(words):
                break

        return chunks
