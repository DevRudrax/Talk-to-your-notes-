import pytest
from app.services.extraction_service import ExtractedSegment
from app.services.chunking_service import ChunkingService


def test_chunking_service():
    segment = ExtractedSegment(
        content="This is a test paragraph about database indexing and performance optimization." * 20,
        page_number=3,
        section_title="Performance Tuning"
    )
    chunker = ChunkingService(target_tokens=100, overlap_tokens=20)
    chunks = chunker.create_chunks(
        segments=[segment],
        document_id="doc-123",
        user_id="user-456",
        source_file="DBMS.pdf"
    )

    assert len(chunks) > 0
    first_chunk = chunks[0]
    assert first_chunk.document_id == "doc-123"
    assert first_chunk.user_id == "user-456"
    assert first_chunk.page_number == 3
    assert first_chunk.section_title == "Performance Tuning"
    assert first_chunk.metadata["source_file"] == "DBMS.pdf"
