# TALK TO YOUR NOTES
## Antigravity Production Repair, RAG Accuracy & Full-Stack Integration Specification

> This README is the persistent execution context for Antigravity.
> The repository/filesystem is the source of truth. Conversation context is temporary.

---

# 1. MISSION

Transform the existing **Talk to Your Notes** application from a partially working prototype into a reliable, production-ready RAG web application.

The Stitch-generated UI already exists and must be preserved.

Primary goals:

- Improve RAG answer accuracy.
- Improve retrieval and context selection.
- Implement proper whole-document summarization.
- Prevent hallucinated citations.
- Persist chat history in Supabase.
- Add reliable chat deletion.
- Make every visible feature and button functional.
- Connect frontend and backend properly.
- Connect Supabase Auth, PostgreSQL, Storage, and pgvector.
- Add security, RLS, validation, testing, and error handling.
- Prepare the frontend for Vercel.
- Prepare the backend for an appropriate production host.
- Verify the GitHub repository only when a real push succeeds.

This is a **repair, integration, testing, and productionization task**.

Do NOT rebuild the application from scratch.

---

# 2. NON-NEGOTIABLE RULES

## Preserve the existing UI

The existing Stitch UI is the visual source of truth.

Do not unnecessarily redesign:

- Layout
- Typography
- Colors
- Spacing
- Sidebar
- Chat workspace
- Documents
- Collections
- Sources
- Responsive behavior
- Existing visual language

Goal:

**Existing Stitch UI + reliable production functionality**

not a new design.

## Do not blindly rewrite code

Before modifying anything:

1. Inspect it.
2. Understand dependencies.
3. Identify what already works.
4. Modify the smallest appropriate area.
5. Test it.
6. Verify it.

Never replace working code without a reason.

## Never assume functionality exists

A visible button does not prove it works.
A displayed source does not prove it is correct.
A generated answer does not prove RAG is correct.
A Supabase client does not prove Supabase is actually connected.

Verify everything.

---

# 3. CONTEXT-WINDOW SAFETY

Antigravity must NOT attempt to keep the entire repository in its context window.

Use a **chunked, checkpoint-driven, container-first workflow**:

```text
Inspect
  ↓
Select relevant files
  ↓
Implement one coherent unit
  ↓
Test
  ↓
Verify
  ↓
Checkpoint
  ↓
Update project state
  ↓
Continue
```

The repository is persistent memory. Conversation context is temporary.

---

# 4. PERSISTENT PROJECT MEMORY

Maintain these files at repository root:

```text
README.md
PROJECT_STATE.md
ARCHITECTURE.md
TASK_PLAN.md
DECISIONS.md
TEST_STATUS.md
```

Keep `PROJECT_STATE.md` concise:

```markdown
# PROJECT STATE

## Current Phase
...

## Current Task
...

## Completed
- ...

## In Progress
- ...

## Blocked
- ...

## Known Issues
- ...

## Important Files
- ...

## Database Status
...

## Backend Status
...

## Frontend Status
...

## RAG Status
...

## Tests
...

## Last Verified
...
```

Do not turn it into a code dump.

---

# 5. CONTEXT RECOVERY PROTOCOL

If context becomes compressed, truncated, or uncertain:

**STOP IMPLEMENTING.**

Then:

```text
1. Read PROJECT_STATE.md
2. Read TASK_PLAN.md
3. Read relevant ARCHITECTURE.md sections
4. Read relevant DECISIONS.md entries
5. Inspect git status
6. Inspect current diff
7. Inspect only relevant source files
8. Run relevant tests
9. Continue
```

Never guess what previous work did.

---

# 6. CHUNKED REPOSITORY INSPECTION

Do not load the entire repository into context.

Inspect logical chunks.

## Chunk A — Frontend

Inspect the existing:

```text
package.json
src/
app/
pages/
components/
hooks/
lib/
services/
```

Determine:

- Framework
- Router
- State management
- API layer
- Supabase client
- Chat implementation
- Document implementation
- Collections
- Mock/hardcoded data
- Loading/error states

## Chunk B — Backend

Inspect relevant:

