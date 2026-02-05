import re
from typing import List, Optional
from uuid import UUID

from loguru import logger

from pydantic import BaseModel

class ChunkMetadata(BaseModel):
    chunk_index:int 
    word_count:int
    event_name:str
    overlap_prev:int
    overlap_next:int

class TextChunk(BaseModel):
    event_id: UUID
    text:str
    ChunkMetadata:ChunkMetadata 


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

    def chunk_event(self, event_record) -> List[TextChunk]:
        """
        Processes an Event database record into a list of TextChunks.
        Injects event-specific context (Guest, Venue, Organizer) into every chunk.
        """
        text = event_record.transcription
        if not text or not text.strip():
            logger.warning(f"No transcription for event: {event_record.id}")
            return []


        header = (
            f"Event: {event_record.event_name} | "
            f"Organizer: {event_record.organizer} | "
            f"Guest: {event_record.chief_guest_name}\n"
            f"Venue: {event_record.venue or 'Unknown'}\n"
            f"--- Content ---\n"
        )

        words = self._split_into_words(text)
        
        if len(words) < self.min_chunk_size:
            return [self._create_chunk(header + text, 0, event_record)]

        chunks = []
        chunk_index = 0
        current_pos = 0

        while current_pos < len(words):
            start = current_pos
            end = min(current_pos + self.chunk_size, len(words))
            
            segment_text = " ".join(words[start:end])
            full_chunk_text = f"{header}{segment_text}"

            chunk = TextChunk(
                text=full_chunk_text,
                event_id=event_record.id,
                metadata=ChunkMetadata(
                    chunk_index=chunk_index,
                    word_count=len(words[start:end]),
                    event_name=event_record.event_name,
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

    def _create_chunk(self, text: str, index: int, event) -> TextChunk:
        """Helper for single-chunk creation."""
        return TextChunk(
            text=text,
            event_id=event.id,
            metadata=ChunkMetadata(chunk_index=index, word_count=len(text.split()))
        )