from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, HTTPException, status
from jose import jwt 
from pydantic import BaseModel, EmailStr

from app.core.config import settings
from app.core.security import verify_password
from app.db.mongo import get_users_collection