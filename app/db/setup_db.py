import asyncio
from sqlalchemy.ext.asyncio import create_async_engine

from sqlalchemy import text
import os
from dotenv import load_dotenv
from app.db.models import journal_entries, mood_logs, metadata

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_async_engine(DATABASE_URL, echo=True)

# Create engine
engine = create_async_engine(DATABASE_URL, echo=True)


async def setup():
    async with engine.begin() as conn:
        # Enable pgvector
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))

        # Create tables from metadata (auto from models)
        await conn.run_sync(metadata.create_all)

        print(" Database setup complete")


async def reset_db():
    async with engine.begin() as conn:
        await conn.run_sync(metadata.drop_all)   #
        await conn.run_sync(metadata.create_all)
        return "Database reset complete"


if __name__ == "__main__":
    asyncio.run(setup())


