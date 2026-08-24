import pytest
from httpx import AsyncClient, ASGITransport
from motor.motor_asyncio import AsyncIOMotorClient

from app.core.config import settings
from app.db.mongodb import db_manager
from app.db.indexes import create_mongo_indexes
from app.main import app

TEST_DB_NAME = "knora_test"


@pytest.fixture(autouse=True)
async def setup_test_database():
    # Override database to test DB
    settings.MONGODB_DATABASE = TEST_DB_NAME
    db_manager.client = AsyncIOMotorClient(settings.MONGODB_URI)
    db_manager.db = db_manager.client[TEST_DB_NAME]

    # Clean test collections before each test run
    await db_manager.db["users"].delete_many({})
    await db_manager.db["otp_verifications"].delete_many({})
    await db_manager.db["sessions"].delete_many({})
    await db_manager.db["resumes"].delete_many({})
    await db_manager.db["resume_files"].delete_many({})

    # Initialize indexes
    try:
        await create_mongo_indexes()
    except Exception:
        pass

    yield

    # Cleanup after test
    await db_manager.db["users"].delete_many({})
    await db_manager.db["otp_verifications"].delete_many({})
    await db_manager.db["sessions"].delete_many({})
    await db_manager.db["resumes"].delete_many({})
    await db_manager.db["resume_files"].delete_many({})


@pytest.fixture
async def async_client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
