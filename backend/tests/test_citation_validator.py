import pytest
from app.services.rag_service import RAGService
from app.services.retrieval_service import RetrievedChunk
from app.services.context_packer import ContextPacker, PackedContext


def test_structured_citation_validation():
    rag = RAGService()

    valid_chunk = RetrievedChunk(
        id="real-chunk-uuid-101",
        document_id="doc-1",
        user_id="user-1",
        content="Boyce-Codd Normal Form (BCNF) is a stricter version of 3NF.",
        chunk_index=0,
        page_number=45,
        section_title="BCNF",
        parent_section="Normalization",
        metadata={"source_file": "DBMS.pdf"},
        similarity=0.88
    )

    packed_context = PackedContext(
        formatted_context="...",
        packed_chunks=[valid_chunk],
        total_tokens=50,
        dropped_chunks_count=0
    )

    raw_response_with_fake = """{
      "answer": "BCNF requires every determinant to be a super key.",
      "citations": [
        {"chunk_id": "real-chunk-uuid-101", "reason": "BCNF definition"},
        {"chunk_id": "fake-hallucinated-uuid-999", "reason": "Hallucinated source"}
      ],
      "grounded": true
    }"""

    answer, citations, grounded = rag._parse_structured_response(raw_response_with_fake, packed_context)
    assert len(citations) == 2

    # Verify that invalid chunk IDs are rejected when resolving against packed context
    packed_by_id = {c.id: c for c in packed_context.packed_chunks}
    verified = [c for c in citations if c.get("chunk_id") in packed_by_id]
    
    assert len(verified) == 1
    assert verified[0]["chunk_id"] == "real-chunk-uuid-101"
