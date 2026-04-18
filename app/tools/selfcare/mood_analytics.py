from datetime import datetime, timedelta

from sqlalchemy import select

from app.db.engine import engine
from app.db.models import journal_entries, messages, mood_logs


async def get_mood_analytics(user_id: str) -> dict:
    async with engine.begin() as conn:
        result = await conn.execute(
            select(mood_logs)
            .where(mood_logs.c.user_id == user_id)
            .order_by(mood_logs.c.timestamp)
        )
        rows = result.fetchall()

    if not rows:
        return {"timeline": [], "distribution": {}, "total_entries": 0, "streak": 0, "sources": {}}

    timeline = [
        {
            "id": row.id,
            "date": str(row.timestamp)[:10] if row.timestamp else "",
            "mood": row.mood_label,
            "message": row.message[:200] if row.message else "",
            "source_type": row.source_type or "explicit",
            "source_id": row.source_id,
            "timestamp": str(row.timestamp) if row.timestamp else "",
        }
        for row in rows
    ]

    distribution: dict[str, int] = {}
    sources: dict[str, int] = {}
    for row in rows:
        label = row.mood_label or "unknown"
        distribution[label] = distribution.get(label, 0) + 1
        src = row.source_type or "explicit"
        sources[src] = sources.get(src, 0) + 1

    # Streak calculation
    dates = sorted(set(
        str(row.timestamp)[:10] for row in rows if row.timestamp
    ))
    streak = 0
    if dates:
        today = datetime.now().strftime("%Y-%m-%d")
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        if dates[-1] in (today, yesterday):
            streak = 1
            for i in range(len(dates) - 1, 0, -1):
                d1 = datetime.strptime(dates[i], "%Y-%m-%d")
                d2 = datetime.strptime(dates[i - 1], "%Y-%m-%d")
                if (d1 - d2).days == 1:
                    streak += 1
                else:
                    break

    return {
        "timeline": timeline,
        "distribution": distribution,
        "total_entries": len(rows),
        "streak": streak,
        "sources": sources,
    }


async def get_mood_detail(mood_id: int, user_id: str) -> dict | None:
    """Get full mood log with linked source content."""
    async with engine.begin() as conn:
        result = await conn.execute(
            select(mood_logs).where(
                mood_logs.c.id == mood_id,
                mood_logs.c.user_id == user_id,
            )
        )
        row = result.fetchone()

    if not row:
        return None

    detail = {
        "id": row.id,
        "mood": row.mood_label,
        "message": row.message,
        "timestamp": str(row.timestamp),
        "source_type": row.source_type or "explicit",
        "source_id": row.source_id,
        "source_content": None,
    }

    # Fetch linked source content
    if row.source_id:
        async with engine.begin() as conn:
            if row.source_type == "journal":
                src = await conn.execute(
                    select(journal_entries).where(journal_entries.c.id == row.source_id)
                )
                src_row = src.fetchone()
                if src_row:
                    detail["source_content"] = src_row.content
            elif row.source_type == "chat":
                src = await conn.execute(
                    select(messages).where(messages.c.id == row.source_id)
                )
                src_row = src.fetchone()
                if src_row:
                    detail["source_content"] = src_row.content

    return detail
