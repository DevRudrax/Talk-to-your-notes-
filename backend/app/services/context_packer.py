import logging
from typing import List, Dict, Any, Tuple
from app.config import settings
from app.services.retrieval_service import RetrievedChunk

logger = logging.getLogger("talk_to_your_notes.context_packer")


class PackedContext:
    def __init__(
        self,
        formatted_context: str,
        packed_chunks: List[RetrievedChunk],
        total_tokens: int,
        dropped_chunks_count: int
    ):
        self.formatted_context = formatted_context
        self.packed_chunks = packed_chunks
        self.total_tokens = total_tokens
        self.dropped_chunks_count = dropped_chunks_count


class ContextPacker:
    CHARS_PER_TOKEN = 4.0

    def __init__(self, max_tokens: int = None):
        self.max_tokens = max_tokens or settings.MAX_CONTEXT_TOKENS
        self.max_chars = int(self.max_tokens * self.CHARS_PER_TOKEN)

    def pack_chunks(self, chunks: List[RetrievedChunk]) -> PackedContext:
        if not chunks:
            return PackedContext(
                formatted_context="[NO RETRIEVED DOCUMENT CONTEXT AVAILABLE]",
                packed_chunks=[],
                total_tokens=0,
                dropped_chunks_count=0
            )

        # 1. Deduplicate by content hash & chunk ID
        seen_ids = set()
        seen_texts = set()
        unique_chunks = []

        for chunk in chunks:
            if chunk.id in seen_ids:
                continue
            normalized_text = " ".join(chunk.content.strip().lower().split())
            if normalized_text in seen_texts:
                continue

            seen_ids.add(chunk.id)
            seen_texts.add(normalized_text)
            unique_chunks.append(chunk)

        # 2. Sort by similarity score descending
        sorted_chunks = sorted(unique_chunks, key=lambda c: c.similarity, reverse=True)

        # 3. Pack chunks within token budget
        packed = []
        current_chars = 0
        dropped_count = 0

        context_blocks = []

        for chunk in sorted_chunks:
            file_name = chunk.metadata.get("source_file", "Document")
            page_str = f"Page {chunk.page_number}" if chunk.page_number else "Page N/A"
            section_str = f"Section: {chunk.section_title}" if chunk.section_title else "Section: N/A"
            
            block_header = (
                f"--- DOCUMENT SOURCE START ---\n"
                f"Chunk ID: {chunk.id}\n"
                f"File: {file_name}\n"
                f"Location: {page_str} | {section_str}\n"
                f"Similarity Score: {chunk.similarity:.4f}\n"
                f"Content:\n"
            )
            block_footer = "\n--- DOCUMENT SOURCE END ---\n"
            
            block = f"{block_header}{chunk.content}{block_footer}"
            block_chars = len(block)

            if current_chars + block_chars <= self.max_chars:
                packed.append(chunk)
                context_blocks.append(block)
                current_chars += block_chars
            else:
                dropped_count += 1

        formatted_text = "\n\n".join(context_blocks)
        total_tokens = int(current_chars / self.CHARS_PER_TOKEN)

        return PackedContext(
            formatted_context=formatted_text,
            packed_chunks=packed,
            total_tokens=total_tokens,
            dropped_chunks_count=dropped_count
        )
