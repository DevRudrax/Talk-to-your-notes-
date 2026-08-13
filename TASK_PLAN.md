# TASK PLAN

## Phase 0 — Repository Analysis
- [x] Inspect project structure
- [x] Identify framework & existing UI mockups
- [x] Identify environment & system tools (Python, Node, npm)
- [x] Document architecture & design system (Quiet Intelligence)
- [x] Initialize persistent project memory files

## Phase 1 — Foundation & Project Setup
- [x] Initialize Git repository
- [x] Setup FastAPI backend project (`/backend` directory, virtual environment, `requirements.txt`, basic healthcheck endpoint)
- [x] Setup React + TypeScript + Tailwind frontend project (`/frontend` directory using Vite/Next.js and Quiet Intelligence theme)
- [x] Setup Environment Configuration (`.env.example`, `.env`)
- [x] Supabase client configuration (Auth, DB, Storage)

## Phase 2 — Supabase Database, Auth & Row Level Security
- [x] Create database migration scripts (`profiles`, `collections`, `documents`, `document_chunks`, `conversations`, `messages`, `message_sources`)
- [x] Configure `pgvector` extension and vector index
- [x] Create Supabase RPC function `match_document_chunks` with strict `user_id` & `collection_id` filtering
- [x] Implement Row Level Security (RLS) policies for all user-owned tables
- [x] Implement Backend Authentication middleware (validate JWT token from Supabase Auth)

## Phase 3 — Storage & Document Ingestion API
- [x] Create private Supabase Storage bucket `documents` with user isolation paths (`documents/{user_id}/{document_id}/original_file`)
- [x] Implement file upload API (`POST /api/documents/upload`) with strict validation (MIME, size <= 25MB, file extension)
- [x] Create Document record with status tracking state machine (`uploaded`, `processing`, `extracting`, `chunking`, `embedding`, `indexed`, `failed`, `deleted`)
- [x] Implement Document CRUD & re-index APIs (`GET /api/documents`, `GET /api/documents/:id`, `DELETE /api/documents/:id`, `POST /api/documents/:id/reindex`)

## Phase 4 — Modular Document Processing & Semantic Chunking
- [x] PDF text extraction with PyMuPDF (preserving page numbers, structure, headings)
- [x] Markdown & TXT parsing (structural parsing, preserving section headers)
- [x] Implement hierarchical semantic chunking (target 700-1000 tokens, 100-150 token overlap, attaching document_id, user_id, chunk_index, page_number, section_title, parent_section metadata)

## Phase 5 — Embeddings & Vector Database Storage
- [x] Implement modular `EmbeddingService` with retry and batching support (Gemini Embeddings API)
- [x] Store chunk embeddings into Supabase `document_chunks` table
- [x] Update document status to `indexed`

## Phase 6 — Retrieval Pipeline & Bounded ContextPacker
- [x] Implement vector retrieval with query normalization and optional conversational query rewriting
- [x] Implement `ContextPacker` (deduplication, overlap removal, ranking, token budget enforcement `MAX_CONTEXT_TOKENS`)
- [x] Implement retrieval threshold & "Not Found" safeguard

## Phase 7 — Grounded RAG, Gemini Generation & Anti-Hallucination Citations
- [x] Implement strict grounded system prompt for Gemini
- [x] Implement structured output contract (JSON response with answer & citation `chunk_id`s)
- [x] Implement backend citation validation & trusted source resolution (DB lookup for page/section display metadata)
- [x] Implement conversation history management (recent messages + compact summary)

## Phase 8 — Streaming Chat & Conversation Persistence
- [x] Implement streaming chat API (`POST /api/chat`)
- [x] Implement conversation management APIs (`GET /api/conversations`, `GET /api/conversations/:id`, `PATCH /api/conversations/:id`, `DELETE /api/conversations/:id`)
- [x] Implement message persistence (`messages` and `message_sources`)

## Phase 9 — UI Integration (Stitch UI + Real Functionality)
- [x] Port active chat workspace UI components with Quiet Intelligence design system
- [x] Port document management UI components (upload dropzone, list, status badges, actions)
- [x] Port collections overview UI components
- [x] Implement source panel viewer with passage highlighting
- [x] Connect frontend state to real backend APIs & Supabase Auth

## Phase 10 — Collections, Search & Advanced Document Viewer
- [x] Implement collections CRUD & filtering in UI/backend
- [x] Connect document viewer with source citation jump & highlight

## Phase 11 — Security Hardening & Isolation Testing
- [x] Test cross-user isolation (User A vs User B for documents, chunks, chats, vectors)
- [x] Ensure `SUPABASE_SERVICE_ROLE_KEY` is backend-only
- [x] Add rate limiting on upload, chat, and reindex endpoints

## Phase 12 — Testing & RAG Evaluation Suite
- [x] Write backend unit tests (chunking, parsing, context packing, citation validation)
- [x] Write integration & security tests
- [x] Build & run RAG Evaluation suite (groundedness, citation accuracy, not-found behavior)

## Phase 13 — Production Ready Verification & Documentation
- [x] Build production frontend & backend bundles
- [x] Final end-to-end verification against completion criteria
- [x] Update deployment & usage documentation
