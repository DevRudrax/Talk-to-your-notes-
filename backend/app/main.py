from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.auth import get_current_user
from app.routers import documents, chat, conversations, collections
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("talk_to_your_notes")

app = FastAPI(
    title="Talk to Your Notes API",
    description="Backend service for grounded RAG document chat and knowledge management",
    version="1.0.0"
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(documents.router)
app.include_router(chat.router)
app.include_router(conversations.router)
app.include_router(collections.router)


@app.get("/")
def root():
    return {
        "app": "Talk to Your Notes API",
        "status": "running",
        "docs": "/docs"
    }


@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "environment": {
            "embedding_model": settings.EMBEDDING_MODEL,
            "llm_model": settings.LLM_MODEL,
            "mock_auth": settings.MOCK_AUTH
        }
    }


@app.get("/api/me")
def get_me(user: dict = Depends(get_current_user)):
    return {"user": user}
