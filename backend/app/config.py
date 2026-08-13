import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

# Resolve path to .env in root directory
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
ENV_PATH = os.path.join(ROOT_DIR, ".env")


class Settings(BaseSettings):
    SUPABASE_URL: str = "https://mock.supabase.co"
    SUPABASE_PUBLISHABLE_KEY: str = "mock-publishable-key"
    SUPABASE_SERVICE_ROLE_KEY: str = "mock-service-role-key"
    SUPABASE_SECRET_KEY: Optional[str] = None
    SUPABASE_JWKS_URL: Optional[str] = None

    DATABASE_URL: Optional[str] = None
    POSTGRES_HOST: Optional[str] = None
    POSTGRES_PORT: Optional[int] = 5432
    POSTGRES_DB: Optional[str] = "postgres"
    POSTGRES_USER: Optional[str] = "postgres"
    POSTGRES_PASSWORD: Optional[str] = None

    GEMINI_API_KEY: str = "mock-gemini-key"
    LLM_MODEL: str = "gemini-flash-latest"
    EMBEDDING_MODEL: str = "text-embedding-004"
    EMBEDDING_DIMENSION: int = 768

    FRONTEND_URL: str = "http://localhost:5173"
    BACKEND_URL: str = "http://localhost:8001"
    MAX_FILE_SIZE_MB: int = 25
    TOP_K: int = 5
    SIMILARITY_THRESHOLD: float = 0.3
    MAX_CONTEXT_TOKENS: int = 3000

    MOCK_AUTH: bool = True

    model_config = SettingsConfigDict(
        env_file=(ENV_PATH, ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @property
    def admin_key(self) -> str:
        return self.SUPABASE_SECRET_KEY or self.SUPABASE_SERVICE_ROLE_KEY


settings = Settings()
