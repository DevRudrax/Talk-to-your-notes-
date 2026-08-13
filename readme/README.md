# Talk to Your Notes

> Production-oriented RAG knowledge workspace built from the Stitch UI mockup and intended for Antigravity autonomous implementation.

## 0. PURPOSE OF THIS FILE

This README is the **persistent project context document** for the coding agent.

The conversation prompt is temporary. The repository is persistent.

When context is lost, compressed, or uncertain, the agent MUST read this file before making architectural or implementation decisions.

**Filesystem > project documentation > conversation memory.**

Do not guess missing project state.

---

# 1. PRODUCT IDENTITY

## Product

**Talk to Your Notes**

## Product Type

Private AI knowledge workspace using Retrieval-Augmented Generation (RAG).

## Core User Journey

```text
Create account
    ↓
Upload PDF / Markdown / TXT
    ↓
Store original file privately
    ↓
Extract text
    ↓
Parse structure
    ↓
Semantic chunking
    ↓
Generate embeddings
    ↓
Store chunks + vectors
    ↓
Document becomes indexed
    ↓
User asks a question
    ↓
Embed query
    ↓
Retrieve relevant chunks
    ↓
Filter by user / collection
    ↓
Pack bounded context
    ↓
Gemini generates grounded answer
    ↓
Validate citations
    ↓
Resolve trusted source metadata
    ↓
Display answer + sources
```

The application is **not a generic chatbot**.

Its primary purpose is answering questions from the user's indexed knowledge base.

---

# 2. DESIGN SOURCE OF TRUTH

The original UI was generated with Stitch and is located in the project archive supplied with this project.

Available Stitch screens:

```text
mobile_chat_workspace/
active_chat_workspace/
document_management/
collections_overview/
quiet_intelligence/DESIGN.md
```

The UI design system is called:

**Quiet Intelligence**

The existing Stitch UI is the **visual source of truth**.

Do NOT replace it with a generic dashboard.

Do NOT redesign the product during backend integration.

The goal is:

```text
Existing Stitch UI
        +
Real production functionality
        =
Talk to Your Notes
```

---

# 3. DESIGN PRINCIPLES

The product should feel:

- Calm
- Intelligent
- Fast
- Private
- Trustworthy
- Content-first
- Minimal
- Highly polished

Avoid:

- Purple AI gradients
- Neon colors
- Excessive rounded cards
- Glassmorphism
- Giant hero sections
- Random illustrations
- Decorative dashboard widgets
- Fake analytics
- Excessive shadows
- Unnecessary animations

The UI should feel closer to a refined AI/productivity application than a template-generated SaaS dashboard.

---

# 4. TECHNOLOGY DECISIONS

These are the default architectural decisions.

## Frontend

Use the framework already present in the Stitch-generated application.

Preferred ecosystem:

- React
- TypeScript
- Tailwind CSS

Do not migrate frameworks unless there is a strong technical reason.

## Backend

**Python + FastAPI**

Responsible for:

- Authentication validation
- Document processing
- Chunking
- Embeddings
- Retrieval
- Context packing
- RAG orchestration
- Gemini calls
- Citation validation
- Source resolution

## Database

**Supabase PostgreSQL**

## Vector Search

**Supabase pgvector**

Do not introduce ChromaDB for production unless explicitly approved.

## File Storage

**Supabase Storage** with private buckets.

## Authentication

**Supabase Auth**

## LLM

**Google Gemini API**

The exact model must be configurable through environment variables.

## Embeddings

Use a configurable embedding provider, initially preferably Gemini embeddings.

The embedding implementation must be abstracted behind an embedding service.

---

# 5. ARCHITECTURE

```text
                         ┌─────────────────────┐
                         │      Stitch UI       │
                         │ React / TypeScript   │
                         └──────────┬──────────┘
                                    │ HTTPS
                                    ▼
                         ┌─────────────────────┐
                         │       FastAPI       │
                         │       Backend       │
                         └───────┬─────┬───────┘
                                 │     │
                  ┌──────────────┘     └──────────────┐
                  ▼                                   ▼
        ┌──────────────────┐                 ┌──────────────────┐
        │ Supabase Postgres│                 │ Gemini API       │
        │ + pgvector       │                 │ LLM + Embeddings │
        └────────┬─────────┘                 └──────────────────┘
                 │
                 ▼
        ┌──────────────────┐
        │ Supabase Storage │
        │ Private files    │
        └──────────────────┘
```

---

# 6. REPOSITORY CONTEXT RULES

