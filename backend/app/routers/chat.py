import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.auth import get_current_user
from app.db import get_supabase_admin_client
from app.services.rag_service import RAGService
import logging

logger = logging.getLogger("talk_to_your_notes.chat_router")

router = APIRouter(prefix="/api/chat", tags=["chat"])


class ChatRequest(BaseModel):
    conversation_id: Optional[str] = None
    message: str
    collection_id: Optional[str] = None


class CitationResponse(BaseModel):
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
    user_message_id: str
    assistant_message_id: str
    answer: str
    citations: List[CitationResponse]
    grounded: bool


@router.post("", response_model=ChatResponse)
def post_chat(
    req: ChatRequest,
    user: dict = Depends(get_current_user)
):
    user_id = user["id"]
    supabase = get_supabase_admin_client()
    now_iso = datetime.utcnow().isoformat()

    # 1. Manage Conversation Record
    conversation_id = req.conversation_id
    if not conversation_id:
        conversation_id = str(uuid.uuid4())
        conv_record = {
            "id": conversation_id,
            "user_id": user_id,
            "collection_id": req.collection_id,
            "title": req.message[:50] + ("..." if len(req.message) > 50 else ""),
            "conversation_summary": None,
            "created_at": now_iso,
            "updated_at": now_iso
        }
        supabase.table("conversations").insert(conv_record).execute()
    else:
        res = supabase.table("conversations").select("*").eq("id", conversation_id).eq("user_id", user_id).execute()
        if not res.data:
            conversation_id = str(uuid.uuid4())
            conv_record = {
                "id": conversation_id,
                "user_id": user_id,
                "collection_id": req.collection_id,
                "title": req.message[:50],
                "created_at": now_iso,
                "updated_at": now_iso
            }
            supabase.table("conversations").insert(conv_record).execute()

    # 2. Fetch recent conversation messages
    history_res = supabase.table("messages").select("role, content").eq("conversation_id", conversation_id).execute()
    history = history_res.data if hasattr(history_res, "data") and history_res.data else []

    # 3. Store User Message
    user_msg_id = str(uuid.uuid4())
    user_msg_record = {
        "id": user_msg_id,
        "conversation_id": conversation_id,
        "user_id": user_id,
        "role": "user",
        "content": req.message,
        "created_at": now_iso
    }
    supabase.table("messages").insert(user_msg_record).execute()

    # 4. Execute Grounded RAG Pipeline
    rag_service = RAGService()
    rag_res = rag_service.generate_grounded_answer(
        user_query=req.message,
        user_id=user_id,
        collection_id=req.collection_id,
        conversation_history=history
    )

    # 5. Store Assistant Message
    asst_msg_id = str(uuid.uuid4())
    asst_msg_record = {
        "id": asst_msg_id,
        "conversation_id": conversation_id,
        "user_id": user_id,
        "role": "assistant",
        "content": rag_res.answer,
        "created_at": datetime.utcnow().isoformat()
    }
    supabase.table("messages").insert(asst_msg_record).execute()

    # 6. Store Message Sources
    source_responses = []
    for rank, cit in enumerate(rag_res.citations):
        source_record = {
            "id": str(uuid.uuid4()),
            "message_id": asst_msg_id,
            "chunk_id": cit.chunk_id,
            "similarity": cit.similarity,
            "rank": rank + 1,
            "created_at": datetime.utcnow().isoformat()
        }
        try:
            supabase.table("message_sources").insert(source_record).execute()
        except Exception as e:
            logger.warning(f"Message source record insert note: {e}")

        source_responses.append(
            CitationResponse(
                chunk_id=cit.chunk_id,
                document_id=cit.document_id,
                file_name=cit.file_name,
                page_number=cit.page_number,
                section_title=cit.section_title,
                snippet=cit.snippet,
                similarity=cit.similarity,
                reason=cit.reason
            )
        )

    supabase.table("conversations").update({"updated_at": datetime.utcnow().isoformat()}).eq("id", conversation_id).execute()

    return ChatResponse(
        conversation_id=conversation_id,
        user_message_id=user_msg_id,
        assistant_message_id=asst_msg_id,
        answer=rag_res.answer,
        citations=source_responses,
        grounded=rag_res.grounded
    )
