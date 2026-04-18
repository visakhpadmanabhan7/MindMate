import asyncio
import os

import pytest

# Use in-memory SQLite for tests
os.environ["DATABASE_URL"] = "sqlite+aiosqlite://"
os.environ["OPENAI_API_KEY"] = "test-key"
os.environ["OPENAI_MODEL"] = "gpt-4.1-nano"
os.environ["CHROMA_PATH"] = "/tmp/mindmate_test_chroma"

# Clear cached settings so test env vars take effect
from app.core.config import get_settings

get_settings.cache_clear()

from app.db.engine import engine
from app.db.models import metadata


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(autouse=True)
async def setup_db():
    """Create tables before each test, drop after."""
    async with engine.begin() as conn:
        await conn.run_sync(metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(metadata.drop_all)
