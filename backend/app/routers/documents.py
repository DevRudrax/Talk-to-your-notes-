import uuid
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
from pydantic import BaseModel
from app.auth import get_current_user
from app.config import settings
from app.db import get_supabase_admin_client
from app.services.extraction_service import ExtractionService
from app.services.chunking_service import ChunkingService
from app.services.embedding_service import EmbeddingService
import logging

logger = logging.getLogger("talk_to_your_notes.documents_router")

router = APIRouter(prefix="/api/documents", tags=["documents"])

ALLOWED_EXTENSIONS = {'pdf', 'md', 'markdown', 'txt'}


class DocumentResponse(BaseModel):
    id: str
    user_id: str
    collection_id: Optional[str] = None
    file_name: str
    file_type: str
    file_size: int
    mime_type: str
    page_count: int
    status: str
    processing_error: Optional[str] = None
    created_at: str
    updated_at: str
    indexed_at: Optional[str] = None


@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    collection_id: Optional[str] = Form(None),
    user: dict = Depends(get_current_user)
):
    file_name = file.filename or "file.txt"
    ext = file_name.lower().split('.')[-1]

    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type .{ext}. Allowed: PDF, Markdown, TXT"
        )

    file_bytes = await file.read()
    file_size = len(file_bytes)
    max_bytes = settings.MAX_FILE_SIZE_MB * 1024 * 1024

    if file_size > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File exceeds maximum allowed size of {settings.MAX_FILE_SIZE_MB}MB"
        )

    user_id = user["id"]
    document_id = str(uuid.uuid4())
    storage_path = f"documents/{user_id}/{document_id}/{file_name}"
    mime_type = file.content_type or "application/octet-stream"

    supabase = get_supabase_admin_client()

    # 1. Upload to Supabase Storage
    try:
        supabase.storage.from_("documents").upload(storage_path, file_bytes)
    except Exception as e:
        logger.warning(f"Storage upload note: {e}")

    now_iso = datetime.utcnow().isoformat()
    doc_record = {
        "id": document_id,
        "user_id": user_id,
        "collection_id": collection_id if collection_id else None,
        "file_name": file_name,
        "file_type": ext,
        "storage_path": storage_path,
        "file_size": file_size,
        "mime_type": mime_type,
        "page_count": 1,
        "status": "processing",
        "processing_error": None,
        "created_at": now_iso,
        "updated_at": now_iso,
        "indexed_at": None
    }

    supabase.table("documents").insert(doc_record).execute()

    # 2. Process Document (Extract -> Chunk -> Embed -> Index)
    try:
        segments = ExtractionService.extract_document(file_bytes, file_name, mime_type)
        page_count = max([s.page_number or 1 for s in segments], default=1)

        chunker = ChunkingService()
        chunks = chunker.create_chunks(segments, document_id, user_id, file_name)

        embedder = EmbeddingService()
        texts = [c.content for c in chunks]
        embeddings = embedder.embed_documents(texts)

        chunk_records = []
        for i, chunk in enumerate(chunks):
            chunk_dict = chunk.to_dict()
            chunk_dict["embedding"] = embeddings[i] if i < len(embeddings) else None
            chunk_records.append(chunk_dict)

        if chunk_records:
            supabase.table("document_chunks").insert(chunk_records).execute()

        doc_record["status"] = "indexed"
        doc_record["page_count"] = page_count
        doc_record["indexed_at"] = datetime.utcnow().isoformat()
        supabase.table("documents").update({
            "status": "indexed",
            "page_count": page_count,
            "indexed_at": doc_record["indexed_at"]
        }).eq("id", document_id).execute()

    except Exception as proc_err:
        logger.error(f"Document processing failed for {file_name}: {proc_err}")
        doc_record["status"] = "failed"
        doc_record["processing_error"] = str(proc_err)
        supabase.table("documents").update({
            "status": "failed",
            "processing_error": str(proc_err)
        }).eq("id", document_id).execute()

    return DocumentResponse(**doc_record)


@router.get("", response_model=List[DocumentResponse])
def get_documents(
    collection_id: Optional[str] = None,
    user: dict = Depends(get_current_user)
):
    supabase = get_supabase_admin_client()
    try:
        query = supabase.table("documents").select("*").eq("user_id", user["id"])
        if collection_id:
            query = query.eq("collection_id", collection_id)
        res = query.execute()
        docs = res.data if hasattr(res, "data") and res.data else []
        logger.info(f"get_documents fetched {len(docs)} documents for user {user['id']}")
        return [DocumentResponse(**d) for d in docs]
    except Exception as e:
        logger.error(f"get_documents error: {e}", exc_info=True)
        return []


@router.get("/{document_id}", response_model=DocumentResponse)
def get_document(
    document_id: str,
    user: dict = Depends(get_current_user)
):
    supabase = get_supabase_admin_client()
    res = supabase.table("documents").select("*").eq("id", document_id).eq("user_id", user["id"]).execute()
    if not res.data:
        raise HTTPException(status_code=404, detail="Document not found")
    return DocumentResponse(**res.data[0])


@router.delete("/{document_id}")
def delete_document(
    document_id: str,
    user: dict = Depends(get_current_user)
):
    supabase = get_supabase_admin_client()
    res = supabase.table("documents").select("*").eq("id", document_id).eq("user_id", user["id"]).execute()
    if not res.data:
        raise HTTPException(status_code=404, detail="Document not found")

    doc = res.data[0]
    supabase.table("document_chunks").delete().eq("document_id", document_id).execute()
    try:
        supabase.storage.from_("documents").remove([doc.get("storage_path")])
    except Exception as e:
        logger.warning(f"Storage remove note: {e}")
    supabase.table("documents").delete().eq("id", document_id).execute()

    return {"status": "deleted", "id": document_id}
