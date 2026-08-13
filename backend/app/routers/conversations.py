from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from app.auth import get_current_user
from app.db import get_supabase_admin_client
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
    messages = msg_res.data if hasattr(msg_res, "data") and msg_res.data else []

    return ConversationDetailResponse(
        **conv,
        messages=[MessageResponse(**m) for m in messages]
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
