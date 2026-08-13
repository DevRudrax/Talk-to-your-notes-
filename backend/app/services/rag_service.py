import json
import logging
import time
import concurrent.futures
from typing import List, Dict, Any, Optional
from app.config import settings
from app.db import get_supabase_admin_client
from app.services.retrieval_service import RetrievalService, RetrievedChunk
from app.services.context_packer import ContextPacker, PackedContext
from app.services.summarization_service import SummarizationService

logger = logging.getLogger("talk_to_your_notes.rag_service")

SYSTEM_GROUNDED_PROMPT = """You are Talk to Your Notes, an intelligent, conversational, and brilliant AI knowledge assistant (like Google Gemini Chat).

YOUR MISSION:
1. Answer the user's question clearly, comprehensively, and intelligently formatted in clean Markdown.
2. Use the provided document context below as your primary knowledge source and anchor.
3. If the user's question is directly addressed in the document context, provide a detailed, accurate explanation supported by the notes.
4. If the exact literal answer is not stated word-for-word in the notes, BUT the topic is related to the user's notes/documents, use your comprehensive AI reasoning to answer the question smoothly and helpfully while connecting to their notes' topic.
5. Provide a natural, engaging, and friendly response (just like Gemini Chat). Do NOT output raw snippet code dumps or mechanical robotic disclaimers.

STRICT CITATION CONTRACT:
- Every citation MUST reference the exact `chunk_id` string specified in the document header.
- Return your final answer as valid JSON matching this schema:
{
  "answer": "Comprehensive answer formatted in clean Markdown...",
  "citations": [
    {
      "chunk_id": "exact-uuid-from-context",
      "reason": "Brief explanation of how this document passage supports the answer"
    }
  ],
  "grounded": true
}
- Output ONLY the JSON object. Do not include markdown code block backticks outside the JSON.
"""

SYSTEM_GENERAL_PROMPT = """You are Talk to Your Notes, an intelligent, conversational AI assistant (like Google Gemini Chat).

The user has asked a question but there are no relevant documents in their notes for this topic.
Answer their question using your own broad AI knowledge, helpfully and clearly in clean Markdown.
Be friendly, thorough, and conversational — like a knowledgeable friend.

Return your answer as valid JSON:
{
  "answer": "Your comprehensive Markdown answer here...",
  "citations": [],
  "grounded": false
}
Output ONLY the JSON object.
"""

# Ordered fallback chain — confirmed working models (tested live against the API)
# Free tier has per-model quotas, so rotating through them gives more capacity
GEMINI_FALLBACK_MODELS = [
    "models/gemini-3.5-flash",
    "models/gemini-3.5-flash-lite",
    "models/gemini-3.1-flash-lite",
    "models/gemini-3-flash-preview",
    "models/gemini-flash-lite-latest",
    "models/gemini-3.1-flash-lite-preview",
    "models/gemma-4-26b-a4b-it",
    "models/gemma-4-31b-it",
]

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
        context_tokens: int,
        rewritten_query: Optional[str] = None,
        debug_info: Optional[Dict[str, Any]] = None
    ):
        self.answer = answer
        self.citations = citations
        self.grounded = grounded
        self.retrieved_chunks_count = retrieved_chunks_count
        self.context_tokens = context_tokens
        self.rewritten_query = rewritten_query
        self.debug_info = debug_info

    def to_dict(self) -> Dict[str, Any]:
        return {
            "answer": self.answer,
            "citations": [c.to_dict() for c in self.citations],
            "grounded": self.grounded,
            "retrieved_chunks_count": self.retrieved_chunks_count,
            "context_tokens": self.context_tokens,
            "rewritten_query": self.rewritten_query,
            "debug_info": self.debug_info
        }


