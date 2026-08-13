import pytest
from app.services.retrieval_service import RetrievedChunk
from app.services.context_packer import ContextPacker


def test_context_packer_deduplication_and_budget():
    c1 = RetrievedChunk(
        id="chunk-1",
        document_id="doc-1",
        user_id="user-1",
        content="Third Normal Form (3NF) requires 2NF and no transitive functional dependencies.",
        chunk_index=0,
        page_number=42,
        section_title="Third Normal Form",
        parent_section="Normalization",
        metadata={"source_file": "DBMS.pdf"},
        similarity=0.92
    )
    # Duplicate text
    c2 = RetrievedChunk(
        id="chunk-2",
        document_id="doc-1",
        user_id="user-1",
        content="Third Normal Form (3NF) requires 2NF and no transitive functional dependencies.",
        chunk_index=1,
        page_number=42,
        section_title="Third Normal Form",
        parent_section="Normalization",
        metadata={"source_file": "DBMS.pdf"},
        similarity=0.91
    )

    packer = ContextPacker(max_tokens=200)
    packed = packer.pack_chunks([c1, c2])

    assert len(packed.packed_chunks) == 1
    assert packed.packed_chunks[0].id == "chunk-1"
    assert "Third Normal Form" in packed.formatted_context
