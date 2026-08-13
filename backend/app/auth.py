from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, Dict, Any
from app.config import settings
from app.db import get_supabase_client
import logging

logger = logging.getLogger("talk_to_your_notes.auth")

security = HTTPBearer(auto_error=False)

DEFAULT_MOCK_USER = {
    "id": "00000000-0000-0000-0000-000000000001",
    "email": "user@example.com",
    "full_name": "Demo User"
}


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Dict[str, Any]:
    if settings.MOCK_AUTH:
        return DEFAULT_MOCK_USER

    if not credentials:
        # Fallback to mock user if dev testing without token
        if settings.MOCK_AUTH or settings.SUPABASE_URL.startswith("https://mock"):
            return DEFAULT_MOCK_USER
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials
    try:
        supabase = get_supabase_client()
        user_response = supabase.auth.get_user(token)
        if user_response and user_response.user:
            return {
                "id": str(user_response.user.id),
                "email": str(user_response.user.email),
                "full_name": user_response.user.user_metadata.get("full_name", "")
            }
    except Exception as e:
        logger.warning(f"Auth token validation error: {e}")

    if settings.MOCK_AUTH or settings.SUPABASE_URL.startswith("https://mock"):
        return DEFAULT_MOCK_USER

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication token",
        headers={"WWW-Authenticate": "Bearer"},
    )