The agent MUST use the repository as persistent memory.

Required persistent files:

```text
PROJECT_STATE.md
ARCHITECTURE.md
TASK_PLAN.md
DECISIONS.md
TEST_STATUS.md
README.md
```

If any are missing, create them.

Never rely on statements such as:

> "I created this earlier."

Verify the filesystem.

---

# 7. CONTEXT WINDOW SAFETY

This project must be developed using bounded context.

Never load the entire repository into the model context unnecessarily.

Use:

```text
Discover
  ↓
Select relevant files
  ↓
Inspect only relevant sections
  ↓
Implement small unit
  ↓
Test
  ↓
Checkpoint
  ↓
Update project state
  ↓
Continue
```

If a source file is large:

1. Identify the relevant function/component.
2. Read only the required region.
3. Make the smallest safe change.
4. Re-read the changed region.
5. Run tests.

Do not rewrite large files from memory.

---

# 8. CONTEXT RECOVERY

If the agent loses context or becomes uncertain:

STOP implementation temporarily.

Read, in this order:

```text
README.md
PROJECT_STATE.md
TASK_PLAN.md
ARCHITECTURE.md
DECISIONS.md
TEST_STATUS.md
```

Then inspect the actual relevant source files and git status.

Never reconstruct missing requirements from memory.

---

# 9. DATABASE MODEL

Minimum tables:

```text
profiles
collections
documents
document_chunks
conversations
messages
message_sources
```

## profiles

```text
id
email
full_name
avatar_url
created_at
updated_at
```

## collections

```text
id
user_id
name
description
created_at
updated_at
```

## documents

```text
id
user_id
collection_id
file_name
file_type
storage_path
file_size
mime_type
page_count
status
processing_error
created_at
updated_at
indexed_at
```

Possible document states:

```text
uploaded
processing
extracting
chunking
embedding
indexed
failed
deleted
```

## document_chunks

```text
id
document_id
user_id
content
chunk_index
page_number
section_title
parent_section
metadata
embedding
created_at
```

## conversations

```text
id
user_id
collection_id
title
conversation_summary
created_at
updated_at
```

## messages

```text
id
conversation_id
user_id
role
content
created_at
```

## message_sources

```text
id
message_id
chunk_id
similarity
rank
created_at
```

Use migrations. Do not rely only on manual dashboard configuration.

---

# 10. SECURITY MODEL

Every user-owned resource must be isolated by authenticated user identity.

Supabase Row Level Security is mandatory.

User A must never access User B's:

- Documents
- Document chunks
- Embeddings
- Conversations
- Messages
- Collections
- Source references

The backend must also validate authorization.

Never trust a `user_id` supplied by the frontend.

Derive identity from the authenticated Supabase token/session.

---

# 11. STORAGE MODEL

Use a private Supabase Storage bucket.

Preferred path:

```text
documents/{user_id}/{document_id}/original_file
```

Never expose the service-role key to frontend code.

Never make the entire document bucket public merely to simplify development.

Use signed URLs when direct file access is required.

---

# 12. DOCUMENT INGESTION

Supported file types:

```text
PDF
MD
MARKDOWN
TXT
```

Suggested maximum file size:

```text
25 MB
```

Make limits configurable.

Validate:

- Extension
- MIME type
- File size
- Empty files
- Corrupt files

Do not trust browser-provided MIME type alone.

---

# 13. DOCUMENT PROCESSING PIPELINE

```text
Upload
  ↓
Validate
  ↓
Store in Supabase Storage
  ↓
Create document record
  ↓
Extract text
  ↓
Normalize text
  ↓
Detect pages/headings
  ↓
Semantic chunking
  ↓
Attach metadata
  ↓
Generate embeddings
  ↓
Store chunks + embeddings
  ↓
Mark indexed
```

Do not create one giant processing function.

Use separate services for:

- Extraction
- Parsing
- Chunking
- Embeddings
- Storage
- Indexing

---

# 14. PDF PROCESSING

Preferred library:

**PyMuPDF**

Preserve:

- Page number
- Text order
- Paragraph boundaries where possible
- Headings where possible

Every chunk originating from a PDF must retain its page number whenever available.

---

# 15. MARKDOWN/TXT PROCESSING

Markdown should preserve structure:

```text
Heading
Subheading
Paragraph
List
Code block
```

Use headings to improve chunk boundaries.

Example:

```text
# Normalization

## First Normal Form
...

## Second Normal Form
...

## Third Normal Form
...
```

The chunk metadata should retain the relevant section title.

---

