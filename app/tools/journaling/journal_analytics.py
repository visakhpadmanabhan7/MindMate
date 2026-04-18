import json
from collections import Counter

from sqlalchemy import desc, select

from app.db.engine import engine
from app.db.models import journal_entries


async def get_journal_entries(
    user_id: str,
    limit: int = 20,
    offset: int = 0,
    search: str | None = None,
) -> dict:
    async with engine.begin() as conn:
        query = (
            select(journal_entries)
            .where(journal_entries.c.user_id == user_id)
        )

        if search:
            query = query.where(journal_entries.c.content.contains(search))

        query = (
            query
            .order_by(desc(journal_entries.c.created_at))
            .limit(limit)
            .offset(offset)
        )

        result = await conn.execute(query)
        rows = result.fetchall()

    entries = []
    for row in rows:
        entries.append({
            "id": row.id,
            "content": row.content,
            "mood_label": row.mood_label,
            "themes": json.loads(row.themes or "[]"),
            "entities": json.loads(row.entities or "[]"),
            "sentiment_score": row.sentiment_score if hasattr(row, "sentiment_score") else None,
            "summary": row.summary if hasattr(row, "summary") else None,
            "created_at": str(row.created_at) if row.created_at else "",
            "updated_at": str(row.updated_at) if row.updated_at else None,
        })

    return {"entries": entries, "count": len(entries)}


async def get_journal_themes(user_id: str) -> dict:
    """Get aggregated theme frequency across all journal entries."""
    async with engine.begin() as conn:
        result = await conn.execute(
            select(journal_entries.c.themes)
            .where(
                journal_entries.c.user_id == user_id,
                journal_entries.c.themes.isnot(None),
            )
        )
        rows = result.fetchall()

    theme_counter: Counter = Counter()
    for row in rows:
        try:
            themes = json.loads(row.themes or "[]")
            for theme in themes:
                theme_counter[theme.lower().strip()] += 1
        except (json.JSONDecodeError, TypeError):
            continue

    return {
        "themes": [
            {"name": name, "count": count}
            for name, count in theme_counter.most_common(30)
        ]
    }
