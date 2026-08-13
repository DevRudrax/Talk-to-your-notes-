import json
import logging
import concurrent.futures
from typing import List, Dict, Any, Optional
from app.config import settings
from app.db import get_supabase_admin_client
from app.services.retrieval_service import RetrievalService, RetrievedChunk
from app.services.context_packer import ContextPacker, PackedContext

logger = logging.getLogger("talk_to_your_notes.rag_service")

SYSTEM_GROUNDED_PROMPT = """You are Talk to Your Notes, a precise and trustworthy AI knowledge assistant.

Your primary role is to answer the user's question using ONLY the provided document context below.

STRICT GROUNDING & CITATION CONTRACT:
1. Base your factual claims solely on the supplied document chunks.
2. Do NOT invent facts, citations, file names, page numbers, or section titles.
3. Every citation MUST reference the exact `chunk_id` string specified in the document header.
4. Return your final answer as valid JSON matching this schema:
{
  "answer": "Detailed answer formatted in clean Markdown...",
  "citations": [
    {
      "chunk_id": "exact-uuid-from-context",
      "reason": "Brief explanation of what claim this chunk supports"
    }
  ],
  "grounded": true
}
5. If the supplied document context is empty or contains insufficient information to answer the question, set "grounded": false and state: "I couldn't find enough information about that in your indexed notes." In this case, citations array MUST be empty [].
6. Output ONLY the JSON object. Do not include markdown code block backticks outside the JSON.
"""


class VerifiedCitation:
    def __init__(
        self,
        chunk_id: str,
        document_id: str,
        file_name: str,
        page_number: Optional[int],
        section_title: Optional[str],
        snippet: str,
        similarity: float,
        reason: str
    ):
        self.chunk_id = chunk_id
        self.document_id = document_id
        self.file_name = file_name
        self.page_number = page_number
        self.section_title = section_title
        self.snippet = snippet
        self.similarity = similarity
        self.reason = reason

    def to_dict(self) -> Dict[str, Any]:
        return {
            "chunk_id": self.chunk_id,
            "document_id": self.document_id,
            "file_name": self.file_name,
            "page_number": self.page_number,
            "section_title": self.section_title,
            "snippet": self.snippet,
            "similarity": self.similarity,
            "reason": self.reason
        }


class RAGResponse:
    def __init__(
        self,
        answer: str,
        citations: List[VerifiedCitation],
        grounded: bool,
        retrieved_chunks_count: int,
        context_tokens: int
    ):
        self.answer = answer
        self.citations = citations
        self.grounded = grounded
        self.retrieved_chunks_count = retrieved_chunks_count
        self.context_tokens = context_tokens

    def to_dict(self) -> Dict[str, Any]:
        return {
            "answer": self.answer,
            "citations": [c.to_dict() for c in self.citations],
            "grounded": self.grounded,
            "retrieved_chunks_count": self.retrieved_chunks_count,
            "context_tokens": self.context_tokens
        }


class RAGService:

    def __init__(
        self,
        retrieval_service: Optional[RetrievalService] = None,
        context_packer: Optional[ContextPacker] = None
    ):
        self.retrieval_service = retrieval_service or RetrievalService()
        self.context_packer = context_packer or ContextPacker()

    def generate_grounded_answer(
        self,
        user_query: str,
        user_id: str,
        collection_id: Optional[str] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> RAGResponse:
        # 1. Retrieve candidate document chunks from pgvector
        retrieved_chunks = self.retrieval_service.retrieve_context(
            user_query=user_query,
            user_id=user_id,
            collection_id=collection_id
        )

        # Retrieval Threshold Check
        if not retrieved_chunks:
            return RAGResponse(
                answer="I couldn't find enough information about that in your indexed notes.",
                citations=[],
                grounded=False,
                retrieved_chunks_count=0,
                context_tokens=0
            )

        # 2. Pack context within token budget
        packed_context = self.context_packer.pack_chunks(retrieved_chunks)
        packed_chunks_by_id = {c.id: c for c in packed_context.packed_chunks}

        # 3. Construct prompt
        formatted_history = ""
        if conversation_history:
            history_lines = [f"{m.get('role', 'user').upper()}: {m.get('content', '')}" for m in conversation_history[-4:]]
            formatted_history = "RECENT CONVERSATION HISTORY:\n" + "\n".join(history_lines) + "\n\n"

        full_prompt = (
            f"{SYSTEM_GROUNDED_PROMPT}\n\n"
            f"{formatted_history}"
            f"DOCUMENT CONTEXT:\n{packed_context.formatted_context}\n\n"
            f"USER QUESTION: {user_query}\n"
        )

        # 4. Generate response via Google Gemini API
        raw_json_str = self._call_gemini(full_prompt, packed_context)

        # 5. Parse & Validate structured JSON response
        answer_text, raw_citations, is_grounded = self._parse_structured_response(raw_json_str, packed_context)

        # 6. Resolve trusted citations against backend chunk records (anti-hallucination)
        verified_citations = []
        for cit in raw_citations:
            cid = cit.get("chunk_id")
            reason = cit.get("reason", "Relevant passage")
            if cid in packed_chunks_by_id:
                chunk = packed_chunks_by_id[cid]
                file_name = chunk.metadata.get("source_file", "Document")
                verified_citations.append(
                    VerifiedCitation(
                        chunk_id=chunk.id,
                        document_id=chunk.document_id,
                        file_name=file_name,
                        page_number=chunk.page_number,
                        section_title=chunk.section_title,
                        snippet=chunk.content[:200] + ("..." if len(chunk.content) > 200 else ""),
                        similarity=chunk.similarity,
                        reason=reason
                    )
                )

        return RAGResponse(
            answer=answer_text,
            citations=verified_citations,
            grounded=is_grounded and bool(verified_citations or "couldn't find" in answer_text.lower()),
            retrieved_chunks_count=len(retrieved_chunks),
            context_tokens=packed_context.total_tokens
        )

    def _call_gemini(self, prompt: str, packed_context: Optional[PackedContext] = None) -> str:
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
                        return response.text
            except Exception as e:
                logger.error(f"Gemini LLM call failed ({settings.LLM_MODEL}): {e}")

        # Fallback offline response dynamically summarizing packed chunks
        mock_cits = []
        answer_summary = "I couldn't find enough information about that in your indexed notes."
        if packed_context and packed_context.packed_chunks:
            top_chunk = packed_context.packed_chunks[0]
            mock_cits = [{"chunk_id": top_chunk.id, "reason": "Primary retrieved context source"}]
            answer_summary = f"Based on your notes:\n\n{top_chunk.content[:400]}"

        return json.dumps({
            "answer": answer_summary,
            "citations": mock_cits,
            "grounded": bool(mock_cits)
        })

    def _parse_structured_response(self, raw_str: str, packed_context: PackedContext):
        try:
            cleaned = raw_str.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.startswith("```"):
                cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            cleaned = cleaned.strip()

            data = json.loads(cleaned)
            answer = data.get("answer", raw_str)
            citations = data.get("citations", [])
            grounded = data.get("grounded", True)
            return answer, citations, grounded
        except Exception as e:
            logger.warning(f"Failed to parse structured JSON from Gemini: {e}")
            default_citations = []
            if packed_context.packed_chunks:
                default_citations = [{"chunk_id": packed_context.packed_chunks[0].id, "reason": "Top matching context"}]
            return raw_str, default_citations, True
