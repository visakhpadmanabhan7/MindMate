import asyncio
import logging

from sqlalchemy import text

from app.db.engine import engine
from app.db.models import metadata

logger = logging.getLogger(__name__)


async def _migrate(conn):
    """Run lightweight migrations for schema changes."""
    migrations = [
        ("messages", "session_id", "ALTER TABLE messages ADD COLUMN session_id INTEGER"),
        ("journal_entries", "sentiment_score", "ALTER TABLE journal_entries ADD COLUMN sentiment_score REAL"),
        ("journal_entries", "summary", "ALTER TABLE journal_entries ADD COLUMN summary TEXT"),
    ]
    for table, column, sql in migrations:
        try:
            # Check if column exists
            result = await conn.execute(text(f"PRAGMA table_info({table})"))
            columns = [row[1] for row in result.fetchall()]
            if column not in columns:
                await conn.execute(text(sql))
                logger.info("Migration: added %s.%s", table, column)
        except Exception as e:
            logger.debug("Migration skipped for %s.%s: %s", table, column, e)


async def setup():
    async with engine.begin() as conn:
        await conn.run_sync(metadata.create_all)
        await _migrate(conn)


async def reset_db():
    async with engine.begin() as conn:
        await conn.run_sync(metadata.drop_all)
        await conn.run_sync(metadata.create_all)
    return {"status": "reset_successful"}


if __name__ == "__main__":
    asyncio.run(setup())
