import os
import asyncio
from dotenv import load_dotenv
from sqlalchemy import Table, Column, Integer, String, Text, TIMESTAMP, MetaData
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.sql import select

# Load .env for DB URL
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

# Async engine
engine = create_async_engine(DATABASE_URL, echo=True)

# Define metadata and table
metadata = MetaData()

journal_entries = Table(
    "journal_entries",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("user_id", String),
    Column("content", Text, nullable=False),
    Column("created_at", TIMESTAMP)
)

# Function to fetch all rows
async def show_all_entries():
    async with engine.begin() as conn:
        result = await conn.execute(select(journal_entries))
        rows = result.mappings().all()
        for row in rows:
            print(dict(row))

# Run test
if __name__ == "__main__":
    asyncio.run(show_all_entries())
