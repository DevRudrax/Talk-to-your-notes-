import logging
import concurrent.futures
from typing import List, Dict, Any, Optional
from app.config import settings
from app.db import get_supabase_admin_client

logger = logging.getLogger("talk_to_your_notes.summarization_service")


class DocumentSummaryResult:
    def __init__(self, summary: str, document_id: str, file_name: str, total_chunks: int):
        self.summary = summary
        self.document_id = document_id
        self.file_name = file_name
        self.total_chunks = total_chunks

    def to_dict(self) -> Dict[str, Any]:
        return {
            "summary": self.summary,
            "document_id": self.document_id,
            "file_name": self.file_name,
            "total_chunks": self.total_chunks
        }


class SummarizationService:

    def summarize_document(self, document_id: str, user_id: str) -> Optional[DocumentSummaryResult]:
        supabase = get_supabase_admin_client()

        # 1. Fetch document record
        doc_res = supabase.table("documents").select("*").eq("id", document_id).eq("user_id", user_id).execute()
        if not doc_res.data:
            return None
        doc = doc_res.data[0]
        file_name = doc.get("file_name", "Document")

        # 2. Fetch document chunks
        chunks_res = supabase.table("document_chunks").select("id, content, chunk_index, page_number, section_title").eq("document_id", document_id).order("chunk_index").execute()
        chunks = chunks_res.data if hasattr(chunks_res, "data") and chunks_res.data else []

        if not chunks:
            return DocumentSummaryResult(
                summary=f"No text content found in document **{file_name}**.",
                document_id=document_id,
                file_name=file_name,
                total_chunks=0
            )

        # 3. Direct summary for small documents (<= 5 chunks)
        if len(chunks) <= 5:
            full_text = "\n\n".join([c.get("content", "") for c in chunks])
            summary = self._summarize_text_block(full_text, file_name)
            return DocumentSummaryResult(
                summary=summary,
                document_id=document_id,
                file_name=file_name,
                total_chunks=len(chunks)
            )

        # 4. Hierarchical summarization for large documents
        batch_size = 5
        batches = [chunks[i:i + batch_size] for i in range(0, len(chunks), batch_size)]
        intermediate_summaries = []

        for b_idx, batch in enumerate(batches):
            batch_text = "\n\n".join([f"[Chunk {c.get('chunk_index')}] {c.get('content', '')}" for c in batch])
            sec_summary = self._summarize_text_block(
                batch_text,
                f"{file_name} (Section {b_idx + 1}/{len(batches)})"
            )
            intermediate_summaries.append(sec_summary)

        # 5. Final consolidation pass
        combined_summaries = "\n\n".join(intermediate_summaries)
        final_summary = self._consolidate_summaries(combined_summaries, file_name)

        return DocumentSummaryResult(
            summary=final_summary,
            document_id=document_id,
            file_name=file_name,
            total_chunks=len(chunks)
        )

    def summarize_all_user_notes(self, user_id: str, collection_id: Optional[str] = None) -> str:
        supabase = get_supabase_admin_client()
        query = supabase.table("documents").select("*").eq("user_id", user_id).eq("status", "indexed")
        if collection_id:
            query = query.eq("collection_id", collection_id)
        res = query.execute()
        docs = res.data if hasattr(res, "data") and res.data else []

        if not docs:
            return "I couldn't find any indexed notes to summarize."

        doc_summaries = []
        for d in docs:
            res_sum = self.summarize_document(d["id"], user_id)
            if res_sum:
                doc_summaries.append(f"## Document: {res_sum.file_name}\n{res_sum.summary}")

        if not doc_summaries:
            return "I couldn't find enough information about that in your indexed notes."

        combined = "\n\n---\n\n".join(doc_summaries)
        if len(docs) == 1:
            return combined

        return f"# Knowledge Base Overview ({len(docs)} Documents)\n\n" + combined

    def _summarize_text_block(self, text: str, context_title: str) -> str:
        prompt = (
            f"Summarize the following document text from '{context_title}' concisely in clean Markdown format.\n"
            f"Highlight key concepts, definitions, and main topics:\n\n"
            f"{text[:12000]}"
        )
        return self._call_llm(prompt)

    def _consolidate_summaries(self, intermediate_text: str, file_name: str) -> str:
        prompt = (
            f"Create a unified, well-structured executive summary of the document '{file_name}' based on the section summaries below.\n"
            f"Use Markdown headings (### Key Concepts, ### Key Definitions, ### Summary Points):\n\n"
            f"{intermediate_text[:12000]}"
        )
        return self._call_llm(prompt)

    def _call_llm(self, prompt: str) -> str:
        if (
            settings.GEMINI_API_KEY
            and not settings.GEMINI_API_KEY.startswith("mock")
            and not settings.GEMINI_API_KEY.startswith("gen-lang-client")
        ):
            try:
                import google.generativeai as genai
                genai.configure(api_key=settings.GEMINI_API_KEY)
                model_name = settings.LLM_MODEL or "gemini-flash-latest"
                model = genai.GenerativeModel(model_name)
                
                with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                    future = executor.submit(model.generate_content, prompt)
                    response = future.result(timeout=10.0)
                    if response and response.text:
                        return response.text.strip()
            except Exception as e:
                logger.error(f"Summarization LLM call failed: {e}")

        return "This document covers key concepts and definitions present in your indexed notes."
