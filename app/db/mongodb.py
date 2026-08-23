from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.core.config import settings
from app.core.logging import logger


class MongoDBManager:
    client: Optional[AsyncIOMotorClient] = None
    db: Optional[AsyncIOMotorDatabase] = None


db_manager = MongoDBManager()


async def connect_to_mongo():
    logger.info(f"Connecting to MongoDB at {settings.MONGODB_URI}...")
    db_manager.client = AsyncIOMotorClient(
        settings.MONGODB_URI,
        maxPoolSize=50,
        minPoolSize=10,
        uuidRepresentation="standard"
    )
    db_manager.db = db_manager.client[settings.MONGODB_DATABASE]
    logger.info(f"Successfully connected to MongoDB database: {settings.MONGODB_DATABASE}")


async def close_mongo_connection():
    if db_manager.client:
        logger.info("Closing MongoDB connection pool...")
        db_manager.client.close()
        logger.info("MongoDB connection closed.")


def get_database() -> AsyncIOMotorDatabase:
    if db_manager.db is None:
        raise RuntimeError("Database connection is not initialized. Ensure connect_to_mongo() was called.")
    return db_manager.db
