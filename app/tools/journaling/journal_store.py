from datetime import datetime
from sqlalchemy import insert

from app.db.engine import engine
from app.db.models import journal_entries

# Tool: save a journal entry
async def save_journal_entry(content: str, user_id: str = "anonymous"):
    """
    Inserts a journal entry into the journal_entries table.
    """
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