```text
backend/
api/
server/
services/
routes/
models/
schemas/
```

Determine:

- Backend framework
- Authentication
- API routes
- RAG pipeline
- Embeddings
- Vector search
- Gemini integration
- Document processing
- Persistence

## Chunk C — Database

Inspect:

```text
supabase/
migrations/
schema/
```

Determine:

- Tables
- Columns
- Foreign keys
- RLS
- pgvector
- RPC functions
- Storage

## Chunk D — Configuration

Inspect:

```text
.env
.env.example
vercel.json
vite.config.*
next.config.*
requirements.txt
package.json
```

Never expose secrets.

## Chunk E — Git

Run:

```bash
git status
git remote -v
git branch
```

Never claim GitHub was updated unless the push actually succeeds.

---

# 7. TARGET TECHNOLOGY

Use the existing framework where possible.

Preferred architecture:

### Frontend
- React
- TypeScript
- Existing Stitch UI
- Tailwind if already present

### Backend
- Python
- FastAPI

### Database
- Supabase PostgreSQL

### Vector search
- Supabase pgvector

### Storage
- Supabase Storage

### Authentication
- Supabase Auth

### LLM
- Google Gemini

### Embeddings
- Configurable embedding provider, preferably Gemini embeddings if compatible.

Do not introduce unnecessary infrastructure.

---

# 8. TARGET ARCHITECTURE

```text
                 ┌─────────────────────┐
                 │       Vercel        │
                 │   React Frontend    │
                 └──────────┬──────────┘
                            │ HTTPS
                            ▼
                 ┌─────────────────────┐
                 │      FastAPI        │
                 │       Backend       │
                 └──────────┬──────────┘
                            │
             ┌──────────────┼──────────────┐
             ▼              ▼              ▼
       ┌──────────┐   ┌──────────┐   ┌──────────┐
       │ Supabase │   │ pgvector │   │  Gemini  │
       │ Postgres │   │ Retrieval│   │   LLM    │
       └────┬─────┘   └──────────┘   └──────────┘
            │
            ▼
       ┌──────────┐
       │ Supabase │
       │ Storage  │
       └──────────┘
```

For heavy PDF processing, do not force long-running work into Vercel serverless functions if that causes timeout or memory problems.

Frontend should be Vercel-compatible.

Backend may be deployed separately to a suitable Python host.

---

# 9. DATABASE

Use migration files.

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

## documents

Use appropriate fields including:

```text
id
user_id
collection_id
file_name
file_type
mime_type
file_size
storage_path
page_count
status
processing_error
created_at
updated_at
indexed_at
```

Statuses should represent actual state:

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
summary
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

Use foreign keys and safe cascading behavior.

---

# 10. SUPABASE SECURITY

Implement strict Row Level Security.

A user must never access another user's:

- Documents
- Chunks
- Embeddings
- Conversations
- Messages
- Collections
- Source relationships

Test cross-user isolation explicitly.

The authenticated user identity must come from the validated Supabase session/token.

Never trust a browser-supplied `user_id`.

---

# 11. SUPABASE STORAGE

Use a private bucket:

```text
documents/
    USER_ID/
        DOCUMENT_ID/
            original_file
```

Use signed URLs for private files.

Never expose:

```text
SUPABASE_SERVICE_ROLE_KEY
```

to browser code.

---

# 12. PRIMARY ISSUE: RAG ACCURACY

The most important problem is answer quality.

Do not solve it only by changing the prompt.

Audit:

```text
User question
↓
Query processing
↓
Query embedding
↓
Vector search
↓
Filtering
↓
Ranking
↓
Deduplication
↓
Context packing
↓
Gemini
↓
Structured output
↓
Citation validation
↓
Trusted source resolution
↓
Frontend
```

Trace at least one real question end-to-end before making major changes.

---

# 13. DOCUMENT INGESTION

Implement:

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
Normalize
 ↓
Parse structure
 ↓
Chunk
 ↓
Generate embeddings
 ↓
Store chunks + vectors
 ↓
