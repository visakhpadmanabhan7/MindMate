import asyncio
from sqlalchemy.ext.asyncio import create_async_engine

from sqlalchemy import text
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_async_engine(DATABASE_URL, echo=True)


async def setup():
    async with engine.begin() as conn:
        # Create pgvector extension
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))

        # Create journal_entries table
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS journal_entries (
                id SERIAL PRIMARY KEY,
                user_id TEXT DEFAULT 'anonymous',
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """))

        print(" Database setup complete")


if __name__ == "__main__":
    asyncio.run(setup())
