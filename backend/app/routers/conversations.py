from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from app.auth import get_current_user
from app.db import get_supabase_admin_client
from app.routers.chat import CitationResponse
import logging

logger = logging.getLogger("talk_to_your_notes.conversations_router")

router = APIRouter(prefix="/api/conversations", tags=["conversations"])


class ConversationResponse(BaseModel):
    id: str
    user_id: str
    collection_id: Optional[str] = None
    title: str
    conversation_summary: Optional[str] = None
    created_at: str
    updated_at: str


class MessageResponse(BaseModel):
    id: str
    conversation_id: str
    user_id: str
    role: str
    content: str
    created_at: str
    citations: List[CitationResponse] = []


class ConversationDetailResponse(ConversationResponse):
    messages: List[MessageResponse] = []


class UpdateConversationRequest(BaseModel):
    title: str


@router.get("", response_model=List[ConversationResponse])
def list_conversations(user: dict = Depends(get_current_user)):
    supabase = get_supabase_admin_client()
    res = supabase.table("conversations").select("*").eq("user_id", user["id"]).execute()
    convs = res.data if hasattr(res, "data") and res.data else []
    return [ConversationResponse(**c) for c in convs]


@router.get("/{conversation_id}", response_model=ConversationDetailResponse)
def get_conversation(
    conversation_id: str,
    user: dict = Depends(get_current_user)
):
    supabase = get_supabase_admin_client()
    res = supabase.table("conversations").select("*").eq("id", conversation_id).eq("user_id", user["id"]).execute()
    if not res.data:
        raise HTTPException(status_code=404, detail="Conversation not found")

    conv = res.data[0]
    msg_res = supabase.table("messages").select("*").eq("conversation_id", conversation_id).execute()
    raw_messages = msg_res.data if hasattr(msg_res, "data") and msg_res.data else []

    message_responses = []
    for m in raw_messages:
        msg_id = m["id"]
        citations = []
        if m["role"] == "assistant":
            try:
                sources_res = supabase.table("message_sources").select("*").eq("message_id", msg_id).execute()
                sources = sources_res.data if hasattr(sources_res, "data") and sources_res.data else []
                for s in sources:
                    chunk_id = s.get("chunk_id")
                    if chunk_id:
                        c_res = supabase.table("document_chunks").select("*").eq("id", chunk_id).execute()
                        if c_res.data:
                            c_data = c_res.data[0]
                            doc_id = c_data.get("document_id")
                            file_name = "Document"
                            if doc_id:
                                d_res = supabase.table("documents").select("file_name").eq("id", doc_id).execute()
                                if d_res.data:
                                    file_name = d_res.data[0].get("file_name", "Document")
                            citations.append(
                                CitationResponse(
                                    chunk_id=chunk_id,
                                    document_id=doc_id or "",
                                    file_name=file_name,
                                    page_number=c_data.get("page_number"),
                                    section_title=c_data.get("section_title"),
                                    snippet=c_data.get("content", "")[:200] + ("..." if len(c_data.get("content", "")) > 200 else ""),
                                    similarity=float(s.get("similarity", 0.0)),
                                    reason="Cited context source"
                                )
                            )
            except Exception as e:
                logger.warning(f"Error fetching citations for message {msg_id}: {e}")

        message_responses.append(
            MessageResponse(
                id=m["id"],
                conversation_id=m["conversation_id"],
                user_id=m["user_id"],
                role=m["role"],
                content=m["content"],
                created_at=m["created_at"],
                citations=citations
            )
        )

    return ConversationDetailResponse(
        **conv,
        messages=message_responses
    )


@router.patch("/{conversation_id}", response_model=ConversationResponse)
def update_conversation(
    conversation_id: str,
    req: UpdateConversationRequest,
    user: dict = Depends(get_current_user)
):
    supabase = get_supabase_admin_client()
    res = supabase.table("conversations").select("*").eq("id", conversation_id).eq("user_id", user["id"]).execute()
    if not res.data:
        raise HTTPException(status_code=404, detail="Conversation not found")

    supabase.table("conversations").update({"title": req.title}).eq("id", conversation_id).execute()
    conv = res.data[0]
    conv["title"] = req.title
    return ConversationResponse(**conv)


@router.delete("/{conversation_id}")
def delete_conversation(
    conversation_id: str,
    user: dict = Depends(get_current_user)
):
    supabase = get_supabase_admin_client()
    res = supabase.table("conversations").select("*").eq("id", conversation_id).eq("user_id", user["id"]).execute()
    if not res.data:
        raise HTTPException(status_code=404, detail="Conversation not found")

    supabase.table("messages").delete().eq("conversation_id", conversation_id).execute()
    supabase.table("conversations").delete().eq("id", conversation_id).execute()
    return {"status": "deleted", "id": conversation_id}
