import os
from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy import Table, Column, Integer, Text, String, MetaData, TIMESTAMP
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.sql import insert

# Load .env
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

# Async DB engine
engine = create_async_engine(DATABASE_URL)

# SQLAlchemy Table definition
metadata = MetaData()

journal_entries = Table(
    "journal_entries",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("user_id", String, default="anonymous"),
    Column("content", Text, nullable=False),
    Column("created_at", TIMESTAMP, default=datetime.utcnow),
)

# Tool: save a journal entry
async def save_journal_entry(content: str, user_id: str = "anonymous"):
    async with engine.begin() as conn:
        stmt = insert(journal_entries).values(
            user_id=user_id,
            content=content,
            created_at=datetime.utcnow()
        )
        await conn.execute(stmt)
#
# if __name__ == "__main__":
#     import asyncio
#     asyncio.run(save_journal_entry("Today I learned async DB in Python!"))