Mark indexed
```

Each stage needs explicit error handling.

Do not create one giant processing function.

---

# 14. FILE SUPPORT

Support:

```text
PDF
TXT
MD
MARKDOWN
```

Validate:

- Extension
- MIME type
- File size
- Empty files
- Corrupted files

Use a configurable limit, initially around 25 MB.

---

# 15. PDF EXTRACTION

Use a reliable parser such as PyMuPDF if compatible with the existing backend.

Preserve:

- Page number
- Text order
- Paragraph boundaries
- Headings where possible

Handle:

- Repeated headers
- Repeated footers
- Broken lines
- Empty pages
- Multi-page sections
- Tables where reasonably possible

Do not embed obvious extraction noise.

---

# 16. SEMANTIC CHUNKING

Chunking is a core RAG feature.

Do NOT use naive fixed-character slicing.

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

Overlap:

```text
100–150 tokens
```

Make both configurable.

Do not split important concepts unnecessarily.

---

# 17. CHUNK METADATA

Every chunk must retain:

```text
chunk_id
document_id
user_id
chunk_index
page_number
section_title
file_name
content
```

Optional:

```text
parent_section
heading_path
metadata
```

This metadata is required for trustworthy citations.

---

# 18. EMBEDDING SERVICE

Create:

```text
EmbeddingService
```

with methods such as:

```text
embed_text()
embed_documents()
```

Keep provider-specific code inside this service.

Implement:

- Batching where supported
- Limited retries
- Error handling
- Configurable model
- No duplicate embedding of unchanged chunks

---

# 19. VECTOR RETRIEVAL

Use Supabase pgvector.

Create an RPC such as:

```text
match_document_chunks(...)
```

Support:

```text
query_embedding
match_count
similarity_threshold
user_id
collection_id
```

The SQL function itself must enforce ownership.

Never retrieve all vectors and filter them later in application code.

---

# 20. RETRIEVAL QUALITY

Do not blindly assume top-K is good context.

Pipeline:

```text
Vector retrieval
 ↓
Metadata filtering
 ↓
Similarity threshold
 ↓
Deduplication
 ↓
Diversity
 ↓
Ranking
 ↓
Context packing
```

Start around:

```text
top_k = 5
```

and test alternatives such as 8 and 10.

Do not increase top-K indefinitely.

---

# 21. HYBRID SEARCH

If practical with the existing architecture, implement:

```text
Semantic vector search
+
Keyword/full-text search
```

This is useful for exact technical terms such as:

```text
3NF
BCNF
ACID
DDL
DML
SQL
DBMS
```

Combine/rerank results.

Document the implementation in `ARCHITECTURE.md`.

---

# 22. CONTEXT PACKER

Create:

```text
ContextPacker
```

Responsibilities:

1. Rank retrieved chunks.
2. Remove duplicates.
3. Remove excessive overlap.
4. Estimate tokens.
5. Enforce a hard context budget.
6. Return only the highest-value evidence.

Example:

```text
MAX_RAG_CONTEXT_TOKENS=6000
```

Make it configurable.

Never send unlimited retrieved content to Gemini.

---

# 23. CONVERSATION CONTEXT

Do not send the entire chat history forever.

Use:

```text
Conversation summary
+
Recent messages
+
Current retrieved document context
+
Current question
```

When conversations become long:

```text
Old messages
 ↓
Compact summary
 ↓
Store summary
 ↓
Keep recent messages
```

Do not summarize the entire conversation on every request.

---

# 24. QUERY REWRITING

Support conversational questions.

Example:

```text
User:
What is normalization?

User:
What about 3NF?
```

The second retrieval query may become:

```text
What is Third Normal Form (3NF) in database normalization?
```

Preserve:

```text
original_query
retrieval_query
```

Only use the rewritten query for retrieval.

---

# 25. QUERY TYPE ROUTING

Do not force every request through identical RAG logic.

Support:

### Factual question
Standard retrieval.

### Explanation
Retrieve the concept plus surrounding context.

### Comparison
Retrieve evidence for all compared concepts.

### Summary
Use summary-oriented retrieval.

### Entire-document summary
Use hierarchical summarization.

### Multi-document comparison
Retrieve evidence across relevant documents.

---

# 26. ENTIRE NOTES / LARGE DOCUMENT SUMMARIZATION

The UI supports requests such as:

> summarise the entire notes

Do NOT answer this by retrieving five arbitrary chunks.

For large documents:

```text
Full document
 ↓
