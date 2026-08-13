import pytest
import time
from app.services.rag_service import RAGService
from app.services.summarization_service import SummarizationService

@pytest.fixture(autouse=True)
def rate_limit_delay():
    time.sleep(12)

@pytest.fixture
def rag_service():
    return RAGService()

@pytest.fixture
def summarization_service():
    return SummarizationService()

def test_rag_dbms_query(rag_service):
    user_id = "00000000-0000-0000-0000-000000000001"
    response = rag_service.generate_grounded_answer("What is DBMS?", user_id=user_id)
    assert response.answer is not None
    assert len(response.answer) > 10
    assert response.grounded is True

def test_rag_3nf_query(rag_service):
    user_id = "00000000-0000-0000-0000-000000000001"
    response = rag_service.generate_grounded_answer("Explain 3NF in database normalization", user_id=user_id)
    assert response.answer is not None
    assert len(response.answer) > 10
    assert response.grounded is True

def test_rag_absent_query(rag_service):
    user_id = "00000000-0000-0000-0000-000000000001"
    response = rag_service.generate_grounded_answer("What is quantum computing according to these notes?", user_id=user_id)
    assert "couldn't find enough information" in response.answer.lower()
    assert len(response.citations) == 0
    assert response.grounded is False

def test_rag_summarise_entire_notes(rag_service):
    user_id = "00000000-0000-0000-0000-000000000001"
    response = rag_service.generate_grounded_answer("summarise the entire notes", user_id=user_id)
    assert response.answer is not None
    assert len(response.answer) > 20
    assert response.grounded is True

def test_rag_query_rewriting(rag_service):
    user_id = "00000000-0000-0000-0000-000000000001"
    history = [
        {"role": "user", "content": "What is database normalization?"},
        {"role": "assistant", "content": "Normalization is the process of organizing data..."}
    ]
    response = rag_service.generate_grounded_answer("What about 3NF?", user_id=user_id, conversation_history=history)
    assert response.answer is not None
    assert response.answer != ""
