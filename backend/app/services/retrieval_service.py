import logging
from typing import List, Dict, Any, Optional
from app.config import settings
from app.db import get_supabase_admin_client
from app.services.embedding_service import EmbeddingService

logger = logging.getLogger("talk_to_your_notes.retrieval")


class RetrievedChunk:
    def __init__(
        self,
        id: str,
        document_id: str,
        user_id: str,
        content: str,
        chunk_index: int,
        page_number: Optional[int],
        section_title: Optional[str],
        parent_section: Optional[str],
        metadata: Dict[str, Any],
        similarity: float
    ):
        self.id = id
        self.document_id = document_id
        self.user_id = user_id
        self.content = content
        self.chunk_index = chunk_index
        self.page_number = page_number
        self.section_title = section_title
        self.parent_section = parent_section
        self.metadata = metadata
        self.similarity = similarity

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "document_id": self.document_id,
            "user_id": self.user_id,
            "content": self.content,
            "chunk_index": self.chunk_index,
            "page_number": self.page_number,
            "section_title": self.section_title,
            "parent_section": self.parent_section,
            "metadata": self.metadata,
            "similarity": self.similarity
        }


class RetrievalService:

    def __init__(self, embedding_service: Optional[EmbeddingService] = None):
        self.embedding_service = embedding_service or EmbeddingService()

    def retrieve_context(
        self,
        user_query: str,
        user_id: str,
        collection_id: Optional[str] = None,
        top_k: Optional[int] = None,
        similarity_threshold: Optional[float] = None
    ) -> List[RetrievedChunk]:
        top_k = top_k or settings.TOP_K
        similarity_threshold = similarity_threshold if similarity_threshold is not None else settings.SIMILARITY_THRESHOLD

        # 1. Embed query
        query_embedding = self.embedding_service.embed_text(user_query)

        # 2. Execute pgvector search RPC
        supabase = get_supabase_admin_client()
        try:
            rpc_res = supabase.rpc(
                "match_document_chunks",
                {
                    "query_embedding": query_embedding,
                    "match_count": top_k,
                    "similarity_threshold": similarity_threshold,
                    "filter_user_id": user_id,
                    "filter_collection_id": collection_id
                }
            ).execute()

            retrieved_chunks = []
            if hasattr(rpc_res, "data") and rpc_res.data:
                for row in rpc_res.data:
                    retrieved_chunks.append(
                        RetrievedChunk(
                            id=row.get("id"),
                            document_id=row.get("document_id"),
                            user_id=row.get("user_id"),
                            content=row.get("content"),
                            chunk_index=row.get("chunk_index"),
                            page_number=row.get("page_number"),
                            section_title=row.get("section_title"),
                            parent_section=row.get("parent_section"),
                            metadata=row.get("metadata", {}),
                            similarity=float(row.get("similarity", 0.0))
                        )
                    )
            return retrieved_chunks
        except Exception as e:
            logger.error(f"Vector search RPC execution failed: {e}")
            return []
