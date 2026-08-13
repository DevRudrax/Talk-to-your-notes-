from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from app.auth import get_current_user
from app.db import get_supabase_admin_client
from app.services.rag_service import RAGService
import uuid
import logging
from datetime import datetime

logger = logging.getLogger("talk_to_your_notes.chat_router")

router = APIRouter(prefix="/api/chat", tags=["chat"])


class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None
    collection_id: Optional[str] = None


class CitationSchema(BaseModel):
    chunk_id: str
    document_id: str
    file_name: str
    page_number: Optional[int] = None
    section_title: Optional[str] = None
    snippet: str
    similarity: float
    reason: str


class ChatResponse(BaseModel):
    conversation_id: str
    message_id: str
    answer: str
    citations: List[CitationSchema]
    grounded: bool
    retrieved_chunks_count: int
    context_tokens: int
    rewritten_query: Optional[str] = None
    debug_info: Optional[Dict[str, Any]] = None


@router.post("", response_model=ChatResponse)
def send_chat_message(
    payload: ChatRequest,
    user: dict = Depends(get_current_user)
):
    return _process_chat(payload, user, include_debug=False)


@router.post("/debug", response_model=ChatResponse)
def send_chat_message_debug(
    payload: ChatRequest,
    user: dict = Depends(get_current_user)
):
    return _process_chat(payload, user, include_debug=True)


def _process_chat(payload: ChatRequest, user: dict, include_debug: bool = False):
    supabase = get_supabase_admin_client()
    user_id = user["id"]

    # 1. Resolve or create conversation
    conv_id = payload.conversation_id
    if not conv_id:
        conv_title = payload.message[:30] + ("..." if len(payload.message) > 30 else "")
        res = supabase.table("conversations").insert({
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "collection_id": payload.collection_id,
            "title": conv_title,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }).execute()
        conv_id = res.data[0]["id"]

    # 2. Fetch recent conversation history
    history_res = supabase.table("messages").select("role, content").eq("conversation_id", conv_id).order("created_at").execute()
    history = history_res.data if hasattr(history_res, "data") and history_res.data else []

    # 3. Store User Message
    user_msg_id = str(uuid.uuid4())
    supabase.table("messages").insert({
        "id": user_msg_id,
        "conversation_id": conv_id,
        "user_id": user_id,
        "role": "user",
        "content": payload.message,
        "created_at": datetime.utcnow().isoformat()
    }).execute()

    # 4. Invoke RAG Service
    rag_service = RAGService()
    rag_res = rag_service.generate_grounded_answer(
        user_query=payload.message,
        user_id=user_id,
        collection_id=payload.collection_id,
        conversation_history=history,
        include_debug=include_debug
    )

    # 5. Store Assistant Message
    assistant_msg_id = str(uuid.uuid4())
    supabase.table("messages").insert({
        "id": assistant_msg_id,
        "conversation_id": conv_id,
        "user_id": user_id,
        "role": "assistant",
        "content": rag_res.answer,
        "created_at": datetime.utcnow().isoformat()
    }).execute()

    # 6. Store Message Sources
    if rag_res.citations:
        sources_records = []
        for rank, cit in enumerate(rag_res.citations, 1):
            sources_records.append({
                "id": str(uuid.uuid4()),
                "message_id": assistant_msg_id,
                "chunk_id": cit.chunk_id,
                "similarity": cit.similarity,
                "rank": rank,
                "created_at": datetime.utcnow().isoformat()
            })
        supabase.table("message_sources").insert(sources_records).execute()

    # 7. Update Conversation Timestamp
    supabase.table("conversations").update({
        "updated_at": datetime.utcnow().isoformat()
    }).eq("id", conv_id).execute()

    citations_schema = [CitationSchema(**c.to_dict()) for c in rag_res.citations]

    return ChatResponse(
        conversation_id=conv_id,
        message_id=assistant_msg_id,
        answer=rag_res.answer,
        citations=citations_schema,
        grounded=rag_res.grounded,
        retrieved_chunks_count=rag_res.retrieved_chunks_count,
        context_tokens=rag_res.context_tokens,
        rewritten_query=rag_res.rewritten_query,
        debug_info=rag_res.debug_info
    )