Chunks
 ↓
Chunk summaries
 ↓
Section summaries
 ↓
Document summary
 ↓
Final user-facing summary
```

For small documents, direct summarization is allowed if it safely fits the model context.

Never send a 300–500 page document wholesale to the LLM.

---

# 27. ANTI-HALLUCINATION CONTRACT

Use a strict system instruction similar to:

```text
You are the AI assistant for Talk to Your Notes.

Answer questions using the supplied retrieved document context.

Do not invent facts.

Do not use unsupported knowledge to answer questions about the user's notes.

Do not invent citations, page numbers, section names, file names, quotations, or source identifiers.

If the retrieved context does not contain enough evidence, say that the information could not be found in the user's indexed notes.

Use only source identifiers supplied by the backend.

Never claim to have read a document that was not retrieved.
```

The prompt is only one layer of hallucination prevention.

---

# 28. STRUCTURED LLM OUTPUT

Prefer structured model output:

```json
{
  "answer": "...",
  "citations": [
    {
      "chunk_id": "..."
    }
  ],
  "grounded": true
}
```

Validate it.

If a returned chunk ID does not exist, remove/reject that citation.

Never allow the model to invent source metadata.

---

# 29. CITATION RESOLUTION

The model returns only internal identifiers such as:

```text
chunk_id
```

Backend resolves:

```text
chunk_id
 ↓
document
 ↓
file_name
 ↓
page_number
 ↓
section_title
```

Frontend displays only backend-verified metadata.

This is mandatory.

---

# 30. NOT-FOUND BEHAVIOR

If retrieval does not meet the minimum similarity threshold:

Do not ask the LLM to invent an answer.

Return:

> I couldn't find enough information about that in your indexed notes.

If weak evidence exists, answer only when evidence is sufficient.

---

# 31. ANSWER FORMATTING

Answers should be:

- Direct
- Readable
- Study-friendly
- Structured
- Grounded
- Concise by default

For educational questions, use appropriate structures such as:

```text
### Definition
...

### Explanation
...

### Example
...

### Key points
...
```

Do not add unsupported information.

---

# 32. SOURCE UI

Improve the existing source area.

Prefer:

```text
Verified Sources

DBMS_Detailed.pdf
Page 2
Normalization
```

when metadata exists.

Clicking a source should open the corresponding document/page/section where possible.

Never display fabricated source metadata.

---

# 33. CHAT HISTORY

Recent chats must be persisted in Supabase.

They must survive browser refresh.

Load conversations using:

```text
updated_at DESC
```

No hardcoded production chat history.

---

# 34. CHAT DELETE

Implement deletion for every conversation.

Use a clean interaction consistent with the existing UI:

```text
Hover chat
 ↓
More (...)
 ↓
Delete
```

Deletion must remove:

```text
Conversation
 ↓
Messages
 ↓
Message sources
```

using safe database relationships/cascades.

---

# 35. DELETE CONFIRMATION

Before destructive deletion:

```text
Delete this conversation?

This action cannot be undone.
```

Actions:

```text
Cancel
Delete
```

Do not delete through accidental clicks.

---

# 36. DOCUMENT MANAGEMENT

Verify:

- Upload
- View
- Search
- Rename
- Delete
- Re-index
- Move to collection
- Open source

Deleting a document must clean up its storage object, record, chunks, vectors, and related source records according to the schema.

---

# 37. COLLECTIONS

Implement:

- Create
- Rename
- Delete
- Move documents
- Filter retrieval

When a collection is selected, retrieval must enforce:

```text
user_id = authenticated user
AND collection_id = selected collection
```

---

# 38. AUTHENTICATION

Use Supabase Auth.

Flow:

```text
Login
 ↓
Supabase session
 ↓
Access token
 ↓
FastAPI
 ↓
Token validation
 ↓
Authenticated user
```

Never trust browser-provided user IDs.

---

# 39. FRONTEND ↔ BACKEND

The frontend and backend must communicate through real APIs:

```text
Stitch React UI
 ↓