# 16. CHUNKING STRATEGY

Chunking is a core RAG requirement.

Do NOT use naive fixed-character splitting as the primary strategy.

Preferred hierarchy:

```text
Document
  ↓
Page
  ↓
Heading
  ↓
Subheading
  ↓
Paragraph
  ↓
Sentence
```

Target approximately:

```text
700–1000 tokens
```

Overlap approximately:

```text
100–150 tokens
```

Make both configurable.

Keep related semantic content together whenever possible.

Every chunk must retain enough metadata to reconstruct its origin.

---

# 17. EMBEDDING MODEL

Create an abstraction:

```text
EmbeddingService
```

Required operations:

```text
embed_text()
embed_documents()
```

Provider-specific code must not be scattered throughout the application.

The selected embedding dimension must match the pgvector column dimension exactly.

Never guess the dimension.

---

# 18. VECTOR RETRIEVAL

Use Supabase pgvector.

Create a PostgreSQL RPC function similar to:

```text
match_document_chunks(
    query_embedding,
    match_count,
    similarity_threshold,
    user_id,
    collection_id
)
```

The SQL function itself must enforce ownership.

Never retrieve all vectors and filter users afterward.

---

# 19. RAG PIPELINE

```text
User Question
      ↓
Query normalization / optional rewrite
      ↓
Query embedding
      ↓
pgvector search
      ↓
User + collection filtering
      ↓
Similarity threshold
      ↓
Top K retrieval
      ↓
Deduplication
      ↓
Context packing
      ↓
Bounded context
      ↓
Gemini
      ↓
Structured response
      ↓
Citation validation
      ↓
Source resolution
      ↓
Answer + sources
```

Default retrieval count:

```text
TOP_K = 5
```

Make configurable.

---

# 20. CONTEXT BUDGET

Never send unlimited retrieved text to the LLM.

Create a dedicated `ContextPacker`.

Responsibilities:

```text
Retrieved chunks
  ↓
Remove duplicates
  ↓
Remove highly overlapping chunks
  ↓
Rank
  ↓
Respect token budget
  ↓
Format source identifiers
  ↓
Return final context
```

Use a configurable:

```text
MAX_CONTEXT_TOKENS
```

The system must estimate request size before calling Gemini.

If context is too large, reduce retrieved chunks rather than exceeding the model limit.

---

# 21. CONVERSATION CONTEXT

Never send an unlimited conversation history.

Use:

```text
Conversation summary
+
Recent messages
+
Current retrieved document context
+
Current user question
```

For long conversations, maintain a compact summary.

Only summarize when needed.

Do not repeatedly summarize the full conversation on every message.

---

# 22. GROUNDED ANSWERS

The RAG assistant must answer from retrieved context.

Core rules:

- Do not invent facts.
- Do not invent citations.
- Do not invent page numbers.
- Do not invent section names.
- Do not claim to have read unretrieved content.
- If evidence is insufficient, say so.
- If the question is unrelated to indexed notes, explain the limitation.

If no chunk meets the retrieval threshold, prefer a controlled not-found response instead of hallucinating.

---

# 23. CITATION ARCHITECTURE

This is a critical anti-hallucination mechanism.

The LLM should reference **chunk IDs**, not arbitrary filenames or page numbers.

Preferred structured response:

```json
{
  "answer": "...",
  "citations": [
    {
      "chunk_id": "...",
      "reason": "supports definition"
    }
  ],
  "grounded": true
}
```

Backend validates every chunk ID.

Then:

```text
chunk_id
  ↓
database
  ↓
document
  ↓
page
  ↓
section
  ↓
trusted citation metadata
```

The model must never be allowed to invent citation metadata.

---

# 24. QUERY REWRITING

Optional query rewriting may be used for conversational follow-ups.

Example:

```text
User: What is normalization?
User: What about 3NF?
```

Retrieval query may become:

```text
What is Third Normal Form (3NF) in database normalization?
```

Store/retain the original user message.

Use the rewritten query only for retrieval.

---

# 25. MULTI-DOCUMENT QUESTIONS

Support questions that require multiple documents.

Example:

```text
Compare the definition of normalization in DBMS.pdf and Database Notes.pdf.
```

Retrieval can return chunks from multiple documents.

Each claim should retain correct source attribution.

---

# 26. COLLECTION FILTERING

When a collection is selected:

```text
user_id = current_user
AND collection_id = selected_collection
```

When no collection is selected:

```text
user_id = current_user
```

Never bypass the user filter.

---

# 27. API CONTRACT