class RAGService:

    def __init__(
        self,
        retrieval_service: Optional[RetrievalService] = None,
        context_packer: Optional[ContextPacker] = None,
        summarization_service: Optional[SummarizationService] = None
    ):
        self.retrieval_service = retrieval_service or RetrievalService()
        self.context_packer = context_packer or ContextPacker()
        self.summarization_service = summarization_service or SummarizationService()

    def generate_grounded_answer(
        self,
        user_query: str,
        user_id: str,
        collection_id: Optional[str] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        include_debug: bool = False
    ) -> RAGResponse:
        # 1. Query Type Routing — Check if user is asking for a whole-document summary
        q_lower = user_query.lower().strip()
        summary_triggers = ["summarise the entire notes", "summarise all notes", "summarize the entire notes", "summarize my notes", "overall summary of notes", "give me a summary of my notes", "tell me about my uploaded pdf", "tell me about the pdf", "tell me about the notes"]
        if any(t in q_lower for t in summary_triggers) or q_lower == "summarise notes" or q_lower == "summarize notes":
            summary_text = self.summarization_service.summarize_all_user_notes(user_id=user_id, collection_id=collection_id)
            return RAGResponse(
                answer=summary_text,
                citations=[],
                grounded=True,
                retrieved_chunks_count=0,
                context_tokens=0
            )

        # 2. Query Rewriting for Conversational Follow-up
        retrieval_query = self._rewrite_query_with_history(user_query, conversation_history)

        # 3. Retrieve candidate document chunks from pgvector
        retrieved_chunks = self.retrieval_service.retrieve_context(
            user_query=retrieval_query,
            user_id=user_id,
            collection_id=collection_id
        )

        # Retrieval Threshold Check - no matching chunks found
        if not retrieved_chunks:
            # Answer from AI general knowledge instead of dead-end error
            general_prompt = (
                f"{SYSTEM_GENERAL_PROMPT}\n\n"
                f"USER QUESTION: {user_query}\n"
            )
            raw_json_str = self._call_gemini(general_prompt, packed_context=None)
            answer_text, _, _ = self._parse_structured_response(raw_json_str, None)
            return RAGResponse(
                answer=answer_text,
                citations=[],
                grounded=False,
                retrieved_chunks_count=0,
                context_tokens=0,
                rewritten_query=retrieval_query if retrieval_query != user_query else None
            )

        # 4. Pack context within token budget
        packed_context = self.context_packer.pack_chunks(retrieved_chunks)
        packed_chunks_by_id = {c.id: c for c in packed_context.packed_chunks}

        # 5. Construct prompt
        formatted_history = ""
        if conversation_history:
            history_lines = [f"{m.get('role', 'user').upper()}: {m.get('content', '')}" for m in conversation_history[-4:]]
            formatted_history = "RECENT CONVERSATION HISTORY:\n" + "\n".join(history_lines) + "\n\n"

        full_prompt = (
            f"{SYSTEM_GROUNDED_PROMPT}\n\n"
            f"{formatted_history}"
            f"DOCUMENT CONTEXT FROM USER NOTES:\n{packed_context.formatted_context}\n\n"
            f"USER QUESTION: {user_query}\n"
        )

        # 6. Generate response via Google Gemini API
        raw_json_str = self._call_gemini(full_prompt, packed_context)

        # 7. Parse & Validate structured JSON response
        answer_text, raw_citations, is_grounded = self._parse_structured_response(raw_json_str, packed_context)

        # 8. Resolve trusted citations against backend chunk records (anti-hallucination)
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

        debug_info = None
        if include_debug:
            dropped = [c.to_dict() for c in retrieved_chunks if c.id not in packed_chunks_by_id]
            debug_info = {
                "original_query": user_query,
                "retrieval_query": retrieval_query,
                "retrieved_chunks": [c.to_dict() for c in retrieved_chunks],
                "similarity_scores": {c.id: c.similarity for c in retrieved_chunks},
                "selected_chunks": [c.to_dict() for c in packed_context.packed_chunks],
                "dropped_chunks": dropped,
                "estimated_context_tokens": packed_context.total_tokens,
                "model_response": raw_json_str,
                "validated_citations": [c.to_dict() for c in verified_citations]
            }

        return RAGResponse(
            answer=answer_text,
            citations=verified_citations,
            grounded=is_grounded and bool(verified_citations or "couldn't find" in answer_text.lower()),
            retrieved_chunks_count=len(retrieved_chunks),
            context_tokens=packed_context.total_tokens,
            rewritten_query=retrieval_query if retrieval_query != user_query else None,
            debug_info=debug_info
        )

    def _rewrite_query_with_history(
        self,
        user_query: str,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        if not conversation_history or len(user_query.split()) > 7:
            return user_query

        # Conversational short follow-up detection (e.g. "What about 3NF?")
        prev_user_msgs = [m.get("content", "") for m in conversation_history if m.get("role") == "user"]
        if not prev_user_msgs:
            return user_query

        last_topic = prev_user_msgs[-1]
        prompt = (
            f"Given the previous question: '{last_topic}'\n"
            f"And the follow-up question: '{user_query}'\n"
            f"Rewrite the follow-up question into a single standalone search query that includes full topic context.\n"
            f"Output ONLY the standalone search query string."
        )

        return self._call_gemini_simple(prompt, default_fallback=f"{last_topic} {user_query}")

    def _call_gemini_simple(self, prompt: str, default_fallback: str) -> str:
        if (
            settings.GEMINI_API_KEY
            and not settings.GEMINI_API_KEY.startswith("mock")
        ):
            import google.generativeai as genai
            genai.configure(api_key=settings.GEMINI_API_KEY)
            for model_name in GEMINI_FALLBACK_MODELS:
                try:
                    model = genai.GenerativeModel(model_name)
                    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                        future = executor.submit(model.generate_content, prompt)
                        response = future.result(timeout=8.0)
                        if response and response.text:
                            return response.text.strip()
                except Exception as e:
                    err_str = str(e)
                    if "429" in err_str or "quota" in err_str.lower() or "exhausted" in err_str.lower():
                        logger.warning(f"Simple call: {model_name} rate limited, trying next...")
                        time.sleep(1)
                        continue
                    logger.warning(f"Simple Gemini call failed with {model_name}: {e}")
                    continue

        return default_fallback

    def _call_gemini(self, prompt: str, packed_context: Optional[PackedContext] = None) -> str:
        if (
            settings.GEMINI_API_KEY
            and not settings.GEMINI_API_KEY.startswith("mock")
        ):
            import google.generativeai as genai
            genai.configure(api_key=settings.GEMINI_API_KEY)

            for model_name in GEMINI_FALLBACK_MODELS:
                try:
                    model = genai.GenerativeModel(model_name)
                    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                        future = executor.submit(model.generate_content, prompt)
                        response = future.result(timeout=30.0)
                        if response and response.text:
                            text = response.text.strip()
                            # Skip if model returned meta-commentary instead of answer
                            # (Gemma models sometimes output 'Topic: X. Constraint: Y.' as response)
                            if text and len(text) > 20:
                                return text
                except Exception as e:
                    err_str = str(e)
                    if "429" in err_str or "quota" in err_str.lower() or "exhausted" in err_str.lower():
                        logger.warning(f"Gemini model {model_name} rate limited (429), trying fallback model...")
                        time.sleep(2)  # Brief wait before next model
                        continue
                    elif "not found" in err_str.lower() or "404" in err_str or "no longer available" in err_str.lower():
                        logger.warning(f"Gemini model {model_name} not available, skipping...")
                        continue
                    logger.error(f"Gemini LLM call failed ({model_name}): {e}")
                    continue

        # All models exhausted - use top chunk content as readable fallback
        mock_cits = []
        answer_summary = "I'm currently unable to reach the AI service. Please try again in a moment."
        if packed_context and packed_context.packed_chunks:
            top_chunk = packed_context.packed_chunks[0]
            mock_cits = [{"chunk_id": top_chunk.id, "reason": "Primary retrieved context source"}]
            answer_summary = (
                f"Here is what your notes say about this topic:\n\n"
                f"{top_chunk.content}"
            )

        return json.dumps({
            "answer": answer_summary,
            "citations": mock_cits,
            "grounded": bool(mock_cits)
        })

    def _parse_structured_response(self, raw_str: str, packed_context: Optional[PackedContext]):
        try:
            cleaned = raw_str.strip()
            # Strip markdown code fences if present
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            elif cleaned.startswith("```"):
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
            # The model returned raw text (not JSON) - treat it as the answer directly
            clean_ans = raw_str.strip()
            default_citations = []
            if packed_context and packed_context.packed_chunks:
                default_citations = [{"chunk_id": packed_context.packed_chunks[0].id, "reason": "Top matching context"}]
            return clean_ans, default_citations, True