Authenticated API request
 ↓
FastAPI backend
 ↓
RAG / Supabase / Gemini
 ↓
Validated response
 ↓
Frontend
```

Remove final production mock repositories.

Never place Gemini secrets or Supabase service-role keys in frontend code.

---

# 40. ENVIRONMENT VARIABLES

Maintain:

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
MAX_RAG_CONTEXT_TOKENS=
```

Create/update `.env.example`.

Never commit real credentials.

---

# 41. API CONTRACT

Use clean typed endpoints such as:

```text
POST   /api/documents/upload
GET    /api/documents
GET    /api/documents/:id
DELETE /api/documents/:id
POST   /api/documents/:id/reindex

POST   /api/chat

GET    /api/conversations
GET    /api/conversations/:id
PATCH  /api/conversations/:id
DELETE /api/conversations/:id

GET    /api/collections
POST   /api/collections
PATCH  /api/collections/:id
DELETE /api/collections/:id
```

Use Pydantic schemas.

---

# 42. STREAMING

If reliable Gemini streaming is available:

```text
Question
 ↓
Retrieval
 ↓
Generation
 ↓
Stream answer
 ↓
Attach verified citations
```

Do not fake streaming.

Prioritize correctness over streaming if the two conflict.

---

# 43. LOADING AND ERROR STATES

Every async operation needs a real state:

```text
Uploading
Extracting
Chunking
Embedding
Indexing
Retrieving
Generating
Deleting
Saving
Loading
```

Provide useful user-facing errors.

Never expose raw stack traces.

---

# 44. FAILED INDEXING

If indexing fails, show:

```text
Indexing failed
Retry
```

Implement:

```text
POST /api/documents/:id/reindex
```

The user should not need to upload the document again.

---

# 45. EVERY BUTTON MUST WORK

Audit every interactive element:

- New Chat
- Send
- Chat history
- Delete
- Upload
- Search
- Filter
- Collections
- Create collection
- Rename
- Delete collection
- Document actions
- Source chips
- Document viewer
- Re-index
- User menu
- Navigation
- Theme controls if present

No dead UI controls.

If a visible feature is unfinished, implement it or intentionally remove it.

---

# 46. NO PRODUCTION MOCK DATA

Search for:

```text
mock
dummy
fake
example
hardcoded
```

Classify each occurrence.

Remove production mock data.

The final application must use real:

```text
Supabase
FastAPI
Gemini
pgvector
Storage
```

---

# 47. RAG DEBUG MODE

Create a developer-only diagnostic path showing:

```text
Original query
Retrieval query
Retrieved chunks
Similarity scores
Selected chunks
Dropped chunks
Estimated context tokens
Final context
Model response
Validated citations
```

Do not expose this to normal users.

---

# 48. RAG EVALUATION

Create tests for:

```text
What is DBMS?
What is normalization?
Explain 3NF.
What is a primary key?
Difference between 2NF and 3NF.
Summarise the entire notes.
```

Verify:

- Correct concept
- Correct document
- Correct page when available
- Correct section when available
- No fabricated citations
- No unsupported claims

Also test questions absent from the notes.

Example:

```text
What is quantum computing according to these notes?
```

Expected:

> I couldn't find enough information about that in your indexed notes.

---

# 49. SECURITY TESTS

Explicitly verify:

```text
User A cannot access User B's documents.
User A cannot access User B's chunks.
User A cannot access User B's chats.
User A cannot delete User B's documents.
User A cannot access User B's collections.
```

Also test:

- Expired auth
- Missing auth
- Invalid IDs
- Oversized files
- Malicious file types

---

# 50. LARGE DOCUMENT TEST

Test a large PDF.

Verify:

- Extraction
- Chunking
- Embedding
- Indexing
- Retrieval
- Summary
- Context budget
- No model overflow
- Correct citations

---

# 51. PERFORMANCE

Avoid:

- Loading all messages at once
- Loading all documents at once
- Re-embedding unchanged chunks
- Sending duplicate chunks
- Sending entire documents to the LLM
- Excessive database calls

Use pagination/lazy loading where appropriate.