Core endpoints:

```text
POST   /api/documents/upload
GET    /api/documents
GET    /api/documents/{id}
DELETE /api/documents/{id}
POST   /api/documents/{id}/reindex

POST   /api/chat

GET    /api/conversations
GET    /api/conversations/{id}
PATCH  /api/conversations/{id}
DELETE /api/conversations/{id}

GET    /api/collections
POST   /api/collections
PATCH  /api/collections/{id}
DELETE /api/collections/{id}
```

Use Pydantic request and response schemas.

---

# 28. FRONTEND REQUIREMENT

Integrate APIs into the existing Stitch UI.

Replace mock data with real data.

Preserve existing visual design.

Important UI states:

```text
Loading
Empty
Uploading
Extracting
Chunking
Embedding
Indexed
Failed
Sending
Retrieving
Generating
Completed
Error
```

Never fake processing progress.

---

# 29. CHAT UX

The active chat should support:

- New chat
- Persistent chat history
- Streaming response
- Source citations
- Source panel
- Copy response
- Regenerate where supported
- Rename conversation
- Delete conversation

The chat should remain visually faithful to Stitch.

---

# 30. DOCUMENT UX

Support:

- Upload
- Search
- Open
- Rename
- Delete
- Favorite
- Re-index
- Move to collection

Document status must reflect the backend state.

---

# 31. SOURCE VIEWER

When a source is clicked:

```text
Source
  ↓
Document
  ↓
Relevant page/section
  ↓
Highlighted passage
```

The highlighted passage must come from the stored chunk/document content.

Do not fabricate highlighted text.

---

# 32. AUTHENTICATION

Use Supabase Auth.

Flow:

```text
Browser session
  ↓
Supabase access token
  ↓
FastAPI
  ↓
Token validation
  ↓
Authenticated user
```

Never accept client-provided user IDs as authoritative.

---

# 33. ENVIRONMENT VARIABLES

Create `.env.example`.

Expected variables include:

```text
SUPABASE_URL=
SUPABASE_PUBLISHABLE_KEY=
SUPABASE_SERVICE_ROLE_KEY=

GEMINI_API_KEY=
LLM_MODEL=
EMBEDDING_MODEL=

FRONTEND_URL=
BACKEND_URL=

MAX_FILE_SIZE=
TOP_K=
SIMILARITY_THRESHOLD=
MAX_CONTEXT_TOKENS=
```

Actual secrets must never be committed.

---

# 34. SERVICE ROLE RULE

`SUPABASE_SERVICE_ROLE_KEY` is backend-only.

Never expose it in:

- React
- Next.js public environment variables
- Browser bundles
- Client-side code

---

# 35. ERROR HANDLING

Never show stack traces to users.

Server logs should contain technical details.

Frontend should receive safe actionable errors.

Example:

```text
Couldn't index this document.
Try uploading the file again.
```

---

# 36. OBSERVABILITY

Use structured logging.

Useful metadata:

```text
request_id
user_id
document_id
conversation_id
processing_time
retrieval_latency
retrieved_count
context_token_count
llm_latency
error_type
```

Never log secrets.

Avoid unnecessarily logging private document contents.

---

# 37. TESTING REQUIREMENTS

Tests must be written alongside implementation.

Minimum coverage areas:

### Unit

- PDF extraction
- Markdown parsing
- Chunking
- Metadata extraction
- Context packing
- Query rewriting
- Citation validation

### Integration

```text
upload
→ extraction
→ chunking
→ embedding
→ storage
```

### RAG

```text
question
→ retrieval
→ context
→ answer
→ citation validation
```

### Security

Verify:

```text
User A cannot access User B
```

### E2E

```text
signup
→ upload
→ index
→ ask
→ answer
→ source
→ document viewer
```

---

# 38. RAG EVALUATION

Create a small evaluation dataset containing:

```text
question
expected_document
expected_section
expected_concept
```

Evaluate:

- Retrieval relevance
- Source correctness
- Groundedness
- Not-found behavior
- Collection filtering
- Multi-document retrieval

Do not claim RAG quality without testing it.

---

# 39. PERFORMANCE

Prefer simple production-safe optimization.

Requirements:

- Batch embeddings where supported
- Paginate lists
- Use database indexes
- Use appropriate pgvector indexes for the selected scale
- Stream LLM responses
- Avoid repeated embeddings
- Avoid loading whole documents into the LLM
- Avoid unnecessary queries

Do not introduce Redis, Kafka, Celery, Kubernetes, or other infrastructure unless actual requirements justify them.

