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