---

# 52. OBSERVABILITY

Use structured logs for:

```text
request_id
user_id
document_id
conversation_id
retrieval_latency
embedding_latency
llm_latency
retrieved_count
selected_count
estimated_context_tokens
errors
```

Never log:

- API keys
- Passwords
- Service credentials

Avoid unnecessary private document content logging.

---

# 53. TESTING STRATEGY

Implement tests alongside features:

```text
Implement
 ↓
Test
 ↓
Fix
 ↓
Verify
 ↓
Checkpoint
```

Do not postpone testing until the end.

Required categories:

- Unit tests
- Integration tests
- RAG tests
- Security/RLS tests
- End-to-end tests
- Production build

---

# 54. GIT WORKFLOW

Before committing:

```bash
git status
git diff
```

Review all changes.

Use logical commits such as:

```text
fix: improve rag retrieval and grounding
feat: add persistent chat deletion
feat: connect supabase persistence
fix: improve document processing
fix: connect frontend and backend
test: add rag evaluation suite
fix: enforce document ownership
```

Only report a GitHub update if the actual push succeeds.

---

# 55. VERCEL READINESS

Determine whether the frontend is Vite/React, Next.js, or another framework.

Preserve it where possible.

Verify the production build.

Do not hardcode localhost API URLs.

Use the framework's proper environment variable mechanism.

The production frontend must communicate with the deployed backend.

---

# 56. BACKEND DEPLOYMENT

If FastAPI performs heavy PDF processing, prefer:

```text
Frontend → Vercel
Backend → Render/Railway/Fly/etc.
Database → Supabase
Storage → Supabase
Vector Search → Supabase pgvector
LLM → Gemini
```

Do not force heavy processing into Vercel serverless execution if it risks timeouts.

Document the final choice.

---

# 57. CORS

Configure production CORS using environment variables.

Allow only trusted origins.

Do not leave:

```python
allow_origins=["*"]
```

on production authenticated APIs.

---

# 58. FINAL END-TO-END ACCEPTANCE TEST

This exact workflow must work:

```text
Open application
 ↓
Create/Login account
 ↓
Upload DBMS_Detailed.pdf
 ↓
File stored in Supabase Storage
 ↓
Document record created
 ↓
Processing begins
 ↓
Text extracted
 ↓
Chunks created
 ↓
Embeddings generated
 ↓
Vectors stored
 ↓
Document becomes Indexed
 ↓
Create New Chat
 ↓
Ask: "What is DBMS?"
 ↓
Correct grounded answer
 ↓
Verified source
 ↓
Ask: "Explain 3NF"
 ↓
Correct grounded answer
 ↓
Correct source
 ↓
Ask: "Summarise the entire notes"
 ↓
Proper document-level summary
 ↓
No context overflow
 ↓
Refresh browser
 ↓
Conversation remains
 ↓
Open recent conversation
 ↓
Messages remain
 ↓
Delete conversation
 ↓
Confirmation
 ↓
Conversation disappears
 ↓
Refresh
 ↓
Conversation remains deleted
```

Then test:

```text
Create collection
 ↓
Move document
 ↓
Select collection
 ↓
Ask question
 ↓
Only collection documents are retrieved
```

---

# 59. PHASED EXECUTION PLAN

## Phase 0 — Audit

- Inspect repository
- Inspect Stitch UI
- Inspect backend
- Inspect database
- Inspect Supabase
- Inspect RAG
- Inspect Git
- Document current state

Do not make large changes yet.

## Phase 1 — Foundation

- Environment
- Supabase
- Auth
- Database
- Storage
- RLS

Checkpoint.

## Phase 2 — Document Pipeline

- Upload
- Validation
- Storage
- Extraction
- Semantic chunking
- Metadata
- Embeddings
- Indexing states

Checkpoint.

## Phase 3 — Retrieval

- pgvector RPC
- Ownership filtering
- Collection filtering
- Similarity threshold
- Deduplication
- Ranking
- ContextPacker
- Token budgeting

Checkpoint.

## Phase 4 — RAG

- Query rewriting
- Grounding
- Structured output
- Citation validation
- Not-found behavior
- Answer formatting
- Evaluation

