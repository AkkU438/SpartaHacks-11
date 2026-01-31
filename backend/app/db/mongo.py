from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

client = AsyncIOMotorClient(settings.mongodb_uri)
db = client.get_database(settings.db_name)

def get_users_collection():
    return db["users"]