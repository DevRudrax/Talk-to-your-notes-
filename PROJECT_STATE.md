# PROJECT STATE — Talk to Your Notes (RAG Production Application)

## Current Phase
**Phase 10 — Production Completion & Master Specification Compliance**

## System Architecture
- **Frontend**: React + Vite + TypeScript (Stitch UI preserved, Vercel-ready with `vercel.json` SPA rewrites).
- **Backend**: FastAPI (Python 3.12) running on port 8001.
- **Database**: Supabase PostgreSQL with `pgvector` HNSW vector index (`vector(768)`).
- **Storage**: Supabase Private Bucket `documents`.
- **LLM**: Google Gemini `gemini-flash-latest` (Generation) & `gemini-embedding-001` (Embeddings).

## Completed Features
- [x] Grounded RAG with strict citation validation & anti-hallucination contract.
- [x] Hierarchical whole-document summarization service for "summarise the entire notes" queries.
- [x] Conversational Query Rewriting for follow-up questions ("What about 3NF?").
- [x] Developer RAG Debug Mode path (`POST /api/chat/debug`).
- [x] Persistent chat history and Delete Chat with interactive confirmation modal.
- [x] One-click document re-indexing endpoint (`POST /api/documents/{id}/reindex`).
- [x] Complete pytest evaluation suite & Vite production build passing with 0 errors.

## Database & API Status
- **Supabase Project URL**: `https://nmnzsyjbzkvfxsmddosh.supabase.co`
- **Tables**: `profiles`, `collections`, `documents`, `document_chunks`, `conversations`, `messages`, `message_sources`.
- **All backend tests**: 10/10 PASSED.
- **Frontend build**: PASSED (0 errors).
