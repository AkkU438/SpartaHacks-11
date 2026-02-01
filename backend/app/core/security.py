from datetime import datetime, timezone
from typing import Any

from fastapi import Cookie, HTTPException, status
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    return pwd_context.verify(password, hashed_password)


async def get_current_user(session_id: str | None = Cookie(default=None)) -> dict[str, Any]:
    """
    FastAPI dependency that loads the current user from session cookie.
    Returns the user document from MongoDB.
    Raises 401 if not authenticated or session expired.
    """
    # Import here to avoid circular imports
    from app.db.mongo import get_sessions_collection, get_users_collection
    
    if not session_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    sessions = get_sessions_collection()
    users = get_users_collection()
    
    # Find session
    session = await sessions.find_one({"session_id": session_id})
    if not session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid session"
        )
    
    # Check expiry (MongoDB stores naive UTC datetimes)
    expires_at = session["expires_at"]
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    if expires_at < datetime.now(timezone.utc):
        await sessions.delete_one({"session_id": session_id})
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expired"
        )
    
    # Get user
    user = await users.find_one({"_id": session["user_id"]})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return user