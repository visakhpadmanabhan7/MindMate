"""Run database schema migrations for existing SQLite databases.

Usage: python -m app.scripts.migrate_schema
"""

import asyncio

from sqlalchemy import text

from app.db.engine import engine

MIGRATIONS = [
    # users — password auth
    "ALTER TABLE users ADD COLUMN password_hash TEXT",
    # mood_logs — source tracking
    "ALTER TABLE mood_logs ADD COLUMN source_type TEXT",
    "ALTER TABLE mood_logs ADD COLUMN source_id INTEGER",
    "ALTER TABLE mood_logs ADD COLUMN confidence TEXT",
    # journal_entries — auto-analysis
    "ALTER TABLE journal_entries ADD COLUMN updated_at DATETIME",
    "ALTER TABLE journal_entries ADD COLUMN mood_label TEXT",
    "ALTER TABLE journal_entries ADD COLUMN themes TEXT",
    "ALTER TABLE journal_entries ADD COLUMN entities TEXT",
    # messages — editability
    "ALTER TABLE messages ADD COLUMN updated_at DATETIME",
    "ALTER TABLE messages ADD COLUMN original_content TEXT",
    # therapy_sessions — editability
    "ALTER TABLE therapy_sessions ADD COLUMN updated_at DATETIME",
]


async def run_migrations():
    async with engine.begin() as conn:
        for sql in MIGRATIONS:
            try:
                await conn.execute(text(sql))
                col = sql.split("ADD COLUMN ")[1].split(" ")[0]
                table = sql.split("ALTER TABLE ")[1].split(" ")[0]
                print(f"  Added {table}.{col}")
            except Exception as e:
                if "duplicate column" in str(e).lower() or "already exists" in str(e).lower():
                    pass  # Column already exists, skip
                else:
                    print(f"  Skipped: {sql[:60]}... ({e})")

    print("Schema migration complete.")


if __name__ == "__main__":
    asyncio.run(run_migrations())
