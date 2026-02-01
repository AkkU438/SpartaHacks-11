from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import uuid4

from bson import ObjectId
from fastapi import APIRouter, HTTPException, status, Response, Cookie, Depends
from pydantic import BaseModel, EmailStr, Field, field_validator

from app.core.config import settings
from app.core.security import hash_password, verify_password, get_current_user
from app.db.mongo import get_users_collection, get_sessions_collection

router = APIRouter()


# ----- Schemas -----

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    first_name: str = Field(min_length=1, max_length=50)
    last_name: str = Field(min_length=1, max_length=50)
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        return v


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: str
    email: str
    first_name: str
    last_name: str
    budget_limit: int


class MessageResponse(BaseModel):
    message: str


# ----- Endpoints -----

@router.post("/register", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def register(data: RegisterRequest):
    """Register a new user."""
    users = get_users_collection()
    
    # Check if user already exists
    existing = await users.find_one({"email": data.email})
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create user document
    user_doc = {
        "email": data.email,
        "password_hash": hash_password(data.password),
        "first_name": data.first_name,
        "last_name": data.last_name,
        "created_at": datetime.now(timezone.utc),
        "budget_limit": 3000,  # default
    }
    
    await users.insert_one(user_doc)
    return {"message": "User registered successfully"}


@router.post("/login", response_model=MessageResponse)
async def login(data: LoginRequest, response: Response):
    """Login and set session cookie."""
    users = get_users_collection()
    sessions = get_sessions_collection()
    
    # Find user
    user = await users.find_one({"email": data.email})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Verify password
    if not verify_password(data.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Create session
    session_id = str(uuid4())
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings.session_exp_minutes)
    
    session_doc = {
        "session_id": session_id,
        "user_id": user["_id"],
        "created_at": datetime.now(timezone.utc),
        "expires_at": expires_at,
    }
    
    await sessions.insert_one(session_doc)
    
    # Set HttpOnly cookie
    response.set_cookie(
        key="session_id",
        value=session_id,
        httponly=True,
        samesite="lax",
        secure=settings.env != "local",  # Secure in production
        max_age=settings.session_exp_minutes * 60,
    )
    
    return {"message": "Login successful"}


@router.post("/logout", response_model=MessageResponse)
async def logout(response: Response, session_id: str | None = Cookie(default=None)):
    """Logout and clear session cookie."""
    if session_id:
        sessions = get_sessions_collection()
        await sessions.delete_one({"session_id": session_id})
    
    response.delete_cookie(key="session_id")
    return {"message": "Logged out successfully"}


@router.get("/me", response_model=UserResponse)
async def get_me(user: dict[str, Any] = Depends(get_current_user)):
    """Get current user info."""
    return UserResponse(
        id=str(user["_id"]),
        email=user["email"],
        first_name=user["first_name"],
        last_name=user["last_name"],
        budget_limit=user.get("budget_limit", 3000),
    )
