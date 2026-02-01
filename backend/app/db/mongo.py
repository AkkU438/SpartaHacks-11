from __future__ import annotations

from motor.motor_asyncio import (
    AsyncIOMotorClient,
    AsyncIOMotorCollection,
    AsyncIOMotorDatabase,
)

from app.core.config import settings

_client: AsyncIOMotorClient | None = None
_db: AsyncIOMotorDatabase | None = None


async def connect_db() -> None:
    """Initialize the Mongo client + database handle (called on app startup)."""
    global _client, _db

    if _client is not None and _db is not None:
        return

    _client = AsyncIOMotorClient(settings.mongodb_uri)
    _db = _client.get_database(settings.db_name)
    await _client.admin.command("ping")
    
    # Create indexes
    await _ensure_indexes()


async def close_db() -> None:
    """Close Mongo client (called on app shutdown)."""
    global _client, _db

    if _client is not None:
        _client.close()

    _client = None
    _db = None


def get_db() -> AsyncIOMotorDatabase:
    """FastAPI dependency: returns initialized database handle."""
    if _db is None:
        raise RuntimeError("Database not initialized. Did you call connect_db() on startup?")
    return _db


def get_collection(name: str) -> AsyncIOMotorCollection:
    """Convenience accessor for a collection by name."""
    return get_db()[name]


def get_users_collection() -> AsyncIOMotorCollection:
    """Convenience accessor for the users collection."""
    return get_collection("users")


def get_sessions_collection() -> AsyncIOMotorCollection:
    """Convenience accessor for the sessions collection."""
    return get_collection("sessions")


def get_connections_collection() -> AsyncIOMotorCollection:
    """Convenience accessor for the connections collection (mock Plaid)."""
    return get_collection("connections")


async def _ensure_indexes() -> None:
    """Create necessary indexes for collections."""
    # Users: unique email index
    users = get_users_collection()
    await users.create_index("email", unique=True)
    
    # Sessions: index on session_id for lookups, TTL index on expires_at for auto-expiry
    sessions = get_sessions_collection()
    await sessions.create_index("session_id", unique=True)
    await sessions.create_index("expires_at", expireAfterSeconds=0)
    
    # Connections: index on user_id for lookups
    connections = get_connections_collection()
    await connections.create_index("user_id", unique=True)