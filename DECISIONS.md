# ARCHITECTURAL DECISIONS

## Decision 001: Supabase pgvector for Vector Storage
- **Status:** Approved
- **Reason:** Keeps relational data, document records, and vector embeddings in a single unified managed PostgreSQL instance with robust SQL Row Level Security.
- **Alternatives Considered:** ChromaDB, Pinecone, Qdrant.

## Decision 002: Modular Python FastAPI Backend
- **Status:** Approved
- **Reason:** Provides high performance, native async support, robust type safety via Pydantic, and access to superior document processing libraries (PyMuPDF, LangChain/LlamaIndex chunkers if needed).
- **Alternatives Considered:** Node.js Express/Next.js API routes.

## Decision 003: "Quiet Intelligence" Design System Preservation
- **Status:** Approved
- **Reason:** The provided Stitch UI mockup is the visual source of truth. The React frontend will mirror the exact CSS tokens, Geist typography, and minimal 3-column layout defined in `DESIGN.md`.
- **Alternatives Considered:** Generic Tailwind dashboard templates.

## Decision 004: Strict Backend-Validated Structured Citation Contract
- **Status:** Approved
- **Reason:** Prevent citation hallucination by requiring Gemini to return raw `chunk_id` UUIDs in structured JSON. The backend verifies that every `chunk_id` existed in the retrieved set before attaching trusted file/page metadata from the database.
- **Alternatives Considered:** Free-form text markdown citations (e.g. `[1]`, `[DBMS.pdf, p. 42]`).
