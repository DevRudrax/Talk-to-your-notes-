# ARCHITECTURE DOCUMENTATION

## Overview

**Talk to Your Notes** is a private, production-ready AI knowledge workspace built using Retrieval-Augmented Generation (RAG). It integrates the **Stitch UI ("Quiet Intelligence" design system)** with a Python FastAPI backend, Supabase (PostgreSQL + pgvector + Auth + Storage), and Google Gemini LLM / Embeddings.

```mermaid
graph TD
    Client["Stitch UI (React + TypeScript + Tailwind)"] -->|HTTPS / REST / SSE| API["FastAPI Backend Service"]
    Client -->|Auth Session / JWT| Auth["Supabase Auth"]
    
    API -->|Validate Token| Auth
    API -->|Database CRUD / RLS| DB[("Supabase PostgreSQL")]
    API -->|Vector Retrieval (RPC match_document_chunks)| Vector[("pgvector Index")]
    API -->|Private File Upload / Signed URLs| Storage["Supabase Storage (documents bucket)"]
    
    API -->|Embeddings API| GeminiEmb["Gemini Embeddings API"]
    API -->|Structured Grounded Generation| GeminiLLM["Gemini LLM (Gemini 1.5 / 2.0 / Flash)"]
```

## System Components

### 1. Frontend
- **Framework:** React + TypeScript + Tailwind CSS (Ported from Stitch HTML mockups)
- **Design System:** "Quiet Intelligence" (Geist font, minimal monochromatic palette `#fcf9f8`, `#2d5bff` accent, 4px-6px border radius, high density)
- **Key Views:**
  - Active Chat Workspace (Chat stream, context summary, source drawer)
  - Document Management (Upload dropzone, processing status list, re-index, delete)
  - Collections Overview (Collection filter, grouped notes)
  - Source Viewer (Document passage highlight by page & section)

### 2. Backend
- **Framework:** Python + FastAPI
- **Responsibilities:**
  - Authentication JWT verification middleware
  - Document processing pipeline (PDF extraction via PyMuPDF, Markdown/TXT structural parsing)
  - Hierarchical semantic chunking & metadata enrichment
  - `EmbeddingService` for vector embeddings
  - Vector retrieval & RPC function calls
  - `ContextPacker` for token budget enforcement
  - Grounded RAG prompt construction & Gemini API integration
  - Structured LLM output parsing & citation validation
  - Conversation history summarization & persistence

### 3. Database & Storage
- **Database:** Supabase PostgreSQL with `pgvector` extension enabled.
- **Security:** Strict Row Level Security (RLS) policies on all tables based on `auth.uid()`.
- **Storage:** Supabase Storage private bucket `documents` (`documents/{user_id}/{document_id}/original_file`).

### 4. Database Schema
- `profiles` (id, email, full_name, avatar_url, created_at, updated_at)
- `collections` (id, user_id, name, description, created_at, updated_at)
- `documents` (id, user_id, collection_id, file_name, file_type, storage_path, file_size, mime_type, page_count, status, processing_error, created_at, updated_at, indexed_at)
- `document_chunks` (id, document_id, user_id, content, chunk_index, page_number, section_title, parent_section, metadata, embedding, created_at)
- `conversations` (id, user_id, collection_id, title, conversation_summary, created_at, updated_at)
- `messages` (id, conversation_id, user_id, role, content, created_at)
- `message_sources` (id, message_id, chunk_id, similarity, rank, created_at)

### 5. Grounded RAG & Anti-Hallucination Pipeline
```text
User Question 
  │
  ├─► Optional Conversational Query Rewrite
  ├─► Embed Query (EmbeddingService)
  ├─► Vector Search via Supabase RPC match_document_chunks (user_id & collection_id enforced in SQL)
  ├─► Check Retrieval Similarity Threshold (If < threshold, trigger "Not Found" response)
  ├─► Deduplicate & Pack Bounded Context (ContextPacker within MAX_CONTEXT_TOKENS)
  ├─► Construct Grounded Gemini Prompt (System Instructions + Summary + Recent Messages + Bounded Context + Question)
  ├─► Gemini Structured JSON Output Generation (Answer + Array of Citation chunk_ids)
  ├─► Validate Citation Chunk IDs against Database (Drop fake/unretrieved IDs)
  ├─► Resolve Trusted Source Metadata (file_name, page_number, section_title)
  └─► Save & Stream Response with Verified Sources
```
