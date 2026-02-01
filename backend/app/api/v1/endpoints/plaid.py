from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.core.security import get_current_user
from app.db.mongo import get_connections_collection

router = APIRouter()


SCENARIOS: list[dict[str, Any]] = [
    {
        # Kept in sync with Frontend/script.js fallback constants
        "name": "baseline",
        "subscriptions": [
            {"name": "Crunchyroll", "icon": "📺", "amount": 7.99, "date": "Feb 15"},
        ],
        "transactions": [
            {"name": "Kroger", "icon": "🛒", "amount": 45.20},
            {"name": "Taco Bell", "icon": "🌮", "amount": 12.85},
            {"name": "Chic-fil-a", "icon": "🍔", "amount": 15.40},
            {"name": "Starbucks", "icon": "☕", "amount": 6.50},
            {"name": "Gas Station", "icon": "⛽", "amount": 40.00},
        ],
        "spending_categories": [
            {"name": "Rent", "amount": 1200, "color": "#4CAF50"},
            {"name": "Food", "amount": 400, "color": "#FF9800"},
            {"name": "Bills", "amount": 250, "color": "#2196F3"},
            {"name": "Fun", "amount": 150, "color": "#E91E63"},
        ],
        "goals": [
            {"name": "Japan 2030", "date": "Jan 2030", "monthly": 100, "total": 12000},
        ],
    },
    {
        "name": "many_subscriptions",
        "subscriptions": [
            {"name": "Netflix", "icon": "🎬", "amount": 15.49, "date": "Feb 03"},
            {"name": "Spotify", "icon": "🎧", "amount": 10.99, "date": "Feb 05"},
            {"name": "Hulu", "icon": "📺", "amount": 7.99, "date": "Feb 07"},
            {"name": "Prime", "icon": "📦", "amount": 14.99, "date": "Feb 10"},
            {"name": "iCloud", "icon": "☁️", "amount": 2.99, "date": "Feb 12"},
            {"name": "Disney+", "icon": "✨", "amount": 13.99, "date": "Feb 14"},
            {"name": "Xbox Game Pass", "icon": "🎮", "amount": 16.99, "date": "Feb 18"},
            {"name": "NYTimes", "icon": "📰", "amount": 6.00, "date": "Feb 21"},
            {"name": "Gym", "icon": "🏋️", "amount": 29.99, "date": "Feb 25"},
            {"name": "Adobe", "icon": "🖌️", "amount": 19.99, "date": "Feb 28"},
        ],
        "transactions": [
            {"name": "Coffee", "icon": "☕", "amount": 6.25},
            {"name": "Groceries", "icon": "🛒", "amount": 62.10},
            {"name": "Takeout", "icon": "🍜", "amount": 18.40},
            {"name": "Gas", "icon": "⛽", "amount": 39.00},
            {"name": "Pharmacy", "icon": "💊", "amount": 12.75},
        ],
        "spending_categories": [
            {"name": "Rent", "amount": 1200, "color": "#4CAF50"},
            {"name": "Food", "amount": 520, "color": "#FF9800"},
            {"name": "Bills", "amount": 260, "color": "#2196F3"},
            {"name": "Fun", "amount": 180, "color": "#E91E63"},
        ],
        "goals": [
            {"name": "Japan 2030", "date": "Jan 2030", "monthly": 100, "total": 12000},
        ],
    },
    {
        "name": "high_spend",
        "subscriptions": [
            {"name": "Netflix", "icon": "🎬", "amount": 15.49, "date": "Feb 03"},
            {"name": "Gym", "icon": "🏋️", "amount": 49.99, "date": "Feb 08"},
            {"name": "DoorDash+", "icon": "🛵", "amount": 9.99, "date": "Feb 11"},
        ],
        "transactions": [
            {"name": "Rent", "icon": "🏠", "amount": 1950.00},
            {"name": "Car Payment", "icon": "🚗", "amount": 520.00},
            {"name": "Groceries", "icon": "🛒", "amount": 210.45},
            {"name": "Weekend Trip", "icon": "✈️", "amount": 680.00},
            {"name": "Dining Out", "icon": "🍽️", "amount": 155.30},
            {"name": "Electronics", "icon": "💻", "amount": 799.99},
        ],
        "spending_categories": [
            {"name": "Housing", "amount": 1950, "color": "#4CAF50"},
            {"name": "Transport", "amount": 650, "color": "#2196F3"},
            {"name": "Food", "amount": 520, "color": "#FF9800"},
            {"name": "Travel", "amount": 680, "color": "#9C27B0"},
            {"name": "Shopping", "amount": 800, "color": "#E91E63"},
        ],
        "goals": [
            {"name": "Emergency Fund", "date": "Dec 2026", "monthly": 250, "total": 5000},
            {"name": "Japan 2030", "date": "Jan 2030", "monthly": 100, "total": 12000},
        ],
    },
    {
        "name": "empty_everything",
        "subscriptions": [],
        "transactions": [],
        "spending_categories": [],
        "goals": [],
    },
    {
        "name": "many_transactions",
        "subscriptions": [
            {"name": "Streaming Bundle", "icon": "📺", "amount": 19.99, "date": "Feb 01"},
        ],
        "transactions": [
            # High count to stress the scroll area + rendering.
            # (Names intentionally repeat with slight variation.)
            *[
                {
                    "name": f"Merchant {i % 25} - Item {i}",
                    "icon": ["🛒", "☕", "🍔", "⛽", "🎮", "📦", "🎵", "🧾"][i % 8],
                    "amount": round((i % 17) * 3.13 + 0.99, 2),
                }
                for i in range(1, 201)
            ],
        ],
        "spending_categories": [
            {"name": "Food", "amount": 450, "color": "#FF9800"},
            {"name": "Shopping", "amount": 300, "color": "#E91E63"},
            {"name": "Transport", "amount": 180, "color": "#2196F3"},
            {"name": "Bills", "amount": 120, "color": "#4CAF50"},
        ],
        "goals": [
            {"name": "New Laptop", "date": "Jun 2026", "monthly": 120, "total": 1200},
        ],
    },
    {
        "name": "many_categories",
        "subscriptions": [
            {"name": "Gym", "icon": "🏋️", "amount": 29.99, "date": "Feb 12"},
        ],
        "transactions": [
            {"name": "Groceries", "icon": "🛒", "amount": 76.55},
            {"name": "Lunch", "icon": "🥗", "amount": 14.20},
            {"name": "Gas", "icon": "⛽", "amount": 41.10},
        ],
        "spending_categories": [
            # Many slices to stress legend + donut.
            *[
                {
                    "name": f"Category {i}",
                    "amount": (i + 1) * 10,
                    "color": [
                        "#4CAF50",
                        "#FF9800",
                        "#2196F3",
                        "#E91E63",
                        "#9C27B0",
                        "#00BCD4",
                        "#FFC107",
                        "#795548",
                    ][i % 8],
                }
                for i in range(0, 24)
            ],
        ],
        "goals": [
            {"name": "Vacation", "date": "Aug 2026", "monthly": 200, "total": 1600},
        ],
    },
    {
        "name": "duplicate_names",
        "subscriptions": [
            {"name": "Netflix", "icon": "🎬", "amount": 15.49, "date": "Feb 03"},
            {"name": "Netflix", "icon": "🎬", "amount": 15.49, "date": "Feb 03"},
            {"name": "Spotify", "icon": "🎧", "amount": 10.99, "date": "Feb 05"},
            {"name": "Spotify", "icon": "🎧", "amount": 10.99, "date": "Feb 05"},
        ],
        "transactions": [
            {"name": "Starbucks", "icon": "☕", "amount": 6.50},
            {"name": "Starbucks", "icon": "☕", "amount": 6.50},
            {"name": "Kroger", "icon": "🛒", "amount": 45.20},
            {"name": "Kroger", "icon": "🛒", "amount": 45.20},
        ],
        "spending_categories": [
            {"name": "Food", "amount": 200, "color": "#FF9800"},
            {"name": "Food", "amount": 200, "color": "#FF9800"},
            {"name": "Bills", "amount": 150, "color": "#2196F3"},
        ],
        "goals": [
            {"name": "Japan 2030", "date": "Jan 2030", "monthly": 100, "total": 12000},
        ],
    },
    {
        "name": "long_strings_unicode",
        "subscriptions": [
            {
                "name": "InternationalStreamingPlusUltra_Maximum_Plan_(年度プラン) “Premium” 😅📺",
                "icon": "🌐",
                "amount": 24.99,
                "date": "Feb 09",
            },
            {
                # Controlled missing_fields case: omit icon + date, null amount
                "name": "MissingFields_Subscription_With_Quotes_'\"_and_Emoji_🧪",
                "amount": None,
            },
        ],
        "transactions": [
            {
                "name": "Café \"Déjà Vu\" — extremely long merchant name with accents, emoji ☕️, and quotes '\"'",
                "icon": "☕",
                "amount": 12.3456,
            },
            {
                # Missing icon/name to force frontend robustness
                "amount": 9.99,
            },
        ],
        "spending_categories": [
            {"name": "Food & Dining (超長いカテゴリ名)", "amount": 333.33, "color": "#FF9800"},
            {
                # Missing color to force fallback color logic
                "name": "Mystery Category ???",
                "amount": 111.11,
            },
        ],
        "goals": [
            {
                "name": "🚀 Super Long Goal Name: Save for a once-in-a-lifetime trip across multiple continents",
                "date": "Nov 2027",
                "monthly": 123.45,
                "total": 9876.54,
            },
        ],
    },
    {
        "name": "zero_and_huge_amounts",
        "subscriptions": [
            {"name": "Free Trial", "icon": "🆓", "amount": 0, "date": "Feb 02"},
            {"name": "Enterprise SaaS", "icon": "🏢", "amount": 1000000, "date": "Feb 20"},
        ],
        "transactions": [
            {"name": "Refunded Coffee", "icon": "☕", "amount": 0},
            {"name": "One Cent Test", "icon": "🧪", "amount": 0.01},
            {"name": "Massive Purchase", "icon": "💳", "amount": 1000000},
        ],
        "spending_categories": [
            {"name": "Zero Category", "amount": 0, "color": "#00BCD4"},
            {"name": "Huge Category", "amount": 1000000, "color": "#E91E63"},
            {"name": "Tiny Category", "amount": 0.01, "color": "#4CAF50"},
        ],
        "goals": [
            {"name": "Big Goal", "date": "Jan 2035", "monthly": 99999.99, "total": 100000000},
        ],
    },
    {
        "name": "negative_amounts",
        "subscriptions": [
            {"name": "Gym", "icon": "🏋️", "amount": 29.99, "date": "Feb 12"},
        ],
        "transactions": [
            {"name": "Grocery Store", "icon": "🛒", "amount": 84.20},
            {"name": "Returned Item (Refund)", "icon": "↩️", "amount": -32.15},
            {"name": "Chargeback", "icon": "⚠️", "amount": -120.00},
            {"name": "Coffee", "icon": "☕", "amount": 6.50},
        ],
        "spending_categories": [
            # Keep categories non-negative per plan note.
            {"name": "Food", "amount": 250, "color": "#FF9800"},
            {"name": "Bills", "amount": 180, "color": "#2196F3"},
            {"name": "Shopping", "amount": 90, "color": "#E91E63"},
        ],
        "goals": [
            {"name": "Pay Down Debt", "date": "Oct 2026", "monthly": 300, "total": 2400},
        ],
    },
]


def _next_scenario_index(current_index: int | None) -> int:
    base = -1 if current_index is None else int(current_index)
    return (base + 1) % len(SCENARIOS)


class MessageResponse(BaseModel):
    message: str


class PlaidStatusResponse(BaseModel):
    connected: bool


@router.post("/connect", response_model=MessageResponse)
async def plaid_connect(user: dict[str, Any] = Depends(get_current_user)):
    """Simulate a Plaid connection and seed demo data (cycles scenarios per user)."""
    connections = get_connections_collection()

    existing = await connections.find_one({"user_id": user["_id"]})
    current_index = existing.get("scenario_index") if existing else None
    scenario_index = _next_scenario_index(current_index)
    scenario = SCENARIOS[scenario_index]

    await connections.update_one(
        {"user_id": user["_id"]},
        {
            "$set": {
                "user_id": user["_id"],
                "connected": True,
                "connected_at": datetime.now(timezone.utc),
                "scenario_index": scenario_index,
                "scenario_name": scenario["name"],
                "subscriptions": scenario["subscriptions"],
                "transactions": scenario["transactions"],
                "spending_categories": scenario["spending_categories"],
                "goals": scenario["goals"],
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
