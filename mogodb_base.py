from loguru import logger
from motor.motor_asyncio import AsyncIOMotorClient

from core.config import MONGODB_URL


class DataBase:
    client: AsyncIOMotorClient = None


db = DataBase()


async def get_database() -> AsyncIOMotorClient:
    return db.client


async def create_db_client():
    logger.info("Connection DB...")
    db.client = AsyncIOMotorClient(MONGODB_URL,
                                   maxPoolSize=10,
                                   minPoolSize=10)
    logger.info("Connected.")


async def shutdown_db_client():
    logger.info("Disconnection DB...")
    db.client.close()
    logger.info("Disconnected.")
