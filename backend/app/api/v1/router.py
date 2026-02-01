from fastapi import APIRouter

from app.api.v1.endpoints import health, auth, plaid, dashboard

api_router = APIRouter()

# Health check
api_router.include_router(health.router, tags=["health"])

# Authentication
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])

# Mock Plaid integration
api_router.include_router(plaid.router, prefix="/plaid", tags=["plaid"])

# Dashboard APIs
api_router.include_router(dashboard.router, tags=["dashboard"])