Checkpoint.

## Phase 5 — Summarization

- Query-type routing
- Whole-document summarization
- Hierarchical summarization
- Large-document safety

Checkpoint.

## Phase 6 — Chat

- Persistent conversations
- Messages
- Recent chats
- Titles
- Delete
- Confirmation
- Refresh persistence
- Streaming if appropriate

Checkpoint.

## Phase 7 — UI Integration

- Connect all controls
- Upload states
- Processing states
- Error states
- Sources
- Viewer
- Collections
- Search
- Delete actions

Checkpoint.

## Phase 8 — Security & Quality

- RLS
- Authorization
- Validation
- Rate limiting
- CORS
- Secrets
- Security tests
- RAG tests
- E2E tests

Checkpoint.

## Phase 9 — Deployment

- Frontend build
- Backend deployment configuration
- Environment variables
- Vercel compatibility
- Production API URL
- CORS
- README deployment instructions

Checkpoint.

## Phase 10 — GitHub

- Review diff
- Remove secrets
- Remove production mocks
- Commit
- Push if authenticated
- Verify repository state

---

# 60. CHECKPOINT RULE

After every phase:

1. Run relevant tests.
2. Inspect `git diff`.
3. Update `PROJECT_STATE.md`.
4. Update `TASK_PLAN.md`.
5. Update `TEST_STATUS.md`.
6. Record important decisions.
7. Verify the application still builds.

Never move forward with an unknown broken state.

---

# 61. DEFINITION OF DONE

The application is NOT complete if:

- UI works but backend is mocked.
- Chat isn't persistent.
- Sources can be hallucinated.
- Answers are poorly grounded.
- Supabase isn't actually connected.
- Delete doesn't work.
- Documents aren't actually indexed.
- Authentication is fake.
- RLS isn't tested.
- Secrets are exposed.
- Frontend cannot communicate with the production backend.
- Large documents overflow context.
- Whole-note summarization retrieves arbitrary top-K chunks.
- Buttons are dead.
- Errors are swallowed.
- Production build fails.

The application IS complete when:

```text
Stitch UI
+
React frontend
+
FastAPI backend
+
Supabase Auth
+
Supabase PostgreSQL
+
Supabase Storage
+
pgvector
+
Embeddings
+
Gemini
+
Semantic chunking
+
Context packing
+
Conversation memory
+
Hierarchical summarization
+
Citation validation
+
Chat persistence
+
Chat deletion
+
Document management
+
Collections
+
Security
+
Testing
+
Deployment configuration
```

all work together.

---

# 62. FINAL ANTIGRAVITY OPERATING RULES

When uncertain:

> Inspect the repository.

When context is too large:

> Chunk the work.

When context is lost:

> Recover from project state files.

When a feature appears to work:

> Test it.

When a citation appears correct:

> Verify it against the database.

When an answer appears good:

> Verify its retrieved evidence.

When a button exists:

> Test it.

When Supabase appears configured:

> Make a real request and verify it.

When GitHub appears connected:

> Verify the remote and push result.

When deployment appears ready:

> Run the actual production build.

Never fabricate:

- Completion
- Test results
- GitHub updates
- Source citations
- Successful deployment

---

# 63. FINAL PRODUCT GOAL

The finished user experience must be:

```text
Upload notes
      ↓
Notes are actually indexed
      ↓
Ask a question
      ↓
Relevant evidence is retrieved
      ↓
Only useful context reaches Gemini
      ↓
Answer is generated from the notes
      ↓
Citations are verified by the backend
      ↓
User can open the exact source
      ↓
Conversation persists
      ↓
User can delete it
      ↓
Everything survives refresh
```

The product should feel like a polished, reliable AI notes assistant — not a prototype with a chat box.

# FINAL COMMAND

**Audit first. Fix second. Test continuously. Checkpoint every phase. Verify everything.**

**Do not redesign the existing Stitch UI unless a functional change requires it.**

**Do not lose project context.**

**Do not rely on memory when the filesystem can provide the answer.**

**Do not declare completion until the complete end-to-end workflow has been verified.**
