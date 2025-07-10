import os
import asyncio
from dotenv import load_dotenv
from sqlalchemy import (
    Table, Column, Integer, String, Text, TIMESTAMP, MetaData, UUID, desc, select
)
from sqlalchemy.ext.asyncio import create_async_engine
from app.db.models import journal_entries, mood_logs, metadata

# Load .env for DB URL
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

# Async engine
engine = create_async_engine(DATABASE_URL, echo=True)

# Fetch sample records from both tables
async def fetch_sample_records(limit: int = 5) -> dict:
    async with engine.begin() as conn:
        # Get recent journal entries
        journal_result = await conn.execute(
            select(journal_entries).order_by(desc(journal_entries.c.created_at)).limit(limit)
        )
        journals = [dict(row) for row in journal_result.mappings().all()]

        # Get recent mood logs
        mood_result = await conn.execute(
            select(mood_logs).order_by(desc(mood_logs.c.timestamp)).limit(limit)
        )
        moods = [dict(row) for row in mood_result.mappings().all()]

        return {
            "journals": journals,
            "mood_logs": moods
        }

# CLI testing
if __name__ == "__main__":
    async def main():
        records = await fetch_sample_records()
        print("Latest Journal Entries:")
        for entry in records["journals"]:
            print(entry)

        print(" Latest Mood Logs:")
        for mood in records["mood_logs"]:
            print(mood)

    asyncio.run(main())