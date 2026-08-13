import pytest
from app.services.rag_service import RAGService
from app.services.retrieval_service import RetrievalService, RetrievedChunk
from app.services.context_packer import ContextPacker


def test_rag_eval_groundedness_and_not_found():
    rag = RAGService()

    # Case 1: Empty retrieval triggers Not Found response without hallucinating facts
    res_empty = rag.generate_grounded_answer(
        user_query="What is quantum computing?",
        user_id="user-eval-1"
    )
    assert res_empty.grounded is False
    assert "couldn't find" in res_empty.answer.lower()
    assert len(res_empty.citations) == 0

    # Case 2: Document retrieval yields grounded citation metadata
    chunk = RetrievedChunk(
        id="chunk-eval-001",
        document_id="doc-eval-001",
        user_id="user-eval-1",
        content="Third Normal Form (3NF) requires a relation to be in 2NF and no non-prime attribute to be transitively dependent on the primary key.",
        chunk_index=0,
        page_number=14,
        section_title="Third Normal Form",
        parent_section="Normalization",
        metadata={"source_file": "Database_Notes.pdf"},
        similarity=0.95
    )

    class MockRetrieval:
        def retrieve_context(self, user_query, user_id, collection_id=None):
            return [chunk]

    rag_mock = RAGService(retrieval_service=MockRetrieval())
    res_grounded = rag_mock.generate_grounded_answer(
        user_query="Explain 3NF in database normalization",
        user_id="user-eval-1"
    )

    assert res_grounded.retrieved_chunks_count == 1
    assert len(res_grounded.citations) == 1
    cit = res_grounded.citations[0]
    assert cit.chunk_id == "chunk-eval-001"
    assert cit.file_name == "Database_Notes.pdf"
    assert cit.page_number == 14
    assert cit.section_title == "Third Normal Form"
