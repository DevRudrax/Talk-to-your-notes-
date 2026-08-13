import uuid
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.auth import get_current_user
from app.db import get_supabase_admin_client
import logging

logger = logging.getLogger("talk_to_your_notes.collections_router")

router = APIRouter(prefix="/api/collections", tags=["collections"])


class CollectionResponse(BaseModel):
    id: str
    user_id: str
    name: str
    description: Optional[str] = None
    created_at: str
    updated_at: str


class CreateCollectionRequest(BaseModel):
    name: str
    description: Optional[str] = None


@router.get("", response_model=List[CollectionResponse])
def list_collections(user: dict = Depends(get_current_user)):
    supabase = get_supabase_admin_client()
    res = supabase.table("collections").select("*").eq("user_id", user["id"]).execute()
    cols = res.data if hasattr(res, "data") and res.data else []
    return [CollectionResponse(**c) for c in cols]


@router.post("", response_model=CollectionResponse)
def create_collection(
    req: CreateCollectionRequest,
    user: dict = Depends(get_current_user)
):
    supabase = get_supabase_admin_client()
    now_iso = datetime.utcnow().isoformat()
    col_id = str(uuid.uuid4())
    col_record = {
        "id": col_id,
        "user_id": user["id"],
        "name": req.name,
        "description": req.description,
        "created_at": now_iso,
        "updated_at": now_iso
    }
    supabase.table("collections").insert(col_record).execute()
    return CollectionResponse(**col_record)


@router.patch("/{collection_id}", response_model=CollectionResponse)
def update_collection(
    collection_id: str,
    req: CreateCollectionRequest,
    user: dict = Depends(get_current_user)
):
    supabase = get_supabase_admin_client()
    res = supabase.table("collections").select("*").eq("id", collection_id).eq("user_id", user["id"]).execute()
    if not res.data:
        raise HTTPException(status_code=404, detail="Collection not found")

    now_iso = datetime.utcnow().isoformat()
    supabase.table("collections").update({
        "name": req.name,
        "description": req.description,
        "updated_at": now_iso
    }).eq("id", collection_id).execute()

    col = res.data[0]
    col["name"] = req.name
    col["description"] = req.description
    col["updated_at"] = now_iso
    return CollectionResponse(**col)


@router.delete("/{collection_id}")
def delete_collection(
    collection_id: str,
    user: dict = Depends(get_current_user)
):
    supabase = get_supabase_admin_client()
    res = supabase.table("collections").select("*").eq("id", collection_id).eq("user_id", user["id"]).execute()
    if not res.data:
        raise HTTPException(status_code=404, detail="Collection not found")

    supabase.table("collections").delete().eq("id", collection_id).execute()
    return {"status": "deleted", "id": collection_id}
