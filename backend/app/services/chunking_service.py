import re
from typing import List, Dict, Any, Optional
from app.services.extraction_service import ExtractedSegment
import logging

logger = logging.getLogger("talk_to_your_notes.chunking")


class DocumentChunk:
    def __init__(
        self,
        document_id: str,
        user_id: str,
        chunk_index: int,
        content: str,
        page_number: Optional[int] = None,
        section_title: Optional[str] = None,
        parent_section: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.document_id = document_id
        self.user_id = user_id
        self.chunk_index = chunk_index
        self.content = content.strip()
        self.page_number = page_number
        self.section_title = section_title
        self.parent_section = parent_section
        self.metadata = metadata or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "document_id": self.document_id,
            "user_id": self.user_id,
            "chunk_index": self.chunk_index,
            "content": self.content,
            "page_number": self.page_number,
            "section_title": self.section_title,
            "parent_section": self.parent_section,
            "metadata": self.metadata
        }


class ChunkingService:
    CHARS_PER_TOKEN = 4.0  # Approximator for token estimation

    def __init__(
        self,
        target_tokens: int = 800,
        overlap_tokens: int = 120
    ):
        self.target_chars = int(target_tokens * self.CHARS_PER_TOKEN)
        self.overlap_chars = int(overlap_tokens * self.CHARS_PER_TOKEN)

    def create_chunks(
        self,
        segments: List[ExtractedSegment],
        document_id: str,
        user_id: str,
        source_file: str
    ) -> List[DocumentChunk]:
        chunks: List[DocumentChunk] = []
        chunk_index = 0

        for segment in segments:
            text = segment.content
            if not text:
                continue

            # If segment is within target size, add as a single chunk
            if len(text) <= self.target_chars:
                chunks.append(
                    DocumentChunk(
                        document_id=document_id,
                        user_id=user_id,
                        chunk_index=chunk_index,
                        content=text,
                        page_number=segment.page_number,
                        section_title=segment.section_title,
                        parent_section=segment.parent_section,
                        metadata={
                            "source_file": source_file,
                            "char_length": len(text),
                            "estimated_tokens": int(len(text) / self.CHARS_PER_TOKEN)
                        }
                    )
                )
                chunk_index += 1
            else:
                # Hierarchical paragraph and sentence splitting with overlap
                sub_texts = self._split_large_segment(text)
                for sub_text in sub_texts:
                    chunks.append(
                        DocumentChunk(
                            document_id=document_id,
                            user_id=user_id,
                            chunk_index=chunk_index,
                            content=sub_text,
                            page_number=segment.page_number,
                            section_title=segment.section_title,
                            parent_section=segment.parent_section,
                            metadata={
                                "source_file": source_file,
                                "char_length": len(sub_text),
                                "estimated_tokens": int(len(sub_text) / self.CHARS_PER_TOKEN)
                            }
                        )
                    )
                    chunk_index += 1

        return chunks

    def _split_large_segment(self, text: str) -> List[str]:
        # Split into paragraphs first
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        result_chunks = []
        current_chunk = []
        current_len = 0

        for para in paragraphs:
            para_len = len(para)
            if current_len + para_len <= self.target_chars:
                current_chunk.append(para)
                current_len += para_len + 2
            else:
                if current_chunk:
                    result_chunks.append("\n\n".join(current_chunk))
                    
                    # Compute overlap from previous chunk
                    overlap_text = "\n\n".join(current_chunk)[-self.overlap_chars:]
                    current_chunk = [overlap_text, para]
                    current_len = len(overlap_text) + para_len + 2
                else:
                    # Paragraph itself is huge, split by sentences
                    sentences = re.split(r'(?<=[.!?])\s+', para)
                    sub_current = []
                    sub_len = 0
                    for sent in sentences:
                        if sub_len + len(sent) <= self.target_chars:
                            sub_current.append(sent)
                            sub_len += len(sent) + 1
                        else:
                            if sub_current:
                                result_chunks.append(" ".join(sub_current))
                                overlap_sent = " ".join(sub_current)[-self.overlap_chars:]
                                sub_current = [overlap_sent, sent]
                                sub_len = len(overlap_sent) + len(sent) + 1
                            else:
                                result_chunks.append(sent[:self.target_chars])
                                sub_current = []
                                sub_len = 0
                    if sub_current:
                        current_chunk = sub_current
                        current_len = sub_len

        if current_chunk:
            result_chunks.append("\n\n".join(current_chunk))

        return result_chunks