---

# 40. RATE LIMITING

Protect expensive endpoints:

```text
chat
upload
reindex
embedding
```

Limits should be configurable.

Use bounded retries with exponential backoff for external API failures.

---

# 41. DEPLOYMENT TARGET

Suggested deployment:

```text
Frontend → Vercel or equivalent
Backend  → Render / Railway / Fly.io / equivalent
Database → Supabase
Storage  → Supabase Storage
Vectors  → Supabase pgvector
LLM      → Gemini
```

The application must still work locally without paid infrastructure.

---

# 42. REQUIRED PROJECT STATE

`PROJECT_STATE.md` must always answer:

```text
What phase are we in?
What was last completed?
What is currently being implemented?
What files matter?
What is broken?
What tests pass?
What remains?
```

Keep it short enough to read quickly.

---

# 43. TASK EXECUTION RULE

Work in coherent phases.

Recommended order:

```text
Phase 0
Repository inspection

Phase 1
Project foundation

Phase 2
Supabase + Auth + RLS

Phase 3
Storage + document upload

Phase 4
Extraction + chunking

Phase 5
Embeddings + pgvector

Phase 6
Retrieval + ContextPacker

Phase 7
Gemini RAG + citations

Phase 8
Chat persistence + streaming

Phase 9
UI integration

Phase 10
Collections + document viewer + search

Phase 11
Security hardening

Phase 12
Testing + evaluation

Phase 13
Deployment + documentation
```

Do not jump randomly between phases.

---

# 44. PHASE CHECKPOINT

At the end of every phase:

```text
1. Run tests
2. Run type checks
3. Run lint
4. Build application
5. Inspect git diff
6. Update PROJECT_STATE.md
7. Update TASK_PLAN.md
8. Update TEST_STATUS.md
9. Record architectural decisions
10. Verify no existing functionality regressed
```

Only then continue.

---

# 45. GIT CHECKPOINTS

Where git is available, create logical commits.

Examples:

```text
feat: establish project foundation
feat: add supabase schema and rls
feat: implement document ingestion
feat: implement semantic chunking
feat: add pgvector retrieval
feat: implement grounded rag
feat: add citation validation
feat: connect chat interface
feat: implement document management
fix: enforce document ownership
 test: add rag evaluation suite
```

Do not commit knowingly broken phases as complete.

---

# 46. COMPLETION CRITERIA

The application is not complete until this exact flow works:

```text
User creates account
      ↓
Uploads DBMS.pdf
      ↓
File stored privately
      ↓
Document record created
      ↓
Text extracted
      ↓
Semantic chunks created
      ↓
Embeddings generated
      ↓
Vectors stored in pgvector
      ↓
Document marked indexed
      ↓
User asks: "Explain 3NF"
      ↓
Question embedded
      ↓
Relevant chunks retrieved
      ↓
User/collection filter enforced
      ↓
Context bounded
      ↓
Gemini receives grounded context
      ↓
Structured answer generated
      ↓
Citation IDs validated
      ↓
Trusted source metadata resolved
      ↓
Answer displayed
      ↓
User clicks source
      ↓
Correct page/section opens
      ↓
Relevant passage is highlighted
```

---

# 47. NON-NEGOTIABLE RULES

1. **Do not redesign the Stitch UI.**
2. **Do not expose secrets.**
3. **Do not bypass RLS.**
4. **Do not trust client-provided user IDs.**
5. **Do not send entire documents to Gemini.**
6. **Do not send unlimited chat history to Gemini.**
7. **Do not use naive chunking as the only strategy.**
8. **Do not invent citations.**
9. **Do not let the LLM invent source metadata.**
10. **Do not retrieve vectors across users and filter afterward.**
11. **Do not fake upload/indexing progress.**
12. **Do not claim a feature works without testing it.**
13. **Do not rewrite large files from memory.**
14. **Do not load the entire repository into context unnecessarily.**
15. **Do not guess when context is missing.**
16. **Use the filesystem as persistent memory.**
17. **Checkpoint after every coherent phase.**
18. **If uncertain, inspect the repository before acting.**

---

# 48. FINAL AGENT MANTRA

```text
The context window is temporary.
The repository is persistent.

Inspect before assuming.
Chunk before loading.
Implement before expanding.
Test before claiming.
Checkpoint before continuing.

Never hallucinate project state.
Never hallucinate source citations.
Never hallucinate requirements.
```

Build **Talk to Your Notes** as a real production application while preserving the existing Stitch design exactly where practical.
