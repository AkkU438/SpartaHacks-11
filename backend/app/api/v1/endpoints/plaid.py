from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.core.security import get_current_user
from app.db.mongo import get_connections_collection

router = APIRouter()


# Kept in sync with Frontend/script.js fallback constants
DEMO_SUBSCRIPTIONS = [
    {"name": "Crunchyroll", "icon": "📺", "amount": 7.99, "date": "Feb 15"},
]

DEMO_TRANSACTIONS = [
    {"name": "Kroger", "icon": "🛒", "amount": 45.20},
    {"name": "Taco Bell", "icon": "🌮", "amount": 12.85},
    {"name": "Chic-fil-a", "icon": "🍔", "amount": 15.40},
    {"name": "Starbucks", "icon": "☕", "amount": 6.50},
    {"name": "Gas Station", "icon": "⛽", "amount": 40.00},
]

DEMO_CATEGORIES = [
    {"name": "Rent", "amount": 1200, "color": "#4CAF50"},
    {"name": "Food", "amount": 400, "color": "#FF9800"},
    {"name": "Bills", "amount": 250, "color": "#2196F3"},
    {"name": "Fun", "amount": 150, "color": "#E91E63"},
]

DEMO_GOALS = [
    {"name": "Japan 2030", "date": "Jan 2030", "monthly": 100, "total": 12000},
]


class MessageResponse(BaseModel):
    message: str


class PlaidStatusResponse(BaseModel):
    connected: bool


@router.post("/connect", response_model=MessageResponse)
async def plaid_connect(user: dict[str, Any] = Depends(get_current_user)):
    """Simulate a Plaid connection and seed demo data."""
    connections = get_connections_collection()

    await connections.update_one(
        {"user_id": user["_id"]},
        {
            "$set": {
                "user_id": user["_id"],
                "connected": True,
                "connected_at": datetime.now(timezone.utc),
                "subscriptions": DEMO_SUBSCRIPTIONS,
                "transactions": DEMO_TRANSACTIONS,
                "spending_categories": DEMO_CATEGORIES,
                "goals": DEMO_GOALS,
            }
        },
        upsert=True,
    )

    return {"message": "Bank connected successfully"}


@router.get("/status", response_model=PlaidStatusResponse)
async def plaid_status(user: dict[str, Any] = Depends(get_current_user)):
    """Get mock Plaid connection status."""
    connections = get_connections_collection()
    connection = await connections.find_one({"user_id": user["_id"]})
    return {"connected": bool(connection and connection.get("connected"))}


@router.post("/disconnect", response_model=MessageResponse)
async def plaid_disconnect(user: dict[str, Any] = Depends(get_current_user)):
    """Disconnect from Plaid and clear demo data."""
    connections = get_connections_collection()

    await connections.update_one(
        {"user_id": user["_id"]},
        {
            "$set": {
                "connected": False,
                "connected_at": None,
                "subscriptions": [],
                "transactions": [],
                "spending_categories": [],
                "goals": [],
            }
        },
        upsert=True,
    )

    return {"message": "Bank disconnected"}
