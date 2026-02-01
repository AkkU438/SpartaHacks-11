from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from app.core.security import get_current_user
from app.db.mongo import get_connections_collection, get_users_collection

router = APIRouter()


# ----- Schemas -----

class BudgetResponse(BaseModel):
    spent: float
    limit: int


class BudgetUpdateRequest(BaseModel):
    limit: int = Field(ge=0, le=1000000, description="Budget limit between 0 and 1,000,000")


class SubscriptionItem(BaseModel):
    name: str
    icon: str
    amount: float
    date: str


class TransactionItem(BaseModel):
    name: str
    icon: str
    amount: float


class CategoryItem(BaseModel):
    name: str
    amount: float
    color: str


class GoalItem(BaseModel):
    name: str
    date: str
    monthly: float
    total: float


class GoalCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100, description="Goal name")
    date: str = Field(min_length=1, description="Target date (e.g., 'Jan 2030')")
    monthly: float = Field(gt=0, le=1000000, description="Monthly contribution amount")
    total: float = Field(gt=0, le=100000000, description="Total target amount")


class MessageResponse(BaseModel):
    message: str


# ----- Endpoints -----

@router.get("/budget", response_model=BudgetResponse)
async def get_budget(user: dict[str, Any] = Depends(get_current_user)):
    """Get user's budget info."""
    connections = get_connections_collection()
    
    # Calculate spent from transactions
    connection = await connections.find_one({"user_id": user["_id"]})
    
    spent = 0.0
    if connection and connection.get("transactions"):
        spent = sum(t.get("amount", 0) for t in connection["transactions"])
    
    return {
        "spent": spent,
        "limit": user.get("budget_limit", 3000)
    }


@router.put("/budget", response_model=BudgetResponse)
async def update_budget(
    data: BudgetUpdateRequest,
    user: dict[str, Any] = Depends(get_current_user)
):
    """Update user's budget limit."""
    users = get_users_collection()
    connections = get_connections_collection()
    
    await users.update_one(
        {"_id": user["_id"]},
        {"$set": {"budget_limit": data.limit}}
    )
    
    # Calculate spent from transactions
    connection = await connections.find_one({"user_id": user["_id"]})
    spent = 0.0
    if connection and connection.get("transactions"):
        spent = sum(t.get("amount", 0) for t in connection["transactions"])
    
    return {
        "spent": spent,
        "limit": data.limit
    }


@router.get("/subscriptions", response_model=list[SubscriptionItem])
async def get_subscriptions(user: dict[str, Any] = Depends(get_current_user)):
    """Get user's subscriptions."""
    connections = get_connections_collection()
    
    connection = await connections.find_one({"user_id": user["_id"]})
    
    if not connection or not connection.get("connected"):
        return []
    
    return connection.get("subscriptions", [])


@router.get("/spending/daily", response_model=list[TransactionItem])
async def get_daily_spending(user: dict[str, Any] = Depends(get_current_user)):
    """Get user's daily transactions."""
    connections = get_connections_collection()
    
    connection = await connections.find_one({"user_id": user["_id"]})
    
    if not connection or not connection.get("connected"):
        return []
    
    return connection.get("transactions", [])


@router.get("/spending/categories", response_model=list[CategoryItem])
async def get_spending_categories(user: dict[str, Any] = Depends(get_current_user)):
    """Get user's spending categories breakdown."""
    connections = get_connections_collection()
    
    connection = await connections.find_one({"user_id": user["_id"]})
    
    if not connection or not connection.get("connected"):
        return []
    
    return connection.get("spending_categories", [])


@router.get("/goals", response_model=list[GoalItem])
async def get_goals(user: dict[str, Any] = Depends(get_current_user)):
    """Get user's savings goals."""
    connections = get_connections_collection()
    
    connection = await connections.find_one({"user_id": user["_id"]})
    
    if not connection or not connection.get("connected"):
        return []
    
    return connection.get("goals", [])


@router.post("/goals", response_model=GoalItem, status_code=status.HTTP_201_CREATED)
async def create_goal(
    data: GoalCreateRequest,
    user: dict[str, Any] = Depends(get_current_user)
):
    """Add a new savings goal."""
    connections = get_connections_collection()
    
    # Ensure connection exists
    connection = await connections.find_one({"user_id": user["_id"]})
    if not connection:
        # Create connection without Plaid but allow goals
        await connections.insert_one({
            "user_id": user["_id"],
            "connected": False,
            "connected_at": None,
            "subscriptions": [],
            "transactions": [],
            "spending_categories": [],
            "goals": [],
        })
    
    goal = {
        "name": data.name,
        "date": data.date,
        "monthly": data.monthly,
        "total": data.total,
    }
    
    await connections.update_one(
        {"user_id": user["_id"]},
        {"$push": {"goals": goal}}
    )
    
    return goal
